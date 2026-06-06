# SiC Games — Architecture (ARCHITECTURE.md)

**The ONE question:** "What is the big-picture structure — how do the pieces fit, where are the seams, what did we decide and why, and what's still open?" (charter home: ARCHITECTURE).

**Status:** split from `MODEL_SPEC.md` v0.2 on 2026-06-06 (charter §6). This file holds the **architectural principle, design-decisions log, architecture seams, and the known-gaps/discrepancies ledger**; the per-construct mechanism content (state variables, σ economy, joint task, Cred, pool, reproduction, shocks, world, metrics) moved to **`MECHANISMS.md`**. Section numbers are **inherited verbatim from MODEL_SPEC v0.2** so existing cross-references still resolve — this file owns §0-principle, §9 (world substrate, per charter §2.1), §12, §13, §15; MECHANISMS owns §0-classification, §1–§8, §10, §11, §14.

---

## 0. The architectural principle (and how to read the model)

The model is built on one principle that the reader must hold throughout:

**One civilizational-mechanics infrastructure, with C and Si as parameterised configurations of it — not two parallel models.** The C-vs-Si contrast (the entire point of the project, testing H1(ii)) is expressed as *parameter values and toggles on shared machinery* wherever possible, so that the contrast is explicit and auditable rather than hidden in divergent code paths. This is both a software-architecture decision and a methodological one: divergent code paths drift silently (this is how the ψ-channel confusion that motivated the model spec arose), whereas a shared mechanism with civilization-differentiated parameters forces every difference to be a named, reviewable value.

Because "Si is C with knobs" is *mostly* true but not *always* true, **every mechanism is classified C1 / C2 / C3** — the per-mechanism classification table and its failure modes live in `MECHANISMS.md` §0. The classification is load-bearing: misclassifying a mechanism is how the model can end up running correctly and being theoretically wrong. The architectural treatments are: C1 → build once, expose knobs; C2 → build once but flag civilization-dependent signal/meaning; C3 → a strategy/coordinator *interface* with distinct implementations, not a flag.

**SEAM (orthogonal status).** A **SEAM** is a documented architectural joint where a *deferred* mechanism will plug in, present in the code as an inert (λ=0 / `NotImplementedError`) placeholder under an equivalence gate. Seams are cheap to place during active development of the host subsystem and ruinous to retrofit into locked, tested code. The seam register is §13.

---

## 9. World / resource substrate

*(The "how the world works" half — charter §2.1 routes the world/resource substrate to ARCHITECTURE. Agent mechanisms that read this world live in `MECHANISMS.md` §1–§8, §10–§11; a pointer stub remains at MECHANISMS §9.)*

### 9.1 Mechanism table

| Aspect | Stage 1–3 (k=1) | Stage 4.4+ (k=4) | Category | Provenance |
|---|---|---|---|---|
| Grid | 50×50, toroidal | Same | C1 | Stage 1 §6.1 |
| Twin peaks | (10,40), (40,10) | Same | C1 | Stage 1 §6.1 |
| Capacity function | c(i,j) = max(0, c_max − ⌊d(i,j)/k⌋); c_max=4, k=6 | c_max=16, k=6 (k_grid=4 → c_max=4·k_grid=16) | C1 | Stage 1 §6.1; Stage 4.4 |
| Growback G_α | s(i,j,t+1) = min(s+α, c_eff); α=1 (k=1) | α=4 (k=4; α=k_grid) | C1 | Stage 1 §6.2; Stage 4.4 |
| Init (sugar) | s(i,j,0) = c(i,j) | Same | C1 | Stage 1 §6.1 |
| k_grid rescale | — | k_grid=4 locked Stage 4.4: minimum k where β_Si=5 Si null control passes | C1 | Stage 4.4 §1 |

### 9.2 Narrative

The Sugarscape substrate is canonical Epstein & Axtell (1996). `[VERIFIED]` Epstein & Axtell 1996 — substrate documented in LITERATURE.md.

