"""R-106 tier-5 INSTRUMENT CHECK: Hill 2011's 28.2 is the MEAN EXPERIENCED band size in ADULTS (person-weighted),
NOT the median over band_ids. The marker scores band_med_adults (median over bands) = ~10.5. On the model's
bimodal band distribution these are very different. This computes the actually-comparable statistic.

For each individual i, A(i) = number of ADULTS in i's band. Hill's quantity = mean_i A(i)  (person-weighted).
Equivalently sum_b (adults_b * size_b) / sum_b size_b. Compared here against 28.2, alongside the median-over-bands
(current marker) and the mean-over-bands, on BOTH biomes. Canon, low-noise 3-world panel.
"""
import os
import sys
import statistics as st
import numpy as np

ROOT = r"C:\Users\syatom\Projects\SiC Games"
sys.path.insert(0, os.path.join(ROOT, "scratchpad"))
from bp_savanna_probe import build, runconfig

STEPS = int(os.environ.get("C_STEPS", "800"))
ADULT_MO = 15.0 * 12.0


def stats(w):
    groups = {}
    for a in w.agent_list:
        groups.setdefault(a._group.band_id, []).append(a)
    adults = [sum(1 for a in g if a.age >= ADULT_MO) for g in groups.values()]
    sizes = [len(g) for g in groups.values()]
    med_ad = st.median(adults) if adults else 0.0          # CURRENT MARKER: median over bands, adults
    mean_ad = float(np.mean(adults)) if adults else 0.0    # mean over bands, adults
    # MEAN EXPERIENCED adults (person-weighted): sum(adults_b * size_b) / sum(size_b)
    tot_people = sum(sizes)
    exp_ad = sum(a_b * n_b for a_b, n_b in zip(adults, sizes)) / tot_people if tot_people else 0.0
    # also experienced TOTAL size (person-weighted total members), for reference
    exp_tot = sum(n_b * n_b for n_b in sizes) / tot_people if tot_people else 0.0
    return med_ad, mean_ad, exp_ad, exp_tot, len(groups)


def run_one(clim, ws):
    canon = dict(runconfig.load()["DemographyConfig"])
    w = build(canon, ws, 0, clim=clim)
    for _ in range(STEPS):
        w.step()
        if not w.agent_list:
            break
    return stats(w)


def ms(v):
    v = np.array(v, float)
    return v.mean(), (v.std(ddof=1) / np.sqrt(len(v)) if len(v) > 1 else 0.0)


def main():
    worlds = [int(x) for x in os.environ.get("C_WORLDS", "0,1,2").split(",")]
    biomes = os.environ.get("C_BIOMES", "temperate,savanna").split(",")
    print(f"BAND-SIZE INSTRUMENT CHECK | canon | {STEPS} steps | worlds {worlds} | Hill 'mean experienced' = 28.2 ADULTS",
          flush=True)
    for clim in biomes:
        rows = [run_one(clim, ws) for ws in worlds]
        med, med_e = ms([r[0] for r in rows])
        mean, _ = ms([r[1] for r in rows])
        exp, exp_e = ms([r[2] for r in rows])
        expt, _ = ms([r[3] for r in rows])
        hit = "  <== ~28.2!" if abs(exp - 28.2) <= 4 else ""
        print(f"  {clim:9s} | median-over-bands adults {med:.1f}+/-{med_e:.1f} (CURRENT MARKER) | "
              f"mean-over-bands adults {mean:.1f} | MEAN EXPERIENCED adults {exp:.1f}+/-{exp_e:.1f}{hit} "
              f"(Hill 28.2) | experienced total {expt:.1f}", flush=True)


if __name__ == "__main__":
    main()
