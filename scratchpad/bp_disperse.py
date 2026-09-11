"""R-106 intervention test #1: does enable_hunger_dispersal ease the temperate PULL packing?

The reach/pull diagnosis (Addendum 77): temperate short adults sit next to reachable empty food but stay put
(PULL). `enable_hunger_dispersal` (built, default-OFF) breaks a settled agent's residence pin when its reserve
falls below `hunger_flee_reserve_frac` (0.35), so its IFD drive can take the better cell one stride away — the
exact PULL-breaker. This tests turning it ON, paired OFF/ON per world, watching e0 AND density AND the packing
metrics together (a disperse rule could just relocate the packing, or trade density for e0 like emigration did).

Canon, biome_seasonality ON, 600 agents; period life table over steps DFROM..end (transient excluded).
"""
import os
import sys
import numpy as np

ROOT = r"C:\Users\syatom\Projects\SiC Games"
sys.path.insert(0, os.path.join(ROOT, "scratchpad"))
from bp_savanna_probe import build, runconfig

BURN_FIELD = 75000.0
STEPS = int(os.environ.get("D_STEPS", "800"))
DFROM = int(os.environ.get("D_DFROM", "400"))


def run_one(clim, world_seed, agent_seed, disperse):
    canon = dict(runconfig.load()["DemographyConfig"])
    if disperse:
        canon["enable_hunger_dispersal"] = True
    w = build(canon, world_seed, agent_seed, clim=clim)
    base = w._harvest_field._base
    E0 = getattr(base, "_base_E", base._E)
    anchor_persons = float(getattr(base, "ceiling", (E0 / BURN_FIELD).sum()))
    land = [(x, y) for y in range(w._harvest_field.height) for x in range(w._harvest_field.width) if E0[y, x] > 0]
    ppl = E0 / BURN_FIELD

    snap = None
    for t in range(STEPS):
        w.step()
        if not w.agent_list:
            break
        if t == DFROM:
            snap = w.raw_demographic_counters()
    lt = w.life_table(since=snap) if snap else w.life_table()
    occ = {}
    for a in w.agent_list:
        occ[a.pos] = occ.get(a.pos, 0) + 1
    fills = [n / ppl[y, x] for (x, y), n in occ.items() if ppl[y, x] > 1e-6]
    return dict(
        pop=len(w.agent_list), density_ratio=len(w.agent_list) / max(anchor_persons, 1e-9),
        e0=lt["e0"], surv_to_15=lt["surv_to_15"], starv_share=lt.get("starv_share", float("nan")),
        spatial_use=len(occ) / max(len(land), 1),
        fill_median=float(np.median(fills)) if fills else 0.0)


def paired(vals):
    v = np.array([x for x in vals if np.isfinite(x)], float)
    if len(v) < 2:
        return (float(v.mean()) if len(v) else float("nan"), float("nan"))
    return float(v.mean()), float(v.std(ddof=1) / np.sqrt(len(v)))


def main():
    biomes = os.environ.get("D_BIOMES", "temperate,savanna").split(",")
    worlds = [int(x) for x in os.environ.get("D_WORLDS", "0,1,2").split(",")]
    agents = [int(x) for x in os.environ.get("D_AGENTS", "0").split(",")]
    print(f"HUNGER-DISPERSAL TEST | canon OFF vs enable_hunger_dispersal ON | {STEPS} steps | "
          f"period LT from {DFROM} | worlds {worlds} x agents {agents}", flush=True)
    keys = ["e0", "surv_to_15", "density_ratio", "spatial_use", "fill_median", "pop"]
    for clim in biomes:
        off_rows, on_rows = [], []
        for ws in worlds:
            for as_ in agents:
                off = run_one(clim, ws, as_, disperse=False)
                on = run_one(clim, ws, as_, disperse=True)
                off_rows.append(off); on_rows.append(on)
                print(f"  {clim} w{ws}a{as_}: e0 {off['e0']:.1f}->{on['e0']:.1f} "
                      f"surv15 {off['surv_to_15']:.2f}->{on['surv_to_15']:.2f} "
                      f"dens {off['density_ratio']:.3f}->{on['density_ratio']:.3f} "
                      f"spatial {off['spatial_use']:.2f}->{on['spatial_use']:.2f} "
                      f"pop {off['pop']}->{on['pop']}", flush=True)
        print(f"  === {clim} PAIRED ON-OFF over {len(off_rows)} worlds ===")
        for k in keys:
            d = [on_rows[i][k] - off_rows[i][k] for i in range(len(off_rows))]
            mo, _ = paired([r[k] for r in off_rows]); mn, _ = paired([r[k] for r in on_rows])
            md, sd = paired(d)
            z = (md / sd) if sd and sd > 0 else float("nan")
            print(f"    {k:14s} OFF {mo:.3f} -> ON {mn:.3f} | delta {md:+.3f} +/- {sd:.3f} (z={z:.1f})")


if __name__ == "__main__":
    main()
