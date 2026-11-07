"""Add.130: read the per-village log against the predictions in add130_predictions.md. Window: steps 1800-3000. Writes docs/evidence/add130_measurement.json."""
import json
import os

ROOT = r"C:\Users\syatom\Projects\SiC Games"
L = os.path.join(ROOT, "scratchpad", "design_logs")
O = os.path.join(ROOT, "sic_games", "outputs", "substrate_run")
W = ("temperate", "savanna", "montane")
S = (0, 1)
AD = 180


def jl(pre, tag):
    return [json.loads(x) for x in open(os.path.join(L, f"{pre}{tag}.jsonl"), encoding="utf-8")]


def med(xs):
    xs = sorted(x for x in xs if x is not None)
    return xs[len(xs) // 2] if xs else None


def mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


def rank(xs):
    o = sorted(range(len(xs)), key=lambda i: xs[i])
    r = [0.0] * len(xs)
    i = 0
    while i < len(o):
        j = i
        while j + 1 < len(o) and xs[o[j + 1]] == xs[o[i]]:
            j += 1
        for k in range(i, j + 1):
            r[o[k]] = (i + j) / 2.0
        i = j + 1
    return r


def spearman(a, b):
    ra, rb = rank(a), rank(b)
    n = len(ra)
    ma, mb = sum(ra) / n, sum(rb) / n
    c = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    va = sum((x - ma) ** 2 for x in ra)
    vb = sum((y - mb) ** 2 for y in rb)
    return c / (va * vb) ** 0.5 if va > 0 and vb > 0 else None


def fmt(v):
    return "None" if v is None else (f"{v:.3f}" if isinstance(v, float) else str(v))


out = {}
print("=== controls")
for w in W:
    for fl in ("off", "on"):
        for s in S:
            tag = f"_vl_{w}_{fl}_s{s}"
            a = json.load(open(os.path.join(O, f"campaign_trajectory{tag}.json"), encoding="utf-8"))["traj"]
            b = {r["step"]: r for r in json.load(open(os.path.join(O, f"campaign_trajectory_vc_{w}_{fl}_c_s{s}.json"), encoding="utf-8"))["traj"]}
            diff = sum(1 for r in a if any(r.get(k) != b[r["step"]].get(k) for k in ("pop", "births", "deaths_starv", "n_settle", "gini_cred")))
            c = jl("chk", tag)
            print(f"{w} {fl} s{s}: C1 rows {len(a)} different {diff} | C2 ds {sum(r['ds'] for r in c)} logged {sum(r['logged'] for r in c)} bad steps {sum(r['ds'] != r['logged'] for r in c)} | C3 bad steps {sum(r['births'] != r['nb'] for r in c)} {sum(r['ds'] + r['dn'] != r['ng'] for r in c)}")

for w in W:
    e = out[w] = {}
    for fl in ("off", "on"):
        D, V, G = [], [], None
        for s in S:
            tag = f"_vl_{w}_{fl}_s{s}"
            D += jl("dth", tag)
            V += [dict(r, seed=s) for r in jl("vlg", tag) if r["n"] >= 6]
            g = json.load(open(os.path.join(L, f"grd{tag}.json"), encoding="utf-8"))
            if G is None:
                G = g
            else:
                for k in ("pgrid", "short"):
                    for a in range(2):
                        for c in range(4):
                            for i in range(10):
                                G[k][a][c][i] += g[k][a][c][i]
        yrs = 2 * 100.0
        sett = [d for d in D if d["s"] is not None]
        mob = [d for d in D if d["s"] is None]
        ad = [d for d in sett if AD <= d["age"]]
        ya = [d for d in sett if 180 <= d["age"] < 312]
        ch = [d for d in sett if d["age"] < 180]
        strand = lambda d: d["left"] >= d["short"]
        indraw = [d for d in sett if d["inq"]]
        o = e[fl] = dict(starv_yr=len(D) / yrs, settled_yr=len(sett) / yrs, mobile_yr=len(mob) / yrs, adults_yr=len(ad) / yrs, kids_yr=len(ch) / yrs,
                         share_strand_all=mean([1.0 if strand(d) else 0.0 for d in sett]), share_strand_ad=mean([1.0 if strand(d) else 0.0 for d in ad]), share_strand_ch=mean([1.0 if strand(d) else 0.0 for d in ch]),
                         not_in_draw=mean([0.0 if d["inq"] else 1.0 for d in sett]), full_draw=mean([1.0 if d["g"] >= d["d"] * 0.999 else 0.0 for d in indraw]),
                         pct_strand_ad=med([d["pct"] for d in ad if strand(d)]), pct_ad=med([d["pct"] for d in ad]), pct_ya=med([d["pct"] for d in ya]), pct_ch=med([d["pct"] for d in ch]),
                         share_equal=med([d["sh"] for d in ad if strand(d)]), kap=med([d["kap"] for d in indraw]), short_steps=med([d["short"] / d["need"] for d in ad]),
                         left_steps=med([d["left"] / (d["nn"] * 75000.0) for d in indraw]), dep_ad=mean([1.0 if d["dep"] else 0.0 for d in ad]), female_ad=mean([1.0 if d["sex"] == "female" else 0.0 for d in ad]))
        hungry = [v for v in V if v["sph_min"] < 1.0]
        fed = [v for v in V if v["sph_min"] >= 1.0]
        rate = lambda vs, k: sum(sum(v[x] for x in k) for v in vs) / max(1.0, sum(v["heads"] for v in vs))
        sr = [(v["ds_inf"] + v["ds_ch"] + v["ds_ad"]) / max(1.0, v["heads"]) for v in V]
        hd = [v["hard"] for v in V]
        o.update(vy=len(V), hungry_vy=len(hungry), hungry_share=len(hungry) / max(1, len(V)), starv_in_hungry=sum(v["ds_inf"] + v["ds_ch"] + v["ds_ad"] for v in hungry) / max(1, sum(v["ds_inf"] + v["ds_ch"] + v["ds_ad"] for v in V)),
                 hard_rho=spearman(hd, sr), hard_h=mean([v["hard"] for v in hungry]), hard_f=mean([v["hard"] for v in fed]), ss_h=mean([v["ss"] for v in hungry]), ss_f=mean([v["ss"] for v in fed]),
                 soil_h=mean([v["soil"] for v in hungry]), soil_f=mean([v["soil"] for v in fed]),
                 out_h=rate(hungry, ("out_mob", "out_vil")), out_f=rate(fed, ("out_mob", "out_vil")), outm_h=rate(hungry, ("out_mob",)), outm_f=rate(fed, ("out_mob",)), diss_h=rate(hungry, ("out_diss",)), diss_f=rate(fed, ("out_diss",)),
                 nc_lean_gt1=mean([1.0 if (v["nc_lean"] or 0) > 1 else 0.0 for v in hungry]), ncmax_gt1=mean([1.0 if v["nc_max"] > 1 else 0.0 for v in hungry]), nc_h=med([v["need"] / v["cap"] for v in hungry if v["cap"]]), nc_f=med([v["need"] / v["cap"] for v in fed if v["cap"]]),
                 heads_h=med([v["heads"] for v in hungry]), heads_f=med([v["heads"] for v in fed]), age_h=med([v["age"] for v in hungry]), age_f=med([v["age"] for v in fed]), fk_h=med([v["fk"] for v in hungry]), fk_f=med([v["fk"] for v in fed]), land_h=med([v["land"] for v in hungry]), land_f=med([v["land"] for v in fed]),
                 capcv_h=med([(v["cap_max"] - v["cap_min"]) / v["cap"] for v in hungry if v["cap"]]), capcv_f=med([(v["cap_max"] - v["cap_min"]) / v["cap"] for v in fed if v["cap"]]),
                 pc_lean_h=med([v["pc_lean"] for v in hungry]), alt_h=med([max(v["alt"]["lean"].values()) if "lean" in v["alt"] else None for v in hungry]), pc_lean_f=med([v["pc_lean"] for v in fed]), alt_f=med([max(v["alt"]["lean"].values()) if "lean" in v["alt"] else None for v in fed]),
                 alt_better_h=mean([1.0 if ("lean" in v["alt"] and max(v["alt"]["lean"].values()) > v["pc_lean"]) else 0.0 for v in hungry]), stranded_steps=sum(v["stranded"] for v in V) / max(1, sum(v["heads"] * v["n"] for v in V)))
        ex = []
        for cl in range(4):
            ex.append([G["pgrid"][1][cl][i] for i in range(10)])
        dth = [[0] * 10 for _ in range(4)]
        for d in indraw:
            if d["pct"] is None:
                continue
            cl = 0 if d["age"] < 180 else (1 if d["age"] < 312 else (2 if d["age"] < 552 else 3))
            dth[cl][min(9, int(10 * d["pct"]))] += 1
        o["hazard"] = [[dth[c][i] / ex[c][i] * 12000 if ex[c][i] else None for i in range(10)] for c in range(4)]
        o["exposure"] = ex
        o["deaths_grid"] = dth
        tot = sum(sum(r) for r in ex)
        cum = 0
        ml = None
        all_d = [sum(ex[c][i] for c in range(4)) for i in range(10)]
        for i in range(10):
            cum += all_d[i]
            if ml is None and cum >= tot / 2:
                ml = i
        o["null_median_decile"] = ml
        print(f"\n=== {w} {fl}")
        print("  " + " ".join(f"{k}={fmt(v)}" for k, v in o.items() if k not in ("hazard", "exposure", "deaths_grid")))
        for c, nm in enumerate(("<15", "15-25", "26-45", "46+")):
            print(f"  hazard /1000 yr by status decile, {nm}: " + " ".join("-" if x is None else f"{x:.0f}" for x in o["hazard"][c]) + f"  (deaths {sum(dth[c])})")
json.dump(out, open(os.path.join(ROOT, "docs", "evidence", "add130_measurement.json"), "w", encoding="utf-8"), indent=1)
