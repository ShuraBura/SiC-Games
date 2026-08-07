"""BATTERY 6 — STRESS. Design + rationale in `DESIGN_stress_battery.md`; read that first.

Batteries 1-5 test the MIDDLE of the range. Every real defect this project has found lived at an EXTREME: the
R-105 runaway after 1750 steps at high density, the cred-ablation ZeroDivisionError when a variable reached
zero, the budding cascade at 400+ settlements. None is reachable by testing typical settings.

STAGES (cheap crash-finders first, so a defect is known before hours of benchmark arms are spent on a broken
substrate):
  S1 ABLATION    every mechanism OFF one at a time - does it SURVIVE, not does it do something
  S2 EXTREMES    every gain at the bounds of its declared range (0 and 10x where none is declared - and
                 THAT is itself reported, since an undeclared range is a finding)
  S3 ENVELOPE    degenerate/extreme worlds; also produces the REGIME MAP Battery 1 lacked
  S5 CONSERVE    rides on S1-S3: quantities finite, non-negative, and checked PER CAPITA (Battery 2's
                 totals-based check produced a false positive when population moved 10%)

S4 (benchmark envelope) and S6 (long-horizon drift) are the multi-hour stages and live in
`battery6_long.py` so this file stays a fast pre-flight.

Run:  py -3 -u sic_games/outputs/mechanism_battery/battery6_stress.py
Env:  S_STEPS (400) · S_WORKERS (7) · S_ONLY (s1,s2,s3)
"""
import json
import math
import os
import sys
import time
import traceback
from concurrent.futures import ProcessPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import battery1_liveness as B1

OUT = os.path.join(HERE, "battery6_results.json")
STEPS = int(os.environ.get("S_STEPS", "400"))
WORKERS = int(os.environ.get("S_WORKERS", "7"))
ONLY = [s for s in os.environ.get("S_ONLY", "").split(",") if s]

# The full-live stack: every Battery 3 fix applied, on a world with room and resources, so a mechanism that
# fails is failing on its own account and not for want of a world.
FULL = dict(B1.VILLAGE)
FULL.update(B1.ELITE)
FULL.update(provision_self_keep=0.6, enable_agriculture=True,
            enable_soil_depletion=True, enable_alluvial_renewal=True, enable_economic_defensibility=True,
            enable_village_budding=True, enable_bud_hazard=True)
WORLD = dict(n=800, patch=24, terr="flat", clim="temperate")

# S3 — the operating envelope. Extinction is a VALID outcome here; an exception is not.
ENVELOPE = [
    ("tiny_10agents", dict(n=10, patch=24, terr="coastal", clim="temperate")),
    ("small_60", dict(n=60, patch=18, terr="coastal", clim="temperate")),
    ("dense_6000", dict(n=6000, patch=24, terr="coastal", clim="temperate")),
    ("dead_boreal", dict(n=600, patch=18, terr="flat", clim="boreal")),
    ("max_tropical", dict(n=600, patch=40, terr="coastal", clim="tropical")),
    ("circumscribed_p12", dict(n=600, patch=12, terr="coastal", clim="temperate")),
    ("unbounded_p60", dict(n=600, patch=60, terr="flat", clim="temperate")),
    ("hilly_temperate", dict(n=600, patch=24, terr="hilly", clim="temperate")),
]

QUANT = ("final_pop", "tot_wealth", "tot_material", "tot_cred", "bonds", "n_settlements",
         "n_ascribed", "n_bigbands", "n_lineages", "births", "deaths", "n_owned", "n_claims")


def s5_check(sig):
    """S5 CONSERVATION, per capita. Battery 2 flagged an exchange operator for moving TOTAL wealth -9.3% when
    the population had moved -9.9% and per-capita wealth was flat: totals are not the invariant. Everything
    here is either a count or normalised by population."""
    bad = []
    pop = sig.get("final_pop") or 0
    for k in QUANT:
        v = sig.get(k)
        if v is None:
            continue
        if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
            bad.append(f"{k} is {v}")
        elif v < 0:
            bad.append(f"{k} negative ({v})")
    if pop > 0:
        for k in ("tot_wealth", "tot_material", "tot_cred"):
            v = sig.get(k)
            if v is not None and pop and (v / pop) < 0:
                bad.append(f"{k} per capita negative")
    return bad