**The k_grid=4 rescale** (Stage 4.4) was the minimum grid scale where β_Si=5 Si differential metabolism becomes viable. At k=1, max_sugar=4 and mean harvest is ~2–3/step, but Si cost at β=5 is 5–20/step — permanently dormant population. At k=4, max_sugar=16 and mean harvest ~10–15/step vs Si cost_mean ~12.5/step, with dormancy handling shortfalls. Stage 4.4 confirmed: k=3 Si population explosion (Stage 4.4 k=3 Feasibility note in ROADMAP). Rationale: the k_grid rescale is a grid parameter co-design with β_Si; the two are coupled (neither is independently free) (Stage 4.4 Q30). `[INLINE]` Si energy budget rationale cited Stage 4.3 §1.1 (Davies et al. 2018 Loihi, neuromorphic silicon energy efficiency); not in LITERATURE.md (OWE-4).

### 9.3 Physical-unit calibration (OWE-1, 2026-05-30)

**STANDING CONSTRAINT (from OWE-1 Blueprint §3, supervisor decision 2026-05-30):**
*Temporal resolution is changeable, but any change requires full recalibration — every
per-step rate (growback_alpha, metabolism, p_fission_Si, p_max_C, pool contribution,
etc.) must be rescaled by the duration ratio AND the key locked findings (H1(ii)
inversion, T*, A*) must be re-confirmed at the new resolution. Resolution is not a
free knob; it is a calibration-defining commitment. The current commitment is: **1 step = 1 month**.*

**Target geometry (locked OWE-1):** 100×100 cells, ~2000 agents (subject to Task 2
carrying-capacity gate — see outputs/owe1_calibration/report_owe1.html).

**Calibration anchors (OWE-1 §3.1):**

| Anchor | Value | Source |
|---|---|---|
| Forager day-range | ♀ ~8 km/day, ♂ ~14 km/day; Aché ~10–12 km/day | Pontzer Hadza GPS; Hill Aché |
| Total daily energy expenditure (TEE) | ~1800–2500 kcal/day (~2000 working) | Pontzer et al. 2012 (doubly-labeled water, Hadza) |
| Forager home-range | !Kung ~100 km²; upper endpoint: Chumash ~21.6 persons/mi² | H-G synthesis |

**Live gate:** emergent home-range (C-static-medium arm), measured in occupied-cell area
over agent lifetime, must land in the ~100 km² forager band when cell-length ℓ is
solved. Home-range is legitimately joint (foraging + social); do not attempt to
isolate a foraging-only component. See OWE-1 report for solved ℓ (km/cell) and
kcal-per-metabolic-unit.

**Planned diagnostic (OWE-13):** movement-decomposition logging — per-agent per-step
foraging-pull vs social-pull displacement. Registered OWE-13; build at
movement-instrumentation stage. Feeds H-ORTHOGONALITY test (TARGETS T-2) and the
MECHANISMS §3 C2 ψ-channel resolution.

**N_carry is a calibration choice, not an emergent prediction (OWE-1.1, 2026-05-31).**
N_carry was originally set in Stage 4.5 Task 0 as a *numerical-stability scale parameter*
(top of the hand-set [150,400] viability band on the 50×50 world), NOT a realistic
ecological estimate. For the 100×100 target geometry it is therefore legitimate to set
N_carry to realise the intended ~20–60 ethnographic-band population (target settled N ≈ 2500;
see OWE-1.1 report for the measured N_carry→settled-N mapping and chosen value). **The absolute
population is set by the supervisor to realise band structure; what remains emergent — and is
the actual scientific finding — is the C-vs-Si difference at the shared, pre-committed N_carry.**
N_carry must be set ONCE, shared across both arms, and locked BEFORE examining the H1(ii)
comparison at the new scale (locking-before-looking; the original H1(ii) findings were locked
the same way). OWE-14 re-confirms the inversion at the calibrated N_carry (≥3 seeds) before
H1(ii) is trusted at 100×100.

**Home-range estimator correction (OWE-1.1):** the OWE-1 §3 home-range figure (~56 cells →
ℓ=1.34 km/cell, 56× overshoot) was computed as a *lifetime-accumulated* distinct-cell track,
which conflates multi-decade drift with contemporaneous territory. OWE-1.1 recomputes it as a
contemporaneous rolling-window range (annual=12 steps, seasonal=3 steps); see the OWE-1.1
report for whether the cell-size inconsistency is downgraded to an estimator artifact or stands
as a genuine mobility tension.

