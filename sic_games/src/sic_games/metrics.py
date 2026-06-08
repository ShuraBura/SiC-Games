from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np


@dataclass
class StepMetrics:
    step: int
    population: int
    mean_wealth: float
    gini_wealth: float
    spatial_dispersion: float
    mean_age: float
    deaths_starvation: int
    deaths_senescence: int
    total_sugar: float
    # Stage 2 additions — 0.0 / 0 for greedy-Si runs
    mean_cred: float = 0.0
    gini_cred: float = 0.0
    max_cred_fraction: float = 0.0
    mean_sigma: float = 0.0
    joint_task_count: int = 0
    joint_task_participants: int = 0
    # Patch 2.1 mode-switch diagnostics
    mean_w_C: float = 0.0
    mean_velocity: float = 0.0
    frac_suppressed: float = 0.0
    # Cred percentiles (for quartile-starvation analysis)
    cred_p25: float = 0.0
    cred_p50: float = 0.0
    cred_p75: float = 0.0
    # Stage 3 age-split starvation
    deaths_starvation_newborn: int = 0      # age < 20 at death
    deaths_starvation_established: int = 0  # age >= 20 at death
    # Stage 3.2 status-amplification diagnostics
    mean_amplification: float = 0.0   # mean(1 + β·tanh(C_i/C**))
    std_w_C: float = 0.0              # std of effective w_C^(i) — behavioral diversity
    frac_amplified: float = 0.0       # fraction of agents with amplification > 1.1
    # Stage 4 seasonal diagnostics
    mean_effective_capacity: float = 0.0  # tracks seasonal phase
    season_phase: float = 0.0             # t mod T / T, normalized [0,1]
    peak_sugar_mean: float = 0.0          # mean sugar at the two peak cells
    # Stage 3.3 trait-vector summary statistics
    mean_phi: float = 0.0
    std_phi: float = 0.0
    mean_psi: float = 0.0
    std_psi: float = 0.0
    mean_c1: float = 0.0
    std_c1: float = 0.0
    mean_c2: float = 0.0
    std_c2: float = 0.0
    corr_phi_psi: float = 0.0         # Pearson r(phi, psi)
    corr_c1_c2: float = 0.0           # Pearson r(c1, c2)
    morans_i_phi: float = 0.0
    morans_i_psi: float = 0.0
    morans_i_c1: float = 0.0
    morans_i_c2: float = 0.0
    reproduction_fallback_count: int = 0
    # Stage 4.1a variable-population diagnostics
    births_c: int = 0
    births_si: int = 0
    birth_rate_c: float = 0.0        # births_c / N per step
    birth_rate_si: float = 0.0       # births_si / N per step
    net_growth_rate: float = 0.0     # (births - deaths) / N — positive = growing
    carrying_capacity_est: float = 0.0  # total_sugar / mean_metabolism
    population_min: int = 0          # running minimum N(t) seen so far
    # Stage 4.1b life-history + DTM diagnostics
    mean_eta: float = 0.0                      # mean η(a) across living agents
    frac_juvenile: float = 0.0                 # fraction with a < forage_age_min
    frac_elder: float = 0.0                    # fraction with a > forage_age_max_i
    frac_active: float = 0.0                   # fraction in active foraging window
    deaths_starvation_juvenile: int = 0        # starvation deaths in juvenile zone
    deaths_starvation_elder: int = 0           # starvation deaths in elder zone
    births_stress_zone: int = 0                # C births fired at P_max (stress zone)
    births_prosperity_zone: int = 0            # C births fired at decayed P (prosperity)
    stress_zone_rate: float = 0.0              # births_stress_zone / N
    # Stage 4.1c support pool diagnostics
    pool_total_contributed: float = 0.0
    pool_total_drawn: float = 0.0
    pool_draw_unmet: int = 0
    pool_draw_unmet_frac: float = 0.0
    mean_parental_transfer: float = 0.0
    cred_pool_contribution: float = 0.0
    elder_starvation_pct: float = 0.0
    # Stage 4.2: Cred-modulated birth diagnostics
    gamma_birth_boost: float = 0.0  # mean (1 + γ·tanh(C/C***)) across C birth events this step
    # Stage 4.3: Si dormancy diagnostics
    n_active_si: int = 0               # Si agents in active (non-dormant) state
    n_dormant_si: int = 0              # Si agents currently dormant
    dormancy_rate: float = 0.0         # n_dormant_si / (n_active_si + n_dormant_si)
    reactivations_per_step: int = 0    # Si agents that reactivated this step
    permanent_dormancy_deaths: int = 0  # Si agents that exceeded T_dormant_max
    mean_dormancy_duration: float = 0.0 # mean steps dormant per dormancy event (t≥500 window)
    trickle_absorbed_per_step: float = 0.0  # total wealth absorbed by dormant Si agents via trickle
    # Stage 4.3: pool carry-over diagnostics
    pool_carryover_balance: float = 0.0  # pool balance carried in from previous step
    pool_cap_clipped: float = 0.0        # contribution wealth blocked by pool cap this step
    # Stage 4.4: λ inheritance + ψ redesign diagnostics
    lambda_inheritance_boost: float = 0.0  # mean λ×mean_w boost per C birth event this step
    psi_gini: float = 0.0                  # Gini coefficient of ψ distribution
    psi_proximity_utility: float = 0.0     # mean ψ_i × c_proximity_i across C agents
    # Stage 4.4 Diagnostic: C spatial density (Allee dispersal test)
    mean_nearest_C_dist: float = 0.0       # mean Chebyshev dist to nearest C neighbour
    pct_isolated_C: float = 0.0            # % active C agents with no C within r=3
    # Stage 4.5: carrying-cost birth ceiling diagnostics (C only)
    carry_discount_mean: float = float("nan")    # carry_discount(N_C) for this step; nan when disabled
    p_birth_effective_mean: float = float("nan") # mean effective birth prob across C attempts; nan when disabled
    # Stage 5 Task 3: Si Cred diagnostics (0.0 for C runs / disabled Si Cred)
    si_cred_mean: float = 0.0        # mean si_cred across active Si agents
    si_cred_std: float = 0.0         # std of si_cred distribution
    si_cred_gini: float = 0.0        # Gini coefficient of si_cred distribution
    sigma_si_eff_mean: float = 0.0   # mean σ_Si_eff_i = σ_Si + κ × tanh(si_cred/C*)
    # Stage 5.1: near-dormancy band diagnostic
    frac_in_band: float = 0.0        # fraction of active Si agents in near-dormancy band at Phase 1b
    # Stage 5.2 Task 1: c2 defection diagnostics (0.0 when disabled or no JT events)
    defection_rate: float = 0.0      # defections / total JT opportunities (sum of cluster sizes)
    defectors_mean_c2: float = float("nan")   # mean c2 of agents who defected this step
    cooperators_mean_c2: float = float("nan") # mean c2 of agents who cooperated in JT this step
    jt_participation_rate: float = 0.0        # agents in JT / N_active
    # Stage 5.2 Task 2: Deffuant cultural trait diagnostics (C only; 0 / nan when disabled)
    deffuant_updates_per_step: float = 0.0   # fraction of active C agents who updated a trait
    deffuant_no_nbr_frac: float = 0.0        # fraction of C agents with no in-bound neighbour
    c1_mean: float = float("nan")            # population mean of c1 trait (C agents)
    c1_std: float = float("nan")             # population std of c1
    c1_gini: float = float("nan")            # Gini(c1) across active C agents
    c2_mean_trait: float = float("nan")      # population mean of c2 trait (C agents)
    c2_std_trait: float = float("nan")
    c2_gini: float = float("nan")
    psi_mean: float = float("nan")           # population mean of ψ trait (C agents)
    psi_std: float = float("nan")
    # Note: psi_gini reuses the Stage 4.4 field (line 103) — no duplicate needed


