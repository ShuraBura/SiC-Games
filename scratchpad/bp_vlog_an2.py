"""Add.130 second reading: the hungry villages (pool, soil, flows), the status order (decile 0 share, kappa), and the strict stranded test at the village-step."""
import json
import os
from collections import Counter, defaultdict

ROOT = r"C:\Users\syatom\Projects\SiC Games"
L = os.path.join(ROOT, "scratchpad", "design_logs")
W = ("temperate", "savanna", "montane")
S = (0, 1)


def jl(pre, tag):
    return [json.loads(x) for x in open(os.path.join(L, f"{pre}{tag}.jsonl"), encoding="utf-8")]


def med(xs):
    xs = sorted(x for x in xs if x is not None)
    return xs[len(xs) // 2] if xs else None


def sm(vs, *k):
    return sum(sum(v[x] or 0 for x in k) for v in vs)


def show(nm, vs):
    if not vs:
        print(f"    {nm}: none")
        return
    h = max(1.0, sum(v["heads"] for v in vs))
    print(f"    {nm}: n={len(vs)} heads med {med([v['heads'] for v in vs])} pool/cap {sm(vs,'pool')/max(1,sm(vs,'cap')):.2f} need/cap {sm(vs,'need')/max(1,sm(vs,'cap')):.2f} intake/need {sm(vs,'intake')/max(1,sm(vs,'need')):.2f} soil {sum(v['soil'] for v in vs)/len(vs):.2f}"
          f" sph {med([v['sph'] for v in vs])} in/yr {sm(vs,'in_mob','in_vil')/h:.2f} out/yr {sm(vs,'out_mob','out_vil')/h:.2f} born/yr {sm(vs,'born')/h:.3f} dead/yr {sm(vs,'dead')/h:.3f} starv/yr {sm(vs,'ds_inf','ds_ch','ds_ad')/h:.3f} fk {med([v['fk'] for v in vs])} hard {sum(v['hard'] for v in vs)/len(vs):.2f} ss {sum(v['ss'] for v in vs)/len(vs):.2f}")


out = {}
for w in W:
    for fl in ("off", "on"):
        V, D = [], []
        for s in S:
            tag = f"_vl_{w}_{fl}_s{s}"
            V += [dict(r, seed=s) for r in jl("vlg", tag) if r["n"] >= 6]
            D += [dict(r, seed=s) for r in jl("dth", tag)]
        print(f"\n=== {w} {fl}")
        H = [v for v in V if v["sph_min"] < 1.0]
        F = [v for v in V if v["sph_min"] >= 1.0]
        show("hungry", H)
        show("fed", F)
        q = sorted(v["soil"] for v in V)
        for a, b in ((0, 0.15), (0.15, 0.3), (0.3, 0.5), (0.5, 0.8), (0.8, 1.01)):
            g = [v for v in V if a <= v["soil"] < b]
            if g:
                print(f"    soil {a}-{b}: n={len(g)} P(hungry)={sum(1 for v in g if v['sph_min'] < 1)/len(g):.3f} pool/cap {sm(g,'pool')/max(1,sm(g,'cap')):.2f} need/cap {sm(g,'need')/max(1,sm(g,'cap')):.2f} starv/yr {sm(g,'ds_inf','ds_ch','ds_ad')/max(1,sum(v['heads'] for v in g)):.3f}")
        # the year before a village first goes hungry
        by = defaultdict(dict)
        for v in V:
            by[(v["seed"], tuple(v["s"]))][v["st"]] = v
        pre = []
        for key, ys in by.items():
            for st, v in ys.items():
                p = ys.get(st - 12)
                pp = ys.get(st - 24)
                if v["sph_min"] < 1 and p and pp and p["sph_min"] >= 1 and pp["sph_min"] >= 1:
                    pre.append(p)
        show("year before entry", pre)
        sett = [d for d in D if d["s"] is not None and d["inq"]]
        print(f"    deaths in draw {len(sett)}; decile0 share {sum(1 for d in sett if d['pct'] < 0.1)/max(1,len(sett)):.3f}; kap {Counter(d['kap'] for d in sett).most_common(4)}")
        grp = defaultdict(list)
        for d in sett:
            grp[(d["seed"], d["st"], tuple(d["s"]))].append(d)
        ok = tot = 0
        for g in grp.values():
            n = len(g)
            tot += n
            if g[0]["left"] >= sum(x["short"] for x in g):
                ok += n
        print(f"    strict: deaths in village-steps where the store left covers all shorts at that step {ok/max(1,tot):.3f}")
        ad = [d for d in sett if d["age"] >= 180]
        print(f"    adults: cred med {med([d['cred'] for d in ad])} prow med {med([d['prow'] for d in ad])} last/need med {med([d['last']/d['need'] for d in ad])} g/need med {med([d['g']/d['need'] for d in ad])} wealth_pre/cap {med([1-d['d']/d['cap'] for d in ad])} cond {med([d['cond'] for d in ad])} ema {med([d['ema'] for d in ad])}")
        lo = [d for d in sett if d["left"] / (d["nn"] * 75000.0) < 1]
        print(f"    deaths with store left < 1 step per claimant: {len(lo)/max(1,len(sett)):.3f}; decile0 among them {sum(1 for d in lo if d['pct'] < 0.1)/max(1,len(lo)):.3f}")
