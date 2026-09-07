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

### CTB THE QUANTITY, NOT ONLY THE ARITHMETIC

**Added 2026-08-08 after commit `4f02e1d`, the first defective instrument that got committed and wired into
every campaign before it was caught.** It shipped with **ten** CTB tests. Every one of them verified that the
ratio was *computed as specified*. Not one asked whether the ratio *meant* anything — it divided a cell capacity
(persons per cell) by a per-person harvest multiple, two quantities that cannot be divided.

So step 1 of CTB says *a world whose ANSWER you know*, and it means the answer, not the formula:

- **Name the unit of every input and of the output, out loud, before writing the test.** If two inputs are
  combined, they must be the same kind of quantity or the combination must be a documented conversion.
- **A test that re-derives the formula proves only that you can write the same formula twice.** Construct a case
  where the *answer* is known independently of the code under test.
- **Before believing a headline ratio, check whether the code already documents it.** `capacity.py`'s header
  stated the "~1–8 vs ~30–50 persons/cell" gap as its own design rationale. It was reported as a defect.

### A "NO EFFECT" RESULT NEEDS A POSITIVE CONTROL THROUGH THE SAME PATH

**Added the same day, after the second instrument failure on the same question.** A measurement claiming a
mechanism is inert must first show a perturbation that **does** move the run, through the identical code path.

The failure it prevents: `TerrainWorld.__init__` does `self._fields = generate_world(knobs)` — the model
**regenerates its own world** and ignores the `WorldFields` the caller built. Perturbing the caller's copy
changed nothing, every arm read "not load-bearing", and the answer was clean, plausible and empty.

- **Perturb, do not read.** Reading call sites tells you where a name APPEARS. Scaling a field ×1000 and
  re-running tells you whether the value MATTERS. Only the second is evidence.
- **Check the run is alive.** A collapsed population is insensitive to everything and makes every field look
  inert.
- **A flag that is ON and changes nothing is a bug until proven otherwise.** The ON-but-dead gate checks the
  CONFIG; a per-flag liveness test checks the RUN. Both are needed. The per-flag test is three lines, and it
  caught a half-wired mechanism the same day it was added (Addendum 37).

Pattern to copy: `sic_games/tests/test_field_load_bearing_ctb.py`, whose first test is the positive control and
whose docstring states that every other test in the file is void if that control ever passes trivially.

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
- **DEFAULT-OFF IS FOR REPRODUCIBILITY, NOT FOR DEFERRING A DECISION.** The dataclass default stays `False` so
  every historical run reproduces bit-exactly. The CANONICAL STACK is a separate question, and the standing
  rule there is the opposite: *every BUILT mechanism runs unless it is off for an ablation*. So a new mechanism
  belongs in `C_ALLON` unless there is a STATED reason it must not be — a genuine alternative to something else
  already on, or a known-broken candidate. **A correction to a defect is never flagged off**; the
  carrying-capacity ceiling bug (2026-08-14) was fixed directly with no flag, and flagging an equally clear
  correction beside it is simply inconsistent. Added 2026-08-15 after the supervisor challenge *"you build
  stuff, flag them off, then wonder why things don't work"* — four mechanisms built that week had been parked
  in the `C_ALLON` skip set for no stated reason, so every arm run that week silently tested the OLD behaviour.
  The audit that created `C_ALLON` found **27 of 79 flags dark and nobody knew**; adding to that pile is the
  failure it exists to prevent.
- **BUILD IT ON, AUDIT THAT IT IS ON, AND DISCUSS EVERY OFF.** Added 2026-08-28 by the supervisor, as the hard
  gate form of the rule above. Three obligations, binding on every mechanism from here:
  1. **Build it ON.** The moment a mechanism is built it goes into the canonical stack (out of the `C_ALLON`
     skip set) and is validated WHILE ON. We do not build dark and "adopt later"; the dataclass default stays
     `False` only for bit-exact reproducibility of historical runs, never as permission to leave it out of
     canonical.
  2. **Audit that it is on.** After building, read the canonical `C_ALLON` resolution back and confirm every
     mechanism built in the working session is live. A flag found OFF is a defect to explain, not a default to
     accept. `grep`ing the source is not enough — resolve the config and look.
  3. **Discuss every OFF.** If a flag must be OFF for any reason — a genuine alternative to something already
     on, a measured net-negative, a known-broken candidate — that is a DISCUSSION to raise with the supervisor,
     with the stated reason recorded in the `C_ALLON` skip set AND surfaced in chat. Never a silent park. A
     measured net-negative (e.g. `enable_village_pooling`, `enable_subsistence_floor`) is turned off only after
     the finding is shown and the supervisor agrees; a falsified mechanism is reverted, not parked.
