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
[repo root]/
  src/sic_games/         — core simulation
    run.py               — main step loop
    world.py             — grid, sugar, growback
    metrics.py           — all logged metrics
    joint_task.py        — JT manager (spatial hash)
    batch.py             — BatchRunner (CRN, parallel)
    agents/
      base.py            — BaseAgent
      perception.py      — LocalVisionPerception
      reproduction.py    — biparental + fission
    strategies/
      carbon.py          — C decision
      silicon.py         — Si decision
      softmax_base.py    — shared softmax
  tests/                 — 285 tests (must stay green)
  configs/               — YAML configs for all runs
  outputs/               — HTML reports + parquets
  BUGS.md                — known-issues ledger
  CLAUDE.md              — this file (master agent contract)
```

**Documentation lives in `../docs/` (the charter's 11 homes), not here.**
INDEX, ROADMAP, ARCHITECTURE, MECHANISMS, TARGETS, HYPOTHESES, RESULTS,
ARTIFACTS, LITERATURE, DEAD_ENDS (+ DOCS_CHARTER) all live under `../docs/`
(reorg 2026-06-05; MODEL_SPEC split into ARCHITECTURE + MECHANISMS 2026-06-06).
PARAMETERS.md not yet extracted — interim param home is the locked-param table
below. Route via `../docs/INDEX.md`. Governance: `../docs/DOCS_CHARTER.md`.

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

3. **Run full test suite after every code change.** All 285 tests must pass
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

11. **A failed gate is a STOP, not a judgment call (added 2026-06-02, R0 process flag).**
    When any blueprint gate fails — *even by a small margin* — STOP and surface it for the
    supervisor's call. Do NOT absorb a gate breach and proceed, and do NOT bundle a gating
    task and the run it gates into one job so the gate cannot block. Gate-first means the
    gate must be a *blocking checkpoint*: confirm PASS before launching the gated run. A small
    breach may well be acceptable, but that judgment belongs to the supervisor, not the coding
    agent. (Origin: in R0, the static equivalence gate's rel_std component was out of tolerance
    by ~2%; CC had bundled Task 1 and Task 2 into one background job and let the seasonal
    matrix proceed rather than stopping. The breach was benign and accepted, but the override
    was the supervisor's to make.)

---

## Locked parameters — do not change without explicit instruction

| Parameter | Value | Locked at |
|---|---|---|
| k_grid | 4 | Stage 4.4 |
| β_Si | 5.0 | Stage 4.4 |
| p_fission_Si | 0.28 | Stage 4.3 |
| p_max_C | 0.12 | Stage 4.5 Task 1 |
| N_carry | 400 | Stage 4.5 Task 0 |
| α_carry | 1.0 | Stage 4.5 Task 0 |
| τ_pool | 0.05 | Stage 4.3 |
| ρ (pool carryover) | 0.3 | Stage 4.3 |
| λ (wealth inheritance) | 0.1 | Stage 4.5 Task 1 |
| σ_Si | 1.238 | Stage 3.4 |
| κ (Cred-σ coupling) | 2.0 | Stage 3.4 |
| α (Matthew partition) | 2.0 | Stage 3.4 |
| β (status amplification) | 1.0 | Stage 3 |
| f_C (newborn Cred endowment) | 0.25 | Stage 3 |
| σ_inherit (trait noise) | 0.05 | Stage 3 |
| age_init_upper_frac | 0.25 | Stage 4.4 patch |
| wealth_init_scale_k | True | Stage 4.4 patch |
| cluster_init (C only) | True, peak_index=0, radius=10 | Stage 4.4 patch |
| T_dormant_max | 50 | Stage 4.3 |
| k_dormant | 1.0 | Stage 4.3 |
| τ_trickle | 0.05 | Stage 4.3 |
| k_reactivate | 3.0 | Stage 4.3 |
| r_cred_Si | RETIRED (Stage 5.1) | replaced by binary near-dormancy trigger |
| k_cred_band | 1.0 | Stage 5.1 |
| κ_Si | 0.5 | Stage 5 |
| C*_Si | 10.0 | Stage 5 |
| c2_defection.enabled | True | Stage 5.2 |
| deffuant.epsilon | 0.2 | Stage 5.2 |
| deffuant.mu | 0.3 | Stage 5.2 |
| sigma_inherit | 0.10 | Stage 5.2 (raised from 0.05) |
| k_density (c_spatial_density period) | 10 | Perf opt pass |
| k_moran (Moran's I period) | 10 | Perf opt pass |

---

## Pre-registered hypotheses — do not modify or ignore

**H1(ii):** Si is more resilient than C under periodic resource shocks.
*Status: INVERTED (robust, 5/5 seeds). C survives A=0.75; Si collapses.*

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