**R0 confound result + regulation-architecture finding (2026-06-02, supervisor-approved).**
Seasonal forcing fires cleanly at this geometry (Task 0 gate: effective_capacity CV≈0.42
over one cycle, trough phase-aligned at T/2). The static world has **est_starv = 0.0000**;
the seasonal trough **restores finite resource-driven mortality** — est_starv rises
0.0000 (static) → 0.0000 (A=0.5) → **0.0612/step (A=0.75, 3 seeds)**, a *monotonic threshold/
cliff* (only the deep A=0.75 trough engages mortality). Marginal-distance time series confirm
margins breathe with the forcing (D1 5th-pctile → ≈3.4 steps-to-starvation at trough, recovers
at peak). Verdict: **R1 (terrain) leads** the Resource-Ecology design doc; R2 (resource-lifetime
classes) is enrichment, not the primary fix. **D3 mechanism finding:** the static zero-starvation
is a *regulation-architecture* feature, NOT resource abundance — the carrying-cost birth
suppression is **density-based** (`carry_discount = max(0, 1 − N_C/N_carry)`), operating entirely
off the wealth axis, so reproduction is throttled by crowding long before any agent nears
starvation (wealth-axis birth floor θ_sub ≈ 5 steps-of-metabolism above the death threshold,
but the density clamp bites first; static D1 5th-pctile = 18.8 steps, D2 5th-pctile = −3.08).
This is an independent argument that R2 will matter *eventually* even though R1 leads: the
proximate cause of zero static starvation is the regulation mechanism (density-decoupled-from-
mortality), not the resource regime. See `outputs/r0_confound/report_r0.html`.

---

## 12. Design-decisions log

*(Dated entries recording *why*, not just *what*. New entries appended; never silently edited.)*

### §12.1-A — Cultural/physical dual-inheritance split (2026-05-29)

*(Pilot §5.1-A preserved verbatim.)*

**Decision:** PROPOSED — separate inheritance into an explicit cultural channel (φ, c1, c2; vertical + horizontal) and a physical channel (metabolism, vision, max-age, fecundity; vertical only). Replaces the current "cultural inherits, physical re-draws" arrangement.
**Motivation:** the current model labels itself dual-inheritance but the physical channel is inert; supervisor flagged the asymmetry. Proper dual inheritance (Boyd & Richerson) is more honest and unlocks heritable fecundity + physical natural selection.
**Constraint:** physical inheritance ON re-introduces a metabolic-adaptation confound on H1(ii). MUST ship with a control arm (toggle, report both ways) — never silently ON.
**Status:** not implemented. Mixing-rule sub-decision (biparental-average vs single-parent-copy for the physical channel) OPEN — see §15. (Mechanism detail: `MECHANISMS.md` §2.2.)

### §12.1-B — Birth-death demographic model (2026-05-29)

*(Pilot §5.1-B preserved verbatim.)*

**Observation:** current reproduction was *death-triggered* (a death spawned a replacement); Stage 4.1a decouples births from deaths. The C-overreproduction-without-surplus dynamic ("illogical but inherently C") cannot appear under death-triggered replacement. A true birth-death model is required for Turchin secular cycles.
**Compute risk:** managed only if reproduction is density/resource-gated. Stage 4.5 carrying-cost is this gate for C.
**Status:** partially in motion (Stage 4.1a+ C birth probability). Full heritable-fecundity birth-death model = Stage 6+ structural.

### §12.1-C — HiveMind / asabiyyah central-coordination (2026-05-29)

*(Pilot §5.1-C preserved verbatim.)*

**Reframe (supervisor):** HiveMind is not Si-only. It is the limiting case of a **general central-coordination mechanism** governing culture, reproduction, and interaction branches, each with independently-evolvable coupling strength. C runs it with high decision-noise; Si runs it cleaner. **TMTS warning: do not bundle three mechanisms.** Build seams opportunistically; defer mechanisms. See §13.
**Status:** mechanism DEFERRED. Seams: §13.

### §12.1-D — σ_inherit calibration target = c1/c2, not ψ (2026-05-29)

*(Pilot §5.1-D preserved verbatim.)*

