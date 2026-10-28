# Shortcut-Learning / Silent-Failure Novelty Synthesis + R1–R7 Stress Test

**Date:** 2026-10-23
**Question:** Is there ONE specific, unpublished shortcut / silent-failure mode in a brain-MRI (or CXR) model that (a) nobody has published, (b) we can prove causally on BraTS 2023 + a 6 GB laptop, (c) flips a clinical decision while standard metrics stay happy?
**Sources:** three parallel researcher notes in `research_notes/Shortcut learning silent failure medical imaging/` (brain_mri_brats_shortcuts.md; cxr_general_shortcuts_and_causal_methods.md; clinical_consequence_metric_blindness.md). Integrity rule: general phenomena below are TAKEN and must be cited, never reclaimed.

---

## 1. The one candidate that survived (refined)

> **A scanner/acquisition (site) shortcut in a glioma *segmentation* model induces a systematic SIGNED tumour-volume bias that is nearly invisible to Dice/HD95, and is large enough to cross clinical volume thresholds (RANO) — turning a metric-passing model into a potentially treatment-changing one.**

The three pieces each exist; **no found paper joins them for segmentation.** It is a *demonstrated causal finding with a named mechanism and a metric-blindness result* — NOT a stapling of modules (this is what distinguishes it from the earlier rejected "combination" ideas).

## 2. What is TAKEN (cite, never claim)

- Shortcut learning exists / defined — Geirhos 2020; shortcuts in CXR — Zech 2018, DeGrave 2021.
- **Site/scanner = secret shortcut, survives ComBat** — but for **classification** (Alzheimer's/Parkinson's/tumour-type): Souza JAMIA 2023; JBHI 2024; Sci Rep 2023.
- Hidden stratification / silent subgroup failure — Oakden-Rayner CHIL 2020 (foundational — MUST differentiate).
- Demographic shortcuts — Gichoya 2022; Seyyed-Kalantari 2021.
- Dice ≠ clinical utility; overlap misses small lesions — Metrics Reloaded (Nat Methods 2024).
- "Evaluation blindness" — term already in use (arXiv 2608.02786): do NOT present as our coinage.
- Silent-failure / OOD benchmarks — Jaeger FD-Shifts ICLR 2023 (treats it as confidence/OOD, NOT attributed to a named shortcut).
- Skull-strip / defacing / slice-selection shortcuts — all for classification or non-BraTS.
- Volume error flips RANO response categories — Slachta et al., Front Neurol 2026 (shows over-segmentation pushes stable disease across the PD threshold) — **but explicitly does NOT discuss shortcut learning.** Closest prior art; must position against it.

## 3. What is OPEN (the unjoined wedge)

- Site/scanner-as-shortcut has **never been translated to glioma SEGMENTATION silent-failure** (only classification). [researcher C1]
- No paper shows a **named shortcut → segmentation signed-volume bias → Dice/HD95-blind → RANO-threshold crossing**, with the crossing quantified. [clinical-consequence note]
- Overlap metrics' blindness to *bias DIRECTION* (signed volume), tied to a named shortcut, is not shown.

## 4. The R1–R7 stress test (honest)

| Risk | Verdict | Reasoning / mitigation |
|---|---|---|
| **R1 — "shortcuts are old news"** | 🟡 **Conditional pass** | General shortcuts + site-as-shortcut-for-classification are taken. The segmentation→signed-volume→Dice-blind conjunction is unjoined. **BUT** "scanner affects measured brain volume" is partly known in *morphometry reproducibility* literature — novelty rests specifically on (DL glioma segmentation + Dice-blindness + causal shortcut attribution + clinical-threshold framing). **Must verify** against Google Scholar + MICCAI/MIDL 2024–26 + FeTS + scanner-volume-reproducibility lit before claiming. |
| **R2 — "audit, not contribution"** | 🟢 **Pass** | It's a demonstrated causal finding with a named mechanism + a metric-blindness result, not module-stapling. Frame as a *finding*. This is why it beats the earlier combination ideas. |
| **R3 — "correlation not causation"** | 🟢 **Pass** | Laptop-feasible causal toolkit: reversed-correlation site splits → confound-only probe (predict site from image) → mask/inpaint + matched control → feature injection. Both-direction causation, no big-model training. Cite Adebayo 2018 saliency caveat; use negative controls. |
| **R4 — "dataset artifact"** | 🟡 **Partial** | BraTS is genuinely multi-site so the effect is real, but a reviewer wants external validation. Mitigate with BraTS's own site diversity + honest scoping; concede generalization as limitation. |
| **R5 — "toy model, not a deployed FM"** | 🟢 **Pass / N/A** | We dropped the foundation-model angle; we use a standard 3D U-Net (SegResNet), which *is* the realistic clinical model. |
| **R6 — "three shallow studies"** | 🟢 **Pass IF not combined for breadth** | Make it ONE sharp finding (site → signed volume bias → Dice-blind). The three arenas become one argument, not three sections. |
| **R7 — "so what / clinical harm"** | 🔴 **Weakest** | **BraTS is cross-sectional; real RANO needs serial scans.** We cannot show a real patient's real decision flipped — only SIMULATE a bias and count threshold crossings over the 1251 cases. A tough reviewer calls this circular/artificial. **Mitigation: frame honestly as a single-timepoint volume-threshold proxy / simulated baseline-vs-biased-follow-up; never claim a real decision flip.** This is the chief reviewer risk and must be owned upfront. |

## 5. Two honest soft spots (do not hide these)

1. **R7 — the clinical "so what" is a simulation, not a real serial-data demonstration.** This is the single biggest weakness. The defensible framing is "metric-blind signed-volume bias of a magnitude that *would* cross clinical thresholds," demonstrated by simulation on real masks — with the serial-data limitation stated plainly.
2. **R1 — the underlying "scanner affects volume" is partly known in morphometry.** Novelty hinges on the specific DL-segmentation + Dice-blindness + causal-shortcut-attribution conjunction, which still needs one verification pass.

## 6. Recommended framing + two gating checks BEFORE building

**Headline:** *"Dice-blind, site-driven volumetric bias in glioma segmentation: a scanner shortcut that overlap metrics cannot see."* Clinical (RANO) consequence lives in the discussion as a quantified simulation, honestly scoped.

**Gate 1 (free, now):** verify C1 is genuinely unclaimed — Google Scholar + MICCAI/MIDL/BrainLes 2024–26 + FeTS federated-tumour literature + scanner/scanner-volume-reproducibility papers.
**Gate 2 (needs the trained model — in progress):** empirically confirm the effect EXISTS and is non-trivial — i.e., does our BraTS segmenter actually produce site-correlated *signed* volume bias while Dice stays flat across sites? If the effect is real and sizeable → proceed. If it's tiny → the paper has no engine, stop.

**Only if both gates pass do we commit.** Note: the segmenter currently training is exactly the instrument Gate 2 needs.

*Integrity: this survives only as the tightly-framed conjunction; all general phenomena are prior art. Honor [[ayshcxr-integrity-stance]] — if Gate 2 shows the effect is negligible, report that and stop.*
