"""CTB — WHAT DO `forage_kcal` AND `game_kcal` ACTUALLY CONTROL IN A CAMPAIGN RUN?

WHY THIS EXISTS. The retracted `food_consistency` diagnostic (commit 4f02e1d, reverted 25df603) treated
`forage_kcal` as if it were the model's food supply. It is not — `capacity.py` says so in its own header, and
the campaign passes an `NPPCapacityField` as `harvest_field`. That left a question nobody had answered: if the
capacity field is the supply, what are the two return-rate fields still doing? The docs carry an anchored
per-biome return-rate table for both, so "nothing" was a live possibility and worth measuring rather than
assuming.

THE METHOD IS PERTURBATION, NOT INSPECTION. Scale a field by 1000x (or zero it) and re-run. A field that can be
multiplied by 1000 with a BIT-IDENTICAL trajectory is not load-bearing on that path, whatever its comments say.
Reading call sites tells you where a name APPEARS; only perturbation tells you whether the value MATTERS.

THE INSTRUMENT HAS A POSITIVE CONTROL, and it is not decoration — the first version of this measurement was
WRONG in exactly the way the control catches. `TerrainWorld.__init__` does `self._fields = generate_world(knobs)`
(phase1_model.py:267): the model REGENERATES its own world and never reads the `WorldFields` the caller built for
the capacity field. Perturbing the caller's copy changed nothing, every arm read "not load-bearing", and the
answer looked clean and meant nothing. `test_positive_control_*` perturbs a field known to be load-bearing and
REQUIRES the run to change; if it ever passes trivially, every other test in this file is void.

THE FINDINGS.

  `game_kcal`  — DEAD on the campaign path. Zero it or multiply it by 1000: bit-identical. It is read only by
                 `TerrainField.game_level`, called only from `_step_agent`, which runs only when the substrate is
                 DISABLED and `game_stream=True`. No harness in the repo sets `game_stream=True` (only
                 test_phase1_kcal.py does). So the per-biome GAME return-rate table — including the wetland and
                 mountain zeros — has never affected a single run. Meat in a campaign is `game_meat_frac * S`,
                 a flat fraction of the NPP capacity pool, modulated by the climate `meat_factor`; it carries NO
                 biome-specific game signal at all.

  `forage_kcal` — LIVE, on three surfaces, and no others:
                 1. BAND PLACEMENT, outside the model, in `seed_band_positions*` (the biggest effect: x0.001
                    scatters the founders across 175 cells, x1000 packs them onto 8).
                 2. the PER-PERSON FORAGE CAP, `enable_forage_cap`.
                 3. the AGGLOMERATION BASE `A_cell = aggl_tier2 * S_pot * (forage_kcal * forage_cap_hours)`,
                    `enable_agglomeration`.
                 Turn both flags off and it is INERT in-model — that is `test_both_consumers_off_makes_it_inert`,
                 which is what makes the list above exhaustive rather than merely everything I happened to find.

Measured on config/runs/full_campaign.toml, the config campaigns actually run.
"""
import random

import pytest

from sic_games import phase1_model, runspec
from sic_games.capacity import NPPCapacityField
from sic_games.config import CarbonConfig, KcalEconomyConfig, SubstrateConfig
from sic_games.phase1_model import TerrainWorld, seed_band_positions_spread
from sic_games.terrain import generate_world, world_lottery_climate

BURN, SEED, NAG, STEPS = 75000.0, 0, 200, 10
PATCH = (20, 20, 60)
_REPO = __import__("pathlib").Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def demog():
    spec = runspec.load(_REPO / "config" / "runs" / "full_campaign.toml", seed=SEED)
    return runspec.build(spec, "DemographyConfig")


def _set(fields, name, arr):
    object.__setattr__(fields, name, arr)          # WorldFields is frozen


def run(demog, scale=None, seed_scale=None, npp_scale=None, update=None):
    """One arm. `scale`/`npp_scale` perturb the MODEL's own fields after construction, while the derived caches
    (`_forage_cap_cache`, `_aggl_point_cache`) are still None; `seed_scale` perturbs the caller's copy before
    seeding, which is the one surface computed OUTSIDE the model."""
    k = world_lottery_climate(SEED, terrain="coastal", climate="temperate")
    f = generate_world(k, mode="climate")
    for nm, s in (seed_scale or {}).items():
        _set(f, nm, getattr(f, nm) * s)
    hf = NPPCapacityField(f, BURN, patch=PATCH, mode="tallavaara", aquatic=True, enable_depletion=True)
    pos = seed_band_positions_spread(f, NAG, hours_per_step=100.0, burn=BURN, band_size=25,
                                     rng=random.Random(SEED))
    w = TerrainWorld(n_agents=NAG, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, game_stream=False, seed=SEED,
                     carbon_cfg=CarbonConfig(kappa=1.5),
                     substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                                   contest_exponent=1.5, move_cost_flat=0.0),
                     harvest_field=hf, placement_positions=pos,
                     demography_cfg=demog.model_copy(update=update) if update else demog)
    for nm, s in (scale or {}).items():
        _set(w._fields, nm, getattr(w._fields, nm) * s)
    if npp_scale is not None:
        _set(w._fields, "npp_gm2", w._fields.npp_gm2 * npp_scale)
        w._harvest_field = NPPCapacityField(w._fields, BURN, patch=PATCH, mode="tallavaara",
                                            aquatic=True, enable_depletion=True)

    pools: list[float] = []
    real = phase1_model.compute_harvest_shares
    phase1_model.compute_harvest_shares = lambda occ, tot, kap, eps=0.0: (pools.append(tot),
                                                                          real(occ, tot, kap, eps))[1]
    try:
        traj = []
        for _ in range(STEPS):
            w.step()
            traj.append(sum(1 for a in w.agent_list if a.alive))
    finally:
        phase1_model.compute_harvest_shares = real
    return {"pop": traj, "pool_sum": round(sum(pools), 6), "seed_cells": len(set(pos))}


