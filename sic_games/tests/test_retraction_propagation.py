"""A retracted anchor must be retracted AT ITS POINT OF USE, not only in the log that retracted it.

MECHANISM_CHARTER P3 says exactly this, and P3 was still being violated by the retraction that motivated it.
Addendum 28 established on 2026-08-04 that **Hill et al. 2011 contains no lineage data** — the word does not
occur in the paper — which voids the "~7 lineages per band / dominant-lineage share 0.38" target. That was
written into RESULTS.md and MARKER_MATRIX.md. It was NOT written into `demography.py`, where three live
parameters went on citing the target, one of them (`rank_hierarchy_frac` = 0.15) deriving its value from the
nonexistent 1/7 and reading, to anyone opening the file, as anchored.

It was found two days later by a provenance audit that had nothing to do with lineages — grouping untagged
parameters by cited source and noticing Hill 2011 appear five times.

So: for each retracted claim, every source file that still mentions it must ALSO carry the retraction marker
nearby. The claim may remain in the file — the reasoning around it is often still sound, and deleting it
would lose the history — but it may not stand unqualified.
"""
import re
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[1] / "src" / "sic_games"

# (label, pattern that finds the retracted claim, pattern that proves the retraction is present)
RETRACTIONS = [
    # The retraction side is matched CASE-INSENSITIVELY and allows "Addendum"/"Addenda" — a guard that demands
    # one exact spelling of the correction is a guard about typography, not about whether the reader is warned.
    ("Hill 2011 as a LINEAGE source (Addendum 28)",
     r"Hill[- ]2011 target|Hill 2011 target|FILED Hill",
     r"does not exist|no lineage data|UNANCHORED|Addend(um|a) 2[89]|retracted"),
    # Matches the DEFINITION line only, not every use. The first version was `ENSO_AMP_(MIN|MAX)\s*[,=]`,
    # which also hit `rng.uniform(ENSO_AMP_MIN, ENSO_AMP_MAX)` in the lottery draw — a legitimate USE of the
    # constant, not a citation of Timmermann. A guard that cries wolf on ordinary code gets switched off.
    ("Timmermann 2018 as the ENSO AMPLITUDE source (Addendum 29)",
     r"^ENSO_AMP_MIN\s*,\s*ENSO_AMP_MAX\s*=",
     r"INTERPRETIVE|RETRACTED"),
    # RESOLVED AND REPLACED, 2026-08-06. This row used to require the words "UNSOURCED|NO PDF" beside any
    # mention of St. John 2022, because the thesis could not be found. The supervisor filed it the same day,
    # it was read, and the row is retired — a retraction guard must be withdrawn when the retraction is, or it
    # becomes a permanent false alarm that trains people to ignore the file.
    # What the reading RETRACTED instead is the period band, so that is what is guarded now.
    ("caribou period 40-90 yr (Addendum 32) — the thesis says 23-67",
     r"40\s*[-–]\s*90\s*yr",
     r"23\s*[-–]\s*67|FALSIFI|corrected"),
]


DOCS = Path(__file__).resolve().parents[2] / "docs"

# RESULTS.md is EXEMPT and must stay so: it is append-only, and its older addenda are the historical record of
# each retraction as it was made. Quoting the superseded claim there is the point, not a defect.
_DOC_EXEMPT = {"RESULTS.md"}


def _files():
    """Source AND the governing docs. The first version scanned only `src/**/*.py`, and on the day the caribou
    band was corrected that let `MODEL_SPEC.md` keep asserting the falsified 40-90 yr range — a live spec claim,
    in the document that is supposed to define the model."""
    py = [p for p in SRC.rglob("*.py") if "__pycache__" not in str(p)]
    md = [p for p in DOCS.glob("*.md") if p.name not in _DOC_EXEMPT]
    return py + md


# How much text around a stale claim counts as "the retraction travels with it". File-level co-occurrence is
# NOT enough: `climate.py` carried the correction in its constants block and the falsified band in a docstring
# 550 lines away, and passed. Proximity is the property that actually matters.
_WINDOW = 1200


@pytest.mark.parametrize("label,claim,retraction", RETRACTIONS, ids=[r[0] for r in RETRACTIONS])
def test_a_retracted_claim_never_stands_unqualified_in_source(label, claim, retraction):
    offenders = []
    for path in _files():
        text = path.read_text(encoding="utf-8", errors="replace")
        for m in re.finditer(claim, text, re.M):
            lo, hi = max(0, m.start() - _WINDOW), min(len(text), m.end() + _WINDOW)
            if not re.search(retraction, text[lo:hi], re.I):
                line = text[:m.start()].count("\n") + 1
                offenders.append(f"{path.name}:{line}")
    assert not offenders, (
        f"{label} is still cited without its retraction NEARBY at: {', '.join(offenders)}. "
        "Charter P3: edit the retracted anchor where it is USED, not only where it was retracted. "
        "A correction elsewhere in the same file does not reach the reader of this line.")


def test_the_guard_would_actually_catch_a_violation(tmp_path):
    """CONSTRUCTED TRUTH for the guard itself — the audit-instrument rule applied to this file. A test that
    can only pass is not a test; this builds a file that violates the rule and confirms the check fires."""
    claim, retraction = RETRACTIONS[0][1], RETRACTIONS[0][2]

    violating = "# the FILED Hill 2011 target is ~7 lineages per band, so 0.15 is ~1/7\nx = 0.15\n"
    assert re.search(claim, violating) and not re.search(retraction, violating), (
        "the guard must flag a bare citation of the retracted target")

    compliant = violating + "# [UNANCHORED] retracted: Hill 2011 has no lineage data (Addendum 28).\n"
    assert re.search(claim, compliant) and re.search(retraction, compliant, re.I), (
        "the guard must accept the same citation once the retraction travels with it")


def test_the_rank_hierarchy_derivation_is_labelled_unanchored():
    """The specific value the void target produced. `rank_hierarchy_frac = 0.15` was documented as DERIVED as
    ~1/7 from a number that does not exist, so it is a free parameter that has been reading as a derived one.
    It is deliberately NOT changed here — re-deriving it is a calibration decision — but it must not present
    as anchored."""
    text = (SRC / "demography.py").read_text(encoding="utf-8", errors="replace")
    # anchor on the FIELD DECLARATION, not the first mention of the name — the retraction note above it also
    # names the parameter, and splitting on the bare name lands in the wrong block (this test found that on
    # its first run)
    m = re.search(r"^\s*rank_hierarchy_frac\s*:\s*float\s*=\s*Field", text, re.M)
    assert m, "rank_hierarchy_frac field declaration not found"
    block = text[m.end():m.end() + 900]
    assert "UNANCHORED" in block, "the value must not present as anchored"
    assert "no lineage data" in block, "the reason must travel with the label"
