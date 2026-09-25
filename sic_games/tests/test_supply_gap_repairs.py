"""Supply-gap repairs (R-106 Addendum 111): `enable_village_granary` and `enable_sticky_pin_release`.

Addendum 110 found the mother of a starving child one cell off the village granary on all three canonical worlds:
the granary is per CELL (only its occupants fill it and draw it), and the residence pin is released by a per-step
coin flip, so families flicker off it. Two repairs, each held dark and tested alone first:

  - village granary: every cell inside a settlement's radius banks into, and draws from, ONE store keyed by the site;
  - sticky pin release: the same release probabilities, drawn once per household and HELD for a year.

These tests pin: both default OFF; each is LIVE (changes the world); and each does what it says (the structural
invariant), in the battery's small temperate world (villages from step ~50; scalar stress on, abandonment off).
"""
import os
import sys

import pytest

from sic_games.demography import DemographyConfig

_HERE = os.path.dirname(os.path.abspath(__file__))
_BATT = os.path.normpath(os.path.join(_HERE, "..", "outputs", "mechanism_battery"))
if _BATT not in sys.path:
    sys.path.insert(0, _BATT)

WORLD = dict(n=900, patch=18, terr="coastal", clim="temperate")


def test_both_default_off():
    c = DemographyConfig()
    assert c.enable_village_granary is False
    assert c.enable_sticky_pin_release is False
    assert c.pin_release_hold_steps == 12


@pytest.mark.slow
def test_hold_length_is_inert_while_sticky_release_is_off():
    """The hold parameter must do nothing unless its flag is on (pure additive mode)."""
    import battery1_liveness as B1
    a, _, _ = B1.signature({}, steps=150, **WORLD)
    b, _, _ = B1.signature(dict(pin_release_hold_steps=3), steps=150, **WORLD)
    assert a == b


@pytest.mark.slow
@pytest.mark.parametrize("flag", ["enable_village_granary", "enable_sticky_pin_release"])
def test_each_repair_changes_the_world(flag):
    import battery1_liveness as B1
    off, _, _ = B1.signature({}, steps=300, **WORLD)
    on, _, _ = B1.signature({flag: True}, steps=300, **WORLD)
    assert on != off, f"{flag} ON is bit-identical to OFF — the branch is dead in this world"


@pytest.mark.slow
def test_village_granary_banks_only_at_sites():
    """The invariant: with the village granary on, no cell INSIDE a village grows a store of its own — a village's
    food is banked at its site. Cells outside every village keep the per-cell store."""
    import battery1_liveness as B1
    w = B1._build(dict(enable_village_granary=True), **WORLD)
    for _ in range(80):                                   # villages exist from ~step 50
        w.step()
    assert w._settlement_sites, "no villages formed — the invariant is untested"
    n_checked = 0
    for _ in range(40):
        before = dict(w._cell_store)
        sites_before = set(w._settlement_sites)
        w.step()
        sites = set(w._settlement_sites)
        for cell, v in w._cell_store.items():
            if cell in sites or cell in sites_before:
                continue
            s = w._nearest_settlement(cell)
            if s is not None and s in sites_before:      # a village that existed through the whole step
                n_checked += 1
                assert v <= before.get(cell, 0.0) + 1e-9, (
                    f"village cell {cell} (not a site) grew its own store {before.get(cell, 0.0):.1f} -> {v:.1f}")
    # The check needs village cells that are NOT sites and still hold a (stale, decaying) store; if none exist the
    # invariant is vacuous here, so also require that some site store is live.
    assert any(w._cell_store.get(s, 0.0) > 0.0 for s in w._settlement_sites), "no site holds a village store"


@pytest.mark.slow
def test_sticky_release_holds_each_household_decision():
    """The invariant: a household's pin decision changes only when its hold expires — never step to step."""
    import battery1_liveness as B1
    w = B1._build(dict(enable_sticky_pin_release=True), **WORLD)
    hold = w._demog.pin_release_hold_steps
    last: dict = {}
    n_checked = 0
    for _ in range(160):
        w.step()
        for a in w.agent_list:
            if not hasattr(a, "_pin_hold_until"):
                continue
            prev = last.get(id(a))
            cur = (a._pin_released, a._pin_hold_until)
            if prev is not None and prev[1] == cur[1]:
                assert prev[0] == cur[0], "release state changed inside its hold window"
                n_checked += 1
            if prev is not None and prev[1] != cur[1]:
                assert cur[1] - prev[1] >= hold, "a new decision was drawn before the old hold expired"
            last[id(a)] = cur
    assert n_checked > 0, "no household held a decision — the sticky branch never ran"
