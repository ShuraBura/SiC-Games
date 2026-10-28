"""R-106 Add.119 diagnosis: is the infant hazard below the Siler schedule because the orphan multiplier is
normalised over ALL children aged 0-9, pooled across ages?

Probe world = the battery world WITH the canonical DemographyConfig values merged in (runconfig.load(); the
battery builder alone does not apply the run file). Per step, after the world has run 300 steps:
  E        = _orphan_e_mult_live(), the divisor (mean raw multiplier over children 0-9 with known parents)
  om_inf   = mean _orphan_mult over infants (age < 12 months) with known parents  -> the infant discount
  om_all   = mean _orphan_mult over all children 0-9 with known parents            -> must be 1.0 (control)
Writes progress to scratchpad/orphan_e_progress.txt.
"""
import os
import statistics as st
import sys

ROOT = r"C:\Users\syatom\Projects\SiC Games"
sys.path.insert(0, os.path.join(ROOT, "sic_games", "src"))
sys.path.insert(0, os.path.join(ROOT, "sic_games", "outputs", "mechanism_battery"))
sys.path.insert(0, os.path.join(ROOT, "sic_games", "outputs", "substrate_run"))
from sic_games import runconfig  # noqa: E402
import battery1_liveness as B1  # noqa: E402

STEPS, BURN = int(os.environ.get("OE_STEPS", "700")), int(os.environ.get("OE_BURN", "300"))
PROG = os.path.join(ROOT, "scratchpad", "orphan_e_progress.txt")
upd = dict(runconfig.load()["DemographyConfig"])
upd.update(enable_condition_full_scale=True)
w = B1._build(upd, n=900, patch=18, terr="coastal", clim="temperate", biome_seasonality=True)
print("orphan mortality on:", w._demog.enable_orphan_mortality, " normalize:", w._demog.orphan_normalize,
      " siler a2:", w._demog.siler_a2, flush=True)
E, INF, ALL, NINF = [], [], [], []
for t in range(STEPS):
    w.step()
    if t % 50 == 0:
        with open(PROG, "w", encoding="utf-8") as fh:
            fh.write(f"step {t}/{STEPS} pop {len(w.agent_list)}\n")
    if t < BURN or not w.agent_list:
        continue
    kids = [a for a in w.agent_list if a.age <= w._demog.orphan_max_age_years * 12
            and (getattr(a, "_mother", None) is not None or getattr(a, "_father", None) is not None)]
    inf = [a for a in kids if a.age < 12]
    if not kids or not inf:
        continue
    E.append(w._orphan_e_mult_live())
    INF.append(st.mean(w._orphan_mult(a) for a in inf))
    ALL.append(st.mean(w._orphan_mult(a) for a in kids))
    NINF.append(len(inf))
print(f"steps {BURN}-{STEPS}, pop at end {len(w.agent_list)}, infants/step {st.mean(NINF):.0f}")
print(f"E (divisor)                    {st.mean(E):.3f}  [{min(E):.3f}, {max(E):.3f}]")
print(f"mean mult, infants             {st.mean(INF):.3f}   -> infant hazard x this vs the schedule")
print(f"mean mult, all children 0-9    {st.mean(ALL):.3f}   (control: must be 1.000)")
