"""TIER 3 — AGE AND SEX STRUCTURE against three forager populations. Requested by the supervisor 2026-08-08.

THE ANCHOR: Hill & Hurtado (1996), *Aché Life History: The Ecology and Demography of a Foraging People*,
Aldine de Gruyter — **Table 4.4, p. 141**, "Age-sex Composition of Ache, !Kung, and Yanomamo Populations".
Verified verbatim; all three rows registered in `tools/verify_anchor.py`.

              0-15                15-60               60+              total        % under 15
  Ache 1970   M140 F89  =  229    M160 F128 =  288    M16 F14 =  30      547           41.9
  !Kung 1968  M58  F73  =  131    M141 F145 =  286    M17 F23 =  40      457           28.7
  Yanomamo    M682 F508 = 1190    M738 F667 = 1405    M11 F16 =  27     2622           45.4

**IT USES OUR EXACT AGE CLASSES.** 0-15 / 15-60 / 60+ is precisely `_AGE_CHILD_YR = 15` and
`_AGE_ELDER_YR = 60`, so the dependency ratio needs NO unit conversion — unlike the prose figure of 0.79,
which the book computes with elders at 65. Two anchors from the same book on two different cutoffs, and this
is the one that matches the model.

WHY THREE SOCIETIES MATTER. A single anchor tells you where one population sat; three tell you the RANGE, and
the range here is wide (dependency 0.598 to 0.899, sex ratio 0.896 to 1.368). A model outside a three-society
range is outside the ethnographic envelope, not merely away from one datum.

A CORRECTION ON THE RECORD: this table was first recorded as "OCR-garbled, not machine-readable" and that was
wrong. Searching for the string "Table 4.4" returned a context window that landed on a different, genuinely
garbled table nearby, and I attributed its content to this one. The table extracts cleanly.
"""
import pytest

# ── Table 4.4, p.141 — verbatim ───────────────────────────────────────────────────────────────────────────
#          name          (M,F) 0-15      (M,F) 15-60     (M,F) 60+
TABLE_4_4 = {
    "Ache 1970":     ((140, 89), (160, 128), (16, 14)),
    "!Kung 1968":    ((58, 73), (141, 145), (17, 23)),
    "Yanomamo 1960s": ((682, 508), (738, 667), (11, 16)),
}

# Measured on long_climate (30,000 steps), last 40 checkpoints.
MODEL = {"dependency_ratio": 1.495, "frac_child": 0.585, "median_age_yr": 11.84,
         "sex_ratio_m_f": 1.061, "adult_sex_ratio": 1.046}


def _n(soc, band):
    m, f = TABLE_4_4[soc][band]
    return m + f


def dependency(soc):
    """(under 15 + 60 and over) / (15-60) — the model's own definition, which is this table's own classes."""
    return (_n(soc, 0) + _n(soc, 2)) / _n(soc, 1)


def frac_child(soc):
    return _n(soc, 0) / sum(_n(soc, b) for b in range(3))


def sex_ratio(soc, bands=(0, 1, 2)):
    m = sum(TABLE_4_4[soc][b][0] for b in bands)
    f = sum(TABLE_4_4[soc][b][1] for b in bands)
    return m / f


# ── the table reproduces its own printed totals ───────────────────────────────────────────────────────────

@pytest.mark.parametrize("soc,total,pct_child", [
    ("Ache 1970", 547, 41.9), ("!Kung 1968", 457, 28.7), ("Yanomamo 1960s", 2622, 45.4)])
def test_the_transcribed_table_reproduces_its_printed_totals(soc, total, pct_child):
    """CTB on the TRANSCRIPTION before any use of it. The printed n and percent columns are independent of the
    male/female cells, so if they agree the cells were copied correctly."""
    assert sum(_n(soc, b) for b in range(3)) == total
    assert frac_child(soc) * 100 == pytest.approx(pct_child, abs=0.1)


def test_the_tables_age_classes_are_the_models_own_cutoffs():
    """Why this anchor beats the prose 0.79: no conversion. The book's prose ratio uses 65 for elders; this
    table uses 60, which is `_AGE_ELDER_YR`."""
    from sic_games.phase1_model import TerrainWorld
    assert TerrainWorld._AGE_CHILD_YR == 15.0
    assert TerrainWorld._AGE_ELDER_YR == 60.0


# ── the model against the ethnographic range ──────────────────────────────────────────────────────────────

