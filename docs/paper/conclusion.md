# Conclusion (draft)

We framed brain-tumour segmentation reliability as the case-level prediction of
**consequential volume error**, with the error endpoint pre-specified against a
clinically motivated threshold and frozen before any test evaluation, and we
compared reference-free feature families against trivial predicted-volume and
single-best-uncertainty baselines using a paired bootstrap, reported as an
operational triage task.

On a feasibility dataset (MSD Task01_BrainTumour) the pre-registered primary
result is **negative**: engineered boundary/morphology and combined features do
not significantly outperform a single uncertainty summary or predicted volume
alone at the 25 % whole-tumour volume-error endpoint (AUROC 0.83–0.88 across all
families; strongest candidate vs. best single score Δ = +0.001, p = 1.00). The
same features *do* separate from the baselines on clearer failures — WT Dice
< 0.80 and WT volume error ≥ 40 % — and all families support a useful operating
point, retaining ~49 % of cases for automation at 90 % sensitivity while reducing
the consequential-error rate on that stream from 35 % to ~6 %.

The contribution is therefore a **pre-registered, reproducible, triage-framed
benchmark** for consequential volume-error prediction, runnable on a single
commodity GPU, together with an honest account of which readily available signals
actually predict it — including where they do not. Confirming these feasibility
findings on the full BraTS 2021 protocol, with cross-fitting and external
validation, is the natural next step; the pipeline and frozen protocol are in
place to do so without changing the endpoint.
