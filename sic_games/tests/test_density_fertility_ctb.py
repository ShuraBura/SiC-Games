"""CTB for DENSITY-DEPENDENT FERTILITY (R-106, 2026-09-05).

THE DEFECT. The intake-fertility brake reads the intake EMA, which RE-SATURATES (median 2.3x requirement even in
a population dying 51% of starvation), so it barely bites and STARVATION does the population regulating — which
holds e0 low (Addendum 64).

THE FIX. `enable_density_fertility`: birth probability is scaled by f = clamp(1 - fill^exponent, 0, 1), fill =
village population / village carrying capacity (Σ K_persons over the territory); a mobile mother uses her cell.
Fill does not re-saturate, so births fall as a village approaches carrying capacity — regulation deaths→births.

LOAD-BEARING is `test_MODEL_dense_village_suppresses_fertility`: with the density brake isolated, a village packed
toward its carrying capacity has a far lower realised fertility factor than a sparse one; with the flag off, the
two match.
"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
for p in (ROOT / "sic_games" / "src", ROOT / "sic_games" / "outputs" / "mechanism_battery",
          ROOT / "sic_games" / "outputs" / "phase1_social_evolution"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from sic_games.demography import DemographyConfig  # noqa: E402


def test_the_flag_defaults_off():
    assert DemographyConfig().enable_density_fertility is False


def _run(density_fert, founders, patch, steps=150):
    import battery1_liveness as B1
    from sic_games import runconfig
    cfg = dict(runconfig.load(refresh=True).get("DemographyConfig", {}))
    # isolate the density brake: turn OFF the intake-EMA fertility so the fertility factor reflects density only
    cfg.update(enable_density_fertility=density_fert, enable_intake_fertility=False,
               enable_energetic_fertility=False, enable_energetic_refractory=False)
    w = B1._build(cfg, n=founders, patch=patch, terr="coastal", clim="temperate", seed=1)
    for _ in range(steps):
        w.step()
        if not w.agent_list:
            break
    ff = (w.fert_factor_sum / w.fert_factor_n) if w.fert_factor_n else float("nan")
    return ff


def test_MODEL_dense_village_suppresses_fertility():
    """LOAD-BEARING. With the density brake ON, a DENSE world (packed toward carrying capacity) has a lower
    realised fertility factor than a SPARSE one. With the brake OFF, the two are both ~1 (no density response)."""
    dense_on = _run(True, founders=800, patch=40)     # many people, poor patch -> high fill
    sparse_on = _run(True, founders=120, patch=80)    # few people, rich patch -> low fill
    assert dense_on < sparse_on - 0.05, (
        f"density brake ON must suppress fertility more in the dense world (dense={dense_on:.3f} sparse={sparse_on:.3f})")

    dense_off = _run(False, founders=800, patch=40)
    sparse_off = _run(False, founders=120, patch=80)
    assert dense_off == pytest.approx(1.0, abs=0.02) and sparse_off == pytest.approx(1.0, abs=0.02), (
        f"with the brake OFF (and intake-fertility off) the fertility factor is ~1 everywhere "
        f"(dense={dense_off:.3f} sparse={sparse_off:.3f})")


def test_the_fill_fraction_is_computed_and_bounded():
    """The village fill fraction (population / carrying capacity) is recorded and lies in a sane range."""
    import battery1_liveness as B1
    from sic_games import runconfig
    cfg = dict(runconfig.load(refresh=True).get("DemographyConfig", {}))
    cfg["enable_density_fertility"] = True
    w = B1._build(cfg, n=500, patch=60, terr="coastal", clim="temperate", seed=1)
    for _ in range(200):
        w.step()
        if not w.agent_list:
            break
    fills = getattr(w, "_dens_fert_fill_village", {})
    assert fills, "the per-village fill fraction must be computed when the brake is on"
    assert all(f >= 0.0 for f in fills.values()), "fill fractions must be non-negative"
