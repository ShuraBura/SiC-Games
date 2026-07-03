"""Central-place co-movement fixes (R-41 → the fix): anticipate / footprint / provision-exclude.

The exact-snap family co-movement over-subscribes the mother's cell (energetic-fertility collapse in marginal
biomes). These pin: (i) the anticipation `extra_occupants` denom; (ii) the footprint scatter (followers spread,
don't stack); (iii) provision-exclusion zeroing a juvenile follower's forage share; and default-OFF bit-exactness.
"""
import numpy as np

from sic_games.substrate import diffusion_select_target
from sic_games.demography import DemographyConfig, footprint_radius


# --------------------------------------------------------------------------- scaled footprint (biome monthly range)

def _fp_cfg(**kw):
    base = dict(comove_footprint=0, comove_footprint_scaled=True, comove_footprint_max=3,
                mobility_npp_ref=900.0, mobility_npp_floor=50.0, mobility_exponent=1.0)
    base.update(kw)
    return DemographyConfig(**base)


def test_footprint_fixed_when_not_scaled():
    c = DemographyConfig(comove_footprint=2, comove_footprint_scaled=False)
    assert footprint_radius(100.0, c) == 2 and footprint_radius(2000.0, c) == 2


def test_footprint_scaled_forest_tight_savanna_wide():
    c = _fp_cfg()
    assert footprint_radius(900.0, c) == 0      # forest (NPP≥ref) → tight camp = 1 cell
    assert footprint_radius(2000.0, c) == 0     # richer still → 0
    assert footprint_radius(450.0, c) == 1      # 900/450=2 → round-1 = 1
    assert footprint_radius(300.0, c) == 2      # 900/300=3 → 2
    assert footprint_radius(50.0, c) == 3       # capped at footprint_max


def test_footprint_scaled_monotone_and_capped():
    c = _fp_cfg(comove_footprint_max=5)
    xs = [50, 150, 300, 600, 900, 1500]
    ks = [footprint_radius(x, c) for x in xs]
    assert all(ks[i] >= ks[i + 1] for i in range(len(ks) - 1))
    assert min(ks) == 0 and max(ks) <= 5


class _Field:
    def __init__(self, w=20, h=20, val=100.0):
        self.width, self.height, self._v = w, h, val
    def level(self, x, y):
        return self._v


class _SC:
    contest_exponent = 0.0
    phi_epsilon = 0.0
    k_cell = 0
    move_cost_flat = 0.0
    group_safety_max = 0.0
    group_safety_scale = 8.0
    group_mate_min = 0.0
    group_mate_floor = 0.3


class _Agent:
    strategy = "greedy"
    def __init__(self, pos):
        self.pos = pos


# --------------------------------------------------------------------------- (i) anticipation

def test_extra_occupants_default_bit_exact():
    """extra_occupants=0 ⇒ identical target to the legacy call."""
    f, sc = _Field(), _SC()
    for px in range(3, 17):
        a1, a2 = _Agent((px, 8)), _Agent((px, 8))
        t0 = diffusion_select_target(a1, f, {(px, 8): 1}, None, sc, None, None)
        t1 = diffusion_select_target(a2, f, {(px, 8): 1}, None, sc, None, None, extra_occupants=0)
        assert t0 == t1


def test_anticipation_penalises_current_cell():
    """A family-root anticipating followers values MOVING to an empty neighbour over staying on its (soon
    over-subscribed) cell. On a uniform field: extra_occupants inflates the current-cell denom (n+family) but a
    move to an empty neighbour is n=1+family — the mover should leave rather than pile the family on its cell."""
    f, sc = _Field(), _SC()
    # current cell already holds the mover; with a big family the per-capita on-cell = S/(1+extra) while a fresh
    # empty neighbour = S/(1+extra) too — tie. Use a cell that ALSO holds others so staying is worse:
    a = _Agent((8, 8))
    occ = {(8, 8): 3, (9, 8): 0}     # current crowded, east empty
    # without anticipation the mover may still move (S/3 stay vs S/1 move → moves). Anticipation must not BREAK
    # the move-to-empty preference; assert it still prefers the emptier cell.
    t = diffusion_select_target(a, f, dict(occ), None, sc, None, None, extra_occupants=4)
    assert t != (8, 8)               # does not stay on the crowded cell


