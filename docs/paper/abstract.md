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
clinically motivated threshold fixed in advance. We derive case-level features
spanning uncertainty, inter-prediction disagreement, and boundary/shape
characteristics, and compare feature families (logistic regression, gradient
boosting) against trivial predicted-volume-only and uncertainty-only baselines. The
system is validated against true errors from expert reference masks and evaluated as
a triage mechanism using AUROC, AUPRC, sensitivity, false-alert rate, and the
fraction of cases retainable for automation at a fixed sensitivity, on held-out
patients, with external validation where feasible.

Experiments use publicly available, expert-annotated BraTS data with patient-level
splits. *(Status: a reproducible pipeline has been implemented and validated
end-to-end; segmentation training and risk-model evaluation are in progress;
reported results are planned, not yet final.)* The expected contribution is honest
evidence on which readily available signals best flag consequential volume errors,
and how many cases can be safely automated at a defined sensitivity.

**Keywords:** brain tumour MRI; segmentation reliability; volumetric error;
uncertainty; quality control; deep learning
