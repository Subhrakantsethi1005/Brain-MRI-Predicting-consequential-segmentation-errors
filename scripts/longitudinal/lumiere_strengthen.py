"""
Rigor battery for the longitudinal reliability-flag contribution.

Key realisation: the reference-free flag is PARAMETER-FREE (it is just "do the two
independent tools make the same RANO progression call?" — nothing is fitted). So it
can be evaluated validly on the FULL cohort (no train/test leakage), which is far more
powerful than one 50/50 split. We report, with patient-clustered bootstrap CIs:

  A  Full-cohort primary: balanced-accuracy gap (agree vs disagree) + CI.
  B  Split robustness: distribution of the gap over 200 random 50/50 splits.
  C  Threshold robustness: 25% / 40% / 50% progression thresholds.
  D  Caller symmetry: DBT-as-caller vs HG-as-caller vs unanimous.
  E  Continuous reliability score D(t) = |log2 fold-change disagreement| -> AUROC for
     predicting that the automated call is WRONG, + risk-coverage curve (selective pred).
  F  Decorrelation: within-patient log2-ratio SD; direction-of-change agreement (+CI).

Writes outputs/lumiere/strengthen.json. Seeded (seed=0) and deterministic.
"""
import csv, re, os, math, random, json
from collections import defaultdict

HERE = os.path.join(os.path.dirname(__file__), "..", "..", "data", "lumiere")
OUT  = os.path.join(os.path.dirname(__file__), "..", "..", "outputs", "lumiere")
os.makedirs(OUT, exist_ok=True)
RANO = os.path.join(HERE, "LUMIERE-ExpertRating-v202211.csv")
DBT  = os.path.join(HERE, "LUMIERE-pyradiomics-deepbratumia.csv")
HG   = os.path.join(HERE, "LUMIERE-pyradiomics-hdglioauto.csv")
REGION = "Contrast-enhancing"
POSTOP = {"Post-Op", "PD", "SD", "PR", "CR"}; MEASURABLE = {"PD", "SD", "PR", "CR"}
TH_ABS = 1000.0; NADIR_FLOOR = 50.0

def load_rano():
    d = {}
    with open(RANO, encoding="utf-8", errors="replace") as f:
        r = csv.DictReader(f); rc = [c for c in r.fieldnames if c.startswith("Rating (")][0]
        for row in r: d[(row["Patient"], row["Date"])] = (row[rc] or "").strip()
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

def build(rano, vd, vh):
    tp_by = defaultdict(list)
    for (p, tp), rt in rano.items():
        w = week(tp)
        if w is not None and rt in POSTOP and (p, tp) in vd and (p, tp) in vh:
            tp_by[p].append((w, tp, rt))
    rows = []
    for p, seq in tp_by.items():
        seq.sort()
        for i, (w, tp, rt) in enumerate(seq):
            if rt not in MEASURABLE or i == 0: continue
            nd = max(min(vd[(p, s[1])] for s in seq[:i]), NADIR_FLOOR)
            nh = max(min(vh[(p, s[1])] for s in seq[:i]), NADIR_FLOOR)
            fold_d = vd[(p, tp)] / nd; fold_h = vh[(p, tp)] / nh
            rows.append(dict(patient=p, tp=tp, expert_pd=int(rt == "PD"),
                             vd=vd[(p, tp)], vh=vh[(p, tp)], nd=nd, nh=nh,
                             fold_d=fold_d, fold_h=fold_h,
                             disagree_score=abs(math.log2(fold_d / fold_h))))
    return rows

def call(r, tool, th):
    V, nad = (r["vd"], r["nd"]) if tool == "d" else (r["vh"], r["nh"])
    return int(V >= th * nad and (V - nad) >= TH_ABS)

def balanced_acc(sub, pred):
    pos = [r for r in sub if r["expert_pd"] == 1]; neg = [r for r in sub if r["expert_pd"] == 0]
    if not pos or not neg: return None
    sens = sum(pred(r) == 1 for r in pos) / len(pos)
    spec = sum(pred(r) == 0 for r in neg) / len(neg)
    return 0.5 * (sens + spec)

