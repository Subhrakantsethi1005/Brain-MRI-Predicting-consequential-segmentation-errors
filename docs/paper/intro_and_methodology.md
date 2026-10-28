# Reference-Free Prediction of Consequential Brain-Tumour Volume Error

## Introduction

Gliomas are among the most common and aggressive primary brain tumours, and
magnetic resonance imaging (MRI) is the principal modality for their diagnosis,
treatment planning, and longitudinal monitoring [1]. A central quantitative
output of this imaging is **tumour volume**: changes in the volume of the whole
tumour, tumour core, and enhancing region over time are used to assess disease
progression and treatment response, and underpin established response-assessment
criteria such as RANO, which defines progression in part through a ≥25 % increase
in tumour burden [2]. Accurate quantification of these volumes is therefore not
merely a segmentation exercise — it directly shapes clinical interpretation.

Deep learning has driven substantial progress in automated brain-tumour
segmentation, with benchmarks such as BraTS establishing 3D convolutional
architectures (e.g., nnU-Net, SegResNet) as strong, reproducible baselines
[3], [4]. In principle these models could automate laborious manual contouring.
In practice their outputs cannot be trusted blindly: even high-performing models
produce occasional failures, and a single segmentation that substantially
mis-estimates tumour volume can propagate into an incorrect assessment of
progression or response. Deploying automated segmentation at scale therefore
requires more than an accurate model — it requires knowing, for each individual
scan, **whether the resulting output can be trusted**, so that unreliable cases
are routed to expert review while the rest are safely automated.

Prior work has approached this reliability problem from several directions, and
each leaves a specific gap. Uncertainty quantification — Monte-Carlo dropout,
deep ensembles, and test-time augmentation — yields voxel-wise uncertainty maps,
and the QU-BraTS benchmark showed that such estimates carry information about
where a model is likely to err, while also concluding that no single uncertainty
method dominates [5]. However, these estimates are evaluated and rewarded mainly
at the voxel level. Jungo, Balsiger and Reyes found that uncertainty that is
well-calibrated at the dataset level becomes **miscalibrated at the subject
level**, with limited ability to localise error, even though aggregating
voxel uncertainty to the case level can still flag clearly failed segmentations
[6]. This motivates treating case-level reliability as a prediction task in its
own right rather than reading it directly off raw uncertainty. Reference-free
quality-control methods address the case level — reverse classification accuracy
predicts segmentation quality without ground truth by retraining a classifier on
the prediction [7], and learned quality predictors flag failures at population
scale [8] — but both target **overlap** quality (Dice-like) rather than volume
error, are not framed against a pre-specified clinical threshold, and are not
reported as an operational triage outcome. More recent work provides calibrated
volumetric uncertainty and conformal guarantees: evidential ensembles yield
calibrated volume estimates for meningioma segmentation with external validation
[9], and conformal methods give predictive intervals for volume that remain
valid under covariate shift [10]. These produce an *uncertainty estimate or
interval*, not a *decision* about whether a given case is wrong enough to matter
clinically. A related line characterises volumetric **bias** of soft-Dice-trained
models, but at the population and theoretical level rather than as a per-case
prediction [11]. Finally, reliability studies under distribution shift [12] and
selective-prediction triage pipelines [13] are emerging, though the former
targets Dice-based error detection under synthetic corruption and the latter
addresses tumour *classification* rather than segmentation; and reference-free
indicators have in some settings proved insufficient for subtle, non-empty
errors [14], a cautionary result that any case-level reliability claim must
confront honestly.

Across this literature, three gaps recur: reliability is related to overlap
metrics such as the Dice coefficient rather than to **volume error**
specifically; error is seldom defined against a **pre-specified, clinically
motivated threshold**; and results are rarely reported as an operational
**triage** outcome — how many cases can be safely automated at a fixed
error-detection sensitivity.

In this work we study segmentation reliability as the **case-level prediction of
consequential volume error**. Rather than proposing a new segmentation
architecture or a new uncertainty-calibration method, we take a standard
segmenter and ask a focused, clinically framed question: can simple,
interpretable models predict — from the segmenter's own stochastic behaviour
(Monte-Carlo dropout with test-time augmentation) — when an output's whole-tumour
volume error exceeds a threshold fixed in advance on clinical grounds? The error
endpoint is pre-specified and frozen before any evaluation on the held-out test
set, with the commit timestamp as evidence that it was not tuned to the result.
From the stochastic predictions we derive case-level features spanning
uncertainty, inter-prediction disagreement, and boundary/shape characteristics,
and compare feature families against trivial (predicted-volume-only) and
single-best-uncertainty baselines using a paired bootstrap. We additionally ask
whether the same reference-free signals can indicate the **direction** of the
error — whether a case is likely over- or under-segmented — a per-case question
distinct from the population-level volumetric bias characterised previously [11].
The predictor is validated against true errors measured from expert reference
masks, evaluated on held-out patients as a triage mechanism, and reported with
failure cases and negative findings.

