"""Run OUR BraTS-trained segmenter as an architecturally-independent THIRD voter on
every LUMIERE timepoint, label-free, with MC-dropout.

LUMIERE ships two tools' segmentations (DeepBraTumIA, HD-GLIO-AUTO); this adds a third,
independent enhancing-tumour (ET) volume per timepoint so we can test whether a 3-way
agreement sharpens the reference-free reliability flag.

Input per timepoint = DeepBraTumIA atlas skull-stripped quartet (1 mm isotropic MNI,
skull-stripped and co-registered — the closest match to the model's BraTS training
space; HD-GLIO's registered images are 6 mm-thick anisotropic and unusable here).
Files are streamed straight from Imaging-v202211.zip (only ~4 small images per case),
so the 32 GB archive is never fully extracted.

Resumable: timepoints already in the output CSV are skipped.

    python scripts/longitudinal/lumiere_thirdvoter.py
"""
import os, sys, zipfile, tempfile, shutil, time
from pathlib import Path
import numpy as np, pandas as pd, torch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from monai import transforms as mt           # noqa: E402
from brainrisk.model import build_unet, stochastic_predict  # noqa: E402

ZIP = ROOT / "data/lumiere/Imaging-v202211.zip"
CKPT = ROOT / "outputs/seg_model_brats23/best.pt"
OUT = ROOT / "outputs/lumiere/thirdvoter_volumes.csv"
SEG = dict(channels=[16, 32, 64, 128, 256], strides=[2, 2, 2, 2], num_res_units=2,
           dropout=0.1, roi_size=[128, 128, 128])
MC = 10
SUB = "DeepBraTumIA-segmentation/atlas/skull_strip/"
MODS = ["t1_skull_strip", "ct1_skull_strip", "t2_skull_strip", "flair_skull_strip"]  # -> t1,t1ce,t2,flair

TF = mt.Compose([
    mt.LoadImaged(keys=["image"], image_only=False),
    mt.EnsureChannelFirstd(keys=["image"]),
    mt.EnsureTyped(keys=["image"]),
    mt.Orientationd(keys=["image"], axcodes="RAS"),
    mt.NormalizeIntensityd(keys="image", nonzero=True, channel_wise=True),
])


def discover(z):
    """Return {(patient, week): [4 zip member paths]} for timepoints with the full quartet."""
    members = set(z.namelist())
    cases = {}
    # a timepoint is Imaging/Patient-XXX/week-YYY/
    tps = sorted({"/".join(n.split("/")[:3]) for n in members
                  if n.startswith("Imaging/Patient-") and n.count("/") >= 3})
    for tp in tps:
        parts = tp.split("/")
        if len(parts) < 3:
            continue
        patient, week = parts[1], parts[2]
        need = [f"{tp}/{SUB}{m}.nii.gz" for m in MODS]
        if all(n in members for n in need):
            cases[(patient, week)] = need
    return cases


def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = build_unet(SEG).to(device)
    model.load_state_dict(torch.load(CKPT, map_location=device))
    OUT.parent.mkdir(parents=True, exist_ok=True)

    done = set()
    if OUT.exists():
        d = pd.read_csv(OUT)
        done = set(zip(d["patient"], d["week"]))

    z = zipfile.ZipFile(ZIP)
    cases = discover(z)
    todo = [(k, v) for k, v in cases.items() if k not in done]
    print(f"{len(cases)} timepoints with quartet; {len(done)} done; {len(todo)} to run -> {OUT}", flush=True)

    for (patient, week), members in todo:
        t0 = time.time()
        tmp = tempfile.mkdtemp()
        try:
            imgs = []
            for mpath in members:
                dst = os.path.join(tmp, os.path.basename(mpath))
                with z.open(mpath) as src, open(dst, "wb") as f:
                    shutil.copyfileobj(src, f)
                imgs.append(dst)
            data = TF({"image": imgs})
            image = data["image"].unsqueeze(0).to(device)
            affine = np.asarray(data["image"].affine)
            spacing = tuple(float(v) for v in np.sqrt((affine[:3, :3] ** 2).sum(0)))
            voxel_ml = float(np.prod(spacing)) / 1000.0
            samp = stochastic_predict(model, image, MC, tuple(SEG["roi_size"]), 2, 0.5, True, True)
            et = samp[:, 2]
            per = np.array([float((et[i] > 0.5).sum() * voxel_ml) for i in range(MC)])
            row = dict(patient=patient, week=week, voxel_ml=round(voxel_ml, 6),
                       et_ml=round(float(per.mean()), 4), et_std=round(float(per.std()), 4),
                       et_meanmask_ml=round(float((et.mean(0) > 0.5).sum() * voxel_ml), 4),
                       dt_s=round(time.time() - t0, 1))
            pd.DataFrame([row]).to_csv(OUT, mode="a", header=not OUT.exists(), index=False)
            print(f"  {patient}/{week}: ET {row['et_ml']:.2f} mL (std {row['et_std']:.2f}) "
                  f"[{row['dt_s']}s]", flush=True)
        except Exception as e:
            print(f"  !! {patient}/{week} FAILED: {type(e).__name__}: {e}", flush=True)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    print("done.", flush=True)


if __name__ == "__main__":
    main()
