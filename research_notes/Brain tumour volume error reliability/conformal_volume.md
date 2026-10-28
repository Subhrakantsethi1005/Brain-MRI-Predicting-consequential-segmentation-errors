# Conformal / distribution-free guarantees for segmentation VOLUME and for triage/selective-prediction (2023–2026), brain-tumour MRI focus

Scope note for the report writer: throughout, I separate two guarantee types that are easy to conflate.
- **Type A — conformal INTERVAL on a volume value**: "the true volume lies in [l, u] with marginal probability ≥ 1−α." A statement about the estimate.
- **Type B — conformal guarantee on a DECISION / risk**: "the triage/abstention rule has FNR (or error-detection sensitivity) ≤ ε with probability ≥ 1−α." A statement about the action taken. The *candidate idea* (a conformal triage guarantee at the RANO ≥25% threshold) is Type B tied to a specific clinical decision boundary. See the final key question for the gap verdict.

---

## Q1. Lambert et al., "Robust Conformal Volume Estimation in 3D Medical Images" (MICCAI 2024) — what it guarantees, data, and successors

### Takeaway
Lambert et al. is squarely **Type A**: it builds calibrated predictive *intervals* around automatic volume measurements and its contribution is making those intervals robust to covariate shift via *weighted* conformal prediction. It does **not** make any decision/triage-level guarantee and does not touch RANO. The one clear direct successor is ConVOLT (2026), also Type A (tighter intervals), not decision-level.

