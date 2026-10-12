"""Reference-based segmentation errors and the endpoint labels derived from them."""

import numpy as np
import pandas as pd
from scipy import ndimage

from . import REGIONS


def dice(a, b):
    a, b = np.asarray(a, bool), np.asarray(b, bool)
    s = a.sum() + b.sum()
    return 1.0 if s == 0 else 2.0 * np.logical_and(a, b).sum() / s


def _surface(mask):
    return mask & ~ndimage.binary_erosion(mask)


def hd95(a, b, spacing=(1.0, 1.0, 1.0)):
    """95th-percentile symmetric surface distance in mm; NaN if either mask is empty."""
    a, b = np.asarray(a, bool), np.asarray(b, bool)
    if not a.any() or not b.any():
        return np.nan
    sa, sb = _surface(a), _surface(b)
    dt_b = ndimage.distance_transform_edt(~sb, sampling=spacing)
    dt_a = ndimage.distance_transform_edt(~sa, sampling=spacing)
    d = np.concatenate([dt_b[sa], dt_a[sb]])
    return float(np.percentile(d, 95))


def case_errors(pred, ref, voxel_ml, spacing=(1.0, 1.0, 1.0)):
    """pred, ref: [3, X, Y, Z] binary in REGIONS order."""
    row = {}
    for i, r in enumerate(REGIONS):
        vp = float(pred[i].sum()) * voxel_ml
        vr = float(ref[i].sum()) * voxel_ml
        abs_err = abs(vp - vr)
        row.update({
            f"{r}_vol_pred_ml": vp,
            f"{r}_vol_ref_ml": vr,
            f"{r}_abs_err_ml": abs_err,
            f"{r}_signed_err_ml": vp - vr,
            # Undefined when the reference region is absent (common for ET).
            f"{r}_rel_err": abs_err / vr if vr > 0 else np.nan,
            f"{r}_dice": dice(pred[i], ref[i]),
            f"{r}_hd95": hd95(pred[i], ref[i], spacing),
        })
    return row


def endpoint_label(df, ep):
    """Binary 'consequential error' label for one endpoint spec from preregistration.yaml.

    Returns a float Series with NaN where the endpoint is undefined.
    """
    r = ep["region"]
    if "dice_below" in ep:
        return (df[f"{r}_dice"] < ep["dice_below"]).astype(float)
    rel = df[f"{r}_rel_err"]
    lab = ((rel >= ep["relative_error_min"]) &
           (df[f"{r}_abs_err_ml"] >= ep.get("absolute_error_min_ml", 0.0))).astype(float)
    return lab.where(rel.notna())


def all_endpoints(prereg):
    eps = [dict(prereg["primary_endpoint"], name="primary")]
    eps += prereg.get("secondary_endpoints", [])
    return eps


def add_labels(df, prereg):
    df = df.copy()
    for ep in all_endpoints(prereg):
        df[f"y_{ep['name']}"] = endpoint_label(df, ep)
    return df


def summarise_segmentation(df):
    rows = []
    for r in REGIONS:
        rows.append({
            "region": r,
            "dice_mean": df[f"{r}_dice"].mean(),
            "dice_median": df[f"{r}_dice"].median(),
            "hd95_median": df[f"{r}_hd95"].median(),
            "abs_err_ml_median": df[f"{r}_abs_err_ml"].median(),
            "rel_err_median": df[f"{r}_rel_err"].median(),
        })
    return pd.DataFrame(rows)
