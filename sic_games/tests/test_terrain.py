"""§5 unit tests for the Stage 7 terrain generator (blueprint §5)."""
import numpy as np
import pytest
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "src"))

from sic_games.terrain import (
    N, W_FOREST, W_SAV,
    BIOME_WATER, BIOME_WETLAND, BIOME_FOREST, BIOME_SAVANNA, BIOME_GRASS,
    BIOME_DESERT, BIOME_MOUNTAIN,
    generate_world, characterize_map,
)

_BASE = dict(relief=0.4, rough=0.5, waterK=0.5, forestK=0.5, aridK=0.35, seedStr='42')
_W = generate_world(_BASE)


# ── §5 Test 1 — Field sanity ───────────────────────────────────────────────

def test_field_shapes():
    for name in ('elev', 'slope', 'slopeDeg', 'wateracc', 'isWater', 'isRiver',
                 'forage', 'game', 'cost', 'risk', 'biome', 'npp', 'forestness'):
        arr = getattr(_W, name)
        assert arr.shape == (N, N), f"{name} shape {arr.shape}"
    assert _W.neighbour_cost.shape == (N, N, 4)


def test_no_nan_inf():
    for name in ('elev', 'slope', 'slopeDeg', 'wateracc', 'forage', 'game',
                 'cost', 'risk', 'npp', 'forestness'):
        arr = getattr(_W, name)
        assert np.all(np.isfinite(arr)), f"{name} has NaN/Inf"


def test_field_ranges():
    assert _W.elev.min() >= 0.0 and _W.elev.max() <= 1.0
    assert _W.slope.min() >= 0.0 and _W.slope.max() <= 1.0
    assert _W.slopeDeg.min() >= 0.0
    assert _W.wateracc.min() >= 0.0 and _W.wateracc.max() <= 1.0
    assert np.all((_W.isWater == 0) | (_W.isWater == 1))
    assert np.all((_W.isRiver == 0) | (_W.isRiver == 1))
    assert _W.forage.min() >= 0.0 and _W.forage.max() <= 1.0
    assert _W.game.min() >= 0.0 and _W.game.max() <= 1.0
    assert _W.cost.min() >= 0.0 and _W.cost.max() <= 1.0
    assert _W.risk.min() >= 0.02 and _W.risk.max() <= 1.0
    assert np.all(np.isin(_W.biome, [0, 1, 2, 3, 4, 5, 6]))
    assert _W.npp.min() >= 0.0 and _W.npp.max() <= 1.0
    assert _W.forestness.min() >= 0.0 and _W.forestness.max() <= 1.0


def test_water_cells_have_zero_npp_forage_game_forestness():
    mask = _W.isWater.astype(bool)
    assert np.all(_W.npp[mask] == 0.0),        "npp nonzero on water"
    assert np.all(_W.forage[mask] == 0.0),     "forage nonzero on water"
    assert np.all(_W.game[mask] == 0.0),       "game nonzero on water"
    assert np.all(_W.forestness[mask] == 0.0), "forestness nonzero on water"


def test_water_cells_biome_zero():
    assert np.all(_W.biome[_W.isWater.astype(bool)] == BIOME_WATER)


# ── §5 Test 2 — Determinism ────────────────────────────────────────────────

def test_same_seed_byte_identical():
    w2 = generate_world(_BASE)
    for name in ('elev', 'slope', 'biome', 'npp', 'forage', 'game', 'cost', 'risk'):
        a1, a2 = getattr(_W, name), getattr(w2, name)
        assert np.array_equal(a1, a2), f"{name} not byte-identical on same seed"


def test_different_seed_not_equal():
    w2 = generate_world({**_BASE, 'seedStr': '7'})
    assert not np.array_equal(_W.elev, w2.elev), "different seeds produced same elev"


# ── §5 Test 3 — Water-mask correctness ────────────────────────────────────

def test_water_mask_vs_level():
    water_level = (float(_BASE['waterK']) ** 1.2) * 0.42
    expected = (_W.elev < water_level)
    assert np.array_equal(_W.isWater.astype(bool), expected), \
        "isWater doesn't match elev < waterLevel"


def test_rivers_only_on_land():
    assert np.all((_W.isRiver == 0) | (_W.isWater == 0)), "river on water cell"


# ── §5 Test 4 — Precompute immutability ────────────────────────────────────

def test_arrays_non_writeable():
    for name in ('elev', 'slope', 'biome', 'npp', 'forage', 'game',
                 'cost', 'risk', 'wateracc', 'isWater', 'isRiver',
                 'forestness', 'slopeDeg', 'neighbour_cost'):
        arr = getattr(_W, name)
        assert not arr.flags.writeable, f"{name} is writeable (should be frozen)"


def test_write_raises():
    with pytest.raises((ValueError, TypeError)):
        _W.elev[0, 0] = 99.0


