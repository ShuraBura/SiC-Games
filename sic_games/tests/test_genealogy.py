"""Stage 2 — genealogy logger (opt-in, pure observer). Locks: (1) off by default ⇒ no buffer, bit-exact;
(2) records births + deaths with the (step, event, uid, mother, father, lineage, band_id, cred) schema;
(3) stable Mesa unique_id (not id()); (4) observer-only ⇒ enabling it does NOT change the dynamics (same
final population / RNG stream); (5) CSV dump round-trips.
"""
from __future__ import annotations
import csv
import os

from sic_games.config import KcalEconomyConfig, SubstrateConfig, CarbonConfig
from sic_games.demography import DemographyConfig
from sic_games.phase1_model import TerrainWorld


def _demog(genea: bool) -> DemographyConfig:
    return DemographyConfig(
        enable_paternity=True, mate_choice_strength=4.0, patriline_weight=0.5, lineage_reversion=0.1,
        enable_cred_status=True, cred_seed_sigma=0.5, cred_inherit_sigma=0.1,
        enable_band_affiliation=True, enable_dynamic_bands=True,
        enable_genealogy_log=genea)


def _world(genea: bool, seed=3, n=80):
    return TerrainWorld(n_agents=n, kcal_cfg=KcalEconomyConfig(), seed=seed, game_stream=False,
                        carbon_cfg=CarbonConfig(kappa=1.5),
                        substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                                      contest_exponent=1.5, move_cost_flat=0.0),
                        demography_cfg=_demog(genea))


def test_genealogy_off_by_default():
    assert DemographyConfig().enable_genealogy_log is False
    w = _world(genea=False)
    for _ in range(20):
        w.step()
    assert w._genealogy_log is None                            # no buffer allocated when off


def test_genealogy_records_births_and_deaths_with_schema():
    w = _world(genea=True)
    for _ in range(60):
        w.step()
    log = w._genealogy_log
    assert log is not None and len(log) > 0
    events = {r[1] for r in log}
    assert "birth" in events and "death" in events            # both kinds recorded
    # schema: (step, event, uid, mother_uid, father_uid, lineage, band_id, cred)
    for r in log:
        assert len(r) == 8
        assert isinstance(r[0], int) and r[1] in ("birth", "death") and isinstance(r[2], int)
    # a birth's uid should be a valid Mesa unique_id (int, monotonic), and mother_uid set (≥0) for IBI births
    births = [r for r in log if r[1] == "birth"]
    assert any(r[3] >= 0 for r in births)                     # at least some births carry a mother uid


def test_genealogy_is_observer_only_bit_exact():
    # enabling the logger must NOT perturb the dynamics (no RNG touch, write-after-step): same final population.
    off = _world(genea=False, seed=11)
    on = _world(genea=True, seed=11)
    for _ in range(80):
        off.step(); on.step()
    assert len(off.agent_list) == len(on.agent_list)
    assert sorted(a.unique_id for a in off.agent_list) == sorted(a.unique_id for a in on.agent_list)


def test_genealogy_dump_csv_roundtrips(tmp_path):
    w = _world(genea=True)
    for _ in range(40):
        w.step()
    path = os.path.join(tmp_path, "genea.csv")
    n = w.dump_genealogy(path)
    assert n == len(w._genealogy_log) > 0
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    assert rows[0] == ["step", "event", "uid", "mother_uid", "father_uid", "lineage", "band_id", "cred"]
    assert len(rows) == n + 1                                 # header + records
