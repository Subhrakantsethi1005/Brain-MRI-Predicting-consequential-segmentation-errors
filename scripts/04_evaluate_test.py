"""One-shot evaluation of frozen risk models on risk_test (or an external dataset).

Refuses to run if configs/preregistration.yaml has uncommitted changes, and records a
lock file so a second look at the test set is visible rather than silent.
"""

import argparse
import datetime
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import joblib  # noqa: E402
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from brainrisk.config import load_config, load_prereg  # noqa: E402
from brainrisk.metrics import add_labels, summarise_segmentation  # noqa: E402
from brainrisk.risk import operating_point, paired_bootstrap_diff, risk_coverage, summarise  # noqa: E402


def prereg_is_committed(path):
    try:
        subprocess.run(["git", "ls-files", "--error-unmatch", path], check=True, capture_output=True)
        dirty = subprocess.run(["git", "status", "--porcelain", path], capture_output=True, text=True).stdout
        return dirty.strip() == ""
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def score(entry, df):
    if "feature" in entry:
        return entry["sign"] * df[entry["feature"]].fillna(entry["median"]).to_numpy()
    return entry["model"].predict_proba(df[entry["features"]].to_numpy(float))[:, 1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/default.yaml")
    ap.add_argument("--prereg", default="configs/preregistration.yaml")
    ap.add_argument("--split", default="risk_test")
    ap.add_argument("--csv", default=None, help="Feature CSV (e.g. outputs/case_features_africa.csv)")
    ap.add_argument("--second-look", action="store_true", help="Re-run after a previous test evaluation")
    args = ap.parse_args()
    cfg, prereg = load_config(args.config), load_prereg(args.prereg)
    rc = cfg["risk"]
    out = Path(rc["out_dir"])

    if not prereg_is_committed(args.prereg):
        sys.exit(f"Commit {args.prereg} before evaluating on held-out data.")
    lock = out / f"EVALUATED_{args.split}.lock"
    if lock.exists() and not args.second_look:
        sys.exit(f"{args.split} was already evaluated ({lock.read_text().strip()}). "
                 "Use --second-look and report it in the paper.")
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    with open(lock, "a") as f:
        f.write(f"{datetime.datetime.now().isoformat()} commit={commit}\n")

    df = add_labels(pd.read_csv(args.csv or cfg["inference"]["out_csv"]), prereg)
    test = df[df.split == args.split].reset_index(drop=True)
    print(f"{args.split}: {len(test)} cases\n", summarise_segmentation(test).round(3))
    frozen = joblib.load(out / "frozen_models.joblib")

    rows, comps, scores = [], [], {}
    for (ep, group, mname), entry in frozen.items():
        sub = test[test[f"y_{ep}"].notna()]
        y = sub[f"y_{ep}"].astype(int).to_numpy()
        if y.min() == y.max():
            print(f"[{ep}] only one class on {args.split}; skipped")
            continue
        s = score(entry, sub)
        scores[(ep, group, mname)] = (y, s)
        rows.append({"endpoint": ep, "group": group, "model": entry.get("feature", mname),
                     **summarise(y, s, rc["bootstrap"]), **operating_point(y, s, entry["threshold"])})

    primary_model = prereg["primary_model"]
    for ep in {k[0] for k in scores}:
        ref_keys = [(ep, "best_single", "none"), (ep, "uncertainty", primary_model), (ep, "volume_only", primary_model)]
        for cand in ("combined", "boundary_morphology", "disagreement"):
            ck = (ep, cand, primary_model)
            for rk in ref_keys:
                if ck in scores and rk in scores:
                    y, sa = scores[ck]
                    comps.append({"endpoint": ep, "candidate": cand, "reference": rk[1],
                                  **paired_bootstrap_diff(y, sa, scores[rk][1], n=rc["bootstrap"])})

    report = pd.DataFrame(rows)
    report.to_csv(out / f"{args.split}_report.csv", index=False)
    pd.DataFrame(comps).to_csv(out / f"{args.split}_comparisons.csv", index=False)
    cols = ["endpoint", "group", "model", "n_pos", "auroc", "auroc_lo", "auroc_hi", "auprc", "prevalence",
            "sensitivity", "false_alert_rate", "retained_frac", "residual_error_rate"]
    print(report[cols].round(3).to_string(index=False))

    fig, ax = plt.subplots(figsize=(5, 4))
    for (ep, group, mname), (y, s) in scores.items():
        if ep == "primary" and mname in (primary_model, "none"):
            cov, risk = risk_coverage(y, s)
            ax.plot(cov, risk, label=group)
    ax.set_xlabel("Fraction of cases retained for automated processing")
    ax.set_ylabel("Consequential-error rate among retained")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out / f"{args.split}_risk_coverage.png", dpi=200)
    print(f"\nwrote reports to {out}")


if __name__ == "__main__":
    main()
