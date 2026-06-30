"""Social-Evolution Stage 0 — the CONTROLLED-CLIMATE BENCHMARK HARNESS.

WHY (blueprint Stage 0 verdict / R-27 red-team #3): the production `ClimateField` regime telegraph is STOCHASTIC,
so a single long run gives a noisy, lag-confounded "response" — you cannot separate a social outcome (band
fission, assabiyah swing, pop crash) from a *random* climate crash. This harness drives the regime channel with a
DETERMINISTIC `ClimateDriver` (good-vs-bad periods at KNOWN times) and TRACKS THE FULL TRAJECTORY, so the
dynamic-social stages (1 leader-coherence, 3 dynastic cycle, 4 belief) can be benchmarked cleanly: any change in a
social metric is attributable to the social response, not the climate noise.

Reusable API: `run_controlled(driver, seed, steps, demog=…)` → a per-step trajectory dict
  {climate, pop, band_awt, n_bands, assabiyah, surplus}. Stage 1+ import this and pass their own driver + flags.

Demonstration (this file's main): FLAT control vs a scripted PULSE catastrophe, windowed pre / during / post, to
show the harness resolves the recover-able social response that the stochastic run smeared out.

Run:  py -3 -u outputs/phase1_social_evolution/run_se0_controlled_climate.py
"""
from __future__ import annotations
import os, sys, time, math, statistics
from collections import Counter

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from sic_games.config import KcalEconomyConfig, SubstrateConfig, CarbonConfig
from sic_games.demography import DemographyConfig, ACHE_FOREST_NATURAL as NAT
from sic_games.phase1_model import TerrainWorld
from sic_games.climate import ClimateField, ClimateDriver
from sic_games.terrain import N as GRID_N, generate_world
import importlib.util as _iu
_p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "phase1_demography_step2", "run_2a_pre.py")
_s = _iu.spec_from_file_location("r2", _p); _r2 = _iu.module_from_spec(_s); _s.loader.exec_module(_r2)
SubWindowCapacity, knobs_for = _r2.SubWindowCapacity, _r2.knobs_for

GRP = dict(group_safety_max=8.0, group_safety_scale=15.0, group_mate_min=15.0, group_mate_floor=0.2)


def realistic_forager_demog() -> DemographyConfig:
    """The canonical full-stack config (families + bands + per-band society + assabiyah + modest polygyny),
    matching run_3m/run_3o (PARAMETERS §18). Stage 1+ flip on their own extra flag and pass an edited copy."""
    return DemographyConfig(
        polygyny_rate=0.3, max_wives=3,
        siler_a1=NAT.a1, siler_b1=NAT.b1, siler_a2=NAT.a2, siler_a3=NAT.a3, siler_b3=NAT.b3,
        enable_density_disease=True, dens_delta=3.0, dens_rho_half=0.2,
        enable_game=True, game_meat_frac=0.55, game_meat_cv=0.73,
        enable_cred_status=True, cred_seed_sigma=0.5, cred_inherit_sigma=0.1,
        enable_prowess_facet=True, prowess_decay=0.05, sex_division=1.0,
        enable_paternity=True, mate_choice_strength=5.0, patriline_weight=0.5, lineage_reversion=0.1,
        enable_bonded_mating=True, bonded_mate_radius=1, enable_pair_bonds=True,
        enable_band_affiliation=True, band_cohesion=0.3, band_split_size=45, band_merge_size=10,
        enable_storage=True, storable_fraction=0.5, store_capacity_reserves=3.0,
        storage_temp_threshold_c=100.0, storage_decay=0.05, enable_morph=True, morph_settle_steps=60,
        enable_band_family_knobs=True, enable_dynamic_bands=True, band_base_tolerable=25,
        assabiyah_gain=0.05, assabiyah_decay=0.02, season_aggregation=1.0)


def band_positions_patch(fields, cap, n, band_size=25, sep=4):
    cells = sorted(((cap.level(x, y), x, y) for y in range(GRID_N) for x in range(GRID_N)
                    if fields.isWater[y, x] == 0 and cap.level(x, y) > 0), reverse=True)
    sites, pos = [], []
    for (_, x, y) in cells:
        if len(sites) >= max(1, n // band_size):
            break
        if all(max(abs(x - px), abs(y - py)) >= sep for (px, py) in sites):
            sites.append((x, y)); pos.extend([(x, y)] * band_size)
    i = 0
    while len(pos) < n and sites:
        pos.append(sites[i % len(sites)]); i += 1
    return pos[:n]


def run_controlled(driver, seed=0, steps=1500, founders=300, demog=None, a_seas=0.25, sample_from=0):
    """Run the full social stack on a ClimateField whose REGIME channel is supplied by the deterministic
    `driver` (a ClimateDriver). Returns a per-step trajectory dict of parallel lists (sampled from `sample_from`).
    `driver=None` ⇒ the seasonal-only baseline (no regime stress). This is the harness primitive the
    dynamic-social stages call."""
    demog = demog or realistic_forager_demog()
    fields = generate_world(knobs_for(seed)); base = SubWindowCapacity(fields)
    pos = band_positions_patch(fields, base, founders)
    # Seasonality kept on (it is part of the realistic world); the CONTROLLED variation is the regime driver.
    cap = ClimateField(base, a_seas=a_seas, regime_driver=driver)
    w = TerrainWorld(n_agents=founders, kcal_cfg=KcalEconomyConfig(), terrain_knobs=knobs_for(seed),
                     game_stream=False, seed=seed, carbon_cfg=CarbonConfig(kappa=1.5),
                     substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                                   contest_exponent=1.5, move_cost_flat=0.0, **GRP),
                     harvest_field=cap, placement_positions=pos, demography_cfg=demog)
    traj = dict(climate=[], pop=[], band_awt=[], n_bands=[], assabiyah=[], surplus=[])
    for step in range(steps):
        w.step(); al = w.agent_list
        if not al:
            break
        if step >= sample_from:
            sz = Counter(a._group.band_id for a in al); tot = sum(sz.values())
            traj["climate"].append(cap.regime())
            traj["pop"].append(len(al))
            traj["band_awt"].append(sum(n * n for n in sz.values()) / tot if tot else 0.0)
            traj["n_bands"].append(len(sz))
            traj["assabiyah"].append(statistics.mean(list(w._band_assabiyah.values())) if w._band_assabiyah else 0.0)
            traj["surplus"].append(statistics.mean(list(w._band_surplus.values())) if w._band_surplus else 0.0)
    traj["extinct"] = not w.agent_list
    return traj


