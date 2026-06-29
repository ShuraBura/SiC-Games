"""capacity.py — the CC-1 NPP-derived carrying-capacity harvest field.

The PROVISIONAL CC-1 capacity field (MODEL_SPEC §4.3.1 / §4.8.4; DEFERRED_MECHANICS CC-1): a cell's extractable
kcal/step is set by its NPP-derived forager density, NOT the bare `forage_kcal` rate. This is the substrate the
demographic + emergent-bands validations run on (R-18/19, E.3-proper, the morph) — the bare forage field
(~1–8 persons/cell) is too poor to hold a band, while this field gives ~30–50 persons/cell so a cell can hold a
band and crowding is density-disease-regulated rather than starvation-limited.

    density = min(DENS_CAP, DENS_SLOPE · npp_gm2 / NPP_THRESH)   people/km²   [Tallavaara 2018; §4.3.1]
    E       = density · CELL_KM2 · burn                          kcal/step    (E/burn = supportable people/cell)

`patch=(x0, y0, size)` masks capacity to a sub-window (0 outside) so agents stay in a bounded-K region and the
population equilibrates (the validated single-patch harness; pass None for the full grid). Duck-typed to the
SugarField/TerrainField interface (`level`, `harvest`, `width`, `height`).
"""
from __future__ import annotations

import numpy as np

NPP_THRESH, DENS_SLOPE, DENS_CAP, CELL_KM2 = 1360.0, 0.3, 0.5, 100.0


class NPPCapacityField:
    """CC-1 NPP capacity field (see module docstring). `burn` = kcal/step so that E/burn = people/cell."""

    def __init__(self, fields, burn: float, patch: tuple[int, int, int] | None = None) -> None:
        npp = np.asarray(fields.npp_gm2, dtype=float)
        self.height, self.width = npp.shape
        dens = np.minimum(DENS_CAP, DENS_SLOPE * npp / NPP_THRESH)
        E = dens * CELL_KM2 * burn
        if patch is not None:
            x0, y0, size = patch
            mask = np.zeros_like(E, dtype=bool)
            mask[y0:y0 + size, x0:x0 + size] = True
            E[~mask] = 0.0
        self._E = E
        # patch carrying-capacity sum (people), land only — diagnostic / ceiling reference
        land = np.asarray(fields.isWater) == 0
        self.ceiling = float((dens * CELL_KM2)[land & (E > 0.0)].sum())

    def level(self, x: int, y: int) -> float:
        return float(self._E[y, x])

    def harvest(self, x: int, y: int) -> float:
        return float(self._E[y, x])
