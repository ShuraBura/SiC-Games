"""Stage 5.1 — B0 Equivalence Gate.

Runs B0 (C static, 50×50, N=250, seed=42, 500 steps) with:
  - Current code (post-change)
  - Backup code (pre-change) from v5.1.1_pre_sicred_redesign

Compares: population N(t) exact, mean_wealth/gini_wealth/mean_cred to 1e-9 rel tol.

Usage:
    py -m sic_games.stage51_b0_gate
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

_REPO = Path(__file__).parent.parent.parent
_BACKUP = Path("G:/My Drive/docs/SiC Games/Model/v5.1.1_pre_sicred_redesign")
_B0_CFG = _REPO / "configs" / "b0_c_static_seed42.yaml"
_B0_CURRENT = _REPO / "outputs" / "b0_c_static_seed42"
_B0_REF = _REPO / "outputs" / "b0_ref_pre_sicred"


def _run_b0_in_env(src_path: Path, out_dir: Path) -> None:
    """Run B0 via subprocess with the given src directory on PYTHONPATH."""
    out_dir.mkdir(parents=True, exist_ok=True)
    script = f"""
import sys
sys.path.insert(0, r"{src_path}")
from sic_games.config import load_config
from sic_games.run import SugarWorld
import pandas as pd
from pathlib import Path

cfg = load_config(r"{_B0_CFG}")
model = SugarWorld(cfg)
for _ in range(cfg.run.n_steps):
    model.step()
df = model.metrics_to_df()
df.to_parquet(r"{out_dir / 'metrics.parquet'}", index=False)
print("B0 done:", len(df), "steps, final pop =", df["population"].iloc[-1])
"""
    result = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print("STDERR:", result.stderr[-2000:])
        raise RuntimeError(f"B0 run failed in {src_path}: {result.returncode}")
    print(result.stdout.strip())


def gate() -> None:
    current_src = _REPO / "src"
    backup_src = _BACKUP / "src"

    if not _BACKUP.exists():
        print("ERROR: Backup not found at", _BACKUP)
        sys.exit(1)

    print("=== Running B0 with CURRENT code ===")
    _run_b0_in_env(current_src, _B0_CURRENT)

    print("\n=== Running B0 with BACKUP code ===")
    _run_b0_in_env(backup_src, _B0_REF)

    print("\n=== Comparing parquets ===")
    cur = pd.read_parquet(_B0_CURRENT / "metrics.parquet")
    ref = pd.read_parquet(_B0_REF / "metrics.parquet")

    assert len(cur) == len(ref), f"Step count mismatch: {len(cur)} vs {len(ref)}"

    # Population exact
    pop_match = (cur["population"] == ref["population"]).all()
    if not pop_match:
        diff_rows = (cur["population"] != ref["population"]).sum()
        print(f"  FAIL population: {diff_rows} steps differ")
    else:
        print("  PASS population: exact match")

    # Numeric metrics to 1e-9 rel tol
    for col in ["mean_wealth", "gini_wealth", "mean_cred"]:
        if col not in cur.columns or col not in ref.columns:
            print(f"  SKIP {col}: not in parquet")
            continue
        cur_vals = cur[col].values.astype(float)
        ref_vals = ref[col].values.astype(float)
        max_reldiff = float(np.max(np.abs(cur_vals - ref_vals) /
                                   (np.abs(ref_vals) + 1e-30)))
        if max_reldiff < 1e-9:
            print(f"  PASS {col}: max_reldiff={max_reldiff:.2e}")
        else:
            print(f"  FAIL {col}: max_reldiff={max_reldiff:.2e} (threshold 1e-9)")

    print("\nB0 gate complete.")


if __name__ == "__main__":
    gate()
