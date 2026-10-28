# Results (draft)

> Status: results computed on **MSD Task01_BrainTumour** (feasibility dataset),
> which stands in for BraTS 2021 while access is pending. All numbers below are
> read directly from `outputs/seg_model_msd/` and `outputs/risk_msd/`. The
> primary endpoint and all comparisons were frozen in
> `configs/preregistration.yaml` (committed `06a9ef7`) before the test set was
> evaluated (`outputs/risk_msd/EVALUATED_risk_test.lock`, commit `e361d06`).
> **Headline: on the pre-specified primary endpoint the candidate feature
> families do not significantly outperform the baselines; significant gains
> appear only on specific secondary endpoints.** This is reported as-is.

## 4.1 Data and splits

We use the MSD Task01_BrainTumour collection (484 patients with expert labels),
split at the patient level into `seg_train` (218), `seg_val` (24), `risk_dev`
(145) and `risk_test` (97). The segmenter sees only `seg_train`/`seg_val`; the
risk models are developed on `risk_dev` with repeated stratified cross-validation
and evaluated once on `risk_test`. Because MSD is drawn from the same source
scans as BraTS 2021, the two are never combined.

## 4.2 Segmentation model (Model 1)

The 3D residual U-Net was trained for 80 epochs; the checkpoint was selected on
`seg_val` mean Dice (best at epoch 44). On `seg_val` (n = 24):

| Region | Dice (mean) | Dice (median) | HD95 (median, mm) | Median abs. vol. error (mL) | Median rel. vol. error |
|---|---|---|---|---|---|
| Whole tumour (WT) | 0.817 | 0.854 | 43.7 | 15.7 | 0.115 |
| Tumour core (TC) | 0.714 | 0.750 | 58.5 | 7.3 | 0.249 |
| Enhancing (ET) | 0.727 | 0.812 | 3.0 | 1.6 | 0.141 |

These are feasibility-grade: the WT Dice of ~0.82 is below the ~0.90 reported by
tuned BraTS systems [3], [4], as expected for a single fixed-budget model trained
on a 6 GB GPU with no architecture search. The segmenter is deliberately
standard — the contribution is the error-risk predictor layered on top of it, not
the segmenter. The non-trivial median relative volume error (11.5 % WT, 24.9 % TC)
confirms that consequential volume errors do occur and are worth flagging.

## 4.3 Prevalence of consequential error

At the primary endpoint (WT relative volume error ≥ 25 % **and** absolute error
≥ 1 mL), the prevalence of consequential error was 37.9 % on `risk_dev` (55/145)
and 35.1 % on `risk_test` (34/97). Prevalence is high because the feasibility
segmenter is weak; a stronger BraTS segmenter will lower it, which the plan
anticipates (likely 5–15 %), widening the confidence intervals.

## 4.4 Primary endpoint — the candidate features do not beat the baselines

The primary model is L2-regularised logistic regression and the primary metric is
AUROC, both fixed in advance. On `risk_test` (n = 97, 34 positives):

| Feature family | AUROC [95 % CI] | AUPRC |
|---|---|---|
| `volume_only` (trivial baseline) | 0.827 [0.733, 0.908] | 0.720 |
| `best_single` (best single uncertainty score, chosen on dev) | 0.879 [0.802, 0.943] | 0.796 |
| `uncertainty` | 0.855 [0.770, 0.921] | 0.768 |
| `disagreement` | 0.875 [0.795, 0.941] | 0.779 |
| `boundary_morphology` (candidate 1) | **0.880** [0.809, 0.939] | 0.791 |
| `combined` (candidate 2) | 0.847 [0.761, 0.924] | 0.776 |

The pre-specified success criterion was that a candidate family
(`boundary_morphology` or `combined`) beat **both** `volume_only` and
`best_single` on a paired bootstrap of AUROC. It was not met:

