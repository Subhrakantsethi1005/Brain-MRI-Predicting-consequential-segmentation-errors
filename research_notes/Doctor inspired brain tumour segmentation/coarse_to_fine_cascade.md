# Coarse-to-Fine / Cascade / Localize-then-Segment ("Glance then Zoom") for Brain-Tumour MRI Segmentation

Scope: brain-tumour MRI segmentation, 2019-2026, with foundational pre-2019 work marked. Focus on
(a) what cascaded/two-stage methods exist and whether they are standard, (b) whether any frame stage-1 as
a FAST glance/saliency step and report SPEED/latency/FLOPs (not just accuracy), (c) what drives the coarse
stage (learned proposal vs thresholding vs attention vs clinically-inspired/label-free saliency), and
(d) how saturated the idea is and what would make it a real contribution.

---

## Q1. What cascaded / two-stage / coarse-to-fine brain-tumour methods exist, and are they standard?

### Takeaway
Coarse-to-fine cascading is one of the dominant, essentially textbook paradigms in brain-tumour MRI
segmentation. Multiple BraTS challenge winners and the reference baseline (nnU-Net) ship a cascade. The
idea "decompose into a coarse stage then refine" is standard and cannot carry a paper as a headline novelty
on its own.

### Cited Findings (foundational, marked)
- **Wang et al. 2017 — Cascaded Anisotropic CNNs (WNet/TNet/ENet).** FOUNDATIONAL. Cascade of three FCNs that
  decomposes multi-class segmentation into a hierarchy of binary problems (whole tumour -> tumour core ->
  enhancing core); each stage's output region is cropped/fed to the next. BraTS 2017 validation Dice 0.7859
  (ET), 0.9050 (WT), 0.8378 (TC). Uses anisotropic + dilated convolutions, residual connections, multi-scale
  prediction. MICCAI BrainLes 2017. — [arXiv:1709.00382](https://arxiv.org/abs/1709.00382)
- **Jiang et al. 2019 — Two-Stage Cascaded U-Net (1st place BraTS 2019).** Stage-1 U-Net variant produces a
  coarse prediction; stage-2 takes the coarse map concatenated with the raw images to refine ("coarse to
  fine"). Average Dice 85.7 (ensemble of 12 models). This is the canonical "two-stage cascaded U-Net"
  reference and directly establishes coarse-to-fine as a winning recipe. MICCAI BrainLes 2019. —
  [Springer 10.1007/978-3-030-46640-4_22](https://link.springer.com/10.1007/978-3-030-46640-4_22); summarized in
  [search results](https://arxiv.org/pdf/2011.02881)
- **nnU-Net 3D cascade (Isensee et al. 2020).** The self-configuring reference baseline auto-generates a
  `3d_lowres -> 3d_cascade_fullres` cascade: a low-resolution 3D U-Net makes a coarse map, which is upsampled
  and passed as an extra input channel to a full-resolution 3D U-Net that refines detail (addresses the
  context-vs-resolution trade-off). The cascade is auto-omitted when the full-res patch already covers most
  of the image. This makes the coarse-to-fine cascade a DEFAULT, not a novelty. —
  [nnU-Net, arXiv:1904.08128](https://alphaxiv.org/abs/1904.08128)
- **CU-Net — Cascaded U-Net with Loss-Weighted Sampling (2019).** Stage-1 U-Net separates whole tumour from
  background; extracted features feed a stage-2 U-Net that segments substructures, exploiting the
  physiological nesting of tumour regions. — [arXiv:1907.07677](https://arxiv.org/pdf/1907.07677)
- **Two-Stage Cascade with VAE + Attention Gates (2020).** Coarse stage then refinement with variational
  autoencoder regularization and attention gates. BraTS. — [arXiv:2011.02881](https://arxiv.org/pdf/2011.02881)
- **Cascaded 3D U-Net with pre-activation Residual-SE attention** and a **two-stage cascaded 3D model with Swin
  Transformer + ASPP + SE (coarse) and a class-wise attention decoder (fine)** are further representative
  entries, confirming breadth. — [search summary](https://arxiv.org/pdf/2410.14020)

### Inferences
- The lineage Wang 2017 -> Jiang 2019 -> nnU-Net cascade shows the idea moved from "a competitive trick" to
  "the default configuration" within ~2 years. Reviewers will treat plain coarse-to-fine as prior art.
- Two sub-families coexist: (i) HIERARCHICAL-SUBREGION cascades (binary WT -> TC -> ET), and (ii)
  LOCALIZE-THEN-SEGMENT / crop-ROI cascades (Q2/Q3). They are often conflated but are different motivations.

### Gaps
- Could not pull an explicit survey section enumerating cascade limitations; brain-tumour surveys (e.g.
  [arXiv:2007.09479](https://arxiv.org/pdf/2007.09479)) focus on architectures/imbalance/multimodality rather
  than a dedicated coarse-to-fine critique.

---

## Q2. Does any method frame stage-1 as a FAST glance/saliency step and report SPEED / latency / FLOPs?

### Takeaway
Many localize-then-segment cascades justify stage-1 by COMPUTATION reduction ("crop so stage-2 is cheaper"),
but almost all still report ACCURACY as the headline and give little or no latency/FLOPs accounting. Explicit
"glance-and-focus for SPEED, measured in ms/FLOPs" framing exists in general/volumetric segmentation
(SegVol, RAZN, zoom-in/zoom-out) but is rarely the headline for brain tumour specifically. This is a genuine
soft spot in the brain-tumour literature.

### Cited Findings
- **Orthogonal-Nets two-stage (BraTS).** Stage-1 predicts labels on the whole 3D image; labels crop ONLY the
  tumour region; stage-2 Orthogonal-Nets run on the cropped region, which "substantially reduces the
  computational burden on the stage-II networks" and reduces class imbalance. Efficiency is argued but speed
  is a side-benefit, not a measured headline. — [search summary](https://arxiv.org/pdf/2007.12066v2)
- **YOLO + modified attention-U-Net two-stage.** YOLOv3 first stage to "quickly and accurately localize"
  tumour ROIs, explicitly "to improve computation speed and efficiency," then U-Net segments. This is the
  closest brain-tumour instance of a fast detector-as-glance framing. — [search summary](https://ieeexplore.ieee.org/document/10947068)
- **General/volumetric glance-and-focus with measured efficiency (not all brain-specific):**
  - **SegVol zoom-out-zoom-in.** Resize volume -> coarse mask -> crop ROI from original -> sliding-window
    zoom-in for precise inference. Efficiency-motivated. — [arXiv:2311.13385](https://arxiv.org/pdf/2311.13385)
  - **RAZN (Reinforced Auto-Zoom Net).** A policy network DECIDES whether to zoom a region; selective zoom-in
    saves computation and adds robustness. — [search summary](https://arxiv.org/pdf/2311.13385)
  - **Selective zooming/skipping** surveyed in "Efficient High-Resolution Deep Learning: A Survey." —
    [arXiv:2207.13050](https://arxiv.org/pdf/2207.13050)
- **Single-stage "fast" brain-tumour models (context for what measured speed claims look like):**
  - **Pseudo-3D + ECA + cross-attention:** 3.57M params, 21.26 GFLOPs, **0.016 s per 3D volume**. —
    [search summary](https://www.frontiersin.org/journals/medicine/articles/10.3389/fmed.2025.1660445/pdf)
  - **EfficientGFormer:** 36.9M params, 198.4 GFLOPs, **~174 ms per volume** ("real-time"). —
    [arXiv:2508.01465](https://arxiv.org/pdf/2508.01465)
  - **LATUP-Net:** lightweight 3D attention U-Net (parallel convolutions) explicitly targeting parameter/compute
    reduction. — [arXiv:2404.05911](https://arxiv.org/pdf/2404.05911)
  - **Model-optimization study:** dynamic-range quantization compresses model 75% and speeds inference 37%. —
    [search summary](https://dspace.vut.cz/items/89297d69-7e47-4f06-8224-b07df4ac123a)

### Inferences
- The "fast GLANCE then focus, with latency/FLOPs reported" niche is credibly UNDER-OCCUPIED for brain tumour
  specifically: cascades that cite computation savings almost never quantify them, and the models that DO
  quantify speed are single-stage efficiency architectures, not glance-then-focus cascades.
- A paper could therefore differentiate by MEASURING and foregrounding latency/FLOPs/throughput of the
  glance-then-focus pipeline, not just Dice — this is a reporting gap, not an unexplored concept.

### Gaps
- Exact citation/venue for the "Orthogonal-Nets" and the YOLO+U-Net brain papers not fully pinned (surfaced
  via search snippets); report-writer should verify authors/year before citing as primary.

---

## Q3. What drives the coarse stage — learned proposal, thresholding, attention, or clinically-inspired / label-free saliency?

### Takeaway
Overwhelmingly, the coarse stage is a LEARNED localizer/segmenter (a trained U-Net, detector, or learned
spatial prior). Classical LABEL-FREE saliency driven by brain bilateral SYMMETRY exists and is effective for
tumour localization, but it predates the deep-cascade era and is rarely used TO DRIVE a modern deep
coarse-to-fine segmenter. A glance stage driven by a clinically-inspired, label-free saliency (symmetry /
modality cues) coupled to a deep refiner appears to be a relatively open combination.

### Cited Findings
- **Learned coarse stage (the norm):**
  - nnU-Net cascade: trained low-res 3D U-Net. — [arXiv:1904.08128](https://alphaxiv.org/abs/1904.08128)
  - Jiang 2019 / Wang 2017 / CU-Net: trained U-Net/FCN coarse stages. — [1709.00382](https://arxiv.org/abs/1709.00382)
  - **PGR-Net (CVPR 2026) — Prior-Guided ROI Reasoning.** Coarse localization driven by a DATA-DRIVEN learned
    spatial prior (distribution/scale of lesions) + a hierarchical Top-K ROI decision mechanism across encoder
    layers + a WinGS-ROI module (multi-window Gaussian templates with spatial-decay to make center-enhanced
    guidance maps). 8.64M params; WT Dice 89.02 / 91.82 / 89.67 on BraTS2019 / BraTS2023 / MSD Task01. No
    speed/latency reported. Note: the "prior" and Gaussian ROI are HAND-DESIGNED guidance but still fit inside
    a trained net, not a label-free pre-segmentation saliency. — [arXiv:2603.21626](https://www.alphaxiv.org/abs/2603.21626),
    [CVPR 2026 poster](https://cvpr.thecvf.com/virtual/2026/poster/38185)
- **Detector/thresholding-driven coarse stage:** YOLOv3 as fast ROI detector; multilevel thresholding for ROI
  segmentation. — [IEEE 10947068](https://ieeexplore.ieee.org/document/10947068);
  [ISI multilevel thresholding](https://digitalcommons.isical.ac.in/conf-articles/354)
- **Label-free / clinically-inspired saliency (mostly classical, FOUNDATIONAL):**
  - **Bilateral-symmetry tumour detection (Saha et al.).** Real-time algorithm puts a bounding box around the
    abnormality by locating what BREAKS left-right brain symmetry; requires NO registration, NO training image,
    and is intensity-variation independent. This is the archetypal clinically-inspired, label-free glance. —
    [arXiv:1412.3009](https://arxiv.org/pdf/1412.3009)
  - **Statistical asymmetry-based tumour segmentation.** — [SciTePress 38922](https://www.scitepress.org/Papers/2012/38922/38922.pdf)
  - **Symmetry / mid-sagittal-plane analysis** is a long-standing preprocessing cue for pathology detection. —
    [TU Wien 2013](https://www.vr.tuwien.ac.at/publications/detection-of-brain-tumors-based-on-automatic-symmetry-analysis-2013/)
- **"Radiologically informed" cascade (clinical knowledge, but different mechanism).** Pediatric two-stage
  cascaded nnU-Net (BraTS-PEDs 2024): "radiologically informed" means radiology GUIDELINES choose WHICH mpMRI
  modality feeds each cascaded sub-model (ET-vs-NET, CC-vs-ED) — clinical knowledge steers modality selection,
  NOT a saliency-driven coarse localizer. Shows clinically-inspired cascade framing is already being published,
  but via modality routing rather than symmetry/saliency. No speed reported. —
  [arXiv:2410.14020](https://arxiv.org/abs/2410.14020v1)

### Inferences
- The specific combination "clinically-inspired LABEL-FREE saliency (bilateral symmetry / modality contrast)
  as the GLANCE that drives a modern deep refiner, with measured speed" sits in a gap between two mature but
  separate literatures (classical symmetry detection vs deep learned cascades). That intersection is the most
  defensible novelty angle here.
- PGR-Net is the strongest recent competitor and partly erodes the "hand-designed guidance" angle (its
  Gaussian/spatial prior is hand-designed guidance) — but it is still a TRAINED localizer and reports no speed,
  so a label-free + speed-measured framing remains distinct.

### Gaps
- Found no 2019-2026 brain-tumour paper that uses bilateral symmetry as the explicit coarse glance for a deep
  coarse-to-fine SEGMENTATION pipeline. Absence of evidence is itself the opportunity, but I cannot prove none
  exists; a targeted search ("symmetry-guided deep cascade brain tumour") is advisable before claiming full
  novelty.

---

## Q4. Is coarse-to-fine so standard it cannot be a headline novelty, and what would make it a contribution?

### Takeaway
Yes — plain coarse-to-fine / localize-then-segment is saturated and standard (challenge winners + nnU-Net
default). It cannot be the headline alone. A contribution requires an ADDITIONAL, defensible twist on the
glance stage (label-free/clinically-inspired driver) AND/OR a RESULT dimension the field under-reports here
(measured speed/latency/FLOPs, or a downstream clinical property).

### Cited Findings
- Coarse-to-fine is a documented winning recipe (Jiang 2019 1st place) and a built-in default (nnU-Net
  cascade), i.e. baseline expectation. — [10.1007/978-3-030-46640-4_22](https://link.springer.com/10.1007/978-3-030-46640-4_22);
  [arXiv:1904.08128](https://alphaxiv.org/abs/1904.08128)
- Newest entries differentiate NOT on "two-stage" but on the MECHANISM of the coarse stage: learned spatial
  priors + ROI reasoning (PGR-Net), radiology-guided modality routing (pediatric cascade), RL zoom policies
  (RAZN). — [arXiv:2603.21626](https://www.alphaxiv.org/abs/2603.21626);
  [arXiv:2410.14020](https://arxiv.org/abs/2410.14020v1); [arXiv:2311.13385](https://arxiv.org/pdf/2311.13385)
- Speed/FLOPs is a live differentiator in brain-tumour segmentation broadly (EfficientGFormer ~174 ms,
  pseudo-3D 0.016 s/volume, LATUP-Net), showing the community rewards measured efficiency — but these are
  single-stage, leaving the "efficient CASCADE" quadrant comparatively open. —
  [arXiv:2508.01465](https://arxiv.org/pdf/2508.01465);
  [fmed 2025](https://www.frontiersin.org/journals/medicine/articles/10.3389/fmed.2025.1660445/pdf);
  [arXiv:2404.05911](https://arxiv.org/pdf/2404.05911)

### Inferences (what would have to be added to make it a contribution)
1. **Replace the learned localizer with a label-free, clinically-inspired saliency glance** (bilateral
   symmetry break, modality-contrast cues) — differentiates from every learned-proposal/nnU-Net cascade and
   from PGR-Net's trained prior; also removes a trained component (data/annotation efficiency argument).
2. **Report SPEED as a first-class result** (latency, FLOPs, throughput, peak memory) — the cascade
   literature almost never does this for brain tumour; doing so credibly occupies the "fast glance-then-focus"
   quadrant.
3. **Tie the glance to a downstream clinical/safety property** (e.g. the project's error-prediction/triage
   theme) rather than only Dice, since raw Dice is saturated.
4. Avoid over-claiming: must explicitly position against Jiang 2019, nnU-Net cascade, Wang 2017, PGR-Net, and
   classical symmetry detectors, and concede that "two-stage" per se is prior art.

### Gaps
- No single source states "coarse-to-fine is saturated"; this is an inference synthesized from the density of
  challenge-winning and default-baseline cascades. Report-writer should present it as an informed assessment,
  not a cited claim.
