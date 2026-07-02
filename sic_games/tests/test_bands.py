"""Emergent bands (E.1 safety + E.2 mating-access drives in the movement utility). Locks: (1) drives OFF ⇒ the
movement is unchanged (back-compat); (2) the grouping drives raise the emergent band size + the fraction of
agents living in bands (vs the anti-clustering IFD baseline)."""
from __future__ import annotations

from collections import Counter

import pytest

from sic_games.config import KcalEconomyConfig, SubstrateConfig
from sic_games.demography import DemographyConfig, LEADER_SOCIETY_WEIGHT, REPULSION_SOCIETY_FACTOR, size_repulsion
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


def test_pair_bonds_form_and_are_monogamous():
    # F.3a: an unpaired adult female + adult male co-resident in a band form a mutual, monogamous durable bond.
    sc = SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion", contest_exponent=0.0,
                         move_cost_flat=1e12)
    w = TerrainWorld(n_agents=2, kcal_cfg=KcalEconomyConfig(), seed=3, game_stream=False, substrate_cfg=sc,
                     harvest_field=_UniformCapacity(3.0), placement_positions=[(10, 10), (11, 10)],
                     demography_cfg=DemographyConfig(enable_pair_bonds=True, enable_paternity=True,
                                                     bonded_mate_radius=1, mate_choice_strength=0.0))
    f, mn = w.agent_list
    f.sex, f.age = "female", 300
    mn.sex, mn.age = "male", 300
    w.step()
    assert f._partner is mn and mn._wives == {f}                 # durable bond: wife→husband + husband's wives set
    assert mn._partner is None                                   # males track wives via _wives, not _partner


def test_nuclear_family_co_moves():
    # F.3b: a dependent child and the bonded father co-locate to the mother each step (the family moves as a unit).
    sc = SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion", contest_exponent=0.0,
                         move_cost_flat=1e12)                     # mother (root) frozen at her cell
    w = TerrainWorld(n_agents=3, kcal_cfg=KcalEconomyConfig(), seed=4, game_stream=False, substrate_cfg=sc,
                     harvest_field=_UniformCapacity(3.0), placement_positions=[(10, 10), (50, 50), (60, 60)],
                     demography_cfg=DemographyConfig(enable_pair_bonds=True, enable_paternity=True,
                                                     bonded_mate_radius=1, family_maturity_months=180))
    mother, father, child = w.agent_list
    mother.sex, mother.age = "female", 300
    father.sex, father.age = "male", 300
    child.age = 0                                                 # dependent (< maturity)
    mother._partner = father; father._wives.add(mother)          # pre-bonded couple (wife→husband + husband's wives)
    child._mother = mother                                        # mother's dependent
    w.step()
    assert father.pos == mother.pos                              # bonded father co-moves to the mother
    assert child.pos == mother.pos                              # dependent child co-moves to the mother


def test_pair_bonds_off_by_default():
    assert DemographyConfig().enable_pair_bonds is False and DemographyConfig().divorce_rate == 0.0


def test_modest_polygyny_high_status_male_takes_multiple_wives():
    # F.3a polygyny: with polygyny_rate>0 + max_wives>1, an already-married male can take additional wives.
    sc = SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion", contest_exponent=0.0, move_cost_flat=1e12)
    w = TerrainWorld(n_agents=3, kcal_cfg=KcalEconomyConfig(), seed=5, game_stream=False, substrate_cfg=sc,
                     harvest_field=_UniformCapacity(3.0), placement_positions=[(10, 10), (10, 10), (11, 10)],
                     demography_cfg=DemographyConfig(enable_pair_bonds=True, bonded_mate_radius=1,
                                                     mate_choice_strength=0.0, polygyny_rate=1.0, max_wives=2))
    f1, f2, mn = w.agent_list
    f1.sex, f1.age = "female", 300
    f2.sex, f2.age = "female", 300
    mn.sex, mn.age = "male", 300
    w.step()
    assert len(mn._wives) == 2 and f1._partner is mn and f2._partner is mn   # one husband, two wives


def test_polygyny_off_by_default():
    assert DemographyConfig().polygyny_rate == 0.0 and DemographyConfig().max_wives == 1


def test_group_vector_inherit():
    # F.3c collective-identity vector: a child copies the mother's vector (all cells), distinct object.
    from sic_games.group import GroupVector
    g = GroupVector(band_id=7, assabiyah=0.5, religion=2)
    c = g.inherit()
    assert (c.band_id, c.assabiyah, c.religion) == (7, 0.5, 2) and c is not g


