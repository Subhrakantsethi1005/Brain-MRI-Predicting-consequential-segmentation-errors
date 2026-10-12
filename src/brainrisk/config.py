from pathlib import Path

import yaml


def load_config(path="configs/default.yaml"):
    with open(path) as f:
        return yaml.safe_load(f)


def load_prereg(path="configs/preregistration.yaml"):
    with open(path) as f:
        return yaml.safe_load(f)


def ensure_dir(path):
    Path(path).mkdir(parents=True, exist_ok=True)
    return Path(path)
