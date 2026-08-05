"""ENFORCEMENT for MECHANISM_CHARTER §3.1 — every mechanism must be classified, so the audit can see it.

THE RULE ALREADY EXISTED. `sic_games/CLAUDE.md` says new Phase-1 mechanics land default-OFF/bit-exact and are
adopted by flipping the flag in the preset; MECHANISM_CHARTER §3.1 makes a TYPE declaration binding, and §6.1
implements the differential audit that checks each type's invariant. What was missing was anything that FAILS
when a new mechanism skips the step.

WHAT IT COST (measured 2026-07-26). The audit's classification table was frozen at R-85 (2026-07-18). By this
date 15 of 75 `enable_*` flags had never been classified — the entire legitimacy/resentment arc (R-86…R-99),
the R-103 accumulation stack, and the R-105 fix itself. Consequence on the record: R-104's circumscription
gradient ran with `enable_material_inheritance`, `enable_lineage_tribute` and `enable_noble_leveling_exemption`
all OFF, and its headline reading — "material lift stays flat at ~1.0 across a 5x reduction in habitable land,
so circumscription does not wake the goods axis" — was VOID. Material could not compound by construction; the
mechanisms under test were disabled. A whole overnight phase answered a question it had not asked.

This test is the missing failure. Adding a mechanism now breaks the suite until it is typed.
"""
import os
import sys

import pytest

from sic_games.demography import DemographyConfig

_HERE = os.path.dirname(os.path.abspath(__file__))
_AUDIT_DIR = os.path.normpath(os.path.join(_HERE, "..", "outputs", "phase1_biome_mortality"))
if _AUDIT_DIR not in sys.path:
    sys.path.insert(0, _AUDIT_DIR)

import audit_flag_invariants as audit           # noqa: E402

CHARTER_TYPES = set("SFTPDXCANHRO") | {"GAUGE"}


def _flags():
    return {k for k in DemographyConfig.model_fields if k.startswith("enable_")}


def test_every_mechanism_flag_is_classified():
    """MECHANISM_CHARTER §3.1: the TYPE declaration is binding. An unclassified flag is invisible to the audit,
    so nothing ever checks that it performs — which is how the material-accumulation stack sat unexercised."""
    missing = sorted(_flags() - set(audit.TYPES))
    assert not missing, (
        "these mechanisms have no charter TYPE, so the flag audit cannot test them:\n  "
        + "\n  ".join(missing)
        + "\n\nAdd each to TYPES in outputs/phase1_biome_mortality/audit_flag_invariants.py with its charter "
          "type (S F T P D X C A N H R O), plus a PREREQ chain and a live MAGNITUDE if its gain defaults to 0.")


def test_no_classification_for_a_flag_that_no_longer_exists():
    """The reverse rot: a retired mechanism left in the table makes coverage look complete when it is not."""
    stale = sorted(set(audit.TYPES) - _flags())
    assert not stale, f"TYPES classifies flags that are not in DemographyConfig (retired?): {stale}"


def test_declared_types_are_charter_types():
    bad = {f: t for f, t in audit.TYPES.items() if t not in CHARTER_TYPES}
    assert not bad, f"types outside MECHANISM_CHARTER §3's operator set: {bad}"


@pytest.mark.parametrize("flag", sorted(
    f for f, t in audit.TYPES.items() if t not in ("O", "GAUGE")))
def test_zero_defaulting_gain_has_a_live_magnitude(flag):
    """R-85c's retracted finding, turned into a check. Most flags pair with a gain that DEFAULTS TO 0, so
    flipping the flag alone leaves the mechanism inert and the audit calls a live mechanism dead. Any flag whose
    audit entry lacks a magnitude must at least be shown not to need one — here, that its own prefix-matching
    parameters are not all zero at their defaults."""
    if flag in audit.MAGNITUDE or flag in getattr(audit, "MAGNITUDE_EXEMPT", ()):
        return
    cfg = DemographyConfig()
    stem = flag[len("enable_"):]
    gains = {k: getattr(cfg, k) for k in DemographyConfig.model_fields
             if not k.startswith("enable_") and k.startswith(stem[:6])
             and isinstance(getattr(cfg, k), (int, float)) and not isinstance(getattr(cfg, k), bool)}
    if gains and all(v == 0 for v in gains.values()):
        pytest.fail(
            f"{flag} has no MAGNITUDE entry but every matching gain defaults to 0 ({gains}) — flipping the flag "
            f"alone leaves it inert, which is exactly the false 'dead knob' verdict retracted in R-85c.")


def test_audit_test_magnitudes_that_disagree_with_the_canonical_run_are_declared():
    """The audit's MAGNITUDE table and the canonical run are two copies of the same numbers, and two copies
    drift — that is exactly how `divorce_rate` came to be 0.004 in the authoritative config file while every
    campaign ran R-78's calibrated 0.005 (R-106 Addendum 21).

    The table's values are TEST magnitudes ("turn it on hard enough for the audit to see it"), not anchors,
    so they are ALLOWED to differ — but every difference must be declared here with its reason, so that a
    mechanism running at zero in the canonical stack can never again be mistaken for one the project has
    decided about.

    WHEN THIS FAILS: either a new disagreement appeared (declare it, or fix the canonical value), or one was
    resolved (drop it from the list)."""
    import tomllib

    root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
    mech = tomllib.load(open(os.path.join(root, "config", "mechanisms.toml"), "rb"))
    par = tomllib.load(open(os.path.join(root, "config", "parameters.toml"), "rb"))

    # flag -> {magnitude: why the canonical run differs}
    DECLARED = {
        "enable_malnutrition_fission": {
            "malnutrition_fission_gain": "demography.py calls it UNANCHORED; and Addendum 23 shows it could "
                                         "not act on a led band anyway, since the cohesion clamp swallows "
                                         "any dispersion term below the median headroom of 0.718"},
        "enable_terrain_pathogen": {
            "pathogen_gamma": "demography.py: '0 = OFF/flat. Sweep low/mid/high' — the sweep the doc asks "
                              "for has not been run, so 0.0 is deliberate-pending rather than a choice"},
        "enable_ascribed_mate_choice": {
            "ascribed_mate_strength": "1.5 is C_ENDOG_A's default, 2.5 is battery1's ELITE overlay — two "
                                      "harness copies, neither anchored; the campaign's own knob wins"},
    }
    found = {}
    for flag, mags in audit.MAGNITUDE.items():
        if mech.get(flag, {}).get("value") is not True:
            continue
        for key, want in mags.items():
            cur = par.get(key, {}).get("value")
            if isinstance(cur, (int, float)) and isinstance(want, (int, float)) and cur < want:
                found.setdefault(flag, {})[key] = (cur, want)

    undeclared = {f: v for f, v in found.items()
                  if f not in DECLARED or set(v) - set(DECLARED[f])}
    assert not undeclared, (
        "the audit table's test magnitude exceeds the canonical run's, undeclared:\n  "
        + "\n  ".join(f"{f}.{k}: canonical {a} < audit {b}"
                      for f, v in undeclared.items() for k, (a, b) in v.items())
        + "\n\nDeclare it in DECLARED above with the reason, or fix the canonical value.")
    resolved = [f for f in DECLARED if f not in found]
    assert not resolved, (
        f"these disagreements are gone — drop them from DECLARED: {resolved}")