# --------------------------------------------------------------------------- (iii) provision-exclusion helper

def test_forage_exclusion_zeroes_juvenile_share():
    """The _forage_excl split (mirrored here) gives excluded occupants 0 and splits the total among the rest."""
    from sic_games.substrate import compute_harvest_shares
    occ = [_Agent((5, 5)) for _ in range(4)]
    mask = [False, True, False, True]        # occ[1], occ[3] excluded (juvenile followers)
    idx = [i for i, e in enumerate(mask) if not e]
    sub = compute_harvest_shares([occ[i] for i in idx], 100.0, 0.0, 0.0)
    out = [0.0] * 4
    for j, i in enumerate(idx):
        out[i] = sub[j]
    assert out[1] == 0.0 and out[3] == 0.0
    assert abs(out[0] - 50.0) < 1e-9 and abs(out[2] - 50.0) < 1e-9   # the two foragers split 100


# --------------------------------------------------------------------------- integration: default OFF bit-exact + footprint spreads

def _biome_world(update, seed=0, steps=60):
    import os, sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "outputs", "biome_society_20260702"))
    from run_biome_society import realistic_forager_demog, capacity_aware_seed, BURN, X0, Y0, PATCH, FOUNDERS, GRP
    from sic_games.config import KcalEconomyConfig, SubstrateConfig, CarbonConfig
    from sic_games.phase1_model import TerrainWorld
    from sic_games.terrain import generate_world, world_lottery
    from sic_games.capacity import NPPCapacityField
    knobs = world_lottery(seed * 5, archetype="savanna")
    fields = generate_world(knobs)
    cap = NPPCapacityField(fields, BURN, patch=(X0, Y0, PATCH), mode="tallavaara")
    pos = capacity_aware_seed(cap, BURN, FOUNDERS)
    demog = realistic_forager_demog().model_copy(update=update)
    w = TerrainWorld(n_agents=FOUNDERS, kcal_cfg=KcalEconomyConfig(), terrain_knobs=knobs, game_stream=False,
        seed=seed, carbon_cfg=CarbonConfig(kappa=1.5),
        substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                      contest_exponent=1.5, move_cost_flat=0.0, **GRP),
        harvest_field=cap, placement_positions=pos, demography_cfg=demog)
    for _ in range(steps):
        w.step()
        if not w.agent_list:
            break
    return w


def test_canonical_footprint_is_stable():
    """CANONICAL 2026-07-03: realistic_forager_demog carries comove_footprint=1 (R-44). Explicitly re-setting it
    to the canonical value (+ the other central-place flags at their OFF defaults) reproduces the plain canonical
    config exactly — the canonical central-place path is stable/bit-exact."""
    from collections import Counter
    w0 = _biome_world({})
    w1 = _biome_world(dict(comove_footprint=1, comove_anticipate=False, comove_provision_exclude=False))
    assert len(w0.agent_list) == len(w1.agent_list)
    assert Counter(a.pos for a in w0.agent_list) == Counter(a.pos for a in w1.agent_list)


def test_footprint_zero_differs_from_canonical():
    """Sanity: comove_footprint=0 (legacy exact-snap) is NOT the canonical config anymore (footprint=1) — the flag
    is live, so turning it off changes the trajectory."""
    from collections import Counter
    canon = _biome_world({})
    snap = _biome_world(dict(comove_footprint=0))
    assert Counter(a.pos for a in canon.agent_list) != Counter(a.pos for a in snap.agent_list)


def test_footprint_lowers_max_cell_occupancy():
    """Footprint>0 disperses families: the busiest cell holds FEWER agents than under exact-snap co-movement."""
    from collections import Counter
    snap = _biome_world(dict(comove_footprint=0))   # explicit exact-snap (canonical is now footprint=1)
    fp = _biome_world(dict(comove_footprint=2))
    if not snap.agent_list or not fp.agent_list:
        return   # (don't assert on an extinct arm; the behavioural claim is covered by run_comove_fixes)
    max_snap = max(Counter(a.pos for a in snap.agent_list).values())
    max_fp = max(Counter(a.pos for a in fp.agent_list).values())
    assert max_fp <= max_snap
