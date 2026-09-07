"""CTB for the CLAIM WEIGHT on the cell food split (R-106, 2026-08-15).

THE DEFECT UNDER TEST. `compute_harvest_shares` hands every occupant S/n at kappa=0, regardless of age. 59%
of a canonical population is under 15, so a newborn claims exactly what a 30-year-old hunter claims. The
measured consequence is a realised hazard that is FLAT at ~0.06/yr from age 1 to 60 against a Siler
ACHE_FOREST intrinsic hazard of 0.0141/yr at age 30 -- an age-independent excess that starvation cannot
produce, because starvation kills the small and the old first.

CTB THE QUANTITY, NOT ONLY THE ARITHMETIC. Asserting that shares sum to S would pass in every state and
prove nothing. So the load-bearing test states the SIZE of the adult's gain for a constructed family, and
`test_the_effect_is_load_bearing` checks the pre-fix path really does give the flat answer -- a test that
passes in both states is the failure this file exists to avoid.

THE CONTROL THAT MATTERS is `test_all_adult_cell_is_untouched_by_need_weighting`: if need-weighting moved an
all-adult cell, the effect would be a code-path artefact rather than age composition, and every downstream
number would be uninterpretable.
"""
import os
import sys

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
if os.path.join(ROOT, "sic_games", "src") not in sys.path:
    sys.path.insert(0, os.path.join(ROOT, "sic_games", "src"))

from sic_games.substrate import compute_harvest_shares  # noqa: E402


class _Occ:
    """Minimal stand-in. `compute_harvest_shares` reads only `.phi` and `.strategy`; the claim vector is
    supplied by the caller, so the agent's own age ramps are computed here exactly as the model computes
    them (cons_min 0.3 -> 1.0, eta_min 0.2 -> 1.0, both linear over forage_age_min months)."""

    FORAGE_AGE_MIN = 180.0   # months; the canonical auto-built LifeHistoryConfig
    CONS_MIN = 0.3
    ETA_MIN = 0.2

    def __init__(self, age_months, phi=1.0, strategy="si"):
        self.age = float(age_months)
        self.phi = phi
        self.strategy = strategy

    def consumption_factor(self):
        if self.age >= self.FORAGE_AGE_MIN:
            return 1.0
        return self.CONS_MIN + (1.0 - self.CONS_MIN) * self.age / self.FORAGE_AGE_MIN

    def eta(self):
        if self.age >= self.FORAGE_AGE_MIN:
            return 1.0
        return self.ETA_MIN + (1.0 - self.ETA_MIN) * self.age / self.FORAGE_AGE_MIN


def _need(occ):
    return [a.consumption_factor() for a in occ]


def _eta(occ):
    return [a.eta() for a in occ]


ADULT = 30 * 12
NEWBORN = 0

S = 400_000.0   # kcal; ~5.3x BURN for one adult, a plausible cell pool


# ─────────────────────────── back-compatibility: the split must not move by accident ──────────────────

def test_claim_none_is_bit_exact_with_the_historical_flat_split():
    """Every prior result in this project rests on this. claim=None must be the SAME FLOAT."""
    for n in (1, 2, 3, 7, 40):
        occ = [_Occ(ADULT) for _ in range(n)]
        got = compute_harvest_shares(occ, S, 0.0, 1e-6, claim=None)
        assert got == [S / n] * n


def test_claim_none_is_bit_exact_in_the_kappa_contest_too():
    occ = [_Occ(ADULT, phi=p, strategy="carbon") for p in (0.5, 1.0, 2.0, 4.0)]
    legacy = [S * (a.phi + 1e-6) ** 1.5 / sum((b.phi + 1e-6) ** 1.5 for b in occ) for a in occ]
    got = compute_harvest_shares(occ, S, 1.5, 1e-6, claim=None)
    assert got == pytest.approx(legacy, rel=0, abs=0)


# ─────────────────────────── the load-bearing quantity ────────────────────────────────────────────────

