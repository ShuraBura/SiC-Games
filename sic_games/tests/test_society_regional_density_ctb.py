"""CTB for REGIONAL-DENSITY society classification (R-106, 2026-08-24).

THE DEFECT -- a units error. The morph classifier `society_from_character` asks "is this band packed past
Binford's threshold?" and Binford's 0.091 persons/km2 is a REGIONAL figure: persons per 100 km2 of RANGE. The
band path fed it `members / occupied-cells` -- a LOCAL density. Because the model crowds everyone onto ~14% of
the land (the packing paradox), a typical band sits on 1.9 cells, so:

    members / occupied cells = 31 / 190 km2 = 0.167/km2 = 1.8x packing  -> STRATIFIED
    members / range share    = 31 / 1234 km2 = 0.025/km2 = 0.28x packing -> egalitarian

The first labelled 57% of a PURE FORAGER world stratified; `SEDENTISM_IBI_MONTHS` then gave those bands a
14-month lactational refractory, the population-weighted base fell to 18 months, and TFR ran ~10 against a
5-8 anchor. Feeding a threshold defined regionally with a local density is the whole bug.

THE FIX introduces NO new number: the classifier density becomes `members / (habitable_km2 / n_bands)` -- the
band's fair share of the range, which equals the true regional density and is the scale Binford's 0.091 means.
The DISEASE hazard keeps LOCAL per-cell density, correctly, because contagion is a local quantity.
"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "sic_games" / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "sic_games" / "src"))

from sic_games.demography import (BINFORD_PACKING_PER_KM2, DemographyConfig,  # noqa: E402
                                  society_from_character)

PACK = BINFORD_PACKING_PER_KM2   # 0.091 /km2


# ─────────────────────────── the flag and the classifier arithmetic ───────────────────────────────────

def test_the_flag_exists_and_defaults_off():
    c = DemographyConfig()
    assert c.enable_society_regional_density is False
    assert "enable_society_regional_density" in DemographyConfig.model_fields


def test_local_density_labels_a_forager_band_a_chiefdom():
    """DOCUMENTS THE DEFECT. 31 members on 1.9 occupied cells is a LOCAL density of 0.167/km2, which the
    classifier reads as packed and (with high surplus) stratified. That is the miscall the fix removes."""
    local = 31.0 / (1.9 * 100.0)
    assert local / PACK > 1.5, "the crowded local density must read as packed"
    assert society_from_character(local, surplus_frac=0.7) == "stratified_chiefdom"


def test_regional_density_labels_the_same_band_a_forager():
    """THE FIX. The same 31 members over their share of a 158,400 km2 range (128 bands) is 0.025/km2 --
    3.6x BELOW packing -- and no longer eligible for the stratified verdict."""
    regional = 31.0 / (158_400.0 / 128.0)
    assert regional / PACK < 0.5, "the true regional density must read as far below packing"
    assert society_from_character(regional, surplus_frac=0.7) != "stratified_chiefdom"


def test_the_two_densities_differ_by_the_crowding_factor():
    """The whole error is one density divided by the crowding fraction. Occupied land is ~14% of habitable,
    so the local density is ~7x the regional one -- exactly the factor that turns 0.28x packing into 1.8x."""
    occupied_frac = 190.0 / 1234.0            # occupied km2 per band / range km2 per band
    local = 31.0 / 190.0
    regional = 31.0 / 1234.0
    assert local / regional == pytest.approx(1.0 / occupied_frac, rel=1e-9)
    assert 5.0 < local / regional < 8.0


# ─────────────────────────── the classifier boundary is on the regional scale ─────────────────────────

def test_the_stratified_threshold_sits_at_binford_packing_regionally():
    """A band AT regional packing with high surplus is the boundary case; below it, egalitarian/complex."""
    assert society_from_character(PACK * 1.01, 0.7) == "stratified_chiefdom"
    assert society_from_character(PACK * 0.99, 0.7) != "stratified_chiefdom"
    # a forager world sits at ~0.28x packing regionally -> nowhere near the boundary
    assert society_from_character(PACK * 0.28, 0.7) != "stratified_chiefdom"


def test_a_genuinely_packed_world_still_stratifies():
    """POSITIVE CONTROL: the fix must not make stratification UNREACHABLE. A population actually at or above
    Binford packing regionally -- the intensified case the ladder exists to detect -- must still stratify."""
    for mult in (1.0, 1.5, 3.0):
        assert society_from_character(PACK * mult, 0.7) == "stratified_chiefdom"


# ─────────────────────────── the two density consumers stay separate ──────────────────────────────────

def test_disease_density_is_LOCAL_and_must_not_change():
    """The disease hazard (density_disease, phase1_model line ~5258) reads per-cell occupancy / 100 km2,
    because contagion is a local quantity. This fix touches ONLY the society classifier. A regression here
    would mean the two density consumers got conflated again -- the very thing being separated.

    Asserted as a source-level guard: the disease site must still divide occupancy by the cell area, not by
    a regional range."""
    src = (ROOT / "sic_games" / "src" / "sic_games" / "phase1_model.py").read_text(encoding="utf-8")
    assert "occ_count.get(a.pos, 1) / _CELL_KM2" in src, \
        "the disease hazard no longer uses LOCAL per-cell density -- it must not be switched to regional"


# ─────────────────────────── THE MODEL PATH, by spying on the exact seam that changed ─────────────────
# The pure-function tests above ALL PASS whether or not the model wiring is connected -- they never run the
# model. Two attempts to write a behavioural model test failed the load-bearing check because the small morph
# harness never reaches the stratified surplus threshold, so "no band stratified" was trivially true in both
# states. Rather than fake it, this spies on the DENSITY the model actually passes to
# `society_from_character`, which is the one value the fix changes. Verified: it FAILS when the
# `if _range_km2 > 0.0` wiring is perturbed out (the two means collapse to equal).

import importlib.util as _iu  # noqa: E402

_MORPH = ROOT / "sic_games" / "tests" / "test_morph.py"


def _mean_density_passed(regional_flag):
    """Run the per-band morph path and capture the density the model hands the classifier."""
    spec = _iu.spec_from_file_location("_morph_harness", _MORPH)
    mod = _iu.module_from_spec(spec)
    spec.loader.exec_module(mod)
    import sic_games.phase1_model as pm
    seen = []
    real = pm.society_from_character

    def spy(density, surplus_frac, *a, **k):
        seen.append(density)
        return real(density, surplus_frac, *a, **k)

    pm.society_from_character = spy
    try:
        w = mod._world(temp_threshold=100.0, affiliation=True, n=300)
        w._demog.enable_society_regional_density = regional_flag
        w._habitable_cells = 6400          # a range far larger than the cells the bands crowd onto
        for _ in range(200):
            w.step()
    finally:
        pm.society_from_character = real
    pos = [d for d in seen if d > 0]
    assert pos, "the classifier was never called with a positive density -- harness not exercising the path"
    return sum(pos) / len(pos)


def test_MODEL_the_flag_lowers_the_density_handed_to_the_classifier():
    """THE LOAD-BEARING MODEL TEST. Off, the model passes members/occupied-cells (a LOCAL density); on, it
    passes members/range-share (the REGIONAL density), which is far smaller because the bands crowd onto a
    fraction of their range. Verified to FAIL when the wiring is perturbed out -- the whole point."""
    off = _mean_density_passed(regional_flag=False)
    on = _mean_density_passed(regional_flag=True)
    assert on < off / 3.0, (
        f"regional density {on:.4f} is not much below the local {off:.4f} -- the fix is not reaching the "
        f"model, or the two density bases were conflated")


def test_MODEL_the_regional_density_the_model_uses_is_below_packing():
    """The regional density the model actually passes must sit below Binford packing on a forager world, so
    the stratified verdict is not reachable by crowding alone."""
    on = _mean_density_passed(regional_flag=True)
    assert on < PACK, f"regional density {on:.4f} is not below packing {PACK} -- crowding still stratifies"
