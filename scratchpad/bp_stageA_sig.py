"""Stage A: are the individual signals live with the flag on? Means, and the change in the first shock year against the paired control."""
import json
import os

ROOT = r"C:\Users\syatom\Projects\SiC Games"
L = os.path.join(ROOT, "scratchpad", "design_logs")
W = ("temperate", "savanna", "montane")
S = (0, 1)


def jl(tag):
    return [json.loads(x) for x in open(os.path.join(L, f"sig{tag}.jsonl"), encoding="utf-8")]


def yr(runs, g, k, a, b):
    v = [(r[g][k] if g else r[k]) for x in runs for r in x[a:b]]
    v = [q for q in v if q is not None]
    return sum(v) / len(v)


ev = {}
for w in W:
    off = [jl(f"_vc_{w}_off_c_s{s}") for s in S]
    on = [jl(f"_vc_{w}_on_c_s{s}") for s in S]
    y1 = [jl(f"_vc_{w}_on_y1_s{s}") for s in S]
    y5 = [jl(f"_vc_{w}_on_y5_s{s}") for s in S]
    print(f"\n=== {w}: women at risk W, children C. Control mean off -> on, then yr1 of x0.70 vs paired on control (%)")
    e = ev[w] = {}
    for g, k in (("W", "ema_p50"), ("W", "ema_p10"), ("W", "f_int_m"), ("W", "fd_m"), ("W", "f_fd"), ("W", "fill_m"), ("W", "cond_m"), ("W", "raw_p50"), ("W", "fed_p10"), ("W", "trough_p10"),
                 ("C", "cond_m"), ("C", "fed_m"), ("C", "fed_p10"), ("C", "trough_p10"), ("C", "raw_p50"), (None, "m_ema"), (None, "m_ema_p10"), (None, "m_unfed")):
        a, b = yr(off, g, k, 0, 36), yr(on, g, k, 0, 36)
        c, x = yr(on, g, k, 36, 48), yr(y1, g, k, 36, 48)
        c5, x5 = yr(on, g, k, 60, 96), yr(y5, g, k, 60, 96)
        e[f"{g}.{k}"] = dict(off=a, on=b, y1=(x / c - 1) * 100 if c else None, y5_yr3_5=(x5 / c5 - 1) * 100 if c5 else None)
        print(f"  {str(g):4s} {k:11s} off {a:8.3f} on {b:8.3f}   yr1 {(x / c - 1) * 100 if c else 0:+6.1f}%   y5 yr3-5 {(x5 / c5 - 1) * 100 if c5 else 0:+6.1f}%")
json.dump(ev, open(os.path.join(ROOT, "docs", "evidence", "add129_signals.json"), "w", encoding="utf-8"), indent=1)
