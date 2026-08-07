"""A RATCHET on provenance coverage: the share of run parameters that say where they came from may rise, and
may not fall.

Coverage was measured for the first time on 2026-08-06 (Addendum 29) and the first measurement was WRONG in
two directions at once, which is why this is a test and not a note:

  * it read 25 parameters as UNDOCUMENTED when 18 of them were documented in the comment directly above their
    own flag -- `gen_runconfig.py` harvested only the line touching each field, so a channel comment reached
    the flag and none of the parameters it constrained. The generator now inherits the channel note.
  * the audit's own classifier tested "ANCHORED" before "UNANCHORED", and since one string contains the other
    it scored 16 explicitly-unanchored parameters as anchored -- a clean sweep that was an artefact of the
    substring. Class order in `audit_provenance.py` is load-bearing for that reason.

Both were measurement bugs, not model bugs, and both flattered the result. CLAUDE.md's first rule applies to
an audit exactly as it applies to a diagnostic: check the instrument against a constructed case before
believing the number.
"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from audit_provenance import audit, classify  # noqa: E402

DECLARING = ("ANCHORED", "PROVISIONAL", "CITES-A-YEAR", "UNANCHORED")

# THE RATCHET IS ON THE NON-DECLARING COUNT, NOT THE DECLARING ONE. The first version asserted
# `declaring >= 144` and it fired within the hour -- on a DELETION. Removing `band_risk_penalty` and
# `band_risk_size`, two parameters that were properly documented, dropped the declaring count to 142 and the
# test called a cleanup a regression. Deleting a documented parameter is exactly the behaviour we want to
# encourage, so the count of parameters that DON'T declare a source is the right invariant: deletions never
# raise it, and every silently-added field does.
BASELINE_NON_DECLARING = 100    # COMMENTED-but-sourceless + UNDOCUMENTED, measured 2026-08-06


@pytest.fixture(scope="module")
def result():
    return audit()


def test_no_parameter_is_completely_undocumented(result):
    """Every number a run reads must carry SOMETHING — an anchor, a provisional bracket, an explicit
    'unanchored', or at minimum a sentence saying what it does."""
    undoc = result.get("UNDOCUMENTED", [])
    assert undoc == [], f"{len(undoc)} parameters carry no comment at all: {undoc}"


def test_provenance_coverage_does_not_regress(result):
    """The ratchet. A parameter added without a source raises the non-declaring count and fails here — the
    backlog got this large by accreting one silent field at a time. Lower the baseline when the backlog is
    genuinely worked down; never raise it to make a run pass."""
    total = sum(len(v) for v in result.values())
    non_declaring = total - sum(len(result.get(k, [])) for k in DECLARING)
    assert non_declaring <= BASELINE_NON_DECLARING, (
        f"{non_declaring} parameters declare no source, above the {BASELINE_NON_DECLARING} baseline — "
        "a new field was added without provenance")


def test_unanchored_beats_anchored_in_the_classifier():
    """THE CONSTRUCTED TRUTH for the audit itself. 'UNANCHORED' contains 'ANCHORED' as a substring; if the
    classes are ever reordered, a parameter that honestly declares it has NO source gets counted as one that
    has one, and the coverage number silently inflates."""
    assert classify("# [UNANCHORED, LIVE] locked by scan, not by literature") == "UNANCHORED"
    assert classify("# [ANCHORED, Bandy 2004 p.330]") == "ANCHORED"
    assert classify("# [PROVISIONAL] working bracket") == "PROVISIONAL"


def test_the_classifier_separates_a_bare_year_from_a_tag():
    """A comment naming 'Hawkes 1991' is better than nothing but is NOT machine-checkable — verify_anchor.py
    only sees registered rows. Keeping the two classes distinct is what makes the remaining backlog visible
    rather than looking like coverage."""
    assert classify("# derived from Hawkes 1991 Table 2") == "CITES-A-YEAR"
    assert classify("# the fraction of the step spent foraging") == "COMMENTED"
    assert classify("") == "UNDOCUMENTED"


def test_a_year_inside_a_tagged_comment_still_reads_as_tagged():
    """Order again: an ANCHORED comment almost always contains a year too. The tag must win."""
    assert classify("# [ANCHORED, Tallavaara 2018 SI] segmented regression") == "ANCHORED"
    assert classify("# [PROVISIONAL] pending the 2026 re-fit") == "PROVISIONAL"


def test_the_dead_carbon_parameters_are_labelled_as_dead(result):
    """Five CarbonConfig fields are unreachable from `phase1_model.py`. That fact is worth more than a
    literature citation would be, and it must survive in the generated config."""
    params = (ROOT / "config" / "parameters.toml").read_text(encoding="utf-8")
    for name in ("cred_decay", "matthew_alpha", "epsilon", "cred_bonus_per_participant", "velocity_tau"):
        block = params.split(f"[{name}]", 1)[1].split("\n[", 1)[0]
        assert "DEAD" in block, f"{name} is unreachable from a campaign run and the config does not say so"
