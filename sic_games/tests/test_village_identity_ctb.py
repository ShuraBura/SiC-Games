"""CTB — VILLAGE IDENTITY: co-residence dissolves band identity (2026-08-12, supervisor decision).

THE MEASURED DEFECT THIS ANSWERS. A 204-person settlement in the campaign stack contains **45 distinct bands**
of ~4-5 co-resident members each. Nothing in the model ever merged co-resident bands: `_maintain_bands`'s
FUSION branch fires only below `band_merge_size` (10), a rescue rule for dying remnants, so bands sit at
equilibrium between merge 10 and split 45 forever. A "village" was a spatial coincidence of strangers, which is
why every fission-cleavage rule tested returned a 1-4 person splinter, and why every splinter founding a
settlement produced the runaway.

THE TIMESCALE IS NOT A NEW NUMBER. `village_identity_months` defaults to 180 = 15 yr = `menarche_months`, the
model's own coming-of-age constant. Identity is inherited at birth, so a merged identity consolidates when the
first cohort born after aggregation reaches adulthood. `test_timescale_is_the_menarche_constant` pins that so a
later edit cannot silently turn it into a free parameter.

THE COUPLING THAT WOULD MAKE THIS THRASH, and the test that would catch it: `_maintain_bands` spatially SPLITS
any band above `band_split_size` (45). A merged village of ~200 would be torn apart on the very step it forms,
leaving the mechanism inert-but-busy — the worst failure mode, because the flag reads ON and the band count
barely moves. `test_a_merged_village_is_exempt_from_band_fission` is the guard, and it is written against the
REAL `_maintain_bands`, not a reimplementation of it.
"""
from types import SimpleNamespace

import pytest

from sic_games.config import CarbonConfig, KcalEconomyConfig, SubstrateConfig
from sic_games.demography import DemographyConfig
from sic_games.group import GroupVector
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world, world_lottery_climate


# ── default state ─────────────────────────────────────────────────────────────────────────────────────────

def test_defaults_off_so_every_prior_run_is_bit_exact():
    d = DemographyConfig()
    assert d.enable_village_identity is False


def test_timescale_is_the_menarche_constant_not_a_free_number():
    """The supervisor chose HALF A GENERATION and the value is sourced from the model, not invented. If someone
    later edits menarche_months, this fails and forces the village timescale to be reconsidered with it."""
    d = DemographyConfig()
    assert d.village_identity_months == d.menarche_months == 180


# ── the merge itself, on a constructed village ────────────────────────────────────────────────────────────

def _fake(site, n_bands, per_band, thr=180, tenure=None):
    """A village of `n_bands` co-resident bands at one settlement site — the measured 45-bands-per-village
    shape in miniature. `tenure` seeds each agent's accrued co-residence."""
    cfg = DemographyConfig(enable_village_identity=True, village_identity_months=thr, settle_radius=2)
    agents = []
    for b in range(n_bands):
        for _ in range(per_band):
            a = SimpleNamespace(pos=site, _group=GroupVector(band_id=b))
            if tenure is not None:
                a._cores_site, a._cores_steps = site, tenure
            agents.append(a)
    f = SimpleNamespace(agent_list=agents, _demog=cfg, _settlement_sites={site: 12},
                        _village_band={}, _village_bands=set(), _nearest_map=None)
    f._nearest_settlement = lambda pos: site if pos == site else None
    return f


def test_below_the_threshold_nothing_merges():
    """THE NEGATIVE. Short-tenure co-residence must leave identity alone — otherwise the mechanism is not a
    timescale at all, it is instant absorption on arrival."""
    f = _fake((50, 50), n_bands=45, per_band=5, tenure=0)
    TerrainWorld._maintain_village_identity(f)
    assert len({a._group.band_id for a in f.agent_list}) == 45, "nothing should merge before the threshold"
    assert f._village_bands == set()


def test_past_the_threshold_the_village_becomes_one_band():
    """THE POSITIVE. 45 bands of 5, all long-resident, become ONE community — the measured defect, fixed."""
    f = _fake((50, 50), n_bands=45, per_band=5, tenure=179)
    TerrainWorld._maintain_village_identity(f)      # 179 -> 180, reaching the threshold on this step
    assert len({a._group.band_id for a in f.agent_list}) == 1, "a long co-resident village is ONE band"
    assert len(f._village_bands) == 1


