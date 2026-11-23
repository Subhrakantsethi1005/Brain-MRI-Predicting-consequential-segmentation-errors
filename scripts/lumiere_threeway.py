"""Does a THIRD independent voter sharpen the reference-free reliability flag?

The frozen 2-way flag is "do DeepBraTumIA (DBT) and HD-GLIO-AUTO (HG) make the same
RANO progression call?" Here we add OUR BraTS-trained segmenter (outputs of
scripts/lumiere_thirdvoter.py) as a third, architecturally-independent voter and ask:

  1) Reproduce the 2-way gap on the subset that also has a third-voter volume (fair base).
  2) 3-way unanimity flag: all three agree (certify) vs not (defer) -> balanced-acc gap.
  3) The sharpening test: among rows the 2-way flag CERTIFIES (DBT & HG agree), does the
     third voter's concordance split them into a cleaner (3/3) vs worse (2/3) pile? If the
     "DBT&HG agree but 3rd disagrees" pile has lower accuracy, the third voter is catching
     calls the 2-way flag wrongly certified.
  4) Coverage/accuracy trade-off: 2-way vs 3-way unanimous.

Same frozen definitions as lumiere_strengthen (nadir-based auto-PD, >=1.40x & >=1 mL,
balanced accuracy, patient-clustered bootstrap). Writes outputs/lumiere/threeway.json.
Honest by design: a null (third voter adds nothing) is a valid result.
"""
import os, csv, json, math, random
from collections import defaultdict
import sys
sys.path.insert(0, os.path.dirname(__file__))
from lumiere_strengthen import (load_rano, load_vol, week, balanced_acc,
                                NADIR_FLOOR, TH_ABS, DBT, HG)

HERE = os.path.join(os.path.dirname(__file__), "..", "data", "lumiere")
OUT = os.path.join(os.path.dirname(__file__), "..", "outputs", "lumiere")
TV = os.path.join(OUT, "thirdvoter_volumes.csv")
POSTOP = {"Post-Op", "PD", "SD", "PR", "CR"}; MEASURABLE = {"PD", "SD", "PR", "CR"}
TH = 1.40


