"""R-97 — does the working elite layer actually CYCLE? Applying R-87's validated detector to the campaign arms.

This is the question the whole R-82…R-96 arc exists to answer. R-58…R-71 produced THREE independent negatives
for secular cycles from the subsistence base, and the standing conclusion was that cycles would need an explicit
Turchin elite layer. That layer now works (R-96: nobility and revolts coexist in a patchwork). So: does it cycle?

INSTRUMENT REUSED, NOT REBUILT. `probe_hcycles.period_of` is the detector fixed twice and supervisor-approved in
R-87c/d: linear detrend (undetrended drift dragged a REAL cycle from ac_peak 0.43 to 0.11), period capped at
window/3 (the unfixed version returned a 269 yr "period" from a 300 yr window — one arc, not a cycle), and a
genuine local maximum required (argmax alone makes pure drift always report a peak).

NULL FLOOR, from R-87's own calibration against white noise: ac_peak mean 0.03, p95 0.13, max 0.19. **Compare
against 0.13, not against an invented cut-off** — using an invented 0.2 was the original R-87c error.

D1 IS THE POINT OF THIS SCRIPT. The campaign snapshots every 25 steps give only ~121 points, far coarser than
the series R-87 validated on. A NEGATIVE from an underpowered detector is worthless, so the positive control
below asks: at THIS length and sampling, would a cycle of the size we care about be found at all? If the control
fails, the arms cannot be interpreted and the honest output is "instrument insufficient", not "no cycles".
"""
import json, os, sys
import numpy as np

HERE = os.path.dirname(__file__)
# probe_hcycles imports the whole model stack at module scope, so import the FUNCTION by source rather than the
# module — this must be the R-87c/d detector unmodified, not a reimplementation of it.
sys.path.insert(0, os.path.join(HERE, "..", "phase1_social_evolution"))
sys.path.insert(0, os.path.join(HERE, "..", "phase1_biome_mortality"))
try:
    from probe_hcycles import period_of                 # preferred: the real module
except Exception:
    import types
    _src = open(os.path.join(HERE, "..", "phase1_biome_mortality", "probe_hcycles.py"), encoding="utf-8").read()
    _start = _src.index("def period_of(")
    _end = _src.index("\nif __name__", _start)
    _mod = types.ModuleType("_hc")
    exec(compile(_src[_start:_end], "probe_hcycles.py:period_of", "exec"), _mod.__dict__)
    period_of = _mod.period_of
    print("(detector lifted verbatim from probe_hcycles.py; model stack not importable here)")

NULL_P95 = 0.13          # R-87 calibrated false-positive floor for ac_peak
SAMPLE_EVERY = 25        # campaign C_LOGEVERY

ARMS = [("coastal (R-96)", "r96"),
        ("tropical, no soil", "bio_nosoil"),
        ("tropical, rot OFF", "bio_swidden"),
        ("TRUE swidden", "bio_swidden_true")]


def load(tag, key="frac_gumsa"):
    p = os.path.join(HERE, f"campaign_trajectory_{tag}.json")
    return [r.get(key, 0.0) for r in json.load(open(p))["traj"]]


def control(n, period_steps, amp, noise_sd, rng):
    """A cycle of KNOWN period injected into noise of the OBSERVED magnitude, at the OBSERVED series length."""
    t = np.arange(n, dtype=float) * SAMPLE_EVERY
    return 0.8 + amp * np.sin(2 * np.pi * t / period_steps) + noise_sd * rng.standard_normal(n)


if __name__ == "__main__":
    rng = np.random.default_rng(0)
    series = {tag: load(tag) for _, tag in ARMS}
    n = min(len(v) for v in series.values())
    obs_sd = float(np.mean([np.std(v) for v in series.values()]))
    print(f"series length {n} points @ {SAMPLE_EVERY} steps = {n*SAMPLE_EVERY} yr; "
          f"resolvable period cap = window/3 = {n*SAMPLE_EVERY//3} yr")
    print(f"observed sd of frac_gumsa across arms: {obs_sd:.3f}\n")

    # ── D1 POSITIVE CONTROL, at this exact length and sampling ──────────────────────────────────────
    print("=== POSITIVE CONTROL: can this detector see a cycle in a series this short? ===")
    print(f"{'period_yr':>10} {'amp':>6} {'found_yr':>9} {'ac_peak':>8}  verdict")
    ok = 0
    for per_yr in (200, 300, 500):
        for amp in (0.30, 0.15, 0.08):
            peaks, pers = [], []
            for _ in range(20):
                y = control(n, per_yr, amp, obs_sd, rng)
                p, a = period_of(y, sample_every=SAMPLE_EVERY)
                peaks.append(a); pers.append(p if p else np.nan)
            mp = float(np.nanmean(peaks)); mper = float(np.nanmean(pers))
            hit = mp > NULL_P95
            ok += hit
            print(f"{per_yr:>10} {amp:>6.2f} {mper:>9.0f} {mp:>8.3f}  {'DETECTED' if hit else 'missed'}")
    print(f"\n  -> detector clears the {NULL_P95} null floor in {ok}/9 injected-cycle cases")
    if ok == 0:
        print("  -> INSTRUMENT INSUFFICIENT at this resolution; no verdict on the arms is possible.")

    # ── the arms ────────────────────────────────────────────────────────────────────────────────────
    print(f"\n=== THE ARMS (null floor {NULL_P95}) ===")
    print(f"{'arm':>20} {'sd':>7} {'period_yr':>10} {'ac_peak':>8}  verdict")
    for lab, tag in ARMS:
        v = series[tag]
        p, a = period_of(v, sample_every=SAMPLE_EVERY)
        verdict = "CYCLE clears null" if (p and a > NULL_P95) else ("below null floor" if p else "no turning point")
        print(f"{lab:>20} {np.std(v):>7.3f} {str(p) if p else '-':>10} {a:>8.3f}  {verdict}")