We do not claim a novel uncertainty estimator, a calibration method, or a
statistical coverage guarantee; those have been studied elsewhere [9], [10]. Nor
do we claim that case-level reliability is newly possible — only that it has not
been posed in the specific form we adopt. Our aim is a clear, reproducible,
clinically-framed baseline for *consequential volume-error triage*, runnable on a
single commodity GPU, and an honest account of which readily available signals
actually predict it.

**Our contributions are:**

1. We **formulate segmentation reliability as the case-level prediction of
   consequential volume error**, with the error endpoint pre-specified against a
   clinically motivated threshold and frozen before test evaluation, rather than
   tuned post hoc.
2. We **compare feature families** — uncertainty, prediction disagreement, and
   boundary/morphology descriptors — against trivial predicted-volume-only and
   single-best-uncertainty baselines with a paired bootstrap, isolating what
   actually predicts volume error, and we additionally test whether these signals
   indicate the **direction** of the error per case.
3. We **evaluate the system with triage-oriented metrics** — AUROC, AUPRC,
   sensitivity, false-alert rate, the fraction of cases retainable for automation
   at a fixed sensitivity, and the risk–coverage curve — on held-out patients,
   reporting failure cases and negative findings alongside successes.

### References

- **[1]** Weller, M. et al. EANO guidelines on the diagnosis and treatment of
  diffuse gliomas of adulthood. *Nat. Rev. Clin. Oncol.* 18(3):170–186, 2021.
  doi:10.1038/s41571-020-00447-z.
- **[2]** Wen, P. Y. et al. Updated response assessment criteria for high-grade
  gliomas: Response Assessment in Neuro-Oncology (RANO) working group.
  *J. Clin. Oncol.* 28(11):1963–1972, 2010. doi:10.1200/JCO.2009.26.3541.
- **[3]** Isensee, F., Jaeger, P. F., Kohl, S. A. A., Petersen, J. &
  Maier-Hein, K. H. nnU-Net: a self-configuring method for deep learning-based
  biomedical image segmentation. *Nat. Methods* 18(2):203–211, 2021.
  doi:10.1038/s41592-020-01008-z.
- **[4]** Baid, U. et al. The RSNA-ASNR-MICCAI BraTS 2021 benchmark on brain
  tumor segmentation and radiogenomic classification. arXiv:2107.02314, 2021.
  (SegResNet architecture: Myronenko, A. 3D MRI brain tumor segmentation using
  autoencoder regularization. *BrainLes @ MICCAI 2018.* arXiv:1810.11654.)
- **[5]** Mehta, R. et al. QU-BraTS: MICCAI BraTS 2020 Challenge on Quantifying
  Uncertainty in Brain Tumor Segmentation. *J. Machine Learning for Biomedical
  Imaging (MELBA)*, 2022. arXiv:2112.10074.
- **[6]** Jungo, A., Balsiger, F. & Reyes, M. Analyzing the Quality and
  Challenges of Uncertainty Estimations for Brain Tumor Segmentation.
  *Front. Neurosci.* 14:282, 2020. doi:10.3389/fnins.2020.00282.
- **[7]** Valindria, V. V. et al. Reverse Classification Accuracy: Predicting
  Segmentation Performance in the Absence of Ground Truth. *IEEE TMI*
  36(8):1597–1606, 2017. arXiv:1702.03407.
- **[8]** Robinson, R. et al. Automated quality control in image segmentation:
  application to the UK Biobank cardiovascular MR imaging study.
  *J. Cardiovasc. Magn. Reson.* 21:18, 2019. doi:10.1186/s12968-019-0523-x.
- **[9]** Guennoun, Y. et al. Segmenting with confidence through uncertainty
  quantification for brain tumor imaging. *npj Digital Medicine*, 2026.
  doi:10.1038/s41746-026-02902-0.
- **[10]** Lambert, B., Forbes, F., Doyle, S. & Dojat, M. Robust Conformal Volume
  Estimation in 3D Medical Images. *MICCAI 2024.* arXiv:2407.19938.
- **[11]** Bertels, J., Robben, D., Vandermeulen, D. & Suetens, P. Optimization
  with Soft Dice Can Lead to a Volumetric Bias. *BrainLes @ MICCAI 2019.*
  doi:10.1007/978-3-030-46640-4_9. arXiv:1911.02278.
