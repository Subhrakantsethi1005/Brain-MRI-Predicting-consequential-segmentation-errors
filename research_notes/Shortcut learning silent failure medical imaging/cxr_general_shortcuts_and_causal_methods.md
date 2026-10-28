# Shortcut Learning & Silent Failure in Medical Imaging (CXR + general): Prior Art and Causal-Proof Methods

**Purpose:** Establish (JOB 1) exactly what "another shortcut paper" looks like so we know what is already TAKEN and cannot be claimed as novel, and (JOB 2) the methods for rigorously *proving causal reliance* on a shortcut, with emphasis on what is feasible on a ~6 GB laptop GPU without training large models.

**Survey date:** 2026-10-23. Target venue: BIOAI-2026.

**Provenance note / honesty flag:** Landmark citations below were located via web search and carry stable, real identifiers (arXiv IDs, DOIs, venue pages) that I verified by title/author/venue match. A handful of *very recent* (2025-2026) hits surfaced by search carry arXiv-style IDs I could **not** independently confirm (flagged inline with ⚠). Treat the flagged ones as "exists in this space, verify the exact ID before citing." Nothing here should be cited in a paper without opening the source PDF.

---

## JOB 1 — The "shortcut / spurious correlation" prior art in CXR & medical imaging (the NOVELTY BAR)

**Bottom line for novelty:** The existence of shortcuts in CXR/medical imaging is *thoroughly established and canonical*. Simply demonstrating that a CXR model (or any medical imaging model) "uses a spurious feature," "fails to generalize across hospitals," "learns a confounder/treatment artifact," or "can predict demographics" is **TAKEN** and will be rejected as non-novel at a serious venue. Below is the map of what is already owned.

### A. Landmark / foundational works

| Work | Shortcut / finding | Status |
|---|---|---|
| **Zech, Badgeley, Liu, Costa, Titano, Oermann (2018)**, *Confounding variables can degrade generalization performance of radiological deep learning models.* PLOS Medicine 2018; arXiv **1807.00431**. | CNNs detect **hospital system / department / scanner (portable vs fixed)** and calibrate disease predictions to site prevalence. Pneumonia AUC dropped significantly on external hospitals in 3/5 comparisons. The archetypal "hospital-system shortcut." | **TAKEN** — the founding citation. |
| **DeGrave, Janizek, Lee (2021)**, *AI for radiographic COVID-19 detection selects shortcuts over signal.* Nature Machine Intelligence 3:610-619; preprint medRxiv 2020.09.13.20193565. | COVID CXR classifiers rely on **dataset-source confounders**: text/laterality markers, patient positioning, shoulder/diaphragm framing, image-processing fingerprints — not lung pathology. Used saliency + generative adversarial counterfactuals to show it. | **TAKEN** — the canonical COVID-CXR shortcut paper; also a *methods* reference (see JOB 2). |
| **Geirhos, Jacobsen, Michaelis, Zemel, Brendel, Bethge, Wichmann (2020)**, *Shortcut learning in deep neural networks.* Nature Machine Intelligence 2:665-673; arXiv **2004.07780**. | Defines the whole framework: shortcuts = decision rules that ace i.i.d. benchmarks but fail under distribution shift. The field-defining conceptual citation (not CXR-specific). | **TAKEN** — the term-defining paper. |
| **Oakden-Rayner, Dunnmon, Carneiro, Ré (2020)**, *Hidden Stratification Causes Clinically Meaningful Failures in Machine Learning for Medical Imaging.* ACM CHIL 2020; arXiv **1909.12475**. | **"Silent failure" / hidden stratification**: aggregate AUC looks great while an unlabeled clinically important subgroup fails. Directly owns the "silent subgroup failure" framing. | **TAKEN** — owns the "silent failure under good average metrics" story. |

### B. Treatment / device / annotation confounders (the "mark of treatment, not disease" class)

