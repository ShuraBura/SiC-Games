"""R-106 Add.117 — DROUGHT TEST: does the canonical population CONTRACT under a climate shock and RECOVER after it?

The supervisor's arc goal: population must expand while food lasts and contract on external shocks (drought). No model
change: this wrapper runs the real `run_campaign.py` and sets a scripted `ClimateDriver.pulse` on the climate field,
which multiplies EVERY cell's yield (`ClimateField.level = base × mean × seasonal × interannual × regime`), so a drought
reaches the forage, the meat pool and the village catchment ceiling (Add.116 review: the ceiling is what binds at
villages; the tier-2 yield shock does not reach food).

Env:  DR_ONSET (step, default 9000), DR_LEN (steps, default 360 = 30 yr), DR_MULT (yield multiplier, e.g. 0.85 / 0.70).
Before the onset the driver returns 1.0 = the default regime multiplier and draws no RNG, so a drought run must match
its paired canon run row for row until DR_ONSET (the built-in control; checked by the analysis).
"""
import os
import runpy
import sys

ROOT = r"C:\Users\syatom\Projects\SiC Games"
sys.path.insert(0, os.path.join(ROOT, "sic_games", "src"))
import sic_games.climate as CL   # noqa: E402

ONSET = int(os.environ.get("DR_ONSET", "9000"))
LEN = int(os.environ.get("DR_LEN", "360"))
MULT = float(os.environ["DR_MULT"])

_orig_build = CL.build_climate_field


def _build(*a, **k):
    field = _orig_build(*a, **k)
    field.regime_driver = CL.ClimateDriver.pulse(ONSET, LEN, MULT)
    print(f"DROUGHT: regime_driver = pulse(onset={ONSET}, len={LEN}, mult={MULT})", flush=True)
    return field


CL.build_climate_field = _build
runpy.run_path(os.path.join(ROOT, "sic_games", "outputs", "substrate_run", "run_campaign.py"), run_name="__main__")
