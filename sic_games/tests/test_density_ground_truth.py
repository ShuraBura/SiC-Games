"""CONSTRUCTED-TRUTH tests for the occupied-cell density and the Hayden band it drives.

CLAUDE.md's first rule, applied to density: place a known population over a known area, and check the
diagnostic returns what was placed.

WHAT THIS PINS. `density_occupied_per_km2` = `n / (len(_cells) * _CELL_KM2)` divides by the cells that are OCCUPIED, not by the
territory. So it is a LOCAL CROWDING measure — mean occupancy per settled cell — and NOT a regional
population density. That distinction is load-bearing because `hayden_stage` classifies the result against
Hayden 1995 Fig. 6's transegalitarian bands, and those are regional densities of people per km² of land.

The consequence, constructed below: the SAME 100 people over the SAME region classify as "entrepreneur" when
clustered on one cell and "egalitarian" when spread over a hundred — the two ends of Hayden's scale, from
clustering alone. A model whose central dynamic is agglomeration will therefore drift up Hayden's ladder
without the region gaining a single person.

MEASURED CONSEQUENCE on eight long arms: the occupied measure runs 1.7-20x (median 2.3x) above the
regional one and moves the Hayden band in 6 of 8. The campaign row now carries BOTH —
`density_occupied_per_km2` for local crowding and `density_regional_per_km2` over habitable land — and
scores `hayden_stage` on the regional one, which is what the anchors measure.
"""
import pytest

from sic_games.phase1_model import _CELL_KM2, TerrainWorld


class _Agent:
    def __init__(self, pos):
        self.pos = pos
        self.age = 12 * 25          # an adult, so the age markers have something to chew on
        self.sex = "female"
        self._partner = None
        self._wives = set()
        self._mother = None
        self._father = None
        self.alive = True
        self.material = 0.0
        self.aggrandizer = 0.0
        self.wealth = 0.0
        self.cred = 1.0


def _dens(pop):
    return TerrainWorld._demog_markers(TerrainWorld, pop)["density_occupied_per_km2"]


def _stage(pop):
    return TerrainWorld._demog_markers(TerrainWorld, pop)["hayden_stage_occupied"]


def test_cell_area_is_the_documented_hundred_km2():
    assert _CELL_KM2 == 100.0, "the whole density scale rests on this"


def test_density_is_population_over_OCCUPIED_cells():
    """100 agents on ONE cell ⇒ 100 / (1 × 100 km²) = 1.0 per km², exactly."""
    assert _dens([_Agent((5, 5)) for _ in range(100)]) == pytest.approx(1.0)


def test_the_same_population_spread_wider_reads_a_hundred_times_lower():
    """100 agents on 100 distinct cells ⇒ 100 / (100 × 100 km²) = 0.01 per km², exactly."""
    spread = [_Agent((i % 10, i // 10)) for i in range(100)]
    assert len({a.pos for a in spread}) == 100
    assert _dens(spread) == pytest.approx(0.01)


def test_empty_land_between_agents_is_invisible_to_the_denominator():
    """THE DEFINITION, stated as a fact. Two agents 90 cells apart occupy 2 cells, so the denominator is
    200 km² — the ~9000 km² of empty land between them does not enter. A regional density would be ~0.0002
    per km²; this reads 0.01, fifty times higher."""
    far = [_Agent((0, 0)), _Agent((90, 90))]
    assert _dens(far) == pytest.approx(2 / (2 * _CELL_KM2))
    assert _dens(far) == pytest.approx(0.01)


def test_clustering_alone_moves_the_population_across_HAYDEN_S_WHOLE_SCALE():
    """The consequence that matters. The SAME 100 people, the SAME region, classified at opposite ends of
    Hayden 1995 Fig. 6 by how they are arranged — because the denominator follows the arrangement.

    `hayden_stage` is the stratification-stage benchmark, and this model's central dynamic is agglomeration.
    """
    clustered = [_Agent((5, 5)) for _ in range(100)]
    spread = [_Agent((i % 10, i // 10)) for i in range(100)]
    assert _stage(clustered) == "entrepreneur"      # 1.0/km² — Hayden's 1.0-10.0 band
    assert _stage(spread) == "egalitarian"          # 0.01/km² — Hayden's .01-<.1 band
    assert len(clustered) == len(spread)


@pytest.mark.parametrize("dens,expected", [
    (0.005, "sub-egalitarian"), (0.01, "egalitarian"), (0.099, "egalitarian"),
    (0.1, "despot"), (0.19, "despot"), (0.2, "reciprocator"), (0.99, "reciprocator"),
    (1.0, "entrepreneur"), (9.99, "entrepreneur"), (10.0, "above-Hayden-range"),
])
def test_hayden_band_edges_are_where_the_paper_puts_them(dens, expected):
    """Fig. 6 (p.77), verified from the page image: Egalitarian .01-<.1 · Despots .1-.2 ·
    Reciprocators .2-1.0 · Entrepreneurs 1.0-10.0. Half-open upward at each edge."""
    assert TerrainWorld._hayden_stage(dens) == expected


def test_a_single_agent_is_a_hundredth_of_a_person_per_km2():
    """The floor case: one agent on one cell is 1/100 km² = 0.01, which is the BOTTOM of Hayden's egalitarian
    band. So no non-empty population can ever read `sub-egalitarian` under this definition — a band that
    exists in the classifier and is unreachable in practice."""
    assert _dens([_Agent((3, 3))]) == pytest.approx(0.01)
    assert _stage([_Agent((3, 3))]) == "egalitarian"


def test_density_is_nan_not_zero_for_an_empty_population():
    """A missing denominator must never read as a real measurement of zero."""
    m = TerrainWorld._demog_markers(TerrainWorld, [])
    assert m == {"n": 0}, "an empty group must report nothing measured, not zeros"
