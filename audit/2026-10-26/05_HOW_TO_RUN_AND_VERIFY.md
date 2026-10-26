# 05 — How to run and verify (2026-10-26)

All commands run from the repository root. On Windows use `py -3` (the project rule). Python 3.14, Mesa; the
`literature/` PDF checks need `pymupdf` (`fitz`).

---

## 1. The test suite (15–50 min)

```
cmd /c "py -3 -m pytest sic_games\tests -q --capture=sys < NUL"
```
Expected at the snapshot: **1,776 passed, 1 xfailed.** The `--capture=sys` and `< NUL` are REQUIRED on Windows: five
configuration test files start subprocesses that fail INTERMITTENTLY with `OSError: [WinError 6]` in
`subprocess._make_inheritable` under pytest's default fd capture (RESULTS Add.111). If one of those files fails, read
the traceback first: WinError 6 is this artifact; any other error is real. Slow tests carry the `slow` marker.

## 2. One canonical campaign

```
py -3 -u sic_games/outputs/substrate_run/run_campaign.py --config config/runs/full_campaign.toml
```
The run file's `[run]` section sets 2,500 steps (a smoke length); the scored runs use 15,000. Output:
`sic_games/outputs/substrate_run/campaign_trajectory_<tag>.json` (git-ignored). Read the `!! SPATIAL:` banner and the
`demography:` banner the run prints (root `CLAUDE.md`).

## 3. Reproduce the runs behind the current scorecard (≈ 7.5 h at 8 processes)

Stage 2 of Add.113: 3 worlds × 3 paired demographic seeds, 15,000 steps, planet fixed (world/climate seed 0), a period
life-table snapshot at step 7,500. Both adopted flags are now in canon, so the canon arm alone reproduces them:
```
set S2_CONC=8
set S2_ONLY_ARM=canon:
py -3 -u scratchpad/bp_stage2_driver.py
py -3 tools/scorecard.py --glob "campaign_trajectory_s2_*_canon_s*.json" --out <scratch>/scorecard.json
py -3 tools/scorecard_fig.py <scratch>/scorecard.json docs/evidence/scorecard_add113_canon.json --png <scratch>/sc.png
```
Run times (8 concurrent): temperate ~5 h, montane ~4 h, savanna ~2 h per run. Progress: `scratchpad/stage2_progress.txt`.
The committed evidence was made from the `riskvg` arm (`C_ALLON` + the two flags then adopted). Today's canon switches
on the same flags through `C_ALLON`, so the runs are EXPECTED to be identical — not yet verified by a run. The canon
tag `_s2_<world>_canon_s<seed>` overwrites older files of that name.
**Cheap check (≈ 2 h):** one world and one seed (`S2_SEEDS=0` and edit `WORLDS` in the driver to savanna only), then
compare its trajectory row by row with `campaign_trajectory_s2_savanna_riskvg_s0.json` (on the supervisor's machine) or
its numbers with `docs/evidence/scorecard_add113_canon.json`.

## 4. The benchmark history and the maps

```
py -3 tools/benchmark_history.py --outdir <scratch>        # needs the five canon run sets on disk
py -3 tools/gen_code_map.py --out <scratch>/map.md
py -3 tools/gen_registry.py --check                        # REGISTRY.md and RESULTS_INDEX.md current?
py -3 tools/doc_audit.py                                    # docs vs code/config
py -3 tools/verify_anchor.py --list                         # literature anchors (needs the PDFs)
```

## 5. A verification checklist (suggested; each item names where its claim lives)

| # | check | expected | claim made in |
|---|---|---|---|
| 1 | the suite | all pass, 1 xfail | `01_CURRENT_STATE.md` §4 |
| 2 | `gen_registry.py --check`; `doc_audit.py --check params` | current; 0 disagreements | Add.114 |
| 3 | `verify_anchor.py --list` | 32/32 (with the PDFs) | LITERATURE.md, MARKER_MATRIX |
| 4 | a control re-run of one stored canon run | row-for-row identical | Add.108–113 |
| 5 | re-score the canon (§3) | the CURRENT SCORECARD values within SE | `02_BENCHMARKS.md` |
| 6 | the spatial banner on a canon run | `spatial_paradox` TRUE | `01_CURRENT_STATE.md` §3 |
| 7 | read one MODEL_SPEC formula and its code (e.g. §4.3.3 vs `_a2_mult`) | they agree (the risk term now does, via `enable_risk_accident_share`) | Add.112–113 |
| 8 | a "bit-exact when off" claim: a flag off vs a stored run | identical | every flag's docstring |
| 9 | one adoption decision: its Stage 2 numbers vs RESULTS | as recorded | RESULTS Add.108, 109, 113 |
| 10 | the benchmark history (§4) | the categories of `02_BENCHMARKS.md` | this package |
