"""terrain.py — Stage 7 terrain generator (production Python port).

Port of sic_terrain_prototype.html into Python/numpy.
Pipeline: elevation (fbm+ridge) → water → rivers → wateracc → moisture →
          NPP/forestness → forage/game/cost/risk → biome classification.

All terrain fields are precomputed once and frozen (non-writeable).
Determinism contract: same (knobs, seedStr) → byte-identical arrays.
"""
from __future__ import annotations

import math
from collections import deque
from dataclasses import dataclass

import numpy as np
from scipy.special import ndtri   # inverse normal CDF Φ⁻¹ (deterministic; used for lognormal rescale)

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
# All forage values trace to LITERATURE.md (canonical home); derivations in
# SiC_Games_Resource_Return_Rate_Table.md §2.2 (forage) / §3.2 (game).
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
# Per-biome literature spread (std) for the lognormal cell-value draw. Biomes absent
# here use DEFAULT_STD_FRAC (10% of mean). Derivations: Resource table §2.2; MECHANISMS §9a.6.
FORAGE_KCAL_STD = {
    BIOME_WETLAND: 3362.0,    # Cunningham diss: mean(Wet)=1428.3, median=558.7 → lognormal std (CV 2.35, skewed USO returns) [LIT]
    BIOME_FOREST:   600.0,    # std across Hill 1987 palm-product rates {2356,3219,2436,2243,1331} [LIT]
    BIOME_SAVANNA:  182.1,    # Berbesque & Marlowe 2009 Table 4: female tuber mean 257.7, SD 182.1 (CV 0.71) [LIT, direct SD]
    BIOME_DESERT:   368.0,    # O'Connell & Hawkes 1984 range 650–1925 → uniform std=(1925-650)/√12 [RANGE-DERIVED]
    # GRASS / MOUNTAIN absent → DEFAULT_STD_FRAC fallback (10% of mean; no usable spread in source)
}

# ── Phase 1 Blueprint A game_kcal constants ────────────────────────────────
# [PROVISIONAL — biome-scaled from return-rate table, pending CC-1 ceiling]
# Per-biome representative values derived in SiC_Games_Resource_Return_Rate_Table.md §3.2
# (the authoritative home for each value; this dict follows the table, never leads it).
# Wetland, Mountain, Water: UNANCHORED → game_kcal zeroed (not present in this dict).
GAME_KCAL_TARGETS = {
    BIOME_FOREST:  5541.0,   # 7-species pursuit-weighted mean (Hill 1987; 1,462,745/264). Resource table §3.2 [NATIVE, handling-only, PROVISIONAL]
    BIOME_SAVANNA:  518.0,   # all-seasons base encounter (static cell; 745 dry-season = seasonality hook). Resource table §3.2 [CONVERTED, PROVISIONAL]
    BIOME_GRASS:   3001.0,   # Hurtado & Hill 1987 direct lift. Resource table §3.2 [NATIVE, PROVISIONAL]
    BIOME_DESERT:   730.0,   # 1201→730: bout-frequency-weighted mean of search-incl. overall hunt-type rates (Bird 2009; 570,262/781). Resource table §3.2 [supervisor-approved 2026-06-15, PROVISIONAL]
}
# Per-biome literature spread (std). Biomes absent here use DEFAULT_STD_FRAC (10% of mean).
# Derivations: Resource table §3.2; MECHANISMS §9a.6.
GAME_KCAL_STD = {
    BIOME_FOREST:  4043.0,   # weighted std of the 7 Hill 1987 species rates (CV 0.73). Resource table §3.2 [NATIVE]
    BIOME_SAVANNA: 1158.0,   # Hawkes 1991: small-game income 0.162±0.362 animals/day → CV 2.24 × mean 518 [LIT-DERIVED, supervisor-review — hunting is high-variance; 10% understates]
    BIOME_DESERT:   210.0,   # weighted std of the 3 Bird 2009 hunt-type rates {641,765,1300} (CV 0.29). Resource table §3.2
    # GRASS absent → DEFAULT_STD_FRAC fallback (10% of mean; Hurtado & Hill 1987 variance source not in repo)
}

# ── Cordain 2000 Table 2 — diet meat-fraction by biome (MODEL_SPEC §4.5.5) ──────────────────
# The animal (hunted) fraction of the *terrestrial* diet = hunted / (plant + hunted), at class-interval
# midpoints, with the fished column DROPPED (the model has a forage + game economy, no aquatic stream).
# Source: Cordain et al. 2000, AJCN 71:682–692, Table 2 (mean subsistence dependence by primary living
# environment, n=63). Used by DemographyConfig.game_meat_frac to split the cell yield (forage + meat).
MEAT_FRAC = {
    BIOME_FOREST:  0.55,   # Subtropical rain forest (Aché): hunted 50.5 / (plant 40.5 + hunted 50.5)
    BIOME_DESERT:  0.45,   # Desert grasses & shrubs (!Kung): 40.5 / (50.5 + 40.5)
    BIOME_SAVANNA: 0.38,   # Tropical grassland (Hadza): 30.5 / (50.5 + 30.5)
    BIOME_GRASS:   0.66,   # Temperate grasslands (steppe/plains): 60.5 / (30.5 + 60.5)
}

# Fallback spread when a biome's std is NOT literature-anchored: std = DEFAULT_STD_FRAC × mean.
# Supervisor rule (2026-06-15): "if [literature std] not available use 10% of the value as std."
# Applies to every biome absent from the *_STD dicts above → every biome uses the lognormal draw.
DEFAULT_STD_FRAC = 0.10

# ── Phase 1 game_mobility SEAM (per-biome migratory-game / herd-following mobility) ─────────
# [SEAM — parameter wired, MECHANIC DEFERRED to the open-biome migration stage; MODEL_SPEC §4.1.7]
# Normalized [0,1]: 0 = resident game (HG mobility comes from seasonal/patchy tracking, not herds);
# 1 = fully migratory megafauna (logistical herd-following dominates mobility, Binford's collector end).
# Anchor: Binford 2001 (residential/logistical mobility + range size by biome / effective-temperature) +
# the forager↔collector continuum. ≈0 in the calibration biomes (forest/desert) → migration is OFF there
# BY CONSTRUCTION (resolves red-team RT-4). Biomes absent here (wetland/mountain/water) → 0.
GAME_MOBILITY = {
    BIOME_FOREST:  0.0,   # Aché — resident forest game; mobility from seasonal/patchy tracking, not herds
    BIOME_DESERT:  0.0,   # !Kung — resident desert game (gemsbok); residential foragers
    BIOME_SAVANNA: 0.2,   # Hadza — dry-season AGGREGATION (access), not true range-shift (§4.1.5)
    BIOME_GRASS:   1.0,   # steppe/grassland — migratory ungulates (Nunamiut caribou, plains bison): logistical herd-following
}

