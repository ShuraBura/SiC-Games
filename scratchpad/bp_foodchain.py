"""R-106 food-economy carrying-capacity diagnosis.

Question: on CANON, mean per-capita intake is abundant (3-5x burn) yet equilibrium density sits BELOW the
Tallavaara anchor (savanna ~46% of the density anchor). Where is the food lost, and what caps density below the
food ceiling?

Instruments the whole chain, per biome, on the low-noise panel (bp OFF = canonical), averaged over the final
year (12 steps) at equilibrium:

  anchor_kcal   = sum over patch land of the undepleted Tallavaara E (persons_per_cell * burn)   [the ceiling]
  delivered     = sum over cells of harvest_field.level()  [after seasonality + depletion]        -> SEASONALITY loss
  extracted     = sum over agents of _last_intake (= eta * forage-capped share)                   -> ACCESS loss
  density_ratio = pop / anchor_persons                                                            [the headline gap]

And the decisive food- vs non-food-bound test, at the last step:
  per occupied cell, occupancy n vs the cell's Tallavaara capacity persons_per_cell.
  If cells are packed to capacity -> food-bound. If n << capacity everywhere -> something else caps density.
Plus the death-cause split (starv vs senesc; senesc bundles the a2 density/disease/condition hazard) and mean
body condition (wealth/cap).
"""
import os
import sys
import numpy as np

ROOT = r"C:\Users\syatom\Projects\SiC Games"
sys.path.insert(0, os.path.join(ROOT, "scratchpad"))
from bp_savanna_probe import build, runconfig  # reuse the decoupled-seed builder + canon loader

BURN_FIELD = 75000.0          # the burn passed to NPPCapacityField in build() (E = persons_per_cell * this)
STEPS = int(os.environ.get("F_STEPS", "800"))
WIN = int(os.environ.get("F_WIN", "12"))         # final-year averaging window for the food-flow ratios
DFROM = int(os.environ.get("F_DFROM", "400"))    # death-cause accumulation window start


def anchor_persons_field(w):
    """Undepleted Tallavaara capacity per cell (persons) and its patch sum."""
    base = w._harvest_field._base
    E0 = getattr(base, "_base_E", base._E)        # undepleted ceiling flow (B=1)
    ppl = E0 / BURN_FIELD
    return ppl, float(getattr(base, "ceiling", ppl.sum()))


def run_one(clim, world_seed, agent_seed):
    canon = dict(runconfig.load()["DemographyConfig"])       # canonical, band provisioning OFF
    w = build(canon, world_seed, agent_seed, clim=clim)
    ppl, anchor_persons = anchor_persons_field(w)
    base = w._harvest_field._base
    E0 = getattr(base, "_base_E", base._E)
    anchor_kcal = float(E0.sum())                            # sum over the whole patch (occupied or not)
    land = [(x, y) for y in range(w._harvest_field.height) for x in range(w._harvest_field.width) if E0[y, x] > 0]

    d_starv = d_senesc = 0
    deliv = extr = 0.0
    nwin = 0
    for t in range(STEPS):
        w.step()
        if not w.agent_list:
            break
        if t >= DFROM:
            d_starv += getattr(w, "deaths_starv_this_step", 0)
            d_senesc += getattr(w, "deaths_senesc_this_step", 0)
        if t >= STEPS - WIN:
            hf = w._harvest_field
            deliv += sum(hf.level(x, y) for (x, y) in land)          # delivered this step (seasonal, depleted)
            extr += sum(getattr(a, "_last_intake", 0.0) for a in w.agent_list)  # extracted this step
            nwin += 1

    pop = len(w.agent_list)
    # occupancy vs capacity at the last step
    occ = {}
    for a in w.agent_list:
        occ[a.pos] = occ.get(a.pos, 0) + 1
    fills = []
    for (x, y), n in occ.items():
        cap = ppl[y, x]
        if cap > 1e-6:
            fills.append(n / cap)
    fills = np.array(fills) if fills else np.array([0.0])
    burn = w._burn
    cond = np.array([a.wealth / (w._reserve_full * a.reserve_scale()) for a in w.agent_list])
    return dict(
        fills=fills, cond_arr=cond,
        pop=pop, anchor_persons=anchor_persons, density_ratio=pop / max(anchor_persons, 1e-9),
        seasonality=(deliv / nwin) / anchor_kcal if nwin else float("nan"),   # delivered/anchor (annual mean)
        extract_of_anchor=(extr / nwin) / anchor_kcal if nwin else float("nan"),
        extract_of_delivered=(extr / deliv) if deliv else float("nan"),
        cells_occupied=len(occ), cells_land=len(land), spatial_use=len(occ) / max(len(land), 1),
        fill_mean=float(fills.mean()), fill_median=float(np.median(fills)), fill_p90=float(np.percentile(fills, 90)),
        d_starv=d_starv, d_senesc=d_senesc, starv_frac=d_starv / max(d_starv + d_senesc, 1),
        cond_mean=float(cond.mean()), cond_median=float(np.median(cond)))


def main():
    biomes = os.environ.get("F_BIOMES", "temperate,savanna").split(",")
    worlds = [int(x) for x in os.environ.get("F_WORLDS", "0,1,2").split(",")]
    agents = [int(x) for x in os.environ.get("F_AGENTS", "0").split(",")]
    print(f"FOOD-CHAIN DIAGNOSIS | canon (bp OFF) | {STEPS} steps | final-year window {WIN} | "
          f"worlds {worlds} x agents {agents}", flush=True)
    keys = ["density_ratio", "seasonality", "extract_of_anchor", "extract_of_delivered", "spatial_use",
            "fill_mean", "fill_median", "fill_p90", "starv_frac", "cond_mean"]
    for clim in biomes:
        rows = []
        for ws in worlds:
            for as_ in agents:
                r = run_one(clim, ws, as_)
                rows.append(r)
                print(f"  {clim} w{ws}a{as_}: pop {r['pop']:.0f}/{r['anchor_persons']:.0f} "
                      f"dens {r['density_ratio']:.2f} | seas {r['seasonality']:.2f} "
                      f"extr/anch {r['extract_of_anchor']:.3f} extr/deliv {r['extract_of_delivered']:.2f} | "
                      f"spatial {r['spatial_use']:.2f} fill(med {r['fill_median']:.2f} p90 {r['fill_p90']:.2f}) | "
                      f"starv% {r['starv_frac']:.2f} cond {r['cond_mean']:.2f}", flush=True)
        print(f"  === {clim} MEAN over {len(rows)} cells ===")
        summ = {}
        for k in keys:
            v = np.array([r[k] for r in rows], float)
            summ[k] = (float(v.mean()), float(v.std(ddof=1) / np.sqrt(len(v))))
            print(f"    {k:22s} {v.mean():.3f} +/- {v.std(ddof=1)/np.sqrt(len(v)):.3f}")
        if os.environ.get("F_DUMP"):
            fills = np.concatenate([r["fills"] for r in rows])
            conds = np.concatenate([r["cond_arr"] for r in rows])
            np.savez(f"{os.environ['F_DUMP']}_{clim}.npz", fills=fills, conds=conds,
                     **{k: np.array(summ[k]) for k in keys})
            print(f"    [dumped {os.environ['F_DUMP']}_{clim}.npz  fills n={len(fills)}]")


if __name__ == "__main__":
    main()
