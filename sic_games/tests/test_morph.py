"""S.4 society morph (per-cell), on the CORRECTED band substrate (CC-1 capacity + emergent-bands grouping +
bonded mating; storage-tethering RETIRED 2026-06-29). Locks the scenario behaviours: (1) a cold, seasonal,
storable region MORPHS egalitarian→complex from EMERGENT band concentration (no tether); (2) emergent bands reach
Binford packing via the grouping drives (the mechanism that replaced the tether); (3) a warm world (storage
ET-gated off) NEVER morphs (immediate-return geography); (4) a sustained famine COLLAPSES morphed cells back to
egalitarian; (5) flag off ⇒ no morph state (back-compat)."""
from __future__ import annotations

from collections import Counter

from sic_games.capacity import NPPCapacityField
from sic_games.config import KcalEconomyConfig, SubstrateConfig, CarbonConfig
from sic_games.demography import DemographyConfig, ACHE_FOREST_NATURAL as NAT, BINFORD_PACKING_PER_KM2
from sic_games.phase1_model import TerrainWorld, _CELL_KM2
from sic_games.terrain import generate_world

_KC = KcalEconomyConfig()
_BURN = _KC.burn_kcal_per_day * _KC.days_per_month
_PATCH = (30, 30, 40)                                   # bounded-K sub-window ⇒ the population equilibrates
_PACK_OCC = BINFORD_PACKING_PER_KM2 * _CELL_KM2         # occupants/cell == Binford packing (≈9.1)
_GRP = dict(group_safety_max=8.0, group_safety_scale=15.0, group_mate_min=15.0, group_mate_floor=0.2)


class _Famine:                       # a sustained downturn: scale the whole field down
    def __init__(self, base, f): self._base = base; self._f = f
    def level(self, x, y): return self._base.level(x, y) * self._f
    def __getattr__(self, n): return getattr(self._base, n)


def _knobs(seed):
    return {"seedStr": f"world{seed}", "relief": 0.50, "rough": 0.50,
            "waterK": 0.30, "forestK": 0.55, "aridK": 0.40}


def _band_seed(fields, cap, n, band_size=25, sep=4):
    x0, y0, sz = _PATCH
    cells = sorted(((cap.level(x, y), x, y) for y in range(y0, y0 + sz) for x in range(x0, x0 + sz)
                    if fields.isWater[y, x] == 0 and cap.level(x, y) > 0), reverse=True)
    sites, pos = [], []
    for (_, x, y) in cells:
        if len(sites) >= max(1, n // band_size):
            break
        if all(max(abs(x - px), abs(y - py)) >= sep for (px, py) in sites):
            sites.append((x, y)); pos.extend([(x, y)] * band_size)
    i = 0
    while len(pos) < n and sites:
        pos.append(sites[i % len(sites)]); i += 1
    return pos[:n]


def _world(temp_threshold, morph=True, seed=7, n=150, affiliation=False, dynamic=False):
    knobs = _knobs(seed)
    fields = generate_world(knobs)
    cap = NPPCapacityField(fields, _BURN, patch=_PATCH)
    pos = _band_seed(fields, cap, n)
    extra = dict(enable_pair_bonds=True, enable_band_affiliation=True, band_cohesion=0.3,
                 band_split_size=45, band_merge_size=10) if affiliation else {}
    if dynamic:
        extra.update(enable_dynamic_bands=True, band_base_tolerable=25, assabiyah_gain=0.05, assabiyah_decay=0.02)
    demog = DemographyConfig(
        siler_a1=NAT.a1, siler_b1=NAT.b1, siler_a2=NAT.a2, siler_a3=NAT.a3, siler_b3=NAT.b3,
        enable_density_disease=True, dens_delta=3.0, dens_rho_half=0.2,
        enable_cred_status=True, cred_seed_sigma=0.6, cred_inherit_sigma=0.3,
        enable_bonded_mating=True, bonded_mate_radius=1,
        enable_storage=True, storable_fraction=0.5, store_capacity_reserves=3.0,
        storage_temp_threshold_c=temp_threshold, storage_decay=0.05,   # S.3 spoilage → stores aren't immortal
        enable_morph=morph, morph_settle_steps=60, **extra)
    w = TerrainWorld(n_agents=n, kcal_cfg=_KC, terrain_knobs=knobs, game_stream=False, seed=seed,
                     carbon_cfg=CarbonConfig(kappa=1.5), harvest_field=cap, placement_positions=pos,
                     substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                                   contest_exponent=1.5, move_cost_flat=0.0, **_GRP),
                     demography_cfg=demog)
    return w


