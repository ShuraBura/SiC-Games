"""CTB — THE PER-BIOME TWO-STREAM ECONOMY (`enable_biome_meat_frac`, `enable_biome_meat_cv`).

WHAT WAS WIRED, AND WHAT WAS ALREADY LIVE. The two-stream split itself has run in every campaign since the
Carbon build: the cell pool `S` divides into a forage stream at a literal κ=0 and a meat stream at the substrate
κ, band-pooled and Cred-weighted. That part was never dead. What was scalar is the SPLIT ITSELF — one
`game_meat_frac` (0.55, the forest value) for every biome, and one `game_meat_cv` for every biome. Addendum 36
then measured that `game_kcal` reaches nothing either, so a campaign carried NO biome signal in its diet at all.

These flags read the cell's biome from dicts that are already anchored. **Neither introduces a new number.**
    `enable_biome_meat_frac` → `terrain.MEAT_FRAC`  (Cordain 2000 Table 2, terrestrial-renormalized)
    `enable_biome_meat_cv`   → `terrain.MEAT_CV`    (cchunts day-to-day CV; Hawkes 1991 for the Hadza)

THE FALLBACKS DIFFER BY DICT, AND THAT IS THE POINT, not an inconsistency. The two dicts record different
reasons for an absent biome:
  - `MEAT_FRAC` omits WETLAND on purpose — terrain.py calls it "a gap, not a measured zero", because 0.0 would
    assert that wetland foragers eat no meat. An absent biome therefore takes the configured SCALAR.
  - `MEAT_CV` omits GRASS/MOUNTAIN/WETLAND for want of a calibration people, and terrain.py's own rule for that
    case is `HUNT_CV` = 2.11 — a MEASURED biome-invariant value, not a filler. An absent biome takes it.
Both fallbacks are pinned below so a later "tidy-up" to 0.0 fails instead of quietly asserting two things no
source supports.

ENERGY CONSERVATION IS THE ONE THING THAT CAN BREAK SILENTLY. The meat pool takes `mf_c · S` and the forage
stream takes `(1 − mf_c) · S`. If the two ever read different fractions, the cell creates or destroys kcal with
no error anywhere. `test_energy_is_conserved_per_cell` is the guard.
"""
import random

import numpy as np
import pytest

from sic_games import phase1_model, runspec
from sic_games.capacity import NPPCapacityField
from sic_games.config import CarbonConfig, KcalEconomyConfig, SubstrateConfig
from sic_games.demography import DemographyConfig
from sic_games.phase1_model import TerrainWorld, seed_band_positions_spread
from sic_games.terrain import (BIOME_FOREST, BIOME_GRASS, BIOME_MOUNTAIN, BIOME_SAVANNA, BIOME_WETLAND,
                               HUNT_CV, MEAT_CV, MEAT_FRAC, generate_world, world_lottery_climate)

BURN, SEED, NAG, STEPS = 75000.0, 0, 200, 8
PATCH = (20, 20, 60)
_REPO = __import__("pathlib").Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def demog():
    spec = runspec.load(_REPO / "config" / "runs" / "full_campaign.toml", seed=SEED)
    return runspec.build(spec, "DemographyConfig")


def build(demog, **update):
    k = world_lottery_climate(SEED, terrain="coastal", climate="savanna")   # a world with several biomes
    f = generate_world(k, mode="climate")
    hf = NPPCapacityField(f, BURN, patch=PATCH, mode="tallavaara", aquatic=True, enable_depletion=True)
    pos = seed_band_positions_spread(f, NAG, hours_per_step=100.0, burn=BURN, band_size=25,
                                     rng=random.Random(SEED))
    return TerrainWorld(n_agents=NAG, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, game_stream=False, seed=SEED,
                        carbon_cfg=CarbonConfig(kappa=1.5),
                        substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                                      contest_exponent=1.5, move_cost_flat=0.0),
                        harvest_field=hf, placement_positions=pos,
                        demography_cfg=demog.model_copy(update=update) if update else demog)


def trajectory(w):
    traj = []
    for _ in range(STEPS):
        w.step()
        traj.append(sum(1 for a in w.agent_list if a.alive))
    return traj


