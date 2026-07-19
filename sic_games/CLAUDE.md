# SiC Games — Claude Code Instructions

## What this project is

SiC Games is an agent-based model comparing C (cooperative) and Si (individualist)
civilisations on matched Sugarscape resource worlds. Central question: H1(ii) —
which strategy is more resilient to periodic resource shocks?

The human supervisor directs the science. Claude Code implements blueprints exactly
as written. When in doubt about scope: stop and ask, do not improvise.

---

## File structure

```
sic_games/
  src/sic_games/              — core simulation package
    config.py                 — Pydantic config models
    world.py                  — grid, sugar, growback
    world_perturbation.py     — seasonal oscillation protocol
    metrics.py                — all logged metrics
    joint_task.py             — JT manager (spatial hash)
    support_pool.py           — L1/L2/L3 pool mechanics
    substrate.py              — multi-occupancy spatial substrate (Stage 6.0a)
    oracle.py                 — archival SugarWorld (D4 backward-compat target)
    run.py                    — 16-line backward-compat re-export
    soa.py                    — SoA data structures
    soa_jt.py                 — vectorised JT manager (VecJTM)
    soa_step.py               — SoAWorld production model
    soa_tier1.py              — Tier-1 determinism helpers
    terrain.py                — Stage 7 terrain generator
    batch.py                  — BatchRunner (CRN, parallel)
    report.py                 — HTML report generator
    agents/
      base.py                 — BaseAgent
      costs.py                — per-agent metabolic costs
      decision.py             — decision dispatch
      perception.py           — LocalVisionPerception
      reproduction.py         — biparental + fission
      traits.py               — cultural trait vector H_i
    strategies/
      carbon.py               — C decision
      si_bounded.py           — Si decision
      softmax_base.py         — shared softmax
      greedy.py               — greedy baseline
  tests/                      — full test suite
  configs/                    — YAML run configs
  scripts/                    — sweep and calibration scripts
  BUGS.md                     — known-issues ledger
  CLAUDE.md                   — this file (master agent contract)
  pyproject.toml              — package metadata
```

