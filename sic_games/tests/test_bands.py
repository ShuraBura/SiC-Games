"""Emergent bands (E.1 safety + E.2 mating-access drives in the movement utility). Locks: (1) drives OFF ⇒ the
movement is unchanged (back-compat); (2) the grouping drives raise the emergent band size + the fraction of
agents living in bands (vs the anti-clustering IFD baseline)."""
from __future__ import annotations

from collections import Counter

import pytest

from sic_games.config import KcalEconomyConfig, SubstrateConfig
from sic_games.demography import DemographyConfig
from sic_games.phase1_model import TerrainWorld, seed_band_positions, _DEFAULT_KNOBS
from sic_games.terrain import generate_world


def _run(steps=400, seed=7, n=200, **grp):
    sc = SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion", contest_exponent=0.0,
                         move_cost_flat=0.0, **grp)
    w = TerrainWorld(n_agents=n, kcal_cfg=KcalEconomyConfig(), seed=seed, game_stream=False,
                     substrate_cfg=sc, demography_cfg=DemographyConfig())
    for _ in range(steps):
        w.step()
    return Counter(a.pos for a in w.agent_list)   # LIVE population (w.agents includes corpses pre-remove; see model)


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


# ── F.1 banded seeding + bonded mating ────────────────────────────────────────
def _seed(n=250, seed=7):
    fields = generate_world({**_DEFAULT_KNOBS, "seedStr": f"world{seed}"})
    return seed_band_positions(fields, n, band_size=25, territory_radius=3), fields


def test_band_seeder_biome_diverse_and_spaced():
    pos, fields = _seed()
    cells = Counter(pos)
    assert len(pos) == 250                                       # exactly n_agents placed
    assert all(20 <= s <= 30 for s in cells.values())           # ~band_size each
    biomes = {int(fields.biome[y, x]) for (x, y) in cells}
    assert len(biomes) >= 2                                      # MULTIPLE biomes (incl. marginal — desert dwellers)
    cl = list(cells)
    mind = min((max(abs(cl[i][0] - cl[j][0]), abs(cl[i][1] - cl[j][1]))
                for i in range(len(cl)) for j in range(i + 1, len(cl))), default=99)
    assert mind >= 3                                             # territory-spaced (non-adjacent)


@pytest.mark.xfail(strict=True, reason="KNOWN: on the BARE forage field (~1-8 persons/cell) seeded 25-agent "
                   "bands over-stack and wipe out in the ~1-step reserve buffer; the prior green was an artifact "
                   "of counting CORPSES in w.agents (now removed). The validated turnover fix is the CC-1 "
                   "NPP-capacity harvest_field (~30-50/cell) + bonded_mate_radius=1 (neighbourhood mate-gate) — "
                   "see scripts/calib_bands_cc1.py. This bare-forage harness awaits the banded-harness sign-off "
                   "before being re-pointed; until then it documents the collapse.")
def test_seeded_bands_persist_with_bonded_mating():
    # the fix: seeded bands + bonded mating ⇒ bands PERSIST (mates co-resident → reproduction sustains them),
    # vs the gas start that bootstrap-failed. Most agents stay in bands; the population doesn't crash.
    pos, _ = _seed()
    sc = SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion", contest_exponent=0.0,
                         move_cost_flat=0.0, group_safety_max=8.0, group_safety_scale=15.0,
                         group_mate_min=15.0, group_mate_floor=0.2)
    w = TerrainWorld(n_agents=250, kcal_cfg=KcalEconomyConfig(), seed=7, game_stream=False, substrate_cfg=sc,
                     demography_cfg=DemographyConfig(enable_bonded_mating=True), placement_positions=pos)
    for _ in range(400):
        w.step()
    occ = Counter(a.pos for a in w.agent_list)                   # LIVE population (not corpses)
    assert len(w.agent_list) > 125                               # population persists (no mate-starved crash)
    assert _frac_in_bands(occ, k=10) > 0.7                       # most agents still live in real bands


# ── F.2 neighbourhood mate-gate + founder mobile reserve ─────────────────────
class _UniformCapacity:
    """A flat, rich harvest field (every cell feeds `per_cell` agents) — isolates the demographic gate from
    terrain starvation in a unit test."""
    def __init__(self, per_cell):
        self.width = self.height = 100
        self._E = per_cell * (KcalEconomyConfig().burn_kcal_per_day * KcalEconomyConfig().days_per_month)
    def level(self, x, y): return self._E
    def harvest(self, x, y): return self._E


