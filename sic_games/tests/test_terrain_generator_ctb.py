"""CTB for the TERRAIN GENERATOR: water, rivers, and per-biome feature abundance (R-106, 2026-08-22).

WHY THIS FILE EXISTS. The generator underpins every result this project has produced and had no coherence
benchmark at all. It was audited only when a downstream result looked wrong -- villages preferring DESERT to
forest -- and the cause turned out to sit upstream of every mechanism being blamed: rivers are allocated by
drainage AREA with no water balance, so deserts get perennial rivers, `aquatic_food` scores them as cold
anadromous fisheries, and settlement follows the water.

WHAT WAS SURVEYED BEFORE ANY ASSERTION WAS WRITTEN. All 25 (terrain x climate) presets at seed 0. The
structural invariants below were MEASURED to hold, so they are regression guards rather than hopes; the
hydrology assertions were measured to FAIL, and are written to say so out loud rather than be skipped.

THE HEADLINE MEASUREMENT, 20 worlds, fraction of biome cells carrying a river:
                    desert   forest   ratio
    runoff OFF       0.075    0.046    1.63   <- deserts are WETTER than forests
    runoff ON        0.016    0.059    0.27   <- forests wetter, as physics requires
"""
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "sic_games" / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "sic_games" / "src"))

import sic_games.terrain as T  # noqa: E402

BIOME_NAME = {1: "wetland", 2: "forest", 3: "savanna", 4: "grass", 5: "desert", 6: "mountain"}
# A representative spread: wet/dry, flat/relief. The full 25-preset sweep is marked slow at the bottom.
CORE = [("coastal", "temperate"), ("coastal", "tropical"), ("flat", "subtropical"),
        ("alpine", "boreal"), ("flat", "savanna"), ("mountainous", "temperate")]
_CACHE: dict = {}


def world(terr, clim, runoff=False):
    key = (terr, clim, runoff)
    if key not in _CACHE:
        k = dict(T.world_lottery_climate(0, terrain=terr, climate=clim))
        if runoff:
            k["runoff_rivers"] = True
        _CACHE[key] = T.generate_world(k, mode="climate")
    return _CACHE[key]


def parts(f):
    land = np.asarray(f.isWater) == 0
    return dict(land=land, water=np.asarray(f.isWater).astype(bool), biome=np.asarray(f.biome),
                river=np.asarray(f.isRiver).astype(bool), shore=np.asarray(f.is_shore).astype(bool),
                aq=np.asarray(f.aquatic_food), precip=np.asarray(f.precip_mm),
                temp=np.asarray(f.temperature), forage=np.asarray(f.forage_kcal),
                npp=np.asarray(f.npp_gm2))


# ─────────────────────────── determinism ──────────────────────────────────────────────────────────────

def test_same_knobs_and_seed_give_byte_identical_fields():
    """The generator's stated contract (module docstring): same (knobs, seedStr) -> byte-identical arrays.
    Every reproducibility claim in this project rests on it."""
    k = T.world_lottery_climate(0, terrain="coastal", climate="temperate")
    a, b = T.generate_world(dict(k), mode="climate"), T.generate_world(dict(k), mode="climate")
    for name in ("isWater", "isRiver", "biome", "precip_mm", "forage_kcal", "aquatic_food", "npp_gm2"):
        assert np.array_equal(np.asarray(getattr(a, name)), np.asarray(getattr(b, name))), \
            f"{name} is not reproducible from the same knobs"


# ─────────────────────────── structural invariants (measured to hold) ─────────────────────────────────

@pytest.mark.parametrize("terr,clim", CORE)
def test_no_field_carries_nan_or_inf(terr, clim):
    p = parts(world(terr, clim))
    for name in ("aq", "precip", "temp", "forage", "npp"):
        assert np.isfinite(p[name]).all(), f"{terr}-{clim}: {name} contains NaN or inf"


@pytest.mark.parametrize("terr,clim", CORE)
def test_rivers_and_shore_never_sit_on_open_water(terr, clim):
    p = parts(world(terr, clim))
    assert not p["river"][p["water"]].any(), "a river cell is also an open-water cell"
    assert not p["shore"][p["water"]].any(), "is_shore is set on an open-water cell"


