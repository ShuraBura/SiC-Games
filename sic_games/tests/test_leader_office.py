"""R-84 CHALLENGE-SUCCESSION — leadership as a tenured office (`enable_leader_office`).

DEFECT FIXED: `band_leaders()` recomputed argmax(cred·prowess) every step, so there was no incumbency, no
tenure, and a leader was never *removed* — he merely stopped being the maximum.

ANCHORS (all [VERIFIED] against the filed PDFs):
  · Boehm 1993 Table I, columns counted over the 48-society survey: DESERTION 17 vs DEPOSITION 9. Followers
    walking away is the COMMONER end of a bad leader than a challenge-and-defeat duel ⇒ deposition is the
    minority channel (`office_deposition_share` = 9/26 ≈ 0.346).
  · Boehm 1993, the 47 coded motivations: "dominating others as leader" (14) + "lack of generosity or
    monopolizing resources" (5) = OVERREACH (19); "ineffectiveness, partiality, or unresponsiveness in a
    leadership role" (10) = FAILURE TO DELIVER ⇒ `office_overreach_weight` = 19/29 ≈ 0.655.
  · Sahlins 1972:209 — the Nootka chief is "an officeholder in a lineage ... ascribed by right of chiefly due"
    so "centricity is built into the structure"; the Siuai big-man's following "will as such dissolve with the
    demise of the pivotal big-man" ⇒ `succession_dissolve`.
  · Hayden 1995 — "About 75% of New Guinea Entrepreneur Big Men had fathers that were also Big Men", but by
    transmitting moka partners and wives, NOT the position ⇒ father-son continuity must EMERGE from heritable
    status, and `leader_tenure()["father_was_leader"]` is a validation target, never an input.
"""
import pytest

from sic_games.capacity import NPPCapacityField
from sic_games.config import CarbonConfig, KcalEconomyConfig, SubstrateConfig
from sic_games.demography import DemographyConfig
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world, world_lottery_climate


def _world(n=260, office=False, gain=0.05, share=0.2, dissolve=False, seed=0, bands=True, **kw):
    k = world_lottery_climate(seed, terrain="coastal", climate="temperate")
    f = generate_world(k, mode="climate")
    hf = NPPCapacityField(f, 75000.0, patch=(20, 20, 60), mode="tallavaara", aquatic=True, enable_depletion=True)
    land = [(x, y) for y in range(100) for x in range(100) if f.isWater[y, x] == 0 and hf.level(x, y) > 0]
    d = DemographyConfig(enable_cred_status=True, cred_seed_sigma=0.5, cred_inherit_sigma=0.1,
                         enable_paternity=True, mate_choice_strength=5.0, enable_prowess_facet=True,
                         enable_pair_bonds=True, enable_band_affiliation=bands,
                         band_cohesion=0.3, band_split_size=45, band_merge_size=10,
                         enable_game=True, game_meat_frac=0.55,   # hides come from GAME — without it material stays 0
                         enable_material_capture=True, material_hide_frac=0.07, material_decay=0.002,
                         enable_leader_share=(share > 0), leader_share_frac=share,
                         enable_leader_office=office, office_grievance_gain=gain,
                         succession_dissolve=dissolve, **kw)
    return TerrainWorld(n_agents=n, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, game_stream=False, seed=seed,
                        carbon_cfg=CarbonConfig(kappa=1.5),
                        substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                                      contest_exponent=1.5, move_cost_flat=0.0),
                        harvest_field=hf, placement_positions=[land[i % len(land)] for i in range(n)],
                        demography_cfg=d)


def test_defaults_off():
    c = DemographyConfig()
    assert c.enable_leader_office is False and c.succession_dissolve is False


def test_anchored_constants_match_boehm():
    """The two ratios are read straight off Boehm 1993 and must not drift silently."""
    c = DemographyConfig()
    assert c.office_deposition_share == pytest.approx(9.0 / 26.0, abs=1e-9)   # deposition 9 : desertion 17
    assert c.office_overreach_weight == pytest.approx(19.0 / 29.0, abs=1e-9)  # (14 dominating + 5 monopolizing) / 29


def test_off_is_bit_exact():
    """Off ⇒ the method returns before any RNG draw ⇒ the stream is untouched."""
    a, b = _world(office=False, seed=3), _world(office=False, seed=3)
    for _ in range(40):
        a.step(); b.step()
    assert [x.unique_id for x in a.agent_list] == [x.unique_id for x in b.agent_list]
    assert [round(x.material, 12) for x in a.agent_list] == [round(x.material, 12) for x in b.agent_list]
    assert a.leader_tenure()["n_closed"] == 0          # the diagnostic reports nothing when the flag is off


