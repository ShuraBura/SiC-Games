"""R-106 Add.127: instrument checks for the one-year shock test, run BEFORE any effect is read.
1 control: each run equals its stored s2_<world>_pair run row for row up to step 9000 (monitor columns of the Add.124
  re-score ignored). 2 the driver: mult_sum rises by 12*m in each shock year and by 12 otherwise. 3 counters: deaths in
  the yearly file equal the trajectory's lt_deaths_total at shared steps. 4 drift: population against the stored control."""
import json, os, statistics as st
ROOT = r"C:\Users\syatom\Projects\SiC Games"
OUT = os.path.join(ROOT, "sic_games", "outputs", "substrate_run")
LOG = os.path.join(ROOT, "scratchpad", "drought_logs")
W = ("temperate", "savanna", "montane")
IGN = {"demog_in_band", "demog_scored"}
shocks = [(9000 + i * 240, (0.85, 0.70)[i % 2]) for i in range(20)]
sh = dict(shocks)
ok_ctl = ok_drv = ok_cnt = 0
for w in W:
    for s in (0, 1, 2):
        T = json.load(open(os.path.join(OUT, f"campaign_trajectory_yr1_{w}_s{s}.json"), encoding="utf-8"))["traj"]
        C = json.load(open(os.path.join(OUT, f"campaign_trajectory_s2_{w}_pair_s{s}.json"), encoding="utf-8"))["traj"]
        cm = {r["step"]: r for r in C}
        tm = {r["step"]: r for r in T}
        bad = None
        n = 0
        for st_, r in tm.items():
            if st_ >= 9000 or st_ not in cm:
                continue
            n += 1
            for k, v in r.items():
                if k in IGN:
                    continue
                if cm[st_].get(k) != v and not (isinstance(v, float) and v != v):
                    bad = (st_, k, v, cm[st_].get(k))
                    break
            if bad:
                break
        ok_ctl += bad is None
        R = [json.loads(l) for l in open(os.path.join(LOG, f"yr1_yr1_{w}_s{s}.jsonl"))]
        dok = all(abs((b["mult_sum"] - a["mult_sum"]) - 12 * sh.get(a["step"], 1.0)) < 1e-6 for a, b in zip(R, R[1:]))
        ok_drv += dok
        rows = {r["step"]: r["lt_deaths_total"] for r in T if "lt_deaths_total" in r}
        shared = [r for r in R if r["step"] in rows]
        cok = len(shared) > 10 and all(sum(r["lt_deaths"]) == rows[r["step"]] for r in shared)
        ok_cnt += cok
        ratio = [tm[t]["pop"] / cm[t]["pop"] for t in tm if t in cm and t >= 9000]
        late = [tm[t]["pop"] / cm[t]["pop"] for t in tm if t in cm and t >= 12000]
        print(f"{w[:4]} s{s}: rows<=9000 {n} control {'OK' if bad is None else bad} | driver {dok} | counters {cok} ({len(shared)} shared) | pop/control min {min(ratio):.3f} mean {st.mean(ratio):.3f} late mean {st.mean(late):.3f}")
print(f"control {ok_ctl}/9  driver {ok_drv}/9  counters {ok_cnt}/9")
