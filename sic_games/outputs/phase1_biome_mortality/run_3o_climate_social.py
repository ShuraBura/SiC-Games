"""Stage 0 — CLIMATE INTEGRATION. Run the full social stack on a CLIMATE-MODULATED CC-1 capacity (ClimateField:
seasonal + ENSO + a regime telegraph), instead of the static SubWindowCapacity. Two checks:
  (1) COHERENCE: the stack still sustains + keeps its results on a varying world (eq_pop stable-lower, bands ~25,
      status->RS ~0.13). Seasonal lean LOWERS mean carrying capacity (Liebig) -- a realistic reduction, not a bug.
  (2) RESPONSE: the social model FEELS adversity -- during a regime DOWN excursion, surplus / assabiyah / pop are
      depressed vs the good state (the variation the dynamic-social stages will ride). Regime recurrence is
      COMPRESSED here (a stress test) so excursions fire inside 1500 steps; the realistic recurrence is millennial.
Run:  py -3 -u outputs/phase1_biome_mortality/run_3o_climate_social.py
"""
from __future__ import annotations
import os, time, math, statistics
from collections import Counter

import sys as _sys
try:
    _sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from sic_games.config import KcalEconomyConfig, SubstrateConfig, CarbonConfig
from sic_games.demography import DemographyConfig, ACHE_FOREST_NATURAL as NAT
from sic_games.phase1_model import TerrainWorld
from sic_games.climate import ClimateField
from sic_games.terrain import generate_world, N as GRID_N
import importlib.util as _iu
_p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "phase1_demography_step2", "run_2a_pre.py")
_s = _iu.spec_from_file_location("r2", _p); _r2 = _iu.module_from_spec(_s); _s.loader.exec_module(_r2)
SubWindowCapacity, knobs_for = _r2.SubWindowCapacity, _r2.knobs_for

SEEDS = list(range(5))
STEPS, FOUNDERS = 1500, 300
GRP = dict(group_safety_max=8.0, group_safety_scale=15.0, group_mate_min=15.0, group_mate_floor=0.2)


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


def run_one(seed, climate=True):
    import random
    fields = generate_world(knobs_for(seed)); base = SubWindowCapacity(fields)
    pos = band_positions_patch(fields, base, FOUNDERS)
    if climate:
        # seasonal + ENSO + a MILD compressed regime telegraph (compressed so down-excursions fire inside 1500
        # steps — a stress test; the realistic recurrence is millennial. Amplitudes kept moderate so the population
        # is perturbed, not crashed: a 4× crash at amp 0.30/recurrence 250 confirmed red-team #1 — trough-limiting.)
        cap = ClimateField(base, a_seas=0.25, interannual_amp=0.2, interannual_period=4 * 12,
                           interannual_phase=1.0, regime_amp=0.15, regime_duration=60, regime_recurrence=400,
                           rng=random.Random(1000 + seed))
    else:
        cap = base
    demog = DemographyConfig(
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
    w = TerrainWorld(n_agents=FOUNDERS, kcal_cfg=KcalEconomyConfig(), terrain_knobs=knobs_for(seed),
                     game_stream=False, seed=seed, carbon_cfg=CarbonConfig(kappa=1.5),
                     substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                                   contest_exponent=1.5, move_cost_flat=0.0, **GRP),
                     harvest_field=cap, placement_positions=pos, demography_cfg=demog)
    t0 = int(0.4 * STEPS)
    pops, bands_awt = [], []
    up = dict(pop=[], assab=[], surplus=[]); down = dict(pop=[], assab=[], surplus=[])
    fc_seeds = []
    for step in range(STEPS):
        w.step(); al = w.agent_list
        if not al:
            break
        if step >= t0:
            pops.append(len(al))
            sz = Counter(a._group.band_id for a in al); tot = sum(sz.values())
            bands_awt.append(sum(n * n for n in sz.values()) / tot if tot else 0.0)
            assab = statistics.mean(list(w._band_assabiyah.values())) if w._band_assabiyah else 0.0
            surplus = statistics.mean(list(w._band_surplus.values())) if w._band_surplus else 0.0
            state = getattr(cap, "_regime_state", 0) if climate else 0   # 1 = down excursion
            bucket = down if state == 1 else up
            bucket["pop"].append(len(al)); bucket["assab"].append(assab); bucket["surplus"].append(surplus)
    al = w.agent_list
    if not al:
        return dict(extinct=True)
    ids = {id(a) for a in al}; fc = {}
    for a in al:
        fa = getattr(a, "_father", None)
        if fa is not None and id(fa) in ids:
            fc[id(fa)] = fc.get(id(fa), 0) + 1
    males = [a for a in al if a.sex == "male"]
    rs = (lambda xs, ys: (lambda n, mx, my: sum((x - mx) * (y - my) for x, y in zip(xs, ys)) /
          (math.sqrt(sum((x - mx) ** 2 for x in xs)) * math.sqrt(sum((y - my) ** 2 for y in ys)) + 1e-12))
          (len(xs), sum(xs) / len(xs), sum(ys) / len(ys)))([a.prowess for a in males], [fc.get(id(a), 0) for a in males]) if len(males) > 2 else 0.0
    m = lambda d: statistics.mean(d) if d else float("nan")
    return dict(extinct=False, eq_pop=m(pops), band=m(bands_awt), rs=rs,
                up_pop=m(up["pop"]), down_pop=m(down["pop"]), up_assab=m(up["assab"]), down_assab=m(down["assab"]),
                up_surplus=m(up["surplus"]), down_surplus=m(down["surplus"]), down_frac=len(down["pop"]) / max(1, len(pops)))


def main():
    t0 = time.time()
    for lab, clim in (("STATIC ", False), ("CLIMATE", True)):
        rows = [r for r in (run_one(s, climate=clim) for s in SEEDS) if not r.get("extinct")]
        if not rows:
            print(f"[{lab}] ALL EXTINCT"); continue
        def agg(k):
            vals = [r[k] for r in rows if isinstance(r.get(k), (int, float)) and not math.isnan(r[k])]
            return statistics.mean(vals) if vals else float("nan")
        a = {k: agg(k) for k in rows[0] if k != "extinct"}
        print(f"[{lab}] eq_pop {a['eq_pop']:.0f} | band {a['band']:.1f} | status->RS {a['rs']:+.3f}  [{time.time()-t0:.0f}s]")
        if clim:
            print(f"          REGIME RESPONSE (down-excursion {a['down_frac']*100:.0f}% of tail): "
                  f"pop {a['up_pop']:.0f}->{a['down_pop']:.0f} | surplus {a['up_surplus']:.2f}->{a['down_surplus']:.2f} | "
                  f"assabiyah {a['up_assab']:.2f}->{a['down_assab']:.2f}")


if __name__ == "__main__":
    main()
