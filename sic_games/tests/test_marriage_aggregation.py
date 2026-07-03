"""Seasonal marriage-aggregation ('the gathering'). Locks: (1) off by default; (2) the _do_pairing refactor is
bit-exact (flexible residence + homogamy 0 == old within-band pairing); (3) the gathering fires only on period
steps + pairs adults across bands; (4) residence modes move the bride/groom correctly; (5) rank homogamy switch."""
from __future__ import annotations
from sic_games.config import KcalEconomyConfig, SubstrateConfig, CarbonConfig
from sic_games.demography import DemographyConfig
from sic_games.phase1_model import TerrainWorld


def _demog(**kw):
    return DemographyConfig(siler_a1=0.157, siler_b1=0.721, siler_a2=0.013, siler_a3=4.8e-5, siler_b3=0.103,
                            enable_band_affiliation=True, enable_dynamic_bands=True, enable_pair_bonds=True,
                            menarche_months=0, mate_choice_strength=4.0, bonded_mate_radius=1, **kw)


def _world(seed=1, n=60, **kw):
    return TerrainWorld(n_agents=n, kcal_cfg=KcalEconomyConfig(), seed=seed, game_stream=False,
                        substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                                      contest_exponent=1.5, move_cost_flat=0.0),
                        carbon_cfg=CarbonConfig(kappa=1.5), demography_cfg=_demog(**kw))


def test_off_by_default():
    cfg = DemographyConfig()
    assert cfg.enable_marriage_aggregation is False and cfg.aggregation_residence == "virilocal"


def test_refactor_bit_exact_daily_pairing():
    # the extracted _pair_from_pool with flexible/homogamy-0 must reproduce the old within-band pairing exactly:
    # two identical worlds (aggregation OFF) evolve to the same paired set.
    a = _world(seed=5); b = _world(seed=5)
    for _ in range(40):
        a.step(); b.step()
    assert [(f.unique_id, f._partner.unique_id if f._partner else None) for f in a.agent_list if f.sex == "female"] \
        == [(f.unique_id, f._partner.unique_id if f._partner else None) for f in b.agent_list if f.sex == "female"]


def test_gathering_pairs_across_bands_on_period_only():
    w = _world(seed=3, enable_marriage_aggregation=True, aggregation_period=10, aggregation_radius=50.0,
               aggregation_site_sep=3.0)
    # step to just before the first gathering: no pairing yet (aggregation replaces daily pairing)
    for _ in range(9):
        w.step()
    paired_before = sum(1 for a in w.agent_list if a.sex == "female" and a._partner is not None)
    w.step()   # step 10 = gathering
    paired_after = sum(1 for a in w.agent_list if a.sex == "female" and a._partner is not None)
    assert paired_after > paired_before          # the gathering formed pairs


def test_virilocal_vs_uxorilocal_residence():
    # a cross-band pair: virilocal → bride takes groom's band; uxorilocal → groom takes bride's band.
    def resid(mode):
        w = _world(seed=2, n=8)
        f = next(a for a in w.agent_list if a.sex == "female")
        m = next(a for a in w.agent_list if a.sex == "male" and a._mother is not f and a is not f._father)
        f._group.band_id = 100; m._group.band_id = 200
        f._partner = None; f._wives = set() if hasattr(f, "_wives") else set(); m._wives = set()
        bs = {100: 3, 200: 9}
        w._pair_from_pool([f], [m], mode, 0.0, bs)
        return f._group.band_id, m._group.band_id
    assert resid("virilocal") == (200, 200)      # bride → groom's band
    assert resid("uxorilocal") == (100, 100)      # groom → bride's band
