"""CTB for the FOUNDING DELAY (R-106, 2026-09-01).

THE DEFECT it addresses. 78% of the villages alive at equilibrium were founded in the FIRST 200 steps — the
founders bunch and settle at t=0 and the settlement pattern then FREEZES, so the empty good land never gets a
village. Delaying founding a startup generation lets the founders SPREAD before "where to settle" is decided.

THE LOAD-BEARING TEST is `test_MODEL_no_settlement_before_the_delay`: with the flag on and delay=120, NO site
exists before step 120 and sites DO form after; verified to FAIL (sites appear early) when the flag is off.
"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
for p in (ROOT / "sic_games" / "src", ROOT / "sic_games" / "outputs" / "mechanism_battery"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from sic_games.demography import DemographyConfig  # noqa: E402


def test_the_flag_defaults_off_with_its_magnitude():
    c = DemographyConfig()
    assert c.enable_founding_delay is False
    assert c.settle_founding_delay_steps == 180


def _max_sites_before(w, delay, run_to):
    """Run `run_to` steps; return (max n_settlements seen at step_count < delay, n_settlements at the end)."""
    before, after = 0, 0
    for _ in range(run_to):
        w.step()
        if w.step_count < delay:
            before = max(before, len(w._settlement_sites))
        after = len(w._settlement_sites)
    return before, after


def _world(flag, delay=120):
    import battery1_liveness as B1
    from sic_games import runconfig
    cfg = dict(runconfig.load().get("DemographyConfig", {}))
    cfg["enable_founding_delay"] = flag
    cfg["settle_founding_delay_steps"] = delay
    return B1._build(cfg, n=1500, patch=30, terr="coastal", clim="temperate", seed=0)


def test_MODEL_no_settlement_before_the_delay():
    """LOAD-BEARING. With the flag ON, no site may exist before the delay step, and sites DO form after it.
    Verified to FAIL (sites appear during the delay window) when the flag is off."""
    off_before, off_after = _max_sites_before(_world(False), delay=120, run_to=220)
    on_before, on_after = _max_sites_before(_world(True), delay=120, run_to=220)
    assert off_before > 0, "sanity: without the delay, settlements form during the first 120 steps"
    assert on_before == 0, f"a settlement was founded during the delay window ({on_before} sites before step 120)"
    assert on_after > 0, "settlements must form AFTER the delay ends — the delay must not disable founding"


def test_MODEL_off_matches_zero_delay():
    """The flag OFF is exactly a zero delay: founding is never suppressed, so the two agree step-for-step on the
    settlement count trajectory (a proxy for bit-exactness of the founding path)."""
    from sic_games import runconfig
    import battery1_liveness as B1
    base = dict(runconfig.load().get("DemographyConfig", {}))
    a = B1._build({**base, "enable_founding_delay": False}, n=1500, patch=30, terr="coastal", clim="temperate", seed=0)
    b = B1._build({**base, "enable_founding_delay": True, "settle_founding_delay_steps": 0},
                  n=1500, patch=30, terr="coastal", clim="temperate", seed=0)
    ta, tb = [], []
    for _ in range(60):
        a.step(); b.step(); ta.append(len(a._settlement_sites)); tb.append(len(b._settlement_sites))
    assert ta == tb, "flag on with delay=0 diverged from flag off — the gate is not a clean no-op at zero delay"
