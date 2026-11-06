"""R-106 Add.127: ONE-YEAR HARVEST TEST, the anchor's own time unit (Dribe, Olsson & Svensson 2010: annual deviations).

No model change. Each run takes DR_N one-year shocks, DR_GAP steps apart, from DR_FIRST, with the depths in DR_MULTS in
turn. One shock in one run has too few events: ages 1-15 give about 36 deaths per year in temperate, so one shock in
3 seeds has a standard error near 14%. Twenty shocks in each run give 3 worlds x 3 seeds x 10 shocks at each depth.

The wrapper appends one JSON line per year to scratchpad/drought_logs/yr1<C_TAG>.jsonl: the raw demographic counters
(pure observer, a copy, no RNG), pop, and `mult_sum`, the running sum of the driver's multiplier (positive control).
Before DR_FIRST the driver returns 1.0 and draws no RNG, so a run must equal its stored `s2_<world>_pair` run row for row.
"""
import json
import os
import runpy
import sys

ROOT = r"C:\Users\syatom\Projects\SiC Games"
sys.path.insert(0, os.path.join(ROOT, "sic_games", "src"))
import sic_games.climate as CL   # noqa: E402
from sic_games.phase1_model import TerrainWorld   # noqa: E402

FIRST = int(os.environ.get("DR_FIRST", "9000"))
GAP = int(os.environ.get("DR_GAP", "240"))
N = int(os.environ.get("DR_N", "20"))
LEN = int(os.environ.get("DR_LEN", "12"))
MULTS = [float(x) for x in os.environ.get("DR_MULTS", "0.85,0.70").split(",")]
FROM = int(os.environ.get("DR_SNAP_FROM", "8760"))
EVERY = int(os.environ.get("DR_SNAP_EVERY", "12"))
OUT = os.path.join(ROOT, "scratchpad", "drought_logs", f"yr1{os.environ.get('C_TAG', '')}.jsonl")
SHOCKS = [(FIRST + i * GAP, MULTS[i % len(MULTS)]) for i in range(N)]


def _mult(t):
    for onset, m in SHOCKS:
        if onset <= t < onset + LEN:
            return m
    return 1.0


_orig_build = CL.build_climate_field
_orig_step = TerrainWorld.step
_field = []
_sum = [0.0]
open(OUT, "w", encoding="utf-8").close()


def _step(self, *a, **k):
    if _field:
        _sum[0] += _mult(_field[-1].t)
    out = _orig_step(self, *a, **k)
    if self.step_count >= FROM and (self.step_count - FROM) % EVERY == 0:
        rec = self.raw_demographic_counters()
        rec.update(pop=len(self.agent_list), mult_sum=_sum[0], field_t=_field[-1].t if _field else None)
        with open(OUT, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec) + "\n")
    return out


def _build(*a, **k):
    field = _orig_build(*a, **k)
    field.regime_driver = CL.ClimateDriver(_mult, f"yr1(first={FIRST},gap={GAP},n={N},len={LEN},m={MULTS})")
    _field.append(field)
    print(f"YR1: {N} shocks, first {FIRST}, gap {GAP}, len {LEN}, mults {MULTS}, snaps from {FROM}", flush=True)
    return field


CL.build_climate_field = _build
TerrainWorld.step = _step
runpy.run_path(os.path.join(ROOT, "sic_games", "outputs", "substrate_run", "run_campaign.py"), run_name="__main__")
