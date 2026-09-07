"""R-105 — the AGGLOMERATION CEILING GAP: the carrying-capacity ceiling must cover the agglomeration bonus.

THE BUG (R-104, diagnosed 2026-07-26). Point-mode agglomeration adds a SUPERLINEAR occupancy bonus
`aggl_R·(n^β − n)` to ANY occupied cell, but the R-63 catchment ceiling was gated on `(cx,cy) in
_settlement_sites`. A NON-settlement cell therefore had unbounded increasing returns — more crowding →
superlinearly more food → more people, with no Malthusian limit anywhere on that path. One campaign arm sat at
pop ~3000 for 1750 steps, then went 3259 → 97551 with ZERO starvation deaths at 61 agents/cell.

WHAT IS PINNED HERE. `enable_aggl_ceiling` makes the ceiling apply wherever the bonus applies. These tests drive a
REAL world for one step with `_settlement_carrying_capacity` stubbed to a known constant and record the food pool
each occupied cell actually hands to `compute_harvest_shares`:
  - flag ON  → every occupied cell's pool is ≤ the ceiling, with NO settlements in existence (i.e. the cap now
               reaches exactly the cells that used to escape it);
  - flag OFF → pools exceed the ceiling (the bug, reproduced — this is what every pre-R-105 result was run on);
  - flag ON but agglomeration OFF → no cap (the fix does not over-reach; non-agglomeration runs stay bit-exact).
`enable_game=False` keeps the arithmetic exact: the whole cell pool goes through one `compute_harvest_shares`
call, rather than being split into a forage stream and a stochastic meat draw.
"""
import os
import sys

import numpy as np
import pytest

from sic_games import phase1_model
from sic_games.config import CarbonConfig, KcalEconomyConfig, SubstrateConfig
from sic_games.capacity import NPPCapacityField
from sic_games.demography import DemographyConfig
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world, world_lottery_climate

CAP = 1000.0            # the stubbed catchment ceiling (kcal); well under a rich cell's raw pool


def _preset():
    # absolute, derived from __file__ — a relative path would silently depend on pytest's cwd
    _here = os.path.dirname(os.path.abspath(__file__))
    _p = os.path.normpath(os.path.join(_here, "..", "outputs", "phase1_social_evolution"))
    if _p not in sys.path:
        sys.path.insert(0, _p)
    from run_se0_controlled_climate import emergent_village_demog
    return emergent_village_demog()


def _packed_world(aggl_ceiling, aggl=True, n=120, seed=0):
    """A real village-stack world with every agent PACKED onto a few adjacent land cells (the crowding regime
    where the superlinear bonus runs away), and no settlement sites yet."""
    k = world_lottery_climate(seed, terrain="coastal", climate="temperate")
    f = generate_world(k, mode="climate")
    hf = NPPCapacityField(f, 75000.0, patch=(20, 20, 60), mode="tallavaara", aquatic=True, enable_depletion=True)
    land = [(x, y) for y in range(100) for x in range(100)
            if f.isWater[y, x] == 0 and hf.level(x, y) > 0]
    assert land, "world generated no habitable land"
    pos = [land[i % 4] for i in range(n)]                  # 4 cells, ~30 occupants each
    d = _preset().model_copy(update=dict(
        enable_agglomeration=aggl, aggl_mode="point", aggl_beta=1.15,
        enable_aggregation_sedentism=True, enable_catchment_ceiling=True,
        enable_aggl_ceiling=aggl_ceiling,
        enable_game=False,                                 # single-stream ⇒ the recorded total IS the cell pool
        enable_forage_cap=False))                          # the per-person cap trims shares, not the pool; keep it out
    return TerrainWorld(n_agents=n, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, game_stream=False, seed=seed,
                        carbon_cfg=CarbonConfig(kappa=1.5),
                        substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                                      contest_exponent=1.5, move_cost_flat=0.0),
                        harvest_field=hf, placement_positions=pos, demography_cfg=d)


def _cell_pools(monkeypatch, world):
    """Step once, returning every food pool handed to `compute_harvest_shares` (i.e. S after any capping)."""
    seen: list = []
    real = phase1_model.compute_harvest_shares

    def spy(occ, total, kappa, phi_eps=0.0, claim=None):
        seen.append(total)
        return real(occ, total, kappa, phi_eps, claim=claim)

    monkeypatch.setattr(phase1_model, "compute_harvest_shares", spy)
    world._settlement_carrying_capacity = lambda site: CAP        # a known ceiling, so the assertion is exact
    world.step()
    assert not world._settlement_sites, "no settlement should exist at step 1 — the point is the UNSITED cells"
    assert seen, "no cell pool was harvested"
    return seen


def test_default_is_off_so_prior_results_stay_bit_exact():
    assert DemographyConfig().enable_aggl_ceiling is False


