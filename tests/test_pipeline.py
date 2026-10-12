"""Smoke tests on synthetic data: unit checks plus the full 00 -> 04 script chain on CPU."""

import subprocess
import sys
from pathlib import Path

import nibabel as nib
import numpy as np
import pandas as pd
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from brainrisk.data import ConvertToRegionsd, discover_msd, make_splits, patient_id, regions_to_labels  # noqa: E402
from brainrisk.features import case_features  # noqa: E402
from brainrisk.metrics import case_errors, dice, endpoint_label  # noqa: E402
from brainrisk.risk import operating_point, threshold_for_sensitivity  # noqa: E402

REPO = Path(__file__).resolve().parents[1]


def _sphere(shape, c, r):
    g = np.indices(shape)
    return ((g - np.array(c)[:, None, None, None]) ** 2).sum(0) <= r ** 2


def test_patient_level_splits_do_not_leak():
    cases = [{"id": f"BraTS-GLI-{p:05d}-{t:03d}"} for p in range(30) for t in range(2)]
    splits = make_splits(cases, {"seg_train": .5, "seg_val": .1, "risk_dev": .2, "risk_test": .2}, 0)
    seen = {}
    for s, ids in splits.items():
        for i in ids:
            assert seen.setdefault(patient_id(i), s) == s
    assert sum(len(v) for v in splits.values()) == 60


def test_errors_and_endpoint():
    ref = np.zeros((3, 20, 20, 20), bool)
    ref[:, 5:15, 5:15, 5:15] = True          # 1000 voxels = 1 mL at 1 mm
    pred = ref.copy()
    pred[:, 5:15, 5:15, 5:10] = False        # half the volume missing
    row = case_errors(pred, ref, voxel_ml=0.001)
    assert np.isclose(row["WT_rel_err"], 0.5)
    assert np.isclose(dice(pred[1], ref[1]), 2 * 500 / 1500)
    lab = endpoint_label(pd.DataFrame([row]), {"region": "WT", "relative_error_min": .25,
                                               "absolute_error_min_ml": 1.0})
    assert lab.iloc[0] == 0.0                # 0.5 mL error is below the 1 mL floor


def test_features_reflect_disagreement():
    shape = (24, 24, 24)
    stable = np.stack([np.stack([_sphere(shape, (12,) * 3, 6)] * 3)] * 5).astype(np.float16)
    unstable = np.stack([np.stack([_sphere(shape, (12,) * 3, r)] * 3) for r in (3, 5, 7, 9, 4)]).astype(np.float16)
    fs, _ = case_features(stable)
    fu, _ = case_features(unstable)
    assert fs["WT_vol_cv"] == 0 and fu["WT_vol_cv"] > 0.3
    assert fu["WT_sample_dice_mean"] < fs["WT_sample_dice_mean"] == 1.0
    assert fu["WT_uncertain_shell_rel"] > fs["WT_uncertain_shell_rel"]


def test_operating_point_hits_target_sensitivity():
    rng = np.random.default_rng(0)
    y = rng.integers(0, 2, 200)
    s = y + rng.normal(0, 1, 200)
    t = threshold_for_sensitivity(y, s, 0.9)
    assert operating_point(y, s, t)["sensitivity"] >= 0.9


def test_region_label_roundtrip():
    lab = np.array([0, 1, 2, 4])
    tc, wt, et = (lab == 1) | (lab == 4), lab > 0, lab == 4
    assert (regions_to_labels(np.stack([tc, wt, et])) == lab).all()


def test_region_conversion_conventions():
    # Same anatomy, two labelling schemes, must give identical TC/WT/ET.
    brats = np.array([[[0, 1, 2, 4]]])          # necrotic=1, oedema=2, enhancing=4
    msd = np.array([[[0, 2, 1, 3]]])            # oedema=1, non-enhancing=2, enhancing=3
    rb = ConvertToRegionsd("label", enhancing_label=4, core_labels=(1,))({"label": brats})["label"]
    rm = ConvertToRegionsd("label", enhancing_label=3, core_labels=(2,))({"label": msd})["label"]
    # channels are [TC, WT, ET]
    assert np.array_equal(rb, rm)
    assert rb[2].tolist() == [[[0, 0, 0, 1]]]   # ET only the enhancing voxel
    assert rb[0].tolist() == [[[0, 1, 0, 1]]]   # TC = core + enhancing
    assert rb[1].tolist() == [[[0, 1, 1, 1]]]   # WT = all non-zero


