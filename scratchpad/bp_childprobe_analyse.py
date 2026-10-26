"""Analyse bp_childprobe outputs: why children starve (juvenile deaths vs living juveniles, per world)."""
import json
import os
import statistics as st

ROOT = r"C:\Users\syatom\Projects\SiC Games"


def fr(xs, p):
    return (sum(1 for x in xs if p(x)) / len(xs)) if xs else float("nan")


def md(xs, k):
    v = [x[k] for x in xs if x.get(k) is not None]
    return st.median(v) if v else float("nan")


def main():
    for w in ("savanna", "montane", "temperate"):
        p = os.path.join(ROOT, "scratchpad", f"childprobe_{w}.json")
        if not os.path.exists(p):
            print(f"== {w}: no file")
            continue
        d = json.load(open(p, encoding="utf-8"))
        D, L = d["deaths"], d["living"]
        DM = [x for x in D if x.get("mother") == "alive"]
        LM = [x for x in L if x.get("mother") == "alive"]
        print(f"\n== {w.upper()}  juvenile starvation deaths {len(D)} | living juvenile samples {len(L)}")
        print(f"   {'':46s}{'DYING':>10s}{'LIVING':>10s}")
        print(f"   {'mother alive':46s}{fr(D, lambda x: x.get('mother') == 'alive'):>10.3f}"
              f"{fr(L, lambda x: x.get('mother') == 'alive'):>10.3f}")
        print(f"   {'child age (yr), median':46s}{md(D, 'age_yr'):>10.2f}{md(L, 'age_yr'):>10.2f}")
        print(f"   {'child own intake (x need), median':46s}{md(D, 'child_intake'):>10.3f}{md(L, 'child_intake'):>10.3f}")
        print("   -- where the mother is alive --")
        rows = [("mother on the SAME cell", lambda xs: fr(xs, lambda x: x["same_cell"])),
                ("mother AT her reserve cap (has overflow)", lambda xs: fr(xs, lambda x: x["m_at_cap"])),
                ("mother reserve fill after provisioning, median", lambda xs: md(xs, "m_fill")),
                ("mother's shareable reserve (child-months), median", lambda xs: md(xs, "m_shareable")),
                ("mother intake (x her need), median", lambda xs: md(xs, "m_intake")),
                ("RATE cap on mother's cell (x her need), median", lambda xs: md(xs, "m_ratecap")),
                ("rate cap BELOW her own need", lambda xs: fr(xs, lambda x: x["m_ratecap"] < 1.0)),
                ("mother's dependent juveniles, median", lambda xs: md(xs, "m_deps")),
                ("mother consumption factor, median", lambda xs: md(xs, "m_cf"))]
        for lab, fn in rows:
            print(f"   {lab:46s}{fn(DM):>10.3f}{fn(LM):>10.3f}")
        if DM:
            gap = fr(DM, lambda x: (not x["m_at_cap"]) and x["m_shareable"] > 0.5)
            sup = fr(DM, lambda x: x["m_ratecap"] < 1.0)
            print(f"   -> of child deaths with a living mother: mother had NO overflow yet held >0.5 child-month of "
                  f"reserve above half-cap = {gap:.1%}   | mother's cell rate-capped below her OWN need = {sup:.1%}")


if __name__ == "__main__":
    main()
