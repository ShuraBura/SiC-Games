"""R-106 Add.105 part 4 — the CORRECTED stay/leave comparison, with the agglomeration bonus included.

part 3 (bp_malthus_cliff.py) REFUTED the tier-2 cliff: tier-2 deposits ~37 kcal at the site against a tier-1 of
~2.27e6, i.e. 1/16000 of the cell. It is numerically irrelevant, and the "the surplus sits at a point" story is
dead. But that probe omitted the AGGLOMERATION term from BOTH sides of the stay/leave comparison:

    S += aggl_R[cy,cx] * (n**aggl_beta - n)          # point mode, superlinear in the CROWD SIZE

That term exists only where a crowd stands, so omitting it understates STAYING and inflates the 14x headroom
part 3 reported. This probe reproduces the model's own per-cell pool EXACTLY (tier-1 + tier-2-if-site + aggl)
and compares, per person:

   stay    S(site, n)   / n            what a member actually eats where it stands
   leave   S(cell, 1)   / 1            what it would eat ALONE on the best cell within one step
   leave_k S(cell, k+1) / (k+1)        ... if k others are already there (the honest IFD comparison)

WHY THE ONE-STEP RING, NOT THE WHOLE MAP. Movement is 1 cell/step (mobility_radius), so the only choice an
agent actually faces is its 8-neighbourhood. A better cell 5 cells away is not an option it can take.

If stay/leave >= 1 the packing is ADAPTIVE (Add.79's conclusion) and the pin is not the defect.
If stay/leave <  1 the packing is IMPOSED by the residence pin against the agents' own interest, and Add.79's
"adaptive equilibrium" conclusion is wrong.
"""
import os
import sys
import statistics as st

ROOT = r"C:\Users\syatom\Projects\SiC Games"
sys.path.insert(0, os.path.join(ROOT, "scratchpad"))
from bp_savanna_probe import build, runconfig

STEPS = int(os.environ.get("C_STEPS", "800"))
SEEDS = [int(x) for x in os.environ.get("C_SEEDS", "0,1,2").split(",")]
N = 100


def run_one(clim, ws):
    canon = dict(runconfig.load()["DemographyConfig"])
    w = build(canon, ws, 0, clim=clim)
    for _ in range(STEPS):
        w.step()
        if not w.agent_list:
            return None
    d = w._demog
    tf = w._harvest_field
    pop = w.agent_list
    cells = {}
    for a in pop:
        cells[a.pos] = cells.get(a.pos, 0) + 1

    aggl_on = getattr(d, "enable_agglomeration", False)
    aggl_mode = getattr(d, "aggl_mode", "point") if aggl_on else "point"
    aggl_R = (w._aggl_point_base_field() if aggl_mode == "point" else w._aggl_R_field()) if aggl_on else None
    aggl_a = (d.aggl_beta if aggl_mode == "point" else d.aggl_alpha) if aggl_on else 1.15
    aggl_h = d.aggl_half if aggl_on else 100.0
    sites = set(w._settlement_sites)

    def pool(cell, n):
        """The model's own per-cell food pool S at occupancy n (phase1_model._do_harvest)."""
        cx, cy = cell
        S = tf.level(cx, cy)
        if cell in sites:
            S += (w._settlement_catchment_yield(cell) * w._tier2_shock
                  * w._settlement_soil.get(cell, 1.0))
        if aggl_on and aggl_R is not None and n > 0:
            if aggl_mode == "point":
                S += float(aggl_R[cy, cx]) * (n ** aggl_a - n)
            else:
                na = n ** aggl_a
                S += float(aggl_R[cy, cx]) * (na / (na + aggl_h ** aggl_a))
        return S

    rows = []
    for a in pop:
        here = a.pos
        n_here = cells.get(here, 1)
        stay = pool(here, n_here) / n_here
        best_alone = best_join = None
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                c = ((here[0] + dx) % N, (here[1] + dy) % N)
                if w._fields.isWater[c[1], c[0]] != 0:
                    continue
                k = cells.get(c, 0)
                alone = pool(c, 1)
                join = pool(c, k + 1) / (k + 1)
                best_alone = alone if best_alone is None else max(best_alone, alone)
                best_join = join if best_join is None else max(best_join, join)
        if best_alone is None:
            continue
        rows.append(dict(stay=stay, leave_alone=best_alone, leave_join=best_join,
                         r_alone=best_alone / stay if stay > 0 else float("nan"),
                         r_join=best_join / stay if stay > 0 else float("nan"),
                         on_site=1.0 if here in sites else 0.0, n_here=n_here))
    if not rows:
        return None
    def m(k):
        v = [r[k] for r in rows if r[k] == r[k]]
        return st.mean(v) if v else float("nan")
    out = {k: m(k) for k in rows[0]}
    out["frac_better_join"] = sum(1 for r in rows if r["r_join"] > 1.0) / len(rows)
    out["frac_better_2x"] = sum(1 for r in rows if r["r_join"] > 2.0) / len(rows)
    # DUMP THE RAW PER-AGENT SIGNAL so the figure can show the distribution, not a mean.
    if os.environ.get("C_DUMP"):
        import json
        with open(os.environ["C_DUMP"], "a") as fh:
            for r in rows:
                fh.write(json.dumps({"r": r["r_join"], "n": r["n_here"], "s": r["on_site"],
                                     "stay": r["stay"]}) + "\n")
    return out


def main():
    clim = os.environ.get("C_BIOME", "temperate")
    print(f"STAY vs LEAVE, agglomeration INCLUDED | {clim} | {STEPS} steps | seeds {SEEDS}")
    print("per-person food, where it stands vs the best cell ONE STEP away\n")
    rows = [r for r in (run_one(clim, s) for s in SEEDS) if r]
    keys = [("n_here", "co-occupants of the agent's cell"),
            ("on_site", "frac standing on a settlement site"),
            ("stay", "STAY: per-person food where it is"),
            ("leave_join", "LEAVE: per-person, joining the best neighbour"),
            ("leave_alone", "LEAVE: per-person, alone there (upper bound)"),
            ("r_join", "ratio leave/stay (realistic)"),
            ("r_alone", "ratio leave/stay (upper bound)"),
            ("frac_better_join", "frac of people for whom leaving PAYS"),
            ("frac_better_2x", "frac for whom leaving pays 2x or more")]
    for k, label in keys:
        v = [r[k] for r in rows if r[k] == r[k]]
        if not v:
            continue
        mm = st.mean(v)
        se = st.stdev(v) / len(v) ** 0.5 if len(v) > 1 else 0.0
        print(f"{label:46s}{mm:14.3f} +/- {se:.3f}")


if __name__ == "__main__":
    main()
