"""R-91 — the consistency checker, validated against the REAL failures it was built from.

D1 applied to the instrument itself: every rule here is first exercised on a reconstruction of an actual
observed failure (the positive control), and then on a healthy trajectory that must stay silent (the null).
A checker that has only ever been tested on invented inputs is not evidence about anything.
"""
from sic_games.invariants import check, first_violations, STUCK_WINDOW, FROZEN_WINDOW, ABSORBING_WINDOW

ELITE_CFG = {"legit_threshold": 0.15}


def _healthy(n=60):
    """A trajectory with no contradiction: rank and society agree, the share test still discriminates,
    reversions keep firing, nothing pinned."""
    return [dict(step=100 + 25 * i, ascribed_frac=0.20 + 0.01 * (i % 7), pct_stratified=30.0 + (i % 5),
                 lineages_per_band=9.0 + 0.1 * (i % 4), cum_reversions=10 * i,
                 frac_gumsa=0.4 + 0.01 * (i % 6), leader_tenure_yr=8.0 + 0.1 * (i % 5),
                 n_lineages=120 - (i % 11))
            for i in range(n)]


def test_healthy_trajectory_is_silent():
    """THE NULL. If this fires, every positive below is uninterpretable."""
    assert check(_healthy(), ELITE_CFG) == []


def test_catches_rank_vs_society_contradiction():
    """POSITIVE CONTROL — the real one: ascribed_frac=1.0 printed beside pct_stratified=11.5 for hours."""
    rows = _healthy()
    rows[-1] = dict(rows[-1], ascribed_frac=1.0, pct_stratified=11.5)
    codes = {v.code for v in check(rows, ELITE_CFG)}
    assert "rank-vs-society" in codes


def test_rank_and_society_agreeing_is_silent():
    """The same high ascription is FINE when the societies are correspondingly ranked — the rule must key on
    the contradiction, not on high ascription alone."""
    rows = _healthy()
    rows[-1] = dict(rows[-1], ascribed_frac=1.0, pct_stratified=80.0)
    assert "rank-vs-society" not in {v.code for v in check(rows, ELITE_CFG)}


def test_catches_degenerate_share_threshold():
    """POSITIVE CONTROL — measured lineages_per_band 2.14 against legit_threshold 0.15 (needs > 6.67)."""
    rows = _healthy()
    rows[-1] = dict(rows[-1], lineages_per_band=2.14)
    v = [x for x in check(rows, ELITE_CFG) if x.code == "share-threshold-degenerate"]
    assert v and "6.67" in v[0].message


def test_share_threshold_silent_above_the_domain():
    rows = _healthy()
    rows[-1] = dict(rows[-1], lineages_per_band=7.0)          # just above 1/0.15
    assert "share-threshold-degenerate" not in {v.code for v in check(rows, ELITE_CFG)}


def test_share_threshold_needs_the_config():
    """Without the threshold it cannot know the domain — it must stay silent rather than guess."""
    rows = _healthy()
    rows[-1] = dict(rows[-1], lineages_per_band=2.14)
    assert "share-threshold-degenerate" not in {v.code for v in check(rows, {})}


def test_catches_frozen_reversion_counter():
    """POSITIVE CONTROL — cum_reversions sat at 4269 for 5,650 steps while ascription was saturated. Read at
    one timepoint it looks like a large number, which is exactly how it was misread."""
    rows = _healthy()
    for i in range(-FROZEN_WINDOW, 0):
        rows[i] = dict(rows[i], cum_reversions=4269, ascribed_frac=1.0)
    assert "reversions-frozen" in {v.code for v in check(rows, ELITE_CFG)}


def test_frozen_counter_silent_when_nothing_to_revert():
    """No ascription anywhere ⇒ zero reversions is correct, not a failure."""
    rows = _healthy()
    for i in range(-FROZEN_WINDOW, 0):
        rows[i] = dict(rows[i], cum_reversions=0, ascribed_frac=0.0)
    assert "reversions-frozen" not in {v.code for v in check(rows, ELITE_CFG)}


def test_catches_pinned_field_and_names_the_bound():
    rows = _healthy()
    for i in range(-STUCK_WINDOW, 0):
        rows[i] = dict(rows[i], ascribed_frac=1.0)
    v = [x for x in check(rows, ELITE_CFG) if x.code == "ascribed_frac-stuck"]
    assert v and "BOUND" in v[0].message


def test_catches_absorbing_lineage_count():
    """POSITIVE CONTROL — n_lineages fixed at exactly 5 for 5,650 steps."""
    rows = _healthy(ABSORBING_WINDOW + 5)
    for i in range(-ABSORBING_WINDOW, 0):
        rows[i] = dict(rows[i], n_lineages=5)
    assert "lineages-absorbing" in {v.code for v in check(rows, ELITE_CFG)}


def test_first_violations_reports_the_earliest_step():
    """The whole value proposition is EARLINESS — report when it would have complained, not merely that it does."""
    rows = _healthy()
    rows[30] = dict(rows[30], ascribed_frac=1.0, pct_stratified=11.5)
    got = first_violations(rows, ELITE_CFG)
    assert got["rank-vs-society"]["step"] == rows[30]["step"]


def test_tolerates_missing_fields():
    """Older archived trajectories predate these fields; the checker must not crash on them."""
    rows = [dict(step=25 * i, pop=1000) for i in range(50)]
    assert check(rows, ELITE_CFG) == []
