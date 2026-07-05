# SiC Games — Targets (TARGETS.md)

**Purpose:** The home for **emergent behaviours the project is shooting for** — qualitative
phenomenology we hope the model produces — that are *not yet* formal predictions. This is the
deliberate counterpart to HYPOTHESES.md: a place for generative ideas to live honestly,
without masquerading as pre-registered predictions.
**Maintainer:** Supervisor curates; Claude Code maintains.
**Created:** 2026-06-05.
**Not here:** *quantitative* empirical benchmarks (village size, density, catchment radius, agglomeration α — the values the model is calibrated/validated against, with extraction methods) live in **`MODEL_SPEC.md` §4.8.21** (the methods home). This doc is for *qualitative emergent aspirations* only.

---

## The line between a TARGET and a HYPOTHESIS (charter §5)

- A **TARGET** is an aspiration — "we're shooting for X to emerge." Qualitative, not tied to
  a specific scheduled run, not falsifiable-as-written.
- A **HYPOTHESIS** is a pre-registration — a falsifiable claim with a test spec (which run,
  which statistic, which threshold) and a pre-committed interpretation, dated *before* the run.

**Graduation rule:** a target becomes a hypothesis the moment it acquires a falsification
spec. At that point it is **moved** (not copied) into HYPOTHESES.md with its registration
date, and its entry here is replaced by a pointer. **A target is never marked
"supported/confirmed"** — only a hypothesis can resolve. The test of whether something is
ready to graduate: *could a run plausibly come out against it and update you?* If not, it
stays a target (or it's really a finding → RESULTS, or an abandoned idea → DEAD_ENDS).

---

## T-1 — Microscale secular cycles from status-coupled decision noise

**Status:** TARGET (highest interest). **Origin:** supervisor, 2026-06-05.

**Aspiration:** the C status–σ coupling (`σ_i = σ_base + κ·tanh(𝒞_i/C*)`, MECHANISMS / Cred)
— high-Cred agents make noisier decisions — produces **boom/bust cyclic dynamics at the
microscale**: within family lineages or local clusters ("tribes"), Cred concentrates →
decision noise rises in the high-Cred set → over-exploration / mis-foraging → local collapse
→ Cred redistributes → recovery. A Turchin-style secular cycle, but emergent at the
lineage/cluster scale rather than imposed at the population scale.

**Why this is a real target and not a rationalization:** it is genuinely falsifiable in
principle — a run could show Cred and decision-noise *don't* couple to any cyclic structure,
or that local dynamics are monotonic rather than oscillatory. That asymmetry (it could embarrass
us) is exactly what makes it worth chasing.

**What it needs to graduate to a HYPOTHESIS:**
- A unit of analysis: lineage (parent-child tree) and/or local cluster (cell-neighbourhood).
- A periodicity statistic: autocorrelation / spectral peak / peak-trough counting on a
  per-unit time series of {cluster size, local mean Cred, Cred concentration (Gini or top-share)}.
- A threshold distinguishing "cyclic" from "noise" and from "monotonic," and seeds (≥5+).
- A pre-committed interpretation of cyclic / acyclic / monotonic outcomes.
- *Watch:* this is a measurement target, not a license to add a group-level cycle mechanism
  (cf. H-EMERGE-1's TMTS guard — emergence must come from existing mechanisms).

---

## T-2 — C/Si home-range orthogonality (movement decomposition)

**Status:** TARGET (deprioritized). **Origin:** routed from the former H-ORTHOGONALITY
pre-registration, 2026-06-05. See DEAD_ENDS for the deprioritization note.

**Aspiration:** C and Si movement decomposes into different mixtures of foraging-pull (sugar
gradient) vs social-pull (ψ proximity) — C weighted toward social, Si toward foraging — as a
*difference-set*, not merely a scale difference.

**Why it's a target, not a hypothesis:** it is close to **implied by construction** — the C2
classification (MECHANISMS: ψ proximity-to-agents for C vs proximity-to-foraging-spots for Si)
already builds the asymmetry in, so a "confirmation" would largely restate the design rather
than risk it. Low capacity to embarrass us. Worth *measuring* if the diagnostic gets built,
but not a live bet.

**What it needs to graduate:** the OWE-13 movement-decomposition diagnostic built and
validated; matched C/Si runs at a density where both survive ≥2000 steps post-transient; and
a pre-committed magnitude threshold for "orthogonal" vs "parallel-but-scaled." If/when OWE-13
is scheduled, this graduates with the test spec already drafted in the original pre-reg.

---

## T-3 — Instinct-debt mortality (culturally-mandated exploration cost)

**Status:** TARGET (contingent, downstream of T-2). **Origin:** routed from the former
H-instinct-debt pre-registration, 2026-06-05.

**Aspiration:** the social-pull term draws C agents away from optimal foraging under stress,
so in deep troughs C agents die at *higher* wealth than starvation would require — a bimodal
terminal-wealth-at-death distribution (one mode near zero = true starvation; one mode at
2–5× metabolism = "instinct-debt death") — absent when the ψ social term is disabled.

**Why it's a (good) target:** more specific and more falsifiable than T-2 — the bimodality
prediction could clearly fail. But it is doubly gated: it needs OWE-13, and it presupposes T-2
holds (no orthogonality ⇒ no pathway). No run is coming, so it waits.

**What it needs to graduate:** OWE-13 built; T-2 measured and holding; terminal-wealth-at-death
histogram logged per strategy per trough phase; a matched C control with the ψ social term
disabled; ≥5 seeds; pre-committed interpretation of bimodal vs unimodal.

---

## T-4 — Emergent nutritional child mortality reproduces the Aché schedule

**Status:** TARGET (downstream of the Resource-Ecology stage). **Origin:** supervisor, 2026-06-19.

**Aspiration:** instead of the all-cause Aché Siler encoding child mortality *by construction*,
**decouple the nutritional component**: keep an exogenous non-nutritional residual (accidents,
violence, non-nutritional infection — from Hill & Hurtado cause-of-death) in the schedule, and let
the **nutritional** part of child mortality EMERGE from the mechanisms — children's low per-class
reserves × scarcity (seasonality / depletion) × parental provisioning load. The emergent nutritional
child mortality + the exogenous residual should then **reproduce the empirical Aché child-mortality
schedule**.

**Why this is a real target and not a rationalization:** it is genuinely falsifiable — the emergent
child mortality could come out too high, too low, or the wrong age-shape, and that would update us on
what the nutrition/provisioning model is missing. It converts "the model reproduces Aché child
mortality" from a **tautology** (painted-in by the all-cause Siler) into a real test of the mechanisms
— the project's "emergent, not painted-in" ideal applied to mortality — and it dissolves the M-3-style
double-count (nutrition is the part *removed* from the Siler, not restated on top of it).

**What it needs to graduate to a HYPOTHESIS:**
- The Resource-Ecology stage built and trustworthy: nutritional variance (seasonality + depletion),
  per-class reserves (children's low buffer), and family provisioning (JV-1 / MR-2).
- A decomposition of Aché child mortality into nutritional vs non-nutritional from Hill & Hurtado
  cause-of-death (the non-nutritional residual stays in the Siler).
- An l(x) / q(x) comparison over child ages with a tolerance band, ≥5 seeds, and a pre-committed
  interpretation of match / too-high / too-low / wrong-shape.
- *Watch (TMTS guard):* the emergent mortality must come from the existing reserve/scarcity/provisioning
  mechanisms, not a new child-mortality knob.

**⚑ [2026-06-20 — ATTEMPTED & DEFERRED — THE MARK FOR LATER]** First attempt at the *fine* (graded
nutrition→disease) version, via **S0** (lagged body-condition EMA so synergy reads sustained nutritional
state, not the bang-bang reserve) + **S1** (child-priority shortfall-sharing). **Result: CORRECT-BUT-INERT**
(red-team `a1f44d9c`, RESULTS R-11). The code is right; it can't bite because provisioning **tops children
to their cap** → survivors sit at condition ≈1.0, and the only under-cap children hit the starvation floor
in ~1 step (R-10 bang-bang) before the EMA moves. The self-regulation attractor (R-5…R-8) defeats it: the
*surviving* mothers are by construction the ones who can cover their kids, so children rarely dwell lean.
**What the fine version needs to graduate (the deferred work):** a TWO-part fix — (a) change provisioning
*target* from cap to maintenance/burn (`phase1_model.py:338`) so a drawn-down child is NOT refilled and
dwells at partial reserve; **AND** (b) slow the child reserve dynamics (widen the cap-to-floor span beyond
~1.3 months) OR add **stochastic foraging returns** so even adequate mothers occasionally fail — i.e.
re-open the R-7 "source-of-variance" problem one level down. Red-team predicts (a) alone stays flat. This is
a dedicated research subproject, NOT a quick add. **Banked, not abandoned:** `enable_condition` /
`condition_alpha` (S0) are kept as **opt-in, off-by-default** flags for this future effort.
**The COARSE version IS in use now** (RESULTS R-11): the model's two existing cause buckets —
**starvation (floor)** vs **Siler baseline `deaths_senesc` (disease+infanticide+accident)** — give a
disease-dominated / low-nutritional child split that roughly matches the Aché coarse benchmark, with **S1
(kept ON)** driving child nutritional death toward the data's ≈0. The Biome-Mortality stage validates this
coarse split as a byproduct; the fine mechanistic synergy is what remains here as T-4.

---

*End of TARGETS — seeded 2026-06-05. Graduate a target by moving it to HYPOTHESES with a test
spec; never mark a target "confirmed."*
