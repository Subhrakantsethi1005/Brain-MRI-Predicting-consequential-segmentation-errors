"""Learned (end-to-end) error detector: a tiny 3D CNN that reads the segmenter's
own uncertainty maps and predicts consequential volume error, with NO hand-crafted
features and NO reference mask as input.

Why this exists
---------------
The hand-crafted feature families (see `features.py` / `risk.py`) did not beat the
trivial baselines on the primary volume-error endpoint. This module tests whether a
network, given the raw uncertainty volumes, can discover a better signal.

HONEST CAVEAT — read before trusting any result from this:
  End-to-end learning is data-hungry. With only ~145 development cases (MSD) this
  network will almost certainly OVERFIT and lose to logistic regression. Treat MSD
  as a machinery smoke-test only. A fair test needs BraTS 2021 (~375 dev cases) and
  a fresh, once-opened test split — the MSD test set is already locked and must not
  be reused to judge a new model.

Protocol parity:
  `learned_oof_scores(...)` mirrors `risk.oof_scores(...)` — it returns one
  out-of-fold risk score per development case under the SAME repeated stratified
  CV — so the learned detector plugs into the existing pre-registered comparison
  (paired bootstrap vs. `volume_only` and `best_single`) as a new family `learned`,
  judged by exactly the same rules.
"""

from __future__ import annotations

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from sklearn.model_selection import StratifiedKFold

from .features import binary_entropy
from . import REGIONS

EPS = 1e-6


# --------------------------------------------------------------------------- #
# Input: compact, reference-free uncertainty volume built from the MC samples
# --------------------------------------------------------------------------- #

def compact_uncertainty(samples, out_size=(64, 64, 64)):
    """samples: [S, 3, X, Y, Z] sigmoid probabilities (REGIONS order), float.

    Returns a float32 array [C, *out_size] with, per region, three channels —
    mean probability, variance across passes, and mean-probability entropy —
    resampled to a fixed small grid so cases are comparable and fit in 6 GB.
    Uses ONLY the stochastic predictions: no image, no reference mask.
    """
    samples = samples.astype(np.float32)
    chans = []
    for i in range(samples.shape[1]):  # per region
        mean_p = samples[:, i].mean(0)
        var_p = samples[:, i].var(0)
        ent = binary_entropy(mean_p)
        chans.extend([mean_p, var_p, ent])
    vol = np.stack(chans)[None]  # [1, C, X, Y, Z]
    t = torch.from_numpy(vol)
    t = F.interpolate(t, size=out_size, mode="trilinear", align_corners=False)
    return t[0].numpy().astype(np.float32)


CHANNELS_PER_REGION = ("mean_p", "var_p", "entropy")
N_CHANNELS = len(REGIONS) * len(CHANNELS_PER_REGION)  # 9


# --------------------------------------------------------------------------- #
# A deliberately tiny, heavily-regularised 3D CNN (few thousand params)
# --------------------------------------------------------------------------- #

class TinyErrorNet(nn.Module):
    """[B, C, D, H, W] -> [B] logit. Small on purpose: positives are scarce."""

    def __init__(self, in_ch=N_CHANNELS, width=8, p_drop=0.4):
        super().__init__()

        def block(ci, co):
            return nn.Sequential(
                nn.Conv3d(ci, co, 3, padding=1, bias=False),
                nn.BatchNorm3d(co), nn.ReLU(inplace=True),
                nn.MaxPool3d(2),
            )

        self.features = nn.Sequential(
            block(in_ch, width),          # 64 -> 32
            block(width, width * 2),      # 32 -> 16
            block(width * 2, width * 4),  # 16 -> 8
        )
        self.pool = nn.AdaptiveAvgPool3d(1)
        self.drop = nn.Dropout(p_drop)
        self.head = nn.Linear(width * 4, 1)

    def forward(self, x):
        x = self.features(x)
        x = self.pool(x).flatten(1)
        return self.head(self.drop(x)).squeeze(1)


