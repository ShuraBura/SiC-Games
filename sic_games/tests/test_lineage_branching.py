"""R-90 — BRANCHING: new heritable sub-branches appear, so descent is not a pure absorbing process.

RESHAPED BY R-92, and these tests were rewritten with it. Branching originally minted a whole new LINEAGE per
birth, which made every new line a SINGLETON; singletons mostly die, so it added a churn of ephemeral names
that inflated the COUNT while concentration got WORSE (campaign scale: n_lineages 5->32 but eff_lineages
3.4->1.8, top_share 0.42->0.73). It now seeds a `_subclan` tag instead, where starting at one member is
harmless — the tag either grows into a real body of kin or vanishes. `_do_lineage_split` (R-92) promotes one
to a full lineage only once it HAS grown, so new lineages are born viable. See test_lineage_split.py.

CHARTER DECLARATION (MECHANISM_CHARTER §3.1):
  TYPE      N (Novelty) — introduces a new label into a heritable discrete space.
  UNIT      BIRTH (per-child), the same unit `genome_mutation` uses.
  INVARIANT conserves nothing and consumes nothing; relabels one child's descent group.
  ANCHOR    the RATE is calibrated against [Hill et al. 2011, FILED] via MODEL_SPEC §4.8.8's already-passed
            target (~7 lineages/band, dominant-lineage share 0.38 — R-25). The BRANCHING DEVICE itself is the
            standard infinite-allele model, already used here by `genome_mutation`.

WHY IT IS REQUIRED, not cosmetic. `_lineage` was founder-seeded and only ever LOST by extinction, never
created — an absorbing Markov chain, so fixation has probability 1 and the only question is when. Measured
(R-89, 12k-step campaign arm): 3000 founding patrilines → 5 by step 1950, then frozen at exactly 5 for the
next 5,650 steps. Two consequences, both load-bearing:
  (a) it BREAKS a target the model already passed — with 5 lineages worldwide you cannot have ~7 per band;
  (b) it FREEZES the elite layer — `_do_delegitimation` needs a non-ascribed lineage to found privilege on,
      and with every surviving lineage ascribed the gumsa→gumlao reversion cannot fire at all (4,269
      reversions before step 1950; exactly 0 in the 5,650 steps after).

WHY NOT SIZE-TRIGGERED SEGMENTATION (the ethnographically obvious alternative). Splitting a lineage once it
exceeds N members would cap lineage size, which would make `top_share` an artifact of the cap — destroying
the very statistic T-9 measures against Zerjal 2003 / Yan 2014. The infinite-allele device imposes no ceiling.
"""
import pytest

from sic_games.capacity import NPPCapacityField
from sic_games.config import CarbonConfig, KcalEconomyConfig, SubstrateConfig
from sic_games.demography import DemographyConfig
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world, world_lottery_climate


def _world(n=260, branch=False, rate=0.0, seed=0):
    k = world_lottery_climate(seed, terrain="coastal", climate="temperate")
    f = generate_world(k, mode="climate")
    hf = NPPCapacityField(f, 75000.0, patch=(20, 20, 60), mode="tallavaara", aquatic=True, enable_depletion=True)
    land = [(x, y) for y in range(100) for x in range(100) if f.isWater[y, x] == 0 and hf.level(x, y) > 0]
    d = DemographyConfig(enable_cred_status=True, cred_seed_sigma=0.5, cred_inherit_sigma=0.1,
                         enable_paternity=True, mate_choice_strength=5.0, enable_prowess_facet=True,
                         enable_pair_bonds=True, enable_band_affiliation=True,
                         band_cohesion=0.3, band_split_size=45, band_merge_size=10,
                         enable_game=True, game_meat_frac=0.55,
                         enable_lineage_branching=branch, lineage_branch_rate=rate)
    return TerrainWorld(n_agents=n, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, game_stream=False, seed=seed,
                        carbon_cfg=CarbonConfig(kappa=1.5),
                        substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                                      contest_exponent=1.5, move_cost_flat=0.0),
                        harvest_field=hf, placement_positions=[land[i % len(land)] for i in range(n)],
                        demography_cfg=d)


