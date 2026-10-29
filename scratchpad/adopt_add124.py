"""R-106 Add.124: adopt the pair enable_condition_full_scale + enable_orphan_norm_by_age (supervisor option A, after
Add.123), with the Add.113/121 steps. Edits are asserted to match exactly once. The MARKER_MATRIX current scorecard is
regenerated from docs/evidence/scorecard_add122_pair.json (no number typed by hand)."""
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
    '''            # MORTALITY-STRUCTURE FIXES from the external audit (R-106 Addendum 118, 2026-10-27). THREE ADOPTED
            # (Addendum 121, 2026-10-28) and so REMOVED from this set -> canonically ON: lifespan_from_siler,
            # density_common_window, eta_once (together, 3 worlds x 3 paired seeds: every banded marker PASSES).
            # The full-scale body condition stays held: alone it puts temperate over the forager band, because the
            # pooled orphan divisor below hides a third of infant deaths (Addendum 120); it is evaluated as a PAIR
            # with the per-age divisor.
            "enable_condition_full_scale",
            # ORPHAN NORMALISATION BY AGE (R-106 Addendum 120): the pooled divisor gives infants with living parents
            # x0.66 of the schedule hazard. A correction under evaluation (with condition_full_scale), so C_ALLON
            # must not enable it by side effect.
            "enable_orphan_norm_by_age",
''',
    '''            # MORTALITY-STRUCTURE FIXES from the external audit (R-106 Addenda 118-124) — ALL ADOPTED and so REMOVED
            # from this set -> canonically ON: lifespan_from_siler, density_common_window, eta_once (Addendum 121);
            # condition_full_scale + orphan_norm_by_age as a PAIR (Addendum 124): with both, the non-starvation
            # hazard equals its Siler schedule at every age on every world (Addendum 122).
''')
sub("sic_games/tests/test_campaign_knobs.py",
    '''               "enable_sticky_pin_release",
               # FULL-SCALE CONDITION (R-106 Addendum 118): under evaluation as a pair with the per-age orphan
               # divisor, held dark. (lifespan_from_siler, density_common_window, eta_once: ADOPTED, Add.121 -> ON.)
               "enable_condition_full_scale",
               # ORPHAN NORMALISATION BY AGE (R-106 Addendum 120): under evaluation, held dark.
               "enable_orphan_norm_by_age"}''',
    '''               "enable_sticky_pin_release"}
               # (the five mortality-structure fixes, Addenda 118-124: ADOPTED -> canonically ON.)''')
sub("sic_games/tests/test_runconfig_sync.py",
    '''               "enable_sticky_pin_release",
               #   condition_full_scale  (Add.118), in Stage 2 as a pair with orphan_norm_by_age
               #   (lifespan_from_siler, density_common_window, eta_once: ADOPTED, Add.121 -> canonically ON)
               "enable_condition_full_scale",
               #   orphan_norm_by_age  the per-age orphan divisor (Add.120), in Stage 2
               "enable_orphan_norm_by_age"}''',
    '''               "enable_sticky_pin_release"}
               # (the five mortality-structure fixes, Addenda 118-124: ADOPTED -> canonically ON.)''')
for f in ("enable_condition_full_scale", "enable_orphan_norm_by_age"):
    sub("config/runs/full_campaign.toml", f"{f} = false\n", f"{f} = true\n")
NOTE = ("    # ADOPTED (R-106 Addendum 124, supervisor 2026-10-29) as a PAIR with the other of condition_full_scale /\n"
        "    # orphan_norm_by_age: with both, the hazard equals its schedule at every age (Add.122). Canonically ON via\n"
        "    # C_ALLON; class default stays False.\n")
for f in ("enable_condition_full_scale", "enable_orphan_norm_by_age"):
    sub("sic_games/src/sic_games/demography.py", f"    {f}: bool = False\n", NOTE + f"    {f}: bool = False\n")

S = json.load(open(os.path.join(ROOT, "docs", "evidence", "scorecard_add122_pair.json"), encoding="utf-8"))["summary"]
W = ["temperate", "savanna", "montane"]


def cell(lab, w):
    c = S[lab][w]
    v = f"{c['mean']:.3g} ± {st.stdev(c['values']) / len(c['values']) ** 0.5:.3g}"
    return v + (f" **{c['verdict']}**" if c.get("verdict") else "")


rows = [f"| {lab} | " + " | ".join(cell(lab, w) for w in W) + " |" for lab in S if not lab.startswith("context")]
ctx = " · ".join(f"{lab[len('context: '):]}: " + " / ".join(f"{S[lab][w]['mean']:.3g}" for w in W)
                 for lab in S if lab.startswith("context"))
p = os.path.join(ROOT, "docs", "MARKER_MATRIX.md")
s = open(p, encoding="utf-8").read()
a, b = s.index("## CURRENT SCORECARD"), s.index("---\n\n**Binding rules")
new = f"""## CURRENT SCORECARD — canon as of R-106 Addendum 124 (re-scored 2026-10-29)

**Read this table for the CURRENT verdicts.** The per-row "status" texts in the matrix below are each marker's
HISTORY (the dated reasoning that set its band, unit and statistic); several of their numbers were measured on
earlier canons and are superseded by this table. Evidence (committed): `docs/evidence/scorecard_add122_pair.json`;
previous canons: `scorecard_add118_three.json` (Add.121), `scorecard_add113_canon.json` (Add.113). Re-score after any
adoption with `tools/scorecard.py` (rule 5 below: absolute values are valid only on the canon they were measured on).

**Runs:** the nine Stage-2 runs of the adopted Add.124 canon (`pair` arm = the Add.121 canon + `condition_full_scale` +
`orphan_norm_by_age`) — real `run_campaign.py` pipeline, 3 canonical worlds × 3 paired demographic seeds, planet fixed
(world/climate seed 0), 15,000 steps. **Method:** per run, the mean over the sustained window (last 15% of rows); #18–#21
from the PERIOD life table (step 7,500 → 15,000); per world, mean ± SE over the 3 seeds; verdict at 1 SE — **PASS** = the
interval inside the band, **FAIL** = outside, **unres.** = straddles an edge; no verdict = no documented band, or the
marker is report-only (#3 max: the ceiling is scored at #17 on the co-residence unit, Add.104; #11: NOT COMPARABLE, wrong
channel, Add.102; #5/#8/#9: need a per-generation / per-village-year / cross-world computation that this table does not
make).

| marker | temperate | savanna | montane |
|---|---|---|---|
""" + "\n".join(rows) + f"""

Context: {ctx}.

**Summary.** With the five mortality fixes of Addenda 118–124 the non-starvation hazard equals its Siler schedule (the
de-warfared Aché, e0 42.7, MODEL_SPEC §4.6.1) at every age on every world, and starvation is the only addition.
Savanna and montane pass #18–#21. **Temperate FAILS #18 and #19 by a small margin** (e0 37.45 against the band's top
37; l15 0.662 against 0.66) and #21 is unresolved: the band's top edge is the Aché TOTAL schedule (contact-era warfare
included) while the model runs the de-warfared schedule by design — the expected result in a well-fed world, recorded
by the supervisor's decision (Add.123 option A, Add.124). Also changed: temperate #1 band size 41.0 unres. (Add.121:
38.2 PASS), savanna #12 rank-size unres. m(5–15), which no earlier canon passed, is 0.0115 in temperate (Aché ~0.010).
TFR is no longer scored against the growth-phase band [4.69, 8.03] but by the stationary iso-growth identity (Add.124).

"""
open(p, "w", encoding="utf-8", newline="").write(s[:a] + new + s[b:])
print("adoption edits done")
