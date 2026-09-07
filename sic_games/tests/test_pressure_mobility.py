"""Pressure-aware mobility (R-106 Addendum 6, `docs/RESULTS.md`).

`mobility_radius`'s NPP-driven stride (§4.8.19) is STATIC/geographic — a cell packed with 40+ occupants still
reads as "rich" (raw local NPP unchanged), so the radius never expands for an agent stuck in a crowded cluster
(measured 2026-07-30: r_used==1 in 100% of equilibrium decisions, Addendum 4). `mobility_pressure_source=
"intake"` swaps the driving variable to the agent's own live `_intake_ema` (the SAME signal
`enable_intake_fertility` computes, R-106) — density-aware by construction, since a crowded cell dilutes the
realized share regardless of the cell's nominal fertility.

These tests pin:
  - the `mobility_radius` shape under source="intake" mirrors source="npp" (same clamp/monotonicity), just
    inverted in what "high" means (high intake ratio = well-fed = short stride, not high NPP);
  - `mobility_pressure_source` defaults to "npp" — existing NPP-mode configs and results are BIT-EXACT;
  - the `_intake_ema` update loop stays live under mobility-intake mode even with `enable_intake_fertility`
    OFF (independent ablatability — the two mechanisms share one signal without requiring each other);
  - flag off (either the master `enable_productivity_mobility`, or leaving source at "npp") ⇒ bit-exact.
"""
import os
import sys

import pytest

from sic_games.demography import DemographyConfig, mobility_radius

_HERE = os.path.dirname(os.path.abspath(__file__))
_BATT = os.path.normpath(os.path.join(_HERE, "..", "outputs", "mechanism_battery"))
if _BATT not in sys.path:
    sys.path.insert(0, _BATT)

WORLD = dict(n=900, patch=18, terr="coastal", clim="temperate")


def _cfg(**kw):
    base = dict(enable_productivity_mobility=True, mobility_pressure_source="intake",
                mobility_base_radius=1, mobility_max_radius=6,
                mobility_intake_ref=1.00, mobility_intake_floor=0.15, mobility_exponent=1.0)
    base.update(kw)
    return DemographyConfig(**base)


# --------------------------------------------------------------------------- config defaults

def test_source_defaults_to_npp():
    c = DemographyConfig()
    assert c.mobility_pressure_source == "npp", "must default to the ORIGINAL formula — pure additive mode"


def test_intake_ref_reuses_the_maintenance_anchor():
    c = DemographyConfig()
    assert c.mobility_intake_ref == c.intake_fert_lo == 1.00, \
        "the mobility-comfort threshold should reuse the already-anchored maintenance ratio, not a new number"


# --------------------------------------------------------------------------- mobility_radius helper, source="intake"

def test_off_returns_base():
    c = _cfg(enable_productivity_mobility=False)
    assert mobility_radius(0.3, c) == 1
    assert mobility_radius(3.0, c) == 1


def test_well_fed_gives_base():
    c = _cfg()
    assert mobility_radius(1.00, c) == 1       # at ref (maintenance) → base
    assert mobility_radius(4.26, c) == 1       # well above ref (R-106's measured p90) → clamped to base


def test_hungry_gives_longer_stride():
    c = _cfg()
    # ratio 0.33 → ref/max(0.33,floor) = 1.00/0.33 = 3.03 → round to 3
    assert mobility_radius(0.33, c) == 3
    # near-starving → clamped by floor (0.15) then r_max (6): 1.00/0.15 = 6.67 → 6
    assert mobility_radius(0.05, c) == 6


def test_monotone_decreasing_in_intake_ratio():
    c = _cfg()
    xs = [0.15, 0.3, 0.5, 0.8, 1.0, 2.0, 4.0]
    rs = [mobility_radius(x, c) for x in xs]
    assert all(rs[i] >= rs[i + 1] for i in range(len(rs) - 1)), "stride must shrink as intake improves"
    assert min(rs) == 1 and max(rs) <= c.mobility_max_radius


def test_exponent_flattens_response():
    steep = _cfg(mobility_exponent=1.0)
    flat = _cfg(mobility_exponent=0.0)
    assert mobility_radius(0.3, flat) == 1
    assert mobility_radius(0.3, steep) > 1


def test_floor_bounds_starvation():
    c = _cfg(mobility_intake_floor=0.5, mobility_max_radius=50)
    # denom floored at 0.5 ⇒ 1.00/0.5 = 2, not larger even at ratio 0
    assert mobility_radius(0.01, c) == 2
    assert mobility_radius(0.0, c) == 2