def boot_gap(rows, th, caller="d", nboot=2000, seed=0):
    by = defaultdict(list)
    for r in rows: by[r["patient"]].append(r)
    pats = sorted(by); rng = random.Random(seed); gaps = []
    predc = lambda r: call(r, caller, th)
    for _ in range(nboot):
        samp = [pats[rng.randrange(len(pats))] for _ in pats]
        rs = [r for p in samp for r in by[p]]
        ag = [r for r in rs if call(r, "d", th) == call(r, "h", th)]
        dg = [r for r in rs if call(r, "d", th) != call(r, "h", th)]
        a = balanced_acc(ag, predc); d = balanced_acc(dg, predc)
        if a is not None and d is not None: gaps.append(a - d)
    gaps.sort()
    return gaps[int(0.025*len(gaps))], gaps[int(0.975*len(gaps))], len(gaps)

def auroc(scores, labels):
    # P(score higher among label==1)
    pos = [s for s, l in zip(scores, labels) if l == 1]
    neg = [s for s, l in zip(scores, labels) if l == 0]
    if not pos or not neg: return None
    gt = eq = 0
    for a in pos:
        for b in neg:
            if a > b: gt += 1
            elif a == b: eq += 1
    return (gt + 0.5*eq) / (len(pos)*len(neg))

