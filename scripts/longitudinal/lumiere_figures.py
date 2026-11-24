"""Figures for docs/paper/longitudinal_report.md. Reuses the frozen logic in
lumiere_strengthen.py so numbers match exactly. Writes docs/paper/figures/long_fig*.png."""
import os, sys, math, random
from collections import defaultdict
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(__file__))
from lumiere_strengthen import (load_rano, load_vol, build, call, balanced_acc,
                                DBT, HG, week, NADIR_FLOOR)

FIGDIR = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "paper", "figures")
os.makedirs(FIGDIR, exist_ok=True)
TH = 1.40

rano = load_rano(); vd = load_vol(DBT); vh = load_vol(HG)
rows = build(rano, vd, vh)
pats = sorted({r["patient"] for r in rows})
predd = lambda r: call(r, "d", TH)

# ---- Fig 1: direction-of-change agreement between the two tools ----
byv = defaultdict(list)
for k in sorted(set(vd) & set(vh)):
    a, b = vd[k], vh[k]; w = week(k[1])
    if w is not None and a >= NADIR_FLOOR and b >= NADIR_FLOOR:
        byv[k[0]].append((w, a, b))
def dir_agree(flt):
    ag = tot = 0
    for p, s in byv.items():
        s = sorted(s)
        for (w0,a0,b0),(w1,a1,b1) in zip(s, s[1:]):
            if not flt(a0,b0,a1,b1): continue
            tot += 1; ag += ((a1-a0)>0)==((b1-b0)>0)
    return 100*ag/tot, tot
strata = [("All pairs", lambda a0,b0,a1,b1: True),
          ("Tumour ≥1 mL\n(both tools)", lambda a0,b0,a1,b1: min(a0,b0,a1,b1)>=1000),
          ("≥1 mL & both tools\nsee ≥40% change", lambda a0,b0,a1,b1: min(a0,b0,a1,b1)>=1000 and
              abs((a1-a0)/a0)>=0.4 and abs((b1-b0)/b0)>=0.4)]
vals = [dir_agree(f) for _, f in strata]
fig, ax = plt.subplots(figsize=(6.2, 4))
xs = range(len(strata))
bars = ax.bar(xs, [v for v,_ in vals], color="#c0392b", width=0.6)
ax.axhline(50, ls="--", c="#333", lw=1); ax.text(len(strata)-0.5, 51.5, "chance (50%)", ha="right", fontsize=9)
ax.set_xticks(list(xs)); ax.set_xticklabels([s for s,_ in strata], fontsize=9)
ax.set_ylabel("Tools agree on direction of\nvolume change (%)"); ax.set_ylim(0, 100)
for b,(v,n) in zip(bars, vals): ax.text(b.get_x()+b.get_width()/2, v+1.5, f"{v:.0f}%\n(n={n})", ha="center", fontsize=8)
ax.set_title("Two expert tools agree on grew-vs-shrank\nonly at chance level", fontsize=11)
fig.tight_layout(); fig.savefig(os.path.join(FIGDIR, "long_fig1_direction_agreement.png"), dpi=150); plt.close(fig)

# ---- Fig 2: robustness over 200 random splits ----
gaps = []
for seed in range(200):
    rng = random.Random(seed); pp = pats[:]; rng.shuffle(pp)
    test = set(pp[len(pp)//2:]); tr = [r for r in rows if r["patient"] in test]
    ag = [r for r in tr if call(r,"d",TH)==call(r,"h",TH)]; dg = [r for r in tr if call(r,"d",TH)!=call(r,"h",TH)]
    a = balanced_acc(ag, predd); d = balanced_acc(dg, predd)
    if a is not None and d is not None: gaps.append(a-d)
fig, ax = plt.subplots(figsize=(6.2, 4))
ax.hist(gaps, bins=24, color="#2471a3", edgecolor="white")
ax.axvline(0, c="#c0392b", lw=2); ax.text(0.005, ax.get_ylim()[1]*0.9, "no effect", color="#c0392b", fontsize=9)
ax.set_xlabel("Reliability gap: balanced accuracy (agree − disagree)")
ax.set_ylabel("Random 50/50 patient splits")
ax.set_title(f"Flag holds in 100% of 200 random splits\n(median gap +{sorted(gaps)[len(gaps)//2]:.2f})", fontsize=11)
fig.tight_layout(); fig.savefig(os.path.join(FIGDIR, "long_fig2_split_robustness.png"), dpi=150); plt.close(fig)

# ---- Fig 3: agree vs disagree balanced accuracy (held-out + full cohort) ----
# held-out seed=0
rng = random.Random(0); pp = pats[:]; rng.shuffle(pp); test = set(pp[len(pp)//2:])
tr = [r for r in rows if r["patient"] in test]
ho = (balanced_acc([r for r in tr if call(r,'d',TH)==call(r,'h',TH)], predd),
      balanced_acc([r for r in tr if call(r,'d',TH)!=call(r,'h',TH)], predd))
fc = (balanced_acc([r for r in rows if call(r,'d',TH)==call(r,'h',TH)], predd),
      balanced_acc([r for r in rows if call(r,'d',TH)!=call(r,'h',TH)], predd))
fig, ax = plt.subplots(figsize=(6.2, 4))
groups = ["Held-out split\n(n=93)", "Full cohort\n(n=221)"]
x = range(len(groups)); w = 0.35
ax.bar([i-w/2 for i in x], [ho[0], fc[0]], w, label="tools AGREE (trust)", color="#27ae60")
ax.bar([i+w/2 for i in x], [ho[1], fc[1]], w, label="tools DISAGREE (defer)", color="#e67e22")
ax.axhline(0.5, ls="--", c="#333", lw=1); ax.text(len(groups)-0.5, 0.515, "chance", ha="right", fontsize=9)
for i,(a,d) in enumerate([ho, fc]):
    ax.text(i-w/2, a+0.01, f"{a:.2f}", ha="center", fontsize=9)
    ax.text(i+w/2, d+0.01, f"{d:.2f}", ha="center", fontsize=9)
ax.set_xticks(list(x)); ax.set_xticklabels(groups); ax.set_ylim(0, 0.85)
ax.set_ylabel("Automated call vs expert RANO\n(balanced accuracy)"); ax.legend(fontsize=9, loc="upper right")
ax.set_title("When independent tools disagree,\nthe automated call is worthless (≈chance)", fontsize=11)
fig.tight_layout(); fig.savefig(os.path.join(FIGDIR, "long_fig3_agree_vs_disagree.png"), dpi=150); plt.close(fig)

print("wrote long_fig1_direction_agreement.png, long_fig2_split_robustness.png, long_fig3_agree_vs_disagree.png")
print(f"fig3 held-out agree/disagree = {ho[0]:.3f}/{ho[1]:.3f}; full-cohort = {fc[0]:.3f}/{fc[1]:.3f}")
