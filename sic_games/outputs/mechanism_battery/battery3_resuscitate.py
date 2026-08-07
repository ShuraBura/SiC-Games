"""BATTERY 3 — RESUSCITATION: for each mechanism Battery 1 floated as INERT, change the one thing that should
let it fire, and re-test.

An INERT verdict is a question, not a conclusion. Battery 1 says "this mechanism does nothing in the regime the
project actually runs". That has five possible causes, and they call for different responses:

  1 CORRECT-BY-DESIGN   an Observer (charter type O) MUST be inert — zero mutation is its invariant.
  2 ZERO-DEFAULT GAIN   the flag is on, the knob is 0 (R-85c's class).
  3 UNMET PREREQUISITE  its chain is off, so it has nothing to act on.
  4 UNIT NEVER REACHED  the mechanism needs a unit the regime never grows (Bandy budding needs a village at
                        the fission threshold; the rank gate needs a band whose ascribed head-share clears
                        `rank_hierarchy_frac`). This is R-82's trap: an operator on a unit of size 1-2 is inert
                        by construction, and no amount of parameter tuning fixes it.
  5 GENUINELY UNWIRED   it survives all of the above and still does nothing. THAT is a defect.

Each recipe below changes exactly one of 2/3/4 and re-runs the liveness test against a baseline rebuilt under
the SAME recipe, so the comparison isolates the flag and not the recipe.

Verdicts:  REVIVED (fires under the recipe) · STILL-INERT (survives it — candidate defect) · BY-DESIGN.

Run:  py -3 -u sic_games/outputs/mechanism_battery/battery3_resuscitate.py
"""
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import battery1_liveness as B1

OUT = os.path.join(HERE, "battery3_results.json")
WORKERS = int(os.environ.get("B3_WORKERS", "6"))

BIG = dict(n=1200, patch=30, terr="coastal", clim="temperate")     # grows villages past the fission threshold
INLAND = dict(n=900, patch=24, terr="flat", clim="temperate")      # cultivability-dominant: soil can deplete
POOR = dict(n=1200, patch=18, terr="flat", clim="boreal")          # low NPP + crowding => real undernourishment
STEPS = int(os.environ.get("B3_STEPS", "400"))

# flag -> (cause being tested, extra config, world overrides)
RECIPES = {
    # 1 — correct by design; no run needed
    "enable_genealogy_log": ("BY-DESIGN: charter type O (Observer) - zero mutation IS its invariant", None, None),

    # 2 — zero-default gain
    "enable_provisioning": ("provision_self_keep=1.0 -> the mother keeps everything, so nothing is provisioned",
                            dict(provision_self_keep=0.6), None),

    # 3 — unmet prerequisite (v2: gates read from the CODE, not guessed — see notes)
    "enable_alluvial_renewal": ("prereq enable_soil_depletion was OFF",
                                dict(enable_soil_depletion=True, enable_agriculture=True), INLAND),
    # phase1_model:654 reads `cultivability` — on a COASTAL world that is ~0 and aquatic is claimable anyway,
    # so defensibility alone was not enough. v1 changed the flag but kept the wrong world.
    "enable_improved_land": ("needs economic_defensibility AND a world with cultivable land to claim",
                             dict(enable_economic_defensibility=True, enable_agriculture=True), INLAND),
    # phase1_model:4011 — synergy multiplies mortality by a term that is 1.0 when agents are WELL FED. It needs
    # genuine undernourishment, which energetic-fertility does not create.
    "enable_nutrition_synergy": ("needs actual undernourishment: poor biome + crowding", None, POOR),

    # 4 — unit never reached in the baseline regime
    "enable_soil_depletion": ("coastal sites are AQUATIC-dominant and exempt from soil (R-53) - retest inland",
                              dict(enable_agriculture=True), INLAND),
    # Bandy's threshold is ~170 in an open landscape; the test regimes never grow a village that large. Lowering
    # it tests WIRING, not calibration - the lit value stays untouched in the model.
    "enable_village_budding": ("village_fission_threshold ~170 never reached; lower it to test the wiring",
                               dict(village_fission_threshold=60.0), BIG),
    "enable_rank_hierarchy": ("needs a band whose ascribed head-share clears rank_hierarchy_frac=0.15",
                              dict(legit_threshold=0.08), BIG),
    "enable_emergent_abandonment": ("needs settlements under HARDSHIP to abandon", None, POOR),
    # phase1_model:4012 - `_condition` is only READ inside the nutrition-synergy branch, so condition without
    # synergy has no consumer. That is the prerequisite, not life-history.
    "enable_condition": ("its only consumer is the nutrition-synergy branch (phase1_model:4012)",
                         dict(enable_nutrition_synergy=True), POOR),
    # phase1_model:2171 - `if bonded and not pair_bonds`. Pair-bonds SUPERSEDES bonded mating, and the live
    # stack runs pair_bonds, so inert-when-on is CORRECT. Revival requires standing pair_bonds down.
    "enable_bonded_mating": ("SUPERSEDED by enable_pair_bonds (phase1_model:2171 `if bonded and not pair_bonds`)",
                             dict(enable_pair_bonds=False), BIG),
    # demography.py:232 - "[UNIMPLEMENTED STUB - no logic reads this]". Inert is the CORRECT verdict; the
    # battery rediscovered a documented stub independently, which is a check on the battery.
    # "enable_infanticide" was here as "BY-DESIGN: documented UNIMPLEMENTED STUB". The flag is DELETED
    # (2026-08-06) -- the battery no longer has to rediscover a stub that no longer exists.
}