@pytest.mark.parametrize("terr,clim", CORE)
def test_aquatic_food_is_bounded_and_only_where_there_is_water(terr, clim):
    """`aquatic_food` = max(anadromous river limb, coastal shellfish limb), so it must be ZERO on land that
    is neither river-adjacent nor shore. If it leaks elsewhere, villages get sited on dry ground."""
    p = parts(world(terr, clim))
    aq = p["aq"]
    assert aq.min() >= 0.0 and aq.max() <= 1.0, f"aquatic_food outside [0,1]: {aq.min()}..{aq.max()}"
    nbr = p["river"].copy()
    for ax in (0, 1):
        for s in (-1, 1):
            nbr |= np.roll(p["river"], s, ax)
    stray = p["land"] & ~nbr & ~p["shore"] & (aq > 1e-9)
    assert not stray.any(), f"{int(stray.sum())} cells have aquatic food with no river adjacency and no shore"


@pytest.mark.parametrize("terr,clim", CORE)
def test_every_biome_label_re_derives_from_its_own_climate(terr, clim):
    """A cell labelled desert must still classify as desert when `whittaker_biome` is re-run on its own
    temperature and precipitation. Otherwise the label and the climate driving it have drifted apart."""
    p = parts(world(terr, clim))
    redo = T.whittaker_biome(p["temp"], p["precip"])
    for code in (2, 3, 4, 5):          # the four Whittaker CLIMATE biomes (wetland/mountain are overlays)
        m = p["land"] & (p["biome"] == code)
        if m.sum() < 30:
            continue
        assert int((redo[m] != code).sum()) == 0, \
            f"{terr}-{clim}: {BIOME_NAME[code]} cells disagree with a whittaker_biome re-run"


# ─────────────────────────── the filed per-biome forage anchors ───────────────────────────────────────

@pytest.mark.parametrize("terr,clim", CORE)
def test_forage_reproduces_the_filed_per_biome_anchor(terr, clim):
    """FORAGE_KCAL_TARGETS is lit-anchored per biome (Hill 1987 Ache palm, Berbesque & Marlowe Hadza tuber,
    Rhode & Rhode limber pine ...). The generator must actually deliver those means.

    SHORE CELLS ARE EXCLUDED, and that exclusion is itself tested below. `SHORE_BONUS_KCAL` (Bird 1997 Meriam
    reef-flat, 1491.5) is ADDED on top of the biome rate, which inflates coastal savanna to 3.14x its anchor.
    That is by design; scoring shore cells against a land anchor would manufacture a defect that is not there.
    """
    p = parts(world(terr, clim))
    for code, target in T.FORAGE_KCAL_TARGETS.items():
        m = p["land"] & (p["biome"] == code) & ~p["shore"]
        if m.sum() < 30:
            continue
        ratio = float(p["forage"][m].mean()) / target
        assert 0.85 <= ratio <= 1.20, \
            f"{terr}-{clim}: {BIOME_NAME[code]} forage is {ratio:.2f}x its filed anchor {target}"


def test_the_shore_bonus_is_real_so_excluding_shore_is_not_hiding_anything():
    """POSITIVE CONTROL for the exclusion above. If shore cells did NOT exceed the land anchor, the exclusion
    would be suppressing a real signal instead of removing a known additive term."""
    p = parts(world("coastal", "savanna"))
    code = 3
    on = p["land"] & (p["biome"] == code) & p["shore"]
    off = p["land"] & (p["biome"] == code) & ~p["shore"]
    if on.sum() < 10:
        pytest.skip("no shore savanna cells in this world")
    assert float(p["forage"][on].mean()) > float(p["forage"][off].mean()) * 1.5, \
        "shore cells do not carry the shore bonus -- the exclusion in the anchor test is unjustified"


# ─────────────────────────── THE HYDROLOGY DEFECT ─────────────────────────────────────────────────────

def _river_density(f, code):
    p = parts(f)
    m = p["land"] & (p["biome"] == code)
    return float(p["river"][m].mean()) if m.sum() >= 30 else None


def test_DEFECT_deserts_are_wetter_than_forests_without_runoff_weighting():
    """DOCUMENTS A KNOWN DEFECT so it cannot be quietly fixed or quietly worsened.

    `flow = np.ones(N*N)` gives every cell one unit of runoff regardless of rainfall, so `isRiver` is pure
    drainage AREA. Measured over 20 worlds: desert river density 0.075 against forest 0.046 -- deserts are
    1.63x WETTER than forests. Physically, catchment discharge is the sum of (P - ET); in a desert that is
    negative, leaving ephemeral wadis and endorheic basins, and only ALLOGENIC rivers (Nile, Colorado) survive.

    When `runoff_rivers` is adopted as the default, this test SHOULD fail and be deleted in favour of the one
    below. That is the intended lifecycle, not an accident.
    """
    d = _river_density(world("coastal", "temperate"), 5)
    f = _river_density(world("coastal", "temperate"), 2)
    if d is None or f is None:
        pytest.skip("world lacks enough desert or forest cells")
    assert d > f, ("desert is no longer wetter than forest with runoff weighting OFF -- if this was fixed "
                   "deliberately, delete this test and keep the runoff one")