def identical(a, b):
    return a["pop"] == b["pop"] and a["pool_sum"] == b["pool_sum"] and a["seed_cells"] == b["seed_cells"]


# ── the instrument, before any claim made with it ─────────────────────────────────────────────────────────

def test_positive_control_the_perturbation_reaches_the_model(demog):
    """THE GATE ON EVERYTHING BELOW. `npp_gm2` feeds the capacity field, which IS the supply, so halving it must
    change the run. If this ever passes trivially, the perturbation is not reaching `w._fields` and every
    "IDENTICAL" verdict in this file is an artefact of the instrument rather than a fact about the model."""
    assert not identical(run(demog), run(demog, npp_scale=0.5)), \
        "halving NPP changed nothing — the harness is not perturbing the field the model reads"


def test_the_baseline_is_a_live_run_not_an_extinction(demog):
    """A dead population is insensitive to everything, so it would make every field look inert. The arms must be
    compared on a world that still has people in it."""
    base = run(demog)
    assert base["pop"][-1] > 50, f"baseline collapsed to {base['pop'][-1]} — nothing can be measured on it"


# ── game_kcal: dead ───────────────────────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("s", [0.0, 1000.0])
def test_game_kcal_is_not_load_bearing_in_a_campaign_run(demog, s):
    """Zero the game return-rate field or multiply it by a thousand: the run is bit-identical. The anchored
    per-biome GAME table does not reach the campaign path at all."""
    assert identical(run(demog), run(demog, scale={"game_kcal": s})), \
        f"game_kcal x{s} changed the run — it is load-bearing after all, and the docs must say where"


def test_the_only_game_kcal_consumer_is_a_path_no_harness_takes(demog):
    """WHY it is dead, pinned structurally so the reason survives a refactor: the campaign is rivalrous, and the
    rivalrous path reads `self._harvest_field` (the capacity field). `game_level` is reachable only from
    `_step_agent`, i.e. only with the substrate DISABLED and `game_stream=True`."""
    src = (_REPO / "sic_games" / "src" / "sic_games" / "phase1_model.py").read_text(encoding="utf-8")
    assert src.count("game_level(") == 1, "a second game_level call site appeared — re-measure the claim above"
    assert "if self._game_stream:" in src


def test_campaign_meat_is_a_flat_fraction_of_CAPACITY_not_a_biome_game_rate(demog):
    """The consequence worth stating: with the game table dead, a campaign's meat is `game_meat_frac * S` — the
    SAME fraction of the capacity pool in every biome. Whatever biome-to-biome variation in hunting the
    return-rate table encodes, the model does not have it. (The climate `meat_factor` still modulates it in time
    on GRASS_STEPPE; that is a temporal channel, not a biome-specific rate.)"""
    assert demog.enable_game and demog.game_meat_frac > 0.0
    src = (_REPO / "sic_games" / "src" / "sic_games" / "phase1_model.py").read_text(encoding="utf-8")
    assert "meat_pool = meat_frac * S" in src


# ── forage_kcal: live, on an exhaustively identified set of surfaces ──────────────────────────────────────

@pytest.mark.parametrize("s", [0.001, 1000.0])
def test_forage_kcal_is_load_bearing_in_model(demog, s):
    assert not identical(run(demog), run(demog, scale={"forage_kcal": s})), \
        f"forage_kcal x{s} changed nothing in-model — a consumer was removed and the docs are now wrong"


def test_forage_kcal_drives_founder_PLACEMENT_hardest(demog):
    """The seeding surface, and the largest effect of the three: the field decides where bands are put and how
    many distinct cells they occupy. This one is computed OUTSIDE the model, in `seed_band_positions_spread`."""
    base, poor, rich = run(demog), run(demog, seed_scale={"forage_kcal": 0.001}), \
        run(demog, seed_scale={"forage_kcal": 1000.0})
    assert poor["seed_cells"] > base["seed_cells"] > rich["seed_cells"], \
        f"placement did not track the field: {poor['seed_cells']} / {base['seed_cells']} / {rich['seed_cells']}"


def test_both_consumers_off_makes_it_inert(demog):
    """THE EXHAUSTIVENESS TEST, and the reason the list of three surfaces is a claim rather than an inventory of
    what I happened to notice. With `enable_agglomeration` and `enable_forage_cap` both off, forage_kcal x1000 is
    bit-identical in-model — so those two flags carry ALL of its in-model influence, and nothing else does."""
    off = {"enable_agglomeration": False, "enable_forage_cap": False}
    assert identical(run(demog, update=off), run(demog, scale={"forage_kcal": 1000.0}, update=off)), \
        "a THIRD in-model consumer of forage_kcal exists — find it before trusting the surface list"


@pytest.mark.parametrize("flag", ["enable_agglomeration", "enable_forage_cap"])
def test_each_named_consumer_carries_some_of_it(demog, flag):
    """Each of the two is individually necessary: turn one off and forage_kcal still matters through the other,
    which is what makes them two carriers rather than one with a spurious companion."""
    off = {"enable_agglomeration": False, "enable_forage_cap": False, flag: True}
    assert not identical(run(demog, update=off), run(demog, scale={"forage_kcal": 1000.0}, update=off)), \
        f"{flag} alone does not transmit forage_kcal — the decomposition is wrong"