# ── Lognormal cell-value rescale (Phase 1, 2026-06-15) ─────────────────────
def _lognormal_rescale(field_norm: np.ndarray, mask: np.ndarray,
                       mean: float, std: float) -> np.ndarray:
    """Map a biome's terrain-field cells onto a lognormal(mean, std), preserving
    spatial ordering. Deterministic (no RNG): each cell's value is the lognormal
    quantile at the cell's rank within the biome, so high-terrain cells get high
    values (terrain coupling) while the realised marginal is the literature-anchored
    lognormal — positive-only, right-skewed. Re-normalised to hit `mean` exactly.

    Returns the rescaled values for the masked cells (1-D, in mask order).
    """
    vals = field_norm[mask]
    n = vals.size
    if n == 0:
        return vals
    if n == 1 or std <= 0.0 or mean <= 0.0:
        return np.full(n, mean, dtype=np.float64)
    # rank → Hazen plotting-position quantiles in (0,1); stable sort = deterministic ties
    ranks = np.argsort(np.argsort(vals, kind="stable"), kind="stable")
    q = (ranks.astype(np.float64) + 0.5) / n
    # lognormal parameters from (mean, std)
    sigma2 = math.log(1.0 + (std / mean) ** 2)
    sigma = math.sqrt(sigma2)
    mu = math.log(mean) - 0.5 * sigma2
    out = np.exp(mu + sigma * ndtri(q))
    out *= mean / float(out.mean())     # exact biome mean (scaling preserves CV & positivity)
    return out


# ── Phase 1 Stage 1b constants ─────────────────────────────────────────────
# Provisional exterior-water guard threshold.
# Derivation (P1S1b blueprint §3): for N=100 with a t-cell ocean rim,
# rim cells = N² − (N−2t)²:  t=1→396 (0.040), t=2→784 (0.078), t=3→1164 (0.116).
# A 2–3 cell rim allows naturalistic edge roughness; threshold = 0.12 (t=3 bound).
# RETIRED as acceptance guard by Stage 1c. Kept as a diagnostic constant.
EXTERIOR_WATER_CEILING = 0.12

# ── Phase 1 Stage 1c constants ─────────────────────────────────────────────
# Single-largest-water-body ceiling (§DECISION-LAKE-BODY-CEILING).
# 0.08 ≈ 80,000 km² at 100 km²/cell — just below Lake Superior (~82,000 km²).
# Conservative-side choice: reject at inland-sea scale, not above it.
# A body this large produces coastal dynamics deferred to §STAGE-GEOSTRUCT.
LARGE_BODY_CEILING = 0.08

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

# ── Climate seam (Phase 1, 2026-06-18) ──────────────────────────────────────────────
# HOMOGENEOUS global-average placeholders. Spatial + seasonal variation (latitude / insolation /
# solar forcing) is the DEFERRED climate-season stage; these constant fields exist NOW so the
# demographic pathogen field (Step 2) can reference real temperature/humidity rather than a
# `wateracc × NPP` proxy. [PLACEHOLDER — exact values + the spatially/seasonally varying field are
# pinned in the climate-season stage; see DEFERRED_MECHANICS CL-1 / MODEL_SPEC §4.3.2.]
MEAN_GLOBAL_TEMP_C = 14.0    # global mean surface air temperature ~14 °C (20th-century baseline; area-mean anchor)
MEAN_REL_HUMIDITY = 0.70     # near-surface relative humidity, land-ish average (fraction)

# ── C.4a sub-biome tag: GRASS splits into tropical-llanos vs temperate-steppe (climate catastrophe stage) ──
# The `temperature` field becomes a LATITUDINAL gradient (was a flat placeholder; verified NOTHING read it).
# Linear in grid row y: y=0 equator (warm) → y=N-1 high latitude (cold); endpoints preserve the 14 °C area-mean.
# This lets the C.4 catastrophe layers separate the two ecologies the single BIOME_GRASS code conflates:
# Hurtado & Hill (tropical llanos, Hiwi/Cuiva) vs Nunamiut caribou / plains bison (temperate-arctic steppe).
TEMP_EQUATOR_C  = 27.0       # mean-annual T at the equatorial edge (tropical savanna/llanos ≈ 27 °C)
TEMP_HIGHLAT_C  = 1.0        # mean-annual T at the high-latitude edge (temperate/boreal steppe ≈ 1 °C); mean (27+1)/2 = 14
GRASS_TROPICAL_THRESHOLD_C = 18.0   # Köppen tropical-A boundary (18 °C isotherm): GRASS warmer → llanos, cooler → steppe
# ── Economy-from-Climate C1 (mode="climate"): real temperature field constants (PROVISIONAL — sign-off) ──
# A 1000×1000 km grid (100 cells × 10 km) spans only ~9° of latitude — so the WITHIN-GRID latitudinal temperature
# gradient is MODEST (~a few °C); the big spatial variability is ELEVATION (lapse) + rain-shadow + coast (a
# mountainous coastal region like Montana/Oregon legitimately holds 4–6 biomes). The world sits at a REGIONAL
# latitude `climate_latitude` (knob, 0=equator … 1=subpolar edge; sets the base T + precip regime); within the grid
# only a narrow band around it is traversed.
CLIMATE_FULL_LAT_DEG   = 65.0     # latitude (°) at the subpolar edge (climate_latitude=1); equator=0
GRID_SPAN_DEG          = 9.0      # N–S extent of the 1000 km grid (1000 km / ~111 km per degree)
REGIONAL_SPAN_FRAC     = GRID_SPAN_DEG / CLIMATE_FULL_LAT_DEG   # ≈0.14 of the full span traversed within the grid
CLIMATE_LATITUDE_DEFAULT = 0.5    # temperate mid-latitude region (knobs['climate_latitude'] overrides)
LAPSE_C_PER_KM   = 6.5        # environmental lapse rate (°C per 1000 m elevation) — montane cooling
TEMP_SEAS_AMP_MAX = 15.0      # max half-amplitude of the seasonal T cycle (°C) at a high-latitude CONTINENTAL interior
                              # (→ ±15 °C = ~30 °C annual range, cf. continental temperate/boreal interiors); PROVISIONAL
MARITIME_DAMP    = 0.6        # fraction by which coastal/near-water cells (high wateracc) DAMP the seasonal amplitude
                              # (maritime moderation: oceans buffer the annual swing); PROVISIONAL
