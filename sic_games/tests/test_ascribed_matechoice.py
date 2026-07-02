"""Ascribed-status mate-choice (society-gated). Locks: (1) off by default; (2) flag off / egalitarian ⇒
prowess-only, bit-exact; (3) the society gate (egalitarian 0 / complex 0.5 / stratified 1.0); (4) when ON in a
stratified band, high-CRED males win more matings than prowess-alone would give.
"""
from __future__ import annotations
import random

from sic_games.config import KcalEconomyConfig, SubstrateConfig, CarbonConfig
from sic_games.demography import DemographyConfig, MATE_ASCRIBED_WEIGHT, mate_ascribed_weight
from sic_games.phase1_model import TerrainWorld


def test_ascribed_mate_choice_off_by_default():
    cfg = DemographyConfig()
    assert cfg.enable_ascribed_mate_choice is False and cfg.ascribed_mate_strength == 0.0


def test_society_gate_ladder():
    assert mate_ascribed_weight("egalitarian_forager") == 0.0
    assert mate_ascribed_weight("complex_forager") == 0.5
    assert mate_ascribed_weight("stratified_chiefdom") == 1.0
    assert mate_ascribed_weight(None) == 0.0                       # unclassified → egalitarian (conservative)
    assert MATE_ASCRIBED_WEIGHT["stratified_chiefdom"] == 1.0


def _pairing_world(asc_on, asc_a=1.0, seed=1, n=40):
    # a dense single cell of unpaired adults so _do_pairing runs its weighted choice; band affiliation on so a
    # society type can gate the weight.
    positions = [(12, 12)] * n
    demog = DemographyConfig(enable_band_affiliation=True, enable_dynamic_bands=True, menarche_months=0,
                             mate_choice_strength=4.0, bonded_mate_radius=1, enable_pair_bonds=True,
                             enable_ascribed_mate_choice=asc_on, ascribed_mate_strength=asc_a)
    w = TerrainWorld(n_agents=n, kcal_cfg=KcalEconomyConfig(), seed=seed, game_stream=False,
                     carbon_cfg=CarbonConfig(kappa=1.5),
                     substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                                   contest_exponent=1.5, move_cost_flat=1e12),
                     placement_positions=positions,
                     demography_cfg=demog)
    # force one band_id + a controlled cred/prowess split among males
    for a in w.agent_list:
        a._group.band_id = 0
        a._partner = None; a._wives = set()
    return w


def test_flag_off_is_prowess_only_bitexact():
    # off vs on-but-egalitarian must give the SAME pairings (both collapse to prowess-only) for the same seed.
    def pairings(asc_on, society):
        w = _pairing_world(asc_on=asc_on, seed=7)
        w._band_society[0] = society
        # deterministic status: give every male a distinct prowess and an ANTI-correlated cred (so cred WOULD change
        # the outcome if it entered) — under prowess-only they must match regardless of cred.
        males = [a for a in w.agent_list if a.sex == "male"]
        for i, m in enumerate(males):
            m.prowess = 1.0 + 0.1 * i; m.cred = 5.0 - 0.1 * i
        w._do_pairing()
        return [(f.unique_id, (f._partner.unique_id if f._partner else None)) for f in w.agent_list if f.sex == "female"]
    off = pairings(asc_on=False, society="stratified_chiefdom")
    egal = pairings(asc_on=True, society="egalitarian_forager")     # gate 0 ⇒ cred^0 ⇒ prowess-only
    assert off == egal                                              # bit-exact: gate 0 == flag off


def test_ascribed_raises_high_cred_mating_in_stratified():
    # In a STRATIFIED band with the flag on, a high-cred / low-prowess male should win MORE matings than under
    # prowess-only (cred now buys marriage). Compare a stark cred outlier's wife count across arms, many trials.
    def wives_of_cred_outlier(asc_on):
        total = 0
        for seed in range(12):
            w = _pairing_world(asc_on=asc_on, seed=seed)
            w._band_society[0] = "stratified_chiefdom"
            males = [a for a in w.agent_list if a.sex == "male"]
            for m in males:                                        # everyone modest prowess...
                m.prowess = 1.0; m.cred = 1.0
            if males:
                males[0].cred = 20.0                               # ...one stark high-CRED (low-prowess-parity) male
            w._do_pairing()
            total += len(males[0]._wives) if males else 0
        return total
    on = wives_of_cred_outlier(asc_on=True)
    off = wives_of_cred_outlier(asc_on=False)
    assert on > off                                                # ascribed status buys marriages when stratified
