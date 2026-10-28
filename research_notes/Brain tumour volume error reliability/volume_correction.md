# Post-hoc, reference-free volume correction / calibration for medical image segmentation (brain-tumour MRI emphasis, 2019-2026)

Scope note: "reference-free" is used in two senses below and they are kept distinct — (a) *no ground truth at test time* (a correction fitted on labelled training/validation data, then applied blind to new cases), versus (b) *no labelled data at all*. Almost all existing "volume correction" is sense (a). Also distinguished throughout: **correcting a point volume estimate** (turning a raw predicted volume into a debiased number) vs **quantifying an interval/uncertainty** around it (conformal prediction, UQ) — the user's idea is the former.

---

## Q1. Papers that CORRECT or calibrate predicted segmentation VOLUME (not just estimate an interval)

### Takeaway
Volume debiasing of segmentations is an established line of work rooted in the soft-Dice volumetric-bias finding. Two concrete correction mechanisms exist: (i) **post-hoc probability calibration + taking the expected volume** (sum of calibrated voxel probabilities), which is unbiased when calibration error is zero (Popordanoska/Bertels, MICCAI 2021); and (ii) **least-squares regression re-calibration** of the volume-bias and volume-dependent slope, fitted on labelled training folds (Bertels et al., MedIA 2021). Both *correct the point estimate* and are reference-free at test time, but both are population/distribution-level debiasers rather than per-case signed-error predictors.

### Cited Findings

