# Shortcut Learning / Silent Failure in Brain-MRI DL — Prior-Art Map (BraTS & gliomas focus)

**Purpose:** Map what is ALREADY PUBLISHED on shortcut learning / spurious correlations /
dataset artifacts / hidden confounders in brain-MRI deep-learning models (classification AND
segmentation), with special focus on **BraTS** and **gliomas**, so we know what is TAKEN and where
a genuinely under-explored shortcut/silent-failure mode might still exist for this project.

**Date compiled:** 2026-10-23. Survey by web search (arXiv, PubMed/PMC, Nature, IEEE, MICCAI, Springer).
**Honesty caveat:** Absence of a paper in these searches is **NOT** proof of novelty. Several venues
(MICCAI/MIDL workshops, SPIE, regional journals) are poorly indexed by web search. Any "candidate"
below must be re-checked against Google Scholar + the specific challenge papers before we claim it.

---

## 1. Documented shortcuts / spurious features in brain-MRI models

### 1a. Clever Hans via radiologist 2D-slice selection (TAKEN — but NOT BraTS, NOT segmentation)
- **Wallis & Buvat, "Clever Hans effect found in a widely used brain tumour MRI dataset," *Medical Image Analysis* 77:102368, 2022.** https://www.sciencedirect.com/science/article/pii/S1361841522000214 · PubMed: https://pubmed.ncbi.nlm.nih.gov/35063892/
  - Showed high tumour-class accuracy on the popular **Figshare / Cheng 2D T1c dataset** (meningioma/glioma/pituitary) **even with the tumour masked out** — the bias comes from *implicit radiologist input in which 2D slices were selected*. Classic "right answer, wrong reason."
  - **Scope:** 2D **classification** dataset, not BraTS, not a segmentation task. CLOSES the "slice-selection shortcut in brain-tumour classification" candidate.

### 1b. Skull-stripping-induced shortcut (TAKEN — for Alzheimer's T1w, NOT tumour)
- **"Skull-stripping induces shortcut learning in MRI-based Alzheimer's disease classification," *Insights into Imaging*, 2025** (s13244-025-02158-4). https://link.springer.com/article/10.1186/s13244-025-02158-4
  - Skull-stripping applied to T1w MRI acts as an unintended cue (Clever Hans) for AD classifiers.
  - **Scope:** AD classification (ADNI-style structural T1w). CLOSES "skull-strip-as-shortcut for AD classification." Leaves tumour **segmentation** open (see §6).

### 1c. Site/scanner is encoded and exploitable ("disease classifier = secret site classifier") (TAKEN — classification)
- **Souza et al., "Image-encoded biological and non-biological variables may be used as shortcuts in deep learning models trained on multisite neuroimaging data," *JAMIA* 30(12):1925, 2023.** https://academic.oup.com/jamia/article/30/12/1925/7260634 · doi:10.1093/jamia/ocad171
  - 1,880 T1w scans / 41 sites (PD + HC). A CNN predicts **acquisition site** at 85% from raw or intensity-harmonized scans, 54% from morphology alone; disease status and scanner type both contribute to site identifiability — i.e. site is a latent shortcut that harmonization does not remove.
- **"Identifying Biases in a Multicenter MRI Database for Parkinson's Disease Classification: Is the Disease Classifier a Secret Site Classifier?," *IEEE JBHI*, 2024.** https://doi.org/10.1109/jbhi.2024.3352513
  - Directly frames the disease classifier as covertly a site classifier (PD, multicenter).
- **"Effects of MRI scanner manufacturers in classification tasks with deep learning models," *Scientific Reports* 13, 2023.** https://www.nature.com/articles/s41598-023-43715-5 · PMC: https://pmc.ncbi.nlm.nih.gov/articles/PMC10556074/
  - ResNet classifies **manufacturer** (GE/Philips/Siemens) at ~95–99% (ADNI1/2, CALSNIC2, PPMI); big cross-manufacturer performance drop; **ComBat did not fix** disease-task performance — residual manufacturer confound persists.
  - **Scope of all three:** structural/classification (AD, PD), not tumour, not segmentation. CLOSES "site/scanner-as-shortcut in multisite neuro **classification**."

### 1d. Demographic shortcuts (TAKEN — AD classification)
- **"Invisible Attributes, Visible Biases: Exploring Demographic Shortcuts in MRI-based Alzheimer's Disease Classification," arXiv:2509.09558, 2025.** https://arxiv.org/abs/2509.09558
  - Age/sex act as demographic shortcuts in AD classifiers. Not tumour.

