"""Visual showcase: the trained model's tumour outlines on REAL brain MRI,
next to the expert ground truth, with measured volumes and the trust verdict.

Produces one panel per example case + a combined montage, proving the system
actually works end-to-end on held-out scans.

    python scripts/showcase_demo.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "brats2023_download" / "ASNR-MICCAI-BraTS2023-GLI-Challenge-TrainingData"
PRED = ROOT / "outputs" / "pred_masks_brats23"
OUT = ROOT / "docs" / "paper" / "figures" / "showcase"
OUT.mkdir(parents=True, exist_ok=True)

REL_MIN, ABS_MIN = 0.25, 1.0


def load(path):
    # Predicted masks were saved with an identity affine while the MRI/GT use an
    # LPS affine; reorient everything to canonical (RAS) so they align voxel-wise.
    img = nib.as_closest_canonical(nib.load(str(path)))
    return np.asarray(img.dataobj), float(np.prod(img.header.get_zooms()))  # data, mm^3/voxel


def wt(mask):                      # whole tumour = any non-zero label
    return mask > 0


def best_slice(gt_wt):
    areas = gt_wt.sum(axis=(0, 1))
    return int(np.argmax(areas))


def panel(ax, bg, overlay, title, color):
    ax.imshow(np.rot90(bg), cmap="gray")
    if overlay is not None:
        ax.contour(np.rot90(overlay), levels=[0.5], colors=[color], linewidths=1.4)
    ax.set_title(title, fontsize=9)
    ax.axis("off")


def make_case(case_id):
    cdir = DATA / case_id
    flair, vmm3 = load(cdir / f"{case_id}-t2f.nii.gz")
    gt, _ = load(cdir / f"{case_id}-seg.nii.gz")
    pred, _ = load(PRED / f"{case_id}.nii.gz")
    gt_wt, pred_wt = wt(gt), wt(pred)
    k = best_slice(gt_wt)
    mlv = vmm3 / 1000.0
    v_true = gt_wt.sum() * mlv
    v_pred = pred_wt.sum() * mlv
    inter = (gt_wt & pred_wt).sum()
    dice = 2 * inter / (gt_wt.sum() + pred_wt.sum() + 1e-9)
    rel = abs(v_pred - v_true) / (v_true + 1e-9)
    flagged = (rel >= REL_MIN) and (abs(v_pred - v_true) >= ABS_MIN)
    verdict = "FLAG -> review" if flagged else "trust (auto)"

    fig, ax = plt.subplots(1, 3, figsize=(9, 3.4))
    panel(ax[0], flair[:, :, k], None, f"{case_id}\nFLAIR MRI (input)", None)
    panel(ax[1], flair[:, :, k], gt_wt[:, :, k], f"Expert outline\ntrue volume = {v_true:.1f} mL", "#2ca02c")
    panel(ax[2], flair[:, :, k], pred_wt[:, :, k],
          f"AI outline (our model)\nmeasured = {v_pred:.1f} mL", "#d62728")
    col = "#c62828" if flagged else "#2e7d32"
    fig.suptitle(f"Dice {dice:.2f}   |   volume error {rel*100:.0f}%   |   checker: {verdict}",
                 fontsize=10, color=col, y=1.02, fontweight="bold")
    fig.tight_layout()
    p = OUT / f"showcase_{case_id}.png"
    fig.savefig(p, dpi=130, bbox_inches="tight")
    plt.close(fig)
    return dict(case=case_id, dice=dice, v_true=v_true, v_pred=v_pred, rel=rel, flagged=flagged, png=p)


def main():
    df = pd.read_csv(ROOT / "outputs" / "case_features_brats2023.csv")
    t = df[df.split == "risk_test"].copy()
    conseq = (t.WT_rel_err >= REL_MIN) & (t.WT_abs_err_ml >= ABS_MIN)
    good = t[~conseq].sort_values("WT_dice", ascending=False).case_id.head(2).tolist()
    flag = t[conseq].sort_values("WT_rel_err", ascending=False).case_id.head(2).tolist()
    picks = good + flag
    print("examples (2 good, 2 flagged):", picks)

    results = [make_case(c) for c in picks]

    # combined montage
    imgs = [plt.imread(str(r["png"])) for r in results]
    fig, ax = plt.subplots(len(imgs), 1, figsize=(9, 3.4 * len(imgs)))
    for a, im, r in zip(np.atleast_1d(ax), imgs, results):
        a.imshow(im); a.axis("off")
    fig.tight_layout()
    combo = OUT / "showcase_montage.png"
    fig.savefig(combo, dpi=130, bbox_inches="tight")
    plt.close(fig)

    print(f"\nwrote {len(results)} case panels + montage to {OUT}")
    for r in results:
        tag = "FLAGGED" if r["flagged"] else "trusted"
        print(f"  {r['case']}: Dice {r['dice']:.2f}, true {r['v_true']:.1f} mL, "
              f"AI {r['v_pred']:.1f} mL, err {r['rel']*100:.0f}% -> {tag}")


if __name__ == "__main__":
    main()