**Foundational — the bias itself**
- Bertels, Eelbode, Berman, Vandermeulen, Maes, Bisschops, Blaschko, "Optimization with soft Dice can lead to a volumetric bias," MICCAI BrainLes / arXiv 1911.02278 (2019/2020). Shows theoretically and on four medical tasks that optimizing with soft Dice introduces a **volumetric bias (systematic over-estimation) that grows with the task's inherent uncertainty**, even while improving Dice — [arXiv](https://arxiv.org/abs/1911.02278)
- The bias is a thresholding/decision-boundary phenomenon: soft-Dice pushes the soft prediction toward a shape that is optimal for the Dice *metric* after thresholding, which is not volume-faithful under uncertainty — [arXiv 1911.02278](https://arxiv.org/pdf/1911.02278)

**Correction mechanism (i): calibration → expected volume**
- Popordanoska, Bertels, Vandermeulen, Maes, Blaschko, "On the relationship between calibrated predictors and unbiased volume estimation," MICCAI 2021 / arXiv 2112.12560. Proves that **if the predictor is calibrated per image, taking the expectation of the per-voxel probability scores (summing the soft map) yields the correct volume**; calibration is *sufficient but not necessary* for an unbiased volume — [arXiv](https://arxiv.org/abs/2112.12560)
- **The absolute value of the volume bias is upper-bounded by the calibration error**; therefore reducing calibration error (e.g. post-hoc temperature scaling) simultaneously reduces volume bias, and zero calibration error gives an unbiased volume — [arXiv 2112.12560](https://arxiv.org/pdf/2112.12560); [MICCAI 2021 daily summary](https://rsipvision.com/MICCAI2021-Thursday/13/)
- Validated with **18 calibration strategies on glioma volume (BraTS 2018) and ischemic stroke lesion volume (ISLES 2018)** — [arXiv 2112.12560](https://arxiv.org/abs/2112.12560)
- Caveat found: convex combinations / ensembles of calibrated classifiers **preserve unbiased volume but do not preserve calibration** — [cs.paperswithcode](https://cs.paperswithcode.com/paper/on-the-relationship-between-calibrated)

**Correction mechanism (ii): regression re-calibration of the volume estimate**
- Bertels, Robben, Vandermeulen, Suetens, "Theoretical analysis and experimental validation of volume bias of soft Dice optimized segmentation maps in the context of inherent uncertainty," Medical Image Analysis (journal version; arXiv 2211.04161). Proposes an **ad-hoc volume analysis with an optional re-calibration step**: a least-squares linear model of the volume-dependent bias ("volume-specificity") and offset is fitted per fold on the **training set (requires GT)** and then applied to correct volumes on the validation set — [arXiv](https://arxiv.org/abs/2211.04161)
- Reported pattern (numbers via automated PDF extraction — treat as approximate/indicative, verify against the paper): soft-Dice U-Net showed large positive volume bias on BraTS vs near-zero for cross-entropy; after regression re-calibration residual bias was largely removed on most datasets but a small significant residual remained on BraTS — [arXiv html 2211.04161](https://arxiv.org/html/2211.04161v1)
- Conclusion: **cross-entropy with soft (expected) volume is close to unbiased without thresholding**, whereas soft-Dice needs correction; correction helps most for high-uncertainty tasks — [arXiv 2211.04161](https://arxiv.org/html/2211.04161v1)

**Threshold / decision-boundary effects on volume**
- No single probability threshold is simultaneously optimal for tumour volume and Dice; lowering the threshold inflates volume, raising it shrinks volume — so thresholded volume is intrinsically biased relative to the expected (soft) volume — [PET DL thresholding, arXiv 2207.01623](https://arxiv.org/pdf/2207.01623)
- Local Temperature Scaling (Ding, Han, Liu, Niethammer, ICCV 2021) calibrates voxel probabilities spatially (per-pixel temperature), relevant because spatially-varying mis-calibration drives boundary/volume error — [BIAG LTS](https://biag.cs.unc.edu/software/local_temperature_scaling/)

### Inferences
- The "raw predicted volume → debiased volume without test-time GT" concept is **already established at the population/distribution level** via two routes (calibrate-then-sum, and regression re-calibration). A reviewer would regard generic "reference-free volume debiasing" as prior art, chiefly Popordanoska 2021 and Bertels 2021.
- Because calibrate-then-sum is literally "take the expected volume from a calibrated soft map," any method that corrects volume via improved calibration is, in effect, a special case already analysed in 2112.12560.

### Gaps
- Exact post-correction effect sizes from Bertels MedIA 2021 are from automated extraction and should be re-checked in the PDF before quoting.

---

## Q2. Does any method predict the SIGNED volume error from reference-free signals and SUBTRACT it, validated against clinically meaningful errors?

### Takeaway
Not in the specific form the project proposes. Existing work removes *systematic/population* bias (a mean offset and a volume-dependent slope) or produces *intervals*; I found **no published method that predicts a per-case signed volume error from reference-free signals (uncertainty maps, soft predictions) and subtracts it to debias that individual case, and then validates the correction against a clinical decision threshold** in brain-tumour MRI.

### Cited Findings
- Bertels 2021 regression re-calibration predicts bias as a function of *predicted volume* (a global curve), not from case-specific uncertainty signals; it is a distribution-level debiaser — [arXiv 2211.04161](https://arxiv.org/html/2211.04161v1)
- Popordanoska 2021 corrects volume via *calibration quality*, not by explicitly regressing a signed error target; the "correction" is implicit in summing calibrated probabilities — [arXiv 2112.12560](https://arxiv.org/abs/2112.12560)
- Structure-wise (whole-object) uncertainty has been used as a proxy to predict the Dice of automated brain-tumour segmentation and to produce **more reliable confidence intervals of tumour volume**, but this is interval/UQ, not point-volume subtraction — Jungo et al., "Analyzing the Quality and Challenges of Uncertainty Estimations for Brain Tumor Segmentation," Front. Neurosci. 2020 — [PMC7156850](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7156850/)
- Reference-free uncertainty signals are empirically weak predictors of local error: an MC-Dropout study on 2D brain-tumour MRI found only weak global uncertainty-error correlation (r ≈ 0.30-0.38) and negligible boundary correlation (|r| < 0.05) — Saumya B., arXiv 2510.15541 (Oct 2025) — [arXiv](https://arxiv.org/abs/2510.15541)
- Conformal-prediction volumetry produces calibrated *intervals* around the automatic volume (reference-free at test time) but does not output a corrected point estimate: Lambert, Forbes, Doyle, Dojat, "Robust Conformal Volume Estimation in 3D Medical Images," MICCAI 2024 / arXiv 2407.19938 — [arXiv](https://arxiv.org/abs/2407.19938); and ConVOLT (Cheung et al.), "Efficient Conformal Volumetry for Template-Based Segmentation," arXiv 2603.00798 (2026) — [arXiv](https://arxiv.org/abs/2603.00798)

### Inferences
- The project's specific contribution — **per-case signed-volume-error regression from reference-free signals, subtracted, and judged by whether it flips/avoids a clinical threshold crossing** — appears to be a genuine white space. The adjacent prior art is either (a) population debiasing or (b) interval UQ.
- The novelty therefore hinges less on "correct volume reference-free" (established) and more on "*per-case* signed-error prediction" + "*clinical-threshold* validation endpoint." Both of those framings are defensible as new; the first framing ("reference-free volume correction") alone is not.

### Gaps
- I did not find any brain-tumour paper that validates a volume correction against a named clinical threshold (e.g. RANO bidimensional/volumetric response cutoffs, or a fixed-ml decision boundary). If the project uses such an endpoint, that strengthens novelty; absence of prior art here is a "did-not-find," not a proof of non-existence.

---

## Q3. Relation to probability calibration (temperature scaling etc.) — does calibrating voxel probabilities correct volume?

### Takeaway
Yes, with a clean theoretical link: volume bias is bounded by calibration error, so post-hoc calibration (temperature scaling / local temperature scaling) plus taking the expected volume is a principled reference-free volume corrector — but only to the extent calibration improves, and calibration is *sufficient, not necessary*, so good volume can occur without good calibration and vice versa.

### Cited Findings
- |volume bias| ≤ calibration error; calibrated-per-image ⇒ expected volume is the true volume (Popordanoska/Bertels 2021) — [arXiv 2112.12560](https://arxiv.org/pdf/2112.12560)
- Post-hoc temperature scaling (temperature fit by minimizing NLL on a held-out ROI) consistently reduces mis-calibration in medical segmentation (reported relative improvements up to ~41% NLL and ~56% ECE in one recent study) — temperature scaling is **post-hoc and reference-free at test time** (temperature fitted on validation) — [WebSearch summary of 2024-26 calibration work]; Local Temperature Scaling, Ding et al. ICCV 2021 — [BIAG](https://biag.cs.unc.edu/publication/dblp-conficcv-ding-hln-21)
- Calibration being *sufficient but not necessary* means a miscalibrated model can still give unbiased volume (over- and under-confident voxels cancel), and calibrating per-pixel does not guarantee the summed volume is right unless calibration holds per image — [arXiv 2112.12560](https://arxiv.org/abs/2112.12560)

### Inferences
- A pure temperature-scaling baseline is the natural *comparator* the project must beat: it is the simplest reference-free volume corrector and is already published. If a learned signed-error corrector does not outperform calibrate-then-sum, the contribution is weak.

### Gaps
- The "up to 41% NLL / 56% ECE" figures come from a search-snippet aggregation, not a fetched primary source; cite only after locating the primary paper. No figure found for how much *volume* (ml) that calibration improvement actually corrects.

---

## Q4. How strong/weak are these corrections empirically, and what are the known limits?

### Takeaway
Corrections reliably remove *systematic* bias in aggregate but are limited: they are curve/offset corrections (not per-case), can leave significant residual bias on the hardest dataset (BraTS), depend on the stationarity of the fitted correction (breaks under distribution shift), and rest on uncertainty signals that are empirically weak at the voxel/boundary level.

### Cited Findings
- Regression re-calibration removed most volume bias across datasets but **left a small, still-significant residual bias on BraTS** after soft-Dice optimization (indicative numbers, auto-extracted) — [arXiv 2211.04161](https://arxiv.org/html/2211.04161v1)
- Soft-Dice bias magnitude **scales with task inherent uncertainty** — the harder/more uncertain the tumour boundary, the larger the uncorrected bias, i.e. correction is most needed exactly where it is least reliable — [arXiv 1911.02278](https://arxiv.org/abs/1911.02278)
- Cross-entropy soft volumes are already near-unbiased, so for CE-trained models the *headroom for volume correction is small* — [arXiv 2211.04161](https://arxiv.org/html/2211.04161v1)
- Conformal/UQ approaches become **overly conservative under covariate/distribution shift**, which is why weighted conformal prediction and deformation-conditioned calibration were introduced — a limit that equally threatens any fitted bias curve — [arXiv 2407.19938](https://arxiv.org/abs/2407.19938); [ConVOLT arXiv 2603.00798](https://arxiv.org/abs/2603.00798)
- Voxel/boundary uncertainty correlates weakly with error (r ≈ 0.3 global, ~0 at boundary), undermining the premise that reference-free uncertainty maps carry enough signal to recover a per-case signed volume error — [arXiv 2510.15541](https://arxiv.org/abs/2510.15541)

### Inferences (incl. the "circularity / marginal" concern the user flagged)
- **Circularity risk:** the same soft prediction/uncertainty that produced the volume is being used to correct the volume. If the network is wrong *and confidently so* (the clinically dangerous case), the reference-free signal is co-degraded with the error, so the correction tends to be small precisely where a large correction is needed. The weak boundary uncertainty-error correlation is direct evidence of this failure mode.
- **Marginality risk:** calibrate-then-sum already captures most of the recoverable systematic bias; a learned signed-error corrector can only add value on the *residual, case-specific* component, which is small and noisy. The project should expect modest ml-level gains and should therefore anchor the claim on *clinical-threshold flips*, not mean volume error, to be meaningful.
- A fitted correction (regression or temperature) is only valid under the distribution it was fitted on; out-of-distribution tumours (the triage-relevant cases) are where it is least trustworthy.

### Gaps
- No primary-source quantification found of how often a reference-free volume correction actually changes a *clinical decision* (threshold crossing) in brain-tumour MRI — this is the specific evidence needed to judge clinical value and appears to be unaddressed in the literature.

---

## Bottom line for the novelty question
- **Reference-free volume correction in the generic sense is NOT novel**: Popordanoska/Bertels MICCAI 2021 (calibrate → expected volume) and Bertels MedIA 2021 (regression re-calibration) both turn a raw predicted volume into a debiased volume without test-time ground truth, and both validate reduced volume bias on brain-tumour (BraTS) data.
- **Reference-free signed-volume correction that is (a) per-case, driven by uncertainty/soft-prediction signals, (b) subtracted to debias the individual case, and (c) validated against a clinical decision threshold — I found no such published method.** That specific combination is the defensible novelty; the bare phrase "reference-free volume correction" is not.
- Required baselines/comparators to establish contribution: cross-entropy soft (expected) volume, post-hoc temperature scaling + expected volume, and Bertels-style regression re-calibration. Beating these on a *clinical-threshold* endpoint (not just mean ml bias) is what would make the idea stand.