# --------------------------------------------------------------------------- #
# Training with scarce-data hygiene: standardisation on train stats, flip
# augmentation, class-weighted loss, fixed short schedule.
# --------------------------------------------------------------------------- #

def _standardiser(X):
    """Per-channel mean/std over the training fold. X: [N, C, D, H, W]."""
    mean = X.mean(axis=(0, 2, 3, 4), keepdims=True)
    std = X.std(axis=(0, 2, 3, 4), keepdims=True) + EPS
    return mean.astype(np.float32), std.astype(np.float32)


def _rand_flip(x):
    """Random axis flips (D/H/W) as cheap augmentation. x: tensor [B,C,D,H,W]."""
    for ax in (2, 3, 4):
        if torch.rand(1).item() < 0.5:
            x = torch.flip(x, (ax,))
    return x


def _train_one(Xtr, ytr, device, epochs=40, lr=1e-3, wd=1e-3, width=8,
               p_drop=0.4, batch=8, seed=0):
    torch.manual_seed(seed)
    net = TinyErrorNet(in_ch=Xtr.shape[1], width=width, p_drop=p_drop).to(device)
    opt = torch.optim.AdamW(net.parameters(), lr=lr, weight_decay=wd)
    pos_weight = torch.tensor([(ytr == 0).sum() / max((ytr == 1).sum(), 1)],
                              dtype=torch.float32, device=device)
    loss_fn = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
    Xtr_t = torch.from_numpy(Xtr)
    ytr_t = torch.from_numpy(ytr.astype(np.float32))
    n = len(Xtr)
    net.train()
    for _ in range(epochs):
        perm = torch.randperm(n)
        for s in range(0, n, batch):
            idx = perm[s:s + batch]
            xb = _rand_flip(Xtr_t[idx].to(device))
            yb = ytr_t[idx].to(device)
            opt.zero_grad()
            loss_fn(net(xb), yb).backward()
            opt.step()
    return net


@torch.no_grad()
def _predict(net, X, device, batch=16):
    net.eval()
    out = []
    Xt = torch.from_numpy(X)
    for s in range(0, len(X), batch):
        xb = Xt[s:s + batch].to(device)
        out.append(torch.sigmoid(net(xb)).cpu().numpy())
    return np.concatenate(out)


def learned_oof_scores(X, y, folds=5, repeats=5, seed=0, device=None, **train_kw):
    """Out-of-fold risk scores from the learned detector, averaged over repeats.

    Drop-in analogue of `risk.oof_scores`. X: [N, C, D, H, W] float32 uncertainty
    volumes; y: binary endpoint labels. Standardisation is fit on each training
    fold only (no leakage).
    """
    y = np.asarray(y, int)
    device = device or ("cuda" if torch.cuda.is_available() else "cpu")
    folds = max(2, min(folds, int(y.sum()), int((1 - y).sum())))
    scores = np.zeros((repeats, len(y)), dtype=np.float64)
    for rep in range(repeats):
        skf = StratifiedKFold(n_splits=folds, shuffle=True, random_state=seed + rep)
        for tr, te in skf.split(np.zeros(len(y)), y):
            mean, std = _standardiser(X[tr])
            Xtr = (X[tr] - mean) / std
            Xte = (X[te] - mean) / std
            net = _train_one(Xtr, y[tr], device, seed=seed + rep, **train_kw)
            scores[rep, te] = _predict(net, Xte, device)
    return scores.mean(0)


def fit_full(X, y, seed=0, device=None, **train_kw):
    """Fit on all development cases; returns (net, mean, std) for scoring test cases."""
    y = np.asarray(y, int)
    device = device or ("cuda" if torch.cuda.is_available() else "cpu")
    mean, std = _standardiser(X)
    net = _train_one((X - mean) / std, y, device, seed=seed, **train_kw)
    return net, mean, std


def predict_scores(net, mean, std, X, device=None):
    device = device or ("cuda" if torch.cuda.is_available() else "cpu")
    return _predict(net, (X - mean) / std, device)
