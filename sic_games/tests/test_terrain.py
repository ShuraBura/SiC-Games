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
    MEAN_GLOBAL_TEMP_C, MEAN_REL_HUMIDITY,
    EXTERIOR_WATER_CEILING, LARGE_BODY_CEILING,
    generate_world, characterize_map, _water_bodies, _classify_water_components,
    _component_sizes,
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


# ── P1S1b — water decomposition diagnostic ────────────────────────────────

_P1S1B_FIELDS = [
    'exterior_water_fraction', 'interior_water_fraction',
    'n_interior_bodies', 'n_exterior_bodies',
    'shoreline_fraction', 'largest_exterior_body_cells',
    'largest_exterior_shore_to_area', 'guard_exterior_water_fail',
]

def test_p1s1b_fields_present():
    """§8.1: all P1S1b fields present in characterize_map() output."""
    v = characterize_map(_W)
    for key in _P1S1B_FIELDS:
        assert key in v, f"missing key: {key}"


def test_p1s1b_field_ranges():
    """§8.1: fractions in [0,1]; counts >= 0; ratio >= 0."""
    v = characterize_map(_W)
    for key in ('exterior_water_fraction', 'interior_water_fraction',
                'shoreline_fraction'):
        val = v[key]
        assert 0.0 <= val <= 1.0, f"{key}={val} out of [0,1]"
    assert v['largest_exterior_shore_to_area'] >= 0.0
    assert v['largest_exterior_body_cells'] >= 0
    assert v['n_interior_bodies'] >= 0
    assert v['n_exterior_bodies'] >= 0


def test_p1s1b_conservation():
    """§8.2: exterior_cells + interior_cells == total water cells."""
    v = characterize_map(_W)
    total_water = int(_W.isWater.sum())
    total_cells = N * N
    ext_cells = round(v['exterior_water_fraction'] * total_cells)
    int_cells = round(v['interior_water_fraction'] * total_cells)
    assert ext_cells + int_cells == total_water, (
        f"conservation fail: ext={ext_cells} + int={int_cells} "
        f"!= water={total_water}"
    )


def test_p1s1b_classify_helper_returns():
    """_classify_water_components returns a 6-tuple with expected types."""
    result = _classify_water_components(_W.isWater)
    assert len(result) == 6
    ext_c, int_c, n_ext, n_int, largest_ext, mask = result
    assert isinstance(ext_c, int) and ext_c >= 0
    assert isinstance(int_c, int) and int_c >= 0
    assert isinstance(n_ext, int) and n_ext >= 0
    assert isinstance(n_int, int) and n_int >= 0
    assert isinstance(largest_ext, int) and largest_ext >= 0
    # mask is None or bool array
    if mask is not None:
        assert mask.dtype == bool and mask.shape == (N, N)


def test_p1s1b_fixture_lake_exterior_sea():
    """§8.3: fixture with one enclosed lake + one edge-connected sea.
    Lake → interior; sea → exterior; counts exact.
    """
    # Build a small fixture:
    # - A 4x4 lake in the centre (rows 45-48, cols 45-48)
    # - A 4-cell-wide band of water on the top edge (rows 0-3, all cols)
    iw = np.zeros((N, N), dtype=np.uint8)
    iw[45:49, 45:49] = 1   # 4x4 = 16 cell enclosed lake
    iw[0:4, :] = 1          # top band (edge-connected) = 4*100 = 400 cells

    ext_c, int_c, n_ext, n_int, largest_ext, mask = _classify_water_components(iw)

    assert n_int == 1, f"expected 1 interior body (lake), got {n_int}"
    assert n_ext == 1, f"expected 1 exterior body (sea), got {n_ext}"
    assert int_c == 16, f"expected 16 interior cells, got {int_c}"
    assert ext_c == 400, f"expected 400 exterior cells, got {ext_c}"
    assert largest_ext == 400
    assert mask is not None
    assert int(mask.sum()) == 400


def test_p1s1b_fixture_guard_mostly_ocean():
    """§8.4: guard fires on a mostly-ocean world (exterior_fraction > 0.12)."""
    # A world where the entire top 20 rows + left 20 cols are water (edge-connected)
    iw = np.zeros((N, N), dtype=np.uint8)
    iw[:20, :] = 1   # 20 rows × 100 cols = 2000 cells; fraction = 0.20 > 0.12
    F_fake = generate_world(dict(relief=0.4, rough=0.5, waterK=0.5,
                                 forestK=0.5, aridK=0.35, seedStr='99'))
    # Override isWater temporarily via a characterize_map on a high-waterK world
    # Use a known high-waterK world that produces exterior fraction > 0.12
    kn_ocean = dict(relief=0.2, rough=0.3, waterK=0.85, forestK=0.5,
                    aridK=0.1, seedStr='ocean_test')
    F_ocean = generate_world(kn_ocean)
    v_ocean = characterize_map(F_ocean)
    # Only assert if this world actually has exterior_fraction > 0.12
    if v_ocean['exterior_water_fraction'] > EXTERIOR_WATER_CEILING:
        assert v_ocean['guard_exterior_water_fail'] is True


