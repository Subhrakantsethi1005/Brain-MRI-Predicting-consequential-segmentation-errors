# Detecting confidently-wrong segmentation errors (reference-free), brain-tumour MRI 2023–2026

Scope note: "confident error" = the model produces a low-uncertainty (confident) but wrong
segmentation. These are the errors that MC-dropout, deep ensembles and predictive entropy are
structurally blind to, because the uncertainty signal is derived from the same model (or a family of
similar models) that is confidently wrong. Priority is **reference-free / deployment-realistic**
methods (no ground truth at decision time). Foundational (pre-2023) work is marked [FOUNDATIONAL].

---

## Q1. What approaches detect errors where the model is confident but wrong?

### Takeaway
No single method "solves" confident-error detection, but the field has converged on moving the error
signal **off the model's own softmax/uncertainty**. The most promising reference-free families are:
(a) independent/second-model or learned error-regression predictors (QCResUNet, RCA and its conformal
extension); (b) feature-space density / OOD distance (Mahalanobis, kNN) to catch silent failures;
(c) internal-concept / mechanistic signals ("feeling of error", 2026); (d) anatomy/shape priors that
flag implausible masks; (e) consistency signals (test-time augmentation, registration). Each catches a
different slice of confident errors, and each has a documented blind spot of its own.

### Cited Findings

