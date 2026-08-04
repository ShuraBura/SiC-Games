"""WHY doesn't `band_med` respond to `cv_safe`? Instrument the terms instead of turning another knob.

THE OBSERVATION (2026-08-04). On the full stack, raising `cv_safe` from 0.037 to 0.045 (+22%) moved
`band_med` by -1.9% (paired, 3 worlds x 2 seeds). If band size were set by the risk-pooling optimum
g* = CV/cv_safe, a +22% rise in the denominator should have cut it by ~18%. It did not, so g* is NOT what
sets realized band size on this stack, and re-fitting `cv_safe` would be turning a knob that is not connected
to the thing being fixed. The project's own rule: a flat diagnostic means instrument the cause first.

THE HYPOTHESIS TO TEST. The tolerable size is

    split_thr = g* + max(0, cap - g*) * cohesion_frac,     cohesion_frac = clamp01(a + leader - rep - maln)

with `cap = band_split_size = 45`. As cohesion_frac -> 1 the expression collapses to `cap` and g* drops out
entirely. The elite layer supplies the leader term, so a FULL stack may be pinning cohesion_frac at its
ceiling — in which case band size is governed by the hard cap, not by the CV, and `cv_safe` is inert by
construction rather than mis-fitted.

WHAT THIS PRINTS, per band, from the model's own stored state (`_band_assabiyah`, `_band_leader_term`,
`_band_repulsion`, `_band_malnutrition`) so nothing is re-derived by hand:
  * the distribution of cohesion_frac, and the SHARE PINNED AT 1.0 (the hypothesis, directly)
  * g*, split_thr and realized size, and corr(g*, size) — v1/v2 measured -0.22, which is what the linear
    law was supposed to fix
  * how much of split_thr's spread survives once cohesion_frac is accounted for

Run:  py -3 -u diag_band_size_terms.py
Env:  D_STEPS (400) D_N (2500) D_PATCH (40)
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

import battery1_liveness as B1                                       # noqa: E402

STEPS = int(os.environ.get("D_STEPS", "400"))
N = int(os.environ.get("D_N", "2500"))
PATCH = int(os.environ.get("D_PATCH", "40"))

# The two mechanisms the +22% was attributed to, plus the elite layer that supplies the leader term.
# B1.VILLAGE + B1.ELITE are applied by `_build`; this adds what C_ALLON turns on for band dynamics.
STACK = dict(enable_emergent_band_size=True, enable_resource_directed_fusion=True,
             enable_dynamic_bands=True, enable_band_affiliation=True,
             enable_size_repulsion=True, enable_village_scaling=True,
             enable_malnutrition_fission=True)


def pct(xs, p):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(p * len(xs)))]


def corr(xs, ys):
    n = len(xs)
    if n < 3:
        return float("nan")
    mx, my = statistics.mean(xs), statistics.mean(ys)
    sx, sy = statistics.pstdev(xs), statistics.pstdev(ys)
    if sx == 0 or sy == 0:
        return float("nan")
    return sum((a - mx) * (b - my) for a, b in zip(xs, ys)) / (n * sx * sy)


def main():
    print(f"[band terms] building n={N} patch={PATCH}, stepping {STEPS}", flush=True)
    w = B1._build(STACK, n=N, patch=PATCH, terr="coastal", clim="temperate")
    for i in range(STEPS):
        w.step()
        if not w.agent_list:
            print("population collapsed"); return
        if (i + 1) % 100 == 0:
            print(f"  step {i+1}: pop={len(w.agent_list)}", flush=True)

    cfg = w._demog
    cap = cfg.band_split_size
    cvf = w._return_cv_field()      # the model's own accessor (phase1_model:3864), not a guessed attribute
    members = {}
    for a in w.agent_list:
        members.setdefault(a._group.band_id, []).append(a)

    rows = []
    for bid, ms in members.items():
        if len(ms) < 2:
            continue
        a_val = w._band_assabiyah.get(bid, 0.0)
        lead = w._band_leader_term.get(bid, 0.0)
        rep = w._band_repulsion.get(bid, 0.0)
        maln = w._band_malnutrition.get(bid, 0.0)
        raw = a_val + lead - rep - maln
        coh = min(1.0, max(0.0, raw))
        g = None
        if cvf is not None:
            g = sum(float(cvf[x.pos[1], x.pos[0]]) for x in ms) / len(ms) / cfg.cv_safe
        base_b = g if g is not None else cfg.band_base_tolerable
        thr = base_b + max(0.0, cap - base_b) * coh
        # Surplus is what drives assabiyah; its FIXED POINT is `gain*surplus = decay`, i.e. surplus_frac
        # = decay/gain. Above that ratio assabiyah climbs until the min(1.0, ...) clamp and stays there.
        rows.append(dict(n=len(ms), a=a_val, lead=lead, rep=rep, maln=maln, raw=raw, coh=coh,
                         g=g, thr=thr, surp=w._band_surplus.get(bid, 0.0)))

    if not rows:
        print("no multi-member bands"); return
    print(f"\n{len(rows)} bands | band_split_size cap = {cap} | cv_safe = {cfg.cv_safe}")

    def line(name, key, fmt="{:.3f}"):
        xs = [r[key] for r in rows if r[key] is not None]
        if not xs:
            print(f"  {name:16s} (none)"); return
        print(f"  {name:16s} min " + fmt.format(min(xs)) + "  p25 " + fmt.format(pct(xs, .25))
              + "  med " + fmt.format(statistics.median(xs)) + "  p75 " + fmt.format(pct(xs, .75))
              + "  max " + fmt.format(max(xs)))

    print("\nDISTRIBUTIONS")
    line("band size", "n", "{:.1f}")
    line("g* = CV/cv_safe", "g", "{:.1f}")
    line("split_thr", "thr", "{:.1f}")
    line("cohesion_frac", "coh")
    line("  assabiyah", "a")
    line("  leader term", "lead")
    line("  repulsion", "rep")
    line("  malnutrition", "maln")
    line("raw (unclamped)", "raw")
    line("band surplus_frac", "surp")

    # Assabiyah is `a += gain*surplus - decay`, clamped to [0,1]. Its fixed point is surplus = decay/gain;
    # ABOVE that ratio it climbs to the clamp and stays. So the share of bands above decay/gain is the share
    # for which assabiyah is a CONSTANT 1.0 rather than a state variable.
    ratio = cfg.assabiyah_decay / cfg.assabiyah_gain if cfg.assabiyah_gain > 0 else float("inf")
    above = sum(1 for r in rows if r["surp"] > ratio)
    print(f"\n  assabiyah fixed point: surplus_frac = decay/gain = {cfg.assabiyah_decay}/"
          f"{cfg.assabiyah_gain} = {ratio:.2f}")
    print(f"  bands ABOVE it (assabiyah pinned at 1.0 by construction): {above}/{len(rows)} "
          f"({100*above/len(rows):.1f}%)")

    pinned = sum(1 for r in rows if r["coh"] >= 0.999)
    over = sum(1 for r in rows if r["raw"] > 1.0)
    print(f"\nTHE HYPOTHESIS")
    print(f"  cohesion_frac PINNED at 1.0 : {pinned}/{len(rows)} bands ({100*pinned/len(rows):.1f}%)")
    print(f"  raw term ALREADY > 1 before clamping: {over}/{len(rows)} ({100*over/len(rows):.1f}%)")
    thr = [r["thr"] for r in rows]
    print(f"  split_thr spread: sd {statistics.pstdev(thr):.2f} on a cap of {cap} "
          f"({100*statistics.pstdev(thr)/cap:.1f}% of cap)")
    if pinned / len(rows) > 0.8:
        print(f"  => split_thr collapses to the CAP for {100*pinned/len(rows):.0f}% of bands, so g* — and "
              f"therefore cv_safe — cannot set band size. The cap is the lever.")

    gs = [r["g"] for r in rows if r["g"] is not None]
    ns = [r["n"] for r in rows if r["g"] is not None]
    print(f"\n  corr(g*, realized size)      = {corr(gs, ns):+.3f}   (v1/v2 measured -0.22; the linear law "
          f"was meant to fix this)")
    print(f"  corr(split_thr, realized size) = "
          f"{corr([r['thr'] for r in rows], [r['n'] for r in rows]):+.3f}")
    print(f"  corr(cohesion_frac, size)      = "
          f"{corr([r['coh'] for r in rows], [r['n'] for r in rows]):+.3f}")
    big = sum(1 for r in rows if r["n"] > cap)
    print(f"\n  bands ABOVE the hard cap {cap}: {big}/{len(rows)} — fission is applied after growth, so a "
          f"steady state sits just under the threshold it is chasing")

    # With cohesion_frac == 1 the threshold reduces to `g* + max(0, cap - g*)` = max(g*, cap): the cap is a
    # FLOOR on the threshold, not a ceiling. So cv_safe can only act through the bands whose g* exceeds the
    # cap — which is why the sweep measured an elasticity of -0.14 instead of the law's -1.0.
    gs2 = [r["g"] for r in rows if r["g"] is not None]
    if gs2:
        above_cap = sum(1 for g in gs2 if g > cap)
        print(f"\n  with cohesion pinned, split_thr == max(g*, {cap}). Bands with g* > {cap}: "
              f"{above_cap}/{len(gs2)} ({100*above_cap/len(gs2):.1f}%) — the ONLY ones cv_safe can move.")


if __name__ == "__main__":
    main()
