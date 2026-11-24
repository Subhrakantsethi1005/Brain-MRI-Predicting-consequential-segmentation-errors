# Left-Right Brain Symmetry as a Prior / Attention / Input Signal for Brain-Tumour & Lesion MRI Segmentation (2020-2026 SOTA)

> Scope note for the report writer: "symmetry" is overloaded in this literature. This file concerns ONLY **left-right / contralateral / bilateral anatomical (midsagittal) symmetry** of the brain — i.e. "compare the two hemispheres to find the lesion." Several highly-ranked search hits use "symmetry/asymmetry" to mean something else (symmetric U-Net architecture, channel/spatial asymmetric attention) and are explicitly flagged below as NOT relevant so they are not mistakenly counted as prior art.

## KQ1: Which segmentation methods explicitly use midline/contralateral symmetry as a prior, attention, or extra channel? (gliomas/BraTS AND stroke/MS)

### Takeaway
Hemispheric-symmetry priors are well established, but the distribution is lopsided: in **stroke and MS** the contralateral-comparison prior is common and repeatedly shown to help (reflective registration, symmetry-enhanced attention, cross-hemispheric attention). For **gliomas/BraTS** the idea exists but is thinner and mostly older or unsupervised — a handful of named works (2017 symmetry-encoding, SD-GAN unsupervised, SACA pretraining 2024), rather than a mainstream supervised BraTS method that bakes in a contralateral-attention prior and tops leaderboards.

