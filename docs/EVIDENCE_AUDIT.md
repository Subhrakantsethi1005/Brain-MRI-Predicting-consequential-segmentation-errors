# Evidence audit, November 24, 2026

## What supports each claim

| Claim | Evidence | Interpretation |
|---|---|---|
| 1,251 BraTS cases, splits 565/62/379/245 | `results/brats2023/splits.json` | Patient-disjoint segmenter training/validation and risk development/test |
| 59 recorded epochs | `results/brats2023/training_history.json` | Epochs 0–58. Configured maximum 150 is not the completed count |
| Best logged mean validation Dice 0.8772 | same history, epoch 49 | WT 0.9038, TC 0.8814, ET 0.8465 at that checkpoint. Not test Dice |
| WT consequential rate 23/245 | case CSV and `optionB/characterize_summary.json` | Research endpoint: relative volume error >=25% AND absolute error >=1 mL |
| AUROC 0.743 vs 0.786 vs 0.838 | `optionB/flag_WT.json` | Consequence flag, overlap-QC logistic baseline, best single uncertainty. This is not a reproduced QCResUNet comparison |
| Paired AUROC difference -0.043, CI [-0.121,0.019], p=0.248 | same JSON | No detected superiority. A nonsignificant difference does not prove equivalence |
| ~56% retained, 2/137 residual errors | same JSON and source evaluator | Retrospective operating point selected using test labels to achieve 90% sensitivity. Not a validated deployment threshold |
| 221 LUMIERE decisions, 70 patients | `results/lumiere/strengthen.json` and source tables | Eligible subset, not all 616 rated timepoints |
| BA 0.693 agreement vs 0.499 disagreement | same JSON | Gap 0.194, patient-bootstrap CI [0.045,0.367]. Agreement subset still has substantial error |
| Positive BA gap in 199/200 splits | `B_split_robustness.frac_positive=0.995` | Older report and demo incorrectly rounded this to 100% |
| Direction agreement 57/114 | `F_decorrelation` and source tables | Tool-to-tool direction agreement, not 50% clinical accuracy and not direct measurement of true mask error correlation |
| Third voter gap 0.200 | `results/lumiere/threeway.json` | Exploratory, same cohort; modest coverage/error tradeoff, no demonstrated headline improvement |

## Important qualifications

1. **Clinical thresholds:** 25% is a project-defined relative volume-error threshold. RANO 2.0 uses a 40% increase for 3D progression (25% for 2D burden). Our longitudinal 40% plus 1 mL rule is a volume-only research proxy, not full RANO. Source: https://doi.org/10.3174/ajnr.A8396.
2. **Protocol deviations:** longitudinal preregistration describes splitting 91 patients and a nadir over prior eligible follow-ups. `lumiere_validate.py` actually splits the 70 eligible patients and includes Post-Op in the nadir. `lumiere_strengthen.py` additionally floors the nadir at 50 mm3. Keep these distinctions visible. The earlier 93-timepoint / 35-patient test result (BA ~0.67 vs ~0.29) belongs to `lumiere_validate.py`, while full-cohort JSON uses `lumiere_strengthen.py`; they are not identical implementations.
3. **Ground truth:** LUMIERE expert RANO labels support decision comparisons, but no manual masks establish which tool's volume is correct. Inter-tool variability alone cannot identify the true segmentation error mechanism. Similar preprocessing also limits independence.
4. **Selection:** repeated random splits measure sensitivity to splitting within the same cohort, not external replication. Full-cohort analysis follows exploration on that cohort. A parameter-free rule can still inherit selection bias.
5. **Conformal extension:** the implementation splits patients but calibrates over individual correlated visits. This alone does not establish exchangeability of the calibration losses or a patient-level CRC theorem. It initializes a threshold even if no grid point passes. Frozen test FNR is 10.67%, 22.67%, 24.00% at targets 5%, 10%, 20%. Across splits the mean is 6.38%, 9.57%, 19.89%; averages do not certify the assumption or a case-level safety guarantee. Treat this as exploratory. A marginal theorem also does not require every realized split to meet alpha. Source: https://arxiv.org/abs/2208.02814.
6. **Novelty:** architecture, dropout, TTA, logistic regression, disagreement and CRC are existing methods. The defensible contribution is the implemented evaluation of consequence-targeted QC and longitudinal decision agreement on these cohorts. No systematic priority search establishes a first-ever claim. Related work includes QCResUNet (https://arxiv.org/abs/2412.07156) and failure detection benchmarking (https://arxiv.org/abs/2406.03323).

## Evidence preservation

Existing historical manuscripts and frozen protocols remain available. This audit supersedes unsupported claims in them. No training was repeated for this documentation refresh. The presentation and demonstration use recorded or recomputed retrospective data and identify illustrative examples explicitly.
