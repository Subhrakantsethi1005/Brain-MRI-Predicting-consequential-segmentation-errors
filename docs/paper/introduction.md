# Introduction (draft)

> Status: draft for BIOAI-2026. Contributions are framed as the problem
> formulation and comparison (not as a claim of beating baselines), which remains
> correct given the feasibility results: see `results.md` — on the pre-registered
> primary endpoint the engineered features do not outperform the baselines. The
> aim-style wording ("we formulate / compare / evaluate") is therefore kept.
> Citations `[n]` map to the list at the foot of this file; all entries were
> verified against source (Oct 2026) — do a final house-style/formatting pass
> before submission.

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

---

### References used in this introduction (verified at source, Oct 2026)

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
