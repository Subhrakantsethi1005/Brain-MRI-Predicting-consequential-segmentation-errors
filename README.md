# Predicting consequential segmentation errors in brain tumour MRI

Can a system tell, without the reference mask, when a brain tumour segmentation is wrong enough to change
the estimated tumour volume? This repository trains a standard 3D U-Net segmenter on BraTS, extracts
uncertainty, boundary and morphology features from stochastic predictions, and evaluates simple
risk models that flag cases for expert review.

This is a research pipeline, not a clinical decision system.

See **[docs/IMPLEMENTATION_PLAN.md](docs/IMPLEMENTATION_PLAN.md)** for the design, endpoint and timeline.

## Setup

```bash
pip install torch --index-url https://download.pytorch.org/whl/cu124   # match your CUDA driver
pip install -r requirements.txt
pytest -q          # synthetic end-to-end smoke test, CPU, ~2 min
```

Put the BraTS 2021 training data at `data/BraTS2021_Training_Data/<case>/<case>_{t1,t1ce,t2,flair,seg}.nii.gz`
(or edit `configs/default.yaml`).

## Pipeline

```bash
python scripts/00_make_splits.py                 # patient-level splits, once
python scripts/01_train_segmentation.py          # add --resume after an interruption
python scripts/02_infer_mc.py                    # features + reference errors -> outputs/case_features.csv
python scripts/03_train_risk_model.py            # risk_dev only: CV comparison, freeze models/thresholds
git commit configs/preregistration.yaml          # freeze the protocol
python scripts/04_evaluate_test.py               # risk_test, once
```

External dataset (e.g. BraTS-Africa 2023):

```bash
python scripts/02_infer_mc.py --external-root data/BraTS-Africa --external-name africa \
    --enhancing-label 3 --modalities t1n t1c t2w t2f
python scripts/04_evaluate_test.py --split africa --csv outputs/case_features_africa.csv
```

Before the real run, try the whole chain on a few cases by setting `data.max_cases: 20` and
`segmentation.max_epochs: 2`, using a separate `splits.file`.

## Layout

| Path | Contents |
|---|---|
| `configs/default.yaml` | paths and hyper-parameters (sized for a 6 GB GPU) |
| `configs/preregistration.yaml` | endpoint definitions and comparisons, committed before test evaluation |
| `src/brainrisk/data.py` | case discovery, patient-level splits, transforms |
| `src/brainrisk/model.py` | 3D U-Net, MC-dropout + flip inference |
| `src/brainrisk/features.py` | reference-free case features |
| `src/brainrisk/metrics.py` | Dice, HD95, volume errors, endpoint labels |
| `src/brainrisk/risk.py` | feature groups, risk models, triage metrics, bootstrap |