**Decision:** σ_inherit / cultural-diversity calibration should target **c1 and c2 diversity** (the traits carrying C-vs-Si theory), with ψ diversity demoted to a reported diagnostic.
**Trigger:** Stage 5.2 Task 3 selected σ*=0.10 by gating on Gini(ψ) — the wrong statistic (use SD) and the wrong target trait. The gate was on the wrong trait and the wrong statistic.
**Status:** supersedes the retired Stage 5.2 Task 3 σ* selection. σ_inherit=0.10 is the current lock but under review. A corrective directive targeting c1/c2, ≥8 seeds, is pending.

### §12.1-E — Metabolism not inherited (current) is a confound-control choice (2026-05-29)

*(Pilot §5.1-E preserved verbatim.)*

**Clarification:** physical attributes are re-drawn fresh, deliberately, following canonical Sugarscape (Epstein & Axtell 1996), to keep differential survival attributable to *strategy* not *metabolic evolution*. Superseded if §12.1-A is adopted.

### §12.1-F — MODEL_SPEC split into ARCHITECTURE + MECHANISMS (2026-06-06)

**Decision:** the single `MODEL_SPEC.md` (v0.2 full extraction) was split into two charter homes per the charter §2.1 mapping — `MECHANISMS.md` (per-construct registry: §0-classification, §1–§8, §10, §11, §14) and `ARCHITECTURE.md` (this file: §0-principle, §9 world substrate, §12, §13, §15). §9 went to ARCHITECTURE as "the how-the-world-works half" (charter §2.1); a pointer stub remains at MECHANISMS §9. The original is archived at `archive/superseded/MODEL_SPEC_v0.2_pre-split_2026-06-06.md`.
**Motivation:** discharges the charter §6 split, which became load-bearing immediately ahead of the §7.5 array-restructure: that refactor's core product is a *per-mechanic* Tier-1/2/3 equivalence classification plus declared update semantics — MECHANISMS content — and it writes its rationale to "the ARCHITECTURE/MECHANISMS decision log," which now exists. Doing the split first means the restructure updates each home in final form rather than the interim MODEL_SPEC, avoiding double-authoring and drift.
**Method:** content moved verbatim, no facts altered; section numbers preserved across both files so every existing "MODEL_SPEC §N / §12.x / §15.x" pointer still resolves. PARAMETERS extraction (the other half of §6) is **not** part of this change — parameter values remain in the `sic_games/CLAUDE.md` locked-param table (the §14 pointer points there) until extracted.
**Status:** done. INDEX.md, README.md, and `sic_games/CLAUDE.md` triggers updated to name the two homes.

### §12.1-G — σ formula is Tier-2 (not Tier-1) under vectorised tanh (2026-06-06)

**Finding (Stage 7.5 WS-A migration):** the blueprint §3 listed the decision-σ formula
`σ = σ_base + κ·tanh(𝒞/C*)` (and `σ_Si_eff`, status amplification) under **Tier 1
(bit-identical)**. Empirically, on **numpy 2.4.3 / this platform, `np.tanh` is NOT
bit-identical to Python's `math.tanh`** — it differs by up to ~1 ULP (max relative
~2.2e-16). (`np.exp` *is* bit-identical here, so the stress sigmoid is unaffected.)
**Therefore the vectorised σ migration is Tier-2 (rtol ≈ 1e-9), not Tier-1** — it
passes the 1e-9 gate with ~10⁷ margin, but cannot be claimed bit-identical without
applying tanh scalar-wise (which forfeits the vectorisation that is the whole point).

**Decision:** classify `temperature_carbon` / `temperature_si` / status-amplification as
**Tier-2**; keep the genuinely pure-arithmetic per-agent updates (cred decay, metabolize,
Si-cred band, η(a)) as **Tier-1 bit-identical** (verified). This is consistent with §3's
own logic — Tier-2 is the home for "algebraically exact, FP differs"; transcendental-
implementation divergence is the same class as reduction-order divergence. The σ value
feeds a softmax; a ~1-ULP shift could in principle flip a movement tie with vanishing
probability — folded into the Tier-3 statistical battery at the full-model gate. Code:
`src/sic_games/soa_tier1.py`; parity tests: `tests/test_soa_tier1.py`.

---

## 13. Architecture seams

*(Pilot §5.2 preserved verbatim.)*