### 1e. Defacing as a confound (TAKEN — structural brain-age / atrophy, NOT tumour)
- **"The Influence of Brain MRI Defacing Algorithms on Brain-Age Predictions via 3D CNNs," bioRxiv 2023.** https://www.biorxiv.org/content/10.1101/2023.04.28.538724
- **"Defacing biases visual quality assessments of structural MRI," bioRxiv 2024 / PMC11974683.** https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11974683/
  - Defacing algorithm choice (AFNI/FSL/Pydeface/SPM) systematically shifts 3D-CNN brain-age and atrophy estimates and even human QC ratings.
  - **Scope:** structural brain-age/atrophy, not tumour segmentation. CLOSES "defacing-as-confound for brain-age." Tumour-segmentation angle appears **open** (see §6).

### 1f. General DL-segmentation shortcuts (TAKEN at the generic level — not brain-specific)
- **Lin et al., "Shortcut Learning in Medical Image Segmentation," MICCAI 2024 / arXiv:2403.06748.** https://arxiv.org/abs/2403.06748
  - Two concrete segmentation shortcuts: (i) **clinical annotation markers (calipers)** as cues, and (ii) **zero-padded convolutions + center-cropped training** → boundary/background pixels become a shortcut (lesions are centered, so near-border = background). Demonstrated on non-brain data (ultrasound/skin-type datasets), **not BraTS**.
- **"Causality-inspired Single-source Domain Generalization for Medical Image Segmentation," arXiv:2111.12525 (CVPR 2022).** https://arxiv.org/abs/2111.12525
  - Background/context confounders are learned as domain-specific cues by segmentation nets and break under domain shift. General, not tumour-specific.
- Survey framing: **"Navigating Shortcuts, Spurious Correlations, and Confounders," arXiv:2412.05152, 2024.** https://arxiv.org/abs/2412.05152

---

## 2. BraTS-specific curation/preprocessing that a model could exploit

- **BraTS canonical pipeline** = rigid registration to **SRI24 atlas** + interpolation to **1 mm³ isotropic** + **skull-stripping**. (Confirmed across BraTS challenge papers, e.g. BraTS-MEN 2023 arXiv:2305.07642; BraTS-Africa arXiv:2305.19369.) Every modality is co-registered and resampled — a strong, uniform **source/provenance signature**.
- **Aggressive skull-strip crops extra-axial tumour (TAKEN, meningioma):** up to ~90% of meningioma cases show abutment/cropping at the brain-mask boundary; BraTS-MEN-RT 2024 therefore **dropped skull-stripping** and used **defacing** instead. **"The 2024 BraTS Meningioma Radiotherapy (BraTS-MEN-RT) dataset," *Scientific Data*, 2026.** https://www.nature.com/articles/s41597-026-06649-x — This documents the mask-boundary artifact as a known failure for meningioma; **glioma/BraTS-GLI analogue is less examined.**
- **Data-leakage concern in BraTS** (overlapping cases across editions inflating scores) is noted in challenge-analysis papers (e.g. BraTS-MET 2023 arXiv:2306.00838; BraTS-MEN analysis arXiv:2405.09787) but this is train/test contamination, not a feature-level shortcut.
- **Synthetic / GAN-inpainted content in BraTS:** since 2023 BraTS has a **missing-modality synthesis** task and winning entries use **synthetic tumour inpainting augmentation** ("How we won BraTS 2023… Just faking it!", ResearchGate 378526480; 3D Wavelet Diffusion arXiv:2411.04630). Whether a downstream segmenter can be *shortcut-ed by detectable synthesis fingerprints* is raised as a generation-quality problem, **not shown as an exploited shortcut.**

---

## 3. Site/batch effect & harmonization for brain MRI — tumour-specific?

- **ComBat works for tumour-TYPE classification:** "MRI data harmonization across sites using ComBat enhances classification of meningioma and glioma brain-tumors in dogs," 2022 (ResearchGate 361826484). Harmonization-helps-classification, i.e. site variance is real and consequential for tumour radiomics.
- General ComBat / DeepComBat / Robust-ComBat / Fed-ComBat literature (Nature s41598-025-25400-x; arXiv:2601.14314; arXiv:2603.17968) is **not tumour-segmentation specific** and mostly targets diffusion/structural features.
- **Gap:** The explicit framing *"a BraTS glioma segmentation model's errors are driven by / predictable from site"* is **not something these searches surfaced**. Site-as-shortcut is well established for **classification** (§1c); its translation to **segmentation error / silent failure** on gliomas looks under-reported.

---

## 4. "Clever Hans" / "right for the wrong reason" specific to brain tumour / neuro MRI

- The ONLY clean brain-tumour Clever Hans result found is **Wallis & Buvat 2022** (§1a) — classification, Figshare dataset, slice-selection bias. No equivalent "right-for-wrong-reason" paper found that targets **BraTS glioma segmentation** specifically.

---

## 5. Subgroup / silent-failure findings in brain-tumour models (TAKEN, well documented)