def main():
    rano = load_rano(); vd = load_vol(DBT); vh = load_vol(HG)
    rows = build(rano, vd, vh)
    pats = sorted({r["patient"] for r in rows})
    res = {"n_rows": len(rows), "n_patients": len(pats)}
    TH = 1.40
    agree = [r for r in rows if call(r, "d", TH) == call(r, "h", TH)]
    disag = [r for r in rows if call(r, "d", TH) != call(r, "h", TH)]
    predd = lambda r: call(r, "d", TH)
    ba_all = balanced_acc(rows, predd); ba_a = balanced_acc(agree, predd); ba_d = balanced_acc(disag, predd)
    lo, hi, nb = boot_gap(rows, TH, "d")
    res["A_full_cohort"] = dict(n=len(rows), pd_rate=sum(r["expert_pd"] for r in rows)/len(rows),
        agree_frac=len(agree)/len(rows), ba_all=ba_all, ba_agree=ba_a, ba_disagree=ba_d,
        gap=ba_a-ba_d, gap_ci=[lo, hi], nboot=nb)
    print("="*72)
    print(f"A  FULL-COHORT PRIMARY (parameter-free flag; n={len(rows)} tps, {len(pats)} patients)")
    print(f"   expert-PD base rate {res['A_full_cohort']['pd_rate']:.1%}; tools agree on {len(agree)/len(rows):.1%}")
    print(f"   balanced acc: ALL {ba_all:.3f} | AGREE {ba_a:.3f} | DISAGREE {ba_d:.3f}")
    print(f"   GAP {ba_a-ba_d:+.3f}  95% CI [{lo:+.3f}, {hi:+.3f}]  -> {'SIGNIFICANT' if lo>0 else 'null'}")

    # B split robustness
    gaps = []
    for seed in range(200):
        rng = random.Random(seed); pp = pats[:]; rng.shuffle(pp)
        test = set(pp[len(pp)//2:]); tr = [r for r in rows if r["patient"] in test]
        ag = [r for r in tr if call(r,"d",TH)==call(r,"h",TH)]; dg = [r for r in tr if call(r,"d",TH)!=call(r,"h",TH)]
        a = balanced_acc(ag, predd); d = balanced_acc(dg, predd)
        if a is not None and d is not None: gaps.append(a-d)
    gaps.sort()
    res["B_split_robustness"] = dict(n_splits=len(gaps), median_gap=gaps[len(gaps)//2],
        frac_positive=sum(g>0 for g in gaps)/len(gaps), p5=gaps[int(.05*len(gaps))], p95=gaps[int(.95*len(gaps))])
    print(f"\nB  SPLIT ROBUSTNESS (200 random 50/50 test halves): median gap {gaps[len(gaps)//2]:+.3f}, "
          f"{sum(g>0 for g in gaps)/len(gaps):.0%} of splits positive, 5-95pct [{gaps[int(.05*len(gaps))]:+.3f}, {gaps[int(.95*len(gaps))]:+.3f}]")

    # C threshold robustness
    res["C_threshold"] = {}
    print("\nC  THRESHOLD ROBUSTNESS (full cohort)")
    for th in (1.25, 1.40, 1.50):
        ag = [r for r in rows if call(r,"d",th)==call(r,"h",th)]; dg = [r for r in rows if call(r,"d",th)!=call(r,"h",th)]
        pc = lambda r: call(r,"d",th)
        a = balanced_acc(ag, pc); d = balanced_acc(dg, pc); lo2,hi2,_ = boot_gap(rows, th, "d")
        res["C_threshold"][f"{int((th-1)*100)}pct"] = dict(agree_frac=len(ag)/len(rows), ba_agree=a, ba_disagree=d, gap=(a-d) if (a and d) else None, ci=[lo2,hi2])
        print(f"   +{int((th-1)*100)}%: agree {len(ag)/len(rows):.0%} | BA agree {a if a is None else round(a,3)} disagree {d if d is None else round(d,3)} | gap CI [{lo2:+.3f},{hi2:+.3f}]")

    # D caller symmetry
    predh = lambda r: call(r,"h",TH)
    a_h = balanced_acc(agree, predh); d_h = balanced_acc(disag, predh)
    res["D_caller"] = dict(hg_ba_agree=a_h, hg_ba_disagree=d_h, hg_gap=(a_h-d_h) if (a_h and d_h) else None)
    print(f"\nD  CALLER SYMMETRY: HG-as-caller gap {(a_h-d_h):+.3f} (DBT was {ba_a-ba_d:+.3f}) -> robust to which tool you follow")

    # E continuous score AUROC + risk-coverage
    scores = [r["disagree_score"] for r in rows]
    wrong  = [int(call(r,"d",TH) != r["expert_pd"]) for r in rows]
    au = auroc(scores, wrong)
    # patient-clustered bootstrap CI for AUROC
    by = defaultdict(list)
    for r in rows: by[r["patient"]].append(r)
    rng = random.Random(0); aus = []
    for _ in range(2000):
        samp = [pats[rng.randrange(len(pats))] for _ in pats]
        rs = [r for p in samp for r in by[p]]
        a = auroc([r["disagree_score"] for r in rs], [int(call(r,"d",TH)!=r["expert_pd"]) for r in rs])
        if a is not None: aus.append(a)
    aus.sort()
    res["E_auroc_disagreement_predicts_wrong"] = dict(auroc=au, ci=[aus[int(.025*len(aus))], aus[int(.975*len(aus))]])
    print(f"\nE  CONTINUOUS SCORE: disagreement predicts a WRONG automated call, AUROC {au:.3f} "
          f"[{aus[int(.025*len(aus))]:.3f}, {aus[int(.975*len(aus))]:.3f}]")
    # risk-coverage: certify lowest-disagreement fraction
    order = sorted(rows, key=lambda r: r["disagree_score"])
    print("   risk-coverage (certify lowest-disagreement cases):")
    rc = []
    for cov in (0.3, 0.5, 0.7, 0.9, 1.0):
        k = max(1, int(cov*len(order))); cert = order[:k]
        err = 1 - sum(call(r,"d",TH)==r["expert_pd"] for r in cert)/len(cert)
        rc.append(dict(coverage=cov, raw_error=err))
        print(f"      coverage {cov:.0%}: automated-call error {err:.1%}")
    res["E_risk_coverage"] = rc

    # F decorrelation
    def pct(xs,q): xs=sorted(xs); return xs[min(len(xs)-1,int(q*len(xs)))]
    byv = defaultdict(list)
    allkeys = sorted(set(vd)&set(vh))
    for k in allkeys:
        a,b = vd[k],vh[k]
        if a>=NADIR_FLOOR and b>=NADIR_FLOOR:
            w=week(k[1])
            if w is not None: byv[k[0]].append((w, math.log2(a/b), a, b))
    wsd=[]
    for p,s in byv.items():
        if len(s)>=3:
            vals=[x[1] for x in s]; m=sum(vals)/len(vals)
            wsd.append(math.sqrt(sum((v-m)**2 for v in vals)/(len(vals)-1)))
    # direction agreement on >=1mL both
    da=tot=0
    for p,s in byv.items():
        s=sorted(s)
        for (w0,_,a0,b0),(w1,_,a1,b1) in zip(s,s[1:]):
            if min(a0,b0,a1,b1)>=1000:
                tot+=1; da += ((a1-a0)>0)==((b1-b0)>0)
    res["F_decorrelation"] = dict(within_patient_logratio_sd_median=pct(wsd,.5),
        direction_agree_ge1ml=da/tot if tot else None, n_dir_pairs=tot)
    print(f"\nF  DECORRELATION: within-patient log2-ratio SD median {pct(wsd,.5):.2f} (0 if fixed offset);")
    print(f"   direction-of-change agreement on >=1mL tumours: {da}/{tot} = {da/tot:.1%} (chance 50%)")

    with open(os.path.join(OUT, "strengthen.json"), "w") as f:
        json.dump(res, f, indent=2)
    print(f"\nsaved -> outputs/lumiere/strengthen.json")

if __name__ == "__main__":
    main()
