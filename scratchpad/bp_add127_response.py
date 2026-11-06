"""R-106 Add.127: the response to a one-year food shock, in the anchor's unit, with the anchor's age bands.

Events: 20 shocks per run, 10 at each depth, 9 runs. Year k of a shock = counters from onset+12k to onset+12(k+1).
BASELINE k=-4..-2. Year -1 is NOT in the baseline: the shock first acts in the step that ends at count = onset (the
smoke test and the row at step 9000 show this), so year -1 holds one shocked month.
RESPONSE WINDOW k=-1..+1 = all shocked months plus the following year: the model's "two-year sum".
NULL k=+10..+12 against the same baseline. Rates: births = fert_births / fert_exposure; deaths = lt_deaths / lt_exposure.
Per 10%: e = sum_k ln(r_k) / ln(m); response = 0.9**e - 1. CI: bootstrap of events (seed, shock), within world.
"""
import json, math, os, sys
import numpy as np
ROOT = r"C:\Users\syatom\Projects\SiC Games"
LOG = os.path.join(ROOT, "scratchpad", "drought_logs")
W = ("temperate", "savanna", "montane")
M = {"085": 0.85, "070": 0.70}
ONS = [(9000 + i * 240, ("085", "070")[i % 2]) for i in range(20)]
KS = list(range(-4, 14))
MEAS = {"births": ("fert_births", "fert_exposure", 0, 100), "d 0": ("lt_deaths", "lt_exposure", 0, 1),
        "d 1-9": ("lt_deaths", "lt_exposure", 1, 10), "d 10-14": ("lt_deaths", "lt_exposure", 10, 15),
        "d 15-24": ("lt_deaths", "lt_exposure", 15, 25), "d 25-44": ("lt_deaths", "lt_exposure", 25, 45),
        "d 45-64": ("lt_deaths", "lt_exposure", 45, 65), "d 65+": ("lt_deaths", "lt_exposure", 65, 100),
        "s 1-9": ("lt_deaths_starv", "lt_exposure", 1, 10), "s 15-24": ("lt_deaths_starv", "lt_exposure", 15, 25),
        "s all": ("lt_deaths_starv", "lt_exposure", 0, 100), "d all": ("lt_deaths", "lt_exposure", 0, 100)}
NM = list(MEAS)
EV = {}   # (world, depth) -> array [event, k, measure, (events, exposure)]; plus seed index
FF = {}
for w in W:
    for s in (0, 1, 2):
        R = {r["step"]: r for r in map(json.loads, open(os.path.join(LOG, f"yr1_yr1_{w}_s{s}.jsonl")))}
        for on, d in ONS:
            a = np.zeros((len(KS), len(NM), 2))
            f = np.zeros(len(KS))
            for ik, k in enumerate(KS):
                x, y = R[on + 12 * k], R[on + 12 * (k + 1)]
                for im, n in enumerate(NM):
                    c, e, lo, hi = MEAS[n]
                    a[ik, im, 0] = sum(y[c][lo:hi]) - sum(x[c][lo:hi])
                    a[ik, im, 1] = (sum(y[e][lo:hi]) - sum(x[e][lo:hi])) / 12
                f[ik] = (y["fert_factor_sum"] - x["fert_factor_sum"]) / max(1, y["fert_factor_n"] - x["fert_factor_n"])
            EV.setdefault((w, d), []).append((s, on, a))
            FF.setdefault((w, d), []).append(f)
base = [KS.index(k) for k in (-4, -3, -2)]
null = [KS.index(k) for k in (10, 11, 12)]
resp = [KS.index(k) for k in (-1, 0, 1)]


def ratios(A):
    """A [event,k,m,2] -> r[k,m] pooled rate ratio to the baseline."""
    S = A.sum(0)
    rate = S[..., 0] / S[..., 1]
    b = S[base].sum(0)
    return rate / (b[..., 0] / b[..., 1])


def per10(r, m, idx):
    e = np.log(r[idx]).sum(0) / math.log(m)
    return (0.9 ** e - 1) * 100


def nullpct(r):
    return (r[null].mean(0) - 1) * 100


rng = np.random.default_rng(127)
def boot(sets, m, fn, n=2000):
    """sets: list of event arrays, one per stratum."""
    out = []
    for _ in range(n):
        S = sum(a[rng.integers(0, len(a), len(a))].sum(0) for a in sets)
        rate = S[..., 0] / np.maximum(S[..., 1], 1e-9)
        b = S[base].sum(0)
        r = rate / (b[..., 0] / b[..., 1])
        out.append(fn(r))
    return np.percentile(np.array(out), [2.5, 97.5], axis=0)


res = {}
EXCL = len(sys.argv) > 1 and sys.argv[1] == "nomont1"
print("events per stratum:", {k: len(v) for k, v in list(EV.items())[:1]}, "| excl montane s1:", EXCL)
for d, m in M.items():
    sets = {}
    for w in W:
        ev = [a for s, on, a in EV[(w, d)] if not (EXCL and w == "montane" and s == 1)]
        sets[w] = np.array(ev)
    for name, ss in list(sets.items()) + [("pooled", None)]:
        group = [ss] if ss is not None else list(sets.values())
        S = sum(a.sum(0, keepdims=True) for a in group)
        r = ratios(S)
        p = per10(r, m, resp)
        ci = boot(group, m, lambda rr: per10(rr, m, resp))
        n0 = nullpct(r)
        nc = boot(group, m, nullpct)
        res[f"{name}|{d}"] = dict(per10={n: float(x) for n, x in zip(NM, p)}, ci={n: [float(ci[0][i]), float(ci[1][i])] for i, n in enumerate(NM)},
                                  null={n: float(x) for n, x in zip(NM, n0)}, nullci={n: [float(nc[0][i]), float(nc[1][i])] for i, n in enumerate(NM)},
                                  ratio={n: [float(x) for x in r[:, i]] for i, n in enumerate(NM)})
        if name == "pooled":
            rc = boot(group, m, lambda rr: rr)
            res[f"{name}|{d}"]["ratio_ci"] = {n: [[float(x) for x in rc[0][:, i]], [float(x) for x in rc[1][:, i]]] for i, n in enumerate(NM)}
        print(f"\n{name} x{m:.2f}  base events/yr: births {S[0][base,0,0].mean():.0f}, d1-9 {S[0][base,2,0].mean():.0f}, d15-24 {S[0][base,4,0].mean():.0f}")
        for n in NM:
            i = NM.index(n)
            print(f"  {n:8s} per10 {p[i]:+7.1f} [{ci[0][i]:+6.1f},{ci[1][i]:+6.1f}]  | yr -1,0,1,2,3: " + " ".join(f"{(r[KS.index(k), i]-1)*100:+6.1f}" for k in (-1,0,1,2,3)) + f" | null {n0[i]:+5.1f} [{nc[0][i]:+5.1f},{nc[1][i]:+5.1f}]")
tag = "_nomont1" if EXCL else ""
ff = {f"{w}|{d}": [float(x) for x in np.mean(FF[(w, d)], 0)] for w in W for d in M}
json.dump(dict(KS=KS, res=res, fert_factor=ff), open(os.path.join(ROOT, "scratchpad", f"add127_response{tag}.json"), "w", encoding="utf-8"), indent=1)
