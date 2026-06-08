"""Stage 7.5 GATE FINAL — Full known-result science run reproduction.

Validates that SoAWorld (VecJTM + C-wire + sparse diagnostics) reproduces
oracle (SugarWorld + oracle JTM) on a real science config within Tier-3
equivalence.

Known-result science config: configs/stage51_si_seasonal_a075_t200_seed42.yaml
  Strategy:      Si_bounded (Si-civilisation, fission reproduction)
  Si_cred:       enabled=True, k_cred_band=1.0  (locked Stage 5.1)
  Perturbation:  seasonal, amplitude=0.75, period=200 (harsh seasonal trough)
  Population:    dynamic (births/deaths active)
  Support pool:  enabled, dormancy enabled (triggers during troughs)
  Grid:          50×50, N_init=250

This is the Stage 5.1 Si-Cred seasonal control config (run_b_si_seasonal_a075_t200_seed42).
The known result: Si agents under seasonal stress show oscillating N, dormancy
activation during troughs, and Si-Cred accumulation during peaks. 400 steps
covers 2 full seasonal cycles (period=200).

Gate criterion (blueprint §8):
  "All gates green + one full known-result science run reproduced within
   Tier-3 equivalence."

Tier-3 criteria (pre-registered below, before running):
  Test 1: N(t) envelope — min per-seed coverage >= 0.85 within
          oracle mean ± 2σ (relaxed from B1's 0.90; dynamic mode has more
          demographic stochasticity from births/deaths).
  Test 2: KS(cred) < 0.15 on pooled steady-state cred distributions
          (steps 251–400). cred is the primary science metric.
  Test 3: Population viability — all 5 SoA seeds reach N_final > 0 at step 400
          AND final N within 40% of oracle seed-mean.
  Test 4: Dormancy fraction — mean dormant fraction (last 100 steps) within
          40% of oracle mean for >= 4/5 seeds (science finding: Si dormancy
          active under resource pressure).

Note on Tier-3 tolerances: These are wider than the B1 fixed-mode battery
because dynamic-mode births/deaths amplify trajectory divergence between runs
sharing the same seed. The C-wire semantic change (pre-batch vs sequential
mean_cred) is a declared Tier-3 change (D2). The goal is to confirm qualitative
science findings reproduce, not trajectory identity.

Usage:
    py outputs/stage7_5/benchmark_final_gate.py
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
from scipy.stats import ks_2samp

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from sic_games.config import load_config
from sic_games.run import SugarWorld
from sic_games.soa_jt import VecJointTaskManager
from sic_games.soa_step import SoAWorld

_SEEDS = [42, 43, 44, 45, 46]
_N_STEPS = 400
_WINDOW_START = 251   # steps 251–400 = last 150 for steady-state pool

_CONFIG_PATH = (
    Path(__file__).parent.parent.parent / "configs" / "stage51_si_seasonal_a075_t200_seed42.yaml"
)
_OUT_DIR = Path(__file__).parent

# Gate thresholds (pre-registered)
_GATE1_COVERAGE  = 0.85   # N(t) min per-seed coverage of oracle mean ± 2σ
_GATE2_KS        = 0.15   # KS(cred) pooled steady-state
_GATE3_N_FRAC    = 0.40   # |ΔN_final|/oracle_N within this fraction
_GATE4_DORM_FRAC = 0.40   # |Δdormant|/oracle_dorm within this fraction
_GATE4_MIN       = 4      # min seeds passing Gate 4 criterion (out of 5)


def _load_cfg(seed: int):
    """Load the science config, override seed and n_steps; disable output writes."""
    cfg = load_config(_CONFIG_PATH)
    cfg = cfg.model_copy(update={
        "seed": seed,
        "run": cfg.run.model_copy(update={
            "n_steps": _N_STEPS,
            "output_dir": "",   # suppress file output during benchmark
        }),
    })
    return cfg


def _make_model(cfg, use_soa: bool):
    """Construct oracle (SugarWorld) or full SoAWorld with VecJTM."""
    if use_soa:
        m = SoAWorld(cfg)
        jt = m._jt_manager
        m._jt_manager = VecJointTaskManager(
            distance_d=jt.distance_d,
            capacity_threshold=jt.capacity_threshold,
            matthew_alpha=jt.matthew_alpha,
            epsilon=jt.epsilon,
            cred_bonus_per_participant=jt.cred_bonus_per_participant,
            seed=cfg.seed,
            c2_defection_enabled=getattr(jt, "c2_defection_enabled", False),
        )
    else:
        m = SugarWorld(cfg)
    return m


def _run_one(seed: int, use_soa: bool) -> dict:
    """Run model for _N_STEPS; return trajectory + steady-state stats."""
    cfg = _load_cfg(seed)
    m = _make_model(cfg, use_soa)

    pop_traj: list[int] = []
    cred_pool: list[float] = []
    dorm_frac_list: list[float] = []
    mean_cred_list: list[float] = []

    for _ in range(_N_STEPS):
        m.step()
        if not m.metrics_log:
            continue
        mets = m.metrics_log[-1]
        pop_traj.append(int(mets.population))
        if mets.step >= _WINDOW_START:
            agents_snap = list(m.agents)
            cred_pool.extend(a.cred for a in agents_snap)
            mean_cred_list.append(float(mets.mean_cred))
            # dormancy fraction: agents in dormant state (attribute: a.dormant)
            n_agents = max(len(agents_snap), 1)
            n_dormant = sum(1 for a in agents_snap if getattr(a, "dormant", False))
            dorm_frac_list.append(n_dormant / n_agents)

    def _mean(lst):
        return float(np.mean(lst)) if lst else float("nan")

    return dict(
        seed=seed,
        pop_traj=pop_traj,
        n_final=pop_traj[-1] if pop_traj else 0,
        cred=cred_pool,
        mean_cred=_mean(mean_cred_list),
        mean_dorm_frac=_mean(dorm_frac_list),
    )


def main() -> None:
    print(f"GATE FINAL — Science config: {_CONFIG_PATH.name}")
    print(f"Seeds: {_SEEDS}  n_steps={_N_STEPS}  window={_WINDOW_START}–{_N_STEPS}")
    print(f"Config: {_CONFIG_PATH}")
    print()

    oracle_runs: list[dict] = []
    soa_runs: list[dict] = []

    for seed in _SEEDS:
        t0 = time.perf_counter()
        print(f"  seed={seed}  oracle...", end="", flush=True)
        o = _run_one(seed, use_soa=False)
        print(f" N_final={o['n_final']}  mean_cred={o['mean_cred']:.3f}"
              f"  dorm={o['mean_dorm_frac']:.3f}  | SoA...", end="", flush=True)
        s = _run_one(seed, use_soa=True)
        dt = time.perf_counter() - t0
        print(f" N_final={s['n_final']}  mean_cred={s['mean_cred']:.3f}"
              f"  dorm={s['mean_dorm_frac']:.3f}  ({dt:.1f}s)")
        oracle_runs.append(o)
        soa_runs.append(s)

    # ── Gate evaluation ────────────────────────────────────────────────────────
    print("\n" + "=" * 65)
    print("GATE FINAL EVALUATION")
    print("=" * 65)

    gate_pass = True
    gate_lines: list[str] = []
    results: dict = {}

    # ── Test 1: N(t) envelope ─────────────────────────────────────────────────
    T = min(len(r["pop_traj"]) for r in oracle_runs)
    oracle_pops = np.array([r["pop_traj"][:T] for r in oracle_runs], dtype=float)
    soa_pops   = np.array([r["pop_traj"][:T] for r in soa_runs],    dtype=float)
    oracle_mean = oracle_pops.mean(axis=0)
    oracle_std  = oracle_pops.std(axis=0)
    lo = oracle_mean - 2.0 * oracle_std
    hi = oracle_mean + 2.0 * oracle_std
    per_seed_cov = np.array([
        float(np.mean((soa_pops[k] >= lo) & (soa_pops[k] <= hi)))
        for k in range(len(_SEEDS))
    ])
    min_cov = float(per_seed_cov.min())
    t1_pass = min_cov >= _GATE1_COVERAGE
    gate_lines.append(
        f"  Test 1 N(t) envelope (min coverage >= {_GATE1_COVERAGE:.2f}): "
        f"{min_cov:.3f}  [{'PASS' if t1_pass else 'FAIL'}]"
    )
    if not t1_pass:
        gate_pass = False
    results["test1_min_coverage"] = min_cov
    results["test1_per_seed"] = per_seed_cov.tolist()

    # ── Test 2: KS(cred) ───────────────────────────────────────────────────────
    pool_o_cred = np.array(sum([r["cred"] for r in oracle_runs], []))
    pool_s_cred = np.array(sum([r["cred"] for r in soa_runs],   []))
    if len(pool_o_cred) >= 2 and len(pool_s_cred) >= 2:
        ks_cred = float(ks_2samp(pool_o_cred, pool_s_cred).statistic)
    else:
        ks_cred = float("nan")
    t2_pass = (not np.isnan(ks_cred)) and ks_cred < _GATE2_KS
    gate_lines.append(
        f"  Test 2 KS(cred) < {_GATE2_KS:.2f} (pooled steps {_WINDOW_START}–{_N_STEPS}): "
        f"{ks_cred:.4f}  [{'PASS' if t2_pass else 'FAIL'}]"
    )
    if not t2_pass:
        gate_pass = False
    results["test2_ks_cred"] = ks_cred

    # ── Test 3: Population viability ──────────────────────────────────────────
    oracle_n_mean = float(np.mean([r["n_final"] for r in oracle_runs]))
    t3_details: list[str] = []
    t3_fail_seeds: list[int] = []
    for k, s in enumerate(soa_runs):
        seed_k = _SEEDS[k]
        alive = s["n_final"] > 0
        rel_err = (abs(s["n_final"] - oracle_runs[k]["n_final"]) /
                   max(oracle_runs[k]["n_final"], 1))
        within = rel_err < _GATE3_N_FRAC
        ok = alive and within
        t3_details.append(
            f"seed={seed_k}: oracle_N={oracle_runs[k]['n_final']}  "
            f"soa_N={s['n_final']}  rel_err={rel_err:.2f}  "
            f"{'OK' if ok else 'FAIL'}"
        )
        if not ok:
            t3_fail_seeds.append(seed_k)
    t3_pass = len(t3_fail_seeds) == 0
    gate_lines.append(
        f"  Test 3 viability (all N_final>0 + within {_GATE3_N_FRAC*100:.0f}%): "
        f"{'PASS' if t3_pass else 'FAIL (' + str(t3_fail_seeds) + ')'}"
    )
    for line in t3_details:
        gate_lines.append(f"    {line}")
    if not t3_pass:
        gate_pass = False
    results["test3_details"] = t3_details

    # ── Test 4: Dormancy fraction ─────────────────────────────────────────────
    t4_pass_count = 0
    t4_details: list[str] = []
    for k, s in enumerate(soa_runs):
        seed_k = _SEEDS[k]
        o_dorm = oracle_runs[k]["mean_dorm_frac"]
        s_dorm = s["mean_dorm_frac"]
        denom = max(o_dorm, 0.01)   # floor to avoid divide-by-zero on near-zero dormancy
        rel_err = abs(s_dorm - o_dorm) / denom
        ok = rel_err < _GATE4_DORM_FRAC
        t4_pass_count += int(ok)
        t4_details.append(
            f"seed={seed_k}: oracle_dorm={o_dorm:.3f}  soa_dorm={s_dorm:.3f}  "
            f"rel_err={rel_err:.2f}  {'OK' if ok else 'FAIL'}"
        )
    t4_pass = t4_pass_count >= _GATE4_MIN
    gate_lines.append(
        f"  Test 4 dormancy fraction (within {_GATE4_DORM_FRAC*100:.0f}%, "
        f">= {_GATE4_MIN}/5 seeds): {t4_pass_count}/5  "
        f"[{'PASS' if t4_pass else 'FAIL'}]"
    )
    for line in t4_details:
        gate_lines.append(f"    {line}")
    if not t4_pass:
        gate_pass = False
    results["test4_dorm_details"] = t4_details

    # ── Summary ───────────────────────────────────────────────────────────────
    print("\n--- Gate evaluation ---")
    for line in gate_lines:
        print(line)

    verdict = "PASS" if gate_pass else "FAIL"
    print(f"\n{'=' * 65}")
    print(f"GATE FINAL: {verdict}")
    print(f"{'=' * 65}")

    # Save results
    out_path = _OUT_DIR / "benchmark_final_gate_results.json"
    payload = {
        "config": str(_CONFIG_PATH),
        "seeds": _SEEDS,
        "n_steps": _N_STEPS,
        "oracle_runs": [
            {k: v for k, v in r.items() if k not in ("cred", "pop_traj")}
            for r in oracle_runs
        ],
        "soa_runs": [
            {k: v for k, v in r.items() if k not in ("cred", "pop_traj")}
            for r in soa_runs
        ],
        "results": results,
        "gate_lines": gate_lines,
        "gate_verdict": verdict,
    }
    with open(out_path, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"\nResults saved to: {out_path.name}")


if __name__ == "__main__":
    main()
