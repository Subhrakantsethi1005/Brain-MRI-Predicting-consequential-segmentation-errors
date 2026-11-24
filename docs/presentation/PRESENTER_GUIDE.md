# Presenter guide

24 main slides and 3 backup slides. Allow about 15–20 minutes for the main talk.

## 1. Can we trust the tumour measurement?

Opening: Our project asks when an automated brain-tumour measurement deserves human review. We built a segmentation and quality-control pipeline, then investigated whether independent tools agreeing on a longitudinal progression call identifies a more reliable subset. We will present the negative results as well as the positive signal. The MRI is a recorded BraTS case, not generated artwork. The existing segmentation architecture is a reused baseline.

Sources:
https://github.com/Subhrakantsethi1005/Brain-MRI-Predicting-consequential-segmentation-errors/blob/codex/presentation-and-repository-refresh/docs/paper/figures/showcase/showcase_BraTS-GLI-01364-000.png

## 2. The measurement and the decision

Explain segmentation as colouring the voxels belonging to a tumour. Counting these voxels gives volume. On a single scan we can ask whether the measurement is wrong. With repeated scans we ask whether a volume-change decision is reliable. Those are related but distinct evaluation tasks. This research does not diagnose cancer or replace RANO assessment.

Sources:
https://github.com/Subhrakantsethi1005/Brain-MRI-Predicting-consequential-segmentation-errors/blob/codex/presentation-and-repository-refresh/README.md
https://doi.org/10.3174/ajnr.A8396

## 3. What the segmenter produces

Four input MRI channels are T1, contrast-enhanced T1, T2 and FLAIR. The network outputs nested binary masks: tumour core, whole tumour and enhancing tumour. This recorded case shows the input FLAIR, expert outline and our model outline. The historic green trust label is computed from reference-mask volume error. It is not the output of a reference-free QC model. Volume is number of positive voxels multiplied by voxel volume.

Sources:
https://github.com/Subhrakantsethi1005/Brain-MRI-Predicting-consequential-segmentation-errors/blob/codex/presentation-and-repository-refresh/src/brainrisk/data.py
https://github.com/Subhrakantsethi1005/Brain-MRI-Predicting-consequential-segmentation-errors/blob/codex/presentation-and-repository-refresh/src/brainrisk/model.py
https://github.com/Subhrakantsethi1005/Brain-MRI-Predicting-consequential-segmentation-errors/blob/codex/presentation-and-repository-refresh/docs/paper/figures/showcase/showcase_BraTS-GLI-01021-000.png

## 4. Two studies, one reliability question

The work evolved from an early MSD feasibility experiment into BraTS 2023 evaluation and a LUMIERE longitudinal investigation. The current README focuses on the later studies. BraTS has manual segmentation labels but is cross-sectional. LUMIERE has repeated visits and expert RANO ratings but no manual segmentation masks. Therefore the ground truth and research question change between the studies.

Sources:
https://github.com/Subhrakantsethi1005/Brain-MRI-Predicting-consequential-segmentation-errors/blob/codex/presentation-and-repository-refresh/results/brats2023/splits.json
https://github.com/Subhrakantsethi1005/Brain-MRI-Predicting-consequential-segmentation-errors/blob/codex/presentation-and-repository-refresh/results/lumiere/strengthen.json
https://doi.org/10.1038/s41597-022-01881-7

## 5. Patient-disjoint development splits

The split JSON contains 565 segmentation training, 62 validation, 379 risk development and 245 risk test case IDs. Keeping segmenter training separate from risk-model development helps avoid evaluating reliability on cases the segmenter trained on. The existing tests check that serial IDs from a patient stay in one partition. The case-feature snapshot includes the risk cohorts and a subset of segmentation validation cases, so not every labelled case has a stochastic feature row.

Sources:
https://github.com/Subhrakantsethi1005/Brain-MRI-Predicting-consequential-segmentation-errors/blob/codex/presentation-and-repository-refresh/results/brats2023/splits.json
https://github.com/Subhrakantsethi1005/Brain-MRI-Predicting-consequential-segmentation-errors/blob/codex/presentation-and-repository-refresh/tests/test_pipeline.py
https://github.com/Subhrakantsethi1005/Brain-MRI-Predicting-consequential-segmentation-errors/blob/codex/presentation-and-repository-refresh/results/brats2023/case_features.csv

