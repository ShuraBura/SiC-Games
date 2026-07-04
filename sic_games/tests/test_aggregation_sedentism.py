"""Aggregation-sedentism Layer 1 — the settlement LIFECYCLE (form → hold → dissolve).

Settlements are MULTI-BAND coalescences at a rich node ("the gathering that stops dispersing"). These pin the
proximity-based lifecycle logic in `_maintain_settlements` / `_nearest_settlement`: an active settlement persists
while ≥ settle_min_pool people are within settle_radius of its site (emergent membership, robust to band churn),
and dissolves (hysteresis) once the pool leaves.
"""
from types import SimpleNamespace

import numpy as np

from sic_games.phase1_model import TerrainWorld
from sic_games.demography import DemographyConfig


def _fake(sites, agent_positions, min_pool=40, rad=2, release=12):
    cfg = DemographyConfig(enable_aggregation_sedentism=True, settle_min_pool=min_pool,
                           settle_radius=rad, settle_release_steps=release)
    f = SimpleNamespace(_settlement_sites=dict(sites), _demog=cfg,
                        agent_list=[SimpleNamespace(pos=p) for p in agent_positions])
    f._torus_cheby = lambda ax, ay, bx, by: TerrainWorld._torus_cheby(f, ax, ay, bx, by)
    return f


def test_settlement_refreshes_while_pool_present():
    site = (50, 50)
    f = _fake({site: 5}, [(50, 50)] * 45)                 # 45 people on-site (≥ min_pool 40)
    TerrainWorld._maintain_settlements(f)
    assert f._settlement_sites.get(site) == 12            # timer refreshed to release_steps


def test_membership_counts_within_radius_not_just_on_cell():
    site = (50, 50)
    f = _fake({site: 5}, [(51, 52)] * 40)                 # all within Chebyshev radius 2
    TerrainWorld._maintain_settlements(f)
    assert f._settlement_sites.get(site) == 12


def test_settlement_dissolves_after_pool_leaves():
    site = (50, 50)
    f = _fake({site: 3}, [(0, 0)] * 45)                   # nobody near the site; timer starts at 3
    for _ in range(3):
        TerrainWorld._maintain_settlements(f)
    assert site not in f._settlement_sites               # decayed to 0 → dissolved


def test_settlement_survives_dip_within_hysteresis():
    site = (50, 50)
    f = _fake({site: 12}, [(0, 0)] * 45)                  # empty near site, full timer
    for _ in range(11):                                   # 11 < release_steps 12
        TerrainWorld._maintain_settlements(f)
    assert site in f._settlement_sites                    # still alive on the last hysteresis step


def test_nearest_settlement_radius_gate():
    f = _fake({(50, 50): 12}, [])
    assert TerrainWorld._nearest_settlement(f, (51, 49)) == (50, 50)   # within radius 2
    assert TerrainWorld._nearest_settlement(f, (54, 54)) is None       # outside radius 2


def test_nearest_settlement_picks_closest():
    f = _fake({(50, 50): 12, (56, 50): 12}, [], rad=3)
    assert TerrainWorld._nearest_settlement(f, (53, 50)) == (50, 50)   # d=3 vs d=3 → tie-break first; both in range
    assert TerrainWorld._nearest_settlement(f, (55, 50)) == (56, 50)   # d=1 to the second


def test_torus_wrap_distance():
    f = _fake({(1, 50): 12}, [], rad=3)
    assert TerrainWorld._nearest_settlement(f, (99, 50)) == (1, 50)    # wraps: |99-1|→2 across the seam


# --------------------------------------------------------------------------- Layer 2: residence pin + catchment tier-2

def _land():
    return SimpleNamespace(_fields=SimpleNamespace(isWater=np.zeros((100, 100))))


def test_toward_steps_one_cell_toward_site():
    f = _land()
    assert TerrainWorld._toward(f, (50, 50), (55, 50)) == (51, 50)     # +x toward site
    assert TerrainWorld._toward(f, (50, 50), (50, 50)) == (50, 50)     # already on site → stay
    assert TerrainWorld._toward(f, (50, 50), (50, 45)) == (50, 49)     # -y


def test_toward_larger_axis_first():
    f = _land()
    assert TerrainWorld._toward(f, (50, 50), (54, 52)) == (51, 50)     # dx=4 > dy=2 → step x


def test_toward_blocked_by_water_uses_other_axis():
    w = np.zeros((100, 100)); w[50, 51] = 1                            # cell (x=51,y=50) is water
    f = SimpleNamespace(_fields=SimpleNamespace(isWater=w))
    assert TerrainWorld._toward(f, (50, 50), (55, 52)) == (50, 51)     # x-step blocked → y-step


def test_catchment_yield_sums_spot_times_multiplier():
    aq = np.zeros((100, 100))
    for (x, y) in [(50, 50), (51, 50), (49, 50)]:
        aq[y, x] = 0.5                                                 # 3 cells × 0.5 = 1.5 within radius 1
    cfg = DemographyConfig(settle_catchment_radius=1, settle_tier2_yield=10.0)
    f = SimpleNamespace(_fields=SimpleNamespace(aquatic_food=aq), _demog=cfg)
    assert abs(TerrainWorld._settlement_catchment_yield(f, (50, 50)) - 15.0) < 1e-9   # 1.5 × 10


def test_catchment_yield_zero_without_spot_field():
    cfg = DemographyConfig()
    f = SimpleNamespace(_fields=SimpleNamespace(aquatic_food=None), _demog=cfg)
    assert TerrainWorld._settlement_catchment_yield(f, (50, 50)) == 0.0
