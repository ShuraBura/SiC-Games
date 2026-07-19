# MECHANISM CHARTER — the operator discipline

**Status:** ADOPTED 2026-07-18 (supervisor). Binding on **every mechanism added from this point**, and the
retrofit classification of the existing 60 is recorded in §4.

This is to mechanisms what `DOCS_CHARTER.md` is to documents: a contract, not a description. Its companion is
`ARCHITECTURE.md` §0 (how to read the model); this document says **what a mechanism is allowed to be**.

---

## 1. Why this exists

The project is positioned as physics benchmarked by anthropology. Audited honestly (2026-07-18), that was only
half true:

- **The terrain layer genuinely is field physics.** NPP, wateracc, cultivability, soil and climate are scalar
  fields on a lattice; IFD movement is gradient response; harvest is local field sampling.
- **A few social pieces are genuinely operator-shaped.** The cred-weighted draw `cred^κ/Σcred^κ` is a projection.
  Deffuant updating is a contraction. The cred homeostat is a contraction with spectral radius < 1 — and that is
  not decorative: R-81's bug was exactly *"the co-moving population mean is not a contraction."*
- **Everything else was procedural accretion.** Three unrelated status scalars with ad-hoc couplings, no shared
  basis, 60 flags with no type, an operation order that is historical rather than principled, and nothing
  declaring what it conserves.

Two of this month's bugs were *type errors wearing domain clothes*:

- **DE-18 / R-82** — a redistribution operator applied to a group of size 1–2. Read as "the mechanism is inert."
  It was the **unit**, not the mechanism.
- **DE-19 / R-84** — an affiliation operator whose ON/OFF output was bit-identical. It **passed while doing
  nothing**.

A typed system catches both mechanically, because **every category carries an invariant, and an invariant is a
test**.

## 2. What "operator" means here — and what it does not

**It means: a declared transformation with a declared invariant.** It does **not** mean a linear map.

Do not attempt to force the model into linear-operator/eigenvalue formalism globally. Birth and death change the
dimension of the state space; mate choice is combinatorial; fission triggers are hysteretic switches. No global
linear operator exists for that, and asserting one would be numerology. The spectral language is legitimate
**locally**, about a linearization around an equilibrium (§5), and nowhere else.

## 3. The type system

**State** (what operators act on):

| Type | Meaning | Examples |
|---|---|---|
| **S — Substrate** | Scalar fields on the lattice; the gradients everything else responds to | NPP, wateracc, cultivability, soil, capacity |
| **F — Forcing** | Exogenous, time-varying drivers | climate, season, ENSO, volcanic, `enable_tier2_shock` |

**Operators** (the eight kinds of thing a mechanism may be):

| Type | Does | **Invariant (= the test)** | Vectorization |
|---|---|---|---|
| **T — Transport** | moves agents in space | agent count AND every per-agent quantity unchanged | **full** — elementwise on position arrays |
| **P — Production** | field → agent quantity (source) | Σ extracted ≤ field availability; field debited by exactly that | **full** — gather by index |
| **D — Dissipation** | destroys quantity (sink) | every affected quantity non-increasing | **trivial** — elementwise multiply |
| **X — Exchange** | moves quantity *between agents* | **Σ quantity conserved** (to float tolerance) | **full** — segment-sum (`np.add.at`/`bincount`) |
| **C — Conversion** | capital type → capital type (**the operator-matrix off-diagonals**) | must declare **debited** or **catalytic** | **full** — grouped normalize |
| **A — Affiliation** | changes the graph (who is bonded/grouped/owns) | **no quantity may change**; and it MUST demonstrably change the graph | partial — graph ops |
| **N — Demographic** | changes the agent set | dimension-changing; must declare what a birth inherits and a death releases | hard — batch by mask |
| **H — Inheritance** | copies state across an N event | acts **only** at birth events; a declared parent→child map | **full** — gather from parent index |
| **R — Regulator** | holds a state variable at a setpoint | preserves *relative* values; is a gauge **only if** nothing downstream reads an absolute scale (must be MEASURED, not asserted) | **full** — normalize |

**Read-only:**

| Type | Rule |
|---|---|
| **O — Observer** | zero mutation, **and must not consume the model RNG** |

O is not aspirational — it is already enforced in code by `_diag_rng` (a dedicated diagnostic RNG so read-outs
never perturb `self.random`). That the taxonomy has an existing, independently-arrived-at member is evidence it
describes the model rather than being imposed on it.

### 3.1 The declaration requirement (binding)

