"""Train the baseline 3D U-Net on seg_train; select the checkpoint on seg_val. Resumable."""

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import torch  # noqa: E402
from monai.data import DataLoader, Dataset, decollate_batch  # noqa: E402
from monai.inferers import sliding_window_inference  # noqa: E402
from monai.losses import DiceLoss  # noqa: E402
from monai.metrics import DiceMetric  # noqa: E402
from monai.utils import set_determinism  # noqa: E402

from brainrisk import REGIONS  # noqa: E402
from brainrisk.config import ensure_dir, load_config  # noqa: E402
from brainrisk.data import discover, eval_transforms, load_splits, train_transforms  # noqa: E402
from brainrisk.model import build_unet  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/default.yaml")
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--warm-start", default=None,
                    help="Path to a .pt state_dict to initialise from (fine-tuning). "
                         "Layers whose shape matches are loaded; the rest keep random init.")
    args = ap.parse_args()
    cfg = load_config(args.config)
    d, sc = cfg["data"], cfg["segmentation"]
    out = ensure_dir(sc["out_dir"])
    set_determinism(sc["seed"])

    cases = {c["id"]: c for c in discover(d)}
    splits = load_splits(cfg["splits"]["file"])
    train = [cases[i] for i in splits["seg_train"]]
    val = [cases[i] for i in splits["seg_val"]]
    print(f"train {len(train)}  val {len(val)}")

    roi = tuple(sc["roi_size"])
    core = d.get("core_labels", [1])
    train_loader = DataLoader(Dataset(train, train_transforms(roi, d["enhancing_label"], core)),
                              batch_size=sc["batch_size"], shuffle=True, num_workers=sc["num_workers"],
                              pin_memory=True, persistent_workers=sc["num_workers"] > 0)
    val_loader = DataLoader(Dataset(val, eval_transforms(d["enhancing_label"], core)), batch_size=1,
                            num_workers=sc["num_workers"])

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = build_unet(sc).to(device)
    loss_fn = DiceLoss(smooth_nr=0, smooth_dr=1e-5, squared_pred=True, sigmoid=True)
    opt = torch.optim.AdamW(model.parameters(), lr=sc["lr"], weight_decay=sc["weight_decay"])
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=sc["max_epochs"])
    scaler = torch.amp.GradScaler(enabled=sc["amp"] and device.type == "cuda")
    dice_metric = DiceMetric(include_background=True, reduction="mean_batch")

    start, best, history = 0, -1.0, []
    ckpt_path = out / "last.pt"
    if args.warm_start and not (args.resume and ckpt_path.exists()):
        src = torch.load(args.warm_start, map_location=device)
        src = src.get("model", src)  # accept a raw state_dict or a training checkpoint
        tgt = model.state_dict()
        loaded = {k: v for k, v in src.items() if k in tgt and v.shape == tgt[k].shape}
        tgt.update(loaded)
        model.load_state_dict(tgt)
        print(f"warm-started: loaded {len(loaded)}/{len(tgt)} tensors from {args.warm_start}")
    if args.resume and ckpt_path.exists():
        ck = torch.load(ckpt_path, map_location=device)
        model.load_state_dict(ck["model"]); opt.load_state_dict(ck["opt"])
        sched.load_state_dict(ck["sched"]); scaler.load_state_dict(ck["scaler"])
        start, best, history = ck["epoch"] + 1, ck["best"], ck["history"]
        print(f"resumed at epoch {start}, best mean Dice {best:.4f}")

    for epoch in range(start, sc["max_epochs"]):
        model.train()
        t0, total = time.time(), 0.0
        for batch in train_loader:
            x, y = batch["image"].to(device), batch["label"].to(device)
            opt.zero_grad(set_to_none=True)
            with torch.autocast(device_type=device.type, enabled=scaler.is_enabled()):
                loss = loss_fn(model(x), y)
            scaler.scale(loss).backward()
            scaler.step(opt)
            scaler.update()
            total += loss.item()
        sched.step()
        rec = {"epoch": epoch, "loss": total / len(train_loader), "sec": round(time.time() - t0)}

        if (epoch + 1) % sc["val_every"] == 0 or epoch + 1 == sc["max_epochs"]:
            model.eval()
            with torch.no_grad():
                for batch in val_loader:
                    x, y = batch["image"].to(device), batch["label"].to(device)
                    with torch.autocast(device_type=device.type, enabled=scaler.is_enabled()):
                        logits = sliding_window_inference(x, roi, 2, model, overlap=0.5)
                    preds = [(torch.sigmoid(p.float()) > 0.5).float() for p in decollate_batch(logits)]
                    dice_metric(y_pred=preds, y=decollate_batch(y))
            per_region = dice_metric.aggregate().tolist()
            dice_metric.reset()
            rec.update({f"val_dice_{r}": v for r, v in zip(REGIONS, per_region)})
            mean = sum(per_region) / 3
            rec["val_dice_mean"] = mean
            if mean > best:
                best = mean
                torch.save(model.state_dict(), out / "best.pt")
        history.append(rec)
        print(json.dumps(rec))
        torch.save({"model": model.state_dict(), "opt": opt.state_dict(), "sched": sched.state_dict(),
                    "scaler": scaler.state_dict(), "epoch": epoch, "best": best, "history": history},
                   ckpt_path)
        with open(out / "history.json", "w") as f:
            json.dump(history, f, indent=1)
    print(f"best val mean Dice {best:.4f}")


if __name__ == "__main__":
    main()
