"""Stage A diagnosis: the food account, the store, who starves, and the response to the shock, flag on against flag off."""
import json
import os

ROOT = r"C:\Users\syatom\Projects\SiC Games"
L = os.path.join(ROOT, "scratchpad", "design_logs")
W = ("temperate", "savanna", "montane")
S = (0, 1)


def jl(pre, tag):
    return [json.loads(x) for x in open(os.path.join(L, f"{pre}{tag}.jsonl"), encoding="utf-8")]


def m(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else float("nan")


ev = {}
for w in W:
    e = ev[w] = {}
    print(f"\n=== {w}: control window, years 2364-2400 before the onset (flag off -> on)")
    for fl in ("off", "on"):
        acc = [r for s in S for r in jl("acc", f"_vc_{w}_{fl}_c_s{s}") if r["step"] < 2400]
        sto = [r for s in S for r in jl("sto", f"_vc_{w}_{fl}_c_s{s}") if r["step"] < 2400]
        t = {k: sum(r[k] for r in acc) / len(acc) for k in ("need", "intake", "cap", "S_site", "S_oth", "heads")}
        sup = t["S_site"] + t["S_oth"]
        lean = [r for r in acc if r["step"] % 12 == 6]
        d = dict(supply=sup / t["cap"], intake=t["intake"] / t["cap"], need=t["need"] / t["cap"], need_sup=t["need"] / sup,
                 need_lean=sum(r["need"] for r in lean) / sum(r["cap"] for r in lean),
                 fill_pw=m([r["fill_pw"] for r in acc]), need_cap_med=m([r["need_cap_med"] for r in acc]), cells=m([r["cells_med"] for r in acc]),
                 store=m([r["all"]["sph_m"] for r in sto]), store_p10=m([r["all"]["sph_p10"] for r in sto]), sph0=m([r["all"]["sph0"] for r in sto]),
                 sfull=m([r["all"]["sfull"] for r in sto]), v_sup_p10=m([r["v_sup_p10"] for r in sto]), v_sup_p50=m([r["v_sup_p50"] for r in sto]), raw_w=m([r["raw_lt1_w"] for r in sto]),
                 mobile=m([r["all"]["mobile"] for r in sto]), child_mobile=m([r["C"]["mobile"] for r in sto]))
        e[fl] = d
        print(f"  {fl}: " + " ".join(f"{k}={v:.2f}" for k, v in d.items()))
    print("  Starvation deaths per year in the control, whole logged window 2364-3000:")
    for fl in ("off", "on"):
        dd = [dict(x) for s in S for r in jl("sto", f"_vc_{w}_{fl}_c_s{s}") for x in r["dead"]]
        yrs = 2 * 636 / 12
        kid = [x for x in dd if 12 <= x["age"] < 120]
        ad = [x for x in dd if 180 <= x["age"] < 540]
        inf = [x for x in dd if x["age"] < 12]
        juv = [x for x in dd if 120 <= x["age"] < 180]
        o = dict(all=len(dd) / yrs, settled=sum(1 for x in dd if not x["mob"]) / yrs, mobile=sum(x["mob"] for x in dd) / yrs,
                 inf=len(inf) / yrs, kid=len(kid) / yrs, juv=len(juv) / yrs, adult=len(ad) / yrs,
                 adult_settled=sum(1 for x in ad if not x["mob"]) / yrs, kid_settled=sum(1 for x in kid if not x["mob"]) / yrs,
                 settled_sph_lt1=m([1.0 if x["sph"] < 1 else 0.0 for x in dd if not x["mob"]]),
                 settled_sph_med=sorted(x["sph"] for x in dd if not x["mob"])[len([x for x in dd if not x["mob"]]) // 2] if any(not x["mob"] for x in dd) else None,
                 settled_fill=m([x["fill"] for x in dd if not x["mob"]]))
        e[fl + "_starv"] = o
        print(f"    {fl}: " + " ".join(f"{k}={v:.2f}" if v is not None else f"{k}=None" for k, v in o.items()))
    print("  Shock response, flag on, arm / control:")
    c = {s: jl("sig", f"_vc_{w}_on_c_s{s}") for s in S}
    cs = {s: jl("sto", f"_vc_{w}_on_c_s{s}") for s in S}
    for a, ln in (("y1", 12), ("y5", 60)):
        x = {s: jl("sig", f"_vc_{w}_on_{a}_s{s}") for s in S}
        xs = {s: jl("sto", f"_vc_{w}_on_{a}_s{s}") for s in S}
        i0 = 36
        for name, lo, hi in (("yr1", 0, 12), ("yr2", 12, 24), ("yr3-5", 24, 60), ("yr6-10", 60, 120), ("yr11-20", 120, 240)):
            bc = sum(r["births"] for s in S for r in c[s][i0 + lo:i0 + hi])
            bx = sum(r["births"] for s in S for r in x[s][i0 + lo:i0 + hi])
            diff = lambda run, k, lo_a, hi_a: sum((run[s][i0 + hi - 1][k][q] - run[s][i0 + lo - 1][k][q]) for s in S for q in range(lo_a, hi_a))
            dc = diff(c, "deaths", 1, 10)
            dx = diff(x, "deaths", 1, 10)
            ac = diff(c, "deaths", 15, 45)
            ax = diff(x, "deaths", 15, 45)
            sc = sum(sum(c[s][i0 + hi - 1]["starv"]) - sum(c[s][i0 + lo - 1]["starv"]) for s in S)
            sx = sum(sum(x[s][i0 + hi - 1]["starv"]) - sum(x[s][i0 + lo - 1]["starv"]) for s in S)
            pc = m([c[s][i0 + hi - 1]["pop"] for s in S])
            px = m([x[s][i0 + hi - 1]["pop"] for s in S])
            st = m([r["all"]["sph_m"] for s in S for r in xs[s][i0 + lo:i0 + hi]])
            stc = m([r["all"]["sph_m"] for s in S for r in cs[s][i0 + lo:i0 + hi]])
            print(f"    {a} {name:7s} births {bx}/{bc} deaths1-9 {dx}/{dc} deaths15-44 {ax}/{ac} starv {sx}/{sc} pop {px:.0f}/{pc:.0f} store {st:.1f}/{stc:.1f}")
json.dump(ev, open(os.path.join(ROOT, "docs", "evidence", "add129_diag.json"), "w", encoding="utf-8"), indent=1)
