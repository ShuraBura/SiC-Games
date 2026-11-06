"""Instrument checks of the signal measurement, then a first table."""
import json, glob, os
ROOT = r"C:\Users\syatom\Projects\SiC Games"
L = os.path.join(ROOT, "scratchpad", "design_logs")
def load(w, m, s):
    return [json.loads(l) for l in open(os.path.join(L, f"sig_dsig_{w}_m{m}_s{s}.jsonl"), encoding="utf-8")]
W = ["temperate", "montane", "savanna"]; M = ["10", "085", "070"]
D = {(w, m, s): load(w, m, s) for w in W for m in M for s in (0, 1)}
print("rows", {len(v) for v in D.values()}, "first/last", D[("temperate","10",0)][0]["step"], D[("temperate","10",0)][-1]["step"])
# 1 arms identical before the onset
ok = 0
for w in W:
    for s in (0, 1):
        c = D[(w,"10",s)]
        for m in ("085","070"):
            x = D[(w,m,s)]
            first = next((a["step"] for a, b in zip(c, x) if {k:v for k,v in a.items()} != b), None)
            print(w, s, m, "first difference at step", first)
# 2 stored run
for w in W:
    for s in (0, 1):
        p = os.path.join(ROOT, "sic_games", "outputs", "substrate_run")
        fs = glob.glob(os.path.join(p, "**", f"campaign_trajectory_s2_{w}_pair_s{s}.json"), recursive=True)
        if not fs:
            print("no stored", w, s); continue
        d = json.load(open(fs[0], encoding="utf-8"))
        rows = d if isinstance(d, list) else d.get("trajectory") or d.get("rows") or d
        if isinstance(rows, dict):
            print(list(rows.keys())[:20]); continue
        got = []
        c = {r["step"]: r for r in D[(w,"10",s)]}
        for r in rows:
            st = r.get("step")
            if st in c:
                got.append((st, r.get("pop", r.get("n_agents", r.get("population"))), c[st]["pop"]))
        print("stored", w, s, got[:6])
# 3 births at first shocked steps
for w in W:
    for s in (0, 1):
        print(w, s, [(st, [D[(w,m,s)][st-1764]["births"] for m in M]) for st in (1797,1798,1799,1800,1801)])
