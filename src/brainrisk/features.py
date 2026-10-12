"""Case-level features computed only from the model's stochastic predictions (no reference needed).

Feature names are '<region>_<feature>' or 'global_<feature>'. Groups used in the
comparisons are defined in risk.py by feature name, so keep names stable.
"""

import numpy as np
from scipy import ndimage

from . import REGIONS

EPS = 1e-6
_STRUCT = ndimage.generate_binary_structure(3, 1)


def binary_entropy(p):
    p = np.clip(p, EPS, 1 - EPS)
    return -(p * np.log(p) + (1 - p) * np.log(1 - p))


def _safe_mean(x, mask):
    return float(x[mask].mean()) if mask.any() else 0.0


def region_features(samples, threshold=0.5, voxel_ml=0.001, band=2, small_cc_vox=100):
    """samples: [S, X, Y, Z] probabilities for one region."""
    samples = samples.astype(np.float32)
    mean_p = samples.mean(0)
    var_p = samples.var(0)
    ent = binary_entropy(mean_p)
    pred = mean_p > threshold
    n_pred = int(pred.sum())
    vol = n_pred * voxel_ml

    f = {"vol_pred_ml": vol, "log_vol_pred": np.log1p(vol)}

    # --- voxel-wise uncertainty summaries (standard baselines) ---
    roi = ndimage.binary_dilation(pred, _STRUCT, iterations=band) if n_pred else pred
    f["mean_entropy_pred"] = _safe_mean(ent, pred)
    f["mean_var_pred"] = _safe_mean(var_p, pred)
    f["mean_entropy_roi"] = _safe_mean(ent, roi)
    f["sum_entropy_ml"] = float(ent.sum()) * voxel_ml

    # --- disagreement between stochastic passes ---
    sample_masks = samples > threshold
    s_vols = sample_masks.reshape(len(samples), -1).sum(1) * voxel_ml
    f["vol_cv"] = float(s_vols.std() / (s_vols.mean() + EPS)) if s_vols.mean() > 0 else 0.0
    f["vol_range_rel"] = float((s_vols.max() - s_vols.min()) / max(vol, voxel_ml))
    dices = []
    for m in sample_masks:
        s = m.sum() + n_pred
        dices.append(1.0 if s == 0 else 2.0 * np.logical_and(m, pred).sum() / s)
    f["sample_dice_mean"] = float(np.mean(dices))
    f["sample_dice_min"] = float(np.min(dices))

    # --- boundary uncertainty: how much volume is genuinely undecided ---
    if n_pred:
        outer = ndimage.binary_dilation(pred, _STRUCT, iterations=band)
        inner = ndimage.binary_erosion(pred, _STRUCT, iterations=band)
        shell = outer & ~inner
    else:
        shell = pred
    f["boundary_entropy_mean"] = _safe_mean(ent, shell)
    f["boundary_var_mean"] = _safe_mean(var_p, shell)
    undecided = (mean_p > 0.2) & (mean_p < 0.8)
    # Volume that could flip either way, relative to predicted volume: a direct
    # proxy for how far the volume estimate could move.
    f["uncertain_shell_rel"] = float(undecided.sum() * voxel_ml / max(vol, voxel_ml))
    f["soft_vol_diff_rel"] = float(abs(mean_p.sum() * voxel_ml - vol) / max(vol, voxel_ml))

    # --- morphology of the predicted region ---
    if n_pred:
        cc, n_cc = ndimage.label(pred, _STRUCT)
        sizes = np.bincount(cc.ravel())[1:]
        f["n_components"] = int(n_cc)
        f["largest_cc_frac"] = float(sizes.max() / n_pred)
        f["n_small_components"] = int((sizes < small_cc_vox).sum())
        surface = pred & ~ndimage.binary_erosion(pred, _STRUCT)
        f["surface_to_volume"] = float(surface.sum() / n_pred)
    else:
        f.update(n_components=0, largest_cc_frac=0.0, n_small_components=0, surface_to_volume=0.0)
    f["empty_pred"] = int(n_pred == 0)
    return f, pred


def case_features(samples, threshold=0.5, voxel_ml=0.001, band=2, brain_mask=None):
    """samples: [S, 3, X, Y, Z] in REGIONS order. Returns (features dict, binary prediction [3, ...])."""
    feats, preds = {}, []
    for i, r in enumerate(REGIONS):
        f, pred = region_features(samples[:, i], threshold, voxel_ml, band)
        feats.update({f"{r}_{k}": v for k, v in f.items()})
        preds.append(pred)
    preds = np.stack(preds)
    tc, wt, et = preds

    # Nested-region consistency: ET should lie in TC, TC in WT.
    feats["global_et_outside_tc"] = float((et & ~tc).sum() / max(et.sum(), 1))
    feats["global_tc_outside_wt"] = float((tc & ~wt).sum() / max(tc.sum(), 1))
    if brain_mask is not None:
        wt_ent = binary_entropy(samples[:, 1].astype(np.float32).mean(0))
        feats["global_brain_entropy"] = _safe_mean(wt_ent, brain_mask)
    return feats, preds