def test_morph_fires_from_emergent_bands_no_tether():
    # the retirement payoff: on the corrected substrate the egalitarian→complex morph fires from EMERGENT band
    # concentration (grouping drives + bonded mating) — NO storage tethering needed.
    w = _world(temp_threshold=100.0)                         # overwintering everywhere
    for _ in range(400):
        w.step()
    assert any(s == "complex_forager" for s in w._cell_society.values())


def test_emergent_bands_reach_packing():
    # the mechanism that replaced the tether: emergent bands concentrate to ≥ Binford packing on their own.
    w = _world(temp_threshold=100.0, morph=False)
    peak = 0
    for _ in range(300):
        w.step()
        occ = Counter(a.pos for a in w.agent_list)
        if occ:
            peak = max(peak, max(occ.values()))
    assert peak >= _PACK_OCC                                  # ≥ 9.1 occupants/cell reached without tethering


def test_morph_geography_warm_world_stays_egalitarian():
    # warm everywhere (storage ET-gated OFF) ⇒ no storage ⇒ no surplus ⇒ never morphs (immediate-return)
    w = _world(temp_threshold=-100.0)
    for _ in range(400):
        w.step()
    assert len(w._cell_store) == 0 and len(w._cell_society) == 0


def test_morph_collapses_under_sustained_famine():
    w = _world(temp_threshold=100.0)
    for _ in range(400):
        w.step()
    assert len(w._cell_society) > 0                           # morphed up first
    w._harvest_field = _Famine(w._harvest_field, 0.04)        # sustained, severe downturn (rich CC-1 substrate)
    for _ in range(500):
        w.step()
    assert len(w._cell_society) == 0                          # … then collapses back to egalitarian


def test_morph_off_no_society_state():
    w = _world(temp_threshold=100.0, morph=False)
    for _ in range(200):
        w.step()
    assert len(w._cell_society) == 0                          # flag off ⇒ no morph state (back-compat)


# ── F.3c-2 per-BAND society (the morph attaches to the band_id, not the cell) ──
def test_per_band_morph_fires_and_bypasses_cells():
    # F.3c-2: with band affiliation, society morphs on the BAND's aggregate character → _band_society populates
    # and the per-CELL detector is bypassed (_cell_society stays empty).
    w = _world(temp_threshold=100.0, affiliation=True)
    for _ in range(400):
        w.step()
    assert any(s == "complex_forager" for s in w._band_society.values())   # a band morphed egalitarian→complex
    assert len(w._cell_society) == 0                          # per-cell society NOT used under per-band


def test_per_band_morph_warm_world_stays_egalitarian():
    # warm everywhere (storage ET-gated off) ⇒ no surplus ⇒ no band morphs (Testart/Woodburn geography, per-band)
    w = _world(temp_threshold=-100.0, affiliation=True)
    for _ in range(400):
        w.step()
    assert len(w._band_society) == 0 and len(w._cell_society) == 0


# ── F.3c-3 dynamic fission/fusion + assabiyah ──
def test_assabiyah_builds_under_dynamic_bands():
    # F.3c-3: a band that accumulates surplus builds solidarity (assabiyah > 0), mirrored onto its members' vector.
    w = _world(temp_threshold=100.0, affiliation=True, dynamic=True)     # overwintering everywhere → surplus
    for _ in range(300):
        w.step()
    assert w._band_assabiyah and max(w._band_assabiyah.values()) > 0.5   # solidarity accrued from surplus
    assert max(a._group.assabiyah for a in w.agent_list) > 0.5           # mirrored onto the collective-identity vector


def test_warm_world_no_assabiyah():
    # no surplus (warm) ⇒ assabiyah decays to ~0 ⇒ bands fission at the base tolerable (no solidarity to grow on)
    w = _world(temp_threshold=-100.0, affiliation=True, dynamic=True)
    for _ in range(300):
        w.step()
    assert all(v < 0.1 for v in w._band_assabiyah.values()) if w._band_assabiyah else True


def test_dynamic_bands_off_by_default():
    assert DemographyConfig().enable_dynamic_bands is False
