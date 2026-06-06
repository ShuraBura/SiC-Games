"""Stage 7.5 Workstream A — Tier-1/2 per-mechanic parity (blueprint §4.1 step 2).

Each vectorised per-agent update in `soa_tier1` is validated against the frozen
object oracle at the gate its arithmetic earns (blueprint §3):
  * pure-arithmetic updates → bit-identical (Tier 1);
  * tanh-bearing σ → rtol 1e-9 (Tier 2; np.tanh ≠ math.tanh by ~1 ULP here).
This is the "prove the harness on the safe cases" step toward GATE A0.
"""
from __future__ import annotations

import numpy as np

from sic_games.config import Config
from sic_games.parity import compare, snapshot
from sic_games.run import SugarWorld
from sic_games.soa import AgentArray
from sic_games.soa_tier1 import (
    cred_decay,
    eta,
    metabolize_basic,
    metabolize_si_dormancy,
    si_cred_band,
    temperature_carbon,
    temperature_si,
)


def _model(strategy="greedy", steps=0, **cfg_over):
    base = dict(
        agents={"initial_population": 40},
        world={"grid_size": (14, 14), "sugar_peaks": [(3, 3), (10, 10)]},
        decision={"strategy": strategy},
        run={"n_steps": max(steps, 1)},
    )
    base.update(cfg_over)
    m = SugarWorld(Config(**base))
    for _ in range(steps):
        m.step()
    return m


def _ordered(model):
    """Agents in snapshot order (model.agents iteration order)."""
    return list(model.agents)


# ── Tier-2: decision temperature σ (tanh) ──────────────────────────────────────

def test_temperature_carbon_tier2():
    m = _model("carbon")
    agents = _ordered(m)
    for a in agents:
        a.cred = (a.unique_id % 20) * 0.7      # spread cred so tanh is exercised
    arr = snapshot(m)
    n = arr.n_slots
    cd = m._carbon_decision
    oracle = np.array([cd.temperature(a) for a in agents])
    vec = temperature_carbon(arr.columns["cred"][:n], cd.sigma_base, cd.kappa, cd.cred_scale)
    # Tier-2: matches to 1e-9 (vastly better — ~1 ULP from np.tanh vs math.tanh)
    assert np.allclose(vec, oracle, rtol=1e-9, atol=0.0)
    assert float(np.abs(vec - oracle).max()) < 1e-12


def test_temperature_si_modulated_tier2():
    m = _model("si_bounded", si_cred={"enabled": True, "kappa_Si": 0.5})
    agents = _ordered(m)
    for a in agents:
        a.si_cred = (a.unique_id % 11) * 0.9
    arr = snapshot(m)
    n = arr.n_slots
    dec = m._decision
    oracle = np.array([dec.temperature(a) for a in agents])
    vec = temperature_si(arr.columns["si_cred"][:n], dec.sigma_si, dec.kappa_si, dec.c_star_si)
    assert np.allclose(vec, oracle, rtol=1e-9, atol=0.0)


def test_temperature_si_fixed_is_bit_identical():
    # kappa_Si = 0 → fixed σ_Si, no tanh → exact
    m = _model("si_bounded")  # si_cred disabled → kappa_si=0
    agents = _ordered(m)
    arr = snapshot(m)
    n = arr.n_slots
    dec = m._decision
    oracle = np.array([dec.temperature(a) for a in agents])
    vec = temperature_si(arr.columns["si_cred"][:n], dec.sigma_si, dec.kappa_si, dec.c_star_si)
    assert np.array_equal(vec, oracle)


# ── Tier-1: cred decay (bit-identical) ─────────────────────────────────────────

def test_cred_decay_bit_identical():
    n = 50
    rng = np.random.default_rng(1)
    cred = rng.uniform(0, 10, n)
    pending = rng.uniform(0, 2, n)
    decay = 0.01
    new_cred, new_pending = cred_decay(cred, pending, decay)
    ref = np.array([(1.0 - decay) * cred[i] + pending[i] for i in range(n)])  # exact oracle line
    assert np.array_equal(new_cred, ref)
    assert np.all(new_pending == 0.0)