def test_ceiling_caps_non_settlement_cells_when_on(monkeypatch):
    pools = _cell_pools(monkeypatch, _packed_world(aggl_ceiling=True))
    assert max(pools) <= CAP + 1e-6, f"a non-settlement cell out-produced its catchment: {max(pools)} > {CAP}"


def test_bug_reproduces_with_the_flag_off(monkeypatch):
    """The A/B control: with the flag OFF the ceiling still misses these cells, so pools blow past it. If this ever
    starts passing, the gap was closed somewhere else and `enable_aggl_ceiling` is no longer the switch."""
    pools = _cell_pools(monkeypatch, _packed_world(aggl_ceiling=False))
    assert max(pools) > CAP, f"expected the un-capped bug at max pool {max(pools)} ≤ {CAP}"


def test_flag_does_not_cap_when_agglomeration_is_off(monkeypatch):
    """The fix is scoped to the agglomeration path: with no bonus there is nothing to escape the ceiling, and a
    non-settlement cell must keep its plain tier-1 return (no behaviour change for non-agglomeration runs)."""
    pools = _cell_pools(monkeypatch, _packed_world(aggl_ceiling=True, aggl=False))
    assert max(pools) > CAP, "the flag capped a cell that has no agglomeration bonus — over-reach"


def test_crowding_inflates_the_pool_only_while_the_gap_is_open(monkeypatch):
    """The runaway's engine is that MORE CROWDING buys MORE FOOD with nothing bounding it. Pinned as the
    comparison that matters: with the gap open the cell pool tracks the crowd, and with the fix on it does not —
    the feedback loop is severed, not merely trimmed. (Deliberately NOT asserting a superlinear ratio here: the
    agents disperse during the step, so occupancy is not proportional to the founder count.)"""
    thin = max(_cell_pools(monkeypatch, _packed_world(aggl_ceiling=False, n=40)))
    thick = max(_cell_pools(monkeypatch, _packed_world(aggl_ceiling=False, n=160)))
    assert thick > thin, f"pool did not track crowding: {thin} → {thick}"
    for n in (40, 160):
        got = max(_cell_pools(monkeypatch, _packed_world(aggl_ceiling=True, n=n)))
        assert got <= CAP + 1e-6, f"n={n}: crowding still bought food past the ceiling ({got})"


def test_capacity_helper_is_geometric_not_site_gated():
    """The fix relies on `_settlement_carrying_capacity` being well-defined at a cell that is NOT a settlement —
    it reads the harvest field over the catchment, so it is purely geometric. Pinned because the fix would
    silently cap to 0.0 (mass starvation) if this ever became a lookup keyed on registered sites."""
    from types import SimpleNamespace
    tf = SimpleNamespace(width=100, height=100, level=lambda x, y: 2.0)
    cfg = DemographyConfig(settle_catchment_radius=1, catchment_ceiling_mult=3.0)
    f = SimpleNamespace(_harvest_field=tf, _demog=cfg, _settlement_sites={})
    got = TerrainWorld._settlement_carrying_capacity(f, (7, 7))       # (7,7) is not a settlement
    assert got == pytest.approx(3.0 * 9 * 2.0)                        # mult × 3×3 catchment × cell level


def test_ceiling_applies_without_aggregation_sedentism(monkeypatch):
    """THE SCOPE NOTE WAS CLOSED 2026-08-14, and this test is what caught it — as designed.

    It previously read `test_ceiling_still_needs_aggregation_sedentism_KNOWN_SCOPE` and asserted the OPPOSITE:
    that a world with agglomeration ON and aggregation-sedentism OFF got no ceiling at all. R-105 pinned that
    as "DOCUMENTED RESIDUAL SCOPE, not an endorsement ... so the gap is visible instead of forgotten", and its
    failure message was written to say "scope note is stale — the ceiling now applies without
    aggregation-sedentism". That message fired on the first run after the fix. The tripwire worked.

    WHAT THE GAP COST WHEN IT WAS FINALLY EXERCISED. The first arms ever run with settlement OFF (2026-08-14)
    reproduced R-104 exactly: population 2916 → 24,727 by step 3000 of 15,000, per-capita intake RISING with
    density (2.37 → 6.76x requirement), 221 occupants per cell, 1.72x the Binford packing anchor and still
    climbing. R-105's own note names the mechanism: "an unbounded increasing-returns loop with no Malthusian
    limit". The old note said campaign runs set both flags "so they are covered" — true until an arm ablated
    settlement, which nothing had done before.

    A ceiling is a statement about LAND. Whether people live in villages cannot decide whether their food
    supply is bounded.
    """
    w = _packed_world(aggl_ceiling=True)
    w._demog = w._demog.model_copy(update=dict(enable_aggregation_sedentism=False))
    pools = _cell_pools(monkeypatch, w)
    assert max(pools) <= CAP * 1.0001, (
        f"a mobile crowd out-produced its land: pool {max(pools):,.0f} > capacity {CAP:,.0f} — the "
        "settlement-off path has lost its ceiling again")
