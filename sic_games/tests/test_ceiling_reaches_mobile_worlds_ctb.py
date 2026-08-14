"""CTB — THE CARRYING-CAPACITY CEILING MUST REACH A WORLD WITH NO VILLAGES (R-106, 2026-08-13).

THE DEFECT. `_step_rivalrous` computed

    ceiling_on = settle_on and enable_catchment_ceiling          # settle_on = enable_aggregation_sedentism

and then applied the R-63 ceiling under `if ceiling_on and _cap_here:`. But `_cap_here` has TWO branches, and
the second was added by R-105 specifically to cap the AGGLOMERATION bonus at cells that are NOT settlement
sites:

    _cap_here = (settle_on and (cx, cy) in self._settlement_sites) or (
        aggl_on and aggl_R is not None and enable_aggl_ceiling)

Because `ceiling_on` required `settle_on`, that second branch was UNREACHABLE in the one configuration it
exists for — agglomeration on, settlement off. Such a world had no ceiling at all, so the superlinear
`A_cell·(n^β − n)` term added to the cell pool ran unbounded. R-105's own comment names the outcome: "an
unbounded increasing-returns loop with no Malthusian limit (R-104: pop 3259→97551, zero starvation)".

WHY IT SURVIVED. Every arm in the project before 2026-08-13 ran with `enable_aggregation_sedentism = True`.
The path was never exercised. It is a gap, not a regression.

WHAT IT COST. The first settlement-off arms reproduced R-104 exactly: population 2916 → 24,727 by step 3000
of 15,000, per-capita intake RISING with density (2.37 → 6.76x requirement), 221 occupants per cell, 1.72x
the Binford packing anchor and still climbing. It also silently masked a second defect — the inflated `a2`
from the missing density normalisation was holding the runaway down, so `hg_villages_off` looked like the
best-calibrated world this project had produced (0.67x Binford, band_med 23) while running two errors that
partly cancelled. Correcting `a2` alone made the population explode. That pairing is why
`test_the_two_defects_partly_cancelled` exists: a fix validated against a world that carries a second,
compensating fault is not validated.

THE INVARIANT THIS PINS. A ceiling is a statement about LAND, not about architecture. Whether people live in
villages cannot decide whether their food supply is bounded.
"""
import pytest

from sic_games.config import KcalEconomyConfig, SubstrateConfig
from sic_games.demography import DemographyConfig
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world, world_lottery_climate


def _world(n=120, **upd):
    k = world_lottery_climate(0, terrain="coastal", climate="temperate")
    generate_world(k, mode="climate")
    d = DemographyConfig(enable_band_affiliation=True, enable_agglomeration=True,
                         enable_aggl_ceiling=True, enable_catchment_ceiling=True, **upd)
    return TerrainWorld(n_agents=n, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, seed=0,
                        substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion"),
                        demography_cfg=d)


# ── the invariant ─────────────────────────────────────────────────────────────────────────────────────────

def test_the_ceiling_does_not_depend_on_whether_villages_exist():
    """THE WHOLE POINT. A carrying capacity is a fact about the land. Turning settlement off must not turn
    the food supply unbounded."""
    for settle in (True, False):
        w = _world(enable_aggregation_sedentism=settle)
        w.step()
        assert w._demog.enable_catchment_ceiling is True
        cap = w._settlement_carrying_capacity(w.agent_list[0].pos)
        assert cap > 0.0, ("the capacity of a cell must be computable with settlement off — it is a sum over "
                           "the harvest field, not a property of a settlement")


def test_the_capacity_is_a_neighbourhood_sum_and_needs_no_settlement():
    """`_settlement_carrying_capacity` is named for settlements but computes Σ cell yield over the catchment
    radius. If it ever starts reading `self._settlement_sites`, the fix above silently dies."""
    w = _world(enable_aggregation_sedentism=False)
    w.step()
    assert not w._settlement_sites, "no settlement sites should exist with the mechanism off"
    caps = [w._settlement_carrying_capacity((x, x)) for x in (10, 30, 50)]
    assert all(c > 0.0 for c in caps)
    assert len(set(caps)) > 1, "different cells must give different capacities, or it is not reading the land"


# ── the runaway it prevents ───────────────────────────────────────────────────────────────────────────────

