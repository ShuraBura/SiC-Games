"""CTB — THE DEMOGRAPHY VERDICT LINE (R-106, 2026-08-14, supervisor request).

WHY A VERDICT AND NOT MORE FIELDS. Every demographic failure of 2026-08-13/14 was visible in numbers the run
was ALREADY printing. What was missing was a line that said OUT-OF-BAND without a human going to look. The
precedent is `ClimateField.health()`, whose UNREACHABLE / NEVER-FIRED verdicts found three dark climate
channels on their first real run.

THE CASE THE GATE EXISTS FOR. `band_med` read 23 against Birdsell's ~25 and looked like a PASS, on a
population that was 54% children — about 11 ADULTS against Hill et al. 2011's 28.2 ADULTS. A marker read as
passing while failing 2.5-fold. `docs/MARKER_MATRIX.md` #1 had already recorded exactly this ("the 23/25
all-ages pass is carried by excess children") and it was still missed. So `structure_ok` is not decoration:
when the age structure is out of band, every marker above demography in the ladder is provisional.

WHAT THIS FILE GUARDS, and each is a way the monitor could quietly stop working:
  · a band that does not match its filed source        -> the whole panel scores against invented numbers
  · a PASS returned for a value outside its band       -> silent false confidence, the original failure
  · the gate not tripping on a skewed age structure    -> the band_med case recurs
  · a denominator swap (surv_to_45 vs the conditional) -> the fifth such retraction in this project
  · an anchorless marker silently dropped              -> a gap nobody can see is a gap nobody fixes
"""
import pytest

from sic_games.demography import (DEMOG_ANCHORS, DEMOG_GATE, DEMOG_UNANCHORED, demography_health)


def _healthy():
    """A row sitting inside every filed band. Values chosen as band midpoints / published anchors."""
    return {"frac_child": 0.37, "dependency_ratio": 0.75, "sex_ratio_m_f": 1.1,
            "realised_e0": 30.0, "e15": 38.5, "e45": 21.1, "surv_to_15": 0.66, "surv_to_45": 0.43,
            "modal_adult_death": 72.0, "realised_tfr": 6.5, "realised_ibi_med": 40.0,
            "frac_motherless": 0.02, "frac_fatherless": 0.05, "band_med_adults": 28.2}


# ── the registry itself ───────────────────────────────────────────────────────────────────────────────────

def test_every_anchor_carries_a_source():
    """A band with no source is an invented number wearing a citation's clothes."""
    for key, spec in DEMOG_ANCHORS.items():
        src = spec[-1]
        assert isinstance(src, str) and len(src) > 20, f"{key} has no usable source string"
        assert any(t in src for t in ("VERIFIED", "Hill", "Gurven", "Table")), f"{key} source is vague: {src}"


def test_the_bands_match_the_filed_values():
    """Pinned against docs/MARKER_MATRIX.md and docs/LITERATURE.md. If a band is edited, this fails and the
    editor must restate the source rather than nudge a number until a run passes."""
    assert DEMOG_ANCHORS["frac_child"][1:3] == (0.287, 0.454)          # Hill & Hurtado T4.4
    assert DEMOG_ANCHORS["dependency_ratio"][1:3] == (0.598, 0.899)    # 0.598 !Kung .. 0.899 Aché
    assert DEMOG_ANCHORS["sex_ratio_m_f"][1:3] == (0.896, 1.368)
    assert DEMOG_ANCHORS["realised_tfr"][1:3] == (4.69, 8.03)          # Hill & Hurtado T8.1/8.2
    assert DEMOG_ANCHORS["realised_ibi_med"][1:3] == (34.4, 49.4)
    assert DEMOG_ANCHORS["realised_e0"][1:3] == (21.0, 37.0)           # G&K cross-HG range
    assert DEMOG_ANCHORS["modal_adult_death"][1:3] == (68.0, 78.0)     # G&K adaptive lifespan
    assert DEMOG_ANCHORS["e15"][1] == 38.5
    assert DEMOG_ANCHORS["band_med_adults"][1] == 28.2                 # Hill 2011 ADULTS


def test_band_size_is_anchored_on_ADULTS_not_all_ages():
    """THE WHOLE POINT OF THE EXERCISE. Hill's 28.2 is adults. If a future edit points this anchor at
    `band_med`, the false pass that started this work comes straight back."""
    assert "band_med_adults" in DEMOG_ANCHORS
    assert "band_med" not in DEMOG_ANCHORS
    assert "ADULT" in DEMOG_ANCHORS["band_med_adults"][-1].upper()


