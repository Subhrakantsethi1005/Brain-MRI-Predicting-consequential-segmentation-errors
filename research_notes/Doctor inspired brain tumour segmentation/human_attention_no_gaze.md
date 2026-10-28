# Human-Visual-Attention / Radiologist-Reading-Inspired Segmentation Without Gaze Data (2020-2026, emphasis brain MRI)

Scope note: this file deliberately EXCLUDES methods that consume recorded eye-gaze/eye-tracking (e.g. MedGaze, GazeSearch/ChestSearch, EyeXNet, gaze-assisted/gaze-weak-supervision segmentation). Those are noted only where needed as contrast. The focus is models that build a human-like attention/saliency/visual-search prior from the IMAGE itself or from clinical reasoning, without gaze.

---

## Q1. Computational models of the radiologist's visual SEARCH / reading process, WITHOUT eye-tracking

### Takeaway
Computational modelling of radiologist "reading" without gaze mostly reduces to classic bottom-up saliency (Itti-Koch / GBVS / SR) and a small number of bio-inspired visual-system emulations; genuine *scanpath / visual-search* prediction for medical images is currently dominated by gaze-trained models, and no gaze-free scanpath model specific to brain-tumour MRI was found.

### Cited Findings
- Itti & Koch's bottom-up saliency model (center-surround over intensity, colour, orientation + winner-take-all focus-of-attention) is the seminal foundational model of human visual attention and has been adapted to medical imaging; because medical images are low-contrast, Itti's model is typically modified (combined with target shape features / dynamic thresholding) rather than applied directly. It has been "modified to compute the saliency map and ROI was extracted with dynamic thresholding for tumor detection in brain MRI images." — [Salience Models review, PMC6969943](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6969943/); [Itti-Koch in medical ROI, academia.edu](https://www.academia.edu/6869012/Contour_Based_Image_Segmentation_Using_Selective_Visaul_Attention)
- A fully bio-inspired visual attention model for detecting multiple sclerosis lesions in brain MRI "emulate[s] the visual perception of the radiologist by using modeling principles of the neuronal centers along the visual system," and aims to differentiate acute vs chronic lesions (most prior methods are non-specific). Authors: Villalon-Reina, Gutierrez-Carvajal, Thompson, Romero-Castro; IX Int. Seminar on Medical Information Processing and Analysis (SPIE), 2013; DOI 10.1117/12.2042046. (FOUNDATIONAL / pre-2020, but directly brain MRI, label-free bottom-up.) — [MSSM scholars record](https://scholars.mssm.edu/en/publications/detecting-multiple-sclerosis-lesions-with-a-fully-bioinspired-vis-2/)
- Computational saliency models (Itti-Koch, GBVS, Spectral Residual) have been evaluated for abnormality detection in medical images; these are image-derived (no gaze needed at inference), though studies often validate them against radiologist gaze. — [What catches a radiologist's eye? ASU CUBIC](https://cubic.asu.edu/node/248); [PMC4702525](https://pmc.ncbi.nlm.nih.gov/articles/PMC4702525)
- CONTRAST (gaze-based, excluded by objective): modern "radiologist reading process" scanpath models are gaze-trained — MedGaze (digital gaze twin, CXR scanpath) and GazeSearch/ChestSearch (first target-present visual-search dataset for CXR, built by converting free-view gaze into finding-aware search). These establish that the no-gaze alternative is under-explored. — [MedGaze arXiv:2407.00129](https://arxiv.org/pdf/2407.00129); [GazeSearch WACV2025](https://openaccess.thecvf.com/content/WACV2025/papers/Pham_GazeSearch_Radiology_Findings_Search_Benchmark_WACV_2025_paper.pdf)

### Inferences
- The "read like a radiologist" idea has historically been implemented as bottom-up saliency (Itti-family) for ROI/detection, not as a modern learned reading prior for segmentation; these are label-free and image-derived but low-level and pre-deep-learning in spirit.
- Scanpath/foveation *sequence* modelling specifically for brain-tumour MRI, without gaze, appears to be an open area.

### Gaps
- No gaze-free scanpath/visual-search sequence model found for brain MRI; could not confirm any 2020-2026 paper that predicts a radiologist-like search trajectory on brain tumour MRI from image content alone.

---

## Q2. Clinically-motivated, LABEL-FREE saliency priors injected into segmentation (as attention supervision or extra channel)

### Takeaway
A clinically-motivated, label-free prior fed into segmentation attention DOES exist (notably RadiomicNet via handcrafted radiomics texture features), but demonstrated on breast ultrasound / endoscopy — NOT brain tumour MRI; the brain-tumour attention-supervision works that do exist derive their prior FROM the labels, so they are not label-free.

### Cited Findings
- **RadiomicNet** (label-free clinical prior, closest concept): a two-stream hybrid that injects handcrafted radiomics features — Gray-Level Co-occurrence Matrix (GLCM) and Local Binary Pattern (LBP) texture — through a "Radiomics Attention Gate (RAG)" that modulates skip-connection attention in a lightweight MobileNetV2 encoder-decoder, giving *ante-hoc* interpretability (no post-hoc approximation). A Radiomics Consistency Loss aligns texture complexity with prediction uncertainty. DSC 0.763±0.231 (BUSI breast ultrasound), 0.854±0.112 (Kvasir-SEG endoscopy); beats U-KAN by 1.2% / 1.8% with only 3.27M params (~9.5x fewer than U-Net); Expected Calibration Error reduced 0.142→0.118. Author: Mohammad Amanour Rahman; arXiv:2607.02185, Jul 2026. Domain is NOT brain MRI. — [chatpaper summary](https://chatpaper.com/de/paper/306601); [arXiv:2607.02185](https://arxiv.org/abs/2607.02185)
- **Prior Attention Network** (label-DERIVED, brain MRI): uses an "intermediate supervision strategy for generating lesion-related attention to acquire the ROIs," folding coarse-to-fine segmentation into a single network. Evaluated on 2D lung-infection CT and 3D brain-MRI lesion segmentation; better performance at lower computational cost than cascaded networks. Prior comes from lesion supervision, so NOT label-free. Zhao et al. (8 authors), arXiv:2110.04735 (eess.IV), Oct 2021. — [arXiv:2110.04735](https://arxiv.org/abs/2110.04735)
- **SegGuidedNet** (label-DERIVED, brain tumour): a "SegAttentionGate module that explicitly supervises the decoder to produce spatially discriminative attention maps" via a lightweight auxiliary loss tied to ground-truth sub-region annotations; gives "free-of-cost spatial interpretability at inference without any post-hoc explanation method." Mean Dice ~0.897-0.905 on BraTS2021/BraTS2023 (ET/TC/WT). Prior derived from labels, NOT label-free. Maqsood, Khan, Vollmer, Dengel, Asim; arXiv:2605.22572, May 2026. — [arXiv:2605.22572](https://arxiv.org/abs/2605.22572)
- Image-derived, label-free saliency used as detection prior in other domains: biologically-inspired saliency for diabetic-retinopathy lesions (spatially-varying morphological enhancement + ensemble saliency map) and "uniqueness-driven" superpixel saliency (uniqueness + compactness, pixel saliency via bilateral filter) for retinal lesion detection. — [bio-inspired fundus saliency, IIIT](https://cdn.iiit.ac.in/cdn/cvit.iiit.ac.in/images/ConferencePapers/2016/biologically-rangrej.pdf); [uniqueness-driven retinal saliency, Nottingham](https://research.nottingham.edu.cn/en/publications/uniqueness-driven-saliency-analysis-for-automated-lesion-detectio/fingerprints)

### Inferences
- The exact pattern the user describes — a label-free, clinically-inspired saliency computed from the input and injected as attention supervision or an extra channel — is realized by RadiomicNet (texture-based) but not in brain-tumour MRI, and not framed as "radiologist reading."
- For brain tumour specifically, existing attention-supervision work (Prior Attention Net, SegGuidedNet) uses the labels to make the prior, which is a materially different (and less novel-for-you) claim than a label-free reading prior.

### Gaps
- No paper found that adds a label-free, clinically/perceptually motivated saliency map as an EXTRA INPUT CHANNEL to a brain-tumour MRI segmentation network (searches returned only generic attention-gated U-Nets).
- Could not find quantitative label-free-prior results on BraTS.

---

## Q3. Bio-inspired / foveated / "glimpse" attention networks for medical or 3D volumetric segmentation

### Takeaway
Foveated/glimpse/zoom-in attention is established and bio-inspired, but medical demonstrations are on 2D ultra-high-resolution histology/pathology (and natural-image glimpse nets); application to 3D volumetric BRAIN MRI segmentation was not found.

### Cited Findings
- **Foveation for Segmentation of Ultra-High Resolution Images** (MICCAI 2020): a learnable "foveation module" acts as an adaptive dataloader that, per spatial location, chooses the field-of-view/resolution trade-off of the input patch, trained jointly with the segmentation net. On prostate histology it beat challenge top-performers on the two most ambiguous Gleason classes (Grade 3/4) by 13.1% and 7.5%, and beat the average of 6 human experts by 6.5%/7.5%. Image-derived, label-free foveation prior; 2D histology, not brain MRI. Jin, Tanno, Xu, Mertzanidou, Alexander; arXiv:2007.15124. — [arXiv:2007.15124](https://arxiv.org/abs/2007.15124)
- **Reinforced Auto-Zoom Net (RAZN)** and **CGS-Net**: explicitly motivated by a pathologist's microscope zoom-in; selective zoom makes RAZN robust to unbalanced/noisy ground-truth and reduces overfitting; CGS-Net processes zoomed-out (context) + zoomed-in (detail) views simultaneously "mirroring how pathologists switch views." Pathology/whole-slide, not brain MRI. — [RAZN, paperswithcode](https://physics.paperswithcode.com/paper/reinforced-auto-zoom-net-towards-accurate-and); [CGS-Net, NCI](https://www.cancer.gov/about-nci/organization/cbiit/news-events/news/2025/deep-learning-model-cgs-net-enhances-medical-image-analysis)
- **Multi-Glimpse Network (MGNet)**: recurrent downsampled-attention that sequentially selects task-relevant regions (glimpse/foveation). +4.76% average accuracy under common corruptions at only 36.9% compute, strong adversarial robustness, and "inherently more interpretable as it explicitly shows where it focuses each iteration." Natural images, not medical. arXiv:2111.02018. — [arXiv:2111.02018](https://arxiv.org/pdf/2111.02018)
- Bio-inspired foveal vision with top-down attention: "Unsupervised Foveal Vision Neural Networks with Top-Down Attention" — aggressive down-sampling to cheaply pick candidate locations for high-res glimpses, repeated to reduce uncertainty. Not medical/segmentation. arXiv:2010.09103. — [arXiv:2010.09103](https://arxiv.org/pdf/2010.09103)
- Note: coarse-to-fine 3D frameworks for volumetric medical segmentation exist (e.g. 3D coarse-to-fine, segmentation-by-detection, volumetric attention) and resemble "localize then refine" reading, but are efficiency/architecture-driven rather than framed as a human-reading prior. — [3D coarse-to-fine, arXiv:1712.00201](https://arxiv.org/pdf/1712.00201); [Volumetric Attention, arXiv:2004.01997](https://arxiv.org/pdf/2004.01997)

### Inferences
- The machinery for a foveated / coarse-to-fine "reading" segmenter transfers conceptually to brain MRI, but the published foveation/glimpse demonstrations stop at 2D gigapixel pathology and natural images; 3D volumetric brain-MRI foveation framed as radiologist reading is not occupied.

### Gaps
- No foveated/glimpse segmentation paper found that operates on 3D brain-tumour MRI volumes.

---

## Q4. Evaluation axis (data-efficiency / robustness / interpretability vs raw accuracy) and the honest gap for brain-tumour MRI

### Takeaway
Where these methods claim an edge, it is usually efficiency, robustness, calibration, or ante-hoc interpretability rather than raw Dice; but almost none of these axes have been demonstrated for a gaze-free radiologist-reading prior on brain-tumour MRI, which is the open gap.

### Cited Findings
- Interpretability / efficiency: SegGuidedNet sells "free-of-cost spatial interpretability at inference" with competitive (not superior) Dice on BraTS — i.e. interpretability, not accuracy, is the claimed contribution (but prior is label-derived). — [arXiv:2605.22572](https://arxiv.org/abs/2605.22572)
- Interpretability + calibration + parameter-efficiency: RadiomicNet's selling points are ante-hoc interpretability, 9.5x fewer parameters, and improved calibration (ECE 0.142→0.118), with only modest Dice gains — again axis-shifted away from raw accuracy (non-brain domain). — [chatpaper](https://chatpaper.com/de/paper/306601)
- Robustness + compute-efficiency + interpretability: MGNet quantifies robustness (+4.76% under corruptions, adversarial resistance) at 36.9% compute — the clearest robustness/efficiency case, but non-medical. — [arXiv:2111.02018](https://arxiv.org/pdf/2111.02018)
- Data-efficiency rationale: visual-attention mechanisms for small MS brain lesions are argued to "prevent overfitting of the background when the amount of data is limited" — i.e. attention as a data-efficiency prior, stated qualitatively, not benchmarked on few-case brain tumour. — [MS lesion visual-attention search summary](https://scholars.mssm.edu/en/publications/detecting-multiple-sclerosis-lesions-with-a-fully-bioinspired-vis-2/)
- Prior Attention Net's measured advantage over cascaded nets is computational cost at equal-or-better accuracy (efficiency axis), on brain MRI + lung CT — but prior is label-derived. — [arXiv:2110.04735](https://arxiv.org/abs/2110.04735)

### Inferences / Explicit statement of what is NOT yet done for brain-tumour MRI without gaze
- A LABEL-FREE, clinically/perceptually-inspired "reading" saliency prior (bottom-up saliency, radiomics texture, foveation, or a visual-search scanpath computed from the image) injected into a modern brain-tumour MRI segmenter (BraTS-style) and evaluated for DATA-EFFICIENCY (few training cases), ROBUSTNESS, or CONSEQUENTIAL-ERROR reduction — rather than raw Dice — was NOT found. This appears to be a genuine white space.
- The nearest neighbours each miss on one dimension: RadiomicNet = right idea (label-free clinical prior + ante-hoc interpretability) but breast-US/endoscopy, not brain; SegGuidedNet & Prior Attention Net = right domain (brain tumour / brain MRI) but label-DERIVED priors; bio-inspired MS-lesion & Itti-modified brain MRI = right domain + label-free but old (2013/classic), detection-oriented, pre-deep-segmentation; foveation/glimpse = right bio-inspired mechanism but 2D pathology / natural images, not 3D brain MRI; gaze scanpath models = right "reading" framing but require eye-tracking.

### Gaps
- No head-to-head benchmark found isolating the value of a human-reading prior on brain tumour under data-scarcity; the data-efficiency claim for attention priors remains largely qualitative.
- Could not retrieve full-text quantitative detail for the 2013 MS bio-inspired brain-MRI model (abstract only).
