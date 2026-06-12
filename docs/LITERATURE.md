# Literature log

This file records every paper, model, or implementation consulted during development.
Format: citation, what was lifted/learned, what was rejected.
See blueprint §10.9 for the maintenance protocol.

---

## Epstein, J. M. & Axtell, R. L. (1996). *Growing Artificial Societies: Social Science from the Bottom Up.* MIT Press / Brookings.

**What was lifted:**
- Stage 1 is a direct implementation of their Chapter 2 model: 50×50 toroidal grid, twin sugar peaks, growback rule G_α (α=1), movement rule M (von Neumann vision, greedy argmax), replacement rule R (constant population N=250).
- Agent attribute distributions: vision U[1,6], metabolism U[1,4], max-age U[60,100], initial wealth U[5,25].
- The canonical qualitative result used as our validation target: right-skewed wealth distribution (Gini ≈ 0.4–0.6), spatial clustering on peaks.

**What was rejected / deferred:**
- Chapters 3+ (sex, culture, trade, combat, disease) — deferred to Stages 7+.
- The "carrying capacity" concept as a single-peak sugar field — we use twin peaks per Agents.jl convention.

---

## JASSS Appendix B (Epstein & Axtell 1996, Chapter 2 formal model)
`https://jasss.soc.surrey.ac.uk/12/1/6/appendixB/EpsteinAxtell1996.html`

**What was lifted:**
- Formal specification of rules G, M, R used to resolve implementation ambiguities.
- Confirmed: M applies to unoccupied cells; current cell is included in candidate set; toroidal movement.
- Scheduling order: G first, then M in random agent order, then R.

**What was rejected:**
- Nothing — this is the authoritative spec for Stage 1.

---

## Agents.jl Sugarscape example
`https://juliadynamics.github.io/Agents.jl/v4.1/examples/sugarscape/`

**What was lifted:**
- Confirmed peak locations: (10, 40) and (40, 10) on a 50×50 grid.
- Capacity formula: `max(0, max_sugar − floor(min_dist / dia))` with `dia = 6`, `max_sugar = 4`.
- Used as a cross-reference for parameter values when the 1996 book is not directly accessible.

**What was rejected:**
- Julia-specific implementation details (Agents.jl API, Julia type system) — not applicable.

---

## Mesa 3.5.1 documentation
`https://mesa.readthedocs.io/en/stable/`

**What was lifted:**
- Mesa 3.x scheduler API: `self.agents.shuffle_do("step")` replaces deprecated `RandomActivation`.
- `Agent.__init__` no longer requires `unique_id` (auto-assigned).
- `super().__init__(seed=seed)` for reproducible seeding in `Model`.
- Agent has `.random` (stdlib Random) and `.rng` (numpy Generator) already seeded.
- Migration guide: `RandomActivation` deprecated in 3.0, removed in 3.1.

**What was rejected:**
- Mesa's spatial grid classes (`SingleGrid`, `MultiGrid`, `OrthogonalVonNeumannGrid`) — not used because the Sugarscape movement rule requires arm-by-arm scanning in cardinal directions, which is cleaner with numpy arrays + occupancy set. Mesa is used only for `Model`/`Agent`/`AgentSet`.

---

## Klein, J. et al. (2024). Common Random Numbers for Variance-Matched Comparisons.

**What was lifted (for Stage 2+):**
- CRN method: paired C vs Si runs must reuse the same RNG seed sequence for environmental stochasticity.
- Only decision-noise RNG draws differ between conditions.
- Reference for honest variance-matched comparison design (blueprint §10.11).

**What was rejected / deferred:**
- Implementation deferred to Stage 2 when the first comparative runs exist.

---

## Klemm, K. et al. (2003). "Global culture: A noise-induced transition in finite systems." *Physical Review E* 67.

**What was noted (for Stage 2+):**
- Key finding: noise has a *non-monotonic* effect on cultural diversity — a prediction that our status-coupled noise mechanism should be compared against.
- Specifically: uniform noise above a threshold destroys diversity; our claim is that status-coupled noise has a different functional form.
- Will inform metric design and the theoretical framing of Stage 2 comparative results.

---

## Gigerenzer, G. & Brighton, H. (2009). "Homo Heuristicus: Why Biased Minds Make Better Inferences." *Topics in Cognitive Science* 1.

