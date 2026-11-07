"""Add.130: dump the static banking gate of each world (`in_owz` by cell), to join it to the village log. Reads state only, 2 steps per world."""
import os
import runpy
import sys

import numpy as np

ROOT = r"C:\Users\syatom\Projects\SiC Games"
sys.path.insert(0, os.path.join(ROOT, "sic_games", "src"))
from sic_games.phase1_model import TerrainWorld   # noqa: E402

_s = TerrainWorld.step
OUT = os.path.join(ROOT, "scratchpad", "design_logs", f"owz{os.environ['C_TAG']}.npz")


def step(self, *a, **k):
    r = _s(self, *a, **k)
    if self.step_count == 1:
        from sic_games.climate import seasonal_amplitude_field
        d = self._demog
        amp = self._seasonal_amp if self._seasonal_amp is not None else seasonal_amplitude_field(self._fields.biome)
        np.savez(OUT, temperature=np.asarray(self._fields.temperature), amp=np.asarray(amp), biome=np.asarray(self._fields.biome), water=np.asarray(self._fields.isWater),
                 tthr=d.storage_temp_threshold_c, athr=d.storage_seasonality_threshold, union=bool(getattr(d, "enable_storage_seasonal_union", False)), seas=bool(getattr(d, "storage_seasonality_gated", False)))
    return r


TerrainWorld.step = step
runpy.run_path(os.path.join(ROOT, "sic_games", "outputs", "substrate_run", "run_campaign.py"), run_name="__main__")
