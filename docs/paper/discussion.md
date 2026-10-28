# Discussion (draft)

> Status: draft reading of the MSD feasibility results (§4). To be revisited if
> BraTS 2021 results are added before submission.

## 5.1 What the results show

We posed segmentation reliability as the case-level prediction of consequential
volume error, pre-registered the endpoint and the comparison, and evaluated the
test set once. Three findings stand.

First, **reference-free case-level prediction of consequential volume error is
feasible but not easy**: every feature family reaches AUROC 0.83–0.88 on the
primary endpoint, and the resulting triage keeps ~49 % of cases for automation at
90 % sensitivity while cutting the consequential-error rate on that stream from
35 % to ~6 %. The decision framing is operationally useful.

Second, and contrary to our working hypothesis, **the engineered
boundary/morphology and combined features do not beat the simple baselines on the
pre-specified volume-error endpoint**. The strongest candidate is
indistinguishable from a single uncertainty score (Δ AUROC = +0.001, p = 1.00)
and from predicted volume alone (Δ = +0.053, p = 0.26). On the primary endpoint,
the "just threshold one uncertainty number" baseline is as good as the richer
feature sets. We report this because it was pre-registered, and because negative
results on reference-free indicators are themselves part of the literature this
work builds on [14].

Third, **where the engineered features help, it is on the clearer failures**:
boundary/morphology, combined and disagreement families separate from the
baselines on WT Dice < 0.80 (overlap failure) and inter-pass disagreement
separates on WT ≥ 40 % volume error. The common thread is that the extra features
earn their place when the error is large or the mask is visibly degenerate, not
in the moderate 25 % volume-error band.

## 5.2 Why the primary signal is weak — and the threshold caveat

The implementation plan flagged this risk in advance: a 25 % relative
volume-error threshold sits close to published inter-rater volume variability for
BraTS, so a non-trivial share of "consequential" cases at 25 % may reflect
annotation noise rather than model failure that reference-free features could
plausibly detect. The pattern in §4 — no separation at 25 %, clear separation at
40 % and at Dice < 0.80 — is consistent with that explanation: as the endpoint
moves away from the annotation-noise floor, the engineered features begin to
matter. A final version should cite measured BraTS inter-rater volume
variability and state explicitly where the 25 % threshold sits relative to it.

## 5.3 Limitations

- **Feasibility dataset and weak segmenter.** Results are on MSD with a
  fixed-budget segmenter (WT Dice ~0.82, below BraTS SOTA). A stronger segmenter
  will lower the prevalence of consequential error and change the operating
  regime; these numbers should be read as feasibility evidence, not a final
  benchmark.
- **Small positive count.** 34 test positives give wide confidence intervals;
  absence of a significant difference is not evidence of equivalence. The planned
  fixes are more data and cross-fitting (every case gets an out-of-fold
  prediction), not a lower threshold.
- **No external validation yet.** BraTS-Africa (lower field strength, different
  population) is supported by the scripts but not yet run.
- **Calibration.** The class-balanced logistic model is not calibrated; the Brier
  score reflects this and probability outputs should not be read as risks without
  recalibration.
- **Single segmenter, single uncertainty source.** We use MC-dropout with
  flip-TTA on one architecture; deep ensembles or other estimators may change the
  feature signal.

## 5.4 Relation to prior work

Our findings refine rather than overturn the prior literature. QU-BraTS found no
single uncertainty method dominates [5]; our primary endpoint echoes this at the
case level — no family dominates for moderate volume error. Jungo et al.'s
subject-level miscalibration [6] is consistent with the engineered features
helping only on clear failures. Unlike reference-free QC that targets overlap
[7], [8], we target volume error against a pre-specified clinical threshold and
report triage outcomes; our honest finding is that this specific, harder target
is not well served by the richer reference-free features at the 25 % level, even
though it is at 40 % and for Dice failure.

## 5.5 What would strengthen the claim

Running the full BraTS 2021 protocol (stronger segmenter, more cases, lower and
more realistic prevalence), adding cross-fitting to roughly double the positive
count, reporting measured inter-rater volume variability against the endpoint,
and adding external validation on BraTS-Africa. Each is implemented or scoped in
the pipeline; none changes the pre-registered endpoint.
