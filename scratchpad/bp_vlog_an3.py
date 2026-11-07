"""Add.130 third reading: join the banking gate to the village log. Does the gate pick the hungry villages?"""
import json
import os

import numpy as np

ROOT = r"C:\Users\syatom\Projects\SiC Games"
L = os.path.join(ROOT, "scratchpad", "design_logs")
W = ("temperate", "savanna", "montane")
out = {}
for w in W:
    z = np.load(os.path.join(L, f"owz_vz_{w}.npz"))
    gate = (z["temperature"] <= float(z["tthr"])) | (z["amp"] >= float(z["athr"]))
    land = z["water"] == 0
    print(f"\n=== {w}: union {z['union']} seas {z['seas']} tthr {z['tthr']} athr {z['athr']}; land cells with gate open {gate[land].mean():.3f}")
    u, c = np.unique(z["biome"][land], return_counts=True)
    print("  biome: " + " ".join(f"{int(b)}:{n} open={gate[land & (z['biome'] == b)].mean():.2f} amp={z['amp'][land & (z['biome'] == b)].mean():.2f}" for b, n in zip(u, c)))
    for fl in ("off", "on"):
        V, D = [], []
        for s in (0, 1):
            tag = f"_vl_{w}_{fl}_s{s}"
            V += [json.loads(x) for x in open(os.path.join(L, f"vlg{tag}.jsonl"), encoding="utf-8")]
            D += [json.loads(x) for x in open(os.path.join(L, f"dth{tag}.jsonl"), encoding="utf-8")]
        V = [v for v in V if v["n"] >= 6]
        rows = {}
        for g in (True, False):
            vs = [v for v in V if bool(gate[v["s"][1], v["s"][0]]) == g]
            dd = [d for d in D if d["s"] is not None and bool(gate[d["s"][1], d["s"][0]]) == g]
            if not vs:
                print(f"  {fl} gate {'open' if g else 'shut'}: no village-years")
                continue
            h = sum(v["heads"] for v in vs)
            st = sum(v["ds_inf"] + v["ds_ch"] + v["ds_ad"] for v in vs)
            sd = sorted(v["sph"] for v in vs)
            r = rows["open" if g else "shut"] = dict(vy=len(vs), heads=h, person_share=h / sum(v["heads"] for v in V), hungry=sum(1 for v in vs if v["sph_min"] < 1) / len(vs), sph_med=sd[len(sd) // 2], starv_rate=st / max(1.0, h), starv_share=st / max(1, sum(v["ds_inf"] + v["ds_ch"] + v["ds_ad"] for v in V)),
                                                     kid_rate=sum(v["ds_ch"] for v in vs) / max(1.0, h), born=sum(v["born"] for v in vs) / max(1.0, h), intake_need=sum(v["intake"] for v in vs) / max(1.0, sum(v["need"] for v in vs)), heads_med=sorted(v["heads"] for v in vs)[len(vs) // 2],
                                                     strand_ad=np.mean([d["left"] >= d["short"] for d in dd if d["age"] >= 180]) if dd else None, in_rate=sum(v["in_mob"] + v["in_vil"] for v in vs) / max(1.0, h), out_rate=sum(v["out_mob"] + v["out_vil"] for v in vs) / max(1.0, h))
            print(f"  {fl} gate {'open' if g else 'shut'}: " + " ".join(f"{k}={v:.3f}" if v is not None else f"{k}=None" for k, v in r.items()))
        out[f"{w}_{fl}"] = rows
json.dump(out, open(os.path.join(ROOT, "docs", "evidence", "add130_gate.json"), "w", encoding="utf-8"), indent=1, default=float)
