# References (working list)

Compiled from the Oct 2026 literature check. **Verify exact authors/year/venue
before submission** — these were gathered from web search and need a final
bibliographic check. The `[n]` keys match the introduction draft.

- **[1]** Glioma MRI / clinical management — *choose a review*, e.g. Weller et al.,
  EANO guidelines (to confirm).
- **[2]** RANO progression criteria — Wen et al., *J Clin Oncol*, 2010 (updated
  response-assessment criteria for high-grade gliomas).
- **[3]** nnU-Net for brain tumour segmentation — Isensee et al., BrainLes/MICCAI
  2020. arXiv:2011.00848.
- **[4]** BraTS 2021 benchmark — Baid et al., 2021. arXiv:2107.02314. (SegResNet /
  autoencoder regularization: Myronenko, 2018.)
- **[5]** QU-BraTS: quantifying uncertainty in brain tumour segmentation — Mehta
  et al., 2022. arXiv:2112.10074.
- **[6]** Analyzing the quality and challenges of uncertainty estimations for brain
  tumour segmentation — Jungo, Balsiger & Reyes, *Front. Neurosci.*, 2020.
  (PMC7156850 — a starting paper from the project brief.)
- **[7]** Reverse classification accuracy: predicting segmentation performance
  without ground truth — Valindria et al., *IEEE TMI*, 2017.
- **[8]** Real-time / automated QC for segmentation (UK Biobank) — Robinson et al.,
  MICCAI 2018 / *J. Cardiovasc. Magn. Reson.*, 2019.
- **[9]** Calibrated volumetric uncertainty for brain tumour imaging — Guennoun
  et al., *npj Digital Medicine*, 2026 (doi:10.1038/s41746-026-02902-0 — the second
  starting paper from the brief); see also Eaton-Rosen et al. (structure-wise
  uncertainty for volume CIs, MICCAI 2018) and "On the relationship between
  calibrated predictors and unbiased volume estimation" (arXiv:2112.12560).
- **[10]** Conformal volume estimation under distribution shift — "Robust Conformal
  Volume Estimation in 3D Medical Images," MICCAI 2024 (arXiv:2407.19938); and
  CA-WCP, arXiv:2610.09392, 2026.

## Note on positioning (important for the related-work section)
[9] and [10] are close to directions we deliberately do **not** claim (calibrated
intervals, signed/asymmetric volume error, conformal guarantees). Cite them
explicitly and state that our contribution is the simpler, clinically-thresholded
*consequential-volume-error triage* framing with an honest feature comparison — not
a new calibration or guarantee method.
