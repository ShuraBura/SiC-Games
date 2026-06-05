"""Stage 6.0a Recovery Gate (§7.1).

Prove the multi-occupancy substrate, forced into the single-occupancy limit
(K_cell=1, legacy movement, κ=0, move_cost=0), reproduces the legacy
one-agent-per-cell model BIT-IDENTICALLY.

Compare: N(t) integer-exact every step; mean_wealth/gini_wealth/mean_cred to 1e-9;
births/deaths exact; final agent positions exact.

Per the Recovery-Gate-Movement patch (2026-06-03): the recovery regime holds the
candidate set at the current vision-`v` rule (movement_mode="legacy"), with the
unoccupied *filter* re-expressed as the K_cell≥count ceiling (at K_cell=1 the two
coincide). It validates the SUBSTRATE refactor only. The r=1 von-Neumann diffusion
restriction is a separate behavioural change (movement_mode="diffusion"), validated
behaviourally in §7.2 — NEVER claimed bit-identical. The report's recovery-gate
section must state this two-regime difference explicitly (anti-confusion requirement).

Usage: py -m sic_games.stage6_0a_recovery
"""
from __future__ import annotations

import numpy as np

from sic_games.config import SubstrateConfig
from sic_games.owe1_calibration import _bench_config
from sic_games.run import SugarWorld

_GRID, _N, _NCARRY, _STEPS, _SEED = 100, 2250, 4100, 500, 42


def _run(substrate: bool):
    cfg = _bench_config(_GRID, _GRID, _N, _STEPS, seed=_SEED, n_carry_override=_NCARRY)
    if substrate:
        cfg = cfg.model_copy(update={"substrate": SubstrateConfig(
            enabled=True, k_cell=1, movement_mode="legacy",
            contest_exponent=0.0, move_cost_flat=0.0,
        )})
    m = SugarWorld(cfg)
    for _ in range(_STEPS):
        m.step()
    df = m.metrics_to_df()
    states = m.agent_states_df().sort_values("unique_id").reset_index(drop=True)
    return df, states


def main() -> None:
    print("=== Stage 6.0a Recovery Gate ===")
    print(f"100x100, N_carry={_NCARRY}, init N={_N}, seed={_SEED}, C static, {_STEPS} steps")
    print("Reference: legacy (substrate disabled)")
    ref_df, ref_states = _run(False)
    print("Test:      substrate enabled, K_cell=1, legacy movement, kappa=0")
    test_df, test_states = _run(True)

    ok = True
    # N(t) integer exact
    pop_exact = (ref_df["population"].values == test_df["population"].values).all()
    print(f"  N(t) integer-exact every step: {'PASS' if pop_exact else 'FAIL'}")
    ok &= bool(pop_exact)

    # numeric to 1e-9 relative
    for col in ["mean_wealth", "gini_wealth", "mean_cred"]:
        if col not in ref_df.columns:
            print(f"  {col}: MISSING"); continue
        r = ref_df[col].values.astype(float); t = test_df[col].values.astype(float)
        maxrd = float(np.max(np.abs(r - t) / (np.abs(r) + 1e-30)))
        passed = maxrd < 1e-9
        print(f"  {col} max_reldiff={maxrd:.2e}: {'PASS' if passed else 'FAIL'}")
        ok &= passed

    # births/deaths exact (sum over run)
    for col in ["births_c", "deaths_starvation", "deaths_senescence"]:
        if col in ref_df.columns:
            eq = (ref_df[col].values == test_df[col].values).all()
            print(f"  {col} exact every step: {'PASS' if eq else 'FAIL'}")
            ok &= bool(eq)

    # final positions exact (same unique_ids + (x,y))
    same_ids = list(ref_states["unique_id"]) == list(test_states["unique_id"])
    if same_ids and len(ref_states) == len(test_states):
        pos_exact = (
            (ref_states["x"].values == test_states["x"].values).all()
            and (ref_states["y"].values == test_states["y"].values).all()
        )
    else:
        pos_exact = False
    print(f"  final positions exact ({len(ref_states)} vs {len(test_states)} agents, "
          f"ids match={same_ids}): {'PASS' if pos_exact else 'FAIL'}")
    ok &= bool(pos_exact)

    print(f"\nRECOVERY GATE: {'PASS' if ok else 'FAIL'}")
    return ok


if __name__ == "__main__":
    main()