# ── Tier-1: C/greedy metabolize (bit-identical), via the parity harness ────────

def _metabolize_parity(strategy):
    m = _model(strategy, steps=3)
    agents = _ordered(m)
    for a in agents:
        a._last_harvested = float((a.unique_id % 7) * 1.3)
        a._last_moved = False
    arr0 = snapshot(m)
    n = arr0.n_slots
    vt = m._velocity_tau
    harvested = np.array([float((a.unique_id % 7) * 1.3) for a in agents])

    # vectorised on the pre-state snapshot
    nw, na, nv, al = metabolize_basic(
        arr0.columns["wealth"][:n], arr0.columns["age"][:n], arr0.columns["max_age"][:n],
        arr0.columns["metabolism"][:n], harvested, arr0.columns["wealth_velocity"][:n], vt,
    )

    # oracle mutates the agents
    for a in agents:
        a.act_metabolize(velocity_tau=vt)
    o_w = np.array([a.wealth for a in agents])
    o_age = np.array([a.age for a in agents])
    o_v = np.array([a.wealth_velocity for a in agents])
    o_alive = np.array([a.alive for a in agents])

    assert np.array_equal(nw, o_w)
    assert np.array_equal(na, o_age)
    assert np.array_equal(nv, o_v)
    assert np.array_equal(al, o_alive)


def test_metabolize_greedy_bit_identical():
    _metabolize_parity("greedy")        # velocity_tau = 0


def test_metabolize_carbon_bit_identical():
    _metabolize_parity("carbon")        # velocity_tau = 10 (velocity EMA exercised)


def test_metabolize_via_harness_compare():
    # End-to-end through the parity harness: write vectorised results into an
    # AgentArray and diff against an oracle re-snapshot at the bit gate.
    m = _model("carbon", steps=3)
    agents = _ordered(m)
    for a in agents:
        a._last_harvested = float((a.unique_id % 5) * 2.0)
        a._last_moved = False
    arr0 = snapshot(m)
    n = arr0.n_slots
    vt = m._velocity_tau
    harvested = np.array([float((a.unique_id % 5) * 2.0) for a in agents])
    nw, na, nv, al = metabolize_basic(
        arr0.columns["wealth"][:n], arr0.columns["age"][:n], arr0.columns["max_age"][:n],
        arr0.columns["metabolism"][:n], harvested, arr0.columns["wealth_velocity"][:n], vt,
    )
    arr_vec = AgentArray.from_oracle(m)   # same pre-state
    nv_slots = arr_vec.n_slots
    arr_vec.columns["wealth"][:nv_slots] = nw
    arr_vec.columns["age"][:nv_slots] = na
    arr_vec.columns["wealth_velocity"][:nv_slots] = nv
    arr_vec.columns["alive"][:nv_slots] = al

    for a in agents:
        a.act_metabolize(velocity_tau=vt)
    arr_oracle = snapshot(m)

    rep = compare(arr_oracle, arr_vec,
                  columns=("wealth", "age", "wealth_velocity"))
    assert rep.passed, rep.summary()


# ── Tier-1: Si Cred near-dormancy band (bit-identical) ─────────────────────────

