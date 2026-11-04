"""R-106 Add.125: EXACT age-specific mortality and fertility in the drought test on the adopted canon.

The saved counters (bp_drought.py) are cumulative by year of age, so a difference is a period rate. Windows:
pre 7500-9000 (meta snapshot), drought 9000-9360, after 9360-9720, late 9720-12000 (final counters).
Exposure is person-MONTHS, so it is divided by 12. Rates are per person-year.

Measures per run and window: m(x) all causes, starvation, non-starvation; the age-standardised death rate (ASDR: the
pre window's age shares applied to the window's m(x), so a fall in births cannot move it); the crude rate; period TFR
(only drought and after: the meta snapshots hold no fertility counters); excess deaths =
sum[(m_win(x) - m_pre(x)) * exposure_win(x)].

Positive controls: (1) sidecar total deaths = trajectory `lt_deaths_total` at step 9000 and between the bracketing rows
at 9360 and 9720; (2) the pre window's non-starvation m(x) / de-warfared Siler is about 1 (Add.122).
Null floor: Poisson SE of each ratio, and the spread across seeds.
"""
import json
import math
import os

ROOT = r"C:\Users\syatom\Projects\SiC Games"
OUT = os.path.join(ROOT, "sic_games", "outputs", "substrate_run")
LOG = os.path.join(ROOT, "scratchpad", "drought_logs")
W = ("temperate", "savanna", "montane")
MS = ("085", "070")
SEEDS = (0, 1, 2)
BANDS = [(0, 1), (1, 5), (5, 15), (15, 45), (45, 65), (65, 100)]
WINS = ("pre", "drought", "after", "late")
a1, b1, a2, a3, b3 = 0.1611, 0.6775, 0.00813, 3.781e-5, 0.1025


def h(t):
    return a1 * math.exp(-b1 * t) + a2 + a3 * math.exp(b3 * t)


def H(t):
    return (a1 / b1) * (1 - math.exp(-b1 * t)) + a2 * t + (a3 / b3) * (math.exp(b3 * t) - 1)


def siler_m(lo, hi, n=400):
    xs = [lo + (i + .5) * (hi - lo) / n for i in range(n)]
    return sum(math.exp(-H(x)) * h(x) for x in xs) / sum(math.exp(-H(x)) for x in xs)


def diff(b, a, k):
    return [y - x for x, y in zip(a[k], b[k])]


def window(a, b):
    """Rates between two counter snapshots, by year of age. Fertility only when both snapshots hold it."""
    win = dict(e=[x / 12.0 for x in diff(b, a, "lt_exposure")], d=diff(b, a, "lt_deaths"), s=diff(b, a, "lt_deaths_starv"))
    if "fert_births" in a and "fert_births" in b:
        win["fb"] = diff(b, a, "fert_births")
        win["fe"] = [x / 12.0 for x in diff(b, a, "fert_exposure")]
    return win


def band(win, key, lo, hi):
    return sum(win[key][lo:hi]), sum(win["e"][lo:hi])


def mean(xs):
    return sum(xs) / len(xs)


res, checks = {}, []
for w in W:
    for m in MS:
        for s in SEEDS:
            tag = f"dr_pair_{w}_m{m}_s{s}"
            doc = json.load(open(os.path.join(OUT, f"campaign_trajectory_{tag}.json"), encoding="utf-8"))
            sc = json.load(open(os.path.join(LOG, f"lt_{tag}.json"), encoding="utf-8"))
            meta, tr = doc["meta"], doc["traj"]
            rows = {r["step"]: r["lt_deaths_total"] for r in tr if "lt_deaths_total" in r}
            ok = sum(sc["9000"]["lt_deaths"]) == rows[9000]
            for t, lo, hi in ((9360, 9350, 9375), (9720, 9700, 9725)):
                ok = ok and rows[lo] <= sum(sc[str(t)]["lt_deaths"]) <= rows[hi]
            ok = ok and meta["life_table_snap_step"] == 7500 and sc["9000"]["step"] == 9000
            checks.append(ok)
            S, F = meta["life_table_snap"], meta["life_table_final"]
            wins = dict(pre=window(S, sc["9000"]), drought=window(sc["9000"], sc["9360"]),
                        after=window(sc["9360"], sc["9720"]), late=window(sc["9720"], F))
            pre = wins["pre"]
            pre_tot = sum(pre["e"])
            shares = [x / pre_tot for x in pre["e"]]
            pre_m = [(d / e if e else 0.0) for d, e in zip(pre["d"], pre["e"])]
            out = {}
            for name in WINS:
                wn = wins[name]
                mx = [(d / e if e else None) for d, e in zip(wn["d"], wn["e"])]
                asdr = sum(sh * (x if x is not None else p) for sh, x, p in zip(shares, mx, pre_m)) * 1000
                exc = sum((d / e - p) * e if e else 0.0 for d, e, p in zip(wn["d"], wn["e"], pre_m))
                asdr_s = sum(sh * (sv / e if e else 0.0) for sh, sv, e in zip(shares, wn["s"], wn["e"])) * 1000
                r = dict(asdr=asdr, asdr_s=asdr_s, asdr_ns=asdr - asdr_s, crude=sum(wn["d"]) / sum(wn["e"]) * 1000, exposure=sum(wn["e"]), deaths=sum(wn["d"]),
                         starv=sum(wn["s"]), excess=exc, bands={})
                r["starv_share"] = r["starv"] / r["deaths"]
                for lo, hi in BANDS:
                    d, e = band(wn, "d", lo, hi)
                    sv, _ = band(wn, "s", lo, hi)
                    r["bands"][f"{lo}-{hi}"] = dict(d=d, s=sv, e=e, m=d / e if e else None, m_ns=(d - sv) / e if e else None,
                                                    m_s=sv / e if e else None, share=e / sum(wn["e"]))
                if "fb" in wn:
                    r["tfr"] = sum(b / e for b, e in zip(wn["fb"], wn["fe"]) if e > 0)
                    r["births"] = sum(wn["fb"])
                out[name] = r
            res.setdefault(w, {}).setdefault(m, {})[s] = out
