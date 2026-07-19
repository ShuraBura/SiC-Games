"""R-86 / DM-F1 — the LEGITIMACY channel: achieved success reinterpreted as ascribed rank.

CHARTER DECLARATION (MECHANISM_CHARTER §3.1):
  TYPE      C (Conversion) — material → heritable cred, gated on a legitimating belief.
  UNIT      LINEAGE (patriline), competing WITHIN a band. Friedman: "one lineage convinces all the others."
  INVARIANT DEBITED — the sacrifice SPENDS material; and the feast REDISTRIBUTES it to the guests rather than
            destroying it, so material is CONSERVED within the band (the X invariant, asserted below).
  ANCHOR    [Flannery & Marcus 2012 ch.10, VERIFIED] for the mechanism; the rates are [DESIGN], calibrated
            against TARGETS T-6 (Hayden's 75% father-was-leader).

The load-bearing detail is the RATCHET. Friedman's key shift is "from 'They must have PLEASED the nats' to
'They must be DESCENDED FROM higher nats than we are'". A legitimacy stock that decays and must be re-earned by
feasting is the former — still achievement-based, and Flannery says achievement alone "produced individual Big
Men who had no way of bequeathing renown to their offspring". Measured: with a decaying stock, father-was-leader
sat at baseline (59–67% vs 65%) at every gain up to 20. With the ratchet it reaches **76% vs Hayden's 75%**.
"""
import pytest

from sic_games.capacity import NPPCapacityField
from sic_games.config import CarbonConfig, KcalEconomyConfig, SubstrateConfig
from sic_games.demography import DemographyConfig
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world, world_lottery_climate


def _world(n=260, legit=False, feast=0.25, cg=10.0, thr=0.15, seed=0):
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
                         enable_legitimacy=legit, legit_feast_frac=feast,
                         legit_cred_gain=cg, legit_threshold=thr, legit_decay=0.02)
    return TerrainWorld(n_agents=n, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, game_stream=False, seed=seed,
                        carbon_cfg=CarbonConfig(kappa=1.5),
                        substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                                      contest_exponent=1.5, move_cost_flat=0.0),
                        harvest_field=hf, placement_positions=[land[i % len(land)] for i in range(n)],
                        demography_cfg=d)


def test_defaults_off():
    c = DemographyConfig()
    assert c.enable_legitimacy is False and c.legit_feast_frac == 0.0 and c.legit_cred_gain == 0.0


def test_off_is_bit_exact():
    a, b = _world(legit=False, seed=3), _world(legit=False, seed=3)
    for _ in range(40):
        a.step(); b.step()
    assert [x.unique_id for x in a.agent_list] == [x.unique_id for x in b.agent_list]
    assert [round(x.cred, 12) for x in a.agent_list] == [round(x.cred, 12) for x in b.agent_list]
    assert a.legitimacy()["n_lineages"] == 0


def test_feast_conserves_material_within_the_band():
    """THE X INVARIANT. A feast is an EXCHANGE, not a sink — Flannery: the sponsor "could sponsor the most
    prestigious sacrifices AND FEED THE MOST VISITORS". The first implementation DESTROYED the spend, which
    inflated the material Gini by ~0.18 through a pure drain that had nothing to do with legitimacy.
    Checked with `material_decay=0` so the only thing that could move the total is the feast itself."""
    w = _world(legit=True)
    for _ in range(30):
        w.step()
        assert w.agent_list
    before = sum(a.material for a in w.agent_list)
    w._do_legitimacy()                                     # the operator in isolation
    after = sum(a.material for a in w.agent_list)
    assert before > 0.0, "no material accumulated — the test would be vacuous"
    assert after == pytest.approx(before, rel=1e-9), "the feast must conserve material, not destroy it"
    assert w.feast_spend_this_step > 0.0, "no feasting happened — the test would be vacuous"


def test_legitimacy_is_a_bounded_share():
    """Legitimacy is an EMA of a lineage's SHARE of its band's feasting, so it is in [0,1] by construction and
    the threshold is directly interpretable."""
    w = _world(legit=True)
    for _ in range(60):
        w.step()
        assert w.agent_list
    assert w._lineage_legit, "no legitimacy accrued"
    assert all(0.0 <= v <= 1.0 for v in w._lineage_legit.values())


def test_ascription_is_recorded_independently_of_the_cred_gain():
    """Whether a lineage is BELIEVED to descend from the nats is a fact about the society, not about how
    strongly the model converts that belief into cred. Regression: the ratchet was first recorded below the
    `legit_cred_gain <= 0` guard, so the diagnostic read 0 ascribed lineages whenever the gain was 0."""
    w = _world(legit=True, cg=0.0, thr=0.10)
    for _ in range(150):
        w.step()
        assert w.agent_list
    assert w._lineage_ascribed, "ascription must be recorded even with the conversion gain at zero"


