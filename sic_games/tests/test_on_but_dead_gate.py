"""CTB for the ON-but-dead gate — the check that refuses a flag switched on with a neutral magnitude.

THE BUG CLASS, which is this project's most expensive. A flag that is TRUE while the magnitude it acts through
sits at its neutral value reads as a live mechanism in every config dump AND as inert in every ablation. It is
invisible from both directions at once:

  * it produced 3 of battery 7's 6 "inert" verdicts
  * R-85's gate scan missed two more (`move_cost_kcal`, `site_gain`) because the zero lived one level deeper,
    inside a field builder rather than at the reader line — R-85b had to be a whole follow-up study
  * `enable_band_risk` survived an entire ablation battery as a fake positive on exactly this, and was deleted
  * on the day this gate was written it caught TWO more in the canonical config — `enable_terrain_pathogen`
    (gamma 0.0, awaiting its Cashdan sweep) and `enable_malnutrition_fission` (gain 0.0, the R-106 negative
    control whose FLAG should have been off rather than its gain zeroed)

The rule it enforces: **you ablate a mechanism by turning its FLAG off, never by zeroing its magnitude.**
Zeroing the magnitude leaves the flag advertising a mechanism that is not running.
"""
import pytest

from sic_games import runconfig


def test_a_flag_on_with_a_zero_magnitude_is_reported():
    """THE POSITIVE CASE, constructed."""
    dead = runconfig.dead_flags({"enable_terrain_pathogen": True, "pathogen_gamma": 0.0})
    assert len(dead) == 1
    assert "enable_terrain_pathogen" in dead[0] and "pathogen_gamma=0.0" in dead[0]


def test_a_flag_on_with_a_live_magnitude_is_silent():
    """THE NULL. If this ever reports, the gate blocks legitimate runs and will be switched off within a week,
    which is worse than not having it."""
    assert runconfig.dead_flags({"enable_terrain_pathogen": True, "pathogen_gamma": 0.35}) == []


def test_a_flag_that_is_OFF_is_not_reported_however_zero_its_magnitude():
    """An ablated mechanism is SUPPOSED to have a dead magnitude. Flagging it would make the gate fire on every
    control arm in the project."""
    assert runconfig.dead_flags({"enable_terrain_pathogen": False, "pathogen_gamma": 0.0}) == []


def test_a_multipliers_neutral_value_is_one_not_zero():
    """The trap that `climate.py`'s `need()` already had to handle. A magnitude that multiplies has a no-op of
    1.0, so a bare falsy check waves it through as configured while it does nothing. `cohesion_leader_weight`
    is the live example — 1.0 means 'exactly today's behaviour, bit-exact'."""
    assert runconfig.NEUTRAL["cohesion_leader_weight"] == 1.0


def test_the_gate_only_judges_fields_the_config_actually_has():
    """`known` scopes the check to one class's fields, so a DemographyConfig is not judged against a climate
    flag it has never heard of. Deleting a field must not turn the gate into a crash."""
    assert runconfig.dead_flags({"enable_terrain_pathogen": True, "pathogen_gamma": 0.0},
                                known={"something_else"}) == []


def test_the_canonical_config_has_no_undocumented_on_but_dead_mechanism():
    """THE REGRESSION THAT MATTERS. What a real run loads must be honest. Anything that appears here is either
    a defect or needs a documented §12 reason and an entry in the campaign's skip list."""
    cfg = runconfig.build("DemographyConfig")
    fields = set(type(cfg).model_fields)
    dead = runconfig.dead_flags({f: getattr(cfg, f) for f in fields}, fields)
    assert dead == [], (
        "the canonical configuration advertises mechanisms that cannot act:\n  " + "\n  ".join(dead))


def test_strict_build_raises_rather_than_returning_a_dishonest_config():
    """`build(strict=True)` is the enforcing path. It must FAIL, not warn — a warning in a 20-minute run scrolls
    past and the run still produces a result that reads as if the mechanism was on."""
    with pytest.raises(SystemExit) as e:
        runconfig.build("DemographyConfig", overrides={"enable_terrain_pathogen": True,
                                                       "pathogen_gamma": 0.0}, strict=True)
    assert "ON-but-dead" in str(e.value)


def test_the_deleted_band_risk_flag_is_not_resurrected_by_the_table():
    """`enable_band_risk` was the archetype of this bug class and is deleted. The gate's table must not still
    name it, or a future reader will think the mechanism exists."""
    assert "enable_band_risk" not in runconfig.FLAG_MAGNITUDES
    assert "enable_infanticide" not in runconfig.FLAG_MAGNITUDES