def test_discover_msd(tmp_path):
    img, lab = tmp_path / "imagesTr", tmp_path / "labelsTr"
    img.mkdir(); lab.mkdir()
    for i in range(3):
        name = f"BRATS_{i:03d}.nii.gz"
        nib.save(nib.Nifti1Image(np.zeros((4, 4, 4, 4), np.float32), np.eye(4)), img / name)
        nib.save(nib.Nifti1Image(np.zeros((4, 4, 4), np.uint8), np.eye(4)), lab / name)
    (img / "._BRATS_000.nii.gz").write_bytes(b"junk")   # macOS resource fork, must be skipped
    (img / "BRATS_999.nii.gz").touch()                  # no matching label, must be skipped
    nib.save(nib.Nifti1Image(np.zeros((4, 4, 4, 4), np.float32), np.eye(4)), img / "BRATS_999.nii.gz")
    cases = discover_msd(str(tmp_path))
    assert [c["id"] for c in cases] == ["BRATS_000", "BRATS_001", "BRATS_002"]
    assert all(isinstance(c["image"], str) for c in cases)


def _write_synthetic_brats(root, n, shape=(40, 40, 40), seed=0):
    rng = np.random.default_rng(seed)
    for i in range(n):
        d = root / f"BraTS2021_{i:05d}"
        d.mkdir(parents=True)
        brain = _sphere(shape, (20, 20, 20), 17)
        c = rng.integers(14, 26, 3)
        wt = _sphere(shape, c, rng.uniform(3, 8))
        tc = _sphere(shape, c, 2.5)
        et = tc & ~_sphere(shape, c, 1.2)
        seg = np.zeros(shape, np.uint8)
        seg[wt] = 2; seg[tc] = 1; seg[et] = 4
        for m in ("t1", "t1ce", "t2", "flair"):
            img = brain * (100 + rng.normal(0, 5, shape)) + wt * rng.uniform(20, 60)
            nib.save(nib.Nifti1Image(img.astype(np.float32), np.eye(4)), d / f"{d.name}_{m}.nii.gz")
        nib.save(nib.Nifti1Image(seg, np.eye(4)), d / f"{d.name}_seg.nii.gz")


def _run(script, cwd, *args):
    r = subprocess.run([sys.executable, str(REPO / "scripts" / script), *args], cwd=cwd,
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    return r.stdout


def test_end_to_end(tmp_path):
    _write_synthetic_brats(tmp_path / "data", 60)
    cfg = yaml.safe_load(open(REPO / "configs/default.yaml"))
    cfg["data"]["root"] = "data"
    cfg["splits"].update(seg_train=.2, seg_val=.05, risk_dev=.5, risk_test=.25)
    cfg["segmentation"].update(roi_size=[32, 32, 32], max_epochs=2, val_every=1, num_workers=0,
                               channels=[8, 16, 32], strides=[2, 2])
    cfg["inference"].update(mc_samples=3)
    cfg["risk"].update(cv_folds=3, cv_repeats=1, bootstrap=50)
    (tmp_path / "configs").mkdir()
    yaml.safe_dump(cfg, open(tmp_path / "configs/default.yaml", "w"))
    (tmp_path / "configs/preregistration.yaml").write_text((REPO / "configs/preregistration.yaml").read_text())

    _run("00_make_splits.py", tmp_path)
    _run("01_train_segmentation.py", tmp_path)
    _run("02_infer_mc.py", tmp_path)
    _run("02_infer_mc.py", tmp_path)  # resumable: second run is a no-op
    csv = tmp_path / "outputs/case_features.csv"
    df = pd.read_csv(csv)
    assert df.case_id.is_unique and set(df.split) == {"seg_val", "risk_dev", "risk_test"}

    # A 2-epoch model is useless, so overwrite the errors with ones tied to a feature,
    # purely to exercise the risk-model plumbing.
    rng = np.random.default_rng(1)
    z = df["WT_vol_cv"].rank(pct=True) + rng.normal(0, .2, len(df))
    df["WT_rel_err"] = np.where(z > z.median(), 0.5, 0.05)
    df["WT_abs_err_ml"] = 5.0
    df["TC_rel_err"], df["TC_abs_err_ml"] = df["WT_rel_err"], 5.0
    df["WT_dice"] = np.where(z > z.median(), 0.6, 0.9)
    df.to_csv(csv, index=False)

    _run("03_train_risk_model.py", tmp_path)
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "add", "configs/preregistration.yaml"], cwd=tmp_path, check=True)
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "prereg"],
                   cwd=tmp_path, check=True)
    out = _run("04_evaluate_test.py", tmp_path)
    assert "auroc" in out
    rep = pd.read_csv(tmp_path / "outputs/risk/risk_test_report.csv")
    assert {"combined", "uncertainty", "volume_only", "best_single"} <= set(rep.group)
    # A second look must be explicit.
    r = subprocess.run([sys.executable, str(REPO / "scripts/04_evaluate_test.py")], cwd=tmp_path,
                       capture_output=True, text=True)
    assert r.returncode != 0 and "already evaluated" in r.stderr
