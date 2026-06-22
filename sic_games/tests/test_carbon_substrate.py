"""Carbon-on-substrate Tier-1 — the Cred hierarchy on the demographic meat economy.

Locks: (1) the `status_of` hook (meat/contest weight reads `cred` under the carbon flag, else `φ` — preserving
the Sugarscape contest tests); (2) Cred-weighted meat concentrates the share on high-Cred agents; (3) G.3
mean-preserving lognormal meat draw; (4) founder Cred seeding produces a heterogeneous heritable hierarchy;
(5) determinism with the new draws. All opt-in (default flags off → 452 unchanged).
"""
from __future__ import annotations

import math
import statistics

from sic_games.substrate import status_of, compute_harvest_shares
from sic_games.config import KcalEconomyConfig, SubstrateConfig, CarbonConfig
from sic_games.demography import DemographyConfig
from sic_games.phase1_model import TerrainWorld


class _MockA:
    def __init__(self, phi=0.5, cred=0.0, strategy="carbon", use_cred_status=False):
        self.phi = phi
        self.cred = cred
        self.strategy = strategy
        self.use_cred_status = use_cred_status


# ── status_of hook ────────────────────────────────────────────────────────────
def test_status_of_defaults_to_phi():
    a = _MockA(phi=0.7, cred=5.0, use_cred_status=False)
    assert status_of(a) == 0.7            # cred ignored unless flagged


def test_status_of_reads_cred_when_flagged():
    a = _MockA(phi=0.7, cred=5.0, use_cred_status=True)
    assert status_of(a) == 5.0


def test_status_of_missing_attr_is_phi():
    class Bare:
        phi = 0.3; strategy = "carbon"
    assert status_of(Bare()) == 0.3       # getattr default → φ (preserves mock-agent tests)


# ── Cred-weighted meat concentrates the share (the mechanism) ──────────────────
def test_cred_weighted_meat_favors_high_cred():
    occ = [_MockA(cred=1.0, use_cred_status=True), _MockA(cred=4.0, use_cred_status=True)]
    shares = compute_harvest_shares(occ, 20.0, kappa=1.0, phi_epsilon=1e-6)
    assert shares[1] > shares[0]                       # higher cred → larger meat share
    assert abs(sum(shares) - 20.0) < 1e-9              # conserved


def test_cred_uniform_when_flag_off():
    # same creds but flag off → weight reads φ (uniform 0.5) → equal split despite cred spread
    occ = [_MockA(cred=1.0, use_cred_status=False), _MockA(cred=9.0, use_cred_status=False)]
    shares = compute_harvest_shares(occ, 20.0, kappa=1.0, phi_epsilon=1e-6)
    assert abs(shares[0] - shares[1]) < 1e-9


# ── G.3 mean-preserving lognormal draw ─────────────────────────────────────────
def test_g3_lognormal_is_mean_preserving():
    import random
    rng = random.Random(0)
    M, cv = 100.0, 0.73
    sig = math.sqrt(math.log(1.0 + cv * cv))
    draws = [math.exp(rng.normalvariate(math.log(M) - 0.5 * sig * sig, sig)) for _ in range(40000)]
    assert abs(statistics.mean(draws) - M) / M < 0.03          # mean preserved (~M)
    assert statistics.pstdev(draws) / statistics.mean(draws) > 0.5   # real variance present


# ── model-level: seeding hierarchy + determinism ──────────────────────────────
def _carbon_world(seed=42, cv=0.0, cred_status=False, seed_sigma=0.0, kappa=1.0, n=200):
    return TerrainWorld(
        n_agents=n, kcal_cfg=KcalEconomyConfig(), seed=seed, game_stream=False,
        carbon_cfg=CarbonConfig(kappa=0.0),    # movement temperature held at σ_base (isolate meat from movement)
        substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                      contest_exponent=kappa, move_cost_flat=0.0),
        demography_cfg=DemographyConfig(enable_game=True, game_meat_frac=0.55, game_meat_cv=cv,
                                        enable_cred_status=cred_status, cred_seed_sigma=seed_sigma,
                                        cred_inherit_sigma=0.1),
    )


def test_founder_cred_seeding_is_heterogeneous():
    w = _carbon_world(cred_status=True, seed_sigma=0.5)
    creds = [a.cred for a in w.agent_list]
    assert all(getattr(a, "use_cred_status") for a in w.agent_list)
    assert statistics.pstdev(creds) > 0.1            # a real hierarchy, not uniform
    assert min(creds) > 0.0                          # lognormal → strictly positive


def test_founder_cred_uniform_when_seed_sigma_zero():
    w = _carbon_world(cred_status=True, seed_sigma=0.0)
    creds = [a.cred for a in w.agent_list]
    assert all(c == 0.0 for c in creds)              # unseeded → cred stays 0 (status_of → (0+ε)^κ uniform)


def test_carbon_g3_determinism():
    w1 = _carbon_world(seed=7, cv=0.73, cred_status=True, seed_sigma=0.5)
    w2 = _carbon_world(seed=7, cv=0.73, cred_status=True, seed_sigma=0.5)
    for _ in range(10):
        w1.step(); w2.step()
    assert len(w1.agent_list) == len(w2.agent_list)
    assert sorted(a.wealth for a in w1.agent_list) == sorted(a.wealth for a in w2.agent_list)
