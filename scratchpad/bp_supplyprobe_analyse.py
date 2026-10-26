"""Analyse bp_supplyprobe output: where are the mothers of starving children, against mothers of living children?"""
import json
import os
import statistics as st
import sys

ROOT = r"C:\Users\syatom\Projects\SiC Games"
W = sys.argv[1:] or ["savanna"]


def cls(r):
    if not r["village"]:
        return "mobile"
    return "on-site" if r["on_site"] else "village-offsite"


def q(v, p):
    v = sorted(v)
    return v[min(len(v) - 1, int(p * len(v)))] if v else float("nan")


for w in W:
    f = os.path.join(ROOT, "scratchpad", f"supplyprobe_{w}.json")
    if not os.path.exists(f):
        print(w, "missing"); continue
    d = json.load(open(f, encoding="utf-8"))
    print(f"\n=== {w.upper()}  deaths n={len(d['deaths'])}  living n={len(d['living'])}")
    for name, R in (("DYING", d["deaths"]), ("LIVING", d["living"])):
        n = len(R)
        c = {k: sum(1 for r in R if cls(r) == k) / n for k in ("on-site", "village-offsite", "mobile")}
        stocked = sum(1 for r in R if r["store_ph"] > 0.01) / n
        print(f"  {name:6s} class: on-site {c['on-site']:.2f}  village-offsite {c['village-offsite']:.2f}  "
              f"mobile {c['mobile']:.2f} | own cell stocked {stocked:.2f} | mother at cap "
              f"{sum(r['m_at_cap'] for r in R) / n:.2f}")
        print(f"         median: occ {q([r['occ'] for r in R], .5)}  store/head {q([r['store_ph'] for r in R], .5):.3f}  "
              f"granary dist {q([r['gdist'] for r in R], .5)} (p90 {q([r['gdist'] for r in R], .9)})  "
              f"site dist {q([r['sdist'] for r in R], .5)}  ratecap {q([r['ratecap'] for r in R if r['ratecap'] is not None], .5):.2f}  "
              f"intake {q([r['m_intake'] for r in R], .5):.2f}")
        va = [r["village_age"] for r in R if r["village_age"] is not None]
        if va:
            print(f"         village age (steps) median {q(va, .5)}  p10 {q(va, .1)}  frac < 60 steps "
                  f"{sum(1 for x in va if x < 60) / len(va):.2f}")
        for k in ("on-site", "village-offsite", "mobile"):
            S = [r for r in R if cls(r) == k]
            if S:
                print(f"         {k:15s} n={len(S):5d}  stocked {sum(1 for r in S if r['store_ph'] > 0.01) / len(S):.2f}  "
                      f"intake med {q([r['m_intake'] for r in S], .5):.2f}  gdist med {q([r['gdist'] for r in S], .5)}  "
                      f"occ med {q([r['occ'] for r in S], .5)}")
    # death risk per class: deaths share / living share (a relative hazard proxy)
    Dn, Ln = len(d["deaths"]), len(d["living"])
    print("  relative risk (death share / living share):",
          {k: round((sum(1 for r in d['deaths'] if cls(r) == k) / Dn) /
                    max(sum(1 for r in d['living'] if cls(r) == k) / Ln, 1e-9), 2)
           for k in ("on-site", "village-offsite", "mobile")})
