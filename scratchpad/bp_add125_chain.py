import json, os, statistics as st
OUT = "sic_games/outputs/substrate_run"
W = ("temperate", "savanna", "montane")
K = ("condition_mean", "mean_reserve", "intake_raw_p10", "intake_raw_p50", "intake_raw_p90", "intake_ema_p10", "intake_ema_p50", "intake_raw_frac_below_hi", "intake_ema_frac_below_hi", "starv_frac_acute")
WIN = {"pre": (8000, 9000), "dr": (9100, 9360), "aft": (9375, 9720)}
def load(p): return json.load(open(p, encoding="utf-8"))["traj"]
def mw(tr, k, a, b):
    xs = [r.get(k) for r in tr if a <= r["step"] <= b and r.get(k) is not None]
    return st.mean(xs) if xs else float("nan")
for w in W:
    ctl = [load(f"{OUT}/campaign_trajectory_s2_{w}_pair_s{s}.json") for s in (0, 1, 2)]
    for m in ("085", "070"):
        runs = [load(f"{OUT}/campaign_trajectory_dr_pair_{w}_m{m}_s{s}.json") for s in (0, 1, 2)]
        print(f"== {w} x0.{m[1:]}")
        for k in K:
            line = []
            for n, (a, b) in WIN.items():
                d = st.mean(mw(t, k, a, b) for t in runs)
                c = st.mean(mw(t, k, a, b) for t in ctl)
                line.append(f"{n}: {d:9.3f} vs {c:9.3f}")
            print(f"   {k:26s}", " | ".join(line))
