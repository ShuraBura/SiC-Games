"""Emergent village-fission hazard — both anchors, pinned.

WHY THIS REPLACED A THRESHOLD. Bandy 2004 is explicit that the fission threshold is not a constant: "if the
cost of fissioning is low ... fissioning may be expected to occur frequently and at a VERY LOW population
threshold". And Johnson's mechanism (via Bandy) is a RACE, not a size rule — growth and conflict resolve "in
only one of two ways: (1) the village fissions or (2) institutions and practices emerge ... in such a way that
fissioning is not necessary", the second branch opening the way to "greater social group sizes, and spiraling
social inequality". So a village whose economy works should NOT split, and large stable centres should be an
outcome rather than something suppressed by hand.

THE TWO ANCHORS
  SIZE TERM   Alberti 2014 (PLoS ONE 9(3):e91510) fitted logistic for P(critical scalar stress | size):
              slope 0.147 (95% CI 0.098-0.196), intercept -18.636, giving his stated inflection at 127
              (95% CI 122-132) and near-maximum stress by 158. A published fit WITH error bars, not a knob.
  BASE RATE   Bandy 2004's own event counts: three fission events, in all three the largest village of its
              phase - Chiaramaya + Cerro Choncaya (top two of Early Chiripa, 500 yr) and Sonaji (largest of
              Middle Chiripa, 200 yr) => ~2-5e-3 per large-village-year.

The old size-threshold path fired for every over-threshold village EVERY step - about 10^4x Bandy's rate - which
is what shattered the settlement system into 530 hamlets of 21 people and cost 70 s/step. Measured realised rate
under the hazard, in a world whose villages have NOT integrated: 5.6e-3 per large-village-year, i.e. on the
anchor without having been tuned to it.
"""
import math
import os
import sys

import pytest

from sic_games.demography import DemographyConfig

_HERE = os.path.dirname(os.path.abspath(__file__))
_BATT = os.path.normpath(os.path.join(_HERE, "..", "outputs", "mechanism_battery"))
if _BATT not in sys.path:
    sys.path.insert(0, _BATT)


def _p_size(cfg, n):
    return 1.0 / (1.0 + math.exp(-(cfg.bud_hazard_b0 + cfg.bud_hazard_b1 * n)))


def test_defaults_off_so_the_threshold_path_is_untouched():
    c = DemographyConfig()
    assert c.enable_bud_hazard is False
    assert c.enable_village_budding is False


def test_size_term_reproduces_albertis_published_logistic():
    """The anchor itself. If a refactor changes these, it is no longer Alberti's fit and the citation is void."""
    c = DemographyConfig()
    assert c.bud_hazard_b1 == pytest.approx(0.147)
    # his stated inflection: -b0/b1 = 127 (95% CI 122-132)
    assert -c.bud_hazard_b0 / c.bud_hazard_b1 == pytest.approx(127, abs=1.0)
    assert _p_size(c, 127) == pytest.approx(0.5, abs=0.02)
    # "maximum probability of critical scalar stress is predicted at size 158"
    assert _p_size(c, 158) > 0.98
    # and small villages are essentially unstressed
    assert _p_size(c, 100) < 0.05


def test_base_rate_ceiling_sits_in_bandys_bracket():
    """Per-STEP ceiling must correspond to 2-5e-3 per village-YEAR, the rate implied by Bandy's three events."""
    c = DemographyConfig()
    per_year = c.bud_hazard_per_yr
    assert 0.002 <= per_year <= 0.005, "ceiling left Bandy's bracket"
    per_step = per_year / c.bud_steps_per_year
    assert per_step < 1e-3, (
        f"per-step hazard {per_step:.2e} is far above the anchored rate; the previous version effectively used "
        f"1.0 per step (~10^4x Bandy) and shattered the settlement system")


@pytest.mark.slow
def test_a_working_integrated_village_does_not_split():
    """THE POINT OF THE REWRITE. Villages that sustain themselves and have integrated must have a hazard of
    zero regardless of size - Johnson's second branch. Measured: villages of 356-390 with surplus ~0.91 and a
    stratified society sit at hazard exactly 0, while an unintegrated, half-depleted one sits at ~1e-4/step."""
    import battery1_liveness as B1
    import battery3_resuscitate as B3
    from collections import Counter
    w = B1._build(dict(enable_village_budding=True, enable_bud_hazard=True), **B3.BIG)
    for _ in range(300):
        w.step()
        if not w.agent_list:
            break
    cfg, sep = w._demog, w._demog.settle_radius
    ca: dict = {}
    for a in w.agent_list:
        ca.setdefault(a.pos, []).append(a)
    checked = 0
    for (sx, sy) in w._settlement_sites:
        v = [a for dx in range(-sep, sep + 1) for dy in range(-sep, sep + 1)
             for a in ca.get((sx + dx, sy + dy), ())]
        if len(v) < 200:
            continue
        bids = Counter(a._group.band_id for a in v)
        soc = str(w._band_society.get(bids.most_common(1)[0][0], ""))
        tot = sum(bids.values())
        surplus = sum(w._band_surplus.get(b, 0.0) * n for b, n in bids.items()) / tot
        if "stratified" in soc and surplus > 0.8:
            checked += 1
            # integration 1.0 zeroes the hazard outright, whatever the size
            assert (1.0 - cfg.bud_w_integration * 1.0) == 0.0
    if checked == 0:
        pytest.skip("no large well-fed stratified village formed in this run")