## 6. What we trained

The code instantiates MONAI networks.nets.UNet with residual units, not SegResNet despite some earlier manuscript wording. It has four input and three output channels, channel widths 16 to 256, four stride-2 stages, two residual units and dropout 0.1. AdamW optimizes squared-prediction Dice loss with sigmoid activation. The cosine schedule uses the configured maximum of 150 epochs. The committed history ends after epoch index 58, so 59 recorded epochs, not 150 completed epochs. We did not rerun training for this presentation.

Sources:
https://github.com/Subhrakantsethi1005/Brain-MRI-Predicting-consequential-segmentation-errors/blob/codex/presentation-and-repository-refresh/src/brainrisk/model.py
https://github.com/Subhrakantsethi1005/Brain-MRI-Predicting-consequential-segmentation-errors/blob/codex/presentation-and-repository-refresh/scripts/pipeline/01_train_segmentation.py
https://github.com/Subhrakantsethi1005/Brain-MRI-Predicting-consequential-segmentation-errors/blob/codex/presentation-and-repository-refresh/configs/brats2023.yaml
https://github.com/Subhrakantsethi1005/Brain-MRI-Predicting-consequential-segmentation-errors/blob/codex/presentation-and-repository-refresh/results/brats2023/training_history.json

## 7. Training improved validation Dice

The line chart uses actual validation checkpoints from the committed training history. Best logged mean Dice is 0.8772197 at epoch index 49, shown as training epoch 50. At that checkpoint TC=0.88137, WT=0.90383, ET=0.84646. The last training loss is about 0.105; the lowest logged loss is not the checkpoint selection criterion. These are validation metrics, not held-out risk-set segmentation Dice and not evidence of a new state-of-the-art architecture.

Sources:
https://github.com/Subhrakantsethi1005/Brain-MRI-Predicting-consequential-segmentation-errors/blob/codex/presentation-and-repository-refresh/results/brats2023/training_history.json

## 8. Reference-free quality signals

Reference-free means that at deployment the QC features come from the image and model predictions, without a manual mask. Ground-truth labels are still required to train and evaluate the risk model. Ten stochastic passes keep dropout active and cycle through eight flip combinations. We aggregate probability entropy, variance, mask/volume disagreement and morphology. A logistic regression maps these features to a case-level score. The architecture, dropout and TTA techniques already exist.

Sources:
https://github.com/Subhrakantsethi1005/Brain-MRI-Predicting-consequential-segmentation-errors/blob/codex/presentation-and-repository-refresh/src/brainrisk/model.py
https://github.com/Subhrakantsethi1005/Brain-MRI-Predicting-consequential-segmentation-errors/blob/codex/presentation-and-repository-refresh/src/brainrisk/features.py
https://github.com/Subhrakantsethi1005/Brain-MRI-Predicting-consequential-segmentation-errors/blob/codex/presentation-and-repository-refresh/src/brainrisk/risk.py

## 9. The consequential-error endpoint

For each region, compare predicted volume with reference volume. A case is positive when the relative absolute volume error is at least 25% and the absolute volume difference is at least 1 mL. The absolute floor avoids flagging tiny numerical changes as consequential. This is a study-defined segmentation-error endpoint, not the RANO clinical progression rule. RANO 2.0 distinguishes 25% for 2D burden and 40% for 3D volume increase. The 20 mL versus 26 mL example below is illustrative arithmetic.

Sources:
https://github.com/Subhrakantsethi1005/Brain-MRI-Predicting-consequential-segmentation-errors/blob/codex/presentation-and-repository-refresh/src/brainrisk/metrics.py
https://github.com/Subhrakantsethi1005/Brain-MRI-Predicting-consequential-segmentation-errors/blob/codex/presentation-and-repository-refresh/docs/paper/optionB_preregistration.md
https://doi.org/10.3174/ajnr.A8396

## 10. The comparison tests our hypothesis

We tested whether learning a consequential-volume-error target helps more than generic overlap quality control. The same logistic model family on reference-free features learns either the consequence label or the low-Dice quality label. The overlap-QC baseline is a lightweight logistic baseline, not a reproduced QCResUNet network. Volume alone and the single uncertainty feature provide simpler comparisons. Selection of the single feature uses development labels. The held-out AUROCs quantify ranking discrimination.