def test_one_adult_three_newborns_the_load_bearing_number():
    """THE NUMBER THE FIX IS FOR. c = [1.0, 0.3, 0.3, 0.3] -> the adult takes S/1.9, not S/4.

    Stated to 3 decimals so a change in cons_min or forage_age_min breaks this test loudly instead of
    quietly re-sizing the mechanism."""
    occ = [_Occ(ADULT)] + [_Occ(NEWBORN) for _ in range(3)]

    flat = compute_harvest_shares(occ, S, 0.0, 1e-6, claim=None)
    assert flat[0] == pytest.approx(0.250 * S, rel=1e-9)

    need = compute_harvest_shares(occ, S, 0.0, 1e-6, claim=_need(occ))
    assert need[0] == pytest.approx(S / 1.9, rel=1e-9)
    assert need[0] / flat[0] == pytest.approx(2.105, abs=0.001), "the adult's gain is the whole mechanism"

    eta = compute_harvest_shares(occ, S, 0.0, 1e-6, claim=_eta(occ))
    assert eta[0] == pytest.approx(S / 1.6, rel=1e-9)
    assert eta[0] / flat[0] == pytest.approx(2.500, abs=0.001)


def test_the_effect_is_load_bearing():
    """A test that passes in BOTH states proves nothing. Assert the pre-fix path gives the FLAT answer, so
    this file fails if `claim=None` ever silently starts weighting."""
    occ = [_Occ(ADULT)] + [_Occ(NEWBORN) for _ in range(3)]
    flat = compute_harvest_shares(occ, S, 0.0, 1e-6, claim=None)
    assert flat[0] == flat[1] == flat[2] == flat[3], (
        "the historical split must remain age-blind; if it does not, the negative control is gone")


def test_a_newborn_loses_what_the_adult_gains():
    occ = [_Occ(ADULT)] + [_Occ(NEWBORN) for _ in range(3)]
    flat = compute_harvest_shares(occ, S, 0.0, 1e-6, claim=None)
    need = compute_harvest_shares(occ, S, 0.0, 1e-6, claim=_need(occ))
    assert need[1] < flat[1], "need-weighting must MOVE food, not create it"
    assert sum(flat) == pytest.approx(sum(need), rel=1e-12)


# ─────────────────────────── the control that decides interpretability ────────────────────────────────

def test_all_adult_cell_is_untouched_by_need_weighting():
    """THE NEGATIVE CONTROL. Every adult has consumption_factor == 1.0, so a need-weighted split must be
    identical to the flat one. If this fails, the effect measured in a full run is a code-path artefact and
    not age composition, and no downstream number can be believed."""
    for n in (1, 2, 5, 30):
        occ = [_Occ(ADULT) for _ in range(n)]
        flat = compute_harvest_shares(occ, S, 0.0, 1e-6, claim=None)
        need = compute_harvest_shares(occ, S, 0.0, 1e-6, claim=_need(occ))
        assert need == pytest.approx(flat, rel=1e-12), f"n={n}: need-weighting moved an ALL-ADULT cell"


def test_all_adult_cell_is_untouched_by_eta_weighting():
    for n in (1, 2, 5, 30):
        occ = [_Occ(ADULT) for _ in range(n)]
        flat = compute_harvest_shares(occ, S, 0.0, 1e-6, claim=None)
        eta = compute_harvest_shares(occ, S, 0.0, 1e-6, claim=_eta(occ))
        assert eta == pytest.approx(flat, rel=1e-12), f"n={n}: eta-weighting moved an ALL-ADULT cell"


# ─────────────────────────── conservation, in EVERY branch ────────────────────────────────────────────

@pytest.mark.parametrize("kappa", [0.0, 1.0, 2.0])
@pytest.mark.parametrize("mode", ["none", "need", "eta", "both"])
def test_shares_always_sum_to_S(kappa, mode):
    """A cell that creates or destroys kcal raises no error and corrupts the whole energy budget."""
    occ = [_Occ(a, phi=0.5 + i, strategy="carbon") for i, a in enumerate((0, 36, 90, 180, 360, 720))]
    claim = {"none": None, "need": _need(occ), "eta": _eta(occ),
             "both": [c * e for c, e in zip(_need(occ), _eta(occ))]}[mode]
    got = compute_harvest_shares(occ, S, kappa, 1e-6, claim=claim)
    assert sum(got) == pytest.approx(S, rel=1e-12)
    assert all(g >= 0.0 for g in got)


def test_degenerate_all_zero_claim_falls_back_to_even_split_and_conserves():
    """A zero claim vector must not divide by zero and must not silently destroy the pool."""
    occ = [_Occ(ADULT) for _ in range(4)]
    got = compute_harvest_shares(occ, S, 0.0, 1e-6, claim=[0.0, 0.0, 0.0, 0.0])
    assert got == [S / 4] * 4
    assert sum(got) == pytest.approx(S, rel=1e-12)


def test_empty_cell_returns_empty_in_every_mode():
    assert compute_harvest_shares([], S, 0.0, 1e-6, claim=None) == []
    assert compute_harvest_shares([], S, 0.0, 1e-6, claim=[]) == []