Every new mechanism must, **in its docstring**, state:

1. **Type** — one of `S F T P D X C A N H R O`. If it needs two, it is **two mechanisms**; split it.
2. **Unit** — the entity it operates on: agent · pair · household · **band** · settlement · cell · region.
   *This line exists because of R-82.* A social operator on a unit of size 1–2 is inert by construction.
3. **Invariant** — the category's invariant, plus how it is asserted in tests.
4. **Anchor** — `[VERIFIED source]`, `[DESIGN]`, or `[PROVISIONAL]`. Unchanged from existing practice.

### 3.2 Composite mechanisms

Some mechanisms genuinely span types — village budding is **A** (fission of the settlement graph) **+ T**
(relocation of the daughter). Split them into typed sub-steps rather than declaring a hybrid, so each piece keeps
a checkable invariant. `_maintain_leader_office` is the worked example: **A** (office succession, changes no
quantity) + **T** (desertion, moves an agent between bands, conserves everything he carries).

## 4. Retrofit classification of the existing 60 flags

Recorded 2026-07-18. Where a flag is composite the **primary** type is given first.

- **T Transport** — `enable_productivity_mobility`, `enable_terrain_move_cost`, `enable_emergent_abandonment`,
  `enable_site_appraisal`, `enable_landscape_packing`
- **P Production** — `enable_game`, `enable_agriculture`, `enable_agglomeration`, `enable_forage_cap`,
  `enable_catchment_ceiling`, `enable_resource_storability`, `enable_improved_land`, `enable_alluvial_renewal`
  (a *source*, not a sink — it renews soil)
- **D Dissipation** — `enable_soil_depletion`; `material_decay`, metabolic burn, storage spoilage (not flags)
- **X Exchange** — `enable_storage`, `enable_store_anchor`, `enable_provisioning`, `enable_leveling`,
  `enable_leader_share`
- **C Conversion** — `enable_cred_status` (cred → food share, exponent κ), `enable_prowess_facet`,
  `enable_ascribed_mate_choice` (status → mating), `enable_material_capture` (production → durable capital),
  `enable_standing`
- **R Regulator** — `enable_cred_renorm` (**re-typed from "gauge fixing" by measurement — R-85**; it moves
  every observable, because the inheritance homeostat's fixed 1.0 anchor makes cred rescaling non-scale-invariant)
- **A Affiliation** — `enable_pair_bonds`, `enable_bonded_mating`, `enable_marriage_aggregation`,
  `enable_exogamy`, `enable_adaptive_connubium`, `enable_band_affiliation`, `enable_dynamic_bands`,
  `enable_emergent_band_size`, `enable_size_repulsion`, `enable_malnutrition_fission`,
  `enable_resource_directed_fusion`, `enable_aggregation_sedentism`, `enable_settlement_scalar_stress`,
  `enable_village_scaling`, `enable_village_budding` (+T), `enable_morph`, `enable_economic_defensibility`
  (ownership = the topology of claims), `enable_leader_office` (+T), `enable_leader_coherence`,
  `enable_band_family_knobs`
- **N Demographic** — `enable_orphan_mortality`, `enable_energetic_fertility`, `enable_sedentism_fertility`,
  `enable_life_history`, `enable_condition`, `enable_nutrition_synergy`, `enable_terrain_risk`,
  `enable_density_disease`, `enable_terrain_pathogen`, `enable_band_risk` (shelved, DE-4),
  `enable_infanticide` (**UNIMPLEMENTED STUB — no logic reads it; a trap, see §6**)
- **H Inheritance** — `enable_genome`, `enable_paternity`
- **F Forcing** — `enable_tier2_shock`
- **O Observer** — `enable_genealogy_log`

**Two classification findings worth keeping:**

1. **`enable_cred_renorm` — I classified this as gauge fixing and the audit REFUTED it (R-85).** The reasoning
   was that it rescales cred to population-mean 1 while every downstream use is *relative* (`cred^κ/Σ`,
   normalised mate weights), so it should change no observable. Measured: it moves population, deaths, wealth,
   material, band structure — everything. **Why the reasoning failed:** the cred INHERITANCE homeostat reverts
   toward a **fixed 1.0 anchor**, so rescaling cred changes each agent's *distance to that anchor* and therefore
   its children's cred. Not scale-invariant. This is not a bug — restoring the anchor's meaning was precisely
   R-81's purpose — but it is **not a gauge**, and calling it one was wrong.
   **Re-typed as a new category, R — Regulator/Homeostat:** holds a state variable at a setpoint; changes
   absolute values while preserving relative ones. The model has several (cred homeostat, band tolerable-size,
   assabiyah).
   **The rule that survives, sharpened:** *a regulator is a gauge ONLY IF nothing downstream references an
   absolute scale — and that is an empirical question, not a design intention.* Run the differential audit to
   decide it. Do not assert gauge-invariance from reading the code, which is exactly the error made here.
2. **Affiliation is over-represented — 20 of 60 flags.** The model's social layer is overwhelmingly *topology*.
   That is the honest shape of the thing we built, and it says where the remaining compute cost lives (§7).

## 5. Dynamics: what kind of feedback produces what behaviour

Not a mechanism — a **design criterion**, applied when choosing one. This is the one place spectral language is
legitimate, and it is about a linearization around equilibrium, not the model as a whole.

| Feedback structure | Linearized signature | Behaviour | Where we have seen it |
|---|---|---|---|
| Instantaneous negative | real eigenvalue < 0 | **stable node** — exponential return | R-68 kill-half → recovery in 250 steps; Boehm leveling caps inequality *within the same step* |
| **Delayed** negative | complex pair, Re > 0 | **oscillation** | **not present anywhere in the model** |
| Positive | real eigenvalue > 0 | runaway / fixation | R-66 winner-take-all patriline fixation |

**This unifies three separate negatives into one statement.** DE-14 records connubium (R-67), substrate (R-68)
and soil (R-71) as three independent failures to produce secular cycles. In these terms they are *one* failure:
**every feedback in the model is instantaneous**, so the linearization has no complex pair, so it cannot
oscillate — it can only return to equilibrium or run away.

**The design criterion that follows:** a mechanism intended to produce cycles must introduce a **lag between a
quantity and the correction that removes it**, of order the system's relaxation time (~250 steps, measured in
R-68). Elite recruitment responding to elite wealth with a generational (~20 yr) delay is the canonical
structure. Registered as **H-CYCLES** in `HYPOTHESES.md`.