@pytest.mark.parametrize("terr,clim", [("coastal", "temperate"), ("flat", "savanna")])
def test_runoff_weighting_makes_forests_wetter_than_deserts(terr, clim):
    """THE FIX, asserted as physics rather than as a tuned number: weighting flow accumulation by
    runoff = max(0, P - PET) reverses the ordering. Measured over 20 worlds, desert/forest river density goes
    from 1.63 to 0.27."""
    d = _river_density(world(terr, clim, runoff=True), 5)
    f = _river_density(world(terr, clim, runoff=True), 2)
    if d is None or f is None:
        pytest.skip("world lacks enough desert or forest cells")
    assert d < f, f"{terr}-{clim}: desert river density {d:.3f} still >= forest {f:.3f} with runoff weighting"


def test_a_pure_desert_world_has_essentially_no_perennial_rivers():
    """flat-subtropical is 100% desert. With no wetter biome anywhere upstream there is no allogenic source,
    so a physical generator must produce almost no perennial river. Measured: 474 river cells -> 0."""
    p_off = parts(world("flat", "subtropical"))
    p_on = parts(world("flat", "subtropical", runoff=True))
    n_off, n_on = int(p_off["river"].sum()), int(p_on["river"].sum())
    assert n_off > 100, f"expected the uniform-flow generator to carve many desert rivers, got {n_off}"
    assert n_on <= n_off * 0.05, \
        f"a 100% desert world still carries {n_on} river cells with runoff weighting (was {n_off})"


def test_runoff_weighting_is_bit_exact_when_off():
    """NEGATIVE CONTROL. Every prior world must stay reproducible, so the knob absent and the knob explicitly
    False must give byte-identical fields."""
    k = T.world_lottery_climate(0, terrain="coastal", climate="temperate")
    a = T.generate_world(dict(k), mode="climate")
    b = T.generate_world(dict(k, runoff_rivers=False), mode="climate")
    for name in ("isRiver", "aquatic_food", "wateracc", "precip_mm", "biome", "forage_kcal"):
        assert np.array_equal(np.asarray(getattr(a, name)), np.asarray(getattr(b, name))), \
            f"{name} changed with runoff_rivers=False -- the default path is not bit-exact"


def test_runoff_weighting_actually_changes_something_when_on():
    """POSITIVE CONTROL for the negative control above: a knob that is bit-exact in BOTH states is inert."""
    k = T.world_lottery_climate(0, terrain="coastal", climate="temperate")
    a = T.generate_world(dict(k), mode="climate")
    b = T.generate_world(dict(k, runoff_rivers=True), mode="climate")
    assert not np.array_equal(np.asarray(a.isRiver), np.asarray(b.isRiver)), \
        "runoff_rivers=True changed no river -- the knob is not wired"


# ─────────────────────────── feature abundance across ALL presets ─────────────────────────────────────

@pytest.mark.slow
def test_every_preset_holds_the_structural_invariants():
    """The full 25-preset sweep. CORE above is a sample; this is the population."""
    bad = []
    for terr in T.TERRAIN_PRESETS:
        for clim in T.CLIMATE_PRESETS:
            p = parts(world(terr, clim))
            w = f"{terr}-{clim}"
            if p["river"][p["water"]].any():
                bad.append(f"{w}: river on open water")
            if p["shore"][p["water"]].any():
                bad.append(f"{w}: shore on open water")
            if not np.isfinite(p["aq"]).all() or p["aq"].max() > 1.0 or p["aq"].min() < 0.0:
                bad.append(f"{w}: aquatic_food unbounded or non-finite")
    assert not bad, "structural violations: " + "; ".join(bad[:10])


@pytest.mark.slow
def test_every_preset_reproduces_its_forage_anchors():
    bad = []
    for terr in T.TERRAIN_PRESETS:
        for clim in T.CLIMATE_PRESETS:
            p = parts(world(terr, clim))
            for code, target in T.FORAGE_KCAL_TARGETS.items():
                m = p["land"] & (p["biome"] == code) & ~p["shore"]
                if m.sum() < 30:
                    continue
                ratio = float(p["forage"][m].mean()) / target
                if not (0.85 <= ratio <= 1.20):
                    bad.append(f"{terr}-{clim} {BIOME_NAME[code]} {ratio:.2f}x")
    assert not bad, "forage off its filed anchor: " + "; ".join(bad[:10])
