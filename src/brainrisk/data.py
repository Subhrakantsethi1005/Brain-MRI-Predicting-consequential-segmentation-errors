"""Case discovery, patient-level splitting and MONAI transforms."""

import json
import random
import re
from collections import defaultdict
from pathlib import Path

import numpy as np
import torch
from monai import transforms as mt

SPLITS = ("seg_train", "seg_val", "risk_dev", "risk_test")


def _find(case_dir, suffix):
    for p in sorted(case_dir.iterdir()):
        name = p.name
        if name.endswith((f"_{suffix}.nii.gz", f"-{suffix}.nii.gz", f"_{suffix}.nii", f"-{suffix}.nii")):
            return str(p)
    return None


def discover_cases(root, modalities, label_suffix="seg", max_cases=0):
    """One entry per case folder that has every modality and a label."""
    cases = []
    for case_dir in sorted(Path(root).iterdir()):
        if not case_dir.is_dir():
            continue
        images = [_find(case_dir, m) for m in modalities]
        label = _find(case_dir, label_suffix)
        if None in images or label is None:
            continue
        cases.append({"id": case_dir.name, "image": images, "label": label})
        if max_cases and len(cases) >= max_cases:
            break
    return cases


def patient_id(case_id):
    """BraTS 2023+ names cases BraTS-GLI-<patient>-<timepoint>; older releases use one case per patient."""
    m = re.match(r"^(BraTS-[A-Za-z]+-\d+)-\d+$", case_id)
    return m.group(1) if m else case_id


def make_splits(cases, fractions, seed):
    """Assign whole patients to splits so no patient appears in two splits."""
    by_patient = defaultdict(list)
    for c in cases:
        by_patient[patient_id(c["id"])].append(c["id"])
    patients = sorted(by_patient)
    random.Random(seed).shuffle(patients)

    total = sum(fractions[s] for s in SPLITS)
    bounds, acc = [], 0.0
    for s in SPLITS:
        acc += fractions[s] / total
        bounds.append(round(acc * len(patients)))
    splits, start = {}, 0
    for s, end in zip(SPLITS, bounds):
        splits[s] = sorted(cid for p in patients[start:end] for cid in by_patient[p])
        start = end
    return splits


def save_splits(splits, path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(splits, f, indent=2)


def load_splits(path):
    with open(path) as f:
        return json.load(f)


class ConvertToRegionsd(mt.MapTransform):
    """BraTS labels -> 3 binary channels [TC, WT, ET] (nested regions)."""

    def __init__(self, keys, enhancing_label=4):
        super().__init__(keys)
        self.et = enhancing_label

    def __call__(self, data):
        d = dict(data)
        for key in self.keys:
            lab = d[key]
            lab = lab[0] if lab.ndim == 4 else lab
            et = lab == self.et
            tc = (lab == 1) | et
            wt = tc | (lab == 2)
            stacked = torch.stack([tc, wt, et]) if isinstance(lab, torch.Tensor) else np.stack([tc, wt, et])
            d[key] = stacked.float() if isinstance(stacked, torch.Tensor) else stacked.astype(np.float32)
        return d


def regions_to_labels(regions, enhancing_label=4):
    """[TC, WT, ET] binary channels -> BraTS label map (uint8)."""
    tc, wt, et = (np.asarray(r, bool) for r in regions)
    out = np.zeros(wt.shape, np.uint8)
    out[wt] = 2
    out[tc] = 1
    out[et] = enhancing_label
    return out


def _base(enhancing_label):
    return [
        mt.LoadImaged(keys=["image", "label"], image_only=False),
        mt.EnsureChannelFirstd(keys=["image", "label"]),
        mt.EnsureTyped(keys=["image", "label"]),
        ConvertToRegionsd(keys="label", enhancing_label=enhancing_label),
        mt.Orientationd(keys=["image", "label"], axcodes="RAS"),
    ]


def train_transforms(roi_size, enhancing_label=4):
    return mt.Compose(_base(enhancing_label) + [
        mt.CropForegroundd(keys=["image", "label"], source_key="image", allow_smaller=True),
        mt.NormalizeIntensityd(keys="image", nonzero=True, channel_wise=True),
        mt.SpatialPadd(keys=["image", "label"], spatial_size=roi_size),
        # Half the patches centred on tumour so small lesions are seen often enough.
        mt.RandCropByPosNegLabeld(keys=["image", "label"], label_key="label", spatial_size=roi_size,
                                  pos=1, neg=1, num_samples=1, image_key="image", image_threshold=0),
        mt.RandFlipd(keys=["image", "label"], prob=0.5, spatial_axis=0),
        mt.RandFlipd(keys=["image", "label"], prob=0.5, spatial_axis=1),
        mt.RandFlipd(keys=["image", "label"], prob=0.5, spatial_axis=2),
        mt.RandScaleIntensityd(keys="image", factors=0.1, prob=1.0),
        mt.RandShiftIntensityd(keys="image", offsets=0.1, prob=1.0),
    ])


def eval_transforms(enhancing_label=4):
    return mt.Compose(_base(enhancing_label) + [
        mt.NormalizeIntensityd(keys="image", nonzero=True, channel_wise=True),
    ])
