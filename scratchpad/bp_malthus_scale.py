"""R-106 Add.105 part 5 — SCALE CHECK: are the settlement economy's terms numerically alive?

part 3 measured tier-2 = 37.3 kcal deposited at a site whose own tier-1 cell yield is 2.27e6. That is 1/61000
of the cell. Both the tier-2 unlock AND the agglomeration bonus are built on S_pot (= aquatic_food, or
max(aquatic_food, cultivability) under agriculture):

    tier-2   settle_tier2_yield * SUM_catchment S_pot            settle_tier2_yield = 40
    aggl     A_cell * (n**beta - n),  A_cell = aggl_tier2 * S_pot * cv_ref     aggl_tier2 = 5

and both are ADDED to the harvest field's cell level. If S_pot and harvest level are in different units, both
terms are dead by construction and the settlement economy does nothing — the recurring hidden-denominator /
unit-mismatch class (MARKER_MATRIX binding rules).

This is a pure measurement. It builds the canonical probe world and prints the distributions side by side.
No dynamics, no seeds needed beyond a couple for the world lottery.
"""
import os
import sys
import statistics as st

ROOT = r"C:\Users\syatom\Projects\SiC Games"
sys.path.insert(0, os.path.join(ROOT, "scratchpad"))
from bp_savanna_probe import build, runconfig

N = 100


def q(v, p):
    v = sorted(v)
    if not v:
        return float("nan")
    i = min(len(v) - 1, max(0, int(p * (len(v) - 1))))
    return v[i]


def main():
    clim = os.environ.get("C_BIOME", "temperate")
    canon = dict(runconfig.load()["DemographyConfig"])
    w = build(canon, 0, 0, clim=clim)
    w.step()                                     # one step so caches/fields are initialised
    d = w._demog
    tf = w._harvest_field
    sp = w._s_pot_field()
    land = [(x, y) for y in range(N) for x in range(N) if w._fields.isWater[y, x] == 0]

    lev = [tf.level(x, y) for x, y in land]
    lev_pos = [v for v in lev if v > 0]
    spv = [float(sp[y, x]) for x, y in land] if sp is not None else []
    sp_pos = [v for v in spv if v > 0]

    print(f"SCALE CHECK | {clim} | {len(land)} land cells\n")
    print(f"{'quantity':38s}{'min':>14s}{'median':>14s}{'max':>14s}{'>0 cells':>10s}")
    print("-" * 90)
    for name, v in (("harvest field level (tier-1)", lev_pos), ("S_pot (aquatic_food / cultivability)", sp_pos)):
        if v:
            print(f"{name:38s}{min(v):14.4g}{q(v,0.5):14.4g}{max(v):14.4g}{len(v):10d}")
        else:
            print(f"{name:38s}{'ALL ZERO':>14s}{'':14s}{'':14s}{0:10d}")

    if not sp_pos or not lev_pos:
        print("\n=> one field is entirely zero; the settlement economy cannot act.")
        return

    print()
    med_l, med_s = q(lev_pos, 0.5), q(sp_pos, 0.5)
    t2_cell = d.settle_tier2_yield * med_s
    rad = d.settle_catchment_radius
    t2_catch = d.settle_tier2_yield * med_s * (2 * rad + 1) ** 2
    print(f"median tier-1 cell level                        {med_l:14.4g}")
    print(f"median S_pot                                    {med_s:14.4g}")
    print(f"tier-2 from ONE catchment cell (40 x S_pot)     {t2_cell:14.4g}")
    print(f"tier-2 from the WHOLE {(2*rad+1)**2}-cell catchment         {t2_catch:14.4g}")
    print(f"  => tier-2 as a FRACTION of one cell's tier-1  {t2_catch / med_l:14.4g}")
    # CORRECTED: the agglomeration base carries cv_ref (= forage_kcal * forage_cap_hours), which converts the
    # [0,1] S_pot index into kcal. Its docstring says so: "in cap-kcal units so aggl_tier2 is a dimensionless
    # intensification multiple". The tier-2 term has NO such factor. That asymmetry is the thing to show.
    fk = getattr(w._fields, "forage_kcal", None)
    if fk is None:
        print("\nno forage_kcal field; cannot price the agglomeration base")
        return
    cv_ref_med = q([float(fk[y, x]) for x, y in land if float(fk[y, x]) > 0], 0.5) * d.forage_cap_hours
    A = d.aggl_tier2 * med_s * cv_ref_med
    beta = d.aggl_beta
    print(f"\ncv_ref = forage_kcal x forage_cap_hours (median)  {cv_ref_med:14.4g}")
    print(f"aggl base A_cell = aggl_tier2 x S_pot x cv_ref    {A:14.4g}")
    for n in (10, 50, 100):
        pc = A * (n ** beta - n) / n
        print(f"  => aggl per-capita bonus at n={n:<4d}            {pc:14.4g}   "
              f"({pc / med_l:.3g} of a cell's tier-1)")
    print("\nTHE ASYMMETRY: both terms read the SAME [0,1] S_pot index.")
    print(f"  agglomeration multiplies it by cv_ref  = {cv_ref_med:.4g}  -> kcal, ALIVE")
    print(f"  tier-2 multiplies it by nothing        = 1            -> index units, DEAD")
    print(f"  settle_tier2_yield needed for parity with one cell's tier-1: "
          f"{med_l / max(med_s, 1e-12):.4g}  (config has {d.settle_tier2_yield:g})")


if __name__ == "__main__":
    main()
