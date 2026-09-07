"""CTB — FOUNDING ON STORABLE SURPLUS, AND YIELD ON WORKED LAND (R-106, 2026-08-15).

ONE DEFECT, TWO SYMPTOMS. `_s_pot_field()` = max(aquatic_food, cultivability) on RAW TERRAIN was answering
three different questions, and conflating a wild cereal stand with a ploughed field in two of them:

    is this worth settling?    -> raw S_pot                    CONFLATED
    what does settling yield?  -> raw S_pot over the catchment CONFLATED
    can you own it?            -> aquatic anywhere;
                                  cultivable ONLY where worked CORRECT

`_update_defensibility_claims` already had the third right — "You own what you've cleared (Testart), not any
fertile wilderness cell" — so the FOUNDING rule permitted founding on land the OWNERSHIP rule says cannot be
claimed until a settlement is already there. Two layers of the same model contradicting each other.

WHY NOT AQUATIC-ONLY FOUNDING, WHICH WAS THE FIRST PROPOSAL AND IS WRONG. The 2026-08-15 site-suitability
survey contradicted it with two published cases:
  MESOAMERICA runs the ordering backwards. Ranere & Piperno PNAS 2009, verbatim: "small groups moved around
    the countryside seasonally ... by farming along river and lake shores". Maize and squash were
    domesticated 8,990-8,610 cal BP by MOBILE people; sedentary villages appear ~3,000 BP. A ~5,700-year lag
    the WRONG way, in one of the three primary domestication centres.
  THE LEVANT, the best case FOR sedentism-first, did not found on a fishery. Natufian base camps sat in
    oak-pistachio woodland on wild cereals, nuts and gazelle (Bar-Yosef, filed), and "storage installations
    are rare in Natufian sites".

SO THE CRITERION IS STORABLE SURPLUS. Hayden 1995 (filed): villages form where someone can control
"spatially restricted resource locations or productive facilities — fishing rocks, weirs, boats, deer fences,
drying sheds". A wild-cereal stand qualifies; a salmon choke point qualifies; open water does not. That
covers BOTH cases, and needs no unlock times and no technology tree.

NO NEW NUMBER IS INTRODUCED. The founding test is S_pot x `_storable_frac_field()`, and that field already
existed, already ran, and already used Testart's STORABILITY_BY_RESOURCE (grain 0.85 / fish 0.80 / forage
0.15 / game 0.35). `test_no_new_constant_is_introduced` pins that.
"""
import pytest

from sic_games.config import KcalEconomyConfig, SubstrateConfig
from sic_games.demography import STORABILITY_BY_RESOURCE, DemographyConfig
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world, world_lottery_climate


def _world(**upd):
    k = world_lottery_climate(0, terrain="coastal", climate="temperate")
    generate_world(k, mode="climate")
    d = DemographyConfig(enable_band_affiliation=True, enable_agriculture=True,
                         enable_resource_storability=True, enable_storage=True, **upd)
    return TerrainWorld(n_agents=120, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, seed=0,
                        substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion"),
                        demography_cfg=d)


# ── default state ─────────────────────────────────────────────────────────────────────────────────────────

def test_both_flags_default_off():
    d = DemographyConfig()
    assert d.enable_storable_founding is False
    assert d.enable_worked_land_yield is False


def test_off_the_founding_field_IS_the_raw_s_pot():
    """Bit-exactness, at the identity level rather than by assertion."""
    w = _world(enable_storable_founding=False)
    a, b = w._founding_pot_field(), w._s_pot_field()
    assert a is b or (a == b).all()


def test_no_new_constant_is_introduced():
    """The whole design argument is that this reuses filed machinery. If a new storability number ever
    appears, the Testart citation stops covering the mechanism."""
    assert STORABILITY_BY_RESOURCE == {"grain": 0.85, "fish": 0.80, "forage": 0.15, "game": 0.35}


# ── the founding criterion ────────────────────────────────────────────────────────────────────────────────

def test_storability_weighting_lowers_the_founding_potential():
    """The storable fraction is <= 1 everywhere, so the weighted field can only ever be MORE selective. A
    version that raised the potential anywhere would loosen the site test, which is the opposite of intent."""
    w = _world(enable_storable_founding=True)
    raw, wtd = w._s_pot_field(), w._founding_pot_field()
    assert (wtd <= raw + 1e-9).all(), "the storable weighting must never increase site potential"


