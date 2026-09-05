"""CTB for ACUTE FAMINE DISPERSAL (R-106, 2026-09-01; Colson 1979 M2 anchor).

THE DEFECT. The residence pin holds a settled agent on its site cell, eating the crashing pooled share, while
food sits one stride away. Diagnosed on canonical: 98% of the hungriest decile are pinned settlers and 99%
would eat >1.3x better by stepping to an adjacent cell — a RETENTION failure, not a reach failure. The
emergent-abandonment valve releases the pin only on CHRONIC remembered hardship, too slow for the one-step
crash that kills (96% of starvation deaths are acute).

THE FIX. `enable_hunger_dispersal`: when a settled agent's reserve fill fraction drops below
`hunger_flee_reserve_frac`, it breaks the pin THIS step and its ordinary IFD drive takes the better cell.

THE LOAD-BEARING TEST is `test_MODEL_hungry_settlers_flee_the_pin`: a crowded settlement of STARVING agents is
stepped once; with the flag ON most leave the site cell, with it OFF they stay pinned. The
`test_MODEL_well_fed_settlers_stay` control is the required negative: a full reserve must NOT release the pin.
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
    c = DemographyConfig()
    assert c.enable_hunger_dispersal is False
    assert c.hunger_flee_reserve_frac == pytest.approx(0.35)


def _world(flag):
    import battery1_liveness as B1
    from sic_games import runconfig
    cfg = dict(runconfig.load().get("DemographyConfig", {}))
    cfg["enable_hunger_dispersal"] = flag
    # ISOLATE the hunger valve: switch off the OTHER pin-release valves (scalar-stress repulsion disperses a
    # crowd regardless of hunger; abandonment is chronic), so only `enable_hunger_dispersal` can break the pin.
    cfg["enable_settlement_scalar_stress"] = False
    cfg["enable_emergent_abandonment"] = False
    return B1._build(cfg, n=300, patch=30, terr="coastal", clim="temperate", seed=0)


def _crowd_one_site(w, frac):
    """Put a settlement at the richest cell, crowd every agent onto it at reserve fill `frac`, and return the
    site. `_nearest_settlement` then pins them there, so the move step must decide stay-or-flee."""
    import numpy as np
    Y = np.array([[w._harvest_field.level(x, y) for x in range(w._fields.isWater.shape[0])]
                  for y in range(w._fields.isWater.shape[0])])
    sy, sx = np.unravel_index(int(np.argmax(Y)), Y.shape)
    site = (int(sx), int(sy))
    w._settlement_sites[site] = getattr(w._demog, "settle_release_steps", 12)
    w._nearest_map = None
    for a in w.agent_list:
        a.pos = site
        flr = a.reserve_floor * a.reserve_scale()
        cap = w._reserve_full * a.reserve_scale()
        a.wealth = flr + frac * (cap - flr)
    return site


def _frac_on_site_after_step(flag, frac):
    w = _world(flag)
    site = _crowd_one_site(w, frac)
    w._do_move() if hasattr(w, "_do_move") else w.step()
    on_site = sum(1 for a in w.agent_list if a.pos == site)
    return on_site / max(1, len(w.agent_list))


def test_MODEL_hungry_settlers_flee_the_pin():
    """LOAD-BEARING. A crowded settlement of STARVING agents (reserve frac 0.15, below the 0.35 flee floor):
    with the flag ON the pin releases and most leave the site cell; with it OFF they stay pinned. Verified to
    FAIL (they stay) when the flag is off."""
    off = _frac_on_site_after_step(False, frac=0.15)
    on = _frac_on_site_after_step(True, frac=0.15)
    assert off > 0.6, f"sanity: with no hunger release, starving settlers stay pinned to the site (got {off:.2f})"
    assert on < off - 0.2, (
        f"the hunger release did not disperse the starving settlers (on-site on={on:.2f} off={off:.2f}) -- "
        "the pin is not being broken on the move path")


def test_MODEL_well_fed_settlers_stay():
    """THE NEGATIVE CONTROL. A FULL reserve (frac 0.95) must NOT release the pin: well-fed settlers stay put
    whether the flag is on or off. If this fails, the mechanism is emptying healthy villages."""
    off = _frac_on_site_after_step(False, frac=0.95)
    on = _frac_on_site_after_step(True, frac=0.95)
    assert on == pytest.approx(off, abs=0.1), (
        f"the hunger release fired on WELL-FED settlers (on={on:.2f} off={off:.2f}) -- it must gate on hunger")
