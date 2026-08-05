"""Can a spatially-keyed mechanism ACT — in the code, in the worlds we draw, and where people live?

R-106. Two climate channels turned out to be correct as fields and unreachable as mechanisms, and neither
existing kind of test could have found them:

  * a UNIT test builds a stub world and hands the mechanism its precondition, so it never asks whether a real
    world supplies one;
  * a CAMPAIGN ABLATION turns the mechanism off and sees no change — which is indistinguishable from a
    mechanism that is broken, and reads as a defect in the mechanism rather than in its habitat.

So reachability is asked in three separate levels, because a mechanism can fail at any one of them:

  LEVEL 1  DOMAIN   — can the precondition be satisfied AT ALL, given the code? (exhaustive, no world)
  LEVEL 2  WORLD    — across the world lottery we actually draw from, how many cells satisfy it?
  LEVEL 3  HABITAT  — of those, how many are inside the inhabited capacity patch, and how many does anyone
                      ever stand on?

`GRASS_LLANOS` fails at level 1. C.5 intercept hunting passes 1 and 2 and fails at level 3.

CONVENTION (as in `test_cohesion_headroom.py` and the Kaplan blocker in `test_intake_fertility.py`): a test
here asserts the CURRENT measured fact, so it cannot rot, and its docstring says what to do when it starts
failing. A blocker test that fails is good news.
"""
import numpy as np
import pytest

from sic_games.terrain import (BIOME_GRASS, BIOME_SAVANNA, GRASS_LLANOS, GRASS_STEPPE,
                               GRASS_TROPICAL_THRESHOLD_C, WHIT_TUNDRA_T, generate_world,
                               whittaker_biome, world_lottery_climate)

WORLDS = [(t, c) for t in ("flat", "coastal", "hilly") for c in ("tropical", "temperate", "boreal")]
# The capacity window `run_campaign.py` masks to: NPPCapacityField(..., patch=(X0, Y0, PATCH)). Capacity is
# ZERO outside it, so this rectangle is the whole inhabitable world as far as any agent is concerned.
PATCH_X0, PATCH_Y0, PATCH_N = 20, 20, 60


def _patch_mask(n=100):
    m = np.zeros((n, n), bool)
    m[PATCH_Y0:PATCH_Y0 + PATCH_N, PATCH_X0:PATCH_X0 + PATCH_N] = True
    return m


# ── LEVEL 1: DOMAIN ──────────────────────────────────────────────────────────────────────────────────

def test_llanos_subbiome_cannot_be_assigned_by_the_classifier():
    """BLOCKER. `GRASS_LLANOS` is unreachable BY CONSTRUCTION, so the whole C.4c llanos-flood layer — its
    Sarmiento/Castello/Hamilton anchors and its two-sided form — has never been able to act in any world.

    The contradiction is two lines of terrain.py:
        whittaker_biome  : `biome[grass_zone & warm] = BIOME_SAVANNA`   (warm grass-zone becomes SAVANNA)
        grass_subtype    : `_is_grass & (temperature >= 18.0) -> GRASS_LLANOS`  (needs warm BIOME_GRASS)
    and the only routes to BIOME_GRASS are the COOL grass zone (T < 18) and the tundra cap (T < -5), so the
    intersection is empty for every possible (T, P).

    Checked exhaustively over the classifier's own input space rather than argued, and confirmed empirically
    at level 2 below: zero llanos cells in 9 world types.

    WHEN THIS STARTS FAILING: decide whether the llanos should be split off BIOME_SAVANNA rather than
    BIOME_GRASS — the Orinoco llanos is warm seasonally-flooded grassland, which Whittaker calls savanna, so
    the classifier is arguably right and the SPLITTER is looking at the wrong parent. Then enable
    `enable_llanos_flood` and add its campaign arm to the climate liveness check."""
    T = np.repeat(np.linspace(-40.0, 50.0, 901)[:, None], 501, axis=1)
    P = np.repeat(np.linspace(0.0, 6000.0, 501)[None, :], 901, axis=0)
    b = whittaker_biome(T, P)
    assert (b == BIOME_GRASS).any() and (b == BIOME_SAVANNA).any(), "the sweep must cover both biomes"
    warm_grass = int(((b == BIOME_GRASS) & (T >= GRASS_TROPICAL_THRESHOLD_C)).sum())
    assert warm_grass == 0, (
        f"{warm_grass} (T,P) points are now BIOME_GRASS at T >= {GRASS_TROPICAL_THRESHOLD_C} C — the llanos "
        f"sub-biome has become assignable. Enable enable_llanos_flood and give it a campaign arm.")


def test_the_two_grass_subbiomes_partition_the_grass_biome():
    """Whatever the llanos gets fixed to, the split must stay a partition: every GRASS cell is exactly one of
    llanos or steppe, and neither code leaks onto a non-GRASS cell."""
    f = generate_world(world_lottery_climate(0, terrain="flat", climate="temperate"), mode="climate")
    is_grass = f.biome == BIOME_GRASS
    tagged = (f.grass_subtype == GRASS_LLANOS) | (f.grass_subtype == GRASS_STEPPE)
    assert (tagged == is_grass).all(), "grass_subtype and BIOME_GRASS disagree about which cells are grass"
    assert WHIT_TUNDRA_T < GRASS_TROPICAL_THRESHOLD_C, "the tundra cap must sit below the tropical isotherm"


# ── LEVEL 2: WORLD ───────────────────────────────────────────────────────────────────────────────────

