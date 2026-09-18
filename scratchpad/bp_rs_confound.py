"""R-106 Addendum 102 — is the #11 status->RS a CONDITION CONFOUND rather than a mating effect?

The ablation showed neither mate choice (m: 5.0 -> 0) nor polygyny (-> 0) materially moves status->RS. So the
correlation is probably not produced by the mating market at all. `prowess` is a decaying EMA of RELATIVE MEAT
INTAKE, so a well-fed man in a good cell carries high prowess AND fathers more children through fertility/survival,
with no mate-choice involvement. That is a COMMON CAUSE, not status->RS.

The marker partials out AGE. It does not partial out CONDITION. This test adds that control:
    r1 = partial(prowess, n_fathered | age)              <- the marker as scored
    r2 = partial(prowess, n_fathered | age, intake_ema)  <- the same, also controlling condition
If r2 collapses toward 0 while r1 does not, the measured status->RS is largely a condition confound.
Comparative test -> probe harness is legitimate (Add.101).
"""
import os
import sys
import numpy as np

ROOT = r"C:\Users\syatom\Projects\SiC Games"
sys.path.insert(0, os.path.join(ROOT, "scratchpad"))
from bp_savanna_probe import build, runconfig

STEPS = int(os.environ.get("C_STEPS", "800"))
MEN_MO = 180.0


def resid(y, X):
    """residual of y after least-squares regression on columns X (with intercept)."""
    A = np.column_stack([np.ones(len(y))] + [np.asarray(c, float) for c in X])
    beta, *_ = np.linalg.lstsq(A, np.asarray(y, float), rcond=None)
    return np.asarray(y, float) - A @ beta


def pcorr(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    if len(x) < 3 or x.std() == 0 or y.std() == 0:
        return float("nan")
    return float(np.corrcoef(x, y)[0, 1])


def partial_on(x, y, controls):
    return pcorr(resid(x, controls), resid(y, controls))


def run_one(clim, ws):
    canon = dict(runconfig.load()["DemographyConfig"])
    w = build(canon, ws, 0, clim=clim)
    for _ in range(STEPS):
        w.step()
        if not w.agent_list:
            break
    males = [a for a in w.agent_list if a.sex == "male" and a.age >= MEN_MO]
    if len(males) < 20:
        return None
    pr = [getattr(a, "prowess", 1.0) for a in males]
    off = [float(getattr(a, "_n_fathered", 0)) for a in males]
    age = [float(a.age) for a in males]
    ie = [float(getattr(a, "_intake_ema", 1.0)) for a in males]
    wl = [float(getattr(a, "wealth", 0.0)) for a in males]
    return dict(
        r_age=partial_on(pr, off, [age]),
        r_age_intake=partial_on(pr, off, [age, ie]),
        r_age_intake_wealth=partial_on(pr, off, [age, ie, wl]),
        c_pr_intake=pcorr(pr, ie),
        c_intake_off=partial_on(ie, off, [age]),
        n=len(males))


def ms(v):
    v = np.array([x for x in v if x == x], float)
    return (v.mean(), v.std(ddof=1) / np.sqrt(len(v))) if len(v) > 1 else (float(v.mean()) if len(v) else float("nan"), 0.0)


def main():
    worlds = [int(x) for x in os.environ.get("C_WORLDS", "0,1,2").split(",")]
    for clim in os.environ.get("C_BIOMES", "temperate,savanna").split(","):
        rows = [r for r in (run_one(clim, ws) for ws in worlds) if r]
        if not rows:
            continue
        print(f"== {clim.upper()} | n_males~{ms([r['n'] for r in rows])[0]:.0f} ==")
        a, ae = ms([r["r_age"] for r in rows])
        b, be = ms([r["r_age_intake"] for r in rows])
        c, ce = ms([r["r_age_intake_wealth"] for r in rows])
        print(f"  partial(prowess, offspring | age)                 = {a:+.3f}+/-{ae:.3f}   <- THE MARKER")
        print(f"  partial(prowess, offspring | age, intake_ema)     = {b:+.3f}+/-{be:.3f}")
        print(f"  partial(prowess, offspring | age, intake, wealth) = {c:+.3f}+/-{ce:.3f}")
        print(f"  corr(prowess, intake_ema)                         = {ms([r['c_pr_intake'] for r in rows])[0]:+.3f}")
        print(f"  partial(intake_ema, offspring | age)              = {ms([r['c_intake_off'] for r in rows])[0]:+.3f}")
        print()


if __name__ == "__main__":
    main()
