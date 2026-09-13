"""R-106 tier-10 wealth/material Gini diagnosis: within-band vs between-band decomposition.

Tier-10 marker #14: material_gini (whole pop) = 0.162 vs BHM 2009 material Gini 0.36. The R-103 thesis: within-
band material is flattened by sharing, so inequality must live BETWEEN bands. This decomposes the total material
Gini into within-band and between-band components (and the same for cred, to connect to the R-103 between-band
cred signal that climbs to ~0.33), and reproduces the whole-pop marker as validation.

Questions:
  - is the whole-pop material Gini (0.162) low because within-band is flat (sharing) AND between-band is weak?
  - does cred concentrate (between-band ~0.33) while material does NOT follow (corr_cred_material weak)?
    -> if so the miss is the status->material coupling (tier-10/11 capture), not the band structure.

Canon, biome_seasonality ON, 600 agents, low-noise panel. Read-only.
"""
import os
import sys
import numpy as np

ROOT = r"C:\Users\syatom\Projects\SiC Games"
sys.path.insert(0, os.path.join(ROOT, "scratchpad"))
from bp_savanna_probe import build, runconfig

STEPS = int(os.environ.get("G_STEPS", "800"))


def gini(xs):
    a = np.sort(np.asarray([v for v in xs if v is not None], dtype=float))
    n = a.size
    if n < 2 or a.sum() <= 0:
        return 0.0
    return float((2.0 * np.sum(np.arange(1, n + 1) * a)) / (n * a.sum()) - (n + 1.0) / n)


def top_share(xs, q=0.10):
    a = np.sort(np.asarray(xs, dtype=float))[::-1]
    if a.sum() <= 0:
        return 0.0
    k = max(1, int(round(len(a) * q)))
    return float(a[:k].sum() / a.sum())


def decompose(vals_by_band):
    """within = size-weighted mean of per-band Gini; between = Gini over band means (weighted by size via
    a repeated-mean expansion). Also the simple Gini over band totals."""
    sizes = [len(v) for v in vals_by_band]
    within = sum(s * gini(v) for s, v in zip(sizes, vals_by_band)) / max(sum(sizes), 1)
    band_means = [np.mean(v) if len(v) else 0.0 for v in vals_by_band]
    # between-band Gini on the per-capita band means, weighted by band size (expand each mean by its size)
    expanded = np.repeat(band_means, sizes) if sizes else np.array([])
    between = gini(expanded)
    between_totals = gini([np.sum(v) for v in vals_by_band])
    return within, between, between_totals


def run_one(clim, world_seed, agent_seed):
    canon = dict(runconfig.load()["DemographyConfig"])
    w = build(canon, world_seed, agent_seed, clim=clim)
    for _ in range(STEPS):
        w.step()
        if not w.agent_list:
            break
    pop = w.agent_list
    mat = [getattr(a, "material", 0.0) for a in pop]
    cred = [getattr(a, "cred", 1.0) for a in pop]
    # group by band
    bands = {}
    for a in pop:
        bands.setdefault(a._group.band_id, []).append(a)
    mat_by_band = [[getattr(a, "material", 0.0) for a in g] for g in bands.values()]
    cred_by_band = [[getattr(a, "cred", 1.0) for a in g] for g in bands.values()]
    mw, mb, mbt = decompose(mat_by_band)
    cw, cb, cbt = decompose(cred_by_band)
    # marker validation via the model's own demography()
    dm = w.demography()
    return dict(
        pop=len(pop), n_bands=len(bands),
        mat_gini=gini(mat), mat_gini_model=dm.get("material_gini", float("nan")),
        mat_mean=float(np.mean(mat)), mat_top10=top_share(mat), mat_frac_pos=float(np.mean(np.array(mat) > 0)),
        mat_within=mw, mat_between=mb, mat_between_tot=mbt,
        cred_gini=gini(cred), cred_within=cw, cred_between=cb,
        corr_cred_mat=float(np.corrcoef(cred, mat)[0, 1]) if np.std(mat) > 0 else float("nan"))


def ms(v):
    v = np.array([x for x in v if x == x], float)
    return (v.mean(), v.std(ddof=1) / np.sqrt(len(v))) if len(v) > 1 else (float(v.mean()) if len(v) else float("nan"), 0.0)


def main():
    biomes = os.environ.get("G_BIOMES", "temperate,savanna").split(",")
    worlds = [int(x) for x in os.environ.get("G_WORLDS", "0,1,2").split(",")]
    agents = [int(x) for x in os.environ.get("G_AGENTS", "0").split(",")]
    print(f"MATERIAL-GINI DIAGNOSIS | canon | {STEPS} steps | worlds {worlds} x agents {agents} | "
          f"anchor BHM material Gini 0.36 (whole-pop 0.25)", flush=True)
    for clim in biomes:
        rows = []
        for ws in worlds:
            for as_ in agents:
                r = run_one(clim, ws, as_)
                rows.append(r)
                print(f"  {clim} w{ws}a{as_}: mat_gini {r['mat_gini']:.3f} (model {r['mat_gini_model']:.3f}) "
                      f"within {r['mat_within']:.3f} between {r['mat_between']:.3f} | mat_mean {r['mat_mean']:.1f} "
                      f"top10 {r['mat_top10']:.2f} frac>0 {r['mat_frac_pos']:.2f} | "
                      f"cred_gini {r['cred_gini']:.3f} cred_between {r['cred_between']:.3f} "
                      f"corr(cred,mat) {r['corr_cred_mat']:.2f} | n_bands {r['n_bands']}", flush=True)
        print(f"  === {clim} MEAN ===")
        for k, lab in [("mat_gini", "material Gini (#14, vs 0.36)"), ("mat_within", "  within-band"),
                       ("mat_between", "  between-band"), ("mat_top10", "material top-10% share"),
                       ("mat_frac_pos", "frac holding material"), ("corr_cred_mat", "corr(cred,material)"),
                       ("cred_gini", "cred Gini (whole-pop)"), ("cred_between", "cred Gini BETWEEN-band (R-103)")]:
            m, e = ms([r[k] for r in rows])
            print(f"    {lab:32s} {m:6.3f} +/- {e:5.3f}")


if __name__ == "__main__":
    main()