def test_ascription_is_a_ratchet():
    """Friedman's shift is from 'they PLEASED the nats' (contingent, re-earned) to 'they are DESCENDED FROM
    higher nats' (ascribed, permanent). Once a lineage crosses, it must not lose the status when its feasting
    share later falls — that reversibility is what kept the mechanism achievement-based and left
    father-was-leader at baseline."""
    w = _world(legit=True, thr=0.10)
    for _ in range(150):
        w.step()
        assert w.agent_list
    seen = set(w._lineage_ascribed)
    assert seen, "nobody was ever ascribed"
    for _ in range(80):
        w.step()
        assert w.agent_list
        assert seen <= w._lineage_ascribed, "ascribed status was revoked — the ratchet leaked"


def test_ascription_raises_cred_above_the_rest():
    """The conversion is the point: an ascribed lineage's members should hold more of the heritable facet."""
    w = _world(legit=True, cg=10.0)
    for _ in range(150):
        w.step()
        assert w.agent_list
    asc = [a.cred for a in w.agent_list if getattr(a, "_lineage", None) in w._lineage_ascribed]
    oth = [a.cred for a in w.agent_list if getattr(a, "_lineage", None) not in w._lineage_ascribed]
    if not oth:
        pytest.skip("everything ascribed at this horizon — saturation, see R-86 open issue")
    assert sum(asc) / len(asc) > sum(oth) / len(oth)


# ── R-87 / DM-F1 stage 2: DELEGITIMATION, the gumsa → gumlao collapse ──────────────────────────────────
# The ratchet alone has no equilibrium (R-86: ascribed_frac_pop 0.70–0.85, nobility becomes universal). Leach's
# Kachin cycle supplies the reverse: hereditary inequality "repeatedly created, lasted for a few generations,
# and then collapsed", driven by ACCUMULATED resentment — "prestige ... only increased their followers'
# resentment and hastened their overthrow". The lag is the mechanism, not a detail (MECHANISM_CHARTER §5).


def _dworld(n=260, alpha=0.05, thr=0.3, seed=0):
    w = _world(n=n, legit=True, feast=0.25, cg=10.0, thr=0.10, seed=seed)
    w._demog = w._demog.model_copy(update=dict(enable_delegitimation=True,
                                               resent_alpha=alpha, resent_threshold=thr))
    return w


def test_delegitimation_defaults_off():
    c = DemographyConfig()
    assert c.enable_delegitimation is False


def test_delegitimation_off_leaves_the_ratchet_monotone():
    """With the reverse disabled, ascription may only grow — the R-86 behaviour must be unchanged."""
    w = _world(legit=True, thr=0.10)
    for _ in range(120):
        w.step()
        assert w.agent_list
    seen = set(w._lineage_ascribed)
    for _ in range(60):
        w.step()
        assert seen <= w._lineage_ascribed


def test_reversion_revokes_ascription():
    """THE POINT: with resentment on, ascription must be LOSABLE — otherwise nobility saturates."""
    w = _dworld(alpha=0.4, thr=0.05)                  # deliberately hair-trigger, to force the event
    ever, reverted = set(), 0
    for _ in range(200):
        w.step()
        assert w.agent_list
        ever |= w._lineage_ascribed
        reverted += w.reversions_this_step
    assert ever, "nobody was ever ascribed — the test would be vacuous"
    assert reverted > 0, "no band ever reverted to gumlao"
    assert w._lineage_ascribed != ever, "ascription was never actually revoked"


def test_resentment_is_bounded_and_resets_on_reversion():
    w = _dworld(alpha=0.4, thr=0.05)
    for _ in range(200):
        w.step()
        assert w.agent_list
        assert all(v >= 0.0 for v in w._band_resentment.values())
        assert all(v < w._demog.resent_threshold + 1e-9 for v in w._band_resentment.values()), \
            "resentment above threshold should have triggered a reversion and reset"


def test_delegitimation_bounds_the_ascribed_fraction():
    """R-86's open problem, closed: the ratchet alone runs to 0.70-0.85 ascribed. The reverse must hold it
    below that, or 'descended from higher nats' stops being a distinction."""
    def frac(deleg):
        w = _dworld(alpha=0.3, thr=0.10) if deleg else _world(legit=True, thr=0.10)
        for _ in range(300):
            w.step()
            assert w.agent_list
        return w.legitimacy()["ascribed_frac_pop"]
    assert frac(True) < frac(False), "delegitimation must reduce the ascribed fraction"


def test_gumsa_state_diagnostic():
    w = _dworld()
    for _ in range(120):
        w.step()
        assert w.agent_list
    g = w.gumsa_state()
    assert g["n_bands"] > 0
    assert 0.0 <= g["frac_gumsa"] <= 1.0
    assert g["max_resentment"] >= g["mean_resentment"] >= 0.0
