# References

Numbered to match `introduction.md`. Status as of the Oct 2026 literature check.
Do a final house-style/format pass (and a last source check on the 2026 preprints,
[12]–[14]) before submission.

- **[1]** Weller, M. et al. EANO guidelines on the diagnosis and treatment of
  diffuse gliomas of adulthood. *Nat. Rev. Clin. Oncol.* 18(3):170–186, 2021.
  doi:10.1038/s41571-020-00447-z. ✅ verified
- **[2]** Wen, P. Y. et al. Updated response assessment criteria for high-grade
  gliomas (RANO working group). *J. Clin. Oncol.* 28(11):1963–1972, 2010.
  doi:10.1200/JCO.2009.26.3541. ✅ verified
- **[3]** Isensee, F., Jaeger, P. F., Kohl, S. A. A., Petersen, J. &
  Maier-Hein, K. H. nnU-Net: a self-configuring method for deep learning-based
  biomedical image segmentation. *Nat. Methods* 18(2):203–211, 2021.
  doi:10.1038/s41592-020-01008-z. ✅ verified
- **[4]** Baid, U. et al. The RSNA-ASNR-MICCAI BraTS 2021 benchmark on brain
  tumor segmentation and radiogenomic classification. arXiv:2107.02314, 2021.
  SegResNet: Myronenko, A. 3D MRI brain tumor segmentation using autoencoder
  regularization. *BrainLes @ MICCAI 2018.* arXiv:1810.11654. ✅ verified
- **[5]** Mehta, R. et al. QU-BraTS: MICCAI BraTS 2020 Challenge on Quantifying
  Uncertainty in Brain Tumor Segmentation. *MELBA*, 2022. arXiv:2112.10074.
  ✅ verified
- **[6]** Jungo, A., Balsiger, F. & Reyes, M. Analyzing the Quality and Challenges
  of Uncertainty Estimations for Brain Tumor Segmentation. *Front. Neurosci.*
  14:282, 2020. doi:10.3389/fnins.2020.00282. ✅ verified
- **[7]** Valindria, V. V. et al. Reverse Classification Accuracy: Predicting
  Segmentation Performance in the Absence of Ground Truth. *IEEE TMI*
  36(8):1597–1606, 2017. arXiv:1702.03407. ✅ verified
- **[8]** Robinson, R. et al. Automated quality control in image segmentation:
  UK Biobank cardiovascular MR imaging study. *J. Cardiovasc. Magn. Reson.*
  21:18, 2019. doi:10.1186/s12968-019-0523-x. ✅ verified
- **[9]** Guennoun, Y. et al. Segmenting with confidence through uncertainty
  quantification for brain tumor imaging. *npj Digital Medicine*, 2026.
  doi:10.1038/s41746-026-02902-0. ✅ verified
- **[10]** Lambert, B., Forbes, F., Doyle, S. & Dojat, M. Robust Conformal Volume
  Estimation in 3D Medical Images. *MICCAI 2024.* arXiv:2407.19938. ✅ verified
- **[11]** Bertels, J., Robben, D., Vandermeulen, D. & Suetens, P. Optimization
  with Soft Dice Can Lead to a Volumetric Bias. *BrainLes @ MICCAI 2019.*
  doi:10.1007/978-3-030-46640-4_9. arXiv:1911.02278. ✅ verified
- **[12]** Shet, R. D., Liang, C. & Zhang, L. Reliability analysis for BraTS-GoAT
  segmentation: a controlled robustness study of deep-ensemble uncertainty.
  arXiv:2608.13223, 2026. ⚠ 2026 preprint — re-confirm before submission
- **[13]** Sharma, M. Monte Carlo Dropout Uncertainty and Entropy-Thresholded
  Selective Prediction for Architecture-Agnostic Brain Tumor MRI Triage.
  arXiv:2607.16317, 2026. *(classification, not segmentation)* ⚠ 2026 preprint
- **[14]** Bricout, A., Hardman, D., Inglis, S., Pye, S. & Moran, C. M. Beyond
  segmentation accuracy: understanding model reliability and failure modes in
  ultrasound image analysis. *Front. Med. Technol.* 8, 2026.
  doi:10.3389/fmedt.2026.1918432. ⚠ 2026 — re-confirm before submission

## Not cited (deliberately left out)
- **CA-WCP** (arXiv:2610.09392, 2026) and **Eaton-Rosen et al.** (structure-wise
  uncertainty, MICCAI 2018): flagged unverified in the source check — **do not cite**
  until confirmed.

## Positioning note (for the related-work section)
[9] and [10] are close to directions we deliberately do **not** claim (calibrated
intervals, conformal guarantees). Cite them explicitly and state that our
contribution is the simpler, clinically-thresholded *consequential-volume-error
triage* framing with an honest feature comparison and a per-case direction-of-error
probe — not a new calibration or guarantee method.