def gini(values: list[float]) -> float:
    """Gini coefficient of a list of non-negative values.

    Returns 0 for a single agent or all-equal distribution.
    Vectorised with numpy: identical result, ~5× faster than the Python loop.
    """
    n = len(values)
    if n < 2:
        return 0.0
    a = np.sort(np.asarray(values, dtype=np.float64))
    total = float(a.sum())
    if total == 0:
        return 0.0
    idx = np.arange(1, n + 1, dtype=np.float64)
    weighted_sum = float(((2.0 * idx - n - 1.0) * a).sum())
    return weighted_sum / (n * total)


def spatial_dispersion(positions: list[tuple[int, int]], width: int, height: int) -> float:
    """Mean of std-x and std-y of agent positions (toroidal-aware).

    circular_std vectorised with numpy: identical result, ~4× faster.
    """
    if not positions:
        return 0.0

    n = len(positions)

    def circular_std(coords_arr: np.ndarray, period: int) -> float:
        angles = (2.0 * math.pi / period) * coords_arr
        sin_mean = float(np.sin(angles).mean())
        cos_mean = float(np.cos(angles).mean())
        r = min(math.sqrt(sin_mean ** 2 + cos_mean ** 2), 1.0)
        return math.sqrt(-2.0 * math.log(r)) * period / (2.0 * math.pi)

    pos_arr = np.asarray(positions, dtype=np.float64)
    xs = pos_arr[:, 0]
    ys = pos_arr[:, 1]
    return (circular_std(xs, width) + circular_std(ys, height)) / 2.0


