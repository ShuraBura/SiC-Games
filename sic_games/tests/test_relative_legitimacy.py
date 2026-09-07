"""R-93 — RELATIVE legitimacy: the crossing test must mean the same thing at any lineage diversity.

THE BUG IT FIXES, stated as arithmetic. Ascription fires when a lineage's SHARE of its band's feasting exceeds
`legit_threshold`. A share has a hidden denominator: the mean share is 1/lineages_per_band. So the test
discriminates only while

    lineages_per_band  >  1 / legit_threshold

At the campaign's 0.15 that boundary is 6.67, against a FILED Hill 2011 target of ~7 — a five percent margin.
Nobody ever changed the parameter; the substrate drifted under it (measured lineages_per_band 2.14–3.69), and
below the boundary the AVERAGE lineage clears the bar, so "nobility" becomes universal by arithmetic rather
than by competition. R-92 confirmed a healthier substrate does not rescue it — the R-91 DOMAIN violation still
fires at step ~650 with segmentation on.

This is a whole BUG CLASS, not one parameter: any threshold applied to a share or a ratio carries an implicit
denominator and therefore a validity domain, and will fail SILENTLY when the denominator moves. The fix is to
make the comparison relative — 1.0 means "exactly what an average lineage contributed" — which is Friedman's
logic anyway: *"one lineage convinces all the others"* is about standing out from your neighbours, not about
clearing a fixed bar.
"""
import pytest

from sic_games.demography import DemographyConfig


def _crossing_fraction(n_lineages, spends, thr, relative):
    """Replicate the crossing arithmetic exactly as `_do_legitimacy` performs it, for ONE band, at equilibrium
    (the EMA has converged, so the stock equals the per-step value). Kept as pure arithmetic rather than a world
    so the diversity can be dialled directly — the property under test is a property of the FORMULA."""
    total = float(sum(spends))
    assert len(spends) == n_lineages
    crossed = 0
    for s in spends:
        share = s / total
        if relative:
            share *= n_lineages          # 1.0 == an exactly average lineage
        if share > thr:
            crossed += 1
    return crossed / n_lineages


def _even_ish(n):
    """A mildly unequal band: one sponsor at double the others, the rest equal."""
    return [2.0] + [1.0] * (n - 1)


def _standout_at(n, rel):
    """A band where ONE lineage sits at exactly `rel` times the average share, the rest sharing the remainder.

    NEEDED because `_even_ish` does NOT hold relative standing constant, and the first cut of the invariance
    test used it and failed on a working mechanism. With one sponsor at double the rest, total = n+1, so the
    standout's relative share is 2n/(n+1) — 1.50 at n=3, 1.82 at n=10, tending to 2.0. A fixed SPEND ratio is
    not a fixed RELATIVE standing, because the standout inflates the very total it is measured against. That is
    the same hidden-denominator trap this whole result is about, reappearing inside its own test fixture."""
    assert n >= 2 and 0 < rel < n
    top = rel / n
    return [top] + [(1.0 - top) / (n - 1)] * (n - 1)


def test_defaults_off():
    c = DemographyConfig()
    assert c.enable_relative_legitimacy is False and c.legit_rel_multiplier == 2.0


@pytest.mark.parametrize("n", [3, 5, 7, 10, 20])
def test_absolute_threshold_degenerates_as_diversity_falls(n):
    """THE BUG. With the absolute test at 0.15, every lineage crosses once the band holds fewer than 1/0.15 =
    6.67 lineages — nobody won anything, the bar sank below the floor."""
    frac = _crossing_fraction(n, _even_ish(n), thr=0.15, relative=False)
    if n < 6.67:
        assert frac == 1.0, f"expected total degeneracy at {n} lineages, got {frac}"
    else:
        assert frac < 1.0


@pytest.mark.parametrize("n", [3, 5, 7, 10, 20])
def test_relative_threshold_is_invariant_to_diversity(n):
    """THE FIX. A lineage held at a FIXED relative standing (1.8x the average) must cross, and the rest must
    not — at EVERY diversity. This is exactly the property the absolute test lacks."""
    frac = _crossing_fraction(n, _standout_at(n, 1.8), thr=1.5, relative=True)
    assert frac == pytest.approx(1.0 / n), f"crossing fraction moved with diversity at n={n}: {frac}"


def test_relative_threshold_still_discriminates_at_the_collapse_point():
    """The measured campaign regime — 2 to 4 lineages per band. On an EVEN band (nobody stands out at all) the
    absolute test ascribes EVERYONE, purely because 1/n exceeds 0.15; the relative test correctly ascribes
    nobody. Even is the right fixture here: the degeneracy claim is that the AVERAGE lineage clears the bar, and
    on a very lopsided band the weak lineages can fall under 0.15 on their own and mask it."""
    for n in (2, 3, 4):
        assert _crossing_fraction(n, [1.0] * n, thr=0.15, relative=False) == 1.0, \
            f"absolute test failed to degenerate at n={n}"
        assert _crossing_fraction(n, [1.0] * n, thr=1.5, relative=True) == 0.0, \
            f"relative test invented nobility on an even band at n={n}"


def test_relative_threshold_can_still_ascribe_nobody():
    """A band where every lineage contributes equally has no standout, so nobody may cross — the mechanism must
    be able to return NO nobility, or it is not measuring anything."""
    for n in (3, 7, 15):
        assert _crossing_fraction(n, [1.0] * n, thr=1.5, relative=True) == 0.0


def test_relative_threshold_can_still_ascribe_a_dominant_lineage():
    """And it must still fire when one lineage genuinely dominates — the fix must not simply suppress everything."""
    spends = [50.0] + [1.0] * 9
    assert _crossing_fraction(10, spends, thr=1.5, relative=True) == pytest.approx(0.1)


def test_the_boundary_is_where_the_arithmetic_says_it_is():
    """Pins the 1/threshold boundary itself, so the DOMAIN rule in sic_games.invariants and this fix cannot
    drift apart silently."""
    thr = 0.15
    boundary = 1.0 / thr
    assert boundary == pytest.approx(6.667, abs=1e-3)
    just_below, just_above = 6, 7
    assert _crossing_fraction(just_below, [1.0] * just_below, thr=thr, relative=False) == 1.0
    assert _crossing_fraction(just_above, [1.0] * just_above, thr=thr, relative=False) == 0.0