**Documentation lives in `../docs/` (the charter's 11 homes), not here.**
INDEX, ROADMAP, ARCHITECTURE, MECHANISMS, TARGETS, HYPOTHESES, RESULTS,
ARTIFACTS, LITERATURE, DEAD_ENDS (+ DOCS_CHARTER) all live under `../docs/`
(reorg 2026-06-05; MODEL_SPEC split into ARCHITECTURE + MECHANISMS 2026-06-06).
**PARAMETERS.md extracted 2026-06-08** — authoritative home for all parameter values, lock history, and status. Route via `../docs/PARAMETERS.md`. Governance: `../docs/DOCS_CHARTER.md`.

---

## Common commands

```bash
pytest tests/ -q                               # run full test suite
pytest tests/test_X.py -q                      # run single test file
python -m sic_games.run configs/X.yaml         # single run
python -m sic_games.batch configs/             # BatchRunner
python -m cProfile -s cumtime sic_games/run.py # profile
```

---

## Standing rules — apply to every task, every stage

**These rules are non-negotiable. They cannot be overridden by a blueprint.**

1. **Never change science without explicit supervisor approval.**
   Science = agent behaviour, RNG draw order, any locked parameter value,
   any mechanic logic. Optimisations that are numerically exact are fine.
   Anything that could change a simulation output is a science change.

2. **Numerical equivalence gate before merging any code change.**
   Run B0: 50×50, N=250, seed=42, static world, C strategy, 500 steps.
   Save reference parquet BEFORE the change. Compare AFTER.
   Required to pass: population N(t) exact, mean_wealth/gini_wealth/mean_cred
   to 1e-9 relative tolerance, deaths/births/positions exact integer match.
   If gate fails: revert immediately, bisect, flag in report.

3. **Run full test suite after every code change.** All tests must pass
   before proceeding. If a test breaks, fix it before the next step.

4. **Implement and test before running simulations.** Never run a production
   job against unverified code.

5. **Apply fixes one at a time.** Confirm suite + equivalence after each.
   Never batch multiple changes before verifying.

6. **Grep before applying any periodic/cached metric fix.**
   `grep -rn "FUNCTION_NAME" src/ --include="*.py" | grep -v metrics.py | grep -v test_`
   Any hit outside the expected file = HIGH risk, stop and flag.

7. **Report format: HTML, self-contained, base64 figures, no external deps.**
   Figures embedded as base64. No CDN links. No external JS.

8. **Report every run with numbers.** No PASS/FAIL without the actual values.
   Every run that executes must appear in the report.

9. **Do not add mechanics, parameters, or config keys not specified in the
   blueprint.** If something is missing from the spec, flag it — do not infer.

10. **Keep the docs homes current — one fact, one home (charter discipline).**
    Each home in `../docs/` has an update trigger; honor it in the *same* change
    that creates the fact. Pointers, not copies. Triggers (see `../docs/INDEX.md`):
    - **End of every stage/directive →** update `../docs/ROADMAP.md` (mark complete,
      note deferred items). Parameter *values* are pointed to, not restated.
    - **Any parameter lock / sweep / retirement →** update `../docs/PARAMETERS.md`
      *(interim, until the §6 extraction: the locked-param table in THIS file below)*.
    - **A construct introduced/redefined or its lock status changes →** update
      `../docs/MECHANISMS.md` (per-construct registry, §0–§11). **A seam, a
      decomposition change, or a design decision →** `../docs/ARCHITECTURE.md`
      (§12 decision-log is append-only; §13 seams; §15 gaps).
    - **Before any analysis that could HARK; on resolution →** `../docs/HYPOTHESES.md`
      (append-only). Aspirations without a test spec go to `../docs/TARGETS.md`.
    - **A finding is established →** `../docs/RESULTS.md` (append-only).
    - **An approach is retired →** `../docs/DEAD_ENDS.md` (append-only).
    - **Any report/benchmark/diagnostic emitted →** `../docs/ARTIFACTS.md` (index + location).
    - **A source consulted →** `../docs/LITERATURE.md`.

11. **Citation-tag discipline (added 2026-06-10, Stage 7).**
    Tags: `[VERIFIED]` = full primary text read and logged in LITERATURE.md with stated provenance.
    `[SECONDARY]` = secondary/encyclopedic source, no single full-text read. `[INLINE]` = cited
    in a blueprint but not yet in LITERATURE.md. `[UNVERIFIED]` = Claude's prior knowledge only.
    **CC must NOT self-upgrade `[SECONDARY]` → `[VERIFIED]`** without a logged primary full-text
    read in the same session. For Stage 7 sources: Morin 2024 and J&H 2014 are `[VERIFIED]`
    (full text read, provenance stated in LITERATURE.md). The forest–savanna mosaic anchor is
    `[SECONDARY]` — do not promote. No other Stage 7 source is authorised for `[VERIFIED]`.

12. **Phase/stage disambiguation (added 2026-06-12, Phase boundary declaration).**
    Bare "Stage N" references in documents dated before the Phase-1 boundary (2026-06-12),
    or in `archive/`, are **Phase 0** (Social Mechanics, Stages 1–7.5, complete).
    New work is **Phase 1** (Terrain & Resource Ecology) and must carry the "Phase 1 Stage N"
    marker. Blueprints live in `blueprints/phase0/` (historical) and `blueprints/phase1/`
    (active). When in doubt, ask — do not assume.

13. **A failed gate is a STOP, not a judgment call (added 2026-06-02, R0 process flag).**
    When any blueprint gate fails — *even by a small margin* — STOP and surface it for the
    supervisor's call. Do NOT absorb a gate breach and proceed, and do NOT bundle a gating
    task and the run it gates into one job so the gate cannot block. Gate-first means the
    gate must be a *blocking checkpoint*: confirm PASS before launching the gated run. A small
    breach may well be acceptable, but that judgment belongs to the supervisor, not the coding
    agent. (Origin: in R0, the static equivalence gate's rel_std component was out of tolerance
    by ~2%; CC had bundled Task 1 and Task 2 into one background job and let the seasonal
    matrix proceed rather than stopping. The breach was benign and accepted, but the override
    was the supervisor's to make.)

14. **Drain the pending-delta buffer on every run (added 2026-06-14).** At the start of any
    blueprint/directive execution, read `context/PENDING_CC.md`. For each `[PENDING]` entry,
    reconcile it into its home-target: if it agrees with the home, mark `[DRAINED <date>]`;
    if it **conflicts** with a home, do NOT silently resolve — surface it to the supervisor
    (charter §1 conflict-surfacing) and leave it `[PENDING]` with a `[CONFLICT]` tag. Never
    promote a pending delta into canon without it agreeing with, or being adjudicated into,
    its home.

15. **Regenerate the fact-file and prompt re-upload (added 2026-06-14).** Whenever a run
    changes any fact projected in `context/CANONICAL_FACTS.md`, regenerate that file from the
    homes as part of the same change, then **STOP and prompt the supervisor to re-upload the
    regenerated `context/CANONICAL_FACTS.md` into the Claude.ai project knowledge.** The file
    is a cache; it must never be hand-edited to diverge from the homes.

16. **Check the spec docs BEFORE re-reading literature PDFs (added 2026-07-17).**
    Extracted lit values are already POOLED into the docs (charter "one fact, one home"): the exact
    extraction/scaling math in `../docs/MODEL_SPEC.md`; per-biome forage/game means+stds with their
    derivations in `../docs/SiC_Games_Resource_Return_Rate_Table.md`; constants in `../docs/PARAMETERS.md`;
    sources + what each was used for in `../docs/LITERATURE.md`. **Grep those FIRST** — the number is almost
    always already there with its arithmetic and citation; cite it, do not re-derive it or re-render the
    table image. Open a `literature/` PDF **only** for (1) a genuinely NEW statistic that isn't pooled
    (e.g. R-72's day-to-day/*temporal* return CV — the tables pool only *spatial* cross-cell variance), or
    (2) verifying a SUSPECTED error in a pooled value (e.g. R-79's Bird 2009 desert-game row). Say which,
    in the RESULTS/commit note, and pool the new value back into its home. When a source must be read,
    render image-only tables with `pymupdf` (`pymupdf.open(p)[i].get_pixmap(dpi=200)`) and read the image —
    `pypdf` text extraction silently transposes/drops table columns, which is how the R-79 error entered.
    *(Phase-1 note: the tooling here is `py -3`, not `python`; before believing any demographic claim run
    `outputs/phase1_biome_mortality/report_demography.py` — R-75. New Phase-1 mechanics land default-OFF /
    bit-exact and are adopted by flipping the flag in `run_se0_controlled_climate.py`'s preset with a
    `# CANONICAL <date>` note, not in the `DemographyConfig` default.)*

17. **Declare a mechanism's TYPE, UNIT and INVARIANT before building it (added 2026-07-18).**
    Binding contract: `docs/MECHANISM_CHARTER.md`. Every new mechanism's docstring must state (a) its **type**
    from `S F T P D X C A N H O`; (b) the **unit** it operates on (agent/pair/household/band/settlement/cell) —
    this line exists because R-82's redistribution operator was applied to a group of size 1-2 and read as
    "inert"; (c) the category **invariant** and how a test asserts it (X conserves its total; A changes the graph
    and NO quantity; T conserves count and every carried quantity; H acts only at births; O mutates nothing and
    must not consume the model RNG). If a mechanism needs two types it is two mechanisms — split it.
    **If a flag's ON/OFF output is indistinguishable, that is a specification bug, not a small effect size**
    (DE-19), unless it is declared *gauge fixing*, where invariance is the point (`enable_cred_renorm`).
    Prefer vectorized execution: T/P/D/X/C/H are elementwise, gather-by-index or segment-reduction and should not
    be written as per-agent Python loops; A and N are where loops remain legitimate.

18. **Validate the INSTRUMENT, not just the mechanism (added 2026-07-18).**
    Binding contract: `docs/MECHANISM_CHARTER.md` §10. Four findings in one day turned out to be artifacts of
    the measuring apparatus, not facts about the model. Before reporting any result ask: **if the effect I am
    claiming (or denying) were absent (or present), would this instrument have told me?**
    The two cheapest and highest-yield, both usually a few lines against synthetic data with no model run:
    **(D1) a POSITIVE CONTROL before any negative** — inject the effect, show the instrument finds it, report the
    detection floor; and **(D2) a NULL FLOOR before any positive** — report what the statistic gives on shuffled
    or noise data and compare to THAT, never to an invented threshold.
    Also: record the **baseline state** beside every verdict ("does nothing when toggled" ≠ "does nothing");
    confirm a swept parameter is actually **rate-limiting** before concluding from the sweep; **detrend** before
    any periodicity claim; **save the raw series** so re-analysis never needs a re-run; check the **magnitude**
    and the magnitudes downstream, not just the flag; and **measure** invariance rather than asserting it from
    reading the code.

19. **PLOT IT — show the supervisor the picture, not just the table (added 2026-07-18).**
    Any analysis that is inherently graphical — time series, sweeps, distributions, power/response curves,
    trends, before/after comparisons — must be rendered as a chart in the chat for visual verification, not
    reported only as numbers. Tables hide what eyes catch instantly: a trend the statistic was blind to, an
    outlier driving a mean, a threshold sitting in the wrong place. **Worked example:** R-87's cycle verdict was
    a table of three autocorrelation values and read as "no cycles"; plotted against its own measured noise
    floor, one value was visibly ABOVE the noise and below only an invented cut-off — obvious in the picture,
    invisible in the table.
    Pair it with §10: a plot of a result should show the **null floor** and, where relevant, the **detection
    floor** on the same axes, so the reader can see whether the signal clears them rather than taking a verdict
    on trust. Persist the raw series (D8) so a plot can be redrawn without re-running the model.

---

## Locked parameters — do not change without explicit instruction

> **Authoritative home: `docs/PARAMETERS.md`** (extracted 2026-06-08, charter §6).
> This table has been superseded. **Do NOT edit this section** — any parameter change goes
> into PARAMETERS.md, not here. The stale values that were here (p_fission_Si=0.28,
> τ_trickle=0.05, σ_inherit=0.05, age_init_upper_frac=0.25) have been corrected in
> PARAMETERS.md as part of D1–D3 discrepancy resolution.

For any parameter value, lock date, sweep history, or status: → **`docs/PARAMETERS.md`**
(organised by: §1 World · §2 Decision/σ · §3 Deffuant · §4 Joint task · §5 Cred ·
§6 Pool · §7 Reproduction · §8 Dormancy · §9 Initialization · §10 Diagnostics).

---

## Pre-registered hypotheses — do not modify or ignore

**H1(ii):** Si is more resilient than C under periodic resource shocks.
*Phase 0 Sugarscape result: INVERTED (robust, 5/5 seeds). C survives A=0.75; Si collapses.*
**⚠ NOT a standing confirmed result on Phase 1 substrate.** Pre-registered for re-test — see `HYPOTHESES.md §H1ii-RETEST` and `RESULTS.md R-1`. The prior confirmation is Sugarscape-era; Phase 1 terrain changes the resource-access dynamics. Do not cite as currently confirmed.

**H_cc:** C's trough recovery speed is faster than DTM formula alone predicts,
due to carry_discount counter-cyclical birth boost (N_C↓ → discount↑ → p_birth↑).
Registered: Stage 4.5 patch §7.3. Test spec: regress C trough recovery time
on N_min/N_carry across seeds; predict negative slope.
*Status: regression-supported at Stage 5, single-seed. Pending multi-seed at A=0.9.*

---

## Performance reference (post-optimisation, v5.1)

| Config | Grid | N | ms/step | LHS (300r, 4w) |
|---|---|---|---|---|
| B0 | 50×50 | 250 | 12.5 | 0.13h |
| B1 | 100×100 | 500 | 53.0 | 0.55h |
| B2 | 100×100 | 1000 | 58.1 | 0.61h |
| B3 | 150×150 | 1000 | 140.7 | 1.47h |
| B4 | 150×150 | 2000 | 117.9 | 1.23h |
| B5 | 200×200 | 1500 | 214.7 | 2.24h |

All B0–B5 are LHS-feasible. Target working grid for Stage 5.x: 100×100.

---

## What is out of scope until explicitly instructed

- c1/c2 behavioral hooks (c2 in Stage 5.2; c1 in Deffuant pass)
- Deffuant cultural updating (Stage 5.2)
- Terrain topography mechanic (Stage 5.x)
- Mixed C+Si populations (never — separate civilisations on matched worlds)
- Inter-pool connectivity (Stage 6+)
- HiveMind (Stage 7+)
- Biparental Si reproduction (Stage 7+)
- Any β, ρ, τ_pool sweep (Stage 5.1)
- Statistical power analysis (Stage 6)

---

## Session management

After completing each full stage or major task, state:

> "Task complete. Recommended: start a fresh Claude Code session for the
> next stage to avoid context compression."

Then provide a 3-bullet summary:
- What was just done (files changed, tests added, parameters locked)
- What the equivalence gate confirmed
- What comes next (next blueprint or task)


R1 — Terminal-state accounting (mandatory, in the MAIN result table)
For every run, the primary results table (not an "informational" or
"note only" table) must contain, per seed:
FieldDefinitionsurvived_to_t_endtrue / falseextinction_stepfirst step t where N_active == 0; — if neverextinction_phaseseasonal phase at extinction_step (peak / trough), and trough index if in a trough; — if survivedN_active_t_endpopulation at the final stepN_min / N_min_steppopulation nadir and the step it occurred
A run that ends in an absorbing state (extinction, population ceiling lock,
total dormancy) must report the step at which it happened and the
environmental conditions at that step. "Note only" is prohibited for any
absorbing-state event.
R2 — Gate-versus-finding separation
A passed gate is not a finding. Every gate result is followed by one
sentence stating what passing or failing means scientifically.
If a gate passes while an adverse terminal event occurs in the same run
(e.g. counter-cyclicality gate passes but the population goes extinct), the
report MUST reconcile the two in prose, in the same section. A green checkmark
may never stand alone next to an extinction or collapse. State plainly: "the
mechanic worked as designed AND the outcome was X."
R3 — Magnitude, not just direction
For any directional gate (X > Y), report the magnitude (ratio or delta)
and compare it to baseline so the reader can judge whether the effect is
meaningful or negligible. "σ_eff rose during troughs ✓" is incomplete; "σ_eff
rose by 0.04 above a baseline of 1.238 (≈3%)" is complete.
R4 — Self-audit / anomaly section (mandatory)
Every report contains an Anomalies & Open Questions section immediately
before the synthesis. It lists: unexpected values, results that complicate the
headline, missing items, internal inconsistencies, and any metric that the
author had to reconcile. The author flags these proactively. If there are none,
the section says "None identified" — it is never omitted.
R5 — Synthesis is the deliverable
Every report ends with a synthesis (≥150 words for routine stages, ≥250 for
H1(ii)-relevant stages) that states: the claim, evidence for, evidence against,
and a confidence level. "See table" is not an acceptable synthesis. The
synthesis must explicitly address any adverse terminal event from R1.
R6 — Required emitted tracking (code-level)
The simulation/diagnostics layer must emit, per run, so that R1 can be filled:

extinction_step — first t with N_active == 0, else null.
seasonal_phase(t) at the extinction step (reuse the existing
seasonal_phase metric from Stage 4.2: peak if sugar > 0.75×peak, trough if
sugar < 0.25×peak, else transition) and the trough index.
N_min and argmin_t N_active (nadir and its step).
t_end value of N_active.

These fields are emitted for all runs regardless of strategy or whether
extinction is expected, so the schema is uniform across stages.
R7 — Report self-check before writing the file
Before producing report.html, confirm internally:

Does every run have an R1 terminal-state row in the main table?
Is every gate followed by an R2 interpretation sentence?
Is any adverse terminal event reconciled with any passed gate (R2)?
Are directional gates accompanied by magnitudes (R3)?
Is the Anomalies section present (R4) and the synthesis present (R5)?

If any answer is "no", fix it before writing the file.