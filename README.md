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

Data options (set with `--config`):

- **`configs/msd.yaml`** — MSD Task01_BrainTumour: downloads instantly, no registration;
  use it to develop the pipeline now. Put it at `data/Task01_BrainTumour/{imagesTr,labelsTr}/`.
- **`configs/default.yaml`** — BraTS 2021 (full quality). Lay out as
  `data/BraTS2021_Training_Data/<case>/<case>_{t1,t1ce,t2,flair,seg}.nii.gz`.
- **`configs/fast.yaml`** — BraTS, laptop-fast overrides (smaller patch, fewer epochs/cases/MC passes).

The config carries the label convention (`enhancing_label`, `core_labels`) and the
dataset `layout` (`brats` folders vs `msd` 4D files), so the same scripts run on either.

## Pipeline

```bash
CFG=configs/msd.yaml                              # or default.yaml / fast.yaml
python scripts/00_make_splits.py --config $CFG            # patient-level splits, once
python scripts/01_train_segmentation.py --config $CFG     # --resume to continue; --warm-start X.pt to fine-tune
python scripts/eval_segmentation.py --config $CFG         # Model 1 report: Dice + volume error on seg_val
python scripts/02_infer_mc.py --config $CFG               # features + reference errors -> case_features*.csv
python scripts/03_train_risk_model.py --config $CFG       # risk_dev only: CV comparison, freeze models/thresholds
git commit configs/preregistration.yaml                   # freeze the protocol
python scripts/04_evaluate_test.py --config $CFG          # risk_test, once
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
| `configs/{default,fast,msd}.yaml` | dataset + hyper-parameter presets (6 GB GPU) |
| `configs/preregistration.yaml` | endpoint definitions and comparisons, committed before test evaluation |
| `docs/paper/` | introduction, abstract, and working reference list |
| `src/brainrisk/data.py` | case discovery (BraTS + MSD), patient-level splits, transforms |
| `src/brainrisk/model.py` | 3D U-Net, MC-dropout + flip inference |
| `src/brainrisk/features.py` | reference-free case features |
| `src/brainrisk/metrics.py` | Dice, HD95, volume errors, endpoint labels |
| `src/brainrisk/risk.py` | feature groups, risk models, triage metrics, bootstrap |
