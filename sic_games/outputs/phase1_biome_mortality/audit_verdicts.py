"""Charter retrofit, stage 2: turn the raw differential signatures into VERDICTS.

Reads `flag_audit.json` (written by `audit_flag_invariants.py`) and re-tests every NO-CHANGE flag at a second
seed and a longer horizon before calling anything a defect — a flag can be inert at one seed by luck.

METHODOLOGICAL LIMIT, learned from the first run and recorded here so it is not forgotten: a BLACK-BOX
differential audit CANNOT test the conservation invariants (X conserves its total, A moves no quantity). Over
200 coupled steps, changing the band graph changes who forages together, which changes wealth — so an A-typed
flag legitimately moves conserved quantities *in the trajectory* even though the operator itself conserves them
*within its own step*. Conservation must be instrumented AROUND THE CALL, not inferred from trajectories.
What this harness CAN establish, soundly: VACUITY, OBSERVER violations, and CRASHES.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from audit_flag_invariants import PREREQ, TYPES, ENRICH, signature  # noqa: E402
sys.path.insert(0, os.path.normpath("sic_games/outputs/phase1_social_evolution"))
from run_se0_controlled_climate import realistic_forager_demog  # noqa: E402

# Flags whose inertness in THIS regime is already explained in the docs — not defects.
EXPLAINED = {
    "enable_genealogy_log": "CORRECT — [O] observer; invariance is the requirement, not a defect",
    # enable_infanticide (KNOWN STUB) and enable_band_risk (SHELVED, death spiral) were both explained here
    # for a year. DELETED 2026-08-06 -- an explanation is not a substitute for removing a knob that cannot work.
    "enable_economic_defensibility": "REGIME-GATED — DE-10: the claim gate (>=3 same-band on a defensible cell) "
                                     "never fires on unsaturated land; 300 agents on 100x100 is that regime",
    "enable_improved_land": "DOWNSTREAM of economic_defensibility, which is itself regime-gated here (R-70 "
                            "needed a low-aquatic/high-cultivability world to show any effect)",
    "enable_aggregation_sedentism": "REGIME-GATED — the discrete settlement machinery is inactive in this world "
                                    "config (_settlement_sites stays 0; VERIFICATION_LOG open-check 2)",
    "enable_settlement_scalar_stress": "DOWNSTREAM of the inactive settlement machinery",
    "enable_village_budding": "DOWNSTREAM of the inactive settlement machinery",
    "enable_catchment_ceiling": "DOWNSTREAM of the inactive settlement machinery",
    "enable_agriculture": "REGIME-GATED — needs the agriculture stack + cultivable land; coastal/temperate at "
                          "this scale is not the flat-tropical rain-fed world R-70 required",
    "enable_soil_depletion": "PREREQ UNMET — needs enable_agriculture",
    "enable_alluvial_renewal": "PREREQ UNMET — needs enable_soil_depletion",
    "enable_emergent_abandonment": "DOWNSTREAM of soil/settlement, both inactive here (R-71 regime)",
}


def main():
    path = os.path.join(os.path.dirname(__file__), "flag_audit.json")
    rows = json.load(open(path))["rows"]
    cfg0 = realistic_forager_demog().model_copy(update=ENRICH)

    nochange = [r for r in rows if not r["changed"]]
    print(f"{len(rows)} flags audited · {len(nochange)} showed NO CHANGE at seed 0 / 120 steps")
    print("Re-testing those at seed 7 / 260 steps before calling anything a defect...\n")

    base2 = signature(seed=7, steps=260)
    still = []
    for r in nochange:
        fl = r["flag"]
        try:
            s = signature(seed=7, steps=260, flip=fl)
        except Exception as e:
            print(f"  {fl:36s} CRASH at seed 7: {type(e).__name__}: {e}")
            continue
        diff = sorted(k for k in base2 if base2[k] != s[k])
        if diff:
            print(f"  {fl:36s} -> ACTIVE at seed 7 ({','.join(diff[:3])}...) — not inert, seed-0 artifact")
        else:
            still.append(fl)

    print("\n" + "=" * 96)
    print("VERDICTS")
    print("=" * 96)
    unexplained = []
    for fl in still:
        ty = TYPES.get(fl, "?")
        unmet = [p for p in PREREQ.get(fl, ()) if not getattr(cfg0, p, False)]
        if fl in EXPLAINED:
            print(f"  [{ty}] {fl:36s} OK/known :: {EXPLAINED[fl]}")
        elif unmet:
            print(f"  [{ty}] {fl:36s} uninformative :: prereq unmet {unmet}")
        else:
            unexplained.append((ty, fl))

    print("\n" + "-" * 96)
    if unexplained:
        print(f"*** {len(unexplained)} UNEXPLAINED INERT FLAGS — prerequisites satisfied, inert at BOTH seeds ***")
        print("These are the charter §6 candidates: a flag whose ON/OFF output is indistinguishable is a")
        print("SPECIFICATION BUG, not a small effect size (DE-19) — unless a regime gate explains it.\n")
        for ty, fl in unexplained:
            print(f"  [{ty}] {fl}")
    else:
        print("No unexplained inert flags.")

    # observer / gauge checks (these the black-box audit CAN decide)
    print("\n" + "-" * 96)
    print("TYPE-SPECIFIC CHECKS THE BLACK-BOX AUDIT CAN SOUNDLY DECIDE")
    for r in rows:
        if r["type"] == "O":
            print(f"  [O] {r['flag']:34s} {'PASS — mutated nothing' if not r['changed'] else '*** O-VIOLATION ***'}")
        if r["type"] == "GAUGE":
            print(f"  [GAUGE] {r['flag']:30s} "
                  f"{'PASS — no observable moved' if not r['changed'] else '*** NOT A GAUGE — moved: ' + ','.join(r['changed']) + ' ***'}")


if __name__ == "__main__":
    main()