### Cited Findings
- Authors Benjamin Lambert, Florence Forbes, Senan Doyle, Michel Dojat; early-accepted MICCAI 2024; arXiv:2407.19938 (29 Jul 2024); code at github.com/benolmbrt/wcp_miccai — [arXiv abs](https://arxiv.org/abs/2407.19938v1); [MICCAI 2024 paper page](https://papers.miccai.org/miccai-2024/paper/3051_paper.pdf)
- Guarantee: Conformal Prediction gives "calibrated predictive intervals associated with automatic volume measurements" — i.e. marginal coverage of the *volume value*, not a decision — [arXiv HTML](https://arxiv.org/html/2407.19938v1)
- Core problem: standard CP assumes calibration/test **exchangeability**, violated in medical imaging; they use **weighted conformal prediction** with **density-ratio estimation** to handle **covariate shift** — [arXiv HTML](https://arxiv.org/html/2407.19938v1)
- Method novelty: estimate the density ratio from the **compressed latent representation** of the segmentation model (not raw high-dimensional images) for efficiency — "W-Latent" variant — [arXiv HTML](https://arxiv.org/html/2407.19938v1)
- Nonconformity score: s_i = max(l_i − Y_i, Y_i − u_i), i.e. interval-accuracy score on the scalar volume Y_i — [arXiv HTML](https://arxiv.org/html/2407.19938v1)
- Datasets: (1) synthetic 32×32×32 cubes with spheres under SNR-controlled shift (95% target coverage); (2) **BraTS 2023** glioblastoma + meningioma, multi-sequence MRI (T1/T2/FLAIR/T1ce), 90% target coverage. The modelled shift is **tumour-subtype frequency shift** (GBM vs meningioma) and SNR shift, NOT explicit scanner/site shift — [arXiv HTML](https://arxiv.org/html/2407.19938v1)
- Representative results (coverage restored under shift): synthetic shifted 87.47%→93.39% (standard CP→W-Latent); brain-tumour necrosis sub-region 80.19%→88.88%; edematous sub-region 80.56%→85.52%; interval widths grow to maintain coverage — [arXiv HTML](https://arxiv.org/html/2407.19938v1)

### Successor / citing work
- **ConVOLT — "Efficient Conformal Volumetry for Template-Based Segmentation"**, Cheung et al., arXiv:2603.00798 (2026). A CP framework that conditions calibration on properties of the **deformation field** in template-based segmentation to achieve target coverage with **substantially tighter intervals** than output-space CP baselines. Still **Type A** (volume interval efficiency), not a decision guarantee — [arXiv abs](https://arxiv.org/abs/2603.00798); [CatalyzeX](https://www.catalyzex.com/paper/efficient-conformal-volumetry-for-template)

### Inferences
- Lambert's robustness contribution (weighted CP under covariate shift) is directly reusable as the *interval* layer underneath a decision rule, but the paper itself stops at the interval — the leap to a guaranteed clinical *decision* is not made.
- "Brain-tumour MRI + conformal volume interval" is already occupied by Lambert (BraTS 2023), so pure volume-interval coverage on brain tumour is not novel.

### Gaps
- I could not open the MICCAI HTML page (bot-verification wall) or the npj/Nature full text; dataset-split sizes and exact per-subregion α tables beyond those above were not fully retrieved.

---

## Q2. Conformal / distribution-free methods giving guaranteed error-detection SENSITIVITY or guaranteed FNR for selective-prediction / triage / abstention — in medical imaging

### Takeaway
Multiple 2024–2026 papers now deliver **Type B** guarantees (distribution-free FNR/FDR/false-positive control) for medical image segmentation, built on **Conformal Risk Control (CRC)** and **Learn-then-Test (LTT)**. BUT they control risk at the **pixel/voxel or lesion level within an image** (e.g. "fraction of tumour pixels missed ≤ ε"), NOT at the **case/patient triage-decision level**, and none is tied to RANO or to a case-level error-detector's sensitivity.

### Cited Findings — foundational machinery
- **Conformal Risk Control (CRC)**, Angelopoulos, Bates, Fisch, Lei, Schuster — extends CP from miscoverage to any monotone risk; picks threshold λ so E[risk] ≤ α with finite-sample validity under **exchangeability**; underpins "guarantee that the average fraction of tumour pixels missed is below a specified level" — [Gentle intro / DFUQ, Angelopoulos & Bates](https://arxiv.org/pdf/2107.07511)
- **Learn-then-Test (LTT)**, Angelopoulos et al., arXiv:2110.01052 — calibrates any model so predictions satisfy explicit finite-sample risk guarantees; for each candidate λ tests H0: R(λ)>α via upper confidence bounds with multiple-testing (FWER) correction; no refitting, distribution-free — [arXiv PDF v4](https://arxiv.org/pdf/2110.01052v4); [SOTA summary](https://sotaverified.org/papers/learn-then-test-calibrating-predictive)

### Cited Findings — medical-imaging Type B applications
- **Conformal Lesion Segmentation (CLS)**, Tan, Wang, Duan, Xu, Shen, Shi, Shen, arXiv:2510.17897 (2025). Guarantees **Pr(FNR(t̂) ≤ ε) ≥ 1−α** on fresh test images via **split conformal prediction**: for each calibration case find the max threshold keeping FN proportion ≤ ε, take the (1−α) quantile. Domains: **6 CT benchmarks** — KiTS21 (kidney), LiTS (liver), NIH-LN (lymph node), LIDC-IDRI (lung), MSD-Colon, MSD-Pancreas. Assumption: exchangeability. The guarantee is on the **within-image FN pixel fraction**, i.e. a calibrated decision *threshold*, NOT a case-level triage decision — [arXiv HTML](https://arxiv.org/html/2510.17897v1)
- **FDR/FNR control via Conformal Risk Control** — "Statistical Management/Guarantees of the False Discovery Rate in Medical Instance Segmentation Based on CRC", arXiv:2504.04482 (2025). Calibration-aware loss adjusts segmentation thresholds to a user risk level α so **expected FDR and FNR stay below α w.h.p.**; motivated by the inadequacy of fixed 0.5 thresholds — [arXiv HTML](https://arxiv.org/html/2504.04482v2); [Moonlight review](https://themoonlight.io/review/statistical-guarantees-of-false-discovery-rate-in-medical-instance-segmentation-tasks-based-on-conformal-risk-control)
- **Controlling False Positives in Image Segmentation via Conformal Prediction**, arXiv:2511.15406 (2025). Post-hoc "confidence masks" with distribution-free, **image-level control of false-positive** rate below tolerance via a conformally selected shrink parameter — [arXiv HTML](https://arxiv.org/html/2511.15406v1); [alphaXiv](https://www.alphaxiv.org/abs/2511.15406)
- **Conformal In-Context RCA** — segmentation **quality control** without ground truth: extends Reverse Classification Accuracy with split conformal to give statistical guarantees on estimated segmentation quality (a step toward case-level QC, but guarantees a quality *estimate*, not a triage sensitivity) — [surfaced via QC search](https://arxiv.org/pdf/2602.20151)
- **Glioma-specific CP QC** — work integrating conformal prediction with DL glioma segmentation on UCSF + U-Penn glioma data, selecting conformal threshold from internal/external calibration nonconformity scores, with "risk-aware dynamic threshold" keeping expected FNR/FDR below a user level — closest to our domain but still pixel/voxel-level, not RANO triage — [search-surfaced](https://eprints.gla.ac.uk/396134/1/396134.pdf)

### Inferences
- The exact statistical tool our candidate idea would need (CRC/LTT to bound an error metric at a chosen operating point with finite-sample validity) is mature and already demonstrated in medical segmentation — so the *method* would be an application, not a new theorem.
- What is consistently missing is applying it to a **case-level decision** ("flag this patient's segmentation as needing review so that missed consequential volume errors ≤ ε") rather than a within-image pixel metric.

### Gaps
- Could not confirm whether any CRC/LTT segmentation paper reports **error-detection *sensitivity*** (recall of a flagging system) as the controlled risk — the published ones control FNR/FDR/FPR of the mask, not the recall of a separate detector.

---

## Q3. Evidential / calibrated volume estimation (Guennoun et al., npj Digital Medicine 2026) — guarantee type vs conformal

### Takeaway
Guennoun et al. is **calibration via evidential deep learning ensembles**, NOT conformal. It reports empirically "well-calibrated volume estimates / credible intervals" but provides **no distribution-free finite-sample coverage guarantee** and no decision/triage guarantee — a fundamentally weaker, assumption-dependent form of reliability than conformal CP/CRC.

### Cited Findings
- Guennoun et al., "Segmenting with confidence through uncertainty quantification for brain tumor imaging," **npj Digital Medicine (2026)**. Evidential deep-learning **ensembles** capturing aleatoric-like + epistemic-like uncertainty; meningioma segmentation; trained on 1655 post-contrast T1w MRIs / 788 patients; median Dice 0.93; external validation 353 patients — [Duke CompHealth listing](https://comphealth.duke.edu/publications/segmenting-with-confidence-through-uncertainty-quantification-for-brain-tumor-imaging/); [Research Square preprint](https://assets-eu.researchsquare.com/files/rs-8407421/v1/b33ad0cbad83b353190cad33.html)
- Guarantee type: "**well-calibrated volume estimates**" and "**calibrated volumetric credible intervals**" are evaluation outcomes of Bayesian/evidential UQ — **no mention of conformal prediction, RANO, or decision thresholds**, and no formal coverage/error bound — [Duke CompHealth listing](https://comphealth.duke.edu/publications/segmenting-with-confidence-through-uncertainty-quantification-for-brain-tumor-imaging/)

### Inferences
- Difference from conformal: evidential/Bayesian "credible intervals" are model-/prior-dependent and calibrated only empirically (can break under shift); conformal gives distribution-free, finite-sample **marginal coverage** under exchangeability, and CRC/LTT give distribution-free **risk** control. Guennoun therefore does not compete with the candidate idea on guarantee strength — it is complementary (a good base segmenter + uncertainty source).
- Its Type is effectively "calibrated estimate" — neither a conformal interval (Type A) nor a decision guarantee (Type B).

### Gaps
- Full npj text not retrieved (Nature paywall/Research Square render failed); the exact credible-interval coverage numbers and whether they test under external-site shift were not captured beyond the abstract-level claim of generalizability.

---

## Q4. Has anyone combined a learned case-level error detector WITH a conformal guarantee for segmentation reliability tied to a clinical threshold like RANO ≥25%?

### Takeaway
**No.** I found no paper that (a) trains a case-level error/failure detector and (b) wraps it in a conformal/CRC guarantee on its triage decision, and (c) ties that guarantee to a clinical decision boundary such as RANO ≥25% volume change. Each ingredient exists separately; the combination — and specifically the RANO-threshold tie-in — appears to be an open gap. This supports the candidate idea being a *novel application/assembly* (Type B at a named clinical threshold), not a re-derivation of an existing result.

### Cited Findings
- Explicit RANO + conformal search returned **no** conformal-prediction-at-RANO work; RANO literature is about response-assessment criteria (CR/PR/SD/PD from size change) and automation, with no distribution-free guarantee attached — [RANO progress report, FIU](https://discovery.fiu.edu/display/pub313834); search yielded no CP+RANO paper — [search result](https://cco.amegroups.org/article/view/16078)
- Learned failure/QC detectors exist but **without** conformal guarantees: separate confidence branches, Reverse Classification Accuracy (registration-based), heteroscedastic-regression QC under domain shift — these are empirical detectors — [QC/failure-detection search](https://arxiv.org/pdf/2503.04522v3)
- Decision-oriented deferral exists but **without** conformal guarantees and **not** on brain tumour: Maganti, "Rethinking Uncertainty in Segmentation: From Estimation to Decision," arXiv:2604.13262 (2026) — pixel-level accept/flag/defer on **retinal vessels** (DRIVE/STARE/CHASE_DB1); thresholds tuned on a validation set by F1, **explicitly no conformal/distribution-free guarantee** ("post-hoc measurement, not a contractual guarantee") — [arXiv HTML](https://arxiv.org/html/2604.13262v1)
- Conformal guarantees exist but at pixel/lesion level, **not** case-triage and **not** RANO: CLS (FNR≤ε) and CRC-FDR papers above control within-image masks — [CLS](https://arxiv.org/html/2510.17897v1); [CRC-FDR](https://arxiv.org/html/2504.04482v2)
- Conformal INTERVALS for longitudinal lesion-size/volume exist (adjacent to RANO's size-change logic) but stop at intervals, not a guaranteed triage decision: "Reliability-Centered ... Sparse Longitudinal CT Lesion-Size Forecasting with Conformal Interval Calibration," arXiv:2609.21197 (2026); and conformal bands for randomly-timed biomarker trajectories, arXiv:2511.13911 (2025) — [lesion-size forecasting](https://arxiv.org/pdf/2609.21197); [biomarker conformal bands](https://arxiv.org/pdf/2511.13911)

### Inferences
- The candidate idea = (learned case-level consequential-error detector) × (CRC/LTT guarantee on its missed-error rate) × (operating point defined by RANO ≥25% volume change). Each factor is published independently; their product is not. Novelty therefore rests on the **assembly + the RANO-threshold framing**, which is defensible as "application of an existing method to an unaddressed, clinically meaningful decision," not as new conformal theory.
- A reviewer could argue CLS/CRC-FDR already "do conformal FNR control for segmentation," so the paper must clearly differentiate **case/patient-level triage recall at a named clinical threshold** from **within-image pixel-FNR control**. That distinction is the crux of the novelty claim.

### Gaps
- I cannot prove a negative exhaustively; a very recent (2026) preprint tying CRC to a case-level triage recall at RANO could exist outside the queries I ran. Highest-risk place to double-check before claiming novelty: MICCAI/UNSURE 2025–2026 proceedings and npj Digital Medicine 2026 issues.
- "Error-detection *sensitivity*" as the explicitly conformally-controlled quantity (vs FNR/FDR of a mask) was not found in any source — worth one more targeted check, as it is the exact framing of the candidate idea.

---

## Quick reference table (for the writer)

| Method | Cite | Guarantee type | Exactly what is guaranteed | Assumptions | Domain | Decision/triage-level? |
|---|---|---|---|---|---|---|
| Lambert et al. | MICCAI 2024, arXiv:2407.19938 | A (interval) | Marginal coverage of volume value under covariate shift (weighted CP) | Exchangeability relaxed via density-ratio weighting | BraTS 2023 brain tumour + synthetic | No |
| ConVOLT (Cheung et al.) | arXiv:2603.00798 (2026) | A (interval) | Target coverage with tighter volume intervals (deformation-field conditioning) | Exchangeability | Template-based seg | No |
| CLS (Tan et al.) | arXiv:2510.17897 (2025) | B (risk) | Pr(FNR≤ε)≥1−α of the mask threshold | Exchangeability (split CP) | 6 CT organs (no brain) | Threshold-level, not case-triage |
| CRC-FDR | arXiv:2504.04482 (2025) | B (risk) | Expected FDR & FNR ≤ α w.h.p. | Exchangeability (CRC) | Medical instance seg | No (pixel/instance) |
| False-positive control | arXiv:2511.15406 (2025) | B (risk) | Image-level FP rate ≤ tolerance | Exchangeability | Image seg | No (pixel) |
| CRC / LTT (foundations) | arXiv:2208.xx / 2110.01052 | B (risk) | E[risk]≤α, finite-sample, distribution-free | Exchangeability | General | Method only |
| Guennoun et al. | npj Digit. Med. 2026 | Calibration (evidential) | Empirically calibrated volume estimates/credible intervals | Model/prior-dependent; no finite-sample bound | Meningioma MRI | No |
| Maganti | arXiv:2604.13262 (2026) | None (empirical) | Deferral removes ~80% errors at 25% deferral (observed) | Validation-tuned thresholds | Retinal vessels | Pixel deferral, no guarantee |
| Lesion-size forecasting | arXiv:2609.21197 (2026) | A (interval) | Conformally calibrated longitudinal size intervals | Exchangeability/longitudinal CP | CT lesions | No |
| **Candidate idea** | — | **B at RANO** | **Conformal bound on triage missed-error rate at RANO ≥25%** | Exchangeability (would need shift handling à la Lambert) | **Brain-tumour MRI volume** | **Yes — appears UNOCCUPIED** |
