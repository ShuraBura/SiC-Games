"""CTB for the DEPLETABLE RESOURCE STOCK (GD-1) and its seasonal coupling (R-106, 2026-09-02).

WHY. The over-clustering investigation needed to know whether depletion actually depletes (it could be
on-but-dead behind the ClimateField wrapper, or too weak to bite). This constructs a cell whose answer is known
and checks the real `NPPCapacityField.deplete_and_regrow` / `ClimateField` path.

WHAT IT ESTABLISHES:
  · the stock B FALLS under foraging pressure and the yield falls with it (load-bearing);
  · it REGROWS when pressure is removed;
  · the equilibrium stock matches the closed form B* = 1 - deplete_frac·pressure (clamped);
  · `season` scales the RATE (a lean season recovers slower);
  · the ClimateField wrapper FORWARDS depletion (delegates) and multiplies the yield by its own seasonal factor;
  · MODEL PATH: a cell foraged ABOVE its capacity depletes in a real run.

The finding this CTB backs (documented, not asserted): depletion is correct but does not cap a village, because
a village sits on a HIGH-capacity cell (Tallavaara ~100 persons on the richest cells) well below its capacity,
so pressure < 1 and B stays high. The over-clustering is high per-cell capacity + agglomeration, not broken
depletion.
"""
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "sic_games" / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "sic_games" / "src"))

from sic_games.capacity import B_FLOOR, DEPLETE_FRAC, NPPCapacityField  # noqa: E402
from sic_games.climate import ClimateField  # noqa: E402
from sic_games.terrain import generate_world, world_lottery_climate  # noqa: E402


def _field(depletion=True):
    k = world_lottery_climate(0, terrain="coastal", climate="temperate")
    f = generate_world(k, mode="climate")
    return NPPCapacityField(f, 75000.0, patch=(20, 20, 30), mode="tallavaara", aquatic=True,
                            enable_depletion=depletion), f


def _rich_cell(fld):
    E = getattr(fld, "_base_E", None)
    if E is None:                                    # depletion off: no _base_E, scan the yield directly
        E = np.array([[fld.level(x, y) for x in range(100)] for y in range(100)])
    ys, xs = np.where(E > 0)
    i = int(np.argmax(E[ys, xs]))
    return int(xs[i]), int(ys[i])


# ─────────────────────────── the load-bearing depletion dynamics ───────────────────────────

def test_MODEL_stock_and_yield_fall_under_pressure():
    """LOAD-BEARING. Foraging a cell at 5x its capacity drives the stock to the floor and the yield down with
    it. Verified to FAIL (stock stays 1.0, yield unchanged) when enable_depletion is off."""
    fld, _ = _field(depletion=True)
    x, y = _rich_cell(fld)
    cap = fld._K_persons[y, x]
    y0 = fld.level(x, y)
    for _ in range(20):
        fld.deplete_and_regrow({(x, y): int(5 * cap)}, season=1.0)
    assert fld._B[y, x] == pytest.approx(B_FLOOR, abs=1e-6), "5x pressure must drive the stock to its floor"
    assert fld.level(x, y) < 0.1 * y0, "the yield must collapse with the depleted stock"


def test_off_is_a_noop():
    fld, _ = _field(depletion=False)
    x, y = _rich_cell(fld)
    y0 = fld.level(x, y)
    fld.deplete_and_regrow({(x, y): 10 ** 6}, season=1.0)   # even absurd pressure does nothing when off
    assert fld.level(x, y) == y0


def test_stock_regrows_when_pressure_is_removed():
    fld, _ = _field(depletion=True)
    x, y = _rich_cell(fld)
    cap = fld._K_persons[y, x]
    for _ in range(20):
        fld.deplete_and_regrow({(x, y): int(5 * cap)}, season=1.0)
    depleted = fld._B[y, x]
    for _ in range(80):
        fld.deplete_and_regrow({}, season=1.0)
    assert fld._B[y, x] > 0.9, "the stock must recover toward full when foraging stops"
    assert fld._B[y, x] > depleted + 0.5, "regrowth must be substantial"


def test_equilibrium_matches_the_closed_form():
    """B* = 1 - deplete_frac·pressure (clamped to [floor, 1]). Check at pressure 1 (occ = capacity)."""
    fld, _ = _field(depletion=True)
    x, y = _rich_cell(fld)
    cap = fld._K_persons[y, x]
    for _ in range(200):
        fld.deplete_and_regrow({(x, y): int(round(cap))}, season=1.0)
    assert fld._B[y, x] == pytest.approx(1.0 - DEPLETE_FRAC * 1.0, abs=0.03), "equilibrium stock at pressure 1"


def test_season_scales_the_rate_not_the_equilibrium():
    """`season` multiplies the whole update, so a LEANER season depletes/recovers SLOWER. One step from full at
    the same pressure moves less under a low season."""
    fx, _ = _field(depletion=True); fy, _ = _field(depletion=True)
    x, y = _rich_cell(fx)
    cap = fx._K_persons[y, x]
    fx.deplete_and_regrow({(x, y): int(5 * cap)}, season=1.0)
    fy.deplete_and_regrow({(x, y): int(5 * cap)}, season=0.3)
    drop_full = 1.0 - fx._B[y, x]
    drop_lean = 1.0 - fy._B[y, x]
    assert drop_lean < drop_full, "a leaner season must deplete more slowly (season scales the rate)"


# ─────────────────────────── the ClimateField wrapper forwards it ───────────────────────────

def test_the_climate_wrapper_forwards_depletion_and_scales_yield():
    """A village's harvest field is `ClimateField(NPPCapacityField(...enable_depletion))`. The wrapper must (a)
    delegate `deplete_and_regrow` to the inner stock (not swallow it) and (b) multiply the yield by its own
    seasonal factor. If the wrapper swallowed depletion, over-clustering would be un-diagnosable."""
    inner, _ = _field(depletion=True)
    wrapped = ClimateField(inner, a_seas=0.4)
    x, y = _rich_cell(inner)
    cap = inner._K_persons[y, x]
    assert hasattr(wrapped, "deplete_and_regrow"), "the wrapper must expose (delegate) deplete_and_regrow"
    y0 = wrapped.level(x, y)
    for _ in range(20):
        wrapped.deplete_and_regrow({(x, y): int(5 * cap)}, season=1.0)
    assert inner._B[y, x] == pytest.approx(B_FLOOR, abs=1e-6), "depletion through the wrapper must reach the stock"
    assert wrapped.level(x, y) < 0.2 * y0, "the wrapped yield must fall with the depleted stock"
