"""DE-RISK PROTOTYPE for the coupled-stochastic-inference reliability method.

Central question (make-or-break): if we run OUR MC-dropout segmenter on two
registered LUMIERE timepoints with the SAME dropout realizations (coupled /
common random numbers), do the two scans' stochastic errors become measurably
CORRELATED -- so that they partially cancel in the volume CHANGE?

  Var(dV) = Var(V_a) + Var(V_b) - 2*Cov(V_a, V_b)

If Cov > 0 under coupling AND rho VARIES across pairs, then rho is a real,
reference-free, per-decision signal of change reliability -> method lives.
If Cov ~ 0 everywhere, coupling buys nothing. If rho ~ 1 everywhere, it cannot
discriminate. We want intermediate + variable.

Mechanism: the dropout mask is drawn inside each forward pass. Setting
torch.manual_seed(seed) immediately before sample i at BOTH timepoints makes the
SAME units drop at both scans -> the same "model instance" segments both -> any
instance-specific over/under-segmentation tendency hits both scans together
(positive Cov). Both LUMIERE atlas timepoints are 182x218x182, so the sliding
window / dropout RNG consumption is identical by construction.

Runs on a handful of patient pairs only (prototype). Writes JSON + prints.

    python scripts/longitudinal/lumiere_coupled_prototype.py
"""
import os, sys, json, zipfile, tempfile, shutil, time
from collections import defaultdict
from pathlib import Path
import numpy as np, torch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from monai import transforms as mt           # noqa: E402
from brainrisk.model import build_unet, stochastic_predict  # noqa: E402

ZIP = ROOT / "data/lumiere/Imaging-v202211.zip"
CKPT = ROOT / "outputs/seg_model_brats23/best.pt"
OUT = ROOT / "outputs/lumiere/coupled_prototype.json"
SEG = dict(channels=[16, 32, 64, 128, 256], strides=[2, 2, 2, 2], num_res_units=2,
           dropout=0.1, roi_size=[128, 128, 128])
SUB = "DeepBraTumIA-segmentation/atlas/skull_strip/"
MODS = ["t1_skull_strip", "ct1_skull_strip", "t2_skull_strip", "flair_skull_strip"]
K = 12            # MC samples per scan
N_PATIENTS = 6    # prototype: first N patients with >=2 timepoints
MAX_PAIRS_PER_PATIENT = 2

TF = mt.Compose([
    mt.LoadImaged(keys=["image"], image_only=False),
    mt.EnsureChannelFirstd(keys=["image"]),
    mt.EnsureTyped(keys=["image"]),
    mt.Orientationd(keys=["image"], axcodes="RAS"),
    mt.NormalizeIntensityd(keys="image", nonzero=True, channel_wise=True),
])


def discover(z):
    members = set(z.namelist())
    tps = sorted({"/".join(n.split("/")[:3]) for n in members
                  if n.startswith("Imaging/Patient-") and n.count("/") >= 3})
    cases = {}
    for tp in tps:
        parts = tp.split("/")
        if len(parts) < 3:
            continue
        patient, week = parts[1], parts[2]
        need = [f"{tp}/{SUB}{m}.nii.gz" for m in MODS]
        if all(n in members for n in need):
            cases[(patient, week)] = need
    return cases


def load_image(z, members, device):
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
        return image, voxel_ml
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def et_volumes_seeded(model, image, voxel_ml, seeds, roi):
    """One ET-volume sample per seed; seed fixes the dropout realization."""
    vols = []
    for s in seeds:
        torch.manual_seed(int(s))
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(int(s))
        samp = stochastic_predict(model, image, 1, roi, 2, 0.5, tta_flips=False, amp=True)
        et = samp[0, 2]
        vols.append(float((et > 0.5).sum()) * voxel_ml)
    return np.array(vols)


