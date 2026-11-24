"""Export a compact JSON for the interactive demo: per-patient enhancing-tumour
volume trajectories from both tools, expert RANO ratings, nadir-based automated
progression calls, and the reference-free agreement flag. Plus headline stats."""
import os, json
from collections import defaultdict
import sys
sys.path.insert(0, os.path.dirname(__file__))
from lumiere_strengthen import (load_rano, load_vol, DBT, HG, week, call, build,
                                balanced_acc, NADIR_FLOOR)

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "outputs", "lumiere")
TH = 1.40
POSTOP = {"Post-Op", "PD", "SD", "PR", "CR"}; MEAS = {"PD", "SD", "PR", "CR"}

rano = load_rano(); vd = load_vol(DBT); vh = load_vol(HG)
rows = build(rano, vd, vh)  # eligible eval rows with flag info

# index eval rows by (patient, tp) for flag lookup
evro = {(r["patient"], r["tp"]): r for r in rows}

patients = {}
for (p, tp), rt in rano.items():
    w = week(tp)
    if w is None or (p, tp) not in vd or (p, tp) not in vh:
        continue
    patients.setdefault(p, []).append((w, tp, rt))

out_pat = {}
for p, seq in patients.items():
    seq.sort()
    # need at least 2 post-op timepoints to be interesting
    tps = []
    for w, tp, rt in seq:
        er = evro.get((p, tp))
        rec = dict(week=w, label=rt,
                   vd=round(vd[(p, tp)] / 1000.0, 2),   # mL
                   vh=round(vh[(p, tp)] / 1000.0, 2))
        if er is not None:
            rec.update(auto_d=er["__d"] if "__d" in er else call(er, "d", TH),
                       auto_h=call(er, "h", TH),
                       agree=bool(call(er, "d", TH) == call(er, "h", TH)),
                       expert_pd=er["expert_pd"])
        tps.append(rec)
    if sum(1 for t in tps if t["label"] in POSTOP) >= 2:
        out_pat[p] = tps

# headline summary (recompute the robust ones; pull split stats if present)
predd = lambda r: call(r, "d", TH)
agree = [r for r in rows if call(r, "d", TH) == call(r, "h", TH)]
disag = [r for r in rows if call(r, "d", TH) != call(r, "h", TH)]
# direction agreement >=1mL
byv = defaultdict(list)
for k in sorted(set(vd) & set(vh)):
    a, b = vd[k], vh[k]; w = week(k[1])
    if w is not None and a >= NADIR_FLOOR and b >= NADIR_FLOOR:
        byv[k[0]].append((w, a, b))
da = tot = 0
for p, s in byv.items():
    s.sort()
    for (w0, a0, b0), (w1, a1, b1) in zip(s, s[1:]):
        if min(a0, b0, a1, b1) >= 1000:
            tot += 1; da += ((a1 - a0) > 0) == ((b1 - b0) > 0)

summary = dict(
    n_patients_total=91, n_patients_shown=len(out_pat),
    n_eval=len(rows), agree_frac=round(len(agree) / len(rows), 3),
    ba_agree=round(balanced_acc(agree, predd), 3),
    ba_disagree=round(balanced_acc(disag, predd), 3),
    ba_all=round(balanced_acc(rows, predd), 3),
    dir_agree_pct=round(100 * da / tot, 1), dir_pairs=tot,
)
# try to enrich from strengthen.json
try:
    sj = json.load(open(os.path.join(OUT, "strengthen.json")))
    summary["splits_positive_pct"] = 100 * sj["B_split_robustness"]["frac_positive"]
    summary["gap"] = round(sj["A_full_cohort"]["gap"], 3)
    summary["gap_ci"] = [round(x, 3) for x in sj["A_full_cohort"]["gap_ci"]]
    summary["auroc_score"] = round(sj["E_auroc_disagreement_predicts_wrong"]["auroc"], 3)
except Exception:
    pass

data = dict(summary=summary, patients=out_pat)
os.makedirs(OUT, exist_ok=True)
path = os.path.join(OUT, "demo_data.json")
json.dump(data, open(path, "w"), separators=(",", ":"))
print(f"wrote {path}  ({os.path.getsize(path)/1024:.0f} KB)  patients={len(out_pat)}  eval_rows={len(rows)}")
print("summary:", json.dumps(summary, indent=2))
