"""Fertility must respond to sustained energy BALANCE, because the stored reserve carries no signal.

THE DEFECT (measured 2026-07-30). `enable_energetic_fertility` scales births by the maternal RESERVE level,
which is inert by construction. Burn is ~68% of the floor-to-full span per step, so an agent either
re-saturates at the cap or dies within a step — there is no persistent intermediate state. Measured across a
5x density range: post-harvest reserve 0.996 of full, post-burn trough 0.318, each with spread ~0.002 and
ZERO density response, so the factor returns ~0.995 always. Consequences, all measured:

  * births barely move with crowding (CBR 53.8 -> 52.0 across 5x density) while deaths do all the work
    (CDR 48.5 -> 77.0, starvation 46% -> 61% of deaths);
  * a stationary population then has e0 = 1/CDR ~ 20.7 yr, median age 13, motherless 8-11%;
  * no Malthusian feedback: a positive control at three resource gradients (per-capita elasticity -0.195 /
    -0.387 / -1.062) produced NO oscillation at any of them, and deaths out-swung births in all three.

THE FIX: read a slow EMA of intake over requirement. Intake is the live signal the reserve level cannot be
(p10 0.93 to p90 4.26 of requirement), and it is the biologically right one — Ellison's energetics has
fecundity tracking energy FLUX, not stored reserve. Thresholds are anchored, not tuned: 0 at maintenance
(no surplus to gestate or lactate), full at maintenance + the lactation increment (~+500 kcal/d on ~2500,
FAO/IOM ⇒ ~1.2x).

DEFAULT OFF and bit-exact when off, per the mechanism charter.
"""
import os
import sys

import pytest

from sic_games.demography import DemographyConfig

_HERE = os.path.dirname(os.path.abspath(__file__))
_BATT = os.path.normpath(os.path.join(_HERE, "..", "outputs", "mechanism_battery"))
if _BATT not in sys.path:
    sys.path.insert(0, _BATT)

WORLD = dict(n=900, patch=18, terr="coastal", clim="temperate")


def test_defaults_off_and_thresholds_anchored():
    c = DemographyConfig()
    assert c.enable_intake_fertility is False, "must be opt-in"
    assert c.intake_fert_lo == 1.00, "the floor is MAINTENANCE — intake=burn leaves no reproductive surplus"
    assert c.intake_fert_hi == 1.20, "the ceiling is maintenance + the lactation increment (FAO/IOM)"
    assert 0.0 < c.intake_ema_alpha <= 1.0


def test_ema_half_life_is_about_fourteen_months():
    """Slow enough that one bad month cannot stop births, fast enough to track a multi-year squeeze."""
    import math
    a = DemographyConfig().intake_ema_alpha
    hl = math.log(2) / -math.log(1 - a)
    assert 10.0 <= hl <= 24.0, f"half-life {hl:.1f} steps is outside the intended ~1-2 yr band"


@pytest.mark.slow
def test_off_is_bit_exact():
    """The charter's adoption gate: with the flag off the world must be unchanged."""
    import battery1_liveness as B1
    base, _, _ = B1.signature({}, steps=120, **WORLD)
    off, _, _ = B1.signature(dict(enable_intake_fertility=False), steps=120, **WORLD)
    assert base == off, "explicitly disabling the flag changed the world — the branch is not inert when off"


@pytest.mark.slow
def test_on_changes_the_world():
    """Liveness: if switching it on is bit-identical, the mechanism is on and doing nothing.

    HORIZON, and why it is 300 rather than 120 (2026-08-04). This ran at 120 steps and was a COIN FLIP: a
    0.001 change in `divorce_rate`, in a different overlay entirely, flipped it from pass to fail. The cause
    is not the mechanism. The brake only bites below `intake_fert_hi` (1.20), and in this world the share of
    fertile women under that gate is measured at 0.0% by step 60, **2.2% (three women) at step 120**, 7.3% at
    180 and 13.1% at 300 — so at 120 steps the verdict turned on whether one of three women happened to be
    drawn for a birth. 300 steps is the horizon at which the gate demonstrably binds, and is what the sibling
    EMA-spread test below already uses. The population GROWS through this window (757 → 867), which is the
    root of it: a fertility brake needs scarcity, and this small test world is rich."""
    import battery1_liveness as B1
    off, _, _ = B1.signature({}, steps=300, **WORLD)
    on, _, _ = B1.signature(dict(enable_intake_fertility=True), steps=300, **WORLD)
    assert on != off, "enabling intake-fertility is bit-identical — the new branch is dead"


@pytest.mark.slow
def test_the_ema_actually_varies_unlike_the_reserve():
    """The whole point. The reserve-based inputs sit at spread ~0.002; this one must genuinely discriminate,
    otherwise we have swapped one dead input for another."""
    import statistics

    import battery1_liveness as B1
    w = B1._build(dict(enable_intake_fertility=True), **WORLD)
    for _ in range(300):
        w.step()
        if not w.agent_list:
            break
    cfg = w._demog
    ema = [a._intake_ema for a in w.agent_list if a.age >= cfg.menarche_months]
    assert len(ema) > 20, "too few adults to judge"
    assert statistics.pstdev(ema) > 0.05, (
        f"intake EMA spread {statistics.pstdev(ema):.4f} — as flat as the reserve it replaced, so fertility "
        f"still cannot discriminate hungry from well-fed agents")


def test_dependent_load_defaults_off_and_needs_its_parent_flag():
    assert DemographyConfig().enable_dependent_load is False, "must be opt-in and independently ablatable"


