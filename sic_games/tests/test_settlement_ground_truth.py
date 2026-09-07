"""CONSTRUCTED-TRUTH tests for the settlement diagnostics: build a map with a known distribution, measure it.

CLAUDE.md's first rule, applied to villages. Two different "village" notions ride in the same campaign
trajectory row and nothing said so:

    run_campaign.py:186   villages = [n for n in band_sizes if n > BAND_SPLIT]   -> n_villages, village_med
    phase1_model.settlements()                                                   -> n_settle, settle_med

The first is *a band with more than 45 members* — a social unit of any spatial extent. The second is *a
registered settlement site*. They are not the same thing, they do not have to move together, and
`settle_med` is what MARKER_MATRIX scores against Bar-Yosef's 50-150. (An analysis on 2026-08-04 used
`n_villages` as an aggregation proxy while reading it as settlements.)

A second definitional fact, invisible from the name: `settlements()` counts agents whose position IS the site
cell (`a.pos in sites`), NOT agents within the settlement's catchment radius. `settle_catchment_radius` is
used for YIELD, not for membership. So a settlement's size is its on-cell occupancy — at 100 km²/cell that is
a defensible definition of a village, but it is a definition, and a marker scored against an ethnographic
village size depends on it.

Everything below is placed by hand and asserted against the construction, element by element.
"""
import pytest

from sic_games.phase1_model import TerrainWorld


class _Agent:
    def __init__(self, pos, band_id=0, lineage=1, cred=1.0):
        self.pos = pos
        self._group = type("G", (), {"band_id": band_id})()
        self._lineage = lineage
        self.cred = cred
        self.alive = True


class _World:
    """A hand-built stand-in carrying only what `settlements()` reads, so the REAL method is under test."""

    def __init__(self, sites, agents):
        self._settlement_sites = list(sites)
        self.agent_list = list(agents)
        self._band_society = {}

    def _settlement_catchment_yield(self, s):
        return 0.0

    settlements = TerrainWorld.settlements


def _built():
    """THE CONSTRUCTION, stated once so every assertion below can be read against it.

        site (10,10)  80 agents ON the cell     <- largest
        site (20,20)  40 agents ON the cell
        site (30,30)  20 agents ON the cell     <- smallest
        (11,10)       25 agents ADJACENT to the first site, inside a radius-1 catchment, NOT on the cell
        (50,50)       15 agents nowhere near a site
        site (40,40)  registered but EMPTY

    Expected: 3 settlements (the empty site drops out), sizes [80, 40, 20], median 40, max 80,
    primate 80/40 = 2.0. The 25 adjacent and 15 distant agents are counted by nothing.
    """
    agents = ([_Agent((10, 10)) for _ in range(80)]
              + [_Agent((20, 20)) for _ in range(40)]
              + [_Agent((30, 30)) for _ in range(20)]
              + [_Agent((11, 10)) for _ in range(25)]
              + [_Agent((50, 50)) for _ in range(15)])
    return _World([(10, 10), (20, 20), (30, 30), (40, 40)], agents)


def test_settlements_finds_exactly_the_sites_that_were_populated():
    st = _built().settlements()
    assert st["n"] == 3, "the registered but EMPTY site (40,40) must not appear"
    assert [q["n"] for q in st["panel"]] == [80, 40, 20]
    assert [q["pos"] for q in st["panel"]] == [(10, 10), (20, 20), (30, 30)]


def test_settlement_size_is_ON_CELL_occupancy_not_the_catchment():
    """THE DEFINITION, pinned. 25 agents sit one cell from the largest site — inside a radius-1 catchment —
    and are NOT counted. If this ever starts failing, `settle_med`'s meaning has changed and every score
    against Bar-Yosef [50-150] has to be re-read."""
    st = _built().settlements()
    biggest = st["panel"][0]
    assert biggest["pos"] == (10, 10)
    assert biggest["n"] == 80, "adjacent agents were counted — membership is no longer on-cell"
    assert st["max"] == 80


def test_median_and_max_are_the_constructed_ones():
    st = _built().settlements()
    assert st["max"] == 80
    assert st["median"] == 40          # median of [80, 40, 20]
    assert st["primate_ratio"] == pytest.approx(2.0)   # 80 / 40


def test_rank_size_statistics_need_enough_sites_and_say_so():
    """primate_ratio needs 2 sites and zipf_slope needs 3 — below that they are None, never a fake number."""
    one = _World([(1, 1)], [_Agent((1, 1)) for _ in range(10)]).settlements()
    assert one["n"] == 1 and one["primate_ratio"] is None and one["zipf_slope"] is None
    two = _World([(1, 1), (2, 2)],
                 [_Agent((1, 1)) for _ in range(10)] + [_Agent((2, 2)) for _ in range(5)]).settlements()
    assert two["primate_ratio"] == pytest.approx(2.0) and two["zipf_slope"] is None
    assert _built().settlements()["zipf_slope"] < 0.0, "a declining rank-size curve must have a negative slope"


def test_no_sites_returns_empty_rather_than_zeros():
    """An empty result must be distinguishable from 'measured, and it was zero'."""
    assert _World([], [_Agent((1, 1))]).settlements() == {}
    assert _World([(9, 9)], [_Agent((1, 1))]).settlements() == {}, "sites with no occupants ⇒ nothing measured"


def test_the_two_village_notions_disagree_on_the_same_world():
    """THE POINT OF THIS FILE. `village_med` counts BANDS over 45; `settle_med` counts SETTLEMENT SITES. Built
    so they cannot be confused: one 60-member band spread across two sites, and three sites whose occupants
    belong to many small bands.

    Constructed: band 7 has 60 members (a 'village' by the band rule) split 40/20 across two sites; every
    other agent is in a band of 10. So the band rule sees ONE village of 60, and the settlement rule sees
    THREE settlements of 40, 20 and 30."""
    BAND_SPLIT = 45
    agents = ([_Agent((10, 10), band_id=7) for _ in range(40)]      # band 7, on site A
              + [_Agent((20, 20), band_id=7) for _ in range(20)]    # band 7, on site B
              + [_Agent((30, 30), band_id=i // 10) for i in range(30)])   # 3 bands of 10, on site C
    w = _World([(10, 10), (20, 20), (30, 30)], agents)
    st = w.settlements()

    from collections import Counter
    band_sizes = Counter(a._group.band_id for a in agents)
    villages_by_band = [n for n in band_sizes.values() if n > BAND_SPLIT]

    assert villages_by_band == [60], "the band rule should see exactly one 'village', of 60"
    assert st["n"] == 3, "the settlement rule should see three sites"
    assert sorted(q["n"] for q in st["panel"]) == [20, 30, 40]
    # The two medians are different numbers about different things — which is the whole hazard.
    assert st["median"] == 30
    assert villages_by_band[0] != st["median"]
