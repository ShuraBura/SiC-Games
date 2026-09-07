"""CTB — THE a2 MODULATOR, FACTOR BY FACTOR (R-106, 2026-08-14).

WHY. `_a2_mult` multiplies three live modulators into Siler's Makeham term, and only the PRODUCT was ever
visible. The product runs ~1.4x on a young run and the 5-15 mortality band runs 5x its published anchor, but
nothing could say WHICH factor carried it. Measured once the observers existed, on an identical pair of runs:

    risk_mult     0.630   -- BELOW 1.0. Terrain risk is a net PROTECTIVE factor, because agents self-select
                             into low-risk cells. The filed calibration intends ~1.1 (accidents ~10% of HG
                             deaths, Hill/Hurtado/Walker 2007), so the realised value has the wrong SIGN
                             relative to its anchor. Not a bug in the multiplier -- a consequence of
                             normalising by a GLOBAL mean risk while agents occupy a biased subset of cells.
    density_mult  2.435 -> 1.329 when enable_density_reference is ON
    synergy_mult  1.000 EXACTLY, with mean body condition 1.0000

THE SYNERGY IS NOT DEAD — IT IS SILENCED BY THE WORLD, and that distinction was forced by these tests. My
first version of this file asserted flatly that `enable_nutrition_synergy` is inert. The test failed
immediately: in the smaller, poorer test world mean body condition is 0.49 and the synergy is live at ~1.76.
The mechanism works. It contributes nothing IN THE CAMPAIGN WORLD because agents there eat 2.6x their
requirement (median intake EMA) and `_condition` saturates at its cap.

That is the same root cause as the dead energetic fertility brake, which reads an intake signal that
saturates for the same reason. TWO MECHANISMS, ONE FAILURE: the world feeds everyone above the level at
which either signal carries information. "World-dependent" is a fixable finding; "inert" would have been a
wrong one, and would have sent the next fix at the wrong target.

THE COMPENSATION RESULT THIS ENABLED, which is the important one. The density fix reduces its own target
hazard by 45% and lifts e0 by 5.8 years at 600 steps -- and by 0.09 years at 15,000 steps, because by then
the population has filled the world and STARVATION ABSORBS THE ENTIRE BENEFIT. The model is Malthusian once
the carrying-capacity ceiling is repaired, so equilibrium e0 is set by the food-to-population balance and
NOT by the hazard parameters. No hazard fix can raise it. That is why the factor decomposition mattered:
without it the density fix reads as inert, when in fact it works exactly as designed and is compensated.
"""
import pytest

from sic_games.config import KcalEconomyConfig, SubstrateConfig
from sic_games.demography import DemographyConfig
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world, world_lottery_climate


def _world(**upd):
    k = world_lottery_climate(0, terrain="coastal", climate="temperate")
    generate_world(k, mode="climate")
    d = DemographyConfig(enable_band_affiliation=True, enable_terrain_risk=True,
                         enable_density_disease=True, dens_delta=3.0, dens_rho_half=0.2, **upd)
    return TerrainWorld(n_agents=120, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, seed=0,
                        substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion"),
                        demography_cfg=d)


def test_the_counters_start_empty_and_fill():
    w = _world()
    assert w.a2_n == 0 and w.a2_total_sum == 0.0
    for _ in range(8):
        w.step()
    assert w.a2_n > 0, "the mortality path must have evaluated a2_mult"


def test_each_factor_is_recorded_once_per_evaluation():
    """CONSERVATION. Every factor sum must advance in lockstep with the evaluation count, or a mean computed
    from it is a mean over an unknown subset."""
    w = _world()
    for _ in range(10):
        w.step()
    n = w.a2_n
    for name in ("a2_risk_sum", "a2_dens_sum", "a2_syn_sum", "a2_total_sum", "a2_cond_sum"):
        v = getattr(w, name)
        assert v > 0.0, f"{name} never advanced"
        assert v / n < 10.0, f"{name} mean implausible: {v / n}"


def test_a_disabled_modulator_contributes_exactly_one():
    """NEUTRALITY. A factor whose flag is off must be 1.0 in the decomposition, not 0.0 and not absent —
    otherwise the reported mean silently rescales when a flag is ablated."""
    k = world_lottery_climate(0, terrain="coastal", climate="temperate")
    generate_world(k, mode="climate")
    d = DemographyConfig(enable_band_affiliation=True, enable_terrain_risk=False,
                         enable_density_disease=False, enable_nutrition_synergy=False)
    w = TerrainWorld(n_agents=120, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, seed=0,
                     substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion"),
                     demography_cfg=d)
    for _ in range(8):
        w.step()
    assert w.a2_n > 0
    assert w.a2_risk_sum / w.a2_n == pytest.approx(1.0)
    assert w.a2_dens_sum / w.a2_n == pytest.approx(1.0)
    assert w.a2_syn_sum / w.a2_n == pytest.approx(1.0)
    assert w.a2_total_sum / w.a2_n == pytest.approx(1.0), "all modulators off must give a2_mult == 1"