- **A SCALAR CANNOT SHOW A STRUCTURE. LOOK AT IT, THEN MEASURE IT.** Adopted 2026-08-16 by the supervisor:
  *"another showcase of how ur math and tables only show a part of the story, often misinterpreted, and the
  paramount importance of visual aids."* Earned three times in one day, and the discipline runs BOTH ways.
  - **The picture generates what a scalar cannot.** `cells_occupied = 213` was logged in every row for a
    week. It says how many cells, never that they form chains through mediocre land while 65% of the richest
    land sits empty. One map said it at a glance.
  - **The number then corrects the picture.** From that same map I claimed "agents avoid the best land". The
    arithmetic said otherwise — they weakly PREFER it (occupied cells +17% forage, r = +0.12); the true
    statement is that 65% of the top decile is unoccupied. A picture invites overstatement exactly as a
    table invites blindness.
  - **A summary statistic of a skewed distribution is a lie of omission.** `settle_med = 11` with
    `settle_max = 86` is not "typical village 11". Reporting the median alone produced "a sprawl of 184 tiny
    hamlets", which was wrong — the real structure was one clustered population counted ~20x by overlapping
    windows.

  **A VISUAL IS MANDATORY, not optional, for:**
  | claim about | required | never sufficient |
  |---|---|---|
  | WHERE — arrangement, settlement, dispersal, territory | a MAP | `cells_occupied`, `n_settle` |
  | a DISTRIBUTION — band/village size, wealth, age | the HISTOGRAM | median, or median+max |
  | EQUILIBRIUM or dynamics | the TRAJECTORY | a last-N-step mean (it hid a peak of 6084 falling to 2317) |
  | whether a mechanism FIRED | raw signal + threshold on the SAME axes | a fired/not-fired verdict |

  **What the figure must carry:** the anchor or band drawn ON the axes, not quoted in the caption; the RAW
  data, not only a fit or a smoothed line; the DENOMINATOR — empty land drawn as empty rather than cropped
  away; and the control arm in the same figure wherever one exists.

  **Then SEND it.** A PNG left on disk is not a report. `sic_games/outputs/substrate_run/plot_spatial.py` is
  the worked example: terrain, people and settlements side by side, one row per arm.

- **CHECK THE POPULATION AGAINST THE MAP, BEFORE ANYTHING ELSE.** Adopted 2026-08-16 by the supervisor, whose
  verdict was: *"Copious amount of time and tokens was wasted not doing just that."* Before diagnosing any
  vital rate, multiply `pop` by the map and see whether the number is even possible. The R-106 arc spent a
  week on mortality and then fertility while the population used **14% of its land**, sat **4.8× BELOW**
  Binford packing regionally and **1.4× ABOVE** it locally, and ate **2.7× requirement**. Every input was in
  every row already. Nothing compared them.
  - The table and the two checks live in `docs/MARKER_MATRIX.md` §"The spatial sanity check". They are WIRED,
    not merely written: `demography.spatial_health()` runs in every campaign snapshot and prints a
    `!! SPATIAL:` banner. Do not report a run without reading that banner.
  - **THE PACKING PARADOX.** A population cannot be PACKED (local density > Binford 0.091/km²) and SPARSE
    (regional < 0.091/km²) at the same time. If it is, it is **not food-limited — it is failing to disperse**,
    and every carrying-capacity conclusion drawn from that run is void. Note that this introduces NO new
    number: it uses one filed anchor twice, once per side.
  - **THE BAND CATCHMENT.** A band must command at least its own foraging radius — 314 km², Vita-Finzi &
    Higgs' 10 km site catchment. Below that, band territories would overlap completely.
  - The habitable area is the **capacity patch's** land (`habitable_cells × 100 km²`, R-103i circumscription),
    NOT the 100×100 grid. The population cannot disperse outside the patch.
  - Only Binford's 0.091 is a filed anchor, and it is a **CEILING**, not a target. The other densities in the
    table are a labelled reference bracket and must never be cited as filed bands (binding rule 2 of
    `MARKER_MATRIX.md`).

- **EVERY REPORT CARRIES THE DEMOGRAPHY PANEL.** Adopted 2026-08-15 by the supervisor. Any report of a run,
  an arm, a comparison or a finding must present the demographic benchmarks alongside whatever it is actually
  about — not a summary verdict, the numbers, each against its filed band:
  **age structure** (`frac_child`, `dependency_ratio` split into child and old-age, the seven age bands),
  **sex** (`sex_ratio_m_f`, `srb_male_frac`, sex-specific `e0`/`e15`),
  **mortality** (`e15` as the headline — NOT `e0`, which cannot separate a forager from an 18th-century Swede
  — plus `surv_to_15`, `surv_to_45`, `modal_adult_death`, and mortality by age band),
  **fertility** (`realised_tfr` against completed cohort parity, `realised_ibi_med`, `age_first_birth_yr`),
  **families** (`frac_both_parents_alive`, `frac_double_orphan`, `frac_never_partnered_30`,
  `frac_widowed_adult`, `frac_partnered_adult`),
  **group size** (`band_med_adults` — Hill's 28.2 anchor is ADULTS, never all-ages),
  and the **iso-growth consistency check** (does the arm's own TFR and l(15) permit its measured r?).
  `demography_health()` computes all of it and returns a verdict line; there is no excuse for a report that
  omits it. WHY: social dynamics are built on the age-sex structure, so a marker read on a skewed population
  is not a result. `band_med` 23 read as a PASS against Birdsell's ~25 on a population that was 54% children
  — about 11 adults against an anchor of 28.2 — and `MARKER_MATRIX.md` had already recorded that failure
  before it recurred.
- A calibrated value has ONE home. Docs cite the config field by name; they do not restate the number
  (charter §11 P1).
- Long runs must be launched from a **clean tree** — `meta.tree_dirty` gates every harness, and an edit
  mid-run invalidates the arms launched after it.
- MARKER_MATRIX binding rule 3: a marker claim needs seeds that beat the variance (R-65 measured 30× seed
  variance).