**What was noted (for Stage 2+):**
- Individual-level evidence that simple heuristics outperform full optimization under uncertainty — the precursor claim our project extends to civilization scale.
- The Stage 2 Si decision logic (bounded-rational softmax) should be designed to match their ecological rationality framing, not the full-optimization strawman.

---

## Deffuant, G. et al. (2000). "Mixing beliefs among interacting agents." *Advances in Complex Systems* 3(1–4), 87–98.

**What was noted (Stage 3.3 literature search):**
- Bounded confidence model: agents update opinions only when the difference falls within a threshold ε. Produces opinion clusters proportional to 1/(2ε).
- Key finding: continuous interaction + averaging produces polarisation or consensus depending on ε — not monotone homogenization.
- For Stage 3.3: this is the model that Stage 4+ Deffuant updating will implement. In Stage 3.3 we use simple midpoint averaging (no bounded confidence). Bounded confidence is explicitly deferred to Stage 4+.
- Rejection for Stage 3.3: no opinion update on interaction — traits are inherited only at reproduction, not continuously updated during life.

---

## Hegselmann, R. & Krause, U. (2002). "Opinion Dynamics and Bounded Confidence." *Journal of Artificial Societies and Social Simulation* 5(3).

**What was noted (Stage 3.3 literature search):**
- HK model: simultaneous averaging with all neighbours within confidence bound, vs Deffuant pairwise. Produces fewer, broader clusters.
- For Stage 3.3: alternative to Deffuant for Stage 4+. Noted but deferred.
- Rejection for Stage 3.3: same reason as Deffuant — no in-life trait updating.

---

## Epstein, J. M. & Axtell, R. L. (1996) Ch. 3 — Cultural transmission in Sugarscape.

**What was lifted (Stage 3.3):**
- Cultural tags are inherited (one tag per dimension) with copy-error noise. Epstein & Axtell use binary strings; we use continuous traits in [0,1] — same inheritance logic, continuous extension.
- Biparental reproduction: we borrow the parent-selection-from-neighbours protocol directly from their ch. 3 model. Toroidal neighbourhood, random pair from nearby candidates.
- Copy-error (σ_inherit = 0.05): chosen to be smaller than the initial trait std (0.2) to slow homogenization without eliminating drift.
- Fallback to fresh trait draw when < 2 neighbours: follows Epstein & Axtell's implicit assumption that isolated agents reproduce asexually (fresh draw).

**What was rejected:**
- Binary tag strings — replaced by continuous [0,1] traits for richer dynamics.
- Sex-based reproduction (same-sex pairs can reproduce in our model). Parent similarity conditions — not implemented; random selection from spatial neighbourhood.

---

## Boyd, R. & Richerson, P. (1985). *Culture and the Evolutionary Process.* University of Chicago. Ch. 5 — Prestige bias.

**What was noted (Stage 3.3 literature search):**
- Prestige bias: individuals preferentially copy high-status models, accelerating convergence on the high-status trait value. Quantified as a frequency-independent bias proportional to social rank.
- For Stage 4+: prestige bias in Stage 3.3+ would mean Cred-weighted parent influence (higher-Cred parent contributes more than 50% of trait midpoint). Deferred — tracked in ROADMAP.md.
- Rejection for Stage 3.3: midpoint mixing (equal weight per parent) is the neutral baseline. Prestige bias is an additional mechanism to be isolated in Stage 4+.

---

## Roll, R. (1986). "The Hubris Hypothesis of Corporate Takeovers." *Journal of Business* 59(2), 197–216.

**What was lifted (Stage 3.2):**
- The hubris hypothesis: high-status decision-makers systematically escalate commitment to
  status-seeking strategies as prior successes accumulate, beyond what expected-value
  calculations justify.
- Empirical basis for β (status amplification): β quantifies the rate at which accumulated
  Cred amplifies a C agent's preference for social positioning over resource acquisition.
  At β=0, the agent behaves as in Stage 3. At β>0, success breeds ambition non-linearly.
- The interaction between stress suppression (wealth velocity term) and amplification is
  intentional and follows Roll's finding: status escalation is a *luxury of success* —
  it activates when performance metrics are strong, suppressed when under resource stress.

**What was rejected:**
- Corporate finance mechanisms (merger premiums, synergy estimates) — domain-specific.
- The rational-market framing; we use the behavioral finding only.

---

## Gurven, M. & Kaplan, H. (2006). "Longevity Among Hunter-Gatherers: A Cross-Cultural Examination." *Population and Development Review* 32(2), 321–365.