- **Small-tumour silent failure is firmly established:** segmentation Dice/IoU rise monotonically from smallest to largest tumours; failures cluster in low tumour–background contrast, very small lesions, small/absent enhancing tumour or necrosis. (BraTS-METS 2023 arXiv:2306.00838; small-tumour study PMC11817956; fairness/robustness review Frontiers; cross-dataset sequence study arXiv:2608.29944.)
- **Tumour type/grade** significantly affects Dice/IoU/BF-score; **population-specific** models (pediatric, Sub-Saharan BraTS-Africa) generalize unevenly (Nature s41598-026-35627-x; BraTS-GoAT 2026 arXiv:2609.15524).
- **Failure/uncertainty/QC literature** (adjacent to this project's goal of *predicting consequential segmentation errors*):
  - QU-BraTS (MICCAI 2020) arXiv:2112.10074; QCResUNet arXiv:2412.07156; Failure-detection benchmark arXiv:2406.03323; budget-aware QA arXiv:2604.11798; self-assessing unified model arXiv:2511.12801.
  - These predict Dice/flag failures from **uncertainty**, generally **without attributing failures to an identified hidden confounder/shortcut.** Linking a *specific* shortcut to *consequential* (not merely small-tumour) error is the opening.

---

## 6. VERDICT

### TAKEN — do NOT claim as novel
1. **Slice-selection Clever Hans** in the Figshare/Cheng 2D brain-tumour **classification** dataset — Wallis & Buvat 2022.
2. **Skull-stripping-induced shortcut** for **Alzheimer's** T1w classification — Insights Imaging 2025.
3. **Site / scanner / manufacturer = latent shortcut in multisite neuro CLASSIFICATION**, surviving ComBat ("disease classifier = secret site classifier") — Souza 2023 (JAMIA), IEEE JBHI 2024, Sci Rep 2023.
4. **Demographic (age/sex) shortcuts** in AD classification — arXiv:2509.09558.
5. **Defacing-algorithm choice as a confound** for brain-age / atrophy / QC — bioRxiv 2023 & 2024.
6. **Generic segmentation shortcuts** — calipers/annotation markers & **zero-pad + center-crop background shortcut** — Lin et al. MICCAI 2024; background/context confounders in SDG — arXiv:2111.12525.
7. **Aggressive BraTS skull-strip crops extra-axial (meningioma) tumour** — documented and already fixed in BraTS-MEN-RT 2024.
8. **Small-tumour / low-contrast / grade / population silent-failure** in BraTS segmentation — multiple (§5).
9. **ComBat harmonization improves tumour-type classification / site variance is real** — ComBat tumour papers (§3).

### APPEARS UNDER-EXPLORED — candidate (verify before claiming; absence ≠ novelty)
- **C1. Site/scanner-as-shortcut in BraTS glioma SEGMENTATION error (not classification).** Site-shortcut is nailed down for classification (AD/PD), but "a glioma segmenter's *consequential* errors are predictable from / caused by site-scanner provenance" was not found. Most testable candidate; directly aligns with this project (predicting consequential segmentation errors) and modest hardware.
- **C2. Resampling/interpolation + SRI24-registration fingerprint as an exploited shortcut in a BraTS tumour model.** Image-forensics shows resampling leaves detectable periodic signatures (arXiv:1707.00433, 1803.01711), and BraTS forces uniform 1 mm³ + atlas registration — but no paper shown here demonstrates a *tumour model exploiting that provenance fingerprint*. Plausible but speculative; needs native-space vs BraTS-space comparison.
- **C3. Synthetic/GAN-inpainted BraTS content as a detectable shortcut** that biases a downstream segmenter. Raised only as a generation-quality concern, not demonstrated as an exploited shortcut.
- **C4. Defacing-as-shortcut for brain-TUMOUR segmentation** (shown for AD classification and brain-age, not tumour). Marginal, since classic BraTS is skull-stripped rather than defaced; more relevant to the newer defaced BraTS-MEN-RT line.
- **C5. Label-fusion / multi-rater annotation-protocol signatures in BraTS labels as a shortcut.** Not surfaced; under-explored but hard to isolate.
- **C6. Attributing consequential silent failures to an identified hidden confounder** (vs the already-known small-tumour effect). QC/uncertainty work predicts *that* a case fails, rarely *why* in terms of a named shortcut.

**Recommendation:** C1 (and optionally its mechanism C2) is the strongest, most-provable gap on modest
hardware and fits the "predicting consequential segmentation errors" project. Before claiming it,
re-search Google Scholar for "BraTS site/scanner segmentation shortcut," check MICCAI/MIDL 2024-2026
workshop proceedings and the FeTS (Federated Tumor Segmentation) literature, which is the most likely
place a site/segmentation-shortcut result would already live.
