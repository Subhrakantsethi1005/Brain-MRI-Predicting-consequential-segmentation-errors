"""Error-risk models, feature groups and evaluation (AUROC, AUPRC, triage metrics, bootstrap CIs)."""

import numpy as np
from sklearn.base import clone
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from . import REGIONS

UNCERTAINTY = ["mean_entropy_pred", "mean_var_pred", "mean_entropy_roi", "sum_entropy_ml"]
DISAGREEMENT = ["vol_cv", "vol_range_rel", "sample_dice_mean", "sample_dice_min"]
BOUNDARY_MORPH = ["boundary_entropy_mean", "boundary_var_mean", "uncertain_shell_rel", "soft_vol_diff_rel",
                  "n_components", "largest_cc_frac", "n_small_components", "surface_to_volume", "log_vol_pred"]


def feature_groups(columns, region):
    """Column lists for each pre-specified comparison, for the endpoint's region."""
    cols = set(columns)

    def pick(names, regions=(region,)):
        return [f"{r}_{n}" for r in regions for n in names if f"{r}_{n}" in cols]

    glob = sorted(c for c in cols if c.startswith("global_"))
    all_feats = pick(UNCERTAINTY + DISAGREEMENT + BOUNDARY_MORPH, REGIONS) + glob
    return {
        "volume_only": pick(["log_vol_pred"]),
        "uncertainty": pick(UNCERTAINTY) + [c for c in glob if c == "global_brain_entropy"],
        "disagreement": pick(DISAGREEMENT),
        "boundary_morphology": pick(BOUNDARY_MORPH),
        "combined": all_feats,
    }


def make_model(name, seed=0):
    if name == "logistic":
        return make_pipeline(SimpleImputer(strategy="median"), StandardScaler(),
                             LogisticRegression(C=1.0, class_weight="balanced", max_iter=5000))
    if name == "gbm":
        # Shallow and regularised: positives are scarce.
        return HistGradientBoostingClassifier(max_depth=3, learning_rate=0.05, max_iter=200,
                                              l2_regularization=1.0, class_weight="balanced",
                                              random_state=seed)
    raise ValueError(name)


def oof_scores(model, X, y, folds=5, repeats=5, seed=0):
    """Out-of-fold risk scores averaged over repeated stratified CV."""
    y = np.asarray(y, int)
    folds = max(2, min(folds, int(y.sum()), int((1 - y).sum())))
    scores = np.zeros((repeats, len(y)))
    for rep in range(repeats):
        skf = StratifiedKFold(n_splits=folds, shuffle=True, random_state=seed + rep)
        for tr, te in skf.split(X, y):
            m = clone(model).fit(X[tr], y[tr])
            scores[rep, te] = m.predict_proba(X[te])[:, 1]
    return scores.mean(0)


def threshold_for_sensitivity(y, s, target):
    """Largest threshold whose sensitivity (flag if s >= t) reaches the target."""
    y, s = np.asarray(y, int), np.asarray(s, float)
    pos = np.sort(s[y == 1])[::-1]
    if len(pos) == 0:
        return np.inf
    k = int(np.ceil(target * len(pos)))
    return float(pos[k - 1])


def operating_point(y, s, t):
    y, s = np.asarray(y, int), np.asarray(s, float)
    flag = s >= t
    tp, fp = int((flag & (y == 1)).sum()), int((flag & (y == 0)).sum())
    fn, tn = int((~flag & (y == 1)).sum()), int((~flag & (y == 0)).sum())
    retained = ~flag
    return {
        "threshold": t,
        "sensitivity": tp / max(tp + fn, 1),
        "specificity": tn / max(tn + fp, 1),
        "false_alert_rate": fp / max(fp + tn, 1),       # share of acceptable cases sent to review
        "alerts_per_100": 100 * flag.mean(),
        "retained_frac": retained.mean(),               # cases left for automated processing
        "residual_error_rate": float(y[retained].mean()) if retained.any() else np.nan,
        "tp": tp, "fp": fp, "fn": fn, "tn": tn,
    }


def risk_coverage(y, s):
    """Error rate among retained cases as cases are retained in order of increasing risk."""
    y = np.asarray(y, float)[np.argsort(s, kind="stable")]
    k = np.arange(1, len(y) + 1)
    return k / len(y), np.cumsum(y) / k


def aurc(y, s):
    _, risk = risk_coverage(y, s)
    return float(risk.mean())


METRICS = {
    "auroc": roc_auc_score,
    "auprc": average_precision_score,
    "brier": lambda y, s: brier_score_loss(y, np.clip(s, 0, 1)),
    "aurc": aurc,
}


def bootstrap_ci(y, s, fn, n=2000, seed=0, alpha=0.05):
    y, s = np.asarray(y), np.asarray(s)
    rng = np.random.default_rng(seed)
    vals = []
    for _ in range(n):
        idx = rng.integers(0, len(y), len(y))
        if y[idx].min() == y[idx].max():
            continue
        vals.append(fn(y[idx], s[idx]))
    return float(fn(y, s)), float(np.quantile(vals, alpha / 2)), float(np.quantile(vals, 1 - alpha / 2))


def paired_bootstrap_diff(y, s_a, s_b, fn=roc_auc_score, n=2000, seed=0):
    """fn(a) - fn(b) with a 95% CI and two-sided bootstrap p-value, resampling cases jointly."""
    y, s_a, s_b = map(np.asarray, (y, s_a, s_b))
    rng = np.random.default_rng(seed)
    diffs = []
    for _ in range(n):
        idx = rng.integers(0, len(y), len(y))
        if y[idx].min() == y[idx].max():
            continue
        diffs.append(fn(y[idx], s_a[idx]) - fn(y[idx], s_b[idx]))
    diffs = np.array(diffs)
    p = 2 * min((diffs <= 0).mean(), (diffs >= 0).mean())
    return {"diff": float(fn(y, s_a) - fn(y, s_b)), "lo": float(np.quantile(diffs, 0.025)),
            "hi": float(np.quantile(diffs, 0.975)), "p": float(min(p, 1.0))}


def summarise(y, s, n_boot=2000, seed=0):
    out = {"n": len(y), "n_pos": int(np.sum(y)), "prevalence": float(np.mean(y))}
    for name, fn in METRICS.items():
        v, lo, hi = bootstrap_ci(y, s, fn, n_boot, seed)
        out.update({name: v, f"{name}_lo": lo, f"{name}_hi": hi})
    return out
