"""Emergent bands (E.1 safety + E.2 mating-access drives in the movement utility). Locks: (1) drives OFF ⇒ the
movement is unchanged (back-compat); (2) the grouping drives raise the emergent band size + the fraction of
agents living in bands (vs the anti-clustering IFD baseline)."""
from __future__ import annotations

from collections import Counter

from sic_games.config import KcalEconomyConfig, SubstrateConfig
from sic_games.demography import DemographyConfig
from sic_games.phase1_model import TerrainWorld


def _run(steps=400, seed=7, n=200, **grp):
    sc = SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion", contest_exponent=0.0,
                         move_cost_flat=0.0, **grp)
    w = TerrainWorld(n_agents=n, kcal_cfg=KcalEconomyConfig(), seed=seed, game_stream=False,
                     substrate_cfg=sc, demography_cfg=DemographyConfig())
    for _ in range(steps):
        w.step()
    return Counter(a.pos for a in w.agents)


def _frac_in_bands(occ, k=5):
    pop = sum(occ.values())
    return sum(s for s in occ.values() if s >= k) / pop if pop else 0.0


def test_grouping_off_unchanged_positions():
    # explicit zeros == the defaults == not passing them: same final occupancy (the drive code path is skipped)
    a = _run(group_safety_max=0.0, group_mate_min=0.0)
    b = _run()
    assert a == b                                                # off ⇒ identical (back-compat)


def test_grouping_raises_band_size_and_membership():
    base = _run()
    grouped = _run(group_safety_max=8.0, group_safety_scale=15.0, group_mate_min=15.0, group_mate_floor=0.2)
    assert max(grouped.values()) > max(base.values())            # bands grow
    assert _frac_in_bands(grouped) > _frac_in_bands(base) + 0.1   # materially more agents live in bands
    assert max(grouped.values()) < sum(grouped.values())         # … but NOT one blob (bounded, multi-band)
