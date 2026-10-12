# Introduction (draft)

> Status: first draft for BIOAI-2026. Results-dependent claims are written as
> "we investigate / propose / evaluate" because experiments are not yet complete.
> Citations `[n]` are placeholders — see `references.md` (to be compiled).

Gliomas are among the most common and aggressive primary brain tumours, and
magnetic resonance imaging (MRI) is the principal modality for their diagnosis,
treatment planning, and longitudinal monitoring [1]. A central quantitative output
of this imaging is **tumour volume**: changes in the volume of the whole tumour,
tumour core, and enhancing region over time are used to assess disease progression
and treatment response, and underpin established response-assessment criteria such
as RANO [2]. Accurate quantification of these volumes is therefore not merely a
segmentation exercise — it directly shapes clinical interpretation.

Deep learning has driven substantial progress in automated brain-tumour
segmentation, with benchmarks such as BraTS establishing 3D convolutional
architectures (e.g., nnU-Net, SegResNet) as strong, reproducible baselines [3], [4].
In principle these models could automate laborious manual contouring. In practice
their outputs cannot be trusted blindly: even high-performing models produce
occasional failures, and a single segmentation that substantially mis-estimates
tumour volume can propagate into an incorrect assessment of progression or response.
Deploying automated segmentation at scale therefore requires more than an accurate
model — it requires knowing, for each individual scan, **whether the resulting
output can be trusted**, so that unreliable cases are routed to expert review while
the rest are safely automated.

Prior work has approached this reliability problem from several directions.
Uncertainty quantification — Monte-Carlo dropout, deep ensembles, and test-time
augmentation — yields voxel-wise uncertainty maps, and benchmarks such as QU-BraTS
have shown these estimates carry information about where a model is likely to err
[5], [6]. Reference-free quality-control methods such as reverse classification
accuracy [7] and learned quality predictors [8] estimate segmentation quality
without ground truth. More recent work provides calibrated volumetric uncertainty
and conformal guarantees on volume estimates [9], [10]. Across much of this
literature, however, reliability is related to overlap metrics such as the Dice
coefficient rather than to **volume error** specifically; error is seldom defined
against a **pre-specified, clinically motivated threshold**; and results are
rarely reported as an operational **triage** outcome — how many cases can be
safely automated at a fixed error-detection sensitivity.

In this work we study segmentation reliability as the **case-level prediction of
consequential volume error**. Rather than proposing a new segmentation
architecture or a new uncertainty-calibration method, we take a standard segmenter
and ask a focused, clinically framed question: can simple, interpretable models
predict — from the segmenter's own behaviour — when an output's whole-tumour volume
error exceeds a threshold fixed in advance on clinical grounds? From Monte-Carlo
dropout with test-time augmentation we derive case-level features spanning
uncertainty, inter-prediction disagreement, and boundary/shape characteristics, and
compare feature families against trivial (predicted-volume-only) and
uncertainty-only baselines. The predictor is validated against true errors measured
from expert reference masks, evaluated on held-out patients as a triage mechanism,
and reported with failure cases and negative findings.

We do not claim a novel uncertainty estimator, a calibration method, or a
statistical coverage guarantee; those have been studied elsewhere [9], [10]. Our
aim is a clear, reproducible, clinically-framed baseline for *consequential
volume-error triage*, and an honest account of which readily available signals
actually predict it.

**Our contributions are:**

1. We formulate segmentation reliability as the **case-level prediction of
   consequential volume error**, with the error endpoint pre-specified against a
   clinically motivated threshold rather than tuned post hoc.
2. We propose and compare **feature families** — uncertainty, prediction
   disagreement, and boundary/morphology descriptors — against trivial and
   uncertainty-only baselines, isolating what actually predicts volume error.
3. We evaluate the system with **triage-oriented metrics** (AUROC, AUPRC,
   sensitivity, false-alert rate, and the fraction of cases retainable for
   automation at a fixed sensitivity) on held-out patients, reporting failure
   cases and negative findings alongside successes.
