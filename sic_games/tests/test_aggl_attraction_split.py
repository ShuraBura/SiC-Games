"""Agglomeration ATTRACTION/PRODUCTION split (R-106 Addendum 13).

THE DEFECT THIS ADDRESSES. The point-superlinear agglomeration term is applied twice from one parameter set:
as a per-capita premium inside the movement scorer (it ATTRACTS movers) and as realized output in the harvest,
`S += aggl_R·(n^β − n)` (it FEEDS them). R-106 Addendum 10 measured the consequence of that entanglement:
ablating agglomeration broke the concentration exactly as intended (max cell occupancy 159 → 10) but cut
population to x0.20–0.45, because the same term supplies over half the economy's output. Concentration could
not be tuned without destroying subsistence.

`aggl_attraction_weight` scales the PERCEIVED premium only. At 0 an agent perceives no co-location bonus and
distributes by food alone (pure IFD) while still RECEIVING the realized production in the harvest.

These tests pin the contract:
  - default 1.0, and 1.0 is BIT-EXACT with the pre-split call (charter adoption gate);
  - the weight actually gates the movement decision (a crowded cell that wins at 1.0 loses at 0.0);
  - it scales the premium linearly and is clamped to be non-negative by the config;
  - it does NOT touch the harvest: realized production is unchanged at any weight.
"""
import numpy as np
import pytest

from sic_games.demography import DemographyConfig
from sic_games.substrate import diffusion_select_target


class _Field:
    """Uniform sugar field on a torus."""
    def __init__(self, w=20, h=20, val=1000.0):
        self.width, self.height, self._v = w, h, val

    def level(self, x, y):
        return self._v


class _SC:
    contest_exponent = 0.0          # even split ⇒ per-capita is S/n, so crowding is a pure penalty
    phi_epsilon = 1e-6
    k_cell = 0
    move_cost_flat = 0.0
    group_safety_max = 0.0
    group_safety_scale = 8.0
    group_mate_min = 0.0
    group_mate_floor = 0.3


class _Agent:
    strategy = "greedy"

    def __init__(self, pos):
        self.pos = pos


def _crowded_setup(premium=4000.0):
    """Agent on a CROWDED cell (8,8) with an empty neighbour at (9,8).

    Without any agglomeration premium the empty neighbour must win on food alone (S/1 vs S/n). The premium is
    sized so that at full weight the crowded cell wins instead — which makes the weight's effect a clean,
    binary read on the chosen target rather than a numeric comparison.
    """
    f, sc = _Field(), _SC()
    a = _Agent((8, 8))
    occ = {(8, 8): 20}
    R = np.zeros((20, 20), dtype=float)
    R[8, 8] = premium
    return f, sc, a, occ, R


# --------------------------------------------------------------------------- config contract

def test_default_is_one_and_non_negative():
    c = DemographyConfig()
    assert c.aggl_attraction_weight == 1.0, "must default to the shipped behaviour"
    with pytest.raises(Exception):
        DemographyConfig(aggl_attraction_weight=-0.5)


# --------------------------------------------------------------------------- bit-exactness gate

def test_weight_one_is_bit_exact_with_the_presplit_call():
    """Charter adoption gate: not passing the argument and passing 1.0 must be identical."""
    for n_here in (1, 5, 20, 100):
        f, sc, a1, occ, R = _crowded_setup()
        a2 = _Agent((8, 8))
        occ = {(8, 8): n_here}
        t_legacy = diffusion_select_target(a1, f, dict(occ), None, sc, None, None, R_field=R)
        t_new = diffusion_select_target(a2, f, dict(occ), None, sc, None, None, R_field=R,
                                        aggl_attract=1.0)
        assert t_legacy == t_new, f"weight=1.0 diverged from the pre-split call at n={n_here}"


# --------------------------------------------------------------------------- the decoupling itself

def test_weight_gates_the_movement_decision():
    """The premium keeps the agent on a crowded cell at full weight; at zero, food alone routes it away."""
    f, sc, a, occ, R = _crowded_setup()
    stay = diffusion_select_target(a, f, dict(occ), None, sc, None, None, R_field=R, aggl_attract=1.0)
    assert stay == (8, 8), "at full weight the co-location premium should hold the agent on the crowded cell"

    a2 = _Agent((8, 8))
    leave = diffusion_select_target(a2, f, dict(occ), None, sc, None, None, R_field=R, aggl_attract=0.0)
    assert leave != (8, 8), "at zero weight the agent should distribute by food alone and leave"


