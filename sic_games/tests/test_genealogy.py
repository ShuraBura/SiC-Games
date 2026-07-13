"""Genealogy logger (opt-in, pure observer) + campaign read-outs. Locks: (1) off by default ⇒ no buffer,
bit-exact; (2) records births + deaths with the enriched GENEA_HEADER schema (status, wealth, RS, cell, society);
(3) stable Mesa unique_id (not id()); (4) observer-only ⇒ enabling it does NOT change the dynamics (same final
population / RNG stream); (5) CSV dump round-trips; (6) flush_genealogy appends + clears (bounded memory);
(7) dynasties()/settlements()/instability()/genetics() read-outs never perturb the model RNG stream.
"""
from __future__ import annotations
import csv
import os

from sic_games.config import KcalEconomyConfig, SubstrateConfig, CarbonConfig
from sic_games.demography import DemographyConfig
from sic_games.phase1_model import TerrainWorld, GENEA_HEADER


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
    # enriched schema: GENEA_HEADER (step,event,uid,mother,father,lineage,band,cred,prowess,wealth,sex,age,
    # parity,n_fathered,x,y,society)
    assert len(GENEA_HEADER) == 17
    for r in log:
        assert len(r) == len(GENEA_HEADER)
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
    assert rows[0] == GENEA_HEADER
    assert len(rows) == n + 1                                 # header + records


def test_flush_genealogy_appends_and_clears(tmp_path):
    """Bounded-memory streaming: flush_genealogy appends buffered rows to CSV and clears the buffer; the header
    is written exactly once and the row count equals the sum of all flushes."""
    w = _world(genea=True)
    path = os.path.join(tmp_path, "genea_stream.csv")
    total = 0
    for _ in range(4):
        for _ in range(15):
            w.step()
        n = w.flush_genealogy(path)
        total += n
        assert w._genealogy_log == []                        # buffer cleared each flush
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    assert rows[0] == GENEA_HEADER                           # header written once, at file creation
    assert len(rows) == total + 1 and total > 0              # one header + every flushed record


def test_campaign_readouts_are_observer_only():
    """dynasties()/settlements()/instability()/genetics() use the dedicated _diag_rng ⇒ interleaving them between
    steps does NOT perturb the model (same final population / unique_ids as an un-probed twin), genome ON."""
    d = _demog(genea=False).model_copy(update=dict(enable_genome=True, genome_loci=32))

    def mk():
        return TerrainWorld(n_agents=80, kcal_cfg=KcalEconomyConfig(), seed=7, game_stream=False,
                            carbon_cfg=CarbonConfig(kappa=1.5),
                            substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                                          contest_exponent=1.5, move_cost_flat=0.0),
                            demography_cfg=d)
    base, probed = mk(), mk()
    for _ in range(60):
        base.step(); probed.step()
        probed.dynasties(); probed.settlements(); probed.instability(); probed.genetics()
    assert len(base.agent_list) == len(probed.agent_list)
    assert sorted(a.unique_id for a in base.agent_list) == sorted(a.unique_id for a in probed.agent_list)
