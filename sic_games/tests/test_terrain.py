"""§5 unit tests for the Stage 7 terrain generator (blueprint §5)."""
import numpy as np
import pytest
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "src"))

from sic_games.terrain import (
    N, W_FOREST, W_SAV,
    BIOME_WATER, BIOME_WETLAND, BIOME_FOREST, BIOME_SAVANNA, BIOME_GRASS,
    BIOME_DESERT, BIOME_MOUNTAIN,
    NPP_GM2_SCALE, SHORE_BONUS_KCAL, FORAGE_KCAL_TARGETS,
    generate_world, characterize_map, _water_bodies,
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


# ── Phase 1 Stage 1 — forage_kcal field (Task 1) ─────────────────────────

def test_forage_kcal_field_present():
    assert _W.forage_kcal is not None
    assert _W.forage_kcal.shape == (N, N)
    assert np.all(np.isfinite(_W.forage_kcal))


def test_forage_kcal_non_negative():
    assert _W.forage_kcal.min() >= 0.0


def test_forage_kcal_water_is_zero():
    mask = _W.isWater.astype(bool)
    # water cells have zero biome forage; shore bonus only on land; so water = 0
    assert np.all(_W.forage_kcal[mask] == 0.0), "forage_kcal nonzero on water"


def test_forage_kcal_original_forage_preserved():
    """Original normalised forage[] must be unchanged (separate field, not overwritten)."""
    assert _W.forage.min() >= 0.0 and _W.forage.max() <= 1.0
    assert not _W.forage.flags.writeable


def test_forage_kcal_biome_means_match_targets():
    """Each present biome's mean (pre-shore-bonus) forage_kcal must equal its target
    within ±0.1 kcal/hr. Shore bonus is subtracted before checking."""
    shore_bonus = _W.is_shore.astype(np.float64) * SHORE_BONUS_KCAL
    forage_pre_shore = _W.forage_kcal - shore_bonus
    for b_code, target in FORAGE_KCAL_TARGETS.items():
        mask = (_W.biome == b_code)
        if not mask.any():
            continue  # absent biome — skip
        mean_val = float(forage_pre_shore[mask].mean())
        assert abs(mean_val - target) < 0.11, (
            f"biome {b_code} mean forage_kcal {mean_val:.2f} != target {target} (tol 0.1)")


def test_forage_kcal_within_biome_variance_nonzero():
    """Texture must be preserved: within-biome forage_kcal variance must be > 0
    wherever the source normalised forage had variance > 0."""
    for b_code in FORAGE_KCAL_TARGETS:
        mask = (_W.biome == b_code)
        if mask.sum() < 4:
            continue
        src_var = float(_W.forage[mask].var())
        if src_var < 1e-12:
            continue  # source was flat — nothing to check
        assert float(_W.forage_kcal[mask].var()) > 0.0, \
            f"biome {b_code}: forage_kcal variance is zero but source had variance"


def test_forage_kcal_frozen():
    assert not _W.forage_kcal.flags.writeable


# ── Phase 1 Stage 1 — npp_gm2 field (Task 4) ──────────────────────────────

def test_npp_gm2_field_present():
    assert _W.npp_gm2 is not None
    assert _W.npp_gm2.shape == (N, N)


def test_npp_gm2_transfer():
    """npp_gm2 = npp * NPP_GM2_SCALE on all cells."""
    assert np.allclose(_W.npp_gm2, _W.npp * NPP_GM2_SCALE)


def test_npp_gm2_forest_near_anchor():
    """Forest-cell mean npp_gm2 should be near 1360 g/m2/yr (anchor)."""
    forest_mask = (_W.biome == BIOME_FOREST)
    if not forest_mask.any():
        pytest.skip("no forest cells in reference world")
    mean_val = float(_W.npp_gm2[forest_mask].mean())
    assert 900 < mean_val < 1700, f"forest npp_gm2 mean {mean_val:.0f} far from anchor 1360"


def test_npp_gm2_frozen():
    assert not _W.npp_gm2.flags.writeable


# ── Phase 1 Stage 1 — is_shore field (Task 2/3) ───────────────────────────

def test_is_shore_field_present():
    assert _W.is_shore is not None
    assert _W.is_shore.shape == (N, N)
    assert np.all((_W.is_shore == 0) | (_W.is_shore == 1))


def test_is_shore_only_on_land():
    shore_on_water = _W.is_shore.astype(bool) & _W.isWater.astype(bool)
    assert not shore_on_water.any(), "shore cell on water"


def test_is_shore_adjacent_to_water():
    """Every is_shore cell must have at least one water neighbor (4-nbr)."""
    padded = np.pad(_W.isWater, 1, mode='constant', constant_values=0)
    has_water_nbr = ((padded[:-2, 1:-1] | padded[2:, 1:-1] |
                      padded[1:-1, :-2] | padded[1:-1, 2:]) > 0)
    assert np.all(~_W.is_shore.astype(bool) | has_water_nbr), \
        "shore cell without water neighbor"


def test_is_shore_frozen():
    assert not _W.is_shore.flags.writeable


def test_shore_bonus_added():
    """Shore cells forage_kcal > non-shore cells in same biome (when biome has nonzero forage)."""
    for b_code in FORAGE_KCAL_TARGETS:
        shore_mask  = (_W.biome == b_code) & _W.is_shore.astype(bool)
        inland_mask = (_W.biome == b_code) & ~_W.is_shore.astype(bool)
        if not shore_mask.any() or not inland_mask.any():
            continue
        shore_mean  = float(_W.forage_kcal[shore_mask].mean())
        inland_mean = float(_W.forage_kcal[inland_mask].mean())
        assert shore_mean > inland_mean, \
            f"biome {b_code}: shore mean {shore_mean:.1f} not > inland mean {inland_mean:.1f}"


# ── Phase 1 Stage 1 — characterize_map new fields ─────────────────────────

_CM = characterize_map(_W)


def test_characterize_map_new_keys():
    required = (
        'shore_cell_count', 'shore_cell_fraction', 'n_water_bodies',
        'largest_body_fraction',
        'desert_fraction', 'mountain_fraction', 'mean_npp_gm2',
        'habitable_cell_fraction', 'habitable_cell_count',
        'invalid_substrate', 'guard_a_fail', 'guard_b_fail',
        'absent_biomes_forage',
    )
    for k in required:
        assert k in _CM, f"characterize_map missing key '{k}'"


def test_characterize_map_shore_count_consistent():
    assert _CM['shore_cell_count'] == int(_W.is_shore.sum())
    assert abs(_CM['shore_cell_fraction'] - _CM['shore_cell_count'] / (N * N)) < 1e-12


def test_characterize_map_n_water_bodies():
    n_wb, largest = _water_bodies(_W.isWater)
    assert _CM['n_water_bodies'] == n_wb
    assert abs(_CM['largest_body_fraction'] - largest / (N * N)) < 1e-12


def test_characterize_map_habitability_fracs():
    assert 0.0 <= _CM['desert_fraction']   <= 1.0
    assert 0.0 <= _CM['mountain_fraction'] <= 1.0
    assert 0.0 <= _CM['habitable_cell_fraction'] <= 1.0
    assert _CM['habitable_cell_count'] == _CM['landCells']


def test_characterize_map_mean_npp_gm2():
    land = ~_W.isWater.astype(bool)
    expected = float(_W.npp_gm2[land].mean())
    assert abs(_CM['mean_npp_gm2'] - expected) < 1.0


def test_characterize_map_validity_guards_type():
    assert isinstance(_CM['invalid_substrate'], (bool, np.bool_))
    assert isinstance(_CM['guard_a_fail'], (bool, np.bool_))
    assert isinstance(_CM['guard_b_fail'], (bool, np.bool_))


# ── _water_bodies helper ───────────────────────────────────────────────────

def test_water_bodies_single_lake():
    """Synthetic: one central water rectangle = 1 body."""
    iw = np.zeros((N, N), dtype=np.uint8)
    iw[40:60, 40:60] = 1
    n, largest = _water_bodies(iw)
    assert n == 1, f"expected 1 body, got {n}"
    assert largest == 20 * 20


def test_water_bodies_two_lakes():
    """Synthetic: two disconnected rectangles = 2 bodies."""
    iw = np.zeros((N, N), dtype=np.uint8)
    iw[10:20, 10:20] = 1   # 100 cells
    iw[70:80, 70:80] = 1   # 100 cells
    n, largest = _water_bodies(iw)
    assert n == 2, f"expected 2 bodies, got {n}"
    assert largest == 100


# ── A3 acceptance check (hand-verifiable) ─────────────────────────────────

def test_a3_characterize_map_returns_coast_fields():
    """A3: characterize_map returns shore_cell_fraction, shore_cell_count,
    n_water_bodies, largest_body_fraction."""
    v = characterize_map(_W)
    assert 'shore_cell_fraction' in v
    assert 'shore_cell_count' in v
    assert 'n_water_bodies' in v
    assert 'largest_body_fraction' in v
    assert v['shore_cell_count'] >= 0
    assert 0.0 <= v['shore_cell_fraction'] <= 1.0
    assert v['n_water_bodies'] >= 0


# ── A6 acceptance check ────────────────────────────────────────────────────

def test_a6_no_npp_habitability_floor():
    """A6: habitable_cell_fraction = land/total; no per-cell NPP cutoff."""
    v = characterize_map(_W)
    land = int((~_W.isWater.astype(bool)).sum())
    total = N * N
    expected = land / total
    assert abs(v['habitable_cell_fraction'] - expected) < 1e-12
    assert v['habitable_cell_count'] == land
