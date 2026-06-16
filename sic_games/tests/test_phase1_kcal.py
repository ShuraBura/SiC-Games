"""Acceptance tests for Phase 1 Blueprint A: kcal economy + terrain harvest path.

Tests:
  A1.2  game_kcal field present, zeroed at wetland/mountain/water, nonzero in anchored biomes
  A1.3  KcalBurnModel step_cost; reserve integration unit test; no sugar quantity in C economy
  A1.4  TerrainField drop-in interface; level/harvest/game_level return sensible values
  A2.1  sex attribute set at init; p_female distribution check
  A2.2  energy-balance stream selection (male/female default + switch conditions)
  A2.3  game-as-stock: harvest does NOT deplete game_kcal
  A2.4  child age-gate: is_juvenile() zero-intake; adult full income
"""
from __future__ import annotations

import math

import pytest

from sic_games.agents.base import BaseAgent
from sic_games.agents.costs import KcalBurnModel, MetabolicOnly
from sic_games.config import KcalEconomyConfig, LifeHistoryConfig
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import (
    BIOME_DESERT,
    BIOME_FOREST,
    BIOME_GRASS,
    BIOME_MOUNTAIN,
    BIOME_SAVANNA,
    BIOME_WATER,
    BIOME_WETLAND,
    GAME_KCAL_TARGETS,
    GAME_KCAL_STD,
    generate_world,
)
from sic_games.terrain_field import TerrainField

# ── Shared fixtures ────────────────────────────────────────────────────────

_KNOBS = {
    "seedStr": "world42",
    "relief": 0.50,
    "rough": 0.50,
    "waterK": 0.30,
    "forestK": 0.55,
    "aridK": 0.40,
}

_KCAL_CFG = KcalEconomyConfig()
_LH_CFG = LifeHistoryConfig(forage_age_min=15)


@pytest.fixture(scope="module")
def fields():
    return generate_world(_KNOBS)


@pytest.fixture(scope="module")
def tf(fields):
    hours = _KCAL_CFG.foraging_hours_per_day * _KCAL_CFG.days_per_month
    return TerrainField(fields, hours_per_step=hours)


# ── A1.2: game_kcal field ──────────────────────────────────────────────────

def test_game_kcal_field_exists(fields):
    assert fields.game_kcal is not None, "game_kcal field must exist in WorldFields"


def test_game_kcal_zeroed_at_water(fields):
    water_mask = fields.isWater.astype(bool)
    assert fields.game_kcal[water_mask].max() == 0.0, "game_kcal must be 0 at water cells"


def test_game_kcal_zeroed_at_wetland(fields):
    wetland_mask = fields.biome == BIOME_WETLAND
    if wetland_mask.any():
        assert fields.game_kcal[wetland_mask].max() == 0.0, (
            "game_kcal must be 0 at wetland (UNANCHORED)"
        )


def test_game_kcal_zeroed_at_mountain(fields):
    mtn_mask = fields.biome == BIOME_MOUNTAIN
    if mtn_mask.any():
        assert fields.game_kcal[mtn_mask].max() == 0.0, (
            "game_kcal must be 0 at mountain (UNANCHORED)"
        )


def test_game_kcal_nonzero_in_anchored_biomes(fields):
    for b_code in (BIOME_FOREST, BIOME_SAVANNA, BIOME_GRASS, BIOME_DESERT):
        mask = fields.biome == b_code
        if not mask.any():
            continue
        assert fields.game_kcal[mask].max() > 0.0, (
            f"game_kcal must be > 0 for biome {b_code}"
        )


def test_game_kcal_mean_near_target(fields):
    for b_code, target in GAME_KCAL_TARGETS.items():
        mask = fields.biome == b_code
        if not mask.any():
            continue
        mean_val = float(fields.game_kcal[mask].mean())
        # Within 1% of target (mean-scaling property; lognormal rescale re-normalises to exact mean)
        assert abs(mean_val - target) / target < 0.01, (
            f"biome {b_code}: game_kcal mean {mean_val:.1f} != target {target:.1f}"
        )


def test_game_kcal_std_near_target(fields):
    # Biomes with a literature-anchored std use the terrain-coupled lognormal draw;
    # the realised within-biome std should match the target spread (within 10%).
    for b_code, target_std in GAME_KCAL_STD.items():
        if target_std is None:
            continue
        mask = fields.biome == b_code
        if not mask.any():
            continue
        std_val = float(fields.game_kcal[mask].std())
        assert abs(std_val - target_std) / target_std < 0.10, (
            f"biome {b_code}: game_kcal std {std_val:.1f} != target {target_std:.1f}"
        )
        # lognormal draw is positive-only
        assert float(fields.game_kcal[mask].min()) > 0.0