def test_band_affiliation_seeds_founder_bands():
    # F.3c-1: founder band_ids are seeded by the initial spatial clusters (two territory-spaced clusters → two bands).
    sc = SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion", contest_exponent=0.0, move_cost_flat=0.0)
    w = TerrainWorld(n_agents=4, kcal_cfg=KcalEconomyConfig(), seed=1, game_stream=False, substrate_cfg=sc,
                     harvest_field=_UniformCapacity(3.0), placement_positions=[(10, 10), (11, 10), (50, 50), (51, 50)],
                     demography_cfg=DemographyConfig(enable_pair_bonds=True, enable_band_affiliation=True,
                                                     bonded_mate_radius=1))
    b = [a._group.band_id for a in w.agent_list]
    assert len(set(b)) == 2                                       # two spatial clusters → two distinct bands
    assert b[0] == b[1] and b[2] == b[3] and b[0] != b[2]         # each cluster shares one band id


def test_band_affiliation_off_by_default():
    assert DemographyConfig().enable_band_affiliation is False and DemographyConfig().band_cohesion == 0.0


def test_band_knob_additive_delta():
    # F.3c-2b: a band's family knob = global (egalitarian baseline) + the society preset's additive delta from
    # egalitarian. Un-morphed band → global EXACTLY (E.3 calibration preserved); a complex band deviates.
    sc = SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion", contest_exponent=0.0, move_cost_flat=0.0)
    w = TerrainWorld(n_agents=1, kcal_cfg=KcalEconomyConfig(), seed=1, game_stream=False, substrate_cfg=sc,
                     harvest_field=_UniformCapacity(2.0), placement_positions=[(10, 10)],
                     demography_cfg=DemographyConfig(mate_choice_strength=5.0, lineage_reversion=0.1))
    assert w._band_knob(0, "mate_choice_strength") == 5.0                  # no society → global baseline (E.3 safe)
    w._band_society[0] = "complex_forager"
    assert abs(w._band_knob(0, "mate_choice_strength") - 7.0) < 1e-9       # 5 + (3.0 − 1.0)
    assert abs(w._band_knob(0, "lineage_reversion") - 0.0) < 1e-9          # 0.1 + (0.10 − 0.30) = −0.1 → clamp 0


def test_dynamic_band_seams_off_by_default():
    cfg = DemographyConfig()
    assert cfg.enable_dynamic_bands is False and cfg.enable_band_family_knobs is False


