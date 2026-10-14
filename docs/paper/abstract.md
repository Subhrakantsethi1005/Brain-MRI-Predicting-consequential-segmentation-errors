# Abstract — BioAI-2026 submission

> ~285 words (limit 300) · 6 keywords (max 6) · Theme 2: Health, Pharmaceutical
> & Forensic Sciences. Reports completed preliminary results honestly.
> **ACTION NEEDED: replace the author line with your name(s) and affiliation.**

**Predicting Consequential Volume Errors in Automated Brain-Tumour MRI Segmentation**

*[Author Name(s)]¹, [Supervisor/Co-author]¹*
*¹[Department, Institution, City, Country] — [corresponding email]*

Tumour volume measured from brain MRI guides the assessment of glioma progression
and treatment response, yet automated segmentation occasionally mis-estimates
volume enough to mislead clinical interpretation. Safe large-scale use therefore
requires knowing, for each scan, whether an output can be trusted. Existing
reliability methods largely relate uncertainty to overlap metrics such as the Dice
coefficient rather than to volume error, seldom define error against a pre-specified
clinical threshold, and are rarely framed as an operational triage task.

We study segmentation reliability as the case-level prediction of *consequential
volume error*. Without introducing a new segmentation architecture or uncertainty
method, we take a standard 3D U-Net and ask whether simple, interpretable models can
predict—from the model's own stochastic behaviour (Monte-Carlo dropout with test-time
augmentation)—when an output's whole-tumour volume error exceeds a clinically
motivated threshold (≥25% and ≥1 mL) fixed before evaluation. Case-level features
spanning uncertainty, inter-prediction disagreement, and boundary/shape are compared,
using logistic regression and gradient boosting, against predicted-volume-only and
standard-uncertainty baselines, with patient-level data splits.

In a preliminary study on publicly available, expert-annotated MRI, the segmenter
reached whole-tumour Dice 0.81. Reference-free features predicted consequential volume
errors with AUROC ≈ 0.88, clearly exceeding the trivial baseline; their advantage over
standard uncertainty was positive but not statistically significant on the small test
set, except for severe (≥40%) errors, where prediction-disagreement significantly
outperformed uncertainty (p = 0.03). At 90% sensitivity, roughly half of cases were
retainable for automation with about 6% residual error; combining all features reduced
performance. These results provide an honest, reproducible triage baseline and motivate
validation on larger data. This is a research pipeline, not a clinical decision system.

**Keywords:** brain tumour MRI; segmentation reliability; volumetric error; uncertainty; quality control; deep learning
