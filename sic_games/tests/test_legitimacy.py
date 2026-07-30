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
sat at baseline (59–67% vs 65%) at every gain up to 20. With the ratchet it reaches 76% vs Hayden's 75%.

VALIDATED AND QUALIFIED (R-86v, 2026-07-20). The 76% is a genuine signal — z = 3.1–4.9 against a 2000-shuffle
permutation null, base rate 0.44 (not the ~0.70 that would have made it arithmetic), and the lift statistic
passes a positive control. **But the mechanism supplies CONCENTRATION, not TRANSMISSION:** age-matched (the
comparison pool averages 17.7 yr against leaders at 36.0, so an ungated pool inflates the ratio), legitimacy ON
and OFF give the SAME lift over null, 1.43 vs 1.43. Legitimacy raises the raw fraction by raising the base rate
in step (0.536 vs 0.439) — more of a favoured lineage's members hold office — while the father→son ASSOCIATION
is unchanged and was already supplied by `cred` inheritance. Hayden's own base rate is unknown, so his lift
cannot be computed and the raw-fraction match cannot distinguish the two.
"""
import pytest

from sic_games.capacity import NPPCapacityField
from sic_games.config import CarbonConfig, KcalEconomyConfig, SubstrateConfig
from sic_games.demography import DemographyConfig
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world, world_lottery_climate


def _world(n=260, legit=False, feast=0.25, cg=10.0, thr=0.15, seed=0, feast_every=0):
    """`feast_every=0` keeps the feast firing EVERY step, which is what these unit tests need.

    The model default is 12 (sacrifices happen at the annual gathering, not continuously — see
    `feast_every` in DemographyConfig). These tests step only a handful of times to isolate the legitimacy
    LOGIC — conservation, the ratchet, the cred gain — so under the annual cadence no feast would fire at all
    and every one of them would assert on an empty world. They all failed with "the test would be vacuous",
    which is the right complaint. The CADENCE itself is pinned separately by
    `test_feast_cadence_is_annual_by_default` below, so neither concern goes untested."""
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
                         legit_cred_gain=cg, legit_threshold=thr, legit_decay=0.02,
                         feast_every=feast_every)
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


def test_saturation_trap_is_fixed_by_the_population_fallback():
    """R-89 regression. Before the fix, a band with zero live commoners of its own ('oth' empty) had its
    resentment merely decay every step (`if not asc or not oth: ... continue`) — a ONE-WAY DOOR, since
    ascription only ever grows (R-86) and nothing else could push the band back out. Measured in a real
    4000-step pilot: one band's saturation went population-wide at step 2625 and stayed frozen (ascribed_frac
    pinned at exactly 1.0) for the remaining 34% of the run. Force the exact broken state — one band, every
    present lineage ascribed, given real cred privilege — and confirm resentment still builds, via the
    population-wide fallback reference, instead of freezing at zero."""
    w = _dworld(alpha=0.4, thr=100.0)        # deliberately unreachable: isolates "does resentment BUILD" from
    for _ in range(60):                      # "does it also cross threshold", which test_fully_ascribed_band_
        w.step()                             # can_still_revert covers separately
        assert w.agent_list
    members: dict = {}
    for a in w.agent_list:
        members.setdefault(a._group.band_id, []).append(a)
    bid, ms = max(members.items(), key=lambda kv: len(kv[1]))
    assert len(ms) >= 2, "need a band with more than one agent for the test to mean anything"
    lineages = {getattr(a, "_lineage", None) for a in ms}
    w._lineage_ascribed |= lineages                 # force full saturation of this one band
    for a in ms:
        a.cred = 50.0                                # real privilege: far above the population baseline
    w._band_resentment[bid] = 0.0
    for _ in range(10):
        w._do_delegitimation()
        assert lineages <= w._lineage_ascribed, "threshold=100 must not have been reachable — test setup bug"
    assert w._band_resentment[bid] > 0.0, \
        "resentment never built in a fully-ascribed band — the R-89 saturation trap has returned"


def test_fully_ascribed_band_can_still_revert():
    """R-89: not just that resentment builds, but that it can cross threshold and fire an actual reversion,
    even though the band itself has no live commoners left to compare against."""
    w = _dworld(alpha=0.4, thr=0.05)
    for _ in range(60):
        w.step()
        assert w.agent_list
    members: dict = {}
    for a in w.agent_list:
        members.setdefault(a._group.band_id, []).append(a)
    bid, ms = max(members.items(), key=lambda kv: len(kv[1]))
    lineages = {getattr(a, "_lineage", None) for a in ms}
    w._lineage_ascribed |= lineages
    for a in ms:
        a.cred = 50.0
    w._band_resentment[bid] = 0.0
    reverted = False
    for _ in range(60):
        w._do_delegitimation()
        if not (lineages & w._lineage_ascribed):
            reverted = True
            break
    assert reverted, "a fully-ascribed band never reverted — the saturation trap is still a one-way door"


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


def test_feast_cadence_is_annual_by_default():
    """THE CADENCE, pinned separately from the logic the other tests exercise.

    `legit_feast_frac` used to be spent EVERY STEP. At 0.25 that is ~97% of the durable stock per year:
    measured over 900 steps the sacrifice drain reached 740 BILLION against 1.1 billion of tribute (673:1)
    on a standing stock of 3.2 billion, so the elite was by construction whoever had burned their wealth
    buying rank — which is why noble material lift sat at ~1.0 under every other remedy tried.
    Legitimacy is an EMA of a lineage's SHARE of its band's feasting, and a share is invariant to scaling
    everyone's spend, so the cadence was free for status and decisive for wealth."""
    from sic_games.demography import DemographyConfig
    assert DemographyConfig().feast_every == 12, "sacrifices happen at the annual gathering, not every step"

    w = _world(legit=True, feast=0.25, feast_every=12)
    spends = []
    for _ in range(26):                       # >2 years, so a feast step must fall inside the window
        w.step()
        if not w.agent_list:
            break
        spends.append(w.feast_spend_this_step)
    fired = [i for i, v in enumerate(spends) if v > 0.0]
    assert fired, "no feast fired in two model years"
    assert len(fired) < len(spends) / 2, (
        f"feasting fired on {len(fired)}/{len(spends)} steps — it is meant to be an EVENT, not a bleed")