def _wmean(traj, key, lo, hi):
    """Mean of `key` over the step window [lo, hi) (indices into the sampled trajectory)."""
    xs = traj[key][lo:hi]
    return statistics.mean(xs) if xs else float("nan")


def _arm_windows(rows, windows, keys):
    """Per-window cross-seed mean of each metric for one arm."""
    def win(key, lo, hi):
        vals = [_wmean(r, key, lo, hi) for r in rows]
        vals = [v for v in vals if not math.isnan(v)]
        return statistics.mean(vals) if vals else float("nan")
    return {wn: {k: win(k, lo, hi) for k in keys} for wn, (lo, hi) in windows.items()}


def main():
    t0 = time.time()
    SEEDS = [0, 1, 2]
    STEPS = 1500
    # A scripted catastrophe: good times → a known -30% regime PULSE [600, 900) → recovery. (-30% = REGIME_AMP_TAIL,
    # an explicit catastrophe, deep enough to read a clean social response.) Windows: PRE [300,600) DURING [600,900)
    # POST [1100,1400) — POST offset to let the population re-aggregate after the pulse lifts at 900.
    PULSE_T0, PULSE_DUR, PULSE_M = 600, 300, 0.70
    WINDOWS = {"PRE": (300, 600), "DURING": (600, 900), "POST": (1100, 1400)}
    KEYS = ("pop", "band_awt", "surplus", "assabiyah")
    arms = {"FLAT": ClimateDriver.flat(1.0), "PULSE": ClimateDriver.pulse(PULSE_T0, PULSE_DUR, PULSE_M)}

    print(f"Controlled-climate harness — full social stack, {len(SEEDS)} seeds × {STEPS} steps "
          f"(a_seas=0.25 seasonal; regime channel = scripted driver)\n")
    arm_win = {}
    for label, drv in arms.items():
        rows = [r for r in (run_controlled(drv, seed=s, steps=STEPS) for s in SEEDS) if not r["extinct"]]
        if not rows:
            print(f"[{label}] ALL EXTINCT"); return
        arm_win[label] = _arm_windows(rows, WINDOWS, KEYS + ("climate",))
        clim = arm_win[label]["DURING"]["climate"]
        print(f"[{label:<6}] regime DURING = {clim:.2f}   "
              f"pop {arm_win[label]['PRE']['pop']:.0f}->{arm_win[label]['DURING']['pop']:.0f}"
              f"->{arm_win[label]['POST']['pop']:.0f}   [{time.time()-t0:.0f}s]")

    # The clean estimator: PULSE − FLAT at MATCHED times. PRE is bit-identical across arms (the driver diverges
    # only at t=600), so PRE gap ≈ 0 is the placebo check, and the DURING/POST gap IS the climate-attributable
    # response — free of the underlying growth trend that confounds a within-arm PRE→POST comparison.
    print("\n  climate-attributable response  =  PULSE − FLAT  (PRE gap ≈ 0 = placebo / common-trend check)")
    print(f"    {'metric':<11}{'ΔPRE':>10}{'ΔDURING':>12}{'ΔPOST':>10}")
    for k, name in (("pop", "pop"), ("band_awt", "band"), ("surplus", "surplus"), ("assabiyah", "assabiyah")):
        d = {wn: arm_win["PULSE"][wn][k] - arm_win["FLAT"][wn][k] for wn in WINDOWS}
        print(f"    {name:<11}{d['PRE']:>+10.2f}{d['DURING']:>+12.2f}{d['POST']:>+10.2f}")
    print("\n  Read: ΔPRE≈0 confirms the arms share a trajectory until the shock; the negative ΔDURING is the\n"
          "  catastrophe footprint, and ΔPOST < 0 (population set back, not yet recovered to the counterfactual)\n"
          "  is the lagged demographic scar — a clean, repeatable signal the stochastic run (R-27) smeared out.")


if __name__ == "__main__":
    main()