def _run(update, world=None, steps=None):
    return B1.signature(update, steps=steps or STEPS, **(world or WORLD))


# ── S1 ─────────────────────────────────────────────────────────────────────────────────────────
def s1_one(flag):
    upd = dict(FULL)
    if flag not in upd and not getattr(B1.baseline_cfg(), flag, False):
        return dict(stage="S1", flag=flag, verdict="SKIP", note="already off in the full-live stack")
    upd[flag] = False
    try:
        sig, probes, secs = _run(upd)
    except Exception as e:
        return dict(stage="S1", flag=flag, verdict="CRASH", error=f"{type(e).__name__}: {e}",
                    tb=traceback.format_exc()[-400:])
    bad = s5_check(sig)
    if bad:
        return dict(stage="S1", flag=flag, verdict="INVARIANT", note="; ".join(bad))
    if sig["final_pop"] == 0:
        return dict(stage="S1", flag=flag, verdict="EXTINCT", pop=0, secs=secs)
    return dict(stage="S1", flag=flag, verdict="OK", pop=sig["final_pop"], secs=secs)


# ── S2 ─────────────────────────────────────────────────────────────────────────────────────────
def _bounds(name):
    """Declared range from the pydantic Field, else (0, 10x default) — and the ABSENCE of a declared range is
    itself reported, since a parameter with no documented bounds has never had one thought about."""
    from sic_games.demography import DemographyConfig
    f = DemographyConfig.model_fields[name]
    lo = hi = None
    for m in f.metadata:
        t = type(m).__name__
        if t == "Ge":
            lo = m.ge
        elif t == "Gt":
            # STRICTLY greater: the bound itself is ILLEGAL, so testing it is testing the schema, not the
            # model. The first run of S2 reported 4 "crashes" that were exactly this — my error, not defects.
            lo = m.gt + (abs(m.gt) * 1e-6 if m.gt else 1e-6)
        elif t == "Le":
            hi = m.le
        elif t == "Lt":
            hi = m.lt - (abs(m.lt) * 1e-6 if m.lt else 1e-6)
    d = f.default
    declared = (lo is not None and hi is not None)
    if lo is None:
        lo = 0.0 if d >= 0 else 10.0 * d
    if hi is None:
        hi = (10.0 * d) if d else 1.0
    return lo, hi, declared


def s2_one(item):
    name, which = item
    lo, hi, declared = _bounds(name)
    val = lo if which == "min" else hi
    if isinstance(_default(name), int) and not isinstance(_default(name), bool):
        val = int(val)
    upd = dict(FULL); upd[name] = val
    try:
        sig, probes, secs = _run(upd)
    except Exception as e:
        return dict(stage="S2", param=name, at=which, value=val, declared_range=declared,
                    verdict="CRASH", error=f"{type(e).__name__}: {e}")
    bad = s5_check(sig)
    if bad:
        return dict(stage="S2", param=name, at=which, value=val, declared_range=declared,
                    verdict="INVARIANT", note="; ".join(bad))
    # runaway: the bounded patch cannot host an unbounded population (R-105's signature)
    dens = sig["final_pop"] / 560.0
    if dens > 40:
        return dict(stage="S2", param=name, at=which, value=val, declared_range=declared,
                    verdict="RUNAWAY", pop=sig["final_pop"], density=round(dens, 1))
    if sig["final_pop"] == 0:
        return dict(stage="S2", param=name, at=which, value=val, declared_range=declared,
                    verdict="EXTINCT")
    return dict(stage="S2", param=name, at=which, value=val, declared_range=declared,
                verdict="OK", pop=sig["final_pop"])


def _default(name):
    from sic_games.demography import DemographyConfig
    return DemographyConfig.model_fields[name].default


# ── S3 ─────────────────────────────────────────────────────────────────────────────────────────
def s3_one(item):
    label, world = item
    try:
        sig, probes, secs = _run(dict(FULL), world=world)
    except Exception as e:
        return dict(stage="S3", world=label, verdict="CRASH", error=f"{type(e).__name__}: {e}",
                    tb=traceback.format_exc()[-400:])
    bad = s5_check(sig)
    v = "OK"
    if bad:
        v = "INVARIANT"
    elif sig["final_pop"] == 0:
        v = "EXTINCT-graceful"          # a valid outcome; only an exception is a defect
    return dict(stage="S3", world=label, verdict=v, note="; ".join(bad) if bad else "",
                pop=sig["final_pop"], secs=secs,
                # the REGIME MAP: which preconditions this world satisfies, so INERT elsewhere can be read
                # as "untestable there" rather than "dead"
                probes={k: (1 if p else 0) for k, p in probes.items()})


