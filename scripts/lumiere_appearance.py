"""Mask-INDEPENDENT, image-level retest of H4: does inter-scan APPEARANCE SHIFT predict
error DECORRELATION between the two tools?

Earlier (lumiere_validate.py) a mask-DEPENDENT CE-texture proxy was NULL (AUC 0.509).
This version uses the DeepBraTumIA atlas images, which are all in the SAME MNI space
across a patient's timepoints, so consecutive scans are spatially aligned and we can
measure how much the WHOLE BRAIN's appearance changed between t and t+1 — no tumour mask
involved. Appearance-shift metrics per consecutive pair (on CT1 and FLAIR, within the
shared brain region): SSIM (lower = more change), histogram Wasserstein distance, and
mean absolute normalised-intensity difference.

Target (the decorrelation signal), per consecutive interval with both tools >=1 mL at both
ends: direction disagreement = the two tools disagree on whether enhancing volume grew or
shrank. H4 predicts appearance shift is HIGHER when the tools decorrelate.

Writes outputs/lumiere/appearance.json. Honest: a null here is a valid result and simply
means the mechanism is still unexplained.
"""
import os, csv, json, zipfile, tempfile, shutil, math
from collections import defaultdict
import sys
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from lumiere_strengthen import load_vol, week, DBT, HG, NADIR_FLOOR

import nibabel as nib
from scipy.stats import wasserstein_distance, spearmanr
from skimage.metrics import structural_similarity as ssim

ROOT = os.path.join(os.path.dirname(__file__), "..")
ZIP = os.path.join(ROOT, "data", "lumiere", "Imaging-v202211.zip")
OUT = os.path.join(ROOT, "outputs", "lumiere")
SUB = "DeepBraTumIA-segmentation/atlas/skull_strip/"
SEQS = {"ct1": "ct1_skull_strip", "flair": "flair_skull_strip"}


def auroc(scores, labels):
    pos = [s for s, l in zip(scores, labels) if l == 1]
    neg = [s for s, l in zip(scores, labels) if l == 0]
    if not pos or not neg:
        return None
    gt = eq = 0
    for a in pos:
        for b in neg:
            if a > b: gt += 1
            elif a == b: eq += 1
    return (gt + 0.5 * eq) / (len(pos) * len(neg))


def load_vol_img(z, tp, seq, tmp):
    mpath = f"{tp}/{SUB}{SEQS[seq]}.nii.gz"
    dst = os.path.join(tmp, os.path.basename(mpath))
    with z.open(mpath) as src, open(dst, "wb") as f:
        shutil.copyfileobj(src, f)
    arr = np.asarray(nib.load(dst).get_fdata(), dtype=np.float32)
    return arr


def norm(a, mask):
    v = a[mask]
    m, s = v.mean(), v.std() + 1e-6
    return (a - m) / s


def appearance_pair(z, tp0, tp1, tmp):
    """Return appearance-shift metrics between two aligned atlas scans, or None."""
    feats = {}
    for seq in SEQS:
        try:
            a0 = load_vol_img(z, tp0, seq, tmp); a1 = load_vol_img(z, tp1, seq, tmp)
        except KeyError:
            return None
        if a0.shape != a1.shape:
            return None
        mask = (a0 != 0) & (a1 != 0)
        if mask.sum() < 1000:
            return None
        n0, n1 = norm(a0, mask), norm(a1, mask)
        dr = float(max(n0[mask].max(), n1[mask].max()) - min(n0[mask].min(), n1[mask].min()))
        feats[f"{seq}_ssim"] = float(ssim(n0 * mask, n1 * mask, data_range=dr))
        v0 = n0[mask]; v1 = n1[mask]
        # subsample for the Wasserstein distance (speed)
        idx = np.random.default_rng(0).choice(v0.size, size=min(20000, v0.size), replace=False)
        feats[f"{seq}_wass"] = float(wasserstein_distance(v0[idx], v1[idx]))
        feats[f"{seq}_mad"] = float(np.abs(v1 - v0).mean())
    return feats


def main():
    vd = load_vol(DBT); vh = load_vol(HG)
    z = zipfile.ZipFile(ZIP)
    members = set(z.namelist())

    # patient -> ordered post-op timepoints that have both tools' CE volume and atlas CT1+FLAIR
    byp = defaultdict(list)
    for (p, tp) in sorted(set(vd) & set(vh)):
        w = week(tp)
        full = f"Imaging/{p}/{tp}"
        has_img = all(f"{full}/{SUB}{SEQS[s]}.nii.gz" in members for s in SEQS)
        if w is not None and has_img:
            byp[p].append((w, tp))

    rows = []
    tmp = tempfile.mkdtemp()
    try:
        for p, seq in byp.items():
            seq.sort()
            for (w0, tp0), (w1, tp1) in zip(seq, seq[1:]):
                v0d, v1d = vd[(p, tp0)], vd[(p, tp1)]
                v0h, v1h = vh[(p, tp0)], vh[(p, tp1)]
                if min(v0d, v1d, v0h, v1h) < 1000:          # >=1 mL both tools both ends
                    continue
                feats = appearance_pair(z, f"Imaging/{p}/{tp0}", f"Imaging/{p}/{tp1}", tmp)
                if feats is None:
                    continue
                dir_dis = int(((v1d - v0d) > 0) != ((v1h - v0h) > 0))
                mag_dis = abs(math.log2((v1d / v0d) / (v1h / v0h)))
                rows.append(dict(patient=p, tp0=tp0, tp1=tp1, dir_disagree=dir_dis,
                                 mag_disagree=mag_dis, **feats))
        for f in os.listdir(tmp):
            os.remove(os.path.join(tmp, f))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    res = {"n_intervals": len(rows)}
    print(f"intervals (>=1 mL both tools both ends, with atlas images): {len(rows)}")
    if len(rows) < 10:
        print("too few intervals for a meaningful test.")
        json.dump(res, open(os.path.join(OUT, "appearance.json"), "w"), indent=2); return

    dirlab = [r["dir_disagree"] for r in rows]
    print(f"direction-disagreement rate: {sum(dirlab)/len(dirlab):.1%}")
    res["dir_disagree_rate"] = sum(dirlab) / len(dirlab)
    metrics = [k for k in rows[0] if k.endswith(("_ssim", "_wass", "_mad"))]
    res["H4_image_level"] = {}
    print("\nDoes appearance shift predict DIRECTION disagreement (decorrelation)?")
    for m in metrics:
        xs = [r[m] for r in rows]
        # SSIM is inverted (higher SSIM = less change), so predict disagree with -ssim
        score = [-x for x in xs] if m.endswith("_ssim") else xs
        au = auroc(score, dirlab)
        rho, pv = spearmanr([r[m] for r in rows], [r["mag_disagree"] for r in rows])
        res["H4_image_level"][m] = dict(auroc_dir=au, spearman_mag=float(rho), spearman_p=float(pv))
        print(f"   {m:12s} AUROC(dir-disagree)={None if au is None else round(au,3)}  "
              f"Spearman vs mag-disagree rho={rho:+.3f} (p={pv:.3f})")

    json.dump(res, open(os.path.join(OUT, "appearance.json"), "w"), indent=2)
    print("\nsaved -> outputs/lumiere/appearance.json")


if __name__ == "__main__":
    main()
