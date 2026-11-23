"""
LUMIERE diagnostic — is the thesis's core signal actually in the data?

The "errors have memory" claim decomposes into measurable sub-claims, none of which
need ground-truth masks (LUMIERE ships none) or the full RANO algorithm:

  C1 (static disagreement): the two independent tools disagree a lot on enhancing volume.
  C2 (DECORRELATION = the novel bit): that disagreement is NOT a fixed per-patient offset
      -- the log-ratio log(V_DBT/V_HG) varies within a patient across time. If it were a
      constant offset, errors would CANCEL in the change; variation => they COMPOUND.
  C3 (consequence on the CHANGE): because of C2, the tools often disagree even on the
      DIRECTION of volume change between consecutive scans.
  C4 (is it just noise on tiny tumours?): check whether disagreement concentrates at
      small volumes (then it is boring) or persists at clinically large volumes.

Pure analysis of the 34 MB CSV core. Reports numbers honestly, no thresholds tuned.
"""
import csv, re, os, math
from collections import defaultdict

HERE = os.path.join(os.path.dirname(__file__), "..", "data", "lumiere")
DBT  = os.path.join(HERE, "LUMIERE-pyradiomics-deepbratumia.csv")
HG   = os.path.join(HERE, "LUMIERE-pyradiomics-hdglioauto.csv")

def load_vol(fn, region="Contrast-enhancing"):
    d = {}
    with open(fn, encoding="utf-8", errors="replace") as f:
        for row in csv.DictReader(f):
            if row["Label name"] == region:
                try:
                    d[(row["Patient"], row["Time point"])] = float(row["original_shape_VoxelVolume"])
                except ValueError:
                    pass
    return d

def week(tp):
    m = re.match(r"week-(\d+)", tp); return int(m.group(1)) if m else None

def pct(xs, q):
    xs = sorted(xs); i = min(len(xs)-1, max(0, int(q*len(xs))))
    return xs[i]

def mean(xs): return sum(xs)/len(xs) if xs else float("nan")
def sd(xs):
    if len(xs) < 2: return float("nan")
    m = mean(xs); return math.sqrt(sum((x-m)**2 for x in xs)/(len(xs)-1))

def main():
    vdbt = load_vol(DBT); vhg = load_vol(HG)
    keys = sorted(set(vdbt) & set(vhg))
    EPS = 50.0  # mm^3 floor so log-ratio is defined (0.05 mL)

    # --- C1: static disagreement (log2 ratio), all timepoints with both tools ---
    log2r = []
    big = []  # disagreement restricted to clinically sizeable tumours (>=1 mL in BOTH)
    for k in keys:
        a, b = vdbt[k], vhg[k]
        if a < EPS or b < EPS:
            continue
        lr = math.log2(a/b)
        log2r.append(lr)
        if a >= 1000 and b >= 1000:
            big.append(abs(lr))
    absr = [abs(x) for x in log2r]
    print(f"C1  STATIC tool disagreement on enhancing volume (n={len(log2r)} timepoints, both>=0.05mL)")
    print(f"    |log2(DBT/HG)|: median {pct(absr,.5):.2f}  (={2**pct(absr,.5):.2f}x)   "
          f"90th pct {pct(absr,.9):.2f} (={2**pct(absr,.9):.2f}x)")
    frac2x = sum(x>=1 for x in absr)/len(absr)
    print(f"    fraction of timepoints where tools differ by >=2x: {frac2x:.1%}")
    print(f"    even on tumours >=1mL in BOTH (n={len(big)}): median |log2| {pct(big,.5):.2f} "
          f"(={2**pct(big,.5):.2f}x), >=2x in {sum(x>=1 for x in big)/len(big):.1%}")

    # --- C2: decorrelation = within-patient variability of the log-ratio ---
    by_pat = defaultdict(list)
    for k in keys:
        a, b = vdbt[k], vhg[k]
        if a < EPS or b < EPS: continue
        w = week(k[1])
        if w is not None:
            by_pat[k[0]].append((w, math.log2(a/b)))
    within_sd = []
    for p, seq in by_pat.items():
        if len(seq) >= 3:
            within_sd.append(sd([lr for _, lr in seq]))
    print(f"\nC2  DECORRELATION: within-patient SD of log2-ratio (patients with >=3 tps, n={len(within_sd)})")
    print(f"    median within-patient SD: {pct(within_sd,.5):.2f}  (a fixed offset would give ~0)")
    print(f"    => if >~0.3, the per-scan error is NOT a constant offset; it does not cancel in the change")

    # --- C3: do tools agree on DIRECTION of consecutive change? ---
    agree_dir = tot = 0
    both_big_change = 0
    for p, seq in by_pat.items():
        seq2 = sorted(set((w,) for w, _ in seq))  # unique weeks
    # recompute with raw volumes for direction
    by_pat_vol = defaultdict(list)
    for k in keys:
        a, b = vdbt[k], vhg[k]
        w = week(k[1])
        if w is not None and a >= EPS and b >= EPS:
            by_pat_vol[k[0]].append((w, a, b))
    for p, seq in by_pat_vol.items():
        seq.sort()
        for (w0, a0, b0), (w1, a1, b1) in zip(seq, seq[1:]):
            da, db = a1-a0, b1-b0
            tot += 1
            if (da > 0) == (db > 0):
                agree_dir += 1
    print(f"\nC3  Agreement on DIRECTION of consecutive volume change (n={tot} pairs)")
    print(f"    tools agree tumour grew-vs-shrank: {agree_dir}/{tot} = {agree_dir/tot:.1%}")
    print(f"    (if errors were systematic/cancelling, this should be near 100%)")

if __name__ == "__main__":
    main()