Sources:
https://github.com/Subhrakantsethi1005/Brain-MRI-Predicting-consequential-segmentation-errors/blob/codex/presentation-and-repository-refresh/scripts/brats/optionB_flag.py
https://github.com/Subhrakantsethi1005/Brain-MRI-Predicting-consequential-segmentation-errors/blob/codex/presentation-and-repository-refresh/src/brainrisk/risk.py

## 11. The consequence model did not win

These are saved held-out WT results on 245 risk-test cases. AUROC: consequence 0.74285, overlap-QC 0.78555, predicted volume 0.76596, best single uncertainty 0.83784. Consequence minus overlap difference is -0.04269, 95% paired-bootstrap CI [-0.12069,0.01897], p=0.248. The confidence interval includes zero, so the study does not detect superiority. It also does not establish formal equivalence. This negative result is central to an honest defence of the project.

Sources:
https://github.com/Subhrakantsethi1005/Brain-MRI-Predicting-consequential-segmentation-errors/blob/codex/presentation-and-repository-refresh/results/brats2023/optionB/flag_WT.json

## 12. Triage performance needs a qualification

The best single uncertainty feature retains 137 out of 245 test cases at the reported 90%-sensitivity point. Two retained cases carry consequential error, giving 1.46% residual error. The evaluator calls threshold_for_sensitivity on the test labels themselves. Therefore this is a retrospective point on the test ROC/risk-coverage curve, not a fixed calibrated operating threshold tested prospectively. Say may support triage after calibration, rather than safely automates 56 percent. Consequential WT errors total 23, so missing 2 gives sensitivity 21/23, or 91.3 percent.

Sources:
https://github.com/Subhrakantsethi1005/Brain-MRI-Predicting-consequential-segmentation-errors/blob/codex/presentation-and-repository-refresh/scripts/brats/optionB_flag.py
https://github.com/Subhrakantsethi1005/Brain-MRI-Predicting-consequential-segmentation-errors/blob/codex/presentation-and-repository-refresh/results/brats2023/optionB/flag_WT.json

## 13. Longitudinal measurements add another problem

A repeated-scan progression call depends on change relative to an earlier measurement. A consistent measurement bias might partly cancel, while variable tool disagreement can reverse the apparent direction. We observe inter-tool variability, not each tool’s true segmentation error, because LUMIERE has no manual masks. Among 114 consecutive intervals with at least 1 mL in both tools at both ends, only 57 direction labels agree. Do not call this 50 percent clinical accuracy or proof that the tools are independent coin flips. Marginal direction frequencies can affect chance agreement.

Sources:
https://github.com/Subhrakantsethi1005/Brain-MRI-Predicting-consequential-segmentation-errors/blob/codex/presentation-and-repository-refresh/results/lumiere/strengthen.json
https://github.com/Subhrakantsethi1005/Brain-MRI-Predicting-consequential-segmentation-errors/blob/codex/presentation-and-repository-refresh/scripts/longitudinal/lumiere_strengthen.py

## 14. The longitudinal agreement rule

Use each tool’s enhancing-tumour volume at the current visit and its own running minimum over prior post-operative visits. In the strengthen implementation this nadir is floored at 0.05 mL. A positive automated progression proxy needs both at least 40 percent growth and at least 1 mL absolute growth. Compare the two binary tool calls. If they disagree, refer for review. If they agree, label the agreement subset, not safe. The full RANO assessment also uses other imaging and clinical context. The earlier validation implementation omits the nadir floor.

Sources:
https://github.com/Subhrakantsethi1005/Brain-MRI-Predicting-consequential-segmentation-errors/blob/codex/presentation-and-repository-refresh/scripts/longitudinal/lumiere_strengthen.py
https://github.com/Subhrakantsethi1005/Brain-MRI-Predicting-consequential-segmentation-errors/blob/codex/presentation-and-repository-refresh/scripts/longitudinal/lumiere_validate.py
https://doi.org/10.3174/ajnr.A8396

## 15. Agreement identifies a more accurate subset

