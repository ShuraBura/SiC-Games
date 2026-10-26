"""Analyse bp_deathprobe outputs: what separates the STARVING from the LIVING, per canonical world.

Every field is compared DYING vs LIVING (same schedule), so a difference is a difference, not a base rate.
The decisive split for the granary hypothesis:
    died with NO stored food on the cell        -> starved AWAY from the granary (access failure)
    died with ample stored food on the cell     -> starved BESIDE the granary (draw failure)
"""
import json
import os
import statistics as st

ROOT = r"C:\Users\syatom\Projects\SiC Games"


def frac(xs, pred):
    return (sum(1 for x in xs if pred(x)) / len(xs)) if xs else float("nan")


def med(xs, k):
    v = [x[k] for x in xs if x.get(k) is not None]
    return st.median(v) if v else float("nan")


def main():
    for w in ("temperate", "savanna", "montane"):
        p = os.path.join(ROOT, "scratchpad", f"deathprobe_{w}.json")
        if not os.path.exists(p):
            print(f"== {w}: no file")
            continue
        d = json.load(open(p, encoding="utf-8"))
        D, L = d["deaths"], d["living"]
        print(f"\n== {w.upper()}  deaths {len(D)}  |  living samples {len(L)}  (from step {d['from_step']})")
        print(f"   {'':40s}{'DYING':>10s}{'LIVING':>10s}")
        rows = [
            ("on a storage-eligible cell", lambda xs: frac(xs, lambda x: x["owz"])),
            ("cell holds ANY stored food (>0.1 res)", lambda xs: frac(xs, lambda x: x["store"] > 0.1)),
            ("cell holds >=1 body-reserve per head", lambda xs: frac(xs, lambda x: x["store"] >= x["occ"])),
            ("stored food on cell, median (reserves)", lambda xs: med(xs, "store")),
            ("occupancy of own cell, median", lambda xs: med(xs, "occ")),
            ("cell food per head (x need), median", lambda xs: med(xs, "food_pc")),
            ("juvenile", lambda xs: frac(xs, lambda x: x["juv"])),
            ("family head: none", lambda xs: frac(xs, lambda x: x["head"] == "none")),
            ("family head: on same cell", lambda xs: frac(xs, lambda x: x["head"] == "here")),
            ("family head: ELSEWHERE", lambda xs: frac(xs, lambda x: x["head"] == "away")),
            ("inside a village", lambda xs: frac(xs, lambda x: x["village"])),
            ("intake this step (x need), median", lambda xs: med(xs, "intake")),
            ("intake EMA (x need), median", lambda xs: med(xs, "ema")),
            ("reserve after harvest (fill), median", lambda xs: med(xs, "fedres")),
            ("age (yr), median", lambda xs: med(xs, "age_yr")),
        ]
        for label, fn in rows:
            print(f"   {label:40s}{fn(D):>10.3f}{fn(L):>10.3f}")
        # THE DECISIVE SPLIT
        beside = [x for x in D if x["store"] >= max(1, x["occ"]) * 0.5]
        away = [x for x in D if x["store"] <= 0.1]
        print(f"   -> died BESIDE a stocked granary (>=0.5 reserve/head on the cell): {len(beside)/len(D):.1%}"
              f"   | died with NO granary on the cell: {len(away)/len(D):.1%}")
        if beside:
            print(f"      of those beside a stocked granary: juvenile {frac(beside, lambda x: x['juv']):.0%}, "
                  f"head none {frac(beside, lambda x: x['head']=='none'):.0%} / here "
                  f"{frac(beside, lambda x: x['head']=='here'):.0%} / away {frac(beside, lambda x: x['head']=='away'):.0%}, "
                  f"post-harvest fill median {med(beside, 'fedres'):.2f}")


if __name__ == "__main__":
    main()