**What was lifted (Stage 4.1b):**
- Empirical life-history efficiency curves for small-scale societies: net caloric productivity peaks in mid-adulthood (~35–45) and declines before and after.
- Juveniles under ~15 are net consumers (subsistence deficit), not net producers — motivates the ramp η(a) from η_min at birth to 1.0 at forage_age_min=15.
- Elders show declining productivity from late adulthood — motivates the η_old=0.4 floor beyond forage_age_max.
- Juvenile dependency period and elder subsistence deficit are cross-culturally robust findings.

**What was rejected:**
- Specific caloric values and productivity curves — translated to dimensionless η ∈ [0,1] bounded on model wealth units.
- Age-specific fertility schedules (used only for the qualitative shape of the efficiency ramp, not for birth probability calibration).

---

## Turchin, P. (2003). *Historical Dynamics: Why States Rise and Fall.* Princeton.

**What was noted (for Stage 2+):**
- Turchin finds stratification destabilizing in historical data — a competing prediction to the "Cred as adaptive mechanism" claim.
- The Stage 6 statistical framework should explicitly test whether our model reproduces or contradicts Turchin's destabilization prediction.

---

> **Merge note (2026-06-05 reorg):** the section below was unified in from a second,
> root-level LITERATURE.md (the focused "Si Cred mechanism" study) that the fuller
> bibliography above did not contain. Where a source recurs (Epstein & Axtell;
> Brock & Hommes), the entry above is the general home and the synthesis below cites
> it for the Si-Cred-specific rationale. Source archived at
> `archive/superseded/LITERATURE_root-SiCred_2026-06-05.md`.

## Stage 5 — Task 3: Si Cred Mechanism

**Question:** What mechanism governs how the Si "Cred" (performance-based
reputation) accumulates and influences behaviour in bounded-rational agents?

**Axelrod (1984) — *The Evolution of Cooperation*:**
Repeated-game reputation (tit-for-tat) stabilises cooperation without central
enforcement; reputation is *relational* (dyadic) and binary. Key insight adopted
for Si Cred: *performance history creates a signal behaviour can condition on*.
**Adopted:** the self-referential performance-feedback loop (agent adjusts its own
temperature from its own recent harvest surplus) — *not* the dyadic reputational
model, which needs interaction tracking deferred to Stage 5.x.

**Nowak & May (1992) — spatial prisoner's dilemma:**
Local-neighbourhood reputation drives spatial clusters of cooperators. Motivates
keeping Si Cred a *local* signal rather than a global broadcast.
**Rejected for Si Cred:** full neighbourhood reputational tracking adds O(N·r²)
state per step; deferred to Stage 5.x.

**Bounded-rationality / performance-modulated temperature (Brock & Hommes 1997
*Econometrica*; Hommes 2006 *JEL*):** the Softmax/Boltzmann σ-temperature rule is
standard, but there global temperature is *fixed*. Si Cred *personalises* it —
high-surplus agents get higher σ_eff (more explorative), mirroring "confidence."
**Adopted:** σ_Si_eff_i(t) = σ_Si + κ_Si · tanh(si_cred_i(t) / C*_Si),
with κ_Si < C's κ because Si has no joint-task amplification channel.

### Mechanism adopted (Stage 5 default — values are authoritative in PARAMETERS.md once split)

```
Δsi_cred_i(t) = max(0, harvest_i(t) − metabolism_i(t)) × r_cred_Si
si_cred_i(t)  = si_cred_i(t−1) × (1 − δ) + Δsi_cred_i(t)
σ_Si_eff_i(t) = σ_Si + κ_Si × tanh(si_cred_i(t) / C*_Si)
```

`enabled=False` recovers Stage 4.5 Si behaviour exactly.
**Note (cross-ref CLAUDE.md param ledger):** `r_cred_Si` was subsequently
**RETIRED** in the Stage 5.1 Si-Cred near-dormancy redesign — see the locked-param
table in `sic_games/CLAUDE.md` (and PARAMETERS.md once the §6 split lands).

### Rejected alternatives
- **Dyadic reputational Cred:** requires a pair-interaction log; deferred to Stage 5.x.
- **Wealth-proportional Cred:** w_i/mean_w conflates stock and flow; surplus-flow
  (harvest−metabolism) is cleaner — signals *current* foraging success, not
  accumulated advantage.
