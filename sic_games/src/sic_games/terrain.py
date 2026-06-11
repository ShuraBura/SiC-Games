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
    forage:        np.ndarray   # (N,N) float64 [0,1]
    game:          np.ndarray   # (N,N) float64 [0,1]
    cost:          np.ndarray   # (N,N) float64 [0,1]
    neighbour_cost: np.ndarray  # (N,N,4) float64; d=0 N, d=1 S, d=2 W, d=3 E
    risk:          np.ndarray   # (N,N) float64 [0.02,1]
    biome:         np.ndarray   # (N,N) uint8  biome codes 0–6
    npp:           np.ndarray   # (N,N) float64 [0,1]
    forestness:    np.ndarray   # (N,N) float64 [0,1]
    dist:          np.ndarray   # (N,N) float64 BFS distance from water/river
    reliefAmpM:    float
    SEA_LEVEL_M:   float = 0.0


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

    # ── Neighbour cost (N,N,4): d=0 N, d=1 S, d=2 W, d=3 E ────────────
    nc = np.ones((N, N, 4), dtype=np.float64)   # sentinel = 1.0 at edges
    nc[1:, :, 0]  = cost[:-1, :]   # north: target (y-1, x)
    nc[:-1, :, 1] = cost[1:, :]    # south: target (y+1, x)
    nc[:, 1:, 2]  = cost[:, :-1]   # west:  target (y, x-1)
    nc[:, :-1, 3] = cost[:, 1:]    # east:  target (y, x+1)

    # ── Freeze all arrays ──────────────────────────────────────────────
    for arr in (elev, slope, slopeDeg, wateracc, isWater, isRiver,
                forage, game, cost, nc, risk, biome, npp, forestness, dist):
        arr.flags.writeable = False

    return WorldFields(
        elev=elev, slope=slope, slopeDeg=slopeDeg,
        wateracc=wateracc, isWater=isWater, isRiver=isRiver,
        forage=forage, game=game, cost=cost, neighbour_cost=nc,
        risk=risk, biome=biome, npp=npp, forestness=forestness,
        dist=dist, reliefAmpM=reliefAmpM, SEA_LEVEL_M=SEA_LEVEL_M,
    )


# ── characterize_map ────────────────────────────────────────────────────────

def characterize_map(F: WorldFields) -> dict:
    """Per-map diagnostic vector. Saved alongside every generated map.

    Vector keys match the oracle battery JSON exactly.
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

    return {
        'waterPct':        water / n * 100,
        'riverPct':        river / land * 100 if land > 0 else 0.0,
        'wetlandPct':      frac['wetland'],
        'hydratedPct':     (water + river + int(counts[BIOME_WETLAND])) / n * 100,
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
    }