# C6 river-source temperature: a river carries the cold of its montane HEADWATER (snowmelt), not the local air —
# so a valley river can be cold even where the air is warm (the salmon-fishery enabler; lit: river T by source).
# T_river = air_T − RIVER_COLD_RETENTION · lapse · (headwater_elev − local_elev); headwater = max upstream elevation.
RIVER_COLD_RETENTION = 0.6    # fraction of the headwater-elevation cooling a river retains by the time it reaches a cell
# ── Economy-from-Climate C7: AQUATIC-FOOD field ∈ [0,1] — the dense STORABLE aquatic resource that underwrites
#    forager complexity (Testart/Ames). Two limbs, per LITERATURE: ANADROMOUS (cold-water salmon runs in sea-
#    connected rivers — salmonid thermal: opt ~16 °C, lethal ~21 °C) and SHELLFISH/marine (coastal littoral, the
#    Bird shore-bonus zone, warm-tolerant). Constants PROVISIONAL. ──
SALMON_T_OPT     = 16.0       # water_temp (°C) at/below which anadromous coldness is FULL
SALMON_T_LETHAL  = 21.0       # water_temp at/above which anadromous coldness is 0
AQUATIC_SEA_CONN_FLOOR = 0.25 # anadromous factor for rivers NOT draining to the sea (endorheic — some lacustrine fish)
SHELLFISH_RICHNESS = 0.7      # coastal littoral aquatic-food level on shore cells (Bird 1997 reef/intertidal richness)


def aquatic_food_field(water_temp, isRiver, is_shore, drains_to_sea, npp01):
    """C7 aquatic-food density ∈ [0,1] on land cells (0 on open water): max of the anadromous (cold sea-connected
    river) and shellfish (coastal) limbs. `npp01` = normalised terrestrial NPP [0,1] (proxy for littoral
    productivity). All inputs (N,N). Vectorized."""
    coldness = np.clip((SALMON_T_LETHAL - water_temp) / (SALMON_T_LETHAL - SALMON_T_OPT), 0.0, 1.0)
    sea_conn = np.where(drains_to_sea, 1.0, AQUATIC_SEA_CONN_FLOOR)
    river_cold = coldness * isRiver.astype(np.float64) * sea_conn        # anadromous ON the river cells
    # foragers harvest from the BANK → spread the river fishery to 4-neighbour land cells (max)
    anadromous = river_cold.copy()
    anadromous[:, 1:]  = np.maximum(anadromous[:, 1:],  river_cold[:, :-1])
    anadromous[:, :-1] = np.maximum(anadromous[:, :-1], river_cold[:, 1:])
    anadromous[1:, :]  = np.maximum(anadromous[1:, :],  river_cold[:-1, :])
    anadromous[:-1, :] = np.maximum(anadromous[:-1, :], river_cold[1:, :])
    shellfish = is_shore.astype(np.float64) * SHELLFISH_RICHNESS * (0.5 + 0.5 * npp01)   # coastal, productivity-scaled
    return np.clip(np.maximum(anadromous, shellfish), 0.0, 1.0)
# ── Economy-from-Climate C2 (mode="climate"): structured annual PRECIPITATION (mm/yr) — Hadley/ITCZ bands +
#    orographic rain-shadow + maritime supply + noise texture. All PROVISIONAL (sign-off). Ranges tuned so the
#    latitudinal profile lands in Earth-like biome bins: equatorial ITCZ ~2600 mm (rainforest), subtropical ~30°
#    trough ~300 mm (desert), mid-latitude storm track ~1350 mm (temperate forest), subpolar edge ~300 mm.
P_BASE_MM        = 250.0      # dry-background precipitation (subtropical/polar deserts floor near here)
P_ITCZ_MM        = 2400.0     # equatorial ITCZ wet peak (added at lat_frac≈0)
P_ITCZ_WIDTH     = 0.15       # ITCZ Gaussian half-width in lat_frac
P_MIDLAT_MM      = 1100.0     # mid-latitude storm-track wet peak
P_MIDLAT_CENTER  = 0.70       # lat_frac of the mid-latitude peak (~50° on the equator→subpolar span)
P_MIDLAT_WIDTH   = 0.18       # mid-latitude Gaussian half-width
# Orographic precipitation — the DOMINANT terrain control (mountains wet, lee dry). Two parts:
#  (i) UPLIFT: air forced up high ground cools & rains → precip rises with elevation (windward + peaks very wet);
#  (ii) RAIN SHADOW: cells DOWNWIND of high terrain are dry (the air already dumped its moisture) — a multi-cell
#       shadow (a big range dries ~tens of km to its lee, e.g. Cascades → high desert). Prevailing wind = +x.
P_ELEV_UPLIFT      = 1.6      # elevation → orographic uplift multiplier (elev=1 ⇒ ×(1+1.6)=2.6 wetter)
P_ORO_SHADOW_CELLS = 6        # rain-shadow reach: max upwind elevation is taken over this many cells (≈60 km)
P_ORO_SHADOW_GAIN  = 1.6      # drying strength in the lee of upwind high terrain
P_ORO_MIN        = 0.25       # clamp floor on the orographic multiplier (deep rain-shadow)
P_ORO_MAX        = 3.2        # clamp cap (windward/peak enhancement)
P_MARITIME_GAIN  = 0.3        # moisture supply: near-water (wateracc) cells wetter
P_ORO_WIND_DX    = 1          # prevailing wind = +x (westerlies): upwind is to the −x (west) side
CLIMATE_ARIDITY_DAMP = 0.75   # climate_aridity∈[0,1] scales precip DOWN by up to this fraction (continental/leeward
                              # dryness independent of latitude — e.g. a temperate but arid interior like central Asia)
# Orographic rain is MOISTURE-LIMITED — a mountain can only wring out the moisture the air carries. So the uplift
# enhancement scales with the regional air moisture (base precip × aridity); dry subtropical highlands stay arid.
P_MOISTURE_REF_MM  = 1500.0   # base precip at which orographic uplift is FULL; below → proportionally weaker
P_UPLIFT_MIN_AVAIL = 0.12     # floor on moisture-availability (even dry air gives a little orographic rain)
# Polar-cell dryness: descending dry air toward the pole → precip declines past the mid-latitude storm track.
POLAR_DRY_ONSET    = 0.72     # cell_lat beyond which polar dryness ramps in
POLAR_DRY_GAIN     = 0.55     # max fractional precip reduction at the pole edge
# ── Economy-from-Climate C3 (mode="climate"): the MIAMI MODEL — NPP from temperature & precipitation ──
# Lieth 1972/1975 (PDF filed; eqs 12-1/12-2, VERIFIED). NPP = min(temperature-limited, precipitation-limited),
# g dry-matter/m²/yr. Coefficients are the published least-squares fit (50 sites / 5 continents). LITERATURE.md.
MIAMI_MAX = 3000.0            # asymptotic NPP ceiling of both limbs (g/m²/yr)
MIAMI_T_A = 1.315            # temperature-limb: NPP_T = MAX / (1 + exp(A − B·T)), T in °C
MIAMI_T_B = 0.119
MIAMI_P_C = 0.000664          # precip-limb: NPP_P = MAX · (1 − exp(−C·P)), P in mm/yr


