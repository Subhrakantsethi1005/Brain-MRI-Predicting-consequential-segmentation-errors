# Implementation plan

**Setup:** RTX 4050 laptop (6 GB VRAM) · no existing model · 2–4 weeks of experiments · abstract due 20 Oct 2026.

## The decision this plan is built around

You need to *make* a segmentation model, but the project's contribution is the **error-risk predictor**, not
the segmenter. So the segmenter is a standard residual 3D U-Net (MONAI), trained once with fixed
settings and no architecture search. You report its Dice next to published BraTS numbers so reviewers
can see that it is a reasonable model, not a weakened one.

The 3D U-Net has dropout in every unit. That makes **MC dropout** usable as the uncertainty source on a
single 6 GB GPU. Training a 5-model deep ensemble would take five times as long.

## Data design (most important for validity)

Dataset: **BraTS 2021 Task 1** training set (1,251 patients with expert labels; register on Synapse, or
use the Kaggle mirror while checking the licence terms). If access is slow, start the feasibility test on
**MSD Task01_BrainTumour** (CC-BY-SA, downloads straight away). MSD comes from BraTS 2016/17, so it
overlaps with BraTS 2021 and you must not combine the two.

Each patient is assigned to exactly one split (`scripts/00_make_splits.py`):

| Split | Share | ≈ cases | Used for |
|---|---|---|---|
| `seg_train` | 45 % | 563 | training the segmenter only |
| `seg_val` | 5 % | 63 | choosing the segmenter checkpoint; reporting its Dice |
| `risk_dev` | 30 % | 375 | features → risk models, repeated 5-fold CV, choosing thresholds |
| `risk_test` | 20 % | 250 | **evaluated once**, after the protocol is committed |

The segmenter never sees the risk cases. If the risk models were trained on the segmenter's own
training cases, the errors would be unrealistically small and the results would not hold up.

**External test (if time allows):** BraTS-Africa 2023 (lower field strength, different population). Its
enhancing label is `3` and its files are named `t1n t1c t2w t2f`. The scripts take both as arguments.

## Endpoint (pre-specified, `configs/preregistration.yaml`)

Primary: **whole-tumour relative volume error ≥ 25 % and absolute error ≥ 1 mL**. The 25 % links to the
RANO progression threshold (a ≥25 % increase in the bidimensional product). The 1 mL floor keeps a
0.3 mL miss on a tiny lesion from counting as consequential. Secondary endpoints (10 %, 40 %, TC, Dice < 0.8)
are all reported, whatever they show.

Before you freeze the endpoint, look up and cite published inter-rater volume variability for BraTS. If
the expert disagreement itself is around 20 %, a 25 % threshold sits close to annotation noise, and the
paper has to say so. **Commit the file before running `04_evaluate_test.py`.** The script will not run
otherwise, and the commit timestamp shows the endpoint was fixed in advance.

**Expected problem:** a good model has a low rate of consequential errors (likely 5–15 % of cases), which
could mean only about 15–35 positives in `risk_test`. Confidence intervals will be wide, and the paper
should say so plainly. If dev shows fewer than ~20 positives, the fix is more data (cross-fitting, below),
not a lower threshold.

## Features (`src/brainrisk/features.py`) and comparisons (`src/brainrisk/risk.py`)

Ten stochastic passes per case: dropout stays active, and each pass also uses a different axis flip.

| Group | Features (per region) | Role |
|---|---|---|
| `volume_only` | log predicted volume | trivial baseline: small tumours have large relative errors |
| `best_single` | strongest single uncertainty score (chosen on dev) | the "just threshold the uncertainty" baseline |
| `uncertainty` | mean entropy / variance inside the mask and around it | standard uncertainty baseline |
| `disagreement` | volume spread across passes, Dice between passes | baseline taken from QC literature |
| `boundary_morphology` | boundary-band uncertainty, **undecided volume / predicted volume**, components, surface/volume | candidate 1 |
| `combined` | everything, all regions, nested-region violations | candidate 2 |

Models: L2 logistic regression is the primary model (fixed in advance), with shallow gradient boosting as
secondary. The paper's claim depends on `combined` or `boundary_morphology` beating **both** `volume_only`
and `best_single` on `risk_test`, using a paired bootstrap. If they don't, that is still a result and gets
reported.

## Evaluation (`scripts/04_evaluate_test.py`)

AUROC and AUPRC (shown next to prevalence) with 95 % bootstrap CIs. The threshold is fixed on dev for
90 % sensitivity, and the test report gives the sensitivity actually achieved, the false-alert rate,
**the share of cases retained for automated processing**, and the residual error rate among retained
cases. It also gives the risk–coverage curve and AURC, plus the Brier score. Class-balanced logistic
regression is not calibrated, so read the Brier score with that in mind. A lock file records every look
at the test set.

## Timeline

| Dates | Work | Exit check |
|---|---|---|
| **12–14 Oct** | Literature (below); request BraTS access on day 1; install environment; `pytest` | access requested; novelty notes written |
| **15–17 Oct** | Feasibility: download data, `max_cases: 20` run of the full chain; then make the real splits and **start training** | the 20-case run finishes 00→03; first epochs timed |
| **18–19 Oct** | Write the abstract while training runs. Report only what exists (pipeline working, maybe interim seg_val Dice); describe everything else as planned | abstract draft |
| **20 Oct** | Submit | confirmation email |
| 21–26 Oct | Training finishes; check seg_val Dice against the literature; run `02_infer_mc.py` on seg_val + risk_dev + risk_test | features CSV complete |
| 27 Oct–2 Nov | `03_train_risk_model.py`, look at the dev results, write up failure cases. **Freeze and commit the protocol**, then run `04` once | test report |
| 3–9 Nov | External validation (BraTS-Africa) if feasible; figures; failure-case gallery from `outputs/pred_masks`; draft paper | draft |

**Compute budget (estimates; measure the first 2 epochs and adjust `max_epochs`):** a 128³ patch, batch 1
with AMP fits in 6 GB. Expect about 0.3–0.6 s per iteration, so roughly 5–10 h for 150 epochs over 563
cases. Run overnight with `--resume` available. Inference takes 10 passes × sliding window ≈ 30–60 s per
case, so about 6–10 h for ~690 cases. Keep the laptop plugged in and cooled; thermal throttling is common
on laptop GPUs.

## Literature to check before claiming novelty

The two papers in the brief, plus: QU-BraTS (Mehta et al., the BraTS uncertainty challenge); Jungo &
Reyes 2019 (uncertainty calibration in brain tumour segmentation); segmentation quality control without
ground truth (Kohlberger et al., MICCAI 2012; Valindria et al., reverse classification accuracy, 2017;
Robinson et al., cardiac MR QC). For each paper, write one line on whether it (a) predicts errors per
case rather than per voxel, (b) targets *volume* error, not Dice, (c) uses a pre-specified clinical
threshold, and (d) reports triage metrics (retained fraction at a fixed sensitivity). The likely gap is
the combination of (b)–(d). Check this yourself, especially against the 2026 npj Digital Medicine paper,
because it also studies volumetric uncertainty.

## Extensions if time allows

- **Cross-fitting:** train 5 segmenters on 5 folds so every case gets an out-of-fold prediction. This
  roughly doubles the number of positives and costs about 5× the training time.
- Ablation of MC dropout alone versus flip-TTA alone (set `tta_flips: false`).
- Regression of the volume error (in mL) alongside the binary flag.