- **[12]** Shet, R. D., Liang, C. & Zhang, L. Reliability analysis for BraTS-GoAT
  segmentation: a controlled robustness study of deep-ensemble uncertainty.
  arXiv:2608.13223, 2026.
- **[13]** Sharma, M. Monte Carlo Dropout Uncertainty and Entropy-Thresholded
  Selective Prediction for Architecture-Agnostic Brain Tumor MRI Triage.
  arXiv:2607.16317, 2026. *(brain-tumour classification, not segmentation)*
- **[14]** Bricout, A., Hardman, D., Inglis, S., Pye, S. & Moran, C. M. Beyond
  segmentation accuracy: understanding model reliability and failure modes in
  ultrasound image analysis. *Front. Med. Technol.* 8, 2026.
  doi:10.3389/fmedt.2026.1918432.

## Methodology

> Describes the implemented pipeline (what we did and how), the feasibility
> experiments run so far, and the planned extensions (what we will do), including
> the learned end-to-end error detector and the move to a larger training corpus.
> Completed work is written in the past tense; planned work in the future tense.

### 1. Problem formulation

We treat brain-tumour segmentation reliability as a **case-level prediction task**:
given an automatic segmentation and the model's own stochastic behaviour — but
**no reference mask** — decide whether the output's whole-tumour volume error is
large enough to be clinically consequential, so that unreliable cases are routed to
expert review while the rest are safely automated. The study is deliberately a
*triage benchmark*: we do not propose a new segmentation architecture or a new
uncertainty estimator, but ask which readily available, reference-free signals
actually predict consequential volume error, under a protocol fixed in advance.

### 2. Data and patient-level splits

All experiments use publicly available, expert-annotated brain-tumour MRI. For the
feasibility stage reported here we used the **MSD Task01_BrainTumour** collection
(484 patients, four co-registered modalities each). The identical pipeline targets
larger glioma corpora (§9) through a configuration switch that carries each
dataset's label convention and file layout.

Each patient was assigned to exactly one of four disjoint splits
(`scripts/00_make_splits.py`), so no patient appears in more than one:

| Split | Share | Purpose |
|---|---|---|
| `seg_train` | 45 % | train the segmenter only |
| `seg_val` | 5 % | select the segmenter checkpoint; report its Dice |
| `risk_dev` | 30 % | develop risk models (repeated cross-validation), fix thresholds |
| `risk_test` | 20 % | evaluate once, after the protocol is committed |

This separation is essential to validity: the segmenter never sees the risk cases,
so the errors the risk model learns from are realistic rather than the unrealistically
small errors a model makes on its own training data. Datasets that share source
scans (e.g. MSD and BraTS) are never combined.

### 3. Segmentation model

The segmenter is a standard residual 3D U-Net (MONAI) with dropout in every unit,
trained once with fixed hyper-parameters (96³ patches, batch size 1, mixed-precision,
Dice loss, Adam, learning rate 2×10⁻⁴) and no architecture search. We report its
Dice against published BraTS numbers so that reviewers can confirm it is a
reasonable, not deliberately weakened, baseline. Dropout in every unit is what makes
Monte-Carlo dropout a usable uncertainty source on a single 6 GB GPU, avoiding the
cost of a deep ensemble.

### 4. Reference-free stochastic inference

For each case we drew multiple stochastic predictions with MC-dropout kept active,
each pass additionally combined with a random axis flip (test-time augmentation), so
that the passes cost the same as plain MC-dropout. From the per-voxel **mean** and
**variance** across passes we computed all downstream signals, for the three nested
BraTS regions — whole tumour (WT), tumour core (TC), enhancing tumour (ET). No
reference mask enters this stage.

### 5. Case-level, reference-free features

From the stochastic probability maps we derived per-region features requiring no
ground truth, organised into the families that the comparison contrasts:

- **`uncertainty`** — mean entropy and variance inside the predicted mask and a
  dilated ROI, and total entropy volume (standard voxel-uncertainty summaries
  aggregated to the case level);
- **`disagreement`** — coefficient of variation and relative range of the per-pass
  predicted volume, and the mean/minimum Dice between each pass and the consensus
  mask (how much the volume estimate moves across passes);
- **`boundary_morphology`** — boundary-band (shell) entropy and variance; the
  *undecided volume fraction* (voxels with probability between 0.2 and 0.8, relative
  to predicted volume) and the soft-minus-hard volume difference, both direct proxies
  for how far the volume estimate could move; and shape descriptors (connected
  components, largest-component fraction, number of small components,
  surface-to-volume ratio) with log predicted volume;
- **`combined`** — all of the above across all regions plus nested-region
  consistency terms (ET outside TC, TC outside WT).

