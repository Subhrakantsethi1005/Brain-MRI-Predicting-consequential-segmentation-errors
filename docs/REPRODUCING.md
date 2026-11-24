# Reproduction

Run from repository root. Python 3.10+ is declared; the available original environment uses Python 3.12 and PyTorch 2.6 / MONAI 1.5. Install a PyTorch build appropriate for your hardware, then `pip install -r requirements.txt` and `pip install -e .`.

## Recorded-data demo

`python demo/run_demo.py` uses only the standard library and the bundled derived measurements. It requires no MRI data or weights.

## BraTS pipeline

Download licensed BraTS 2023 adult glioma data separately. Set `data.root` in `configs/brats2023.yaml` to a folder whose immediate children are BraTS-GLI case folders. The default portable location is `data/BraTS2023_GLI`. Run:

```bash
python scripts/pipeline/00_make_splits.py --config configs/brats2023.yaml
python scripts/pipeline/01_train_segmentation.py --config configs/brats2023.yaml
python scripts/pipeline/eval_segmentation.py --config configs/brats2023.yaml
python scripts/pipeline/02_infer_mc.py --config configs/brats2023.yaml
python scripts/pipeline/03_train_risk_model.py --config configs/brats2023.yaml
python scripts/pipeline/04_evaluate_test.py --config configs/brats2023.yaml
```

This trains a standard MONAI UNet with residual units, not SegResNet. Four channels (T1, T1c, T2, FLAIR), output TC/WT/ET. Channels 16/32/64/128/256, two residual units, stride 2, dropout 0.1. Training uses foreground crop, nonzero channel normalization, positive/negative patch sampling, random flips and intensity scale/shift augmentation. Dice loss uses sigmoid outputs and squared predictions. AMP is enabled on CUDA, batch size 1. Validation occurs every five epochs; best mean Dice selects the checkpoint. Stochastic inference uses 10 passes cycling eight flip combinations, sliding-window overlap 0.5 and threshold 0.5.

To reproduce the Option B analyses from versioned features, without GPU training:

```bash
python scripts/brats/optionB_characterize.py --csv results/brats2023/case_features.csv
python scripts/brats/optionB_flag.py --csv results/brats2023/case_features.csv --region WT
```

These write new files under ignored `outputs/`. Do not interpret reruns of a previously inspected test set as a new locked validation. The 90%-sensitivity Option B operating point uses test labels; future work must freeze the threshold on development/calibration data.

## LUMIERE

Obtain the public LUMIERE expert ratings and DeepBraTumIA / HD-GLIO-AUTO pyradiomics CSVs from https://doi.org/10.1038/s41597-022-01881-7 and place them in `data/lumiere/` using the original release filenames. Then:

```bash
python scripts/longitudinal/lumiere_validate.py
python scripts/longitudinal/lumiere_strengthen.py
python scripts/longitudinal/lumiere_export_demo.py
```

The exporter writes `outputs/lumiere/demo_data.json`. The bundled `demo/data/lumiere.json` is a provenance-labelled replay snapshot, with calls recomputed from its recorded measurements at source precision. Expert labels are for retrospective evaluation only, never inputs to a reliability rule. See the audit for protocol deviations and why the conformal extension is exploratory.
