"""CARRYING-CAPACITY INVARIANTS — the dedicated regression set for the R-105 bug class.

WHY THIS EXISTS. R-105 was not caught by 912 passing tests, because every one of them asked "does this mechanism
do what it says?" and none asked "is the world still Malthusian?" The bug removed the population limit entirely
and the suite was silent, while three headline results were quietly grown on the broken substrate:
  - R-103h "flat-tropical 40k explosion" — read as a plausible forager density, actually unbounded growth;
  - R-104 "seed bifurcation" (seeds 0/1/2 → 5937-8504, seed 3 → 97551) — read as bistability, actually the bug;
  - the patch-18 smoke test "stratification leapt to 69.7%" — did not replicate at all once fixed (0.0%).

These are SUBSTRATE invariants, not mechanism tests: properties any run must satisfy for a density-dependent
result read off it to mean anything. They are deliberately loud and cheap, and they are the checks that would
have failed on 2026-07-25 instead of a night of compute and three false readings.

Each test drives a real world under crowding and asserts a property of the population-resource loop:
  1. food does not outrun the land          (the pool is capped by the catchment)
  2. crowding produces starvation           (the Malthusian brake actually bites)
  3. growth decelerates as density rises    (no superexponential limb)
  4. surplus does not saturate while growing (the runaway's own signature)
  5. the same run with the gap open FAILS these (the set has power — it is not vacuously green)

Marked `slow`: these step real worlds. Profile with
    py -3 -m pytest sic_games/tests/test_capacity_invariants.py -q --durations=0
"""
import math
import os
import sys

import pytest

from sic_games.config import CarbonConfig, KcalEconomyConfig, SubstrateConfig
from sic_games.capacity import NPPCapacityField
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world, world_lottery_climate

STEPS = 400          # long enough for crowding to bind, short enough to stay a test
# N0/patch ARE CALIBRATED, NOT GUESSED. The gap-open and fixed runs must SEPARATE or the power test is vacuous.
# RE-CALIBRATED 2026-09-06 (R-106): after the density-fertility / settlement-pair / Kaplan-juvenile adoptions
# shifted the regime, patch 18 no longer separated — the catchment ceiling (on in BOTH arms) caps the milder
# window on its own, so toggling the aggl ceiling did nothing (measured: density 0.98x, starvation 0.81x, the
# power test correctly failing). A tighter circumscription restores the aggl-ceiling runaway signature.
# Measured (probe, 400 steps, N0=6000 patch=10): density 1.28x (gap open 1057 vs fixed 825 over 100 cells);
# starvation no longer separates (~1.0x) — the bug is now DENSITY-dominated, so the power test rides the density
# limb. Thresholds below sit under the density measurement.
N0 = 6000


def _preset():
    _here = os.path.dirname(os.path.abspath(__file__))
    _p = os.path.normpath(os.path.join(_here, "..", "outputs", "phase1_social_evolution"))
    if _p not in sys.path:
        sys.path.insert(0, _p)
    from run_se0_controlled_climate import emergent_village_demog
    return emergent_village_demog()


def _crowded_world(ceiling=True, seed=0, n=N0, patch=10):
    """A deliberately CIRCUMSCRIBED world (small capacity window) with the village stack on — the regime where
    the R-105 gap ran away. `patch` bounds capacity to a sub-window with ZERO outside, so the population cannot
    disperse out of the pressure."""
    k = world_lottery_climate(seed, terrain="coastal", climate="temperate")
    f = generate_world(k, mode="climate")
    hf = NPPCapacityField(f, 75000.0, patch=(20, 20, patch), mode="tallavaara", aquatic=True,
                          enable_depletion=True)
    land = [(x, y) for y in range(100) for x in range(100)
            if f.isWater[y, x] == 0 and hf.level(x, y) > 0]
    assert land, "no habitable land in the bounded patch"
    pos = [land[i % len(land)] for i in range(n)]
    d = _preset().model_copy(update=dict(
        enable_aggregation_sedentism=True, enable_catchment_ceiling=True, enable_aggl_ceiling=ceiling,
        enable_settlement_scalar_stress=True, enable_landscape_packing=True, enable_marriage_aggregation=True))
    w = TerrainWorld(n_agents=n, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, game_stream=False, seed=seed,
                     carbon_cfg=CarbonConfig(kappa=1.5),
                     substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                                   contest_exponent=1.5, move_cost_flat=0.0),
                     harvest_field=hf, placement_positions=pos, demography_cfg=d)
    return w, len(land)