def c_spatial_density(
    c_positions: list[tuple[int, int]],
    width: int,
    height: int,
    isolation_radius: int = 3,
) -> tuple[float, float]:
    """Compute two C spatial density diagnostics (Stage 4.4 Diagnostic).

    Parameters
    ----------
    c_positions : list of (x, y) positions of active C agents.
    width, height : grid dimensions (toroidal).
    isolation_radius : Chebyshev radius used to define 'isolated' (default 3 = parent_radius).

    Returns
    -------
    mean_nearest_C_dist : float
        Mean Chebyshev distance to the nearest other C agent.  0.0 if N<2.
    pct_isolated_C : float
        Percentage of C agents whose nearest C neighbour is beyond isolation_radius.
        100.0 if only 1 agent (trivially isolated).  0.0 if N==0.
    """
    n = len(c_positions)
    if n == 0:
        return 0.0, 0.0
    if n == 1:
        return 0.0, 100.0

    xs = np.array([p[0] for p in c_positions], dtype=np.float64)
    ys = np.array([p[1] for p in c_positions], dtype=np.float64)

    # Toroidal Chebyshev distances (O(N²) — acceptable for N≤500)
    dx = np.abs(xs[:, None] - xs[None, :])
    dy = np.abs(ys[:, None] - ys[None, :])
    dx = np.minimum(dx, width - dx)
    dy = np.minimum(dy, height - dy)
    cheb = np.maximum(dx, dy)

    # Exclude self-distance
    np.fill_diagonal(cheb, np.inf)

    nearest = cheb.min(axis=1)  # shape (N,)
    mean_nearest = float(nearest.mean())
    pct_isolated = float(100.0 * (nearest > isolation_radius).sum() / n)
    return mean_nearest, pct_isolated


def morans_i(
    values: list[float],
    positions: list[tuple[int, int]],
    width: int,
    height: int,
    cutoff: float = 5.0,
    W: "np.ndarray | None" = None,
) -> float:
    """Moran's I spatial autocorrelation with inverse-distance weights (toroidal).

    Uses toroidal Euclidean distance; pairs beyond cutoff get weight 0.
    Returns 0.0 when fewer than 2 agents or zero variance.

    Optional: pass a pre-computed W matrix (from _moran_W()) to avoid
    recomputing when calling for multiple trait vectors on the same positions.
    Uses z @ W @ z (BLAS) instead of element-wise outer-product sum.
    """
    n = len(values)
    if n < 2:
        return 0.0
    v = np.asarray(values, dtype=np.float64)
    if v.std() == 0.0:
        return 0.0

    if W is None:
        W = _moran_W(positions, width, height, cutoff)

    W_sum = float(W.sum())
    if W_sum == 0.0:
        return 0.0

    z = v - v.mean()
    # z @ W @ z is equivalent to (W * z[:,None] * z[None,:]).sum()
    # but uses two O(N²) BLAS calls instead of allocating an extra N×N array.
    numerator = float(z @ W @ z)
    denominator = float((z ** 2).sum())
    if denominator == 0.0:
        return 0.0
    return (n / W_sum) * (numerator / denominator)


def _moran_W(
    positions: list[tuple[int, int]],
    width: int,
    height: int,
    cutoff: float = 5.0,
) -> np.ndarray:
    """Compute the N×N inverse-distance weight matrix for Moran's I.

    Call once per compute_metrics() step and reuse across all four trait
    vectors (phi, psi, c1, c2) — W depends only on agent positions.
    """
    n = len(positions)
    xs = np.array([p[0] for p in positions], dtype=np.float64)
    ys = np.array([p[1] for p in positions], dtype=np.float64)
    dx = np.abs(xs[:, None] - xs[None, :])
    dy = np.abs(ys[:, None] - ys[None, :])
    dx = np.minimum(dx, width - dx)
    dy = np.minimum(dy, height - dy)
    dist = np.sqrt(dx ** 2 + dy ** 2)
    with np.errstate(divide="ignore", invalid="ignore"):
        W = np.where((dist > 0) & (dist <= cutoff), 1.0 / dist, 0.0)
    return W


