"""BATTERY 2 — does a (resuscitated) mechanism PERFORM, and what does it cost?

Battery 1 answers "does flipping this change anything". That is liveness, not performance. A mechanism can move
the signature and still be doing the wrong thing — R-82's aggrandizer capture was live and inert-in-effect
because it operated on a unit of size 1-2, and R-103's classifier was live while keying on the wrong quantity.

So this battery reports, per mechanism, two different things and never conflates them:

  (a) DOES IT PERFORM ITS DECLARED JOB
      · WHICH quantities it moves and by how much (signed, relative) — so "it moved something" can be checked
        against "it moved the thing it claims to move";
      · its CHARTER-TYPE INVARIANT where a black-box test can decide it:
            X  Exchange     Σ of the moved quantity conserved vs baseline (to tolerance)
            P  Production   the quantity it sources does not exceed what the field can supply
            D  Dissipation  the quantity it destroys is non-increasing
            A  Affiliation  no conserved quantity moved, AND the graph demonstrably changed
        MECHANISM_CHARTER §6.2 is explicit that A-type conservation is NOT decidable black-box over a long
        coupled run (changing the band graph changes who eats), so A verdicts are reported as INDICATIVE only.

  (b) WHAT IT COSTS
      Δ wall-seconds vs the baseline run, per mechanism, plus the aggregate for the whole resuscitated set —
      the number that sets the next overnight's budget.

Run:  py -3 -u sic_games/outputs/mechanism_battery/battery2_benchmark.py
Env:  B2_FLAGS (csv, required) · B2_STEPS (400) · B2_N (600) · B2_PATCH (24) · B2_SEED (0) · B2_WORKERS (6)
"""
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "sic_games", "outputs", "phase1_biome_mortality"))

import battery1_liveness as B1                                          # regime, baseline, signature, controls

STEPS = int(os.environ.get("B2_STEPS", "400"))
WORKERS = int(os.environ.get("B2_WORKERS", "6"))
FLAGS = [f for f in os.environ.get("B2_FLAGS", "").split(",") if f]
OUT = os.path.join(HERE, "battery2_results.json")

# Quantities each charter type is answerable for, in signature terms.
CONSERVED = ("tot_material", "tot_wealth", "tot_cred")
GRAPH = ("pop_hash", "bonds", "n_settlements", "n_lineages")


def charter_type(flag):
    try:
        import audit_flag_invariants as A
        return A.TYPES.get(flag, "?")
    except Exception:
        return "?"


def bench(flag):
    # A RESUSCITATED mechanism must be benchmarked UNDER ITS RECIPE — benchmarking it in the regime where it was
    # inert would just re-measure the inertness. Baseline is rebuilt under the same recipe so the comparison
    # isolates the mechanism and not the recipe.
    import battery3_resuscitate as B3
    why, extra, world = B3.RECIPES.get(flag, (None, None, None))
    extra = dict(extra or {})
    world = dict(world or {})
    base_sig, _, base_s = (B1.signature(extra, steps=STEPS, **world) if (extra or world) else B1._baseline())
    cfg = B1.baseline_cfg()
    cur = getattr(cfg, flag, None)
    if cur is None:
        return dict(flag=flag, error="not a config field")
    upd = dict(extra)
    upd[flag] = (not cur)
    if not cur:
        MAG, _ = B1._magnitudes()
        upd.update(MAG.get(flag, {}))
        upd.update(extra)
    try:
        sig, _, secs = B1.signature(upd, steps=STEPS, **world)
    except Exception as e:
        return dict(flag=flag, error=f"{type(e).__name__}: {e}")

    deltas = {}
    for k, v in base_sig.items():
        if k.endswith("_hash") or not isinstance(v, (int, float)):
            deltas[k] = ("changed" if sig[k] != v else "same")
            continue
        d = sig[k] - v
        deltas[k] = dict(base=round(v, 4), flip=round(sig[k], 4), delta=round(d, 4),
                         pct=(round(100.0 * d / v, 2) if v else None))

    ty = charter_type(flag)
    verdict = []
    moved_q = [q for q in CONSERVED
               if isinstance(deltas.get(q), dict) and abs(deltas[q]["delta"]) > 1e-6]
    moved_g = [g for g in GRAPH if deltas.get(g) == "changed"
               or (isinstance(deltas.get(g), dict) and abs(deltas[g]["delta"]) > 0)]
    if ty == "A":
        if moved_q:
            verdict.append(f"INDICATIVE A-violation (moved {moved_q}) — §6.2: not decidable black-box")
        if not moved_g:
            verdict.append("GRAPH-INERT — typed A but no graph field moved")
    elif ty == "X":
        # An exchange REDISTRIBUTES: totals should be far less affected than the distribution. A large swing in
        # the total is evidence the operator is sourcing or destroying, not exchanging.
        for q in moved_q:
            p = deltas[q]["pct"]
            if p is not None and abs(p) > 5.0:
                verdict.append(f"X moved TOTAL {q} by {p:+.1f}% — an exchange should redistribute, not create")
    elif ty == "D":
        for q in moved_q:
            if deltas[q]["delta"] > 0:
                verdict.append(f"D INCREASED {q} (+{deltas[q]['delta']}) — a sink must be non-increasing")
    return dict(flag=flag, type=ty, baseline_on=cur, secs=secs, base_secs=base_s,
                cost_delta_s=round(secs - base_s, 1),
                cost_pct=(round(100.0 * (secs - base_s) / base_s, 1) if base_s else None),
                moved=[k for k, v in deltas.items()
                       if v == "changed" or (isinstance(v, dict) and v["delta"] != 0)],
                deltas=deltas, invariant_flags=verdict)


def main():
    if not FLAGS:
        print("B2_FLAGS is required (csv of enable_* flags)."); return
    print(f"BATTERY 2 — performance of {len(FLAGS)} mechanisms | {STEPS} steps | {WORKERS} workers", flush=True)
    rows = []

    def flush():
        json.dump(dict(steps=STEPS, rows=rows), open(OUT, "w", encoding="utf-8"), indent=1)

    t0 = time.time()
    with ProcessPoolExecutor(max_workers=WORKERS) as ex:
        for i, r in enumerate(ex.map(bench, FLAGS), 1):
            rows.append(r); flush()
            if r.get("error"):
                print(f"{i:3d}/{len(FLAGS)} {r['flag']:40s} ERROR {r['error']}", flush=True)
                continue
            print(f"{i:3d}/{len(FLAGS)} {r['flag']:40s} [{r['type']}] cost {r['cost_delta_s']:+.1f}s "
                  f"({r['cost_pct']:+.0f}%) moved {len(r['moved'])} fields"
                  + (f"  !! {'; '.join(r['invariant_flags'])}" if r["invariant_flags"] else ""), flush=True)
    flush()
    tot = sum(r.get("cost_delta_s", 0) or 0 for r in rows)
    print(f"\naggregate added cost of this set: {tot:+.1f}s on a {rows[0].get('base_secs')}s baseline run")
    print(f"{time.time()-t0:.0f}s -> {OUT}")


if __name__ == "__main__":
    main()