def test_si_cred_band_bit_identical():
    m = _model("si_bounded", steps=2,
               si_cred={"enabled": True, "kappa_Si": 0.5},
               dormancy={"enabled": True})
    agents = _ordered(m)
    for a in agents:
        a.wealth = float((a.unique_id % 5) * a.metabolism)   # span bands
        a.si_cred = (a.unique_id % 8) * 0.6
        a.dormant = (a.unique_id % 4 == 0)                   # some dormant
    arr = snapshot(m)
    n = arr.n_slots
    beta = m._si_cost_model.beta
    k_dormant = m._dormancy_cfg.k_dormant
    sc = m._si_cred_cfg

    active = ~arr.columns["dormant"][:n]
    vec = si_cred_band(
        arr.columns["si_cred"][:n], arr.columns["wealth"][:n], arr.columns["metabolism"][:n],
        active, beta, k_dormant, sc.k_cred_band, sc.decay, sc.C_star_Si,
    )

    ref = []
    for a in agents:
        if not a.dormant:
            cost = a.metabolism * beta
            w_lo = k_dormant * cost
            w_hi = (k_dormant + sc.k_cred_band) * cost
            delta = 1.0 if w_lo <= a.wealth < w_hi else 0.0
            ref.append(min(a.si_cred * (1.0 - sc.decay) + delta, sc.C_star_Si))
        else:
            ref.append(a.si_cred)
    assert np.array_equal(vec, np.array(ref))


# ── Tier-1: η(a) age-efficiency ramp (bit-identical) ───────────────────────────

def test_eta_bit_identical():
    m = _model("carbon")  # carbon agents have the η ramp active (life_history default)
    agents = _ordered(m)
    for a in agents:
        a.age = a.unique_id % 90   # spread across juvenile / full / elder
    arr = snapshot(m)
    n = arr.n_slots
    lh = m.cfg.life_history
    vec = eta(
        arr.columns["age"][:n], arr.columns["max_age"][:n],
        lh.forage_age_min, lh.forage_age_max_offset, lh.eta_min, lh.eta_old,
    )
    oracle = np.array([a.eta() for a in agents])
    assert np.array_equal(vec, oracle)


# ── Tier-1: Si dormancy-aware metabolize state machine (bit-identical) ──────────

def _setup_si_dormancy_branches(agents, beta, k_dormant, k_reactivate, t_dormant_max):
    """Assign states covering every branch of the Si dormancy state machine."""
    for i, a in enumerate(agents):
        a.age = 30
        a.alive = True
        a._last_moved = False
        a._last_harvested = 0.0
        cost = a.metabolism * beta
        r = i % 7
        if r == 0:    # dormant -> reactivate (wealth >= k_react*cost)
            a.dormant, a.dormant_steps, a.wealth = True, 10, k_reactivate * cost + 1.0
        elif r == 1:  # dormant -> permanent death (steps+1 > t_max, no reactivate)
            a.dormant, a.dormant_steps, a.wealth = True, t_dormant_max + 1, 0.5 * cost
        elif r == 2:  # dormant -> continue dormant
            a.dormant, a.dormant_steps, a.wealth = True, 5, 0.5 * cost
        elif r == 3:  # active -> enter dormancy (wealth < k_dormant*cost)
            a.dormant, a.dormant_steps, a.wealth = False, 0, 0.5 * k_dormant * cost
        elif r == 4:  # active -> normal, survive
            a.dormant, a.dormant_steps, a.wealth = False, 0, 5.0 * cost
        elif r == 5:  # active -> normal, starve (wealth == cost -> 0 after pay)
            a.dormant, a.dormant_steps, a.wealth = False, 0, cost
        else:         # active -> normal, senesce next step
            a.dormant, a.dormant_steps, a.wealth = False, 0, 5.0 * cost
            a.age = a.max_age - 1


def _oracle_si_metabolize(agents, k_dormant, k_reactivate, t_dormant_max):
    """Faithful transcription of run.py's Si dormancy metabolize block.

    Uses the REAL cost model (agent._cost.step_cost) — only the branch control flow
    is transcribed from run.py. Mutates agents; returns (reactivations, perm_deaths).
    """
    react = perm = 0
    for a in agents:
        cost = a._cost.step_cost(a, {"moved": a._last_moved, "harvested": a._last_harvested})
        if a.dormant:
            a.dormant_steps += 1
            if a.wealth >= k_reactivate * cost:
                a.dormant = False
                a.dormant_steps = 0
                react += 1
            elif a.dormant_steps > t_dormant_max:
                a.alive = False
                perm += 1
            a.age += 1
            if a.age >= a.max_age:
                a.alive = False
        else:
            if a.wealth < k_dormant * cost:
                a.dormant = True
                a.dormant_steps = 0
                a.age += 1
                if a.age >= a.max_age:
                    a.alive = False
            else:
                a.wealth -= cost
                a.age += 1
                if a.wealth <= 0 or a.age >= a.max_age:
                    a.alive = False
    return react, perm


