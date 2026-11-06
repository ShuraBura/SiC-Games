import json, os
ROOT = r"C:\Users\syatom\Projects\SiC Games"
L = os.path.join(ROOT, "scratchpad", "design_logs")
W = ["temperate", "montane", "savanna"]; A = ["c", "y1", "y5"]
def load(w, a, s):
    return [json.loads(l) for l in open(os.path.join(L, f"sto_dsto_{w}_{a}_s{s}.jsonl"), encoding="utf-8")]
D = {(w, a, s): load(w, a, s) for w in W for a in A for s in (0, 1)}
print("rows", {len(v) for v in D.values()}, D[("savanna","c",0)][0]["step"], D[("savanna","c",0)][-1]["step"], "capsteps", D[("savanna","c",0)][0]["capsteps"])
# pairing with the first run: control pop
for w in W:
    for s in (0, 1):
        f = [json.loads(l) for l in open(os.path.join(L, f"sig_dsig_{w}_m10_s{s}.jsonl"), encoding="utf-8")]
        c = D[(w, "c", s)]
        same = all(a["pop"] == b["pop"] and a["births"] == b["births"] for a, b in zip(f, c))
        print(w, s, "control equals first run:", same, "arms first differ:", [next((x["step"] for x, y in zip(c, D[(w, a, s)]) if x["pop"] != y["pop"] or x["births"] != y["births"]), None) for a in ("y1", "y5")])
def v(w, a, g, k, i0, i1):
    t = []
    for s in (0, 1):
        for r in D[(w, a, s)][i0:i1]:
            x = r[g][k] if g else r[k]
            if x is not None: t.append(x)
    return sum(t)/len(t) if t else float("nan")
print("== control 3 yr")
for w in W:
    print(w, {k: round(v(w,"c","all",k,0,36),3) for k in ("n","mobile","sph_m","sph_p10","sph_p50","sph_p90","sph0","sfull")},
          "C", {k: round(v(w,"c","C",k,0,36),3) for k in ("mobile","sph_m","sph_p10","sph_p50","sph0","sfull")},
          "v", {k: round(v(w,"c",None,k,0,36),3) for k in ("v_n","v_sph_p10","v_sph_p50","v_sph_p90","v_sup_p10","v_sup_p50","raw_lt1_w","raw_lt1_m")})
print("== season, control: month, all sph_m sph_p50 sph0 v_sup_p50 v_sup_p10")
for w in W:
    print(w)
    for mo in range(12):
        rows = [r for s in (0,1) for r in D[(w,"c",s)][:36] if r["step"] % 12 == mo]
        print(mo, *[round(sum(r["all"][k] for r in rows)/len(rows),3) for k in ("sph_m","sph_p50","sph_p10","sph0","sfull")], *[round(sum(r[k] for r in rows)/len(rows),3) for k in ("v_sup_p50","v_sup_p10","raw_lt1_w","raw_lt1_m")])
print("== response by year: all.sph_m, all.sph_p10, all.sph0, C.sph0, v_sup_p50, raw_lt1_m")
for w in W:
    for a in A:
        out = []
        for y in range(-1, 7):
            i0 = 36 + 12*y; i1 = i0 + 12
            if i0 < 0 or i1 > 121: continue
            out.append((y, round(v(w,a,"all","sph_m",i0,i1),2), round(v(w,a,"all","sph_p10",i0,i1),2), round(v(w,a,"all","sph0",i0,i1),3), round(v(w,a,"C","sph0",i0,i1),3), round(v(w,a,None,"v_sup_p50",i0,i1),2), round(v(w,a,None,"raw_lt1_m",i0,i1),3)))
        print(w, a, out)
print("== starvation deaths by year: n, share mobile, share age<15, share with sph<1, mean fill")
for w in W:
    for a in A:
        out = []
        for y in range(-3, 7):
            i0 = 36 + 12*y; i1 = i0 + 12
            if i0 < 0 or i1 > 121: continue
            dd = [d for s in (0,1) for r in D[(w,a,s)][i0:i1] for d in r["dead"]]
            n = len(dd)
            if not n: out.append((y,0)); continue
            sett = [d for d in dd if not d["mob"]]
            out.append((y, n, round(sum(d["mob"] for d in dd)/n,2), round(sum(1 for d in dd if d["age"]<180)/n,2), round(sum(1 for d in sett if d["sph"]<1)/max(1,len(sett)),2)))
        print(w, a, out)
print("== settled child starvation, control vs y1 vs y5")
for w in W:
    for a in A:
        dd = [d for s in (0,1) for r in D[(w,a,s)][36:] for d in r["dead"]]
        ch = [d for d in dd if 12 <= d["age"] < 120]
        print(w, a, "all", len(dd), "age1-9", len(ch), "mobile", sum(d["mob"] for d in ch), "mom alive", sum(d["mom"] for d in ch), "sph<1 settled", sum(1 for d in ch if not d["mob"] and d["sph"]<1))
