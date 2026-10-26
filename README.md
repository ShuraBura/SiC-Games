# SiC Games

An agent-based model (Python, Mesa) of **emergent social evolution**: forager bands on climate-generated terrain
worlds grow into villages, connubia and stratified centres, with an explicit demography (Siler mortality, energetic
fertility, families, provisioning), an economy in kcal, storage, and an elite / dynasty layer. Every mechanism is a
flag, and the canonical run is one configuration file. The model is calibrated against the ethnographic and
archaeological record through a scored marker table.

**Auditing or reviewing the project? Start at [`docs/AUDIT_GUIDE.md`](docs/AUDIT_GUIDE.md).**

The project began (June 2026) as a comparison of two strategies, C (cooperative) and Si (individualist), on a
Sugarscape world. That question (RESULTS R-1) is historical; the current work is the R-106 demographic and
settlement calibration arc. See `docs/AUDIT_GUIDE.md` §1 for the history in one page.

## Where things are

| You want… | Go to |
|---|---|
| **The auditor's entry point** — what to read, in which order, and how to run things | **[`docs/AUDIT_GUIDE.md`](docs/AUDIT_GUIDE.md)** |
| The routing table: which document owns which kind of fact | [`docs/INDEX.md`](docs/INDEX.md) |
| **What works, what meets its benchmarks, what does not** | **[`docs/MODEL_STATE.md`](docs/MODEL_STATE.md)** |
| The current scorecard of the model against the record | [`docs/MARKER_MATRIX.md`](docs/MARKER_MATRIX.md) (top section) |
| Every mechanism flag and parameter of the canonical run (generated) | [`docs/REGISTRY.md`](docs/REGISTRY.md) |
| Every finding, append-only, and its index (generated) | [`docs/RESULTS.md`](docs/RESULTS.md) · [`docs/RESULTS_INDEX.md`](docs/RESULTS_INDEX.md) |
| What a canonical run executes | [`config/runs/full_campaign.toml`](config/runs/full_campaign.toml) |
| The working rules (CTB, build-it-on, the visual rule, …) | [`CLAUDE.md`](CLAUDE.md) |
| The model code | [`sic_games/src/sic_games/`](sic_games/src/sic_games/) |
| Run harnesses (the canonical campaign is `sic_games/outputs/substrate_run/run_campaign.py`) | [`sic_games/outputs/`](sic_games/outputs/) |
| Tests | [`sic_games/tests/`](sic_games/tests/) |
| Supervisor directives (historical, by stage) · handoffs · the founding spec · superseded material | [`blueprints/`](blueprints/) · [`handoffs/`](handoffs/) · [`origin/`](origin/) · [`archive/`](archive/) |

## Run it (from the repo root; Windows uses `py -3`)

```bash
# the full test suite (~1,780 tests, 15–50 min). --capture=sys and stdin from NUL are REQUIRED on Windows:
# the config tests start subprocesses that fail with WinError 6 under pytest's default capture (RESULTS Add.111).
cmd /c "py -3 -m pytest sic_games\tests -q --capture=sys < NUL"

# one canonical campaign (the run file states everything; the [run] section's 2500 steps is a smoke length)
py -3 -u sic_games/outputs/substrate_run/run_campaign.py --config config/runs/full_campaign.toml

# the documentation audit, the registries and the scorecard
py -3 tools/doc_audit.py
py -3 tools/gen_registry.py --check
py -3 tools/scorecard.py --glob "campaign_trajectory_s2_*_riskvg_s*.json"
```

The full-length (15,000-step) three-world runs that the scorecard uses are made by `scratchpad/bp_stage2_driver.py`;
`docs/AUDIT_GUIDE.md` §5 gives the exact commands and the expected run times.

## Conventions (short version)

- **One fact, one home.** Every kind of fact has one authoritative document (`docs/INDEX.md`). Executable truth
  wins over prose: code > `config/runs/full_campaign.toml` > `config/*.toml` > `docs/`.
- **Append-only ledgers.** RESULTS, HYPOTHESES, DEAD_ENDS and TARGETS are never rewritten; a correction is a
  later dated entry.
- **Every mechanism is a flag, default OFF and bit-exact when off;** the canonical stack switches on every built
  mechanism unless a stated reason is recorded (`run_campaign.py` `_skip`).
- **Nothing is hard-deleted.** Retired material moves to `archive/`.

*Remote: github.com/ShuraBura/SiC-Games. README rewritten 2026-10-26 for the audit (the previous version described
the June 2026 C/Si project).*