def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = build_unet(SEG).to(device)
    model.load_state_dict(torch.load(CKPT, map_location=device))
    roi = tuple(SEG["roi_size"])

    z = zipfile.ZipFile(ZIP)
    cases = discover(z)
    by_patient = defaultdict(list)
    for (patient, week) in sorted(cases):
        by_patient[patient].append(week)

    pairs = []
    for patient in sorted(by_patient):
        weeks = by_patient[patient]
        if len(weeks) < 2:
            continue
        for a, b in list(zip(weeks, weeks[1:]))[:MAX_PAIRS_PER_PATIENT]:
            pairs.append((patient, a, b))
        if len({p for p, _, _ in pairs}) >= N_PATIENTS:
            break

    print(f"{len(cases)} timepoints; prototype on {len(pairs)} consecutive pairs "
          f"from {len({p for p,_,_ in pairs})} patients; K={K} MC samples.", flush=True)

    base = 1000
    results = []
    for (patient, wa, wb) in pairs:
        t0 = time.time()
        try:
            img_a, vml = load_image(z, cases[(patient, wa)], device)
            img_b, _ = load_image(z, cases[(patient, wb)], device)
            seeds = [base + i for i in range(K)]
            seeds_indep = [base + 500 + i for i in range(K)]  # different instances for B

            va = et_volumes_seeded(model, img_a, vml, seeds, roi)
            vb_coupled = et_volumes_seeded(model, img_b, vml, seeds, roi)        # SAME seeds
            vb_indep = et_volumes_seeded(model, img_b, vml, seeds_indep, roi)    # different seeds

            var_a = float(va.var())
            var_b = float(vb_coupled.var())
            cov = float(np.cov(va, vb_coupled)[0, 1])
            denom = np.sqrt(va.var() * vb_coupled.var())
            rho = float(cov / denom) if denom > 1e-9 else float("nan")

            d_coupled = va - vb_coupled
            d_indep = va - vb_indep
            var_dv_coupled = float(d_coupled.var())
            var_dv_indep = float(var_a + float(vb_indep.var()))  # independent -> no cov term
            observed_change = float(va.mean() - vb_coupled.mean())

            row = dict(patient=patient, week_a=wa, week_b=wb,
                       et_a=round(float(va.mean()), 3), et_b=round(float(vb_coupled.mean()), 3),
                       observed_change_ml=round(observed_change, 3),
                       sd_a=round(float(va.std()), 4), sd_b=round(float(vb_coupled.std()), 4),
                       rho=round(rho, 3), cov=round(cov, 4),
                       sd_dv_coupled=round(float(np.sqrt(max(var_dv_coupled, 0))), 4),
                       sd_dv_indep=round(float(np.sqrt(max(var_dv_indep, 0))), 4),
                       dt_s=round(time.time() - t0, 1))
            results.append(row)
            print(f"  {patient} {wa}->{wb}: dV={row['observed_change_ml']:+.2f} mL | "
                  f"rho={row['rho']:+.2f} | sd(dV) coupled {row['sd_dv_coupled']:.3f} "
                  f"vs indep {row['sd_dv_indep']:.3f} mL  [{row['dt_s']}s]", flush=True)
        except Exception as e:
            print(f"  !! {patient} {wa}->{wb} FAILED: {type(e).__name__}: {e}", flush=True)

    rhos = [r["rho"] for r in results if not np.isnan(r["rho"])]
    summary = dict(
        n_pairs=len(results),
        rho_median=round(float(np.median(rhos)), 3) if rhos else None,
        rho_min=round(float(np.min(rhos)), 3) if rhos else None,
        rho_max=round(float(np.max(rhos)), 3) if rhos else None,
        mean_sd_dv_coupled=round(float(np.mean([r["sd_dv_coupled"] for r in results])), 4) if results else None,
        mean_sd_dv_indep=round(float(np.mean([r["sd_dv_indep"] for r in results])), 4) if results else None,
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(dict(summary=summary, pairs=results), indent=2))
    print("\nSUMMARY:", json.dumps(summary, indent=2), flush=True)
    print(f"\nVerdict hint: method LIVES if rho is clearly >0 (coupled sd(dV) < indep) "
          f"AND rho VARIES across pairs (rho_max-rho_min sizeable). Written -> {OUT}", flush=True)


if __name__ == "__main__":
    main()
