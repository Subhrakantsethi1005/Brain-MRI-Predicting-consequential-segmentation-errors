# Clinical Consequence & Metric Blindness — Literature Survey

**Purpose:** Scope the "SO WHAT" (shortcut → changed clinical decision / patient-relevant outcome)
and "metrics don't catch it" (aggregate metrics stay high while the model is dangerously wrong)
angles for a shortcut-learning / silent-failure paper.

**Date:** 2026-10-23
**Our data:** BraTS 2023 adult glioma (1251 cases, 4 modalities + seg labels), 6 GB laptop; plus a CXR project.
**Constraint:** AVOID needing a new dataset.

**Bottom line up front.** The *ingredients* are all taken — shortcut learning (DeGrave), metric
blindness (Oakden-Rayner hidden stratification, Metrics Reloaded), fairness silent failure
(Seyyed-Kalantari), silent-failure monitoring (Jaeger FD-Shifts), and segmentation-volume QC
(QCResUNet, downstream-aware QC) are each well-established. What appears **OPEN** is the *specific
conjunction*: a named, reproducible shortcut in a brain-MRI (glioma) model that **silently flips a
RANO 2.0 response category** (a treatment-relevant decision) while Dice / AUROC stay high, with the
decision flip *quantified* on existing data. No single paper found closes that conjunction.

---

## 1. Shortcut → CHANGED CLINICAL DECISION (not just accuracy drop)

Who has shown a shortcut flips a diagnosis / treatment decision?

