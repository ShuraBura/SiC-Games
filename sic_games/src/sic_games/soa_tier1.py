"""Stage 7.5 Workstream A — Tier-1/2 per-agent updates and population reductions.

**Per-agent independent updates (§4.1 step 2):** each function reads only the
agent's own state, so simultaneous (array) == sequential (loop). Validated against
the frozen oracle by the parity harness at the gate earned by the arithmetic:

  * **Tier-1 (bit-identical).** Pure +,−,×,÷, comparison, min/max:
    `cred_decay`, `metabolize_basic`, `si_cred_band`, `eta`,
    `metabolize_si_dormancy`.
  * **Tier-2 (rtol≈1e-9).** Transcendentals: `temperature_carbon`,
    `temperature_si` use `np.tanh`. **Finding (2026-06-06, numpy 2.4.3):**
    `np.tanh` is NOT bit-identical to `math.tanh` — up to ~1 ULP (max rel
    ~2.2e-16). Logged in ARCHITECTURE §12.1-G (platform-pinned).

**Population-level reductions (§4.1 step 3, GATE A1):** column-level aggregates
that replace per-agent-iteration loops, all Tier-2 (numpy pairwise sum may shift
last bits vs left-to-right Python sum):

  * `mean_cred_vec` — O(N) column-mean; kills the O(N²) hotspot in run.py's
    mean_cred-per-birth (oracle calls `sum(a.cred for a in agents)/len(agents)`
    once per newborn → O(N) × O(N_births) = O(N²)/step).
  * `mean_wealth_vec` — same pattern.
  * `gini_vec` — column-level Gini; mirrors `metrics.gini` exactly.
  * `harvest_split_segment` — per-cell harvest shares via CellBuckets segment-
    sum; vectorised replacement for the multi-occupancy `compute_harvest_shares`
    loop (Stage 6.0a path).

Nothing here is wired into `run.py`; the object model stays the reference oracle
until the FINAL gate (decision D4).
"""
from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from sic_games.soa import CellBuckets

# Strategy int codes (mirrors soa.STRATEGY_*; reproduced here to keep this module
# importable without pulling in the full SoA container).
_STRATEGY_CARBON = 1

# ── Tier-2: decision temperature σ (uses tanh → not bit-identical, see header) ──

def temperature_carbon(
    cred: np.ndarray, sigma_base: float, kappa: float, cred_scale: float
) -> np.ndarray:
    """C decision σ_i = σ_base + κ·tanh(𝒞_i / C*).  (Tier-2: np.tanh ≈ math.tanh.)"""
    return sigma_base + kappa * np.tanh(cred / cred_scale)


def temperature_si(
    si_cred: np.ndarray, sigma_si: float, kappa_si: float, c_star_si: float
) -> np.ndarray:
    """Si σ_Si_eff = σ_Si + κ_Si·tanh(si_cred / C*_Si); κ_Si=0 → fixed σ_Si. (Tier-2.)"""
    if kappa_si == 0.0:
        return np.full(si_cred.shape, sigma_si, dtype=np.float64)
    return sigma_si + kappa_si * np.tanh(si_cred / c_star_si)


# ── Tier-1: Cred decay + pending-delta flush (carbon only) ─────────────────────

def cred_decay(
    cred: np.ndarray, pending: np.ndarray, decay: float
) -> tuple[np.ndarray, np.ndarray]:
    """𝒞 ← (1−δ)·𝒞 + Δ_pending, then Δ_pending ← 0. Returns (new_cred, new_pending).

    Mirrors the run.py flush line exactly: `(1 - decay) * cred + pending`.
    """
    new_cred = (1.0 - decay) * cred + pending
    return new_cred, np.zeros_like(pending)


# ── Tier-1: C/greedy metabolize (MetabolicOnly cost) ───────────────────────────