| Seam | Where it enters | Inert form | Equivalence gate (required) | Natural host stage to place it |
|---|---|---|---|---|
| Reproduction coordinator (HiveMind) | `ReproductionCoordinator` dispatch | `_si_hivemind_birth` → `NotImplementedError` | coordinator=`individual` reproduces current behaviour bit-exact | **Already placed** (4.1a §1.4) ✓ |
| Asabiyyah → culture coupling | Deffuant update step | central-attractor term with λ_cult = 0 (term present, contributes nothing) | λ_cult=0 → bit-identical to no-attractor Deffuant | whichever stage finalises Deffuant |
| Asabiyyah → reproduction coupling | birth-probability computation | collective-modulation factor = 1 (multiplicative identity) at λ_rep=0 | λ_rep=0 → bit-identical to ungated P_birth | the birth-death stage (§12.1-B) |
| Asabiyyah → interaction coupling | movement/partner utility | coupling term with λ_int = 0 | λ_int=0 → bit-identical to current utility | whichever stage activates the interaction hook |
| Asabiyyah trait dimension | trait vector H_i | extra inherited dimension, behaviourally unread until a λ>0 | trait carried but inert → no behavioural change vs absent | when any of the above seams is first placed |

**Seam discipline:** a seam is an asset only if **provably inert** under its equivalence gate.

> **§7.5 array-restructure note (2026-06-06):** the array reformulation will migrate each mechanism above against a frozen object-model oracle under a per-mechanic equivalence tier (bit / 1e-9 / statistical). The seam discipline is unchanged — every `enabled=False`/λ=0 path must still recover the prior stage at Tier 1/2. See `blueprints/stage 7/` (or `blueprints/restructure/`) and the parity-harness artifacts indexed in ARTIFACTS.md.

---

## 15. Known gaps, unsourced items, and discrepancies

### 15.1 Citations needing LITERATURE.md entries

The following citations appear in blueprints but were NOT in the focused LITERATURE.md Si-Cred section. They enter as **`[INLINE]`** and must be confirmed against `docs/LITERATURE.md` (now the full unified bibliography) before use in any write-up:

| Citation | Mechanism | Blueprint(s) | Current tag |
|---|---|---|---|
| Deffuant et al. (2000), *Mixing beliefs among interacting agents* | Deffuant bounded-confidence updating (MECHANISMS §3.3) | Stage 3.3 §0; 5.2 §3 | `[INLINE]` |
| Hegselmann & Krause (2002) — HK opinion dynamics | Deffuant alternative form | Stage 3.3 §0 | `[INLINE]` |
| Boyd & Richerson (1985), ch. 5 — prestige bias | Cred-weighted Deffuant; dual inheritance | Stage 3.3 §0; ROADMAP | `[INLINE]` |
| Turchin (2003) — secular cycles | Cred-modulated C birth (elite overproduction) | ROADMAP; Stage 4.1a | `[INLINE]` |
| Epstein & Axtell (1996), ch. 3 — Sugarscape cultural transmission | World substrate; endowment distributions | Stage 1 §1; LITERATURE.md (partial) | `[VERIFIED]` for substrate; `[INLINE]` for cultural chapter specifically |
| Axelrod (1997) — Dissemination of Culture | Between-run diversity frame | Stage 1 §1.4 | `[INLINE]` |
| Klemm et al. (2003) — noise non-monotonic effect on cultural diversity | Project contribution frame | Stage 1 §1.4 | `[INLINE]` |
| Gurven & Kaplan (2006) — Longevity Among Hunter-Gatherers | η(a) age-efficiency ramp | Stage 4.1b §1.2 | `[INLINE]` |
| Davies et al. (2018), Loihi — neuromorphic silicon | Si β=5 energy ratio | Stage 4.3 §1.1 | `[INLINE]` |
| Brock & Hommes (1997) — Boltzmann decision rule | Si Cred σ-modulation form | LITERATURE.md (cited) | `[VERIFIED]` |
| Axelrod (1984) — Evolution of Cooperation | Si Cred self-referential loop | LITERATURE.md | `[VERIFIED]` |
| Nowak & May (1992) — spatial prisoner's dilemma | Si Cred rejected alternative | LITERATURE.md | `[VERIFIED]` (rejected) |

**Citations from Claude's general knowledge — `[UNVERIFIED]`, confirm before any write-up:**

