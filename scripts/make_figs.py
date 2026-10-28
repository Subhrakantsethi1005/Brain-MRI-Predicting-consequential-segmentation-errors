"""Generate paper figures from risk_msd outputs. Honest, feasibility-run numbers."""
import csv, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = r"C:\Users\SUBHRAKANT SETHI\Brain-MRI-Predicting-consequential-segmentation-errors"
OUT = os.path.join(ROOT, "docs", "paper", "figures")
os.makedirs(OUT, exist_ok=True)

def read(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))

test = read(os.path.join(ROOT, "outputs", "risk_msd", "risk_test_report.csv"))
comp = read(os.path.join(ROOT, "outputs", "risk_msd", "risk_test_comparisons.csv"))

FAM_ORDER = ["volume_only", "best_single", "uncertainty", "disagreement",
             "boundary_morphology", "combined"]
FAM_LABEL = {"volume_only": "volume_only\n(baseline)", "best_single": "best_single\n(baseline)",
             "uncertainty": "uncertainty", "disagreement": "disagreement",
             "boundary_morphology": "boundary_\nmorphology", "combined": "combined"}

# --- Figure 1: AUROC by family on the primary endpoint (logistic; best_single as-is) ---
rows = {}
for r in test:
    if r["endpoint"] != "primary":
        continue
    if r["group"] == "best_single" or r["model"] == "logistic":
        rows[r["group"]] = r
xs = [f for f in FAM_ORDER if f in rows]
auroc = [float(rows[f]["auroc"]) for f in xs]
lo = [float(rows[f]["auroc"]) - float(rows[f]["auroc_lo"]) for f in xs]
hi = [float(rows[f]["auroc_hi"]) - float(rows[f]["auroc"]) for f in xs]
colors = ["#9aa0a6" if f in ("volume_only", "best_single") else "#1f77b4" for f in xs]

fig, ax = plt.subplots(figsize=(7.2, 4.0))
pos = range(len(xs))
ax.bar(pos, auroc, yerr=[lo, hi], color=colors, capsize=4, width=0.62,
       error_kw=dict(ecolor="#333", lw=1.1))
ax.set_xticks(list(pos))
ax.set_xticklabels([FAM_LABEL[f] for f in xs], fontsize=8.5)
ax.set_ylabel("AUROC (test, 95% CI)")
ax.set_ylim(0.5, 1.0)
ax.axhline(0.5, color="#bbb", lw=0.8, ls=":")
ax.set_title("Primary endpoint (WT vol. error \u2265 25% & \u2265 1 mL), n=97, 34 pos.\n"
             "Candidates (blue) vs. baselines (grey) \u2014 no significant separation",
             fontsize=9)
for i, v in enumerate(auroc):
    ax.text(i, v + hi[i] + 0.012, f"{v:.3f}", ha="center", fontsize=8)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "fig_auroc_primary.png"), dpi=200)
plt.close(fig)

# --- Figure 2: forest plot of candidate - baseline dAUROC across endpoints ---
EP_ORDER = ["primary", "WT_rel40", "WT_dice80"]
EP_LABEL = {"primary": "Primary (WT \u226525% & \u22651mL)",
            "WT_rel40": "WT \u226540% vol. error",
            "WT_dice80": "WT Dice < 0.80"}
want = [("boundary_morphology", "best_single"), ("boundary_morphology", "volume_only"),
        ("disagreement", "best_single"), ("disagreement", "volume_only"),
        ("combined", "volume_only")]
labels, diffs, los, his, sig = [], [], [], [], []
yticks = []
y = 0
rowmap = {(r["endpoint"], r["candidate"], r["reference"]): r for r in comp}
for ep in EP_ORDER:
    for cand, ref in want:
        r = rowmap.get((ep, cand, ref))
        if not r:
            continue
        labels.append(f"{cand} \u2212 {ref}")
        diffs.append(float(r["diff"]))
        los.append(float(r["diff"]) - float(r["lo"]))
        his.append(float(r["hi"]) - float(r["diff"]))
        sig.append(float(r["p"]) < 0.05)
        yticks.append((y, ep))
        y += 1
    y += 0.8  # gap between endpoint blocks

fig, ax = plt.subplots(figsize=(7.6, 6.2))
ys = [t[0] for t in yticks]
cols = ["#2ca02c" if s else "#9aa0a6" for s in sig]
ax.errorbar(diffs, ys, xerr=[los, his], fmt="o", ecolor="#666", elinewidth=1.2,
            capsize=3, mfc="w", mec="none", ls="none", zorder=1)
ax.scatter(diffs, ys, c=cols, s=42, zorder=2)
ax.axvline(0, color="#d62728", lw=1.0, ls="--")
ax.set_yticks(ys)
ax.set_yticklabels(labels, fontsize=8)
ax.invert_yaxis()
ax.set_xlabel("\u0394 AUROC (candidate \u2212 baseline), paired bootstrap 95% CI")
# endpoint section labels
seen = set()
for yv, ep in yticks:
    if ep not in seen:
        ax.text(ax.get_xlim()[0], yv - 0.45, EP_LABEL[ep], fontsize=8.5,
                fontweight="bold", color="#333")
        seen.add(ep)
ax.set_title("Candidate feature families vs. baselines, by endpoint (test)\n"
             "green = CI excludes 0 (p<0.05); grey = not significant", fontsize=9)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "fig_forest_comparisons.png"), dpi=200)
plt.close(fig)

print("wrote:", sorted(os.listdir(OUT)))
