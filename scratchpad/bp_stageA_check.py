import json, math
O="sic_games/outputs/substrate_run/campaign_trajectory"
L="scratchpad/design_logs/"
ev={}
for w in ("temperate","savanna","montane"):
    v={}
    for fl in ("off","on"):
        p=[]
        for s in (0,1):
            t=json.load(open(f"{O}_vc_{w}_{fl}_c_s{s}.json"))["traj"]
            r=[x["pop"] for x in t if 1800<=x["step"]<=3000]
            p.append(sum(r)/len(r))
        v[fl]=p
    print(w,"pop per seed", {k:[round(x) for x in q] for k,q in v.items()}, "pct by seed",[round((a/b-1)*100) for a,b in zip(v["on"],v["off"])], "pct of means", round((sum(v["on"])/sum(v["off"])-1)*100))
    jl=lambda a,s:[json.loads(x) for x in open(f"{L}sig_vc_{w}_on_{a}_s{s}.jsonl")]
    c=[jl("c",s) for s in (0,1)]; x=[jl("y5",s) for s in (0,1)]
    e={}
    for nm,lo,hi in (("d1_9",1,10),("d15_44",15,45)):
        cc=sum(sum(r[60][lo:hi])-sum(r[36][lo:hi]) for r in [[q["deaths"] for q in g] for g in c])
        xx=sum(sum(r[60][lo:hi])-sum(r[36][lo:hi]) for r in [[q["deaths"] for q in g] for g in x])
        e[nm]=(xx,cc,round((( xx/cc)**(math.log(.9)/math.log(.7))-1)*100,1))
    bc=sum(q["births"] for g in c for q in g[37:61]); bx=sum(q["births"] for g in x for q in g[37:61])
    e["births"]=(bx,bc,round(((bx/bc)**(math.log(.9)/math.log(.7))-1)*100,1))
    print("  two-year, arm/control, per10%:",e); ev[w]=e
json.dump(ev,open("docs/evidence/add129_per10.json","w"),indent=1)