def test_the_village_id_is_an_EXISTING_band_never_a_minted_one():
    """Deterministic and traceable: the modal band among the qualifying cohort, tie-broken by lowest id."""
    f = _fake((50, 50), n_bands=3, per_band=4, tenure=179)
    for a in f.agent_list[:6]:
        a._group.band_id = 7                         # make 7 the clear modal bloc
    TerrainWorld._maintain_village_identity(f)
    assert {a._group.band_id for a in f.agent_list} == {7}


def test_tenure_resets_on_leaving_so_it_is_per_agent_not_a_global_clock():
    site = (50, 50)
    f = _fake(site, n_bands=2, per_band=3, tenure=179)
    mover = f.agent_list[0]
    mover.pos = (0, 0)                               # walked out of every settlement's radius
    TerrainWorld._maintain_village_identity(f)
    assert mover._cores_steps == 0 and mover._cores_site is None
    assert mover._group.band_id != f.agent_list[-1]._group.band_id, "a leaver must not take the village id"


def test_arriving_at_a_DIFFERENT_site_restarts_the_clock():
    f = _fake((50, 50), n_bands=1, per_band=2, tenure=179)
    a = f.agent_list[0]
    a._cores_site = (10, 10)                         # its tenure was accrued somewhere else
    TerrainWorld._maintain_village_identity(f)
    assert a._cores_steps == 1, "tenure at a new site starts from 1, it is not inherited"


def test_a_dissolved_settlement_does_not_preserve_its_identity():
    """`_village_band` is keyed by site; when the site is gone the entry must go, or a rebuilt settlement on
    the same cell would silently inherit a stale community."""
    site = (50, 50)
    f = _fake(site, n_bands=2, per_band=3, tenure=179)
    TerrainWorld._maintain_village_identity(f)
    assert site in f._village_band
    f._settlement_sites.clear()                      # the village dissolved
    f._nearest_settlement = lambda pos: None
    TerrainWorld._maintain_village_identity(f)
    assert f._village_band == {} and f._village_bands == set()


# ── THE COUPLING: the merged village must survive band fission ────────────────────────────────────────────