def test_attraction_is_monotone_in_the_weight():
    """A larger weight can only make a crowded cell MORE attractive, never less — the term is a plain
    non-negative multiplier on the premium, so the stay/leave decision must not flip back and forth."""
    # R sized so the sweep straddles the boundary: leaving is worth S/1 − S/n = 900, and the premium is
    # wt·R·(n^0.15 − 1) = wt·R·0.4125, so the flip sits between wt 0.5 (619) and 1.0 (1237).
    f, sc = _Field(), _SC()
    R = np.zeros((20, 20), dtype=float)
    R[8, 8] = 3000.0
    occ = {(8, 8): 10}
    stays = []
    for wt in (0.0, 0.25, 0.5, 1.0, 2.0):
        a = _Agent((8, 8))
        t = diffusion_select_target(a, f, dict(occ), None, sc, None, None, R_field=R, aggl_attract=wt)
        stays.append(t == (8, 8))
    # once staying becomes preferred it must remain preferred at every higher weight
    assert stays == sorted(stays), f"stay-preference was not monotone in the weight: {stays}"
    assert stays[0] is False and stays[-1] is True, (
        "the sweep must actually straddle the decision boundary, otherwise it tests nothing")


def test_weight_multiplies_the_premium_exactly():
    """Quantitative contract: the perceived premium must equal wt · R · (n^(β−1) − 1).

    Recovered by bisecting the move cost at which staying and leaving are exactly balanced — that cost IS the
    utility gap, so it reads the premium directly out of the scorer rather than trusting the source."""
    beta, n, Rv = 1.15, 10.0, 1000.0
    expected_full = Rv * (n ** (beta - 1.0) - 1.0)

    def gap_at(wt):
        """Smallest flat move cost that stops the agent leaving = the utility advantage of the move."""
        f, sc = _Field(), _SC()
        R = np.zeros((20, 20), dtype=float)
        R[8, 8] = Rv
        lo, hi = 0.0, 5000.0
        for _ in range(40):
            mid = (lo + hi) / 2.0
            sc.move_cost_flat = mid
            a = _Agent((8, 8))
            t = diffusion_select_target(a, f, {(8, 8): int(n)}, None, sc, None, None,
                                        R_field=R, aggl_alpha=beta, aggl_attract=wt)
            if t == (8, 8):
                hi = mid
            else:
                lo = mid
        return (lo + hi) / 2.0

    # Leaving is worth (S/1 − S/n) in food; staying additionally gains wt·premium. So the balancing move cost
    # falls by exactly the premium as the weight rises: gap(0) − gap(wt) == wt · premium.
    g0 = gap_at(0.0)
    for wt in (0.25, 0.5, 1.0):
        got = g0 - gap_at(wt)
        assert got == pytest.approx(wt * expected_full, rel=0.02), (
            f"premium at weight {wt} read {got:.1f}, expected {wt * expected_full:.1f}")


def test_the_weight_never_reaches_the_harvest():
    """The split's whole point: this weight is PERCEPTION-only. Realized production
    (`S += aggl_R·(n^β − n)`) must be untouched at any weight, or the decoupling is a lie.

    Asserted at the source level because the harvest's realized output cannot be isolated behaviourally —
    changing the weight changes where agents stand, which changes occupancy, which changes output."""
    import inspect

    from sic_games import phase1_model
    src = inspect.getsource(phase1_model)
    # The config field may be READ exactly once (to build the mover's argument) and must never appear in the
    # harvest expression. Locate the realized-production line and assert the weight is absent from it.
    prod_lines = [ln for ln in src.splitlines() if "aggl_R[cy, cx]" in ln or "aggl_R[cy," in ln]
    assert prod_lines, "could not locate the realized agglomeration production line — test needs updating"
    for ln in prod_lines:
        assert "aggl_at" not in ln and "aggl_attraction_weight" not in ln, (
            f"attraction weight leaked into realized production: {ln.strip()}")
    assert src.count("aggl_attraction_weight") == 1, (
        "the weight should be read exactly once, to build the mover's argument")


def test_substrate_signature_contract():
    import inspect
    sig = inspect.signature(diffusion_select_target)
    assert "aggl_attract" in sig.parameters
    assert sig.parameters["aggl_attract"].default == 1.0