On the 221-decision full cohort of 70 patients, DBT calls versus expert RANO have balanced accuracy 0.608 overall, 0.693 when the tools agree, and 0.499 when they disagree. Balanced accuracy averages sensitivity and specificity to reduce the effect of the high PD prevalence. The difference is 0.1938 with patient-clustered bootstrap CI [0.0452,0.3665]. The agreement subset retains 124/221 decisions and has raw error 34.7 percent. A higher average reliability subset is not a clinical safety certificate or evidence that the flag causes improvement.

Sources:
https://github.com/Subhrakantsethi1005/Brain-MRI-Predicting-consequential-segmentation-errors/blob/codex/presentation-and-repository-refresh/results/lumiere/strengthen.json
https://github.com/Subhrakantsethi1005/Brain-MRI-Predicting-consequential-segmentation-errors/blob/codex/presentation-and-repository-refresh/results/lumiere/threeway.json

## 16. Held-out validation supports the same direction

We independently reran the original lumiere_validate.py against the local source CSVs. It emits 221 eligible rows, then splits the 70 eligible patients 50/50 with random seed zero. The test half has 93 visits from 35 patients. All=0.526, agree=0.666, disagree=0.292. The gap is 0.374 and 95% clustered bootstrap CI [0.083,0.624], based on 1987 valid resamples of 2000. Raw error of the agreement pile is 38.2 percent. The preregistration described a split of 91 patients; the implementation splits eligible patients instead. It also includes postoperative baseline visits in the nadir. These deviations must be stated. This is the validation implementation, distinct from the floored-nadir full-cohort analysis.

Sources:
https://github.com/Subhrakantsethi1005/Brain-MRI-Predicting-consequential-segmentation-errors/blob/codex/presentation-and-repository-refresh/scripts/longitudinal/lumiere_validate.py
https://github.com/Subhrakantsethi1005/Brain-MRI-Predicting-consequential-segmentation-errors/blob/codex/presentation-and-repository-refresh/docs/paper/longitudinal_preregistration.md
https://github.com/Subhrakantsethi1005/Brain-MRI-Predicting-consequential-segmentation-errors/blob/codex/presentation-and-repository-refresh/docs/EVIDENCE_AUDIT.md

## 17. The effect usually survives another split

The saved robustness JSON has frac_positive=0.995 across 200 random patient splits, which is 199/200. Previous report prose and demo hard-coded 100 percent. The median BA gap is 0.1909 and the 5th-to-95th percentile span is approximately 0.066 to 0.354. Similar gaps appear at the 25, 40 and 50 percent volume thresholds and when following the other tool. Repeated splits reuse the same cohort and are robustness checks, not 200 independent external validations. We report the corrected value.

Sources:
https://github.com/Subhrakantsethi1005/Brain-MRI-Predicting-consequential-segmentation-errors/blob/codex/presentation-and-repository-refresh/results/lumiere/strengthen.json

## 18. Demonstration: one real patient trajectory

This is Patient-002 from the actual derived public LUMIERE demo snapshot. Week 3 is postoperative baseline with DBT 24.93 mL and HG 0.13. At week 37 DBT=0.07 and HG=4.88. DBT calls non-PD because it is below its prior nadir, while HG calls PD. The agreement rule refers this visit. At week 47 both call PD relative to their own nadirs. The default demo was deliberately selected to contain a disagreement and is not a performance estimate. The slide displays values rounded to 0.01 mL; the replay uses source precision. Run python demo/run_demo.py to replay.

Sources:
https://github.com/Subhrakantsethi1005/Brain-MRI-Predicting-consequential-segmentation-errors/blob/codex/presentation-and-repository-refresh/demo/data/lumiere.json
https://github.com/Subhrakantsethi1005/Brain-MRI-Predicting-consequential-segmentation-errors/blob/codex/presentation-and-repository-refresh/demo/run_demo.py
https://doi.org/10.1038/s41597-022-01881-7

## 19. Demonstration: why week 37 gets referred

Walk through the arithmetic slowly. DBT volume falls from 24.93 to 0.07 mL, so its progression proxy is negative. HG grows from 0.13 to 4.88 mL: 4.88 exceeds 1.4 times 0.13 and the 4.75 mL increase exceeds the 1 mL floor, so its proxy is positive. The tools disagree. The expert label happens to be PD for this visit. That expert label is shown only for retrospective comparison and does not enter the flag. The goal is not to resolve which tool’s outline is correct but to identify a decision needing review.

