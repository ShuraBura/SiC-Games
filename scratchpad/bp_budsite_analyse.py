"""Analyse bp_budsite_probe outputs.

Q1  Do buds found daughters OFF the food patch, and do those villages die?
Q2  Are the starving OFF the patch, and if so, how did they get there — in an off-patch bud village, or by
    wandering off the edge outside any village?
"""
import json
import os
import statistics as st

ROOT = r"C:\Users\syatom\Projects\SiC Games"
BORN_AFTER = int(os.environ.get("BA_BORN_AFTER", "1000"))   # skip the founding transient


def fr(xs, p):
    return (sum(1 for x in xs if p(x)) / len(xs)) if xs else float("nan")


def lifestats(sites, end_step):
    dead = [s for s in sites if s["died"] is not None]
    life = [s["died"] - s["born"] for s in dead]
    short = sum(1 for L in life if L < 100)
    return (len(sites), (short / len(sites)) if sites else float("nan"),
            st.median(life) if life else float("nan"), len(dead) / len(sites) if sites else float("nan"))


def main():
    for w in ("temperate", "montane", "savanna"):
        p = os.path.join(ROOT, "scratchpad", f"budprobe_{w}.json")
        if not os.path.exists(p):
            print(f"== {w}: no file")
            continue
        d = json.load(open(p, encoding="utf-8"))
        S = [s for s in d["sites"] if s["born"] >= BORN_AFTER]
        D, L = d["deaths"], d["living"]
        end = max([x["step"] for x in D] + [0])
        bud = [s for s in S if s["bud"]]
        print(f"\n== {w.upper()}  patch {d['patch_cells']} cells | sites born >= {BORN_AFTER}: {len(S)} "
              f"({len(bud)} by budding) | deaths {len(D)} | living {len(L)}")
        print(f"   Q1  bud sites founded OFF the patch: {fr(bud, lambda s: not s['on_patch']):.1%}"
              f"   (non-bud sites off patch: {fr([s for s in S if not s['bud']], lambda s: not s['on_patch']):.1%})")
        for lab, grp in (("bud, ON patch ", [s for s in bud if s["on_patch"]]),
                         ("bud, OFF patch", [s for s in bud if not s["on_patch"]]),
                         ("non-bud       ", [s for s in S if not s["bud"]])):
            n, short, med, dfr = lifestats(grp, end)
            print(f"       {lab}: n={n:5d}  dead<100 steps {short:.1%}  dead overall {dfr:.1%}  "
                  f"median lifetime of the dead {med:.0f} steps")
        print(f"   Q2  {'':42s}{'DYING':>10s}{'LIVING':>10s}")
        rows = [("OFF the food patch", lambda xs: fr(xs, lambda x: not x["on_patch"])),
                ("in any village", lambda xs: fr(xs, lambda x: x["village"])),
                ("in a BUD village", lambda xs: fr(xs, lambda x: x["in_bud_village"])),
                ("in an OFF-patch bud village", lambda xs: fr(xs, lambda x: x["in_bud_village"] and x["bud_village_on_patch"] is False)),
                ("off patch AND in no village", lambda xs: fr(xs, lambda x: (not x["on_patch"]) and not x["village"])),
                ("distance to patch, median", lambda xs: st.median([x["patch_dist"] for x in xs])),
                ("distance to a stocked granary, median", lambda xs: st.median([x["granary_dist"] for x in xs])),
                ("people on own cell, median", lambda xs: st.median([x["occ"] for x in xs]))]
        for lab, fn in rows:
            print(f"       {lab:42s}{fn(D):>10.3f}{fn(L):>10.3f}")
        off = [x for x in D if not x["on_patch"]]
        if off:
            print(f"       -> of the OFF-patch dead: in an off-patch bud village "
                  f"{fr(off, lambda x: x['in_bud_village'] and x['bud_village_on_patch'] is False):.1%}, "
                  f"in some other village {fr(off, lambda x: x['village'] and not (x['in_bud_village'] and x['bud_village_on_patch'] is False)):.1%}, "
                  f"in no village {fr(off, lambda x: not x['village']):.1%}; "
                  f"median distance to patch {st.median([x['patch_dist'] for x in off])}")


if __name__ == "__main__":
    main()
