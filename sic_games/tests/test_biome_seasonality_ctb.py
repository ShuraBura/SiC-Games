"""CTB for PER-BIOME SEASONALITY (R-106, 2026-09-07).

THE DEFECT. `ClimateField.season()` applies a single scalar `a_seas` uniformly to every cell, so an aseasonal
rainforest (real seasonal amplitude ~0.05) gets the same seasonal food swing as a savanna (~0.40). The fake dry
season STARVES the richest biome: coastal-tropical (95% forest, NPP 2243) realises e0 23 against the Ache-forest
anchor 37, and turning the seasonality off (a_seas 0.5->0) lifts it 23->32.5.

THE FIX. `ClimateConfig.enable_biome_seasonality`: level(x,y) swings the food capacity by the CELL's OWN biome
amplitude (`seasonal_amplitude_field`: forest 0.05, savanna 0.40, grass 0.60) about the shared time-of-year
wave, instead of the scalar. A/B: tropical e0 +6.6, savanna +2.9, temperate/boreal -0.6/-0.7 (stay at anchor).

LOAD-BEARING is `test_MODEL_forest_swings_less_than_savanna`: with the flag on, a FOREST cell's peak->trough
food swing is far smaller than a SAVANNA cell's; with the flag off, both swing by the same scalar.
"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
for p in (ROOT / "sic_games" / "src",):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import numpy as np  # noqa: E402
from sic_games.climate import ClimateConfig, build_climate_field, SEASON_PERIOD_DEFAULT  # noqa: E402
from sic_games.capacity import NPPCapacityField  # noqa: E402
from sic_games.terrain import (generate_world, world_lottery_climate, BIOME_FOREST,  # noqa: E402
                               BIOME_SAVANNA)


def test_the_flag_defaults_off():
    assert ClimateConfig().enable_biome_seasonality is False


def _world_with(clim="savanna", seed=0):
    k = world_lottery_climate(seed, terrain="coastal", climate=clim)
    f = generate_world(k, mode="climate")
    base = NPPCapacityField(f, 75000.0, patch=(20, 20, 24), mode="tallavaara", aquatic=True, enable_depletion=True)
    return f, base


def _swing(field, x, y):
    """peak->trough ratio of the cell's food level (isolates the seasonal factor; base is constant)."""
    field.set_step(0)                                   # cos=1 -> wave=1 -> peak
    peak = field.level(x, y)
    field.set_step(SEASON_PERIOD_DEFAULT // 2)          # cos=-1 -> wave=0 -> trough
    trough = field.level(x, y)
    return (trough / peak) if peak > 0 else float("nan")


def _cells(f, base):
    biome = np.asarray(f.biome)
    forest = savanna = None
    for y in range(100):
        for x in range(100):
            if f.isWater[y, x] or base.level(x, y) <= 0:
                continue
            if forest is None and biome[y, x] == BIOME_FOREST:
                forest = (x, y)
            if savanna is None and biome[y, x] == BIOME_SAVANNA:
                savanna = (x, y)
    return forest, savanna


def test_MODEL_forest_swings_less_than_savanna():
    """LOAD-BEARING. With per-biome seasonality ON, a forest cell's seasonal food swing is far shallower than a
    savanna cell's (amp 0.05 vs 0.40); with it OFF, both swing by the same scalar a_seas."""
    # find a world holding BOTH a forest and a savanna land cell
    forest = savanna = None
    for clim in ("savanna", "tropical", "temperate"):
        f, base = _world_with(clim)
        fo, sa = _cells(f, base)
        if fo and sa:
            forest, savanna = fo, sa
            break
    if not (forest and savanna):
        pytest.skip("no world with both a forest and a savanna land cell in the tried climates")

    on = build_climate_field(base, ClimateConfig(enable_seasonality=True, a_seas=0.5,
                                                 enable_biome_seasonality=True), fields=f, seed=0)
    f_swing_on, s_swing_on = _swing(on, *forest), _swing(on, *savanna)
    # trough/peak: higher ratio = shallower swing. Forest (amp 0.05 -> ~0.95) must be much shallower than
    # savanna (amp 0.40 -> ~0.60).
    assert f_swing_on > s_swing_on + 0.15, (
        f"per-biome ON: forest must swing LESS than savanna (forest trough/peak {f_swing_on:.3f} vs "
        f"savanna {s_swing_on:.3f})")
    assert f_swing_on > 0.85, f"a forest cell should be nearly aseasonal (trough/peak {f_swing_on:.3f})"

    off = build_climate_field(base, ClimateConfig(enable_seasonality=True, a_seas=0.5,
                                                  enable_biome_seasonality=False), fields=f, seed=0)
    f_swing_off, s_swing_off = _swing(off, *forest), _swing(off, *savanna)
    assert abs(f_swing_off - s_swing_off) < 1e-9, (
        f"scalar path: forest and savanna must swing the SAME (forest {f_swing_off:.3f} savanna {s_swing_off:.3f})")
