"""Demographic diagnostics (R-75) — a standing dashboard, broken down by village/band.

WHY THIS EXISTS. R-74 spent a session chasing a "3.4× orphan excess" that turned out to be R-16's
fertility-pinning working correctly. Four hypotheses died before the answer arrived. All of it would have
been visible at a glance with the orphan-exposure markers sitting next to e₀ on a per-village read-out.
So: measure every demographic marker continuously, per settlement, and let drift announce itself.

Two layers:
  1. UNIT — the marker arithmetic on synthetic populations (fast; always run).
  2. INTEGRATION — drive a real village-forming world and assert the markers land in lit-anchored bands.

BENCHMARKS (see MODEL_SPEC §4.6 / LITERATURE / RESULTS):
  SRB 0.512 male ⇒ sex ratio ≈ 1.05                        (MODEL_SPEC §366)
  IBI ≈ 37 mo, TFR ≈ 8                                     (Aché anchor; realized 37.0/7.9, R-3)
  e₀ 36.5 growing → ~28 stationary at K                    (R-3 / R-16 fertility-pinning)
  village 50–150, bounded stratified tail to ~240          (Bar-Yosef; R-63/R-64)
  orphan exposure: Aché mother-alive 0.98 / father 0.95    (Hill & Hurtado Tab. 13.1)
    — the MODEL must sit ABOVE the Aché orphan rate: it is fertility-pinned at e₀~28 while the Aché were
      growing at e₀ 36.5 (NRR>1). Measured E[mult] 3.28 vs their 1.499 (R-74). That is not a defect.
"""


import math
import pytest

from sic_games.capacity import NPPCapacityField
from sic_games.config import KcalEconomyConfig
from sic_games.demography import DemographyConfig, MONTHS_PER_YEAR
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world, world_lottery_climate

YR = MONTHS_PER_YEAR


# ── unit: marker arithmetic on synthetic populations ─────────────────────────────────────────────

def _world(n=0, **kw):
    k = world_lottery_climate(0, terrain="coastal", climate="temperate")
    f = generate_world(k, mode="climate")
    hf = NPPCapacityField(f, 75000.0, patch=(20, 20, 60), mode="tallavaara", aquatic=True, enable_depletion=True)
    return TerrainWorld(n_agents=n, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, game_stream=False, seed=0,
                        harvest_field=hf, demography_cfg=DemographyConfig(**kw))


class _P:
    """Minimal stand-in for an agent. A plain class (not SimpleNamespace) because real Mesa agents are
    hashable and `_wives` is a set."""
    def __init__(self, sex="male", age_yr=30.0, mother=None, father=None, partner=None):
        self.sex = sex
        self.age = age_yr * YR
        self._mother = mother
        self._father = father
        self._partner = partner
        self._wives = set()
        self.alive = True


def _person(sex="male", age_yr=30.0, mother=None, father=None, partner=None):
    return _P(sex, age_yr, mother, father, partner)


def test_empty_population_is_not_a_fake_zero():
    w = _world()
    assert w.demography() == {"n": 0}          # no invented denominators


def test_sex_ratio_and_age_classes():
    w = _world()
    pop = ([_person("male", 5.0)] * 2 + [_person("female", 5.0)] * 2      # 4 children
           + [_person("male", 30.0)] * 4 + [_person("female", 30.0)] * 2  # 6 adults
           + [_person("female", 70.0)] * 2)                               # 2 elders
    m = w._demog_markers(pop)
    assert m["n"] == 12
    assert m["n_male"] == 6 and m["n_female"] == 6
    assert m["sex_ratio_m_f"] == pytest.approx(1.0)
    assert m["frac_child"] == pytest.approx(4 / 12)
    assert m["frac_adult"] == pytest.approx(6 / 12)
    assert m["frac_elder"] == pytest.approx(2 / 12)
    assert m["dependency_ratio"] == pytest.approx(6 / 6)      # (child+elder)/adult


def test_age_class_boundaries_are_the_anchored_ones():
    """child < 15 = pre-menarche (menarche_months 180); elder >= 60 follows the Aché cause-of-death
    classes (Table 5.1: 0-3 / 4-14 / 15-59 / 60+)."""
    w = _world()
    assert w._AGE_CHILD_YR * YR == DemographyConfig().menarche_months
    just_child = w._demog_markers([_person("male", 14.99)])
    just_adult = w._demog_markers([_person("male", 15.01)])
    assert just_child["frac_child"] == 1.0 and just_adult["frac_adult"] == 1.0
    assert w._demog_markers([_person("male", 60.01)])["frac_elder"] == 1.0


