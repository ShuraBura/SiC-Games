"""CTB for VILLAGE-SCALED DENSITY DISEASE (R-106, 2026-09-03; the keystone).

THE DEFECT. The density-disease hazard reads occ_count[cell] (single-cell occupancy) — so it is the only
Malthusian brake AND it is defeated by dispersal: spread the people, per-cell occupancy falls, the brake
releases, the population runs away (catchment-spread A.58, colonizing budding A.59).

THE FIX. `enable_village_density_disease`: a SETTLED agent's disease density is its VILLAGE population over the
village territory ((2·settle_radius+1)² cells) — spread-invariant. A mobile agent keeps the single-cell form.

LOAD-BEARING (`test_MODEL_disease_is_spread_invariant_when_on`): the same village population, packed onto one
cell vs spread across its territory, yields the SAME disease multiplier when the flag is ON — and a DIFFERENT
one (much higher packed) when the flag is OFF. That is exactly the property that lets dispersal happen without
releasing the brake.
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
    assert DemographyConfig().enable_village_density_disease is False


def _world(village_disease):
    import battery1_liveness as B1
    from sic_games import runconfig
    cfg = dict(runconfig.load(refresh=True).get("DemographyConfig", {}))
    # isolate the density-disease term: turn off the other a2 modulators so _a2_mult == the disease factor alone
    cfg.update(enable_density_disease=True, enable_density_reference=True,
               enable_village_density_disease=village_disease,
               enable_terrain_risk=False, enable_terrain_pathogen=False,
               enable_nutrition_synergy=False, enable_condition=False, enable_terrain_pathogen_climate=False)
    w = B1._build(cfg, n=50, patch=40, terr="coastal", clim="temperate", seed=0)
    return w


def _rich_site(w):
    import numpy as np
    hf = w._harvest_field
    Y = np.array([[hf.level(x, y) for x in range(100)] for y in range(100)])
    sy, sx = np.unravel_index(int(np.argmax(Y)), Y.shape)
    return int(sx), int(sy)


def _packed_and_spread_mult(w, N=600):
    """Compute the a2 disease multiplier for one member of a village of N people, arranged (a) all packed on the
    site cell and (b) spread evenly across the village territory. Returns (packed_mult, spread_mult)."""
    site = _rich_site(w)
    w._settlement_sites[site] = 12
    w._nearest_map = None
    a = w.agent_list[0]
    rad = w._demog.settle_radius
    Ngrid = w._fields.isWater.shape[0]

    # (a) packed: the member stands on the site, all N on the site cell
    a.pos = site
    w.step_count += 1                                   # invalidate the per-step village-pop cache
    packed = w._a2_mult(a, {site: N})

    # (b) spread: the member stands on a territory cell, N spread evenly across the (2·rad+1)² territory
    per = max(1, N // ((2 * rad + 1) ** 2))
    occ_spread = {((site[0] + dx) % Ngrid, (site[1] + dy) % Ngrid): per
                  for dx in range(-rad, rad + 1) for dy in range(-rad, rad + 1)}
    a.pos = ((site[0] + 1) % Ngrid, site[1])           # a dwelling cell inside the territory (still a member)
    w.step_count += 1
    spread = w._a2_mult(a, occ_spread)
    return packed, spread


def test_MODEL_disease_is_spread_invariant_when_on():
    """LOAD-BEARING. With the flag ON the disease multiplier is (near-)identical whether the village is packed on
    one cell or spread across its territory — the brake keys on village size, not dwelling packing."""
    w = _world(True)
    packed, spread = _packed_and_spread_mult(w)
    assert packed > 1.0, "a 200-person village must generate excess disease (sanity — the brake exists)"
    assert spread == pytest.approx(packed, rel=0.05), (
        f"village-scaled disease must be spread-invariant (packed={packed:.3f} spread={spread:.3f})")


def test_MODEL_single_cell_disease_is_defeated_by_spread_when_off():
    """CONTRAST. With the flag OFF (single-cell), spreading the SAME village collapses the disease multiplier —
    this is the defeatable brake the fix replaces."""
    w = _world(False)
    packed, spread = _packed_and_spread_mult(w)
    assert packed > 1.0, "packed village generates excess disease under the single-cell form too"
    assert spread < 0.5 * (packed - 1.0) + 1.0, (
        f"single-cell disease must fall sharply when the village spreads (packed={packed:.3f} spread={spread:.3f})")
