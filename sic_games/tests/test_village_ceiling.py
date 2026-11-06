"""R-106 Add.128, Stage A: `enable_village_ceiling`. The sum of the food pools of a village obeys the ceiling at the site.

THE DEFECT (Add.128). The harvest applies `S = min(S, cap)` cell by cell, and each occupied cell has its own overlapping
9-cell sum. So a village of 7-10 cells collected 1.7-3.6 × the ceiling that the density brake reads.

WHAT IS PINNED HERE. These tests drive a REAL world for one step with one known settlement and read the model's own
`_diag_pool` hook, which records S after every bonus and every ceiling.
  - flag ON:  the sum of the pools of each village is at most the ceiling at its site;
  - flag OFF: the sum exceeds that ceiling (the positive control: the defect is present and the instrument sees it);
  - flag ON:  the scale is pro rata, and a mobile cell outside every village keeps its pool;
  - flag ON:  a village under its ceiling keeps its pools (the flag does not over-reach).
The ceiling is a stub with a known value, because the agents disperse before the harvest and the true ceiling depends on
the world. The per-cell ceiling stays active, so each cell obeys CAP and only the village sum can exceed it. Bit-exactness of
the flag-off path is not a unit test: the proof is the control arm of the Stage A sweep, which must equal the stored `pair`
run of Add.124 at each shared step.
"""
import os
import sys

import pytest

from sic_games.capacity import NPPCapacityField
from sic_games.config import CarbonConfig, KcalEconomyConfig, SubstrateConfig
from sic_games.demography import DemographyConfig
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world, world_lottery_climate

CAP = 1.0e7             # the stubbed ceiling: below the pool of a rich packed cell, above the pool of a mobile cell


def _preset():
    _here = os.path.dirname(os.path.abspath(__file__))
    _p = os.path.normpath(os.path.join(_here, "..", "outputs", "phase1_social_evolution"))
    if _p not in sys.path:
        sys.path.insert(0, _p)
    from run_se0_controlled_climate import emergent_village_demog
    return emergent_village_demog()


def _village_world(flag, n=160, seed=0, cap=CAP):
    """A real world with the agents packed on 8 cells around one known settlement, plus 6 agents on one far cell."""
    k = world_lottery_climate(seed, terrain="coastal", climate="temperate")
    f = generate_world(k, mode="climate")
    hf = NPPCapacityField(f, 75000.0, patch=(20, 20, 60), mode="tallavaara", aquatic=True, enable_depletion=True)
    land = {(x, y) for y in range(100) for x in range(100) if f.isWater[y, x] == 0 and hf.level(x, y) > 0}
    site = next(c for c in sorted(land) if all(((c[0] + dx) % 100, (c[1] + dy) % 100) in land
                                               for dx in range(-2, 3) for dy in range(-2, 3)))
    ring = [((site[0] + dx) % 100, (site[1] + dy) % 100) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    far = next(c for c in sorted(land) if min(abs(c[0] - site[0]), 100 - abs(c[0] - site[0])) > 10)
    pos = [ring[i % len(ring)] for i in range(n - 6)] + [far] * 6
    d = _preset().model_copy(update=dict(
        enable_agglomeration=True, aggl_mode="point", aggl_beta=1.15,
        enable_aggregation_sedentism=True, enable_catchment_ceiling=True, enable_aggl_ceiling=True,
        enable_game=False, enable_forage_cap=False, enable_village_ceiling=flag))
    w = TerrainWorld(n_agents=n, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, game_stream=False, seed=seed,
                     carbon_cfg=CarbonConfig(kappa=1.5),
                     substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                                   contest_exponent=1.5, move_cost_flat=0.0),
                     harvest_field=hf, placement_positions=pos, demography_cfg=d)
    w._settlement_sites[site] = w._settlement_sites.get(site, 0)
    w._nearest_map = None
    w._settlement_carrying_capacity = lambda s: cap
    return w, site


def _pools(world):
    """Step once with the diagnostic hook armed. Return the pools and a cell → site map, frozen at the harvest."""
    world._diag_pool = {}
    world.step()
    pool = dict(world._diag_pool)
    return pool, {c: world._nearest_settlement(c) for c in pool}


def _village_sums(pool, member):
    out = {}
    for c, (S, _n) in pool.items():
        s = member.get(c)
        if s is not None:
            out[s] = out.get(s, 0.0) + S
    return out


def test_default_is_off():
    assert DemographyConfig().enable_village_ceiling is False


def test_positive_control_defect_with_flag_off():
    """The A/B control. If this starts to fail, the defect was closed elsewhere, or the instrument lost it."""
    w, site = _village_world(False)
    pool, member = _pools(w)
    sums = _village_sums(pool, member)
    assert site in sums
    assert max(S for S, _n in pool.values()) <= CAP * (1.0 + 1e-9), "the per-cell ceiling must hold in this world"
    assert sums[site] > 1.5 * CAP, "the defect is absent: this flag has no job"


def test_village_sum_obeys_the_ceiling_with_flag_on():
    w, site = _village_world(True)
    pool, member = _pools(w)
    sums = _village_sums(pool, member)
    assert site in sums
    for s, tot in sums.items():
        assert tot <= CAP * (1.0 + 1e-9), (s, tot)
    assert sums[site] == pytest.approx(CAP, rel=1e-9), "the ceiling must bind here"


def test_scale_is_pro_rata_and_mobile_cells_keep_their_pool():
    """Same world, same seed, flag off against flag on: one scale for all cells of a village, 1 outside it."""
    w0, site = _village_world(False)
    w1, _ = _village_world(True)
    p0, m0 = _pools(w0)
    p1, m1 = _pools(w1)
    inside = [c for c in p1 if m1.get(c) == site and c in p0 and p0[c][1] == p1[c][1]]
    assert len(inside) >= 3
    ratios = [p1[c][0] / p0[c][0] for c in inside]
    assert max(ratios) - min(ratios) < 1e-9, ratios
    assert ratios[0] < 1.0
    outside = [c for c in p1 if m1.get(c) is None and c in p0 and p0[c][1] == p1[c][1]]
    assert outside, "the test needs a cell outside every village"
    for c in outside:
        assert p1[c][0] == pytest.approx(p0[c][0], rel=1e-12)


def test_no_scale_when_the_village_is_under_its_ceiling():
    """A very high ceiling leaves every pool unchanged: the flag caps and does nothing else."""
    w0, _ = _village_world(False, cap=1e12)
    w1, _ = _village_world(True, cap=1e12)
    p0, _ = _pools(w0)
    p1, _ = _pools(w1)
    assert p0.keys() == p1.keys()
    for c in p0:
        assert p1[c] == pytest.approx(p0[c], rel=1e-12)
