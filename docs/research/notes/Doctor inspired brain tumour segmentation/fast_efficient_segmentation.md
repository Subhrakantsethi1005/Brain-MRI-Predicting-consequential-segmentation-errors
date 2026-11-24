# Fast / Lightweight / Efficient / Real-time 3D Brain-Tumour MRI Segmentation (2021–2026)

Scope: efficient 3D volumetric brain-tumour segmentation (BraTS-scale), the efficiency techniques used, their params/FLOPs/latency/memory, accuracy vs standard baselines, and what a new "fast, efficient, doctor-like" method must beat. Laptop / 6 GB-VRAM feasibility assessed throughout.

---

## Key Question 1: Main efficient/lightweight 3D approaches (with param/FLOP/latency numbers)

### Takeaway
The field spans four families — (a) lightweight CNN U-Nets with attention/parallel convs, (b) knowledge distillation into compact students, (c) efficient hybrid transformers (SlimUNETR, UNETR++), and (d) Mamba / state-space models (SegMamba, LightM-UNet, and 2025–26 state-space successors). Sub-2M-parameter models now match or beat the 5.9M standard 3D U-Net and approach nnU-Net accuracy, but low parameter count does NOT guarantee low FLOPs or low latency (Mamba models can still be heavy in GFLOPs).

### Cited Findings

