"""Stage 5: BatchRunner — multi-seed, multi-config runner with CRN support.

Common-random-numbers (CRN): when crn=True, all configs sharing the same
seed use env_rng=np.random.default_rng(seed) and agent_rng=seed+10000.
C and Si worlds at the same seed therefore see identical environmental draws
(placement positions, bio attributes) so population differences are attributable
to agent strategy, not environmental variance.

Existing runs (e.g. Stage 4.5 seed=42 parquets) are loaded from cache via
the `existing_map` parameter — no re-run, no wasted compute.

API:
    runner = BatchRunner(
        configs=[c_cfg_path, si_cfg_path],
        seeds=[42, 43, 44, 45, 46],
        crn=True,
        n_workers=4,
        task_id="T1",
        output_root=Path("outputs/stage5"),
        existing_map={("T1_C_mod_stress", 42): Path("outputs/stage45_seed42/T4_C_A050_T200")},
    )
    df = runner.run()   # pd.DataFrame with one row per (config, seed)
"""
from __future__ import annotations

import shutil
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

_STABLE_T = 500
_N_BOMB = 800


# ─── per-job helpers (module-level so ProcessPoolExecutor can pickle them) ────

def _mean_late(df: pd.DataFrame, col: str, stable_t: int = _STABLE_T) -> float:
    late = df[df["step"] >= stable_t]
    if late.empty or col not in late.columns:
        return float("nan")
    return float(late[col].mean())


def _summarise(df: pd.DataFrame, strategy: str,
               A: float, T: int, tf: float) -> dict:
    """Compute tidy summary metrics from a run's metrics DataFrame."""
    pop_col = "n_active_si" if strategy == "si_bounded" else "population"
    if pop_col not in df.columns:
        pop_col = "population"

    late_pop = df[df["step"] >= _STABLE_T][pop_col] if pop_col in df.columns else pd.Series(dtype=float)
    N_lo = int(late_pop.min()) if not late_pop.empty else 0
    N_hi = int(late_pop.max()) if not late_pop.empty else 0
    N_mean = float(late_pop.mean()) if not late_pop.empty else 0.0

    all_pop = df[pop_col] if pop_col in df.columns else pd.Series([0])
    collapse_rows = df[all_pop < 10]
    collapse = not collapse_rows.empty
    collapse_step = int(collapse_rows["step"].iloc[0]) if collapse else None

    births_col = "births_si" if strategy == "si_bounded" else "births_c"

    return dict(
        strategy=strategy, A=A, T=T, tf=tf,
        N_lo=N_lo, N_hi=N_hi, N_mean=N_mean,
        collapse=collapse, collapse_step=collapse_step,
        dormancy_rate=_mean_late(df, "dormancy_rate"),
        carry_disc_mean=_mean_late(df, "carry_discount_mean"),
        est_starv=_mean_late(df, "deaths_starvation_established"),
        births_per_step=_mean_late(df, births_col),
        senes_per_step=_mean_late(df, "deaths_senescence"),
    )


def _run_one_job(cfg_path_str: str, seed: int, crn: bool,
                 out_dir_str: str, n_bomb: int, n_steps: int | None) -> dict:
    """Execute a single (config, seed) job. Module-level for pickling."""
    from sic_games.config import Config, load_config
    from sic_games.run import SugarWorld

    cfg_path = Path(cfg_path_str)
    out_dir = Path(out_dir_str)
    parquet = out_dir / "metrics.parquet"

    # Load base config, override seed and output dir
    base_cfg = load_config(str(cfg_path))
    cfg_dict = base_cfg.model_dump()
    cfg_dict["seed"] = seed
    cfg_dict["run"]["output_dir"] = str(out_dir)
    if n_steps is not None:
        cfg_dict["run"]["n_steps"] = n_steps

    out_dir.mkdir(parents=True, exist_ok=True)
    run_cfg_path = out_dir / "run_config.yaml"
    with open(run_cfg_path, "w") as f:
        yaml.dump(cfg_dict, f, default_flow_style=False, sort_keys=False)

    run_cfg = Config.model_validate(cfg_dict)

    if parquet.exists():
        df = pd.read_parquet(parquet)
    else:
        env_seed = seed if crn else None
        agent_seed = (seed + 10000) if crn else None
        world = SugarWorld(run_cfg, env_seed=env_seed, agent_seed=agent_seed)
        total_steps = run_cfg.run.n_steps
        for step_i in range(total_steps):
            world.step()
            if step_i > 50:
                n_total = len(list(world.agents))
                if n_total > n_bomb:
                    break
        df = world.metrics_to_df()
        df.to_parquet(parquet, index=False)
        ddf = world.death_events_df()
        ddf.to_parquet(out_dir / "death_events.parquet", index=False)

    pc = run_cfg.perturbation
    A  = float(pc.amplitude)    if pc.type == "seasonal" else 0.0
    T  = int(pc.period)         if pc.type == "seasonal" else 0
    tf = float(pc.trough_fraction) if pc.type == "seasonal" else 0.5
    strategy = run_cfg.decision.strategy

    summary = _summarise(df, strategy, A, T, tf)
    summary["config"] = cfg_path.stem
    summary["seed"] = seed
    return summary


