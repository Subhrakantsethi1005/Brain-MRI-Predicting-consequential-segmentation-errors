# Methodology

> Self-contained methodology for the project. Describes the
> implemented pipeline (what we did and how), the feasibility experiments run so
> far, and the planned extensions (what we will do), including the learned
> end-to-end error detector and the move to a larger training corpus. Completed
> work is written in the past tense; planned work in the future tense.

## 1. Problem formulation

We treat brain-tumour segmentation reliability as a **case-level prediction task**:
given an automatic segmentation and the model's own stochastic behaviour — but
**no reference mask** — decide whether the output's whole-tumour volume error is
large enough to be clinically consequential, so that unreliable cases are routed to
expert review while the rest are safely automated. The study is deliberately a
*triage benchmark*: we do not propose a new segmentation architecture or a new
uncertainty estimator, but ask which readily available, reference-free signals
actually predict consequential volume error, under a protocol fixed in advance.

## 2. Data and patient-level splits

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

## 3. Segmentation model

The segmenter is a standard residual 3D U-Net (MONAI) with dropout in every unit,
trained once with fixed hyper-parameters (96³ patches, batch size 1, mixed-precision,
Dice loss, Adam, learning rate 2×10⁻⁴) and no architecture search. We report its
Dice against published BraTS numbers so that reviewers can confirm it is a
reasonable, not deliberately weakened, baseline. Dropout in every unit is what makes
Monte-Carlo dropout a usable uncertainty source on a single 6 GB GPU, avoiding the
cost of a deep ensemble.

## 4. Reference-free stochastic inference

For each case we drew multiple stochastic predictions with MC-dropout kept active,
each pass additionally combined with a random axis flip (test-time augmentation), so
that the passes cost the same as plain MC-dropout. From the per-voxel **mean** and
**variance** across passes we computed all downstream signals, for the three nested
BraTS regions — whole tumour (WT), tumour core (TC), enhancing tumour (ET). No
reference mask enters this stage.

## 5. Case-level, reference-free features

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

## 6. Pre-specified error endpoints

The analysis protocol was fixed and committed before any evaluation on the test set
(`configs/preregistration.yaml`; the commit timestamp is the evidence, and the
evaluation script refuses to run with uncommitted changes to it). The **primary
endpoint** labels a case consequential when the whole-tumour relative volume error
is ≥ 25 % **and** the absolute error is ≥ 1 mL: the 25 % links to the RANO
progression threshold, and the 1 mL floor prevents a sub-millilitre miss on a tiny
lesion from being counted. Reference volume error is measured from the expert mask.
Secondary endpoints (WT at 10 % and 40 %, TC at 25 %, and WT Dice < 0.80) are
reported in full whatever they show and are not used to pick the primary result.

## 7. Risk models and comparison

The primary model is L2-regularised logistic regression (class-balanced, median
imputation, standardised features); shallow histogram gradient boosting is the
secondary model. On `risk_dev` we obtained risk scores by repeated (5×) stratified
5-fold cross-validation (out-of-fold scores), which we used to compare feature
families, choose `best_single`, and fix the operating threshold at 90 % sensitivity.
The frozen models and threshold were then applied **once** to `risk_test`. The
pre-specified success criterion was that a candidate family (`boundary_morphology`
or `combined`) beat **both** baselines on a paired bootstrap of AUROC; the outcome
was reported whether or not it held.

## 8. Evaluation

We report AUROC (primary metric) and AUPRC shown against prevalence, each with 95 %
bootstrap confidence intervals (2,000 resamples). As a triage mechanism we report,
at the fixed-sensitivity operating point, the sensitivity actually achieved, the
false-alert rate, the fraction of cases retained for automation, and the residual
consequential-error rate among retained cases, together with the risk–coverage curve
and its area and the Brier score (read with the caveat that a class-balanced
logistic model is not calibrated). Feature families are compared with a paired
bootstrap of AUROC, reporting the difference, its 95 % CI, and a two-sided p-value.

## 9. Planned extensions (future work)

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
