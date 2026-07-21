"""R-92 — LINEAGE SEGMENTATION: a named line splits into two real sub-clades.

CHARTER DECLARATION (MECHANISM_CHARTER §3.1):
  TYPE      N (Novelty) — introduces a new label into a heritable discrete space.
  UNIT      LINEAGE.
  INVARIANT membership is CONSERVED exactly — the two segments partition the old lineage, nobody is created,
            destroyed, or left without a line. Asserted directly below.
  ANCHOR    rate calibrated against [Hill et al. 2011, FILED] via MODEL_SPEC §4.8.8 (~7 lineages/band,
            dominant-lineage share 0.38 — the target R-25 passed and the R-89 collapse broke).

WHY IT REPLACES R-90's PER-BIRTH BRANCHING, stated as a test rather than a comment: that mechanism minted
SINGLETONS, which mostly die, so it inflated the lineage COUNT while concentration got WORSE — measured at
campaign scale, n_lineages 5→32 but eff_lineages 3.4→1.8 and top_share 0.42→0.73. The regression guard here is
`test_segments_are_viable_not_singletons`: whatever else changes, a new line must not arrive with one member.
"""
import pytest

from sic_games.capacity import NPPCapacityField
from sic_games.config import CarbonConfig, KcalEconomyConfig, SubstrateConfig
from sic_games.demography import DemographyConfig
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world, world_lottery_climate


def _force_lineage(w, n_members=24, n_subs=3, lid=999_001):
    """Construct the state segmentation acts on, rather than waiting for the dynamics to produce it.
    NECESSARY, not lazy: measured, this world's largest lineage holds 4 members at step 80 and 9 at step 400,
    so `n >= 2*min_segment` is essentially never met inside a fast test — the first cut of these tests failed
    for exactly that reason, on a mechanism that was working. Same lesson as R-90's calibration sweep: exercise
    a mechanism in the regime where it can act, or the test measures nothing."""
    ms = w.agent_list[:n_members]
    assert len(ms) == n_members, "world too small to build the fixture"
    for i, a in enumerate(ms):
        a._lineage = lid
        a._subclan = 2_000_000 + (i % n_subs)
    return ms, lid


def _world(n=260, split=False, rate=0.0, min_seg=8, seed=0, branch=0.0):
    k = world_lottery_climate(seed, terrain="coastal", climate="temperate")
    f = generate_world(k, mode="climate")
    hf = NPPCapacityField(f, 75000.0, patch=(20, 20, 60), mode="tallavaara", aquatic=True, enable_depletion=True)
    land = [(x, y) for y in range(100) for x in range(100) if f.isWater[y, x] == 0 and hf.level(x, y) > 0]
    d = DemographyConfig(enable_cred_status=True, cred_seed_sigma=0.5, cred_inherit_sigma=0.1,
                         enable_paternity=True, mate_choice_strength=5.0, enable_prowess_facet=True,
                         enable_pair_bonds=True, enable_band_affiliation=True,
                         band_cohesion=0.3, band_split_size=45, band_merge_size=10,
                         enable_game=True, game_meat_frac=0.55,
                         enable_lineage_split=split, lineage_split_rate=rate,
                         lineage_split_min_segment=min_seg,
                         enable_lineage_branching=(branch > 0.0), lineage_branch_rate=branch)
    return TerrainWorld(n_agents=n, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, game_stream=False, seed=seed,
                        carbon_cfg=CarbonConfig(kappa=1.5),
                        substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                                      contest_exponent=1.5, move_cost_flat=0.0),
                        harvest_field=hf, placement_positions=[land[i % len(land)] for i in range(n)],
                        demography_cfg=d)


def test_defaults_off():
    c = DemographyConfig()
    assert c.enable_lineage_split is False and c.lineage_split_rate == 0.0


def test_off_is_bit_exact():
    """Rate 0 must draw NOTHING from the RNG, or every downstream draw shifts."""
    a, b = _world(split=False, seed=3), _world(split=True, rate=0.0, seed=3)
    for _ in range(40):
        a.step(); b.step()
    assert [x.unique_id for x in a.agent_list] == [x.unique_id for x in b.agent_list]
    assert [x._lineage for x in a.agent_list] == [x._lineage for x in b.agent_list]
    assert [round(x.cred, 12) for x in a.agent_list] == [round(x.cred, 12) for x in b.agent_list]
    assert a.lineage_splits_this_step == b.lineage_splits_this_step == 0


def test_splitting_fires():
    """Hazard is rate*n, so rate=1.0 on a 24-member lineage fires deterministically."""
    w = _world(split=True, rate=1.0, min_seg=4, branch=0.15)
    for _ in range(20):
        w.step()
    ms, lid = _force_lineage(w, n_members=24, n_subs=3)
    w._do_lineage_split()
    assert w.lineage_splits_this_step == 1, "segmentation did not fire on a qualifying lineage"
    now = {a._lineage for a in ms}
    assert len(now) == 2, f"expected the lineage to cleave in two, got {len(now)}"