def test_a_fresh_forage_cell_is_penalised_more_than_a_grain_or_fish_cell():
    """THE DISCRIMINATION THE WHOLE DESIGN RESTS ON. Testart's storabilities put grain at 0.85 and fish at
    0.80 against forage at 0.15, so a cell whose calories are mostly fresh forage must lose far more of its
    founding potential than one whose calories are grain or fish. Constructed directly on the field."""
    import numpy as np
    w = _world(enable_storable_founding=True)
    f = w._fields
    shp = np.asarray(f.cultivability).shape
    for nm, arr in (("cultivability", np.zeros(shp)), ("aquatic_food", np.zeros(shp)),
                    ("forage", np.zeros(shp)), ("game", np.zeros(shp))):
        setattr(f, nm, arr)
    f.cultivability[0, 0] = 1.0        # pure grain
    f.aquatic_food[0, 1] = 1.0         # pure fish
    f.forage[0, 2] = 1.0               # pure fresh forage
    f.cultivability[0, 2] = 1.0        # ...with the same raw potential as the grain cell
    w._spot_cache = None; w._storable_frac_cache = None; w._founding_pot_cache = None
    pot = w._founding_pot_field()
    grain, fish, diluted = pot[0, 0], pot[0, 1], pot[0, 2]
    assert grain > diluted, f"a grain cell ({grain:.3f}) must beat one diluted by fresh forage ({diluted:.3f})"
    assert fish > diluted, f"a fish cell ({fish:.3f}) must beat one diluted by fresh forage ({diluted:.3f})"
    assert grain == pytest.approx(STORABILITY_BY_RESOURCE["grain"], rel=1e-6)
    assert fish == pytest.approx(STORABILITY_BY_RESOURCE["fish"], rel=1e-6)


def test_only_the_FOUNDING_calls_changed():
    """Production and movement must still read raw S_pot. If agglomeration or the harvest loop started
    reading the storability-weighted field, this would silently change the ECONOMY as well as the site test,
    and the two effects could never be separated in a run."""
    import re
    from pathlib import Path
    src = Path(__file__).resolve().parents[1] / "src" / "sic_games" / "phase1_model.py"
    body = src.read_text(encoding="utf-8")
    fn = None
    users = {}
    for line in body.splitlines():
        m = re.match(r"    def (\w+)", line)
        if m:
            fn = m.group(1)
        if "_founding_pot_field()" in line and fn and fn != "_founding_pot_field":
            users.setdefault(fn, 0)
            users[fn] += 1
    assert set(users) == {"_found_settlements_by_occupancy", "_do_gathering", "_maintain_village_budding"}, \
        f"the storability weighting reached a non-founding caller: {sorted(users)}"


# ── worked-land yield ─────────────────────────────────────────────────────────────────────────────────────

def test_worked_land_yield_is_zero_before_anything_is_owned():
    """THE LAG, at its starkest. With no owned cells the tier-2 unlock is nothing, so founding buys only the
    tier-1 return — which is why the Natufians settled on a wild stand, and is exactly the immediacy the
    default behaviour lacked."""
    w = _world(enable_worked_land_yield=True)
    w.step()
    w._cell_owner.clear()
    assert w._settlement_catchment_yield((50, 50)) == pytest.approx(0.0)


def test_the_yield_ramps_as_claims_are_granted():
    """It must RISE with owned area, so the ramp is emergent from the clearing process rather than a
    delay parameter."""
    w = _world(enable_worked_land_yield=True)
    w.step()
    site = (50, 50)
    rad = w._demog.settle_catchment_radius
    seen = []
    w._cell_owner.clear()
    for k in (0, 3, 8, (2 * rad + 1) ** 2):
        cells = [((site[0] + dx) % 100, (site[1] + dy) % 100)
                 for dy in range(-rad, rad + 1) for dx in range(-rad, rad + 1)]
        w._cell_owner = {c: 1 for c in cells[:k]}
        seen.append(w._settlement_catchment_yield(site))
    assert all(a <= b for a, b in zip(seen, seen[1:])), f"yield must not fall as land is claimed: {seen}"
    assert seen[-1] > seen[0], "fully-owned catchment must out-yield an unowned one"


def test_fully_owned_matches_the_legacy_yield_exactly():
    """The upper end of the ramp must reproduce the old behaviour, or the mechanism is not a LAG but a
    permanent tax on settlement yield — a different change with different consequences."""
    site = (50, 50)
    off = _world(enable_worked_land_yield=False)
    on = _world(enable_worked_land_yield=True)
    for w in (off, on):
        w.step()
    rad = on._demog.settle_catchment_radius
    on._cell_owner = {((site[0] + dx) % 100, (site[1] + dy) % 100): 1
                      for dy in range(-rad, rad + 1) for dx in range(-rad, rad + 1)}
    assert on._settlement_catchment_yield(site) == pytest.approx(off._settlement_catchment_yield(site))


def test_tier1_is_untouched_so_a_wild_stand_still_pays_at_once():
    """The mechanism must delay CULTIVATED returns only. If it also suppressed the tier-1 cell return there
    would be no reason to settle at all, and the Natufian case would become unreproducible."""
    off, on = _world(enable_worked_land_yield=False), _world(enable_worked_land_yield=True)
    for w in (off, on):
        w.step()
    assert (off._s_pot_field() == on._s_pot_field()).all()
    assert off._harvest_field.level(50, 50) == pytest.approx(on._harvest_field.level(50, 50))
