"""Score Stage A of Add.128 against the gates that were fixed before the data. Writes docs/evidence/add129_measurement.json."""
import glob
import json
import os
import sys
from types import SimpleNamespace

ROOT = r"C:\Users\syatom\Projects\SiC Games"
sys.path.insert(0, os.path.join(ROOT, "sic_games", "src"))
from sic_games.phase1_model import TerrainWorld   # noqa: E402
O = os.path.join(ROOT, "sic_games", "outputs", "substrate_run")
L = os.path.join(ROOT, "scratchpad", "design_logs")
W = ("temperate", "savanna", "montane")
S = (0, 1)
KEYS = ("lt_exposure", "lt_deaths", "lt_deaths_starv", "lt_deaths_senesc")
ONSET = 2400


def traj(tag):
    return json.load(open(os.path.join(O, f"campaign_trajectory{tag}.json"), encoding="utf-8"))


def jl(pre, tag):
    return [json.loads(x) for x in open(os.path.join(L, f"{pre}{tag}.jsonl"), encoding="utf-8")]


def period(d):
    m = d["meta"]
    fin, snap = m["life_table_final"], m["life_table_snap"]
    f = lambda c: SimpleNamespace(**{k: list(c[k]) for k in KEYS})
    t = TerrainWorld.life_table(f(fin), since={k: snap[k] for k in KEYS})
    return {k: t.get(k) for k in t if not isinstance(t[k], (list, dict))}


def m(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


ev = dict(a1=dict(), worlds={})
# A1: the flag-off control against the stored Add.124 canon
bad = 0
for w in W:
    for s in S:
        a = {r["step"]: r for r in traj(f"_vc_{w}_off_c_s{s}")["traj"]}
        b = {r["step"]: r for r in traj(f"_s2_{w}_pair_s{s}")["traj"]}
        sh = sorted(set(a) & set(b))
        diff = [k for k in sh if any(a[k].get(q) != b[k].get(q) for q in ("pop", "births", "deaths_starv", "n_settle", "gini_cred"))]
        print(f"A1 off vs pair {w} s{s}: {len(sh)} shared rows, {len(diff)} differ, first {diff[:1]}")
        bad += len(diff)
ev["a1"]["off_vs_pair_rows_differ"] = bad
for w in W:
    for s in S:
        c = traj(f"_vc_{w}_on_c_s{s}")["traj"]
        for a in ("y1", "y5"):
            x = traj(f"_vc_{w}_on_{a}_s{s}")["traj"]
            d = [r["step"] for r, q in zip(c, x) if r["step"] <= ONSET and r["pop"] != q["pop"]]
            f = [r["step"] for r, q in zip(c, x) if r["pop"] != q["pop"]]
            print(f"A1 pre-shock {w} s{s} {a}: differ before onset {len(d)}, first split {f[:1]}")
mx, over, n = 0.0, 0, 0
for w in W:
    for s in S:
        for a in ("c", "y1", "y5"):
            for r in jl("acc", f"_vc_{w}_on_{a}_s{s}"):
                n += 1
                mx = max(mx, r["sup_cap_max"] or 0)
                over += r["sup_cap_over"]
print(f"A1 sum/cap: {n} step records, max {mx:.4f}, village-steps above 1.001 {over}")
ev["a1"].update(sum_cap_max=mx, over_1001=over)
# A3, A4: control arms, flag off against flag on, sustained window
for w in W:
    e = ev["worlds"][w] = {}
    for fl in ("off", "on"):
        p = [period(traj(f"_vc_{w}_{fl}_c_s{s}")) for s in S]
        tr = [traj(f"_vc_{w}_{fl}_c_s{s}")["traj"] for s in S]
        rows = [r for t in tr for r in t if 1800 <= r["step"] <= 3000]
        g = lambda k: m([r.get(k) for r in rows])
        e[fl] = dict(pop=g("pop"), villages=g("n_settle"), village_med=g("village_med"), settle_med=g("settle_med"), band_med=g("band_med"), n_bands=g("n_bands"),
                     gini_cred=g("gini_cred"), gini_material=g("gini_material"), juv=g("juv_frac"),
                     e0s=[x["e0"] for x in p], **{k: m([x.get(k) for x in p]) for k in p[0] if isinstance(p[0][k], (int, float))})
        e[fl]["mobile_share"] = m([r["all"]["mobile"] for s in S for r in jl("sto", f"_vc_{w}_{fl}_c_s{s}")[:36]])
    print(f"\n{w}: off/on, mean of 2 seeds, steps 1800-3000 (life table 1200-3000)")
    for k in ("pop", "villages", "village_med", "band_med", "n_bands", "mobile_share", "e0", "gini_cred", "gini_material"):
        print(f"  {k:14s} {e['off'][k]}  ->  {e['on'][k]}")
    print("  period keys:", {k: round(v, 3) for k, v in e["on"].items() if isinstance(v, float)})
json.dump(ev, open(os.path.join(ROOT, "docs", "evidence", "add129_measurement.json"), "w", encoding="utf-8"), indent=1, default=str)