**Learned error-regression / quality predictors (model-agnostic, reference-free)**
- **QCResUNet** (Qiu et al., arXiv:2412.07156, Dec 2024, Washington Univ. School of Medicine) predicts
  subject-level DSC/NSD *and* voxel-level error maps from the image+mask, **agnostic to the model that
  produced the segmentation** — so its signal is independent of that model's uncertainty. Brain-tumour
  specific: trained on BraTS 2021 (n=1251) with synthetically degraded segmentations; external tests
  BraTS-SSA (n=40), WUSM (n=175), ACDC (n=100). Internal BraTS DSC prediction Pearson r=0.968, MAE=0.064;
  NSD r=0.958. — [arXiv:2412.07156](https://arxiv.org/html/2412.07156v1)
- **Reverse Classification Accuracy (RCA)** [FOUNDATIONAL] (Valindria et al., IEEE TMI 2017,
  arXiv:1702.03407): trains a classifier on a *single* test image using its predicted mask as pseudo-GT,
  then evaluates that reverse classifier on a reference DB with known GT; poor transfer ⇒ poor
  segmentation. Reference-free quality prediction per image. — [arXiv:1702.03407](https://arxiv.org/abs/1702.03407)
- **Conformal In-Context RCA** (Cosarinsky, Billot, Mansilla, … Ferrante, arXiv:2503.04522, 2025) modernises
  RCA with in-context models (UniverSeg, SAM 2) as the reverse classifier + split conformal prediction to
  give segmentation-quality estimates **with formal coverage guarantees**, reference-free. Evaluated on 10
  datasets (CXR, US, dermoscopy, histo, cardiac MRI, abdominal) — **not brain-tumour**; focuses on quality
  metrics, not specifically model-confident errors. — [arXiv:2503.04522](https://arxiv.org/html/2503.04522v3)

**Independent/second-model disagreement & silent-failure benchmarking**
- The strongest reference-free baseline in the field benchmark is the **pairwise Dice between ensemble
  (or MC-dropout) predictions** — i.e. a *disagreement* signal among discrete predictions rather than
  pixel entropy (Zenk et al., arXiv:2406.03323; see Q2 for the key caveat). — [arXiv:2406.03323](https://arxiv.org/html/2406.03323v1)

**Feature-space density / OOD distance (catches silent failures)**
- **Mahalanobis-distance OOD in feature space** (González et al., "Detecting when pre-trained nnU-Net
  models fail silently…", arXiv:2208.03217 / 2107.05975, 2021–22) explicitly targets models that
  "fail silently" on OOD data; integrates into nnU-Net without retraining. Demonstrated on Covid lung
  lesion CT. — [arXiv:2208.03217](https://arxiv.org/abs/2208.03217v1)
- **Dimensionality reduction + kNN distance** (arXiv:2408.02761, 2024) improves scalability/performance
  over Mahalanobis for OOD in medical segmentation; reports up to 92% AUROC / 94% AUPRC, CPU-fast. — [arXiv:2408.02761](https://arxiv.org/html/2408.02761v3)

**Internal-concept / mechanistic signals (2026, directly aimed at the confident-error blind spot)**
- **"Medical AI Encodes a 'Feeling of Error': Verifying Cancer Segmentation via Internal Concepts"**
  (Ma, Peng, Li, Lin, Zhao, Akin, Peng; arXiv:2609.08879, 2026). Uses sparse-autoencoder–decomposed
  internal activations as human-interpretable concepts and trains a classifier on concept activations to
  detect errors. **Explicitly framed around the blind spot where models are high-confidence but wrong**
  ("anatomically plausible yet incorrect masks"), reference-free at test time (needs only internal
  activations), and demonstrated on **brain-tumour** cancer segmentation. Reports AUROC separating correct
  vs erroneous predictions (specific value not extracted). — [arXiv:2609.08879](https://arxiv.org/pdf/2609.08879)

**Anatomy / shape priors (flag implausible masks)**
- **Post-DAE** (Larrazabal et al., arXiv:2006.13791, 2020) [FOUNDATIONAL] learns a low-dim manifold of
  anatomically plausible masks from **masks only** (modality/intensity independent) via denoising
  autoencoders; off-manifold masks are implausible. — [arXiv:2006.13791](https://arxiv.org/pdf/2006.13791)
- **Cardiac segmentation with strong anatomical guarantees** (Painchaud et al., IEEE TMI 2020,
  arXiv:1906.02343 / 2006.08825): a constrained VAE identifies anatomically implausible outputs and warps
  them to the nearest valid shape. — [arXiv:2006.08825](https://fugumt.com/fugumt/paper_check/2006.08825v1_enmode)

**Consistency signals (test-time augmentation, registration)**
- **Test-time-augmentation aleatoric uncertainty** (Wang et al., Neurocomputing 2019, arXiv:1807.07356;
  BraTS application 1810.07884) gives structure-wise uncertainty from input transforms and is reported to
  "help reduce overconfident incorrect predictions" better than dropout-based model uncertainty. — [arXiv:1807.07356](https://arxiv.org/html/1807.07356)
- **Registration inverse-consistency** as a reference-free QC feature for atlas-based brain segmentation
  (global registration quality estimated by inverse consistency). — [arXiv:1906.11014](https://arxiv.org/pdf/1906.11014)

### Inferences
- The explicit design principle shared by the most on-target methods (QCResUNet, RCA, feature-distance,
  internal-concept) is **decoupling the error estimate from the segmentation model's own confidence** —
  either a separate network, a distance in feature space, or an internal-representation probe. This is
  exactly the mechanism needed to catch confident errors, and it is the defensible core of a "real"
  contribution.
- Anatomy/shape priors and TTA/registration consistency are only partial: a confident error that is
  *anatomically plausible and transform-stable* (plausible wrong boundary, systematic over/under-call)
  will pass all of them. The "feeling of error" paper is the one that most directly attacks the
  plausible-but-wrong case.

### Gaps
- Could not extract the exact AUROC figure from the 2026 "feeling of error" paper (PDF saved locally; a
  deeper read would quantify it).

---

## Q2. Explicit evidence that aggregated uncertainty FAILS on confident / subtle non-empty errors

### Takeaway
Yes — there is direct, quantified evidence. The clearest is the field benchmark by Zenk et al., which
documents **ensemble overconfidence on wrongly-segmented regions** (members agree on the wrong answer),
plus a 2026 aggregation paper showing global-average aggregation is structurally blind to where
uncertainty sits. I could **not** verify the specific "Bricout et al. 2026, Front. Med. Technol." citation
named in the brief (see Gaps).

### Cited Findings
- **Zenk et al.**, "Comparative Benchmarking of Failure Detection Methods in Medical Image Segmentation:
  Unveiling the Role of Confidence Aggregation" (arXiv:2406.03323 v1 2024 / v2; authors Zenk, Zimmerer,
  Isensee, Traub, Norajitra, **Paul F. Jäger**, Klaus Maier-Hein — DKFZ):
  - Explicit silent-failure statement: **"the ensemble is overconfident in this case, as the ensemble
    members agree on the wrongly segmented region"** — i.e. aggregated uncertainty is blind when the
    members are jointly, confidently wrong. Observed on kidney-tumour segmentation. — [arXiv:2406.03323](https://arxiv.org/html/2406.03323v1)
  - The naive baseline (single network + mean predictive entropy) **performs poorly on most tasks**;
    aggregation choice dominates. Best method = Ensemble + **pairwise Dice** (disagreement among discrete
    predictions), MC-Dropout + pairwise Dice close second. — [arXiv:2406.03323](https://arxiv.org/html/2406.03323v1)
  - Quantified: on the kidney-tumour dataset the **AURC gap between naive baseline and best method can
    exceed 0.1** (≈0.1 mean-Dice gain when rejecting low-confidence cases). Datasets: BraTS 2019
    (brain tumour), M&Ms heart, Prostate, Covid, KiTS23 kidney tumour. Advocates **risk-coverage
    analysis**. — [arXiv:2406.03323](https://arxiv.org/html/2406.03323v1)
- **"Better than Average: Spatially-Aware Aggregation of Segmentation Uncertainty Improves Downstream
  Performance"** (arXiv:2603.29941, submitted Mar 2026): the default **Global Average aggregation ignores
  spatial/structural features** — it cannot tell scattered noise from boundary-concentrated uncertainty,
  so it dilutes the error signal. Proposes focusing on a fraction of most-uncertain pixels proportional to
  predicted-object size; a "GMM-All" meta-aggregator is most robust. Direct evidence that *how* you
  aggregate, not just the uncertainty, decides whether subtle errors survive. — [arXiv:2603.29941](https://www.alphaxiv.org/abs/2603.29941)
- **Subject-level miscalibration** (Jungo et al., MICCAI 2019, "Assessing Reliability and Challenges of
  Uncertainty Estimations for Medical Image Segmentation", BORIS/138564): uncertainty methods are
  well-calibrated at **dataset** level but **miscalibrated at subject level** with limited error
  localisation — undercutting per-case reliability (which is what matters for a single patient's volume).
  — [BORIS 138564](https://boris.unibe.ch/138564)

### Inferences
- The Zenk "members agree on the wrongly segmented region" result is the single most useful citation for a
  paper arguing that aggregated uncertainty is blind to confident errors: it is from a top group (Jäger /
  Maier-Hein, DKFZ), it is quantified, and it **includes BraTS brain tumour** among its datasets.
- The 2026 aggregation paper reframes part of the "uncertainty fails" problem as an *aggregation* failure,
  not solely a model-confidence failure — worth distinguishing in the writeup, because it implies some
  "confident errors" are actually recoverable with better aggregation and are therefore NOT in the truly
  blind set.

### Gaps
- **"Bricout et al. 2026, Front. Med. Technol."** named in the brief could not be located via web search
  (queries returned only finance/industry "medtech 2026" noise and unrelated Frontiers neuroscience
  papers). Either the citation details are off (author/venue/year), it is paywalled/not yet indexed, or it
  is mis-remembered. **Do not cite it until verified at source.** The Zenk benchmark covers the same claim
  and IS verifiable.

---

## Q3. Brain-tumour specific: epistemic blind spot vs detectable error / architectural-disagreement signal

### Takeaway
Brain-tumour-specific reference-free error detection exists (QCResUNet, "feeling of error"), and BraTS is a
standard testbed in the failure-detection benchmarks. The benchmark evidence suggests the *disagreement*
signal (pairwise Dice across predictions) is the practical workhorse — but no retrieved work cleanly
isolates an "epistemic-uncertainty blind spot" from detectable error using **architecturally different**
models for brain tumour specifically.

### Cited Findings
- QCResUNet (above) is explicitly brain-tumour (BraTS 2021/BraTS-SSA/WUSM), reference-free, model-agnostic,
  and gives per-tissue voxel error maps — the closest thing to a deployable brain-tumour confident-error
  localiser. — [arXiv:2412.07156](https://arxiv.org/html/2412.07156v1)
- "Feeling of error" (Ma et al. 2026) demonstrates on brain-tumour cancer segmentation and is framed
  around high-confidence-but-wrong detection via internal concepts. — [arXiv:2609.08879](https://arxiv.org/pdf/2609.08879)
- Zenk benchmark uses **BraTS 2019** as one of five datasets; the best reference-free failure signal there
  is **inter-prediction disagreement (pairwise Dice)**, i.e. a disagreement signal — though among members
  of the *same* ensemble/dropout family, not architecturally distinct models. — [arXiv:2406.03323](https://arxiv.org/html/2406.03323v1)

### Inferences
- The retrieved literature uses disagreement among *homogeneous* models (same architecture, ensembled or
  dropout). Using **architecturally-different** second models as an independent cross-check is the natural
  next step the benchmark implies but does not itself test — a plausible whitespace for a contribution, as
  homogeneous ensembles are exactly what Zenk shows can be jointly, confidently wrong.

### Gaps
- No retrieved paper explicitly partitions brain-tumour errors into "epistemic blind spot (undetectable by
  any uncertainty)" vs "detectable by independent signal" and quantifies the split. This appears genuinely
  open and is a candidate framing for the project.

---

## Q4. What is genuinely unsolved about confident-error detection for VOLUME specifically?

### Takeaway
Everything above operates on **overlap/boundary** metrics (Dice, NSD, voxel error maps) or on image-level
failure flags. None of the retrieved reference-free methods is built to predict **volume error (signed
bias in mm³/mL)** while the model is confident — this looks genuinely unsolved and is the strongest
candidate contribution.

### Cited Findings
- QC/error predictors target **DSC/NSD and voxel error maps**, not volumetric bias; QCResUNet predicts DSC
  r=0.968 but reports no volume-error metric. — [arXiv:2412.07156](https://arxiv.org/html/2412.07156v1)
- Failure-detection benchmarks optimise **risk-coverage on Dice**, not on volume. — [arXiv:2406.03323](https://arxiv.org/html/2406.03323v1)
- Clinical brain-tumour volumetry work treats reliability via **inter-/intra-rater ICC and
  least-significant-change thresholds** and still relies on **radiologist visual QC** because "errors in
  segmentation are still possible" — i.e. there is no automated, reference-free volume-error flag at
  decision time; Bayesian partial-volume methods reduce but do not detect per-case error (reported ~5% vs
  13% volume error). — [EASE/clinical volumetry, PMC8523989](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8523989/)

### Inferences
- A high Dice can coexist with large signed volume error, and vice versa; because every retrieved
  reference-free method is overlap- or flag-oriented, **predicting/ bounding volume error under model
  confidence is an open gap**. Note the important asymmetry: errors that are *confident, anatomically
  plausible, transform-stable, and ensemble-agreed* (e.g. a systematically mis-placed tumour boundary that
  shifts volume) defeat uncertainty, shape priors, TTA/registration consistency, and homogeneous-ensemble
  disagreement simultaneously — exactly the regime relevant to volume bias and the strongest argument for
  an independent, volume-targeted error model.
- A conformal/statistical-guarantee framing (cf. Conformal In-Context RCA) applied to **volume** rather
  than Dice would be novel on the retrieved evidence.

### Gaps
- No reference-free method found that outputs a per-case **signed volume-error estimate or interval** for
  brain tumour (or any organ) at deployment time. If this is the project's claim, the retrieved literature
  supports "not yet done."
- Could not confirm whether any 2025–26 UNSURE/MICCAI workshop paper targets volume-error specifically
  (search budget reached); worth a targeted follow-up on UNSURE 2024/2025 proceedings.

---

## Source index (primary)
- Zenk et al. 2024, Comparative Benchmarking / Confidence Aggregation — arXiv:2406.03323 (BraTS + KiTS; silent-failure, pairwise-Dice)
- Spatially-Aware Aggregation 2026 — arXiv:2603.29941
- QCResUNet, Qiu et al. 2024 — arXiv:2412.07156 (brain tumour, reference-free, model-agnostic)
- "Feeling of Error", Ma et al. 2026 — arXiv:2609.08879 (brain tumour, internal concepts, confident-error targeted)
- RCA, Valindria et al. 2017 [FOUNDATIONAL] — arXiv:1702.03407
- Conformal In-Context RCA, Cosarinsky et al. 2025 — arXiv:2503.04522
- Mahalanobis silent-failure, González et al. 2021–22 — arXiv:2208.03217 / 2107.05975
- kNN/DimRed OOD 2024 — arXiv:2408.02761
- Post-DAE, Larrazabal et al. 2020 [FOUNDATIONAL] — arXiv:2006.13791
- Painchaud et al. 2020 anatomical guarantees [FOUNDATIONAL] — arXiv:2006.08825 / 1906.02343
- Wang et al. 2019 TTA aleatoric uncertainty [FOUNDATIONAL] — arXiv:1807.07356 (BraTS: 1810.07884)
- Jungo et al. 2019 subject-level miscalibration [FOUNDATIONAL] — BORIS 138564
- Clinical glioma volumetry (EASE) — PMC8523989

Unverified / do not cite until checked at source: "Bricout et al. 2026, Front. Med. Technol."
