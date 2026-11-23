"""Conformal selective-triage layer on the reference-free longitudinal flag.

Upgrade over the binary agree/defer flag: a DISTRIBUTION-FREE GUARANTEE. We use
Conformal Risk Control (CRC; Angelopoulos et al. 2023) to calibrate a single
referral threshold tau so that, on future exchangeable data, the missed-progression
rate among AUTO-CLEARED decisions is provably bounded:

    decision rule (tau):  AUTO-CLEAR (safe, no referral) iff  fold_d < tau AND fold_h < tau
                          REFER to a human otherwise  (either tool shows >= tau growth)
    risk (clinically critical):  FNR(tau) = P(auto-cleared | expert PD)
                                 = fraction of true progressions wrongly auto-cleared

FNR(tau) is monotone non-decreasing in tau (a larger tau clears more, so more PDs slip
through). CRC picks the LARGEST tau (=> most coverage) whose finite-sample-corrected
calibration FNR is <= alpha:

    tau_hat = sup { tau : (m * Rhat(tau) + 1) / (m + 1) <= alpha }

with m = number of expert-PD timepoints in the calibration half and loss bound B=1.
Theorem gives  E[ FNR_test(tau_hat) ] <= alpha.  Coverage = fraction of ALL decisions
auto-cleared is what the guarantee BUYS the clinic (the rest are deferred).

Calibration is PATIENT-DISJOINT (timepoints within a patient are not exchangeable, so
we split by patient, mirroring the frozen prereg's seed=0 50/50 split). We report the
frozen split as headline AND the mean realised test-FNR over 200 random patient splits
as an empirical check that the guarantee holds marginally. Honest caveats carried in
the paper: patient-level (not timepoint) exchangeability; small cohort => wide slack;
volume-only is not the full RANO assessment, so coverage at low alpha is limited by the
~80% PD base rate of measurable timepoints, not a flaw in the guarantee.

Reuses the FROZEN definitions from lumiere_strengthen.py. Deterministic (seed=0).

    python scripts/lumiere_conformal.py
"""
import os, sys, json, random
from collections import defaultdict

sys.path.insert(0, os.path.dirname(__file__))
from lumiere_strengthen import load_rano, load_vol, build, DBT, HG  # frozen defs

OUT = os.path.join(os.path.dirname(__file__), "..", "outputs", "lumiere")
os.makedirs(OUT, exist_ok=True)
ALPHAS = [0.05, 0.10, 0.20]
# candidate referral thresholds on fold-change-to-nadir (1.0 = clear nothing above nadir)
GRID = [1.0 + 0.02 * i for i in range(0, 201)]  # 1.00 .. 5.00


def cleared(r, tau):
    """Auto-clear (no referral) iff BOTH tools report sub-threshold growth."""
    return r["fold_d"] < tau and r["fold_h"] < tau


def fnr(rows, tau):
    """Missed-progression rate: fraction of expert-PD timepoints auto-cleared."""
    pos = [r for r in rows if r["expert_pd"] == 1]
    if not pos:
        return None
    return sum(cleared(r, tau) for r in pos) / len(pos)


def coverage(rows, tau):
    return sum(cleared(r, tau) for r in rows) / len(rows) if rows else 0.0


def crc_threshold(cal_rows, alpha):
    """Largest tau whose finite-sample-corrected calibration FNR <= alpha."""
    pos = [r for r in cal_rows if r["expert_pd"] == 1]
    m = len(pos)
    if m == 0:
        return GRID[0]
    best = GRID[0]
    for tau in GRID:
        rhat = sum(cleared(r, tau) for r in pos) / m
        corrected = (m * rhat + 1.0) / (m + 1.0)
        if corrected <= alpha:
            best = tau  # monotone: keep the largest passing tau
        else:
            break
    return best