Two reference points anchor every comparison: **`volume_only`** (log predicted
volume alone — small tumours have large relative errors) and **`best_single`** (the
single strongest uncertainty score, selected on `risk_dev`), i.e. the
"just threshold one uncertainty number" baseline.

### 6. Pre-specified error endpoints

The analysis protocol was fixed and committed before any evaluation on the test set
(`configs/preregistration.yaml`; the commit timestamp is the evidence, and the
evaluation script refuses to run with uncommitted changes to it). The **primary
endpoint** labels a case consequential when the whole-tumour relative volume error
is ≥ 25 % **and** the absolute error is ≥ 1 mL: the 25 % links to the RANO
progression threshold, and the 1 mL floor prevents a sub-millilitre miss on a tiny
lesion from being counted. Reference volume error is measured from the expert mask.
Secondary endpoints (WT at 10 % and 40 %, TC at 25 %, and WT Dice < 0.80) are
reported in full whatever they show and are not used to pick the primary result.

### 7. Risk models and comparison

The primary model is L2-regularised logistic regression (class-balanced, median
imputation, standardised features); shallow histogram gradient boosting is the
secondary model. On `risk_dev` we obtained risk scores by repeated (5×) stratified
5-fold cross-validation (out-of-fold scores), which we used to compare feature
families, choose `best_single`, and fix the operating threshold at 90 % sensitivity.
The frozen models and threshold were then applied **once** to `risk_test`. The
pre-specified success criterion was that a candidate family (`boundary_morphology`
or `combined`) beat **both** baselines on a paired bootstrap of AUROC; the outcome
was reported whether or not it held.

### 8. Evaluation

We report AUROC (primary metric) and AUPRC shown against prevalence, each with 95 %
bootstrap confidence intervals (2,000 resamples). As a triage mechanism we report,
at the fixed-sensitivity operating point, the sensitivity actually achieved, the
false-alert rate, the fraction of cases retained for automation, and the residual
consequential-error rate among retained cases, together with the risk–coverage curve
and its area and the Brier score (read with the caveat that a class-balanced
logistic model is not calibrated). Feature families are compared with a paired
bootstrap of AUROC, reporting the difference, its 95 % CI, and a two-sided p-value.

### 9. Planned extensions (future work)

The feasibility stage established a working, pre-registered pipeline and an honest
baseline comparison. On that feasibility dataset the engineered features did not
outperform the simple baselines on the primary endpoint, which motivates the
following planned work; none of it alters the frozen endpoint.

1. **Scale to a large training corpus.** End-to-end learning and reliable effect
   estimates require many more cases than MSD provides. We will run the identical
   protocol on a large, expert-annotated glioma corpus (candidate: BraTS 2023 Adult
   Glioma, 1,251 cases, extendable toward the ~2,200-case BraTS 2024 cohort, and
   optionally pooled with other whole-tumour-annotated collections), giving roughly
   an order of magnitude more development cases and a lower, more realistic
   prevalence of consequential error.

2. **A learned, end-to-end error detector.** In place of hand-crafted features we
   will train a small, heavily-regularised 3D convolutional network that reads the
   segmenter's uncertainty volumes directly (per-region mean probability, variance,
   and entropy, resampled to a fixed low-resolution grid) and outputs a single
   case-level risk score. The network is deliberately tiny (on the order of 10⁴
   parameters) with dropout, weight decay, and flip augmentation, because positives
   are scarce. Crucially, it is evaluated under the *same* pre-registered protocol —
   the same repeated cross-validation on `risk_dev`, the same fixed-sensitivity
   threshold, and the same paired-bootstrap comparison against `volume_only` and
   `best_single` — so that "learned" enters as one more family on equal terms. The
   learned detector is judged only on a fresh, once-opened test split; the existing
   feasibility test set is not reused.

3. **Cross-fitting for more positives.** Training several segmenters on disjoint
   folds so that every case receives an out-of-fold prediction roughly doubles the
   number of error positives available to the risk model, tightening confidence
   intervals without lowering the clinical threshold.

4. **Direction and magnitude of error.** Beyond the binary flag, we will test
   whether the same reference-free signals indicate whether a case is over- or
   under-segmented and by how much, moving from error *detection* toward reference-free
   volume *correction*.

5. **External validation and calibration.** We will validate on an out-of-distribution
   cohort (e.g. BraTS-Africa: lower field strength, different population) and add
   probability calibration so that outputs can be read as risks.

6. **Annotation-noise context.** We will cite measured inter-rater *volume*
   variability for BraTS and state where the 25 % threshold sits relative to it, since
   our feasibility results suggest the engineered signals help mainly once the error
   exceeds the annotation-noise floor (large errors and overlap failures).
