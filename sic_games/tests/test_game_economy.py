"""Game/meat two-stream economy — blueprint v2 G.1 (Cordain split) + G.2 (κ on meat).

Locks: (1) MEAT_FRAC values (Cordain 2000 Table 2, terrestrial-renormalized); (2) energy conservation /
κ=0 inertness — the two-stream split sums to the single stream (exact back-compat); (3) the RT-B contract —
forage stays EQUAL at κ>0 while meat is Cred-weighted (κ is NOT double-applied); (4) model-level wiring:
game-on at κ=0 reproduces game-off exactly.
"""
from __future__ import annotations

from sic_games.substrate import compute_harvest_shares
from sic_games.config import KcalEconomyConfig, SubstrateConfig
from sic_games.demography import DemographyConfig
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import (
    MEAT_FRAC, BIOME_FOREST, BIOME_DESERT, BIOME_SAVANNA, BIOME_GRASS,
)


class _MockA:
    """compute_harvest_shares reads only .phi and .strategy."""
    def __init__(self, phi: float = 0.5, strategy: str = "carbon") -> None:
        self.phi = phi
        self.strategy = strategy


def _two_stream(occ, S, mf, kappa, eps=1e-6):
    """Replicate the model's _step_rivalrous two-stream composition (forage κ=0 + meat κ)."""
    f = compute_harvest_shares(occ, (1.0 - mf) * S, 0.0, eps)
    m = compute_harvest_shares(occ, mf * S, kappa, eps)
    return [a + b for a, b in zip(f, m)], f, m


# ── MEAT_FRAC (Cordain 2000 Table 2) ──────────────────────────────────────────
def test_meat_frac_in_unit_interval():
    assert all(0.0 < v < 1.0 for v in MEAT_FRAC.values())


def test_meat_frac_forest_value():
    # Subtropical rain forest (Aché): hunted 50.5 / (plant 40.5 + hunted 50.5) ≈ 0.555
    assert abs(MEAT_FRAC[BIOME_FOREST] - 0.55) < 0.02


def test_meat_frac_ordering():
    # temperate grassland (steppe, migratory game) most meat; tropical grassland (savanna) least
    assert (MEAT_FRAC[BIOME_GRASS] > MEAT_FRAC[BIOME_FOREST]
            > MEAT_FRAC[BIOME_DESERT] > MEAT_FRAC[BIOME_SAVANNA])


# ── conservation + κ=0 inertness (composition level) ──────────────────────────
def test_two_stream_conserves():
    occ = [_MockA(phi=p) for p in (0.2, 0.5, 0.9)]
    shares, _, _ = _two_stream(occ, 30.0, mf=0.55, kappa=1.0)
    assert abs(sum(shares) - 30.0) < 1e-9


def test_two_stream_kappa0_equals_single_stream():
    occ = [_MockA(phi=0.1 * i) for i in range(6)]
    S = 17.0
    two, _, _ = _two_stream(occ, S, mf=0.55, kappa=0.0)
    one = compute_harvest_shares(occ, S, 0.0, 1e-6)
    assert all(abs(a - b) < 1e-9 for a, b in zip(two, one))   # energy-conserving, inert at κ=0


# ── RT-B: forage equal at κ>0, meat Cred-weighted (no double-apply) ────────────
def test_forage_equal_meat_weighted_at_kappa_pos():
    occ = [_MockA(phi=0.2), _MockA(phi=0.9)]
    _, f, m = _two_stream(occ, 20.0, mf=0.5, kappa=1.0)
    assert abs(f[0] - f[1]) < 1e-9      # forage half is κ=0 → equal regardless of φ
    assert m[1] > m[0]                  # meat half is Cred-weighted toward higher φ
    assert (f[1] + m[1]) > (f[0] + m[0])   # higher-φ Carbon agent gets the larger total


def test_silicon_meat_not_weighted():
    occ = [_MockA(phi=0.9, strategy="silicon"), _MockA(phi=0.2, strategy="silicon")]
    _, f, m = _two_stream(occ, 20.0, mf=0.5, kappa=1.0)
    assert abs(m[0] - m[1]) < 1e-9      # Silicon: equal meat regardless of φ (weight 1.0)


# ── model-level: game-on at κ=0 ≡ game-off (wiring + back-compat) ──────────────
def _world(enable_game: bool, seed: int = 42) -> TerrainWorld:
    return TerrainWorld(
        n_agents=120, kcal_cfg=KcalEconomyConfig(), seed=seed, game_stream=False,
        substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                      contest_exponent=0.0, move_cost_flat=0.0),
        demography_cfg=DemographyConfig(enable_game=enable_game, game_meat_frac=0.55),
    )


def test_model_game_on_kappa0_matches_game_off():
    w_off, w_on = _world(False), _world(True)
    for _ in range(12):
        w_off.step(); w_on.step()
    assert len(w_off.agent_list) == len(w_on.agent_list)
    woff = sorted(a.wealth for a in w_off.agent_list)
    won = sorted(a.wealth for a in w_on.agent_list)
    assert all(abs(a - b) < 1e-6 for a, b in zip(woff, won))