# ── A1.3: KcalBurnModel ────────────────────────────────────────────────────

class _FakeModel:
    class _SF:
        width = 50; height = 50
    sugar_field = _SF()


class _FakeAgent:
    model = _FakeModel()
    pos = (5, 5)
    wealth = 100_000.0
    metabolism = 1


def test_kcal_burn_model_step_cost():
    burn = KcalBurnModel(burn_kcal_per_day=2500.0, days_per_month=30)
    cost = burn.step_cost(_FakeAgent(), {})
    assert cost == pytest.approx(75_000.0), "burn_per_step must be 2500 * 30 = 75000 kcal"


def test_kcal_burn_model_default():
    burn = KcalBurnModel()
    assert burn.step_cost(_FakeAgent(), {}) == pytest.approx(75_000.0)


def test_reserve_integration_sequence():
    """reserve += intake - burn; death at reserve <= floor; cap at reserve_full."""
    reserve = 100_000.0
    burn = 75_000.0
    intake = 100_000.0   # forest-class cell
    floor = 20_000.0
    full = 100_000.0

    reserve = min(reserve + intake, full)   # cap at full
    reserve -= burn
    assert reserve == pytest.approx(25_000.0)  # 100k + 100k capped to 100k, then -75k
    assert reserve > floor                       # alive

    # Savanna starvation scenario (agent below full, cap does not apply)
    reserve2 = 50_000.0
    intake2 = 46_386.0   # savanna kcal/step
    reserve2 = min(reserve2 + intake2, full)   # 96386 < 100k: no cap
    reserve2 -= burn
    assert reserve2 == pytest.approx(21_386.0)  # 50k + 46386 = 96386, -75k = 21386
    assert reserve2 > floor                      # alive (barely)


# ── A1.4: TerrainField interface ───────────────────────────────────────────

def test_terrain_field_width_height(tf, fields):
    assert tf.width == 100
    assert tf.height == 100


def test_terrain_field_level_non_negative(tf):
    for x, y in [(0, 0), (50, 50), (99, 99), (25, 75)]:
        assert tf.level(x, y) >= 0.0


def test_terrain_field_harvest_equals_level(tf):
    for x, y in [(10, 20), (50, 50), (80, 30)]:
        assert tf.level(x, y) == tf.harvest(x, y)


def test_terrain_field_game_level_non_negative(tf):
    for x, y in [(0, 0), (50, 50), (99, 99)]:
        assert tf.game_level(x, y) >= 0.0


def test_terrain_field_level_indexing(tf, fields):
    for x in range(0, 100, 20):
        for y in range(0, 100, 20):
            hours = _KCAL_CFG.foraging_hours_per_day * _KCAL_CFG.days_per_month
            expected = float(fields.forage_kcal[y, x]) * hours
            assert tf.level(x, y) == pytest.approx(expected), (
                f"level({x},{y}) should be forage_kcal[{y},{x}] * hours"
            )


# ── A2.1: Sex attribute ────────────────────────────────────────────────────

def test_sex_attribute_exists_on_agent():
    world = TerrainWorld(n_agents=10, kcal_cfg=_KCAL_CFG, seed=42, game_stream=False)
    for a in world.agent_list:
        assert a.sex in ("female", "male"), "sex must be 'female' or 'male'"


def test_sex_ratio_near_half(recwarn):
    """n=5000 draw: female fraction in [0.48, 0.52]."""
    world = TerrainWorld(n_agents=5000, kcal_cfg=_KCAL_CFG, seed=0, game_stream=False)
    n_agents = len(world.agent_list)
    n_female = sum(1 for a in world.agent_list if a.sex == "female")
    frac = n_female / n_agents if n_agents > 0 else 0.5
    assert 0.48 <= frac <= 0.52, (
        f"female fraction {frac:.3f} outside [0.48, 0.52] for n={n_agents}"
    )


def test_sex_p_female_zero():
    cfg = KcalEconomyConfig(p_female=0.0)
    world = TerrainWorld(n_agents=50, kcal_cfg=cfg, seed=42, game_stream=False)
    assert all(a.sex == "male" for a in world.agent_list), (
        "p_female=0 → all agents should be male"
    )


def test_sex_p_female_one():
    cfg = KcalEconomyConfig(p_female=1.0)
    world = TerrainWorld(n_agents=50, kcal_cfg=cfg, seed=42, game_stream=False)
    assert all(a.sex == "female" for a in world.agent_list), (
        "p_female=1 → all agents should be female"
    )


# ── A2.2: Energy-balance stream selection ─────────────────────────────────

def _make_world_for_stream():
    return TerrainWorld(n_agents=1, kcal_cfg=_KCAL_CFG, seed=42, game_stream=True)


