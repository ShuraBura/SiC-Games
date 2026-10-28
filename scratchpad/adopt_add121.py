"""R-106 Add.121: adopt enable_lifespan_from_siler + enable_density_common_window + enable_eta_once (the Add.113 steps).

Edits, each asserted to match exactly once: the _skip set, both allowed-dark test lists, the canon run file, an
ADOPTED note on each DemographyConfig field (class defaults stay False), and the MARKER_MATRIX current scorecard,
regenerated from docs/evidence/scorecard_add118_three.json (no number typed by hand).
"""
import json
import os
import statistics as st

ROOT = r"C:\Users\syatom\Projects\SiC Games"


def sub(rel, a, b):
    p = os.path.join(ROOT, rel)
    s = open(p, encoding="utf-8").read()
    assert s.count(a) == 1, (rel, a[:60])
    open(p, "w", encoding="utf-8", newline="").write(s.replace(a, b))


sub("sic_games/outputs/substrate_run/run_campaign.py",
    '''            # MORTALITY-STRUCTURE FIXES from the external audit (R-106 Addendum 118, 2026-10-27): the 900-month
            # lifespan cap, the constant body-condition signal, the regional-vs-local disease density, and the double
            # η. Each changes mortality in every run and is UNDER EVALUATION in Stage 2 (single-fix arms first), so
            # C_ALLON must not enable them by side effect.
            "enable_lifespan_from_siler", "enable_condition_full_scale", "enable_density_common_window",
            "enable_eta_once",
''',
    '''            # MORTALITY-STRUCTURE FIXES from the external audit (R-106 Addendum 118, 2026-10-27). THREE ADOPTED
            # (Addendum 121, 2026-10-28) and so REMOVED from this set -> canonically ON: lifespan_from_siler,
            # density_common_window, eta_once (together, 3 worlds x 3 paired seeds: every banded marker PASSES).
            # The full-scale body condition stays held: alone it puts temperate over the forager band, because the
            # pooled orphan divisor below hides a third of infant deaths (Addendum 120); it is evaluated as a PAIR
            # with the per-age divisor.
            "enable_condition_full_scale",
''')
sub("sic_games/tests/test_campaign_knobs.py",
    '''               # MORTALITY-STRUCTURE FIXES (R-106 Addendum 118): under evaluation in Stage 2, held dark.
               "enable_lifespan_from_siler", "enable_condition_full_scale", "enable_density_common_window",
               "enable_eta_once",''',
    '''               # FULL-SCALE CONDITION (R-106 Addendum 118): under evaluation as a pair with the per-age orphan
               # divisor, held dark. (lifespan_from_siler, density_common_window, eta_once: ADOPTED, Add.121 -> ON.)
               "enable_condition_full_scale",''')
sub("sic_games/tests/test_runconfig_sync.py",
    '''               #   the four mortality-structure fixes (Add.118), in Stage 2
               "enable_lifespan_from_siler", "enable_condition_full_scale", "enable_density_common_window",
               "enable_eta_once",''',
    '''               #   condition_full_scale  (Add.118), in Stage 2 as a pair with orphan_norm_by_age
               #   (lifespan_from_siler, density_common_window, eta_once: ADOPTED, Add.121 -> canonically ON)
               "enable_condition_full_scale",''')
for f in ("enable_lifespan_from_siler", "enable_density_common_window", "enable_eta_once"):
    sub("config/runs/full_campaign.toml", f"{f} = false\n", f"{f} = true\n")
NOTE = ("    # ADOPTED (R-106 Addendum 121, supervisor 2026-10-28) together with the other two of lifespan_from_siler /\n"
        "    # density_common_window / eta_once: every banded marker passes on 3 worlds. Canonically ON via C_ALLON; class\n"
        "    # default stays False.\n")
sub("sic_games/src/sic_games/demography.py", "    enable_lifespan_from_siler: bool = False\n",
    NOTE + "    enable_lifespan_from_siler: bool = False\n")
