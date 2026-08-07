# SiC Games — working instructions

## THE FIRST RULE: **CTB — CONSTRUCTED-TRUTH BENCHMARK**

> **Build a world whose answer you already know. Measure it with the real diagnostic. Verify the measurement
> returns what you built.**

**Named 2026-08-06 at supervisor request** ("we need an acronym for this procedure, I am tired of typing it").
CTB is the name for the rule below — use it in commit messages, RESULTS entries, test docstrings and chat.
*"CTB'd the village diagnostic"* means all three steps were done. It is a verb.

Three rules travel with it:
- **Measure with the REAL diagnostic**, never a reimplementation of it in the test. A test that reimplements
  the thing it checks proves only that you can write the same bug twice.
- **Construct the NEGATIVE too.** A benchmark with only positive cases cannot tell a working instrument from
  one that always says yes. Build the case that must read "nothing here" and check that it does.
- **A verdict about the CONFIG is read from the config, not from the observation.** "You never switched it on"
  and "you switched it on and it never fired" are different findings and must never collapse into one.

Reference implementation: `sic_games/tests/test_climate_health_ctb.py`, which constructs all four health
verdicts explicitly. On the day it was written it caught **three defects in the instrument it was benchmarking**
and none in the model (RESULTS Addendum 31).


### The rule in full

**Adopted 2026-08-04 by the supervisor, after a single day in which interpretations of the same measurement
were revised three times — each revision caused by the INSTRUMENT, never by the model.**

Before a diagnostic is used to say anything about the model:

1. **Build a world whose answer you already know.** Place the agents, the villages, the ages, the pairings by
   hand — a constructed distribution, not a simulated one.
2. **Run the diagnostic on it.**
3. **Check the diagnostic returns what you constructed.** If it does not, the diagnostic is wrong, and every
   number it has ever produced is suspect.

Only then is that diagnostic allowed to be used on a real run. **This applies to everything** — terrain,
villages, band size, age structure, mating pools, wealth, lineages. Need to measure villages? Build a map with
a known settlement distribution, measure it, confirm the measurement matches the construction.

### Why this rule exists — the day it was adopted

| what was claimed | how many times it was revised | what the instrument was actually doing |
|---|---|---|
| `connubium_med` overshoots its anchor | 3 | the statistic is TWO different quantities appended to one list — Cut-1 appends a pool-of-adults count, Cut-2 appends total population within the search radius. The class comment declares only the first. |
| four mechanisms are "structurally inert" | 1 | they read LIVE under ablation; the clamp binds only on bands that have a leader |
| the clamp-swallowing failure is widespread | 1 | a whole-run average buried it; the clamp binds ~0% during the founding transient and ~100% at equilibrium |
| four climate channels are inert | 1 | three were my test setup — wrong world, wrong horizon, unplumbed masks |

Each revision was reasoned carefully from the evidence available. That is the point: **careful reasoning about
an unvalidated instrument produces confident, wrong answers, repeatedly.** A synthetic fixture would have
settled every one of them in minutes, before any interpretation was written down.

### What a constructed-truth fixture looks like

- **not** "run the model and see if the number looks plausible"
- **not** "the docstring says it counts X"  ← this failed; the docstring described one of two code paths
- **yes** "place 40 agents in one cell and 10 in another, with 6 paired females and 4 unpaired adult males;
  assert the diagnostic reports exactly that"

Assert the CONSTRUCTION, element by element. If the diagnostic aggregates, construct a case where the
aggregate is computable by hand.

### The corollary

A diagnostic without a constructed-truth test is not evidence. If a result rests on one, say so in the same
breath, and build the fixture before the result is written into `docs/RESULTS.md`.

---

## Process rules that already bind

- `docs/RESULTS.md` is **APPEND-ONLY**. Corrections are new addenda, never edits.
- `docs/MECHANISM_CHARTER.md` §3 (mechanism type declaration), §10 (the diagnostic discipline, D1–D16) and
  §11 (the propagation discipline, P1–P5) are binding. Read them before adding a mechanism or a measurement.
- Use `py -3`, never `python`.
- Run pytest from the **repo root**, never from `sic_games/` — `audit_flag_invariants` has a path assumption
  that breaks collection otherwise.
- Every mechanism is a **flag, default OFF, bit-exact when off**, with its magnitude beside it. A boolean flip
  without its magnitude is not enabling a mechanism (R-85c).
- A calibrated value has ONE home. Docs cite the config field by name; they do not restate the number
  (charter §11 P1).
- Long runs must be launched from a **clean tree** — `meta.tree_dirty` gates every harness, and an edit
  mid-run invalidates the arms launched after it.
- MARKER_MATRIX binding rule 3: a marker claim needs seeds that beat the variance (R-65 measured 30× seed
  variance).
