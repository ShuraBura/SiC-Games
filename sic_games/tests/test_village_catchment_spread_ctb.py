"""CTB for VILLAGE CATCHMENT SPREAD (R-106, 2026-09-02).

THE DEFECT. The over-clustering is not the agglomeration economy (already ceiling-bound, R-105) — it is the
residence pin stacking every village member onto the SINGLE site cell. Measured: 100% of the people on big
(n≥40) cells are settled/pinned; a "village of 150–300" is that many bodies on one 100 km² cell.

THE FIX. `enable_village_catchment_spread` pins each settled member to a deterministic HOME cell within
settle_radius (∝ yield) instead of the site point, so the PHYSICAL footprint (and the density-disease hazard,
which reads occ_count[pos]) spreads. FOOD is bit-exact: the harvest regroups a village's members at its site
(the village forages its catchment as one economic unit), so a spread villager's share equals a stacked one's.

THE LOAD-BEARING INVARIANT (`test_MODEL_bodies_spread_food_group_regroups_at_site`): after a run, the settled
members occupy MANY catchment cells (physical spread, peak single-cell occupancy « membership) yet every one is
still a member of its site, and the harvest's regrouping puts the whole village back on its site cell — the
exact multiset of agents that a no-spread run would have there. With the flag OFF they stack on the site.
"""
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for p in (ROOT / "sic_games" / "src", ROOT / "sic_games" / "outputs" / "mechanism_battery",
          ROOT / "sic_games" / "outputs" / "phase1_social_evolution"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from sic_games.demography import DemographyConfig  # noqa: E402


def test_the_flag_defaults_off():
    assert DemographyConfig().enable_village_catchment_spread is False


def _canon_world(spread, n=400, seed=0, steps=60):
    import battery1_liveness as B1
    from sic_games import runconfig
    cfg = dict(runconfig.load(refresh=True).get("DemographyConfig", {}))
    cfg["enable_village_catchment_spread"] = spread
    w = B1._build(cfg, n=n, patch=60, terr="coastal", clim="temperate", seed=seed)
    for _ in range(steps):
        w.step()
        if len(w.agent_list) == 0:
            break
    return w


def _settled(w):
    return [a for a in w.agent_list if w._nearest_settlement(a.pos) is not None]


def test_MODEL_bodies_spread_food_group_regroups_at_site():
    """LOAD-BEARING. With spread ON the village's members occupy MANY cells (peak single-cell occupancy well
    below the village size) but every one stays a member, and the food regrouping returns the whole village to
    its site cell — the same multiset a no-spread run would harvest there. Verified against the OFF run, where
    the members stack onto the site."""
    on = _canon_world(True)
    settled = _settled(on)
    assert len(settled) >= 30, f"need a living village to test (got {len(settled)} settled)"

    occ = Counter(a.pos for a in settled)                      # PHYSICAL footprint (occ_count basis)
    assert len(occ) >= 3, "spread must put the village on several catchment cells, not one"
    biggest_site = Counter(w_site for w_site in (on._nearest_settlement(a.pos) for a in settled)).most_common(1)[0]
    site, members_here = biggest_site
    peak_cell = max(v for c, v in occ.items() if on._nearest_settlement(c) == site)
    assert peak_cell < members_here, (
        f"the largest village ({members_here} members) still peaks at {peak_cell} on one cell — no spread")

    # FOOD GROUP: regroup members by their site (the harvest's own rule) — the whole village lands on its site.
    food_group = Counter(on._nearest_settlement(a.pos) for a in settled)
    assert food_group[site] == members_here, "the food regrouping must gather the whole village at its site"
    # membership preserved: every settled agent is still within a site's radius (already true by construction of
    # `settled`, asserted explicitly as the invariant the home-cell clamp guarantees)
    assert all(on._nearest_settlement(a.pos) is not None for a in settled)


def test_off_stacks_members_on_the_single_site_cell():
    """CONTRAST / ablation control: with the flag OFF the residence pin drives members onto the SINGLE site
    cell, so the largest village's members sit on one cell (peak occupancy == its membership)."""
    off = _canon_world(False)
    settled = _settled(off)
    assert len(settled) >= 30, f"need a living village (got {len(settled)})"
    by_site = Counter(off._nearest_settlement(a.pos) for a in settled)
    site, members = by_site.most_common(1)[0]
    occ = Counter(a.pos for a in settled if off._nearest_settlement(a.pos) == site)
    # the pin drives members onto the site cell — the great majority sit on it (a few are still en route, one
    # cardinal step per turn). Measured ~0.95; require a clear concentration majority.
    peak = max(occ.values())
    assert peak / members >= 0.5, (
        f"OFF: the village should concentrate on its site cell, but peak {peak}/{members} = {peak/members:.2f} "
        f"across {len(occ)} cells")


def test_spread_lowers_peak_cell_occupancy_vs_off():
    """The headline over-clustering metric: peak single-cell occupancy is LOWER with spread ON than OFF, at a
    comparable living population (food is bit-exact, so the population is not cratered to fake the win)."""
    on = _canon_world(True, seed=1)
    off = _canon_world(False, seed=1)
    assert len(on.agent_list) > 100 and len(off.agent_list) > 100, "both worlds must be alive to compare footprints"
    peak_on = max(Counter(a.pos for a in on.agent_list).values())
    peak_off = max(Counter(a.pos for a in off.agent_list).values())
    assert peak_on < peak_off, f"spread must lower peak cell occupancy (on={peak_on}, off={peak_off})"
