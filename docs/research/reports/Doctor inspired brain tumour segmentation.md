# Doctor-Inspired Brain-Tumour Segmentation — Novelty Synthesis Report

**Date:** 2026-10-23
**Question that drove this research:** The professor's criticism is that the project "just uses off-the-shelf models with no novelty." The user's proposed direction is to **make the AI read a brain-MRI scan the way a doctor does — and as fast as possible.** Concretely, two paths were chosen:

- **Path B — doctor-like *priors*:** inject two clinically-motivated, **label-free** signals the model can compute from the image itself:
  1. **left–right (hemispheric) symmetry break** — "the lesion is where the two halves of the brain stop matching," and
  2. **cross-modality disagreement** — "the lesion is where the four MRI sequences (T1, T1c, T2, FLAIR) stop agreeing."
- **Path C — fast "glance-then-zoom":** a cheap coarse *glance* that localizes the tumour, then a detailed *zoom* refiner only on that region, with **inference speed measured and reported as a first-class result** (not just Dice).

This report synthesises five researcher notes (`research_notes/Doctor inspired brain tumour segmentation/`) plus fresh verification searches run on 2026-10-23, and delivers an **honest novelty verdict**. It follows the project integrity rule: *do not overstate novelty; name the prior art that would get us rejected; report what is genuinely open and what is not.*

---

## 1. Bottom line (read this first)

**None of the three individual ingredients is novel on its own. Each is published, some of it very directly.** Specifically:

- **Symmetry-as-prior for gliomas is TAKEN**, more than the earlier notes implied. The decisive hit is **Chen et al., "Deep Convolutional Symmetric Neural Network" (DCSNN)**, which adds **Left–Right Similarity Masks (LRSM)** at multiple feature scales, feeds the image *and its mirror* into the network, and reports **DSC ≈ 0.852 on BraTS**. That is almost exactly "bake hemispheric symmetry into a supervised glioma segmenter." A pure-symmetry claim would be rejected.
- **Cross-modality disagreement as a signal is PARTIALLY taken.** **ReCoSeg++** (arXiv:2508.01058) turns a cross-modal *reconstruction residual* into an error-aware attention channel; **EnTrust** (arXiv:2606.21384) decomposes features into "conflict signals" for uncertainty. Both route disagreement through a *learned* model.
- **Coarse-to-fine cascades are SATURATED** — the nnU-Net default and multiple BraTS challenge winners (Wang 2017, Jiang 2019) are cascades. Plain "two-stage" cannot be a headline.

**What remains genuinely open is the *specific combination* plus three distinctive framings that nobody has put together:**

> A **fast, label-free, model-free glance-then-zoom** segmenter whose *glance* is driven by **two simple, interpretable, training-free saliency maps — hemispheric-symmetry-break AND cross-modality variance — computed directly from the normalised input**, feeding a standard deep refiner, **with inference latency/FLOPs reported as a headline**, and **evaluated not only on Dice but on the project's consequential volume-error / RANO triage endpoint.**

This is **novel as an assembly and as a framing, not as new theory.** That is a legitimate, defensible contribution for an original course project — *provided* we position explicitly against DCSNN, ReCoSeg++, EnTrust, PGR-Net and the nnU-Net cascade, and we do **not** claim to have invented symmetry priors, disagreement signals, or cascades. Honesty here is not optional: a reviewer who knows DCSNN will reject an over-claim instantly.

**Confidence:** medium-high on "individual pieces are taken" (direct citations); medium on "the exact combination is unclaimed" (this is inferred from absence across ~12 targeted searches + a fusion survey, not from a paper that says "nobody has done this").

---

## 2. State of the art, component by component

### 2.1 Hemispheric-symmetry priors (Path B, signal 1)