**Deliberately NOT adopted:** rebuilding as a mean-field/Fokker–Planck field theory. It would make the spectrum
analytically available but would destroy the individual-level results that are the project's actual output — RS
skew, dynasties, kinship, orphan mortality. Mean-field linearization stays available as an *analysis* tool for
H-CYCLES specifically, never as the model.

## 6. What the invariants would have caught (and must catch next time)

| Failure | Category | Invariant that catches it |
|---|---|---|
| R-82 aggrandizer capture inert (DE-18) | X on the wrong unit | the **Unit** declaration — X on a unit of size 1–2 is inert by construction |
| R-84 `succession_dissolve` vacuous (DE-19) | A that changed no graph | A **must demonstrably change the graph** |
| R-74 vacuous test (`1.0 == 1.0`) | N with an untested invariant | N must declare what a death releases |
| `enable_infanticide` stub | N with no implementation | **every declared flag must have a live reader** |

**Standing check, from DE-19:** if a flag's ON/OFF output is indistinguishable, that is a **specification bug**,
not a small effect size — unless it is declared gauge fixing (§4), where invariance is the point.

### 6.1 The audit that follows from this charter (R-85, 2026-07-18)

`outputs/phase1_biome_mortality/audit_flag_invariants.py` + `audit_verdicts.py` implement the black-box half:
flip each flag against an ENRICHED baseline (prerequisite chains satisfied — a bare preset makes
material-dependent flags read as falsely vacuous, the R-82 trap), diff the signature, re-test every no-change
flag at a second seed, then classify. Findings on first run:

- **A CRASH in freshly-committed code.** `enable_leader_office` + `enable_band_affiliation=False` raised
  `AttributeError: _next_band_id`. The office deliberately runs OUTSIDE the affiliation guard, but its desertion
  branch allocated from a band-id counter created only INSIDE that guard. **Every R-84 test set affiliation
  True**, so ten passing tests missed it; the audit hit it on the 7th flag.
- **`enable_cred_renorm` is not a gauge** (above).
- **~~A new defect class: FLAG ON, MAGNITUDE ZERO~~ — RETRACTED (R-85c).** The seven flags reported here as
  "enabled in the preset with a dead gain" are **not enabled in that preset at all**, and run at live values in
  `emergent_village_demog()`. The harness had flipped them ON while their gain stayed at the zero DEFAULT. The
  claim that this invalidated the 2026-07-15 config audit is **also withdrawn**. See RESULTS R-85c.
  **What is true, and still worth a standing check:** a boolean flip is not enabling a mechanism — most flags
  pair with a gain that defaults to 0, so `enable_X=True` alone leaves X inert. That is a trap for whoever
  enables a flag (it caught this harness), not evidence that a preset is misconfigured.