def _moran_W_csr(
    positions: list[tuple[int, int]],
    width: int,
    height: int,
    cutoff: float = 5.0,
    block_size: int = 1000,
) -> "scipy.sparse.csr_matrix":
    """Build sparse-CSR Moran weight matrix — O(N × block_size) peak memory.

    Gives the same non-zero weights as _moran_W() (identical formula:
    w_ij = 1/dist for dist ≤ cutoff, 0 otherwise; self-pairs and same-cell
    co-agents get weight 0).  The result is stored as a scipy.sparse.csr_matrix
    so that subsequent ``z @ W @ z`` products are O(nnz) rather than O(N²).

    For large N on sparse grids (typical production: N=500, 100×100, cutoff=5),
    nnz ≪ N²; the sparse multiply is 50–150× faster than the dense BLAS equivalent.
    Peak memory is O(N × block_size) during construction instead of O(N²) for
    the dense version — critical for N > ~3 000.

    GATE C1: replaces _moran_W in SoAWorld via the _moran_W_fn hook so the array
    model no longer caps full-step affordable N at ~3–4k.

    Tier-2 gate: result agrees with _moran_W within floating-point sum-order
    variation (|Δ| < 1e-9) — the non-zero entries are computed identically;
    only the summation order in the sparse multiply differs.
    """
    from scipy.sparse import csr_matrix as _csr

    n = len(positions)
    if n == 0:
        return _csr((n, n), dtype=np.float64)

    xs = np.array([p[0] for p in positions], dtype=np.float64)
    ys = np.array([p[1] for p in positions], dtype=np.float64)
    cutoff_sq = cutoff * cutoff

    row_parts: list[np.ndarray] = []
    col_parts: list[np.ndarray] = []
    dat_parts: list[np.ndarray] = []

    for start in range(0, n, block_size):
        end = min(start + block_size, n)

        # Distances from block [start:end] to all n agents — O(block × n) memory
        xi = xs[start:end, None]   # (block, 1)
        yi = ys[start:end, None]
        xj = xs[None, :]           # (1, n)
        yj = ys[None, :]

        dx = np.abs(xi - xj)
        dy = np.abs(yi - yj)
        dx = np.minimum(dx, width  - dx)
        dy = np.minimum(dy, height - dy)
        dist_sq = dx * dx + dy * dy                    # (block, n)

        # Same filter as _moran_W: pairs with dist > 0 and dist ≤ cutoff.
        # dist == 0 covers both self-pairs AND same-cell co-agents (multi-occ) —
        # both get weight 0, matching the oracle behaviour.
        mask = (dist_sq > 0) & (dist_sq <= cutoff_sq)  # (block, n)

        br, bc = np.nonzero(mask)          # local row, global col
        row_parts.append(br + start)       # global row index
        col_parts.append(bc)
        dat_parts.append(1.0 / np.sqrt(dist_sq[br, bc]))

    rows = np.concatenate(row_parts) if row_parts else np.empty(0, np.int64)
    cols = np.concatenate(col_parts) if col_parts else np.empty(0, np.int64)
    data = np.concatenate(dat_parts) if dat_parts else np.empty(0, np.float64)

    return _csr((data, (rows, cols)), shape=(n, n), dtype=np.float64)


def c_spatial_density_blocked(
    c_positions: list[tuple[int, int]],
    width: int,
    height: int,
    isolation_radius: int = 3,
    block_size: int = 500,
) -> tuple[float, float]:
    """c_spatial_density computed in blocks — O(N × block_size) peak memory.

    Gives identical results to c_spatial_density() for all inputs; the only
    difference is that the N×N Chebyshev matrix is never allocated in full.
    For N > 1000 this avoids allocating > 8 MB arrays on every k_density step.

    GATE C1: used by SoAWorld._step_density_diag() to prevent the O(N²)
    memory allocation from capping full-step affordable N.
    """
    n = len(c_positions)
    if n == 0:
        return 0.0, 0.0
    if n == 1:
        return 0.0, 100.0

    xs = np.array([p[0] for p in c_positions], dtype=np.float64)
    ys = np.array([p[1] for p in c_positions], dtype=np.float64)

    nearest = np.full(n, np.inf, dtype=np.float64)

    for start in range(0, n, block_size):
        end = min(start + block_size, n)

        xi = xs[start:end, None]   # (block, 1)
        yi = ys[start:end, None]
        xj = xs[None, :]           # (1, n)
        yj = ys[None, :]

        dx = np.abs(xi - xj)
        dy = np.abs(yi - yj)
        dx = np.minimum(dx, width  - dx)
        dy = np.minimum(dy, height - dy)
        cheb = np.maximum(dx, dy)  # (block, n)

        # Zero out self-distances: local index k → global index start+k
        bsz = end - start
        cheb[np.arange(bsz), np.arange(start, end)] = np.inf

        nearest[start:end] = cheb.min(axis=1)

    mean_nearest = float(nearest.mean())
    pct_isolated = float(100.0 * (nearest > isolation_radius).sum() / n)
    return mean_nearest, pct_isolated


