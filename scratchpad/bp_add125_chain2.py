"""R-106 Add.125 chain checks.
1. Fertility chain per window from the sidecars: period TFR, mean fertility factor, share saturated, mean IBI.
2. Time course: crude deaths per 1000/yr in 5-year bins through the drought, paired with the control, to find an onset
   spike that the 30-year window could hide. Also pop and median intake.
3. Was `condition` flat in the Add.119 all4 drought runs too?
4. ASDR decomposition: starvation vs non-starvation part, pre -> drought -> after.
"""
import json
import os
import statistics as st

ROOT = r"C:\Users\syatom\Projects\SiC Games"
OUT = os.path.join(ROOT, "sic_games", "outputs", "substrate_run")
LOG = os.path.join(ROOT, "scratchpad", "drought_logs")
W = ("temperate", "savanna", "montane")
MS = ("085", "070")
S = (0, 1, 2)


def traj(tag):
    return json.load(open(os.path.join(OUT, f"campaign_trajectory_{tag}.json"), encoding="utf-8"))


print("1. FERTILITY CHAIN: window: TFR | mean factor | share saturated | mean IBI months")
for w in W:
    for m in MS:
        for name, a, b in (("drought", "9000", "9360"), ("after", "9360", "9720")):
            T, FF, SAT, IB, BF = [], [], [], [], []
            for s in S:
                sc = json.load(open(os.path.join(LOG, f"lt_dr_pair_{w}_m{m}_s{s}.json"), encoding="utf-8"))
                A, B = sc[a], sc[b]
                fb = [y - x for x, y in zip(A["fert_births"], B["fert_births"])]
                fe = [(y - x) / 12 for x, y in zip(A["fert_exposure"], B["fert_exposure"])]
                T.append(sum(p / q for p, q in zip(fb, fe) if q > 0))
                n = B["fert_factor_n"] - A["fert_factor_n"]
                FF.append((B["fert_factor_sum"] - A["fert_factor_sum"]) / n)
                SAT.append((B["fert_factor_sat"] - A["fert_factor_sat"]) / n)
                ib = [y - x for x, y in zip(A["ibi_hist"], B["ibi_hist"])]
                IB.append(sum(i * c for i, c in enumerate(ib)) / max(sum(ib), 1))
            print(f"  {w[:4]} x0.{m[1:]} {name:8s} TFR {st.mean(T):.2f} | factor {st.mean(FF):.3f} | sat {st.mean(SAT):.3f} | IBI {st.mean(IB):.1f}")

print("\n2. TIME COURSE: crude deaths/1000/yr per 5-yr bin, drought minus control, mean of 3 paired seeds; [min..max]")
EDGES = list(range(9000, 9400, 75))   # 75 steps = 6.25 yr, on the 25-step grid
for w in W:
    ctl = {s: {r["step"]: r for r in traj(f"s2_{w}_pair_s{s}")["traj"]} for s in S}
    for m in MS:
        cells = []
        for a, b in zip(EDGES, EDGES[1:]):
            ds = []
            for s in S:
                tr = {r["step"]: r for r in traj(f"dr_pair_{w}_m{m}_s{s}")["traj"]}
                rate = lambda T: (T[b]["lt_deaths_total"] - T[a]["lt_deaths_total"]) / ((b - a) / 12) / ((T[a]["pop"] + T[b]["pop"]) / 2) * 1000
                ds.append(rate(tr) - rate(ctl[s]))
            cells.append(f"{a}:{st.mean(ds):+.1f}[{min(ds):+.1f}..{max(ds):+.1f}]")
        print(f"  {w[:4]} x0.{m[1:]}", " ".join(cells))

print("\n3. condition_mean in the Add.119 all4 drought runs and the canon of the time")
for arm in ("all4", ""):
    for w in W:
        for m in ("070",):
            vals, cvals = [], []
            for s in S:
                p = f"dr_{arm + '_' if arm else ''}{w}_m{m}_s{s}"
                if not os.path.exists(os.path.join(OUT, f"campaign_trajectory_{p}.json")):
                    continue
                t = traj(p)["traj"]
                vals.append((st.mean(r["condition_mean"] for r in t if 8000 <= r["step"] < 9000),
                             st.mean(r["condition_mean"] for r in t if 9100 <= r["step"] <= 9360)))
            if vals:
                print(f"  {arm or 'canon A117':10s} {w[:4]} x0.70 pre {st.mean(v[0] for v in vals):.4f} drought {st.mean(v[1] for v in vals):.4f}")

print("\n4. ASDR PARTS /1000/yr (pre age shares): non-starvation + starvation")
d = json.load(open(os.path.join(ROOT, "scratchpad", "drought_age_pair.json"), encoding="utf-8"))
BK = ("0-1", "1-5", "5-15", "15-45", "45-65", "65-100")
for w in W:
    for m in MS:
        cells = []
        for wn in ("pre", "drought", "after"):
            ns, sv = [], []
            for s in S:
                r = d[w][m][str(s)]
                sh = {k: r["pre"]["bands"][k]["share"] for k in BK}
                ns.append(sum(sh[k] * r[wn]["bands"][k]["m_ns"] for k in BK) * 1000)
                sv.append(sum(sh[k] * r[wn]["bands"][k]["m_s"] for k in BK) * 1000)
            cells.append(f"{wn}: {st.mean(ns):5.1f} + {st.mean(sv):4.1f}")
        print(f"  {w[:4]} x0.{m[1:]}", " | ".join(cells))