def _band_world(village_size, exempt):
    """A single oversized band, run through the REAL `_maintain_bands` fission branch."""
    cfg = DemographyConfig(band_split_size=45, band_merge_size=10, enable_dynamic_bands=False)
    agents = [SimpleNamespace(pos=(50 + (i % 5), 50 + (i // 5) % 5), _group=GroupVector(band_id=3))
              for i in range(village_size)]
    f = SimpleNamespace(agent_list=agents, _demog=cfg, _next_band_id=100, _band_assabiyah={},
                        _band_surplus={}, _band_starv_this_step={}, _village_bands=({3} if exempt else set()))
    return f


def test_a_merged_village_is_exempt_from_band_fission():
    """THE THRASH GUARD. Without the exemption a 200-person village is split back below band_split_size on the
    same step it merges, and the mechanism reads ON while doing nothing. Asserted against the real method."""
    f = _band_world(200, exempt=True)
    TerrainWorld._maintain_bands(f)
    assert len({a._group.band_id for a in f.agent_list}) == 1, "an exempt village band must NOT be split"


def test_the_exemption_does_not_over_reach_a_normal_band_still_fissions():
    """The A/B control: the SAME oversized band, not marked as a village, must still be cut. If this ever
    passes, the exemption has leaked and band-size dynamics are silently disabled everywhere."""
    f = _band_world(200, exempt=False)
    TerrainWorld._maintain_bands(f)
    assert len({a._group.band_id for a in f.agent_list}) > 1, "a non-village band must still fission"


# ── end-to-end: the flag reaches a real run and is not inert ──────────────────────────────────────────────

def _world(**upd):
    k = world_lottery_climate(0, terrain="coastal", climate="temperate")
    generate_world(k, mode="climate")
    d = DemographyConfig(enable_band_affiliation=True, **upd)
    return TerrainWorld(n_agents=60, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, seed=0,
                        substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion"),
                        demography_cfg=d)


def test_the_flag_is_reachable_and_the_state_exists_after_a_step():
    w = _world(enable_village_identity=True)
    w.step()
    assert isinstance(w._village_band, dict) and isinstance(w._village_bands, set)


def test_off_leaves_the_state_untouched():
    w = _world(enable_village_identity=False)
    w.step()
    assert w._village_band == {} and w._village_bands == set()


# ── BUD SITE SEPARATION: daughter catchments must not overlap the parent's ────────────────────────────────

def test_bud_site_separation_defaults_off():
    assert DemographyConfig().enable_bud_site_separation is False


@pytest.mark.parametrize("radius", [1, 2, 3, 4])
def test_the_separation_rule_makes_catchments_DISJOINT(radius):
    """THE PROPERTY, checked as geometry rather than as a magic number. `_maintain_settlements` counts a site's
    pool over the (2·r+1)-wide block centred on it. Two sites whose centres are >= 2·r+1 apart in Chebyshev
    distance share NO cell of those blocks; at the old `r+1` they share a strip 2·r+1 deep. Verified by
    enumerating the blocks, so the invariant is tested, not the arithmetic restated."""
    block = lambda c: {(c[0] + dx, c[1] + dy)
                       for dx in range(-radius, radius + 1) for dy in range(-radius, radius + 1)}
    parent = (50, 50)
    new_sep, old_sep = 2 * radius + 1, radius + 1
    assert not (block(parent) & block((50 + new_sep, 50))), "new rule must give DISJOINT catchments"
    if old_sep < new_sep:
        assert block(parent) & block((50 + old_sep, 50)), "the old rule must OVERLAP (else nothing was wrong)"


def _bud_village(sep_on):
    """A real world with one oversized village that ACTUALLY BUDS, run through the REAL budding method.

    THE FIRST VERSION OF THIS TEST WAS VACUOUS. Synthetic agents built by `_make_agent` have no parents and no
    genome, so `_kin_affinity` returns 0 for every pair and the faction collapsed to the rival alone
    (len < 2 -> `continue`). No daughter was ever sited, in EITHER branch, and the A/B assertions passed
    without executing one line of the siting code they claim to test. Verified by printing the sited distance:
    None / None. Here the rival is given a patriline bloc, so `_kin_affinity` returns 0.25 to the rival and
    0.0 to the head for its members and a real faction forms.
    """
    import numpy as np
    from sic_games.terrain import generate_world, world_lottery_climate
    k = world_lottery_climate(0, terrain="coastal", climate="temperate")
    generate_world(k, mode="climate")
    cfg = DemographyConfig(enable_village_budding=True, enable_band_affiliation=True,
                           village_fission_threshold=20, village_circumscription_gain=0.0,
                           enable_bud_site_separation=sep_on, settle_radius=2)
    w = TerrainWorld(n_agents=4, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, seed=0,
                     substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion"),
                     demography_cfg=cfg)
    aqf = w._s_pot_field()
    y, x = np.unravel_index(int(np.argmax(aqf)), aqf.shape)
    site = (int(x), int(y))
    w._settlement_sites[site] = cfg.settle_release_steps
    for i in range(40):
        a = w._make_agent(sex="male", lh_cfg=None)
        a.pos = site
        a._group.band_id = 0
        a._genome = None                       # force the genealogical fallback, not all-zero genome IBS
        a.cred = 9.0 if i == 0 else (5.0 if i == 1 else 1.0)
        a._lineage = 1 if i in (1, 2, 3, 4) else 2     # rival (i=1) plus three patrilineal kin
        w.agent_list.append(a)
    w._next_band_id = 50
    return w, site


def test_the_daughter_is_sited_FARTHER_AWAY_with_the_rule_on():
    """A/B on the real method: same village, same world, only the flag differs. A daughter MUST be sited in
    both branches (asserted, so this can never silently go vacuous again), and the separation rule must push
    it beyond the hold window."""
    dist = {}
    for on in (False, True):
        w, site = _bud_village(on)
        before = set(w._settlement_sites)
        w._maintain_village_budding()
        new = [s for s in w._settlement_sites if s not in before]
        assert new, f"NO daughter sited with rule={on} — the test would be vacuous"
        dist[on] = max(abs(new[0][0] - site[0]), abs(new[0][1] - site[1]))
    assert dist[True] >= 5, f"rule ON must site the daughter >=5 cells away, got {dist[True]}"
    assert dist[False] >= 3, "the old rule still enforces its own 3-cell floor"
    assert dist[True] > dist[False], (
        f"the rule must push the daughter FARTHER: off={dist[False]} on={dist[True]}")


# ── EXCLUSIVE MEMBERSHIP: spacing becomes emergent, no distance constant ──────────────────────────────────

def test_exclusive_membership_defaults_off():
    assert DemographyConfig().enable_exclusive_village_membership is False


def _two_villages(exclusive, n_shared, sep=2):
    """Two settlements `sep` cells apart with `n_shared` people sitting BETWEEN them, inside both hold
    windows. Under the block sum each village counts all of them; under exclusive membership each person is
    claimed by exactly one."""
    cfg = DemographyConfig(enable_aggregation_sedentism=True, settle_min_pool=40, settle_radius=2,
                           settle_release_steps=12,
                           enable_exclusive_village_membership=exclusive)
    a_site, b_site = (50, 50), (50 + sep, 50)
    mid = ((a_site[0] + b_site[0]) // 2, 50)
    agents = [SimpleNamespace(pos=mid) for _ in range(n_shared)]
    f = SimpleNamespace(agent_list=agents, _demog=cfg,
                        _settlement_sites={a_site: 12, b_site: 12},
                        settle_released_this_step=0, _nearest_map=None)
    f._torus_cheby = lambda ax, ay, bx, by: TerrainWorld._torus_cheby(f, ax, ay, bx, by)
    f._build_nearest_map = lambda: TerrainWorld._build_nearest_map(f)
    f._nearest_settlement = lambda pos: TerrainWorld._nearest_settlement(f, pos)
    return f, a_site, b_site


def test_the_block_sum_lets_TWO_villages_live_off_ONE_pool():
    """THE DEFECT, reproduced. 45 people between two nearby sites keep BOTH alive under the block sum, even
    though there are not 80 people to go round — each village counts all 45. This is the mutual subsidy that
    drove the runaway, and it must still be demonstrable or the fix is aimed at nothing."""
    f, a, b = _two_villages(exclusive=False, n_shared=45)
    TerrainWorld._maintain_settlements(f)
    assert f._settlement_sites.get(a) == 12 and f._settlement_sites.get(b) == 12, \
        "under the block sum both villages should be refreshed by the same 45 people"


def test_exclusive_membership_makes_them_COMPETE_for_the_same_people():
    """THE FIX. The same 45 people, counted once each: one village holds them, the other starves and its
    hysteresis timer starts running down. No distance rule is involved — spacing emerges from competition."""
    f, a, b = _two_villages(exclusive=True, n_shared=45)
    TerrainWorld._maintain_settlements(f)
    timers = sorted([f._settlement_sites.get(a), f._settlement_sites.get(b)])
    assert timers == [11, 12], f"exactly one village should be refreshed and one decaying, got {timers}"


def test_a_village_with_its_OWN_pool_is_untouched_by_the_rule():
    """The over-reach control: a settlement that genuinely holds settle_min_pool people of its own must be
    refreshed whether or not the rule is on. If this fails, the rule is starving legitimate villages."""
    for exclusive in (False, True):
        cfg = DemographyConfig(enable_aggregation_sedentism=True, settle_min_pool=40, settle_radius=2,
                               settle_release_steps=12,
                               enable_exclusive_village_membership=exclusive)
        site = (50, 50)
        f = SimpleNamespace(agent_list=[SimpleNamespace(pos=site) for _ in range(45)], _demog=cfg,
                            _settlement_sites={site: 5}, settle_released_this_step=0, _nearest_map=None)
        f._torus_cheby = lambda ax, ay, bx, by: TerrainWorld._torus_cheby(f, ax, ay, bx, by)
        f._build_nearest_map = lambda: TerrainWorld._build_nearest_map(f)
        f._nearest_settlement = lambda pos: TerrainWorld._nearest_settlement(f, pos)
        TerrainWorld._maintain_settlements(f)
        assert f._settlement_sites[site] == 12, f"a self-sufficient village must hold (exclusive={exclusive})"


def test_no_distance_constant_appears_in_the_exclusive_path():
    """The DIRECTIVE, pinned: spacing must be emergent. The exclusive branch may not consult settle_radius,
    a separation constant, or any hard-coded distance — it counts claimed members and nothing else."""
    import inspect
    src = inspect.getsource(TerrainWorld._maintain_settlements)
    branch = src.split("if exclusive:")[2].split("else:")[0]     # the counting branch inside the site loop
    for forbidden in ("rad", "2 *", "settle_radius", "_minsep"):
        assert forbidden not in branch, f"the exclusive branch must not use {forbidden!r}: {branch!r}"


# ── BUD-FOUNDING BYPASS: budding must not create a settlement out of a pair of people ─────────────────────

def test_bud_requires_occupancy_defaults_off():
    assert DemographyConfig().enable_bud_requires_occupancy is False


def test_a_bud_still_RELOCATES_and_splits_the_band_with_the_rule_on():
    """The bud is not disabled — only its power to conjure a settlement is. The faction must still move and
    still take a new band_id, or this has silently deleted village fission instead of gating its founding."""
    w, site = _bud_village(False)
    w._demog = w._demog.model_copy(update={"enable_bud_requires_occupancy": True})
    before_ids = {a._group.band_id for a in w.agent_list}
    w._maintain_village_budding()
    after_ids = {a._group.band_id for a in w.agent_list}
    assert len(after_ids) > len(before_ids), "the faction must still take a NEW band_id"
    assert any(a.pos != site for a in w.agent_list), "the faction must still RELOCATE off the parent site"
    assert w.bud_events > 0, "the bud event itself must still be counted"


def test_the_bud_founds_NO_site_with_the_rule_on():
    """THE FIX. Budding may no longer bypass `_found_settlements_by_occupancy`'s settle_min_pool gate."""
    w, site = _bud_village(False)
    w._demog = w._demog.model_copy(update={"enable_bud_requires_occupancy": True})
    before = set(w._settlement_sites)
    w._maintain_village_budding()
    assert set(w._settlement_sites) == before, "a bud must not create a settlement site"
    assert w.settle_formed_this_step == 0, "and must not be counted as a formation"


def test_the_bud_DOES_found_a_site_with_the_rule_off():
    """The A/B control, and the reproduction of the defect: with the bypass intact a two-person faction still
    founds a full settlement. If this ever stops failing, the runaway's generator is gone by other means."""
    w, site = _bud_village(False)
    before = set(w._settlement_sites)
    w._maintain_village_budding()
    assert set(w._settlement_sites) != before, "with the bypass ON a bud still founds a site (the defect)"


# ── EMERGENT VILLAGE FOUNDING: one rule, three conditions, no candidate list ──────────────────────────────

def test_emergent_founding_defaults_off():
    assert DemographyConfig().enable_emergent_village_founding is False


def _found_world(spot_cells, agent_cells, existing=(), cr=1, thr=0.3, min_pool=40):
    """A world where founding is evaluated where people ARE. `spot_cells` carry proto-ag/fishing potential."""
    import numpy as np
    aq = np.zeros((100, 100))
    for (x, y) in spot_cells:
        aq[y, x] = 0.9
    cfg = DemographyConfig(enable_emergent_village_founding=True, settle_persist_threshold=thr,
                           settle_min_pool=min_pool, settle_radius=2, settle_catchment_radius=cr,
                           settle_release_steps=12)
    agents = [SimpleNamespace(pos=c) for c in agent_cells]
    f = SimpleNamespace(agent_list=agents, _demog=cfg, _spot_cache=None,
                        _fields=SimpleNamespace(aquatic_food=aq, cultivability=None),
                        _harvest_field=SimpleNamespace(width=100, height=100),
                        _settlement_sites={s: 12 for s in existing}, settle_formed_this_step=0)
    f._s_pot_field = lambda: TerrainWorld._s_pot_field(f)
    return f


def test_a_village_forms_where_people_gather_on_a_fitting_cell():
    """THE POSITIVE. All three conditions met: fitting cell, 45 people, no other village near."""
    site = (50, 50)
    f = _found_world([site], [site] * 45)
    TerrainWorld._found_settlements_by_occupancy(f)
    assert site in f._settlement_sites and f.settle_formed_this_step == 1


def test_condition_1_an_unfitting_cell_never_becomes_a_village():
    """No proto-ag / fishing potential ⇒ no village, however many people stand there."""
    site = (50, 50)
    f = _found_world([], [site] * 200)                 # nobody's cell is storable
    TerrainWorld._found_settlements_by_occupancy(f)
    assert not f._settlement_sites


def test_condition_2_too_few_people_never_becomes_a_village():
    """A roving band that has not reached settle_min_pool stays roving."""
    site = (50, 50)
    f = _found_world([site], [site] * 39)              # one short of the 40 gate
    TerrainWorld._found_settlements_by_occupancy(f)
    assert not f._settlement_sites


def test_condition_3_inside_another_villages_catchment_is_refused():
    """THE SPACING CONDITION, and it is the only one that constrains distance. Chebyshev catchments of radius
    r are disjoint exactly when centres are MORE than 2r apart, so at r=1 a site 2 cells away is refused and
    one 3 cells away is allowed. Anchored to Vita-Finzi & Higgs' ~10 km forager territory, not invented."""
    old = (50, 50)
    for d, expect in ((1, False), (2, False), (3, True)):
        site = (50 + d, 50)
        f = _found_world([site], [site] * 45, existing=[old], cr=1)
        TerrainWorld._found_settlements_by_occupancy(f)
        got = site in f._settlement_sites
        assert got is expect, f"at distance {d} with catchment radius 1, founded={got}, expected {expect}"


def test_the_catchment_rule_scales_with_the_anchored_radius():
    """Not a magic 3: the refusal distance follows settle_catchment_radius, so re-anchoring the territory
    re-anchors the spacing automatically."""
    old = (50, 50)
    for cr in (1, 2, 3):
        for d, expect in ((2 * cr, False), (2 * cr + 1, True)):
            site = (50 + d, 50)
            f = _found_world([site], [site] * 45, existing=[old], cr=cr)
            TerrainWorld._found_settlements_by_occupancy(f)
            assert (site in f._settlement_sites) is expect, f"cr={cr} d={d}"


def test_the_emergent_path_consults_NO_candidate_list_and_NO_separation_constant():
    """THE DIRECTIVE, pinned. The old path ranked storable cells, capped at 40, and min-separated them by
    `aggregation_site_sep` -- which measurement showed was really controlling map coverage. The emergent
    branch must not reach for any of that."""
    import inspect
    src = inspect.getsource(TerrainWorld._found_settlements_by_occupancy)
    branch = src.split("enable_emergent_village_founding", 1)[1].split("return", 1)[0]
    # STRIP COMMENTS FIRST. The branch's own explanation NAMES the things it avoids ("no
    # `aggregation_site_sep`", "stops at 40"), so a raw text search matches the documentation rather than the
    # code and fails a correct implementation. Test what EXECUTES, not what is written about it.
    code = chr(10).join(ln.split("#", 1)[0] for ln in branch.splitlines())
    for forbidden in ("aggregation_site_sep", "cands", "sites =", "40"):
        assert forbidden not in code, f"the emergent branch must not use {forbidden!r}: {code!r}"


def test_two_distant_gatherings_both_found_in_one_step():
    """Villages are not competing for slots in a capped list -- every qualifying place founds."""
    a, b = (20, 20), (60, 60)
    f = _found_world([a, b], [a] * 45 + [b] * 45)
    TerrainWorld._found_settlements_by_occupancy(f)
    assert a in f._settlement_sites and b in f._settlement_sites
    assert f.settle_formed_this_step == 2
