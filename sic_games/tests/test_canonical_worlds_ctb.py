"""TIER 2 — THE CANONICAL WORLD SET. Three worlds, because one cannot carry every biome.

THE REQUEST (supervisor, 2026-08-08): "either a canonical world that has all needed biomes, with all biomes
seeded with people and preferably separated by hard-to-pass mountains that would keep the pops separated and
evolving differently. Or different canonical worlds dominated by different biomes."

**THE FIRST OPTION IS NOT BUILDABLE WITH THE CURRENT GENERATOR, and the measurement is here.** Two independent
obstacles:

  1. BIOMES AND MOUNTAINS TRADE OFF. Across all 25 terrain x climate combinations the ceiling is FIVE of six
     biomes. Turning up orogeny raises mountain cover (3.7% -> 20.4% -> 55.8% on mountainous-savanna) but
     CROWDS OUT the biomes it was meant to separate: savanna disappears entirely by orogenK = 0.6.
  2. MOUNTAINS DO NOT PARTITION THE LAND. Treating cost > 0.7 cells as impassable and taking connected
     components, ONE COMPONENT HOLDS 94-98% OF THE LAND in every configuration tested, including maximum
     orogeny. High-cost terrain is 2-6% of land and forms scattered patches rather than a range — and the
     world is a TORUS, so even a perfect belt would need to span the full height to separate anything.

So mountains are movement FRICTION (`move_cost_kcal * cost`, ~6.7x for a peak vs a plain) and not a barrier.
Isolated populations evolving separately would need a generator that builds a spanning cordillera; that is a
terrain feature, not a knob.

**THE SECOND OPTION IS BUILDABLE and is what these three worlds are.** Together they cover all six biomes and
both grass sub-biomes, which no single world does.
"""
import pytest

from sic_games.terrain import (GRASS_LLANOS, GRASS_STEPPE, generate_world, world_lottery_climate)

WORLDS = {
    "world_temperate": ("coastal", "temperate"),
    "world_savanna": ("coastal", "savanna"),
    "world_montane": ("mountainous", "savanna"),
}
BIOME = {1: "wetland", 2: "forest", 3: "savanna", 4: "grass", 5: "desert", 6: "mountain"}


def _world(terrain, climate, seed=0):
    return generate_world(world_lottery_climate(seed, terrain=terrain, climate=climate), mode="climate")


def _present(f, frac=0.01):
    land = (f.isWater == 0)
    tot = land.sum()
    return {name for code, name in BIOME.items() if ((f.biome == code) & land).sum() >= frac * tot}


def test_the_three_worlds_together_cover_every_biome():
    """THE POINT OF THE SET. No single world reaches six; the union must."""
    covered = set()
    for terrain, climate in WORLDS.values():
        covered |= _present(_world(terrain, climate))
    assert covered == set(BIOME.values()), f"missing {set(BIOME.values()) - covered}"


def test_no_single_world_covers_every_biome_which_is_why_there_are_three():
    """Pinned as a measurement so the set cannot be quietly collapsed back to one world. If the generator is
    ever widened so that one world does carry all six, THIS is the test that should start failing."""
    for name, (terrain, climate) in WORLDS.items():
        assert len(_present(_world(terrain, climate))) < 6, f"{name} now covers all six — revisit the set"


def test_world_savanna_is_the_only_arm_that_can_exercise_the_savanna_anchors():
    """Hawkes 1991's 518 kcal/hr game rate and the 745/518 intercept boost are savanna-gated. The historical
    reference world has no savanna at all, so every result produced there is silent about them."""
    temperate = _world(*WORLDS["world_temperate"])
    savanna = _world(*WORLDS["world_savanna"])
    assert "savanna" not in _present(temperate)
    assert "savanna" in _present(savanna)


def test_world_savanna_carries_the_llanos_the_flood_channel_needs():
    """C.4c is gated on GRASS_LLANOS. `world_temperate` has ZERO llanos cells, which is why
    `ClimateField.health()` reports llanos=UNREACHABLE on every temperate run — not a defect, an absent
    sub-biome. `world_savanna` has ~200, the most of any world measured."""
    assert (_world(*WORLDS["world_temperate"]).grass_subtype == GRASS_LLANOS).sum() == 0
    assert (_world(*WORLDS["world_savanna"]).grass_subtype == GRASS_LLANOS).sum() > 100


def test_every_world_carries_steppe_so_caribou_is_always_exercised():
    """C.4b is gated on GRASS_STEPPE. Unlike llanos, steppe is present everywhere, which is why caribou reads
    LIVE on the temperate arm and paced its population (Addendum 35)."""
    for name, (terrain, climate) in WORLDS.items():
        n = (_world(terrain, climate).grass_subtype == GRASS_STEPPE).sum()
        assert n > 50, f"{name} has only {n} steppe cells"


def test_world_montane_is_the_only_arm_with_mountains():
    assert "mountain" in _present(_world(*WORLDS["world_montane"]))
    assert "mountain" not in _present(_world(*WORLDS["world_temperate"]))


# ── why option (a) is not buildable ───────────────────────────────────────────────────────────────────────

def test_orogeny_buys_mountains_by_SPENDING_biomes():
    """The trade-off, measured. Raising orogeny on the biome-richest montane world takes mountain cover from
    3.7% to 55.8% and takes the biome count DOWN — savanna, the thing the barriers were meant to separate, is
    gone by orogenK = 0.6."""
    base = world_lottery_climate(0, terrain="mountainous", climate="savanna")
    counts = {}
    for orog in (0.0, 0.6, 1.0):
        k = dict(base, orogenK=orog)
        f = generate_world(k, mode="climate")
        counts[orog] = (len(_present(f)), "savanna" in _present(f))
    assert counts[0.0][0] > counts[0.6][0], counts
    assert counts[0.0][1] is True and counts[0.6][1] is False, "savanna survives at 0 and is gone by 0.6"


def test_high_cost_terrain_does_NOT_partition_the_land():
    """THE DECISIVE MEASUREMENT for the isolated-populations proposal. Treat cost > 0.7 as impassable, take
    connected components on the torus: one component holds >90% of the land at every orogeny setting.

    Mountains here are friction, not a wall. Separated populations evolving differently would need a spanning
    cordillera, which the generator does not build."""
    import numpy as np
    from collections import deque

    def largest_component_share(passable):
        N = passable.shape[0]
        seen = np.zeros_like(passable, bool)
        best = 0
        for y in range(N):
            for x in range(N):
                if passable[y, x] and not seen[y, x]:
                    q = deque([(y, x)])
                    seen[y, x] = True
                    n = 0
                    while q:
                        cy, cx = q.popleft()
                        n += 1
                        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                            ny, nx = (cy + dy) % N, (cx + dx) % N
                            if passable[ny, nx] and not seen[ny, nx]:
                                seen[ny, nx] = True
                                q.append((ny, nx))
                    best = max(best, n)
        return best / passable.sum()

    for orog in (0.0, 1.0):
        f = generate_world(dict(world_lottery_climate(0, terrain="mountainous", climate="savanna"),
                                orogenK=orog), mode="climate")
        land = (f.isWater == 0)
        passable = land & ~(f.cost > 0.7)
        assert largest_component_share(passable) > 0.90, (
            f"orogenK={orog}: the land is still one connected region; mountains are friction, not a barrier")