json.dump(res, open(os.path.join(ROOT, "scratchpad", "drought_age_pair.json"), "w", encoding="utf-8"), indent=1)
print(f"POSITIVE CONTROL 1 (sidecar = trajectory): {sum(checks)}/{len(checks)}")
print("\nPOSITIVE CONTROL 2: pre-window non-starvation m / de-warfared Siler (mean of seeds)")
for w in W:
    print(f"  {w:9s}", " ".join(
        f"{lo}-{hi}:{mean([res[w]['085'][s]['pre']['bands'][f'{lo}-{hi}']['m_ns'] for s in SEEDS]) / siler_m(lo, hi):.2f}"
        for lo, hi in BANDS))

print("\nAGE-STANDARDISED DEATH RATE /1000/yr (pre shares) and crude; per seed")
for w in W:
    for m in MS:
        rr = res[w][m]
        print(f" {w[:4]} x0.{m[1:]}")
        for wn in WINS:
            a = [rr[s][wn]["asdr"] for s in SEEDS]
            c = [rr[s][wn]["crude"] for s in SEEDS]
            tf = [rr[s][wn]["tfr"] for s in SEEDS if "tfr" in rr[s][wn]]
            print(f"   {wn:8s} ASDR {mean(a):5.1f} ({min(a):5.1f}-{max(a):5.1f})  crude {mean(c):5.1f}"
                  f"  starv share {mean([rr[s][wn]['starv_share'] for s in SEEDS]):.3f}"
                  + (f"  TFR {mean(tf):.2f}" if tf else ""))

print("\nRATIO m(window) / m(pre), by age, mean of 3 seeds; [min-max]; +- = Poisson SE of the pooled ratio")
for w in W:
    for m in MS:
        rr = res[w][m]
        for wn in ("drought", "after"):
            parts = []
            for lo, hi in BANDS:
                k = f"{lo}-{hi}"
                q = [rr[s][wn]["bands"][k]["m"] / rr[s]["pre"]["bands"][k]["m"] for s in SEEDS]
                dd = sum(rr[s][wn]["bands"][k]["d"] for s in SEEDS)
                dp = sum(rr[s]["pre"]["bands"][k]["d"] for s in SEEDS)
                pse = mean(q) * math.sqrt(1 / max(dd, 1) + 1 / max(dp, 1))
                parts.append(f"{k}:{mean(q):.2f}[{min(q):.2f}-{max(q):.2f}]+-{pse:.2f}")
            print(f" {w[:4]} x0.{m[1:]} {wn:8s}", " ".join(parts))

print("\nSTARVATION m by age: pre -> drought (mean of seeds, per 1000 py)")
for w in W:
    for m in MS:
        rr = res[w][m]
        print(f" {w[:4]} x0.{m[1:]}", " ".join(
            f"{lo}-{hi}:{mean([rr[s]['pre']['bands'][f'{lo}-{hi}']['m_s'] for s in SEEDS]) * 1000:.2f}"
            f"->{mean([rr[s]['drought']['bands'][f'{lo}-{hi}']['m_s'] for s in SEEDS]) * 1000:.2f}"
            for lo, hi in BANDS))

print("\nEXCESS DEATHS in the drought window (age-exact, against own pre rates)")
for w in W:
    for m in MS:
        rr = res[w][m]
        print(f" {w[:4]} x0.{m[1:]} excess {[round(rr[s]['drought']['excess']) for s in SEEDS]}"
              f"  deaths {[rr[s]['drought']['deaths'] for s in SEEDS]}  births {[rr[s]['drought'].get('births') for s in SEEDS]}")
