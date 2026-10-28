# Methods (draft)

> Status: describes the implemented pipeline (`src/brainrisk/`, `scripts/`). The
> design and endpoint were fixed in advance; see `configs/preregistration.yaml`
> and `docs/IMPLEMENTATION_PLAN.md`. Numbers reported here match the MSD
> feasibility run; the identical pipeline runs on BraTS 2021 via `configs/`.

## 3.1 Overview

We decompose segmentation reliability into two stages. A standard 3D segmenter
produces, for each case, a set of stochastic predictions. From those predictions
alone — with no reference mask — we compute case-level features and train a small
classifier to predict whether the case's whole-tumour volume error exceeds a
clinically motivated threshold. The segmenter is held fixed; the study concerns
the second stage and its comparison against baselines.

## 3.2 Data and patient-level splits

Experiments use expert-annotated, publicly available brain-tumour MRI. For the
feasibility results reported here we use MSD Task01_BrainTumour (484 patients,
four co-registered modalities per case); the same pipeline targets BraTS 2021
(1,251 patients) through a configuration switch, with the dataset's label
convention (`enhancing_label`, `core_labels`) and file layout carried in the
config. Each patient is assigned to exactly one of four disjoint splits
(`scripts/00_make_splits.py`): `seg_train` (45 %), `seg_val` (5 %), `risk_dev`
(30 %) and `risk_test` (20 %). The segmenter is trained and selected only on
`seg_train`/`seg_val`; risk models are developed on `risk_dev` and evaluated once
on `risk_test`. This separation is essential: training the risk model on the
segmenter's own training cases would make the observed errors unrealistically
small. MSD and BraTS 2021 share source scans and are never mixed.

## 3.3 Segmentation model and stochastic inference

The segmenter is a residual 3D U-Net (MONAI) with dropout in every unit, trained
once with fixed hyper-parameters (96³ patches, batch 1, AMP, Dice loss, Adam,
LR 2×10⁻⁴). No architecture search is performed. We report its Dice against
published BraTS numbers so reviewers can confirm it is a reasonable, not
weakened, baseline. We deliberately do not propose a new segmentation
architecture or uncertainty estimator.

For each case we draw stochastic predictions with MC-dropout kept active, each
pass combined with a random axis flip (test-time augmentation). The feasibility
run used 5 passes; the plan specifies up to 10. The per-voxel mean and variance
across passes are the raw material for all features. Predictions are produced for
the three nested BraTS regions — whole tumour (WT), tumour core (TC), enhancing
tumour (ET).

## 3.4 Case-level, reference-free features (`features.py`)

From the stochastic probability maps we derive per-region features that require
no ground truth, grouped into the families compared below:

- **`uncertainty`** — mean binary entropy and variance inside the predicted mask
  and in a dilated ROI, and total entropy volume. Standard voxel-uncertainty
  summaries aggregated to the case level.
- **`disagreement`** — coefficient of variation and relative range of the
  per-pass predicted volume, and the mean/min Dice between each pass and the
  consensus mask. Captures how much the volume estimate moves across stochastic
  passes.
- **`boundary_morphology`** — boundary-band (shell) entropy and variance; the
  **undecided volume fraction** (voxels with 0.2 < p < 0.8, relative to predicted
  volume) and the soft-minus-hard volume difference, both direct proxies for how
  far the volume estimate could move; and morphology descriptors (connected
  components, largest-component fraction, number of small components,
  surface-to-volume ratio) plus log predicted volume.
- **`combined`** — all of the above across all three regions, plus nested-region
  consistency terms (ET outside TC, TC outside WT).

Two reference points anchor the comparison: **`volume_only`** (log predicted
volume alone — small tumours have large relative errors) and **`best_single`**
(the single strongest uncertainty score, selected on `risk_dev`), the
"just threshold the uncertainty" baseline.

## 3.5 Error endpoints (pre-specified, `preregistration.yaml`)

The **primary endpoint** labels a case consequential when the whole-tumour
relative volume error is ≥ 25 % **and** the absolute error is ≥ 1 mL. The 25 %
links to the RANO progression threshold [2]; the 1 mL floor prevents a sub-mL
miss on a tiny lesion from being counted. Reference volume error is computed from
the expert mask (`metrics.py`). Secondary endpoints — WT at 10 % and 40 %, TC at
25 %, and WT Dice < 0.80 — are reported in full whatever they show and are not
used to select the primary result. The endpoint file was committed before any
test evaluation; `scripts/04_evaluate_test.py` refuses to run with uncommitted
changes to it, and a lock file records each look at the test set.

## 3.6 Risk models and comparison (`risk.py`)

The primary model is L2-regularised logistic regression (class-balanced,
median-imputed, standardised); shallow histogram gradient boosting is the
secondary model. On `risk_dev`, risk scores are obtained by repeated (5×)
stratified 5-fold cross-validation (out-of-fold scores), used to compare feature
families, choose `best_single`, and fix the operating threshold at 90 %
sensitivity. The frozen models and threshold are then applied once to
`risk_test`. The pre-specified claim was that a candidate family
(`boundary_morphology` or `combined`) beat both baselines on a paired bootstrap;
the outcome is reported in §4 whether or not it held.

## 3.7 Evaluation metrics

We report AUROC (primary metric) and AUPRC shown against prevalence, each with
95 % bootstrap confidence intervals (2,000 resamples). As a triage mechanism we
report, at the fixed-sensitivity operating point, the sensitivity actually
achieved, the false-alert rate, the fraction of cases retained for automation,
and the residual consequential-error rate among retained cases, plus the
risk–coverage curve and its area (AURC) and the Brier score. Because the
logistic model is class-balanced rather than calibrated, the Brier score is read
with that caveat. Feature families are compared with a paired bootstrap of AUROC
(cases resampled jointly), reporting the difference, its 95 % CI, and a two-sided
p-value.