def miami_npp(temperature_c, precip_mm):
    """Miami model NPP (Lieth 1972/1975), g dry-matter/m²/yr: the MINIMUM of a temperature-limited and a
    precipitation-limited saturating curve — cold OR dry both cap productivity. Vectorized (arrays or scalars)."""
    npp_t = MIAMI_MAX / (1.0 + np.exp(MIAMI_T_A - MIAMI_T_B * np.asarray(temperature_c, dtype=float)))
    npp_p = MIAMI_MAX * (1.0 - np.exp(-MIAMI_P_C * np.asarray(precip_mm, dtype=float)))
    return np.minimum(npp_t, npp_p)


# ── Economy-from-Climate C4: WHITTAKER biome from (annual T × annual P) — biome is an OUTCOME of climate, not a
#    label. Thresholds rise with temperature (evapotranspiration: warmer needs more rain for the same class), mapped
#    onto the model's coarse codes: DESERT (arid, any T) / FOREST (wet) / SAVANNA (warm grassland) / GRASS (cool
#    grassland-steppe). Cold+wet → FOREST (taiga); cold+dry → GRASS (steppe/tundra). Terrain overrides (MOUNTAIN,
#    WETLAND, WATER) apply on top. Thresholds PROVISIONAL. ──
WHIT_DESERT_BASE   = 200.0    # P (mm/yr) below (BASE + SLOPE·max(T,0)) → DESERT
WHIT_DESERT_SLOPE  = 15.0
WHIT_FOREST_BASE   = 500.0    # P (mm/yr) above (BASE + SLOPE·max(T,0)) → FOREST
WHIT_FOREST_SLOPE  = 35.0
WHIT_TUNDRA_T      = -5.0     # below this mean-annual T it is too cold for trees → would-be FOREST becomes GRASS (tundra)


def whittaker_biome(temperature_c, precip_mm):
    """Whittaker CLIMATE biome (BIOME_DESERT/SAVANNA/GRASS/FOREST) from annual mean T (°C) and annual P (mm/yr).
    Temperature-scaled aridity/forest thresholds (warm → higher P needed). Vectorized; terrain overrides
    (MOUNTAIN/WETLAND/WATER) are applied by the caller. Returns a uint8 code array (or scalar)."""
    T = np.asarray(temperature_c, dtype=float)
    P = np.asarray(precip_mm, dtype=float)
    Tp = np.maximum(T, 0.0)                                   # evapotranspiration scales with warmth
    desert_thr = WHIT_DESERT_BASE + WHIT_DESERT_SLOPE * Tp
    forest_thr = WHIT_FOREST_BASE + WHIT_FOREST_SLOPE * Tp
    biome = np.full(T.shape, BIOME_GRASS, dtype=np.uint8)     # default: cool grassland/steppe
    warm = T >= GRASS_TROPICAL_THRESHOLD_C                    # 18 °C tropical isotherm → SAVANNA vs GRASS
    grass_zone = (P >= desert_thr) & (P < forest_thr)
    biome[grass_zone & warm] = BIOME_SAVANNA
    biome[P >= forest_thr] = BIOME_FOREST
    biome[P < desert_thr] = BIOME_DESERT
    # cold cap: too cold for trees → tundra (open, → GRASS); a would-be FOREST becomes GRASS. Cold+dry stays DESERT.
    biome[(T < WHIT_TUNDRA_T) & (biome == BIOME_FOREST)] = BIOME_GRASS
    return biome
GRASS_NONE   = 0             # grass_subtype codes
GRASS_LLANOS = 1             # tropical GRASS (Hurtado & Hill Hiwi/Cuiva) → wet/dry flood-tail regime (C.4c)
GRASS_STEPPE = 2             # temperate/arctic GRASS (caribou/bison) → migratory-herd quasi-cycle (C.4b)

# ── Agriculture tier — cultivability (Layer A; blueprint …_AgricultureTier_Scoping). Agro-climatic cultivation
# potential that EMERGES from climate (like Miami-NPP / Whittaker-biome), not a hand-drawn mask. Anchors: FAO
# agro-ecological zones (crop suitability from climate); growing-degree-days / growing-season length; UNEP aridity
# index P/PET. PROVISIONAL thresholds — sign-off. ──
CULT_T_BASE      = 8.0     # °C crop base temperature — a growing month has monthly-mean T ≥ this (wheat~5, maize~10)
CULT_GS_LOW      = 0.33    # growing-season fraction (~4 mo/yr) below which cultivation fails (too short/cold)
CULT_GS_HIGH     = 0.60    # season fraction (~7 mo) at/above which the season is non-limiting
CULT_PET_PER_DEG = 55.0    # mm/yr potential evapotranspiration per °C annual mean (simple Thornthwaite-style PET proxy)
CULT_AI_LOW      = 0.20    # aridity index P/PET below which rain-fed ag fails (UNEP arid limit)
CULT_AI_HIGH     = 0.50    # AI at/above which water is non-limiting (sub-humid; UNEP)
CULT_SLOPE_PEN   = 1.5     # slope penalty — steep ground is not arable


