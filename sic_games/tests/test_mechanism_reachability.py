"""Can a spatially-keyed mechanism ACT — in the code, in the worlds we draw, and where people live?

R-106. Two climate channels were correct as fields and unreachable as mechanisms, and neither existing kind
of test could have found them:

  * a UNIT test builds a stub world and hands the mechanism its precondition, so it never asks whether a real
    world supplies one;
  * a CAMPAIGN ABLATION turns the mechanism off and sees no change — indistinguishable from a broken
    mechanism, and it points at the mechanism rather than at its habitat.

So reachability is asked at three levels, because a mechanism can fail at any one:

  LEVEL 1  DOMAIN   — can the precondition be satisfied AT ALL, given the code? (exhaustive, no world)
  LEVEL 2  WORLD    — across the world lottery, how many cells satisfy it?
  LEVEL 3  HABITAT  — of those, how many are inside the inhabited capacity patch, and how many does anyone
                      ever stand on?

WHAT THE THREE LEVELS FOUND, AND WHAT WAS DONE:

  `GRASS_LLANOS` failed at LEVEL 1 — unreachable for every possible (T, P), because `whittaker_biome` sends
  warm grass-zone cells to BIOME_SAVANNA while the splitter asked for BIOME_GRASS at T >= 18. FIXED: the
  llanos is a SAVANNA sub-type (warm seasonally-flooded grassland is savanna in Whittaker terms), selected by
  the wetland geometry `dist <= 2 & slope < 0.12` — the wetland test's own constants, so no new threshold —
  which after BIOME_WETLAND has claimed the wetter cells leaves exactly the drier seasonally-inundated
  floodplain.

  C.5 intercept hunting passed 1 and 2 and failed at LEVEL 3: savanna was 0-0.6% of the capacity patch and
  0 of ~1500 agents ever stood on an eligible cell. FIXED without touching the generator: `terrain.py` had
  carried a `savanna` CLIMATE_PRESET since 2026-07-08, explicit-only so no harness ever asked for it. In a
  savanna world the intercept biome is 52-67% of the patch and 35% of agents stand on one.

CONVENTION: each test asserts the CURRENT measured fact so it cannot rot, and its docstring says what to do
when it starts failing.
"""
import numpy as np
import pytest

from sic_games.terrain import (BIOME_GRASS, BIOME_SAVANNA, GRASS_LLANOS, GRASS_STEPPE,
                               GRASS_TROPICAL_THRESHOLD_C, WHIT_TUNDRA_T, generate_world,
                               whittaker_biome, world_lottery_climate)

# The capacity window `run_campaign.py` masks to: NPPCapacityField(..., patch=(X0, Y0, PATCH)). Capacity is
# ZERO outside it, so this rectangle is the whole inhabitable world as far as any agent is concerned.
PATCH_X0, PATCH_Y0, PATCH_N = 20, 20, 60


def _patch_mask(n=100):
    m = np.zeros((n, n), bool)
    m[PATCH_Y0:PATCH_Y0 + PATCH_N, PATCH_X0:PATCH_X0 + PATCH_N] = True
    return m


def _world(terr, clim, seed=0):
    return generate_world(world_lottery_climate(seed, terrain=terr, climate=clim), mode="climate")


# ── LEVEL 1: DOMAIN ──────────────────────────────────────────────────────────────────────────────────

def test_warm_grass_is_still_impossible_so_the_old_llanos_rule_would_still_be_empty():
    """The defect that started this, kept as a standing fact about the classifier rather than a memory.

    `whittaker_biome` sends warm grass-zone cells to BIOME_SAVANNA, so BIOME_GRASS only survives in the COOL
    grass zone (T < 18) and under the tundra cap (T < -5). Any future rule of the form
    `BIOME_GRASS & (T >= 18)` is therefore empty, whatever it is used for — which is why the llanos splitter
    now reads BIOME_SAVANNA instead."""
    T = np.repeat(np.linspace(-40.0, 50.0, 901)[:, None], 501, axis=1)
    P = np.repeat(np.linspace(0.0, 6000.0, 501)[None, :], 901, axis=0)
    b = whittaker_biome(T, P)
    assert (b == BIOME_GRASS).any() and (b == BIOME_SAVANNA).any(), "the sweep must cover both biomes"
    assert int(((b == BIOME_GRASS) & (T >= GRASS_TROPICAL_THRESHOLD_C)).sum()) == 0
    assert WHIT_TUNDRA_T < GRASS_TROPICAL_THRESHOLD_C, "the tundra cap must sit below the tropical isotherm"


def test_llanos_comes_from_savanna_and_steppe_from_grass():
    """The corrected parentage. Llanos on a BIOME_GRASS cell would be the old bug returning."""
    for clim in ("savanna", "tropical", "temperate"):
        f = _world("flat", clim)
        ll = f.grass_subtype == GRASS_LLANOS
        st = f.grass_subtype == GRASS_STEPPE
        assert not (ll & (f.biome != BIOME_SAVANNA)).any(), f"{clim}: a llanos cell that is not savanna"
        assert not (st & (f.biome != BIOME_GRASS)).any(), f"{clim}: a steppe cell that is not grass"
        assert not (ll & st).any(), "a cell tagged both sub-biomes"
        assert (st == (f.biome == BIOME_GRASS)).all(), "every GRASS cell must be steppe"