sub("sic_games/src/sic_games/demography.py", "    enable_density_common_window: bool = False\n",
    NOTE + "    enable_density_common_window: bool = False\n")
sub("sic_games/src/sic_games/demography.py", "    enable_eta_once: bool = False\n",
    NOTE + "    enable_eta_once: bool = False\n")

# ---- MARKER_MATRIX current scorecard, from the evidence file ----
S = json.load(open(os.path.join(ROOT, "docs", "evidence", "scorecard_add118_three.json"), encoding="utf-8"))["summary"]
W = ["temperate", "savanna", "montane"]


def cell(lab, w):
    c = S[lab][w]
    se = st.stdev(c["values"]) / len(c["values"]) ** 0.5
    v = f"{c['mean']:.3g} ± {se:.3g}"
    return v + (f" **{c['verdict']}**" if c.get("verdict") else "")


rows = [f"| {lab} | " + " | ".join(cell(lab, w) for w in W) + " |" for lab in S if not lab.startswith("context")]
ctx = " · ".join(f"{lab[len('context: '):]}: " + " / ".join(f"{S[lab][w]['mean']:.3g}" for w in W)
                 for lab in S if lab.startswith("context"))
p = os.path.join(ROOT, "docs", "MARKER_MATRIX.md")
s = open(p, encoding="utf-8").read()
a = s.index("## CURRENT SCORECARD")
b = s.index("---\n\n**Binding rules")
new = f"""## CURRENT SCORECARD — canon as of R-106 Addendum 121 (re-scored 2026-10-28)

**Read this table for the CURRENT verdicts.** The per-row "status" texts in the matrix below are each marker's
HISTORY (the dated reasoning that set its band, unit and statistic); several of their numbers were measured on
earlier canons and are superseded by this table. Evidence (committed): `docs/evidence/scorecard_add118_three.json`;
previous canon for comparison: `docs/evidence/scorecard_add113_canon.json` (`scorecard_add118_riskvg.json` is the same
canon re-scored from the Add.118 Stage 2). Re-score after any adoption with `tools/scorecard.py` (rule 5 below: absolute
values are valid only on the canon they were measured on).

**Runs:** the nine Stage-2 runs of the adopted Add.121 canon (`three` arm = the Add.113 canon + `lifespan_from_siler`,
`density_common_window`, `eta_once`) — real `run_campaign.py` pipeline, 3 canonical worlds × 3 paired demographic seeds,
planet fixed (world/climate seed 0), 15,000 steps. **Method:** per run, the mean over the sustained window (last 15% of
rows); #18–#21 from the PERIOD life table (step 7,500 → 15,000); per world, mean ± SE over the 3 seeds; verdict at 1 SE
— **PASS** = the interval inside the band, **FAIL** = outside, **unres.** = straddles an edge; no verdict = no documented
band, or the marker is report-only (#3 max: the ceiling is scored at #17 on the co-residence unit, Add.104; #11: NOT
COMPARABLE, wrong channel, Add.102; #5/#8/#9: need a per-generation / per-village-year / cross-world computation that this
table does not make).

| marker | temperate | savanna | montane |
|---|---|---|---|
""" + "\n".join(rows) + f"""

Context: {ctx}.

**Summary.** EVERY banded marker PASSES on every world (Add.113 left two unresolved on temperate, #1 band size and #17
fission ceiling; both pass now). The adoption raised e0 by 0.9–1.1 yr and savanna/montane l15 by 0.01–0.02 (all within
band) and removed the age-75 death spike (`modal_adult_death` is no longer the 900-month placeholder). **Known
compensating defects still in this canon (Add.120):** the constant synergy (×2 on ages 5–15, why m(5–15) never passes)
and the pooled orphan divisor (infants ×0.66). Fixing either alone moves #18/#19 out of band; they are under evaluation
as a pair.

"""
open(p, "w", encoding="utf-8", newline="").write(s[:a] + new + s[b:])
print("adoption edits done")
