"""Anchor verification: pull the QUOTED text out of a source PDF and show it, so a number in the code can be
checked against the page that is supposed to carry it.

This exists because of a repeated failure mode (Addendum 28, the Bar-Yosef case): a number is written into a
code comment with a citation, the comment is then trusted by everything downstream, and nobody ever opens the
paper. Four MARKER_MATRIX rows were mis-attributed that way. MECHANISM_CHARTER P1 says docs cite rather than
restate; this is the tool that makes citing cheap.

Usage:
    py -3 tools/verify_anchor.py <pdf> <regex> [<regex> ...]      # show every match with context
    py -3 tools/verify_anchor.py --list                           # the registry of wired anchors, checked

An anchor is VERIFIED when the number in the code appears in the source text. It is UNVERIFIED when the PDF is
present and the number is absent (which is a finding, not an error), and UNSOURCED when there is no PDF.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LIT = ROOT / "literature"


def pdf_text(path: Path) -> str:
    import fitz
    with fitz.open(path) as doc:
        return "\n".join(page.get_text() for page in doc)


def _norm(s: str) -> str:
    """Collapse the whitespace and unify the dash zoo, so a regex written with a plain hyphen matches text that
    uses an en-dash, and a phrase that broke across a line still matches."""
    return re.sub(r"\s+", " ", s.replace("–", "-").replace("—", "-").replace("−", "-"))


def find(path: Path, pattern: str, width: int = 160) -> list[str]:
    text = _norm(pdf_text(path))
    out = []
    for m in re.finditer(pattern, text, re.I):
        lo, hi = max(0, m.start() - width), min(len(text), m.end() + width)
        out.append(text[lo:hi])
    return out


# ── the registry ───────────────────────────────────────────────────────────────────────────────────────────
# Each entry is (label, pdf-relative-path-or-None, regex-or-None). Three outcomes, and the middle one is the
# reason the tool exists:
#
#   VERIFIED     the number is printed in the source (or falls out of a documented conversion of numbers that
#                are printed in the source)
#   INTERPRETIVE pattern None -- the value is a MODELLING JUDGEMENT that the cited paper informs but does not
#                state. Legitimate, but it must SAY so, because an interpretive value scored against a marker
#                is being scored against our own opinion.
#   UNSOURCED    path None -- no PDF, so nothing can be checked at all
#
# Verified 2026-08-06 against the PDFs in literature/. Anything added here must be run, not assumed.
REGISTRY = [
    # ── climate: the four anchors wired in 2026-08-04, checked against the papers for the first time ────────
    ("Timmermann 2018 - ENSO period, EOF1 quasi-quadrennial 3-7 yr",
     "SiC_Games_B1.1_Timmermann2018_ENSOComplexity.pdf",
     r"quasi-quadrennial timescales \(3-7 years"),
    ("Timmermann 2018 - ENSO period, EOF2 quasi-biennial ~2 yr (the lower bound of our 2-7 band)",
     "SiC_Games_B1.1_Timmermann2018_ENSOComplexity.pdf",
     r"timescales of approximately four and two years"),
    ("ENSO amplitude 0.20-0.40 of carrying capacity",
     "SiC_Games_B1.1_Timmermann2018_ENSOComplexity.pdf",
     None),   # INTERPRETIVE -- Timmermann is an SST-dynamics review and states no production amplitude
    ("Wanner 2008 - AD 1000-1850 peak-to-peak global mean ~0.5 degC",
     "SiC_Games_B1.4a_Wanner2008_HoloceneClimateOverview.pdf",
     r"peak to peak variations in the order of 0\.5"),
    ("Regime amplitude 0.10-0.15 of carrying capacity (the degC->CC%% step)",
     "SiC_Games_B1.4a_Wanner2008_HoloceneClimateOverview.pdf",
     None),   # INTERPRETIVE -- and LITERATURE.md already says so; kept here so both siblings read alike
    ("Sarmiento 2004 - flood-year ANPP, ungrazed 1996 vs 1997 (265/418 vs 601/659 g/m2)",
     "Sarmiento et al. - 2004 - Effects of soil water regime and grazing on vegetation diversity and production in a hyperseasonal s.pdf",
     r"Total ANPP \(\*\) 236 . 36 265 . 38 428 . 71 601 . 58"),
    ("Hawkes 1991 - Hadza encounter 0.71 vs intercept 1.02 kg/hr (Table 2), the 518/745 kcal/hr inputs",
     "hawkes-1991-pdf.pdf",
     r"mean number of hours spent by adult men in day-time foraging was about 4\.5"),
    # Was UNSOURCED on the morning of 2026-08-06; the supervisor filed the thesis that afternoon. The pattern
    # deliberately matches ".871" WITHOUT a leading zero -- the paper writes it that way, and searching for
    # "0.871" returned nothing on a paper that plainly contains the number.
    ("St. John 2022 - caribou amplitude, median of 19 cyclic herds",
     "Understanding Caribou Population Cycles.pdf",
     r"Median=\.871"),
    ("St. John 2022 - caribou period distribution 23-67 yr (median 40.5), which FALSIFIED our 40-90 band",
     "Understanding Caribou Population Cycles.pdf",
     r"Min=23, Q1=33, Median=40\.5, Q3=50, Max=67"),
    ("St. John 2022 - only 19 of 43 herds are cyclic",
     "Understanding Caribou Population Cycles.pdf",
     r"of the 43 herds, I only 19 were deemed cyclic"),

    # ── settlement/demography anchors touched by the 2026-08-05 provenance sweep ───────────────────────────
    ("Alberti 2014 - scalar-stress community-size threshold 127 (95%% CI 122-132)",
     "SiC_Games_D1_Alberti2014_ScalarStressLogistic.pdf",
     r"critical scalar stress threshold at community size 127"),
    ("Alvard 2009 - Yanomamo village 50-250",
     "AlvardPaper2.pdf",
     r"50 or so up to 250"),
    ("Hamilton 2007 - aggregated group 53.66",
     "Hamilton et al. - 2007 - The complex structure of hunter–gatherer social networks.pdf",
     r"53\.66"),
    # Cited in MARKER_MATRIX as "Marlowe, The Hadza" -- an author and a book, the citation shape that failed
    # for Bar-Yosef, BHM, Hill 2011 and Timmermann. It survived only because the book is filed. Registered
    # 2026-08-07 so the check is mechanical, and note what the sentence says the DENOMINATOR is: all MEN.
    ("Marlowe, The Hadza - polygyny ~4% of MEN (not of married men), never more than two wives",
     "The Hadza- Hunter-Gatherers of Tanzania (Origins of Human -- Frank Marlowe, Frank Marlowe -- ( WeLib.org ).pdf",
     r"about 4% of men have 2 wives at any given time, but never more than two wives"),
    # TIER 3 age-structure anchor, found 2026-08-08. The DEFINITION travels with the number in the prose,
    # which is what makes it checkable -- and it differs from ours (they cut elders at 65, we cut at 60).
    ("Ache precontact (1970) dependency ratio 0.79, defined as (<15 or >65) / (15-65)",
     "Aché life history - the ecology and demography of a -- Kim Hill and A. Magdalena Hurtado -- ( WeLib.org ).pdf",
     r"0\.79 for 1970"),
    # Table 4.4, p.141. I FIRST RECORDED THIS AS "OCR-garbled, not machine-readable" AND THAT WAS WRONG:
    # searching for the string "Table 4.4" returned a context window that landed on a DIFFERENT, genuinely
    # garbled table nearby, and I attributed its content to this one. The table itself extracts cleanly.
    # Three societies on OUR EXACT age classes (0-15 / 15-60 / 60+), which is why no unit conversion is needed.
    ("Ache 1970 precontact age-sex composition (Table 4.4 p.141): 229/288/30, M316 F231",
     "Aché life history - the ecology and demography of a -- Kim Hill and A. Magdalena Hurtado -- ( WeLib.org ).pdf",
     r"Ache 1970 0-15 140 89 229"),
    ("!Kung 1968 age-sex composition (Lee 1979:45, via Table 4.4): 131/286/40",
     "Aché life history - the ecology and demography of a -- Kim Hill and A. Magdalena Hurtado -- ( WeLib.org ).pdf",
     r"Kung 1968\* - 0-15 58 73 131"),
    ("Yanomamo 1960s age-sex composition (Neel & Weiss 1975:28, via Table 4.4): 1190/1405/27",
     "Aché life history - the ecology and demography of a -- Kim Hill and A. Magdalena Hurtado -- ( WeLib.org ).pdf",
     r"0-15 682 508 1190"),
    ("Hayden 1995 Fig. 6 - transegalitarian density bands",
     "hayden1995.pdf",
     None),   # a FIGURE: the bands were read off the page image, which no text search can confirm
]

_TAGS = {"VERIFIED": "[VERIFIED    ]", "INTERPRETIVE": "[INTERPRETIVE]",
         "UNSOURCED": "[UNSOURCED   ]", "MISSING": "[MISSING     ]", "UNVERIFIED": "[UNVERIFIED  ]"}


def check(rel, pattern) -> tuple[str, str]:
    """Classify one registry row. Returns (status, evidence)."""
    if rel is None:
        return "UNSOURCED", "no PDF in literature/ -- the number cannot be checked"
    path = LIT / rel
    if not path.exists():
        return "MISSING", f"expected {rel}"
    if pattern is None:
        return "INTERPRETIVE", f"source present ({Path(rel).name}); the VALUE is our judgement, not its text"
    hits = find(path, pattern)
    if hits:
        return "VERIFIED", "..." + hits[0].strip() + "..."
    return "UNVERIFIED", f"PDF present, pattern /{pattern}/ absent"


def run_registry() -> int:
    bad = 0
    for label, rel, pattern in REGISTRY:
        status, evidence = check(rel, pattern)
        print(f"{_TAGS[status]} {label}\n               {evidence}")
        if status in ("UNVERIFIED", "MISSING"):
            bad += 1
    n = len(REGISTRY)
    print(f"\n{n - bad}/{n} rows accounted for; {bad} could not be checked against their own source")
    return bad


def main(argv: list[str]) -> int:
    # PDF text carries ligatures, dingbats and degree signs that the Windows console codepage cannot encode;
    # a quotation must never die on the way to the screen.
    try:
        sys.stdout.reconfigure(errors="replace")
    except AttributeError:
        pass
    if not argv or argv[0] == "--list":
        return 0 if run_registry() == 0 else 1
    path = Path(argv[0])
    if not path.exists():
        path = LIT / argv[0]
    for pattern in argv[1:] or [r"."]:
        print(f"--- /{pattern}/ in {path.name} ---")
        for h in find(path, pattern)[:20]:
            print(f"  ...{h.strip()}...")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