def test_the_ethnographic_dependency_range_and_where_the_model_falls():
    """THE FINDING. Three real forager populations span 0.598-0.899. The model reads 1.495 — **1.66x the
    highest** and 2.5x the lowest. Every one of the three has more workers than dependants; the model has
    more dependants than workers."""
    ratios = {s: dependency(s) for s in TABLE_4_4}
    assert ratios["!Kung 1968"] == pytest.approx(0.598, abs=0.002)
    assert ratios["Yanomamo 1960s"] == pytest.approx(0.866, abs=0.002)
    assert ratios["Ache 1970"] == pytest.approx(0.899, abs=0.002)

    hi = max(ratios.values())
    assert all(r < 1.0 for r in ratios.values()), "no forager population has more dependants than workers"
    assert MODEL["dependency_ratio"] > hi
    assert MODEL["dependency_ratio"] / hi == pytest.approx(1.66, abs=0.03)


def test_the_child_fraction_is_outside_the_three_society_range_too():
    """Same fault, second view. The three span 28.7-45.4% under 15; the model reads 58.5%."""
    fracs = [frac_child(s) for s in TABLE_4_4]
    assert min(fracs) == pytest.approx(0.287, abs=0.002)
    assert max(fracs) == pytest.approx(0.454, abs=0.002)
    assert MODEL["frac_child"] > max(fracs) + 0.10, "outside the range by a wide margin, not at its edge"


def test_the_two_book_anchors_differ_because_their_ELDER_CUTOFFS_differ():
    """The book gives 0.79 in prose (elders at 65) and this table gives 0.899 on the same population (elders
    at 60). Both are correct; they are different quantities. Pinned so nobody 'corrects' one to the other.

    Moving the cutoff from 65 to 60 shifts 60-65-year-olds from workers to dependants, which RAISES the ratio
    — and 0.899 > 0.79, the expected direction."""
    assert dependency("Ache 1970") > 0.79
    assert dependency("Ache 1970") - 0.79 == pytest.approx(0.109, abs=0.01)


# ── sex ratio: the side that was previously unanchored ────────────────────────────────────────────────────

def test_the_sex_ratio_range_across_the_three_societies():
    """Now anchored, and the spread is large: !Kung are female-biased, Ache strongly male-biased."""
    assert sex_ratio("!Kung 1968") == pytest.approx(0.896, abs=0.003)
    assert sex_ratio("Yanomamo 1960s") == pytest.approx(1.202, abs=0.003)
    assert sex_ratio("Ache 1970") == pytest.approx(1.368, abs=0.003)


def test_the_model_sex_ratio_is_INSIDE_the_ethnographic_range():
    """The one age/sex measure that passes. 1.061 sits between the !Kung (0.896) and the Yanomamo (1.202).
    Worth stating plainly given how much else at this tier does not."""
    lo, hi = sex_ratio("!Kung 1968"), sex_ratio("Ache 1970")
    assert lo < MODEL["sex_ratio_m_f"] < hi
    assert lo < MODEL["adult_sex_ratio"] < hi


def test_the_model_is_far_less_male_biased_than_the_ACHE_whose_mortality_it_uses():
    """A CONSISTENCY FLAG, not a failure. The Siler schedule is fitted to the Ache (Gurven & Kaplan), and the
    Ache adult sex ratio is 1.250 against the model's 1.046. The M-3 sex split exists precisely to produce
    this, so a model using Ache mortality and landing near !Kung sex composition is worth a look — the split
    may be too weak, or the excess turnover may be washing it out."""
    ache_adult = TABLE_4_4["Ache 1970"][1][0] / TABLE_4_4["Ache 1970"][1][1]
    assert ache_adult == pytest.approx(1.250, abs=0.003)
    assert MODEL["adult_sex_ratio"] < ache_adult
    assert ache_adult - MODEL["adult_sex_ratio"] > 0.15


def test_the_ache_juvenile_sex_ratio_is_the_most_extreme_cell_in_the_table():
    """1.573 males per female under 15 — the book attributes it to male-biased sex ratio at birth, higher
    female childhood mortality, and preferential female infanticide. Recorded because it is the strongest
    signal in the table and the model produces nothing like it."""
    assert sex_ratio("Ache 1970", bands=(0,)) == pytest.approx(1.573, abs=0.003)
    assert sex_ratio("!Kung 1968", bands=(0,)) == pytest.approx(0.795, abs=0.003)


def test_all_three_societies_are_registered_as_verified_anchors():
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
    from verify_anchor import REGISTRY, check
    rows = {lab: check(rel, pat) for lab, rel, pat in REGISTRY if "Table 4.4" in lab or "via Table 4.4" in lab}
    assert len(rows) == 3, rows
    assert all(s == "VERIFIED" for s, _ in rows.values()), rows
