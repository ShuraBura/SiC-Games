"""R-87 — THE H-CYCLES TEST. Does a DELAYED negative feedback produce secular cycles where three
instantaneous-feedback mechanisms could not?

MECHANISM_CHARTER §5 / HYPOTHESES H-CYCLES: connubium (R-67), substrate (R-68) and soil (R-71) all failed to
cycle, and in linearized terms that is ONE fact — every feedback in the model is INSTANTANEOUS negative
feedback, giving a real negative eigenvalue and therefore a stable node. Oscillation needs a complex pair, which
needs a LAG.

R-87 supplies the lag: resentment against ascribed lineages accumulates on a generational EMA and eventually
triggers the gumsa -> gumlao reversion. `resent_alpha` IS the lag, so the discriminating experiment is a SWEEP
OVER IT, not a single run:

    alpha = 0.002  (~40 yr memory)  -> should cycle
    alpha = 0.004  (~20 yr memory)  -> should cycle (the ethnographic setting)
    alpha = 0.05   (~1.7 yr memory) -> should NOT cycle; nearly instantaneous, i.e. back to a stable node

A mechanism that oscillates at EVERY alpha is wiggling for some other reason. The prediction is specifically
that the cycle appears only when the delay is comparable to the system's relaxation time (~250 steps, R-68).

ANCHOR [Leach via Flannery ch.10, VERIFIED]: hereditary inequality "repeatedly created, lasted for A FEW
GENERATIONS, and then collapsed" => a period of ~60-100 yr = 720-1200 steps.
"""
import os
import sys

sys.path.insert(0, os.path.normpath("sic_games/outputs/phase1_social_evolution"))
from run_se0_controlled_climate import realistic_forager_demog

from sic_games.capacity import NPPCapacityField
from sic_games.climate import ClimateField
from sic_games.config import CarbonConfig, KcalEconomyConfig, SubstrateConfig
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world, world_lottery_climate

PROG = os.path.join(os.path.dirname(__file__), "progress_hcycles.txt")


def run(alpha, steps=2400, n=500, seed=0, thr=0.5):
    k = world_lottery_climate(seed, terrain="coastal", climate="temperate")
    f = generate_world(k, mode="climate")
    hf = ClimateField(NPPCapacityField(f, 75000.0, patch=(20, 20, 60), mode="tallavaara", aquatic=True,
                                       enable_depletion=True), a_seas=0.5)
    hf0 = NPPCapacityField(f, 75000.0, patch=(20, 20, 60), mode="tallavaara", aquatic=True, enable_depletion=True)
    land = [(x, y) for y in range(100) for x in range(100) if f.isWater[y, x] == 0 and hf0.level(x, y) > 0]
    d = realistic_forager_demog().model_copy(update=dict(
        enable_material_capture=True, material_hide_frac=0.07, material_decay=0.002, aggrandizer_frac=0.15,
        enable_leader_share=True, leader_share_frac=0.20,
        enable_leveling=True, leveling_strength=0.79, leveling_share=0.8,
        enable_leader_office=True, office_grievance_gain=0.05,
        enable_legitimacy=True, legit_feast_frac=0.25, legit_cred_gain=10.0,
        legit_threshold=0.15, legit_decay=0.02,
        enable_delegitimation=True, resent_alpha=alpha, resent_threshold=thr,
        # CRITICAL (R-87a): normalise privilege by the cred advantage ascription actually confers.
        # Left at 1.0, privilege ~= legit_cred_gain = 10, i.e. 20x the threshold — so even a '40-year'
        # EMA crosses in ~12 steps and the lag is nullified by the signal magnitude. The first sweep
        # therefore compared three arms that were ALL effectively instantaneous, and tested nothing.
        resent_privilege_ref=10.0))
    w = TerrainWorld(n_agents=n, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, game_stream=False, seed=seed,
                     carbon_cfg=CarbonConfig(kappa=1.5),
                     substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                                   contest_exponent=1.5, move_cost_flat=0.0),
                     harvest_field=hf, placement_positions=[land[i % len(land)] for i in range(n)],
                     demography_cfg=d)
    series, rev, pops = [], 0, []
    for t in range(steps):
        w.step()
        if not w.agent_list:
            break
        rev += w.reversions_this_step
        if t % 4 == 0:
            g = w.gumsa_state()
            series.append(g["frac_gumsa"])
            pops.append(len(w.agent_list))
        if t % 200 == 0:
            with open(PROG, "w") as fh:
                fh.write(f"alpha={alpha} step {t}/{steps} pop={len(w.agent_list)} rev={rev}\n")
                fh.flush()
    return series, rev, pops


def period_of(series, sample_every=4):
    """First autocorrelation peak after the first zero-crossing, in STEPS. None if no clear peak."""
    import numpy as np
    x = np.asarray(series, dtype=float)
    if len(x) < 60:
        return None, 0.0
    x = x - x.mean()
    if x.std() < 1e-9:
        return None, 0.0
    ac = np.correlate(x, x, mode="full")[len(x) - 1:]
    ac /= ac[0]
    neg = np.where(ac < 0)[0]
    if len(neg) == 0:
        return None, 0.0                      # never goes negative => no oscillation, just drift
    start = neg[0]
    seg = ac[start:]
    if len(seg) < 3:
        return None, 0.0
    k = int(np.argmax(seg)) + start
    return k * sample_every, float(ac[k])


if __name__ == "__main__":
    import numpy as np
    print(__doc__.strip().split("\n")[0])
    print(f"\n{'alpha':>7} {'memory':>9} {'revs':>6} {'mean_gumsa':>11} {'sd_gumsa':>9} "
          f"{'period_yr':>10} {'ac_peak':>8} {'verdict':>14} {'pop':>6}")
    print("-" * 96)
    # crossing time ~= 0.69/alpha steps once privilege is O(1): 1380 / 690 / 35 steps = 115 / 58 / 3 yr.
    # The ethnographic anchor (60-100 yr) sits between the first two; the last is the negative control.
    for alpha in (0.0005, 0.001, 0.02):
        series, rev, pops = run(alpha, steps=3600)
        if not series:
            print(f"{alpha:7.3f}  *** EXTINCT ***")
            continue
        per, peak = period_of(series)
        arr = np.asarray(series)
        mem_yr = (1.0 / alpha) / 12.0
        if per is None:
            verdict = "NO CYCLE"
        elif peak < 0.2:
            verdict = "weak/none"
        else:
            verdict = "CYCLES"
        pstr = f"{per / 12.0:10.1f}" if per else f"{'-':>10}"
        print(f"{alpha:7.3f} {mem_yr:8.1f}y {rev:6d} {arr.mean():11.3f} {arr.std():9.3f} "
              f"{pstr} {peak:8.2f} {verdict:>14} {np.mean(pops):6.0f}")
    print("\nANCHOR: Kachin hereditary inequality lasted 'a few generations' ~60-100 yr before collapsing.")
    print("PREDICTION: cycles at SLOW alpha only. Oscillation at every alpha => something else is wiggling.")