@pytest.mark.slow
def test_no_generated_world_contains_a_llanos_cell():
    """Level 1 says it cannot happen; this confirms it in the worlds actually drawn, so a future terrain
    change that made it possible would flip level 1 and this together."""
    for terr, clim in WORLDS:
        for seed in range(2):
            f = generate_world(world_lottery_climate(seed, terrain=terr, climate=clim), mode="climate")
            n = int((f.grass_subtype == GRASS_LLANOS).sum())
            assert n == 0, f"{terr}-{clim} seed {seed} now has {n} llanos cells — see the blocker above"


@pytest.mark.slow
def test_the_biomes_each_climate_keyed_mechanism_needs_exist_somewhere():
    """A mechanism keyed to a biome that no world contains is inert for a TERRAIN reason, and that reason
    belongs on the record next to the mechanism rather than being rediscovered by an ablation."""
    seen = {"savanna": 0, "steppe": 0, "llanos": 0}
    per_climate = {}
    for terr, clim in WORLDS:
        f = generate_world(world_lottery_climate(0, terrain=terr, climate=clim), mode="climate")
        sav = int((f.biome == BIOME_SAVANNA).sum())
        st = int((f.grass_subtype == GRASS_STEPPE).sum())
        seen["savanna"] += sav
        seen["steppe"] += st
        seen["llanos"] += int((f.grass_subtype == GRASS_LLANOS).sum())
        per_climate.setdefault(clim, {"savanna": 0, "steppe": 0})
        per_climate[clim]["savanna"] += sav
        per_climate[clim]["steppe"] += st
    assert seen["steppe"] > 0, "C.4b caribou has no steppe to act on in ANY world"
    assert seen["savanna"] > 0, "C.5 intercept has no savanna to act on in ANY world"
    assert seen["llanos"] == 0, "llanos became reachable — see the level-1 blocker"
    # THE MEASURED SPLIT, pinned as measured rather than as the tidier claim I first wrote. Savanna is
    # tropical-ONLY (0 cells in temperate worlds). Steppe is overwhelmingly temperate/boreal but NOT
    # exclusively: tropical worlds carry a handful (29 across the three, from cold high-elevation cells under
    # the tundra cap) against thousands in a temperate world. So a tropical world cannot MEANINGFULLY
    # exercise C.4b even though its steppe count is not literally zero — which is why the channel check runs
    # caribou temperate and the intercept tropical, and why no single world can do both.
    assert per_climate["temperate"]["savanna"] == 0, "savanna is no longer tropical-only"
    assert per_climate["tropical"]["savanna"] > 0
    assert per_climate["temperate"]["steppe"] > 20 * max(1, per_climate["tropical"]["steppe"]), (
        f"tropical steppe ({per_climate['tropical']['steppe']}) is no longer negligible against temperate "
        f"({per_climate['temperate']['steppe']}) — a tropical world may now exercise the herd swing")


# ── LEVEL 3: HABITAT — the level that caught the intercept ───────────────────────────────────────────

@pytest.mark.slow
def test_the_intercept_biome_is_almost_absent_from_the_inhabited_patch():
    """BLOCKER. C.5 intercept hunting acts on savanna + llanos. Savanna exists only in tropical worlds, and
    `run_campaign` masks capacity to a 60x60 patch with ZERO outside — so the patch, not the world, is what an
    agent can live in. Measured: of 3600 patch cells, savanna is 0 (flat-tropical), 20 (coastal-tropical),
    39 (hilly-tropical). The layer is correct, plumbed, and cannot act.

    WHEN THIS STARTS FAILING: the patch or the world has changed so the aggregation biome is inhabitable —
    re-run the climate liveness check, where `no_intercept` should stop reading INERT."""
    worst = None
    for terr in ("flat", "coastal", "hilly"):
        f = generate_world(world_lottery_climate(0, terrain=terr, climate="tropical"), mode="climate")
        inside = int(((f.biome == BIOME_SAVANNA) & _patch_mask()).sum())
        worst = inside if worst is None else max(worst, inside)
    frac = worst / float(PATCH_N * PATCH_N)
    assert frac < 0.05, (
        f"savanna is now {frac*100:.1f}% of the capacity patch — the intercept can reach the population. "
        f"Re-check `no_intercept` in the climate liveness run.")


@pytest.mark.slow
def test_agents_never_stand_where_the_intercept_can_act():
    """The measurement that a unit test and an ablation both miss: not "does the field compute a boost" but
    "does anyone live on a cell it applies to". Zero of ~1500 agents do.

    This is the reusable shape for any spatially-keyed mechanism — soil, alluvial renewal, improved land,
    terrain risk, water access all key on spatial subsets and can fail the same way."""
    import os
    import sys
    batt = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "outputs",
                                         "mechanism_battery"))
    if batt not in sys.path:
        sys.path.insert(0, batt)
    import battery1_liveness as B1

    from sic_games import runconfig
    f = generate_world(world_lottery_climate(0, terrain="flat", climate="tropical"), mode="climate")
    agg = (f.biome == BIOME_SAVANNA) | (f.grass_subtype == GRASS_LLANOS)
    assert agg.sum() > 0, "no aggregation biome in this world at all — level 2 should have caught that"

    w = B1._build(dict(runconfig.load().get("DemographyConfig", {})), n=1200, patch=30,
                  terr="flat", clim="tropical")
    for _ in range(120):
        w.step()
        if not w.agent_list:
            pytest.skip("population collapsed")
    on_agg = sum(1 for a in w.agent_list if agg[a.pos[1], a.pos[0]])
    frac = on_agg / len(w.agent_list)
    assert frac < 0.01, (
        f"{frac*100:.1f}% of agents now stand on an intercept-eligible cell (was 0.0%) — the mechanism can "
        f"reach the population. Re-run the climate liveness check and expect `no_intercept` to differ.")