### Cited Findings — Tumour / glioma / BraTS
- **"Segmenting Brain Tumors with Symmetry"** (Zhang, Zhu, Willke; NIPS ML4H Workshop, 2017; arXiv:1711.06636). Encodes brain symmetry directly into an existing SOTA medical segmentation network; premise: "a healthy human brain is symmetric at a high level of abstraction, and the high-level asymmetric parts are more likely to be tumor regions." Evaluated on a brain-tumour-segmentation-challenge dataset (BraTS); reports more efficient feature extraction vs baseline. Foundational, pre-2020. — [arXiv](https://arxiv.org/abs/1711.06636)
- **SD-GAN — "Unsupervised Brain Tumor Segmentation using a Symmetric-driven Adversarial Network"** (Univ. of Sydney thesis / associated publication). A GAN learns a non-linear mapping between left and right brain images to model the manifold of *normal* symmetry variation; tumours are segmented from high **reconstruction error** where the brain fails to be symmetric. Unsupervised. Datasets: BraTS 2012 and 2018. Reported: best among unsupervised methods, within <3% Dice of supervised U-Net. — [USyd](https://ses.library.usyd.edu.au/handle/2123/25106)
- **SACA / SA-Swin — "Symmetry Awareness Encoded Deep Learning Framework for Brain Imaging Analysis"** (Wang et al.; MICCAI 2024; arXiv:2407.08948). Symmetry-Aware Cross-Attention (SACA) module does cross-attention between an original 3D volume and its mirror (flipped) volume; a Symmetry-Aware Head (SAH) proxy task + contrastive pretraining on a large 3D brain dataset (Swin transformer backbone). Improves downstream **classification and lesion segmentation** on multi-center MRI. Code: github.com/bitMyron/sa-swin. — [arXiv](https://arxiv.org/abs/2407.08948); [MICCAI](https://papers.miccai.org/miccai-2024/750-Paper2579.html)

### Cited Findings — Stroke (symmetry priors common here)
- **Reflective registration** (Raina, Yahorau, Schmah; 2019; arXiv:1907.08196). Registers an image to its mirrored version (reflective registration) to find homologous contralateral voxels; adds a **patch around the homologous voxel as extra input features** to a CNN. Task: ischemic stroke lesion segmentation, multimodal MRI, ISLES 2015 SISS. Nonlinear reflective registration gave **+13 and +9 Dice points** over two baseline CNN architectures; affine helped less. — [arXiv](https://arxiv.org/abs/1907.08196)
- **SEAN — Symmetry-Enhanced Attention Network** (Liang, Han, Li, Cheng, Li, Wang, Yu; MICCAI 2021; arXiv:2110.05039). Transforms input NCCT into a "standard space where brain tissue is bilaterally symmetric," then a U-shaped net with symmetry-enhanced attention captures long-range context from the **opposite side** of the image. Task: acute ischemic infarct segmentation (CT, not MRI). Reports outperforming symmetry-based SOTA on Dice and infarct localization. — [arXiv](https://arxiv.org/abs/2110.05039)
- **AsymFeX** (Shah, Sundaresan; arXiv:2608.19769, Aug 2026). AsymFeX module compares each voxel to its **true contralateral counterpart within a local 3×3×3 neighborhood** via cross-hemispheric attention + feature-disparity estimation + dual-scale gating (handles large and small infarcts). Two-stage: first corrects head tilt to the mid-sagittal plane. Task: acute ischemic stroke segmentation, generalizes across NCCT/MRI modalities and stroke stages. Datasets: AISD, ATLAS v2.1, ISLES'24. AISD: 0.6796 Dice, HD95 23.53 mm, AVD 7.69 mL. Code: biomedia-lab/AIS-detection. — [arXiv](https://arxiv.org/abs/2608.19769)

### Cited Findings — MS lesions
- Symmetry/asymmetry features are an established prior in MS lesion segmentation: methods add **measures of asymmetry of typical lesions** and long-range contralateral comparison as features (multi-channel T1/T2/FLAIR + spatial prior), reporting statistically significant Dice improvements (lineage of Geremia et al. spatial decision forests for MS lesions, MICCAI 2010). Asymmetry index between a lesion and contralateral normal-appearing white matter (NAWM) quantifies lesion asymmetry. — [Spatial decision forests, MICCAI 2010](https://www.nmr.mgh.harvard.edu/publications/journal_articles/4751)

### Inferences
- The contralateral-comparison prior is treated almost as standard practice for **stroke/MS**, where lesions are subtle/low-contrast and the healthy side is a reliable reference. For **gliomas** the enthusiasm is weaker because tumours are already high-contrast on multimodal MRI, so the marginal value of a symmetry channel is smaller and less explored in modern supervised pipelines.

### Gaps
- No single modern (2022-2026) supervised BraTS leaderboard method was found whose *primary* novelty is a hemispheric-symmetry attention prior; the strongest glioma entries (SACA 2024) frame symmetry as a **pretraining** signal rather than an in-model segmentation prior.

## KQ2: "Symmetry-aware" / "asymmetry-attention" networks — names, mechanism, datasets, gains

### Takeaway
Named hemispheric-symmetry networks exist: SEAN, AsymFeX, SACA/SA-Swin, SD-GAN, and the 2017 symmetry-encoding net. Most report gains, but stroke/CT examples dominate and glioma-specific supervised gains are sparse.

### Cited Findings
- SEAN (symmetry-enhanced attention, long-range opposite-side context; stroke CT; MICCAI 2021) — reports Dice + localization gains over symmetry-based SOTA. — [arXiv](https://arxiv.org/abs/2110.05039)
- AsymFeX (cross-hemispheric attention, voxel-to-contralateral disparity; stroke, multi-modality; 2026) — AISD Dice 0.6796; cross-dataset generalization claimed. — [arXiv](https://arxiv.org/abs/2608.19769)
- SACA / SA-Swin (symmetry-aware cross-attention between volume and its mirror; pretraining proxy; MICCAI 2024) — improved classification + lesion segmentation on multi-center MRI. — [arXiv](https://arxiv.org/abs/2407.08948)
- SD-GAN (symmetric-driven adversarial, reconstruction-error from asymmetry; BraTS 2012/2018, unsupervised) — best unsupervised, <3% below supervised U-Net. — [USyd](https://ses.library.usyd.edu.au/handle/2123/25106)

### IMPORTANT — false positives to exclude (NOT hemispheric symmetry)
- **CASPIANET++** (Liew et al., arXiv:2107.04099, 2021). "Asymmetric attention" here = **channel-wise and spatial-wise asymmetric attention** (treating channel/spatial dims differently), NOT left-right brain symmetry. BraTS 2020, WT 91.19 / TC 87.6 / ET 81.03 Dice. Do not count as a contralateral-symmetry method. — [arXiv](https://arxiv.org/abs/2107.04099)
- **"A Symmetrical Approach... Threefold Attention"** (Symmetry journal, 2023, DOI 10.3390/SYM15101912). "Symmetrical" refers to the **symmetric U-Net architecture** and mirrored residual structure, NOT hemispheric comparison. Exclude as prior art. — [DOAJ](https://doaj.org/article/4fa0824ca9d74650ac0d17f549d11ff0)

### Gaps
- Could not confirm from abstracts the exact Dice deltas attributable to the symmetry module alone (ablation numbers) for SEAN and SACA.

## KQ3: How is the midline/symmetry plane obtained, and failure modes?

### Takeaway
Three families: (a) explicit registration to a mirrored copy (reflective/nonlinear registration), (b) learned transform to a canonical symmetric "standard space," (c) classical/atlas midsagittal-plane (MSP) extraction. The recognized failure mode is exactly the one a tumour prior cares about: pathology that is itself asymmetric (mass effect, midline shift, edema, tumours crossing midline) degrades or biases MSP/symmetry estimation.

### Cited Findings
- **Reflective/nonlinear registration** to the mirror image to define homologous contralateral voxels (Raina et al. 2019). — [arXiv](https://arxiv.org/abs/1907.08196)
- **Learned transform to symmetric standard space**: SEAN automatically transforms the CT into a bilaterally-symmetric standard space before attention (MICCAI 2021). — [arXiv](https://arxiv.org/abs/2110.05039)
- **Tilt correction to the anatomical mid-sagittal plane** as an explicit first stage (AsymFeX, 2026). — [arXiv](https://arxiv.org/abs/2608.19769)
- **Flip/mirror as implicit plane**: SACA simply flips the 3D volume and cross-attends original vs flipped (MICCAI 2024). — [arXiv](https://arxiv.org/abs/2407.08948)
- **Classical MSP extraction** is surveyed (Liu et al., "Symmetry plane detection in brain image analysis: A survey", PolyU) and dates to Prima/CMU work on "Automatic bilateral symmetry (midsagittal) plane extraction from pathological 3D neuroradiological images" (SPIE 1998). — [PolyU survey](https://research.polyu.edu.hk/en/publications/symmetry-plane-detection-in-brain-image-analysis-a-survey/); [SPIE 1998](https://www.ri.cmu.edu/?p=14577)
- **Failure modes (explicit):** MSP detection "was very sensitive to asymmetry in the 3D images and could not deal with pathological images"; tumours cause **mass effect** (diseased tissue displaces healthy tissue) and radiometric asymmetry in adjacent normal structures due to **edema**, making accurate MSP localization harder exactly when a lesion is present. — [USPTO/Google Patents US7409085](https://patents.google.com/patent/US7409085); search synthesis of MSP survey

### Inferences
- A symmetry prior for tumours faces a chicken-and-egg problem: the very asymmetry you exploit also corrupts the plane estimate. Methods that *learn* the symmetric space (SEAN) or operate on a *local* contralateral neighborhood with soft disparity (AsymFeX) are plausibly more robust to midline shift than rigid global reflection, but none of the sources quantified robustness specifically under large glioma mass effect.

### Gaps
- No source gave a quantitative breakdown of symmetry-prior accuracy for **midline-crossing gliomas** vs confined ones; this failure mode is acknowledged qualitatively, not benchmarked.

## KQ4: Remaining gaps — what is NOT yet done with symmetry for brain-tumour segmentation?

### Takeaway
The strongest unmet combination is: a **hemispheric cross-attention prior used as an in-model signal for fine supervised glioma segmentation, fused with multimodal MRI cues, robust to mass effect/midline shift, in a fast/cascade setting.** Each piece exists somewhere, but not together for tumours.

### Cited Findings / structured gap map
- **Symmetry used for detection/coarse localization or anomaly reconstruction, not fine multi-class glioma segmentation:** SD-GAN uses asymmetry→reconstruction error (unsupervised, coarse), not fine WT/TC/ET labeling. — [USyd](https://ses.library.usyd.edu.au/handle/2123/25106)
- **Symmetry as pretraining, not as an in-model segmentation prior:** SACA encodes symmetry during self-supervised pretraining, then fine-tunes; the symmetry signal is not an explicit attention branch at inference for tumour segmentation. — [arXiv](https://arxiv.org/abs/2407.08948)
- **Strong cross-hemispheric attention modules are built for stroke, not glioma:** SEAN (CT infarct) and AsymFeX (ischemic stroke) are the most developed contralateral-attention mechanisms but neither targets multimodal glioma BraTS. — [SEAN](https://arxiv.org/abs/2110.05039); [AsymFeX](https://arxiv.org/abs/2608.19769)
- **Not combined with multimodal cues as a dedicated prior:** no found glioma method fuses a contralateral-symmetry attention branch with the T1/T1c/T2/FLAIR multimodal fusion that defines BraTS SOTA.
- **Not in a fast/cascade setting:** cascade BraTS works (e.g. cascaded 3D U-Net with pre-activation residual SE attention, 2025) do coarse→fine but use architectural/SE attention, **not** hemispheric symmetry as the coarse localizer. — [Univ. of Ghana](https://pure.ug.edu.gh/en/publications/a-cascaded-3d-unet-with-pre-activation-residual-se-attention-for-/)

### Inferences (novelty judgment for the parent project)
- "Compare the two hemispheres to find the lesion" is **not novel as a concept** — it is textbook for stroke/MS and has >1 glioma instantiation since 2017.
- However, a **symmetry-driven attention prior specifically for supervised multi-class glioma segmentation**, designed to be (i) an explicit in-model attention branch (not just pretraining or reconstruction), (ii) fused with multimodal MRI, (iii) robust to mass-effect/midline-crossing, and (iv) usable in a fast cascade, appears **under-explored and defensible as a contribution** — the novelty lives in the *combination and the tumour-specific robustness*, not in the hemispheric-comparison idea itself. Framing claims around "first to do X with symmetry for gliomas" would be risky; framing around a specific mechanism + robustness-under-mass-effect + multimodal fusion is more defensible.

### Gaps
- No systematic ablation in the literature isolating how much a symmetry prior adds for gliomas specifically (vs stroke) — the parent project could contribute exactly this evidence.
- Did not locate a 2025-2026 supervised BraTS paper whose headline is a contralateral-attention prior; absence is suggestive of a gap but is not proof none exists (search, not exhaustive review).
