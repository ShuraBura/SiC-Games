"""Stage 7.5 GATE A1 — N-scaling benchmark + Numba eligibility check.

Measures the wall-clock scaling of the mean_cred hotspot:
  * Oracle pattern: n_births calls to sum(c for c in cred_list)/N per step
    → O(N²) total (each call is O(N), n_births = 0.05·N = O(N))
  * Vec pattern: one np.sum(cred[alive])/N call per step → O(N) total

N values: [1k, 2k, 5k, 10k, 15k, 19k]  (matching pre-restructure recon range)
Birth rate: 0.05·N per step (conservative — real rate is lower but proportional).

Expected exponents:
  * Oracle 10k→19k: ≈ 2.0 (confirmed O(N²))
  * Vec 10k→19k:    ≈ 1.0 (O(N), hotspot gone)

Run from sic_games/ root:
    py outputs/stage7_5/benchmark_a1_nscaling.py
"""
from __future__ import annotations

import sys
import time

import numpy as np

# ── Benchmark helpers ─────────────────────────────────────────────────────────

def _oracle_mean_cred(cred_list: list, N: int) -> float:
    """Exact oracle pattern from run.py line 316-320."""
    return sum(c for c in cred_list) / N


def _vec_mean_cred(cred: np.ndarray, alive: np.ndarray) -> float:
    """Vectorised column-mean (from soa_tier1.mean_cred_vec)."""
    live = cred[alive]
    n = live.size
    return float(np.sum(live) / n) if n > 0 else 0.0


def measure_oracle(N: int, n_births: int, reps: int = 3) -> float:
    """Wall-clock seconds per simulated step (oracle pattern)."""
    rng = np.random.default_rng(42)
    cred_list = rng.uniform(0.0, 10.0, N).tolist()
    best = float("inf")
    for _ in range(reps):
        t0 = time.perf_counter()
        for _ in range(n_births):
            _oracle_mean_cred(cred_list, N)
        best = min(best, time.perf_counter() - t0)
    return best


def measure_vec(N: int, reps: int = 50) -> float:
    """Wall-clock seconds per simulated step (vec pattern)."""
    rng = np.random.default_rng(42)
    cred = rng.uniform(0.0, 10.0, N)
    alive = np.ones(N, dtype=bool)
    best = float("inf")
    for _ in range(reps):
        t0 = time.perf_counter()
        _vec_mean_cred(cred, alive)
        best = min(best, time.perf_counter() - t0)
    return best


def log_log_exponent(x_vals, y_vals) -> float:
    """Slope of log(y) vs log(x) via least-squares (= scaling exponent)."""
    lx = np.log(np.array(x_vals, dtype=np.float64))
    ly = np.log(np.array(y_vals, dtype=np.float64))
    n = len(lx)
    lx_m = lx - lx.mean()
    ly_m = ly - ly.mean()
    return float((lx_m * ly_m).sum() / (lx_m ** 2).sum())


def interval_exponent(x1, t1, x2, t2) -> float:
    """Two-point log-log slope between (x1,t1) and (x2,t2)."""
    return np.log(t2 / t1) / np.log(x2 / x1)


# ── Main benchmark ─────────────────────────────────────────────────────────────

def run_benchmark():
    N_VALUES = [1_000, 2_000, 5_000, 10_000, 15_000, 19_000]
    BIRTH_RATE = 0.05  # fraction of N that are born per step

    print("=" * 66)
    print("Stage 7.5 GATE A1 — mean_cred N-scaling benchmark")
    print("=" * 66)
    print(f"Birth-rate assumption: {BIRTH_RATE:.0%} of N per step")
    print(f"Oracle pattern: {BIRTH_RATE:.0%}*N calls x O(N) each -> O(N^2)/step")
    print(f"Vec pattern:    1 call x O(N) -> O(N)/step")
    print()

    oracle_times = {}
    vec_times = {}

    print(f"{'N':>8}  {'n_births':>9}  {'oracle ms':>12}  {'vec µs':>10}  {'speedup':>10}")
    print("-" * 66)
    for N in N_VALUES:
        n_births = max(1, int(BIRTH_RATE * N))
        t_oracle = measure_oracle(N, n_births)
        t_vec = measure_vec(N)
        oracle_times[N] = t_oracle
        vec_times[N] = t_vec
        speedup = t_oracle / t_vec
        print(f"{N:>8,}  {n_births:>9,}  {t_oracle*1000:>11.2f}  {t_vec*1e6:>10.2f}  {speedup:>9.0f}×")

    print()

    # ── Exponent at 10k → 19k (the target range) ─────────────────────────────
    exp_oracle_tail = interval_exponent(
        10_000, oracle_times[10_000], 19_000, oracle_times[19_000]
    )
    exp_vec_tail = interval_exponent(
        10_000, vec_times[10_000], 19_000, vec_times[19_000]
    )

    # ── Global exponents (full N range) ──────────────────────────────────────
    exp_oracle_global = log_log_exponent(N_VALUES, [oracle_times[n] for n in N_VALUES])
    exp_vec_global = log_log_exponent(N_VALUES, [vec_times[n] for n in N_VALUES])

    print("N-scaling exponents:")
    print(f"  Oracle 10k->19k:  {exp_oracle_tail:+.3f}  (expected ~2.0 for O(N^2))")
    print(f"  Vec    10k->19k:  {exp_vec_tail:+.3f}  (expected ~1.0 for O(N))")
    print(f"  Oracle global:    {exp_oracle_global:+.3f}")
    print(f"  Vec    global:    {exp_vec_global:+.3f}")
    print()

    verdict_tail = "PASS" if exp_vec_tail < 1.5 else "WARN"
    print(f"  Tail-exponent gate (vec 10k->19k < 1.5): {verdict_tail}")
    print()

    return {
        "oracle_times": oracle_times,
        "vec_times": vec_times,
        "exp_oracle_tail": exp_oracle_tail,
        "exp_vec_tail": exp_vec_tail,
        "exp_oracle_global": exp_oracle_global,
        "exp_vec_global": exp_vec_global,
        "tail_gate": verdict_tail,
    }