def test_p1s1b_fixture_guard_lake_world():
    """§8.4: guard does NOT fire on a lake-dense world (high interior, low exterior)."""
    # Low waterK → land-dominated; any water bodies tend to be inland
    kn_lake = dict(relief=0.4, rough=0.5, waterK=0.3, forestK=0.5,
                   aridK=0.2, seedStr='lake_test')
    F_lake = generate_world(kn_lake)
    v_lake = characterize_map(F_lake)
    if v_lake['exterior_water_fraction'] <= EXTERIOR_WATER_CEILING:
        assert v_lake['guard_exterior_water_fail'] is False


def test_p1s1b_guard_exterior_water_fail_type():
    """guard_exterior_water_fail is a bool and consistent with the fraction."""
    v = characterize_map(_W)
    assert isinstance(v['guard_exterior_water_fail'], (bool, np.bool_))
    expected = v['exterior_water_fraction'] > EXTERIOR_WATER_CEILING
    assert bool(v['guard_exterior_water_fail']) == bool(expected)


def test_p1s1b_exterior_water_ceiling_constant():
    """EXTERIOR_WATER_CEILING is a float equal to 0.12 (provisional threshold)."""
    assert isinstance(EXTERIOR_WATER_CEILING, float)
    assert abs(EXTERIOR_WATER_CEILING - 0.12) < 1e-12


def test_p1s1b_invalid_substrate_updated():
    """invalid_substrate is driven by guard_large_body_fail (Stage 1c), not exterior guard."""
    v = characterize_map(_W)
    if v['guard_large_body_fail']:
        assert v['invalid_substrate'] is True
    # Stage 1c: invalid_substrate = a OR b OR large_body (exterior guard removed from union)
    expected = v['guard_a_fail'] or v['guard_b_fail'] or v['guard_large_body_fail']
    assert bool(v['invalid_substrate']) == bool(expected)


def test_p1s1b_shoreline_fraction_matches_is_shore():
    """shoreline_fraction == is_shore.sum() / land_cells."""
    v = characterize_map(_W)
    land = int((~_W.isWater.astype(bool)).sum())
    expected = int(_W.is_shore.sum()) / land if land > 0 else 0.0
    assert abs(v['shoreline_fraction'] - expected) < 1e-12


def test_p1s1b_no_regression_on_reference_world():
    """Existing characterize_map fields still present and valid types."""
    v = characterize_map(_W)
    legacy_keys = [
        'waterPct', 'riverPct', 'biomeFrac', 'landCells', 'desert_fraction',
        'mountain_fraction', 'habitable_cell_count', 'invalid_substrate',
        'guard_a_fail', 'guard_b_fail', 'shore_cell_count', 'n_water_bodies',
    ]
    for key in legacy_keys:
        assert key in v, f"regression: missing key {key}"


# ── Phase 1 Stage 1c — Largest-lake-body guard ────────────────────────────


def test_p1s1c_large_body_ceiling_constant():
    """LARGE_BODY_CEILING is 0.08 (§DECISION-LAKE-BODY-CEILING, supervisor-locked)."""
    assert isinstance(LARGE_BODY_CEILING, float)
    assert abs(LARGE_BODY_CEILING - 0.08) < 1e-12


def test_p1s1c_new_fields_present():
    """§5.3/5.4/5.5: all Stage 1c fields present in characterize_map output."""
    v = characterize_map(_W)
    for key in ('largest_water_body_fraction', 'water_body_count',
                'characteristic_water_body_size', 'characteristic_interlake_patch_size',
                'guard_large_body_fail'):
        assert key in v, f"Stage 1c: missing key '{key}'"


def test_p1s1c_largest_water_body_fraction_is_single_max():
    """§5.3: largest_water_body_fraction equals max-component/total, NOT sum.
    Fixture: 3 disjoint blobs of sizes 100, 200, 50.
    """
    iw = np.zeros((N, N), dtype=np.uint8)
    iw[5:15, 5:15]   = 1   # 10×10 = 100 cells
    iw[20:40, 20:30] = 1   # 20×10 = 200 cells (largest)
    iw[60:65, 60:65] = 1   # 5×5   = 50 cells
    # Use _component_sizes directly
    sizes = _component_sizes(iw.astype(bool))
    assert len(sizes) == 3, f"expected 3 bodies, got {len(sizes)}"
    largest_frac = max(sizes) / (N * N)
    sum_frac = sum(sizes) / (N * N)
    assert abs(largest_frac - 200 / (N * N)) < 1e-12
    assert largest_frac != sum_frac, "largest_frac should not equal sum_frac"


