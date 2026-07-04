"""Economic defensibility / owned-patch (Dyson-Hudson & Smith 1978) — the between-band driver of concentration.

Two layers are pinned here:
  (1) the movement multiplier in `diffusion_select_target` — an OWNED cell TETHERS its owner-band members
      (× tether, beating IFD's self-limiting per-capita) and EXCLUDES outsiders (× exclusion, routing them away);
      cell_owner=None ⇒ bit-exact.
  (2) `TerrainWorld._update_defensibility_claims` — a band that lead-occupies a DEFENSIBLE cell (aquatic_food ≥
      defensibility_min) with ≥ claim_min members for claim_dwell steps OWNS it; only defensible cells are
      claimable; ownership lapses (hysteresis) once abandoned.
"""
from types import SimpleNamespace

import numpy as np

from sic_games.substrate import diffusion_select_target
from sic_games.demography import DemographyConfig
from sic_games.phase1_model import TerrainWorld


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


# --------------------------------------------------------------------------- (1) movement multiplier

def test_defensibility_default_bit_exact():
    """cell_owner=None ⇒ identical target to the legacy call (the ownership hook is skipped)."""
    f, sc = _Field(), _SC()
    for px in range(3, 17):
        a1, a2 = _Agent((px, 8)), _Agent((px, 8))
        t0 = diffusion_select_target(a1, f, {(px, 8): 1}, None, sc, None, None)
        t1 = diffusion_select_target(a2, f, {(px, 8): 1}, None, sc, None, None,
                                     cell_owner=None, agent_band=5, owner_exclusion=0.2, owner_tether=6.0)
        assert t0 == t1


def test_tether_pulls_owner_member_onto_owned_cell():
    """An owner-band member prefers its band's owned (crowded) reach over an empty neighbour — the tether (×6)
    overrides IFD's self-limiting per-capita, so the band concentrates onto its cell."""
    f, sc = _Field(), _SC()
    a = _Agent((8, 8))
    occ = {(8, 8): 4, (9, 8): 4}          # east reach already holds 4; empty N/S/W would out-yield it under IFD
    owner = {(9, 8): 7}                    # band 7 owns the east reach; our agent IS band 7
    t = diffusion_select_target(a, f, dict(occ), None, sc, None, None,
                                cell_owner=owner, agent_band=7, owner_exclusion=0.2, owner_tether=6.0)
    assert t == (9, 8)                     # 100/5×6 = 120 > 100 (empties) > 25 (crowded current)


def test_exclusion_pushes_outsider_off_owned_cell():
    """An outsider avoids a cell owned by another band even when it is the emptiest (best per-capita) option."""
    f, sc = _Field(), _SC()
    a = _Agent((8, 8))
    occ = {(8, 8): 3, (9, 8): 0}          # east empty = best per-capita under IFD; current crowded
    owner = {(9, 8): 7}                    # but band 7 owns east; our agent is band 3
    t = diffusion_select_target(a, f, dict(occ), None, sc, None, None,
                                cell_owner=owner, agent_band=3, owner_exclusion=0.2, owner_tether=6.0)
    assert t != (9, 8)                     # 100×0.2 = 20 < 100 (the unowned empty N/S/W) → routed away


# --------------------------------------------------------------------------- (2) claim lifecycle

def _mk_self():
    cfg = DemographyConfig(enable_economic_defensibility=True, defensibility_min=0.15,
                           defensibility_claim_dwell=6, defensibility_claim_min=3,
                           defensibility_exclusion=0.2, defensibility_tether=6.0)
    aq = np.zeros((1, 6)); aq[0, 2] = 0.8            # only cell (2,0) is defensible
    return SimpleNamespace(_demog=cfg, _fields=SimpleNamespace(aquatic_food=aq),
                           _cell_owner={}, _cell_claim={}, agent_list=[])


def _occupy(fake, cell_band_counts):
    al = []
    for (x, y), bands in cell_band_counts.items():
        for b, n in bands.items():
            al.extend(SimpleNamespace(pos=(x, y), _group=SimpleNamespace(band_id=b)) for _ in range(n))
    fake.agent_list = al


def test_claim_forms_only_after_dwell():
    fake = _mk_self()
    for step in range(6):                            # dwell = 6
        _occupy(fake, {(2, 0): {9: 4}})              # band 9 lead-holds the defensible cell (4 ≥ claim_min 3)
        TerrainWorld._update_defensibility_claims(fake)
        if step < 5:
            assert (2, 0) not in fake._cell_owner    # not yet owned before dwell reached
    assert fake._cell_owner.get((2, 0)) == 9         # owned at dwell


def test_nondefensible_cell_never_claimable():
    fake = _mk_self()
    for _ in range(12):
        _occupy(fake, {(0, 0): {9: 20}})             # crowded but aquatic_food=0 < defensibility_min
        TerrainWorld._update_defensibility_claims(fake)
    assert (0, 0) not in fake._cell_owner


def test_claim_below_min_members_does_not_form():
    fake = _mk_self()
    for _ in range(12):
        _occupy(fake, {(2, 0): {9: 2}})              # only 2 members < claim_min 3
        TerrainWorld._update_defensibility_claims(fake)
    assert (2, 0) not in fake._cell_owner


def test_ownership_lapses_when_abandoned():
    fake = _mk_self()
    for _ in range(6):                               # form the claim
        _occupy(fake, {(2, 0): {9: 4}})
        TerrainWorld._update_defensibility_claims(fake)
    assert fake._cell_owner.get((2, 0)) == 9
    for _ in range(20):                              # owner leaves → claim decays → lapse (hysteresis)
        _occupy(fake, {(2, 0): {}})
        TerrainWorld._update_defensibility_claims(fake)
    assert (2, 0) not in fake._cell_owner