def metabolize_basic(
    wealth: np.ndarray,
    age: np.ndarray,
    max_age: np.ndarray,
    metabolism: np.ndarray,
    harvested: np.ndarray,
    wealth_velocity: np.ndarray,
    velocity_tau: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """C/greedy `act_metabolize`: pay cost, velocity EMA, age++, alive check.

    cost = metabolism (MetabolicOnly). Returns (wealth, age, wealth_velocity, alive).
    Bit-identical to the per-agent scalar path (pure arithmetic).
    """
    cost = metabolism.astype(np.float64)
    delta_w = harvested - cost
    new_wealth = wealth - cost
    if velocity_tau > 0:
        alpha = 1.0 / velocity_tau
        new_v = (1.0 - alpha) * wealth_velocity + alpha * delta_w
    else:
        new_v = wealth_velocity.copy()
    new_age = age + 1
    alive = ~((new_wealth <= 0) | (new_age >= max_age))
    return new_wealth, new_age, new_v, alive


# ── Tier-1: Si Cred near-dormancy band accumulation (Stage 5.1) ────────────────

def si_cred_band(
    si_cred: np.ndarray,
    wealth: np.ndarray,
    metabolism: np.ndarray,
    active: np.ndarray,
    beta: float,
    k_dormant: float,
    k_cred_band: float,
    decay: float,
    c_star_si: float,
) -> np.ndarray:
    """Δsi_cred = 1 if w_lo ≤ wealth < w_hi else 0; si_cred ← min(si_cred·(1−δ)+Δ, C*_Si).

    w_lo = k_dormant·cost, w_hi = (k_dormant+k_cred_band)·cost, cost = metabolism·β.
    Only active (non-dormant) agents accumulate (matches run.py); dormant unchanged.
    Bit-identical (arithmetic + comparison + min).
    """
    cost = metabolism.astype(np.float64) * beta
    w_lo = k_dormant * cost
    w_hi = (k_dormant + k_cred_band) * cost
    delta = ((wealth >= w_lo) & (wealth < w_hi)).astype(np.float64)
    updated = np.minimum(si_cred * (1.0 - decay) + delta, c_star_si)
    return np.where(active, updated, si_cred)


# ── Tier-1: age-efficiency ramp η(a) ───────────────────────────────────────────

def eta(
    age: np.ndarray,
    max_age: np.ndarray,
    forage_age_min: int,
    forage_age_max_offset: int,
    eta_min: float,
    eta_old: float,
    eta_juvenile_exponent: float = 1.0,
) -> np.ndarray:
    """Piecewise-linear η(a) ∈ [eta_min, 1.0], vectorised to match BaseAgent.eta().

    Juvenile ramp (a<a_min), full window (a_min≤a≤a_max), elder decline (a>a_max),
    with a_max = max_age − offset per agent and remaining = max_age − a_max = offset.
    Caller is responsible for agents where the ramp is inactive (η=1.0): pass only
    ramp-active agents, or overwrite η=1.0 where `_use_eta` is False.
    """
    a = age.astype(np.float64)
    a_min = float(forage_age_min)
    a_max = (max_age - forage_age_max_offset).astype(np.float64)
    remaining = a_max.copy()
    remaining[:] = float(forage_age_max_offset)  # = max_age - a_max, constant offset

    # juvenile branch
    if a_min == 0.0:
        juv = np.ones_like(a)
    else:
        _t = a / a_min
        if eta_juvenile_exponent != 1.0:   # must track BaseAgent.eta()'s Kaplan-convex branch
            _t = _t ** eta_juvenile_exponent
        juv = eta_min + (1.0 - eta_min) * _t
    # elder branch (guard offset<=0 → eta_old)
    if forage_age_max_offset <= 0:
        elder = np.full_like(a, eta_old)
    else:
        elder = 1.0 - (1.0 - eta_old) * (a - a_max) / remaining

    out = np.ones_like(a)                      # full window default
    out = np.where(a < a_min, juv, out)
    out = np.where(a > a_max, elder, out)
    return out


# ── Tier-1: Si dormancy-aware metabolize state machine (Stage 4.3) ─────────────

def metabolize_si_dormancy(
    wealth: np.ndarray,
    age: np.ndarray,
    max_age: np.ndarray,
    metabolism: np.ndarray,
    dormant: np.ndarray,
    dormant_steps: np.ndarray,
    alive: np.ndarray,
    beta: float,
    k_dormant: float,
    k_reactivate: float,
    t_dormant_max: int,
    k_carry: float | None = None,
    phi_carry: float = 0.02,
) -> dict:
    """Vectorised Si dormancy metabolize (run.py Phase-3 Si branch), bit-identical.

    Per-agent independent state machine — each agent's transition depends only on
    its own (wealth, age, dormant, dormant_steps) and the shared config, so
    simultaneous == sequential. cost = metabolism·β (ScaledMetabolicCost), with the
    optional Stage-4.5 k_carry wealth-penalty side effect applied first (to all
    agents, dormant included — matching step_cost). Si uses velocity_tau=0 so
    wealth_velocity is never touched here.

    Returns dict of new columns: wealth, age, dormant, dormant_steps, alive, plus
    scalar counters reactivations and permanent_dormancy_deaths (for metrics parity).
    """
    wealth = wealth.astype(np.float64).copy()
    metab = metabolism.astype(np.float64)

    # cost = step_cost: optional k_carry penalty (side effect on wealth), then metab·β
    if k_carry is not None:
        ceiling = k_carry * metab
        over = wealth > ceiling
        wealth = np.where(over, wealth - phi_carry * (wealth - ceiling), wealth)
    cost = metab * beta

    is_dorm = dormant.astype(bool)
    active = ~is_dorm

    # ── dormant branch: steps++, then reactivate (precedence) elif permanent death ──
    stepped = np.where(is_dorm, dormant_steps + 1, dormant_steps)
    reactivate = is_dorm & (wealth >= k_reactivate * cost)
    perm_death = is_dorm & (~reactivate) & (stepped > t_dormant_max)

    # ── active branch: enter dormancy if below floor, else pay cost (normal) ──
    enter_dorm = active & (wealth < k_dormant * cost)
    normal = active & (~enter_dorm)

    new_wealth = np.where(normal, wealth - cost, wealth)

    new_dormant = is_dorm.copy()
    new_dormant = np.where(reactivate, False, new_dormant)
    new_dormant = np.where(enter_dorm, True, new_dormant)

    new_steps = stepped.copy()
    new_steps = np.where(reactivate, 0, new_steps)
    new_steps = np.where(enter_dorm, 0, new_steps)

    new_age = age + 1
    senesce = new_age >= max_age
    starve = normal & (new_wealth <= 0)

    alive_out = alive.astype(bool).copy()
    alive_out = np.where(perm_death, False, alive_out)
    alive_out = np.where(senesce, False, alive_out)
    alive_out = np.where(starve, False, alive_out)

    return {
        "wealth": new_wealth,
        "age": new_age,
        "dormant": new_dormant,
        "dormant_steps": new_steps,
        "alive": alive_out,
        "reactivations": int(reactivate.sum()),
        "permanent_dormancy_deaths": int(perm_death.sum()),
    }


# ══════════════════════════════════════════════════════════════════════════════
# GATE A1 — Population-level reductions (Tier-2, rtol 1e-9)
# ══════════════════════════════════════════════════════════════════════════════

def mean_cred_vec(cred: np.ndarray, alive: np.ndarray) -> float:
    """Mean Cred over living agents — O(N) column-mean; kills the O(N²) hotspot.

    **The hotspot:** Oracle's `mean_cred()` calls `sum(a.cred for a in agents) /
    len(agents)` once per newborn (f_C endowment). In a stable population,
    O(N_births) = O(N) births/step, so the total cost is O(N²)/step. Here, one
    `np.sum` over the column slice is O(N) regardless of birth count.

    Caller passes column slices of length `n_slots` (i.e. `col[:arr.n_slots]`).
    Tier-2: numpy's pairwise summation may differ from the oracle's left-to-right
    Python `sum` by a few ULPs (rtol ≈ 1e-9 in practice, vastly tighter).
    """
    live_cred = cred[alive]
    n = live_cred.size
    return float(np.sum(live_cred) / n) if n > 0 else 0.0


def mean_wealth_vec(wealth: np.ndarray, alive: np.ndarray) -> float:
    """Mean wealth over living agents — O(N) column-mean (Tier-2, rtol 1e-9).

    Oracle: `sum(a.wealth for a in agents) / len(agents)`. Same reasoning and
    tier as `mean_cred_vec`. Caller passes `col[:arr.n_slots]` slices.
    """
    live_w = wealth[alive]
    n = live_w.size
    return float(np.sum(live_w) / n) if n > 0 else 0.0


def gini_vec(values: np.ndarray, alive: np.ndarray) -> float:
    """Gini coefficient over a living-agent column slice (Tier-2, rtol 1e-9).

    Mirrors `metrics.gini(list[float])` exactly: sort ascending, apply the
    symmetric Gini formula. The oracle builds a Python list first (`[a.wealth for
    a in agents]`) and passes it to `metrics.gini`, which then calls `np.sort` and
    the same formula — so the arithmetic is identical once the list is built; the
    tier-2 delta comes only from list-to-array and sum order. Caller passes
    `col[:arr.n_slots]` slices.
    """
    v = values[alive].astype(np.float64)
    n = v.size
    if n < 2:
        return 0.0
    a = np.sort(v)
    total = float(a.sum())
    if total == 0.0:
        return 0.0
    idx = np.arange(1, n + 1, dtype=np.float64)
    weighted_sum = float(((2.0 * idx - n - 1.0) * a).sum())
    return weighted_sum / (n * total)


def harvest_split_segment(
    buckets: "CellBuckets",
    sugar_values: np.ndarray,
    phi: np.ndarray,
    strategy: np.ndarray,
    kappa: float,
    phi_epsilon: float,
) -> np.ndarray:
    """Per-occupant harvest shares via CellBuckets segment-sum (multi-occupancy path).

    Vectorised replacement for the oracle's per-cell loop + `compute_harvest_shares`
    (Stage 6.0a, `multi_occupancy.enabled=True`). For the legacy one-agent-per-cell
    path, each agent harvests its cell directly and this function is not needed.

    Parameters
    ----------
    buckets       : CellBuckets from `arr.bucket_by_cell()`.
    sugar_values  : shape (n_unique_cells,) — the sugar at each occupied cell in
                    `buckets.unique_cells` order (caller reads from sugar_field).
    phi           : phi column slice (length n_slots).
    strategy      : strategy column slice (int64, length n_slots).
    kappa         : contest exponent (0.0 = even split; >0 = Cred-weighted contest).
    phi_epsilon   : φ-floor to avoid zero weights.

    Returns float64 array of length n_slots (indexed by slot).  0 for slots not
    in the buckets (dead agents excluded by bucket_by_cell). Pre-efficiency:
    caller multiplies by η before banking (Σ shares per cell == S exactly).

    Tier-2 (rtol 1e-9): segment-sum division matches the oracle within FP round-
    off; kappa=0 / n=1 paths produce the same result as `compute_harvest_shares`.
    """
    n_slots = phi.size
    result = np.zeros(n_slots, dtype=np.float64)
    if buckets.sorted_idx.size == 0:
        return result

    phi_sorted = phi[buckets.sorted_idx]
    strat_sorted = strategy[buckets.sorted_idx]

    if kappa == 0.0:
        weights = np.ones(buckets.sorted_idx.size, dtype=np.float64)
    else:
        is_carbon = strat_sorted == _STRATEGY_CARBON
        raw_w = (phi_sorted + phi_epsilon) ** kappa
        weights = np.where(is_carbon, raw_w, 1.0)

    for k in range(buckets.unique_cells.size):
        s = int(buckets.seg_starts[k])
        c = int(buckets.seg_counts[k])
        seg = slice(s, s + c)
        w_seg = weights[seg]
        w_total = float(w_seg.sum())
        sugar = float(sugar_values[k])
        if w_total == 0.0:
            cell_shares = np.full(c, sugar / c if c > 0 else 0.0, dtype=np.float64)
        else:
            cell_shares = sugar * w_seg / w_total
        result[buckets.sorted_idx[seg]] = cell_shares

    return result