def revive(item):
    flag, (why, extra, world) = item
    if extra is None and world is None:
        return dict(flag=flag, verdict="BY-DESIGN", why=why)
    world = dict(world or {})
    extra = dict(extra or {})
    steps = STEPS
    try:
        # baseline REBUILT under the same recipe, so the comparison isolates the flag, not the recipe
        base_sig, probes, base_s = B1.signature(extra, steps=steps, **world)
        cfg = B1.baseline_cfg()
        cur = getattr(cfg, flag)
        upd = dict(extra)
        upd[flag] = (not cur)
        if not cur:
            MAG, _ = B1._magnitudes()
            upd.update(MAG.get(flag, {}))
            upd.update(extra)                     # recipe wins over generic magnitude
        flip_sig, _, secs = B1.signature(upd, steps=steps, **world)
    except Exception as e:
        return dict(flag=flag, verdict="CRASH", why=why, note=f"{type(e).__name__}: {e}")
    changed = sorted(k for k in base_sig if base_sig[k] != flip_sig[k])
    # The recipe changes the WORLD, so the precondition must be re-checked IN THAT WORLD. Measured case:
    # `enable_emergent_abandonment` was retested in a poor boreal world that formed ZERO settlements, so
    # "still inert" would have been a statement about the recipe's world, not the mechanism. Same distinction
    # Battery 1 makes; it has to survive into Battery 3 or the recipes quietly reintroduce the original error.
    unmet = None
    need = B1.NEEDS.get(flag)
    if need and not changed:
        key, why_unmet = B1.PRECOND[need]
        if not probes.get(key):
            unmet = why_unmet
    verdict = "REVIVED" if changed else ("UNTESTABLE" if unmet else "STILL-INERT")
    return dict(flag=flag, verdict=verdict, unmet_precondition=unmet, why=why,
                changed=changed, n_changed=len(changed), probes=probes,
                recipe=dict(extra=extra, world=world), secs=secs)


def main():
    items = list(RECIPES.items())
    print(f"BATTERY 3 — resuscitation of {len(items)} inert mechanisms | {STEPS} steps | {WORKERS} workers",
          flush=True)
    rows = []

    def flush():
        json.dump(dict(rows=rows), open(OUT, "w", encoding="utf-8"), indent=1)

    t0 = time.time()
    with ProcessPoolExecutor(max_workers=WORKERS) as ex:
        for i, r in enumerate(ex.map(revive, items), 1):
            rows.append(r); flush()
            print(f"{i:3d}/{len(items)} {r['flag']:34s} {r['verdict']:12s} "
                  f"{('%d fields' % r['n_changed']) if r.get('n_changed') else ''}  <- {r['why'][:70]}",
                  flush=True)
    flush()
    print("\n" + "=" * 78)
    for v in ("REVIVED", "STILL-INERT", "UNTESTABLE", "BY-DESIGN", "CRASH"):
        got = [r["flag"] for r in rows if r["verdict"] == v]
        print(f"{v:12s} {len(got):2d}  " + ", ".join(got))
    print(f"\n{time.time()-t0:.0f}s -> {OUT}")


if __name__ == "__main__":
    main()
