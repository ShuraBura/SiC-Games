"""The cohesion budget has no headroom — pinned as a FACT about the model, not as a passing feature.

R-106 Addendum 22. The band-fission threshold is

    split_thr      = g* + max(0, cap - g*) * cohesion_frac,   cap = band_split_size
    cohesion_frac  = clamp01(assabiyah + leader_term - repulsion - malnutrition)

and on the live stack `cohesion_frac` is pinned at 1.0 for every band that HAS a leader, so `split_thr`
collapses to the constant `cap` and `g* = CV/cv_safe` drops out of the model. Two independent causes:

  (a) assabiyah's update is `a += gain*surplus - decay` clamped to [0,1], so its fixed point is
      `surplus_frac = decay/gain = 0.40`. Measured band surplus runs 0.35-0.99 (median 0.69), so ~96% of
      bands sit above the fixed point. Its median reaches exactly 1.000 by step 100 and stays — it is not a
      state variable, it is a constant.
  (b) the leader term (median ~0.8-1.1) is ADDED on top of that, putting the unclamped sum 70-110% above the
      clamp at the median band.

The share of bands pinned tracks the share that has acquired a leader: measured 0% at step 50 (no leaders
yet), 68/86% at 100, 88/99% at 200, 96/100% at 400 (n=1200 patch=30 / n=2500 patch=40), and at every
checkpoint the UNPINNED bands are exactly the leaderless ones.

Consequences, all measured (RESULTS Addendum 22): `corr(g*, band size) = -0.077` on 94 bands — R-72 built v3
precisely because v1/v2 measured -0.22 — and a `cv_safe` sweep over +22/+41/+62% moved `band_med` by
-1.9/-3.5/-8.4%, an elasticity of -0.14 against the law's -1.0.

THESE TESTS SHOULD START FAILING when the headroom is restored (by changing assabiyah's clamp, its
`decay/gain` fixed point, or the leader term's scale). When they do: re-enable the four mechanisms that feed
this expression — emergent band size, dynamic bands, size repulsion, malnutrition fission — re-measure
`band_med` against Johnson [18-35] and Hill 25-30, and update R-106.
"""
import os
import statistics
import sys

import pytest

_HERE = os.path.dirname(os.path.abspath(__file__))
_BATT = os.path.normpath(os.path.join(_HERE, "..", "outputs", "mechanism_battery"))
if _BATT not in sys.path:
    sys.path.insert(0, _BATT)

STACK = dict(enable_emergent_band_size=True, enable_resource_directed_fusion=True,
             enable_dynamic_bands=True, enable_band_affiliation=True,
             enable_size_repulsion=True, enable_village_scaling=True,
             enable_malnutrition_fission=True)
# 200 steps is chosen from the measurement above, not for convenience: assabiyah saturates by ~100 and the
# leaderless minority is down to ~12% by 200. Going longer only makes the effect stronger.
WORLD = dict(n=1200, patch=30, terr="coastal", clim="temperate")
STEPS = 200


@pytest.fixture(scope="module")
def bands():
    """(model, [per-band term dict]) after STEPS, read from the model's own stored state."""
    import battery1_liveness as B1
    w = B1._build(STACK, **WORLD)
    for _ in range(STEPS):
        w.step()
        if not w.agent_list:
            pytest.skip("population collapsed before bands could form")
    cfg = w._demog
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
        raw = a_val + lead - rep - maln
        g = sum(float(cvf[x.pos[1], x.pos[0]]) for x in ms) / len(ms) / cfg.cv_safe
        rows.append(dict(n=len(ms), a=a_val, lead=lead, raw=raw, coh=min(1.0, max(0.0, raw)), g=g,
                         surp=float(w._band_surplus.get(bid, 0.0))))
    if len(rows) < 10:
        pytest.skip(f"only {len(rows)} multi-member bands — too few to judge")
    return w, rows


@pytest.mark.slow
def test_every_band_with_a_leader_is_pinned_at_the_clamp(bands):
    """THE BLOCKER, stated as the deterministic rule rather than as a percentage: a leader term on top of a
    saturated assabiyah always exceeds the clamp, so the only bands whose cohesion can discriminate are the
    ones with no leader at all."""
    _, rows = bands
    led = [r for r in rows if r["lead"] > 0.0]
    assert led, "no band has a leader term — the leader-coherence stack is not running in this world"
    loose = [r for r in led if r["coh"] < 0.999]
    assert not loose, (
        f"{len(loose)}/{len(led)} led bands now have cohesion_frac below 1.0 (min raw "
        f"{min(r['raw'] for r in loose):.3f}) — the tolerable-size expression can discriminate again. "
        f"Re-enable and re-measure the four mechanisms that feed it.")


@pytest.mark.slow
def test_most_bands_are_pinned(bands):
    """The population-level version: the unpinned remainder is the leaderless minority and it shrinks."""
    _, rows = bands
    pinned = sum(1 for r in rows if r["coh"] >= 0.999)
    assert pinned / len(rows) > 0.8, (
        f"only {pinned}/{len(rows)} bands are pinned — the budget has regained headroom")


@pytest.mark.slow
def test_assabiyah_sits_above_its_own_fixed_point(bands):
    """Cause (a), stated as the arithmetic: above `surplus = decay/gain` the accumulator can only climb."""
    w, rows = bands
    cfg = w._demog
    ratio = cfg.assabiyah_decay / cfg.assabiyah_gain
    above = sum(1 for r in rows if r["surp"] > ratio)
    assert above / len(rows) > 0.8, (
        f"only {above}/{len(rows)} bands are above the assabiyah fixed point surplus={ratio:.2f} — the "
        f"economy or the gain/decay ratio has moved, so solidarity is a state variable again")
    assert statistics.median(r["a"] for r in rows) >= 0.999, (
        "median assabiyah is no longer at its clamp — solidarity discriminates between bands again")


@pytest.mark.slow
def test_the_unclamped_sum_is_well_above_one(bands):
    """Cause (b), and the number that matters for anyone calibrating a term that SUBTRACTS from this sum
    (malnutrition_fission_gain, band_risk_penalty, repulsion_gain): that term must exceed the median headroom
    before it changes a single median band's threshold."""
    _, rows = bands
    med_raw = statistics.median(r["raw"] for r in rows)
    assert med_raw > 1.3, (
        f"median unclamped cohesion sum is {med_raw:.3f} — the headroom has shrunk enough that a dispersion "
        f"term could now bite, so the inert verdicts for those mechanisms should be re-measured")


@pytest.mark.slow
def test_g_star_does_not_reach_realized_band_size(bands):
    """The consequence R-72's v3 was built to prevent, measured again. v1/v2 read -0.22; v3 reads about
    -0.08 — the linear law did not restore the gradient, because the term it feeds is clamped."""
    _, rows = bands
    gs = [r["g"] for r in rows]
    ns = [float(r["n"]) for r in rows]
    mx, my = statistics.mean(gs), statistics.mean(ns)
    sx, sy = statistics.pstdev(gs), statistics.pstdev(ns)
    if sx == 0.0:
        pytest.skip("g* has no spread in this world — nothing to correlate")
    r = sum((a - mx) * (b - my) for a, b in zip(gs, ns)) / (len(gs) * sx * sy)
    assert abs(r) < 0.25, (
        f"corr(g*, band size) = {r:+.3f} — the CV now reaches realized band size. cv_safe has become a live "
        f"calibration lever again and should be re-fitted to Hill 2011's 25-30.")
