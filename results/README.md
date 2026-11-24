# Frozen evidence snapshots

These are preserved outputs, not a fresh training run. BraTS artifacts came from Git commit `c0f2e1bc9889c911250964fedcdf2486782642e8`. LUMIERE JSON artifacts already existed in the author's local checkout and were previously excluded by the blanket `outputs/` ignore rule. Their code and values were inspected during the November 24, 2026 audit.

- `brats2023/`: patient splits, stochastic case features, logged training history and Option B summary JSON.
- `lumiere/`: full-cohort robustness, three-way comparison, appearance analysis and exploratory conformal results.

Do not overwrite these snapshots when reproducing. New runs belong in `outputs/`. See `docs/EVIDENCE_AUDIT.md` for limitations and the exact distinction between reported values and independently recomputed values.