def cultivability_field(temperature, temp_seas_amp, precip_mm, slope, is_water):
    """Agro-climatic cultivation potential ∈[0,1], EMERGENT from climate — the `cultivability` S_pot source
    (agriculture tier Layer A). Product of three limiters (min-of-Liebig style, multiplicative):
      f_gs  GROWING SEASON — fraction of the annual temperature cosine (mean ± seasonal half-amplitude) with
            monthly T ≥ CULT_T_BASE; cold/short-season land (tundra, high montane) → 0.
      f_ai  WATER — aridity index AI = P/PET (PET ≈ CULT_PET_PER_DEG·max(T,1)); arid (AI<LOW) → 0, sub-humid+ → 1.
      f_terr ARABLE — low slope, not water.
    Peaks in temperate/subtropical/Mediterranean sub-humid low-relief land (the fertile belt); ~0 in desert,
    tundra, and steep terrain. PROVISIONAL (sign-off)."""
    Tm = temperature
    A = np.maximum(temp_seas_amp, 1e-6)
    c = np.clip((CULT_T_BASE - Tm) / A, -1.0, 1.0)              # cosine level for the crop base temperature
    gs = np.arccos(c) / np.pi                                   # fraction of the year above CULT_T_BASE (0..1)
    f_gs = np.clip((gs - CULT_GS_LOW) / (CULT_GS_HIGH - CULT_GS_LOW), 0.0, 1.0)
    ai = precip_mm / (CULT_PET_PER_DEG * np.maximum(Tm, 1.0))
    f_ai = np.clip((ai - CULT_AI_LOW) / (CULT_AI_HIGH - CULT_AI_LOW), 0.0, 1.0)
    f_terr = np.clip(1.0 - CULT_SLOPE_PEN * slope, 0.0, 1.0)
    cult = f_gs * f_ai * f_terr
    cult[is_water == 1] = 0.0
    return cult


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
    # Phase 1 Blueprint A fields (added 2026-06-14)
    # [PROVISIONAL — biome-scaled from return-rate table, pending CC-1 ceiling]
    game_kcal:     np.ndarray = None  # (N,N) float64 kcal/forager-hr; 0 at wetland/mountain/water
    # Phase 1 game_mobility seam (added 2026-06-20) — per-biome migratory-game/herd-following factor [0,1];
    # ≈0 forest/desert (resident), finite grass/steppe (migratory). MECHANIC DEFERRED (open-biome stage).
    game_mobility: np.ndarray = None  # (N,N) float64 [0,1]; GAME_MOBILITY[biome]. [SEAM — MODEL_SPEC §4.1.7]
    # Phase 1 climate seam (added 2026-06-18) — HOMOGENEOUS placeholders (spatially constant); the
    # spatial/seasonal (solar-forced) field is the deferred climate-season stage. [PLACEHOLDER]
    temperature:   np.ndarray = None  # (N,N) float64 °C; LATITUDINAL gradient (C.4a; was a flat placeholder)
    humidity:      np.ndarray = None  # (N,N) float64 [0,1] rel. humidity; constant = MEAN_REL_HUMIDITY
    # Economy-from-Climate C1 (mode="climate"): `temperature` = ANNUAL-MEAN (lat − lapse·elev + maritime); the
    # per-cell seasonal HALF-AMPLITUDE is `temp_seas_amp` (0 in legacy mode; the monthly wave is applied by the
    # climate layer). Under mode="legacy" temperature is the latitudinal placeholder and temp_seas_amp is 0.
    temp_seas_amp: np.ndarray = None  # (N,N) float64 °C seasonal half-amplitude (0 = legacy/aseasonal)
    precip_mm:     np.ndarray = None  # (N,N) float64 annual precipitation mm/yr (C2; 0 in legacy mode)
    water_temp:    np.ndarray = None  # (N,N) float64 °C river/surface-water temp (C6, headwater-sourced; 0 in legacy)
    aquatic_food:  np.ndarray = None  # (N,N) float64 [0,1] dense storable aquatic-food density (C7; 0 in legacy)
    cultivability: np.ndarray = None  # (N,N) float64 [0,1] agro-climatic cultivation potential (agriculture Layer A; 0 in legacy)
    # C.4a GRASS sub-biome tag: 0 non-grass, GRASS_LLANOS=1 (tropical), GRASS_STEPPE=2 (temperate) — by isotherm.
    grass_subtype: np.ndarray = None  # (N,N) uint8


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


def _component_sizes(mask: np.ndarray) -> list[int]:
    """Return list of connected-component sizes (4-nbr) for all True cells in mask."""
    visited = np.zeros((N, N), dtype=bool)
    sizes: list[int] = []
    for r0 in range(N):
        for c0 in range(N):
            if not mask[r0, c0] or visited[r0, c0]:
                continue
            size = 0
            q: deque = deque([(r0, c0)])
            visited[r0, c0] = True
            while q:
                r, c = q.popleft()
                size += 1
                for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    nr, nc_ = r + dr, c + dc
                    if 0 <= nr < N and 0 <= nc_ < N and mask[nr, nc_] and not visited[nr, nc_]:
                        visited[nr, nc_] = True
                        q.append((nr, nc_))
            sizes.append(size)
    return sizes


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


# ── World lottery — a diverse per-world ENSEMBLE ────────────────────────────
# Parallel to the climate orbital-lottery (climate.py): instead of fixed knobs for every seed (→ every world the
# same dry-savanna, biome 3), draw per-world knobs so the ensemble spans world-TYPES — biome-DOMINATED worlds
# (forest / savanna / desert / montane) AND well-MIXED worlds. Ranges are EMPIRICALLY calibrated (knob→biome
# sweep 2026-07-02): forest/savanna/desert dominate cleanly; montane = mountainous-with-lowlands (peaks are
# naturally sparse) ; mixed = high-roughness multi-biome. Each archetype draws its knobs uniformly (jitter);
# the seed cycles through the archetypes so a small ensemble covers every type. Deterministic per seed.
WORLD_ARCHETYPES: dict[str, dict[str, tuple[float, float]]] = {
    # archetype:  (relief),      (rough),      (waterK),     (forestK),    (aridK)
    "forest":  dict(relief=(0.30, 0.55), rough=(0.40, 0.60), waterK=(0.30, 0.45), forestK=(0.80, 0.95), aridK=(0.05, 0.20)),
    "savanna": dict(relief=(0.35, 0.55), rough=(0.45, 0.65), waterK=(0.25, 0.40), forestK=(0.45, 0.62), aridK=(0.35, 0.52)),
    "desert":  dict(relief=(0.35, 0.60), rough=(0.45, 0.65), waterK=(0.08, 0.20), forestK=(0.10, 0.25), aridK=(0.72, 0.90)),
    "montane": dict(relief=(0.82, 0.96), rough=(0.72, 0.90), waterK=(0.25, 0.45), forestK=(0.40, 0.65), aridK=(0.30, 0.55)),
    "mixed":   dict(relief=(0.45, 0.70), rough=(0.70, 0.90), waterK=(0.30, 0.50), forestK=(0.55, 0.72), aridK=(0.30, 0.48)),
}
WORLD_ARCHETYPE_ORDER = ("forest", "savanna", "desert", "montane", "mixed")