- **Confirmed independently:** `enable_infanticide` has no reader (the known stub), and `enable_genealogy_log`
  [O] mutates nothing (the observer invariant HOLDS).

**New standing check (restated after R-85c):** a flag audit must inspect the flag AND its magnitude, **and must
record the BASELINE STATE of the flag beside every verdict** — "does nothing when I turn it on" and "does
nothing" are different claims, and conflating them is what produced the retracted finding. Scope a config audit
to the preset FUNCTION, not the file: `run_se0_controlled_climate.py` contains two presets, and grepping the
file attributes the union to both.

**~~And the magnitude can sit one level deeper than the flag (R-85b)~~ — RETRACTED with the above (R-85c):**
`move_cost_kcal` and `site_gain` are 0 only because the forager preset does not enable those mechanisms; both
are live in `emergent_village_demog()` (750.0 and 0.3). **The diagnostic technique nonetheless stands and is
worth keeping:** *a derived field whose standard deviation is exactly 0 while its input's is not* (terrain `cost`
std 0.188 -> move-cost field std 0.000) is a reliable tell that a builder is multiplying a varying input by
zero — it correctly located the zero, and only the INTERPRETATION of why it was zero was wrong.

### 6.2 What a black-box differential audit CANNOT decide

Learned on the first run, recorded so it is not re-attempted: **conservation invariants (X conserves its total,
A moves no quantity) are NOT testable this way.** Over a long coupled run, changing the band graph changes who
forages together, which changes wealth — so an A-typed flag legitimately moves conserved quantities *in the
trajectory* while the operator still conserves them *within its own step*. Conservation must be instrumented
**around the call** (snapshot before/after the specific method), not inferred from trajectories. The black-box
audit soundly decides only: **vacuity, observer violations, crashes, and magnitude-zero gating.**

## 7. Compute: the type tells you the vectorization strategy

Supervisor directive (2026-07-18): *vectorization, not looping, where possible.* The categories map directly onto
how each mechanism should be executed — which is why typing is a prerequisite for the performance work, not a
detour from it.

- **Vectorizable now (T, P, D, X, C, H — 6 of 8):** all are elementwise, gather-by-index, or segment-reduction
  operations. X in particular is `np.add.at` / `bincount` over a group-id array — the current Python loop over
  bands is the textbook case for replacement.
- **Hard (A, N — 2 of 8):** A is graph mutation, N changes dimension. These are where per-agent loops are
  *legitimate*, and where `soa.py` (structure-of-arrays) would pay off via masked batch operations rather than
  vectorized arithmetic.

Since **A is 20 of 60 flags**, the honest expectation is that vectorizing T/P/D/X/C buys real time on the
economy, while the social layer stays loop-bound until the affiliation representation itself changes (agent
objects → id arrays + adjacency). Do not promise a blanket speedup; promise it per category.

## 8. Applying this to new work

For every proposed mechanism, before writing code:

1. **Name its type.** If you cannot, the mechanism is not yet understood well enough to build.
2. **Name its unit.** (R-82.)
3. **Write the invariant assertion first**, as a test. It is cheap and it is the thing that catches the two bug
   classes above.
4. **State the anchor** — `[VERIFIED]` / `[DESIGN]` / `[PROVISIONAL]`.
5. **Default-OFF, bit-exact** when off. Unchanged from existing practice.

**Agent specializations** (warriors, shamans, managers) are the dual of this system: a mechanism is an operator;
a specialization is **which operators an agent is coupled to**. `aggrandizer` is already a de-facto agent type,
and `prowess` generalising from scalar to a per-activity vector is the natural basis. Build only after the typing
retrofit, so specialised couplings inherit the invariants rather than re-introducing the R-82 unit error in new
clothes.
## 9. What a STRATIFICATION mechanism has to be (Flannery & Marcus 2012, added 2026-07-18)

A design constraint, at the same level as §5's feedback criterion, and it bears directly on the elite layer.

**9.1 Material accumulation alone does NOT produce hereditary rank.** Flannery's warning is blunt: *"if feasting
were all it took to produce hereditary inequality, there would have been no achievement-based societies left for
anthropologists to study."* Competitive feasting *"produced individual Big Men who had no way of bequeathing
renown to their offspring."*

