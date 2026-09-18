"""R-106 #11 status->RS re-measure + audit. Anchor (von Rueden & Jaeggi 2016, PDF-read): corr(male status,
offspring) via the FERTILITY channel; cross-system r~0.19 (polygyny-inflated), MONOGAMOUS r~0.15, and a
monogamy-dominant model 'SHOULD sit ~0.13-0.15'. The model's polygyny is now corrected (Add.91, ~0.025), so the old
+0.170 (a 6x-polygyny artefact, R-77) should be gone.

The marker `status_rs_r` = corr(prowess, _n_fathered) over ALL males age>=15 — but that CONFLATES AGE (old men have
both high accumulated prowess and high cumulative offspring; von Rueden controls for age). This reports:
  r_all     : the current marker (all repro-age males)
  r_mature  : males age>=40yr (more completed fertility, less young-zero dilution)
  r_partial : age-PARTIALLED corr (prowess vs offspring | age) — the cleanest age-controlled, von-Rueden-comparable
Current canon, full-length (800 steps), both biomes, 3-world panel.
"""
import os
import sys
import numpy as np

ROOT = r"C:\Users\syatom\Projects\SiC Games"
sys.path.insert(0, os.path.join(ROOT, "scratchpad"))
from bp_savanna_probe import build, runconfig

STEPS = 800
MEN_MO = 180.0


def pcorr(x, y):
    x = np.asarray(x, float); y = np.asarray(y, float)
    if len(x) < 3 or x.std() == 0 or y.std() == 0:
        return float("nan")
    return float(np.corrcoef(x, y)[0, 1])


def partial(x, y, z):
    """partial corr of x,y controlling z."""
    rxy, rxz, ryz = pcorr(x, y), pcorr(x, z), pcorr(y, z)
    d = ((1 - rxz ** 2) * (1 - ryz ** 2)) ** 0.5
    return (rxy - rxz * ryz) / d if d > 0 else float("nan")


def run_one(clim, ws):
    w = build(dict(runconfig.load()["DemographyConfig"]), ws, 0, clim=clim)
    for _ in range(STEPS):
        w.step()
        if not w.agent_list:
            break
    males = [a for a in w.agent_list if a.sex == "male" and a.age >= MEN_MO]
    pr = [getattr(a, "prowess", 1.0) for a in males]
    off = [float(getattr(a, "_n_fathered", 0)) for a in males]
    age = [a.age for a in males]
    mat = [(p, o, g) for p, o, g in zip(pr, off, age) if g >= 40 * 12]
    r_all = pcorr(pr, off)
    r_part = partial(pr, off, age)
    r_mat = pcorr([m[0] for m in mat], [m[1] for m in mat]) if len(mat) > 3 else float("nan")
    return r_all, r_mat, r_part, len(males), len(mat), float(np.mean(off)) if off else 0.0


def ms(v):
    v = np.array([x for x in v if x == x], float)
    return (v.mean(), v.std(ddof=1) / np.sqrt(len(v))) if len(v) > 1 else (float(v.mean()) if len(v) else float("nan"), 0.0)


for clim in ("temperate", "savanna"):
    rows = [run_one(clim, ws) for ws in (0, 1, 2)]
    ra, rae = ms([r[0] for r in rows]); rm, rme = ms([r[1] for r in rows]); rp, rpe = ms([r[2] for r in rows])
    nm = ms([r[3] for r in rows])[0]; nmat = ms([r[4] for r in rows])[0]; mo = ms([r[5] for r in rows])[0]
    print(f"== {clim.upper()} | anchor: monogamous r~0.15, cross-system 0.19; model should sit ~0.13-0.15 ==", flush=True)
    print(f"  r_all (marker, all repro males) {ra:+.3f}+/-{rae:.3f}   r_mature (age>=40) {rm:+.3f}+/-{rme:.3f}   "
          f"r_partial (age-controlled) {rp:+.3f}+/-{rpe:.3f}", flush=True)
    print(f"  n_males {nm:.0f}  n_mature {nmat:.0f}  mean_offspring {mo:.2f}", flush=True)