# ── Economy-from-Climate C4 (part B): worlds are drawn as INDEPENDENT terrain × climate; biomes fall out of
#    Whittaker(T,P) at generate_world(mode="climate"). TERRAIN = physical geography (relief, water/coast); CLIMATE =
#    latitude band + extra aridity. Any pairing is legal (tropical-lowland → rainforest; tropical-montane → Andes;
#    subtropical-flat-arid → Sahara; temperate-montane → Rockies; boreal-flat → taiga). Ranges PROVISIONAL. ──
TERRAIN_PRESETS: dict[str, dict[str, tuple[float, float]]] = {
    "flat":        dict(relief=(0.05, 0.15), rough=(0.35, 0.55), waterK=(0.25, 0.40)),
    "hilly":       dict(relief=(0.35, 0.55), rough=(0.55, 0.75), waterK=(0.25, 0.42)),
    "mountainous": dict(relief=(0.82, 0.96), rough=(0.72, 0.90), waterK=(0.25, 0.45)),
    "coastal":     dict(relief=(0.20, 0.45), rough=(0.45, 0.65), waterK=(0.45, 0.62)),
}
CLIMATE_PRESETS: dict[str, dict[str, tuple[float, float]]] = {
    # climate: (climate_latitude), (climate_aridity)
    "tropical":    dict(climate_latitude=(0.05, 0.15), climate_aridity=(0.00, 0.20)),
    "subtropical": dict(climate_latitude=(0.28, 0.38), climate_aridity=(0.40, 0.75)),  # the arid Hadley-descent belt
    "temperate":   dict(climate_latitude=(0.48, 0.62), climate_aridity=(0.10, 0.45)),
    "boreal":      dict(climate_latitude=(0.78, 0.92), climate_aridity=(0.15, 0.45)),
}
TERRAIN_ORDER = ("flat", "hilly", "mountainous", "coastal")
CLIMATE_ORDER = ("tropical", "subtropical", "temperate", "boreal")


