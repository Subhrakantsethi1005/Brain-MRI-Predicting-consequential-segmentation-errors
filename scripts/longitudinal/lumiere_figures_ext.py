"""Figures for the exploratory extensions (Sections 4.4-4.5): the image-level
appearance-shift null and the third-voter sharpening. Reads the result JSONs so the
numbers match the analysis exactly. Writes docs/paper/figures/long_fig{4,5}_*.png."""
import os, json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "outputs", "lumiere")
FIGDIR = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "paper", "figures")
os.makedirs(FIGDIR, exist_ok=True)

appe = json.load(open(os.path.join(OUT, "appearance.json")))
tw = json.load(open(os.path.join(OUT, "threeway.json")))

# ---- Fig 4: image-level appearance shift does NOT predict decorrelation ----
label = {"ct1_ssim": "CT1 structural similarity", "ct1_wass": "CT1 histogram distance",
         "ct1_mad": "CT1 intensity difference", "flair_ssim": "FLAIR structural similarity",
         "flair_wass": "FLAIR histogram distance", "flair_mad": "FLAIR intensity difference"}
order = ["ct1_ssim", "ct1_wass", "ct1_mad", "flair_ssim", "flair_wass", "flair_mad"]
aur = [appe["H4_image_level"][k]["auroc_dir"] for k in order]
names = [label[k] for k in order]

fig, ax = plt.subplots(figsize=(6.4, 4))
ypos = range(len(order))
ax.barh(list(ypos), aur, color="#7f8c8d", height=0.6)
ax.axvline(0.5, ls="--", c="#c0392b", lw=1.5)
ax.text(0.5, len(order) - 0.3, "chance (0.5)", color="#c0392b", fontsize=9, ha="center")
for i, a in enumerate(aur):
    ax.text(a + 0.006, i, f"{a:.2f}", va="center", fontsize=8)
ax.set_yticks(list(ypos)); ax.set_yticklabels(names, fontsize=9)
ax.set_xlim(0, 0.75); ax.invert_yaxis()
ax.set_xlabel("AUROC for predicting direction disagreement")
ax.set_title("Whole-brain appearance shift does not predict\nthe decorrelation (all at or below chance)", fontsize=11)
fig.tight_layout(); fig.savefig(os.path.join(FIGDIR, "long_fig4_appearance_null.png"), dpi=150); plt.close(fig)

# ---- Fig 5: third voter catches false certifications within 2-way-certified calls ----
sh = tw["sharpening_within_2way_certified"]
cats = [f"3rd voter CONCURS\n(3/3, n={sh['n_3of3']})", f"3rd voter DISSENTS\n(2/3, n={sh['n_2of3']})"]
acc = [sh["acc_3of3"], sh["acc_2way_but_3rd_disagrees"]]
fig, ax = plt.subplots(figsize=(6.0, 4))
bars = ax.bar(range(2), acc, width=0.55, color=["#27ae60", "#e67e22"])
for b, a in zip(bars, acc):
    ax.text(b.get_x() + b.get_width() / 2, a + 0.012, f"{a:.2f}", ha="center", fontsize=10)
ax.set_xticks(range(2)); ax.set_xticklabels(cats, fontsize=9)
ax.set_ylim(0, 0.85)
ax.set_ylabel("Automated call accuracy vs expert RANO")
ax.set_title("Among calls the two-tool flag certifies, an independent\nthird voter's dissent marks the less-accurate ones", fontsize=10.5)
fig.tight_layout(); fig.savefig(os.path.join(FIGDIR, "long_fig5_thirdvoter.png"), dpi=150); plt.close(fig)

print("wrote long_fig4_appearance_null.png, long_fig5_thirdvoter.png")
print(f"  appearance AUROCs: {[round(a,2) for a in aur]}")
print(f"  third voter: concur acc {acc[0]:.2f} (n={sh['n_3of3']}) vs dissent acc {acc[1]:.2f} (n={sh['n_2of3']})")
