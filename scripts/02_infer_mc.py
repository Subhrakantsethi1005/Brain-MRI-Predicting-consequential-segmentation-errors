"""Stochastic inference on held-out cases: one CSV row per case with features and reference errors.

Resumable: cases already in the CSV are skipped.

    python scripts/02_infer_mc.py --splits seg_val risk_dev risk_test
    python scripts/02_infer_mc.py --external-root data/BraTS-Africa --external-name africa --enhancing-label 3
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import nibabel as nib  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import torch  # noqa: E402
from tqdm import tqdm  # noqa: E402

from brainrisk.config import ensure_dir, load_config  # noqa: E402
from brainrisk.data import discover, discover_cases, eval_transforms, load_splits, regions_to_labels  # noqa: E402
from brainrisk.features import case_features  # noqa: E402
from brainrisk.metrics import case_errors  # noqa: E402
from brainrisk.model import build_unet, stochastic_predict  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/default.yaml")
    ap.add_argument("--splits", nargs="+", default=["seg_val", "risk_dev", "risk_test"])
    ap.add_argument("--checkpoint", default=None)
    ap.add_argument("--external-root", default=None, help="Evaluate every case under this folder instead")
    ap.add_argument("--external-name", default="external")
    ap.add_argument("--enhancing-label", type=int, default=None)
    ap.add_argument("--core-labels", nargs="+", type=int, default=None, help="Non-enhancing core labels")
    ap.add_argument("--modalities", nargs="+", default=None, help="Override for external naming, e.g. t1n t1c t2w t2f")
    args = ap.parse_args()
    cfg = load_config(args.config)
    d, sc, ic = cfg["data"], cfg["segmentation"], cfg["inference"]
    et_label = args.enhancing_label or d["enhancing_label"]
    core = args.core_labels or d.get("core_labels", [1])
    mods = args.modalities or d["modalities"]

    if args.external_root:
        cases = discover_cases(args.external_root, mods, d["label_suffix"])
        todo = [(args.external_name, c) for c in cases]
        out_csv = Path(ic["out_csv"]).with_name(f"case_features_{args.external_name}.csv")
    else:
        by_id = {c["id"]: c for c in discover(d)}
        splits = load_splits(cfg["splits"]["file"])
        for s in args.splits:
            if s.startswith("seg_train"):
                sys.exit("Refusing to compute features on the segmentation training set.")
        todo = [(s, by_id[i]) for s in args.splits for i in splits[s]]
        out_csv = Path(ic["out_csv"])

    done = set(pd.read_csv(out_csv)["case_id"]) if out_csv.exists() else set()
    todo = [(s, c) for s, c in todo if c["id"] not in done]
    print(f"{len(todo)} cases to process ({len(done)} already done) -> {out_csv}")
    ensure_dir(out_csv.parent)
    mask_dir = ensure_dir(ic["save_masks_dir"]) if ic["save_masks_dir"] else None

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = build_unet(sc).to(device)
    model.load_state_dict(torch.load(args.checkpoint or Path(sc["out_dir"]) / "best.pt", map_location=device))
    tf = eval_transforms(et_label, core)

    for split, case in tqdm(todo):
        data = tf(case)
        image = data["image"].unsqueeze(0).to(device)
        ref = data["label"].numpy().astype(bool)
        affine = np.asarray(data["image"].affine)
        spacing = tuple(float(v) for v in np.sqrt((affine[:3, :3] ** 2).sum(0)))
        voxel_ml = float(np.prod(spacing)) / 1000.0
        brain = (data["image"].numpy() != 0).any(0)

        samples = stochastic_predict(model, image, ic["mc_samples"], tuple(sc["roi_size"]),
                                     ic["sw_batch_size"], ic["overlap"], ic["tta_flips"], sc["amp"])
        feats, pred = case_features(samples, ic["threshold"], voxel_ml, ic["boundary_band_vox"], brain)
        errs = case_errors(pred, ref, voxel_ml, spacing)
        row = {"case_id": case["id"], "split": split, "voxel_ml": voxel_ml, **feats, **errs}
        pd.DataFrame([row]).to_csv(out_csv, mode="a", header=not out_csv.exists(), index=False)

        if mask_dir is not None:
            nib.save(nib.Nifti1Image(regions_to_labels(pred, et_label), affine), mask_dir / f"{case['id']}.nii.gz")


if __name__ == "__main__":
    main()
