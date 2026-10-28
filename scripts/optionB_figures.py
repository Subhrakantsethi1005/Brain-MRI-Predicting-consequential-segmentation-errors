"""Figures for the Option B report, from the inference CSV. Saves PNGs to docs/paper/figures/."""
import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

REL_MIN, ABS_MIN_ML, DICE_GOOD = 0.25, 1.0, 0.85


def conseq(df, r):
    rel = df[f"{r}_rel_err"]
    return ((rel >= REL_MIN) & (df[f"{r}_abs_err_ml"] >= ABS_MIN_ML)).where(rel.notna())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="outputs/case_features_brats2023.csv")
    ap.add_argument("--splits", nargs="+", default=["risk_dev", "risk_test"])
    ap.add_argument("--out", default="docs/paper/figures")
    args = ap.parse_args()
    df = pd.read_csv(args.csv)
    df = df[df["split"].isin(args.splits)].copy()
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    regions = ["WT", "TC", "ET"]

    # Fig 1: Dice vs relative volume error (WT), coloured by consequential
    d = df[df["WT_rel_err"].notna()].copy()
    y = conseq(d, "WT").astype(bool)
    fig, ax = plt.subplots(figsize=(5.2, 4))
    ax.scatter(d["WT_dice"][~y], d["WT_rel_err"][~y] * 100, s=18, c="#4C78A8", label="not consequential", alpha=.7)
    ax.scatter(d["WT_dice"][y], d["WT_rel_err"][y] * 100, s=30, c="#E4572E", label="consequential", alpha=.9)
    ax.axhline(REL_MIN * 100, ls="--", c="#888", lw=1)
    ax.axvline(DICE_GOOD, ls=":", c="#888", lw=1)
    ax.set_xlabel("Whole-tumour Dice"); ax.set_ylabel("Relative volume error (%)")
    ax.set_title("Consequential errors coincide with low Dice (WT)")
    ax.legend(fontsize=8, frameon=False)
    fig.tight_layout(); fig.savefig(out / "fig1_dice_vs_volerr.png", dpi=150); plt.close(fig)

    # Fig 2: consequential-error rate by sub-region
    rates = [float(conseq(df, r).mean()) * 100 for r in regions]
    fig, ax = plt.subplots(figsize=(4.2, 3.6))
    ax.bar(regions, rates, color=["#4C78A8", "#72B7B2", "#E4572E"])
    for i, v in enumerate(rates):
        ax.text(i, v + 0.3, f"{v:.1f}%", ha="center", fontsize=9)
    ax.set_ylabel("Consequential-error rate (%)")
    ax.set_title("Consequential volume errors by sub-region")
    fig.tight_layout(); fig.savefig(out / "fig2_rate_by_region.png", dpi=150); plt.close(fig)

    print(f"saved figures to {out} (n={len(df)} cases, splits={args.splits})")


if __name__ == "__main__":
    main()