| Work | What it does | Domain | Why it matters to us |
|---|---|---|---|
| **Chen et al. — DCSNN + LRSM** (Neurocomputing, ~2019; *verify exact year/vol*) | Left–Right Similarity Masks at multiple scales; feeds image + its flip; DSC ≈ 0.852 | **Glioma / BraTS, supervised** | **Closest prior art.** Directly does "symmetry as in-model prior for glioma seg." Must cite and differentiate. |
| Zhang, Zhu, Willke — "Segmenting Brain Tumors with Symmetry" (arXiv:1711.06636) | Encodes symmetry into a SOTA seg net | BraTS | Foundational; pre-2020 |
| SD-GAN (USyd) | Asymmetry → reconstruction error | BraTS, **unsupervised** | Coarse anomaly, not fine multi-class |
| SACA / SA-Swin (MICCAI 2024, arXiv:2407.08948) | Symmetry-aware cross-attention as **pretraining** proxy | Multi-centre MRI | Symmetry at pretraining, not an inference-time prior |
| SEAN (MICCAI 2021), AsymFeX (arXiv:2608.19769) | Strong contralateral cross-attention | **Stroke (CT/MRI)**, not glioma | The best symmetry *mechanisms* live in stroke |

**Verdict:** "Compare the two hemispheres to find the tumour" is textbook and, via **DCSNN**, already instantiated for supervised BraTS. **Symmetry alone is not novel.** Known failure mode we must address: large gliomas cause **mass effect / midline shift**, which corrupts the very symmetry plane the prior relies on — DCSNN's naive flip does not handle this well, which is one crack we can exploit.

### 2.2 Cross-modality disagreement (Path B, signal 2)

| Work | What it does | Gap vs our idea |
|---|---|---|
| **ReCoSeg++** (arXiv:2508.01058) | Diffusion synthesises T1c; **residual (real−synth T1c)** = attention channel; Dice ≈ 93% WT (BraTS2021) | Disagreement only for *one synthesised* modality, via a heavy learned generator |
| **EnTrust** (arXiv:2606.21384) | Learned "conflict signal" decomposition → **uncertainty** (TrustMap) | Conflict drives *uncertainty*, not a positive localisation prior; needs a learned module |
| DGRNet (arXiv:2603.21086) | Disagreement across **model views** (not modalities) | Different disagreement axis |
| CMAF-Net, mmFormer, RFNet, Tri-Attention | Cross-modal *fusion* (combine complementary info) | Fusion ≠ disagreement-as-saliency |

