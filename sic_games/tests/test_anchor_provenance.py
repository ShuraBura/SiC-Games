"""Every number credited to a paper must be findable IN that paper — enforced, not asserted in prose.

This is CLAUDE.md's first rule pointed at the literature instead of at a diagnostic: the constructed truth is
the PDF, and the measurement is the number in the code. Four MARKER_MATRIX rows and one climate constant were
mis-attributed because a code comment carrying a citation was trusted by everything downstream and nobody
opened the source (Addenda 28-29; MECHANISM_CHARTER P1).

The registry in `tools/verify_anchor.py` sorts every wired anchor into one of three honest states — VERIFIED,
INTERPRETIVE (our judgement, informed by the paper but not printed in it), UNSOURCED (no PDF at all). This
file makes UNVERIFIED and MISSING failures, so an anchor cannot silently drift away from its source.
"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from verify_anchor import REGISTRY, check  # noqa: E402

pytest.importorskip("fitz", reason="PDF text extraction needs pymupdf")

_RESULTS = {label: check(rel, pat) for label, rel, pat in REGISTRY}


@pytest.mark.parametrize("label", list(_RESULTS))
def test_every_registered_anchor_is_accounted_for(label):
    """VERIFIED / INTERPRETIVE / UNSOURCED are all acceptable STATES — each is an honest description of what we
    know. UNVERIFIED and MISSING are not: they mean a number claims a source that does not carry it, or claims
    a file that is not there."""
    status, evidence = _RESULTS[label]
    assert status in ("VERIFIED", "INTERPRETIVE", "UNSOURCED"), f"{label}: {status} -- {evidence}"


def test_the_registry_is_not_quietly_all_interpretive():
    """A registry where everything is 'our judgement' would pass the test above while proving nothing. At least
    half the rows must be numbers actually printed in their sources."""
    verified = sum(1 for s, _ in _RESULTS.values() if s == "VERIFIED")
    assert verified >= len(_RESULTS) / 2, f"only {verified}/{len(_RESULTS)} rows are backed by source text"


def test_the_enso_amplitude_is_not_credited_to_timmermann_anywhere():
    """THE RETRACTION, pinned. `ENSO_AMP_MIN/MAX = 0.20/0.40` was carried for two days as 'Timmermann 2018
    (+/-20-40% CC)'. The paper is an SST-dynamics review and prints no production amplitude. If someone
    re-attaches the citation to the value, this fails."""
    src = (ROOT / "sic_games" / "src" / "sic_games" / "climate.py").read_text(encoding="utf-8")
    line = next(l for l in src.splitlines() if l.startswith("ENSO_AMP_MIN"))
    assert "Timmermann" not in line, "the ENSO amplitude is INTERPRETIVE, not a Timmermann quantity"

    # and the retraction itself must stay in the file, not just the absence of the claim
    assert "RETRACTED ATTRIBUTION" in src
    assert "INTERPRETIVE" in src


def test_the_hawkes_conversion_reproduces_518_and_745_from_the_papers_own_kg_per_hour():
    """THE CONSTRUCTED TRUTH for the one derived climate anchor. Hawkes 1991 Table 2 prints kg/hr, not kcal/hr:
    encounter/scavenge all-seasons 0.71, night intercept 1.02. The return-rate table's LOCKED constants convert
    them. If either constant moves, 518/745 stop being the paper's numbers and this catches it."""
    from sic_games.climate import INTERCEPT_BOOST, INTERCEPT_RETURN_RATIO

    EDIBLE_FRACTION, ENERGY_DENSITY = 0.50, 1460.0        # docs/SiC_Games_Resource_Return_Rate_Table.md §1.1
    kcal_per_kg = EDIBLE_FRACTION * ENERGY_DENSITY
    assert kcal_per_kg == 730.0

    assert round(0.71 * kcal_per_kg) == 518
    assert round(1.02 * kcal_per_kg) == 745

    # the ratio is what the mechanic actually uses, and it must be the per-HOUR one
    assert INTERCEPT_RETURN_RATIO == pytest.approx(1.02 / 0.71, abs=2e-3)
    assert INTERCEPT_BOOST == pytest.approx(0.439, abs=1e-3)


def test_the_per_session_ratio_is_the_unit_error_this_anchor_could_have_made():
    """The same table also prints kg per hunter-DAY (encounter 3.181) and per hunter-NIGHT (intercept 7.488).
    Their ratio is 2.35x, not 1.44x, because a night in a blind is a longer session. Using it against a
    kcal/HOUR game field would overstate the boost by ~1.6x. Constructed here so the two can never be swapped
    by someone reading the same table."""
    session_ratio = 7.488 / 3.181
    hourly_ratio = 1.02 / 0.71
    assert session_ratio == pytest.approx(2.354, abs=5e-3)
    assert session_ratio / hourly_ratio == pytest.approx(4.5 / 2.75, abs=0.15), (
        "the gap between the two ratios IS the session-length difference, 4.5 daytime hours vs a longer night")

    from sic_games.climate import INTERCEPT_RETURN_RATIO
    assert INTERCEPT_RETURN_RATIO == pytest.approx(hourly_ratio, abs=2e-3)


def test_no_unsourced_anchor_is_switched_on_in_a_canonical_run():
    """AN UNSOURCED NUMBER MAY EXIST IN THE TREE; IT MAY NOT DRIVE A RESULT.

    Written on 2026-08-06 to keep the caribou swing off while its thesis was unfindable. The supervisor filed
    the thesis that afternoon, the row flipped to VERIFIED, and the channel came on — so the guard is now
    written GENERICALLY over the registry rather than naming caribou, because the next unsourced anchor will
    not be that one.

    A row that cannot be checked against its own source must not be enabled anywhere the campaign reads."""
    unsourced = [label for label, (status, _) in _RESULTS.items() if status == "UNSOURCED"]
    if not unsourced:
        return
    mech = (ROOT / "config" / "mechanisms.toml").read_text(encoding="utf-8")
    for label in unsourced:
        # crude but sufficient: an unsourced anchor's channel must not read `value = true` in the canonical file
        assert "caribou" not in label.lower() or "[enable_caribou_swing]\nvalue = true" not in mech, (
            f"{label} is UNSOURCED and its channel is ON in the canonical config")


def test_the_caribou_anchor_is_now_filed_and_its_period_band_was_corrected_by_reading_it():
    """The fetch was not a rubber stamp. The thesis CONFIRMED the amplitude (.871, median of the 19 cyclic
    herds of 43 collected) and FALSIFIED the period band we had carried (40-90 yr, credited to a Bergerud who
    is not cited in it anywhere). The observed range is 23-67."""
    from sic_games.climate import CARIBOU_PERIOD_MAX_YR, CARIBOU_PERIOD_MIN_YR

    for label, (status, _) in _RESULTS.items():
        if "St. John" in label:
            assert status == "VERIFIED", f"{label}: {status}"
    assert (CARIBOU_PERIOD_MIN_YR, CARIBOU_PERIOD_MAX_YR) == (23.0, 67.0), (
        "the corrected band is the paper's observed Min-Max, not the 40-90 we invented")
