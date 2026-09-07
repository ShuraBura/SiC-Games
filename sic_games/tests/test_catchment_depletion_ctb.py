"""CTB for CATCHMENT-FORAGING DEPLETION (R-106, 2026-09-02).

THE DEFECT. `deplete_and_regrow` keys on `occ_count` (where agents STAND). A settled village forages its whole
catchment (tier-2, pooled) but stands on the site cell, so a foraged catchment cell that nobody stands on is
NEVER depleted — the village lives on an inexhaustible catchment, which is the engine of the over-clustering.

THE FIX. `enable_catchment_depletion` replaces the standing-occupancy pressure with a FORAGING map: each
settled villager's take is spread over its catchment ∝ each cell's yield; mobile agents forage where they
stand. So the catchment depletes in proportion to how hard it is foraged.

THE LOAD-BEARING TEST is `test_MODEL_a_foraged_but_unoccupied_catchment_cell_depletes`: a village stands on its
site cell; a neighbouring catchment cell nobody occupies is driven down under the foraging map but stays FULL
under the standing-occupancy map. Verified to fail (no depletion) without the foraging map.
"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
for p in (ROOT / "sic_games" / "src", ROOT / "sic_games" / "outputs" / "mechanism_battery"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from sic_games.demography import DemographyConfig  # noqa: E402


def test_the_flag_defaults_off():
    assert DemographyConfig().enable_catchment_depletion is False


def _world(flag):
    import battery1_liveness as B1
    from sic_games import runconfig
    cfg = dict(runconfig.load().get("DemographyConfig", {}))
    cfg["enable_catchment_depletion"] = flag
    return B1._build(cfg, n=200, patch=30, terr="coastal", clim="temperate", seed=0)


def _Bfield(w):
    hf = w._harvest_field
    return getattr(hf, "_B", None) if getattr(hf, "_B", None) is not None else hf._base._B


def _seat_a_village(w):
    """Put a settlement at a rich cell and stand EVERY agent on the site cell (catchment cells stay empty).
    Returns (site, an adjacent catchment cell that nobody occupies)."""
    import numpy as np
    hf = w._harvest_field
    Y = np.array([[hf.level(x, y) for x in range(w._fields.isWater.shape[0])]
                  for y in range(w._fields.isWater.shape[0])])
    sy, sx = np.unravel_index(int(np.argmax(Y)), Y.shape)
    site = (int(sx), int(sy))
    w._settlement_sites[site] = getattr(w._demog, "settle_release_steps", 12)
    w._nearest_map = None
    for a in w.agent_list:
        a.pos = site
    N = w._fields.isWater.shape[0]
    adj = ((site[0] + 1) % N, site[1])          # a catchment cell (radius>=1) nobody stands on
    return site, adj


def test_the_map_spreads_a_villager_over_the_catchment():
    """The pressure map: a settled villager's 1 unit is spread over the catchment (∝ yield), so the site cell
    holds only its share and the neighbouring catchment cells get a positive share."""
    w = _world(True)
    site, adj = _seat_a_village(w)
    press = w._catchment_foraging_pressure({site: len(w.agent_list)})
    assert press.get(adj, 0.0) > 0.0, "a catchment cell must receive foraging pressure even with nobody on it"
    assert press.get(site, 0.0) < len(w.agent_list), "the site must hold only its catchment SHARE, not all foragers"
    assert sum(press.values()) == pytest.approx(len(w.agent_list), rel=1e-6), "conservation: total foragers preserved"


def test_MODEL_a_foraged_but_unoccupied_catchment_cell_depletes():
    """LOAD-BEARING. A neighbouring catchment cell nobody stands on is driven DOWN under the foraging map
    (`enable_catchment_depletion`) and stays FULL under the plain standing-occupancy map."""
    # ON: deplete through the foraging pressure map
    w_on = _world(True)
    site, adj = _seat_a_village(w_on)
    occ = {site: len(w_on.agent_list)}
    B_on = _Bfield(w_on)
    for _ in range(20):
        w_on._harvest_field.deplete_and_regrow(w_on._catchment_foraging_pressure(occ), 1.0)
    # OFF baseline: deplete through the standing-occupancy map (the historical path)
    w_off = _world(False)
    site2, adj2 = _seat_a_village(w_off)
    occ2 = {site2: len(w_off.agent_list)}
    B_off = _Bfield(w_off)
    for _ in range(20):
        w_off._harvest_field.deplete_and_regrow(occ2, 1.0)
    assert B_off[adj2[1], adj2[0]] > 0.98, (
        "sanity: with standing-occupancy depletion, an EMPTY catchment cell is never depleted")
    assert B_on[adj[1], adj[0]] < 0.9, (
        f"the foraged catchment cell did not deplete (B={B_on[adj[1], adj[0]]:.2f}) -- the foraging map is not "
        "reaching deplete_and_regrow")


def test_a_bigger_village_hunts_its_catchment_harder():
    """Monotonicity: more foragers on the same catchment leave a lower stock (an 'exact map' of take→yield)."""
    w = _world(True)
    site, adj = _seat_a_village(w)
    def _depleted_B(nforagers):
        Binner = _Bfield(w); Binner[:] = 1.0          # reset the inner depletable stock to full
        occ = {site: nforagers}
        for _ in range(20):
            w._harvest_field.deplete_and_regrow(w._catchment_foraging_pressure(occ), 1.0)
        return float(Binner[adj[1], adj[0]])
    small = _depleted_B(40)
    big = _depleted_B(400)
    assert big < small, f"a bigger village must leave a lower catchment stock (big={big:.2f} small={small:.2f})"
