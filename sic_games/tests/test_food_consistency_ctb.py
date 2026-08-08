"""CTB for the two-food-model consistency diagnostic.

THE DEFECT IT EXISTS TO CATCH. The model carries two independent descriptions of how much food a cell holds —
an NPP→density capacity field that sets what the population relaxes toward, and a per-biome return-rate table
that agents actually eat from. Neither knows about the other, so a biome can be rich in one and poor in the
other while every run looks sensible.

That is not hypothetical: `world_savanna` settles at **9% of its trough-limited capacity** where temperate and
montane reach 51% and 69%, because savanna is 48% of its land and savanna's two food models disagree by 16.9x.

THE DIAGNOSTIC IS A RATIO, NOT A MATCH. The two quantities are on different definitions — equilibrium density
versus theoretical maximum harvest — so capacity exceeds delivery everywhere. What matters is whether a biome
sits in the band the others occupy.
"""
import pytest

from sic_games.food_consistency import CLUSTER_HI, CLUSTER_LO, complaints, per_biome

pytest.importorskip("numpy")

BURN = 75000.0


def _report(terrain, climate, seed=0):
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "outputs" / "biome_society_20260702"))
    from run_biome_society import PATCH, X0, Y0

    from sic_games.capacity import NPPCapacityField
    from sic_games.terrain import generate_world, world_lottery_climate
    f = generate_world(world_lottery_climate(seed, terrain=terrain, climate=climate), mode="climate")
    cap = NPPCapacityField(f, BURN, patch=(X0, Y0, PATCH), mode="tallavaara",
                           aquatic=True, enable_depletion=True)
    return per_biome(f, cap, BURN)


# ── the constructed truth: a synthetic world where the answer is arithmetic ────────────────────────────────

class _Fields:
    """Two biomes, hand-set rates, so the expected ratio is computed by hand rather than by the code."""
    def __init__(self):
        import numpy as np
        self.biome = np.full((20, 20), 2, dtype=int)      # forest
        self.biome[10:, :] = 3                            # savanna in the lower half
        self.isWater = np.zeros((20, 20), dtype=int)
        self.forage_kcal = np.where(self.biome == 2, 2000.0, 200.0)
        self.game_kcal = np.where(self.biome == 2, 4000.0, 400.0)


class _Cap:
    """Uniform capacity everywhere — so any ratio difference between biomes comes from DELIVERY alone."""
    def __init__(self, per_cell_persons):
        self._e = per_cell_persons * BURN

    def level(self, x, y):
        return self._e


def test_the_ratio_is_capacity_over_delivery_computed_by_hand():
    """forest: (2000+4000) kcal/hr * 6h * 30d / 75000 = 14.4 persons/cell; capacity 20 -> ratio 1.39
       savanna: (200+400) * 6 * 30 / 75000 = 1.44 persons/cell; capacity 20 -> ratio 13.9"""
    r = per_biome(_Fields(), _Cap(20.0), BURN, min_cells=10)
    assert r["forest"]["delivery_per_cell"] == pytest.approx(14.4, abs=0.05)
    assert r["savanna"]["delivery_per_cell"] == pytest.approx(1.44, abs=0.02)
    assert r["forest"]["ratio"] == pytest.approx(1.4, abs=0.1)
    assert r["savanna"]["ratio"] == pytest.approx(13.9, abs=0.2)


def test_a_biome_inside_the_cluster_reads_CONSISTENT_and_one_outside_reads_STARVES():
    """The verdict, not the number, is what a reader acts on. Ten times more capacity than food is a biome
    whose agents starve in a world the capacity field calls rich."""
    r = per_biome(_Fields(), _Cap(20.0), BURN, min_cells=10)
    assert r["forest"]["verdict"] in ("CONSISTENT", "OVERFEEDS")
    assert r["savanna"]["verdict"] == "STARVES"


def test_a_biome_with_more_food_than_capacity_reads_OVERFEEDS():
    """The other direction has to be nameable too, or the diagnostic only sees one failure mode."""
    r = per_biome(_Fields(), _Cap(2.0), BURN, min_cells=10)
    assert r["forest"]["ratio"] < CLUSTER_LO
    assert r["forest"]["verdict"] == "OVERFEEDS"


def test_complaints_is_EMPTY_when_every_biome_is_consistent():
    """A diagnostic that always prints is one nobody reads. Silence must mean something."""
    import numpy as np

    class Uniform(_Fields):
        def __init__(self):
            super().__init__()
            self.forage_kcal = np.full((20, 20), 1000.0)
            self.game_kcal = np.full((20, 20), 1000.0)
    # delivery = 2000*180/75000 = 4.8 persons/cell; capacity 12 -> ratio 2.5, inside the cluster
    assert complaints(per_biome(Uniform(), _Cap(12.0), BURN, min_cells=10)) == []


def test_a_biome_too_small_to_measure_is_SKIPPED_not_reported_as_broken():
    """A five-cell biome's mean is noise. Reporting it would train people to ignore the diagnostic."""
    r = per_biome(_Fields(), _Cap(20.0), BURN, min_cells=500)
    assert r == {}


# ── the real worlds: the measurement that motivated the diagnostic ────────────────────────────────────────

def test_four_biomes_cluster_and_savanna_is_the_outlier_on_a_real_world():
    """THE FINDING, on `world_savanna` as actually generated. Savanna is the dominant biome there and its two
    food models disagree by an order of magnitude."""
    r = _report("coastal", "savanna")
    assert r["savanna"]["ratio"] > 10.0, r["savanna"]
    assert r["savanna"]["verdict"] == "STARVES"
    assert r["forest"]["verdict"] == "CONSISTENT"
    assert r["grass"]["verdict"] == "CONSISTENT"


def test_the_two_outliers_are_explained_by_documented_gaps_in_the_return_rate_table():
    """Not two mysteries. Savanna's forage is a single-activity Hadza tuber rate (257.7) standing in for a
    whole diet; wetland's GAME IS ZERO because it is unanchored — the return-rate table says so in as many
    words ("a gap, not a measured zero"). The complaint text names the cause so the reader does not have to
    go looking."""
    r = _report("coastal", "savanna")
    msgs = " ".join(complaints(r))
    assert "savanna" in msgs and "forage only" in msgs
    if "wetland" in r:
        assert r["wetland"]["game_kcal_hr"] == 0.0


def test_mountain_has_zero_game_too_but_stays_CONSISTENT():
    """The control that stops "zero game" being read as the whole story. Mountain's game is equally unanchored,
    and its forage (5,387 kcal/hr) carries the biome into the cluster anyway. A missing channel only matters
    when nothing else compensates."""
    r = _report("mountainous", "savanna")
    if "mountain" in r:
        assert r["mountain"]["game_kcal_hr"] == 0.0
        assert r["mountain"]["verdict"] == "CONSISTENT", r["mountain"]


@pytest.mark.parametrize("terrain,climate", [("coastal", "temperate"), ("mountainous", "tropical")])
def test_forest_and_grass_stay_in_the_cluster_across_worlds(terrain, climate):
    """The baseline has to be stable or "outlier" means nothing. Forest and grass sit at 1.6-2.8 on every
    world measured."""
    r = _report(terrain, climate)
    for b in ("forest", "grass"):
        if b in r:
            assert CLUSTER_LO <= r[b]["ratio"] <= CLUSTER_HI, (b, r[b])
