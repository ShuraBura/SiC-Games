# SiC Games

An agent-based model (Mesa, Python) studying how two civilisational strategies —
**C** (cooperative) and **Si** (individualist) — fare under periodic resource
shocks on a Sugarscape-style world. Headline finding so far: the resilience
ordering *inverts* the naive prior (the cooperative strategy persists where the
individualist one collapses under deep seasonal troughs). See
[`docs/RESULTS.md`](docs/RESULTS.md).

## Where things are

| You want… | Go to |
|---|---|
| **To find anything** — the routing table for every kind of fact | **[`docs/INDEX.md`](docs/INDEX.md)** ← start here |
| The documentation homes (roadmap, mechanisms, results, hypotheses, …) | [`docs/`](docs/) |
| The rules that govern the docs | [`docs/DOCS_CHARTER.md`](docs/DOCS_CHARTER.md) |
| The model code | [`sic_games/`](sic_games/) |
| The agent contract for working on the code | [`sic_games/CLAUDE.md`](sic_games/CLAUDE.md) |
| Supervisor directives, by stage | [`blueprints/`](blueprints/) |
| Session & standing handoffs | [`handoffs/`](handoffs/) |
| The founding specification | [`origin/`](origin/) |
| Superseded docs, backups, prior code snapshots | [`archive/`](archive/) |

## Run it

```bash
cd sic_games
pytest tests/ -q                                # full suite (256 tests, must stay green)
python -m sic_games.run configs/<config>.yaml   # single run
python -m sic_games.batch configs/              # batch (CRN, parallel)
```

## Conventions (short version)

- **One fact, one home.** Every kind of fact has exactly one authoritative
  document (see `docs/INDEX.md`); everything else points to it, never copies it.
- **Append-only ledgers.** HYPOTHESES / RESULTS / DEAD_ENDS / TARGETS are never
  silently rewritten — supersede with a dated note.
- **Nothing is hard-deleted.** Retired material moves to `archive/`, not the bin.

*Repo reorganised 2026-06-05 per the DOCS_CHARTER. Remote: github.com/ShuraBura/SiC-Games.*