**Verdict:** The idea "where modalities disagree is where the lesion is" exists **indirectly** (always through a learned synthesis/decomposition step). A **direct, model-free** disagreement map — e.g. voxel-wise variance / Jensen–Shannon divergence across the four intensity-normalised, co-registered sequences, used as an explicit attention prior or extra input channel to *localise* the tumour — appears **genuinely unclaimed** for brain-tumour MRI. This is the strongest single novelty seed, *because* it is model-free (no generator, so it is cheap — which also serves Path C's speed goal).

### 2.3 Coarse-to-fine / fast glance-then-zoom (Path C)

- **Saturated as a concept:** nnU-Net ships a `3d_lowres → 3d_cascade_fullres` cascade by default; Wang 2017 and Jiang 2019 (BraTS winners) are cascades. Plain two-stage = prior art.
- **Two real soft spots:**
  1. **Measured speed is almost never the headline** for brain-tumour cascades — they argue "cropping saves compute" but rarely report latency/FLOPs/throughput. Single-stage efficient models *do* report speed (pseudo-3D 0.016 s/vol; EfficientGFormer ~174 ms; LATUP-Net; Uni-Light 289 ms/scan, 1.52M params). The **efficient *cascade* quadrant with measured speed is comparatively open.**
  2. **The coarse stage is almost always a *learned* localizer.** A **label-free, clinically-inspired glance** (symmetry-break + modality-variance saliency, computed with no training) driving a modern deep refiner sits in a gap between classical symmetry-detection (Saha et al., arXiv:1412.3009) and deep cascades. **PGR-Net (CVPR 2026, arXiv:2603.21626)** is the closest recent competitor but its prior is *hand-designed-yet-trained* and it reports **no speed** — so "label-free glance + measured speed" stays distinct.

### 2.4 "Reading like a radiologist" without gaze data (feasibility of the framing)

- **No public brain-MRI eye-gaze dataset exists** (only private Stember et al. data). So "learn from real doctor gaze" is **data-blocked** — correctly dropped earlier.
- The achievable version is a **label-free saliency/reading prior computed from the image**. Closest analog: **RadiomicNet** (arXiv:2607.02185) injects handcrafted radiomics texture via an attention gate with ante-hoc interpretability — but on breast-US/endoscopy, **not brain**, and not symmetry/modality-based. Brain-tumour attention-supervision works (SegGuidedNet arXiv:2605.22572; Prior Attention Net arXiv:2110.04735) derive their prior **from the labels**, so they are *not* label-free.
- **White space confirmed:** a label-free, clinically-motivated reading prior injected into a BraTS segmenter and evaluated for **data-efficiency / robustness / consequential-error reduction** rather than raw Dice was not found.

### 2.5 Fast/efficient 3D segmentation (the baselines Path C must beat)

- Standard 3D U-Net ≈ 5.9M params / 148 GFLOPs. Sub-2M-param models now match or beat it: **LHC-Net** (1.65M), **LATUP-Net** (3.07M), **Uni-Light** (1.52M, 289 ms/scan on a T4, KD from a teacher), Mamba/SSM models (SegMamba, LightM-UNet).
- **Caution for us:** low parameter count ≠ low latency (Mamba can be FLOP-heavy). If we claim "fast," we must measure wall-clock latency and FLOPs, not just params — and ideally on our actual 6 GB laptop GPU, which is itself an honest, relatable efficiency setting.

---

## 3. The honest novelty verdict

**What we CANNOT claim (would be rejected):**
- ❌ "We are the first to use brain symmetry for tumour segmentation." (DCSNN, Zhang 2017, SD-GAN, SACA.)
- ❌ "We are the first to use modality disagreement." (ReCoSeg++, EnTrust.)
- ❌ "We introduce a coarse-to-fine cascade for brain tumours." (nnU-Net default; Jiang 2019.)
- ❌ "We read the scan like a radiologist" framed as learned visual search. (No gaze data; bottom-up saliency for this is pre-deep and detection-only.)

**What we CAN defensibly claim (novel as assembly + framing):**
1. ✅ A **unified, model-free, training-free saliency glance** that *combines* hemispheric-symmetry-break **and** cross-modality variance into one interpretable localisation prior — the *direct, generator-free* disagreement map in particular is unclaimed for brain tumour.
2. ✅ Using that label-free glance to **drive a fast coarse-to-fine refiner**, with **latency / FLOPs / peak-memory reported as headline results on commodity (6 GB) hardware** — occupying the under-reported "efficient cascade with measured speed" quadrant.
3. ✅ **Evaluating against the project's consequential volume-error / RANO triage endpoint**, not just Dice — tying the doctor-like prior to a clinical safety property. This is the cleanest differentiator: no symmetry/disagreement paper is evaluated this way.
4. ✅ A **clean ablation isolating how much a symmetry prior vs a disagreement prior actually adds for gliomas specifically, including under mass-effect / midline-shift** — the literature acknowledges this failure mode qualitatively but **never benchmarks it**. This evidence contribution is genuinely missing.

**Framing rule:** lead with the *combination + clinical-safety evaluation + measured efficiency + mass-effect robustness*, explicitly concede that symmetry, disagreement and cascades are each prior art, and position by name against **DCSNN, ReCoSeg++, EnTrust, PGR-Net, SACA**.

---

## 4. Recommended concrete proposal (feasible on the 6 GB laptop)

A compact, honest, buildable system — call it a working name like **GSZ (Glance–Symmetry/Disagreement–Zoom)**:

1. **Glance (label-free, ~free compute):** from the normalised, co-registered T1/T1c/T2/FLAIR, compute two maps with *no training*:
   - **Asymmetry map** = voxel distance to its contralateral counterpart after a learned-light or robust midsagittal alignment (must handle midline shift — e.g. local-neighbourhood disparity à la AsymFeX rather than rigid global flip, to beat DCSNN's naive flip).
   - **Disagreement map** = voxel-wise variance / Jensen–Shannon divergence across the four normalised modalities.
   Fuse into one saliency volume → cheap coarse ROI.
2. **Zoom (standard refiner):** run the existing 3D residual U-Net (already training on BraTS) only on the ROI, optionally taking the two saliency maps as extra input channels / attention gates.
3. **Report:** Dice (WT/TC/ET) **and** latency/FLOPs/peak-memory **and** the consequential-volume-error / triage metrics, with an **ablation** (no prior / symmetry only / disagreement only / both) and a **mass-effect-stratified** breakdown.

**Why feasible here:** the glance is model-free (no extra GPU training); the refiner is the net already being trained; it reuses the frozen BraTS pipeline and the project's existing error/triage evaluation. The efficiency story is *strengthened*, not weakened, by the modest hardware.

---

## 5. Must-do before claiming novelty in the paper

- [ ] **Read DCSNN in full** (Neurocomputing, S0925231219304692 — blocked by paywall here; get via institution). Confirm its exact symmetry mechanism and whether it reports latency / handles midline shift. This is the paper most likely to be cited against us.
- [ ] Targeted proceedings search (MICCAI/BrainLes 2024–2026, IEEE TMI) for any **symmetry-guided *deep cascade*** or **model-free disagreement-as-attention** paper not surfaced on arXiv/PMC.
- [ ] Confirm whether **EnTrust**'s "brain" benchmark is BraTS specifically and its per-region Dice.
- [ ] Verify **PGR-Net** (CVPR 2026) final numbers and that it reports no latency.
- [ ] Lock an **ablation + mass-effect-stratified** protocol *before* touching the test split (same pre-registration discipline as the volume-error study).

## 6. Sources (key)

- Chen et al., Deep Convolutional Symmetric Neural Network (LRSM) — https://www.sciencedirect.com/science/article/abs/pii/S0925231219304692 ; https://www.researchgate.net/publication/332646477
- Zhang, Zhu, Willke, Segmenting Brain Tumors with Symmetry — https://arxiv.org/abs/1711.06636
- SACA / SA-Swin (MICCAI 2024) — https://arxiv.org/abs/2407.08948
- AsymFeX — https://arxiv.org/abs/2608.19769 · SEAN — https://arxiv.org/abs/2110.05039
- ReCoSeg++ — https://arxiv.org/abs/2508.01058 (HTML: https://arxiv.org/html/2508.01058)
- EnTrust — https://arxiv.org/abs/2606.21384 · DGRNet — https://www.alphaxiv.org/abs/2603.21086
- PGR-Net (CVPR 2026) — https://www.alphaxiv.org/abs/2603.21626
- nnU-Net — https://arxiv.org/abs/1904.08128 · Jiang 2019 cascade — https://link.springer.com/10.1007/978-3-030-46640-4_22 · Wang 2017 — https://arxiv.org/abs/1709.00382
- RadiomicNet — https://arxiv.org/abs/2607.02185 · SegGuidedNet — https://arxiv.org/abs/2605.22572 · Prior Attention Net — https://arxiv.org/abs/2110.04735
- Uni-Light — https://arxiv.org/html/2609.06729 · LATUP-Net — https://arxiv.org/abs/2404.05911 · LHC-Net — https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9749147/
- Bilateral-symmetry label-free detection (Saha et al.) — https://arxiv.org/pdf/1412.3009
- Towards Label-Free Brain Tumor Segmentation (MViT-AE, symmetry+reconstruction) — https://arxiv.org/pdf/2510.15684

*Per the project integrity stance ([[ayshcxr-integrity-stance]]): novelty here is combination + framing, not new theory; the paper must concede prior art and may still report a null if the priors do not help.*