def test_the_conditional_survivorship_is_not_scored_against_the_from_birth_anchor():
    """DENOMINATOR GUARD. The published 0.43 is l(45) FROM BIRTH. `surv_15_to_45_cond` is 0.65 and must NOT
    be scored against it — that swap would mark a correct schedule wrong by ~50%."""
    assert DEMOG_ANCHORS["surv_to_45"][1] == 0.43
    assert "FROM BIRTH" in DEMOG_ANCHORS["surv_to_45"][-1]
    assert "surv_15_to_45_cond" not in DEMOG_ANCHORS


# ── the verdicts ──────────────────────────────────────────────────────────────────────────────────────────

def test_a_healthy_row_passes_everything():
    h = demography_health(_healthy())
    bad = [v for v in h["verdicts"] if v["verdict"] in ("OUT-OF-BAND", "DEVIATION")]
    assert not bad, f"a row on the anchors should pass: {[(v['marker'], v['value']) for v in bad]}"
    assert h["structure_ok"] is True
    assert h["n_out"] == 0


@pytest.mark.parametrize("marker,bad_value", [
    ("frac_child", 0.60), ("dependency_ratio", 1.5), ("realised_tfr", 10.5),
    ("realised_ibi_med", 22.0), ("realised_e0", 17.7), ("modal_adult_death", 22.0),
])
def test_each_band_actually_rejects_a_value_outside_it(marker, bad_value):
    """THE NEGATIVE CONTROL, one per band. A band that never rejects anything is decoration. Every value
    here is one this model has actually produced in the last two days."""
    row = _healthy(); row[marker] = bad_value
    v = next(x for x in demography_health(row)["verdicts"] if x["marker"] == marker)
    assert v["verdict"] == "OUT-OF-BAND", f"{marker}={bad_value} should not pass"


def test_point_anchors_report_a_ratio_and_flag_a_deviation():
    row = _healthy(); row["band_med_adults"] = 9.0        # the measured value, 0.32x Hill's 28.2
    v = next(x for x in demography_health(row)["verdicts"] if x["marker"] == "band_med_adults")
    assert v["verdict"] == "DEVIATION"
    assert v["ratio"] == pytest.approx(9.0 / 28.2, rel=1e-6)


def test_the_gate_trips_on_a_skewed_age_structure_and_says_so():
    """The band_med case, reconstructed. The gate must fire and the banner must SAY that everything above
    demography is provisional — the sentence is the deliverable, not the boolean."""
    row = _healthy(); row["frac_child"] = 0.54           # the population band_med 23 was read on
    h = demography_health(row)
    assert h["structure_ok"] is False
    assert "PROVISIONAL" in h["banner"]


def test_the_gate_watches_only_the_age_structure():
    """A fertility or mortality miss must NOT trip the structural gate — that would make it fire constantly
    and stop meaning anything. Only the age composition gates the markers above."""
    row = _healthy(); row["realised_tfr"] = 10.5
    h = demography_health(row)
    assert h["structure_ok"] is True and h["n_out"] == 1
    assert set(DEMOG_GATE) == {"frac_child", "dependency_ratio"}


def test_missing_and_nan_values_are_NO_DATA_not_PASS():
    """A monitor that scores an absent field as passing is worse than no monitor."""
    row = _healthy(); row["e15"] = float("nan"); del row["surv_to_45"]
    vs = {v["marker"]: v["verdict"] for v in demography_health(row)["verdicts"]}
    assert vs["e15"] == "NO-DATA" and vs["surv_to_45"] == "NO-DATA"


def test_unanchored_markers_are_reported_not_dropped():
    """A gap that is invisible is a gap nobody fixes. These have no filed anchor and must say so."""
    row = _healthy(); row["age_first_birth_yr"] = 24.9; row["srb_male_frac"] = 0.463
    vs = {v["marker"]: v["verdict"] for v in demography_health(row)["verdicts"]}
    assert vs["age_first_birth_yr"] == "NO-ANCHOR" and vs["srb_male_frac"] == "NO-ANCHOR"
    assert "age_first_birth_yr" in DEMOG_UNANCHORED


def test_unanchored_markers_do_not_count_toward_the_score():
    """They are context, not a verdict. Counting them would dilute the in-band fraction and make a failing
    panel look healthier as more unanchored fields are added."""
    a = demography_health(_healthy())
    row = _healthy(); row["age_first_birth_yr"] = 24.9
    b = demography_health(row)
    assert a["n_scored"] == b["n_scored"]


def test_the_banner_names_the_worst_offenders():
    row = _healthy()
    row["frac_child"] = 0.60
    row["band_med_adults"] = 9.0
    b = demography_health(row)["banner"]
    assert "frac_child" in b and "band_med_adults" in b
    assert "in band" in b