# ── Social-Evolution Stage 1: LEADER COHERENCE (additive 2nd cohesion source, Boehm-gated) ────────
def _leader_world(n=8, seed=1, base=5, cap=9, merge=1, positions=None, **cfg_kw):
    # One connected spatial cluster (some x/y spread so a fission has a real median cut), all forced into ONE
    # band_id — isolates `_maintain_bands`'s split-threshold arithmetic from the seeding/affiliation machinery
    # (same direct-call convention as test_band_knob_additive_delta). `positions`/`merge` let the fusion tests
    # place several distinct bands with a chosen merge threshold.
    if positions is None:
        positions = [(10 + i % 4, 10 + i // 4) for i in range(n)]
    sc = SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion", contest_exponent=0.0, move_cost_flat=1e12)
    w = TerrainWorld(n_agents=n, kcal_cfg=KcalEconomyConfig(), seed=seed, game_stream=False, substrate_cfg=sc,
                     harvest_field=_UniformCapacity(3.0), placement_positions=positions,
                     demography_cfg=DemographyConfig(enable_dynamic_bands=True, band_base_tolerable=base,
                                                     band_split_size=cap, band_merge_size=merge, assabiyah_decay=0.0,
                                                     **cfg_kw))
    for a in w.agent_list:
        a._group.band_id = 0
        a.cred, a.prowess = 1.0, 1.0
    w._next_band_id = 1                                           # fission needs a fresh id counter (normally
                                                                    # seeded by enable_band_affiliation; bypassed here)
    return w


def test_leader_coherence_off_by_default():
    cfg = DemographyConfig()
    assert cfg.enable_leader_coherence is False and cfg.leader_coherence_gain == 0.0


def test_leader_society_weight_boehm_ladder():
    # egalitarian bands actively LEVEL leaders (Boehm 1999) → the mechanism is INERT there (weight 0), not just
    # weak; complex/stratified rise. Unclassified/None defaults to the conservative egalitarian weight.
    assert LEADER_SOCIETY_WEIGHT["egalitarian_forager"] == 0.0
    assert 0.0 < LEADER_SOCIETY_WEIGHT["complex_forager"] < LEADER_SOCIETY_WEIGHT["stratified_chiefdom"]
    from sic_games.demography import leader_society_weight
    assert leader_society_weight(None) == 0.0 and leader_society_weight("egalitarian_forager") == 0.0


def test_leader_term_zero_when_flag_off():
    # flag off ⇒ leader_term ≡ 0 regardless of gain (bit-exact-when-off contract).
    w = _leader_world(enable_leader_coherence=False, leader_coherence_gain=5.0)
    w.agent_list[0].cred = 100.0                                  # a stark status outlier
    w._band_society[0] = "stratified_chiefdom"
    w._maintain_bands()
    assert w._band_leader_term[0] == 0.0


def test_leader_term_zero_in_egalitarian_band():
    # Boehm gate: flag+gain ON but the band is (unclassified ⇒) egalitarian ⇒ leader_term still 0.
    w = _leader_world(enable_leader_coherence=True, leader_coherence_gain=1.0)
    w.agent_list[0].cred = 100.0
    w._maintain_bands()
    assert w._band_leader_term[0] == 0.0


def test_leader_term_positive_and_scales_with_society_weight():
    # Same stark leader in a complex vs. a stratified band → term scales with the Boehm weight (0.5 vs 1.0),
    # i.e. exactly double for the identical leader_strength (weight is a pure multiplier).
    terms = {}
    for soc in ("complex_forager", "stratified_chiefdom"):
        w = _leader_world(enable_leader_coherence=True, leader_coherence_gain=1.0)
        w.agent_list[0].cred = 100.0
        w._band_society[0] = soc
        w._maintain_bands()
        terms[soc] = w._band_leader_term[0]
    assert terms["complex_forager"] > 0.0
    assert abs(terms["stratified_chiefdom"] - 2.0 * terms["complex_forager"]) < 1e-9


def test_leader_coherence_prevents_premature_fission():
    # THE benchmark payoff: band_base_tolerable=5 < size(8) ≤ band_split_size=9. With leader coherence OFF the
    # band has no cohesion (assabiyah=0) ⇒ tolerable=base=5 ⇒ 8>5 FISSIONS. With a stark leader in a stratified
    # band, the added cohesion lifts tolerable above 8 ⇒ the SAME band stays intact.
    off = _leader_world(enable_leader_coherence=False)
    off._maintain_bands()
    assert len({a._group.band_id for a in off.agent_list}) > 1              # fissioned

    on = _leader_world(enable_leader_coherence=True, leader_coherence_gain=1.0)
    on.agent_list[0].cred = 100.0                                            # one stark leader
    on._band_society[0] = "stratified_chiefdom"
    on._maintain_bands()
    assert len({a._group.band_id for a in on.agent_list}) == 1               # stayed together


def test_leader_coherence_hard_cap_still_holds():
    # RED-TEAM #4: no amount of leader_coherence_gain can push tolerable_size above band_split_size (the cap is
    # on cohesion_frac ≤ 1.0, not on the gain). A band bigger than the cap fissions regardless.
    w = _leader_world(n=12, enable_leader_coherence=True, leader_coherence_gain=1000.0)
    w.agent_list[0].cred = 100.0
    w._band_society[0] = "stratified_chiefdom"
    w._maintain_bands()
    assert len({a._group.band_id for a in w.agent_list}) > 1                 # 12 > cap(9) ⇒ still fissions


def test_leader_coherence_additive_to_assabiyah_not_a_relabel():
    # RED-TEAM #1: assabiyah and leader coherence are SEPARATE additive terms, each independently ablatable.
    # Give the band positive surplus (⇒ assabiyah > 0 after one step) with leader coherence OFF, then ON, and
    # confirm the leader-only term is on top of (not a substitute for) the assabiyah contribution.
    w = _leader_world(enable_leader_coherence=False, assabiyah_gain=0.5)
    w._band_surplus[0] = 1.0
    w._maintain_bands()
    assert w._band_assabiyah[0] > 0.0 and w._band_leader_term[0] == 0.0     # assabiyah alone, leader inert

    w2 = _leader_world(enable_leader_coherence=True, leader_coherence_gain=1.0, assabiyah_gain=0.5)
    w2._band_surplus[0] = 1.0
    w2.agent_list[0].cred = 100.0
    w2._band_society[0] = "stratified_chiefdom"
    w2._maintain_bands()
    assert w2._band_assabiyah[0] > 0.0 and w2._band_leader_term[0] > 0.0    # BOTH contribute


def test_band_leaders_diagnostic_identifies_top_status():
    w = _leader_world(n=4, enable_leader_coherence=True, leader_coherence_gain=1.0)
    w.agent_list[2].cred = 50.0                                             # a clear top-status agent
    leaders = w.band_leaders()
    assert leaders[0] is w.agent_list[2]


def test_band_leaders_reflects_a_forced_removal():
    # The controlled-experiment hook: force-remove the current leader (set .alive=False, then apply the same
    # pruning `step()` does) and confirm `band_leaders()` picks up the new (2nd-highest-status) leader.
    w = _leader_world(n=4, enable_leader_coherence=True, leader_coherence_gain=1.0)
    w.agent_list[2].cred = 50.0
    w.agent_list[1].cred = 10.0
    leader1 = w.band_leaders()[0]
    assert leader1 is w.agent_list[2]
    leader1.alive = False
    w.agent_list = [a for a in w.agent_list if a.alive]
    leader2 = w.band_leaders()[0]
    assert leader2 is not leader1 and leader2.cred == 10.0                  # the next-highest status takes over


# ── Social-Evolution Stage 1b: SIZE-DRIVEN REPULSION (Johnson 1982 scalar stress) ─────────────────
def test_size_repulsion_off_by_default():
    cfg = DemographyConfig()
    assert cfg.enable_size_repulsion is False and cfg.repulsion_gain == 0.0


def test_size_repulsion_function_shape():
    # A logistic in band size: ~0 for tiny bands, rising monotone, saturating toward gain·factor for large ones.
    f = lambda n, soc="egalitarian_forager": size_repulsion(n, gain=1.0, midpoint=25.0, width=6.0, society=soc)
    assert f(0) == 0.0 or f(5) < 0.05                                       # small band → negligible scalar stress
    assert f(10) < f(25) < f(40)                                           # monotone rising in size
    assert abs(f(25) - 0.5) < 1e-9                                         # at the midpoint → half of gain·factor
    assert f(60) > 0.95                                                    # large band → saturates toward gain
    assert size_repulsion(40, gain=0.0, midpoint=25, width=6, society="egalitarian_forager") == 0.0   # gain 0 ⇒ 0


def test_size_repulsion_relieved_by_hierarchy():
    # Johnson's thesis: organizational structure ABSORBS scalar stress, so at the SAME size a hierarchical band
    # feels less repulsion than an egalitarian one (egalitarian 1.0 > complex 0.5 > stratified 0.25).
    kw = dict(gain=1.0, midpoint=25.0, width=6.0)
    eg = size_repulsion(40, society="egalitarian_forager", **kw)
    cx = size_repulsion(40, society="complex_forager", **kw)
    st = size_repulsion(40, society="stratified_chiefdom", **kw)
    assert eg > cx > st > 0.0
    assert abs(cx - 0.5 * eg) < 1e-9 and abs(st - 0.25 * eg) < 1e-9        # exactly the society-factor ladder
    assert REPULSION_SOCIETY_FACTOR["egalitarian_forager"] == 1.0
    assert size_repulsion(40, society=None, **kw) == eg                    # None → egalitarian (full stress)


def test_repulsion_term_zero_when_flag_off():
    # flag off ⇒ repulsion ≡ 0 regardless of gain (bit-exact-when-off contract), even for a large band.
    w = _leader_world(n=12, enable_size_repulsion=False, repulsion_gain=5.0)
    w._maintain_bands()
    assert w._band_repulsion[0] == 0.0


def test_repulsion_causes_fission_of_a_large_mobile_band():
    # THE Stage-1b payoff: a large EGALITARIAN (mobile) band that assabiyah would otherwise hold together
    # fissions under size-driven repulsion — resource-INDEPENDENTLY (surplus/assabiyah are maxed here).
    # base=5, cap=15 (headroom 10), n=10. OFF: assabiyah≈1 ⇒ tolerable≈cap=15 ⇒ n=10 not > 15 ⇒ stays whole.
    off = _leader_world(n=10, base=5, cap=15, enable_size_repulsion=False, assabiyah_gain=1.0)
    off._band_surplus[0] = 1.0
    off._maintain_bands()
    assert len({a._group.band_id for a in off.agent_list}) == 1            # cohesive, intact

    # ON: the same maxed assabiyah, but repulsion knocks cohesion_frac down ⇒ tolerable falls below 10 ⇒ fissions.
    on = _leader_world(n=10, base=5, cap=15, enable_size_repulsion=True, repulsion_gain=0.8, repulsion_midpoint=6.0,
                       repulsion_width=2.0, assabiyah_gain=1.0)
    on._band_surplus[0] = 1.0
    on._maintain_bands()
    assert len({a._group.band_id for a in on.agent_list}) > 1              # scalar stress fissioned it


def test_repulsion_relieved_band_stays_together():
    # Same large band + same repulsion, but STRATIFIED (hierarchy absorbs scalar stress) → the relieved repulsion
    # is small enough that assabiyah still holds it together. The "settling/hierarchy unlocks larger groups" lever.
    rep = dict(base=5, cap=15, enable_size_repulsion=True, repulsion_gain=0.8, repulsion_midpoint=6.0,
               repulsion_width=2.0, assabiyah_gain=1.0)
    st = _leader_world(n=10, **rep)
    st._band_surplus[0] = 1.0
    st._band_society[0] = "stratified_chiefdom"
    st._maintain_bands()
    assert len({a._group.band_id for a in st.agent_list}) == 1            # hierarchy-relieved → stays whole
    # and it genuinely felt LESS repulsion than the egalitarian arm did (which fissioned above):
    eg = _leader_world(n=10, **rep)
    eg._band_surplus[0] = 1.0
    eg._maintain_bands()
    assert st._band_repulsion[0] < eg._band_repulsion[0]
    assert len({a._group.band_id for a in eg.agent_list}) > 1             # egalitarian arm fissioned


def test_repulsion_restores_headroom_for_leader_coherence():
    # The measured full-stack problem (assabiyah saturates cohesion_frac at 1.0 ⇒ leader term is absorbed by the
    # clamp): with repulsion pulling cohesion_frac off the ceiling, the leader term again MOVES tolerable_size.
    def tol(leader_on):
        w = _leader_world(n=10, base=5, cap=15, enable_size_repulsion=True, repulsion_gain=0.6,
                          repulsion_midpoint=6.0, repulsion_width=2.0, assabiyah_gain=1.0,
                          enable_leader_coherence=leader_on, leader_coherence_gain=1.0)
        w._band_surplus[0] = 1.0
        w.agent_list[0].cred = 100.0                                       # a stark leader
        w._band_society[0] = "stratified_chiefdom"
        w._maintain_bands()
        # reconstruct the band's split threshold the same way _maintain_bands did
        cfg = w._demog
        a = w._band_assabiyah[0]; lt = w._band_leader_term[0]; rp = w._band_repulsion[0]
        frac = min(1.0, max(0.0, a + lt - rp))
        return cfg.band_base_tolerable + (cfg.band_split_size - cfg.band_base_tolerable) * frac
    assert tol(True) > tol(False)                                         # leader coherence now lifts tolerable


# ── M2: malnutrition fission (severe scarcity → LARGE bands break up; realized-starvation signal) ────
def test_malnutrition_fission_off_by_default():
    cfg = DemographyConfig()
    assert cfg.enable_malnutrition_fission is False and cfg.malnutrition_fission_gain == 0.0
    assert cfg.malnutrition_starv_rate == 0.05 and cfg.malnutrition_ema_alpha == 0.3


def test_malnutrition_term_fires_on_realized_starvation_only():
    # pressure = gain·min(1, ema/rate); the EMA is built from THIS step's per-band starvation deaths. No deaths ⇒ 0.
    fed = _leader_world(n=6, assabiyah_gain=1.0, enable_malnutrition_fission=True,
                        malnutrition_fission_gain=1.0, malnutrition_starv_rate=0.05)
    fed._band_surplus[0] = 1.0
    fed._band_starv_this_step = {}                                       # no starvation deaths this step
    fed._maintain_bands()
    assert fed._band_malnutrition[0] == 0.0

    starv = _leader_world(n=6, assabiyah_gain=1.0, enable_malnutrition_fission=True,
                          malnutrition_fission_gain=1.0, malnutrition_starv_rate=0.05, malnutrition_ema_alpha=0.3)
    starv._band_surplus[0] = 1.0
    starv._band_starv_this_step = {0: 3}                                 # 3 of (6+3) starved → rate 1/3
    starv._maintain_bands()
    ema = 0.3 * (3 / 9)                                                  # prev 0 → alpha·rate = 0.1
    assert abs(starv._band_malnutrition[0] - 1.0 * min(1.0, ema / 0.05)) < 1e-9   # saturates (0.1/0.05 → 1)


def test_malnutrition_fissions_large_starving_band():
    # THE M2 payoff: a large band that assabiyah holds together with NO deaths breaks up once it starts starving.
    fed = _leader_world(n=8, base=5, cap=9, assabiyah_gain=1.0, enable_malnutrition_fission=True,
                        malnutrition_fission_gain=1.5, malnutrition_starv_rate=0.05)
    fed._band_surplus[0] = 1.0
    fed._band_starv_this_step = {}                                       # no starvation
    fed._maintain_bands()
    assert len({a._group.band_id for a in fed.agent_list}) == 1          # well-fed large band stays whole

    starv = _leader_world(n=8, base=5, cap=9, assabiyah_gain=1.0, enable_malnutrition_fission=True,
                          malnutrition_fission_gain=1.5, malnutrition_starv_rate=0.05)
    starv._band_surplus[0] = 1.0
    starv._band_starv_this_step = {0: 3}                                 # losing members to starvation
    starv._maintain_bands()
    assert len({a._group.band_id for a in starv.agent_list}) > 1         # starving large band broke up


def test_malnutrition_size_gate_spares_small_bands():
    # Intrinsic size-gate: tolerable floors at base_tolerable, so a starving band SMALLER than base can't fission.
    small = _leader_world(n=4, base=5, cap=9, assabiyah_gain=1.0, enable_malnutrition_fission=True,
                          malnutrition_fission_gain=1.5, malnutrition_starv_rate=0.05)
    small._band_surplus[0] = 1.0
    small._band_starv_this_step = {0: 3}                                 # starving, but only 4 < base 5
    small._maintain_bands()
    assert len({a._group.band_id for a in small.agent_list}) == 1        # untouched (below the base floor)


def test_malnutrition_zero_and_bit_exact_when_off():
    off = _leader_world(n=8, base=5, cap=9, assabiyah_gain=1.0, enable_malnutrition_fission=False,
                        malnutrition_fission_gain=1.5)
    off._band_surplus[0] = 1.0
    off._band_starv_this_step = {0: 5}                                   # heavy starvation, but flag OFF
    off._maintain_bands()
    assert off._band_malnutrition[0] == 0.0
    assert len({a._group.band_id for a in off.agent_list}) == 1          # off ⇒ assabiyah holds it, no fission


# ── F: resource-directed fusion (starving remnant → RICHEST nearby band, not nearest) ───────────────
_FUSE_POS = [(10, 10), (10, 11),                       # band 0: remnant (size 2 < merge 3)
             (14, 10), (14, 11), (14, 12),             # band 1: NEAR, poor (size 3)
             (30, 30), (30, 31), (30, 32)]             # band 2: FAR, rich (size 3)


def _fusion_world(rdf, radius=40.0):
    w = _leader_world(n=8, merge=3, positions=_FUSE_POS,
                      enable_resource_directed_fusion=rdf, fusion_search_radius=radius)
    for i, a in enumerate(w.agent_list):
        a._group.band_id = 0 if i < 2 else (1 if i < 5 else 2)
    w._band_surplus = {0: 0.0, 1: 0.0, 2: 1.0}          # the FAR band is the rich one
    return w


def test_resource_directed_fusion_off_by_default():
    assert DemographyConfig().enable_resource_directed_fusion is False


def test_fusion_joins_nearest_when_off():
    off = _fusion_world(rdf=False)
    off._maintain_bands()
    assert off.agent_list[0]._group.band_id == 1        # nearest to the remnant is the NEAR poor band


def test_fusion_joins_richest_nearby_when_on():
    on = _fusion_world(rdf=True, radius=40.0)            # rich far band (~29 away) is within radius
    on._maintain_bands()
    assert on.agent_list[0]._group.band_id == 2         # joined the RICH band, though it's farther


def test_fusion_radius_bounds_the_search():
    on = _fusion_world(rdf=True, radius=10.0)            # rich far band (~29) is OUT of range → nearest only
    on._maintain_bands()
    assert on.agent_list[0]._group.band_id == 1         # falls back to the near (poor) band
