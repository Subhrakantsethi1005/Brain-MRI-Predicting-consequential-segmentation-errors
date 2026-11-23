"""
Frozen-protocol validation for docs/paper/longitudinal_preregistration.md.

Tests the reference-free reliability FLAG (two independent segmenters agree on the
RANO progression call) against EXPERT RANO ratings, on a held-out 50% patient split.

Definitions are exactly as pre-registered:
  - eligible timepoint: post-op follow-up rated PD/SD/PR/CR, CE volume in both tools
  - running nadir (per tool): min CE volume over all prior post-op timepoints (incl. Post-Op)
  - auto_PD_tool(t): V(t) >= 1.40*nadir AND V(t)-nadir >= 1000 mm^3
  - expert_PD(t): rating == PD
  - agree(t): auto_PD_DBT == auto_PD_HG  (reference-free "trust" flag)
Primary endpoint: balanced-accuracy gap (agree vs disagree subset) on test, with a
patient-clustered bootstrap 95% CI (2000 resamples, seed=0). Null is valid.
"""
import csv, re, os, math, random
from collections import defaultdict

HERE = os.path.join(os.path.dirname(__file__), "..", "data", "lumiere")
RANO = os.path.join(HERE, "LUMIERE-ExpertRating-v202211.csv")
DBT  = os.path.join(HERE, "LUMIERE-pyradiomics-deepbratumia.csv")
HG   = os.path.join(HERE, "LUMIERE-pyradiomics-hdglioauto.csv")
REGION = "Contrast-enhancing"
POSTOP = {"Post-Op", "PD", "SD", "PR", "CR"}
MEASURABLE = {"PD", "SD", "PR", "CR"}
TH_REL, TH_ABS = 1.40, 1000.0

def load_rano():
    d = {}
    with open(RANO, encoding="utf-8", errors="replace") as f:
        r = csv.DictReader(f)
        rate_col = [c for c in r.fieldnames if c.startswith("Rating (")][0]
        for row in r:
            d[(row["Patient"], row["Date"])] = (row[rate_col] or "").strip()
    return d

def load_vol(fn):
    d = {}
    with open(fn, encoding="utf-8", errors="replace") as f:
        for row in csv.DictReader(f):
            if row["Label name"] == REGION:
                try: d[(row["Patient"], row["Time point"])] = float(row["original_shape_VoxelVolume"])
                except ValueError: pass
    return d

def week(tp):
    m = re.match(r"week-(\d+)", tp); return int(m.group(1)) if m else None

def auto_pd(v, nadir):
    if nadir is None: return None
    return int(v >= TH_REL * nadir and (v - nadir) >= TH_ABS)

def build(rano, vdbt, vhg):
    """Per patient, ordered post-op timepoints; emit eligible eval rows with per-tool auto_PD."""
    tp_by_pat = defaultdict(list)
    for (p, tp), rt in rano.items():
        w = week(tp)
        if w is None or rt not in POSTOP: continue
        if (p, tp) in vdbt and (p, tp) in vhg:
            tp_by_pat[p].append((w, tp, rt))
    rows = []
    for p, seq in tp_by_pat.items():
        seq.sort()
        for i, (w, tp, rt) in enumerate(seq):
            if rt not in MEASURABLE or i == 0:
                continue  # need >=1 prior post-op timepoint to define a nadir
            nd = min(vdbt[(p, s[1])] for s in seq[:i])
            nh = min(vhg[(p, s[1])] for s in seq[:i])
            apd = auto_pd(vdbt[(p, tp)], nd); aph = auto_pd(vhg[(p, tp)], nh)
            if apd is None or aph is None: continue
            rows.append(dict(patient=p, tp=tp,
                             auto_dbt=apd, auto_hg=aph,
                             agree=int(apd == aph),
                             expert_pd=int(rt == "PD")))
    return rows

def balanced_acc(sub, call="auto_dbt"):
    pos = [r for r in sub if r["expert_pd"] == 1]
    neg = [r for r in sub if r["expert_pd"] == 0]
    if not pos or not neg: return None
    sens = sum(r[call] == 1 for r in pos) / len(pos)
    spec = sum(r[call] == 0 for r in neg) / len(neg)
    return 0.5 * (sens + spec)

def main():
    rano = load_rano(); vdbt = load_vol(DBT); vhg = load_vol(HG)
    rows = build(rano, vdbt, vhg)

    # frozen patient split 50/50, seed=0
    pats = sorted({r["patient"] for r in rows})
    rng = random.Random(0); rng.shuffle(pats)
    half = len(pats) // 2
    calib = set(pats[:half]); test = set(pats[half:])
    test_rows = [r for r in rows if r["patient"] in test]

    n = len(test_rows)
    agree = [r for r in test_rows if r["agree"]]
    disag = [r for r in test_rows if not r["agree"]]
    pd_rate = sum(r["expert_pd"] for r in test_rows) / n
    print(f"Eligible eval timepoints: {len(rows)} total | test {n} (patients {len(test)})")
    print(f"Test expert-PD base rate: {pd_rate:.1%}")
    print(f"Tools AGREE: {len(agree)}/{n} ({len(agree)/n:.1%}) | DISAGREE: {len(disag)}/{n}")

    ba_all = balanced_acc(test_rows); ba_a = balanced_acc(agree); ba_d = balanced_acc(disag)
    def fmt(x): return "n/a" if x is None else f"{x:.3f}"
    print("\n--- PRIMARY: balanced accuracy of automated progression call vs expert RANO ---")
    print(f"  ALL test (single tool, no gating): {fmt(ba_all)}")
    print(f"  AGREE subset (reference-free trust): {fmt(ba_a)}")
    print(f"  DISAGREE subset (reference-free defer): {fmt(ba_d)}")
    gap = (ba_a - ba_d) if (ba_a is not None and ba_d is not None) else None
    print(f"  GAP (agree - disagree): {fmt(gap)}")

    # patient-clustered bootstrap CI on the gap
    if gap is not None:
        test_pats = sorted(test)
        by_pat = defaultdict(list)
        for r in test_rows: by_pat[r["patient"]].append(r)
        brng = random.Random(0); gaps = []
        for _ in range(2000):
            samp = [p for p in (test_pats[brng.randrange(len(test_pats))] for _ in test_pats)]
            rs = [r for p in samp for r in by_pat[p]]
            a = balanced_acc([r for r in rs if r["agree"]])
            d = balanced_acc([r for r in rs if not r["agree"]])
            if a is not None and d is not None: gaps.append(a - d)
        gaps.sort()
        lo = gaps[int(0.025 * len(gaps))]; hi = gaps[int(0.975 * len(gaps))]
        print(f"  95% patient-clustered bootstrap CI on gap: [{lo:+.3f}, {hi:+.3f}]  (n_boot={len(gaps)})")
        print(f"  => {'SIGNIFICANT (excludes 0)' if lo > 0 else 'NULL (CI includes 0)'}")

    # selective prediction: certify agree-pile, defer disagree-pile
    if ba_a is not None:
        cert_err = 1 - (sum(r['auto_dbt'] == r['expert_pd'] for r in agree) / len(agree))
        base_err = 1 - (sum(r['auto_dbt'] == r['expert_pd'] for r in test_rows) / n)
        print("\n--- Selective triage (certify where tools agree, defer where they disagree) ---")
        print(f"  coverage auto-certified: {len(agree)/n:.1%}")
        print(f"  raw error on certified pile: {cert_err:.1%} vs no-gating {base_err:.1%}")

if __name__ == "__main__":
    main()
