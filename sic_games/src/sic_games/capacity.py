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

# CC-1 FITTED: Tallavaara et al. 2018 segmented (2-piece) regression of ln(density) on NPP (LITERATURE.md,
# extracted from their data-analyses SI + validated vs Dataset_4). density in #/100km² = persons/CELL (our cell =
# 100 km²), so `E = density·burn` directly (no ×CELL_KM2, unlike the linear-provisional per-km² form).
TALL_BP, TALL_INT, TALL_B1, TALL_U1 = 1371.664, -0.1352714, 0.0028623, -0.0030745


def density_tallavaara(npp_gm2):
    """persons per 100 km² (= per cell) from NPP (g/m²/yr) via the Tallavaara 2018 segmented regression:
    ln(d) = INT + B1·npp + U1·(npp−BP)₊ ; hump-shaped (rises then slightly declines above the ~1372 breakpoint)."""
    npp = np.asarray(npp_gm2, dtype=float)
    ln_d = TALL_INT + TALL_B1 * npp + np.where(npp > TALL_BP, TALL_U1 * (npp - TALL_BP), 0.0)
    return np.exp(ln_d)


class NPPCapacityField:
    """CC-1 NPP capacity field (see module docstring). `burn` = kcal/step so that E/burn = people/cell. `mode`:
    'tallavaara' = the FITTED segmented regression (persons/cell = density·burn); 'linear' = the provisional
    linear-clamp `min(0.5, 0.3·npp/1360)·100` (per-km²×100). Default 'linear' keeps prior runs bit-exact."""

    def __init__(self, fields, burn: float, patch: tuple[int, int, int] | None = None, mode: str = "linear") -> None:
        npp = np.asarray(fields.npp_gm2, dtype=float)
        self.height, self.width = npp.shape
        self.mode = mode
        if mode == "tallavaara":
            ppl_per_cell = density_tallavaara(npp)                     # #/100km² = persons/cell
        else:
            ppl_per_cell = np.minimum(DENS_CAP, DENS_SLOPE * npp / NPP_THRESH) * CELL_KM2   # per-km²×100
        E = ppl_per_cell * burn
        if patch is not None:
            x0, y0, size = patch
            mask = np.zeros_like(E, dtype=bool)
            mask[y0:y0 + size, x0:x0 + size] = True
            E[~mask] = 0.0
        self._E = E
        # patch carrying-capacity sum (people), land only — diagnostic / ceiling reference
        land = np.asarray(fields.isWater) == 0
        self.ceiling = float(ppl_per_cell[land & (E > 0.0)].sum())

    def level(self, x: int, y: int) -> float:
        return float(self._E[y, x])

    def harvest(self, x: int, y: int) -> float:
        return float(self._E[y, x])