def test_orphan_exposure_matches_table_131_covariates():
    """The risk set is ages 0-9 (Table 13.1's window). Divorce is defined ONLY when both parents live
    (footnote **) — a dead parent is an orphan, not a divorce."""
    w = _world()
    mum, dad = _person("female", 30.0), _person("male", 32.0)
    mum._partner = dad
    intact = _person("male", 3.0, mother=mum, father=dad)
    dead_mum = _person("female", 30.0); dead_mum.alive = False
    orphan_m = _person("female", 3.0, mother=dead_mum, father=dad)
    other = _person("male", 33.0)
    remarried = _person("female", 30.0); remarried._partner = other      # mother re-paired => "divorced"
    divorced_kid = _person("male", 4.0, mother=remarried, father=dad)
    m = w._demog_markers([intact, orphan_m, divorced_kid])
    assert m["n_risk_0_9"] == 3
    assert m["frac_motherless"] == pytest.approx(1 / 3)
    assert m["frac_parents_divorced"] == pytest.approx(1 / 3)
    assert m["frac_fatherless"] == 0.0


def test_risk_set_excludes_unknown_parentage_and_over_9s():
    """Founders have no parent links: they are not in the risk set. Counting them as non-orphans would
    dilute the marker toward 0 early in a run and hide exactly the drift this exists to catch."""
    w = _world()
    founder = _person("male", 2.0)                       # no _mother/_father
    mum = _person("female", 30.0)
    teen = _person("male", 12.0, mother=mum)             # past Table 13.1's 0-9 window
    kid = _person("male", 3.0, mother=mum)
    m = w._demog_markers([founder, teen, kid])
    assert m["n_risk_0_9"] == 1                          # only `kid`


def test_pairing_and_polygyny_markers():
    w = _world()
    husband = _person("male", 35.0)
    w1, w2 = _person("female", 30.0), _person("female", 28.0)
    w1._partner = husband; w2._partner = husband; husband._wives = {w1, w2}
    mono_h = _person("male", 35.0); mono_w = _person("female", 30.0)
    mono_w._partner = mono_h; mono_h._wives = {mono_w}
    single_f = _person("female", 25.0)
    m = w._demog_markers([husband, w1, w2, mono_h, mono_w, single_f])
    assert m["frac_paired_adult_f"] == pytest.approx(3 / 4)
    assert m["mean_wives_married_m"] == pytest.approx(1.5)      # (2 + 1) / 2
    assert m["frac_polygynous_m"] == pytest.approx(0.5)


def test_by_argument_is_validated():
    w = _world()
    with pytest.raises(ValueError):
        w.demography(by="tribe")


# ── integration: drive a real village-forming world ──────────────────────────────────────────────

def _village_world(seed=0, n=500):
    import os
    import sys
    # absolute, derived from __file__ — a relative path would silently depend on pytest's cwd
    _here = os.path.dirname(os.path.abspath(__file__))
    _preset = os.path.normpath(os.path.join(_here, "..", "outputs", "phase1_social_evolution"))
    if _preset not in sys.path:
        sys.path.insert(0, _preset)
    from run_se0_controlled_climate import emergent_village_demog
    from sic_games.config import SubstrateConfig, CarbonConfig
    from sic_games.climate import ClimateField
    from sic_games.demography import ACHE_FOREST_NATURAL as NAT
    k = world_lottery_climate(seed, terrain="coastal", climate="temperate")
    f = generate_world(k, mode="climate")
    hf = ClimateField(NPPCapacityField(f, 75000.0, patch=(20, 20, 60), mode="tallavaara",
                                       aquatic=True, enable_depletion=True), a_seas=0.5)
    hf0 = NPPCapacityField(f, 75000.0, patch=(20, 20, 60), mode="tallavaara", aquatic=True, enable_depletion=True)
    land = [(x, y) for y in range(100) for x in range(100) if f.isWater[y, x] == 0 and hf0.level(x, y) > 0]
    pos = [land[i % len(land)] for i in range(n)]
    d = emergent_village_demog().model_copy(update=dict(
        siler_a1=NAT.a1, siler_b1=NAT.b1, siler_a2=NAT.a2, siler_a3=NAT.a3, siler_b3=NAT.b3,
        enable_cred_status=True, cred_seed_sigma=0.5, cred_inherit_sigma=0.1,
        enable_paternity=True, divorce_rate=0.004,
        enable_marriage_aggregation=True, enable_aggregation_sedentism=True, enable_catchment_ceiling=True,
        enable_settlement_scalar_stress=True, enable_landscape_packing=True, enable_sedentism_fertility=True))
    return TerrainWorld(n_agents=n, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, game_stream=False, seed=seed,
                        carbon_cfg=CarbonConfig(kappa=1.5),
                        substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                                      contest_exponent=1.5, move_cost_flat=0.0),
                        harvest_field=hf, placement_positions=pos, demography_cfg=d)


