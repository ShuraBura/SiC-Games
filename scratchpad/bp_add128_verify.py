"""Check the numbers quoted in Add.128 against the logs, and write the evidence file."""
import json, os
ROOT = r"C:\Users\syatom\Projects\SiC Games"
L = os.path.join(ROOT, "scratchpad", "design_logs")
W = ("temperate", "savanna", "montane")
ev = {}
def jl(p):
    return [json.loads(l) for l in open(os.path.join(L, p), encoding="utf-8")]
for w in W:
    e = ev[w] = {}
    sig = {m: [jl(f"sig_dsig_{w}_m{m}_s{s}.jsonl") for s in (0, 1)] for m in ("10", "085", "070")}
    sto = {a: [jl(f"sto_dsto_{w}_{a}_s{s}.jsonl") for s in (0, 1)] for a in ("c", "y1", "y5")}
    acc = jl(f"acc_dacc_{w}_s0.jsonl") + jl(f"acc_dacc_{w}_s1.jsonl")
    yr = lambda runs, g, k, i0, i1: sum((r[g][k] if g else r[k]) for x in runs for r in x[i0:i1]) / sum(len(x[i0:i1]) for x in runs)
    e["m_ema_shockyear_control"] = yr(sig["10"], None, "m_ema", 36, 48)
    e["m_ema_p10_control"] = yr(sig["10"], None, "m_ema_p10", 36, 48)
    e["m_ema_change_070_pct"] = (yr(sig["070"], None, "m_ema", 36, 48) / e["m_ema_shockyear_control"] - 1) * 100
    for k in ("fill_m", "fd_m", "raw_p50", "f_int_m"):
        e[f"W_{k}_change_070_pct"] = (yr(sig["070"], "W", k, 36, 48) / yr(sig["10"], "W", k, 36, 48) - 1) * 100
    e["W_ema_p50_control"] = yr(sig["10"], "W", "ema_p50", 0, 36)
    e["W_f_int_control"] = yr(sig["10"], "W", "f_int_m", 0, 36)
    e["W_unfed_control"], e["W_unfed_070"] = yr(sig["10"], "W", "unfed_m", 36, 48), yr(sig["070"], "W", "unfed_m", 36, 48)
    e["store_control"] = yr(sto["c"], "all", "sph_m", 0, 36)
    e["store_y5_year4"] = yr(sto["y5"], "all", "sph_m", 36 + 48, 36 + 60)
    e["sfull_control"] = yr(sto["c"], "all", "sfull", 0, 36)
    e["v_sup_control"] = yr(sto["c"], None, "v_sup_p50", 0, 36)
    e["v_sup_y5"] = yr(sto["y5"], None, "v_sup_p50", 36, 96)
    e["child_mobile_control"] = yr(sto["c"], "C", "mobile", 0, 121)
    dd = [d for x in sto["c"] for r in x for d in r["dead"] if 12 <= d["age"] < 120]
    e["starved_children_n"] = len(dd)
    e["starved_children_outside"] = sum(d["mob"] for d in dd) / len(dd)
    out = [d for d in dd if d["mob"]]
    e["starved_outside_no_mother"] = 1 - sum(d["mom"] for d in out) / len(out)
    n = len(acc)
    t = {k: sum(r[k] for r in acc) / n for k in ("need", "intake", "cap", "sum25", "S_site", "S_oth", "lev_oth")}
    e["account"] = dict(site=t["S_site"] / t["cap"], other_yield=t["lev_oth"] / t["cap"], bonus=(t["S_oth"] - t["lev_oth"]) / t["cap"],
                        supply=(t["S_site"] + t["S_oth"]) / t["cap"], intake=t["intake"] / t["cap"], need=t["need"] / t["cap"],
                        need_supply=t["need"] / (t["S_site"] + t["S_oth"]), sum25=t["sum25"] / t["cap"], fill_pw=sum(r["fill_pw"] for r in acc) / n,
                        cells_med=sum(r["cells_med"] for r in acc) / n)
    lean = [r for r in acc if r["step"] % 12 == 6]
    e["account"]["need_lean"] = sum(r["need"] for r in lean) / sum(r["cap"] for r in lean)
    settled = {a: sum(1 for x in sto[a] for r in x[36:48] for d in r["dead"] if not d["mob"]) for a in ("c", "y1")}
    e["settled_starv_shockyear"] = settled
    e["settled_starv_sph_lt1_y1"] = sum(1 for x in sto["y1"] for r in x[36:48] for d in r["dead"] if not d["mob"] and d["sph"] < 1)
# per-10% birth response under an EMA of the fertility factor
for w in W:
    res = {}
    for m, mv in (("085", .85), ("070", .70)):
        cc, xx = [], []
        for s in (0, 1):
            for name, dst in (("10", cc), (m, xx)):
                r = jl(f"sig_dsig_{w}_m{name}_s{s}.jsonl")
                dst.append([(r[i + 1]["fert_factor"] - r[i]["fert_factor"]) / max(1, r[i + 1]["fert_n"] - r[i]["fert_n"]) for i in range(len(r) - 1)])
        c = [sum(v) / 2 for v in zip(*cc)]
        x = [sum(v) / 2 for v in zip(*xx)]
        base = sum(c[:35]) / 35
        o = {}
        import math
        for tau in (1.4, 5, 10, 20):
            a = 1 / (tau * 12)
            ec = ex = base
            sc = sx = 0
            for i in range(35, len(c)):
                ec += a * (c[i] - ec)
                ex += a * (x[i] - ex)
                if i < 35 + 24:
                    sc += ec
                    sx += ex
            r2 = sx / sc
            o[str(tau)] = round((0.9 ** (math.log(r2) / math.log(mv)) - 1) * 100, 2)
        res[m] = o
    ev[w]["ema_birth_response_per_10pct"] = res
json.dump(ev, open(os.path.join(ROOT, "docs", "evidence", "add128_measurement.json"), "w", encoding="utf-8"), indent=1)
print(json.dumps(ev, indent=0))
