"""Option B / A1+A2: characterise glioma segmentation errors and show the
'Dice-blind consequential error' phenomenon, straight from the inference CSV.

Headline finding (A2, metric-blindness): how many cases look GOOD by overlap
(Dice >= tau) yet still carry a CLINICALLY CONSEQUENTIAL whole-tumour volume
error (frozen endpoint: WT rel err >= 25% AND abs err >= 1 mL)?

A1 (characterisation): signed volume error distribution, over- vs under-
segmentation rates, and consequential-error rate stratified by tumour size.

Runs on whatever cases are present in the CSV (partial runs are fine).

    python scripts/optionB_characterize.py
    python scripts/optionB_characterize.py --csv outputs/case_features_brats2023.csv --splits risk_dev risk_test
"""

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

# Frozen primary endpoint (do NOT change — see docs/paper/optionB_preregistration.md)
REL_MIN = 0.25
ABS_MIN_ML = 1.0
DICE_GOOD = 0.85  # "looks good by overlap" threshold for the metric-blindness story


def consequential(df, region):
    """Consequential-error label for a region; NaN where undefined (ref region absent)."""
    rel = df[f"{region}_rel_err"]
    lab = ((rel >= REL_MIN) & (df[f"{region}_abs_err_ml"] >= ABS_MIN_ML)).astype(float)
    return lab.where(rel.notna())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="outputs/case_features_brats2023.csv")
    ap.add_argument("--splits", nargs="+", default=["risk_dev", "risk_test"])
    ap.add_argument("--out", default="outputs/optionB")
    args = ap.parse_args()

    csv = Path(args.csv)
    if not csv.exists():
        raise SystemExit(f"CSV not found: {csv} (run scripts/02_infer_mc.py first)")
    df = pd.read_csv(csv)
    if "split" in df:
        present = [s for s in args.splits if s in set(df["split"])]
        df = df[df["split"].isin(args.splits)].copy()
        print(f"Using splits {present}; {len(df)} cases "
              f"(CSV total {len(pd.read_csv(csv))}).")
    outdir = Path(args.out)
    outdir.mkdir(parents=True, exist_ok=True)

    summary = {"n_cases_total": int(len(df)), "splits": args.splits, "regions": {}}
    print("\n===== OPTION B — characterisation (A1/A2), per region =====")

    for region in ("WT", "TC", "ET"):
        df[f"y_{region}"] = consequential(df, region)
        valid = df[df[f"y_{region}"].notna()].copy()
        n = len(valid)
        if n == 0:
            print(f"[{region}] no cases with defined endpoint yet — skipping")
            continue

        s = valid[f"{region}_signed_err_ml"]
        rpt = {
            "n_defined": int(n),
            "consequential_rate": float(valid[f"y_{region}"].mean()),
            "over_seg_rate": float((s > 0).mean()),
            "under_seg_rate": float((s < 0).mean()),
            "signed_err_ml_median": float(s.median()),
        }
        # metric-blindness: good Dice but consequential volume error
        good = valid[valid[f"{region}_dice"] >= DICE_GOOD]
        rpt["n_dice_good"] = int(len(good))
        rpt["dice_blind_consequential_count"] = int(good[f"y_{region}"].sum()) if len(good) else 0
        rpt["dice_blind_consequential_rate"] = (
            float(good[f"y_{region}"].mean()) if len(good) else None)
        sub = valid[valid[f"{region}_rel_err"].notna()]
        if len(sub) > 2 and sub[f"{region}_dice"].std() > 0:
            rpt["corr_dice_vs_relvolerr"] = float(
                np.corrcoef(sub[f"{region}_dice"], sub[f"{region}_rel_err"])[0, 1])
        summary["regions"][region] = rpt

        tag = " (PRIMARY/frozen)" if region == "WT" else " (secondary/exploratory)"
        print(f"\n[{region}]{tag}  n={n}")
        print(f"  consequential-error rate : {rpt['consequential_rate']:.1%}")
        print(f"  over / under segmentation: {rpt['over_seg_rate']:.0%} / {rpt['under_seg_rate']:.0%}")
        if rpt["n_dice_good"]:
            print(f"  Dice-blind consequential : {rpt['dice_blind_consequential_count']}/"
                  f"{rpt['n_dice_good']} ({rpt['dice_blind_consequential_rate']:.1%}) "
                  f"of Dice>={DICE_GOOD} cases are still consequential")
        if "corr_dice_vs_relvolerr" in rpt:
            print(f"  corr(Dice, |rel vol err|): {rpt['corr_dice_vs_relvolerr']:.2f}")

    (outdir / "characterize_summary.json").write_text(json.dumps(summary, indent=2))
    print(f"\nsaved: {outdir/'characterize_summary.json'}")


if __name__ == "__main__":
    main()