def main():
    from sic_games.demography import DemographyConfig
    rows = []

    def flush():
        json.dump(dict(full=FULL, world=WORLD, steps=STEPS, rows=rows),
                  open(OUT, "w", encoding="utf-8"), indent=1, default=str)

    print(f"BATTERY 6 — STRESS | {STEPS} steps | {WORKERS} workers", flush=True)
    # CONTROLS FIRST, as everywhere: an instrument that cannot detect is not evidence of anything.
    b1, _, s = _run(dict(FULL))
    b2, _, _ = _run(dict(FULL))
    print(f"  C1 NULL full-live twice -> {'IDENTICAL (PASS)' if b1 == b2 else '*** DIFFERS (FAIL) ***'} "
          f"[{s}s/run, pop {b1['final_pop']}]", flush=True)
    if b1 != b2:
        print("*** CONTROL FAILED — no verdicts emitted. ***"); return

    t0 = time.time()
    if not ONLY or "s1" in ONLY:
        flags = sorted(k for k in DemographyConfig.model_fields if k.startswith("enable_"))
        print(f"\nS1 ABLATION — {len(flags)} mechanisms off one at a time", flush=True)
        with ProcessPoolExecutor(max_workers=WORKERS) as ex:
            for r in ex.map(s1_one, flags):
                rows.append(r); flush()
                if r["verdict"] not in ("OK", "SKIP"):
                    print(f"   !! {r['flag']:38s} {r['verdict']} {r.get('error') or r.get('note','')}",
                          flush=True)
        bad = [r for r in rows if r["stage"] == "S1" and r["verdict"] not in ("OK", "SKIP")]
        print(f"  S1: {sum(1 for r in rows if r.get('verdict') == 'OK')} OK, {len(bad)} problem(s)", flush=True)

    if not ONLY or "s2" in ONLY:
        params = [k for k, v in DemographyConfig.model_fields.items()
                  if isinstance(v.default, (int, float)) and not isinstance(v.default, bool)]
        items = [(p, w) for p in sorted(params) for w in ("min", "max")]
        print(f"\nS2 EXTREMES — {len(params)} parameters x 2 bounds", flush=True)
        with ProcessPoolExecutor(max_workers=WORKERS) as ex:
            for r in ex.map(s2_one, items):
                rows.append(r); flush()
                if r["verdict"] != "OK":
                    print(f"   !! {r['param']:34s} @{r['at']:3s}={r['value']!s:12s} {r['verdict']} "
                          f"{r.get('error') or r.get('note') or r.get('density','')}", flush=True)
        s2 = [r for r in rows if r["stage"] == "S2"]
        undecl = sorted({r["param"] for r in s2 if not r["declared_range"]})
        print(f"  S2: {sum(1 for r in s2 if r['verdict'] == 'OK')}/{len(s2)} OK | "
              f"{len(undecl)} parameter(s) have NO declared range", flush=True)

    if not ONLY or "s3" in ONLY:
        print(f"\nS3 ENVELOPE — {len(ENVELOPE)} extreme worlds", flush=True)
        with ProcessPoolExecutor(max_workers=min(WORKERS, len(ENVELOPE))) as ex:
            for r in ex.map(s3_one, ENVELOPE):
                rows.append(r); flush()
                live = [k for k, v in (r.get("probes") or {}).items() if v]
                print(f"   {r['world']:20s} {r['verdict']:18s} pop {r.get('pop')} "
                      f"| units present: {','.join(live) if live else 'NONE'}", flush=True)

    flush()
    print(f"\n{'=' * 70}")
    for v in ("CRASH", "INVARIANT", "RUNAWAY", "EXTINCT"):
        got = [r for r in rows if r.get("verdict") == v]
        if got:
            print(f"{v:11s} {len(got):3d}  " + ", ".join(sorted({r.get('flag') or r.get('param') or r.get('world')
                                                                for r in got})[:12]))
    print(f"\n{time.time() - t0:.0f}s -> {OUT}")


if __name__ == "__main__":
    main()
