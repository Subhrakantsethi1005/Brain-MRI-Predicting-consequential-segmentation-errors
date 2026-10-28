# Pre-Registration — Consequence-Targeted Reference-Free Error Characterisation for Glioma Segmentation

**Frozen:** 2026-10-23 (before looking at held-out results). Honor the project integrity stance: endpoints fixed in advance; report nulls as-is; no overclaiming.

## 1. One-line contribution
Reference-free segmentation QC predicts *overlap quality* (Dice/NSD); we instead **characterise which glioma segmentation errors are clinically consequential (volume/RANO-relevant) and build a reference-free flag targeted at consequence, not overlap** — showing generic QC misses consequential volume errors that a consequence-targeted flag catches.

## 2. Positioning (related work to cite, NOT reclaim)
- QCResUNet (Med. Image Anal. 2026, arXiv:2412.07156) — reference-free quality + voxel error maps on 1251 BraTS. We differ: consequence-targeted, not overlap-quality.
- Frontiers Neurol. 2026 review (fneur.2026.1797487) — states systematic errors can flip RANO without biological change (the open problem we address).
- "No tool validated vs RANO 2.0" (as of late 2024); GlioMODA / AutoRANO emerging.
- Our own prior MSD result: engineered features only TIED baselines (null) — reported honestly.

## 3. Data & model (no new dataset)
- BraTS 2023 adult glioma, patient-disjoint splits already frozen (`outputs/splits_brats2023.json`): seg_train 565 / seg_val 62 / risk_dev 379 / risk_test 245.
- Segmenter: our trained 3D residual U-Net (checkpoint `outputs/seg_model_brats23/best.pt`, val WT 0.89 / TC 0.88 / ET 0.85). Frozen; not retrained for this study.

## 4. Definitions (frozen)
- **Signed volume error** per case & per sub-region (WT/TC/ET): `(V_pred - V_gt)` in mL, and relative `(V_pred-V_gt)/V_gt`.
- **Consequential error (primary, pre-existing frozen endpoint):** WT volume error rel ≥25% AND abs ≥1 mL.
- **Consequential error (RANO-2.0 proxy, secondary, SIMULATED — single-timepoint):** error magnitude ≥ the RANO-2.0 thresholds (ET ≥50%, FLAIR/non-enh ≥40%); reported explicitly as a cross-sectional proxy, NOT a real serial-scan decision.
- **Error TYPES (frozen taxonomy):** over-segmentation / under-segmentation (signed), boundary-leak, missed-component (false negative region), spurious-component (false positive region, e.g. vessel/choroid/blood mislabelled as ET).

## 5. Analyses (pre-registered)
- **A1 Characterisation (the finding):** distribution of signed volume error and error-types by sub-region, by tumour SIZE, by LOCATION (register to a standard atlas; error aggregated per region), by morphology (multifocality/shape). Report which configurations concentrate consequential error.
- **A2 Metric-blindness check:** show Dice/HD95 stay ~flat across cases/regions where signed volume error (and consequential-error rate) varies sharply.
- **A3 Consequence-targeted reference-free flag:** features = reference-free only (MC-dropout + flip-TTA uncertainty; threshold-sweep [0.3–0.7] volume instability; boundary/morphology; location prior from A1). Logistic regression (primary) vs gradient boosting (secondary), tuned on risk_dev with repeated CV, operating point at 90% sensitivity, evaluated ONCE on risk_test.
- **A4 Differentiation:** compare the consequence-targeted flag vs a generic overlap-quality predictor (Dice/NSD-targeted, QCResUNet-style baseline) on the SAME cases — hypothesis: consequence-flag catches consequential volume errors the overlap-QC baseline misses. Paired bootstrap.

## 6. Primary endpoint & success
Primary: AUROC of the consequence-targeted flag for the frozen WT ≥25%&≥1mL endpoint on risk_test, vs (i) volume_only, (ii) best single uncertainty, (iii) overlap-QC baseline. Report triage curve (fraction automatable at 90% sensitivity; residual consequential-error rate in the trusted pile). **A null (no significant gain) is a valid, reportable outcome.**

## 7. Honesty guards
- Cross-sectional RANO proxy stated as a limitation everywhere.
- risk_test opened exactly once.
- All related recent work cited; contribution framed as consequence-targeting + characterisation, never as "first reference-free error detector."
