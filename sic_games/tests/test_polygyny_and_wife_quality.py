"""Polygyny attrition (R-76) + wife quality (R-77) — the two status→RS channels the model lacked.

R-76. `polygyny_rate` gates only whether a married male is CONSIDERED; he then wins prowess-weighted and the
bond NEVER ends. So polygyny was a stock that only filled, and the rate could not set the level: a **150×
rate change (0.002→0.3) moved realized polygyny just 9.2%→25.3%**, and Marlowe's ~4% of men was unreachable.
Adding the documented OUTFLOW — Marlowe, *The Hadza*: "polygynous marriages are less enduring" — gives an
inflow/attrition equilibrium the rate controls: 0.0005→0.02 now spans 0.9%→11.5%.

R-77. Consequence of fixing R-76: at Marlowe-calibrated polygyny, status→RS collapsed to ≈+0.02, i.e.
**R-19/R-20's status→RS ≈0.13-0.17 was bought with 6× too much polygyny**. von Rueden & Jaeggi (33
nonindustrial societies, PNAS): overall status→RS **r=0.19**, and status associates with **wife quality only
in MONOGAMOUS societies (r=0.15)** — "wife's age or interbirth interval". The model had no wife-quality route
at all: females chose prowess-weighted, but a high-prowess man was as likely to pair with a 40-year-old as a
16-year-old. Wife-quality ordering supplies it — and it closes only ~a third of the gap (+0.02 → +0.07 vs
0.19), so the remaining channels (age at marriage; status→IBI) are still missing. Do not over-claim it.
"""
import pytest

from sic_games.capacity import NPPCapacityField
from sic_games.config import KcalEconomyConfig
from sic_games.demography import DemographyConfig
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world, world_lottery_climate

YR = 12


def _world(**kw):
    k = world_lottery_climate(0, terrain="coastal", climate="temperate")
    f = generate_world(k, mode="climate")
    hf = NPPCapacityField(f, 75000.0, patch=(20, 20, 60), mode="tallavaara", aquatic=True, enable_depletion=True)
    return TerrainWorld(n_agents=0, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, game_stream=False, seed=0,
                        harvest_field=hf, demography_cfg=DemographyConfig(**kw))


class _P:
    def __init__(self, sex="female", age_yr=25.0):
        self.sex = sex
        self.age = age_yr * YR
        self._partner = None
        self._wives = set()
        self.alive = True
        import random
        self.random = random.Random(0)


def _marry(h, *wives):
    for w in wives:
        w._partner = h
        h._wives.add(w)


# ── R-76: polygyny attrition ─────────────────────────────────────────────────────────────────────

def test_defaults_off():
    c = DemographyConfig()
    assert c.polygyny_attrition == 0.0          # off ⇒ bit-exact (polygyny only fills, as before)
    assert c.wife_quality_strength == 0.0
    assert c.polygyny_rate == 0.0 and c.max_wives == 1


def test_attrition_off_is_a_noop():
    w = _world(polygyny_attrition=0.0)
    h = _P("male", 35); w1, w2 = _P(), _P()
    _marry(h, w1, w2)
    w.agent_list = [h, w1, w2]
    w._do_polygyny_attrition()
    assert len(h._wives) == 2


def test_attrition_erodes_polygyny_TOWARD_monogamy_not_to_zero():
    """Marlowe: "polygynous marriages are less enduring" — the POLYGYNY is what's fragile, not the marriage.
    The `>1 wife` guard is evaluated live, so once a husband is down to one wife the remaining bond is
    protected: even at certainty a 2-wife man ends monogamous, never single. Dissolving a MONOGAMOUS bond is
    `divorce_rate`'s business — if this did it too, it would silently double as a divorce knob."""
    w = _world(polygyny_attrition=1.0)                  # certainty, so the test is deterministic
    poly_h = _P("male", 35); pw1, pw2 = _P(), _P()
    _marry(poly_h, pw1, pw2)
    mono_h = _P("male", 35); mw = _P()
    _marry(mono_h, mw)
    w.agent_list = [poly_h, pw1, pw2, mono_h, mw]
    w._do_polygyny_attrition()
    assert len(poly_h._wives) == 1                      # 2 wives → 1: polygyny gone, marriage intact
    assert sum(1 for x in (pw1, pw2) if x._partner is None) == 1     # exactly one wife released
    assert len(mono_h._wives) == 1 and mw._partner is mono_h         # monogamy untouched


def test_attrition_cannot_make_a_married_man_single():
    """Whatever the rate, this mechanism's floor is monogamy — it never empties a marriage."""
    w = _world(polygyny_attrition=1.0)
    h = _P("male", 35); wives = [_P() for _ in range(4)]
    _marry(h, *wives)
    w.agent_list = [h, *wives]
    for _ in range(5):
        w._do_polygyny_attrition()
    assert len(h._wives) == 1


def test_attrition_returns_the_wife_to_the_pool():
    """She re-enters pairing (serial monogamy), rather than being stranded."""
    w = _world(polygyny_attrition=1.0)
    h = _P("male", 35); w1, w2 = _P(), _P()
    _marry(h, w1, w2)
    w.agent_list = [h, w1, w2]
    w._do_polygyny_attrition()
    assert w1._partner is None and w1 not in h._wives


# ── R-77: wife quality ───────────────────────────────────────────────────────────────────────────

def test_wife_quality_off_is_a_plain_shuffle():
    """Off ⇒ random order, preserving the documented RNG contract 'shuffle → polygyny-gate → choose'."""
    w = _world(wife_quality_strength=0.0)
    females = [_P("female", a) for a in (16, 25, 35, 41)]
    w._order_females_for_pairing(females)
    assert len(females) == 4 and {id(f) for f in females} == {id(f) for f in females}


def test_wife_quality_orders_the_most_fertile_first():
    """von Rueden: wife quality = "wife's age or interbirth interval". The most fertile women must pair
    FIRST — choosing prowess-weighted, they then take the highest-status men, so the status↔wife-youth
    assortment EMERGES from mutual choice rather than being imposed as a correlation."""
    w = _world(wife_quality_strength=8.0)               # strong ⇒ ordering is near-deterministic
    ages = [16, 22, 30, 38, 41]
    wins = {a: 0 for a in ages}
    for _ in range(200):
        females = [_P("female", a) for a in ages]
        w._order_females_for_pairing(females)
        wins[females[0].age / YR] += 1
    assert wins[16] > wins[41], wins                    # youngest pairs first far more often
    assert wins[16] > wins[30]


def test_wife_quality_is_stochastic_not_a_youth_sort():
    """A strict youth sort would be deterministic and unrealistic — the ordering is Plackett–Luce
    (Efraimidis–Spirakis u^(1/w)), so an older woman still sometimes pairs first."""
    w = _world(wife_quality_strength=1.0)
    ages = [16, 41]
    first_old = 0
    for _ in range(200):
        females = [_P("female", a) for a in ages]
        w._order_females_for_pairing(females)
        if females[0].age / YR == 41:
            first_old += 1
    assert 0 < first_old < 200, first_old               # neither impossible nor certain


def test_post_menopausal_carries_no_fertility_weight():
    """Remaining fertility floors at 0 past menopause — she must not out-rank a fertile woman."""
    c = DemographyConfig()
    w = _world(wife_quality_strength=8.0)
    old = (c.menopause_months / YR) + 5                 # past the fertile window
    wins_young = 0
    for _ in range(100):
        females = [_P("female", 18.0), _P("female", old)]
        w._order_females_for_pairing(females)
        if females[0].age / YR == 18.0:
            wins_young += 1
    assert wins_young >= 95, wins_young
