"""Stage 7.5 Workstream A — Tier-1/2 per-agent independent updates (vectorised).

The first mechanic migration off the object oracle (blueprint §4.1 step 2):
per-agent updates that read only the agent's own state, so simultaneous (array)
== sequential (loop). Each function here is a pure column op validated against the
frozen oracle by the parity harness (`parity.py`), at the gate its arithmetic
earns (blueprint §3):

  * **Tier-1 (bit-identical).** Pure +,−,×,÷, comparison, min/max:
    `cred_decay`, `metabolize_basic`, `si_cred_band`, `eta`. These match the
    oracle's scalar Python float arithmetic bit-for-bit (IEEE-754 doubles, same
    operation order).
  * **Tier-2 (rtol≈1e-9).** Anything with a transcendental: `temperature_carbon`,
    `temperature_si` use `tanh`. **Finding (2026-06-06, numpy 2.4.3):** `np.tanh`
    is NOT bit-identical to `math.tanh` — it differs by up to ~1 ULP (max rel
    ~2.2e-16). `np.exp` IS bit-identical here. So the σ formula, which §3 listed
    under Tier-1, is in practice **Tier-2 under vectorised tanh** (bit-identical
    only if applied scalar-wise, which forfeits vectorisation). It passes the
    1e-9 gate with enormous margin. Logged in ARCHITECTURE §12.1-F follow-up.

Nothing here is wired into `run.py`; the object model stays the reference oracle
until the FINAL gate (decision D4).
"""
from __future__ import annotations

import numpy as np

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
        juv = eta_min + (1.0 - eta_min) * a / a_min
    # elder branch (guard offset<=0 → eta_old)
    if forage_age_max_offset <= 0:
        elder = np.full_like(a, eta_old)
    else:
        elder = 1.0 - (1.0 - eta_old) * (a - a_max) / remaining

    out = np.ones_like(a)                      # full window default
    out = np.where(a < a_min, juv, out)
    out = np.where(a > a_max, elder, out)
    return out