@pytest.mark.slow
def test_children_are_net_producers_which_is_WHY_dependent_load_is_inert():
    """THE BLOCKER, pinned as a fact about the model rather than as a passing feature.

    Life-history IS on in these presets (eta_min 0.2, cons_min 0.3) and mother-links resolve for ~91% of
    juveniles — so the dependent-load mechanism is wired correctly. It still finds nothing, because juveniles
    GATHER MORE THAN THEY NEED: measured eta med 0.529 vs consumption_factor med 0.588, and with adults taking
    ~1.7x their own burn a child still clears ~1.5x its requirement. Only ~1% run any deficit.

    That contradicts Kaplan 2000 — the net child deficit cited by `consumption_factor()`'s own docstring, and
    the anchor under human life-history theory (long juvenile period, provisioning, grandmothering).

    THIS TEST SHOULD START FAILING once the juvenile eta ramp is recalibrated against Kaplan's curves
    (foragers do not break even until ~18-20 yr). When it does, flip it and enable dependent-load.
    """
    import battery1_liveness as B1
    w = B1._build(dict(enable_intake_fertility=True, enable_dependent_load=True), **WORLD)
    for _ in range(300):
        w.step()
        if not w.agent_list:
            break
    juv = [a for a in w.agent_list if a.is_juvenile()]
    assert len(juv) > 30, "too few juveniles to judge"
    in_deficit = sum(1 for a in juv
                     if w._burn * a.consumption_factor() - a._last_intake > 0.0) / len(juv)
    assert in_deficit < 0.10, (
        f"{in_deficit*100:.1f}% of juveniles now run a deficit (was 1.0%) — children may have become net "
        f"CONSUMERS as Kaplan describes. If so this blocker is cleared: enable dependent-load, re-run the "
        f"materiality check, and update R-106.")


@pytest.mark.slow
def test_dependent_load_is_bit_exact_when_off():
    import battery1_liveness as B1
    a, _, _ = B1.signature(dict(enable_intake_fertility=True), steps=120, **WORLD)
    b, _, _ = B1.signature(dict(enable_intake_fertility=True, enable_dependent_load=False), steps=120, **WORLD)
    assert a == b, "explicitly disabling dependent-load changed the world"


@pytest.mark.slow
def test_dependent_load_does_nothing_without_intake_fertility():
    """It widens the intake-fertility denominator, so it must be inert on its own — not a silent second path."""
    import battery1_liveness as B1
    off, _, _ = B1.signature({}, steps=120, **WORLD)
    alone, _, _ = B1.signature(dict(enable_dependent_load=True), steps=120, **WORLD)
    assert off == alone, "dependent-load acted without its parent flag"


@pytest.mark.xfail(reason="BLOCKED: children are net producers in this model (only ~1% of juveniles run a "
                          "deficit), so there is no dependent load to find. See the Kaplan 2000 blocker test "
                          "above and R-106. Unblocks when the juvenile eta ramp is recalibrated.",
                   strict=True)
@pytest.mark.slow
def test_dependent_load_reaches_the_denominator_and_is_material():
    """The mechanism proper, tested DIRECTLY rather than by comparing mothers against childless women.

    That comparison is confounded and was tried first: high-intake women are exactly the ones who succeed in
    conceiving, so mothers read a HIGHER EMA than childless women (measured 4.11 vs 1.82) — which is the brake
    working as designed, and it swamps the load effect entirely. Selection, not mechanism.

    So: recompute the load the way the model does and assert (a) it reaches a material share of mothers and
    (b) it is big enough to move the denominator, rather than being a rounding error.
    """
    import statistics

    import battery1_liveness as B1
    w = B1._build(dict(enable_intake_fertility=True, enable_dependent_load=True,
                       enable_life_history=True), **WORLD)
    for _ in range(300):
        w.step()
        if not w.agent_list:
            break
    cfg = w._demog
    load = {}
    for c in w.agent_list:
        if not c.is_juvenile():
            continue
        m = getattr(c, "_mother", None)
        if m is None or not m.alive:
            continue
        d = w._burn * c.consumption_factor() - c._last_intake
        if d > 0.0:
            load[m] = load.get(m, 0.0) + d
    women = [a for a in w.agent_list
             if a.sex == "female" and cfg.menarche_months <= a.age <= cfg.menopause_months]
    assert women, "no fertile women"
    carrying = [a for a in women if load.get(a, 0.0) > 0.0]
    assert len(carrying) / len(women) > 0.05, (
        f"only {len(carrying)}/{len(women)} fertile women carry any dependent load — the mother-link or the "
        f"juvenile deficit is not being found")
    rel = [load[a] / (w._burn * a.consumption_factor()) for a in carrying]
    assert statistics.median(rel) > 0.10, (
        f"median dependent load is {statistics.median(rel)*100:.1f}% of own maintenance — too small to move the "
        f"denominator, so the mechanism is on but immaterial")


@pytest.mark.slow
def test_juveniles_do_not_accumulate_a_penalty():
    """A child's GATHERED intake understates what it EATS, because juveniles are provisioned. The EMA must
    therefore stay at its neutral start until menarche, or girls would reach fertility pre-penalised."""
    import battery1_liveness as B1
    w = B1._build(dict(enable_intake_fertility=True), **WORLD)
    for _ in range(60):
        w.step()
        if not w.agent_list:
            break
    cfg = w._demog
    kids = [a._intake_ema for a in w.agent_list if a.age < cfg.menarche_months]
    assert kids, "no juveniles"
    assert all(abs(v - cfg.intake_fert_hi) < 1e-12 for v in kids), (
        "a juvenile's intake EMA drifted from neutral — it must only accumulate from menarche")
