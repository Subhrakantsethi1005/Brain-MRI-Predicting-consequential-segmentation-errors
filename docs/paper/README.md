# Paper — BIOAI-2026 submission

Reference-free prediction of **consequential volume errors** in brain-tumour MRI
segmentation, posed as a pre-registered triage benchmark.

## Section files (compile in this order)

| # | File | Status |
|---|---|---|
| — | `abstract.md` | Reframed around the actual feasibility finding (primary null; gains on secondary endpoints). ~300 words. |
| 1–2 | `introduction.md` | Full draft, 14 refs verified at source. Framed as aims — consistent with the negative primary result. |
| 3 | `methods.md` | Full draft. Matches implemented pipeline + frozen `preregistration.yaml`. |
| 4 | `results.md` | Full draft. Numbers read directly from `outputs/risk_msd/` and `outputs/seg_model_msd/`. |
| 5 | `discussion.md` | Full draft. Reads the negative primary result and the secondary-endpoint gains honestly. |
| 6 | `conclusion.md` | Full draft. |
| — | `references.md` | Working list; `introduction.md` has the verified [1]–[14] used in the intro. |
| — | `figures/` | `fig_auroc_primary.png`, `fig_forest_comparisons.png`; plus `../../outputs/risk_msd/risk_test_risk_coverage.png`. |

## Headline (honest, pre-registered)

On the MSD feasibility dataset, **all feature families reach AUROC 0.83–0.88 on
the primary endpoint and support a useful triage point (~49 % retained at 90 %
sensitivity, residual error 35 %→~6 %), but the engineered boundary/morphology
and combined features do NOT significantly beat a single uncertainty score or
predicted volume alone on the pre-specified 25 % volume-error endpoint.**
Significant gains appear only on `WT_dice80` (overlap failure) and `WT_rel40`
(large volume error). The contribution is the pre-registered, reproducible,
triage-framed benchmark + the honest finding.

## Before submission — open items

- **Dataset decision.** Results are MSD (feasibility). Either (a) submit as a
  feasibility study clearly labelled as such, or (b) rerun the identical pipeline
  on BraTS 2021 and swap in stronger numbers (needs Synapse/Kaggle access +
  compute). The text is written so either path needs only the numbers updated.
- Cite measured BraTS inter-rater **volume** variability against the 25 %
  threshold (flagged in `discussion.md` §5.2 and the implementation plan).
- `preregistration.yaml` still reads `STATUS: DRAFT`; it was committed (`06a9ef7`)
  before the test lock (`e361d06`), so the timestamp evidence holds — update the
  status line when finalising.
- Optional strengthening: cross-fitting (≈2× positives), external validation on
  BraTS-Africa, failure-case gallery from `outputs/pred_masks_msd/`.
- Final house-style / formatting pass; convert to the venue template.

## Regenerate figures

```bash
python scripts/make_figs.py   # (script currently in the session scratchpad; move it here to keep)
```