Sources:
https://github.com/Subhrakantsethi1005/Brain-MRI-Predicting-consequential-segmentation-errors/blob/codex/presentation-and-repository-refresh/demo/run_demo.py
https://github.com/Subhrakantsethi1005/Brain-MRI-Predicting-consequential-segmentation-errors/blob/codex/presentation-and-repository-refresh/demo/data/lumiere.json

## 20. A third voter changes the trade-off slightly

The separately trained BraTS U-Net provides a third opinion on LUMIERE. Two-way agreement covers 56.1 percent with raw error 34.7 percent. Requiring three-way unanimity covers 49.3 percent with raw error 33.0 percent. The BA gaps are 0.194 and 0.200 respectively, so the headline effect hardly changes. Within the 124 two-way agreement calls, the third voter dissents on 15; their raw accuracy is 53.3 percent versus 67.0 percent for unanimous cases. Small subsets and shared preprocessing constrain the interpretation. Architecture/preprocessing differences alone do not prove statistical independence.

Sources:
https://github.com/Subhrakantsethi1005/Brain-MRI-Predicting-consequential-segmentation-errors/blob/codex/presentation-and-repository-refresh/results/lumiere/threeway.json
https://github.com/Subhrakantsethi1005/Brain-MRI-Predicting-consequential-segmentation-errors/blob/codex/presentation-and-repository-refresh/scripts/longitudinal/lumiere_thirdvoter.py

## 21. The conformal extension remains exploratory

Conformal risk control is an existing framework with a marginal guarantee under appropriate exchangeability and calibration assumptions. Our implementation splits patients but treats correlated visits as calibration observations; that alone does not prove a patient-level theorem. It also defaults to the smallest grid threshold even if no candidate satisfies the corrected constraint. The frozen test FNR exceeds all targets: 10.67 vs 5 percent, 22.67 vs 10 percent, 24 vs 20 percent. A marginal theorem need not hold on every split, so these violations alone do not disprove CRC. But the dependence and implementation issues prevent a certified safety claim. Across repeated splits the means are 6.38, 9.57 and 19.89 percent. The slide explicitly avoids claiming a guarantee.

Sources:
https://github.com/Subhrakantsethi1005/Brain-MRI-Predicting-consequential-segmentation-errors/blob/codex/presentation-and-repository-refresh/results/lumiere/conformal.json
https://github.com/Subhrakantsethi1005/Brain-MRI-Predicting-consequential-segmentation-errors/blob/codex/presentation-and-repository-refresh/scripts/longitudinal/lumiere_conformal.py
https://arxiv.org/abs/2208.02814

## 22. Our contribution and its novelty

Our strongest contribution is a careful implemented study, not invention of the baseline architecture. We built the pipeline, defined and tested a consequence-labelled evaluation, reported its null superiority result, and investigated longitudinal decision agreement against expert RANO. Existing literature already covers segmentation QC, MC dropout, model disagreement and risk control. The specific longitudinal application is a plausible incremental contribution; first-ever priority has not been established. A student-level implementation contribution can be meaningful even when methodological novelty is modest. Formal novelty strength requires a systematic literature search and more external evidence.

Sources:
https://github.com/Subhrakantsethi1005/Brain-MRI-Predicting-consequential-segmentation-errors/blob/codex/presentation-and-repository-refresh/docs/EVIDENCE_AUDIT.md
https://arxiv.org/abs/2412.07156
https://arxiv.org/abs/2406.03323
https://arxiv.org/abs/2208.02814

## 23. What the evidence still needs

The next validation should separate model and threshold selection from locked evaluation, preserve all patient-level dependencies, and use an external cohort. Reproduce the longitudinal study with an explicitly documented patient universe, baseline/nadir definition and mask provenance. Compare the agreement rule with strong uncertainty, overlap-QC and longitudinal alternatives under matched coverage. If a conformal extension is pursued, use exchangeable patient-level losses or a justified clustered theorem with a valid fallback threshold. A prospective reader study would be needed before clinical use.

Sources:
https://github.com/Subhrakantsethi1005/Brain-MRI-Predicting-consequential-segmentation-errors/blob/codex/presentation-and-repository-refresh/docs/EVIDENCE_AUDIT.md

## 24. What we can defend

