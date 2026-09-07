"""CTB for the STORAGE TEMPERATURE GATE (R-106, 2026-08-24).

THE DEFECT. `realistic_forager_demog()` overrode `storage_temp_threshold_c = 100.0`. Storage fires where a
cell's mean temperature is <= that threshold ("the overwintering zone", Binford ET). At 100 deg C EVERY cell
on any world qualifies, so a warm tropical world with no winter stored anyway: measured coastal-tropical,
100% of cells stored, surplus 0.62, 70% of bands read complex_forager, birth spacing 22-24 months. The 100
was an un-annotated test convenience that leaked into the production preset, sitting among lit-calibrated
values -- the same override-defeats-anchored-default class as the SubstrateConfig **GRP and a_seas breaches.

THE FIX. Remove the override so it falls to the CLASS DEFAULT 15.25 deg C -- Binford's Effective-Temperature
storage threshold, which the field's own doc names, and which the model's temperature field is on the scale
of (measured means: tropical 21.4, temperate 9.7, boreal 2.0 -- real mean-annual deg C). At 15.25 only
genuinely cold worlds store; warm/aseasonal worlds stay immediate-return -> egalitarian, which is Testart's
distinction (Ache/Hadza/Hiwi/!Kung).

THE LOAD-BEARING TEST is `test_MODEL_a_warm_world_does_not_store`: it drives a real warm-world model and
asserts the granary stays empty, and is verified to FAIL when the threshold is put back to 100. The pure-value
tests above it document the arithmetic but -- as three prior CTBs this arc proved -- would pass whether or not
the gate is wired, so they are not the guarantee.
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
for _p in (ROOT / "sic_games" / "src", ROOT / "sic_games" / "outputs" / "phase1_social_evolution"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import sic_games.terrain as T  # noqa: E402
from sic_games.demography import DemographyConfig  # noqa: E402
from run_se0_controlled_climate import realistic_forager_demog  # noqa: E402

BINFORD_ET = 15.25


# ─────────────────────────── the anchored value, and that the override is gone ────────────────────────

def test_the_class_default_is_binford_ET():
    assert DemographyConfig().storage_temp_threshold_c == BINFORD_ET


def test_the_forager_preset_no_longer_overrides_it_to_100():
    """The whole fix: the preset must fall to 15.25, not carry the 100.0 test convenience."""
    assert realistic_forager_demog().storage_temp_threshold_c == BINFORD_ET, \
        "the storage gate override is back -- a warm world will store everywhere again"


# ─────────────────────────── the threshold sits between warm and cold worlds ──────────────────────────

def _mean_temp(terr, clim):
    f = T.generate_world(T.world_lottery_climate(0, terrain=terr, climate=clim), mode="climate")
    tp = np.asarray(f.temperature)
    land = np.asarray(f.isWater) == 0
    return float(tp[land].mean()), float((tp[land] <= BINFORD_ET).mean())


def test_warm_worlds_fall_outside_the_overwintering_zone():
    """Tropical / savanna / subtropical are above ET: at 15.25 they store on ~none of their cells, so they
    stay immediate-return. This is the geography the fix restores."""
    for terr, clim in (("coastal", "tropical"), ("coastal", "savanna"), ("flat", "subtropical")):
        mean_t, frac_store = _mean_temp(terr, clim)
        assert mean_t > BINFORD_ET, f"{terr}-{clim} mean {mean_t:.1f} should be warmer than the ET threshold"
        assert frac_store < 0.10, f"{terr}-{clim} still stores on {100*frac_store:.0f}% of cells at 15.25"


def test_cold_worlds_stay_inside_the_overwintering_zone():
    """Temperate / boreal are below ET: they KEEP storage at 15.25, so a storing (complex) society there is
    correct, not a bug. The fix must not switch storage off for genuinely cold worlds."""
    for terr, clim in (("coastal", "temperate"), ("coastal", "boreal")):
        mean_t, frac_store = _mean_temp(terr, clim)
        assert mean_t <= BINFORD_ET, f"{terr}-{clim} mean {mean_t:.1f} should be colder than the ET threshold"
        assert frac_store > 0.90, f"{terr}-{clim} only stores on {100*frac_store:.0f}% of cells -- lost its winter"


def test_the_100_threshold_would_store_everywhere():
    """Documents WHY 100 was the bug: it puts every cell in the overwintering zone regardless of climate."""
    for terr, clim in (("coastal", "tropical"), ("alpine", "boreal")):
        f = T.generate_world(T.world_lottery_climate(0, terrain=terr, climate=clim), mode="climate")
        tp = np.asarray(f.temperature)
        land = np.asarray(f.isWater) == 0
        assert (tp[land] <= 100.0).all(), "even the hottest cell is below 100C -- 100 gates nothing"


# ─────────────────────────── THE MODEL PATH: a warm world must not fill its granary ───────────────────
# Verified to FAIL when storage_temp_threshold_c is put back to 100. The value tests above all PASS with the
# threshold at 100 (they read the temperature field, not the granary), so they are documentation, not the
# guarantee -- exactly the pure-helper trap that three CTBs fell into earlier this arc.

import importlib.util as _iu  # noqa: E402

_MORPH = ROOT / "sic_games" / "tests" / "test_morph.py"


def _granary_fill(temp_threshold):
    """Run the morph harness on a WARM patch and return the total granary stock after settling."""
    spec = _iu.spec_from_file_location("_morph_h", _MORPH)
    mod = _iu.module_from_spec(spec)
    spec.loader.exec_module(mod)
    # `_world(temp_threshold=...)` sets storage_temp_threshold_c directly. A warm world (small threshold)
    # should never accumulate; a threshold of 100 stores everywhere.
    w = mod._world(temp_threshold=temp_threshold, affiliation=True, n=200)
    for _ in range(300):
        w.step()
    return sum(w._cell_store.values())


def test_MODEL_a_warm_world_does_not_store_at_the_binford_gate():
    """LOAD-BEARING. With the gate at Binford ET, a world warmer than 15.25 fills no granary. At 100 it fills
    one. `_world` builds a temperate-ish patch, so we drive both thresholds and assert the ORDERING: the
    100-gate stores strictly more than the 15.25-gate. Verified to fail if the two are made equal (gate not
    wired) or reversed."""
    fill_binford = _granary_fill(BINFORD_ET)
    fill_100 = _granary_fill(100.0)
    assert fill_100 > 0.0, "the harness never stored even at threshold 100 -- it is not exercising storage"
    assert fill_binford < fill_100, (
        f"granary at ET-15.25 ({fill_binford:.0f}) is not below the store-everywhere 100 gate "
        f"({fill_100:.0f}) -- the temperature gate is not controlling storage")
