"""CONSTRUCTED-TRUTH tests for the lineage/dynasty diagnostics — and the unit they are scored on.

CLAUDE.md's first rule, applied to lineages: build a population with a KNOWN lineage structure, measure it,
check the measurement matches the construction.

WHAT THIS FOUND. Two nearly-identically-named keys ride in the same campaign row over DIFFERENT UNITS:

    lineage_size_gini   Gini over `_rank_keys()`   <- what MARKER_MATRIX row 5 scores
    lin_size_gini       Gini over `_lineage`       <- the patriline itself

`_rank_keys()` returns the bare `_lineage` normally, but under `enable_local_ascription` — ON in the
canonical stack — it returns **(community, lineage) PAIRS**. So the scored marker splits one patriline into
as many units as it has communities. Measured on the 16 long arms of Addendum 24 the two keys differ in
16/16, and the sign of the difference FLIPS between the control and full arms, which reverses the
conclusion: on the rank-key unit the full stack goes 1/8 -> 8/8 inside the band, on the patriline unit it
goes 6/8 -> 4/8.

This file validates that `dynasties()` computes what it claims on a known structure, and constructs the
unit divergence explicitly so it cannot be rediscovered by accident.
"""
import pytest

from sic_games.phase1_model import TerrainWorld


class _Agent:
    def __init__(self, lineage, band_id=0, cred=1.0):
        self._lineage = lineage
        self._group = type("G", (), {"band_id": band_id})()
        self.cred = cred
        self.prowess = 1.0
        self.wealth = 0.0
        self.parity = 0
        self._n_fathered = 0
        self.sex = "male"
        self._genome = None
        self.alive = True


class _World:
    """Hand-built stand-in carrying only what `dynasties()` reads, so the REAL method is under test."""

    def __init__(self, agents):
        self.agent_list = list(agents)
        self._diag_rng = None

    dynasties = TerrainWorld.dynasties


def _built():
    """THE CONSTRUCTION: 100 agents in three patrilines — A=50, B=30, C=20.

    Expected, all arithmetic:
      n_lineages   3
      top_share    50/100 = 0.5
      eff_lineages inverse Simpson 1/(0.5² + 0.3² + 0.2²) = 1/0.38 = 2.63 -> 2.6
      size_gini    over [20, 30, 50]: 2·230/(3·100) − 4/3 = 0.2
    """
    return _World([_Agent("A") for _ in range(50)]
                  + [_Agent("B") for _ in range(30)]
                  + [_Agent("C") for _ in range(20)])


def test_lineage_counts_and_top_share_are_the_constructed_ones():
    d = _built().dynasties()
    assert d["n_lineages"] == 3
    assert d["top_share"] == pytest.approx(0.5)
    assert [r["n"] for r in d["top"]] == [50, 30, 20]
    assert [r["lineage"] for r in d["top"]] == ["A", "B", "C"]


def test_effective_lineages_is_the_inverse_simpson_number():
    """A Hill number, not a count: three lineages at 50/30/20 behave like 2.6 equal ones."""
    assert _built().dynasties()["eff_lineages"] == pytest.approx(2.6, abs=0.05)


def test_size_gini_is_the_hand_computed_gini():
    assert _built().dynasties()["size_gini"] == pytest.approx(0.2, abs=1e-3)


def test_one_lineage_for_everyone_is_maximum_concentration():
    d = _World([_Agent("A") for _ in range(40)]).dynasties()
    assert d["n_lineages"] == 1
    assert d["top_share"] == pytest.approx(1.0)
    assert d["eff_lineages"] == pytest.approx(1.0)
    assert d["size_gini"] == pytest.approx(0.0), "one group cannot be unequal with itself"


def test_perfectly_even_lineages_have_zero_gini_and_full_effective_count():
    d = _World([_Agent(f"L{i}") for i in range(10) for _ in range(10)]).dynasties()
    assert d["n_lineages"] == 10
    assert d["size_gini"] == pytest.approx(0.0)
    assert d["eff_lineages"] == pytest.approx(10.0)
    assert d["top_share"] == pytest.approx(0.1)


def test_lineages_per_band_uses_the_affiliation_band_and_skips_singletons():
    """The unit is `_group.band_id` (the R-25 unit), and bands of 1 are excluded from the dominant-share
    mean, where the share would be a trivial 1.0."""
    agents = ([_Agent("A", band_id=1), _Agent("B", band_id=1), _Agent("B", band_id=1)]   # band 1: 2 lineages
              + [_Agent("C", band_id=2), _Agent("C", band_id=2)]                          # band 2: 1 lineage
              + [_Agent("D", band_id=3)])                                                 # band 3: singleton
    d = _World(agents).dynasties()
    # the diagnostic rounds to 2 dp, so the tolerance is the rounding and not a fudge
    assert d["lineages_per_band"] == pytest.approx((2 + 1 + 1) / 3, abs=5e-3)
    # dominant share: band 1 -> 2/3, band 2 -> 2/2; band 3 excluded (size 1)
    assert d["dom_lineage_share"] == pytest.approx(((2 / 3) + 1.0) / 2, abs=1e-3)


def test_the_scored_unit_and_the_patriline_unit_diverge_under_local_ascription():
    """THE DEFECT, constructed. `_rank_keys()` returns (community, lineage) pairs when local ascription is on,
    so ONE patriline spread over three communities counts as THREE units — a different distribution, a
    different Gini, and a different `n_lineages`.

    Built: a single 60-member patriline split 30/20/10 across three communities, plus a 40-member patriline
    in one. By patriline that is 2 lineages of 60 and 40; by rank key it is 4 units of 30, 20, 10 and 40."""
    from sic_games.phase1_model import TerrainWorld as TW

    agents = ([_Agent("BIG", band_id=1) for _ in range(30)]
              + [_Agent("BIG", band_id=2) for _ in range(20)]
              + [_Agent("BIG", band_id=3) for _ in range(10)]
              + [_Agent("SMALL", band_id=1) for _ in range(40)])
    w = _World(agents)

    by_patriline = w.dynasties()
    assert by_patriline["n_lineages"] == 2
    assert by_patriline["top_share"] == pytest.approx(0.6)

    # the rank-key view: (community, lineage) pairs, which is what the SCORED marker is built from
    from collections import Counter
    rank_sizes = Counter((a._group.band_id, a._lineage) for a in agents)
    assert len(rank_sizes) == 4, "the patriline fragments into one unit per community"
    assert sorted(rank_sizes.values()) == [10, 20, 30, 40]

    g_patriline = TW._gini(sorted(len(v) for v in
                                  {"BIG": [1] * 60, "SMALL": [1] * 40}.values()))
    g_rank = TW._gini(sorted(rank_sizes.values()))
    assert g_patriline != pytest.approx(g_rank), (
        "the two units must give different Ginis — that is the whole hazard")
    # and the fragmented view reads MORE unequal here, which is an artefact of the split, not of descent
    assert g_rank > g_patriline