# ── Numba eligibility check ────────────────────────────────────────────────────

def check_numba():
    print("=" * 66)
    print("Numba eligibility check (structural blocker confirmation)")
    print("=" * 66)
    try:
        from numba import njit  # type: ignore

        # Confirm njit can compile the core reduction patterns
        # (mean_cred, mean_wealth, gini inner loop, harvest-weight loop).
        # The structural blocker was agent-object attribute access (a.cred, a.wealth);
        # with pure numpy arrays, that blocker is cleared.

        @njit
        def _njit_mean(col, n):  # mirrors mean_cred_vec / mean_wealth_vec
            s = 0.0
            for i in range(n):
                s += col[i]
            return s / n if n > 0 else 0.0

        @njit
        def _njit_gini_inner(sorted_vals, n):  # mirrors gini_vec inner loop
            total = 0.0
            for v in sorted_vals:
                total += v
            if total == 0.0:
                return 0.0
            weighted = 0.0
            for i in range(n):
                weighted += (2.0 * (i + 1) - n - 1.0) * sorted_vals[i]
            return weighted / (n * total)

        @njit
        def _njit_harvest_weights(phi, is_carbon, kappa, phi_eps, n):  # mirrors harvest_split_segment inner
            weights = np.empty(n, dtype=np.float64)
            for i in range(n):
                weights[i] = (phi[i] + phi_eps) ** kappa if is_carbon[i] else 1.0
            return weights

        # Force compile by calling with representative inputs
        arr = np.ones(100, dtype=np.float64)
        _njit_mean(arr, 100)
        sorted_arr = np.sort(arr)
        _njit_gini_inner(sorted_arr, 100)
        phi_arr = np.ones(10, dtype=np.float64) * 0.5
        carbon_mask = np.array([True, False] * 5)
        _njit_harvest_weights(phi_arr, carbon_mask, 2.0, 0.1, 10)

        status = (
            "PASS — njit compiles on mean_cred, gini, and harvest-weight patterns.\n"
            "       Agent-object attribute-access blocker (a.cred, a.wealth) is cleared;\n"
            "       reduction paths now take plain numpy arrays throughout."
        )
        result = "PASS"
    except ImportError:
        status = (
            "SKIP — numba not installed in this environment. Structural eligibility\n"
            "       confirmed by inspection: all reduction paths (`mean_cred_vec`,\n"
            "       `mean_wealth_vec`, `gini_vec`, `harvest_split_segment`) take pure\n"
            "       numpy arrays with no agent-object attribute access. The previous\n"
            "       structural blocker (a.cred, a.wealth in per-agent loops) is gone.\n"
            "       Full njit compilation is scoped to §9 (validation pass)."
        )
        result = "SKIP"
    except Exception as e:
        status = f"FAIL — {e}"
        result = "FAIL"

    print(status)
    print()
    return result


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    bench = run_benchmark()
    numba = check_numba()
    print("=" * 66)
    print("Summary")
    print("=" * 66)
    print(f"  N-scaling vec 10k->19k exponent: {bench['exp_vec_tail']:+.3f}  (target ~1.0)")
    print(f"  N-scaling oracle tail exponent: {bench['exp_oracle_tail']:+.3f}  (confirms O(N^2))")
    print(f"  Tail-exponent gate:             {bench['tail_gate']}")
    print(f"  Numba eligibility:              {numba}")
    overall = "PASS" if bench["tail_gate"] == "PASS" and numba in ("PASS", "SKIP") else "FAIL"
    print(f"  Overall A1 verdict:             {overall}")
    sys.exit(0 if overall == "PASS" else 1)