| Finding | Claim | Verdict |
|---|---|---|
| **DeGrave, Janizek, Lee — "AI for radiographic COVID-19 detection selects shortcuts over signal," *Nature Machine Intelligence* 2021** (https://www.nature.com/articles/s42256-021-00338-7) | Canonical shortcut paper: COVID CXR models use text markers / patient positioning / dataset source, not pathology; fail on external hospitals. | **TAKEN** for the *existence* of shortcuts; but stops at generalization failure — does NOT quantify a flipped treatment decision (authors note models were not clinically deployed; RT-PCR is used). SO-WHAT left implicit. |
| **Winkler et al., skin-marking shortcut, *JAMA Dermatology* 2019; Narla/Esteva line; CAMEO 2026** (https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8774502/) | Dermoscopy classifiers key on rulers / surgical skin markings; markings *raise* melanoma probability score — the closest thing to a shortcut moving a decision variable. | **PARTIALLY TAKEN** for "shortcut moves the output toward a different call." It changes a probability/benign-vs-malignant score, i.e. a diagnostic decision — but this is dermatology, 2D, and about a classifier score, not a staging/response decision. The brain-tumour analogue is still open. |
| **Visual concept ranking uncovers medical shortcuts used by LMMs, arXiv 2602.05096 (2026)** (https://arxiv.org/pdf/2602.05096) | Large multimodal models rely on spurious visual concepts for medical answers. | TAKEN for LMMs; not tied to a quantified decision flip. |
| **Shortcut learning → sex bias in photoacoustic tomography, PMC12226672** (https://pmc.ncbi.nlm.nih.gov/articles/PMC12226672/) | A shortcut produces a demographic bias. | TAKEN for shortcut→bias link; outcome is bias, not a decision flip. |

**Assessment (angle 1): largely OPEN for brain tumour.** Many papers show shortcuts cause
*generalization failure* or *bias*; the dermatology work is the strongest "shortcut nudges a
decision" case. No paper found demonstrates a shortcut flipping a **RANO response category, glioma
staging, or a neuro-oncology treatment decision**. That specific SO-WHAT is open.

---

## 2. "Metrics hide failure" — aggregate metrics stay high, model dangerously wrong

| Finding | Claim | Verdict |
|---|---|---|
| **Oakden-Rayner, Dunnmon, Carneiro, Ré — "Hidden Stratification Causes Clinically Meaningful Failures in ML for Medical Imaging," CHIL 2020** (https://arxiv.org/pdf/1909.12475) | *The* reference for metric blindness: high overall performance hides >20% relative performance gaps on clinically important subsets (e.g. pneumothorax without chest drain, rare aggressive cancer subtype). Names "spurious correlates" as a cause of hidden strata. | **TAKEN** — this is the foundational "aggregate metrics mask failure" paper and even links it to spurious correlates. Any paper here must cite it and differentiate. |
| **Maier-Hein, Reinke et al. — "Metrics Reloaded," *Nature Methods* 2024** (https://www.nature.com/articles/s41592-023-02151-z); Reinke perspective, *Clin Transl Med* 2025 (https://onlinelibrary.wiley.com/doi/full/10.1002/ctm2.70237) | DSC does not reflect actual clinical need; voxel sensitivity misses small-but-clinically-relevant lesions; metric choice has task-dependent pitfalls. | **TAKEN** at the *metric-design* level — establishes that Dice ≠ clinical utility. Does not itself demonstrate a shortcut-driven silent failure; it is the methodological backbone to justify "Dice is blind here." |
| **High AUROC can mask decision failure (sepsis transcriptomic classifiers), PMC13541173 (2026)** (https://pmc.ncbi.nlm.nih.gov/articles/PMC13541173/) | AUROC near-perfect yet balanced accuracy 0.50 at a fixed threshold after cohort/platform transfer — rank discrimination conceals fixed-threshold failure. | TAKEN for "AUROC masks threshold failure." Genomics, not imaging. |
| **RISED pre-deployment eval framework, arXiv 2605.12895; KAISEN subgroup fairness auditing, arXiv 2607.28608 (2026)** | Subgroup failures (inclusivity, sensitivity) invisible to AUROC; "expose subgroup failures before aggregate performance hides them." | TAKEN — evaluation-framework angle is crowded in 2026. |
| **"Evaluation Blindness: How Silent Measurement Failures Corrupt AI Systems," arXiv 2608.02786 (2026)** | Coins/frames "evaluation blindness." | TAKEN — the *name* is now used; avoid presenting it as novel terminology. |

**Assessment (angle 2): heavily TAKEN at the general level.** "Aggregate metrics hide subgroup /
clinically-important-subset failure" is a mature, even crowded, 2020-2026 literature. A new paper
**cannot claim the phenomenon as novel**. The only defensible contribution is specificity: a
*particular* metric-blind spot (e.g., Dice/HD95 insensitive to volume error *at the RANO threshold*)
tied to a *named shortcut*, with the clinical decision flip measured.

---

## 3. Silent-failure / distribution-shift monitoring in deployed medical AI

| Finding | Claim | Verdict |
|---|---|---|
| **Jaeger et al. — "A Call to Reflect on Evaluation Practices for Failure Detection," ICLR 2023; FD-Shifts benchmark** (https://arxiv.org/pdf/2211.15259) | Defines silent failure = wrong prediction + high confidence; large-scale benchmark; Max Softmax Response baseline is hard to beat. | **TAKEN** — defines and benchmarks silent failure for classification. |
| **Band / Bungert et al. — "Understanding Silent Failures in Medical Image Classification," 2023** (https://arxiv.org/pdf/2307.14729); large-scale realistic-shift benchmark, medRxiv 2026 (https://www.medrxiv.org/content/10.64898/2026.05.04.26350496v1.full) | Confidence scoring functions evaluated specifically on silent failures in medical image classification under realistic shift. | **TAKEN** — silent failure in medical imaging classification is directly covered. |
| **Distribution-shift detection for post-market surveillance (retrospective simulation), PMC11082139** (https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11082139/) | Classifier-based shift tests best; deployable in post-market monitoring; FDA 2024 guidance mandates post-market monitoring. | TAKEN — monitoring/surveillance angle. |
| **Distance-based OOD silent-failure detection for COVID lung-lesion *segmentation*, arXiv 2208.03217** (https://arxiv.org/pdf/2208.03217) | Silent failure extended to segmentation via OOD distance. | TAKEN — silent failure in segmentation exists, but via OOD detection, not shortcut attribution. |

**Assessment (angle 3): TAKEN as a field, but the shortcut tie-in is OPEN.** Silent failure is
well-defined and benchmarked. Crucially, the monitoring literature treats silent failure as a
*confidence/OOD* problem and does **not** attribute it to a *specific identified shortcut*, nor map
it to a clinical-decision flip. "Silent failure caused by a known shortcut, with clinical
consequence quantified" is the open seam.

---

## 4. Brain tumour: which failure modes are clinically consequential, and are any shortcut-driven?

Clinically consequential glioma failure modes (established):

- **Volume error at the RANO 2.0 threshold.** RANO 2.0 (2023) uses **≥50% increase in enhancing
  volume** (or ≥40% increase in T2/FLAIR non-enhancing) for **progressive disease**, and **≥50%
  decrease in enhancing volume** for **partial response**. Systematic over/under-segmentation can
  push a *stable* patient across the PD threshold with no biological change → false progression →
  changed treatment. (Classic 2D RANO used the 25% bidimensional-product change; confirm which
  criterion the paper targets.)
- **Slachta et al., *Frontiers in Neurology* 2026** — "Validation of open-source DL segmentation
  tools for automated glioma volumetry … RANO 2.0 implementation"
  (https://www.frontiersin.org/journals/neurology/articles/10.3389/fneur.2026.1797487/full).
  Tools hit Dice 0.73–0.92 but **none prospectively validated against RANO 2.0**; Figure 1 shows
  systematic bias → false progression. Stresses **longitudinal consistency > Dice**; a moderate-Dice
  tool that tracks volume may beat a high-Dice tool with poor reproducibility. **Explicitly does NOT
  discuss shortcut learning.**
- **Metrics Reloaded:** voxel sensitivity misses **small but clinically relevant lesions** → maps
  directly to small enhancing tumour / post-op residual failure modes.
- **Known hard subpopulations:** small enhancing tumour, early post-operative MRI (cavity, blood
  products, post-surgical enhancement), specific locations, multifocality — all where segmentation
  is least reliable and most decision-relevant.

Segmentation QC that predicts downstream volume error (feasible-without-new-data toolkit):

- **QCResUNet (Med Image Anal 2025), arXiv 2412.07156** (https://arxiv.org/pdf/2412.07156) —
  joint subject- and voxel-level segmentation-quality prediction, incl. BraTS.
- **Downstream-Aware Automated QC of Images and AI-Generated Segmentations, *J Digit Imaging* 2026**
  (https://link.springer.com/article/10.1007/s10278-026-02156-y) — Accept/Reject/Rework by
  predicted downstream impact; Rework correction changed total volume by a median 9.1%.
- **Real-time prediction of segmentation quality, arXiv 1806.06244** — no-reference QC baseline.
- **MRI QC dashboard (PMC8992954):** on BraTS, error-free seg RMSE 12.2 cm³ vs failed seg 27.4 cm³
  vs reference volume — i.e., volume error scales with (predictable) segmentation quality.

Are any brain-tumour failure modes shown to be **shortcut-driven**?

- **"Image-encoded biological and non-biological variables as shortcuts in multisite neuroimaging,"
  *JAMIA* 2023 (ocad171)** (https://dx.doi.org/10.1093/jamia/ocad171) — scanner/site info is encoded
  and usable as a shortcut; not removable by simple harmonization. Scanner-as-shortcut is real.
- **"Mitigating Shortcut Learning in Brain Tumour MRI Classification," Zenodo 2025**
  (https://zenodo.org/records/21903347) and the glioma-imaging AI review (MDPI, Biomedinformatics
  2026) — controlled experiments show acquisition shortcuts **overestimate classification accuracy
  by ~20%**. **Classification only** — not segmentation, not volume, not RANO.
- **"Invisible Attributes, Visible Biases: Demographic Shortcuts in MRI-based Alzheimer's
  Classification," arXiv 2509.09558** — demographic shortcuts in brain MRI (AD, not glioma).

**Assessment (angle 4): the clinical-consequence catalogue is TAKEN; the shortcut→consequence link
for glioma is OPEN.** We know (a) volume error at the RANO threshold flips response categories
(Slachta/Frontiers, RANO 2.0) and (b) scanner/acquisition shortcuts exist in brain MRI (JAMIA,
Zenodo). **No paper joins them**: nobody shows a *specific shortcut* in a glioma segmentation model
that *silently produces a volume error that crosses the RANO threshold* and that *Dice fails to
flag*. That is the sharpest open contribution.

---

## 5. FAccT / fairness: subgroup silent failure traced to a shortcut AND clinically consequential

| Finding | Claim | Verdict |
|---|---|---|
| **Seyyed-Kalantari et al. — "Underdiagnosis bias … under-served populations," *Nature Medicine* 2021; "CheXclusion," PSB 2021** (https://psb.stanford.edu/psb-online/proceedings/psb21/seyyed-kalantari.pdf) | CXR classifiers selectively **underdiagnose** under-served/intersectional subgroups (e.g. Hispanic female); underdiagnosis = a clinically consequential silent error (missed care). | **TAKEN** for "subgroup silent failure that is clinically consequential." But the *mechanism* is characterized as bias, **not explicitly traced to an identified shortcut**. |
| **Gichoya et al. — "AI recognition of patient race in medical images," *Lancet Digital Health* 2022** | Models detect race from images via unknown features; the mechanism enabling demographic shortcuts. | TAKEN as the mechanism paper; does not itself show a decision flip. |
| **MEDFAIR (ICLR 2023, arXiv 2210.01725); subgroup separability (arXiv 2307.02791); "Fairness Beyond Demographics / appearance-based hidden cohorts" (arXiv 2605.29827, 2026)** | Benchmarks/analyses of subgroup fairness; hidden cohorts beyond demographics. | TAKEN — fairness-benchmark space is crowded. |

**Assessment (angle 5): TAKEN for "subgroup silent failure is clinically consequential"; OPEN for
the full chain "shortcut → subgroup silent failure → quantified clinical-decision flip."** The
fairness literature documents consequential underdiagnosis but usually does not (i) name the specific
shortcut feature driving it *and* (ii) quantify the resulting change in a clinical decision for the
same cases. The causal chain is implied, rarely closed end-to-end.

---

## Synthesis — what is TAKEN vs OPEN

**TAKEN (do not claim as novel):**
1. Shortcut learning exists in medical imaging, incl. brain MRI classification (DeGrave; JAMIA 2023; Zenodo 2025).
2. Aggregate metrics (AUROC/accuracy/Dice) hide clinically-important-subset failure — *hidden
   stratification* (Oakden-Rayner 2020) and Dice≠clinical-utility (Metrics Reloaded 2024). This is
   the single biggest "already told" risk; the phenomenon is foundational, not new.
3. Silent failure is defined and benchmarked, incl. medical imaging and segmentation
   (Jaeger ICLR 2023; FD-Shifts; Band 2023; OOD-seg 2208.03217).
4. Segmentation-volume error flips RANO 2.0 response categories (Slachta/Frontiers 2026; RANO 2.0).
5. Subgroup silent failure is clinically consequential (Seyyed-Kalantari *Nat Med* 2021).
6. No-reference QC can predict segmentation/volume error on BraTS (QCResUNet 2025; downstream-aware
   QC 2026; MRI QC dashboard).

**OPEN (defensible contribution surface):**
- **A.** A *specific, named* shortcut in a brain-MRI **segmentation / volumetry** model (not just a
  classifier) — glioma. The shortcut→segmentation literature is thin; almost all brain shortcut work
  is classification.
- **B.** That shortcut producing a **silent, systematic volume error that crosses a RANO 2.0
  threshold** → a flipped response category (SD↔PD or PR) → a changed treatment decision, with the
  flip **quantified** (how many of 1251 cases flip; at what shortcut strength).
- **C.** Showing that **standard segmentation metrics (Dice, HD95) stay high / barely move** while
  the clinically-decisive volume-at-threshold error is large — i.e., the metric is *blind by
  construction* to the direction that matters (systematic bias vs. overlap).
- **D.** (Optional fairness cut) the volume bias being *subgroup-concentrated* (scanner/site/field-
  strength cohort as the shortcut), tying angle 4 to angle 5 — a chain nobody closes end-to-end.

**The paper's one-sentence wedge:** *"A scanner/acquisition shortcut in a glioma segmentation model
induces a systematic volumetric bias that is nearly invisible to Dice/HD95 yet silently flips RANO
2.0 response categories — turning a metric-passing model into a treatment-changing one."* No single
found paper closes this; the pieces exist but have not been joined.

---

## Feasibility WITHOUT new data (BraTS 2023, 1251 cases, 6 GB laptop)

**Feasible (recommended):**
- **RANO-flip quantification from volumes alone.** BraTS seg labels → enhancing-tumour volume.
  Simulate a shortcut-induced systematic bias (e.g., scanner-correlated over/under-segmentation) and
  count how many cases cross the ±50% (RANO 2.0) / 25% (RANO 1.0) threshold vs. an unbiased baseline.
  Pure volumetric arithmetic on existing masks — no new data, trivially fits 6 GB. **Strongest feasible SO-WHAT.**
- **Metric-blindness demonstration.** Show Dice/HD95 vs. volume-at-threshold error under systematic
  bias: Dice can stay ~constant while signed volume error (the decision-relevant quantity) grows.
  Computable from existing masks.
- **Longitudinal caveat (honest limitation):** real RANO needs *serial* scans; BraTS is cross-
  sectional. Frame as a *single-timepoint volume-threshold* proxy / simulated two-timepoint
  (baseline mask vs. biased follow-up) — state this limitation explicitly. This is the main
  methodological risk to rebut.
- **Scanner/site shortcut:** BraTS 2023 is multi-institution; site metadata is limited but
  field-strength / intensity-profile surrogates can stand in for a scanner shortcut.

**Needs care / possibly needs more than BraTS:**
- A *real* (not simulated) deployed shortcut with real RANO ground-truth response labels → would
  need a longitudinal neuro-oncology cohort (RT-PCR-style external validation). Avoid; simulate +
  argue.
- CXR project could host the fairness/underdiagnosis-shortcut cut (angle 5) if brain route stalls,
  but that space is more crowded (Seyyed-Kalantari et al.).

---

## Key references (quick list)

- DeGrave, Janizek, Lee. AI for radiographic COVID-19 detection selects shortcuts over signal. *Nat Mach Intell* 2021. https://www.nature.com/articles/s42256-021-00338-7
- Oakden-Rayner et al. Hidden Stratification Causes Clinically Meaningful Failures… CHIL 2020. https://arxiv.org/pdf/1909.12475
- Maier-Hein, Reinke et al. Metrics Reloaded. *Nat Methods* 2024. https://www.nature.com/articles/s41592-023-02151-z
- Jaeger et al. A Call to Reflect on Evaluation Practices for Failure Detection. ICLR 2023. https://arxiv.org/pdf/2211.15259
- Band/Bungert et al. Understanding Silent Failures in Medical Image Classification. 2023. https://arxiv.org/pdf/2307.14729
- Seyyed-Kalantari et al. Underdiagnosis bias of AI… *Nat Med* 2021. (CheXclusion, PSB 2021: https://psb.stanford.edu/psb-online/proceedings/psb21/seyyed-kalantari.pdf)
- Gichoya et al. AI recognition of patient race in medical imaging. *Lancet Digit Health* 2022.
- Slachta et al. Open-source DL glioma volumetry & RANO 2.0. *Front Neurol* 2026. https://www.frontiersin.org/journals/neurology/articles/10.3389/fneur.2026.1797487/full
- Image-encoded variables as shortcuts in multisite neuroimaging. *JAMIA* 2023. https://dx.doi.org/10.1093/jamia/ocad171
- Mitigating Shortcut Learning in Brain Tumour MRI Classification. Zenodo 2025. https://zenodo.org/records/21903347
- QCResUNet. *Med Image Anal* 2025. https://arxiv.org/pdf/2412.07156
- Downstream-Aware Automated QC of segmentations. *J Digit Imaging* 2026. https://link.springer.com/article/10.1007/s10278-026-02156-y
- Distribution-shift detection for post-market surveillance. 2024. https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11082139/
- Distance-based OOD silent-failure detection for lung-lesion segmentation. arXiv 2208.03217.
- Shortcut learning in skin-cancer models (ruler/marking). PMC8774502. https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8774502/
