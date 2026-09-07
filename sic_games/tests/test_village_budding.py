"""Village budding (Bandy 2004): a village past the fission threshold sheds a rival faction, which relocates to a
nearby available storable site and founds a daughter village. Default-OFF ⇒ bit-exact.

CLEAVAGE AXIS CHANGED 2026-07-27 — these tests used to pin a split along the 2nd-largest LINEAGE. Alvard 2009
(literature/AlvardPaper2.pdf), reanalysing Chagnon's Mishimishimaböwei-teri axe fight — a village that had just
fissioned — finds factions assort by GENETIC KINSHIP (~15% of variance), while lineage alone explains ~3% and
becomes non-significant (p=0.281) once kinship is controlled: "lineage identity explained nothing". Lineage-
assorted factions are that paper's LAMALERA contrast case, not the Yanomamö fission pattern. The village now
splits between its two highest-standing men, each keeping those more closely related to him.

The old rule also silently disabled the mechanism: it required a rival lineage bloc of ≥25% (a share with no
[ANCHORED] tag, and absent from Bandy, which never mentions faction size), while a measured 475-person village
held 126 lineages with the largest at 8.2%. Budding never fired at any village size.

Test villages are therefore built as KIN GROUPS (agents sharing a father) rather than lineage labels, since a
shared label is not a kin tie and the cleavage no longer reads labels."""
import pytest

from sic_games.config import KcalEconomyConfig
from sic_games.demography import DemographyConfig
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world, world_lottery_climate
from sic_games.capacity import NPPCapacityField


def _world(**kw):
    k = world_lottery_climate(0, terrain="coastal", climate="temperate")
    f = generate_world(k, mode="climate")
    hf = NPPCapacityField(f, 75000.0, patch=(20, 20, 60), mode="tallavaara", aquatic=True, enable_depletion=True)
    d = DemographyConfig(**kw)
    return TerrainWorld(n_agents=0, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, game_stream=False, seed=0,
                        harvest_field=hf, demography_cfg=d)


def _place(w, cell, n, lineage, band_id):
    out = []
    for _ in range(n):
        a = w._make_agent(sex="male", lh_cfg=None)
        a.pos = cell; a._lineage = lineage; a._group.band_id = band_id
        w.agent_list.append(a); out.append(a)
    return out


def _kin_group(w, cell, n, lineage, band_id, cred=1.0, leader_cred=None):
    """A FACTION: `n` agents sharing one father, so they are siblings (r=0.5 under the genealogical fallback)
    and genuinely closer to each other than to anyone else. The father is an identity only — never added to
    `agent_list`, so he is not a village member. `leader_cred` marks the faction's standing man."""
    dad = w._make_agent(sex="male", lh_cfg=None)          # identity only; deliberately NOT placed in the village
    out = _place(w, cell, n, lineage, band_id)
    for a in out:
        a._father = dad
        a.cred = cred
    if leader_cred is not None:
        out[0].cred = leader_cred
    return out


def _site_with_neighbor(w):
    """A storable cell that has ANOTHER storable cell within [sep+1, R] (so a daughter site exists)."""
    aqf = w._s_pot_field(); persist = w._demog.settle_persist_threshold
    sep = w._demog.settle_radius; R = w._demog.village_bud_search_radius
    storable = [(x, y) for y in range(100) for x in range(100) if aqf[y, x] >= persist]
    S = set(storable)
    for (sx, sy) in storable:
        for (x, y) in storable:
            if sep + 1 <= max(abs(x - sx), abs(y - sy)) <= R:
                return (sx, sy)
    return None


def test_village_budding_defaults_off():
    c = DemographyConfig()
    assert c.enable_village_budding is False
    assert c.village_fission_threshold == 170
    assert c.village_bud_min_faction == 0.0      # the 25% rival-bloc rule was unanchored and blocked budding
    assert c.village_circumscription_gain == 0.6