# ── LEVEL 2: WORLD ───────────────────────────────────────────────────────────────────────────────────

@pytest.mark.slow
def test_the_llanos_exists_and_is_the_flooded_MINORITY_of_savanna():
    """Not all savanna floods — the Hadza savanna this biome is anchored to does not — so the llanos must be
    a small, water-adjacent, flat subset. Measured 3.6-4.4% of savanna cells. If this ever approached 100%
    the splitter would have stopped discriminating and Orinoco flood dynamics would be running on Hadza
    country."""
    for terr in ("flat", "coastal"):
        f = _world(terr, "savanna")
        sav = int((f.biome == BIOME_SAVANNA).sum())
        ll = int((f.grass_subtype == GRASS_LLANOS).sum())
        assert sav > 0 and ll > 0, f"{terr}-savanna has savanna={sav} llanos={ll}"
        share = ll / sav
        assert 0.005 < share < 0.25, (
            f"{terr}-savanna: llanos is {share*100:.1f}% of savanna — outside the flooded-minority band")
        # The geometry it was selected by: near water and flat.
        ys, xs = np.where(f.grass_subtype == GRASS_LLANOS)
        assert (f.slope[ys, xs] < 0.12).all(), "a llanos cell on a slope — it is a floodplain"


@pytest.mark.slow
def test_which_worlds_carry_which_climate_keyed_biome():
    """A mechanism keyed to a biome no world contains is inert for a TERRAIN reason, and that belongs on the
    record beside the mechanism rather than being rediscovered by an ablation. This also pins WHY no single
    world can check both C.4b and C.5: savanna and steppe do not co-occur meaningfully."""
    got = {}
    for clim in ("tropical", "savanna", "temperate", "boreal"):
        f = _world("flat", clim)
        got[clim] = dict(savanna=int((f.biome == BIOME_SAVANNA).sum()),
                         llanos=int((f.grass_subtype == GRASS_LLANOS).sum()),
                         steppe=int((f.grass_subtype == GRASS_STEPPE).sum()))
    assert got["savanna"]["savanna"] > 1000, "the savanna preset must actually be savanna-dominated"
    assert got["savanna"]["llanos"] > 0 and got["tropical"]["llanos"] > 0
    assert got["temperate"]["savanna"] == 0 and got["boreal"]["savanna"] == 0
    assert got["temperate"]["steppe"] > 1000 and got["boreal"]["steppe"] > 1000
    # Savanna worlds are where C.5/C.4c live; temperate/boreal are where C.4b lives. No overlap worth using.
    assert got["savanna"]["steppe"] * 20 < got["temperate"]["steppe"]


# ── LEVEL 3: HABITAT — the level that caught the intercept ───────────────────────────────────────────

@pytest.mark.slow
def test_the_intercept_biome_reaches_the_patch_only_in_a_savanna_world():
    """The measurement that made the case for adding the preset, kept as a standing comparison. Capacity is
    zero outside the patch, so the patch — not the world — is what an agent can live in."""
    patch = _patch_mask()
    frac = {}
    for clim in ("tropical", "savanna"):
        f = _world("flat", clim)
        elig = (f.biome == BIOME_SAVANNA) | (f.grass_subtype == GRASS_LLANOS)
        frac[clim] = int((elig & patch).sum()) / float(PATCH_N * PATCH_N)
    assert frac["tropical"] < 0.05, (
        f"savanna is now {frac['tropical']*100:.1f}% of the patch in a TROPICAL world — the default worlds "
        f"may no longer need the savanna preset to exercise C.5")
    assert frac["savanna"] > 0.30, (
        f"the savanna world gives only {frac['savanna']*100:.1f}% of the patch — C.5's habitat has shrunk")


@pytest.mark.slow
def test_agents_actually_stand_where_the_intercept_can_act():
    """The question a unit test and an ablation both miss: not "does the field compute a boost" but "does
    anyone live on a cell it applies to". Measured 0.0% in flat-tropical against 35.3% in flat-savanna.

    This is the reusable shape for any spatially-keyed mechanism — soil, alluvial renewal, improved land,
    terrain risk and water access all key on spatial subsets and can fail the same way."""
    import os
    import sys
    batt = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "outputs",
                                         "mechanism_battery"))
    if batt not in sys.path:
        sys.path.insert(0, batt)
    import battery1_liveness as B1

    from sic_games import runconfig
    stack = dict(runconfig.load().get("DemographyConfig", {}))
    out = {}
    for clim in ("tropical", "savanna"):
        f = _world("flat", clim)
        elig = (f.biome == BIOME_SAVANNA) | (f.grass_subtype == GRASS_LLANOS)
        w = B1._build(stack, n=1200, patch=30, terr="flat", clim=clim)
        for _ in range(120):
            w.step()
            if not w.agent_list:
                pytest.skip(f"population collapsed in flat-{clim}")
        out[clim] = sum(1 for a in w.agent_list if elig[a.pos[1], a.pos[0]]) / len(w.agent_list)
    assert out["tropical"] < 0.01, (
        f"{out['tropical']*100:.1f}% of agents stand on an eligible cell in a TROPICAL world (was 0.0%)")
    assert out["savanna"] > 0.10, (
        f"only {out['savanna']*100:.1f}% of agents stand on an eligible cell in a SAVANNA world — C.5 and "
        f"C.4c have lost their population again")
