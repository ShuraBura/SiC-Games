"""Why test_fertility_and_mobility_intake_modes_are_independently_ablatable went bit-identical after Add.109.
Counts, per step, the fertile women whose intake-fertility factor is < 1 (the gate binds), in the test's own
world, with paternal_provision_frac at the new canon 0.5 and at the old 0.0. Also repeats the test's comparison
for each value (the positive control: 0.0 must reproduce the pre-adoption PASS)."""
import os
import sys

ROOT = r"C:\Users\syatom\Projects\SiC Games"
sys.path.insert(0, os.path.join(ROOT, "sic_games", "src"))
sys.path.insert(0, os.path.join(ROOT, "sic_games", "outputs", "mechanism_battery"))
import battery1_liveness as B1   # noqa: E402

WORLD = dict(n=900, patch=18, terr="coastal", clim="temperate")
BASE = dict(enable_productivity_mobility=True, mobility_pressure_source="intake")

for pat in (0.0, 0.5):
    mo, _, _ = B1.signature(dict(BASE, enable_intake_fertility=False, paternal_provision_frac=pat), steps=300, **WORLD)
    bo, _, _ = B1.signature(dict(BASE, enable_intake_fertility=True, paternal_provision_frac=pat), steps=300, **WORLD)
    w = B1._build(dict(BASE, enable_intake_fertility=True, paternal_provision_frac=pat), **WORLD)
    c = w._demog
    sp = c.intake_fert_hi - c.intake_fert_lo
    bound = fert = 0
    for _ in range(300):
        w.step()
        for a in w.agent_list:
            if a.sex == "female" and c.menarche_months <= a.age and a.alive:
                fert += 1
                if (a._intake_ema - c.intake_fert_lo) / sp < 1.0:
                    bound += 1
    print(f"paternal {pat}: test comparison differs = {mo != bo}; gate binds on {bound}/{fert} "
          f"woman-steps = {bound / max(fert, 1):.4f}; final pop {len(w.agent_list)}", flush=True)