def test_metabolize_si_dormancy_bit_identical():
    m = _model("si_bounded", steps=2,
               si_bounded={"beta_metabolism": 5.0},
               dormancy={"enabled": True})
    agents = _ordered(m)
    beta = m._si_cost_model.beta
    dc = m._dormancy_cfg
    _setup_si_dormancy_branches(agents, beta, dc.k_dormant, dc.k_reactivate, dc.t_dormant_max)

    arr = snapshot(m)
    n = arr.n_slots
    res = metabolize_si_dormancy(
        arr.columns["wealth"][:n], arr.columns["age"][:n], arr.columns["max_age"][:n],
        arr.columns["metabolism"][:n], arr.columns["dormant"][:n],
        arr.columns["dormant_steps"][:n], arr.columns["alive"][:n],
        beta, dc.k_dormant, dc.k_reactivate, dc.t_dormant_max,
        k_carry=m._si_cost_model.k_carry, phi_carry=m._si_cost_model.phi_carry,
    )

    react, perm = _oracle_si_metabolize(agents, dc.k_dormant, dc.k_reactivate, dc.t_dormant_max)

    assert np.array_equal(res["wealth"], np.array([a.wealth for a in agents]))
    assert np.array_equal(res["age"], np.array([a.age for a in agents]))
    assert np.array_equal(res["dormant"], np.array([a.dormant for a in agents]))
    assert np.array_equal(res["dormant_steps"], np.array([a.dormant_steps for a in agents]))
    assert np.array_equal(res["alive"], np.array([a.alive for a in agents]))
    assert res["reactivations"] == react
    assert res["permanent_dormancy_deaths"] == perm
    # sanity: the setup actually exercised the interesting branches
    assert react > 0 and perm > 0


def test_metabolize_si_dormancy_kcarry_penalty():
    # k_carry wealth-penalty side effect (Stage 4.5) must match step_cost exactly
    m = _model("si_bounded", steps=1,
               si_bounded={"beta_metabolism": 5.0, "k_carry": 2.0, "phi_carry": 0.02},
               dormancy={"enabled": True})
    agents = _ordered(m)
    beta = m._si_cost_model.beta
    dc = m._dormancy_cfg
    for i, a in enumerate(agents):
        a.age, a.alive, a.dormant, a.dormant_steps = 30, True, False, 0
        a._last_moved, a._last_harvested = False, 0.0
        a.wealth = float((i % 6) * 4 * a.metabolism)   # some above the k_carry ceiling

    arr = snapshot(m)
    n = arr.n_slots
    res = metabolize_si_dormancy(
        arr.columns["wealth"][:n], arr.columns["age"][:n], arr.columns["max_age"][:n],
        arr.columns["metabolism"][:n], arr.columns["dormant"][:n],
        arr.columns["dormant_steps"][:n], arr.columns["alive"][:n],
        beta, dc.k_dormant, dc.k_reactivate, dc.t_dormant_max,
        k_carry=m._si_cost_model.k_carry, phi_carry=m._si_cost_model.phi_carry,
    )
    _oracle_si_metabolize(agents, dc.k_dormant, dc.k_reactivate, dc.t_dormant_max)
    assert np.array_equal(res["wealth"], np.array([a.wealth for a in agents]))
    assert np.array_equal(res["alive"], np.array([a.alive for a in agents]))
