"""R-98 — RANK unlocks HIERARCHY: a village that is actually ranked climbs the ladder.

THE GAP. `society_from_character(density, surplus_frac)` reads CROWDING and SURPLUS only — it never asks whether
anyone is ranked. So a village where every lineage is hereditary nobility is still classified
`egalitarian_forager` if it is sparse and poor. And because `LEADER_SOCIETY_WEIGHT["egalitarian_forager"]` is
0.0, that nobility has NO structural consequence: the band cannot grow past its cap, sheds no scalar stress
(Johnson 1982: hierarchy is what dissipates it), and the entire elite layer is decorative with respect to
settlement size. Measured in the wild: `ascribed_frac=1.0` sitting beside 88% of people in "egalitarian_forager"
bands, which is what the R-91 checker flags as the rank-vs-society CONTRADICTION.

THE ANCHOR SAYS RANK CAN COME FIRST. Leach's gumsa were rain-fed swidden hill farmers — no storable aquatic
glut, no great surplus — and nonetheless had ranked lineages, chiefs, tribute, and "all settlements under one
chief". Testart's storable-surplus route is ONE road to hierarchy, not the only one, so the promotion is applied
AFTER the aquatic gate rather than before it.

DELIBERATELY ONE RUNG. Rank opens the route; it does not hand out chiefdoms. `egalitarian → complex →
stratified`, and stratified is a fixed point.
"""
import pytest

from sic_games.demography import DemographyConfig, LEADER_SOCIETY_WEIGHT, society_from_character
from sic_games.phase1_model import _RANK_LADDER


def test_defaults_off():
    c = DemographyConfig()
    assert c.enable_rank_hierarchy is False and c.rank_hierarchy_frac == 0.15


def test_the_gap_is_real_the_classifier_ignores_rank():
    """THE BUG, stated as arithmetic: the classifier's inputs do not include rank, so a sparse poor village is
    'egalitarian' no matter how thoroughly ranked it is."""
    assert society_from_character(density_per_km2=0.01, surplus_frac=0.0) == "egalitarian_forager"
    # ...and in that state a leader counts for nothing at all
    assert LEADER_SOCIETY_WEIGHT["egalitarian_forager"] == 0.0


def test_ladder_promotes_exactly_one_rung():
    assert _RANK_LADDER["egalitarian_forager"] == "complex_forager"
    assert _RANK_LADDER["complex_forager"] == "stratified_chiefdom"


def test_stratified_is_a_fixed_point():
    """Rank opens the route, it does not escalate without bound — the top rung must not promote past itself."""
    assert _RANK_LADDER["stratified_chiefdom"] == "stratified_chiefdom"


def test_promotion_actually_buys_leader_weight():
    """The POINT of the change: promotion must convert into a non-zero leader weight, or nothing downstream
    changes and the fix is cosmetic."""
    before = LEADER_SOCIETY_WEIGHT["egalitarian_forager"]
    after = LEADER_SOCIETY_WEIGHT[_RANK_LADDER["egalitarian_forager"]]
    assert before == 0.0 and after > 0.0


def test_threshold_means_one_ranked_lineage_among_the_hill_2011_seven():
    """The 0.15 default is tied to a target the model already carries, not chosen freely: the FILED Hill 2011
    figure is ~7 lineages per band, so ONE ranked lineage among them is ~1/7 = 0.143 of heads."""
    c = DemographyConfig()
    hill_lineages_per_band = 7.0
    assert 1.0 / hill_lineages_per_band < c.rank_hierarchy_frac < 2.0 / hill_lineages_per_band


def test_ladder_covers_every_society_the_classifier_can_emit():
    """A missing key would raise mid-run. Enumerate the classifier's actual outputs rather than assuming three."""
    emitted = {society_from_character(d, s)
               for d in (0.0, 0.01, 1.0, 10.0, 100.0) for s in (0.0, 0.4, 0.6, 0.8, 1.0)}
    assert emitted <= set(_RANK_LADDER), f"classifier can emit {emitted - set(_RANK_LADDER)} with no ladder entry"
