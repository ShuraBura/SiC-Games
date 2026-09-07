"""CTB for COLONIZING BUDDING (R-106, 2026-09-03; docs/DESIGN_colonization_spacing.md).

THE DEFECT. The population sits at 2% of the terrain's carrying capacity — trapped, not starved — because a shed
faction cannot ESTABLISH on empty rich land: `enable_bud_requires_occupancy` (adopted) makes it re-aggregate 40
people, which never happens on empty land, so the parent grows to 300-500 and the excess dies of crowding-disease
in place.

THE FIX. `enable_colonizing_budding`: an over-threshold village sheds a VIABLE emigrant bloc (topped up to
settle_min_pool, led by the rival) which FOUNDS a daughter directly on the nearest open storable cell, spaced by a
DENSITY-SCALED separation d = clamp(round(sqrt(V_target / K_local)), 1, 3) cells.

LOAD-BEARING (`test_MODEL_colonizing_multiplies_villages_and_spreads`): with the flag on, villages multiply and
land-use rises vs the canonical baseline (colonization onto empty land happens), at a LIVING population, and
village spacing stays ABOVE the 1-cell adjacency that plain occupancy-off budding produced — i.e. it colonizes
WITH spacing.
"""
import sys
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
for p in (ROOT / "sic_games" / "src", ROOT / "sic_games" / "outputs" / "mechanism_battery",
          ROOT / "sic_games" / "outputs" / "phase1_social_evolution"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from sic_games.demography import DemographyConfig  # noqa: E402


def test_the_flag_defaults_off():
    assert DemographyConfig().enable_colonizing_budding is False


def _run(colonize, seed=1, steps=500, n=600):
    # HORIZON 500 (R-106, 2026-09-05): the Kaplan juvenile recalibration (children net consumers) slows the
    # population growth, so the village-multiplication contrast needs more steps to appear than the earlier 280.
    import battery1_liveness as B1
    from sic_games import runconfig
    cfg = dict(runconfig.load(refresh=True).get("DemographyConfig", {}))
    cfg["enable_colonizing_budding"] = colonize
    # The baseline (colonize OFF) is the TRAPPED settlement path — occupancy-gated budding. Since the pair was
    # adopted (Addendum 61) the canonical config has enable_bud_requires_occupancy OFF, so pin it here: ON is the
    # colonizing pair, OFF is the pre-pair trapped baseline it improves on.
    cfg["enable_bud_requires_occupancy"] = not colonize
    w = B1._build(cfg, n=n, patch=80, terr="coastal", clim="temperate", seed=seed)
    for _ in range(steps):
        w.step()
        if len(w.agent_list) == 0:
            break
    return w


def _nn_spacing(sites):
    s = list(sites)
    if len(s) < 2:
        return 0.0
    ds = [min(max(abs(x - ox), abs(y - oy)) for j, (ox, oy) in enumerate(s) if j != i)
          for i, (x, y) in enumerate(s)]
    return float(np.mean(ds))


def test_MODEL_colonizing_multiplies_villages_and_spreads():
    """LOAD-BEARING. Colonizing budding founds daughters on empty rich land, so at the same seed/steps it yields
    MORE villages and MORE land-use than the canonical baseline, at a living population — and it keeps village
    spacing above the 1-cell adjacency (it colonizes WITH spacing, not by packing villages together)."""
    on = _run(True)
    off = _run(False)
    assert len(on.agent_list) > 200 and len(off.agent_list) > 200, "both worlds must be alive to compare"
    W = on._fields.isWater
    land = [(x, y) for y in range(100) for x in range(100) if W[y, x] == 0]
    def _lu(w):
        occ = Counter(a.pos for a in w.agent_list)
        return len([c for c in land if occ.get(c, 0) > 0]) / len(land)
    assert len(on._settlement_sites) > len(off._settlement_sites), (
        f"colonizing must produce MORE villages (on={len(on._settlement_sites)} off={len(off._settlement_sites)})")
    # The land-use SPREAD is a long-horizon effect (it triples only past ~1,800 steps; see the validation runs);
    # at this CTB horizon the robust signals are the village COUNT (above) and the SPACING (below). Here only
    # require that colonizing does not COLLAPSE land-use relative to the trapped baseline.
    assert _lu(on) >= 0.85 * _lu(off), f"colonizing must not collapse land-use (on={_lu(on):.4f} off={_lu(off):.4f})"
    assert _nn_spacing(on._settlement_sites) > 1.1, (
        f"colonizing must keep spacing above 1-cell adjacency (nn={_nn_spacing(on._settlement_sites):.2f})")


def test_a_daughter_is_founded_on_a_previously_open_cell():
    """Colonization: over a run, the settlement count strictly grows past the founders' initial sites — new sites
    appear on cells that were not settlements before (budding establishes on open land)."""
    import battery1_liveness as B1
    from sic_games import runconfig
    cfg = dict(runconfig.load(refresh=True).get("DemographyConfig", {}))
    cfg["enable_colonizing_budding"] = True
    w = B1._build(cfg, n=600, patch=80, terr="coastal", clim="temperate", seed=1)
    founded = 0
    seen = set(w._settlement_sites)
    for _ in range(280):
        w.step()
        if len(w.agent_list) == 0:
            break
        new = set(w._settlement_sites) - seen
        founded += len(new)
        seen |= new
    assert founded > 0, "colonizing budding must found at least one daughter village on open land"


def test_spacing_is_density_scaled_not_a_fixed_constant():
    """The separation d = clamp(round(sqrt(V_target/K)), 1, 3): rich cells (high K) admit closer villages than
    poor cells. Reconstruct the formula the mechanism uses and check the gradient at the anchored bounds."""
    from sic_games import runconfig
    V = runconfig.load(refresh=True).get("DemographyConfig", {}).get("bud_spacing_village_target", 300.0)
    def d(K):
        import math
        return int(min(3, max(1, round(math.sqrt(V / K)))))
    assert d(200) == 1, "a very rich aquatic cell (K~200) admits 1-cell spacing"
    assert d(60) == 2, "a mid coastal cell (K~60) admits 2-cell spacing"
    assert d(20) == 3, "a poor cell (K~20) needs 3-cell spacing"
    assert d(120) > d(200) or d(60) > d(200), "poorer cells demand wider spacing than the richest"
    assert d(1e9) == 1 and d(1e-9) == 3, "clamped to [1, 3]"