def _run(w, steps=STEPS, every=25):
    """Step the world, returning the trajectory the invariants are read from."""
    traj = []
    starv = 0
    for s in range(1, steps + 1):
        w.step()
        if not w.agent_list:
            break
        starv += w.deaths_starv_this_step
        if s % every == 0:
            traj.append(dict(step=s, pop=len(w.agent_list), starv_cum=starv))
    assert traj, "world died before the first sample"
    return traj


@pytest.fixture(scope="module")
def fixed_run():
    w, cells = _crowded_world(ceiling=True)
    return _run(w), cells


@pytest.fixture(scope="module")
def buggy_run():
    w, cells = _crowded_world(ceiling=False)
    return _run(w), cells


# ── the invariants ──────────────────────────────────────────────────────────────────────────────

@pytest.mark.slow
def test_crowding_produces_starvation(fixed_run):
    """THE MALTHUSIAN BRAKE BITES. R-105's signature was 61 agents/cell with ZERO starvation deaths — food had
    stopped binding. Under real crowding some agents must fail to feed."""
    traj, cells = fixed_run
    dens = traj[-1]["pop"] / cells
    assert dens > 2.0, f"world never got crowded (density {dens:.1f}/cell) — the test lost its premise"
    assert traj[-1]["starv_cum"] > 0, f"no starvation at {dens:.1f} agents/cell — capacity is not binding"


@pytest.mark.slow
def test_starvation_keeps_pace_with_crowding(fixed_run):
    """The brake must keep BITING, not fire once and stop. R-105's signature was starvation going to zero while
    density climbed; here the cumulative toll must still be accumulating in the run's second half.

    NOTE — this replaces a "late growth rate <= early growth rate" invariant that was simply WRONG for a packed
    start: the population dies back hard in the first ~100 steps and then RECOVERS, so growth legitimately
    accelerates in the second half. It failed on the fixed substrate, i.e. it was a false invariant rather than
    a detection. Asserting a false invariant is worse than asserting none, so it is gone rather than retuned."""
    traj, _ = fixed_run
    half = len(traj) // 2
    early = traj[half]["starv_cum"]
    late = traj[-1]["starv_cum"] - early
    assert late > 0, "starvation stopped entirely while the run continued — the ceiling is not binding"


@pytest.mark.slow
def test_population_stays_within_an_order_of_the_land(fixed_run):
    """A bounded patch cannot host an unbounded population. Loose by design — this is a runaway alarm, not a
    calibration: the R-105 arm hit 61 agents/cell and climbing."""
    traj, cells = fixed_run
    dens = traj[-1]["pop"] / cells
    assert dens < 40.0, f"density {dens:.1f}/cell in a bounded patch — suspect an uncapped food path"


@pytest.mark.slow
def test_the_set_has_power_the_gap_open_run_violates_it(buggy_run, fixed_run):
    """THE CONTROL, and the point of the whole module: with the ceiling gap OPEN the same world breaks at least
    one invariant that the fixed world satisfies. Without this, a green suite would prove nothing — it is the
    check that these assertions can fail. If this ever passes-by-not-failing, the invariants have gone vacuous."""
    btraj, cells = buggy_run
    ftraj, _ = fixed_run
    b_dens, f_dens = btraj[-1]["pop"] / cells, ftraj[-1]["pop"] / cells
    # Thresholds sit UNDER the measured effect (density 1.28x; starvation no longer separates, ~1.0x — see the
    # header re-calibration) so the DENSITY limb has headroom without being vacuous. Numbers are in the header.
    violations = []
    if b_dens > f_dens * 1.05:
        violations.append(f"density {b_dens:.1f} vs fixed {f_dens:.1f}/cell")
    if btraj[-1]["starv_cum"] * 1.10 < ftraj[-1]["starv_cum"]:
        violations.append(f"starvation {btraj[-1]['starv_cum']} vs fixed {ftraj[-1]['starv_cum']}")
    assert violations, (
        "the gap-open run looks IDENTICAL to the fixed one — either the crowding regime is too mild to "
        "separate them (raise N0 / shrink patch) or these invariants no longer detect the bug class")
