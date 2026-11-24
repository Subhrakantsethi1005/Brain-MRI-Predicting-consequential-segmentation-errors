"""Figure for Section 4.6 (conformal guarantee). Reads outputs/lumiere/conformal.json
so numbers match the analysis exactly. Writes docs/paper/figures/long_fig6_conformal.png."""
import os, json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "outputs", "lumiere")
FIGDIR = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "paper", "figures")
os.makedirs(FIGDIR, exist_ok=True)

c = json.load(open(os.path.join(OUT, "conformal.json")))
alphas = [0.05, 0.10, 0.20]
keys = ["alpha_0.05", "alpha_0.1", "alpha_0.2"]
fnr = [c["robustness"][k]["mean_test_fnr"] for k in keys]
cov = [c["robustness"][k]["mean_coverage"] for k in keys]
x = range(len(alphas))
xl = [f"{a:.0%}" for a in alphas]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.4, 3.5))

# (a) guarantee: realised miss-rate vs target alpha
ax1.bar(x, fnr, width=0.55, color="#2c7fb8")
ax1.plot(x, alphas, "o--", color="#c0392b", lw=1.5, label="target (guarantee)")
for i, (f, a) in enumerate(zip(fnr, alphas)):
    ax1.text(i, f + 0.006, f"{f:.1%}", ha="center", fontsize=8)
ax1.set_xticks(list(x)); ax1.set_xticklabels(xl)
ax1.set_ylim(0, 0.26)
ax1.set_xlabel("target max miss-rate  (alpha)")
ax1.set_ylabel("mean realised missed-progression rate")
ax1.set_title("Guarantee holds: realised miss-rate\ntracks the target (200 patient splits)", fontsize=10)
ax1.legend(fontsize=8, loc="upper left")

# (b) coverage bought at each guarantee level
ax2.bar(x, cov, width=0.55, color="#31a354")
for i, v in enumerate(cov):
    ax2.text(i, v + 0.006, f"{v:.0%}", ha="center", fontsize=8)
ax2.set_xticks(list(x)); ax2.set_xticklabels(xl)
ax2.set_ylim(0, 0.30)
ax2.set_xlabel("target max miss-rate  (alpha)")
ax2.set_ylabel("mean auto-cleared share (coverage)")
ax2.set_title("Coverage is modest, ceiled by the\n80% progression base rate of the cohort", fontsize=10)

fig.tight_layout()
fig.savefig(os.path.join(FIGDIR, "long_fig6_conformal.png"), dpi=150)
plt.close(fig)
print("wrote long_fig6_conformal.png")
print(f"  mean FNR {[round(f,3) for f in fnr]} vs alpha {alphas}; coverage {[round(v,3) for v in cov]}")
