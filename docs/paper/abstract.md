# Abstract — BIOAI-2026 submission (draft)

> ~290 words (limit 300) · 6 keywords (max 6) · Theme 2: Health, Pharmaceutical
> & Forensic Sciences. Includes the required line distinguishing planned work
> from completed results.

**Predicting Consequential Volume Errors in Automated Brain-Tumour MRI Segmentation**

Tumour volume derived from brain MRI is central to assessing glioma progression and
treatment response, yet automated segmentation models occasionally produce outputs
that mis-estimate volume enough to mislead clinical interpretation. Deploying such
models safely requires knowing, for each scan, whether its output can be trusted.
Existing reliability methods largely relate uncertainty to overlap metrics such as
the Dice coefficient rather than to volume error specifically, seldom define error
against a pre-specified clinical threshold, and are rarely framed as an operational
triage task.

We study segmentation reliability as the case-level prediction of consequential
volume error. Rather than proposing a new segmentation architecture or uncertainty
method, we take a standard 3D segmenter and ask whether simple, interpretable models
can predict — from the model's own stochastic behaviour (Monte-Carlo dropout with
test-time augmentation) — when an output's whole-tumour volume error exceeds a
clinically motivated threshold (relative error ≥ 25 %, absolute ≥ 1 mL) fixed and
committed in advance. We derive case-level features spanning uncertainty,
inter-prediction disagreement, and boundary/shape characteristics, and compare
feature families (logistic regression, gradient boosting) against trivial
predicted-volume-only and single-best-uncertainty baselines using a paired
bootstrap. The system is validated against true errors from expert reference masks
and evaluated as a triage mechanism using AUROC, AUPRC, sensitivity, false-alert
rate, and the fraction of cases retainable for automation at a fixed sensitivity, on
held-out patients.

Experiments use publicly available, expert-annotated brain-tumour MRI with
patient-level splits. On a feasibility dataset, all feature families reach AUROC
0.83–0.88 and support a useful operating point — retaining ~49 % of cases for
automation at 90 % sensitivity while cutting the consequential-error rate on that
stream from 35 % to ~6 %. Critically, and against our working hypothesis, on the
pre-registered primary endpoint the engineered boundary/morphology and combined
features do **not** significantly outperform a single uncertainty score or predicted
volume alone; they separate from the baselines only on clearer failures (Dice < 0.80
and ≥ 40 % volume error). *(Status: results are on a feasibility dataset standing in
for BraTS while access is pending; the identical pre-registered pipeline targets
BraTS 2021.)* Our contribution is a pre-registered, reproducible, triage-framed
benchmark for consequential volume-error prediction and an honest account of which
readily available signals do — and do not — predict it.

**Keywords:** brain tumour MRI; segmentation reliability; volumetric error;
uncertainty; quality control; deep learning