- **Binary high/low Cred:** loses gradient information that σ modulation uses.

---

## Stage 7 — Terrain Generator

### Morin, Bird, Winterhalder & Bliege Bird (2024). "Why Do Humans Hunt Cooperatively? Ethnohistoric Data Reveal the Contexts, Advantages, and Evolutionary Importance of Communal Hunting." *Current Anthropology* 65(5):876–921. DOI 10.1086/732354. `[VERIFIED]`

**Role:** Savanna-game / communal-drive-hunt (CDH) anchor — grounds the soft-gate (steep-but-finite, not hard step) for open-ground game.

**What was lifted:**
- Ungulate CDH success rate **67.2%** (85% CI 56.5–80.1) vs **42%** encounter (CI 36.1–49.0).
- Flight-initiation distance at 40 kg: **177 m** (ungulates) vs **45 m** (non-ungulates); escape velocity 59 vs 39 km/h.
- Herding roughly **doubles** CDH probability (0.76 vs 0.41 at 40 kg).
- Patch-creation framing: open environments = steering herds to vulnerable locations; forests = funnel/beater patch-creation.
- CDH advantage is **episodic / seasonal-aggregation-dependent**, not a steady tap.

**Provenance:** Full text read in chat session; tables 1, 4, 5, figs 5–8. `[VERIFIED]` authorised on this provenance.

**What was rejected / deferred:**
- Game-field rework tying game to savanna/open-woody herd-density: deferred to Stage 7.2 (see §12 pre-registered finding, terrain blueprint).

---

### Janssen, M. A. & Hill, K. (2014). "An agent-based model of resource distribution and cooperative hunting among Aché hunter-gatherers of Paraguay." *Human Ecology* 42:823–835. DOI 10.1007/s10745-014-9693-1. `[VERIFIED]`

**Full citation:** Marco A. Janssen & Kim Hill (2014). *Human Ecology* 42, 823–835. DOI 10.1007/s10745-014-9693-1. CoMSES model codebase: 3902.

**Role:** Forest-game anchor (Aché cooperative hunting in closed canopy).

**Model environment:** Mbaracayu Reserve, Paraguay (tropical forest). 100 replicate runs per condition over 1 simulated year; 100 simulated years for group-size sweep.

**CORRECTED reading (supersedes any prior abstract-only summary):**
- Cooperative hunting (CCSP model) yields **−4% mean harvest vs solitary** (2.82 vs 2.95 kg/day/hunter).
- Risk reduction is large: zero-return day probability **83% lower** (9% cooperative camp vs 52% solitary).
- Optimal band size of **7–8 hunters** is a smooth budget-constraint tangent (Fig. 7 indifference curve), **not** a threshold cliff or access gate.
- The −4% mean-yield cost and 83% risk-reduction are net effects of the full CCSP strategy (coordinated search + cooperative pursuit) relative to solitary IRM(depletion); the intermediate CUS step (group living, uncoordinated) itself drops yield further, and cooperative pursuit partially recovers it (+17% over CUS).
- No hard threshold or access-gate exists in the model. Group-size effects are smooth and monotonic in the relevant range.
- Recruitment distance Dmax ~200 m (2 cells); rarely larger.
- There is **no access gate** anywhere in the model — solo hunting works, just worse.
- Any concept-map text treating cooperative hunting as yield-superadditive is wrong.

**What was lifted:**
- Variance-reduction framing for cooperative hunting: mean yield is approximately flat (net −4%); the primary benefit is reduced harvest failure probability (83% fewer zero-return days).
- Solo-viable principle: cooperative hunting is always an option (not gated), but carries coordination cost vs. variance benefit.
- 7–8 hunter optimal band figure is a smooth indifference-curve tangent (Fig. 7), not a feasibility threshold.

**Provenance:** Full text read in chat session; tables and figures verified. `[VERIFIED]` authorised on this provenance.

---

### Janssen, M. A. & Hill, K. (2016). "An Agent-Based Model of Resource Distribution on Hunter-Gatherer Foraging Strategies: Clumped Habitats Favor Lower Mobility, but Result in Higher Foraging Returns." Chapter 3 in J.A. Barceló & F. Del Castillo (Eds.), *Simulating Prehistoric and Ancient Worlds* (Computational Social Sciences). Springer International Publishing, pp. 159–174. DOI 10.1007/978-3-319-31481-5_3. `[VERIFIED]`

