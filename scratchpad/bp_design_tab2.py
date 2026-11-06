import json, os
ROOT = r"C:\Users\syatom\Projects\SiC Games"
L = os.path.join(ROOT, "scratchpad", "design_logs")
def load(w, m, s):
    return [json.loads(l) for l in open(os.path.join(L, f"sig_dsig_{w}_m{m}_s{s}.jsonl"), encoding="utf-8")]
W = ["temperate", "montane", "savanna"]; M = ["10", "085", "070"]
D = {(w, m, s): load(w, m, s) for w in W for m in M for s in (0, 1)}
AG=[(0,1,"0"),(1,5,"1-4"),(5,10,"5-9"),(10,15,"10-14"),(15,25,"15-24"),(25,45,"25-44"),(45,100,"45+")]
def tot(r0,r1,key,a,b): return sum(r1[key][a:b])-sum(r0[key][a:b])
print("deaths and starvation in the shock year (index 35 to 47: steps 1799->1811) by age, sum over 6 runs: all / starv")
for (a,b,lab) in AG:
    row=[lab]
    for m in M:
        al=st=0
        for w in W:
            for s in (0,1):
                x=D[(w,m,s)]; al+=tot(x[35],x[47],"deaths",a,b); st+=tot(x[35],x[47],"starv",a,b)
        row.append(f"{m}: {al}/{st}")
    print(*row)
print("offline EMA on the fert factor per step (fert_factor diff / fert_n diff), area and two-year sum")
for w in W:
    for m in ("085","070"):
        cc=[];xx=[]
        for s in (0,1):
            for name,dst in (("10",cc),(m,xx)):
                r=D[(w,name,s)]
                f=[(r[i+1]["fert_factor"]-r[i]["fert_factor"])/max(1,r[i+1]["fert_n"]-r[i]["fert_n"]) for i in range(len(r)-1)]
                dst.append(f)
        c=[sum(v)/2 for v in zip(*cc)]; x=[sum(v)/2 for v in zip(*xx)]
        base=sum(c[:35])/35
        # area from 1800 on (index 35..71), in pct*yr of baseline
        area=sum(x[i]-c[i] for i in range(35,len(c)))/base/12*100
        out=[]
        for tau in (1.4,5,10,20):
            a=1/(tau*12)
            ec=ex=base; sc=sx=0
            for i in range(35,len(c)):
                ec+=a*(c[i]-ec); ex+=a*(x[i]-ex)
                if i<35+24: sc+=ec; sx+=ex
            out.append((tau,round((sx/sc-1)*100,2)))
        print(w,m,"base",round(base,3),"area %yr",round(area,1),"2yr pct under EMA:",out)
