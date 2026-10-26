"""R-106 Add.106 part 1 — is the density-fertility brake mis-scaled by a NUMERATOR/DENOMINATOR RADIUS MISMATCH?

The density brake is  p_birth *= 1 - fill**exponent  (exponent = 6), where
    fill = (people within settle_radius) * burn / (food within settle_catchment_radius)
and in the code the two radii DIFFER:
    people : settle_radius            = 2  -> 5x5 = 25-cell window (phase1_model:2963)
    food   : settle_catchment_radius  = 1  -> 3x3 =  9-cell window (phase1_model:1317, _settlement_carrying_capacity)
The numerator spans 2.78x the denominator's area, so `fill` reads the food NEED over 25 cells against the food
SUPPLY of 9 cells. That inflates the Malthusian stress signal, and with exponent 6 the brake is ~0 below
fill 0.7 and near-total at fill 1, so a small inflation of fill moves the brake a lot.

HYPOTHESIS: at equilibrium the as-coded fill sits high enough (~0.7-0.9) to cut births hard, while the
MATCHED-radius fill (people and food both over radius 1) sits near ~0.3 — the village's true fraction of its
food ceiling — where the brake is negligible. If so, the preventive check fires at ~1/3 of true food capacity
because of the radius mismatch, and THAT is why the population stalls at ~8% of regional capacity.

This is a pure observer at equilibrium. Nothing is changed. It measures, per settlement, PERSON-WEIGHTED (the
brake a mother actually experiences):
    fill_ascoded   people(r=2) * burn / ceiling(r=1)     what the model uses now
    fill_matched   people(r=1) * burn / ceiling(r=1)     numerator and denominator on the SAME 9 cells
    brake = 1 - fill**6 for each
If the two brakes differ, the mismatch is load-bearing and the fix is to match the numerator radius to the
anchored food radius (1) — NOT to touch the anchored settle_catchment_radius.
"""
import os
import sys
import statistics as st

ROOT = r"C:\Users\syatom\Projects\SiC Games"
sys.path.insert(0, os.path.join(ROOT, "scratchpad"))
from bp_savanna_probe import build, runconfig

STEPS = int(os.environ.get("C_STEPS", "1200"))
SEEDS = [int(x) for x in os.environ.get("C_SEEDS", "0,1,2").split(",")]
PATCH = int(os.environ.get("C_PATCH", "40"))
N = 100


def run_one(ws):
    canon = dict(runconfig.load()["DemographyConfig"])
    w = build(canon, ws, 0, patch=PATCH, clim="temperate", terr="coastal")
    for _ in range(STEPS):
        w.step()
        if not w.agent_list:
            return None
    d = w._demog
    burn = w._burn
    exp = d.density_fert_exponent
    r_people = d.settle_radius            # 2, as coded
    r_food = d.settle_catchment_radius    # 1, anchored
    occ = {}
    for a in w.agent_list:
        occ[a.pos] = occ.get(a.pos, 0) + 1

    def block(site, rad):
        sx, sy = site
        return sum(occ.get(((sx + dx) % N, (sy + dy) % N), 0)
                   for dx in range(-rad, rad + 1) for dy in range(-rad, rad + 1))

    rows = []
    for site in w._settlement_sites:
        cap = w._settlement_carrying_capacity(site)      # food over r_food, in kcal/step
        if cap <= 0:
            continue
        n_coded = block(site, r_people)                  # people over r=2
        n_match = block(site, r_food)                    # people over r=1
        fill_coded = n_coded * burn / cap
        fill_match = n_match * burn / cap
        rows.append((n_match, fill_coded, fill_match,
                     1.0 - min(1.0, fill_coded) ** exp,
                     1.0 - min(1.0, fill_match) ** exp))
    if not rows:
        return None
    # PERSON-WEIGHTED by the r=1 head-count (the mothers who feel the brake)
    def pw(idx):
        num = sum(r[0] * r[idx] for r in rows)
        den = sum(r[0] for r in rows)
        return num / den if den else float("nan")
    return dict(exp=exp, n_sites=len(rows),
                fill_coded=pw(1), fill_match=pw(2),
                brake_coded=pw(3), brake_match=pw(4))


def ms(v):
    v = [x for x in v if x == x]
    if not v:
        return float("nan"), 0.0
    return st.mean(v), (st.stdev(v) / len(v) ** 0.5 if len(v) > 1 else 0.0)


def main():
    print(f"DENSITY-FERTILITY FILL: as-coded vs matched-radius | temperate patch {PATCH} | {STEPS} steps | seeds {SEEDS}")
    rows = [r for r in (run_one(s) for s in SEEDS) if r]
    if not rows:
        print("no data")
        return
    print(f"\nexponent = {rows[0]['exp']:.0f} | sites {ms([r['n_sites'] for r in rows])[0]:.0f}")
    print(f"\n{'quantity':40s}{'as-coded (r=2/r=1)':>22s}{'matched (r=1/r=1)':>22s}")
    print("-" * 84)
    for k, label in (("fill", "village fill fraction (person-wtd)"),
                     ("brake", "birth multiplier 1-fill^6 (person-wtd)")):
        mc, ec = ms([r[f"{k}_coded"] for r in rows])
        mm, em = ms([r[f"{k}_match"] for r in rows])
        print(f"{label:40s}{f'{mc:.3f} +/- {ec:.3f}':>22s}{f'{mm:.3f} +/- {em:.3f}':>22s}")
    bc = ms([r['brake_coded'] for r in rows])[0]
    bm = ms([r['brake_match'] for r in rows])[0]
    print(f"\n  as-coded, births are cut to {bc*100:.0f}% of nominal by the density brake at equilibrium")
    print(f"  matched,  births would be    {bm*100:.0f}% of nominal")
    print(f"  => the radius mismatch accounts for a {(bm-bc)*100:.0f} percentage-point birth suppression")


if __name__ == "__main__":
    main()
