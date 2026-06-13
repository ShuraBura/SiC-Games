"""terrain.py — Stage 7 terrain generator (production Python port).

Port of sic_terrain_prototype.html into Python/numpy.
Pipeline: elevation (fbm+ridge) → water → rivers → wateracc → moisture →
          NPP/forestness → forage/game/cost/risk → biome classification.

All terrain fields are precomputed once and frozen (non-writeable).
Determinism contract: same (knobs, seedStr) → byte-identical arrays.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass

import numpy as np

# ── Constants ─────────────────────────────────────────────────────────────

N              = 100        # grid side (100×100 cells)
RELIEF_FLOOR_M = 120.0      # peak-to-trough at relief=0 (gentle rolling)
RELIEF_CEIL_M  = 2500.0     # peak-to-trough at relief=1 (mountainous)
SEA_LEVEL_M    = 0.0
CELL_EDGE_M    = 10000.0    # cell edge in metres (100 km²/cell)
W_FOREST       = 0.45       # forestness >= this → closed-canopy forest
W_SAV          = 0.18       # forestness in [W_SAV, W_FOREST) → savanna/woodland

BIOME_WATER    = 0
BIOME_WETLAND  = 1
BIOME_FOREST   = 2
BIOME_SAVANNA  = 3
BIOME_GRASS    = 4
BIOME_DESERT   = 5
BIOME_MOUNTAIN = 6

# ── Phase 1 Stage 1 constants ──────────────────────────────────────────────
# All forage values trace to LITERATURE.md Survey A (canonical home).
NPP_GM2_SCALE = 3400.0        # npp_gm2 = npp * NPP_GM2_SCALE
                               # Anchor: generator forest-onset (npp≈0.4) →
                               # Tallavaara 2018 saturation ~1360 g/m²/yr (single-point assertion)
SHORE_BONUS_KCAL = 1491.5     # Bird 1997 Meriam reef-flat intertidal mean (kcal/forager-hr)
FORAGE_KCAL_TARGETS = {       # per-biome target means (kcal/forager-hr)
    BIOME_WETLAND:  1428.3,   # Cunningham, Okavango "Wet"
    BIOME_FOREST:   2630.0,   # Hill 1987, Ache palm
    BIOME_SAVANNA:   257.7,   # Berbesque & Marlowe 2009, Hadza tuber (Table 4)
    BIOME_GRASS:    1125.0,   # Hurtado & Hill 1987, Cuiva root collecting
    BIOME_DESERT:   1200.0,   # PROVISIONAL; O'Connell & Hawkes 1984 range 650-1925
    BIOME_MOUNTAIN: 5387.0,   # Rhode & Rhode 2015, limber pine unhulled
}

# ── Phase 1 Stage 1b constants ─────────────────────────────────────────────
# Provisional exterior-water guard threshold.
# Derivation (P1S1b blueprint §3): for N=100 with a t-cell ocean rim,
# rim cells = N² − (N−2t)²:  t=1→396 (0.040), t=2→784 (0.078), t=3→1164 (0.116).
# A 2–3 cell rim allows naturalistic edge roughness; threshold = 0.12 (t=3 bound).
# PROVISIONAL — confirm against sweep distribution before treating as final.
EXTERIOR_WATER_CEILING = 0.12

_NOISE_G = 257  # noise grid side (wraps on itself)

# ── PRNG (mulberry32 + FNV-1a hashSeed) ───────────────────────────────────

_M32 = 0xFFFF_FFFF


def _i32(x: int) -> int:
    """Signed int32 (JavaScript |0)."""
    x &= _M32
    return x - 0x1_0000_0000 if x >= 0x8000_0000 else x


def _mul32(a: int, b: int) -> int:
    """32-bit signed multiply (JavaScript Math.imul)."""
    return _i32((a & _M32) * (b & _M32))


def _u(x: int, n: int) -> int:
    """Unsigned right shift n bits (JavaScript >>>)."""
    return (x & _M32) >> n


def hash_seed(s: str) -> int:
    """FNV-1a string → uint32. Matches prototype hashSeed(s)."""
    h = 2166136261
    for ch in s:
        h ^= ord(ch)
        h = _mul32(h, 16777619) & _M32
    return h & _M32


def _mulberry32_generate(seed: int, count: int) -> np.ndarray:
    """Generate count float64 values from mulberry32(seed). Matches JS exactly."""
    a = _i32(seed)
    out = np.empty(count, dtype=np.float64)
    ADD = 0x6D2B79F5
    for i in range(count):
        a = _i32(a + ADD)
        t = _mul32(a ^ _u(a, 15), a | 1)
        t = _i32(t + _mul32(t ^ _u(t, 7), t | 61)) ^ t
        out[i] = _u(t ^ _u(t, 14), 0) / 4_294_967_296
    return out


# ── Value-noise ────────────────────────────────────────────────────────────

def _make_noise_grid(seed: int) -> np.ndarray:
    """Build 257×257 noise grid as float32 (matches JS Float32Array storage)."""
    vals = _mulberry32_generate(seed, _NOISE_G * _NOISE_G)
    return vals.astype(np.float32).reshape(_NOISE_G, _NOISE_G)


def _noise_at(grid_f64: np.ndarray, x_arr: np.ndarray, y_arr: np.ndarray) -> np.ndarray:
    """Bilinear interpolation on a (257,257) float64 grid.

    smooth(t) = t*t*(3-2*t) — matches prototype makeNoise/at.
    Vectorized over x_arr / y_arr arrays.
    """
    G = _NOISE_G
    xi = np.floor(x_arr).astype(np.int64)
    yi = np.floor(y_arr).astype(np.int64)
    xf = x_arr - xi.astype(np.float64)
    yf = y_arr - yi.astype(np.float64)
    x0 = xi % G;  x1 = (xi + 1) % G
    y0 = yi % G;  y1 = (yi + 1) % G
    a = grid_f64[y0, x0]; b = grid_f64[y0, x1]
    c = grid_f64[y1, x0]; d = grid_f64[y1, x1]
    u = xf * xf * (3 - 2 * xf)
    v = yf * yf * (3 - 2 * yf)
    return (a * (1 - u) + b * u) * (1 - v) + (c * (1 - u) + d * u) * v


def _fbm(grid_f64: np.ndarray, x_arr: np.ndarray, y_arr: np.ndarray,
         oct: int, lac: float, gain: float) -> np.ndarray:
    """Fractal Brownian Motion over coordinate arrays. Matches prototype fbm()."""
    amp = 1.0; freq = 1.0
    total = np.zeros(len(x_arr), dtype=np.float64)
    norm = 0.0
    for _ in range(oct):
        total += amp * _noise_at(grid_f64, x_arr * freq, y_arr * freq)
        norm += amp
        amp *= gain; freq *= lac
    return total / norm


# ── WorldFields ────────────────────────────────────────────────────────────

@dataclass
class WorldFields:
    """Frozen terrain field set. All arrays non-writeable after generate_world()."""
    elev:          np.ndarray   # (N,N) float64 normalised [0,1]
    slope:         np.ndarray   # (N,N) float64 normalised [0,1]
    slopeDeg:      np.ndarray   # (N,N) float64 degrees
    wateracc:      np.ndarray   # (N,N) float64 [0,1]
    isWater:       np.ndarray   # (N,N) uint8  {0,1}
    isRiver:       np.ndarray   # (N,N) uint8  {0,1}
    forage:        np.ndarray   # (N,N) float64 [0,1] (original normalised field)
    game:          np.ndarray   # (N,N) float64 [0,1]
    cost:          np.ndarray   # (N,N) float64 [0,1]
    neighbour_cost: np.ndarray  # (N,N,4) float64; d=0 N, d=1 S, d=2 W, d=3 E
    risk:          np.ndarray   # (N,N) float64 [0.02,1]
    biome:         np.ndarray   # (N,N) uint8  biome codes 0-6
    npp:           np.ndarray   # (N,N) float64 [0,1]
    forestness:    np.ndarray   # (N,N) float64 [0,1]
    dist:          np.ndarray   # (N,N) float64 BFS distance from water/river
    reliefAmpM:    float
    SEA_LEVEL_M:   float = 0.0
    # Phase 1 Stage 1 fields (added 2026-06-12)
    forage_kcal:   np.ndarray = None  # (N,N) float64 kcal/forager-hr (per-biome + shore bonus)
    npp_gm2:       np.ndarray = None  # (N,N) float64 g/m2/yr (Tallavaara 2018 anchor)
    is_shore:      np.ndarray = None  # (N,N) uint8 land cells with >=1 water nbr (4-nbr)


# ── Water-body connected components ───────────────────────────────────────

def _water_bodies(isWater: np.ndarray) -> tuple[int, int]:
    """Return (n_bodies, largest_body_size) using 4-neighbor BFS on water mask."""
    visited = np.zeros((N, N), dtype=bool)
    n_bodies = 0; largest = 0
    for r0 in range(N):
        for c0 in range(N):
            if not isWater[r0, c0] or visited[r0, c0]:
                continue
            n_bodies += 1; size = 0
            q: deque = deque([(r0, c0)])
            visited[r0, c0] = True
            while q:
                r, c = q.popleft(); size += 1
                for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    nr, nc_ = r + dr, c + dc
                    if 0 <= nr < N and 0 <= nc_ < N and isWater[nr, nc_] and not visited[nr, nc_]:
                        visited[nr, nc_] = True; q.append((nr, nc_))
            if size > largest: largest = size
    return n_bodies, largest


def _classify_water_components(
    isWater: np.ndarray,
) -> tuple[int, int, int, int, int, "np.ndarray | None"]:
    """Classify water connected components (4-nbr) into exterior vs interior.

    A component is exterior if any cell touches the grid boundary
    (row 0, row N-1, col 0, or col N-1); interior otherwise.

    Returns:
        (exterior_cells, interior_cells, n_exterior, n_interior,
         largest_exterior_cells, largest_exterior_mask)
    largest_exterior_mask is a (N,N) bool array for the largest exterior
    component, or None if there are no exterior bodies.
    """
    visited = np.zeros((N, N), dtype=bool)
    exterior_cells = 0
    interior_cells = 0
    n_exterior = 0
    n_interior = 0
    largest_ext_cells = 0
    largest_ext_mask: "np.ndarray | None" = None

    for r0 in range(N):
        for c0 in range(N):
            if not isWater[r0, c0] or visited[r0, c0]:
                continue
            component: list[tuple[int, int]] = []
            q: deque = deque([(r0, c0)])
            visited[r0, c0] = True
            is_ext = False
            while q:
                r, c = q.popleft()
                component.append((r, c))
                if r == 0 or r == N - 1 or c == 0 or c == N - 1:
                    is_ext = True
                for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    nr, nc_ = r + dr, c + dc
                    if (0 <= nr < N and 0 <= nc_ < N
                            and isWater[nr, nc_] and not visited[nr, nc_]):
                        visited[nr, nc_] = True
                        q.append((nr, nc_))
            size = len(component)
            if is_ext:
                n_exterior += 1
                exterior_cells += size
                if size > largest_ext_cells:
                    largest_ext_cells = size
                    largest_ext_mask = np.zeros((N, N), dtype=bool)
                    for r, c in component:
                        largest_ext_mask[r, c] = True
            else:
                n_interior += 1
                interior_cells += size

    return (exterior_cells, interior_cells, n_exterior, n_interior,
            largest_ext_cells, largest_ext_mask)


# ── Main generator ─────────────────────────────────────────────────────────

def generate_world(knobs: dict) -> WorldFields:
    """Generate terrain from knob dict; return frozen WorldFields.

    knobs keys: relief, rough, waterK, forestK, aridK, seedStr (string).
    Determinism: same (knobs, seedStr) → byte-identical arrays.
    """
    relief  = float(knobs['relief'])
    rough   = float(knobs['rough'])
    waterK  = float(knobs['waterK'])
    forestK = float(knobs['forestK'])
    aridK   = float(knobs['aridK'])
    seed_str = str(knobs.get('seedStr', knobs.get('seed', '0')))

    seed  = hash_seed(seed_str)
    seed2 = seed ^ 0x9e3779b9

    # Build noise grids (float32 → float64 for computation, matching JS semantics)
    g1 = _make_noise_grid(seed).astype(np.float64)
    g2 = _make_noise_grid(seed2).astype(np.float64)

    # ── Elevation ──────────────────────────────────────────────────────
    gain  = 0.35 + rough * 0.45
    scale = 3.2
    ys, xs = np.mgrid[0:N, 0:N]
    nx = (xs.astype(np.float64) / N * scale).ravel()
    ny = (ys.astype(np.float64) / N * scale).ravel()

    e_fbm = _fbm(g1, nx, ny, 5, 2.0, gain)
    r_fbm = _fbm(g2, nx * 1.3 + 10, ny * 1.3 + 10, 4, 2.0, 0.5)
    ridge = 1.0 - np.abs(2.0 * r_fbm - 1.0)
    e_raw = e_fbm * (1 - relief * 0.6) + ridge * (relief * 0.6)
    moist_flat = _fbm(g2, nx * 0.8 + 5, ny * 0.8 + 5, 4, 2.0, 0.45)

    reliefAmpM = RELIEF_FLOOR_M + (RELIEF_CEIL_M - RELIEF_FLOOR_M) * relief

    # Normalise elevation to [0,1]
    emin, emax = e_raw.min(), e_raw.max()
    elev = np.clip((e_raw - emin) / (emax - emin + 1e-9), 0.0, 1.0).reshape(N, N)
    moist = moist_flat.reshape(N, N)

    # ── Water level & open-water mask ──────────────────────────────────
    waterLevel = (waterK ** 1.2) * 0.42
    isWater = (elev < waterLevel).astype(np.uint8)

    # ── Flow accumulation (D8, 8-neighbour) → rivers ───────────────────
    # Note: prototype uses 8 neighbours (blueprint text says 4 — prototype governs)
    elev_flat = elev.ravel()
    isWater_flat = isWater.ravel()
    land_idx = np.where(isWater_flat == 0)[0]
    # Sort land cells by descending elevation
    order = land_idx[np.argsort(-elev_flat[land_idx], kind='stable')]

    flow = np.ones(N * N, dtype=np.float64)
    D8 = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)]
    for idx in order:
        x_c = int(idx % N)
        y_c = int(idx // N)
        lowest_j = -1
        le = float(elev_flat[idx])
        for dx, dy in D8:
            xx, yy = x_c + dx, y_c + dy
            if 0 <= xx < N and 0 <= yy < N:
                j = yy * N + xx
                ej = float(elev_flat[j])
                if ej < le:
                    le = ej
                    lowest_j = j
        if lowest_j >= 0:
            flow[lowest_j] += flow[idx]

    land_flow = flow[land_idx]
    fmax = float(land_flow.max()) if len(land_flow) > 0 else 1.0
    riverThresh = fmax * (0.10 - waterK * 0.06)
    isRiver_flat = ((isWater_flat == 0) & (flow > riverThresh)).astype(np.uint8)
    isRiver = isRiver_flat.reshape(N, N)

    # ── Water-accessibility BFS (4-neighbour) ──────────────────────────
    dist_flat = np.full(N * N, np.inf, dtype=np.float64)
    q: deque = deque()
    for i in range(N * N):
        if isWater_flat[i] or isRiver_flat[i]:
            dist_flat[i] = 0.0
            q.append(i)

    D4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    while q:
        i = q.popleft()
        x_c, y_c = int(i % N), int(i // N)
        d = dist_flat[i]
        for dx, dy in D4:
            xx, yy = x_c + dx, y_c + dy
            if 0 <= xx < N and 0 <= yy < N:
                j = yy * N + xx
                if dist_flat[j] > d + 1:
                    dist_flat[j] = d + 1
                    q.append(j)

    dist = dist_flat.reshape(N, N)
    decay = 0.30 + (1 - waterK) * 0.22
    wateracc = np.where(isWater, 1.0, np.exp(-decay * dist))

    # ── Slope (normalised) ─────────────────────────────────────────────
    # Central differences with boundary replication
    xl = np.empty_like(elev); xl[:, 1:] = elev[:, :-1]; xl[:, 0]  = elev[:, 0]
    xr = np.empty_like(elev); xr[:, :-1] = elev[:, 1:]; xr[:, -1] = elev[:, -1]
    yu = np.empty_like(elev); yu[1:, :]  = elev[:-1, :]; yu[0, :]  = elev[0, :]
    yd = np.empty_like(elev); yd[:-1, :] = elev[1:, :]; yd[-1, :]  = elev[-1, :]

    slope_raw = np.sqrt((xr - xl) ** 2 + (yd - yu) ** 2) * 0.5
    smax = float(slope_raw.max())
    slope = slope_raw / (smax + 1e-9)

    # Absolute slope in degrees (physical units: CELL_EDGE_M = 10000 m)
    dzx = (xr - xl) * reliefAmpM / (2 * CELL_EDGE_M)
    dzy = (yd - yu) * reliefAmpM / (2 * CELL_EDGE_M)
    slopeDeg = np.degrees(np.arctan(np.sqrt(dzx ** 2 + dzy ** 2)))

    # ── Effective moisture ─────────────────────────────────────────────
    wet = np.clip((0.45 * moist + 0.55 * wateracc) * (1 - aridK * 0.92), 0.0, 1.0)

    # ── NPP ────────────────────────────────────────────────────────────
    elev_pen = 1.0 - np.clip((elev - 0.6) / 0.4, 0.0, None)
    slope_pen = 1.0 - slope * 0.7
    npp = np.where(isWater, 0.0, np.maximum(0.0, wet * elev_pen * slope_pen))

    # ── Forestness ─────────────────────────────────────────────────────
    forestness = np.where(isWater, 0.0,
                          np.clip(wet * 0.7 + forestK * 0.5 - elev * 0.3, 0.0, 1.0))

    # ── Forage ─────────────────────────────────────────────────────────
    forage = np.where(isWater, 0.0, np.minimum(1.0, npp * (0.6 + 0.6 * forestness)))

    # ── Game ───────────────────────────────────────────────────────────
    hump = np.exp(-((npp - 0.5) / 0.22) ** 2)
    game = np.where(isWater, 0.0, np.minimum(1.0, hump * (0.35 + 0.75 * (1.0 - forestness))))

    # ── Movement cost ──────────────────────────────────────────────────
    cost_land = np.minimum(1.0, 0.15 + slope * 0.85 + np.maximum(0.0, elev - 0.7))
    cost = np.where(isWater, 1.0, cost_land)

    # ── Base mortality risk ─────────────────────────────────────────────
    exposure = slope * 0.5 + np.maximum(0.0, elev - 0.55) * 0.6
    thirst   = (1.0 - wateracc) * 0.4
    shelter  = forestness * 0.15
    risk = np.where(isWater, 0.85,
                    np.clip(0.12 + exposure + thirst - shelter, 0.02, 1.0))

    # ── Biome classification (woody-cover ladder) ───────────────────────
    mtn_elev_thresh  = 0.72 + (1 - relief) * 0.5
    mtn_slope_thresh = 0.18 + (1 - relief) * 0.4

    is_land    = (isWater == 0)
    is_mtn     = is_land & (elev > mtn_elev_thresh) & (slope > mtn_slope_thresh)
    is_desert  = is_land & ~is_mtn & (npp < 0.10)
    is_wetland = is_land & ~is_mtn & ~is_desert & (dist <= 2) & (npp > 0.45) & (slope < 0.12)
    remaining  = is_land & ~is_mtn & ~is_desert & ~is_wetland
    is_forest  = remaining & (forestness >= W_FOREST)
    is_savanna = remaining & (forestness >= W_SAV) & (forestness < W_FOREST)
    is_grass   = remaining & (forestness < W_SAV)

    biome = np.zeros((N, N), dtype=np.uint8)  # default 0 = BIOME_WATER
    biome[is_mtn]     = BIOME_MOUNTAIN
    biome[is_desert]  = BIOME_DESERT
    biome[is_wetland] = BIOME_WETLAND
    biome[is_forest]  = BIOME_FOREST
    biome[is_savanna] = BIOME_SAVANNA
    biome[is_grass]   = BIOME_GRASS

    # ── NPP physical units (Task 4 — Tallavaara 2018 single-point anchor) ──
    # Anchor: generator forest-onset npp≈0.4 → empirical saturation ~1360 g/m²/yr.
    # Linear transfer: npp_gm2 = npp * (1360/0.4) = npp * 3400. Land-only interpretation;
    # water cells have npp=0, so npp_gm2=0 is consistent (no meaning on water).
    npp_gm2 = npp * NPP_GM2_SCALE

    # ── Shore mask: land cells with >=1 water neighbor (4-nbr, non-toroidal) ─
    padded_w = np.pad(isWater, 1, mode='constant', constant_values=0)
    has_water_nbr = ((padded_w[:-2, 1:-1] | padded_w[2:, 1:-1] |
                      padded_w[1:-1, :-2] | padded_w[1:-1, 2:]) > 0)
    is_shore = ((isWater == 0) & has_water_nbr).astype(np.uint8)

    # ── forage_kcal: per-biome mean-scaling (Task 1) + shore bonus (Task 3) ─
    # Original normalised forage[] is preserved. forage_kcal is a separate field.
    forage_kcal = np.zeros((N, N), dtype=np.float64)
    for b_code, target_mean in FORAGE_KCAL_TARGETS.items():
        mask = (biome == b_code)
        if not mask.any():
            continue                       # absent biome: cells stay 0, logged in characterize_map
        mean_norm = float(forage[mask].mean())
        if mean_norm == 0.0:
            continue                       # zero-mean biome: avoid divide-by-zero; stays 0
        forage_kcal[mask] = forage[mask] * (target_mean / mean_norm)
    # Shore modifier: additive bonus on land-shore cells (1491.5 kcal/hr; Bird 1997)
    forage_kcal += is_shore.astype(np.float64) * SHORE_BONUS_KCAL

    # ── Neighbour cost (N,N,4): d=0 N, d=1 S, d=2 W, d=3 E ────────────
    nc = np.ones((N, N, 4), dtype=np.float64)   # sentinel = 1.0 at edges
    nc[1:, :, 0]  = cost[:-1, :]   # north: target (y-1, x)
    nc[:-1, :, 1] = cost[1:, :]    # south: target (y+1, x)
    nc[:, 1:, 2]  = cost[:, :-1]   # west:  target (y, x-1)
    nc[:, :-1, 3] = cost[:, 1:]    # east:  target (y, x+1)

    # ── Freeze all arrays ──────────────────────────────────────────────
    for arr in (elev, slope, slopeDeg, wateracc, isWater, isRiver,
                forage, game, cost, nc, risk, biome, npp, forestness, dist,
                npp_gm2, is_shore, forage_kcal):
        arr.flags.writeable = False

    return WorldFields(
        elev=elev, slope=slope, slopeDeg=slopeDeg,
        wateracc=wateracc, isWater=isWater, isRiver=isRiver,
        forage=forage, game=game, cost=cost, neighbour_cost=nc,
        risk=risk, biome=biome, npp=npp, forestness=forestness,
        dist=dist, reliefAmpM=reliefAmpM, SEA_LEVEL_M=SEA_LEVEL_M,
        forage_kcal=forage_kcal, npp_gm2=npp_gm2, is_shore=is_shore,
    )


# ── characterize_map ────────────────────────────────────────────────────────

def characterize_map(F: WorldFields, initial_agent_count: int = 500) -> dict:
    """Per-map diagnostic vector. Saved alongside every generated map.

    Vector keys match the oracle battery JSON exactly.
    initial_agent_count: used for Task 6 Guard A (habitable_cell_count >= max(N_init, 50)).
    """
    n = N * N
    land = 0; water = 0; river = 0
    counts = np.zeros(7, dtype=np.int64)
    slope_sum = 0.0; slope_max = 0.0; steep = 0
    e_min = np.inf; e_max = -np.inf; e_sum = 0.0

    for i in range(n):
        b = int(F.biome.ravel()[i])
        counts[b] += 1
        if F.isWater.ravel()[i]:
            water += 1
            continue
        land += 1
        if F.isRiver.ravel()[i]:
            river += 1
        sd = float(F.slopeDeg.ravel()[i])
        slope_sum += sd
        if sd > slope_max:
            slope_max = sd
        if sd > 15.0:
            steep += 1
        m = float(F.elev.ravel()[i]) * F.reliefAmpM + F.SEA_LEVEL_M
        if m < e_min: e_min = m
        if m > e_max: e_max = m
        e_sum += m

    def fr(code):
        return counts[code] / land * 100 if land > 0 else 0.0

    frac = {
        'wetland':   fr(BIOME_WETLAND),
        'forest':    fr(BIOME_FOREST),
        'savanna':   fr(BIOME_SAVANNA),
        'grassland': fr(BIOME_GRASS),
        'desert':    fr(BIOME_DESERT),
        'mountain':  fr(BIOME_MOUNTAIN),
    }

    # 7×7 adjacency (shared-edge counts, 4-neighbour, all biomes)
    biome_flat = F.biome
    adj = [[0] * 7 for _ in range(7)]
    for row in range(N):
        for col in range(N):
            bi = int(biome_flat[row, col])
            if col + 1 < N:
                bj = int(biome_flat[row, col + 1])
                adj[bi][bj] += 1; adj[bj][bi] += 1
            if row + 1 < N:
                bj = int(biome_flat[row + 1, col])
                adj[bi][bj] += 1; adj[bj][bi] += 1

    # forestTouchSavanna: forest external edges touching savanna / all forest external
    f_edge_other = sum(adj[BIOME_FOREST][b] for b in range(7) if b != BIOME_FOREST)
    forest_touch_sav  = adj[BIOME_FOREST][BIOME_SAVANNA] / f_edge_other if f_edge_other > 0 else 0.0
    forest_touch_grass = adj[BIOME_FOREST][BIOME_GRASS]  / f_edge_other if f_edge_other > 0 else 0.0

    # gameHumpPeak: NPP bin where mean game is maximal (bins=20)
    bins = 20
    g_sum = np.zeros(bins); g_cnt = np.zeros(bins)
    npp_f = F.npp.ravel(); game_f = F.game.ravel(); iw = F.isWater.ravel()
    for i in range(n):
        if iw[i]: continue
        bb = min(bins - 1, int(np.floor(npp_f[i] * bins)))
        g_sum[bb] += game_f[i]; g_cnt[bb] += 1
    peak_bin = -1; peak_v = -1.0
    for b in range(bins):
        if g_cnt[b] < 3: continue
        m = g_sum[b] / g_cnt[b]
        if m > peak_v: peak_v = m; peak_bin = b
    game_hump_peak = peak_bin / bins if peak_bin >= 0 else None

    # Task 2: coast/water-body diagnostics ─────────────────────────────
    n_wb, largest_wb = _water_bodies(F.isWater)
    shore_count = int(F.is_shore.sum()) if F.is_shore is not None else 0
    total_cells = N * N

    # P1S1b — exterior/interior water decomposition ─────────────────────
    # Convention: water-extent fields use total-cell denominator (consistent with
    # shore_cell_fraction, waterPct). shoreline_fraction uses land denominator
    # (consistent with per-biome fractions). See P1S1b blueprint §4.3.
    (ext_cells, int_cells, n_ext_bodies, n_int_bodies,
     largest_ext_cells, largest_ext_mask) = _classify_water_components(F.isWater)

    exterior_water_frac = ext_cells / total_cells
    interior_water_frac = int_cells / total_cells
    shoreline_frac = shore_count / land if land > 0 else 0.0

    if largest_ext_mask is not None and largest_ext_cells > 0:
        water_mask = F.isWater.astype(bool)
        padded_ext = np.pad(largest_ext_mask, 1, mode='constant', constant_values=False)
        adj_land = (~water_mask) & (
            padded_ext[:-2, 1:-1] | padded_ext[2:, 1:-1] |
            padded_ext[1:-1, :-2] | padded_ext[1:-1, 2:]
        )
        largest_exterior_shore_to_area = int(adj_land.sum()) / largest_ext_cells
    else:
        largest_exterior_shore_to_area = 0.0
    # NOTE: largest_exterior_shore_to_area measures crinkliness-per-unit-water
    # (shoreline / body-area ratio), NOT coastline length. A large sea with a
    # long coast scores LOW s2a because the body-area denominator is large.
    # Do NOT use s2a to infer presence/absence of coastal morphology.
    # Absolute exterior shoreline (deferred to §STAGE-GEOSTRUCT) is the correct
    # coastline-length statistic.

    # Task 5: habitability coordinates ─────────────────────────────────
    desert_frac   = counts[BIOME_DESERT]   / land if land > 0 else 0.0
    mountain_frac = counts[BIOME_MOUNTAIN] / land if land > 0 else 0.0
    habitable_cell_count = land              # land = land-only; water excluded
    habitable_cell_frac  = land / total_cells
    mean_npp_gm2 = (float(F.npp_gm2[~F.isWater.astype(bool)].mean())
                    if F.npp_gm2 is not None and land > 0 else 0.0)

    # forage_kcal absent-biome log ─────────────────────────────────────
    absent_biomes = [b for b in FORAGE_KCAL_TARGETS if counts[b] == 0]

    # Task 6 + P1S1b: validity guards ────────────────────────────────────
    floor = max(initial_agent_count, 50)
    guard_a_fail = habitable_cell_count < floor
    guard_b_fail = any(counts[b] / total_cells >= 0.95 for b in range(7))
    # Exterior-water guard (P1S1b): maps with mostly-ocean are not a testbed.
    # PROVISIONAL threshold — see EXTERIOR_WATER_CEILING constant comment.
    guard_exterior_water_fail = exterior_water_frac > EXTERIOR_WATER_CEILING
    invalid_substrate = guard_a_fail or guard_b_fail or guard_exterior_water_fail

    return {
        'waterPct':        water / total_cells * 100,
        'riverPct':        river / land * 100 if land > 0 else 0.0,
        'wetlandPct':      frac['wetland'],
        'hydratedPct':     (water + river + int(counts[BIOME_WETLAND])) / total_cells * 100,
        'landCells':       land,
        'riverCells':      river,
        'drainagePct':     river / land * 100 if land > 0 else 0.0,
        'reliefEnvelopeM': e_max - e_min,
        'elevMinM':        e_min,
        'elevMaxM':        e_max,
        'elevMeanM':       e_sum / max(1, land),
        'meanSlopeDeg':    slope_sum / max(1, land),
        'maxSlopeDeg':     slope_max,
        'steepLandPct':    steep / max(1, land) * 100,
        'biomeFrac':       frac,
        'gameHumpPeak':    game_hump_peak,
        'adjacency':       adj,
        'forestTouchSavanna':       forest_touch_sav,
        'forestTouchGrassland':     forest_touch_grass,
        'forestSavannaSharedEdges': adj[BIOME_FOREST][BIOME_SAVANNA],
        # Task 2 — coast/water-body diagnostics
        'shore_cell_count':    shore_count,
        'shore_cell_fraction': shore_count / total_cells,
        'n_water_bodies':      n_wb,
        'largest_body_fraction': largest_wb / total_cells,
        # P1S1b — exterior/interior water decomposition
        'exterior_water_fraction':        exterior_water_frac,
        'interior_water_fraction':        interior_water_frac,
        'n_interior_bodies':              n_int_bodies,
        'n_exterior_bodies':              n_ext_bodies,
        'shoreline_fraction':             shoreline_frac,
        'largest_exterior_body_cells':    largest_ext_cells,
        'largest_exterior_shore_to_area': largest_exterior_shore_to_area,
        # Task 5 — habitability coordinates
        'desert_fraction':         desert_frac,
        'mountain_fraction':       mountain_frac,
        'mean_npp_gm2':            mean_npp_gm2,
        'habitable_cell_fraction': habitable_cell_frac,
        'habitable_cell_count':    habitable_cell_count,
        # Task 6 + P1S1b — validity guards
        'invalid_substrate':          invalid_substrate,
        'guard_a_fail':               guard_a_fail,
        'guard_b_fail':               guard_b_fail,
        'guard_exterior_water_fail':  guard_exterior_water_fail,
        # forage_kcal diagnostics
        'absent_biomes_forage': absent_biomes,
    }
