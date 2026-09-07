"""R-96 — rank is LOCAL: a lineage is noble in a place, not in the world.

THE BUG. `_lineage_ascribed` was a single global set, while every mechanism that acts on it is local. So when
one village revolted, `discard(lineage)` de-ranked that lineage in EVERY other village at the same instant.
Measured (R-95, campaign scale): ~7% of all lineages stripped per revolt, and villages holding nobility fell
from 82% to 3% — nobility ANNIHILATED rather than cycled, with the revolt curve flattening for want of anything
left to overthrow.

It contradicts the anchor head-on. Leach's whole observation is that Kachin communities sit in DIFFERENT states
at the same time — the "shifting back and forth" is a patchwork across villages, not a synchronised worldwide
flip. A single global set cannot represent that, no matter how it is tuned.

WHY IT WAS INVISIBLE UNTIL NOW, which is the recurring shape of this whole arc: before R-93 the ascription
threshold was degenerate, so status was re-earned within a few years and the global strip was undone before
anyone could notice the scope was wrong. Fixing the threshold made status genuinely hard to earn, at which
point the same strip became permanent. The previous behaviour was only ever working by accident.
"""
import pytest

from sic_games.capacity import NPPCapacityField
from sic_games.config import CarbonConfig, KcalEconomyConfig, SubstrateConfig
from sic_games.demography import DemographyConfig
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world, world_lottery_climate


def _world(n=260, local=False, seed=0):
    k = world_lottery_climate(seed, terrain="coastal", climate="temperate")
    f = generate_world(k, mode="climate")
    hf = NPPCapacityField(f, 75000.0, patch=(20, 20, 60), mode="tallavaara", aquatic=True, enable_depletion=True)
    land = [(x, y) for y in range(100) for x in range(100) if f.isWater[y, x] == 0 and hf.level(x, y) > 0]
    d = DemographyConfig(enable_cred_status=True, cred_seed_sigma=0.5, cred_inherit_sigma=0.1,
                         enable_paternity=True, mate_choice_strength=5.0, enable_prowess_facet=True,
                         enable_pair_bonds=True, enable_band_affiliation=True,
                         band_cohesion=0.3, band_split_size=45, band_merge_size=10,
                         enable_game=True, game_meat_frac=0.55,
                         enable_material_capture=True, material_hide_frac=0.07, material_decay=0.0,
                         enable_legitimacy=True, legit_feast_frac=0.25, legit_cred_gain=10.0,
                         legit_threshold=0.10, legit_decay=0.02,
                         enable_delegitimation=True, resent_alpha=0.4, resent_threshold=0.05,
                         enable_local_ascription=local)
    return TerrainWorld(n_agents=n, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, game_stream=False, seed=seed,
                        carbon_cfg=CarbonConfig(kappa=1.5),
                        substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                                      contest_exponent=1.5, move_cost_flat=0.0),
                        harvest_field=hf, placement_positions=[land[i % len(land)] for i in range(n)],
                        demography_cfg=d)


def test_defaults_off():
    assert DemographyConfig().enable_local_ascription is False


def test_off_is_bit_exact():
    """The load-bearing guarantee: with the flag off the keys stay bare lineage ids and nothing shifts."""
    a, b = _world(local=False, seed=3), _world(local=False, seed=3)
    for _ in range(40):
        a.step(); b.step()
    assert [x.unique_id for x in a.agent_list] == [x.unique_id for x in b.agent_list]
    assert [round(x.cred, 12) for x in a.agent_list] == [round(x.cred, 12) for x in b.agent_list]
    assert all(not isinstance(k, tuple) for k in a._lineage_ascribed), "keys should be bare lineage ids when off"


def test_local_keys_are_community_lineage_pairs():
    w = _world(local=True)
    for _ in range(60):
        w.step()
        assert w.agent_list
    keys = w._rank_keys()
    assert keys, "no agents"
    assert all(isinstance(k, tuple) and len(k) == 2 for k in keys.values())


