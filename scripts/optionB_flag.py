"""Option B / A3+A4: the consequence-targeted reference-free flag, and the key
differentiation vs a generic overlap-quality (QC) baseline.

A3  consequence flag : logistic on reference-free features -> predict the frozen
                       consequential-error label (WT rel>=25% & abs>=1mL).
A4  differentiation  : train a generic-QC baseline (same features -> predict a
                       low-Dice 'quality' target, QCResUNet-style) and test whether
                       it catches CONSEQUENTIAL errors as well as the consequence flag.
                       Hypothesis (our novelty): consequence flag > overlap-QC at
                       catching consequential errors. A null (they tie) is a valid,
                       reportable outcome and means overlap QC already suffices.

Protocol: fit on risk_dev, evaluate ONCE on risk_test (frozen). Trivial baselines
(volume_only, best single uncertainty) included for context.

    python scripts/optionB_flag.py --region WT
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from brainrisk.risk import (feature_groups, make_model, oof_scores, operating_point,  # noqa: E402
                            paired_bootstrap_diff, summarise, threshold_for_sensitivity)

REL_MIN, ABS_MIN_ML, DICE_GOOD, TARGET_SENS = 0.25, 1.0, 0.85, 0.90


def label_conseq(df, region):
    rel = df[f"{region}_rel_err"]
    y = ((rel >= REL_MIN) & (df[f"{region}_abs_err_ml"] >= ABS_MIN_ML)).astype(float)
    return y.where(rel.notna())


def fit_score(model_name, Xtr, ytr, Xte):
    from sklearn.base import clone
    m = clone(make_model(model_name)).fit(Xtr, np.asarray(ytr, int))
    return m.predict_proba(Xte)[:, 1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="outputs/case_features_brats2023.csv")
    ap.add_argument("--region", default="WT", choices=["WT", "TC", "ET"])
    ap.add_argument("--out", default="outputs/optionB")
    args = ap.parse_args()

    df = pd.read_csv(args.csv)
    df["y"] = label_conseq(df, args.region)
    df = df[df["y"].notna()].copy()
    dev = df[df["split"] == "risk_dev"].copy()
    test = df[df["split"] == "risk_test"].copy()
    print(f"[{args.region}] risk_dev n={len(dev)} (pos={int(dev['y'].sum())}) | "
          f"risk_test n={len(test)} (pos={int(test['y'].sum())})")
    if dev["y"].sum() < 5 or (len(test) and test["y"].sum() < 2):
        print("  -> not enough positives yet; let inference finish, then re-run.")
        if dev["y"].sum() < 5:
            return

    groups = feature_groups(df.columns, args.region)
    feats_all = groups["combined"]
    outdir = Path(args.out); outdir.mkdir(parents=True, exist_ok=True)

    Xdev = dev[feats_all].to_numpy(float); ydev = dev["y"].to_numpy(int)
    have_test = len(test) and test["y"].nunique() > 1
    Xte = test[feats_all].to_numpy(float) if have_test else None
    yte = test["y"].to_numpy(int) if have_test else None

    scores = {}  # name -> (dev_oof, test_score)

    # (A3) consequence-targeted flag: predict the consequential-error label
    scores["consequence_flag"] = (
        oof_scores(make_model("logistic"), Xdev, ydev),
        fit_score("logistic", Xdev, ydev, Xte) if have_test else None)

    # (A4) generic overlap-QC baseline: predict low-Dice 'quality', repurpose to flag consequence
    q_dev = (dev[f"{args.region}_dice"] < DICE_GOOD).astype(int).to_numpy()
    if q_dev.sum() >= 5 and q_dev.sum() < len(q_dev):
        scores["overlap_qc_baseline"] = (
            oof_scores(make_model("logistic"), Xdev, q_dev),  # dev: score ranks by predicted low-quality
            fit_score("logistic", Xdev, q_dev, Xte) if have_test else None)

    # trivial baselines
    Xvo_dev = dev[groups["volume_only"]].to_numpy(float)
    Xvo_te = test[groups["volume_only"]].to_numpy(float) if have_test else None
    scores["volume_only"] = (
        oof_scores(make_model("logistic"), Xvo_dev, ydev),
        fit_score("logistic", Xvo_dev, ydev, Xvo_te) if have_test else None)
    # best single uncertainty feature (abs corr with y on dev)
    unc = groups["uncertainty"]
    if unc:
        best = max(unc, key=lambda c: abs(np.corrcoef(dev[c].fillna(dev[c].median()), ydev)[0, 1])
                   if dev[c].notna().any() else 0)
        scores["best_single_uncertainty"] = (dev[best].fillna(dev[best].median()).to_numpy(),
                                              test[best].fillna(dev[best].median()).to_numpy() if have_test else None)

    # ---- evaluate ----
    report = {"region": args.region, "n_dev": len(dev), "n_test": len(test),
              "dev": {}, "test": {}, "A4_differentiation": None}

    def eval_block(y, name_to_s):
        out = {}
        for nm, s in name_to_s.items():
            if s is None:
                continue
            res = summarise(y, s, n_boot=2000)
            t = threshold_for_sensitivity(y, s, TARGET_SENS)
            op = operating_point(y, s, t)
            out[nm] = {"auroc": res["auroc"], "auroc_lo": res["auroc_lo"], "auroc_hi": res["auroc_hi"],
                       "auprc": res["auprc"], "retained_frac@90sens": op["retained_frac"],
                       "residual_error@90sens": op["residual_error_rate"]}
        return out

    report["dev"] = eval_block(ydev, {k: v[0] for k, v in scores.items()})
    if have_test:
        report["test"] = eval_block(yte, {k: v[1] for k, v in scores.items()})
        if "overlap_qc_baseline" in scores:
            report["A4_differentiation"] = paired_bootstrap_diff(
                yte, scores["consequence_flag"][1], scores["overlap_qc_baseline"][1])

    (outdir / f"flag_{args.region}.json").write_text(json.dumps(report, indent=2))

    # ---- console ----
    block = report["test"] if report["test"] else report["dev"]
    where = "risk_test" if report["test"] else "risk_dev (OOF; test not ready)"
    print(f"\n===== A3/A4 flag results on {where} ({args.region}) =====")
    for nm, m in sorted(block.items(), key=lambda kv: -kv[1]["auroc"]):
        print(f"  {nm:24s} AUROC {m['auroc']:.3f} [{m['auroc_lo']:.3f},{m['auroc_hi']:.3f}]"
              f"  retain@90sens {m['retained_frac@90sens']:.0%}"
              f"  residual {m['residual_error@90sens']:.1%}" if m['residual_error@90sens'] is not None
              else f"  {nm:24s} AUROC {m['auroc']:.3f}")
    if report["A4_differentiation"]:
        d = report["A4_differentiation"]
        verdict = ("consequence flag BEATS overlap-QC (supports novelty)" if d["lo"] > 0
                   else "no significant gain over overlap-QC (honest null — QC already suffices)")
        print(f"\nA4 consequence_flag - overlap_qc AUROC diff = {d['diff']:+.3f} "
              f"[{d['lo']:+.3f},{d['hi']:+.3f}], p={d['p']:.3f}\n  -> {verdict}")
    print(f"\nsaved: {outdir/f'flag_{args.region}.json'}")


if __name__ == "__main__":
    main()
