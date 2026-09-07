"""R-88 — BAND CHURN vs the delegitimation lag. Does band fission/fusion reset `_band_resentment` faster than
`resent_alpha` can accumulate it, which would explain R-87d's finding that correlation time (~22 yr) came out
IDENTICAL across lag settings of 167 / 83 / 4 yr — i.e. the lag parameter measurably does not govern the
dynamics?

MECHANISM (confirmed by reading the code, not inferred): `_maintain_bands()` FISSION mints a new band_id via
`new_id = self._next_band_id; self._next_band_id += 1` and moves roughly half a band's members onto it —
`self._band_resentment.get(new_id, 0.0)` then returns 0.0, a SILENT RESET, regardless of what had accumulated
in the parent. FUSION moves every agent in the smaller band onto the surviving band_id and simply abandons the
smaller band's `_band_resentment` entry; the survivor's entry now tracks a population that just changed
composition. Neither event fires through `_do_delegitimation()`, so neither shows up in `reversions_this_step`
— these are resets nobody currently counts.

This closes the loop from R-84 (106 of 135 leader tenures ended by band COLLISION, not politics) — the same
substrate churn plausibly governs a second, independently-built mechanism.

METHOD: instrument `_maintain_bands()`-adjacent state directly. For every band_id that ever exists, record its
first-seen and last-seen step (a lifetime); separately record, at each sampled step, the AGE of every currently
live band_id (steps since its most recent fission/fusion event) as the direct proxy for "how long has this
band's resentment clock had to run since its last reset."
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.normpath("sic_games/outputs/phase1_social_evolution"))
from run_se0_controlled_climate import realistic_forager_demog

from sic_games.capacity import NPPCapacityField
from sic_games.climate import ClimateField
from sic_games.config import CarbonConfig, KcalEconomyConfig, SubstrateConfig
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world, world_lottery_climate

PROG = os.path.join(os.path.dirname(__file__), "progress_bandchurn.txt")


def run(alpha=0.001, steps=3600, n=500, seed=0, sample_every=4):
    k = world_lottery_climate(seed, terrain="coastal", climate="temperate")
    f = generate_world(k, mode="climate")
    hf = ClimateField(NPPCapacityField(f, 75000.0, patch=(20, 20, 60), mode="tallavaara", aquatic=True,
                                       enable_depletion=True), a_seas=0.5)
    hf0 = NPPCapacityField(f, 75000.0, patch=(20, 20, 60), mode="tallavaara", aquatic=True, enable_depletion=True)
    land = [(x, y) for y in range(100) for x in range(100) if f.isWater[y, x] == 0 and hf0.level(x, y) > 0]
    d = realistic_forager_demog().model_copy(update=dict(
        enable_material_capture=True, material_hide_frac=0.07, material_decay=0.002, aggrandizer_frac=0.15,
        enable_leader_share=True, leader_share_frac=0.20,
        enable_leveling=True, leveling_strength=0.79, leveling_share=0.8,
        enable_leader_office=True, office_grievance_gain=0.05,
        enable_legitimacy=True, legit_feast_frac=0.25, legit_cred_gain=10.0,
        legit_threshold=0.15, legit_decay=0.02,
        enable_delegitimation=True, resent_alpha=alpha, resent_threshold=0.5, resent_privilege_ref=10.0))
    w = TerrainWorld(n_agents=n, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, game_stream=False, seed=seed,
                     carbon_cfg=CarbonConfig(kappa=1.5),
                     substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                                   contest_exponent=1.5, move_cost_flat=0.0),
                     harvest_field=hf, placement_positions=[land[i % len(land)] for i in range(n)],
                     demography_cfg=d)

    # band_id -> [first_seen_step, last_seen_step]  (a "lifetime" record)
    lifetimes: dict[int, list[int]] = {}
    # band_id -> step it was last (re)created (fission target) or last received a fusion (i.e. its "birth" step
    # for AGE purposes) — approximated as first_seen for a fresh id, and we track fusion events separately.
    born_at: dict[int, int] = {}
    age_samples: list[float] = []          # age (steps) of each live band at each sampled step
    n_fissions = 0
    n_fusions = 0
    prev_ids: set[int] = set()

    for t in range(steps):
        before_next = w._next_band_id
        w.step()
        if not w.agent_list:
            break
        after_next = w._next_band_id
        n_fissions += (after_next - before_next)          # each fission mints exactly one new id

        cur_ids = {a._group.band_id for a in w.agent_list}
        new_ids = cur_ids - prev_ids
        vanished = prev_ids - cur_ids
        n_fusions += len(vanished)                         # an id that disappears was absorbed (fusion) or died out
        for bid in new_ids:
            born_at[bid] = t
            lifetimes[bid] = [t, t]
        for bid in cur_ids:
            if bid in lifetimes:
                lifetimes[bid][1] = t
            else:                                          # founder-era id, born at t=0
                born_at.setdefault(bid, 0)
                lifetimes[bid] = [0, t]
        prev_ids = cur_ids

        if t % sample_every == 0:
            for bid in cur_ids:
                age_samples.append(float(t - born_at.get(bid, 0)))
        if t % 400 == 0:
            with open(PROG, "w") as fh:
                fh.write(f"alpha={alpha} step {t}/{steps} pop={len(w.agent_list)} "
                        f"n_bands={len(cur_ids)} fissions={n_fissions} fusions={n_fusions}\n")
                fh.flush()

    life_steps = np.array([b - a for a, b in lifetimes.values()])
    return {
        "life_steps": life_steps, "age_samples": np.array(age_samples),
        "n_fissions": n_fissions, "n_fusions": n_fusions, "n_bands_total": len(lifetimes),
        "final_pop": len(w.agent_list),
    }


if __name__ == "__main__":
    print(__doc__.strip().split("\n")[0])
    print(f"\n{'lag memory':>11} {'n bands':>8} {'fissions':>9} {'fusions':>8} "
          f"{'life median':>12} {'life mean':>10} {'age median':>11} {'age mean':>9}")
    print("-" * 90)
    for alpha, lab in ((0.001, "83 yr"), (0.02, "4 yr (ctrl)")):
        r = run(alpha=alpha)
        life_yr = r["life_steps"] * 4 / 12.0 if len(r["life_steps"]) else np.array([0.0])
        # NOTE: life_steps records are only updated every model step, not every `sample_every` — steps count is
        # exact (not the 4-step sample); life is already in raw steps, convert directly:
        print(f"{lab:>11} {r['n_bands_total']:8d} {r['n_fissions']:9d} {r['n_fusions']:8d} "
              f"{np.median(r['life_steps']) / 12:10.1f}yr {np.mean(r['life_steps']) / 12:8.1f}yr "
              f"{np.median(r['age_samples']) * 4 / 12:9.1f}yr {np.mean(r['age_samples']) * 4 / 12:7.1f}yr")

    print("\nCOMPARISON: R-87d measured correlation time ~22 yr (uniform across lags 167/83/4 yr) and mean")
    print("ranked-spell length 2.7-4.6 yr. If band lifetime/age here is of the SAME ORDER, band churn is the")
    print("candidate governor — resent_alpha cannot express a memory longer than the band structure itself lasts.")