# ── LIVENESS runs on a LIVING population (CTB "check the run is alive") ─────────────────────────────────────
# The savanna world above collapses to ~63 in 8 steps, and a collapsed population is insensitive to everything,
# so a knife-edge trajectory equality there is noise, not a verdict. This surfaced on 2026-09-01 when
# `enable_metabolic_downreg` (a validated, unrelated mechanism) tipped that equality from (65,63) to (63,63).
# `meat_frac`/`meat_cv` ARE live — they change a SURVIVING run — so the liveness tests use a world that lives.
_LIVE_NAG, _LIVE_STEPS, _LIVE_PATCH = 600, 25, (30, 30, 80)


def _live_build(demog, **update):
    k = world_lottery_climate(SEED, terrain="coastal", climate="temperate")   # a world that survives 25 steps
    f = generate_world(k, mode="climate")
    hf = NPPCapacityField(f, BURN, patch=_LIVE_PATCH, mode="tallavaara", aquatic=True, enable_depletion=True)
    pos = seed_band_positions_spread(f, _LIVE_NAG, hours_per_step=100.0, burn=BURN, band_size=25,
                                     rng=random.Random(SEED))
    return TerrainWorld(n_agents=_LIVE_NAG, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, game_stream=False,
                        seed=SEED, carbon_cfg=CarbonConfig(kappa=1.5),
                        substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                                      contest_exponent=1.5, move_cost_flat=0.0),
                        harvest_field=hf, placement_positions=pos,
                        demography_cfg=demog.model_copy(update=update) if update else demog)


def _live_trajectory(w):
    traj = []
    for _ in range(_LIVE_STEPS):
        w.step()
        traj.append(sum(1 for a in w.agent_list if a.alive))
    assert traj[-1] > 200, f"liveness world collapsed (final pop {traj[-1]}) -- a dead run tests nothing (CTB)"
    return traj


# ── default state: every prior run stays bit-exact ────────────────────────────────────────────────────────

def test_both_flags_default_off_in_the_config_class():
    """Charter §12: a new mechanism defaults OFF in the class, so a harness that does not know about it keeps
    its old behaviour. The CAMPAIGN default is separate and lives in config/mechanisms.toml."""
    d = DemographyConfig()
    assert d.enable_biome_meat_frac is False
    assert d.enable_biome_meat_cv is False


def test_flags_off_reproduces_the_scalar_run_bit_exactly(demog):
    off = dict(enable_biome_meat_frac=False, enable_biome_meat_cv=False)
    assert trajectory(build(demog, **off)) == trajectory(build(demog, **off))


def test_turning_the_flags_on_changes_the_run(demog):
    """THE POSITIVE CONTROL for this mechanism. A flag that is on and changes nothing is the failure mode the
    ON-but-dead gate exists for (Charter §12), and it produced 3 of battery 7's 6 "inert" verdicts."""
    off = _live_trajectory(_live_build(demog, enable_biome_meat_frac=False, enable_biome_meat_cv=False))
    on = _live_trajectory(_live_build(demog, enable_biome_meat_frac=True, enable_biome_meat_cv=True))
    assert off != on, "both flags on and the trajectory is unchanged — the wiring does not reach the harvest"


@pytest.mark.parametrize("flag", ["enable_biome_meat_frac", "enable_biome_meat_cv"])
def test_each_flag_is_live_on_its_own(demog, flag):
    base = dict(enable_biome_meat_frac=False, enable_biome_meat_cv=False)
    assert _live_trajectory(_live_build(demog, **base)) != _live_trajectory(_live_build(demog, **{**base, flag: True}))


# ── the fields carry the anchored values, and the fallbacks are the documented ones ───────────────────────

def test_meat_frac_field_reads_cordain_where_cordain_has_a_value(demog):
    w = build(demog, enable_biome_meat_frac=True)
    fld, biome = w._biome_meat_frac_field(), w._fields.biome
    for b in (BIOME_FOREST, BIOME_SAVANNA, BIOME_GRASS, BIOME_MOUNTAIN):
        m = biome == b
        if m.any():
            assert np.allclose(fld[m], MEAT_FRAC[b]), f"biome {b} does not carry MEAT_FRAC {MEAT_FRAC[b]}"


def test_wetland_takes_the_SCALAR_not_zero(demog):
    """`MEAT_FRAC` omits wetland deliberately — "a gap, not a measured zero". A 0.0 here would assert that
    wetland foragers eat no meat, which no source says."""
    w = build(demog, enable_biome_meat_frac=True)
    m = w._fields.biome == BIOME_WETLAND
    if not m.any():
        pytest.skip("this world generated no wetland")
    assert np.allclose(w._biome_meat_frac_field()[m], demog.game_meat_frac)
    assert not np.allclose(w._biome_meat_frac_field()[m], 0.0)