| Comparison (candidate − reference), primary endpoint | ΔAUROC [95 % CI] | p |
|---|---|---|
| `boundary_morphology` − `best_single` | +0.001 [−0.050, +0.057] | 1.00 |
| `boundary_morphology` − `uncertainty` | +0.025 [−0.020, +0.075] | 0.28 |
| `boundary_morphology` − `volume_only` | +0.053 [−0.041, +0.149] | 0.26 |
| `combined` − `best_single` | −0.032 [−0.110, +0.044] | 0.44 |
| `combined` − `volume_only` | +0.021 [−0.083, +0.124] | 0.69 |
| `disagreement` − `volume_only` | +0.049 [−0.025, +0.130] | 0.22 |

Every candidate–baseline difference on the primary endpoint has a confidence
interval straddling zero. In particular, the strongest candidate
(`boundary_morphology`, AUROC 0.880) is statistically indistinguishable from the
single best uncertainty score (`best_single`, 0.879; Δ = +0.001, p = 1.00) and
from the trivial predicted-volume baseline (Δ = +0.053, p = 0.26). **On the
pre-specified primary endpoint, the engineered boundary/morphology and combined
features provide no measurable advantage over a single uncertainty summary or
even predicted volume alone.**

## 4.5 Triage operating point

With the threshold fixed on `risk_dev` for 90 % sensitivity, the primary-endpoint
`boundary_morphology` logistic model achieves, on `risk_test`: sensitivity 0.91,
a retained fraction of 0.49 (49 % of cases passed through for automated
processing), a residual consequential-error rate among retained cases of 6.3 %
(down from the 35 % base rate), and a false-alert rate of 0.29. So at a fixed
high sensitivity the system can safely automate roughly half of cases while
cutting the consequential-error rate on the automated stream by ~5.6×. This
triage behaviour, however, is delivered about equally well by the baselines — it
is a property of case-level reliability prediction in general, not of the
engineered features specifically.

## 4.6 Secondary endpoints — where signal does appear

The candidate features do separate from the baselines on two secondary endpoints
(paired bootstrap of AUROC, logistic, `risk_test`):

**`WT_dice80` (WT Dice < 0.80 — an overlap-failure endpoint):**

| Comparison | ΔAUROC [95 % CI] | p |
|---|---|---|
| `boundary_morphology` − `volume_only` | +0.133 [+0.038, +0.243] | 0.007 |
| `boundary_morphology` − `best_single` | +0.041 [+0.010, +0.079] | 0.005 |
| `combined` − `volume_only` | +0.120 [+0.031, +0.223] | 0.01 |
| `disagreement` − `volume_only` | +0.139 [+0.058, +0.241] | <0.001 |

**`WT_rel40` (WT relative volume error ≥ 40 % — a large-error endpoint):**

| Comparison | ΔAUROC [95 % CI] | p |
|---|---|---|
| `disagreement` − `best_single` | +0.059 [+0.008, +0.122] | 0.025 |
| `disagreement` − `uncertainty` | +0.043 [+0.004, +0.094] | 0.034 |
| `disagreement` − `volume_only` | +0.084 [+0.007, +0.178] | 0.035 |

On `WT_dice80` the boundary/morphology, combined, and disagreement families all
beat the trivial baseline and `best_single` with intervals clear of zero. On the
large-error `WT_rel40` endpoint, inter-pass disagreement is the family that
separates. No family beats the baselines on `TC_rel25`.

## 4.7 Reading of the results

Three things hold together. (i) Reference-free case-level prediction of
consequential volume error is feasible: all families reach AUROC 0.83–0.88 on the
primary endpoint and support a useful triage operating point. (ii) For the
pre-specified *volume*-error endpoint, the engineered features add nothing over a
single uncertainty summary or predicted volume alone — a negative result we
report in full because it was pre-registered. (iii) The engineered features *do*
help when the target is overlap failure (Dice < 0.80) or a large (≥ 40 %) volume
error, suggesting their advantage is concentrated in the clearer failures rather
than in the moderate 25 % volume-error regime that sits closest to annotation
noise. All results are on a feasibility dataset with a weak segmenter and 34 test
positives (wide intervals); they are feasibility evidence, not a final claim.