def test_office_confers_incumbency_not_argmax():
    """THE POINT OF THE MECHANISM: with the office on, the leader is the sitting HOLDER, so he need not be the
    instantaneous cred·prowess maximum of his band — which is exactly what the legacy behaviour forced."""
    w = _world(office=True)
    for _ in range(120):
        w.step()
        assert w.agent_list
    leaders = w.band_leaders()
    assert leaders, "some band should hold an office"
    members: dict = {}
    for a in w.agent_list:
        members.setdefault(a._group.band_id, []).append(a)
    merit = lambda a: a.cred * getattr(a, "prowess", 1.0)
    incumbent_not_top = sum(1 for bid, ld in leaders.items()
                            if max(members[bid], key=merit) is not ld)
    assert incumbent_not_top > 0, "every holder being the current maximum means incumbency is not binding"


def test_only_adults_hold_office():
    """A high-cred CHILD could otherwise hold office (inherited cred, default prowess 1.0) — measured mean
    leader age 23.5 yr against an adult mean of 34.1 before the eligibility gate."""
    w = _world(office=True)
    for _ in range(120):
        w.step()
        assert w.agent_list
    floor = w._demog.menarche_months
    assert all(ld.age >= floor for ld in w.band_leaders().values())


def test_desertion_is_the_commoner_sanction():
    """Boehm 17:9 ⇒ desertion should be ~65% of sanction ATTEMPTS (a challenge may fail; a desertion cannot)."""
    w = _world(office=True, gain=0.25)
    chal = des = 0
    for _ in range(150):
        w.step()
        assert w.agent_list
        chal += w.challenges_this_step
        des += w.desertions_this_step
    assert chal + des > 30, "too few sanctions to judge the split"
    assert 0.5 < des / (chal + des) < 0.8, f"desertion share {des / (chal + des):.2f} should sit near 17/26"


def test_tenure_diagnostic_is_sane():
    w = _world(office=True)
    for _ in range(150):
        w.step()
        assert w.agent_list
    t = w.leader_tenure()
    assert t["n_bands"] > 0 and t["n_held"] > 0
    assert t["n_closed"] > 0, "no tenure ever closed in 150 steps"
    assert 0.0 < t["mean_years"] < 60.0
    assert t["vacant"] == 0, "the chiefly regime fills every office"


def test_dissolve_leaves_offices_vacant():
    """Sahlins' Siuai big-man: the following was one man's achievement and does not transfer, so a successor
    must stand clear of his nearest rival — where none does, the band stays leaderless (and levies nothing)."""
    w = _world(office=True, dissolve=True, gain=0.25)
    for _ in range(150):
        w.step()
        assert w.agent_list
    t = w.leader_tenure()
    assert t["vacant"] > 0, "big-man dissolution should leave some band leaderless"
    assert set(w.band_leaders()) != {a._group.band_id for a in w.agent_list}


def test_office_survives_without_band_affiliation():
    """REGRESSION (charter flag audit, 2026-07-18): `_maintain_leader_office` runs OUTSIDE the
    `enable_band_affiliation` guard so the office can stand alone — but the desertion branch allocates from
    `_next_band_id`, which was only created INSIDE that guard. With affiliation off the office crashed with
    AttributeError. Every R-84 test world sets enable_band_affiliation=True, so none of them caught it; the
    differential flag audit did, on the 7th flag it tried."""
    w = _world(office=True, gain=0.25, bands=False)
    for _ in range(60):
        w.step()
        assert w.agent_list
    assert isinstance(w._next_band_id, int)
    w.leader_tenure()                                 # diagnostic must not blow up either


def test_a_greedier_levy_draws_more_challenges():
    """The loop Boehm describes: overreach is read off the leader's own material relative to his band, which is
    what `leader_share_frac` inflates ⇒ a greedier levy raises the sanction hazard on the man taking it."""
    def challenges(share):
        w = _world(office=True, gain=0.25, share=share, seed=5)
        n = 0
        for _ in range(150):
            w.step()
            assert w.agent_list
            n += w.challenges_this_step + w.desertions_this_step
        return n
    assert challenges(0.5) > challenges(0.0)
