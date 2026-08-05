"""Which candidate restores the cohesion budget's headroom — and does it cost anything?

R-106 Addendum 22 measured `cohesion_frac = clamp01(assabiyah + leader - repulsion - malnutrition)` pinned at
1.0 for every band with a leader, so `split_thr` collapses to the constant `band_split_size`, g* drops out,
and FOUR mechanisms (emergent band size, dynamic bands, size repulsion, malnutrition fission) are inert at any
magnitude. Two flagged candidates, both default-off and bit-exact:

  LEAKY      `a += gain*s*(1-a) - decay*a` instead of `a += gain*s - decay`. The default form is a pure
             integrator with a CONSTANT leak and therefore has no interior fixed point — it is bang-bang by
             construction and no gain/decay choice makes it graded. The leaky form's fixed point
             a* = gain*s/(gain*s + decay) tracks surplus (0.47 at s=0.35, 0.63 at the median 0.69).
  LEADERW    scales the leader term (0.41-1.64, median 0.78) into the [0,1] budget, since it re-saturates the
             sum on its own even with a graded assabiyah.

WHAT IS MEASURED, per cell of the grid:
  * headroom     — share of LED bands with cohesion_frac < 1 (the defect, directly)
  * spread       — sd of split_thr as a share of the cap (0 = every band gets the same threshold)
  * corr(g*, n)  — does the CV finally reach realized band size? v1/v2 read -0.22, v3 reads -0.08
  * band_med     — against Johnson [18-35] and Hill 25-30, so a "fix" that breaks the marker is visible

A candidate is only interesting if it restores the headroom AND leaves band_med defensible.

Run:  py -3 -u diag_cohesion_candidates.py
Env:  K_STEPS (300) K_N (1500) K_PATCH (30) K_SEEDS (0,1)
"""
import os
import statistics
import sys

ROOT = r"C:\Users\syatom\Projects\SiC Games"
for _p in (os.path.join(ROOT, "sic_games", "src"),
           os.path.join(ROOT, "sic_games", "outputs", "phase1_social_evolution"),
           os.path.join(ROOT, "sic_games", "outputs", "mechanism_battery")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import battery1_liveness as B1                                        # noqa: E402
from sic_games import runconfig                                       # noqa: E402

STEPS = int(os.environ.get("K_STEPS", "300"))
N = int(os.environ.get("K_N", "1500"))
PATCH = int(os.environ.get("K_PATCH", "30"))
SEEDS = [int(s) for s in os.environ.get("K_SEEDS", "0,1").split(",") if s]

# (label, config overrides)
CANDIDATES = [
    ("baseline",              {}),
    ("leaky",                 {"enable_leaky_assabiyah": True}),
    ("leaderw 0.5",           {"cohesion_leader_weight": 0.5}),
    ("leaderw 0.25",          {"cohesion_leader_weight": 0.25}),
    ("leaky + leaderw 0.5",   {"enable_leaky_assabiyah": True, "cohesion_leader_weight": 0.5}),
    ("leaky + leaderw 0.25",  {"enable_leaky_assabiyah": True, "cohesion_leader_weight": 0.25}),
    ("leaky + leaderw 0.1",   {"enable_leaky_assabiyah": True, "cohesion_leader_weight": 0.1}),
]
BAND_LO, BAND_HI = 18, 35          # Johnson / R-72
HILL_LO, HILL_HI = 25, 30          # Hill 2011 mean band


def corr(xs, ys):
    n = len(xs)
    if n < 3:
        return float("nan")
    mx, my = statistics.mean(xs), statistics.mean(ys)
    sx, sy = statistics.pstdev(xs), statistics.pstdev(ys)
    if sx == 0 or sy == 0:
        return float("nan")
    return sum((a - mx) * (b - my) for a, b in zip(xs, ys)) / (n * sx * sy)


def measure(over, seed):
    stack = dict(runconfig.load().get("DemographyConfig", {}))
    stack.update(over)
    w = B1._build(stack, n=N, patch=PATCH, terr="coastal", clim="temperate", seed=seed)
    for _ in range(STEPS):
        w.step()
        if not w.agent_list:
            return None
    cfg = w._demog
    cap = cfg.band_split_size
    cvf = w._return_cv_field()
    members = {}
    for a in w.agent_list:
        members.setdefault(a._group.band_id, []).append(a)
    rows = []
    for bid, ms in members.items():
        if len(ms) < 2:
            continue
        a_val = float(w._band_assabiyah.get(bid, 0.0))
        lead = float(w._band_leader_term.get(bid, 0.0))
        rep = float(w._band_repulsion.get(bid, 0.0))
        maln = float(w._band_malnutrition.get(bid, 0.0))
        raw = a_val + cfg.cohesion_leader_weight * lead - rep - maln
        coh = min(1.0, max(0.0, raw))
        g = sum(float(cvf[x.pos[1], x.pos[0]]) for x in ms) / len(ms) / cfg.cv_safe
        rows.append(dict(n=len(ms), a=a_val, lead=lead, coh=coh, g=g,
                         thr=g + max(0.0, cap - g) * coh))
    if len(rows) < 8:
        return None
    led = [r for r in rows if r["lead"] > 0.0]
    sizes = sorted(r["n"] for r in rows)
    return dict(
        n_bands=len(rows),
        headroom=(sum(1 for r in led if r["coh"] < 0.999) / len(led)) if led else float("nan"),
        med_assab=statistics.median(r["a"] for r in rows),
        thr_spread=statistics.pstdev(r["thr"] for r in rows) / cap,
        corr_g=corr([r["g"] for r in rows], [float(r["n"]) for r in rows]),
        band_med=statistics.median(sizes),
    )


def main():
    print(f"[cohesion candidates] n={N} patch={PATCH} steps={STEPS} seeds={SEEDS}")
    print(f"[cohesion candidates] the defect: cohesion_frac pinned at 1.0 for every LED band, so split_thr "
          f"== band_split_size and g* drops out\n")
    print(f"{'candidate':>22} {'headroom':>9} {'medAssab':>9} {'thrSpread':>10} {'corr(g*,n)':>11} "
          f"{'band_med':>9} {'in band':>8}")
    for label, over in CANDIDATES:
        got = [measure(over, s) for s in SEEDS]
        got = [g for g in got if g]
        if not got:
            print(f"{label:>22}   (all seeds collapsed)")
            continue
        hr = statistics.mean(g["headroom"] for g in got)
        ma = statistics.mean(g["med_assab"] for g in got)
        ts = statistics.mean(g["thr_spread"] for g in got)
        cg = statistics.mean(g["corr_g"] for g in got)
        bm = statistics.median([g["band_med"] for g in got])
        mark = "HILL" if HILL_LO <= bm <= HILL_HI else ("ok" if BAND_LO <= bm <= BAND_HI else "OUT")
        print(f"{label:>22} {hr*100:>8.1f}% {ma:>9.3f} {ts*100:>9.1f}% {cg:>+11.3f} {bm:>9.1f} {mark:>8}",
              flush=True)
    print("\nheadroom  = share of LED bands whose cohesion_frac is BELOW the clamp (0% = the defect)")
    print("thrSpread = sd of split_thr as % of band_split_size (0% = every band gets the same threshold)")
    print("corr(g*,n)= does the CV reach realized band size? v1/v2 measured -0.22, v3 measures -0.08")
    print("band_med  = Johnson [18-35], Hill 25-30. A candidate that restores headroom but breaks the marker")
    print("            is not a fix; both columns have to hold.")


if __name__ == "__main__":
    main()
