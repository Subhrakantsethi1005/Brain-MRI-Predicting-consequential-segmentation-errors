"""One-command download of the BraTS 2023 Adult Glioma training set (public, no login).

    python scripts/download_brats2023.py

Downloads ~13.4 GB into data/brats2023_download/, finds the folder that holds the
BraTS-GLI-* case folders, and prints the exact `root:` line to put in
configs/brats2023.yaml. Safe to re-run: it resumes and skips files already fetched.
"""
import os
import sys
import time
from pathlib import Path

# Use the plain, reliable HTTPS download path. The fast "Xet" / hf_transfer
# backends are quicker but throw transient CAS server errors on flaky networks;
# plain mode is slower but almost never fails. Must be set BEFORE the HF import.
os.environ["HF_HUB_DISABLE_XET"] = "1"
os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "0"

from huggingface_hub import snapshot_download

REPO = "MedOtter/brats2023-gli-dataset"
DEST = Path(__file__).resolve().parents[1] / "data" / "brats2023_download"
MAX_TRIES = 30


def main():
    DEST.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {REPO} (~13.4 GB) into:\n  {DEST}\n"
          "Slow-but-reliable mode. It resumes automatically, so a dropped\n"
          "connection is fine — already-downloaded files are kept.\n")
    path = None
    for attempt in range(1, MAX_TRIES + 1):
        try:
            path = snapshot_download(repo_id=REPO, repo_type="dataset",
                                     local_dir=str(DEST),
                                     max_workers=4)
            break  # finished
        except KeyboardInterrupt:
            print("\nStopped by user. Re-run the same command to resume.")
            sys.exit(1)
        except Exception as e:
            print(f"\n[attempt {attempt}/{MAX_TRIES}] transient error, resuming in 10s:\n  {e}")
            time.sleep(10)
    if path is None:
        print("\nStill failing after many retries — likely an unstable connection. "
              "Just run the command again later; it resumes where it left off.")
        sys.exit(1)

    # Find the directory whose immediate children are the BraTS-GLI-* case folders.
    root = None
    for d in Path(path).rglob("*"):
        if d.is_dir() and any(c.is_dir() and c.name.startswith("BraTS-GLI-")
                              for c in d.iterdir()):
            root = d
            break

    n_cases = n_seg = 0
    if root:
        cases = [c for c in root.iterdir() if c.is_dir() and c.name.startswith("BraTS-GLI-")]
        n_cases = len(cases)
        n_seg = sum(1 for _ in root.glob("BraTS-GLI-*/*seg.nii.gz"))

    print("\n" + "=" * 70)
    print("DONE.")
    print(f"case folders found: {n_cases}   (expect ~1251)")
    print(f"segmentation files: {n_seg}   (MUST be ~1251, not 0)")
    if root and n_cases and n_seg:
        print("\nThis looks correct. Set this line in configs/brats2023.yaml:\n")
        print(f'  root: {root.as_posix()}')
    elif root and n_seg == 0:
        print("\nWARNING: no segmentation (-seg) files found — this would be the unlabelled "
              "validation set, unusable for training. Re-check the source.")
    else:
        print("\nCould not locate BraTS-GLI-* case folders automatically; look under:", path)
    print("=" * 70)


if __name__ == "__main__":
    main()
