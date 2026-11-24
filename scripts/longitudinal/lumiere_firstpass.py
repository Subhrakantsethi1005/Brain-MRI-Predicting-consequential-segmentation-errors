"""
LUMIERE first-pass experiment — the "errors have memory" thesis, simplest form.

Idea: a tumour-volume CHANGE between two timepoints is trustworthy not when each
scan is well-segmented, but when two architecturally-independent segmenters make
the SAME decision. We use the two tools LUMIERE ships (DeepBraTumIA, HD-GLIO-AUTO)
as the independent pair, the enhancing-tumour volume as the measurement, and the
expert RANO rating as the clinical ground truth for the decision.

Falsifiable prediction: on consecutive follow-up pairs where the two tools AGREE on
the progression call, that call matches the expert far more often than on pairs where
they DISAGREE. If so, "defer when the tools disagree" is a reference-free reliability
flag — no ground truth needed.

Reads only the 34 MB CSV core in data/lumiere/. Honest, pre-analysis sanity script
(NOT the frozen pre-registered endpoint; this is exploration to see if signal exists).
"""
import csv, re, os
from collections import defaultdict

HERE = os.path.join(os.path.dirname(__file__), "..", "..", "data", "lumiere")
RANO = os.path.join(HERE, "LUMIERE-ExpertRating-v202211.csv")
DBT  = os.path.join(HERE, "LUMIERE-pyradiomics-deepbratumia.csv")
HG   = os.path.join(HERE, "LUMIERE-pyradiomics-hdglioauto.csv")

MEASURABLE = {"PD", "SD", "PR", "CR"}        # follow-up response categories
PROGRESSION_TH = 0.40                        # RANO-2.0-style enhancing-volume increase
MIN_PREV_MM3 = 200.0                         # need a non-trivial baseline to form a ratio

def load_rano():
    d = {}
    with open(RANO, encoding="utf-8", errors="replace") as f:
        r = csv.DictReader(f)
        rate_col = [c for c in r.fieldnames if c.startswith("Rating (")][0]
        for row in r:
            d[(row["Patient"], row["Date"])] = (row[rate_col] or "").strip()
    return d

def load_vol(fn, region="Contrast-enhancing"):
    """(patient, timepoint) -> enhancing VoxelVolume in mm^3."""
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
    m = re.match(r"week-(\d+)", tp)
    return int(m.group(1)) if m else None

def build_pairs(rano, vdbt, vhg):
    """Consecutive measurable follow-up pairs with both tools' enhancing volumes."""
    by_pat = defaultdict(list)
    for (p, tp), rt in rano.items():
        if rt in MEASURABLE and week(tp) is not None:
            if (p, tp) in vdbt and (p, tp) in vhg:
                by_pat[p].append((week(tp), tp, rt))
    pairs = []
    for p, tps in by_pat.items():
        tps.sort()
        for (w0, t0, _), (w1, t1, rt1) in zip(tps, tps[1:]):
            pairs.append(dict(patient=p, t_prev=t0, t=t1, rating=rt1,
                              dbt0=vdbt[(p, t0)], dbt1=vdbt[(p, t1)],
                              hg0=vhg[(p, t0)], hg1=vhg[(p, t1)]))
    return pairs

def rel_change(v0, v1):
    if v0 < MIN_PREV_MM3:
        return None
    return (v1 - v0) / v0

def main():
    rano = load_rano()
    vdbt = load_vol(DBT); vhg = load_vol(HG)
    pairs = build_pairs(rano, vdbt, vhg)

    rows = []
    for pr in pairs:
        cd = rel_change(pr["dbt0"], pr["dbt1"])
        ch = rel_change(pr["hg0"], pr["hg1"])
        if cd is None or ch is None:
            continue
        auto_dbt = int(cd >= PROGRESSION_TH)
        auto_hg  = int(ch >= PROGRESSION_TH)
        expert_pd = int(pr["rating"] == "PD")
        rows.append(dict(agree=int(auto_dbt == auto_hg),
                         auto_dbt=auto_dbt, auto_hg=auto_hg,
                         expert_pd=expert_pd))

    n = len(rows)
    print(f"Usable consecutive follow-up pairs (both tools, baseline>={MIN_PREV_MM3/1000:.1f}mL): {n}")
    pd_rate = sum(r["expert_pd"] for r in rows) / n
    print(f"Expert-PD rate among these pairs: {pd_rate:.1%}")

    agree = [r for r in rows if r["agree"]]
    disag = [r for r in rows if not r["agree"]]
    print(f"\nTools AGREE on progression call: {len(agree)}/{n} ({len(agree)/n:.1%})")
    print(f"Tools DISAGREE:                  {len(disag)}/{n} ({len(disag)/n:.1%})")

    def acc(subset):
        """Accuracy of the (DBT) auto call vs expert-PD on a subset."""
        if not subset: return float("nan"), 0
        c = sum(int(r["auto_dbt"] == r["expert_pd"]) for r in subset)
        return c / len(subset), len(subset)

    # On agree-subset both tools give the same call, so either tool = the agreed call.
    a_acc, _ = acc(agree)
    d_acc, _ = acc(disag)
    all_acc, _ = acc(rows)
    print(f"\n--- HEADLINE: reliability of the automated progression call vs expert ---")
    print(f"Accuracy, ALL pairs (single tool, no gating):      {all_acc:.1%}")
    print(f"Accuracy on AGREE pile  (reference-free 'trust'):  {a_acc:.1%}")
    print(f"Accuracy on DISAGREE pile (reference-free 'defer'):{d_acc:.1%}")
    print(f"\nIf we DEFER the disagree pile to an expert and auto-certify the agree pile:")
    print(f"  fraction auto-certified: {len(agree)/n:.1%} at accuracy {a_acc:.1%}")
    print(f"  (coin-flip reference for the deferred pile would be ~{max(pd_rate,1-pd_rate):.1%})")

if __name__ == "__main__":
    main()