def test_npp_and_intake_sources_are_independent_configs():
    """Setting the intake-mode fields must not perturb the npp-mode formula, and vice versa."""
    npp_cfg = DemographyConfig(enable_productivity_mobility=True, mobility_pressure_source="npp",
                                mobility_intake_ref=999.0, mobility_intake_floor=999.0)  # should be IGNORED
    assert mobility_radius(900.0, npp_cfg) == 1        # npp path uses mobility_npp_ref/floor, unaffected


# --------------------------------------------------------------------------- world-level liveness (slow)

@pytest.mark.slow
def test_off_is_bit_exact():
    """NOTE: the preset (`emergent_village_demog`) has `enable_productivity_mobility=True` by default (§4.8.19),
    so the correct baseline for "master flag off" is `enable_productivity_mobility=False` itself, not `{}` —
    comparing against `{}` would conflate this test with turning the (already-on) mechanism off, a real
    behaviour change covered by the npp-vs-off mobility tests, not this one."""
    import battery1_liveness as B1
    off_npp, _, _ = B1.signature(dict(enable_productivity_mobility=False), steps=120, **WORLD)
    off_intake, _, _ = B1.signature(dict(enable_productivity_mobility=False,
                                          mobility_pressure_source="intake"), steps=120, **WORLD)
    assert off_npp == off_intake, "flag off must be bit-exact regardless of what source is configured"


@pytest.mark.slow
def test_npp_source_default_stays_bit_exact_with_new_fields_present():
    """Merely having the new mobility_intake_* fields on the config (at their defaults) must not perturb the
    existing NPP-mode mechanism — this is the pure-additive-mode guarantee."""
    import battery1_liveness as B1
    legacy, _, _ = B1.signature(dict(enable_productivity_mobility=True), steps=120, **WORLD)
    explicit_npp, _, _ = B1.signature(dict(enable_productivity_mobility=True,
                                            mobility_pressure_source="npp"), steps=120, **WORLD)
    assert legacy == explicit_npp


@pytest.mark.slow
def test_intake_source_changes_the_world():
    import battery1_liveness as B1
    off, _, _ = B1.signature(dict(enable_productivity_mobility=False), steps=120, **WORLD)
    on, _, _ = B1.signature(dict(enable_productivity_mobility=True,
                                  mobility_pressure_source="intake"), steps=120, **WORLD)
    assert on != off, "enabling intake-pressure mobility is bit-identical — the new branch is dead"


@pytest.mark.slow
def test_intake_ema_stays_live_without_fertility_flag():
    """The independent-ablatability guarantee: mobility-intake mode must keep `_intake_ema` updating even
    with `enable_intake_fertility` OFF, not silently read the frozen birth-value (intake_fert_hi) forever."""
    import battery1_liveness as B1
    w = B1._build(dict(enable_productivity_mobility=True, mobility_pressure_source="intake",
                        enable_intake_fertility=False), **WORLD)
    for _ in range(60):
        w.step()
        if not w.agent_list:
            pytest.skip("population collapsed before the EMA could diverge")
    adults = [a for a in w.agent_list if a.age >= w._demog.menarche_months]
    assert adults, "no adults survived to check"
    hi = w._demog.intake_fert_hi
    n_moved = sum(1 for a in adults if abs(a._intake_ema - hi) > 1e-9)
    assert n_moved > 0, "_intake_ema never left its frozen birth value — the mobility-only gate is dead"


@pytest.mark.slow
def test_fertility_and_mobility_intake_modes_are_independently_ablatable():
    """Flipping enable_intake_fertility ON TOP of mobility-intake mode must further change the world (the
    fertility branch reads the same EMA but is gated separately) — proof the two flags are not silently the
    same mechanism wearing two names.

    300 steps, not 120, for the reason measured in `test_intake_fertility.test_on_changes_the_world`: the
    fertility gate binds on only 2.2% of fertile women by step 120 in this world and 13.1% by step 300, so at
    120 the comparison was decided by whether one of three gated women was drawn for a birth — a coin flip
    that an unrelated 0.001 change in `divorce_rate` was enough to turn over."""
    import battery1_liveness as B1
    mobility_only, _, _ = B1.signature(dict(enable_productivity_mobility=True,
                                             mobility_pressure_source="intake",
                                             enable_intake_fertility=False), steps=300, **WORLD)
    both, _, _ = B1.signature(dict(enable_productivity_mobility=True,
                                    mobility_pressure_source="intake",
                                    enable_intake_fertility=True), steps=300, **WORLD)
    assert mobility_only != both