# Task 3 (perf-fix C): module-level Moran's I cache.
# _moran_W (N×N float64) + 4 morans_i calls are O(N²) each.
# Sampled every k_moran steps; intermediate steps reuse cached values.
# Safe under BatchRunner: each worker process has independent module state.
_MORAN_CACHE: dict[str, float] = {"phi": 0.0, "psi": 0.0, "c1": 0.0, "c2": 0.0}


def _pearson(a: list[float], b: list[float]) -> float:
    if len(a) < 2:
        return 0.0
    va, vb = np.array(a, dtype=float), np.array(b, dtype=float)
    if va.std() == 0 or vb.std() == 0:
        return 0.0
    return float(np.corrcoef(va, vb)[0, 1])


def compute_metrics(
    step: int,
    agents,
    sugar_field,
    deaths_starvation: int,
    deaths_senescence: int,
    deaths_starvation_newborn: int = 0,
    deaths_starvation_established: int = 0,
    joint_task_events=None,
    carbon_decision=None,
    si_bounded_sigma: float = 0.0,
    reproduction_fallback_count: int = 0,
    season_phase: float = 0.0,
    mean_effective_capacity: float = 0.0,
    peak_sugar_mean: float = 0.0,
    births_c: int = 0,
    births_si: int = 0,
    population_min: int = 0,
    deaths_starvation_juvenile: int = 0,
    deaths_starvation_elder: int = 0,
    births_stress_zone: int = 0,
    births_prosperity_zone: int = 0,
    pool_total_contributed: float = 0.0,
    pool_total_drawn: float = 0.0,
    pool_draw_unmet: int = 0,
    pool_draw_unmet_frac: float = 0.0,
    mean_parental_transfer: float = 0.0,
    cred_pool_contribution: float = 0.0,
    elder_starvation_pct: float = 0.0,
    gamma_birth_boost: float = 0.0,
    # Stage 4.3: Si dormancy + pool carry-over
    n_active_si: int = 0,
    n_dormant_si: int = 0,
    reactivations_per_step: int = 0,
    permanent_dormancy_deaths: int = 0,
    mean_dormancy_duration: float = 0.0,
    trickle_absorbed_per_step: float = 0.0,
    pool_carryover_balance: float = 0.0,
    pool_cap_clipped: float = 0.0,
    # Stage 4.4: λ + ψ diagnostics
    lambda_inheritance_boost: float = 0.0,
    psi_proximity_utility: float = 0.0,
    # Stage 4.4 Diagnostic: C spatial density
    mean_nearest_C_dist: float = 0.0,
    pct_isolated_C: float = 0.0,
    # Stage 4.5: carrying-cost diagnostics
    carry_discount_mean: float = float("nan"),
    p_birth_effective_mean: float = float("nan"),
    # Stage 5 Task 3: Si Cred diagnostics
    si_cred_mean: float = 0.0,
    si_cred_std: float = 0.0,
    si_cred_gini: float = 0.0,
    sigma_si_eff_mean: float = 0.0,
    # Stage 5.1: near-dormancy band diagnostic
    frac_in_band: float = 0.0,
    # Stage 5.2 Task 1: c2 defection diagnostics
    defection_rate: float = 0.0,
    defectors_mean_c2: float = float("nan"),
    cooperators_mean_c2: float = float("nan"),
    jt_participation_rate: float = 0.0,
    # Stage 5.2 Task 2: Deffuant diagnostics
    deffuant_updates_per_step: float = 0.0,
    deffuant_no_nbr_frac: float = 0.0,
    c1_mean: float = float("nan"),
    c1_std: float = float("nan"),
    c1_gini: float = float("nan"),
    c2_mean_trait: float = float("nan"),
    c2_std_trait: float = float("nan"),
    c2_gini: float = float("nan"),
    psi_mean: float = float("nan"),
    psi_std: float = float("nan"),
    # Note: psi_gini already handled by Stage 4.4 (computed internally as psi_gini_val)
    # Task 3 (perf-fix C): Moran's I sampling period
    k_moran: int = 10,
    # GATE C1: injectable W-matrix builder.  Default None → uses module-level
    # _moran_W() (dense, backward-compatible).  Pass _moran_W_csr to use the
    # sparse-CSR version in SoAWorld without modifying oracle behaviour.
    moran_W_fn=None,
) -> StepMetrics:
    wealths = [a.wealth for a in agents]
    ages = [a.age for a in agents]
    positions = [a.pos for a in agents]
    n = len(agents)

    # Cred metrics
    creds = [a.cred for a in agents]
    mean_cred = sum(creds) / n if n else 0.0
    gini_cred = gini(creds)
    total_cred = sum(creds)
    max_cred_fraction = (max(creds) / total_cred) if total_cred > 0 else 0.0

    # Cred percentiles for quartile analysis
    if n >= 4:
        sc = sorted(creds)
        cred_p25 = sc[n // 4]
        cred_p50 = sc[n // 2]
        cred_p75 = sc[(3 * n) // 4]
    else:
        cred_p25 = cred_p50 = cred_p75 = mean_cred

    # mean_sigma and mode-switch diagnostics
    if carbon_decision is not None:
        mean_sigma = sum(carbon_decision.sigma(a) for a in agents) / n if n else 0.0
        w_c_vals = [carbon_decision.w_C_eff(a) for a in agents]
        mean_w_C = sum(w_c_vals) / n if n else 0.0
        mean_velocity = sum(a.wealth_velocity for a in agents) / n if n else 0.0
        frac_suppressed = (
            sum(1 for a, wc in zip(agents, w_c_vals) if wc < 0.1 * a.phi) / n
            if n else 0.0
        )
        amp_vals = [carbon_decision.amplification(a) for a in agents]
        mean_amplification = sum(amp_vals) / n if n else 0.0
        w_c_mean = mean_w_C
        std_w_C = math.sqrt(sum((w - w_c_mean) ** 2 for w in w_c_vals) / n) if n else 0.0
        frac_amplified = sum(1 for v in amp_vals if v > 1.1) / n if n else 0.0
    elif si_bounded_sigma > 0.0:
        # BoundedRationalSi: temperature is constant and exact
        mean_sigma = si_bounded_sigma
        mean_w_C = 0.0
        mean_velocity = 0.0
        frac_suppressed = 0.0
        mean_amplification = 1.0
        std_w_C = 0.0
        frac_amplified = 0.0
    else:
        mean_sigma = 0.0
        mean_w_C = 0.0
        mean_velocity = 0.0
        frac_suppressed = 0.0
        mean_amplification = 1.0
        std_w_C = 0.0
        frac_amplified = 0.0

    # Stage 3.3 trait-vector metrics
    phi_vals = [a.traits.phi for a in agents] if n and hasattr(agents[0], "traits") else []
    psi_vals = [a.traits.psi for a in agents] if phi_vals else []
    c1_vals  = [a.traits.c1  for a in agents] if phi_vals else []
    c2_vals  = [a.traits.c2  for a in agents] if phi_vals else []
    if phi_vals:
        def _std(lst):
            a = np.array(lst, dtype=float)
            return float(a.std()) if len(a) > 1 else 0.0
        mean_phi = float(np.mean(phi_vals))
        std_phi  = _std(phi_vals)
        mean_psi = float(np.mean(psi_vals))
        std_psi  = _std(psi_vals)
        psi_gini_val = gini(psi_vals)
        mean_c1  = float(np.mean(c1_vals))
        std_c1   = _std(c1_vals)
        mean_c2  = float(np.mean(c2_vals))
        std_c2   = _std(c2_vals)
        corr_phi_psi = _pearson(phi_vals, psi_vals)
        corr_c1_c2   = _pearson(c1_vals, c2_vals)
        # Task 3 (perf-fix C): _moran_W + 4×morans_i sampled every k_moran steps.
        # W depends only on positions; Moran's I is a diagnostic logged metric only.
        # GATE C1: moran_W_fn hook lets SoAWorld substitute _moran_W_csr (sparse)
        # without changing the oracle.  morans_i() accepts both dense numpy arrays
        # and scipy.sparse CSR matrices via the W= kwarg (@ works for both).
        _w_builder = moran_W_fn if moran_W_fn is not None else _moran_W
        if step % k_moran == 0:
            _W = _w_builder(positions, sugar_field.width, sugar_field.height)
            _MORAN_CACHE["phi"] = morans_i(phi_vals, positions, sugar_field.width, sugar_field.height, W=_W)
            _MORAN_CACHE["psi"] = morans_i(psi_vals, positions, sugar_field.width, sugar_field.height, W=_W)
            _MORAN_CACHE["c1"]  = morans_i(c1_vals,  positions, sugar_field.width, sugar_field.height, W=_W)
            _MORAN_CACHE["c2"]  = morans_i(c2_vals,  positions, sugar_field.width, sugar_field.height, W=_W)
        mi_phi = _MORAN_CACHE["phi"]
        mi_psi = _MORAN_CACHE["psi"]
        mi_c1  = _MORAN_CACHE["c1"]
        mi_c2  = _MORAN_CACHE["c2"]
    else:
        mean_phi = std_phi = mean_psi = std_psi = 0.0
        mean_c1  = std_c1  = mean_c2  = std_c2  = 0.0
        corr_phi_psi = corr_c1_c2 = 0.0
        mi_phi = mi_psi = mi_c1 = mi_c2 = 0.0
        psi_gini_val = 0.0

    # Joint task counts
    if joint_task_events:
        jt_count = len(joint_task_events)
        jt_participants = sum(len(e.cluster) for e in joint_task_events)
    else:
        jt_count = 0
        jt_participants = 0

    # Stage 4.1a birth/population diagnostics
    total_births = births_c + births_si
    total_deaths = deaths_starvation + deaths_senescence
    birth_rate_c = births_c / n if n else 0.0
    birth_rate_si = births_si / n if n else 0.0
    net_growth_rate = (total_births - total_deaths) / n if n else 0.0
    mean_metabolism = sum(a.metabolism for a in agents) / n if n else 1.0
    carrying_capacity_est = sugar_field.total_sugar() / mean_metabolism if mean_metabolism > 0 else 0.0

    # Stage 4.1b life-history metrics (no-op when _use_eta=False → all eta=1.0)
    if n and hasattr(agents[0], "_use_eta") and agents[0]._use_eta:
        eta_vals = [a.eta() for a in agents]
        mean_eta = sum(eta_vals) / n
        n_juv = sum(1 for a in agents if a.is_juvenile())
        n_eld = sum(1 for a in agents if a.is_elder())
        frac_juvenile = n_juv / n
        frac_elder = n_eld / n
        frac_active = 1.0 - frac_juvenile - frac_elder
    else:
        mean_eta = 1.0
        frac_juvenile = frac_elder = 0.0
        frac_active = 1.0

    stress_zone_rate = births_stress_zone / n if n else 0.0

    return StepMetrics(
        step=step,
        population=n,
        mean_wealth=sum(wealths) / n if n else 0.0,
        gini_wealth=gini(wealths),
        spatial_dispersion=spatial_dispersion(
            positions, sugar_field.width, sugar_field.height
        ),
        mean_age=sum(ages) / n if n else 0.0,
        deaths_starvation=deaths_starvation,
        deaths_senescence=deaths_senescence,
        total_sugar=sugar_field.total_sugar(),
        mean_cred=mean_cred,
        gini_cred=gini_cred,
        max_cred_fraction=max_cred_fraction,
        mean_sigma=mean_sigma,
        joint_task_count=jt_count,
        joint_task_participants=jt_participants,
        mean_w_C=mean_w_C,
        mean_velocity=mean_velocity,
        frac_suppressed=frac_suppressed,
        cred_p25=cred_p25,
        cred_p50=cred_p50,
        cred_p75=cred_p75,
        deaths_starvation_newborn=deaths_starvation_newborn,
        deaths_starvation_established=deaths_starvation_established,
        mean_amplification=mean_amplification,
        std_w_C=std_w_C,
        frac_amplified=frac_amplified,
        mean_phi=mean_phi,
        std_phi=std_phi,
        mean_psi=mean_psi,
        std_psi=std_psi,
        mean_c1=mean_c1,
        std_c1=std_c1,
        mean_c2=mean_c2,
        std_c2=std_c2,
        corr_phi_psi=corr_phi_psi,
        corr_c1_c2=corr_c1_c2,
        morans_i_phi=mi_phi,
        morans_i_psi=mi_psi,
        morans_i_c1=mi_c1,
        morans_i_c2=mi_c2,
        reproduction_fallback_count=reproduction_fallback_count,
        mean_effective_capacity=mean_effective_capacity,
        season_phase=season_phase,
        peak_sugar_mean=peak_sugar_mean,
        births_c=births_c,
        births_si=births_si,
        birth_rate_c=birth_rate_c,
        birth_rate_si=birth_rate_si,
        net_growth_rate=net_growth_rate,
        carrying_capacity_est=carrying_capacity_est,
        population_min=population_min,
        mean_eta=mean_eta,
        frac_juvenile=frac_juvenile,
        frac_elder=frac_elder,
        frac_active=frac_active,
        deaths_starvation_juvenile=deaths_starvation_juvenile,
        deaths_starvation_elder=deaths_starvation_elder,
        births_stress_zone=births_stress_zone,
        births_prosperity_zone=births_prosperity_zone,
        stress_zone_rate=stress_zone_rate,
        pool_total_contributed=pool_total_contributed,
        pool_total_drawn=pool_total_drawn,
        pool_draw_unmet=pool_draw_unmet,
        pool_draw_unmet_frac=pool_draw_unmet_frac,
        mean_parental_transfer=mean_parental_transfer,
        cred_pool_contribution=cred_pool_contribution,
        elder_starvation_pct=elder_starvation_pct,
        gamma_birth_boost=gamma_birth_boost,
        n_active_si=n_active_si,
        n_dormant_si=n_dormant_si,
        dormancy_rate=(n_dormant_si / (n_active_si + n_dormant_si)) if (n_active_si + n_dormant_si) > 0 else 0.0,
        reactivations_per_step=reactivations_per_step,
        permanent_dormancy_deaths=permanent_dormancy_deaths,
        mean_dormancy_duration=mean_dormancy_duration,
        trickle_absorbed_per_step=trickle_absorbed_per_step,
        pool_carryover_balance=pool_carryover_balance,
        pool_cap_clipped=pool_cap_clipped,
        lambda_inheritance_boost=lambda_inheritance_boost,
        psi_gini=psi_gini_val,
        psi_proximity_utility=psi_proximity_utility,
        mean_nearest_C_dist=mean_nearest_C_dist,
        pct_isolated_C=pct_isolated_C,
        carry_discount_mean=carry_discount_mean,
        p_birth_effective_mean=p_birth_effective_mean,
        si_cred_mean=si_cred_mean,
        si_cred_std=si_cred_std,
        si_cred_gini=si_cred_gini,
        sigma_si_eff_mean=sigma_si_eff_mean,
        frac_in_band=frac_in_band,
        defection_rate=defection_rate,
        defectors_mean_c2=defectors_mean_c2,
        cooperators_mean_c2=cooperators_mean_c2,
        jt_participation_rate=jt_participation_rate,
        deffuant_updates_per_step=deffuant_updates_per_step,
        deffuant_no_nbr_frac=deffuant_no_nbr_frac,
        c1_mean=c1_mean,
        c1_std=c1_std,
        c1_gini=c1_gini,
        c2_mean_trait=c2_mean_trait,
        c2_std_trait=c2_std_trait,
        c2_gini=c2_gini,
        psi_mean=psi_mean,
        psi_std=psi_std,
        # psi_gini reuses Stage 4.4 field — already set above via psi_gini=psi_gini_val
    )


# ─── R6 terminal-state summary (Stage 5.2) ────────────────────────────────────

def compute_run_summary(df: "pd.DataFrame", strategy: str = "carbon") -> dict:
    """Compute R6 terminal-state summary from a completed run's metrics DataFrame.

    Returns a dict with:
      extinction_step  : int | None   — step of first zero-population event, None if survived
      N_min            : int          — minimum population over the run
      argmin_t         : int          — step at which N_min occurred (first occurrence)
      N_active_t_end   : int          — population at the final recorded step
      n_steps          : int          — total number of recorded steps

    The population column used:
      - strategy == 'si_bounded' : 'n_active_si'  (excludes dormant agents)
      - otherwise                : 'population'
    """
    import pandas as _pd  # local import to avoid circular at module level

    pop_col = "n_active_si" if strategy == "si_bounded" else "population"
    if pop_col not in df.columns:
        pop_col = "population"

    pop = df[pop_col]

    extinct_rows = df.loc[pop == 0]
    extinction_step: int | None = (
        int(extinct_rows["step"].iloc[0]) if not extinct_rows.empty else None
    )

    n_min = int(pop.min())
    argmin_t = int(df.loc[pop.idxmin(), "step"])
    n_active_t_end = int(pop.iloc[-1])
    n_steps = int(df["step"].iloc[-1]) + 1 if not df.empty else 0

    return {
        "extinction_step": extinction_step,
        "N_min": n_min,
        "argmin_t": argmin_t,
        "N_active_t_end": n_active_t_end,
        "n_steps": n_steps,
    }
