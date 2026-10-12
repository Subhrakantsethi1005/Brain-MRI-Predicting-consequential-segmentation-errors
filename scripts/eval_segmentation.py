"""Evaluate Model 1 (the segmenter) on a held-out split with a single forward pass.

Reports Dice (TC/WT/ET) and tumour-volume error — the reproducible-baseline deliverable.
This is deterministic (no MC dropout): it measures the segmenter itself, not its uncertainty.

    python scripts/eval_segmentation.py --split seg_val
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import torch  # noqa: E402
from monai.inferers import sliding_window_inference  # noqa: E402
from tqdm import tqdm  # noqa: E402

from brainrisk.config import ensure_dir, load_config  # noqa: E402
from brainrisk.data import discover, eval_transforms, load_splits  # noqa: E402
from brainrisk.metrics import case_errors, summarise_segmentation  # noqa: E402
from brainrisk.model import build_unet  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/default.yaml")
    ap.add_argument("--split", default="seg_val")
    ap.add_argument("--checkpoint", default=None)
    args = ap.parse_args()
    cfg = load_config(args.config)
    d, sc, ic = cfg["data"], cfg["segmentation"], cfg["inference"]
    if args.split.startswith("seg_train"):
        sys.exit("Reporting on the training split would overstate quality; use seg_val or a risk split.")

    by_id = {c["id"]: c for c in discover(d)}
    cases = [by_id[i] for i in load_splits(cfg["splits"]["file"])[args.split]]
    tf = eval_transforms(d["enhancing_label"], d.get("core_labels", [1]))
    roi = tuple(sc["roi_size"])

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = build_unet(sc).to(device).eval()
    ckpt = args.checkpoint or Path(sc["out_dir"]) / "best.pt"
    model.load_state_dict(torch.load(ckpt, map_location=device))

    rows = []
    with torch.no_grad():
        for case in tqdm(cases):
            data = tf(case)
            image = data["image"].unsqueeze(0).to(device)
            ref = data["label"].numpy().astype(bool)
            affine = np.asarray(data["image"].affine)
            spacing = tuple(float(v) for v in np.sqrt((affine[:3, :3] ** 2).sum(0)))
            voxel_ml = float(np.prod(spacing)) / 1000.0
            with torch.autocast(device_type=device.type, enabled=sc["amp"] and device.type == "cuda"):
                logits = sliding_window_inference(image, roi, ic["sw_batch_size"], model, overlap=ic["overlap"])
            pred = (torch.sigmoid(logits.float())[0].cpu().numpy() > ic["threshold"])
            rows.append({"case_id": case["id"], **case_errors(pred, ref, voxel_ml, spacing)})

    df = pd.DataFrame(rows)
    out = ensure_dir(sc["out_dir"])
    df.to_csv(out / f"seg_eval_{args.split}.csv", index=False)
    summary = summarise_segmentation(df)
    summary.to_csv(out / f"seg_eval_{args.split}_summary.csv", index=False)
    print(f"\nModel 1 on {args.split} (n={len(df)}):")
    print(summary.round(3).to_string(index=False))
    print("\nBenchmark BraTS Dice for context: WT ~0.89, TC ~0.85, ET ~0.82")


if __name__ == "__main__":
    main()
