"""Develop error-risk models on risk_dev only (repeated CV), then fit final models and freeze thresholds.

Nothing here reads risk_test. Use the dev report to sanity-check, not to redefine endpoints.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import joblib  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.metrics import roc_auc_score  # noqa: E402

from brainrisk.config import ensure_dir, load_config, load_prereg  # noqa: E402
from brainrisk.metrics import add_labels, all_endpoints, summarise_segmentation  # noqa: E402
from brainrisk.risk import (DISAGREEMENT, UNCERTAINTY, feature_groups, make_model, oof_scores,  # noqa: E402
                            operating_point, summarise, threshold_for_sensitivity)


def best_single_feature(df, y, region):
    """Strongest single uncertainty/disagreement score on dev, with its direction fixed on dev."""
    best = None
    for n in UNCERTAINTY + DISAGREEMENT:
        col = f"{region}_{n}"
        if col not in df:
            continue
        x = df[col].fillna(df[col].median()).to_numpy()
        auc = roc_auc_score(y, x)
        sign = 1.0 if auc >= 0.5 else -1.0
        if best is None or max(auc, 1 - auc) > best[2]:
            best = (col, sign, max(auc, 1 - auc))
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/default.yaml")
    ap.add_argument("--prereg", default="configs/preregistration.yaml")
    args = ap.parse_args()
    cfg, prereg = load_config(args.config), load_prereg(args.prereg)
    rc = cfg["risk"]
    out = ensure_dir(rc["out_dir"])

    df = add_labels(pd.read_csv(cfg["inference"]["out_csv"]), prereg)
    if "seg_val" in set(df["split"]):
        print("Segmentation quality on seg_val:\n", summarise_segmentation(df[df.split == "seg_val"]).round(3))
    dev = df[df.split == "risk_dev"].reset_index(drop=True)
    print("Segmentation quality on risk_dev:\n", summarise_segmentation(dev).round(3))

    rows, frozen = [], {}
    for ep in all_endpoints(prereg):
        name, region = ep["name"], ep["region"]
        sub = dev[dev[f"y_{name}"].notna()].reset_index(drop=True)
        y = sub[f"y_{name}"].astype(int).to_numpy()
        print(f"\n[{name}] n={len(y)} positives={y.sum()} ({y.mean():.1%})")
        if y.sum() < 5 or (1 - y).sum() < 5:
            print("  fewer than 5 cases in a class on dev; skipping (report this, do not change the endpoint)")
            continue

        col, sign, _ = best_single_feature(sub, y, region)
        s = sign * sub[col].fillna(sub[col].median()).to_numpy()
        t = threshold_for_sensitivity(y, s, rc["target_sensitivity"])
        frozen[(name, "best_single", "none")] = {"feature": col, "sign": sign, "median": float(sub[col].median()),
                                                 "threshold": t}
        rows.append({"endpoint": name, "group": "best_single", "model": col, **summarise(y, s, rc["bootstrap"]),
                     **operating_point(y, s, t)})

        for group, feats in feature_groups(sub.columns, region).items():
            if not feats:
                continue
            X = sub[feats].to_numpy(float)
            for mname in prereg["models"]:
                s = oof_scores(make_model(mname), X, y, rc["cv_folds"], rc["cv_repeats"])
                t = threshold_for_sensitivity(y, s, rc["target_sensitivity"])
                rows.append({"endpoint": name, "group": group, "model": mname, "n_features": len(feats),
                             **summarise(y, s, rc["bootstrap"]), **operating_point(y, s, t)})
                final = make_model(mname).fit(X, y)
                frozen[(name, group, mname)] = {"model": final, "features": feats, "threshold": t}
                print(f"  {group:20s} {mname:8s} AUROC {rows[-1]['auroc']:.3f} "
                      f"[{rows[-1]['auroc_lo']:.3f}, {rows[-1]['auroc_hi']:.3f}]  "
                      f"retained@{rc['target_sensitivity']:.0%}sens {rows[-1]['retained_frac']:.1%}")

    report = pd.DataFrame(rows)
    report.to_csv(out / "dev_report.csv", index=False)
    joblib.dump(frozen, out / "frozen_models.joblib")
    with open(out / "dev_meta.json", "w") as f:
        json.dump({"n_dev": len(dev), "target_sensitivity": rc["target_sensitivity"]}, f, indent=2)
    print(f"\nwrote {out/'dev_report.csv'} and {out/'frozen_models.joblib'}")


if __name__ == "__main__":
    main()