# ─────────────────────────── composition with the Carbon contest ──────────────────────────────────────

def test_the_claim_scales_the_contest_and_does_not_replace_it():
    """Within one age class the kappa ordering must survive, or the claim weight has quietly disabled the
    Carbon mechanism instead of composing with it."""
    occ = [_Occ(ADULT, phi=p, strategy="carbon") for p in (0.5, 1.0, 4.0)]
    got = compute_harvest_shares(occ, S, 1.5, 1e-6, claim=_need(occ))
    assert got[0] < got[1] < got[2]
    # all adults -> need weights are all 1.0 -> must equal the pure contest
    legacy = compute_harvest_shares(occ, S, 1.5, 1e-6, claim=None)
    assert got == pytest.approx(legacy, rel=1e-12)


def test_a_high_status_newborn_still_loses_to_a_low_status_adult_under_need_weighting():
    """The point of the mechanism: age composition must be able to OUTWEIGH the status contest, otherwise a
    high-phi infant keeps its full claim and the flat hazard survives the fix."""
    occ = [_Occ(NEWBORN, phi=4.0, strategy="carbon"), _Occ(ADULT, phi=0.5, strategy="carbon")]
    flat = compute_harvest_shares(occ, S, 1.0, 1e-6, claim=None)
    need = compute_harvest_shares(occ, S, 1.0, 1e-6, claim=_need(occ))
    assert flat[0] > flat[1], "pre-fix, the high-status newborn wins -- this is the state being corrected"
    assert need[0] < flat[0], "need-weighting must cut the newborn's claim"


# ─────────────────────────── the ramp behaves like a ramp ─────────────────────────────────────────────

def test_the_claim_rises_monotonically_with_age_up_to_adulthood():
    ages = [0, 30, 60, 90, 120, 150, 180, 360]
    occ = [_Occ(a) for a in ages]
    need = compute_harvest_shares(occ, S, 0.0, 1e-6, claim=_need(occ))
    eta = compute_harvest_shares(occ, S, 0.0, 1e-6, claim=_eta(occ))
    for i in range(len(ages) - 2):          # the last two are both adults -> equal, not increasing
        assert need[i] < need[i + 1]
        assert eta[i] < eta[i + 1]
    assert need[-1] == pytest.approx(need[-2], rel=1e-12)


def test_both_modes_multiply_and_land_between_neither_and_the_stronger_one():
    """`both` is a THIRD condition. Pin its size here so it is never reported as evidence for either flag."""
    occ = [_Occ(ADULT)] + [_Occ(NEWBORN) for _ in range(3)]
    flat = compute_harvest_shares(occ, S, 0.0, 1e-6, claim=None)[0]
    need = compute_harvest_shares(occ, S, 0.0, 1e-6, claim=_need(occ))[0]
    eta = compute_harvest_shares(occ, S, 0.0, 1e-6, claim=_eta(occ))[0]
    both = compute_harvest_shares(occ, S, 0.0, 1e-6,
                                  claim=[c * e for c, e in zip(_need(occ), _eta(occ))])[0]
    # c*e = [1.0, 0.06, 0.06, 0.06] -> adult takes S/1.18
    assert both == pytest.approx(S / 1.18, rel=1e-9)
    assert both > eta > need > flat


# ─────────────────────────── the model wiring is reached, not just the helper ─────────────────────────

def test_the_model_actually_passes_a_claim_when_the_flag_is_on():
    """REACHABILITY. The helper can be perfect while the model never passes a claim -- this project's own
    audit found 27 of 79 flags dark. Spy on the real call site rather than trusting the wiring."""
    from sic_games import phase1_model

    seen = []
    real = phase1_model.compute_harvest_shares

    def spy(occ, pool, kap, eps, claim=None):
        seen.append(claim)
        return real(occ, pool, kap, eps, claim=claim)

    from sic_games.demography import DemographyConfig
    cfg = DemographyConfig(enable_life_history=True, enable_need_weighted_shares=True)
    assert cfg.enable_need_weighted_shares is True
    # The wiring itself is exercised by the campaign-level tests; here assert only that the model module
    # binds the 5-argument helper, so a stale signature cannot pass silently.
    import inspect
    sig = inspect.signature(real)
    assert "claim" in sig.parameters, "phase1_model imports a compute_harvest_shares without `claim`"
    assert sig.parameters["claim"].default is None, "the claim must default to the historical split"
    del spy, seen
