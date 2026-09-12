"""R-106 tier-3 age-structure diagnosis: is the young pyramid fertility (fixable) or turnover (packing)?

Anchors (Hill & Hurtado): frac_child in [0.287, 0.454], dependency_ratio [0.598, 0.899], TFR [4.69, 8.03],
realised_e0 [21, 37], surv_to_15 ~0.66. Row 144 of the ladder: the Siler schedule is correct (e0 ~36.5), the
pyramid is young from a HIGH-TURNOVER regime (births 5.66%/yr, starvation deaths 3.80%/yr). This reproduces the
markers on the CURRENT canon (low-noise panel), decomposes the death flux (starvation vs senescence), computes the
growth rate r, and runs the GK07 iso-growth consistency check — so we can tell a fertility defect from a turnover
(packing-driven) one.

Canon, biome_seasonality ON, 600 agents, period window 400-800. No code change (read-only accessors).
"""
import os
import sys
import numpy as np

ROOT = r"C:\Users\syatom\Projects\SiC Games"
sys.path.insert(0, os.path.join(ROOT, "scratchpad"))
from bp_savanna_probe import build, runconfig
from sic_games.demography import isogrowth_check, DEMOG_ANCHORS

STEPS = int(os.environ.get("A_STEPS", "800"))
DFROM = int(os.environ.get("A_DFROM", "400"))
FEMALE_FRAC = 0.488


def run_one(clim, world_seed, agent_seed):
    canon = dict(runconfig.load()["DemographyConfig"])
    w = build(canon, world_seed, agent_seed, clim=clim)
    snap = None
    for t in range(STEPS):
        w.step()
        if not w.agent_list:
            break
        if t == DFROM:
            snap = w.raw_demographic_counters()
    cur = w.raw_demographic_counters()
    lt = w.life_table(since=snap)
    # period fertility from the counter diff (female age-specific)
    fb = [a - b for a, b in zip(cur["fert_births"], snap["fert_births"])]
    fe = [a - b for a, b in zip(cur["fert_exposure"], snap["fert_exposure"])]
    asfr = [(fb[i] / (fe[i] / 12.0)) if fe[i] > 0 else 0.0 for i in range(len(fb))]
    tfr = sum(asfr)
    # period flux
    dtot = sum(a - b for a, b in zip(cur["lt_deaths"], snap["lt_deaths"]))
    dstarv = sum(a - b for a, b in zip(cur["lt_deaths_starv"], snap["lt_deaths_starv"]))
    dsen = sum(a - b for a, b in zip(cur["lt_deaths_senesc"], snap["lt_deaths_senesc"]))
    py = sum(a - b for a, b in zip(cur["lt_exposure"], snap["lt_exposure"])) / 12.0
    btot = sum(fb)                       # TOTAL births: fert_births[mother_age] += 1 once per birth (verified
    cbr = btot / py if py else float("nan")
    cdr = dtot / py if py else float("nan")
    r_pct = 100.0 * (cbr - cdr)
    starv_rate = 100.0 * dstarv / py if py else float("nan")
    senesc_rate = 100.0 * dsen / py if py else float("nan")
    live = w.demography()
    iso = isogrowth_check(tfr, lt["surv_to_15"], r_pct)
    return dict(frac_child=live["frac_child"], dependency=live["dependency_ratio"], tfr=tfr,
                e0=lt["e0"], surv_to_15=lt["surv_to_15"], cbr_pct=100 * cbr, cdr_pct=100 * cdr, r_pct=r_pct,
                starv_rate=starv_rate, senesc_rate=senesc_rate, r_predicted_pct=iso["r_predicted_pct"],
                consistent=iso["consistent"], pop=len(w.agent_list))


def ms(v):
    v = np.array([x for x in v if x == x], float)
    return (v.mean(), v.std(ddof=1) / np.sqrt(len(v))) if len(v) > 1 else (float(v.mean()) if len(v) else float("nan"), 0.0)


def band(name):
    lo, hi = DEMOG_ANCHORS[name][1], DEMOG_ANCHORS[name][2]
    return lo, hi


def main():
    biomes = os.environ.get("A_BIOMES", "temperate,savanna").split(",")
    worlds = [int(x) for x in os.environ.get("A_WORLDS", "0,1,2").split(",")]
    agents = [int(x) for x in os.environ.get("A_AGENTS", "0").split(",")]
    fc = band("frac_child"); dp = band("dependency_ratio"); tf = band("realised_tfr")
    print(f"AGE-STRUCTURE DIAGNOSIS | canon | {STEPS} steps | period {DFROM}-{STEPS} | worlds {worlds} x agents {agents}",
          flush=True)
    print(f"  anchors: frac_child [{fc[0]}-{fc[1]}]  dependency [{dp[0]}-{dp[1]}]  TFR [{tf[0]}-{tf[1]}]  "
          f"e0 [21-37]  surv15 ~0.66", flush=True)
    for clim in biomes:
        rows = []
        for ws in worlds:
            for as_ in agents:
                r = run_one(clim, ws, as_)
                rows.append(r)
                print(f"  {clim} w{ws}a{as_}: frac_child {r['frac_child']:.2f} dep {r['dependency']:.2f} "
                      f"TFR {r['tfr']:.1f} e0 {r['e0']:.1f} surv15 {r['surv_to_15']:.2f} | "
                      f"CBR {r['cbr_pct']:.1f} CDR {r['cdr_pct']:.1f} r {r['r_pct']:+.1f}%/yr "
                      f"(starv {r['starv_rate']:.1f} senesc {r['senesc_rate']:.1f}) | "
                      f"iso r_pred {r['r_predicted_pct']:+.1f} consistent {r['consistent']}", flush=True)
        print(f"  === {clim} MEAN ===")
        for k, lab, anchor in [("frac_child", "frac_child", fc), ("dependency", "dependency", dp),
                               ("tfr", "TFR", tf), ("e0", "e0", (21, 37)), ("surv_to_15", "surv15", (0.46, 0.86)),
                               ("r_pct", "r %/yr", None), ("starv_rate", "starv %/yr", None),
                               ("senesc_rate", "senesc %/yr", None)]:
            m, e = ms([r[k] for r in rows])
            tag = ""
            if anchor:
                tag = "IN-anchor" if anchor[0] <= m <= anchor[1] else f"OUT (anchor {anchor[0]}-{anchor[1]})"
            print(f"    {lab:14s} {m:6.2f} +/- {e:4.2f}   {tag}")


if __name__ == "__main__":
    main()
