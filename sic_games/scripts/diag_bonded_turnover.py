"""Diagnose the frozen-population bug under enable_bonded_mating on seeded bands.

Reproduces the handoff symptom (near-frozen pop, ~3-6 births/window vs ~15-30 IFD) and
instruments WHY: per-step births, mate-gate rejections, fertile-female count, and the
co-resident-male availability inside cells that hold a fertile female.
"""
from __future__ import annotations

import sys
from collections import Counter

from sic_games.config import KcalEconomyConfig, SubstrateConfig, CarbonConfig
from sic_games.demography import DemographyConfig, is_fertile
from sic_games.phase1_model import TerrainWorld, seed_band_positions, _DEFAULT_KNOBS
from sic_games.terrain import generate_world


def _carbon():
    try:
        return CarbonConfig()
    except Exception:
        return None


def build(bonded: bool, seed: int = 7, n: int = 250, full_carbon: bool = False):
    fields = generate_world({**_DEFAULT_KNOBS, "seedStr": f"world{seed}"})
    pos = seed_band_positions(fields, n, band_size=25, territory_radius=3)
    sc = SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                         contest_exponent=1.5 if full_carbon else 0.0,
                         move_cost_flat=0.0, group_safety_max=8.0, group_safety_scale=15.0,
                         group_mate_min=15.0, group_mate_floor=0.2)
    dkw = dict(enable_bonded_mating=bonded)
    if full_carbon:
        dkw.update(enable_cred_status=True, cred_seed_sigma=0.6, enable_prowess_facet=True,
                   prowess_decay=0.1, enable_paternity=True, mate_choice_strength=4.0,
                   sex_division=1.0, enable_game=True, game_meat_frac=0.4, game_meat_cv=2.24,
                   lineage_reversion=0.1)
    carbon = _carbon() if full_carbon else None
    w = TerrainWorld(n_agents=n, kcal_cfg=KcalEconomyConfig(), seed=seed, game_stream=False,
                     substrate_cfg=sc, carbon_cfg=carbon,
                     demography_cfg=DemographyConfig(**dkw), placement_positions=pos)
    return w


def gate_diagnostics(w):
    """Replicate the F.1 mate-gate check to count fertile females and how many are mate-gated."""
    cfg = w._demog
    males_by_cell = {}
    for x in w.agent_list:
        if x.sex == "male" and x.age >= cfg.menarche_months:
            males_by_cell.setdefault(x.pos, []).append(x)
    fertile = 0
    gated = 0
    have_any_male = 0
    for a in w.agent_list:
        if a.sex != "female":
            continue
        if not is_fertile(a.age, a.months_since_birth, cfg):
            continue
        fertile += 1
        cell_males = males_by_cell.get(a.pos, ())
        if cell_males:
            have_any_male += 1
        if not any(m._mother is not a for m in cell_males):
            gated += 1
    return fertile, gated, have_any_male


def run(label, bonded, full_carbon, steps=600):
    w = build(bonded, full_carbon=full_carbon)
    print(f"\n=== {label} (bonded={bonded}, full_carbon={full_carbon}) ===")
    print(f"{'step':>5} {'pop':>5} {'births':>7} {'deaths':>7} {'fert':>5} {'gated':>6} {'haveM':>6} {'ncells':>6} {'meanocc':>7}")
    win_b = 0
    win_d = 0
    for s in range(1, steps + 1):
        w.step()
        win_b += w.births_this_step
        win_d += w.deaths_starv_this_step + w.deaths_senesc_this_step
        if s % 100 == 0:
            fert, gated, haveM = gate_diagnostics(w)
            occ = Counter(a.pos for a in w.agent_list)
            ncells = len(occ)
            meanocc = (sum(occ.values()) / ncells) if ncells else 0.0
            print(f"{s:>5} {len(w.agent_list):>5} {win_b:>7} {win_d:>7} {fert:>5} {gated:>6} {haveM:>6} {ncells:>6} {meanocc:>7.2f}")
            win_b = 0
            win_d = 0
    return w


if __name__ == "__main__":
    fc = "--full" in sys.argv
    run("CONTROL no-bond", bonded=False, full_carbon=fc)
    run("BONDED", bonded=True, full_carbon=fc)
