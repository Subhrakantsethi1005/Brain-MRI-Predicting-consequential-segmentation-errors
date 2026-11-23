# Pre-Registration — Reference-Free Reliability of Automated Longitudinal Tumour-Volume Change in Glioma ("Error Memory")

**Frozen:** 2026-10-31, before running the flag-validation against expert RANO (Section 5/6).
Honor the project integrity stance ([[ayshcxr-integrity-stance]]): endpoints fixed in advance;
a null is a valid, reportable result; no overclaiming; all related work cited not reclaimed.

**What was already seen (exploratory, motivates but is NOT the pre-registered test):** tool-vs-tool
*disagreement* diagnostics on the whole dataset (`scripts/lumiere_disagreement.py`): static
enhancing-volume disagreement (median 3.6×), within-patient log-ratio SD (≈2.8), and
direction-of-change agreement (~50%). These motivate the hypotheses. The frozen tests below —
the reference-free reliability **flag validated against expert RANO**, on a held-out patient
split — have NOT been run at freeze time.

## 1. One-line contribution
Automated longitudinal glioma volumetry is widely trusted, but we show its per-scan errors
**decorrelate across a patient's own timeline** (they compound, not cancel, in the volume
*change*), that single-scan QC cannot see this, and that a **reference-free agreement signal**
between two architecturally-independent segmenters flags the unreliable progression decisions —
validated against expert RANO ratings.

## 2. Positioning (cite, NOT reclaim)
- QCResUNet (Med. Image Anal. 2026, arXiv:2412.07156), QU-BraTS, RCA — reference-free QC, but
  **per-scan overlap/quality**, not longitudinal change reliability.
- Guennoun et al. "Segmenting with Confidence" (npj Digit. Med. 2026, s41746-026-02902-0) —
  evidential-ensemble **per-scan credible intervals**, on **meningioma**; does not model the
  cross-scan error correlation that governs the change. We differ: glioma, change-level,
  error-correlation-driven.
- Suter et al. 2023 (PMC10513769) — articulates that random vs systematic serial error matters
  for trend monitoring, **qualitatively**; reports ~81% trend agreement. We MODEL and PREDICT it
  reference-free and tie it to the decision.
- Zenk et al. (arXiv:2406.03323) — architecturally-independent disagreement is the strong
  reference-free signal (per-scan). We extend the principle to the longitudinal decision.
- RANO 2.0 volumetric thresholds (Ellingson 2024, AJNR); Frontiers Neurol. 2026 review
  (fneur.2026.1797487) — systematic errors can flip RANO.

## 3. Data & split (frozen)
- **LUMIERE** (Figshare 5904905, CC-BY): 91 GBM patients, 616 expert-RANO-rated timepoints.
  Two shipped automated segmentations: **DeepBraTumIA (DBT)** and **HD-GLIO-AUTO (HG)**.
  Common comparable sub-region = **Contrast-enhancing (CE)** (the RANO target); volume =
  `original_shape_VoxelVolume` (mm³) from the provided pyradiomics tables.
- **No manual ground-truth masks exist** in LUMIERE. Therefore "which tool is correct" is NOT
  claimed; the clinical ground truth for the *decision* is the **expert RANO rating**.
- **Patient-level split (frozen, seed=0):** randomly assign the 91 patients 50/50 to
  `calib` and `test` (patient-disjoint). The flag operating point / any threshold choices are
  fixed on `calib`; all headline numbers are reported **once** on `test`.

## 4. Definitions (frozen)
- **Eligible timepoint:** a post-operative follow-up whose expert rating ∈ {PD, SD, PR, CR}
  (exclude Pre-Op / Post-Op / None), with a CE volume available from both tools.
- **Running nadir (per tool, per patient):** the minimum CE volume over all prior eligible
  follow-ups (RANO measures progression from the post-treatment low point, not the previous scan).
- **Automated progression call (per tool):** `auto_PD_tool(t) = 1` iff
  `V_tool(t) ≥ 1.40 × nadir_tool(t)` **and** `V_tool(t) − nadir_tool(t) ≥ 1000 mm³` (1 mL),
  i.e. a RANO-2.0-style ≥40% enhancing-volume increase from nadir with a minimum absolute change.
  (New enhancing lesion where nadir ≈ 0 and `V(t) ≥ 1000 mm³` also counts as progression.)
- **Expert label:** `expert_PD(t) = 1` iff rating == PD.
- **Reference-free reliability flag (the contribution):** `agree(t) = 1` iff
  `auto_PD_DBT(t) == auto_PD_HG(t)` — the two independent tools make the same progression call.
  `agree=1` ⇒ "trust/auto-certify"; `agree=0` ⇒ "defer to expert".
- **Appearance-shift (mechanism feature):** z-scored Euclidean distance between the CE-region
  first-order + texture radiomic vectors (volume/shape features excluded) at t−1 and t, per tool,
  averaged. Computed only for the mechanism analysis (H4).

## 5. Hypotheses (frozen)
- **H1 (decorrelation):** within-patient SD of log₂(V_DBT/V_HG) ≫ 0 on `test` (errors are not a
  fixed offset). Descriptive; CI reported.
- **H2 (change unreliability):** the two tools agree on the **direction** of consecutive CE-volume
  change at ≤70% on `test` (chance=50%), including on the ≥1 mL / ≥40%-change subset.
- **H3 (PRIMARY — the flag works):** among eligible `test` timepoints, the automated progression
  call matches expert RANO **more accurately when `agree=1` than when `agree=0`**.
- **H4 (mechanism):** inter-scan appearance-shift is higher for pairs where the tools' progression
  calls disagree / direction flips — i.e. appearance change drives decorrelation.

## 6. Primary endpoint & success
**Primary:** balanced accuracy (mean of sensitivity & specificity, to neutralise the high PD base
rate) of `auto_PD_DBT` vs `expert_PD`, computed on the `agree` subset vs the `disagree` subset of
`test`. **Success = the agree-subset balanced accuracy exceeds the disagree-subset by a margin
whose 95% bootstrap CI (patient-clustered, 2000 resamples, seed=0) excludes 0.**
Also reported: selective-prediction curve (coverage = fraction `agree`; selective balanced accuracy;
residual error on the certified pile) vs the no-gating single-tool baseline. **A null (no gap)
is a valid, reported outcome** and would itself be informative (agreement carries no reliability
information).

## 7. Honesty guards
- `test` opened exactly once for the headline; thresholds frozen here / fixed on `calib`.
- No GT masks ⇒ we claim *unreliability/disagreement*, never *which tool is right*.
- Near-zero-volume log-ratio swings are partly real biology (true CE resolution/recurrence under
  treatment); the robust claims are reported on ≥1 mL subsets and this caveat stated everywhere.
- Small cohort (91 patients) ⇒ wide CIs; stated. 2D-vs-volumetric and single-dataset limits stated.
- Contribution framed as a characterisation + reference-free flag, never "first reliability method".
