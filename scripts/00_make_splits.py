"""Discover cases and write patient-level splits. Run once; never regenerate after training starts."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from brainrisk.config import load_config  # noqa: E402
from brainrisk.data import discover_cases, make_splits, save_splits  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/default.yaml")
    ap.add_argument("--overwrite", action="store_true")
    args = ap.parse_args()
    cfg = load_config(args.config)
    d, s = cfg["data"], cfg["splits"]

    if Path(s["file"]).exists() and not args.overwrite:
        sys.exit(f"{s['file']} exists. Splits must stay fixed; pass --overwrite only before any training.")

    cases = discover_cases(d["root"], d["modalities"], d["label_suffix"], d["max_cases"])
    if not cases:
        sys.exit(f"No complete cases found under {d['root']}")
    splits = make_splits(cases, s, s["seed"])
    save_splits(splits, s["file"])
    for name, ids in splits.items():
        print(f"{name:10s} {len(ids):5d}")


if __name__ == "__main__":
    main()
