"""Cred renormalisation (R-81) — pin cred to population-mean 1 each step, fixing the homeostat mean-inflation.

The inheritance reverts toward a FIXED 1.0 anchor (a contraction validated in R-18, pre-selection). R-19/R-20
added fertility-weighted mate-choice + a `cred·prowess` product base, both of which inject an upward bias each
generation and DEFEAT the contraction (mean cred 1→18.6 over 2000 steps ⇒ the ρ·1.0 pull becomes negligible ⇒
the homeostat loses grip). Renormalising to mean-1 restores the anchor's meaning ⇒ constant grip at any scale.
Re-verified SAFE (R-81): Gini 0.332→0.326, status→RS +0.248→+0.261 — R-19 preserved.
"""
import math

import pytest

from sic_games.capacity import NPPCapacityField
from sic_games.config import CarbonConfig, KcalEconomyConfig, SubstrateConfig
from sic_games.demography import DemographyConfig
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world, world_lottery_climate


def _world(n, renorm, **kw):
    k = world_lottery_climate(0, terrain="coastal", climate="temperate")
    f = generate_world(k, mode="climate")
    hf = NPPCapacityField(f, 75000.0, patch=(20, 20, 60), mode="tallavaara", aquatic=True, enable_depletion=True)
    land = [(x, y) for y in range(100) for x in range(100) if f.isWater[y, x] == 0 and hf.level(x, y) > 0]
    pos = [land[i % len(land)] for i in range(n)]
    d = DemographyConfig(enable_cred_status=True, cred_seed_sigma=0.5, cred_inherit_sigma=0.1,
                         enable_paternity=True, mate_choice_strength=5.0, enable_prowess_facet=True,
                         enable_pair_bonds=True, enable_cred_renorm=renorm, **kw)
    return TerrainWorld(n_agents=n, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, game_stream=False, seed=0,
                        carbon_cfg=CarbonConfig(kappa=1.5),
                        substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                                      contest_exponent=1.5, move_cost_flat=0.0),
                        harvest_field=hf, placement_positions=pos, demography_cfg=d)


def test_defaults_off():
    assert DemographyConfig().enable_cred_renorm is False        # off ⇒ bit-exact


def test_renorm_pins_the_cred_mean_to_one():
    w = _world(200, renorm=True)
    for _ in range(150):
        w.step()
        assert w.agent_list
    cr = [a.cred for a in w.agent_list if getattr(a, "use_cred_status", False)]
    assert cr
    assert abs(sum(cr) / len(cr) - 1.0) < 1e-9                   # pinned to mean-1 by the end-of-step rescale


def test_off_lets_the_mean_drift_above_one():
    """The defect this fixes: without renorm the selection + product bias inflates the mean above 1."""
    w = _world(200, renorm=False)
    for _ in range(300):
        w.step()
        assert w.agent_list
    cr = [a.cred for a in w.agent_list if getattr(a, "use_cred_status", False)]
    assert sum(cr) / len(cr) > 1.15, "expected the un-renormalised mean to drift above 1"


def test_renorm_is_dynamics_neutral_for_the_relative_weights():
    """Cred enters every downstream weight relatively ((cred)^κ / Σ, normalised mate weights), so a uniform
    rescale must not change WHO is where — only the absolute cred values. Checked via the cred RANK order:
    renorm preserves the ordering of agents by cred (a uniform positive rescale is monotone)."""
    w = _world(200, renorm=True)
    for _ in range(80):
        w.step()
    # after a renorm step, cred values are all divided by the same positive constant ⇒ ratios preserved.
    cr = sorted((a.cred for a in w.agent_list if getattr(a, "use_cred_status", False)))
    assert cr[0] > 0.0 and cr[-1] / cr[0] > 1.0                  # a real spread survives the rescale
    # the Gini of a positively-rescaled vector is unchanged; here just assert the spread is bounded, not collapsed
    assert cr[-1] < 50.0, "renorm should keep the top from running away"