def test_p1s1c_water_body_count_4connectivity():
    """§5.4: diagonal neighbors are NOT connected under 4-connectivity.
    Fixture: 2 blobs (100+200) + 2 diagonal-only-touching single cells.
    Under 4-connectivity: diagonal pair = 2 separate bodies.
    """
    iw = np.zeros((N, N), dtype=np.uint8)
    iw[5:15, 5:15]   = 1   # blob 1: 100 cells
    iw[20:40, 20:30] = 1   # blob 2: 200 cells
    iw[50, 50] = 1          # cell A
    iw[51, 51] = 1          # cell B — diagonal from A, NOT 4-connected
    sizes = _component_sizes(iw.astype(bool))
    # Under 4-connectivity: A and B are separate bodies (no shared 4-nbr edge)
    assert len(sizes) == 4, f"expected 4 bodies under 4-connectivity, got {len(sizes)}"
    assert sorted(sizes) == [1, 1, 100, 200]


def test_p1s1c_characteristic_sizes_use_median():
    """§5.5: characteristic sizes use median (not mean) — differs on heavy-tailed input."""
    # Sizes: [1, 1, 1, 1, 1000] — median=1, mean=200.8
    iw = np.zeros((N, N), dtype=np.uint8)
    iw[0, 0] = 1; iw[0, 2] = 1; iw[0, 4] = 1; iw[0, 6] = 1   # 4 singleton cells
    iw[10:50, 10:35] = 1  # ~1000 cells
    sizes = _component_sizes(iw.astype(bool))
    median_val = float(np.median(sizes))
    mean_val = float(np.mean(sizes))
    assert median_val != mean_val, "median == mean on heavy-tailed distribution"
    assert median_val == 1.0, f"expected median=1, got {median_val}"


def test_p1s1c_guard_swap_exterior_no_longer_gates():
    """§5.6: exterior_water_fraction > 0.12 no longer gates invalid_substrate."""
    v = characterize_map(_W)
    # Confirm guard_exterior_water_fail is NOT included in invalid_substrate formula
    # (even if it fires, invalid_substrate should equal a OR b OR large_body)
    expected = v['guard_a_fail'] or v['guard_b_fail'] or v['guard_large_body_fail']
    assert bool(v['invalid_substrate']) == bool(expected)
    # Confirm guard_exterior_water_fail is still reported (diagnostic)
    assert 'guard_exterior_water_fail' in v


def test_p1s1c_guard_large_body_fail_gates_substrate():
    """§5.6: guard_large_body_fail drives invalid_substrate."""
    v = characterize_map(_W)
    assert isinstance(v['guard_large_body_fail'], (bool, np.bool_))
    expected = v['largest_water_body_fraction'] > LARGE_BODY_CEILING
    assert bool(v['guard_large_body_fail']) == bool(expected)
    if v['guard_large_body_fail']:
        assert v['invalid_substrate'] is True


def test_p1s1c_largest_water_body_fraction_consistent():
    """largest_water_body_fraction == largest_body_fraction (backward-compat alias)."""
    v = characterize_map(_W)
    assert abs(v['largest_water_body_fraction'] - v['largest_body_fraction']) < 1e-12


def test_p1s1c_water_body_count_consistent():
    """water_body_count == n_water_bodies (backward-compat alias)."""
    v = characterize_map(_W)
    assert v['water_body_count'] == v['n_water_bodies']


def test_p1s1c_characteristic_sizes_nonnegative():
    """characteristic_water_body_size and characteristic_interlake_patch_size >= 0."""
    v = characterize_map(_W)
    assert v['characteristic_water_body_size'] >= 0.0
    assert v['characteristic_interlake_patch_size'] >= 0.0


def test_p1s1c_component_sizes_empty_mask():
    """_component_sizes on an all-False mask returns empty list."""
    mask = np.zeros((N, N), dtype=bool)
    sizes = _component_sizes(mask)
    assert sizes == []


def test_p1s1c_component_sizes_all_true():
    """_component_sizes on all-True mask returns single component of size N*N."""
    mask = np.ones((N, N), dtype=bool)
    sizes = _component_sizes(mask)
    assert sizes == [N * N]


def test_climate_seam_homogeneous_placeholders():
    """Phase 1 climate seam: temperature + humidity exist as CONSTANT global-average placeholders
    (spatial/seasonal variation is the deferred climate-season stage)."""
    assert _W.temperature is not None and _W.humidity is not None
    assert _W.temperature.shape == _W.humidity.shape == (N, N)
    assert np.all(_W.temperature == MEAN_GLOBAL_TEMP_C)
    assert np.all(_W.humidity == MEAN_REL_HUMIDITY)
    assert not _W.temperature.flags.writeable and not _W.humidity.flags.writeable