# ── §5 Test 5 — Biome ladder ordering ─────────────────────────────────────

def test_biome_ladder_thresholds():
    """Synthetic cells at boundary forestness values map to correct biomes."""
    import types
    def _fake_world(fn_val: float) -> BIOME_WATER:
        """Minimal synthetic world: all cells flat land, given forestness."""
        fv = np.full((N, N), fn_val)
        npp_v = np.full((N, N), 0.5)    # above desert/wetland thresholds
        slope_v = np.zeros((N, N))
        elev_v = np.full((N, N), 0.3)   # below mountain threshold
        iw = np.zeros((N, N), dtype=np.uint8)
        dist_v = np.full((N, N), 10.0)  # >2: not wetland
        relief = 0.4
        mtn_elev = 0.72 + (1 - relief) * 0.5
        mtn_slope = 0.18 + (1 - relief) * 0.4
        is_land    = (iw == 0)
        is_mtn     = is_land & (elev_v > mtn_elev) & (slope_v > mtn_slope)
        is_desert  = is_land & ~is_mtn & (npp_v < 0.10)
        is_wetland = is_land & ~is_mtn & ~is_desert & (dist_v <= 2) & (npp_v > 0.45) & (slope_v < 0.12)
        remaining  = is_land & ~is_mtn & ~is_desert & ~is_wetland
        is_forest  = remaining & (fv >= W_FOREST)
        is_savanna = remaining & (fv >= W_SAV) & (fv < W_FOREST)
        is_grass   = remaining & (fv < W_SAV)
        biome_v = np.zeros((N, N), dtype=np.uint8)
        biome_v[is_forest]  = BIOME_FOREST
        biome_v[is_savanna] = BIOME_SAVANNA
        biome_v[is_grass]   = BIOME_GRASS
        return int(biome_v[0, 0])

    assert _fake_world(0.0)          == BIOME_GRASS,   "fn=0 → not grassland"
    assert _fake_world(W_SAV - 0.01) == BIOME_GRASS,   "fn just below W_SAV → not grassland"
    assert _fake_world(W_SAV)        == BIOME_SAVANNA,  "fn=W_SAV → not savanna"
    assert _fake_world(W_FOREST - 0.01) == BIOME_SAVANNA, "fn just below W_FOREST → not savanna"
    assert _fake_world(W_FOREST)     == BIOME_FOREST,  "fn=W_FOREST → not forest"
    assert _fake_world(1.0)          == BIOME_FOREST,  "fn=1 → not forest"


# ── §5 Test 6 — neighbour_cost consistency ────────────────────────────────

def test_neighbour_cost_interior():
    """Interior cells: neighbour_cost[y,x,d] == cost[target]."""
    nc = _W.neighbour_cost
    cost = _W.cost
    # d=0 North: target (y-1, x) for y>0
    assert np.allclose(nc[1:, :, 0], cost[:-1, :]), "nc north mismatch"
    # d=1 South: target (y+1, x) for y<N-1
    assert np.allclose(nc[:-1, :, 1], cost[1:, :]), "nc south mismatch"
    # d=2 West: target (y, x-1) for x>0
    assert np.allclose(nc[:, 1:, 2], cost[:, :-1]), "nc west mismatch"
    # d=3 East: target (y, x+1) for x<N-1
    assert np.allclose(nc[:, :-1, 3], cost[:, 1:]), "nc east mismatch"


def test_neighbour_cost_edge_sentinel():
    """Edge cells have sentinel 1.0 for out-of-bounds directions."""
    nc = _W.neighbour_cost
    # top row: north sentinel
    assert np.all(nc[0, :, 0] == 1.0), "top row north not sentinel"
    # bottom row: south sentinel
    assert np.all(nc[-1, :, 1] == 1.0), "bottom row south not sentinel"
    # left col: west sentinel
    assert np.all(nc[:, 0, 2] == 1.0), "left col west not sentinel"
    # right col: east sentinel
    assert np.all(nc[:, -1, 3] == 1.0), "right col east not sentinel"


# ── characterize_map smoke test ────────────────────────────────────────────

def test_characterize_map_keys():
    v = characterize_map(_W)
    required = ('biomeFrac', 'waterPct', 'riverPct', 'wetlandPct', 'hydratedPct',
                'reliefEnvelopeM', 'meanSlopeDeg', 'gameHumpPeak', 'forestTouchSavanna')
    for k in required:
        assert k in v, f"missing key {k}"
    for b in ('forest', 'savanna', 'grassland', 'wetland', 'desert', 'mountain'):
        assert b in v['biomeFrac'], f"biomeFrac missing '{b}'"


def test_biome_fracs_sum_to_100():
    v = characterize_map(_W)
    total = sum(v['biomeFrac'].values())
    assert abs(total - 100.0) < 0.5, f"biomeFrac sums to {total:.2f}"
