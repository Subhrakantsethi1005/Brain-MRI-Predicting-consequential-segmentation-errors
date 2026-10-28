# Cross-Modality Disagreement as an Attention/Saliency Signal in Multimodal Brain-Tumour MRI Segmentation (2020–2026)

> Scope note: focus is brain MRI (T1/T1c/T2/FLAIR), BraTS-family datasets. Several of the most on-point papers are **2026 arXiv preprints** (IDs 2603.*, 2606.*) retrieved during this search; today is 2026-10-22, so these dates are valid, but treat them as recent, possibly not-yet-peer-reviewed preprints. Where WebFetch inferred content from a PDF it could not fully parse, that is flagged.

## Q1. How do current multimodal brain-tumour segmentation models FUSE modalities? Dominant approaches.

### Takeaway
The field is dominated by (a) **input-level/early fusion** (stack the 4 modalities as a 4-channel volume — nnU-Net) and (b) **modality-specific encoders + attention/cross-attention fusion** (mmFormer, RFNet, tri-attention, modality-aware mixers). Fusion is about *combining complementary information*; standard surveys do **not** list "modality disagreement as a saliency signal" as a recognized fusion category.

### Cited Findings
- **nnU-Net (early/4-channel fusion)** is the dominant strong baseline: BraTS inputs are the 4 co-registered sequences (T1n/T1c/T2w/T2f=FLAIR) stacked as channels; nnU-Net won BraTS 2020 with Dice 88.95 (WT) / 85.06 (TC) / 82.03 (ET) using region-based training, aggressive augmentation and BraTS-specific postprocessing — [nnU-Net for Brain Tumor Segmentation, Isensee et al., arXiv:2011.00848](https://arxiv.org/abs/2011.00848); [nnU-Net v2 4-modality model card](https://huggingface.co/NicoloPecco/nnUNet_BraTS_Metastases).
- **mmFormer (modality-specific encoders + modality-correlated cross-modal Transformer)**: hybrid CNN + intra-modal Transformer encoders per modality, plus a modality-correlated encoder for long-range inter-modal dependencies; designed for *incomplete* (missing) modalities; +19.07% average Dice with only one modality available — [mmFormer, Zhang et al., MICCAI 2022, arXiv:2206.02425](https://arxiv.org/abs/2206.02425).
- **RFNet (Region-aware Fusion Network)**: adaptively aggregates multi-modal features by exploiting spatial relationships between modalities and tumour sub-regions; a leading missing-modality method — summarized in [mmFormer survey/related work](https://arxiv.org/pdf/2206.02425).
- **Modality-Aware and Shift Mixer (MASM)**: a Modality-Aware module models specific modality-pair relationships at low levels; a Modality-Shift module explores cross-modal relationships at high levels via self-attention (fusion of intra- and inter-modality dependencies) — [MASM, arXiv:2403.02074](https://arxiv.org/abs/2403.02074v1). (Full PDF would not parse; details from arXiv abstract/search summary.)
- **Cross-Modality Deep Feature Learning**: cross-modality feature transition (CMFT) + cross-modality feature fusion (CMFF) — "transit and fuse knowledge across modalities" — [Zhang et al., Pattern Recognition, arXiv:2201.02356](https://arxiv.org/pdf/2201.02356).
- **Tri-Attention fusion** (modality-attention + spatial-attention + correlation-attention paths) for 3D multimodal BraTS — [Tri-Attention fusion guided network, Pattern Recognition](https://www.datalearner.com/academic/journal-papers/0031-3203/volumes-and-issues/503/paper-detail/26381).
- **Survey taxonomy**: a 2024 prospective survey categorizes by architecture (CNN / Transformer / hybrid) and names attention-based fusion (MAF-Net, AABTS-Net), cross-attention fusion (TransConver's CAFGL), and modality-specific-encoder designs (MM-BiFPN) as the main fusion patterns; nnU-Net, mmFormer, RFNet, ViTs are the recurring dominant methods — [Abidin et al., 2024, PMC11298476](https://pmc.ncbi.nlm.nih.gov/articles/PMC11298476/).

### Inferences
- The canonical fusion strategies treat each modality as a *complementary information source* and learn attention weights to emphasize informative modalities/regions — none of the standard taxonomies frame inter-modality *disagreement itself* as the quantity to attend to.

### Gaps
- Could not extract MASM's exact datasets/Dice from the PDF; relied on abstract-level summary.

## Q2. Has anyone explicitly computed a modality-DISAGREEMENT / discrepancy / variance-across-modalities map and used it as attention/saliency/extra channel to guide segmentation?

### Takeaway
**Partially, and very recently.** The closest and most direct precedent is **ReCoSeg/ReCoSeg++**, which turns a *cross-modal reconstruction residual* ("where synthesized T1c disagrees with real T1c") into an error-aware attention prior and feeds it as an extra 4th channel. **EnTrust (2026)** explicitly decomposes multimodal features into a "spatially localized conflict" component and uses it to condition segmentation. However, **no paper I found computes a direct, model-free variance/disagreement map across the four co-registered raw modalities and uses that as a spatial attention prior** — the precedents all route disagreement through a learned synthesis/reconstruction or feature-decomposition step.

### Cited Findings
- **ReCoSeg / ReCoSeg++ — strongest direct analog.** A residual-guided DDPM synthesizes T1ce from FLAIR/T1/T2; **residual maps = voxel-wise absolute difference between real and predicted T1ce**, serving as "dynamic error-aware priors that guide segmentation more precisely toward tumour regions." ReCoSeg++ **fuses FLAIR, T1, T2 + residual map into a 4-channel input** to a 2D U-Net head. Original ReCoSeg: Dice 91.7% / IoU 85.3% (WT, BraTS 2020); ReCoSeg++: Dice ~93.02% / IoU 86.7% (BraTS 2021, >1,250 subjects) — [ReCoSeg++, Yavari, Pandya, Furst, arXiv:2508.01058](https://arxiv.org/abs/2508.01058); [HTML version](https://arxiv.org/html/2508.01058v1). This is cross-modal *disagreement-as-saliency*, but disagreement is defined only for the single synthesized modality (T1ce), not as variance across all four.
- **EnTrust — explicit inter-modal conflict as signal (2026).** Decomposes multimodal features into three parts: shared anatomical consensus, modality-specific cues, and **"spatially localized conflict signals"** (extracted by an EnFuse module via a cross-covariance independence objective). Conflict signals condition **SegDiff**, a diffusion segmentation model "whose sampled hypotheses diverge specifically in regions of modal disagreement"; a **TrustMap** turns divergence into calibrated pixel-wise uncertainty. Evaluated on 4 benchmarks spanning brain/cardiac/lesion/oncology (BraTS not explicitly named); SOTA accuracy, 40% lower calibration error — [EnTrust, Mahapatra, Das, Bozorgtabar, Ge et al., arXiv:2606.21384 (Jun 2026)](https://arxiv.org/abs/2606.21384). Note: conflict here primarily drives *uncertainty/trustworthiness*, not a hard spatial attention prior for localization.
- **DGRNet — disagreement-guided, but NOT inter-modality.** Disagreement comes from four *view-specific adapters* on a shared encoder-decoder (a within-model pseudo-ensemble), using prediction variance, pairwise soft-Dice disagreement, and predictive entropy to drive text-guided refinement of uncertain regions. Dataset TextBraTS (T1/T1ce/T2/FLAIR), Dice 87.6% (+2.4%), HD95 4.57mm (−11%) — [DGRNet, Mohammadi et al., arXiv:2603.21086 (Mar 2026)](https://www.alphaxiv.org/abs/2603.21086). Relevant as "disagreement-guided refinement," but the disagreement is across model views, not across MRI modalities.
- **MIMoSA — inter-modal coupling (foundational, MS lesions).** Uses novel covariance features from **inter-modal coupling regression** (relationships *between* FLAIR/T2/T1/PD) plus mean structure to model per-voxel lesion probability — an early example of inter-modality statistical relationship as a segmentation feature, though not framed as attention/saliency — [MIMoSA, Valcarcel et al.](https://scholar.usuhs.edu/en/publications/mimosa-an-automated-method-for-intermodal-segmentation-analysis-o/); [PMC6030441](https://pmc.ncbi.nlm.nih.gov/articles/PMC6030441).
- **MoSID (breast MRI, adjacent domain)**: disentangles modality-specific information to extract **both intra- and inter-modality attention maps** as complementary clues for tumour segmentation — closest "inter-modality attention map" framing, but not brain and not disagreement-as-such — [MoSID, MICCAI/related](https://kms.shanghaitech.edu.cn/handle/2MSLDSTB/346421).
- **MRADE-Net**: multi-modality reconstruction attention using orthogonal 2D coefficient maps to build a 3D attention map weighting modalities — attention derived from reconstruction, adjacent to the residual idea — (from search summary; [IEEE Access 2022](https://doaj.org/article/ae983fed01134197b0d71b0e553b6a64)).

### Inferences
- The idea "where modalities disagree is where the lesion is" **has been instantiated indirectly** — via (i) cross-modal *reconstruction residual* (ReCoSeg) and (ii) learned *feature conflict decomposition* (EnTrust). Both require a learned generative/decomposition model to surface disagreement.
- A **direct, interpretable disagreement map** (e.g., voxel-wise variance / Jensen-Shannon divergence / disagreement across the normalized co-registered T1/T1c/T2/FLAIR, computed without synthesis) used as an explicit spatial attention prior or extra input channel appears **genuinely unclaimed** for brain tumour segmentation.

### Gaps
- Could not confirm whether EnTrust's "brain" benchmark is BraTS specifically, nor its per-region Dice on brain data.
- ReCoSeg++ full-text dataset/results confirmed via search summary; the PDF itself did not parse for independent verification of exact numbers.

## Q3. Clinical modality roles (FLAIR→edema, T1c→enhancing rim) — any model encoding this clinical knowledge structurally?

### Takeaway
The clinical mapping is universally *acknowledged* and used to interpret sub-regions, and a few knowledge-guided / modality-aware models encode it softly (text priors, modality-pair attention), but structural hard-coding of "FLAIR governs whole-tumour/edema, T1c governs enhancing core" into the architecture is uncommon.

### Cited Findings
- Standard clinical roles are explicit in the literature: **FLAIR → whole tumour / edema delineation; T1c (gadolinium) → enhancing tumour / rim; T1/T2 for structure** — [prior-knowledge segmentation tool, arXiv:2109.14775](https://arxiv.org/pdf/2109.14775); sub-region classes (necrosis, edema, non-enhancing, enhancing) tied to modalities — [knowledge-guided segmentation summary](https://arxiv.org/html/2512.17566v1).
- **ReCoSeg structurally encodes one clinical role**: it specifically reconstructs **T1ce** (the enhancing-tumour modality) from the others, so its residual is biased toward the enhancing/active region — an implicit encoding of the T1c→enhancing-rim prior — [arXiv:2508.01058](https://arxiv.org/abs/2508.01058).
- **Knowledge-Guided / text-guided fusion**: methods inject clinical-text or semantic priors (e.g., Multi-modal Semantic Fusion Adapter + Bidirectional Interactive Visual-semantic Attention; TextBraTS-based DGRNet) to bring modality/region knowledge into the model — [Knowledge-Guided Synchronized Prior Fusion, arXiv:2507.08574](https://arxiv.org/pdf/2507.08574); [DGRNet TextBraTS](https://www.alphaxiv.org/abs/2603.21086).
- **Cross-modality guidance**: a primary modality guides secondary modalities during training to leverage complementary info while suppressing noise (a soft structural prior) — [Cross-modality Guidance-aided Multi-modal Learning with Dual Attention, arXiv:2401.09029](https://arxiv.org/abs/2401.09029v1).

### Inferences
- No retrieved model builds an explicit per-region routing of "this sub-region should be driven by this modality." The clinical mapping is mostly left for the network to learn implicitly or injected loosely via text/semantic priors — leaving room for a model that structurally ties modality-disagreement channels to specific sub-regions (e.g., T1-vs-T1c disagreement → enhancing core; FLAIR-vs-T1 disagreement → edema/whole tumour).

### Gaps
- Did not find a paper that hard-codes modality→sub-region attention routing; this may exist in niche venues not surfaced.

## Q4. Is modality disagreement used elsewhere (uncertainty, missing-modality, pseudo-labels) in overlapping ways? What remains unclaimed?

### Takeaway
Disagreement/variance signals are actively used for **uncertainty estimation and trustworthiness** (EnTrust, DGRNet) and inter-modal relationships are exploited for **missing-modality robustness** (mmFormer, RFNet) — but these use disagreement to flag *uncertainty* or to *reconstruct missing data*, not as a positive *spatial attention prior that says "attend here, the lesion is here."*

### Cited Findings
- **Disagreement → uncertainty/calibration**: EnTrust treats inter-modal conflict as the primary source of predictive uncertainty and produces calibrated pixel-wise uncertainty (TrustMap) — [arXiv:2606.21384](https://arxiv.org/abs/2606.21384); DGRNet converts prediction ambiguity into an "active mechanism for guiding targeted segmentation improvement in uncertain regions" — [arXiv:2603.21086](https://www.alphaxiv.org/abs/2603.21086).
- **Disagreement/conflict for trustworthy fusion**: EnTrust explicitly separates "conflict signals" from consensus — [arXiv:2606.21384](https://arxiv.org/abs/2606.21384).
- **Missing-modality / incomplete learning** exploits inter-modal correlation to compensate for absent modalities rather than to localize lesions: mmFormer, RFNet, knowledge-distillation adaptation ([No Modality Left Behind, arXiv:2509.15017](https://arxiv.org/pdf/2509.15017)), meta-guided MGML ([arXiv:2512.23936](https://arxiv.org/pdf/2512.23936)).
- **Residual/reconstruction error as prior**: ReCoSeg's residual is an error-aware prior (overlaps most with the target idea) — [arXiv:2508.01058](https://arxiv.org/abs/2508.01058).
- **Inter-rater (not inter-modality) disagreement**: UAS-Net models annotation/consensus disagreement with structure-aware weighting — a different disagreement axis, noted to avoid conflation — (from search summary of disagreement-modeling work).

### Inferences — what remains genuinely unclaimed
- **Unclaimed:** a *direct, explicit, model-free* cross-modality disagreement/variance/divergence map computed over the co-registered, intensity-normalized T1/T1c/T2/FLAIR and injected as (a) an explicit spatial **attention prior** or (b) an extra **input channel** to *localize* the lesion for segmentation on BraTS.
- **Unclaimed:** framing disagreement as a *positive saliency/localization* signal ("disagreement = lesion presence") rather than as *uncertainty to down-weight* or *data to reconstruct*.
- **Unclaimed:** structurally tying specific *modality-pair* disagreement channels to specific tumour sub-regions (clinical-role-aware disagreement attention).
- **Closest prior art to differentiate against in any novelty claim:** ReCoSeg/ReCoSeg++ (residual-as-attention channel, but via learned T1ce synthesis, single modality) and EnTrust (learned conflict decomposition → uncertainty, not a localization prior). Any new work must position against these two explicitly.

### Gaps
- Could not find a negative-result or explicit statement in the literature saying "nobody has used raw cross-modality variance as an attention prior" — this conclusion is inferred from the absence of such a method across the fusion survey and ~15 targeted searches, not from a direct citation.
- Scholar/IEEE TMI and MICCAI/BrainLes proceedings were only partially covered via arXiv/PMC mirrors; a dedicated proceedings search could surface additional niche candidates.
