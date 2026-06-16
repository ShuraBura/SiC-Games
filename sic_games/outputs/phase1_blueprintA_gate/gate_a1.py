"""gate_a1.py — Gate A-1: correctness rails for Blueprint A substrate migration.

Pre-committed parameters (supervisor-confirmed):
  L_short = 500 steps
  S = 3 seeds (42, 43, 44)
  occ_cap_loose = 10/cell → explosion bound = 100,000 agents (100×100 × 10)

Rails:
  RAIL 1 (no extinction):  population > 0 at run end
  RAIL 2 (no explosion):   population <= EXPLOSION_BOUND (100,000)
  RAIL 3 (economy coherent): mean reserve in kcal bounds
    - no alive-but-negative reserve
    - mean reserve stays finite (< 10× reserve_full at any step)
  RAIL 4 (existing tests green): verified separately by pytest; not re-run here

Failure action: print FAIL + details and exit with code 1 (STOP, CLAUDE.md Rule 11).
On pass: print PASS summary and write results to gate_a1_results.json.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# Allow running from the outputs directory
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from sic_games.config import KcalEconomyConfig
from sic_games.phase1_model import TerrainWorld

# ── Gate parameters (supervisor-confirmed 2026-06-14) ──────────────────────
L_SHORT = 500
SEEDS = [42, 43, 44]
OCC_CAP_LOOSE = 10
EXPLOSION_BOUND = 100 * 100 * OCC_CAP_LOOSE   # 100,000

N_AGENTS_INIT = 250     # initial population per seed
KCAL_CFG = KcalEconomyConfig()                 # default placeholders [MR-1 pending]
# TerrainWorld uses _DEFAULT_KNOBS with seedStr=f"world{seed}" per-seed → deterministic


def run_seed(seed: int) -> dict:
    """Run one seed for L_SHORT steps. Return diagnostic dict."""
    world = TerrainWorld(
        n_agents=N_AGENTS_INIT,
        kcal_cfg=KCAL_CFG,
        seed=seed,
        game_stream=False,   # A-1: forage only
    )

    min_pop = world.population()
    max_pop = world.population()
    found_alive_negative = False
    max_mean_reserve = world.mean_reserve()

    for step in range(L_SHORT):
        world.step()
        pop = world.population()
        mean_res = world.mean_reserve()

        if pop < min_pop:
            min_pop = pop
        if pop > max_pop:
            max_pop = pop
        if world.any_alive_below_floor():
            found_alive_negative = True
        if mean_res > max_mean_reserve:
            max_mean_reserve = mean_res

    final_pop = world.population()
    return {
        "seed": seed,
        "final_pop": final_pop,
        "min_pop": min_pop,
        "max_pop": max_pop,
        "found_alive_below_floor": found_alive_negative,
        "max_mean_reserve": max_mean_reserve,
        "reserve_full": KCAL_CFG.reserve_full_kcal,
    }


def check_rails(result: dict) -> list[str]:
    """Return list of failure messages (empty = all pass)."""
    failures = []
    r = result
    seed = r["seed"]

    # RAIL 1: no extinction
    if r["final_pop"] <= 0:
        failures.append(
            f"RAIL 1 FAIL (seed={seed}): extinction — final_pop={r['final_pop']}"
        )

    # RAIL 2: no explosion
    if r["max_pop"] > EXPLOSION_BOUND:
        failures.append(
            f"RAIL 2 FAIL (seed={seed}): explosion — max_pop={r['max_pop']} > {EXPLOSION_BOUND}"
        )

    # RAIL 3a: no alive-but-negative-reserve
    if r["found_alive_below_floor"]:
        failures.append(
            f"RAIL 3a FAIL (seed={seed}): alive agent(s) found with reserve < floor"
        )

    # RAIL 3b: no unbounded monotonic growth (cap at 10× reserve_full)
    cap_check = 10.0 * r["reserve_full"]
    if r["max_mean_reserve"] > cap_check:
        failures.append(
            f"RAIL 3b FAIL (seed={seed}): mean_reserve {r['max_mean_reserve']:.0f} "
            f"> 10× reserve_full = {cap_check:.0f}"
        )

    return failures


def main() -> None:
    print(f"Gate A-1 — forage-only substrate migration correctness rails")
    print(f"L_short={L_SHORT}, seeds={SEEDS}, occ_cap_loose={OCC_CAP_LOOSE}, "
          f"explosion_bound={EXPLOSION_BOUND}")
    print(f"N_init={N_AGENTS_INIT}, burn={KCAL_CFG.burn_kcal_per_day * KCAL_CFG.days_per_month:.0f} "
          f"kcal/step, hours_per_step={KCAL_CFG.foraging_hours_per_day * KCAL_CFG.days_per_month:.0f}")
    print()

    all_results = []
    all_failures: list[str] = []

    for seed in SEEDS:
        print(f"  seed={seed} ...", end="", flush=True)
        result = run_seed(seed)
        all_results.append(result)
        failures = check_rails(result)
        all_failures.extend(failures)
        status = "PASS" if not failures else "FAIL"
        print(
            f" {status} | pop={result['final_pop']} "
            f"(min={result['min_pop']}, max={result['max_pop']}) "
            f"| max_mean_res={result['max_mean_reserve']:.0f} kcal"
        )

    print()
    if all_failures:
        print("GATE A-1: FAIL")
        for f in all_failures:
            print(f"  {f}")
        sys.exit(1)

    print("GATE A-1: PASS — all rails green across all seeds.")
    print("Proceed to Phase A-2 (sex attribute + game stream + age-gate).")

    out_path = Path(__file__).parent / "gate_a1_results.json"
    with open(out_path, "w") as fh:
        json.dump(
            {
                "gate": "A-1",
                "status": "PASS",
                "L_short": L_SHORT,
                "seeds": SEEDS,
                "occ_cap_loose": OCC_CAP_LOOSE,
                "explosion_bound": EXPLOSION_BOUND,
                "n_agents_init": N_AGENTS_INIT,
                "results": all_results,
            },
            fh,
            indent=2,
        )
    print(f"Results written to {out_path}")


if __name__ == "__main__":
    main()
