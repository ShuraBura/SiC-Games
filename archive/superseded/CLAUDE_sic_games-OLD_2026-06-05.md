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
  tests/                 — 201 tests (must stay green)
  configs/               — YAML configs for all runs
  outputs/               — HTML reports + parquets
  ROADMAP.md             — stage status + locked params
  LITERATURE.md          — literature search log
  VERSION_NOTES.md       — snapshot at v5.1-postaudit-clean
```

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

3. **Run full test suite after every code change.** All 201 tests must pass
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

10. **Update ROADMAP.md at the end of every stage.** Mark stage complete,
    add locked parameter values, note deferred items.

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
| r_cred_Si | 0.1 | Stage 5 |
| κ_Si | 0.5 | Stage 5 |
| C*_Si | 10.0 | Stage 5 |
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