Closing: We trained a standard segmenter and built a reference-free QC evaluation. The consequence-targeted model did not improve over simpler uncertainty checks on the BraTS test set. A longitudinal agreement signal identifies a more accurate subset of LUMIERE volume-based decisions, but substantial errors remain. The defensible contribution is an honest investigation of where reliability signals help, with clear negative results and limits. Invite the audience to inspect the recorded-data demo and artifacts.

Sources:
https://github.com/Subhrakantsethi1005/Brain-MRI-Predicting-consequential-segmentation-errors/blob/codex/presentation-and-repository-refresh/README.md
https://github.com/Subhrakantsethi1005/Brain-MRI-Predicting-consequential-segmentation-errors/blob/codex/presentation-and-repository-refresh/docs/EVIDENCE_AUDIT.md

## 25. Backup: metrics in plain language

Dice measures overlap between predicted and reference masks. AUROC measures ranking discrimination across positive and negative cases, not accuracy at a specific threshold. Balanced accuracy averages sensitivity and specificity, useful when expert PD is common. Coverage is the proportion retained by a selective rule. Residual error is the observed error rate in the retained group. Distinguish residual error P(error|retained) from missed-progression rate P(cleared|expert PD).

Sources:
https://github.com/Subhrakantsethi1005/Brain-MRI-Predicting-consequential-segmentation-errors/blob/codex/presentation-and-repository-refresh/src/brainrisk/metrics.py
https://github.com/Subhrakantsethi1005/Brain-MRI-Predicting-consequential-segmentation-errors/blob/codex/presentation-and-repository-refresh/src/brainrisk/risk.py
https://github.com/Subhrakantsethi1005/Brain-MRI-Predicting-consequential-segmentation-errors/blob/codex/presentation-and-repository-refresh/scripts/longitudinal/lumiere_conformal.py

## 26. Backup: what failed and what remains open

The consequence-targeted flag did not beat the simpler comparator. High-Dice consequential errors were uncommon: WT 1/205, TC 1/196, ET 2/169 high-Dice region observations. This is partly constrained by overlap-volume geometry and does not prove all clinical consequences are visible to Dice. Graded disagreement has AUROC 0.596 for wrong longitudinal calls. Global image appearance shift did not predict direction disagreement in the analysis. The third-voter effect is modest, and risk-control assumptions remain unresolved. These findings help narrow future work.

Sources:
https://github.com/Subhrakantsethi1005/Brain-MRI-Predicting-consequential-segmentation-errors/blob/codex/presentation-and-repository-refresh/results/brats2023/optionB/characterize_summary.json
https://github.com/Subhrakantsethi1005/Brain-MRI-Predicting-consequential-segmentation-errors/blob/codex/presentation-and-repository-refresh/results/lumiere/strengthen.json
https://github.com/Subhrakantsethi1005/Brain-MRI-Predicting-consequential-segmentation-errors/blob/codex/presentation-and-repository-refresh/results/lumiere/appearance.json
https://github.com/Subhrakantsethi1005/Brain-MRI-Predicting-consequential-segmentation-errors/blob/codex/presentation-and-repository-refresh/results/lumiere/threeway.json

## 27. Backup: sources and reproducibility

All project numbers trace to versioned snapshots or the independently rerun original longitudinal validation script. The repo contains a full evidence audit, portable command organization and a dataset-free recorded-data demo. Cite the LUMIERE authors and license for derived measurements. Clinical context comes from the RANO 2.0 operationalization paper. Related work narrows the novelty claim. No full retraining was performed for this presentation.

Sources:
https://github.com/Subhrakantsethi1005/Brain-MRI-Predicting-consequential-segmentation-errors/blob/codex/presentation-and-repository-refresh/results/README.md
https://github.com/Subhrakantsethi1005/Brain-MRI-Predicting-consequential-segmentation-errors/blob/codex/presentation-and-repository-refresh/docs/REPRODUCING.md
https://github.com/Subhrakantsethi1005/Brain-MRI-Predicting-consequential-segmentation-errors/blob/codex/presentation-and-repository-refresh/docs/EVIDENCE_AUDIT.md
https://doi.org/10.1038/s41597-022-01881-7
https://doi.org/10.3174/ajnr.A8396
https://arxiv.org/abs/2412.07156
https://arxiv.org/abs/2406.03323
https://arxiv.org/abs/2208.02814