**This reframes our own results rather than contradicting them.** The elite layer stratifies on material
(R-82/R-83), and we measured exactly what Flannery describes: leaders 3.68× ahead, yet father-was-a-leader only
53–69% and no hereditary transmission (R-84). **The model is behaving CORRECTLY as an achievement-based
society.** T-5's failing agricultural arm (0.435 vs 0.48) is therefore probably NOT a calibration shortfall —
it is a missing mechanism, and adding material heritability alone would be forcing the number rather than
supplying the cause.

**9.2 The missing operator is LEGITIMACY, and it is a C (Conversion), not an X (Exchange).** Friedman's
endogenous scenario: success is reinterpreted, not accumulated — *"The key shift in social logic was ... from
'They must have pleased the nats' to 'They must be descended from higher nats than we are.'"* Once a lineage is
descended from the ruling spirits it controls the land and is entitled to tribute. **This converts ACHIEVED
status into ASCRIBED rank — an off-diagonal in the capital matrix, from prowess/material into cred — gated on a
legitimating belief.** The `GroupVector.religion` cell exists and is a **stub**; it is the natural carrier, and
this is the first concrete reason to build it.

**9.3 The status vector should be three-way, not two.** Goldman's Polynesian triad is an independent
decomposition that matches ours and then splits one axis: **mana** (ascribed, born-with = `cred`), **tohunga**
(expertise: administrative/ritual/craft, raised by training), **toa** (martial prowess). Our single `prowess`
conflates the last two, and they have different social functions — expertise attaches to a role, while toa is
*the channel by which low birth is overridden* (*"a warrior of humble birth could rise ... even by chiefly
individuals"*). **A warrior facet is the social-mobility mechanism, not decoration.** Weights differ by society
(Tonga/Hawaii, the most unequal, use "the entire playbook"), which is the same society-dependent weighting BHM's
α supplies quantitatively.

**9.4 Power-balance devices are structural, and cheap to model.** Tonga: a **sacred/secular office split** makes
assassination harder but creates usurpation risk, controlled by *limiting the land allocated to the secular
chief*. Tikopia: *"The simultaneous presence of four chiefs acted as a system of checks and balances, preventing
one ambitious leader from taking over."* Both are A-type (Affiliation) constraints on the office graph, and both
suggest that **the number and separation of offices is a governing parameter** — something the model currently
fixes at one leader per band.

## 10. THE DIAGNOSTIC DISCIPLINE — rules for the instrument, not the mechanism

**Adopted 2026-07-18 after four findings in one day turned out to be artifacts of the measuring apparatus rather
than facts about the model.** §3 governs what a MECHANISM must declare. This section governs what a MEASUREMENT
must declare, and it exists because the failures were not careless — each passed review, and each was caught by
an outside question rather than by the person who ran it.

**The single sentence that unifies all four:** *the mechanism was validated; the instrument was not.* Effort went
into showing a mechanism does something, and none into showing the instrument could tell if it didn't.

### The four failures these rules are derived from

| # | Failure | What the instrument actually did | Rule |
|---|---|---|---|
| R-82 | "aggrandizer capture is inert" | a redistribution statistic computed over a unit of size 1–2 | **D6** |
| R-85/85c | "seven dead knobs" | flipped booleans without their magnitudes; never recorded the baseline state; grepped a file holding two presets | **D3 D7 D9** |
| R-87 | "the lag doesn't matter" | swept a time constant that was nullified — the driving signal ran 20× the threshold, so every arm crossed in ~12 steps | **D4** |
| R-87c | "no cycles, fourth negative" | an autocorrelation test whose sensitivity, noise floor and trend-robustness were all unmeasured | **D1 D2 D5 D8** |

### The rules (binding on any reported measurement)

**D1 — POSITIVE CONTROL before any negative.** Never report "X does not occur" without showing the instrument
detects X when X is *injected*. Report the **detection floor**. *(R-87c: the cycle detector goes blind below
SNR ≈ 1 — a cycle must be about as large as the noise to register. Unmeasured, a "fourth independent negative"
was reported on the project's central open question.)*

**D2 — NULL FLOOR before any positive, and never an invented threshold.** Report what the statistic returns on
shuffled/noise data, and compare against that. *(R-87c: white-noise ac_peak is mean 0.088 / max 0.138 over 40
trials. The measured 0.19 was ABOVE the noise ceiling and had been dismissed as "weak/none" only because an
invented 0.2 cut happened to sit above it.)*

**D3 — RECORD THE BASELINE STATE beside every verdict.** *"Does nothing when I toggle it"* and *"does nothing"*
are different claims, and only the baseline distinguishes them. *(R-85c: seven flags reported as
"enabled-with-a-dead-gain" were simply OFF in that preset and live in another.)*

**D4 — VERIFY THE SWEPT PARAMETER IS RATE-LIMITING.** Before drawing any conclusion from a sweep, confirm the
parameter changes the OUTCOME, not merely its own value — e.g. sweeping a time constant, check that the event
TIMING actually moves. If the arms behave identically, the parameter is not governing. *(R-87: a lag sweep in
which all three arms were effectively instantaneous.)*

**D5 — DETREND BEFORE ANY TEMPORAL CLAIM.** Autocorrelation, periodicity and stationarity claims on a series
from a growing population must remove the trend, and say so. *(R-87c: a full-range drift drags a genuinely
present cycle from ac_peak 0.43 to 0.11 and misreports the period by 80%. The R-87 run grew 500 → 3200 agents
undetrended, biasing it AGAINST finding cycles.)*

**D6 — DECLARE THE UNIT of every statistic.** A statistic over the wrong unit is §3.1's unit error in
measurement form. *(R-82.)*

**D7 — SCOPE A CONFIG AUDIT TO THE FUNCTION, NOT THE FILE.** `run_se0_controlled_climate.py` defines both
`realistic_forager_demog()` and `emergent_village_demog()`; grepping the file attributes the union to both.
*(R-85c.)*

**D8 — SAVE THE RAW SERIES.** Re-analysis must never require re-running the model. *(R-87c forced a ~20-minute
re-run purely because `frac_gumsa` had not been persisted.)*

**D9 — CHECK THE MAGNITUDE, AND THE MAGNITUDES DOWNSTREAM.** `flag is True` is not evidence a mechanism is live;
the gain may be zero, and it may be zero one level down inside a field builder. A reliable tell: **a derived
field whose standard deviation is exactly 0 while its input's is not.** *(R-85b.)*

**D12 — A VERDICT NEEDS BOTH EFFECT SIZE AND GOODNESS-OF-FIT.** An amplitude (or any effect size) that clears
its null is not sufficient — the model that produced it must also explain the data. *(R-87d: the sinusoid fit
cleared its null in both arms, 0.174 vs 0.061 and 0.130 vs 0.074, while explaining only 14% and 5% of variance.
Amplitude-versus-null alone would have declared a cycle in both. The series was not sinusoidal at all.)*

**D13 — REJECT UNRESOLVABLE SCALES.** A period, wavelength or timescale longer than ~1/3 of the observation
window cannot be distinguished from a trend. Cap the search grid. *(R-87d: two independent instruments both
returned ~250–270 yr from a 300 yr window — one arc, reported as a cycle.)* Related: require a genuine local
maximum rather than the largest value in a tail; an unconditional `argmax` turns drift into a "peak".

**D10 — MEASURE INVARIANCE, NEVER ASSERT IT FROM READING CODE.** *(`enable_cred_renorm` was declared gauge-fixing
on the argument that all downstream cred use is relative; measurement refuted it — the inheritance homeostat's
fixed 1.0 anchor makes rescaling non-scale-invariant. A differential ON/OFF run is cheap; the reasoning was not
sound.)*

**D11 — PLOT ANY GRAPHICAL RESULT, with its floors on the same axes.** Time series, sweeps, distributions,
response/power curves and before/after comparisons get rendered as a chart for visual verification, not reported
only as a table. Show the **null floor** and, where relevant, the **detection floor** on the same axes so a
reader can see whether the signal clears them instead of taking the verdict on trust. *(R-87's cycle verdict was
three autocorrelation numbers in a table and read as "no cycles"; plotted against its own noise floor, one value
was visibly above the noise and below only an invented cut-off. The picture made in one glance a point the table
had buried.)* D8 (persist the raw series) exists so plots can be redrawn without re-running the model.

### The habit these encode

Before reporting any result, ask: **if the effect I am claiming (or denying) were absent (or present), would this
instrument have told me?** If that question has not been answered with a run, the result is not yet a finding.
D1 and D2 are the two that would have caught the most, and they are the cheapest — a positive control and a null
floor are usually a few lines against synthetic data, with no model run at all.


---

*Charter adopted 2026-07-18. Amend by dated note; classifications in §4 are append/update, not rewrite.*