# ─── BatchRunner ──────────────────────────────────────────────────────────────

class BatchRunner:
    """Multi-seed, multi-config runner with common-random-numbers (CRN) support.

    Parameters
    ----------
    configs : list[Path]
        YAML config paths. Each is run at every seed.
    seeds : list[int]
        Seeds to run. Seed=42 results are loaded from cache when found.
    crn : bool
        When True, env_seed=seed, agent_seed=seed+10000 for all runs at that
        seed. Ensures C vs Si differences are strategy-attributable.
    n_workers : int
        ProcessPoolExecutor workers. Set to 1 to disable parallelism (useful
        for tests and debugging).
    task_id : str
        Sub-folder under output_root: outputs/stage5/{task_id}/.
    output_root : Path
        Root of Stage 5 outputs.
    n_bomb : int
        Population ceiling; run aborts early if exceeded.
    n_steps : int | None
        Override n_steps from config (useful for ψ co-evolution 3000-step runs).
    existing_map : dict[(config_stem, seed), Path]
        Map of pre-existing run directories (parquets are copied, not re-run).
        Key: (config_stem, seed). Value: path to directory containing
        metrics.parquet (and optionally death_events.parquet).
    """

    def __init__(
        self,
        configs: list[Path],
        seeds: list[int],
        crn: bool = True,
        n_workers: int = 4,
        task_id: str = "T0",
        output_root: Path = Path("outputs/stage5"),
        n_bomb: int = _N_BOMB,
        n_steps: int | None = None,
        existing_map: dict[tuple[str, int], Path] | None = None,
    ) -> None:
        self.configs = [Path(c) for c in configs]
        self.seeds = list(seeds)
        self.crn = crn
        self.n_workers = n_workers
        self.task_id = task_id
        self.output_root = Path(output_root)
        self.n_bomb = n_bomb
        self.n_steps = n_steps
        self.existing_map: dict[tuple[str, int], Path] = {
            k: Path(v) for k, v in (existing_map or {}).items()
        }

    # ------------------------------------------------------------------

    def _out_dir(self, cfg_path: Path, seed: int) -> Path:
        return self.output_root / self.task_id / f"{cfg_path.stem}_seed{seed}"

    def _prepare_existing(self, cfg_path: Path, seed: int) -> None:
        """Copy metrics + death_events from existing_map source if not yet present."""
        key = (cfg_path.stem, seed)
        if key not in self.existing_map:
            return
        src_dir = self.existing_map[key]
        out_dir = self._out_dir(cfg_path, seed)
        out_dir.mkdir(parents=True, exist_ok=True)
        for fname in ("metrics.parquet", "death_events.parquet"):
            src = src_dir / fname
            dst = out_dir / fname
            if src.exists() and not dst.exists():
                shutil.copy2(src, dst)

    def run(self) -> pd.DataFrame:
        """Run all (config, seed) pairs. Return tidy summary DataFrame."""
        # Stage existing results first (copy parquets to expected locations)
        for cfg_path in self.configs:
            for seed in self.seeds:
                self._prepare_existing(cfg_path, seed)

        jobs = [
            (cfg_path, seed, self._out_dir(cfg_path, seed))
            for cfg_path in self.configs
            for seed in self.seeds
        ]

        if self.n_workers <= 1 or len(jobs) == 1:
            rows = [
                _run_one_job(str(cfg), seed, self.crn, str(out_dir),
                             self.n_bomb, self.n_steps)
                for cfg, seed, out_dir in jobs
            ]
        else:
            rows = self._run_parallel(jobs)

        return pd.DataFrame(rows)

    def _run_parallel(self, jobs: list) -> list[dict]:
        rows: list[dict | None] = [None] * len(jobs)
        with ProcessPoolExecutor(max_workers=self.n_workers) as executor:
            futures = {
                executor.submit(
                    _run_one_job,
                    str(cfg), seed, self.crn, str(out_dir),
                    self.n_bomb, self.n_steps
                ): i
                for i, (cfg, seed, out_dir) in enumerate(jobs)
            }
            for fut in as_completed(futures):
                idx = futures[fut]
                rows[idx] = fut.result()
        return rows  # type: ignore[return-value]