| Work | Shortcut | Status |
|---|---|---|
| **Chest drains in pneumothorax** — documented across several works (e.g., Oakden-Rayner's hidden-stratification examples; Jiménez-Sánchez et al.; and the "Exploiting and Preventing Shortcuts" line, arXiv **2009.10132**). | Chest drain = tube inserted to *treat* pneumothorax, so it co-occurs with positive labels. DenseNet-121 on NIH-CXR14 reportedly ~0.94 AUROC on drain-present pneumothorax vs ~0.77 on drain-absent — model learned the **treatment marker**, not the collapsed lung. | **TAKEN** — the textbook device-confounder example. |
| **Laterality tokens / L-R lead markers / view-position (PA vs AP) / technologist initials / hospital burn-in text.** Covered by DeGrave 2021, Zech 2018, and the laterality-marker detection work (YOLOv3 marker-obscuration; MIDL 2020 Hashir et al.) and arXiv **2009.10132**. | Physical lead markers, burned-in text, and view/positioning differ systematically by site and acquisition protocol and leak the label. Standard mitigation = detect + obscure markers. | **TAKEN** — annotation/text/laterality shortcuts are explicitly catalogued. |
| **Pacemakers, lines, ECG leads, support devices** as co-occurring with ICU/sick status → shortcut for various pathologies. | Devices tag the "sick/portable/bedside" population; same mechanism as chest drains. | **TAKEN** (within the device-confounder family). |
| ⚠ Recent (2025-2026) real-world probe studies, e.g. *"Look What the Probes Dragged In! Real-World Chest X-ray Shortcuts in MedCLIP"* and layer-probe analyses locating *where* in the network the drain signal separates. | Extends device-shortcut work to **foundation/vision-language models (MedCLIP)** and uses linear probes per layer to localize the shortcut. | ⚠ ID unverified — but signals the frontier has moved to foundation models. |

### C. Demographic shortcuts (model reads protected attributes off the pixels)

| Work | Shortcut | Status |
|---|---|---|
| **Gichoya et al. (2022)**, *AI recognition of patient race in medical imaging: a modelling study.* Lancet Digital Health 4(6):e406-e414; PMID **35568690**. | Models predict **self-reported race** from CXR, CT, mammography with high AUC, robust to heavy degradation/cropping/low-pass filtering. No known human-visible correlate. "Hidden signals" the model can exploit → a latent confounding axis for any downstream task. | **TAKEN** — the definitive race-detection paper. |
| **Age & sex from CXR** — e.g. *Using Deep Neural Networks for Predicting Age and Sex in Healthy Adult Chest Radiographs* (Radiology/PMC8509558) and related. | Sex AUC >0.99 (~98% acc); age MAE ~2 years. Demographics are trivially readable → available as shortcuts/confounders. | **TAKEN**. |
| **Seyyed-Kalantari, Zhang, McDermott, Chen, Ghassemi (2021)**, *Underdiagnosis bias of AI algorithms applied to chest radiographs in under-served patient populations.* Nature Medicine 27:2176-2182. | CXR classifiers **selectively underdiagnose** (false "no finding") females, under-20s, Black, Hispanic, Medicaid patients, worst at intersections. The fairness/subgroup-silent-failure anchor. | **TAKEN** — the fairness/underdiagnosis anchor. |
| **Glocker, Jones, Roschewitz, Winzeck et al. (~2023)**, *Algorithmic encoding of protected characteristics in CXR disease detection models* (and follow-ups). | Shows disease models **encode race/sex/age in their features** even when not asked to, linking demographic encoding → bias. | **TAKEN** (demographic encoding → fairness bias link). |

### D. What counts as "just another shortcut paper" (do NOT claim as novel)
- "We found model X uses spurious feature Y in CXR." (Zech/DeGrave own this.)
- "Model fails to generalize to an external hospital." (Zech owns this.)
- "A treatment device / annotation marker / positioning drives the prediction." (drain/marker literature owns this.)
- "Average AUC hides a failing subgroup." (Oakden-Rayner owns this.)
- "The model can read demographics / is unfair to subgroup Z." (Gichoya, Seyyed-Kalantari, Glocker own this.)
- "Saliency shows the model looks at the wrong place." (DeGrave + Lapuschkin own this, and saliency alone is not proof — see JOB 2.)

**Implication for a BIOAI-2026 paper:** Novelty must come from something *beyond* demonstrating a shortcut exists. Viable differentiators: (i) a **new causal-proof methodology** feasible on modest hardware; (ii) a shortcut in an **under-studied modality/task** (e.g., brain MRI segmentation-error / consequential-error prediction — note this is the user's actual project) rather than CXR classification; (iii) connecting shortcut reliance to a **downstream clinical-decision harm** that is quantified, not just AUC drop; (iv) a **detection/abstention mechanism** rather than yet another demonstration. CXR is the saturated baseline that sets the bar — the paper should position CXR findings as *known prior art* and claim contribution elsewhere.

---

## JOB 2 — Methods to PROVE causal reliance on a shortcut (laptop-feasible focus)

Guiding distinction: **correlation evidence** (saliency overlaps with the feature; subgroup AUC differs) only *suggests* a shortcut. **Causal evidence** requires an *intervention*: change the suspected feature while holding the pathology fixed (or vice versa) and measure the prediction change. Below, each method is rated for what it proves, what it cannot, and 6 GB-GPU feasibility.

### Survey/framework anchors (read first)
- **Brown, Tomasev, Freyberg, Liu, Karthikesalingam, Schrouff et al. / and Steinmann, Pfrommer, et al. (2024)**, *Navigating Shortcuts, Spurious Correlations, and Confounders: From Origins via Detection to Mitigation.* arXiv **2412.05152**. Taxonomy of detection methods: (1) assess model utility, (2) perturbation-based, (3) XAI-based, (4) causality-based. Good scaffold for a Methods/Related-Work section.
- **Geirhos et al. 2020** (above) for the conceptual frame; **Lapuschkin et al. 2019** (below) for the Clever-Hans framing.

### Method 1 — Controlled interventions / counterfactual edits (mask, inpaint, remove) — THE GOLD STANDARD on a laptop
- **What it proves:** *Causal* reliance. If you remove/mask/inpaint the suspected shortcut (e.g., paint out the chest drain, blank the corner text, obscure the L/R marker) and performance *drops specifically on the shortcut-correlated cases*, the model was causally using it. Conversely, transplanting the shortcut onto negatives and seeing predictions flip is strong provocation evidence.
- **What it cannot prove:** That the *only* mechanism is the shortcut (model may use several); inpainting can introduce its own artifacts (confound the confound); masking changes image statistics, so a performance drop could be partly from distribution shift rather than the feature per se. Mitigate by masking a *control* region of equal size/location.
- **Compute / laptop feasibility:** **Excellent.** Simple masking/occlusion, corner-cropping, and classical inpainting (OpenCV Telea/Navier-Stokes) are **CPU-only / near-free**. You run *inference only* on an already-trained model — no training. Diffusion-based counterfactual inpainting is heavier but a small latent-diffusion/inpainting model can run on 6 GB at low resolution; classical inpainting is the safe default.
- **Key citations:** DeGrave et al. 2021 (generative counterfactuals on COVID CXR, Nat Mach Intell); **COIN: Counterfactual Inpainting for weakly supervised segmentation**, arXiv **2404.12832** (inpainting-based counterfactuals in medical images); diffusion counterfactual/anomaly work arXiv **2308.02062**. ⚠ Several 2025-26 "diffusion counterfactual to remove shortcut and measure Δperformance" papers exist (IDs unverified).

### Method 2 — "Confound-only" / shortcut-only training (measure exploitable signal)
- **What it proves:** An *upper bound on the information leak*. Train (or linearly probe) a model on **only the suspected shortcut channel** — e.g., image corners/borders only, image with the lung field blacked out, heavily low-pass/downsampled image, or metadata alone — to predict the label. Above-chance performance proves the shortcut *carries exploitable signal*; this is how Gichoya proved race is readable from degraded images and how "background-only" baselines work in natural images.
- **What it cannot prove:** That the *target* model actually used it (it proves availability, not usage — pair with Method 1 for usage).
- **Compute / laptop feasibility:** **Excellent.** You are training tiny models on degraded/cropped inputs, or just logistic-regression probes on frozen features. Fits 6 GB easily; often CPU-only.
- **Key citations:** Gichoya et al. 2022 (degraded-image race prediction); background/confound-only baselines discussed in the shortcut survey arXiv 2412.05152; Shortcut Detection with VAEs arXiv **2302.04246**.

### Method 3 — Out-of-distribution / subgroup stress splits (shortcut-balanced test sets)
- **What it proves:** Behavioral dependence. Construct test splits where the shortcut-label correlation is **broken or reversed** (e.g., pneumothorax *without* drains vs *with*; disease cases from the "wrong" hospital). A large AUC gap between shortcut-aligned and shortcut-conflicting subgroups is strong evidence of reliance; reversed-correlation splits are near-causal.
- **What it cannot prove:** The *mechanism* (which pixels) — only that performance tracks the shortcut distribution. Needs subgroup labels (drain annotations, site, demographics), which may be unavailable → see hidden-subgroup discovery.
- **Compute / laptop feasibility:** **Excellent** — inference only on curated splits. Free.
- **Key citations:** Oakden-Rayner et al. 2020 (hidden stratification 1909.12475); Zech 2018 (cross-hospital); the drain-stratified pneumothorax evaluations; slice-discovery for finding failing subgroups when labels are missing (*Domino* / slice-discovery, arXiv **2406.12142** context).

### Method 4 — Saliency / attribution audits (necessary but NOT sufficient; include the caveat)
- **What it proves:** Weak, *correlational* localization — "the model attends to region R." Useful for hypothesis generation.
- **What it CANNOT prove:** Causation, and can be actively misleading. **Adebayo et al., Sanity Checks for Saliency Maps, NeurIPS 2018 (arXiv 1810.03292)** showed several popular methods (e.g., Guided Backprop) are **independent of the model's learned weights and of the labels** — they pass a model-randomization test, i.e., produce the same map for a random network. Reviewers now *expect* you to cite this and not rest a causal claim on saliency alone.
- **Compute / laptop feasibility:** **Excellent** (Grad-CAM, Integrated Gradients, occlusion maps = inference-time, 6 GB fine). But treat as a supporting exhibit, always paired with an intervention (Method 1).
- **Key citations:** Adebayo et al. 2018 (**1810.03292**); Grad-CAM (Selvaraju et al. 2017); Integrated Gradients (Sundararajan et al. 2017). The sanity-check / "don't trust saliency" point is itself a required rigor item.

### Method 5 — Clever-Hans detection: Spectral Relevance Analysis (SpRAy) + LRP
- **What it proves:** *Dataset-scale, semi-automated* discovery of shortcut strategies. **Lapuschkin, Wäldchen, Binder, Montavon, Samek, Müller (2019), Unmasking Clever Hans predictors, Nature Communications (arXiv 1902.10178)** cluster LRP relevance maps across the whole dataset (SpRAy) to surface systematic "Clever-Hans" behaviors (e.g., a copyright tag deciding "horse"). Good for *finding* an unknown shortcut rather than confirming a hypothesized one.
- **What it cannot prove:** Still attribution-based (inherits saliency caveats); clustering reveals a *suspicious strategy*, not proof — confirm with Method 1.
- **Compute / laptop feasibility:** **Good.** LRP + spectral clustering over a dataset is inference + light CPU linear algebra; fits 6 GB. Heavier than single-image Grad-CAM but manageable at modest resolution/sample size.
- **Key citations:** Lapuschkin et al. 2019 (**1902.10178**); LRP (Bach et al. 2015).

### Method 6 — Concept-based testing (TCAV)
- **What it proves:** Whether a *human-defined concept* (e.g., "presence of a drain," "text marker") is directionally important to the prediction at a given layer, with statistical significance across random runs. More quantitative than saliency; concept-level not pixel-level.
- **What it cannot prove:** Full causation (it is a sensitivity/directional-derivative measure, not an intervention on the input); requires you to *name and collect example images of the concept* up front; results are layer- and concept-set-dependent.
- **Compute / laptop feasibility:** **Good.** Needs activations from a frozen model + training small linear CAV classifiers → light. 6 GB fine. Main cost is curating concept example sets.
- **Key citations:** **Kim et al. 2018, Interpretability Beyond Feature Attribution: Quantitative Testing with Concept Activation Vectors (TCAV), ICML 2018 (arXiv 1711.11279)**.

### Method 7 — Shortcut "provocation" / stress tests (inject or amplify the shortcut)
- **What it proves:** Causal sensitivity in the *forward* direction: paste the suspected shortcut (a synthetic tag, a drain-like line, a hospital text stamp) onto *healthy/negative* images and measure the induced increase in positive predictions. A large flip rate is strong causal evidence the feature drives the output.
- **What it cannot prove:** Natural reliance magnitude (injection can be out-of-distribution/exaggerated); needs a realistic injection to be convincing.
- **Compute / laptop feasibility:** **Excellent** — image compositing + inference only. Free.
- **Key citations:** Conceptually from DeGrave 2021 (generative "provocation"); Geirhos 2020 framing; closely related to the adversarial/trigger literature.

### Rigor checklist reviewers expect (cite these so the paper reads as rigorous)
- **External / multi-site validation** reported, with explicit site composition (per Zech 2018). Report subgroup metrics, not just pooled AUC (per Oakden-Rayner, Seyyed-Kalantari).
- **CLAIM — Checklist for AI in Medical Imaging** (Mongan, Moy, Kahn, Radiology: AI 2020; updated CLAIM 2024, Radiology: AI). The de-facto reporting standard; fill it out.
- **TRIPOD-AI / TRIPOD+AI** (Collins et al., BMJ 2024) for prediction-model reporting; **STARD-AI**, **DECIDE-AI** for clinical AI studies.
- State the **saliency caveat explicitly** (Adebayo 2018) and never let an attribution map be the sole causal evidence.
- Use a **negative-control intervention** (mask a matched irrelevant region) so a measured Δ is attributable to the feature, not to generic image perturbation.

### Laptop-feasible causal-proof toolkit (recommended stack, cheapest → strongest)
1. **Subgroup / shortcut-balanced splits** (Method 3) — free, establishes behavioral dependence.
2. **Confound-only / degraded-input probes** (Method 2) — near-free, proves signal availability (and is how Gichoya-style claims are made).
3. **Masking + classical inpainting counterfactuals with a negative-control region** (Method 1) — free, CPU-fine, the *causal* core.
4. **Provocation / feature-injection flips** (Method 7) — free, the forward-direction causal confirmation.
5. **TCAV** (Method 6) for a concept-level, statistically-tested cross-check — light GPU.
6. **Saliency / Grad-CAM + SpRAy** (Methods 4-5) as *supporting* exhibits only, always with the Adebayo caveat.

The combination of **(1)+(2) to show the shortcut is available and the model's behavior tracks it, then (3)=Method 1 masking/inpainting + (4)=Method 7 injection to show removing it hurts and adding it flips** is the defensible causal argument that needs no large-model training and fits a 6 GB GPU.

---

## Key sources (verified identifiers)

**JOB 1**
- Zech et al. 2018 — arXiv 1807.00431 ; https://arxiv.org/abs/1807.00431 (PLOS Medicine)
- DeGrave, Janizek, Lee 2021 — Nature Machine Intelligence 3:610-619 ; preprint https://www.medrxiv.org/content/10.1101/2020.09.13.20193565v2
- Geirhos et al. 2020 — Nat Mach Intell 2:665-673 ; arXiv 2004.07780 ; https://www.nature.com/articles/s42256-020-00257-z
- Oakden-Rayner et al. 2020 — arXiv 1909.12475 ; https://arxiv.org/abs/1909.12475 (ACM CHIL)
- Gichoya et al. 2022 — Lancet Digital Health 4(6):e406-e414 ; https://pubmed.ncbi.nlm.nih.gov/35568690/
- Seyyed-Kalantari et al. 2021 — Nature Medicine 27:2176-2182 ; https://pmc.ncbi.nlm.nih.gov/articles/PMC8674135
- Age/sex from CXR — https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8509558/
- "Exploiting and Preventing Shortcuts" (laterality/markers) — arXiv 2009.10132 ; https://arxiv.org/pdf/2009.10132
- Laterality-marker detection (YOLOv3, MIDL 2020 Hashir et al.) — https://2020.midl.io/slides/hashir20.pdf
- ⚠ MedCLIP real-world probes / layer-probe drain studies (2025-26) — ID unverified, locate before citing.

**JOB 2**
- Shortcut survey (origins→detection→mitigation) — arXiv 2412.05152 ; https://arxiv.org/abs/2412.05152
- Adebayo et al. 2018, Sanity Checks for Saliency Maps — arXiv 1810.03292 ; NeurIPS 2018 ; https://arxiv.org/abs/1810.03292
- Lapuschkin et al. 2019, Unmasking Clever Hans (SpRAy+LRP) — arXiv 1902.10178 ; Nature Communications ; https://arxiv.org/abs/1902.10178
- Kim et al. 2018, TCAV — arXiv 1711.11279 ; ICML 2018 ; https://proceedings.mlr.press/v80/kim18d.html
- COIN counterfactual inpainting (medical) — arXiv 2404.12832 ; https://arxiv.org/abs/2404.12832
- Diffusion counterfactual/anomaly in brain images — arXiv 2308.02062
- Shortcut Detection with VAEs — arXiv 2302.04246
- Slice-discovery context (Domino / "Slicing Through Bias") — arXiv 2406.12142
- CLAIM — Mongan, Moy, Kahn, Radiology: Artificial Intelligence 2020 ; updated 2024 (https://pubs.rsna.org/doi/10.1148/ryai.240300)
- TRIPOD+AI — Collins et al., BMJ 2024

_⚠ = search-surfaced identifier not independently verified; open the PDF before citing._