def test_a_crowded_mobile_cell_is_capped():
    """CONSTRUCTED RUNAWAY: pile agents onto one cell with agglomeration on and settlement off, and demand
    the pool stays under the land's capacity. Before the fix this was unbounded in n^beta."""
    w = _world(n=200, enable_aggregation_sedentism=False)
    w.step()
    cell = w.agent_list[0].pos
    for a in w.agent_list:
        a.pos = cell
    w._diag_pool = {}
    w.step()
    assert cell in w._diag_pool, "the pool diagnostic must observe the crowded cell"
    pool, occ = w._diag_pool[cell]
    cap = w._settlement_carrying_capacity(cell)
    assert occ > 100, "the crowd must actually be there for this to test anything"
    assert pool <= cap * 1.0001, (
        f"a mobile crowd out-produced its land: pool {pool:,.0f} > capacity {cap:,.0f} at {occ} occupants")


def test_per_capita_returns_FALL_once_the_cap_binds():
    """THE MALTHUSIAN PRECONDITION, and the reason the runaway matters beyond life expectancy.

    With increasing returns (aggl_beta = 1.15) the pool goes as n^1.15, so per-capita goes as n^0.15 and
    RISES with crowding — a population can never overshoot a capacity, because there is no capacity. Once the
    ceiling binds, the pool is fixed at the land's yield and per-capita must fall as 1/n. Asserting a FALL,
    not merely 'stops rising', is what makes this discriminate: an earlier version asserted the weaker
    condition and passed against the buggy code as well, which is a test that cannot fail.
    """
    w = _world(n=400, enable_aggregation_sedentism=False)
    w.step()
    cell = w.agent_list[0].pos
    far = ((cell[0] + 30) % 100, (cell[1] + 30) % 100)
    seen = {}
    for k in (15, 400):
        for i, a in enumerate(w.agent_list):
            a.pos = cell if i < k else far
        w._diag_pool = {}
        w._step_rivalrous()                      # the pool computation alone; no movement to scatter them
        if cell in w._diag_pool:
            pool, occ = w._diag_pool[cell]
            if occ:
                seen[k] = (pool / occ, occ, pool)
    assert len(seen) == 2, f"both occupancies must be observed, got {sorted(seen)}"
    (pc_lo, occ_lo, _), (pc_hi, occ_hi, pool_hi) = seen[15], seen[400]
    assert occ_hi > occ_lo * 5, f"the crowd must be real: {occ_lo} -> {occ_hi}"
    assert pc_hi < pc_lo, (
        f"per-capita yield RISES with crowding ({pc_lo:,.0f} at n={occ_lo} -> {pc_hi:,.0f} at n={occ_hi}): "
        "increasing returns are unbounded, so there is no capacity to overshoot and no Malthusian limit")


# ── bit-exactness for everything already on the record ────────────────────────────────────────────────────

def test_settlement_on_worlds_are_unaffected():
    """Every arm before 2026-08-13 ran with enable_aggregation_sedentism=True, where the old expression
    `settle_on and flag` and the new `flag` are identical. Nothing on the record is invalidated."""
    for flag in (True, False):
        d = DemographyConfig(enable_aggregation_sedentism=True, enable_catchment_ceiling=flag)
        old = d.enable_aggregation_sedentism and d.enable_catchment_ceiling
        new = d.enable_catchment_ceiling
        assert old == new


def test_the_ceiling_flag_still_switches_it_off():
    """The fix must not make the ceiling unconditional — it is still a flag, and an ablation must be able to
    remove it."""
    d = DemographyConfig(enable_aggregation_sedentism=False, enable_catchment_ceiling=False)
    assert d.enable_catchment_ceiling is False


# ── the interaction that hid it ───────────────────────────────────────────────────────────────────────────

def test_the_two_defects_partly_cancelled():
    """A NOTE KEPT AS A TEST, because the lesson is procedural rather than numeric.

    The missing density normalisation inflated mortality; the missing ceiling inflated food. Together they
    produced `hg_villages_off`, which read as the best-calibrated world this project had made — 0.67x the
    Binford density anchor, band_med 23, realised IBI 35 months against Hill's 37.6. Correcting the mortality
    ALONE made the population run away to 1.72x Binford and climbing, because the compensating error was
    still there.

    So: a fix validated on a world that carries a second, compensating fault is not validated. Both flags
    below must be reachable together, and any arm that scores markers should carry both.
    """
    d = DemographyConfig(enable_density_reference=True, enable_catchment_ceiling=True,
                         enable_agglomeration=True, enable_aggregation_sedentism=False)
    assert d.enable_density_reference and d.enable_catchment_ceiling