def test_budding_sheds_rival_kin_faction_to_new_site():
    """The village splits between its two standing men, each keeping his own kin (Alvard 2009)."""
    # circ_gain=0 isolates the fires-behaviour from the circumscription threshold-rise (tested separately)
    w = _world(enable_village_budding=True, enable_band_affiliation=True, village_fission_threshold=20,
               village_circumscription_gain=0.0)
    site = _site_with_neighbor(w)
    assert site is not None, "coastal world should have a storable site with a storable neighbor in reach"
    maj = _kin_group(w, site, 20, 1, 0, cred=1.0, leader_cred=9.0)   # incumbent headman + his kin
    riv = _kin_group(w, site, 10, 2, 0, cred=1.0, leader_cred=5.0)   # rival headman + his kin
    w._settlement_sites[site] = w._demog.settle_release_steps
    w._next_band_id = 7                       # invariant: the id counter is above all live band_ids (as in a real run)
    n0 = len(w._settlement_sites)
    w._maintain_village_budding()
    riv_bids = set(a._group.band_id for a in riv)
    assert len(riv_bids) == 1 and 0 not in riv_bids, "rival faction takes ONE new band_id"
    assert all(a.pos != site for a in riv), "rival faction relocates off the parent site"
    assert all(a._group.band_id == 0 and a.pos == site for a in maj), "majority stays put"
    assert len(w._settlement_sites) > n0, "a daughter settlement is founded"


def test_circumscription_raises_threshold_and_blocks_small_bud():
    """Bandy circumscription: a steep relocation cost lifts the effective fission threshold above the village size →
    no bud (the village would grow + stratify instead). Same village that fissions at circ_gain=0."""
    w = _world(enable_village_budding=True, enable_band_affiliation=True, village_fission_threshold=20,
               village_circumscription_gain=5.0)            # eff_thr = 20·(1+5·d/8) ≫ 30 at any reachable d ≥ 3
    site = _site_with_neighbor(w)
    _kin_group(w, site, 20, 1, 0, cred=1.0, leader_cred=9.0)
    riv = _kin_group(w, site, 10, 2, 0, cred=1.0, leader_cred=5.0)
    w._settlement_sites[site] = w._demog.settle_release_steps
    w._next_band_id = 7
    n0 = len(w._settlement_sites)
    w._maintain_village_budding()
    assert all(a._group.band_id == 0 for a in riv), "circumscription cost should block this small fission"
    assert len(w._settlement_sites) == n0


def test_single_kin_group_village_does_not_bud():
    """One kin group = no cleavage: every member is equidistant between the two standing men, so the only
    'faction' is the rival himself, and one man is not a daughter village."""
    w = _world(enable_village_budding=True, enable_band_affiliation=True, village_fission_threshold=20)
    site = _site_with_neighbor(w)
    riv = _kin_group(w, site, 30, 1, 0, cred=1.0, leader_cred=9.0)   # ONE kin group -> no cleavage line
    w._settlement_sites[site] = w._demog.settle_release_steps
    n0 = len(w._settlement_sites)
    w._maintain_village_budding()
    assert len(w._settlement_sites) == n0 and all(a._group.band_id == 0 for a in riv)


def test_stratified_village_does_not_bud():
    """Bandy: integrative institutions (stratification) suppress fission."""
    w = _world(enable_village_budding=True, enable_band_affiliation=True, village_fission_threshold=20)
    site = _site_with_neighbor(w)
    _kin_group(w, site, 20, 1, 0, cred=1.0, leader_cred=9.0)
    riv = _kin_group(w, site, 10, 2, 0, cred=1.0, leader_cred=5.0)
    w._band_society[0] = "stratified_chiefdom"     # the village's band is stratified
    w._settlement_sites[site] = w._demog.settle_release_steps
    n0 = len(w._settlement_sites)
    w._maintain_village_budding()
    assert len(w._settlement_sites) == n0 and all(a._group.band_id == 0 for a in riv)


def test_below_threshold_does_not_bud():
    w = _world(enable_village_budding=True, enable_band_affiliation=True, village_fission_threshold=50)
    site = _site_with_neighbor(w)
    _kin_group(w, site, 20, 1, 0, cred=1.0, leader_cred=9.0)
    riv = _kin_group(w, site, 10, 2, 0, cred=1.0, leader_cred=5.0)   # 30 ≤ 50 threshold
    w._settlement_sites[site] = w._demog.settle_release_steps
    w._maintain_village_budding()
    assert all(a._group.band_id == 0 for a in riv)