def test_meat_cv_field_reads_cchunts_where_cchunts_has_a_people(demog):
    w = build(demog, enable_biome_meat_cv=True)
    fld, biome = w._biome_meat_cv_field(), w._fields.biome
    for b, cv in MEAT_CV.items():
        m = biome == b
        if m.any():
            assert np.allclose(fld[m], cv), f"biome {b} does not carry MEAT_CV {cv}"


def test_biomes_without_a_calibration_people_take_HUNT_CV(demog):
    """terrain.py's own rule at the MEAT_CV definition: absent ⇒ HUNT_CV, "the CV is biome-invariant ... never
    GAME_KCAL_STD/mean". HUNT_CV is measured across ~15,600 trips, so this is an anchor, not a filler."""
    w = build(demog, enable_biome_meat_cv=True)
    fld, biome = w._biome_meat_cv_field(), w._fields.biome
    for b in (BIOME_GRASS, BIOME_MOUNTAIN, BIOME_WETLAND):
        m = biome == b
        if m.any():
            assert np.allclose(fld[m], HUNT_CV)


def test_the_new_cv_path_does_not_carry_the_MIS_ANCHORED_073(demog):
    """R-72/R-73: 0.73 is `GAME_KCAL_STD/mean` for forest — a SPATIAL cross-cell spread fed to a TEMPORAL
    per-step draw, 2.7× low. The per-biome field must not reproduce it anywhere.

    IT IS STILL THE SCALAR IN full_campaign.toml, AND THAT IS DELIBERATE, not an oversight (Addendum 38
    corrects Addendum 37 on this). R-73 swept CV 0…5.29 and found the Cred effect flat across it, so at
    forest's true 1.97 the result is statistically indistinguishable from the 0.73 the old arms ran at. Its
    closing line: "Harness CVs left at 0.73 with the mis-anchoring documented, since … re-running them would be
    compute spent to reproduce the same numbers." Do not "fix" the scalar on the strength of this test."""
    w = build(demog, enable_biome_meat_cv=True)
    assert not np.any(np.isclose(w._biome_meat_cv_field(), 0.73)), "the retired spatial anchor came back"
    assert demog.game_meat_cv == 0.73, "if the scalar changed, update this test's premise (see R-73)"


# ── the one thing that can break silently ─────────────────────────────────────────────────────────────────

def test_energy_is_conserved_per_cell(demog, monkeypatch):
    """The meat pool is `mf_c·S` and the forage stream is `(1−mf_c)·S`. They must read the SAME `mf_c`, or the
    cell creates or destroys kcal with no error raised. Recorded straight off `compute_harvest_shares`: for each
    cell, forage_total + meat_total must equal the pool. The G.3 lognormal draw is disabled here (`meat_cv=0`)
    so the meat pool is deterministic — with the draw on, the sum is mean-preserving but not exact."""
    seen: list[float] = []
    real = phase1_model.compute_harvest_shares

    def spy(occ, total, kappa, phi_eps=0.0, claim=None):
        seen.append(total)
        return real(occ, total, kappa, phi_eps, claim=claim)

    monkeypatch.setattr(phase1_model, "compute_harvest_shares", spy)
    w = build(demog, enable_biome_meat_frac=True, enable_biome_meat_cv=False, game_meat_cv=0.0)
    w._diag_pool = {}
    w.step()
    pools = dict(w._diag_pool)
    assert pools, "no cell was harvested"
    # Two calls per occupied cell, forage then meat, in cell order — their sum is that cell's pool.
    assert len(seen) == 2 * len(pools), f"expected 2 calls per cell, got {len(seen)} for {len(pools)} cells"
    for i, (S, _n) in enumerate(pools.values()):
        got = seen[2 * i] + seen[2 * i + 1]
        assert got == pytest.approx(S, rel=1e-9), f"cell {i}: forage+meat {got} != pool {S}"


def test_the_split_actually_varies_across_biomes_in_this_world(demog):
    """Guards the WORLD, not the code: if the test world had one biome the flags would be trivially inert and
    every assertion above would pass while proving nothing."""
    w = build(demog, enable_biome_meat_frac=True)
    land = w._fields.isWater == 0
    assert len(np.unique(w._biome_meat_frac_field()[land])) >= 3, \
        "this world has fewer than 3 distinct meat fractions — pick a richer world for the test"
