"""R-106 Add.105 part 7 — IS THE POPULATION FOOD-LIMITED BY STOCK, OR BY RATE?

The canonical config has `enable_forage_cap = True`, `forage_cap_hours = 100`. So a person's intake is
    intake <= forage_kcal(cell) * 100
regardless of how much food STOCK the cell holds. A person needs BURN = 75,000 per year, so a cell can feed
ANYONE only if
    forage_kcal >= BURN / forage_cap_hours = 750 kcal/hr.

Two different carrying capacities therefore exist, and the project has been reading the wrong one:
  STOCK capacity   sum over cells of level/BURN        what "82% of forage is unused" measures
  RATE capacity    sum over cells that clear 750       who can actually eat

If most land fails the RATE test, then "starving next to available food" is literally true and is NOT a
dispersal failure: the food next door cannot be extracted fast enough to live on. That would also explain why
hunger dispersal RAISED the starvation share (0.32 -> 0.46) — it moves people onto cells that cannot feed them.

Static fields only, so this is cheap and exact. No dynamics, no seeds beyond the world lottery.
"""
import os
import sys
import statistics as st

ROOT = r"C:\Users\syatom\Projects\SiC Games"
sys.path.insert(0, os.path.join(ROOT, "scratchpad"))
from bp_savanna_probe import build, runconfig

N = 100
BURN = 75000.0
WORLDS = {
    "temperate": dict(terr="coastal", clim="temperate"),
    "savanna":   dict(terr="coastal", clim="savanna"),
    "montane":   dict(terr="mountainous", clim="savanna"),
}


def q(v, p):
    v = sorted(v)
    return v[min(len(v) - 1, max(0, int(p * (len(v) - 1))))] if v else float("nan")


def one(terr, clim, ws):
    canon = dict(runconfig.load()["DemographyConfig"])
    w = build(canon, ws, 0, clim=clim, terr=terr)
    w.step()
    d, tf = w._demog, w._harvest_field
    fk = getattr(w._fields, "forage_kcal", None)
    thr = BURN / d.forage_cap_hours                     # kcal/hr a cell must return to feed ONE person
    land = [(x, y) for y in range(N) for x in range(N) if w._fields.isWater[y, x] == 0]
    rates = [float(fk[y, x]) for x, y in land]
    stock = [tf.level(x, y) for x, y in land]
    # STOCK capacity: what the land holds, if extraction were free
    stock_cap = sum(s for s in stock) / BURN
    # RATE capacity: only cells that clear the per-person rate threshold can host anyone at all
    ok = [(x, y) for (x, y) in land if float(fk[y, x]) >= thr]
    rate_cap = sum(tf.level(x, y) for x, y in ok) / BURN
    # and even on a good cell, the stock may run out first
    return dict(
        thr=thr,
        rate_med=st.median(rates), rate_p10=q(rates, 0.10), rate_p90=q(rates, 0.90),
        frac_land_ok=len(ok) / len(land),
        frac_foodcells_ok=(len([1 for x, y in ok if tf.level(x, y) > 0])
                           / max(1, len([1 for x, y in land if tf.level(x, y) > 0]))),
        stock_cap=stock_cap, rate_cap=rate_cap,
        ratio=(rate_cap / stock_cap) if stock_cap > 0 else float("nan"))


def main():
    print("RATE CAP vs STOCK CAP | canonical config | static fields\n")
    print(f"a person needs BURN = {BURN:,.0f}/yr; the cap allows forage_kcal x {100} per year")
    print(f"=> a cell feeds ANYONE only if forage_kcal >= {BURN/100:,.0f} kcal/hr\n")
    res = {n: [one(c["terr"], c["clim"], s) for s in (0, 1, 2)] for n, c in WORLDS.items()}
    keys = [("rate_p10", "forage_kcal p10 (kcal/hr)", "{:.0f}"),
            ("rate_med", "forage_kcal median", "{:.0f}"),
            ("rate_p90", "forage_kcal p90", "{:.0f}"),
            ("thr", "THRESHOLD to feed one person", "{:.0f}"),
            ("frac_land_ok", "frac of LAND that clears the rate", "{:.3f}"),
            ("frac_foodcells_ok", "frac of FOOD cells that clear it", "{:.3f}"),
            ("stock_cap", "STOCK capacity (people)", "{:.0f}"),
            ("rate_cap", "RATE capacity (people)", "{:.0f}"),
            ("ratio", "rate / stock capacity", "{:.3f}")]
    print(f"{'metric':42s}" + "".join(f"{w:>20s}" for w in WORLDS))
    print("-" * 102)
    for k, label, fmt in keys:
        line = ""
        for wn in WORLDS:
            v = [r[k] for r in res[wn] if r[k] == r[k]]
            m = st.mean(v); e = st.stdev(v) / len(v) ** 0.5 if len(v) > 1 else 0.0
            line += f"{fmt.format(m) + ' +/- ' + fmt.format(e):>20s}"
        print(f"{label:42s}{line}")


if __name__ == "__main__":
    main()