| Citation | Claim | SPEC section |
|---|---|---|
| Richerson & Boyd (2005), *Not by Genes Alone* | Dual inheritance theory | MECHANISMS §2.2 |
| Price (1970, 1972); Frank (1995/1997/2012) | Price-equation selection decomposition | MECHANISMS §10 |
| Grimm et al. (2006, 2010, 2020) | ODD protocol | MECHANISMS header |
| Merton (1968) | Matthew Effect (cumulative advantage) | MECHANISMS §4.2 |

### 15.2 Discrepancies (code/blueprint vs ROADMAP)

| ID | Description | Source |
|---|---|---|
| D1 | τ_trickle in ROADMAP locked-param table says 0.3, CLAUDE.md says 0.05, Stage 4.3 blueprint says 0.05. ROADMAP rationale row says "raised to 0.3" — Stage 4.5 onward used 0.3. CLAUDE.md appears stale. Resolved: 0.3 is the actual value in Stage 5+ configs (verified from Stage 5 T3_Si_null_cred.yaml). No code change; note for CLAUDE.md update. | Stage 4.3 §1.2; Stage 5 configs |
| D2 | σ_inherit in CLAUDE.md says 0.05 (Stage 3.3 original lock). Stage 5.2 raised it to 0.10 and updated CLAUDE.md. ROADMAP locked-param table now shows 0.10 at Stage 5.2. Consistent. No discrepancy. | Stage 5.2 |
| D3 | p_fission_Si: CLAUDE.md says 0.28 (Stage 4.3 lock). ROADMAP shows 0.065 for Stage 4.4 (β=5, k=4). Stage 5+ configs used 0.065. CLAUDE.md appears stale for this parameter — it was not updated when Stage 4.4 changed the value. The operative value for Stage 5+ is 0.065. | Stage 4.4; Stage 5 configs |

### 15.3 Open modelling decisions

*(Pilot §6 open decisions preserved; extended with Stage 5.2 additions.)*

1. **ψ's channel** — cultural (Deffuant-subject) vs physical (vertical-only disposition). MECHANISMS §2.3. Resolving toward physical dissolves the Cell B tension.
2. **Physical-channel mixing rule** — biparental-average (C) vs single-parent-copy (Si) for physical inheritance. MECHANISMS §2.2 / §12.1-A.
3. **Asabiyyah locus** — per-agent evolvable trait vs population-level variable. §12.1-C.
4. **Physical-inheritance control design** — variance-matched-across-civ vs toggle-and-report-both. §12.1-A.
5. **σ_inherit corrective sweep** — targeting c1/c2, ≥8 seeds, correct statistic (SD not Gini). σ_inherit=0.10 current lock is under review (§12.1-D).
6. **C\*\* = C\*** pinning — C\*\* pinned to C\* at Stage 3.2 as an implementation choice; deferred Q11 (ROADMAP). Not resolved.

### 15.4 Statistic note

*(Pilot §6 statistic note preserved verbatim.)*

ψ, c1, c2 are bounded `[0,1]` traits initialised at mean 0.5 with SD 0.2. **Gini is the wrong dispersion measure** for a bounded, mean-0.5 trait. Use **SD (or variance)** referenced to the initial SD=0.2; a collapse to SD < ~0.05 is a meaningful homogenisation signal. The Stage 5.2 report's Gini(ψ) ≥ 0.15 floor was arbitrary partly *because* it was the wrong statistic. (Operative rule also stated at MECHANISMS §11.3.)

### 15.5 NOT-YET-ADOPTED literature

*(Pilot §6 NOT-YET-ADOPTED list preserved verbatim for HiveMind/asabiyyah branch.)*

- Turchin (2003, 2016) — asabiyyah as a dynamic solidarity variable over secular cycles.
- Norenzayan (2013), *Big Gods*; Norenzayan et al. (2016, *BBS*) — moralising/centralised religion as cooperation-scaling technology.
- Henrich (2015), *The Secret of Our Success* — conformist transmission as a population-level force.
- HK/Deffuant-with-exogenous-attractor — the mechanical precedent for "central institution biases cultural transmission toward an attractor."

---

*End of ARCHITECTURE.md — split from MODEL_SPEC v0.2 on 2026-06-06. Per-construct mechanism content is in `MECHANISMS.md`.*