def _mate_gate_births(mate_r, female_pos, male_pos):
    # Movement frozen (huge move_cost) so the two agents stay put; rich field so neither starves. One fertile
    # female + one unrelated adult male; fecundability=1 ⇒ a birth fires iff the mate-gate passes.
    sc = SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion", contest_exponent=0.0,
                         move_cost_flat=1e12)
    w = TerrainWorld(n_agents=2, kcal_cfg=KcalEconomyConfig(), seed=5, game_stream=False, substrate_cfg=sc,
                     harvest_field=_UniformCapacity(2.0), placement_positions=[female_pos, male_pos],
                     demography_cfg=DemographyConfig(enable_bonded_mating=True, bonded_mate_radius=mate_r,
                                                     fecundability=1.0))
    f, m = w.agent_list
    f.sex, f.age, f.months_since_birth = "female", 300, 999      # fertile (in window, past refractory)
    m.sex, m.age, m.months_since_birth = "male", 300, 999        # unrelated adult male (_mother is None)
    return sum((w.step() or w.births_this_step) for _ in range(3))


def test_neighbourhood_mate_gate():
    # adjacent unrelated male: the per-CELL gate (r=0) finds no mate ⇒ no birth; the neighbourhood gate (r=1,
    # the band territory) finds him ⇒ a birth. Same cell: both gates allow it (r=0 back-compat).
    assert _mate_gate_births(0, (10, 10), (11, 10)) == 0
    assert _mate_gate_births(1, (10, 10), (11, 10)) > 0
    assert _mate_gate_births(0, (10, 10), (10, 10)) > 0


def test_founder_buffer_extends_survival():
    # On a zero-intake field a founder dies once its ~1-step reserve buffer is gone; a carried mobile reserve
    # (founder_buffer_steps) keeps it alive proportionally longer (the founding-transient bridge).
    class _ZeroField:
        width = height = 100
        def level(self, x, y): return 0.0
        def harvest(self, x, y): return 0.0

    def survival(buf):
        sc = SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion", contest_exponent=0.0,
                             move_cost_flat=1e12)
        w = TerrainWorld(n_agents=1, kcal_cfg=KcalEconomyConfig(), seed=1, game_stream=False, substrate_cfg=sc,
                         harvest_field=_ZeroField(), placement_positions=[(40, 40)],
                         demography_cfg=DemographyConfig(), founder_buffer_steps=buf)
        for s in range(1, 40):
            w.step()
            if not w.agent_list:
                return s
        return 40

    assert survival(6) >= survival(0) + 4                        # carried reserve bridges several extra steps


def test_homogenize_flattens_status_within_band():
    # Band-as-unit lump (E.3-proper): with homogenize_cred + homogenize_prowess and a band radius, every agent in
    # a spatially-connected band ends the step with the band-mean cred AND prowess (no within-band heterogeneity).
    sc = SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion", contest_exponent=0.0,
                         move_cost_flat=1e12)                     # freeze movement → the band stays connected
    w = TerrainWorld(n_agents=3, kcal_cfg=KcalEconomyConfig(), seed=2, game_stream=False, substrate_cfg=sc,
                     harvest_field=_UniformCapacity(3.0), placement_positions=[(20, 20), (21, 20), (40, 40)],
                     demography_cfg=DemographyConfig(bonded_mate_radius=1, homogenize_cred=True,
                                                     homogenize_prowess=True))
    a, b, c = w.agent_list                                        # a,b adjacent (one band); c isolated
    a.cred, b.cred, c.cred = 0.5, 1.5, 4.0
    a.prowess, b.prowess, c.prowess = 0.4, 1.6, 9.0
    w.step()
    assert abs(a.cred - 1.0) < 1e-9 and abs(b.cred - 1.0) < 1e-9      # band mean cred
    assert abs(a.prowess - 1.0) < 1e-9 and abs(b.prowess - 1.0) < 1e-9  # band mean prowess
    assert abs(c.cred - 4.0) < 1e-9 and abs(c.prowess - 9.0) < 1e-9   # singleton untouched (no band to lump)


def test_bands_method_connected_components():
    # F.2 diagnostics: bands() partitions the live population into spatially-connected components (incl singletons)
    # at the configured mate radius. Movement frozen so the placement is the partition.
    sc = SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion", contest_exponent=0.0,
                         move_cost_flat=1e12)
    pos = [(10, 10), (11, 10), (50, 50), (50, 51), (80, 80)]      # two adjacent pairs + one singleton
    w = TerrainWorld(n_agents=5, kcal_cfg=KcalEconomyConfig(), seed=1, game_stream=False, substrate_cfg=sc,
                     harvest_field=_UniformCapacity(3.0), placement_positions=pos,
                     demography_cfg=DemographyConfig(bonded_mate_radius=1))
    w.step()
    assert sorted(len(b) for b in w.bands()) == [1, 2, 2]        # r=1: two adjacent pairs band up + one singleton
    assert sorted(len(b) for b in w.bands(radius=0)) == [1, 1, 1, 1, 1]  # r=0 (per-cell): the pairs are on separate cells


def test_band_risk_shelved_off_by_default():
    # F.2 risk-dilution mortality was shelved (death spiral, run_3i) — the flag must stay OFF by default.
    assert DemographyConfig().enable_band_risk is False