**Full citation:** Marco A. Janssen & Kim Hill (2016). Chapter 3 in J.A. Barceló & F. Del Castillo (Eds.), *Simulating Prehistoric and Ancient Worlds*. Springer. pp. 159–174. DOI 10.1007/978-3-319-31481-5_3. CoMSES model codebase: 4538.

**Role:** Extension of J&H 2014 — landscape heterogeneity and clumpiness axes; targeted mobility benefit in patchy terrain. Terrain-generator relevance and candidate mechanism for C-agent advantage in clumped habitats.

**Design/scope:** Extends the Mbaracayu landscape along two axes: habitat clumpiness (three levels — 30%, 60% [original], 90% same-vegetation neighbour fraction) and between-habitat prey-density variation (Original vs High, ~10× difference between richest and poorest habitat, total biomass held constant). Six landscape types: O30, O60, O90, H30, H60, H90. 64,800 simulations total (100 runs × 108 camp-mobility configs × 6 landscapes). All runs use cooperative hunting with coordinated search. Camp mobility varies along: targeted vs random relocation, and adaptive (threshold-based) vs non-adaptive (fixed-interval) movement.

**Findings:**
- **Optimal group size robust at 7 hunters across all six landscapes** — unaffected by clumpiness or prey-variation manipulations; consistent with J&H 2014 (7–8 optimum).
- **Mobility largely stable under natural conditions:** moving camp every day remains optimal for O-series landscapes and low/medium clumpiness, matching Ache ethnographic observation. Only under H90 (high prey-variation + high clumpiness) does optimal mean camp-staying time rise to **2.1 days** (vs ~1 day baseline).
- **Headline result is targeted movement, not group size or raw mobility.** In clumped, heterogeneous landscapes (H60/H90), targeted camp relocation achieves **~30% higher return rates** than random relocation. Combining targeted movement + adaptive staying yields up to **35% higher mean daily return** in H90 vs O60 — despite identical total prey biomass.
- **Table 3.3 quantitative anchors:** O60 non-targeted/non-adaptive ≈ 2.835 kg/hunter/day, zero-meat fraction = 0.041. H90 targeted/adaptive = 3.836 kg/hunter/day, zero-meat = 0.026. H90 targeted/non-adaptive = 3.789, 0.032.
- **Targeting can be worse than random** in O30 (low between-habitat variation, dispersed): targeting only pays when habitats differ substantially AND are spatially clumped.
- **No cost-of-movement term** in model — hunters hunt en route regardless of strategy; return comparisons reflect foraging tradeoffs only, not travel cost.

**What was lifted:**
- Literature-grounded mechanism by which terrain/biome clumpiness → foraging-return differentials: payoff from spatial targeting scales with both clumpiness and between-habitat productivity variance.
- Candidate mechanism for C-agent advantage in clumped/patchy terrain (information-sharing supports targeted relocation), independent of the existing seasonal-shock resilience finding (H1(ii)).
- 7-hunter optimum confirmed landscape-invariant; group-size robustness is not a terrain artefact.

**Provenance:** Full text read in chat session (2026-06-11); findings extracted directly from source. `[VERIFIED]` authorised on this provenance.

---

### Forest–savanna mosaic / woody-cover coverage anchor. (Ecoregion + savanna-ecology literature; e.g. WWF forest–savanna mosaic ecoregions; savanna woody-cover definitions.) `[SECONDARY]`

**Role:** Terrain coverage target and biome-classifier grounding for the woody-cover ladder (Stage 7 terrain generator).

**What was lifted:**
- Savanna = wooded grassland on a continuous woody-cover axis; mosaic = savanna/woodland matrix + minority gallery/patch forest + grassland.
- Approximate canopy cover: savanna ~5–10% lower / ~25–30% upper; forest above.
- **Foragers span the full gradient** (closed-forest Aché through woodland-savanna Hadza) — do not force forest as a minority.

**Provenance:** Secondary/encyclopedic + ecology web sources. Tag `[SECONDARY]` — do **NOT** mark `[VERIFIED]` (no single primary full-text read). Flag for a future primary-source pass if a hard numeric cutoff is ever locked.

**What was rejected:**
- Specific canopy-cover percentages used as hard thresholds in the classifier — translated to dimensionless `W_FOREST=0.45 / W_SAV=0.18` on the `forestness` axis (locked in terrain blueprint §2.9); not a direct canopy-cover literal.
