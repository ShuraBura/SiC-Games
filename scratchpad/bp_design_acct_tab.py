import json, os
ROOT = r"C:\Users\syatom\Projects\SiC Games"
L = os.path.join(ROOT, "scratchpad", "design_logs")
W = ["temperate", "montane", "savanna"]
for w in W:
    rows = []
    for s in (0, 1):
        f = os.path.join(L, f"acc_dacc_{w}_s{s}.jsonl")
        rs = [json.loads(l) for l in open(f, encoding="utf-8")]
        print(w, s, "rows", len(rs), "pop", rs[0]["pop"], rs[-1]["pop"], "villages", rs[0]["n_v"], "cells_med", rs[0]["cells_med"])
        rows += rs
    n = len(rows)
    t = {k: sum(r[k] for r in rows) / n for k in ("need", "intake", "cap", "sum25", "S_site", "S_oth", "lev_oth", "heads")}
    print(" annual mean per step, ratios to cap:", {k: round(t[k] / t["cap"], 3) for k in ("need", "intake", "sum25", "S_site", "S_oth", "lev_oth")})
    print(" need/supply", round(t["need"] / (t["S_site"] + t["S_oth"]), 3), "intake/supply", round(t["intake"] / (t["S_site"] + t["S_oth"]), 3), "need per head / burn-equivalent")
    print(" medians: need_cap", round(sum(r["need_cap_med"] for r in rows) / n, 3), "sup_cap", round(sum(r["sup_cap_med"] for r in rows) / n, 3), "fill_med", round(sum(r["fill_med"] for r in rows) / n, 3), "fill_pw", round(sum(r["fill_pw"] for r in rows) / n, 3), "cells", round(sum(r["cells_med"] for r in rows) / n, 1))
    m = sum(r["mob"]["heads"] for r in rows) / n
    print(" mobile heads", round(m), "need/intake mobile", round(sum(r["mob"]["need"] for r in rows) / max(1e-9, sum(r["mob"]["intake"] for r in rows)), 3))
    print(" month: need/cap(sum), sup/cap, fill_pw")
    for mo in range(12):
        rr = [r for r in rows if r["step"] % 12 == mo]
        nn = sum(r["need"] for r in rr); c = sum(r["cap"] for r in rr); sp = sum(r["S_site"] + r["S_oth"] for r in rr)
        print("  ", mo, round(nn / c, 3), round(sp / c, 3), round(sum(r["fill_pw"] for r in rr) / len(rr), 3))
