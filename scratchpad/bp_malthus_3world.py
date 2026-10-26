"""R-106 Add.105 part 6 — THREE-WORLD DIAGNOSIS, using the model's OWN harvest hook.

The supervisor's call: diagnose further before changing anything, and check whether the dead tier-2 term masks
a SECOND defect. This probe therefore measures, on all three canonical worlds:

  1. IS THE UNIT BUG WORLD-INDEPENDENT?  tier-2 measured at real sites vs the cell tier-1 it is added to.
  2. WHAT ACTUALLY FEEDS A SETTLED PERSON?  the real per-cell food pool S and occupancy, read from the model's
     own `_diag_pool` hook — recorded AFTER every bonus AND the carrying-capacity ceiling. Three of my earlier
     measurements were wrong because I re-implemented the harvest; this one cannot be, because it is the
     harvest's own number.
  3. DOES THE CEILING BIND?  S vs `_settlement_carrying_capacity`. If the ceiling binds, the village IS
     food-limited by its 9-cell catchment and the system is already Malthusian at the village scale — which
     would mean the defect is the CATCHMENT SIZE, not (only) the dead tier-2 term.
  4. IS THERE FOOD NEXT DOOR?  per-capita where people stand vs the best EMPTY neighbour cell (capped the same
     way). This is the supervisor's question: do they starve beside available food?

A SECOND DEFECT would show as: the ceiling binding hard while occupied cells still hold far more people than
their own catchment feeds, or a biome where the numbers do not follow the temperate pattern.
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
BURN = 75000.0

WORLDS = {
    "temperate":  dict(terr="coastal", clim="temperate"),
    "savanna":    dict(terr="coastal", clim="savanna"),
    "montane":    dict(terr="mountainous", clim="savanna"),
}


def run_one(terr, clim, ws):
    canon = dict(runconfig.load()["DemographyConfig"])
    w = build(canon, ws, 0, clim=clim, terr=terr)
    for _ in range(STEPS - 1):
        w.step()
        if not w.agent_list:
            return None
    w._diag_pool = {}            # arm the model's OWN hook for the final step
    w.step()
    if not w.agent_list:
        return None
    pool = w._diag_pool
    w._diag_pool = None
    if not pool:
        return None
    d, tf = w._demog, w._harvest_field
    sites = set(w._settlement_sites)
    ceiling_on = getattr(d, "enable_catchment_ceiling", False)

    occ = {c: n for c, (S, n) in pool.items() if n > 0}
    pc = {c: S / n for c, (S, n) in pool.items() if n > 0}
    tot_pop = sum(occ.values())

    # (1) the unit bug, measured at REAL sites by the model's own function
    t2 = [w._settlement_catchment_yield(s) for s in sites]
    t1_at_sites = [tf.level(*s) for s in sites]

    # (3) does the ceiling bind?  S vs the catchment ceiling, at occupied cells where the cap applies.
    # PERSON-WEIGHTED. A mean over CELLS answers "what fraction of cells bind"; the question is "what does a
    # PERSON experience", and the binding cells are exactly the crowded ones. Both are reported so the gap is
    # visible — this is the hidden-denominator class the project keeps hitting.
    bind, bind_pw = [], []
    for c, (S, n) in pool.items():
        if n <= 0:
            continue
        capped = (c in sites) or getattr(d, "enable_aggl_ceiling", False)
        if ceiling_on and capped:
            cap = w._settlement_carrying_capacity(c)
            if cap > 0:
                bind.append(S / cap)
                bind_pw.extend([S / cap] * n)

    # (4) food next door: per-capita here vs the best EMPTY neighbour (a lone mover, capped the same way)
    # EVERY row below is PERSON-WEIGHTED (each cell's value repeated n times). The per-cell means are kept
    # alongside, because the gap between them IS the finding on the ceiling row: the cells that bind are
    # exactly the crowded ones, so a per-cell mean understates what a PERSON experiences.
    ratios, fed_here, feeds_cell = [], [], []
    ratios_c = []
    for c, n in occ.items():
        best = None
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                q = ((c[0] + dx) % N, (c[1] + dy) % N)
                if w._fields.isWater[q[1], q[0]] != 0 or q in occ:
                    continue                      # EMPTY neighbours only
                v = tf.level(*q)
                if ceiling_on and getattr(d, "enable_aggl_ceiling", False):
                    v = min(v, w._settlement_carrying_capacity(q))
                best = v if best is None else max(best, v)
        if best is not None and pc[c] > 0:
            ratios_c.append(best / pc[c])
            ratios.extend([best / pc[c]] * n)
        fed_here.extend([pc[c] / BURN] * n)          # BURN-units the CELL POOL gives each occupant on average
        feeds_cell.extend([tf.level(*c) / BURN] * n)  # people this cell's OWN forage would feed

    # THE DISTRIBUTIONAL CHECK. The cell pool is split by `compute_harvest_shares` with a contest exponent,
    # so a healthy CELL mean is consistent with a starving tail. `_intake_ema` is the agent's own realised
    # intake relative to need (~1.0 = fed), per-agent, so it carries no denominator ambiguity.
    ie = [getattr(a, "_intake_ema", float("nan")) for a in w.agent_list]
    ie = [v for v in ie if v == v]
    ie_s = sorted(ie)
    def pct(p):
        return ie_s[min(len(ie_s) - 1, max(0, int(p * (len(ie_s) - 1))))] if ie_s else float("nan")

    lt = w.life_table()
    n_food = sum(1 for y in range(N) for x in range(N)
                 if w._fields.isWater[y, x] == 0 and tf.level(x, y) > 0)
    return dict(
        pop=tot_pop, e0=lt["e0"], starv=lt["starv_share"],
        n_sites=len(sites), occ_cells=len(occ),
        ppc=tot_pop / len(occ),
        t2=st.mean(t2) if t2 else float("nan"),
        t1=st.mean(t1_at_sites) if t1_at_sites else float("nan"),
        t2_frac=(st.mean(t2) / st.mean(t1_at_sites)) if t2 and st.mean(t1_at_sites) > 0 else float("nan"),
        bind_cell=st.mean(bind) if bind else float("nan"),
        bind=st.mean(bind_pw) if bind_pw else float("nan"),
        bind_frac_cell=(sum(1 for b in bind if b > 0.99) / len(bind)) if bind else float("nan"),
        bind_frac=(sum(1 for b in bind_pw if b > 0.99) / len(bind_pw)) if bind_pw else float("nan"),
        fed=st.mean(fed_here), feeds=st.mean(feeds_cell),
        ratio=st.median(ratios) if ratios else float("nan"),
        ratio_cell=st.median(ratios_c) if ratios_c else float("nan"),
        frac_better=(sum(1 for r in ratios if r > 1) / len(ratios)) if ratios else float("nan"),
        ie_mean=st.mean(ie) if ie else float("nan"),
        ie_p10=pct(0.10), ie_p50=pct(0.50),
        ie_short=(sum(1 for v in ie if v < 1.0) / len(ie)) if ie else float("nan"),
        land_use=len(occ) / max(1, n_food))


def ms(v):
    v = [x for x in v if x == x]
    if not v:
        return float("nan"), 0.0
    return st.mean(v), (st.stdev(v) / len(v) ** 0.5 if len(v) > 1 else 0.0)


def main():
    print(f"THREE-WORLD DIAGNOSIS | {STEPS} steps | seeds {SEEDS} | model's own _diag_pool hook\n")
    res = {}
    for name, cfg in WORLDS.items():
        res[name] = [r for r in (run_one(cfg["terr"], cfg["clim"], s) for s in SEEDS) if r]
        print(f"  {name}: {len(res[name])}/{len(SEEDS)} seeds completed", flush=True)
    print()
    keys = [("pop", "pop", "{:.0f}"), ("e0", "e0 (yr)", "{:.1f}"),
            ("starv", "starvation share of deaths", "{:.2f}"),
            ("__1", "-- 1. IS THE UNIT BUG UNIVERSAL? --", ""),
            ("t1", "tier-1 at site cells", "{:.3g}"),
            ("t2", "tier-2 at site cells (MEASURED)", "{:.3g}"),
            ("t2_frac", "tier-2 / tier-1", "{:.2e}"),
            ("__2", "-- 3. DOES THE CEILING BIND? (person-weighted) --", ""),
            ("bind", "S / carrying capacity  [PERSON-wtd]", "{:.2f}"),
            ("bind_cell", "S / carrying capacity  (per-cell)", "{:.2f}"),
            ("bind_frac", "frac AT the ceiling    [PERSON-wtd]", "{:.2f}"),
            ("bind_frac_cell", "frac AT the ceiling    (per-cell)", "{:.2f}"),
            ("__3", "-- 2+4. FOOD, AND FOOD NEXT DOOR --", ""),
            ("ppc", "people per occupied cell", "{:.1f}"),
            ("feeds", "people the cell's forage feeds [PERSON-wtd]", "{:.1f}"),
            ("fed", "BURN-units from the cell pool  [PERSON-wtd]", "{:.2f}"),
            ("ratio", "best EMPTY nbr / here  [PERSON-wtd]", "{:.2f}"),
            ("frac_better", "frac of PEOPLE with a better empty nbr", "{:.2f}"),
            ("__4", "-- IS STARVATION DISTRIBUTIONAL? (per-agent) --", ""),
            ("ie_mean", "intake_ema, mean", "{:.2f}"),
            ("ie_p50", "intake_ema, median", "{:.2f}"),
            ("ie_p10", "intake_ema, p10 (the tail)", "{:.2f}"),
            ("ie_short", "frac of agents BELOW need (<1.0)", "{:.2f}"),
            ("land_use", "frac of food-bearing cells used", "{:.3f}")]
    print(f"{'metric':40s}" + "".join(f"{w:>22s}" for w in WORLDS))
    print("-" * 106)
    for k, label, fmt in keys:
        if not fmt:
            print(f"\n{label}")
            continue
        line = ""
        for wname in WORLDS:
            m, e = ms([r[k] for r in res[wname]])
            line += f"{fmt.format(m) + ' +/- ' + fmt.format(e):>22s}"
        print(f"{label:40s}{line}")


if __name__ == "__main__":
    main()
