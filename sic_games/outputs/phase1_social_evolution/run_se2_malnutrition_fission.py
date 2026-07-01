"""Social-Evolution Stage — M2 MALNUTRITION FISSION: the SUBSTITUTION TEST.

Blueprint `…_ResourceResponse_Scoping.md`. M2 gives a band losing members to REALIZED starvation a dispersive
term that fissions it (large bands only — tolerable floors at band_base_tolerable); the child band diffuses apart
→ lower local density → higher per-capita yield → FEWER subsequent starvation deaths. The decisive validation is
the SUBSTITUTION TEST: under a scripted severe-scarcity pulse, M2-on should show LOWER total starvation mortality
than M2-off (dispersal reroutes the cost from death), not merely more fission.

Signal note (R-32): M2 fires on `_band_starv_ema` (per-band realized starvation rate), NOT `_condition` — the
latter samples the post-harvest FED reserve, so it stays pinned ~1.0 under scarcity (survivor-biased). Anchored to
REALIZED starvation (supervisor: bands disperse when starvation bites, not on a forecast).

Run:  py -3 -u outputs/phase1_social_evolution/run_se2_malnutrition_fission.py
"""
from __future__ import annotations
import os, sys, statistics
from collections import Counter

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_se1_leader_coherence import realistic_forager_demog, band_positions_patch, GRP
from sic_games.config import KcalEconomyConfig, SubstrateConfig, CarbonConfig
from sic_games.phase1_model import TerrainWorld
from sic_games.climate import ClimateField, ClimateDriver
from sic_games.terrain import generate_world
import importlib.util as _iu
_p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "phase1_demography_step2", "run_2a_pre.py")
_s = _iu.spec_from_file_location("r2", _p); _r2 = _iu.module_from_spec(_s); _s.loader.exec_module(_r2)
SubWindowCapacity, knobs_for = _r2.SubWindowCapacity, _r2.knobs_for

SEEDS = [0, 1, 2]
STEPS, FOUNDERS = 850, 300
PULSE_T0, PULSE_DUR, PULSE_M = 500, 300, 0.5     # severe −50% regime pulse (a catastrophe deep enough to starve)


def run_one(seed, m2_on, gain=2.0, starv_rate=0.03):
    demog = realistic_forager_demog().model_copy(update=dict(
        enable_malnutrition_fission=m2_on, malnutrition_fission_gain=gain, malnutrition_starv_rate=starv_rate))
    fields = generate_world(knobs_for(seed)); base = SubWindowCapacity(fields)
    pos = band_positions_patch(fields, base, FOUNDERS)
    cap = ClimateField(base, a_seas=0.25, regime_driver=ClimateDriver.pulse(PULSE_T0, PULSE_DUR, PULSE_M))
    w = TerrainWorld(n_agents=FOUNDERS, kcal_cfg=KcalEconomyConfig(), terrain_knobs=knobs_for(seed),
                     game_stream=False, seed=seed, carbon_cfg=CarbonConfig(kappa=1.5),
                     substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                                   contest_exponent=1.5, move_cost_flat=0.0, **GRP),
                     harvest_field=cap, placement_positions=pos, demography_cfg=demog)
    cum_starv, nbands, maxpress = 0, [], 0.0
    for step in range(STEPS):
        w.step()
        if not w.agent_list:
            break
        if PULSE_T0 <= step < PULSE_T0 + PULSE_DUR:                # measure over the pulse window
            cum_starv += w.deaths_starv_this_step
            nbands.append(len(Counter(a._group.band_id for a in w.agent_list)))
            if w._band_malnutrition:
                maxpress = max(maxpress, statistics.mean(w._band_malnutrition.values()))
    return dict(starv=cum_starv, nbands=statistics.mean(nbands) if nbands else 0.0,
                endpop=len(w.agent_list), maxpress=maxpress)


def main():
    print(f"M2 substitution test — severe pulse [{PULSE_T0},{PULSE_T0+PULSE_DUR}) at ×{PULSE_M}, {len(SEEDS)} seeds")
    print("Claim: M2 dispersal reroutes the scarcity cost from DEATH → M2-on starvation deaths < M2-off.\n")
    print(f"  {'seed':<6}{'starv OFF':>10}{'starv ON':>10}{'Δstarv':>9}{'bands OFF→ON':>16}{'endpop OFF→ON':>16}{'M2 press':>10}")
    dtot = []
    for seed in SEEDS:
        off = run_one(seed, False); on = run_one(seed, True)
        d = on["starv"] - off["starv"]; dtot.append(d)
        print(f"  {seed:<6}{off['starv']:>10}{on['starv']:>10}{d:>+9}"
              f"{off['nbands']:>7.1f}→{on['nbands']:<7.1f}{off['endpop']:>7}→{on['endpop']:<7}{on['maxpress']:>10.2f}")
    print(f"\n  mean Δ(starvation deaths) = {statistics.mean(dtot):+.0f}  "
          f"({'SUBSTITUTION CONFIRMED — M2 lowers starvation mortality' if statistics.mean(dtot) < 0 else 'NO substitution'})")


if __name__ == "__main__":
    main()
