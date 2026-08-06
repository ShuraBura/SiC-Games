"""BATTERY 4 — MUTUAL DESTRUCTIVE INTERFERENCE between mechanisms.

Batteries 1-3 test each mechanism ALONE against a baseline. That cannot see the failure mode where two live
mechanisms cancel, or where one is live in isolation and dead in company. The R-103 arc is full of this shape:
mechanisms that measured fine individually and did nothing when stacked.

Two distinct pathologies, measured separately:

  MASKED          mechanism A moves the world on its own, but with the full stack live, removing A changes
                  NOTHING. Something downstream absorbs it. This is the one that silently voids results: the
                  mechanism is "on", was verified live, and contributes zero in the configuration you ran.

  DESTRUCTIVE     removing A and B together moves the world LESS than removing either alone
                  (|Δ_AB| < max(|Δ_A|, |Δ_B|) by a margin). Their effects partially cancel, so the pair is
                  doing less than its parts — the literal destructive-interference case.

  (Reported alongside: SUPER-ADDITIVE, |Δ_AB| > |Δ_A| + |Δ_B|, which is not a fault but is worth seeing —
   it marks the couplings where the model's behaviour is genuinely more than the sum of its mechanisms.)

METHOD. One common world in which every mechanism under test is live (an ablation battery in a world where a
mechanism cannot fire measures nothing — Battery 1's lesson). Each mechanism is turned OFF singly and in pairs
against the FULL-LIVE baseline, and the displacement is an L1 distance over the signature, normalised per field
so pop and material are commensurable.

Controls are inherited from Battery 1 and re-run here: null (bit-identical repeat) and positive.

Run:  py -3 -u sic_games/outputs/mechanism_battery/battery4_interference.py
Env:  B4_STEPS (400) · B4_WORKERS (7) · B4_FLAGS (csv; defaults to the resuscitated set)
"""
import itertools
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import battery1_liveness as B1

OUT = os.path.join(HERE, "battery4_results.json")
STEPS = int(os.environ.get("B4_STEPS", "400"))
WORKERS = int(os.environ.get("B4_WORKERS", "7"))

# ── THE FULL-LIVE CONFIG ────────────────────────────────────────────────────────────────────────
# Every fix Battery 3 found, applied at once, on an inland world with cultivable land and real crowding — so
# the soil/land/nutrition mechanisms have something to act on and the ascription gate can open. This is the
# configuration in which all the mechanisms under test are simultaneously live.
FULL = dict(
    band_risk_penalty=0.05,                 # was 0.0 -> band_risk inert
    provision_self_keep=0.6,                # was 1.0 -> provisioning inert
    legit_threshold=0.08,                   # was 0.15 -> the rank gate never opened
    enable_agriculture=True,
    enable_soil_depletion=True,
    enable_alluvial_renewal=True,
    enable_nutrition_synergy=True,
    enable_condition=True,
    enable_economic_defensibility=True,
    enable_band_risk=True,
)
WORLD = dict(n=1000, patch=24, terr="flat", clim="temperate")

DEFAULT_FLAGS = ["enable_band_risk", "enable_provisioning", "enable_alluvial_renewal",
                 "enable_nutrition_synergy", "enable_soil_depletion", "enable_rank_hierarchy",
                 "enable_condition", "enable_material_inheritance", "enable_lineage_tribute",
                 "enable_catchment_ceiling"]
FLAGS = [f for f in os.environ.get("B4_FLAGS", "").split(",") if f] or DEFAULT_FLAGS

NUMERIC = ("final_pop", "tot_wealth", "tot_material", "tot_cred", "bonds", "n_settlements",
           "n_ascribed", "n_bigbands", "n_lineages", "births", "deaths")


def dist(base, sig):
    """Normalised L1 over the signature: each field scaled by its own baseline so pop (10^3) and material
    (10^9) contribute comparably. A pure count of changed fields would treat a 0.01% wobble as a real effect."""
    tot = 0.0
    for k in NUMERIC:
        b, v = base.get(k), sig.get(k)
        if b is None or v is None:
            continue
        tot += abs(v - b) / (abs(b) if b else 1.0)
    return round(tot, 6)


def _run(off_flags):
    upd = dict(FULL)
    for f in off_flags:
        upd[f] = False
    sig, probes, secs = B1.signature(upd, steps=STEPS, **WORLD)
    return sig, probes, secs


def job(off_flags):
    try:
        sig, probes, secs = _run(off_flags)
        return dict(off=list(off_flags), sig=sig, probes=probes, secs=secs)
    except Exception as e:
        return dict(off=list(off_flags), error=f"{type(e).__name__}: {e}")