**Baselines (what new work is measured against):**
- Standard 3D U-Net: ~5.89M params / 148.17G FLOPs (one commonly cited config); a second source lists 5.65M params. BraTS2020 Dice ~73.5% ET / 89.4% WT / 81.9% TC — [LHC-Net / BMC Bioinformatics](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9749147/); [LATUP-Net](https://ar5iv.labs.arxiv.org/html/2404.05911)
- nnU-Net: ~181.56M params — treated as the heavy, high-accuracy reference baseline — [LATUP-Net](https://ar5iv.labs.arxiv.org/html/2404.05911)
- SwinUNETR: large (≈62M params class); ~34,000 MB training memory, 9,480 MB inference memory, 1.68 cases/s — used as the "heavy transformer" baseline — [SegMamba, Table 9](https://ar5iv.labs.arxiv.org/html/2401.13560)

**(a) Lightweight CNN U-Nets:**
- **LHC-Net** (Lightweight Hierarchical Convolution Network, 2022): 1.65M params / 35.58G FLOPs (~2× fewer params, ~3× less compute than 3D U-Net). BraTS2020 Dice 76.38% ET / 90.01% WT / 83.32% TC — beats 3D U-Net — [PMC9749147](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9749147/)
- **LATUP-Net** (Lightweight 3D Attention U-Net w/ Parallel Convolutions, 2024): 3.07M params (59× fewer than nnU-Net's 181.56M). BraTS2020 Dice 73.67% ET / 88.41% WT / 83.82% TC; BraTS2021 (5-fold) 83.92% ET / 90.29% WT / 89.54% TC. GPU: single NVIDIA V100 16GB, batch 1. FLOPs and inference latency NOT reported — [LATUP-Net arXiv 2404.05911](https://ar5iv.labs.arxiv.org/html/2404.05911)
- **MBDRes-U-Net** (Multi-scale lightweight, 2024) and a lightweight U-Net on optimal MRI slices also reported — [MBDRes arXiv 2411.01896](https://arxiv.org/pdf/2411.01896)

**(b) Knowledge distillation:**
- **Uni-Light** (Ultra-lightweight, uncertainty-aware KD, 2026): 1.52M params (97.56% reduction vs teacher) / 214.10G FLOPs (73.03% reduction) / 289 ms per scan / 1,547 MB inference memory / 4,059 MB training memory on a single NVIDIA T4. BraTS2023-GLI Dice 89.97% avg (teacher Res-UNet 85.66%); MSD-BTS 84.40%. Claims 3.5× faster than SwinUNETR, 4.7× faster than SegMamba; explicitly targets edge/resource-constrained clinical deployment — [Uni-Light arXiv 2609.06729](https://arxiv.org/html/2609.06729)
- Other KD lines: multi-modal→mono-modal KD ([arXiv 2106.09564](https://arxiv.org/pdf/2106.09564)); Detail-Consistent Stage-Wise Distillation (wavelet-domain, 2026, [alphaXiv 2605.26382](https://www.alphaxiv.org/abs/2605.26382)); MST-KDNet (multi-scale transformer KD, MICCAI 2025); "Efficient KD for Brain Tumor Segmentation" (Applied Sciences 2022, [doi 10.3390/app122311980](https://doi.org/10.3390/app122311980))

**(c) Efficient hybrid transformers:**
- **SlimUNETR** (IEEE TMI 2023, DOI 10.1109/TMI.2023.3326188): CNN+transformer hybrid with self-attention decomposition. BraTS2021 Dice 92.44%, **34.6× smaller and 13.4× faster inference than Swin UNETR**; uses throughput as the efficiency metric; explicitly positioned for resource-constrained devices. (Exact absolute params/FLOPs not captured — see Gaps.) — [IEEE TMI](https://unpaywall.org/10.1109%2FTMI.2023.3326188)
- **UNETR++** (efficient paired-attention): 71% reduction in both params AND FLOPs vs the best prior method; evaluated on Synapse, BTCV, ACDC, BraTS, Decathlon-Lung — [UNETR++ GitHub](https://github.com/Amshaker/unetr_plus_plus)

**(d) Mamba / state-space models:**
- **SegMamba** (MICCAI 2024): accuracy-focused, not ultra-light. BraTS2023 Dice 91.32% avg (93.61% WT / 92.65% TC / 87.71% ET), input 128³, trained on 4× A100. Inference memory 6,279 MB, inference 1.51 cases/s. Linear-complexity alternative to self-attention (self-attention baseline went OOM in their study) — [SegMamba arXiv 2401.13560](https://ar5iv.labs.arxiv.org/html/2401.13560)
- **LightM-UNet** (2024): 1.87M params (3D) / **457.62 GFLOPs (3D)** — note GFLOPs stay high despite tiny param count. vs nnU-Net: 47.39× fewer params, 15.82× less compute; vs U-Mamba: 224× fewer params. GPU: Quadro RTX 8000. Validated on LiTS (3D liver CT) + lung X-ray — NOT on brain tumour. (Abstract elsewhere claims 116×/21× vs nnU-Net — conflicts with the 47.39×/15.82× table values.) — [LightM-UNet arXiv 2403.05246](https://arxiv.org/html/2403.05246v1)
- **SuperLightNet** (CVPR 2025): random-multiview-drop encoder + learnable residual skip decoder. 95.59% param reduction, 96.78% compute-efficiency gain, 96.86% memory-access improvement, +0.21% avg Dice vs SOTA on BraTS2019 + BraTS2021 — [SuperLightNet CVPR 2025](https://openaccess.thecvf.com/content/CVPR2025/papers/Yu_SuperLightNet_Lightweight_Parameter_Aggregation_Network_for_Multimodal_Brain_Tumor_Segmentation_CVPR_2025_paper.pdf); code [GitHub](https://github.com/WTU1020-Medical-Segmentation/SuperLightNet)
- **MedNeXt** (MICCAI 2023, ConvNeXt-scaled): BraTS21 Dice ~88.01% (MedNeXt-L 5×5×5 ensemble). An **EfficientMedNeXt** variant reports EfficientMedNeXt-L at 87.0% BTCV Dice with 96.5% fewer params / 77.03% lower FLOPs, and -S with 98.5% fewer params / 95% fewer FLOPs — [MedNeXt arXiv 2303.09975](https://arxiv.org/pdf/2303.09975)
- 2025–26 successors (state-space + MoE / lightweight): **M4Fuse** (lightweight state-space MoE, [arXiv 2605.02444](https://arxiv.org/pdf/2605.02444)); **SegMaFormer** (hybrid state-space+transformer, [arXiv 2603.22002](https://arxiv.org/pdf/2603.22002)); **Graph-based multi-modal lightweight** ([arXiv 2507.09995](https://arxiv.org/pdf/2507.09995)); lightweight transformer w/ contextual synergic enhancement ([arXiv 2603.23390](https://arxiv.org/pdf/2603.23390)); **PocketNet** (smaller CNN, [arXiv 2104.10745](https://arxiv.org/pdf/2104.10745))

### Inferences
- Pruning/quantization as standalone techniques are under-represented in the top-cited brain-tumour literature; the dominant levers are architectural (lightweight blocks, efficient attention, state-space) and distillation.
- The "winning" current recipe for ultra-light brain-tumour is compact multi-scale CNN + distillation (Uni-Light) or state-space aggregation (SuperLightNet), both hitting ~1.5M params with ~90% WT-class Dice.

### Gaps
- SlimUNETR absolute params/FLOPs not captured (only relative 34.6×/13.4× vs Swin UNETR and BraTS2021 Dice 92.44%); IEEE TMI PDF behind access control.
- Quantization/INT8 and ONNX/TensorRT-deployment numbers for brain-tumour 3D models not found.

---

## Key Question 2: Efficiency metrics the field reports + typical numbers on one mid-range GPU

### Takeaway
Standard reported metrics are: parameter count (M), FLOPs/GFLOPs (spatial vs time complexity), inference latency (ms/scan or cases/sec, sometimes throughput/FPS), and GPU memory (training and inference, in MB/GB). Typical BraTS-scale (128³ patch, 4 modalities) single-GPU inference memory is ~6 GB for a mid-weight model and ~1.5 GB for an ultra-light one; latency ranges from ~0.3 s to ~1–2 cases/s.

### Cited Findings
- Metric definitions: "FLOPs = floating-point ops per forward pass; Params = spatial complexity, FLOPS = time complexity," reported alongside inference time — [LATUP-Net](https://ar5iv.labs.arxiv.org/html/2404.05911)
- Throughput (cases/sec or volumes/sec) is an explicit efficiency indicator — used by SlimUNETR ([IEEE TMI](https://unpaywall.org/10.1109%2FTMI.2023.3326188)) and SegMamba (cases/s) ([SegMamba](https://ar5iv.labs.arxiv.org/html/2401.13560))
- Typical memory/latency at 128³ input: SegMamba 6,279 MB inference / 1.51 cases/s; large-kernel-conv variant 5,776 MB / 1.92 cases/s; SwinUNETR 9,480 MB / 1.68 cases/s; full self-attention = OOM — [SegMamba Table 9](https://ar5iv.labs.arxiv.org/html/2401.13560)
- Ultra-light end: Uni-Light 1,547 MB inference memory, 289 ms/scan, 4,059 MB training memory on a single T4 — [Uni-Light](https://arxiv.org/html/2609.06729)
- Standard 3D U-Net reference compute: ~148 GFLOPs at 5.89M params — [PMC9749147](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9749147/)
- A 2026 "unified benchmark" explicitly evaluates 3D U-Net, SegResNet, Swin UNETR, SegMamba, SegMambaV2 on BraTS2023 + BraTS2024 using accuracy + inference time + model size as the comparison axes — [Unified Benchmark alphaXiv 2607.28858](https://www.alphaxiv.org/abs/2607.28858)

### Inferences
- A credible efficiency paper is expected to report at minimum the 4-tuple {params, FLOPs/GFLOPs, latency or throughput, GPU memory} plus the GPU model — reporting only params (as LATUP-Net does) is now considered incomplete.
- GFLOPs and params are partly decoupled: LightM-UNet (1.87M params but 457 GFLOPs) shows a tiny model can be compute-heavy, so latency/FLOPs must be reported, not inferred from param count.

### Gaps
- Few papers report wall-clock latency on genuinely low-end hardware (laptop iGPU / 6 GB consumer GPU); most use V100/A100/T4/RTX 8000.

---

## Key Question 3: Efficiency combined with attention/ROI/cascade; ~6 GB-VRAM feasibility

### Takeaway
Yes — several methods combine efficiency with attention (LATUP-Net, UNETR++ efficient paired-attention, SlimUNETR decomposed self-attention) or multi-scale/ROI design (MBDRes, Uni-Light's compact multi-scale). 6 GB VRAM inference is clearly feasible for the ultra-light class; 6 GB training is borderline and typically needs patching/small batch.

### Cited Findings
- Attention + efficiency: LATUP-Net = parallel convolutions + attention at 3.07M params ([LATUP-Net](https://ar5iv.labs.arxiv.org/html/2404.05911)); UNETR++ = efficient paired attention, 71% fewer params+FLOPs ([UNETR++](https://github.com/Amshaker/unetr_plus_plus)); SlimUNETR = self-attention decomposition for resource-constrained devices ([IEEE TMI](https://unpaywall.org/10.1109%2FTMI.2023.3326188))
- 6 GB feasibility (inference): Uni-Light uses 1,547 MB inference / 4,059 MB training on a T4, explicitly for "edge-computing settings" and avoiding OOM on standard hardware — comfortably within 6 GB — [Uni-Light](https://arxiv.org/html/2609.06729)
- SegMamba's own 128³ inference needs ~6,279 MB — right at the 6 GB limit for a mid-weight model — [SegMamba](https://ar5iv.labs.arxiv.org/html/2401.13560)
- SlimUNETR claims SOTA accuracy/size/efficiency "when deployed on resource-constrained devices," 13.4× faster inference than Swin UNETR — [SlimUNETR](https://unpaywall.org/10.1109%2FTMI.2023.3326188)

### Inferences
- A 6 GB consumer GPU (e.g. laptop RTX) can run inference for ultra-light (≤2M param, ≤1.6 GB) and most mid-weight 128³ models, but full-volume or multi-modal batch>1 training on 6 GB generally requires patch-based training and gradient checkpointing.
- Heavy transformers (SwinUNETR ~9.5 GB inference) and full self-attention (OOM) are NOT 6 GB-feasible — this is precisely the gap lightweight/Mamba/distilled methods exploit.

### Gaps
- No source gives a direct, measured benchmark of these models on a specific 6 GB consumer/laptop GPU; feasibility is inferred from reported A100/T4 memory figures.

---

## Key Question 4: What a NEW method must show; how saturated is the field?

### Takeaway
The efficiency niche is heavily contested and near-saturated at the extremes: multiple 2024–2026 methods already hit ~1.5M params with ~90% WT-class Dice, and reductions of 95–98% in params/FLOPs vs standard baselines are now routine. A new method cannot win on raw compression alone; it needs a genuinely Pareto-dominant point (equal/better Dice AND better on ≥1 efficiency axis) AND a differentiator (e.g. the "doctor-like"/ROI/uncertainty angle, measured latency on truly low-end hardware, or robustness).

### Cited Findings
- Compression benchmarks a new method must beat: 95.59% param reduction + 96.78% compute reduction at +0.21% Dice (SuperLightNet, BraTS2019/2021) ([SuperLightNet](https://openaccess.thecvf.com/content/CVPR2025/papers/Yu_SuperLightNet_Lightweight_Parameter_Aggregation_Network_for_Multimodal_Brain_Tumor_Segmentation_CVPR_2025_paper.pdf)); 97.56% param / 73.03% FLOP reduction while BEATING the teacher (Uni-Light, +4.3% Dice over teacher) ([Uni-Light](https://arxiv.org/html/2609.06729)); 34.6× smaller + 13.4× faster than Swin UNETR at 92.44% BraTS2021 Dice (SlimUNETR) ([IEEE TMI](https://unpaywall.org/10.1109%2FTMI.2023.3326188))
- Accuracy ceiling to stay competitive: BraTS WT Dice ~90–93%, TC ~89–92%, ET ~84–88% is the current lightweight-competitive band (LATUP-Net, SuperLightNet, SlimUNETR, SegMamba, Uni-Light all cluster here) — [LATUP-Net](https://ar5iv.labs.arxiv.org/html/2404.05911); [SegMamba](https://ar5iv.labs.arxiv.org/html/2401.13560); [Uni-Light](https://arxiv.org/html/2609.06729)
- The field is actively benchmarking efficiency-vs-accuracy tradeoffs as a first-class question (2026 unified benchmark of 5 models on BraTS2023/2024) — signals the community now expects explicit tradeoff curves, not single-point claims — [Unified Benchmark](https://www.alphaxiv.org/abs/2607.28858)
- Rapid 2025–2026 churn (M4Fuse, SegMaFormer, graph-lightweight, contextual-synergic transformer, SuperLightNet) confirms crowding — [arXiv 2605.02444](https://arxiv.org/pdf/2605.02444); [arXiv 2603.22002](https://arxiv.org/pdf/2603.22002); [arXiv 2507.09995](https://arxiv.org/pdf/2507.09995)

### Inferences
- A defensible efficiency claim in 2026 must: (1) report the full {params, FLOPs, latency, memory, GPU} tuple; (2) show a Pareto point not dominated by SuperLightNet/Uni-Light/SlimUNETR (i.e., ≥ their Dice at ≤ their params/FLOPs/latency, OR clearly better Dice at comparable cost); (3) ideally demonstrate on BraTS2023/2024 (newer, harder: post-treatment glioma, meningioma) not just BraTS2020/2021; and (4) add a non-compression differentiator — this is where a "doctor-like" ROI/cascade/uncertainty mechanism (cf. Uni-Light's uncertainty-aware KD) can carve defensible novelty rather than competing on FLOPs alone.
- Pure "smaller + same Dice" is largely saturated; the open space is measured real-hardware/edge latency, robustness/domain shift, and clinically-motivated mechanisms — not another percentage-point of param reduction.

### Gaps
- No single head-to-head table was found placing SuperLightNet, Uni-Light, SlimUNETR and MedNeXt on identical hardware/data, so the true current Pareto frontier is assembled from heterogeneous papers (different GPUs, BraTS years, splits) and should be read with that caveat.
- Absolute params/FLOPs for SlimUNETR and absolute params for SuperLightNet not pinned down (only relative reductions).
