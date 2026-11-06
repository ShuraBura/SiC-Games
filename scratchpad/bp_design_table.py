import json, os, statistics as st
ROOT = r"C:\Users\syatom\Projects\SiC Games"
L = os.path.join(ROOT, "scratchpad", "design_logs")
def load(w, m, s):
    return [json.loads(l) for l in open(os.path.join(L, f"sig_dsig_{w}_m{m}_s{s}.jsonl"), encoding="utf-8")]
W = ["temperate", "montane", "savanna"]; M = ["10", "085", "070"]
D = {(w, m, s): load(w, m, s) for w in W for m in M for s in (0, 1)}
def avg(rows, g, k):
    v=[r[g][k] for r in rows if r[g].get(k) is not None]
    return sum(v)/len(v) if v else float('nan')
print("== control, 1764-1799 (3 yr), women at risk: by world (mean over 2 seeds)")
keys=["n","fill_m","fill_p10","fill_p50","fill_p90","fill_gt1","fd_m","fd_ann_m","f_int_m","f_fd","ema_p10","ema_p50","ema_m","raw_p10","raw_p50","cond_m","unfed_m","fed_m","fed_p10","trough_m","trough_p10","trough_p01"]
for w in W:
    print(w, {k: round(sum(avg(D[(w,"10",s)][:36],"W",k) for s in (0,1))/2,3) for k in keys})
print("== control, by month of year, women at risk, temperate s0+s1: fill_m fd_m fd_ann f_int births")
for w in W:
    print(w)
    for mo in range(12):
        rows=[r for s in (0,1) for r in D[(w,"10",s)][:36] if r["step"]%12==mo]
        print(mo, *[round(sum(r["W"][k] for r in rows)/len(rows),3) for k in ("fill_m","fd_m","fd_ann_m","f_int_m","ema_p10","fill_gt1","trough_m","trough_p10")], round(sum(r["births"] for r in rows)/len(rows),1))
print("== response in shock year 1800-1811 vs paired control, ratio of means")
def R(w,m,g,k):
    a=[avg(D[(w,m,s)][36:48],g,k) for s in (0,1)]; b=[avg(D[(w,"10",s)][36:48],g,k) for s in (0,1)]
    return sum(a)/2, sum(b)/2
for g,keys2 in (("W",["fill_m","fd_m","fd_ann_m","f_int_m","ema_p10","raw_p50","raw_p10","cond_m","fed_m","fed_p10","trough_m","trough_p10","trough_p01","unfed_m"]),("C",["fill_m","fd_m","raw_m","raw_p50","raw_p10","cond_m","fed_m","fed_p10","trough_m","trough_p10","trough_p01"]),("A",["raw_p50","raw_p10","cond_m","fed_m","fed_p10","trough_m","trough_p10","trough_p01","ema_p10","f_int_m"])):
    print("--",g)
    for k in keys2:
        print(k.ljust(11), *[ "%s c=%.3f 085=%.3f 070=%.3f |"%(w[:4],R(w,"10",g,k)[1],R(w,"085",g,k)[0],R(w,"070",g,k)[0]) for w in W])
print("-- child mother signal")
for k in ("m_ema","m_ema_p10","m_unfed"):
    for w in W:
        print(k,w,*[round(sum(sum(r[k] for r in D[(w,m,s)][36:48])/12 for s in (0,1))/2,3) for m in M])