def test_the_density_factor_responds_to_its_own_flag():
    """LOAD-BEARING. The reference normalisation must move the DENSITY factor and leave the others alone —
    that separation is the whole reason the factors are reported individually."""
    off, on = _world(enable_density_reference=False), _world(enable_density_reference=True)
    for w in (off, on):
        for _ in range(10):
            w.step()
    d_off = off.a2_dens_sum / off.a2_n
    d_on = on.a2_dens_sum / on.a2_n
    assert d_on < d_off, f"the normalisation must lower the density factor: {d_off:.3f} -> {d_on:.3f}"
    r_off, r_on = off.a2_risk_sum / off.a2_n, on.a2_risk_sum / on.a2_n
    assert r_on == pytest.approx(r_off, rel=0.25), "the risk factor must not move with a density flag"


def test_the_synergy_tracks_body_condition_and_is_world_DEPENDENT():
    """A CLAIM OF MINE, CORRECTED BY THIS TEST BEFORE IT SHIPPED.

    I first asserted that `enable_nutrition_synergy` is simply DEAD, having measured `synergy_mult` = 1.000
    and mean condition = 1.0000 on a campaign run. This test failed at once: in the smaller, poorer test
    world mean condition is 0.49 and the synergy is correspondingly live. So the mechanism is not inert —
    it is inert IN THE CAMPAIGN WORLD, because agents there eat 2.6x their requirement (median intake EMA)
    and `_condition` saturates at its cap.

    That is the same root cause as the dead energetic fertility brake, which reads an intake signal that
    saturates for the same reason. Two mechanisms, one failure: the world feeds everyone above the level at
    which either signal carries information. Recording it as world-dependence rather than as inertness is
    the difference between a fixable finding and a wrong one.

    The formula itself is checked directly: synergy = 1 + (mu_max - 1) * (1 - condition).
    """
    w = _world(enable_nutrition_synergy=True, enable_condition=True, mu_max=2.5)
    w.step()
    occ = {a.pos: 1 for a in w.agent_list}
    for cond, want in ((1.0, 1.0), (0.5, 1.75), (0.0, 2.5)):
        a = w.agent_list[0]
        a._condition = cond
        w.a2_n = 0; w.a2_syn_sum = 0.0
        w.a2_risk_sum = w.a2_dens_sum = w.a2_total_sum = w.a2_cond_sum = 0.0
        TerrainWorld._a2_mult(w, a, occ)
        assert w.a2_syn_sum / w.a2_n == pytest.approx(want, rel=1e-6), (
            f"synergy at condition {cond} should be {want}")


def test_the_campaign_world_saturates_condition_and_so_silences_the_synergy():
    """The measurement that matters for attribution, kept separate from the formula check above.

    MEASURED 2026-08-14 on a 600-step campaign (900 founders, coastal temperate): mean body condition
    1.0000 and mean synergy EXACTLY 1.000, so the term contributes nothing to a2 in any scored arm. The
    campaign world is not reproduced here — this test asserts the IMPLICATION, which is what a reader needs:
    at saturated condition the synergy cannot modulate anything, so it cannot be the source of the a2
    inflation, and the search moves to the density and risk factors.
    """
    w = _world(enable_nutrition_synergy=True, enable_condition=True, mu_max=2.5)
    w.step()
    occ = {a.pos: 1 for a in w.agent_list}
    a = w.agent_list[0]
    a._condition = 1.0
    w.a2_n = 0; w.a2_syn_sum = 0.0
    w.a2_risk_sum = w.a2_dens_sum = w.a2_total_sum = w.a2_cond_sum = 0.0
    TerrainWorld._a2_mult(w, a, occ)
    assert w.a2_syn_sum / w.a2_n == pytest.approx(1.0), "saturated condition must silence the synergy"


def test_the_cap_is_counted_when_it_binds():
    """The product is capped at a2_cap; a capped evaluation must still be counted, or the mean is taken over
    a filtered sample that silently excludes the most extreme agents."""
    w = _world(a2_cap=1.0001)          # bind almost immediately
    for _ in range(8):
        w.step()
    assert w.a2_n > 0
    assert w.a2_total_sum / w.a2_n <= 1.0002


def test_the_observers_consume_no_randomness():
    """PURITY. Two worlds from the same seed must stay identical; the decomposition may not perturb the
    stream. The counters are sums over values the model already computed."""
    a, b = _world(), _world()
    for _ in range(12):
        a.step(); b.step()
    assert len(a.agent_list) == len(b.agent_list)
    assert a.a2_n == b.a2_n
    assert a.a2_total_sum == pytest.approx(b.a2_total_sum)