@pytest.mark.slow
def test_village_demography_is_sane_and_lit_anchored():
    """THE benchmark. Drive a real village-forming world and check every marker against its anchor.
    Bands are deliberately WIDE: this is a drift alarm, not a calibration. A breach means the demography
    moved — go look, don't just widen the band."""
    w = _village_world()
    for _ in range(400):
        w.step()
        assert w.agent_list, "population went extinct"

    whole = w.demography()
    vil = w.demography(by="village")
    villages = {k: m for k, m in vil.items() if k is not None and m["n"] >= 50}
    assert len(villages) >= 3, f"expected a few large villages, got {len(villages)}"

    # SRB 0.512 male (MODEL_SPEC §366) ⇒ ~1.05 at birth; adult male-biased mortality pulls it down a little.
    assert 0.85 <= whole["sex_ratio_m_f"] <= 1.25

    # Growing population ⇒ young. NOT the stationary forager profile; pinned as a drift alarm.
    assert 0.25 <= whole["frac_child"] <= 0.65
    assert 0.4 <= whole["dependency_ratio"] <= 2.0
    assert 8.0 <= whole["median_age_yr"] <= 30.0
    assert whole["frac_elder"] < 0.15

    # Every marker must be finite and in-range in EVERY large village (per-village is the point: a sane
    # whole-population mean can hide a village at 37% motherless).
    for site, m in villages.items():
        assert m["n_male"] + m["n_female"] == m["n"], site
        assert 0.4 <= m["sex_ratio_m_f"] <= 2.5, (site, m["sex_ratio_m_f"])
        assert 0.0 <= m["frac_child"] <= 0.8, (site, m["frac_child"])
        for key in ("frac_motherless", "frac_fatherless", "frac_parents_divorced"):
            v = m[key]
            assert v == v and 0.0 <= v <= 1.0, (site, key, v)     # finite + a proper fraction

    # Orphan exposure. `enable_orphan_mortality` is CANONICAL from 2026-07-17 (R-74), so this figure is
    # POST-selection — motherless infants die and leave the risk set — exactly as Hill & Hurtado's observed
    # 2.0% is. Measured: 1.5% on the plain forager preset (from 4.4% with the channel off — it reproduces
    # their depletion against an anchor it was not fitted to), but ~4.0-4.2% on THIS village stack, i.e.
    # still ~2× the Aché. Two forces pull opposite ways and the band must not hide either: R-16's
    # fertility-pinning (e₀~28 vs the Aché's growing 36.5) pushes exposure UP; the orphan channel culls it
    # DOWN. Drift outside this range means one of them moved — go look.
    assert 0.005 < whole["frac_motherless"] < 0.20, whole["frac_motherless"]


@pytest.mark.slow
def test_grouping_partitions_the_population_exactly():
    """by='village' and by='band' must PARTITION the live population — no agent lost, none double-counted.
    The hinterland (key None) is a real group, not a leak: R-69 found the shock hits the mobile hinterland
    while the storing village rides through, so a village-only view hides half the story."""
    w = _village_world(n=300)
    for _ in range(200):
        w.step()
        assert w.agent_list
    n = len(w.agent_list)
    assert sum(m["n"] for m in w.demography(by="village").values()) == n
    assert sum(m["n"] for m in w.demography(by="band").values()) == n
    assert w.demography()["n"] == n
