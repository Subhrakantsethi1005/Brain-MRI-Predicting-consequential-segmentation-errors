# Predicting Consequential Volume Errors in Automated Brain-Tumour MRI Segmentation

> **One-line summary:** A system that looks at an AI's brain-tumour outline and predicts — *without ever seeing the correct answer* — whether the outline got the tumour's **size** badly wrong, so risky cases can be sent to a doctor and safe ones trusted automatically.

**Type:** University AI course project. &nbsp;|&nbsp; **Status:** study complete.
**Team:** Subhrakant Sethi, Ayush Singh, Abhayaditya Sogi, Pratyaksh Singh — B.Tech Biotechnology, Thapar Institute of Engineering and Technology, Patiala.

> ⚠️ This is a **research pipeline, not a clinical decision system.**

---

## 1. Problem & Motivation
Doctors measure a brain tumour's **volume** from MRI to track whether it is growing or shrinking (the RANO guideline calls a ≥25% increase "progression"). AI can outline (**segment**) the tumour automatically, but it occasionally makes a bad mistake on a single scan — **without warning** — and a wrong volume could change a treatment decision. In the real world there is no "correct answer" to check against at the time of use.

**Research question:** *For this one scan, can we trust the AI's tumour-size measurement, or should a human review it?*

## 2. Our Approach (two parts)
| Part | What it does | Our contribution? |
|---|---|---|
| **Model 1 — Segmenter** | A standard **3D U-Net** (MONAI) draws the tumour outline | No — reused as a fair baseline |
| **Model 2 — Reliability checker** | Predicts, per scan, whether the volume error is **"consequential"** (≥25% **and** ≥1 mL), using only the AI's own behaviour | **Yes — this is the contribution** |

**How Model 2 works (reference-free):** run the segmenter several times with small random changes (**Monte-Carlo dropout + test-time augmentation**); if the attempts disagree, the AI is unsure. From this we build case-level **features** (uncertainty, inter-run disagreement, boundary/shape) and train a **simple, interpretable model** (logistic regression) to output a **risk score**. A threshold turns it into a **triage** decision: trust vs. send-to-human.

**Scientific rigour:** patients split **by patient** (no leakage); the error definition was **pre-registered and frozen before testing**; the test set was evaluated **once**.

## 3. What Has Been Done ✅
- [x] Full, reproducible, tested pipeline (8 passing end-to-end tests).
- [x] Segmentation model trained and evaluated (Dice + volume error).
- [x] Reference-free feature extraction (MC-dropout + TTA).
- [x] Pre-registered endpoint (committed before test evaluation).
- [x] Risk models trained & compared against baselines (repeated cross-validation).
- [x] **One-shot locked test evaluation** with AUROC, triage metrics, and paired-bootstrap significance.
- [x] Full paper drafted — **[`docs/paper/paper.tex`](docs/paper/paper.tex)** (LaTeX), plus abstract & introduction.
- [ ] *(next)* Full **BraTS 2021** run for a larger, powered confirmation.

## 4. Results (preliminary — MSD dataset, locked test set *n = 97*)

**Segmenter (Model 1):** Whole-tumour **Dice 0.81**, tumour-core 0.70, enhancing 0.73.

**Reliability checker (Model 2) — primary endpoint (consequential WT volume error):**

| Feature set | Test AUROC | Note |
|---|---|---|
| Predicted volume only (trivial baseline) | 0.827 | baseline |
| Standard uncertainty | 0.855 | strong baseline |
| Prediction disagreement | 0.875 | |
| **Boundary / morphology (candidate)** | **0.880** | best |
| Combined (all features) | 0.847 | overfits |

**Triage payoff:** at 90% sensitivity, **~50% of cases can be safely automated**, with only **~6% residual error** among the automated ones.

**Honest findings (reported in full):**
- The candidate features **clearly beat the trivial baseline**.
- Their advantage over standard uncertainty was **not statistically significant** on this small test set — **except for severe (≥40%) errors**, where disagreement significantly beat uncertainty (*p = 0.03*).
- Combining all features **reduced** performance (overfitting) — a reported negative finding.

## 5. Repository Structure
```
├── src/brainrisk/        # core library
│   ├── data.py           # case discovery (BraTS + MSD), patient-level splits, transforms
│   ├── model.py          # 3D U-Net + MC-dropout/flip inference
│   ├── features.py       # reference-free case-level features
│   ├── metrics.py        # Dice, HD95, volume errors, endpoint labels
│   └── risk.py           # risk models, triage metrics, bootstrap tests
├── scripts/              # pipeline, run in order 00 → 04
│   ├── 00_make_splits.py 01_train_segmentation.py eval_segmentation.py
│   └── 02_infer_mc.py    03_train_risk_model.py   04_evaluate_test.py
├── configs/              # default(BraTS) / fast / msd / msd_feasibility / preregistration
├── docs/
│   ├── IMPLEMENTATION_PLAN.md
│   └── paper/            # paper.tex, introduction.(md/docx), abstract.(md/docx), references.md
└── tests/test_pipeline.py
```

## 6. How to Reproduce
```bash
# 1. Environment (Python 3.12; CUDA GPU recommended)
pip install torch==2.6.0 --index-url https://download.pytorch.org/whl/cu124
pip install -r requirements.txt
pytest -q                                       # synthetic end-to-end test (~2 min)

# 2. Run the pipeline (MSD dataset; use configs/default.yaml for BraTS 2021)
CFG=configs/msd.yaml
python scripts/00_make_splits.py --config $CFG
python scripts/01_train_segmentation.py --config $CFG
python scripts/eval_segmentation.py --config $CFG
python scripts/02_infer_mc.py --config $CFG
python scripts/03_train_risk_model.py --config $CFG
git commit configs/preregistration.yaml         # freeze the protocol before testing
python scripts/04_evaluate_test.py --config $CFG # locked test, once
```
Datasets are **not** included (download separately): MSD Task01_BrainTumour, or BraTS 2021.
Tip: for a quick sanity run use `configs/msd_feasibility.yaml` (20 cases, 2 epochs).

## 7. Limitations & Next Steps
- Preliminary: small dataset/test set → wide confidence intervals; single modest segmenter; retrospective, one dataset.
- **Next:** repeat the identical, pre-registered pipeline on the **full BraTS 2021** cohort for a powered confirmation, and explore external validation.

## 8. Paper & Documents
- **Full paper:** [`docs/paper/paper.tex`](docs/paper/paper.tex) (compile on Overleaf)
- **Abstract:** [`docs/paper/abstract.md`](docs/paper/abstract.md)
- **Introduction & references:** [`docs/paper/introduction.md`](docs/paper/introduction.md), [`docs/paper/references.md`](docs/paper/references.md)
- **Design & plan:** [`docs/IMPLEMENTATION_PLAN.md`](docs/IMPLEMENTATION_PLAN.md)