def test_local_rank_needs_a_PERSISTENT_community_and_the_band_is_not_one():
    """A REAL DEPENDENCY, discovered by this test failing rather than assumed.

    With rank keyed to the BAND, emergent ascription never happens at all: the legitimacy stock is now held per
    (community, lineage), band fission mints a fresh band_id, and the stock starts from zero there. The EMA
    needs ~50 steps to mature (legit_decay=0.02) while R-88 measured band lifetime at 10.2 yr median — the
    memory outlives its container, which is EXACTLY the R-95 finding reappearing one level up, now in the
    forward mechanism rather than the reverse one.

    So local ascription is only meaningful on a unit that persists: the settlement. This test pins the
    dependency so it cannot be forgotten, and documents why the flag is not useful on its own."""
    w = _world(local=True)
    for _ in range(150):
        w.step()
        assert w.agent_list
    assert not w._lineage_ascribed, (
        "band-keyed local ascription produced nobility — if this now passes, band lifetime or legit_decay has "
        "changed and the village-unit dependency should be re-derived rather than assumed")


def test_a_revolt_strips_only_the_community_that_revolted():
    """THE R-95 REGRESSION GUARD, and the whole point of the change. Ennoble one lineage in TWO communities,
    force a revolt in one, and the other must be untouched. Under the global set this test fails by
    construction — discarding the lineage removed it everywhere."""
    w = _world(local=True)
    for _ in range(60):
        w.step()
        assert w.agent_list
    units = w._rank_units()
    by_unit: dict = {}
    for a in w.agent_list:
        by_unit.setdefault(units[a], []).append(a)
    big = sorted(by_unit.items(), key=lambda kv: -len(kv[1]))[:2]
    assert len(big) == 2 and len(big[1][1]) >= 2, "need two populated communities"
    (u1, m1), (u2, m2) = big

    # one shared lineage, ennobled in BOTH communities, with real privilege in the first
    lid = 987_654
    for a in m1 + m2:
        a._lineage = lid
    w._lineage_ascribed.add((u1, lid))
    w._lineage_ascribed.add((u2, lid))
    for a in m1:
        a.cred = 50.0
    w._band_resentment[u1] = 0.0

    for _ in range(40):
        w._do_delegitimation()
        if (u1, lid) not in w._lineage_ascribed:
            break
    assert (u1, lid) not in w._lineage_ascribed, "the revolting community never lost its rank"
    assert (u2, lid) in w._lineage_ascribed, \
        "a revolt in one community stripped rank in ANOTHER — the R-95 global-scope bug is back"


def test_the_same_lineage_can_be_noble_here_and_common_there():
    """Leach's actual claim, as a property: communities in DIFFERENT states simultaneously. A single global set
    cannot express this at all."""
    w = _world(local=True)
    for _ in range(60):
        w.step()
    units = w._rank_units()
    by_unit: dict = {}
    for a in w.agent_list:
        by_unit.setdefault(units[a], []).append(a)
    big = sorted(by_unit.items(), key=lambda kv: -len(kv[1]))[:2]
    (u1, m1), (u2, m2) = big
    lid = 123_456
    for a in m1 + m2:
        a._lineage = lid
    w._lineage_ascribed.add((u1, lid))          # noble here, common there
    w._lineage_ascribed.discard((u2, lid))
    keys = w._rank_keys()
    assert all(keys[a] in w._lineage_ascribed for a in m1)
    assert all(keys[a] not in w._lineage_ascribed for a in m2)


def test_dead_communities_are_forgotten():
    """Villages come and go over a campaign; their rank entries must not accumulate without bound."""
    w = _world(local=True)
    for _ in range(150):
        w.step()
        assert w.agent_list
    w._lineage_ascribed.add((("v", (-99, -99)), 555))     # a community that does not exist
    w._lineage_legit[(("v", (-99, -99)), 555)] = 0.9
    w._do_delegitimation()
    assert (("v", (-99, -99)), 555) not in w._lineage_ascribed
    assert (("v", (-99, -99)), 555) not in w._lineage_legit
