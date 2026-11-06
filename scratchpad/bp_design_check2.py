import json, glob, os
ROOT = r"C:\Users\syatom\Projects\SiC Games"
L = os.path.join(ROOT, "scratchpad", "design_logs")
def load(w, m, s):
    return [json.loads(l) for l in open(os.path.join(L, f"sig_dsig_{w}_m{m}_s{s}.jsonl"), encoding="utf-8")]
W = ["temperate", "montane", "savanna"]
for w in W:
    for s in (0, 1):
        fs = glob.glob(os.path.join(ROOT, "sic_games", "outputs", "**", f"campaign_trajectory_s2_{w}_pair_s{s}.json"), recursive=True)
        d = json.load(open(fs[0], encoding="utf-8")); tr = d["traj"]
        if isinstance(tr, dict):
            print(list(tr.keys())[:8]); 
        c = {r["step"]: r for r in load(w,"10",s)}
        print(w, s, type(tr), len(tr), list(tr[0].keys())[:8] if isinstance(tr,list) else "")
        key = [k for k in tr[0] if k in ("step","t")][0]
        pk = [k for k in tr[0] if k in ("pop","n_agents","population","N","n")]
        print("  key", key, pk, [(r[key], r[pk[0]], c[r[key]]["pop"]) for r in tr if r[key] in c][:5])