def test_defaults_off():
    c = DemographyConfig()
    assert c.enable_lineage_branching is False and c.lineage_branch_rate == 0.0


def test_off_is_bit_exact():
    """The load-bearing guarantee: rate 0 must draw NOTHING from the RNG, or every downstream draw shifts."""
    a, b = _world(branch=False, seed=3), _world(branch=True, rate=0.0, seed=3)
    for _ in range(40):
        a.step(); b.step()
    assert [x.unique_id for x in a.agent_list] == [x.unique_id for x in b.agent_list]
    assert [x._lineage for x in a.agent_list] == [x._lineage for x in b.agent_list]
    assert [round(x.cred, 12) for x in a.agent_list] == [round(x.cred, 12) for x in b.agent_list]
    assert a.lineage_branches_this_step == b.lineage_branches_this_step == 0


def test_branching_fires_and_mints_fresh_subclan_ids():
    """Branching now tags SUB-BRANCHES, not lineages. Rate 0.3 is deliberate: at 0.05 this world yields ~51
    births in 60 steps => ~2.6 expected events => P(zero) ~ 7%, and the first cut of this test duly drew zero
    and failed on a working mechanism. A presence assertion has to be POWERED."""
    w = _world(branch=True, rate=0.3)
    seen_new = set()
    for _ in range(60):
        w.step()
        assert w.agent_list
        for a in w.agent_list:
            if a._subclan is not None and a._subclan >= 260:      # 260 founders => tags 0..259
                seen_new.add(a._subclan)
    assert seen_new, "branching never fired at rate 0.3"
    assert w._next_subclan_id > 260
    assert all(i >= 260 for i in seen_new)


def test_branching_alone_does_not_create_lineages():
    """THE R-92 CORRECTION, asserted. Branching must no longer touch `_lineage` at all — a new named line may
    only arrive via segmentation, which guarantees it is born with real membership."""
    w = _world(branch=True, rate=0.3)
    founders = {a._lineage for a in w.agent_list}
    for _ in range(60):
        w.step()
        assert w.agent_list
    assert {a._lineage for a in w.agent_list} <= founders, "branching minted a lineage — singleton regression"


def test_branching_raises_subclan_diversity():
    """It must hold SUB-BRANCH diversity up against drift — that is the pool segmentation later draws on.

    NB the previous version of this test compared LINEAGE counts and still passed after the R-92 reshaping,
    which it should not have: branching no longer touches `_lineage`, so it was passing purely because adding
    an RNG draw shifts the whole stream and yields a different trajectory. A false pass, kept in mind here."""
    def subclans(w):
        return len({a._subclan for a in w.agent_list})
    off = _world(branch=False, seed=5)
    on = _world(branch=True, rate=0.3, seed=5)
    for _ in range(120):
        off.step(); on.step()
        assert off.agent_list and on.agent_list
    assert subclans(on) > subclans(off)


def test_branching_does_not_cap_top_share():
    """Deliberately NOT size-triggered segmentation — no ceiling is imposed on a lineage's size, so `top_share`
    stays a free measurement rather than an artifact of a threshold (the reason T-9 can use it at all)."""
    w = _world(branch=True, rate=0.02)
    for _ in range(60):
        w.step()
        assert w.agent_list
    d = w.dynasties()
    assert 0.0 < d["top_share"] <= 1.0
    sizes = [r["n"] for r in d["top"]]
    assert sizes == sorted(sizes, reverse=True)


def test_per_band_lineage_diagnostic_reports():
    """R-90 diagnostic against the FILED Hill 2011 target (~7 lineages/band, dom share 0.38). Checks the
    read-out is wired and self-consistent — the CALIBRATION itself is a probe, not a unit test."""
    w = _world(branch=True, rate=0.3)
    for _ in range(60):
        w.step()
        assert w.agent_list
    d = w.dynasties()
    assert d["lineages_per_band"] >= 1.0
    assert 0.0 < d["dom_lineage_share"] <= 1.0
    assert d["lineages_per_band"] <= d["n_lineages"], "a band cannot hold more lineages than exist"