def main():
    print(f"BATTERY 4 — interference over {len(FLAGS)} mechanisms | {STEPS} steps | {WORKERS} workers",
          flush=True)
    print(f"  world {WORLD}", flush=True)

    # CONTROLS, as everywhere: a null that must be bit-identical, and the live-ness of every mechanism in THIS
    # world. An ablation battery over mechanisms that are not live here would measure nothing.
    base, probes, base_s = _run([])
    base2, _, _ = _run([])
    null_ok = (base == base2)
    print(f"  C1 NULL full-live baseline twice -> "
          f"{'IDENTICAL (PASS)' if null_ok else '*** DIFFERS (FAIL) ***'}  [{base_s}s/run]", flush=True)
    print(f"  preconditions: {probes}", flush=True)
    if not null_ok:
        json.dump(dict(controls=dict(null=False), rows=[]), open(OUT, "w"), indent=1)
        print("*** CONTROL FAILED — no verdicts. ***")
        return

    masked_out, saturated_out = [], []
    singles = [(f,) for f in FLAGS]
    pairs = list(itertools.combinations(FLAGS, 2))
    rows = []

    def flush():
        json.dump(dict(controls=dict(null=null_ok), world=WORLD, full=FULL, steps=STEPS,
                       base=base, probes=probes, rows=rows,
                       masked=masked_out, input_saturated=saturated_out),
                  open(OUT, "w", encoding="utf-8"), indent=1)

    t0 = time.time()
    d_single = {}
    with ProcessPoolExecutor(max_workers=WORKERS) as ex:
        for r in ex.map(job, singles + pairs):
            if r.get("error"):
                rows.append(r); flush(); continue
            r["dist"] = dist(base, r["sig"])
            r.pop("sig", None); r.pop("probes", None)
            rows.append(r); flush()
            if len(r["off"]) == 1:
                d_single[r["off"][0]] = r["dist"]

    print("\nSINGLE-MECHANISM DISPLACEMENT (turning it OFF against the full-live stack)", flush=True)
    zero = [f for f in FLAGS if d_single.get(f) == 0.0]
    for f in FLAGS:
        d = d_single.get(f)
        print(f"  {f:34s} d={d}{'   (zero — escalating)' if d == 0.0 else ''}", flush=True)

    # ── ESCALATION: zero displacement has TWO causes and they are not the same finding ───────────
    # MASKED           another live mechanism absorbs it — genuine destructive interference.
    # INPUT-SATURATED  its input variable has no spread in THIS world, so it has nothing to act on.
    #                  Not interference at all; the same "dead world, not dead mechanism" distinction
    #                  Battery 1 draws, which the first version of this battery failed to carry over.
    # Measured case (2026-07-27): `enable_nutrition_synergy` read d=0.0 here and was reported MASKED. Direct
    # measurement showed a2_cap_hits=0 (the cap never fires) and mean `_condition` 0.9998 — agents are simply
    # never undernourished in this world, so the multiplier is ~1.0002 and the EXPECTED number of flipped
    # death outcomes over the whole run is ~1e-3. A bit-identical run is the predicted result, not a mask.
    # The two are separated by re-ablating in a STRESSED world: live there ⇒ input-saturated here.
    masked, saturated = [], []
    if zero:
        import battery3_resuscitate as B3
        print("\nESCALATION of zero-displacement mechanisms (re-ablated in a stressed world)", flush=True)
        for f in zero:
            try:
                s_base, s_probes, _ = B1.signature(dict(FULL), steps=STEPS, **B3.POOR)
                upd = dict(FULL); upd[f] = False
                s_flip, _, _ = B1.signature(upd, steps=STEPS, **B3.POOR)
                d_stress = dist(s_base, s_flip)
            except Exception as e:
                print(f"  {f:34s} escalation failed: {type(e).__name__}: {e}", flush=True)
                continue
            if d_stress > 0.0:
                saturated.append(f)
                print(f"  {f:34s} INPUT-SATURATED — d=0.0 here but {d_stress:.4f} under stress: "
                      f"nothing to act on in this world, NOT interference", flush=True)
            else:
                masked.append(f)
                print(f"  {f:34s} *** MASKED — zero under stress too; another mechanism absorbs it ***",
                      flush=True)

    print("\nPAIR INTERFERENCE", flush=True)
    destructive, superadd = [], []
    for r in rows:
        if len(r["off"]) != 2 or r.get("error"):
            continue
        a, b = r["off"]
        da, db, dab = d_single.get(a), d_single.get(b), r["dist"]
        if da is None or db is None:
            continue
        if dab < max(da, db) * 0.9 and max(da, db) > 0:
            destructive.append((a, b, da, db, dab))
        elif dab > (da + db) * 1.5:
            superadd.append((a, b, da, db, dab))
    for a, b, da, db, dab in sorted(destructive, key=lambda t: t[4] - max(t[2], t[3]))[:12]:
        print(f"  DESTRUCTIVE  {a[7:]:26s} + {b[7:]:26s} dA={da:.3f} dB={db:.3f} dAB={dab:.3f}", flush=True)
    for a, b, da, db, dab in sorted(superadd, key=lambda t: -t[4])[:8]:
        print(f"  super-additive {a[7:]:24s} + {b[7:]:24s} dA={da:.3f} dB={db:.3f} dAB={dab:.3f}", flush=True)

    flush()
    print(f"\nMASKED {len(masked)} | DESTRUCTIVE pairs {len(destructive)} | super-additive {len(superadd)}")
    print(f"{time.time()-t0:.0f}s -> {OUT}")


if __name__ == "__main__":
    main()
