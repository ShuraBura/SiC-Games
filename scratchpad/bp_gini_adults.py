"""R-106 marker audit — #14 material_gini STATISTIC check on the ADOPTED canon (Add.87).

The marker computes the material Gini over the WHOLE population (children included, who hold ~0). BHM 2009's 0.36 is
AGE-ADJUSTED over wealth-holders (adults). Children as zero-holders INFLATE a Gini, so the model's raw all-ages Gini
> its adult-only Gini. Add.87 calibrated the RAW ALL-AGES figure to 0.363. This checks whether the ADULT-ONLY (the
BHM-comparable) figure is still ~0.36 or well below it (which would mean the adoption over-concentrated to hit the
wrong statistic). Reports all-ages vs adults-only material Gini on the adopted canon, both biomes.
"""
import os
import sys
import numpy as np

ROOT = r"C:\Users\syatom\Projects\SiC Games"
sys.path.insert(0, os.path.join(ROOT, "scratchpad"))
from bp_savanna_probe import build, runconfig
from bp_gini import gini

STEPS = int(os.environ.get("C_STEPS", "800"))
ADULT_MO = 15.0 * 12.0


def run_one(clim, ws):
    canon = dict(runconfig.load()["DemographyConfig"])
    w = build(canon, ws, 0, clim=clim)
    for _ in range(STEPS):
        w.step()
        if not w.agent_list:
            break
    pop = w.agent_list
    mat_all = [getattr(a, "material", 0.0) for a in pop]
    mat_ad = [getattr(a, "material", 0.0) for a in pop if a.age >= ADULT_MO]
    frac_child = sum(1 for a in pop if a.age < ADULT_MO) / len(pop)
    # fraction of ADULTS holding zero material (zero-holders also inflate the adult Gini)
    zero_ad = sum(1 for m in mat_ad if m <= 0.0) / max(len(mat_ad), 1)
    return gini(mat_all), gini(mat_ad), frac_child, zero_ad


def ms(v):
    v = np.array(v, float)
    return v.mean(), (v.std(ddof=1) / np.sqrt(len(v)) if len(v) > 1 else 0.0)


def main():
    worlds = [int(x) for x in os.environ.get("C_WORLDS", "0,1,2").split(",")]
    biomes = os.environ.get("C_BIOMES", "temperate,savanna").split(",")
    print(f"#14 MATERIAL GINI STATISTIC CHECK | ADOPTED canon | {STEPS} steps | worlds {worlds} | BHM 0.36 "
          f"(age-adjusted adults)", flush=True)
    for clim in biomes:
        rows = [run_one(clim, ws) for ws in worlds]
        ga, gae = ms([r[0] for r in rows])
        gd, gde = ms([r[1] for r in rows])
        fc, _ = ms([r[2] for r in rows])
        za, _ = ms([r[3] for r in rows])
        print(f"  {clim:9s} | ALL-AGES gini {ga:.3f}+/-{gae:.3f} (the marker, calibrated to 0.36) | "
              f"ADULTS-ONLY gini {gd:.3f}+/-{gde:.3f} (BHM-comparable) | frac_child {fc:.2f}  adult zero-holders {za:.0%}",
              flush=True)


if __name__ == "__main__":
    main()