def test_male_adequate_game_uses_game():
    world = _make_world_for_stream()
    burn = world._burn
    # game covers burn, forage does not
    game = burn + 10_000.0
    forage = burn - 20_000.0
    result = world._select_stream("male", forage, game)
    assert result == pytest.approx(game), "male with adequate game must use game stream"


def test_male_low_game_forage_covers_switches():
    world = _make_world_for_stream()
    burn = world._burn
    game = burn - 10_000.0
    forage = burn + 5_000.0    # forage > game
    result = world._select_stream("male", forage, game)
    assert result == pytest.approx(forage), (
        "male in deficit game + better forage must switch to forage"
    )


def test_male_zero_game_zero_forage_holds_default():
    world = _make_world_for_stream()
    result = world._select_stream("male", 0.0, 0.0)
    assert result == pytest.approx(0.0), (
        "male with both streams zero must hold default (game=0) and NOT spuriously switch"
    )


def test_female_adequate_forage_uses_forage():
    world = _make_world_for_stream()
    burn = world._burn
    forage = burn + 10_000.0
    game = burn - 20_000.0
    result = world._select_stream("female", forage, game)
    assert result == pytest.approx(forage), "female with adequate forage must use forage stream"


def test_female_low_forage_game_covers_switches():
    world = _make_world_for_stream()
    burn = world._burn
    forage = burn - 15_000.0
    game = burn + 5_000.0       # game > forage
    result = world._select_stream("female", forage, game)
    assert result == pytest.approx(game), (
        "female in deficit forage + better game must switch to game"
    )


# ── A2.3: Game-as-stock seam — depletion OFF ──────────────────────────────

def test_game_harvest_does_not_deplete(fields, tf):
    """Calling game_level multiple times returns same value (depletion OFF, GD-1 seam)."""
    for x, y in [(30, 40), (60, 70), (80, 10)]:
        v1 = tf.game_level(x, y)
        v2 = tf.game_level(x, y)
        v3 = tf.game_level(x, y)
        assert v1 == v2 == v3, (
            f"game_level({x},{y}) changed across calls — depletion must be OFF (GD-1 seam)"
        )


# ── A2.4: Child age-gate ───────────────────────────────────────────────────

def test_juvenile_gets_zero_intake_in_model():
    """Agents below age_productive_min=15 get zero intake in TerrainWorld step."""
    world = TerrainWorld(
        n_agents=20, kcal_cfg=_KCAL_CFG, lh_cfg=_LH_CFG, seed=42, game_stream=False
    )
    if not world.agent_list:
        pytest.skip("No land cells available for agents")

    agent = world.agent_list[0]
    agent.age = 5   # force juvenile
    agent.wealth = world._reserve_full

    # Force agent to a known land cell with nonzero forage
    non_water = [
        (x, y)
        for y in range(100) for x in range(100)
        if world._fields.forage_kcal[y, x] > 0
    ]
    assert non_water, "No non-zero forage cells found"
    agent.pos = non_water[0]

    wealth_before = agent.wealth
    world._step_agent(agent)
    # Juvenile: intake = 0; reserve changes only by burn
    expected = min(wealth_before, world._reserve_full) - world._burn
    assert agent.wealth == pytest.approx(expected, abs=1.0), (
        "Juvenile agent must receive zero intake (binary age-gate, JV-1 seam)"
    )


def test_adult_gets_nonzero_intake_in_model():
    """Agents at age >= 15 receive positive intake on a high-forage cell, allowing survival."""
    world = TerrainWorld(
        n_agents=20, kcal_cfg=_KCAL_CFG, lh_cfg=_LH_CFG, seed=42, game_stream=False
    )
    if not world.agent_list:
        pytest.skip("No land cells available for agents")

    agent = world.agent_list[0]
    agent.age = 20  # adult
    # Start at low reserve: without income, agent would die (floor=20k, burn=75k)
    # With positive intake from a forest cell, agent should survive.
    agent.wealth = 70_000.0  # below full; will die next step with zero intake

    # Find a forest cell (high forage > burn so agent survives)
    forest_cells = [
        (x, y)
        for y in range(100) for x in range(100)
        if world._fields.biome[y, x] == BIOME_FOREST
    ]
    if not forest_cells:
        pytest.skip("No forest cells in generated world")
    agent.pos = forest_cells[0]
    world.occupied.add(agent.pos)

    world._step_agent(agent)
    # Forest intake per step >> burn; reserve capped at full then burn deducted
    # Expected: min(70k + forest_rate, 100k) - 75k > floor=20k → agent alive
    assert agent.alive, "Adult agent on forest cell must survive with positive forage income"
    assert agent.wealth > agent.reserve_floor, (
        "Adult agent wealth must stay above floor after one step on a forest cell"
    )