def world_lottery_climate(seed: int, terrain: str | None = None, climate: str | None = None) -> dict:
    """Economy-from-Climate world draw: INDEPENDENT terrain × climate → knobs for `generate_world(…, mode="climate")`,
    where the biome EMERGES from Whittaker(T,P). `seed` cycles terrain and climate on co-prime periods (4 × 4 = 16
    distinct pairings over seeds 0–15) unless forced. `forestK`/`aridK` (legacy moisture knobs) are neutralised —
    climate, not a knob, sets moisture. Use with `mode="climate"`."""
    import random as _random
    terr = terrain or TERRAIN_ORDER[seed % len(TERRAIN_ORDER)]
    clim = climate or CLIMATE_ORDER[(seed // len(TERRAIN_ORDER)) % len(CLIMATE_ORDER)]
    rng = _random.Random(20260703 + seed)
    knobs = {k: rng.uniform(lo, hi) for k, (lo, hi) in TERRAIN_PRESETS[terr].items()}
    knobs.update({k: rng.uniform(lo, hi) for k, (lo, hi) in CLIMATE_PRESETS[clim].items()})
    knobs["forestK"] = 0.5    # neutral (climate sets moisture; forestK is a legacy woody-cover knob)
    knobs["aridK"] = 0.0      # neutral (legacy aridity; superseded by climate_aridity)
    knobs["mode"] = "climate"
    knobs["seedStr"] = f"{terr}-{clim}{seed}"
    knobs["terrain"] = terr
    knobs["climate"] = clim
    return knobs


def world_lottery(seed: int, archetype: str | None = None) -> dict:
    """Per-world knob draw for a DIVERSE ensemble. `seed` cycles through `WORLD_ARCHETYPE_ORDER` (so seeds 0–4 give
    forest/savanna/desert/montane/mixed, 5–9 repeat, …) unless `archetype` is forced; knobs are drawn uniformly
    within the archetype ranges, seeded by `seed` (reproducible). Returns a `generate_world` knobs dict tagged with
    the archetype in `seedStr`."""
    import random as _random
    arch = archetype or WORLD_ARCHETYPE_ORDER[seed % len(WORLD_ARCHETYPE_ORDER)]
    rng = _random.Random(20260702 + seed)
    ranges = WORLD_ARCHETYPES[arch]
    knobs = {k: rng.uniform(lo, hi) for k, (lo, hi) in ranges.items()}
    knobs["seedStr"] = f"{arch}{seed}"
    knobs["archetype"] = arch
    return knobs


# ── Main generator ─────────────────────────────────────────────────────────

def generate_world(knobs: dict, mode: str = "legacy") -> WorldFields:
    """Generate terrain from knob dict; return frozen WorldFields.

    knobs keys: relief, rough, waterK, forestK, aridK, seedStr (string).
    Determinism: same (knobs, seedStr) → byte-identical arrays.

    `mode`: "legacy" (default) = the historical substrate (bit-exact). "climate" = Economy-from-Climate: the
    `temperature` field becomes a real annual mean (latitude − elevation lapse + maritime moderation) with a
    per-cell seasonal amplitude `temp_seas_amp` (C1). `mode` may also be supplied via knobs["mode"].
    """
    mode = str(knobs.get("mode", mode))
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
    src_elev = elev_flat.copy()          # C6: max upstream (headwater) elevation draining through each cell
    downstream = np.full(N * N, -1, dtype=np.int64)     # C7: the cell each land cell flows to (−1 = pit/endorheic)
    D8 = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)]
    for idx in order:                    # descending elevation ⇒ a cell's upstream contributors are processed first
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
        downstream[idx] = lowest_j
        if lowest_j >= 0:
            flow[lowest_j] += flow[idx]
            if src_elev[idx] > src_elev[lowest_j]:
                src_elev[lowest_j] = src_elev[idx]      # carry the headwater elevation downstream

    # C7 sea-connectivity: a river drains to the SEA if its downstream path terminates at open water (not an
    # endorheic pit). Propagate UPSTREAM (ascending elevation): a cell drains-to-sea iff its downstream cell does.
    drains_to_sea = isWater_flat.astype(bool).copy()    # open water IS the sea
    for idx in land_idx[np.argsort(elev_flat[land_idx], kind='stable')]:   # ascending: downstream processed first
        d = downstream[idx]
        if d >= 0 and drains_to_sea[d]:
            drains_to_sea[idx] = True

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

    # ── Climate fields (C1 temperature / C2 precipitation) — computed BEFORE NPP so Miami (C3) can read them ──
    lat_frac = (np.arange(N, dtype=np.float64) / (N - 1)).reshape(N, 1)        # local grid row 0 → 1 (N to S)
    temp_lat = (TEMP_EQUATOR_C + (TEMP_HIGHLAT_C - TEMP_EQUATOR_C) * lat_frac) * np.ones((1, N))   # legacy full transect
    temp_seas_amp = np.zeros((N, N), dtype=np.float64)
    precip_mm = np.zeros((N, N), dtype=np.float64)
    water_temp = np.zeros((N, N), dtype=np.float64)      # C6 river/surface-water temperature (0 in legacy mode)
    if mode == "climate":
        # REGIONAL climate: the grid is a ~9°-wide swath centred on `climate_latitude` (0=equator … 1=subpolar). The
        # WITHIN-GRID latitudinal gradient is therefore MODEST (~REGIONAL_SPAN_FRAC of the full 26 °C ≈ 3.6 °C); the
        # big variability comes from elevation (lapse) + rain-shadow + coast. `cell_lat` = each cell's ABSOLUTE
        # latitude fraction (for the base T level, the seasonal amplitude, and the precip regime).
        climate_latitude = float(knobs.get("climate_latitude", CLIMATE_LATITUDE_DEFAULT))
        cell_lat = np.clip(climate_latitude + REGIONAL_SPAN_FRAC * (lat_frac - 0.5), 0.0, 1.0) * np.ones((1, N))
        # C1: annual-mean T = regional-latitude base (modest gradient) − elevation lapse; amplitude ∝ absolute latitude.
        temperature = (TEMP_EQUATOR_C + (TEMP_HIGHLAT_C - TEMP_EQUATOR_C) * cell_lat) \
            - LAPSE_C_PER_KM * (elev * reliefAmpM) / 1000.0
        temp_seas_amp = TEMP_SEAS_AMP_MAX * cell_lat * (1.0 - MARITIME_DAMP * wateracc)
        # C2: precip regime set by the cell's ABSOLUTE latitude on the Hadley/ITCZ curve × orographic × maritime × noise.
        itcz = P_ITCZ_MM * np.exp(-(cell_lat / P_ITCZ_WIDTH) ** 2)
        midlat = P_MIDLAT_MM * np.exp(-((cell_lat - P_MIDLAT_CENTER) / P_MIDLAT_WIDTH) ** 2)
        # polar-cell dryness: precip declines past the mid-latitude storm track toward the pole
        polar_dry = 1.0 - POLAR_DRY_GAIN * np.clip((cell_lat - POLAR_DRY_ONSET) / (1.0 - POLAR_DRY_ONSET), 0.0, 1.0)
        aridity = 1.0 - CLIMATE_ARIDITY_DAMP * float(knobs.get("climate_aridity", 0.0))   # continental/leeward dryness
        p_band = (P_BASE_MM + itcz + midlat) * polar_dry * aridity            # the REGIONAL air-moisture supply
        # orographic uplift is MOISTURE-LIMITED (scales with available air moisture) × rain shadow (dry lee)
        moist_avail = np.clip(p_band / P_MOISTURE_REF_MM, P_UPLIFT_MIN_AVAIL, 1.0)
        uplift = 1.0 + P_ELEV_UPLIFT * elev * moist_avail
        upwind_max = elev.copy()
        for _s in range(1, P_ORO_SHADOW_CELLS + 1):
            upwind_max = np.maximum(upwind_max, np.roll(elev, _s * P_ORO_WIND_DX, axis=1))
        shadow = np.clip(1.0 - P_ORO_SHADOW_GAIN * np.maximum(0.0, upwind_max - elev), P_ORO_MIN, 1.0)
        oro = np.clip(uplift * shadow, P_ORO_MIN, P_ORO_MAX)
        precip_mm = np.clip(p_band * oro * (1.0 + P_MARITIME_GAIN * wateracc) * (0.7 + 0.6 * moist), 0.0, None)
        precip_mm[isWater == 1] = 0.0
        # C6: river/surface-water temperature carries the cold of its montane HEADWATER (snowmelt), not the local
        # air — a valley river can be cold where the air is warm. headwater = max upstream elevation (src_elev).
        water_temp = temperature - RIVER_COLD_RETENTION * LAPSE_C_PER_KM \
            * (src_elev.reshape(N, N) - elev) * reliefAmpM / 1000.0
    else:
        temperature = temp_lat

    # ── NPP ────────────────────────────────────────────────────────────
    # legacy: noise-moisture × terrain penalties. climate (C3): MIAMI(T,P) g/m²/yr, normalised by NPP_GM2_SCALE so
    # the downstream `npp_gm2 = npp × NPP_GM2_SCALE` recovers the real Miami g/m²/yr (Miami ≤ 3000 < 3400 ⇒ npp ≤ 0.88).
    # Elevation enters climate-NPP through TEMPERATURE (cold highlands → low NPP_T), so no separate elev penalty.
    if mode == "climate":
        npp = np.where(isWater, 0.0, miami_npp(temperature, precip_mm) / NPP_GM2_SCALE)
    else:
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

    if mode == "climate":
        # C4: biome EMERGES from Whittaker(T, P); MOUNTAIN/WETLAND are TERRAIN overrides on top; water stays water.
        biome = whittaker_biome(temperature, precip_mm)
        is_wetland = is_land & ~is_mtn & (dist <= 2) & (npp > 0.45) & (slope < 0.12)
        biome[is_mtn]     = BIOME_MOUNTAIN
        biome[is_wetland] = BIOME_WETLAND
        biome[isWater == 1] = BIOME_WATER
        # (is_desert/is_forest/is_savanna kept below only for the legacy branch)
        is_desert = biome == BIOME_DESERT
        is_forest = biome == BIOME_FOREST
        is_savanna = biome == BIOME_SAVANNA
    else:
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

    # ── C7 aquatic-food field (climate mode): dense storable aquatic resource (anadromous cold rivers + shellfish
    #    coasts). 0 in legacy mode (unused). Uses C6 water_temp + sea-connectivity from the flow routing. ──
    aquatic_food = np.zeros((N, N), dtype=np.float64)
    if mode == "climate":
        aquatic_food = aquatic_food_field(water_temp, isRiver, is_shore,
                                          drains_to_sea.reshape(N, N), np.clip(npp, 0.0, 1.0))
        aquatic_food[isWater == 1] = 0.0

    # ── Agriculture tier Layer A: cultivability (climate mode) — the 2nd S_pot source, EMERGENT from climate. ──
    cultivability = np.zeros((N, N), dtype=np.float64)
    if mode == "climate":
        cultivability = cultivability_field(temperature, temp_seas_amp, precip_mm, slope, isWater)

    # ── forage_kcal: per-biome mean-scaling (Task 1) + shore bonus (Task 3) ─
    # Original normalised forage[] is preserved. forage_kcal is a separate field.
    forage_kcal = np.zeros((N, N), dtype=np.float64)
    for b_code, target_mean in FORAGE_KCAL_TARGETS.items():
        mask = (biome == b_code)
        if not mask.any() or target_mean <= 0.0:
            continue                       # absent / zero-mean biome: cells stay 0
        # terrain-coupled lognormal(mean, std); std = literature value or 10% fallback
        std = FORAGE_KCAL_STD.get(b_code, DEFAULT_STD_FRAC * target_mean)
        forage_kcal[mask] = _lognormal_rescale(forage, mask, target_mean, std)
    # Shore modifier: additive bonus on land-shore cells (1491.5 kcal/hr; Bird 1997)
    forage_kcal += is_shore.astype(np.float64) * SHORE_BONUS_KCAL

    # ── game_kcal: per-biome mean-scaling of normalized game[] field ────
    # [PROVISIONAL — biome-scaled from return-rate table, pending CC-1 ceiling]
    # Wetland (UNANCHORED), Mountain (UNANCHORED), Water (out of scope) → stay 0.
    # Non-rivalrous (each agent gets full rate); depletion OFF (GD-1 seam).
    game_kcal = np.zeros((N, N), dtype=np.float64)
    for b_code, target_mean in GAME_KCAL_TARGETS.items():
        mask = (biome == b_code)
        if not mask.any() or target_mean <= 0.0:
            continue
        # terrain-coupled lognormal(mean, std); std = literature value or 10% fallback
        std = GAME_KCAL_STD.get(b_code, DEFAULT_STD_FRAC * target_mean)
        game_kcal[mask] = _lognormal_rescale(game, mask, target_mean, std)

    # ── game_mobility: per-biome migratory-game/herd-following factor (SEAM; mechanic deferred) ──
    game_mobility = np.zeros((N, N), dtype=np.float64)
    for b_code, val in GAME_MOBILITY.items():
        game_mobility[biome == b_code] = val

    # ── Neighbour cost (N,N,4): d=0 N, d=1 S, d=2 W, d=3 E ────────────
    nc = np.ones((N, N, 4), dtype=np.float64)   # sentinel = 1.0 at edges
    nc[1:, :, 0]  = cost[:-1, :]   # north: target (y-1, x)
    nc[:-1, :, 1] = cost[1:, :]    # south: target (y+1, x)
    nc[:, 1:, 2]  = cost[:, :-1]   # west:  target (y, x-1)
    nc[:, :-1, 3] = cost[:, 1:]    # east:  target (y, x+1)

    # (Climate temperature + precipitation fields are computed EARLIER — before NPP — so Miami NPP can read them
    #  under mode="climate"; see the "Climate fields (C1/C2)" block above the NPP section. `temperature`,
    #  `temp_seas_amp`, `precip_mm` are already in scope here.)
    humidity = np.full((N, N), MEAN_REL_HUMIDITY, dtype=np.float64)
    # grass_subtype: split BIOME_GRASS by the tropical isotherm (warm → llanos, cool → steppe); 0 elsewhere.
    grass_subtype = np.zeros((N, N), dtype=np.uint8)
    _is_grass = (biome == BIOME_GRASS)
    grass_subtype[_is_grass & (temperature >= GRASS_TROPICAL_THRESHOLD_C)] = GRASS_LLANOS
    grass_subtype[_is_grass & (temperature <  GRASS_TROPICAL_THRESHOLD_C)] = GRASS_STEPPE

    # ── Freeze all arrays ──────────────────────────────────────────────
    for arr in (elev, slope, slopeDeg, wateracc, isWater, isRiver,
                forage, game, cost, nc, risk, biome, npp, forestness, dist,
                npp_gm2, is_shore, forage_kcal, game_kcal, game_mobility, temperature, humidity, grass_subtype,
                temp_seas_amp, precip_mm, water_temp, aquatic_food):
        arr.flags.writeable = False

    return WorldFields(
        elev=elev, slope=slope, slopeDeg=slopeDeg,
        wateracc=wateracc, isWater=isWater, isRiver=isRiver,
        forage=forage, game=game, cost=cost, neighbour_cost=nc,
        risk=risk, biome=biome, npp=npp, forestness=forestness,
        dist=dist, reliefAmpM=reliefAmpM, SEA_LEVEL_M=SEA_LEVEL_M,
        forage_kcal=forage_kcal, npp_gm2=npp_gm2, is_shore=is_shore,
        game_kcal=game_kcal, game_mobility=game_mobility, temperature=temperature, humidity=humidity,
        grass_subtype=grass_subtype, temp_seas_amp=temp_seas_amp, precip_mm=precip_mm, water_temp=water_temp,
        aquatic_food=aquatic_food, cultivability=cultivability,
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
    water_mask_bool = F.isWater.astype(bool)
    water_sizes = _component_sizes(water_mask_bool)
    n_wb = len(water_sizes)
    largest_wb = max(water_sizes) if water_sizes else 0
    char_water_body_size = float(np.median(water_sizes)) if water_sizes else 0.0
    land_sizes = _component_sizes(~water_mask_bool)
    char_interlake_size = float(np.median(land_sizes)) if land_sizes else 0.0
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

    # Task 6 + P1S1b + Stage 1c: validity guards ─────────────────────────
    floor = max(initial_agent_count, 50)
    guard_a_fail = habitable_cell_count < floor
    guard_b_fail = any(counts[b] / total_cells >= 0.95 for b in range(7))
    # Exterior-water guard (P1S1b): kept as diagnostic; no longer gates acceptance.
    # Retired by Stage 1c (mis-specified: area measure firing on edge-connectivity event).
    guard_exterior_water_fail = exterior_water_frac > EXTERIOR_WATER_CEILING
    # Largest-body guard (Stage 1c, §DECISION-LAKE-BODY-GUARD): rejects inland-sea worlds.
    guard_large_body_fail = (largest_wb / total_cells) > LARGE_BODY_CEILING
    invalid_substrate = guard_a_fail or guard_b_fail or guard_large_body_fail

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
        'largest_body_fraction': largest_wb / total_cells,   # backward-compat alias
        # Stage 1c — largest-body guard descriptors (§DECISION-LAKE-BODY-GUARD)
        'largest_water_body_fraction':     largest_wb / total_cells,
        'water_body_count':                n_wb,
        'characteristic_water_body_size':  char_water_body_size,
        'characteristic_interlake_patch_size': char_interlake_size,
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
        # Task 6 + P1S1b + Stage 1c — validity guards
        'invalid_substrate':          invalid_substrate,
        'guard_a_fail':               guard_a_fail,
        'guard_b_fail':               guard_b_fail,
        'guard_exterior_water_fail':  guard_exterior_water_fail,  # diagnostic; not in invalid_substrate
        'guard_large_body_fail':      guard_large_body_fail,
        # forage_kcal diagnostics
        'absent_biomes_forage': absent_biomes,
    }
