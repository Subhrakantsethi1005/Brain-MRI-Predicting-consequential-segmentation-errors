# Reference-free, uncertainty-based case-level prediction of VOLUME error in brain-tumour MRI segmentation (2023–2026 SOTA)

*Scope note: the crux throughout is distinguishing methods that target VOLUME error (absolute/relative volume difference, volumetric confidence intervals, tumour-burden change) from the overwhelming majority that target Dice/overlap (DSC, Hausdorff). Foundational pre-2023 work is marked as such; it is included because the 2023–2026 literature is almost entirely built on it.*

## Q1. Which papers do reference-free / no-ground-truth CASE-LEVEL QC for segmentation, and do any target VOLUME error specifically rather than Dice/overlap?

### Takeaway
A mature body of reference-free, per-case QC exists, but it overwhelmingly predicts **Dice/overlap** (RCA, Robinson, QU-BraTS, Jungo subject-level aggregation). The single clearest example that targets **volume** is Eaton-Rosen et al. 2018 — and it predicts volumetric *uncertainty (error bars)*, not a binary case-level "consequential volume-error" flag. No located paper does reference-free case-level prediction of *consequential volume error against a clinical threshold* for brain tumour.

### Cited Findings
- **Reverse Classification Accuracy (RCA)** — Valindria et al., *IEEE TMI* 2017 (foundational). Predicts segmentation quality per-case with NO ground truth by training a "reverse classifier" on the predicted mask as pseudo-GT and evaluating it against a small reference DB with GT; predicts **DSC (overlap)**. Reported 99% accuracy classifying low/high quality on 400 scans, 95% on 4800 scans. Framed for per-case QC in large-scale population imaging (UK Biobank). — [arXiv 1702.03407](https://arxiv.org/abs/1702.03407); [PMC6416857](https://pmc.ncbi.nlm.nih.gov/articles/PMC6416857)
- **Robinson et al. "Real-time Prediction of Segmentation Quality"** — *MICCAI* 2018 (foundational). CNN trained on 12,880 samples predicts **per-case DSC**; MAE 0.03 on 1,610 test samples, 97% binary (low/high quality) accuracy. In a no-manual-annotation scenario, DSC predicted from RCA-derived pseudo-quality gave MAE 0.14, 91% accuracy. Enables in-scanner feedback. Target is overlap, not volume. — [arXiv 1806.06244](https://arxiv.org/abs/1806.06244); [DeepAI](https://deepai.org/publication/real-time-prediction-of-segmentation-quality)
- **Robinson et al. UK Biobank cardiac QC** — *J. Cardiovascular Magnetic Resonance* 2019 (foundational). RCA-based per-case discrimination of successful vs failed segmentation; 99% accuracy on initial 400 scans. Overlap-based. — [arXiv 1901.09351](https://arxiv.org/pdf/1901.09351)
- **QU-BraTS (Mehta et al.)** — *MELBA (J. Machine Learning for Biomedical Imaging)* 2022; from MICCAI BraTS 2019/2020 uncertainty task. The QU-BraTS score is **voxel-level and overlap-based**: it combines three AUCs — DSC vs uncertainty-threshold, filtered-true-positive ratio, filtered-true-negative ratio — rewarding confident-correct / unconfident-incorrect voxels. It does **not** address volume error. It *ranks uncertainty methods*, and found segmentation quality and uncertainty quality are complementary/independent (teams good at one are not necessarily good at the other, across 14 teams). Reference-free at test time. — [arXiv 2112.10074](https://arxiv.org/abs/2112.10074); [PMC10060060](https://pmc.ncbi.nlm.nih.gov/articles/PMC10060060)
- **Jungo, Balsiger & Reyes "Analyzing the Quality and Challenges of Uncertainty Estimations"** — *Frontiers in Neuroscience* 2020 (foundational, brain tumour). Shows voxel-wise uncertainty is heavily **miscalibrated for direct error localisation**, but when **aggregated at the subject level it becomes a reliable predictor of overall segmentation failure** — the canonical "aggregate voxel uncertainty → case-level flag" result. Quality depends strongly on training-set size. Target is failure/overlap, not volume. — [doi:10.3389/fnins.2020.00282](https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2020.00282/full); [PMC7156850](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7156850/)
- **Eaton-Rosen, Bragman, Bisdas, Ourselin, Cardoso "Towards safe deep learning: accurately quantifying biomarker uncertainty"** — *MICCAI* 2018; BraTS 2017 (285 glioma subjects). **The volume-targeted reference-free method.** Converts voxel-wise MC-dropout uncertainty into **calibrated volumetric confidence intervals** for tumour volume (Active/Core/Whole). Key honest caveat: naive volume variance across stochastic forward passes was "wholly inadequate"; they needed voxel-quantile CDF construction + histogram-equalisation affine calibration on validation percentiles so 95% CIs contain GT volume. Reference-free at test (only train/val for calibration). Mean Dice 0.79–0.86. CIs stayed valid under synthetic noise. **No clinical threshold.** — [arXiv 1806.08640](https://arxiv.org/abs/1806.08640); [ar5iv](https://ar5iv.labs.arxiv.org/html/1806.08640)
- **Ma et al. "Medical AI Encodes a 'Feeling of Error': Verifying Cancer Segmentation via Internal Concepts"** — arXiv, submitted Sep 2026. Reference-free **case-level failure detection** using Sparse-Autoencoder internal concepts (failures = fewer active concepts, lower activation magnitude); classifier flags failures while preserving segmentation quality. Evaluated on prostate, pancreatic and **brain** cancer (abstract implies MSD-style data). Targets segmentation accuracy generally — **does not isolate volume vs Dice**; no clinical threshold. — [arXiv 2609.08879](https://arxiv.org/abs/2609.08879)

### Inferences
- The field's default QC target is DSC/overlap; "volume error" is addressed almost exclusively via *uncertainty error-bars* (Eaton-Rosen lineage), not via a reference-free *classifier of consequential volume error*. This is a genuine opening for a "reference-free consequential volume-error triage" framing.
- QU-BraTS, despite being the brain-tumour uncertainty benchmark, is structurally unsuited to the volume question: it scores voxel-overlap under thresholding and ranks methods, not cases.

### Gaps
- Could not confirm whether the "Feeling of Error" paper's brain results report any volume-specific metric (abstract-level only; full-text metrics not retrieved).

## Q2. Has anyone framed the task against a PRE-SPECIFIED clinical threshold (e.g. RANO ≥25% volume change) and reported it as an operational TRIAGE outcome (fraction automatable at fixed error-detection sensitivity)?

### Takeaway
No located paper combines all three elements (reference-free + pre-specified clinical volume threshold + fraction-automatable-at-fixed-sensitivity triage) for brain tumour. Clinical-threshold volume work exists but validates agreement against manual readings (not reference-free QC); deferral/triage framings exist but are pixel-level, retinal, and threshold-free. This specific framing appears **unclaimed**.

### Cited Findings
- **Evaluating automated longitudinal tumour measurements for glioblastoma response assessment** — *Frontiers in Radiology* 2023. Uses RANO-style progression thresholds on automated volumes (HD-GLIO, BraTumIA). Tumour-volume trend agreement vs expert bidimensional: HD-GLIO 81.1%, BraTumIA 79.7%. BraTumIA best matched expert time-to-progression at the recommended RANO threshold. Conclusion: expert supervision / manual correction still required — i.e. it measures agreement, **not** a reference-free flag of volume error. — [doi:10.3389/fradi.2023.1211859](https://www.frontiersin.org/articles/10.3389/fradi.2023.1211859/full)
- **AutoRANO / repeatability** (same literature cluster): automated FLAIR, contrast-enhancing, and AutoRANO volumes showed high repeatability (ICC 0.986/0.991/0.977) and manual-vs-auto agreement (ICC 0.915/0.924/0.965); longitudinal-change ICCs 0.917/0.966/0.850. Threshold-anchored but reference-dependent (compares to manual). — [doi:10.3389/fradi.2023.1211859](https://www.frontiersin.org/articles/10.3389/fradi.2023.1211859/full)
- **EASE (Erasmus Automated SEgmentation), clinical implementation for low-grade glioma volume quantification** — *Front. Medicine* 2021. Explicitly keeps **radiologist visual QC** in the loop; the stated main risk is incorrect segmentation → incorrect volume. Demonstrates clinical need for volume-error QC but provides no automated reference-free detector. — [PMC8523989](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8523989/); [Front Med 2021](https://www.frontiersin.org/journals/medicine/articles/10.3389/fmed.2021.738425/full)
- **Maganti "Rethinking Uncertainty in Segmentation: From Estimation to Decision"** — arXiv, Apr 2026. Frames QC as a two-stage estimation→**deferral decision**; confidence-aware deferral rule; reports an operational curve: "removes up to 80% of segmentation errors at only 25% pixel deferral." BUT: **pixel-level** error (not volume), **retinal vessels** (DRIVE/STARE/CHASE_DB1, no brain), no clinical threshold. Closest analogue to a "fraction automatable at fixed budget" outcome. — [arXiv 2604.13262](https://arxiv.org/abs/2604.13262)
- Secondary search surfaced a deferral result (source paper unidentified): "confidence-aware deferral dominates at low review budgets (5–10%), the regime most relevant for clinical workflows, while adaptive thresholding wins at higher budgets (20–30%)." — [WebSearch-surfaced, primary source not confirmed](https://arxiv.org/pdf/2604.13262)

### Inferences
- The "fraction-automatable-at-fixed-sensitivity" triage outcome is established *methodologically* (deferral curves) but has not been instantiated for brain-tumour **volume** error against a RANO-type threshold. A framing that ties reference-free case-level volume-error detection to RANO ≥25% and reports automatable fraction at fixed sensitivity would, on this evidence, be novel.

### Gaps
- Could not find any brain-tumour paper reporting a deferral/triage operating curve keyed to a volume-change clinical threshold. Absence of evidence, searched multiple phrasings — report-writer should treat as "no claim found," not "proven absent."
- The 5–10%/20–30% budget quote came via search snippet; its exact source paper was not confirmed by direct fetch.

## Q3. Aggregating voxel uncertainty (MC-dropout, ensembles, TTA) to a case-level reliability score for volume, and documented limitations?

### Takeaway
Subject-level aggregation of voxel uncertainty is the standard route to a case-level reliability score and works for failure detection, but the documented limitations are serious: naive volume variance is inadequate and needs explicit calibration; voxel uncertainty is miscalibrated at subject level; and (newest result) calibration does not imply good decisions, with MC-dropout confidence specifically called unreliable.

### Cited Findings
- **Jungo et al. 2020**: voxel uncertainty miscalibrated for localisation but aggregated subject-level uncertainty reliably predicts segmentation failure; dependent on training-set size. — [doi:10.3389/fnins.2020.00282](https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2020.00282/full)
- **Eaton-Rosen et al. 2018**: MC-dropout per-pass volume variance was "wholly inadequate" for CIs that cover GT volume; required voxel-quantile spatial-correlation modelling + affine histogram-equalisation calibration. Demonstrates aggregation to a *volume* reliability estimate is non-trivial. — [ar5iv 1806.08640](https://ar5iv.labs.arxiv.org/html/1806.08640)
- **Wong, Sarikaya, Zucker, De Kamps, Ravikumar "Confidence is Not Reliability: Rethinking MC Dropout in Brain Tumour Segmentation"** — arXiv, Jun 2026. Core negative result: MC-dropout confidence does **not** track true reliability; produces high-confidence predictions that mask failures. Addresses case-level reliability at the volume (3D scan) level, departing from Dice-only focus. — [arXiv 2606.19300](https://arxiv.org/abs/2606.19300)
- **Maganti 2026**: "Calibration improvements do not translate to better decision quality" — standard uncertainty/calibration metrics misalign with deferral utility (compares MC-dropout vs TTA). — [arXiv 2604.13262](https://arxiv.org/abs/2604.13262)
- General subject-level framing (background): uncertainty methods tend to be well-calibrated at **dataset** level but miscalibrated at **subject** level, limiting error localisation; voxel uncertainty aggregated to subject level is useful for detecting failed segmentations. — [Frontiers / Jungo lineage](https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2020.00282/full)

### Inferences
- Across sources the consistent message is: aggregation can yield a usable case-level *reliability/failure* flag, but mapping it specifically and quantitatively to *volume error* requires dedicated calibration (Eaton-Rosen) and cannot be assumed from raw MC-dropout confidence (Wong 2026, Maganti 2026).

### Gaps
- No head-to-head benchmark located that compares MC-dropout vs deep ensembles vs TTA specifically for predicting *volume* error at case level in brain tumour (existing comparisons target overlap or pixel error).

## Q4. Acknowledged open problems / negative results (2024–2026)

### Takeaway
The 2024–2026 literature is increasingly self-critical: MC-dropout confidence is unreliable, calibration gains don't yield better triage decisions, and subject-level/volume-specific reference-free QC against clinical thresholds remains essentially open. Positive momentum is in internal-signal (mechanistic-interpretability) failure detectors and decision-theoretic deferral framings.

### Cited Findings
- MC-dropout confidence ≠ reliability in brain-tumour segmentation; high confidence can mask failure (Wong et al. 2026). — [arXiv 2606.19300](https://arxiv.org/abs/2606.19300)
- Better calibration does not improve deferral/decision quality (Maganti 2026). — [arXiv 2604.13262](https://arxiv.org/abs/2604.13262)
- Subject-level miscalibration and limited error localisation remain unresolved from the foundational Jungo 2020 result through to 2026 work. — [Frontiers 2020](https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2020.00282/full)
- Emerging alternative to output-based uncertainty: internal-concept ("feeling of error") detectors claim to outperform output-based failure detection (Ma et al. 2026) — signals the community views output-probability uncertainty as insufficient. — [arXiv 2609.08879](https://arxiv.org/abs/2609.08879)
- Clinical-deployment papers (EASE 2021; glioblastoma longitudinal 2023) still require human visual QC / manual correction of volumes, i.e. the volume-QC automation gap is openly acknowledged in practice. — [PMC8523989](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8523989/); [Front Radiol 2023](https://www.frontiersin.org/articles/10.3389/fradi.2023.1211859/full)

### Inferences
- Taken together, the strongest defensible gap for a new paper: reference-free, case-level detection of *consequential volume error* (tied to a pre-specified clinical threshold such as RANO ≥25% tumour-burden change) reported as an operational triage outcome (automatable fraction at fixed error-detection sensitivity) is **not claimed** in the located 2023–2026 brain-tumour literature. Adjacent components each exist (volume error-bars: Eaton-Rosen; subject-level flagging: Jungo; deferral curves: Maganti; MC-dropout critique: Wong) but have not been combined for this target.

### Gaps
- No systematic review specifically of *volume-error* reference-free QC in brain tumour was located (reviews exist for uncertainty/QC broadly). 
- Full-text quantitative results for the two 2026 arXiv preprints (2606.19300, 2609.08879) were only partially accessible (binary PDFs); venue/peer-review status unconfirmed — treat as preprints.
