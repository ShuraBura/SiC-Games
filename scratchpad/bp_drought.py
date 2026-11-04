"""R-106 Add.117 — DROUGHT TEST: does the canonical population CONTRACT under a climate shock and RECOVER after it?

The supervisor's arc goal: population must expand while food lasts and contract on external shocks (drought). No model
change: this wrapper runs the real `run_campaign.py` and sets a scripted `ClimateDriver.pulse` on the climate field,
which multiplies EVERY cell's yield (`ClimateField.level = base × mean × seasonal × interannual × regime`), so a drought
reaches the forage, the meat pool and the village catchment ceiling (Add.116 review: the ceiling is what binds at
villages; the tier-2 yield shock does not reach food).

Env:  DR_ONSET (step, default 9000), DR_LEN (steps, default 360 = 30 yr), DR_MULT (yield multiplier, e.g. 0.85 / 0.70).
Before the onset the driver returns 1.0 = the default regime multiplier and draws no RNG, so a drought run must match
its paired canon run row for row until DR_ONSET (the built-in control; checked by the analysis).

EXACT AGE-SPECIFIC MORTALITY (Add.125). Add.119's crude rates understate the response, because a fall in births lowers
the crude death rate by itself, and the trajectory's `m_*` rows are too coarse to difference. So this wrapper also saves
the raw life-table counters at the steps in DR_SNAPS (default: onset, end, end + 30 yr) to
scratchpad/drought_logs/lt<C_TAG>.json. Pure observer: it reads `raw_demographic_counters()` (a copy) after a step and
draws no RNG; the row-for-row control before the onset proves that it changes nothing.
"""
import json
import os
import runpy
import sys

ROOT = r"C:\Users\syatom\Projects\SiC Games"
sys.path.insert(0, os.path.join(ROOT, "sic_games", "src"))
import sic_games.climate as CL   # noqa: E402
from sic_games.phase1_model import TerrainWorld   # noqa: E402

ONSET = int(os.environ.get("DR_ONSET", "9000"))
LEN = int(os.environ.get("DR_LEN", "360"))
MULT = float(os.environ["DR_MULT"])
SNAPS = {int(x) for x in os.environ.get("DR_SNAPS", f"{ONSET},{ONSET + LEN},{ONSET + 2 * LEN}").split(",")}
SNAP_FILE = os.path.join(ROOT, "scratchpad", "drought_logs", f"lt{os.environ.get('C_TAG', '')}.json")

_orig_build = CL.build_climate_field
_orig_step = TerrainWorld.step
_saved = {}


def _step(self, *a, **k):
    out = _orig_step(self, *a, **k)
    if self.step_count in SNAPS and self.step_count not in _saved:
        _saved[self.step_count] = self.raw_demographic_counters()
        with open(SNAP_FILE, "w", encoding="utf-8") as fh:
            json.dump(_saved, fh)
    return out


def _build(*a, **k):
    field = _orig_build(*a, **k)
    field.regime_driver = CL.ClimateDriver.pulse(ONSET, LEN, MULT)
    print(f"DROUGHT: regime_driver = pulse(onset={ONSET}, len={LEN}, mult={MULT})", flush=True)
    return field


CL.build_climate_field = _build
TerrainWorld.step = _step
runpy.run_path(os.path.join(ROOT, "sic_games", "outputs", "substrate_run", "run_campaign.py"), run_name="__main__")