def patient_split(rows, seed):
    pats = sorted({r["patient"] for r in rows})
    rng = random.Random(seed)
    rng.shuffle(pats)
    half = set(pats[len(pats) // 2:])
    cal = [r for r in rows if r["patient"] not in half]
    test = [r for r in rows if r["patient"] in half]
    return cal, test


def main():
    rano = load_rano(); vd = load_vol(DBT); vh = load_vol(HG)
    rows = build(rano, vd, vh)
    pats = sorted({r["patient"] for r in rows})
    base_pd = sum(r["expert_pd"] for r in rows) / len(rows)
    res = {"n_rows": len(rows), "n_patients": len(pats), "pd_base_rate": round(base_pd, 4),
           "method": "CRC FNR-control, patient-disjoint calibration", "frozen": {}, "robustness": {}}

    print("=" * 74)
    print(f"CONFORMAL SELECTIVE TRIAGE  (n={len(rows)} timepoints, {len(pats)} patients, "
          f"expert-PD base {base_pd:.1%})")
    print("Guarantee target: missed-progression rate (FNR) among auto-cleared <= alpha")
    print("=" * 74)

    # ---- Headline: frozen seed=0 patient-disjoint split ----
    cal, test = patient_split(rows, 0)
    print(f"\nFROZEN SPLIT (seed=0): calibrate on {len({r['patient'] for r in cal})} patients "
          f"({len(cal)} tps), test on {len({r['patient'] for r in test})} patients ({len(test)} tps)")
    print(f"{'alpha':>6} | {'tau_hat':>7} | {'test FNR':>9} | {'test coverage':>13} | guarantee")
    for a in ALPHAS:
        tau = crc_threshold(cal, a)
        tfnr = fnr(test, tau); cov = coverage(test, tau)
        ok = (tfnr is not None and tfnr <= a)
        res["frozen"][f"alpha_{a}"] = dict(tau=round(tau, 3),
            test_fnr=None if tfnr is None else round(tfnr, 4),
            test_coverage=round(cov, 4), holds=bool(ok))
        print(f"{a:>6.2f} | {tau:>7.2f} | {('n/a' if tfnr is None else f'{tfnr:>8.1%}')} | "
              f"{cov:>12.1%} | {'held' if ok else 'exceeded (single split; see 200-split mean)'}")

    # ---- Robustness: mean realised test-FNR over 200 random patient splits ----
    print(f"\n200-SPLIT MARGINAL CHECK (mean realised test metrics; guarantee is in expectation)")
    print(f"{'alpha':>6} | {'mean test FNR':>13} | {'mean coverage':>13} | {'% splits FNR<=alpha':>19}")
    for a in ALPHAS:
        fnrs, covs = [], []
        for seed in range(200):
            c, t = patient_split(rows, seed)
            tau = crc_threshold(c, a)
            f_ = fnr(t, tau); cov = coverage(t, tau)
            if f_ is not None:
                fnrs.append(f_); covs.append(cov)
        mean_fnr = sum(fnrs) / len(fnrs); mean_cov = sum(covs) / len(covs)
        frac_ok = sum(f_ <= a for f_ in fnrs) / len(fnrs)
        res["robustness"][f"alpha_{a}"] = dict(mean_test_fnr=round(mean_fnr, 4),
            mean_coverage=round(mean_cov, 4), frac_splits_fnr_le_alpha=round(frac_ok, 4),
            n_splits=len(fnrs))
        print(f"{a:>6.2f} | {mean_fnr:>12.1%} | {mean_cov:>12.1%} | {frac_ok:>18.0%}")
        print(f"       -> guarantee {'HOLDS in expectation' if mean_fnr <= a else 'VIOLATED'} "
              f"(mean FNR {mean_fnr:.1%} vs target {a:.0%})")

    with open(os.path.join(OUT, "conformal.json"), "w") as f:
        json.dump(res, f, indent=2)
    print(f"\nsaved -> outputs/lumiere/conformal.json")


if __name__ == "__main__":
    main()