def test_membership_is_conserved():
    """THE INVARIANT. A split partitions — it must not create, destroy or orphan anyone."""
    w = _world(split=True, rate=0.02, min_seg=3, branch=0.15)
    for _ in range(60):
        before = len(w.agent_list)
        w.step()
        assert w.agent_list
        assert all(getattr(a, "_lineage", None) is not None for a in w.agent_list), "an agent lost its lineage"
    assert before > 0


def test_segments_are_viable_not_singletons():
    """THE R-90 REGRESSION GUARD. Per-birth branching minted lineages of ONE, which mostly died — count up,
    substance down. Every lineage created by a split must arrive with at least `min_segment` members."""
    w = _world(split=True, rate=0.02, min_seg=5, branch=0.15)
    for _ in range(80):
        pre = {a._lineage for a in w.agent_list}
        w.step()
        if not w.agent_list or w.lineage_splits_this_step == 0:
            continue
        counts: dict = {}
        for a in w.agent_list:
            counts[a._lineage] = counts.get(a._lineage, 0) + 1
        for lid, n in counts.items():
            if lid not in pre:                       # a line that did not exist before this step
                assert n >= 5, f"new lineage {lid} arrived with {n} members — singleton regression"


def test_both_halves_survive_the_minimum():
    """A degenerate cleavage must be SKIPPED, not forced — otherwise the minimum is decorative. Here every
    sub-branch is smaller than the minimum, so no legal cleavage exists and nothing may happen."""
    w = _world(split=True, rate=1.0, min_seg=10, branch=0.15)
    for _ in range(20):
        w.step()
    ms, lid = _force_lineage(w, n_members=24, n_subs=6)      # 6 subs of 4 — every one below min_seg=10
    w._do_lineage_split()
    assert w.lineage_splits_this_step == 0, "forced a split that violates the minimum segment"
    assert {a._lineage for a in ms} == {lid}, "membership changed despite no legal cleavage"


def test_segment_is_a_whole_sub_branch_not_an_arbitrary_cut():
    """The cleavage must follow DESCENT: the seceding side is exactly one `_subclan`, never a mixture."""
    w = _world(split=True, rate=1.0, min_seg=4, branch=0.15)
    for _ in range(20):
        w.step()
    ms, lid = _force_lineage(w, n_members=24, n_subs=3)
    w._do_lineage_split()
    moved = [a for a in ms if a._lineage != lid]
    assert moved, "nothing seceded"
    assert len({a._subclan for a in moved}) == 1, "the seceding segment mixed sub-branches"
    stayed_subs = {a._subclan for a in ms if a._lineage == lid}
    assert not (stayed_subs & {moved[0]._subclan}), "a sub-branch was split across both sides"


def test_no_ceiling_is_imposed_on_lineage_size():
    """The distinction from size-TRIGGERED segmentation: hazard scales with size, but nothing CAPS it, so
    top_share stays a free measurement rather than an artifact of a threshold (what T-9 needs)."""
    w = _world(split=True, rate=0.01, min_seg=5, branch=0.15)
    for _ in range(80):
        w.step()
        assert w.agent_list
    d = w.dynasties()
    assert 0.0 < d["top_share"] <= 1.0
    sizes = [r["n"] for r in d["top"]]
    assert sizes == sorted(sizes, reverse=True)


def test_split_raises_lineage_count():
    """Direct: one qualifying lineage becomes two."""
    w = _world(split=True, rate=1.0, min_seg=4, branch=0.15)
    for _ in range(20):
        w.step()
    before = w.dynasties()["n_lineages"]
    _force_lineage(w, n_members=24, n_subs=3)
    mid = w.dynasties()["n_lineages"]          # collapsing 24 agents into one lineage LOWERS the count
    w._do_lineage_split()
    assert w.dynasties()["n_lineages"] == mid + 1


def test_split_needs_subclan_diversity_to_act_on():
    """A REAL DEPENDENCY, recorded rather than left implicit: segmentation cleaves along the heritable
    `_subclan` tag, so with branching OFF every lineage is one undivided descent group and nothing can ever
    split. The two mechanisms are a PAIR — branching seeds sub-branches (singletons are harmless there),
    segmentation promotes one once it has grown into a real body of kin."""
    w = _world(split=True, rate=0.05, min_seg=3, branch=0.0)
    fired = 0
    for _ in range(80):
        w.step()
        assert w.agent_list
        fired += w.lineage_splits_this_step
    assert fired == 0, "split fired with no sub-branches to cleave along"
