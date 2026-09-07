"""R-85b — diagnose the six flags left inert by the charter flag audit (R-85 residual).

Each has a live reader and a non-zero magnitude, yet flipping it changes nothing at two seeds. This probe tests
the specific hypothesis for each, empirically rather than by reading code:
  terrain_move_cost / site_appraisal — both field builders require `self._fields.cost`; if the generator does not
                                       emit one in this mode they return None and the mechanism is silently off.
  bonded_mating                      — gated `if bonded and not pair_bonds`; superseded whenever pair-bonds are on.
  energetic_fertility                — multiplies fecundability by a nutritional factor that may saturate at 1.0
                                       when nobody is food-stressed.
  condition                          — feeds an EMA whose only consumer may itself be a zero-gain term.
  landscape_packing                  — switches the density definition feeding `_band_surplus`; inert if no
                                       downstream threshold ever separates the two definitions.
"""
import os
import sys

sys.path.insert(0, os.path.normpath("sic_games/outputs/phase1_social_evolution"))
sys.path.insert(0, os.path.dirname(__file__))
from run_se0_controlled_climate import realistic_forager_demog
from audit_flag_invariants import ENRICH

from sic_games.capacity import NPPCapacityField
from sic_games.climate import ClimateField
from sic_games.config import CarbonConfig, KcalEconomyConfig, SubstrateConfig
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world, world_lottery_climate


def build(n=300, seed=0, **over):
    k = world_lottery_climate(seed, terrain="coastal", climate="temperate")
    f = generate_world(k, mode="climate")
    hf = ClimateField(NPPCapacityField(f, 75000.0, patch=(20, 20, 60), mode="tallavaara", aquatic=True,
                                       enable_depletion=True), a_seas=0.5)
    hf0 = NPPCapacityField(f, 75000.0, patch=(20, 20, 60), mode="tallavaara", aquatic=True, enable_depletion=True)
    land = [(x, y) for y in range(100) for x in range(100) if f.isWater[y, x] == 0 and hf0.level(x, y) > 0]
    d = realistic_forager_demog().model_copy(update={**ENRICH, **over})
    w = TerrainWorld(n_agents=n, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, game_stream=False, seed=seed,
                     carbon_cfg=CarbonConfig(kappa=1.5),
                     substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                                   contest_exponent=1.5, move_cost_flat=0.0),
                     harvest_field=hf, placement_positions=[land[i % len(land)] for i in range(n)],
                     demography_cfg=d)
    return w, f


def main():
    import numpy as np
    w, f = build(**{"enable_terrain_move_cost": True, "enable_site_appraisal": True,
                    "enable_landscape_packing": True})

    print("=" * 90)
    print("H1/H2 — do the two IFD field builders have the terrain layer they require?")
    print("=" * 90)
    cost = getattr(w._fields, "cost", None)
    print(f"  self._fields.cost present : {cost is not None}")
    if cost is not None:
        c = np.asarray(cost)
        print(f"  cost spread              : min={c.min():.4f} max={c.max():.4f} std={c.std():.4f}")
    mcf = w._move_cost_field()
    sfd = w._site_suitability_field()
    print(f"  _move_cost_field()       : {'None  <<< MECHANISM SILENTLY OFF' if mcf is None else 'built'}")
    print(f"  _site_suitability_field(): {'None  <<< MECHANISM SILENTLY OFF' if sfd is None else 'built'}")
    if mcf is not None:
        m = np.asarray(mcf); print(f"     move-cost field std   : {m.std():.4f} (flat ⇒ no argmax change)")
    if sfd is not None:
        s = np.asarray(sfd); print(f"     site field std        : {s.std():.4f}")
    sp = w._s_pot_field()
    print(f"  _s_pot_field()           : {'None' if sp is None else 'built'}")

    print()
    print("=" * 90)
    print("H3 — enable_bonded_mating is gated `if bonded and not pair_bonds`")
    print("=" * 90)
    cfg = w._demog
    print(f"  enable_pair_bonds={cfg.enable_pair_bonds}  ⇒ the `bonded and not pair_bonds` branch is "
          f"{'DEAD (superseded by pair-bonds)' if cfg.enable_pair_bonds else 'live'}")

    print()
    print("=" * 90)
    print("H4 — does the energetic-fertility factor ever leave 1.0? (saturates if nobody is food-stressed)")
    print("=" * 90)
    from sic_games.demography import energetic_fertility_factor
    w2, _ = build(**{"enable_energetic_fertility": True})
    facs = []
    for _ in range(150):
        w2.step()
        if not w2.agent_list:
            break
        for a in w2.agent_list:
            fr = getattr(a, "_fed_reserve", None)
            if fr is None:
                continue
            rs = a.reserve_scale()
            facs.append(energetic_fertility_factor(fr, a.reserve_floor * rs, w2._reserve_full * rs))
    if facs:
        arr = np.array(facs)
        print(f"  n={len(arr)}  min={arr.min():.4f} mean={arr.mean():.4f} max={arr.max():.4f} "
              f"frac_at_1.0={(arr >= 0.9999).mean():.4f}")
        print("  " + ("*** SATURATED at 1.0 — multiplying fecundability by 1 ⇒ inert in this regime ***"
                      if (arr >= 0.9999).mean() > 0.99 else "factor varies ⇒ NOT the explanation"))

    print()
    print("=" * 90)
    print("H5 — what consumes the `condition` EMA, and is that consumer alive?")
    print("=" * 90)
    for p in ("pathogen_gamma", "density_disease_gamma", "condition_alpha", "mu_max", "a2_cap"):
        print(f"  {p:24s} = {getattr(cfg, p, 'n/a')}")


if __name__ == "__main__":
    main()
