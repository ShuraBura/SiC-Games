"""Check whether the adopted canon (Add.87) stably shifts the colonizing land-use ratio below the 0.85 CTB floor,
or whether it is one-seed noise. Reuses the CTB's own _run."""
import sys
from collections import Counter
from pathlib import Path
import numpy as np

ROOT = Path(r"C:\Users\syatom\Projects\SiC Games")
for p in (ROOT / "sic_games" / "tests",):
    sys.path.insert(0, str(p))
import test_colonizing_budding_ctb as T


def lu(w):
    W = w._fields.isWater
    land = [(x, y) for y in range(100) for x in range(100) if W[y, x] == 0]
    occ = Counter(a.pos for a in w.agent_list)
    return len([c for c in land if occ.get(c, 0) > 0]) / len(land)


for seed in (1, 2, 3):
    on = T._run(True, seed=seed)
    off = T._run(False, seed=seed)
    ron, roff = lu(on), lu(off)
    print(f"seed {seed}: on_sites {len(on._settlement_sites)} off_sites {len(off._settlement_sites)} | "
          f"lu_on {ron:.4f} lu_off {roff:.4f} ratio {ron/roff:.3f} "
          f"{'PASS' if ron >= 0.85*roff else 'FAIL(<0.85)'} | pop on/off {len(on.agent_list)}/{len(off.agent_list)}",
          flush=True)