def load_thirdvoter():
    """(patient, week) -> volume in mm^3 (et_ml * 1000), to match VoxelVolume units."""
    d = {}
    if not os.path.exists(TV):
        return d
    with open(TV, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            try:
                d[(row["patient"], row["week"])] = float(row["et_ml"]) * 1000.0
            except (ValueError, KeyError):
                pass
    return d


def build3(rano, vd, vh, vt):
    """Eligible rows that have DBT, HG AND third-voter volumes, with per-tool nadirs."""
    tp_by = defaultdict(list)
    for (p, tp), rt in rano.items():
        w = week(tp)
        if w is not None and rt in POSTOP and (p, tp) in vd and (p, tp) in vh and (p, tp) in vt:
            tp_by[p].append((w, tp, rt))
    rows = []
    for p, seq in tp_by.items():
        seq.sort()
        for i, (w, tp, rt) in enumerate(seq):
            if rt not in MEASURABLE or i == 0:
                continue
            prior = seq[:i]
            nd = max(min(vd[(p, s[1])] for s in prior), NADIR_FLOOR)
            nh = max(min(vh[(p, s[1])] for s in prior), NADIR_FLOOR)
            nt = max(min(vt[(p, s[1])] for s in prior), NADIR_FLOOR)
            rows.append(dict(patient=p, tp=tp, expert_pd=int(rt == "PD"),
                             vd=vd[(p, tp)], vh=vh[(p, tp)], vt=vt[(p, tp)],
                             nd=nd, nh=nh, nt=nt))
    return rows


def pd_call(V, nad, th=TH):
    return int(V >= th * nad and (V - nad) >= TH_ABS)


def calls(r, th=TH):
    return (pd_call(r["vd"], r["nd"], th), pd_call(r["vh"], r["nh"], th), pd_call(r["vt"], r["nt"], th))


def majority(r, th=TH):
    return int(sum(calls(r, th)) >= 2)


def boot_gap(rows, agree_fn, pred, nboot=2000, seed=0):
    by = defaultdict(list)
    for r in rows:
        by[r["patient"]].append(r)
    pats = sorted(by); rng = random.Random(seed); gaps = []
    for _ in range(nboot):
        samp = [pats[rng.randrange(len(pats))] for _ in pats]
        rs = [r for p in samp for r in by[p]]
        ag = [r for r in rs if agree_fn(r)]; dg = [r for r in rs if not agree_fn(r)]
        a = balanced_acc(ag, pred); d = balanced_acc(dg, pred)
        if a is not None and d is not None:
            gaps.append(a - d)
    gaps.sort()
    return (gaps[int(0.025 * len(gaps))], gaps[int(0.975 * len(gaps))]) if gaps else (None, None)


def main():
    rano = load_rano(); vd = load_vol(DBT); vh = load_vol(HG); vt = load_thirdvoter()
    print(f"third-voter volumes loaded: {len(vt)} (patient, week) keys")
    # key-alignment diagnostic
    kd = set(vd); kt = set(vt)
    print(f"keys shared DBT-and-3rd: {len(kd & kt)}  (DBT {len(kd)}, 3rd {len(kt)})")

    rows = build3(rano, vd, vh, vt)
    pats = sorted({r["patient"] for r in rows})
    res = {"n_rows": len(rows), "n_patients": len(pats)}
    if not rows:
        print("NO eligible 3-tool rows — check key alignment (week strings).");
        json.dump(res, open(os.path.join(OUT, "threeway.json"), "w"), indent=2); return

    predd = lambda r: pd_call(r["vd"], r["nd"])      # DBT caller, for comparability with frozen primary
    predm = lambda r: majority(r)                    # natural 3-voter decision

    print("=" * 72)
    print(f"Eligible rows with all THREE tools: n={len(rows)} / {len(pats)} patients "
          f"(expert-PD {sum(r['expert_pd'] for r in rows)/len(rows):.1%})")

    # (1) 2-way gap on this subset (baseline)
    ag2 = lambda r: calls(r)[0] == calls(r)[1]
    a = balanced_acc([r for r in rows if ag2(r)], predd)
    d = balanced_acc([r for r in rows if not ag2(r)], predd)
    lo, hi = boot_gap(rows, ag2, predd)
    res["two_way_DBTvsHG"] = dict(agree_frac=sum(ag2(r) for r in rows)/len(rows),
                                  ba_agree=a, ba_disagree=d, gap=(a-d), gap_ci=[lo, hi])
    print(f"\n(1) 2-WAY flag (DBT vs HG), DBT caller: agree {sum(ag2(r) for r in rows)/len(rows):.0%} | "
          f"BA agree {a:.3f} / disagree {d:.3f} | gap {a-d:+.3f} CI [{lo:+.3f},{hi:+.3f}]")

    # (2) 3-way unanimity, majority caller
    ag3 = lambda r: len(set(calls(r))) == 1
    a3 = balanced_acc([r for r in rows if ag3(r)], predm)
    d3 = balanced_acc([r for r in rows if not ag3(r)], predm)
    lo3, hi3 = boot_gap(rows, ag3, predm)
    res["three_way_unanimous"] = dict(agree_frac=sum(ag3(r) for r in rows)/len(rows),
                                      ba_agree=a3, ba_disagree=d3, gap=(a3-d3), gap_ci=[lo3, hi3])
    print(f"(2) 3-WAY unanimity (all 3 agree), majority caller: unanimous {sum(ag3(r) for r in rows)/len(rows):.0%} | "
          f"BA unanimous {a3:.3f} / split {d3:.3f} | gap {a3-d3:+.3f} CI [{lo3:+.3f},{hi3:+.3f}]")

    # (3) THE sharpening test: within DBT&HG-agree, does the 3rd voter split them?
    cert2 = [r for r in rows if ag2(r)]
    thirdalso = [r for r in cert2 if calls(r)[2] == calls(r)[0]]
    thirdnot = [r for r in cert2 if calls(r)[2] != calls(r)[0]]
    ba_all3 = balanced_acc(thirdalso, predd)
    ba_2not3 = balanced_acc(thirdnot, predd)
    # plain accuracy too (subsets may lack both classes for balanced acc)
    def acc(sub, pred): return sum(pred(r) == r["expert_pd"] for r in sub)/len(sub) if sub else None
    res["sharpening_within_2way_certified"] = dict(
        n_2way_cert=len(cert2),
        n_3of3=len(thirdalso), n_2of3=len(thirdnot),
        ba_3of3=ba_all3, ba_2way_but_3rd_disagrees=ba_2not3,
        acc_3of3=acc(thirdalso, predd), acc_2way_but_3rd_disagrees=acc(thirdnot, predd))
    print(f"\n(3) SHARPENING within the {len(cert2)} rows the 2-way flag CERTIFIES:")
    print(f"      3rd voter ALSO agrees (3/3): n={len(thirdalso)}  acc {acc(thirdalso,predd)} "
          f"BA {None if ba_all3 is None else round(ba_all3,3)}")
    print(f"      3rd voter DISAGREES (2/3):   n={len(thirdnot)}  acc {acc(thirdnot,predd)} "
          f"BA {None if ba_2not3 is None else round(ba_2not3,3)}")
    print("      -> if the 2/3 pile is LESS accurate, the third voter catches false certifications.")

    # (4) coverage/accuracy trade-off
    def cov_err(agree_fn, pred):
        cert = [r for r in rows if agree_fn(r)]
        return len(cert)/len(rows), (1 - acc(cert, pred)) if cert else None
    c2, e2 = cov_err(ag2, predd); c3, e3 = cov_err(ag3, predm)
    res["coverage_tradeoff"] = dict(two_way=dict(coverage=c2, raw_error=e2),
                                    three_way=dict(coverage=c3, raw_error=e3))
    print(f"\n(4) COVERAGE/ERROR: 2-way certify {c2:.0%} @ raw err {e2:.1%} | "
          f"3-way unanimous certify {c3:.0%} @ raw err {e3:.1%}")

    json.dump(res, open(os.path.join(OUT, "threeway.json"), "w"), indent=2)
    print(f"\nsaved -> outputs/lumiere/threeway.json")


if __name__ == "__main__":
    main()
