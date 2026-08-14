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
- Per-capita CDH return rates by species available in Table 1 (e.g. elephant: 4,939 kcal/hr/capita). **Not the primary kcal/hr savanna anchor** — Hawkes et al. 1991 holds that role. Morin 2024 is used for cooperation mechanic parameterisation only (soft-gate sigmoid shape for group-size effect on savanna yield).

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

---

## Stage 1 — Survey A: Forage Return-Rate Sources (per-biome kcal/forager-hr)

> **Canonical-home note:** As of the 2026-06-12 reorg, LITERATURE.md is the bibliography of record for all Survey A forage sources. `SiC_Games_Forage_Return_Rate_Table.md` is a **derived view** — it carries the kcal/hr values inline for use, but the authoritative citation and source-location for each cell lives here. If a citation detail (page, table number) is corrected, correct it HERE first; the table follows.

---

### Hill, K., Hawkes, K., Hurtado, A.M., & Kaplan, H. (1987). "Foraging Decisions Among Ache Hunter-Gatherers: New Data and Implications for Optimal Foraging Models." *Ethology and Sociobiology*, 8, 1–36. `[VERIFIED]`

**Role:** Forest biome forage anchor (closed-canopy, Ache, Paraguay).

**Value lifted:** 2630 kcal/forager-hr (palm starch/fiber, women's potential rate). Cf. whole-diet aggregate 1339 (men) / 1221 (women).
**Source location:** Table 1 (whole-diet aggregate, p.9); palm-fiber comparison in "Nutrient Preferences" subsection, p.11 ("...1340 calories derived from meat... may be worth more than 2630 calories of palm products").

**What was rejected:** Whole-diet aggregate (1339/1221) as the forest cell value — rejected in favour of the activity-specific palm rate for consistency with the other activity-specific cells.

**Game role (Survey B, 2026-06-14):** Forest biome game anchor — post-encounter return rates by species, Table 2 [NATIVE]. Handling-only denominator (construct-seam exception: "Includes time spent in acquisition attempts plus all relevant processing" per Table 2 footnote a — search time excluded; all other game biomes are search-inclusive). energy_density = 1,460 kcal/kg from fn 3 (same constant as forage role above). Seven game species extracted from Table 2 (see `SiC_Games_Resource_Return_Rate_Table.md §3.3`). Dual-value entries: footnote d (white-lipped peccary — first value includes tracking time; second from point animal is heard/seen); footnote e (armadillo — first value = surface encounter; second = burrow excavation). Note: tapir mentioned in text as hunted but not in Table 2 (sample insufficient or excluded).

---

### Hurtado, A.M. & Hill, K. (1987). "Early Dry Season Subsistence Ecology of Cuiva (Hiwi) Foragers of Venezuela." *Human Ecology*, 15(2), 163–187. `[VERIFIED]`

**Role:** Grassland biome forage anchor (Cuiva/Hiwi, Venezuela).

**Value lifted:** 1125 kcal/forager-hr (root collecting, women). Cf. 3001 (hunting, men — *game, not forage*; excluded from forage field).
**Source location:** Table II ("The Sexual Division of Labor among the Cuiva"), p.178; rate stated in text p.179 ("women's returns per hour of root collecting were only 1125 calories per hour").

**What was rejected:** Men's hunting return (3001) — this is game, not forage; belongs to the game field (Stage 2), not the forage field.

**Game role (Survey B, 2026-06-14):** Grassland biome game anchor: **3,001 kcal/hr** (hunting, men; search-inclusive, whole-activity denominator). Source of edible_fraction = **0.50** (conservative/consumed fraction; used across all game biomes). High-amplitude seasonal anchor: ~90% of annual rain (~1,665 mm) in wet season (May–Nov); wet=lean (flood suppresses access); dry=game-fat via prey aggregation (caiman: 44→489 kg/km², ~11× wet→dry swing). Corroborated by Gurven & Hill 2009 at ~2,700 kcal/hr (see Survey B entry).

---

### Cunningham, A. [Harvard dissertation]. "Forager Habitat Quality: Quantifying Hunter-Gatherer Habitats, Past and Present." Harvard University. `[VERIFIED]`

**Role:** Wetland biome forage anchor (Okavango Delta "Wet" habitat).

**Value lifted:** 1428.3 kcal/forager-hr (mean), 558.7 (median), post-encounter.
**Source location:** Chapter 3, "Q1: Wet vs Dry Foraging" results, p.62–63; Figure 3.11 (box plot), Figure 3.12 (violin plot).

**Cross-ref (not a biome cell):** Okavango "Dry" habitat = 2956.6 mean / 2320.9 median (same source, same figures). Retained as a calibration cross-check only — riparian-adjacent dry ground, does not map to one of the six terrain biomes. See table §"Cross-reference."

---

### O'Connell, J.F. & Hawkes, K. (1984). "Food Choice and Foraging Sites among the Alyawara." *Journal of Anthropological Research*, 40(4), 504–535. `[VERIFIED]`

**Role:** Desert biome forage anchor (Alyawara, Australia) — supplies BOTH desert sub-type values.

**Values lifted:**
- Sandplain: ~3200 kcal/forager-hr (range 750–4500). Resources: Ipomoea roots, Solanum fruit, ripe Acacia seeds. Source: Results p.512, Figure 4.
- Mulga woodland: ~650 kcal/forager-hr (range 500–800). Resources: cossid larvae, lizards, Acacia seeds. Source: Results p.512, Figure 5.

**Open design decision (unresolved — Stage 1 pre-work):** 5× spread between sub-types within one biome. If the locked terrain generator emits desert as a single undifferentiated biome, the cell value must be chosen (recommended: mean ~1925, or dominant-sub-type pick). Tracked in table §"Open design decisions" #1.

---

### Rhode, D. & Rhode, J. (2015). "Energetic Return Rates from Limber Pine Seeds." *Journal of California and Great Basin Anthropology*, 35(2), 291–298. `[VERIFIED]`

**Role:** Mountain / alpine biome forage anchor (limber pine, *Pinus flexilis*, Great Basin).

**Value lifted:** 5387 kcal/forager-hr (unhulled seeds, kernel-only assimilated — the behaviorally rational strategy per source). Cf. 178 (hand-hulled kernels only — processing floor).
**Source location:** Results p.295–296; Table 5 ("Return Rate Estimates (kcal/hr.) for Selected Great Basin Resources"). Site: 2,978 m altitude, Nevada (38.45°N, 118.78°W).

**What was lifted / decided:** 5387 (unhulled) adopted as the mountain cell value — the source frames unhulled processing as behaviorally rational; a return-optimizing forager would not hand-hull to the 178 floor.
**What was rejected:** 178 (hand-hulled floor) — a worst-case processing artifact, not a realistic field rate; using it would understate mountain return ~30× and distort downstream resilience comparisons. Retained only as the documented processing floor. (Stage 1 pre-work decision #2, resolved.)

---

### Bird, D.W. (1997). "Behavioral Ecology and the Archaeological Consequences of Central Place Foraging among the Meriam." (Chapter 16). `[VERIFIED]`

**Role:** Intertidal / shore biome forage anchor (water-edge subtype; Meriam, Torres Strait Islands, Australia).

**Value lifted:** 1491.5 ± 173.2 kcal/forager-hr (overall mean, searching + handling). Individual high-rank resources up to 6858.9 (Hippopus) and 13064.8 (*Tridacna gigas*).
**Source location:** Chapter 16, "Observed prey choice" section; Figure 16.1. Reef-flat collecting, n=47 follows (overall); Tridacna n=4, Hippopus n=34.

**Open design decision (unresolved — Stage 1 pre-work):** Whether intertidal is in or out of Stage 1. At 1491.5 mean (up to 13064.8 top resource), it dominates every terrestrial cell and could swamp terrestrial spatial dynamics if the water-edge cell gets full draw. Tracked in table §"Open design decisions" #3. Also the proxy basis for shore-fishing (below).

---

### Hill, K., Hawkes, K., Hurtado, A.M., & Kaplan, H. (1984). "Seasonal variance in the diet of Ache hunter-gatherers in Eastern Paraguay." *Human Ecology*, 12(2), 101–135. DOI: 10.1007/BF01531269. `[VERIFIED]`

**Role:** Fish (shore subtype) — **negative result**. Companion paper to Hill 1987; cited within Hill 1987 as the source of resource-level caloric equivalents.

**What was lifted (negative finding):** Table II breaks Ache game/resource items down by species (opossum, peccaries, pacas, coatis) with no fish category. The only mention of fish in the paper is fish-poison used by *other* regional groups, not the Ache. Ache fish exploitation is caloric-insignificant; no source isolates a fish rate because fish was not a measured resource category for this population.

**Disposition:**
- **Shore fishing/gathering** → reduced-fraction proxy of the Intertidal/shore cell (Bird 1997) — same low-capital, individual activity class. No independent anchor needed.
- **Offshore/boat fishing** → deferred capital-gated higher tier; anchor TBD; requires a non-Ache population where riverine/lacustrine boat fishing is a major caloric contributor (e.g. Amazonian or Pacific Northwest maritime forager). Future-stage retrieval target. Sits on the existing water-edge cell — no new terrain biome class required.

---

### Berbesque, J.C. & Marlowe, F.W. (2009). "Sex Differences in Food Preferences of Hadza Hunter-Gatherers." *Evolutionary Psychology*, 7(4), 601–616. `[VERIFIED]`

**Role:** Savanna / dry-woodland biome forage anchor (Hadza, Tanzania) — **resolves the prior savanna aggregate-type exception**.

**Value lifted:** 257.7 kcal/forager-hr (female tuber digging, //ekwa-type — the defining savanna baseline foraging activity; overwhelmingly female, N=56 female vs 6 male forays, so the female rate *is* the activity rate).
**Source location:** Table 4 ("Hourly acquisition and percentage contribution to diet of Hadza men and women"), p.609.
**Full Table 4 row set (recorded for auditability):** honey 229.7(M)/94.3(F); baobab 81.3/125.5; meat 163.6/66.6; berry 65.8/224.7; tuber 40.3/257.7.

**What was lifted:** Single-activity tuber rate (257.7) as the savanna cell value — like-for-like with the other seven activity-specific cells (directly measured, kcal/hr). Replaces the prior whole-diet aggregate (Marlowe 2010, 343–795), which is retained only as a secondary cross-reference.

**What was rejected (anti-regression — do not re-propose):** A ~1000 kcal/hr honey figure (derived secondhand from a Crittenden 2009 citation, "≈3000 kcal per 3-hr trip") was REJECTED as the savanna anchor. (1) Data: Marlowe's directly-measured honey return is 229.7(M)/94.3(F), male SD 201.9 — the ~1000 figure was a peak-haul anecdote misread as a mean, 4–10× too high. (2) Role: honey is a high-variance bonus resource, not baseline forage — wrong category for a baseline cell regardless of magnitude. Honey parked for a future high-variance-bonus-resource stage.

**Provenance:** Full text read in chat session (2026-06-12); Table 4 values extracted directly. `[VERIFIED]` authorised on this provenance.

---

### Marlowe, F.W. & Berbesque, J.C. (2009). "Tubers as Fallback Foods and Their Impact on Hadza Hunter-Gatherers." *American Journal of Physical Anthropology*, 140, 751–758. DOI: 10.1002/ajpa.21040. `[VERIFIED]`

**Role:** Savanna cell — *role/floor-property* citation (pairs with Berbesque & Marlowe 2009 above, which supplies the coefficient).

**What was lifted:** Establishes tubers as the year-round, continuously-available fallback/floor food (the seasonal-floor property of the savanna forage field). Tubers are the least-preferred but most-continuously-available Hadza food; available year-round, vary more by region than season.

**What was NOT lifted (pairing rule):** This paper reports availability in **kilograms, not kcal/hr**, and explicitly states caloric values were still being analysed. Do **not** source the 257.7 coefficient to this paper — coefficient comes from Berbesque & Marlowe 2009 (*Evol. Psychol.*). This paper grounds the *role* only.

**Provenance:** Full text read in chat session (2026-06-12). `[VERIFIED]`.

---

### Marlowe, F.W., Berbesque, J.C., Wood, B., Crittenden, A., Porter, C., & Mabulla, A. (2014). "Honey, Hadza, hunter-gatherers, and human evolution." *Journal of Human Evolution* [2014, in press]. DOI: 10.1016/j.jhevol.2014.03.006. `[VERIFIED — FUTURE-STAGE, NOT SURVEY A]`

**Role:** Parked reference for a future high-variance-bonus-resource stage. **Not a Stage 1 forage-table source.**

**What it grounds (when that stage lands):** Definitive Hadza honey dataset — kg and kcal by bee species and sex; honey ≈14% of Hadza diet by kcal despite being ≈5% by weight; high-variance acquisition (male mean 1.033 kg/foray, SD high; female 0.732). Seven bee species (Table 2); ba'alako (*Apis mellifera*) the high-value stinging-bee honey in baobab trees.

**Why parked, not used now:** Honey is excluded from the Stage 1 savanna baseline cell (see Berbesque & Marlowe 2009 rejection note). This paper is the home for the honey mechanic if/when a bonus-resource stage is built.

**Provenance:** Full text read in chat session (2026-06-12). `[VERIFIED]`.

---

## Survey B: Game Return-Rate Sources (per-biome kcal/hr)

> **Canonical-home note (2026-06-14):** LITERATURE.md is the bibliography of record for all Survey B game sources. `SiC_Games_Resource_Return_Rate_Table.md` is the derived view — it carries the kcal/hr values inline for use, but authoritative citations and source locations live here. Correct citation details here first; the table follows.

---

### Hawkes, K., O'Connell, J.F., & Blurton Jones, N.G. (1991). "Hunting income patterns among the Hadza: big game, common goods, foraging goals and the evolution of the human diet." *Philosophical Transactions of the Royal Society B*, 334, 243–251. DOI: 10.1098/rstb.1991.0106.

**Role:** Savanna biome game anchor [CONVERTED]. Primary kcal/hr anchor for savanna cell.

**Values lifted (raw kg/hr, from Survey A session read):**
- Encounter/scavenge — all seasons: ~0.71 kg/hr
- Encounter — late dry season: ~0.45 kg/hr
- Intercept (night, at water blinds) — dry season only: ~1.02 kg/hr (~7.5 kg/hunter-night)

**Converted via formula (edible_fraction = 0.50, energy_density = 1,460 kcal/kg):**
- Encounter/scavenge, all seasons: **518 kcal/hr**
- Encounter, late dry: **329 kcal/hr**
- Intercept, dry season: **745 kcal/hr**

**Seasonal mechanism confirmed:** Intercept hunting practiced ONLY in late dry season (Aug–Oct) at shrinking water sources — second independent confirmation (cf. Hiwi caiman ~11× swing) of dry-season prey aggregation as the savanna game access mechanism. Wet-season encounter rate: 1 animal/37 hunter-days; late-dry encounter: 1/53 days, supplemented by high-yield intercept.

**What was rejected:** Big-game collective-action / PD-framing content — forward-relevant to Cred/pool layer, not folded into resource build at this stage.

---

### Gurven, M. & Hill, K. (2009). "Why Do Men Hunt? A Reevaluation of 'Man the Hunter' and the Sexual Division of Labor." *Current Anthropology*, 50(1), 51–74. DOI: 10.1086/596611.

**Role:** Grassland game corroboration only. Hiwi grassland hunting ~2,700 kcal/hr, consistent with Hurtado & Hill 1987 anchor (3,001 kcal/hr). Theory/review paper — no new energetics data; does not replace the primary anchor.

**Checked for wetland game kcal/hr: negative.** Does not supply time-denominated energetics data for wetland or aquatic prey. Does not anchor wetland.

**Citation tag:** [CORROBORATION — do not use as primary anchor; wetland negative]

---

### Bird, D.W., Bird, R.B., & Parker, C.H. (2009). "Martu hunting strategies and the evolution of human capacities for niche construction." *Journal of Human Evolution*, 57, 217–233. DOI: 10.1016/j.jhevol.2008.11.004.

**Role:** Desert biome game anchor [NATIVE]. Primary anchor for desert cell. Per-species post-encounter return rates from Table 1 entered directly without formula conversion.

**Values lifted (Table 1, search-inclusive denominator):**
- Species range: 641–1,761 kcal/hr (reflects prey composition — reptiles at low end, larger game at high end).
- Rates taken [NATIVE] — no formula conversion applied.

**Denominator:** Search-inclusive (time from departure to return, including travel and search). Consistent with all non-forest game biomes.

**What was rejected:** Formula re-conversion — rates are already reported in kcal/hr.

---

### Ugan, A. & Simms, S.R. (2012). "Prey Mobility, Prey Rank, and the Foraging Goals of Early Americans." *Journal of Ethnobiology*, 32(2), 163–181. DOI: 10.2993/0278-0771-32.2.163.

**Role:** Construct-reconciliation rule. Grounds the forage≠game distinction — mobile prey ranks differ from sedentary resource ranks because prey mobility and detectability factor into encounter rates independently of caloric yield. Anchors the biome-binning rule: why game peaks at savanna/edge rather than forest, despite forest having higher NPP (prey detectability-constrained in dense canopy, not energy-constrained).

**What was lifted:** Methodological principle only — encounter rate for mobile prey must be distinguished from handling-time return rate; the two denominators produce different biome rankings.

**What was rejected:** Specific numeric values — used as methodological anchor only, not as a caloric rate source for any biome cell.

---

### Bliege Bird, R., Smith, E.A., & Bird, D.W. (2001). "The hunting handicap: costly signaling in human foraging strategies." *Behavioral Ecology and Sociobiology*, 50, 9–19. DOI: 10.1007/s002650100338.

**Role:** Intertidal biome game anchor [NATIVE]. Gross pre-sharing turtle hunting return rate 4,653 ± 1,213 kcal/hr (hunting season, search-inclusive, Table 2).

**MANDATORY CAVEAT:** Cell value represents gross pre-sharing return rate only. Net hunter consumption is near zero — turtle meat is shared broadly in a costly-signaling context; hunting functions as reputation signal, not caloric acquisition. **Do not use as a functional forager net-yield figure for this biome without explicit justification.** If the model uses net yield, intertidal game is functionally ≈0.

**Values lifted:** 4,653 ± 1,213 kcal/hr (hunting season, Table 2, search-inclusive).

**What was rejected:** Net consumption rate — conceptually inappropriate given the costly-signaling context.

---

### Smith, E.A. & Bliege Bird, R. (2000). "Turtle hunting and tombstoning on Mer: These are the data." *Current Anthropology*, 41(4), 587–609. DOI: 10.1086/317987.

**Role:** Intertidal yield corroboration only. Confirms mean edible turtle yield ~50.1 kg per hunt. No hunt-time denominator reported — cannot compute an independent kcal/hr rate from this source alone. Superseded for rate purposes by Bliege Bird et al. 2001.

**Citation tag:** [CORROBORATION — rate superseded by Bliege Bird et al. 2001; mass cross-check only]

---

### Hill, K., Padwe, J., Bejyvagi, C., Bepurangi, A., Jakugi, F., Tykuarangi, R., & Tykuarangi, T. (1997). "Impact of hunting on large vertebrates in the Mbaracayu Reserve, Paraguay." *Conservation Biology*, 11(6), 1339–1353. DOI: 10.1046/j.1523-1739.1997.96048.x.

**Checked for wetland game kcal/hr: negative** — paper contains zero time-denominated energetics data. Caiman appears as trace Ache prey (5 individuals, 25 kg total over study period) with no time denominator; cannot yield a kcal/hr rate. Does not anchor wetland or any other biome.

**What was lifted:** Corroborates Ache forest prey composition (species lists); confirms caiman as low-frequency, low-mass Ache game item.

**Citation tag:** [CHECKED — negative for wetland kcal/hr; forest prey composition corroboration only]

---

### Redford, K.H. & Robinson, J.G. (1987). "The game of choice: Patterns of Indian and colonist hunting in the Neotropics." *American Anthropologist*, 89(3), 650–667. DOI: 10.1525/aa.1987.89.3.02a00070.

**Checked for wetland game kcal/hr: negative** — paper's primary metric is a dimensionless Harvest Rate (animals killed per consumer per year), not a time-denominated energetics figure. Capybara (*Hydrochaeris hydrochaeris*) harvest rate = 0.154 animals/consumer-year (range 0.013–0.580, n=5 studies); caiman appears in qualitative species rankings only. No kcal/hr data for any species. Cannot feed the return-rate conversion formula.

**Citation tag:** [CHECKED — negative for wetland kcal/hr; offtake index only, no energetics]

---

### De Vynck, J.C., Cowling, R.M., Potts, A.J., & Marean, C.W. (2016). "Seasonal availability of edible underground carbohydrates in South African fynbos." DOI: [confirm with PDF — South African Journal of Science or similar]. Read: Survey A session, pre-2026-06-14.

**Role:** Forage seasonality anchor for the phenomenological seasonal curve (fynbos/Cape Floristic Region shrubland biome, South Africa).

**Values lifted:**
- USO availability peaks in ~6-month window: July–December (southern hemisphere winter through early summer).
- Lean season: December–February (hot-dry austral summer — the 3 most stressful months).
- Amplitude: moderate (not the flat-forest extreme, not the high-llanos extreme). The fynbos biome sits in the middle of the empirical amplitude range.

**What was rejected:** DOI not confirmed from PDF (file not in project as of 2026-06-14). Entry relies on Survey A session read. DOI requires verification from the source PDF before use in any write-up.

---

### Tallavaara, M., Eronen, J.T. & Luoto, M. (2018). "Productivity, biodiversity, and pathogens influence the global hunter-gatherer population density." *PNAS* 115(6):1232–1237. Data/script: Zenodo record 1069787. **Data-analyses SI filed `literature/Tallavaara_Data_analyses.pdf` 2026-07-02; regression EXTRACTED.**

**What was lifted — the CC-1 NPP→density regression (§4.3.1; blueprint …_CC1_TallavaaraCapacity) — SI READ:** the actual fitted model is a **segmented (2-piece) linear regression of `ln(density)` on NPP** (`segmented` R pkg): **`ln(density) = −0.1352714 + 0.0028623·NPP − 0.0030745·(NPP−1371.664)₊`**, R²=0.45, n=298. **Breakpoint NPP = 1371.664 g/m²/yr** (SE 103; ≈ the provisional's 1360). Below it density rises steeply; above it the slope goes slightly NEGATIVE (0.0028623−0.0030745 = −0.0002 → the hump-shaped, pathogen-limited high-NPP decline). **Density units:** `densityC` in **#/100 km²** (Binford 2001 + Kelly 2013 combined HG data, subpop="n"), and since our cell = 100 km², **model density = persons/cell directly** (`E = density·burn`, NO ×100 — unlike the provisional's per-km²×100). **NPP** = Miami model (Lieth 1973): `npp = min(3000/(1+e^{1.315−0.119·T}), 3000·(1−e^{−0.000664·P}))` g/m²/yr — our `fields.npp_gm2` (= raw npp×3400) is on this g/m² scale (terrain median ~633, range ~228–1860). **Impact (verified):** the real curve gives **~57% of the provisional patch capacity** (provisional over-generous at low NPP where 97% of our cells sit) → CC-1 lowers eq_pop ~40%, a correctness improvement (Tallavaara ~0.05/km² at NPP 633 matches the ethnographic record). **Biodiversity + pathogen SEM terms NOT lifted** (the univariate NPP main effect is the CC-1 scope; biodiv/pathogen deferred to their own channels). **Validated against `Tallavaara_Dataset_4.xls`** (filed; the ethnographic response data — 357 HG groups, Binford+Kelly `densityC` in #/100 km²): observed density **min 0.2, median 11.9, max 494.9** — the extracted curve's output (2–44 over our NPP 228–1860) sits inside this range; observed median 11.9 ⇒ NPP≈913, so our terrain median (NPP 633 → 5.3) is at the arid-lower end of forager environments. **Status: EXTRACTED + validated — ready to implement.**
**Citation tag:** [MECHANISM — CC-1 NPP→density segmented regression (§4.3.1)]

**What was lifted:**
- **CC-1 capacity (NPP→density):** HG population density rises with net primary productivity; the low/high-productivity break is at **NPP = 1,360 g/m²/yr**. Basis for the provisional CC-1 cell-capacity field: density = min(0.5, 0.3·npp_gm2/1360) people/km².
- **Pathogen stress (demographic stage):** pathogen stress is a major driver that **lowers** HG density, **dominant in high-productivity regions (NPP > 1,360) and the tropics** (structural-equation model; biodiversity dominates in low-productivity regions). Anchors the terrain pathogen field (Demography blueprint §3.3) — penalty bites hardest in high-NPP cells. NOTE (red-team m-1): the SEM path is a *continuous* coefficient, not a step at 1360 — use a smooth NPP weighting, not a hard gate.

**To extract (Step-2 calibration):** standardized SEM coefficients for the pathogen-stress path (Zenodo 1069787) to set pathogen-field magnitude.

**Citation tag:** [USED — CC-1 NPP anchor; pathogen-field anchor]

---

### Guernier, V., Hochberg, M.E. & Guégan, J.-F. (2004). "Ecology Drives the Worldwide Distribution of Human Diseases." *PLoS Biology* 2(6):e141.

**What was lifted:** human pathogen species richness rises with **temperature and precipitation** (precipitation range the single best predictor) and falls with latitude. Justifies the terrain pathogen field's warmth + standing-water drivers (Demography blueprint §3.3).

**Citation tag:** [USED — pathogen-field climate driver]

---

### Dunn, F.L. (1968) "Epidemiological factors: Health and disease in hunter-gatherers" (in *Man the Hunter*); Houldcroft, C.J. & Underdown, S.J. (2023) "Infectious disease in the Pleistocene: Old friends or old foes?" *Am. J. Biol. Anthropol.* [Houldcroft & Underdown 2023 in lit folder; Dunn 1968 NOT filed — redundant with Houldcroft for our use]

**What was lifted:** the Paleolithic/HG disease-scape is **zoonotic / vector-borne / environmental, NOT crowd-epidemic** — crowd diseases (measles, influenza) need large host pools and post-date agriculture. Bounds the model's density-disease channel to *endemic/zoonotic* transmission rising modestly with aggregation, not epidemic crowd disease (Demography blueprint §3.2).

**Citation tag:** [USED — bounds density-disease channel]

---

### Gurven, M. & Kaplan, H. (2007). "Longevity Among Hunter-Gatherers: A Cross-Cultural Examination." *Population and Development Review* 33(2):321–365. DOI 10.1111/j.1728-4457.2007.00171.x. Open-access PDF: gurven.anth.ucsb.edu.

**Role:** the **M-1 anchor** for the demographic stage — published Siler competing-hazard fits per HG population. Siler form `h(x) = a1·exp(−b1·x) + a2 + a3·exp(b3·x)`; `a2` = age-independent (Makeham) "exogenous mortality due to environmental conditions" (the term the model's terrain/disease modulators act on).

**What was lifted — Aché forest-period coefficients (Table 2; both sexes; ANNUAL, x in years):**
- a1 = 0.157, b1 = 0.721, a2 = 0.013, a3 = 4.80×10⁻⁵, b3 = 0.103 (MRDT = ln2/b3 ≈ 6.7 yr).
- Realized: e₀ = 37, **e₁₅ = 38.5 remaining yr**, e₄₅ = 21.1, survival-to-15 = 0.66, survival 15→45 = 0.43, modal adult death = 71 (forest) / 78 (settled). Adult baseline ~1%/yr to age ~40, then Gompertz. Aché a1 ≈ half of other foragers (higher child survivorship).
- **DENOMINATOR NOTE (R-106, 2026-08-13) — "survival 15→45 = 0.43" is `l(45)` FROM BIRTH, not conditional on reaching 15.** Fed these exact coefficients, the model's `life_table()` returns `l(15) = 0.66` (matching to 2 dp) and a CONDITIONAL 15→45 of **0.65**; `0.66 × 0.65 = 0.43` recovers the published figure. Scoring the conditional against 0.43 would mark a correct schedule as wrong by ~50%. `life_table()` therefore returns `surv_to_45` and `surv_15_to_45_cond` as separately named fields — compare **`surv_to_45`** against this 0.43. Same failure class as the four earlier "right number, wrong denominator" retractions.
- Cross-HG: e₀ 21–37; modal adult death avg 72; adaptive lifespan 68–78.

**Use:** Siler coefficients FIXED as constants (M-1), converted per-month (÷12). G&K Table 2 is both-sexes; sex-specific + maternal-removed (M-3) fits to come from Hill & Hurtado.

**Provenance:** Table 2 extracted via pdfplumber word-coordinate reconstruction (table rendered RTL), cross-checked two ways AND **spot-checked against the filed `literature/` PDF 2026-06-18 — CONFIRMED** (a1=0.157, b1=0.721, a2=0.013, a3=4.80e-5, b3=0.103; e₀/e₁₅/e₄₅/mode reproduce the paper exactly via closed-form survivorship).

**Citation tag:** [USED — demographic Siler anchor (M-1); coefficients CONFIRMED vs filed PDF 2026-06-18]

---

### Howell, N. (2010 [1979]). *Demography of the Dobe !Kung*, 2nd ed. — and Blurton Jones, N. (2016). *Demography and Evolutionary Ecology of Hadza Hunter-Gatherers*, Cambridge Univ. Press.

**Role:** IBI/TFR **comparanda** — cross-checks, NOT anchors (Step-1 calibrates to the Aché). Values lifted:
- !Kung (Howell): inter-birth interval ≈ 44 mo; completed TFR ≈ 4.7.
- Hadza (Blurton Jones): IBI ≈ 38 mo; TFR ≈ 6.2.
- Aché (our anchor; Hill & Hurtado): IBI ≈ 37 mo; TFR ≈ 8.

Our Step-1 realized **IBI 37.0 / TFR 7.9** sits at the high-fertility (Aché) end of this HG range — as intended (we calibrate to the Aché, not the cross-HG mean).

**Citation tag:** [COMPARANDUM — IBI/TFR cross-check; books, may reside in the G: drive lit store rather than repo `literature/`]

---

### Hill, K., Hurtado, A.M. & Walker, R.S. (2007). "High adult mortality among Hiwi hunter-gatherers: Implications for human evolution." *J. Human Evolution* 52:443–454. FILED `literature/` 2026-06-19.

**What was lifted:** accidental death ≈ **10% of all deaths** across age groups (Hiwi accidental ~297/100k person-yr; ~1.1%/yr combat+homicide+accident pre-contact). Anchors the **terrain risk-scale** (Demography Step-2): the risk multiplier is calibrated so terrain accident-mortality ≈ 10% of baseline `a2` in average-risk terrain. See MODEL_SPEC §4.3.3.

**Citation tag:** [USED — terrain risk-scale anchor (Step-2)]

---

### Pelletier, D.L. (1994). "The Potentiating Effects of Malnutrition on Child Mortality: Epidemiologic Evidence and Policy Implications." *Nutrition Reviews* 52(12):409–415. (cf. Scrimshaw, Taylor & Gordon 1968.)

**What was lifted:** malnutrition **multiplicatively** (not additively) potentiates infectious mortality; mild-to-moderate malnutrition ≈ 2× mortality risk, severe higher. Anchors the **nutrition×disease synergy `μ_max ≈ 2–3`** (Demography Step-2; MODEL_SPEC §4.3.3).

**Status:** **NOT yet in `literature/`** (paywalled — supervisor to fetch). `μ_max` PROVISIONAL pending the filed paper + the RR-by-severity table; the RR is child-mortality data extrapolated to adult reserve depletion.

**Citation tag:** [USED — nutrition-synergy μ_max anchor (Step-2); PROVISIONAL, source not yet filed]

---

### Pontzer, H., Raichlen, D.A., Wood, B.M., et al. (2012). "Hunter-Gatherer Energetics and Human Obesity." *PLoS ONE* 7(7):e40503. DOI 10.1371/journal.pone.0040503. FILED `literature/` 2026-06-19 (open access).

**What was lifted — per-class body composition (Hadza; MR-1 / Resource-Ecology Phase B):** body fat by sex — **women 24.2 ± 5.8%**, **men 8.6 ± 3.8%** (mean ± SD); child fat ~similar to age 10 then rises for females. Anchors the per-agent `reserve_full ~ N(sex × age)`: women carry far more *absolute* fat (the reproductive buffer). Provisional kcal stores (fat × 9 kcal/g; assumed body weights ♀~50 kg, ♂~55 kg): **female adult ~109k ± 26k**, **male adult ~43k ± 19k** (note: men's is *below* the current 100k global constant); child low (~scale by body mass); senior declining. [Body weights assumed — refine from Hadza/Aché anthropometry.] See MODEL_SPEC §4.3.3.

**Citation tag:** [USED — per-class reserve anchor (Resource-Ecology Phase B / MR-1)]

---

### Cashdan, E. (2014). "Biogeography of Human Infectious Diseases: A Global Historical Analysis." *PLoS ONE* 9(10):e106752. DOI 10.1371/journal.pone.0106752. FILED `literature/` 2026-06-20 (open access).

**What was lifted — pathogen-prevalence-by-climate anchor (Biome-Mortality / pathogen channel, §4.6.3):** a **pathogen *prevalence* index** (10 pathogens, ordinal 1–4 = absent→epidemic) across **SCCS societies** (Standard Cross-Cultural Sample — includes foragers / traditional pre-modern-medicine societies), OLS-modelled on mean annual temperature, # frost-free months, temperature extremes, precipitation, habitat diversity, population density (adj. R²≈0.48). **Shape:** prevalence ↑ with temperature + frost-free climate + seasonal-dry-extremes; predictors **switch by latitude** (high-lat temperature-driven, low-lat precipitation-driven, precip. peaking at intermediate rainfall). Standardized β coefficients reported (magnitude; precise extraction deferred to the channel wire). Maps onto terrain temperature + humidity (CL-1) + NPP. The **prevalence**-not-richness metric makes prevalence→mortality a small, bracketable leap. Replaces the non-extractable Tallavaara/Guernier richness path.

**Citation tag:** [USED — pathogen channel direction+shape+magnitude (Biome-Mortality §4.6.3)]

---

### Dunn, R.R., Davies, T.J., Harris, N.C., Gavin, M.C. (2010). "Global drivers of human pathogen richness and prevalence." *Proc. R. Soc. B* 277(1694):2587–2595. DOI 10.1098/rspb.2010.0340. FILED `literature/` 2026-06-20 (Europe PMC GREEN OA: PMC2982038).

**What was lifted — corroborating pathogen-richness drivers (Biome-Mortality §4.6.3):** pathogen *richness* GLM **pseudo-r²=0.82**, most variation explained by **reservoir-host (bird + mammal) species diversity** plus temperature / precipitation / actual evapotranspiration (AET). Supports the Holocene-stability case (environmental/host-driven pathogen distribution) and the warm/wet/productive → higher-pathogen direction. Secondary to Cashdan (richness, not prevalence).

**Citation tag:** [USED — pathogen channel corroboration (Biome-Mortality §4.6.3)]

---

## Climate / orbital-lottery anchors (Climate stage C.1–C.3, MODEL_SPEC §4.1.9, added 2026-06-24)

These ground the per-world climate lottery in `climate.py`. PDFs are astronomy/paleoclimate references not
filed locally (PDFs gitignored); each is anchored to the specific number lifted.

### Spiegel, D.S., Menou, K., Scharf, C.A. (2009). "Habitable Climates: The Influence of Obliquity." *ApJ* 691:596. & Spiegel, D.S., Raymond, S.N., Dressing, C.D., et al. (2010). "Generalized Milankovitch Cycles and Long-Term Climatic Habitability." *ApJ* 721:1308.
**What was lifted — obliquity & eccentricity bounds (C.1/C.2):** a BROAD habitable obliquity band (no clean monotone obliquity→snowball threshold) → uniform ε∈[0°,60°] draw; eccentricity habitability marginal above e≈0.6 (snowball risk 0.4<e<0.6) → uniform e∈[0,0.6]; and the **annual-mean flux brightening `(1−e²)^(−½)`** used as `mean_factor`. **Rejected:** any per-step Milankovitch insolation integration — we BOUND draws only.
**Citation tag:** [USED — obliquity & eccentricity draw bounds + (1−e²)^−½ brightening (§4.1.9 C.1/C.2)]

### Williams, D.M. & Kasting, J.F. (1997). "Habitable Planets with High Obliquities." *Icarus* 129:254–267.
**What was lifted — obliquity→insolation-contrast intuition (C.1):** at high obliquity the pole receives more annual insolation than the equator (contrast crosses ≈54°); motivates the monotone `sin ε/sin 23.4°` scaling of the empirical Earth seasonal amplitude. **Rejected:** the literal pole>equator transfer as a food signal — forage amplitude is rain/phenology-driven (Q1-B keeps it a provisional bounding heuristic).
**Citation tag:** [USED — obliquity→amplitude scaling rationale (§4.1.9 C.1)]

### Kopparapu, R.K., Ramirez, R., Kasting, J.F., et al. (2013). "Habitable Zones around Main-Sequence Stars: New Estimates." *ApJ* 765:131.
**What was lifted — stellar-flux HZ edges (C.2):** conservative HZ flux range ≈ [0.34, 1.05] S⊕ (max-greenhouse outer edge → moist/runaway inner edge) → uniform S draw; `T(S)=14+255·(S^¼−1)` °C uses Stefan-Boltzmann `T_eff∝S^¼` anchored S=1→14 °C via a fixed effective-greenhouse offset. **Rejected:** a full radiative-convective climate model — T̄ is a dormant world property (nothing reads it yet).
**Citation tag:** [USED — stellar-flux draw bounds + S→T̄ map (§4.1.9 C.2)]

### Timmermann, A., An, S.-I., Kug, J.-S., et al. (2018). "El Niño–Southern Oscillation complexity." *Nature* 559:535–545.
**What was lifted — interannual (ENSO) layer (C.2):** the **PERIOD only**. `interannual_period` ∈ [2, 7] yr is the **union of the paper's two observed modes**, not a range it prints: EOF1 (classical EP El Niño) has "quasi-quadrennial timescales (3-7 years)", EOF2 (zonal dipole, 25% of EOF1's variance) has "quasi-biennial and decadal timescales", and the coupled-eigenmode section pins the pair at "timescales of approximately four and two years, respectively". So 7 yr is EOF1's ceiling and 2 yr is EOF2's floor. `[SYNTHESIS]` — both quotations verified against the PDF 2026-08-06.
**RETRACTED 2026-08-06 (Addendum 29) — the amplitude was never in this paper.** This entry previously read "±20–40% CC swing in marginal biomes → `interannual_amp`". Timmermann 2018 is an **SST-dynamics review**: it discusses ENSO amplitude only qualitatively (skewness, "a wide range of amplitudes" in palaeo-reconstructions) and states **no production or carrying-capacity amplitude anywhere**. `ENSO_AMP_MIN/MAX = 0.20/0.40` is therefore a **modelling judgement**, now tagged `[INTERPRETIVE]` in `climate.py` — the same treatment its sibling `REGIME_AMP` (Wanner) has always carried. It is **bounded**, not anchored: Sarmiento 2004 measures −37…−56% ANPP in an *exceptional* flood year, and an ordinary interannual excursion must be milder, so [0.20, 0.40] below [0.37, 0.56] is coherent. Found by `tools/verify_anchor.py`; it was believed because the code comment was trusted instead of the paper (the Bar-Yosef pattern, MECHANISM_CHARTER P1).
**Rejected:** stochastic/irregular ENSO realism — a single drawn period is used (refinement deferred).
**Citation tag:** [USED — interannual ENSO **period only** (§4.1.9 C.2); the amplitude is NOT from this source]

### Wanner, H., Beer, J., Bütikofer, J., et al. (2008). "Mid- to Late Holocene climate change: an overview." *Quaternary Science Reviews* 27:1791–1828.
**What was lifted — regime-shift amplitude (C.3):** Little Ice Age global-mean cooling ~0.5 °C (p.1793) → an *interpretive* central ±10–15% CC depression (`regime_amp∈[0.10,0.15]`); LIA excursion duration ≈ 500 yr → `regime_duration` upper bound. **Rejected:** °C→CC% as a calibrated transfer (no NPP transfer fn — flagged interpretive); the ±30% / ~1 °C tail is RESERVED for explicitly-flagged 8.2-kyr/YD catastrophe events (C.4), not the routine lottery.
**Citation tag:** [USED — regime amplitude + excursion duration (§4.1.9 C.3)]

### Mayewski, P.A., Rohling, E.E., Stager, J.C., et al. (2004). "Holocene climate variability." *Quaternary Research* 62:243–255. & Bond, G., Kromer, B., Beer, J., et al. (2001). *Science* 294:2130.
**What was lifted — regime-shift recurrence (C.3):** Holocene Rapid Climate Change events recur on ~1500 / ~2000–2800 yr pacing (Bond ~1500 yr) → `regime_recurrence∈[1000,2000]` yr. The two-state Markov **telegraph** dwell/recurrence split (DURATION ≠ RECURRENCE) is anchored here. **Rejected:** glacial-cycle (10⁴–10⁵ yr) timescales — out of scope; an OU/mean-reverting process (v2 red-team: these are sustained regime shifts, not wiggles).
**Citation tag:** [USED — regime recurrence + step-process justification (§4.1.9 C.3)]

### St. John, Jack R. (2022). "Understanding Caribou Population Cycles." **UNDERGRADUATE thesis**, University of Montana (ScholarWorks: *Undergraduate Theses, Professional Papers, and Capstone Artifacts*). & Vors, L.S. & Boyce, M.S. (2009). "Global declines of caribou and reindeer." *Global Change Biology* 15:2626–2633.
**STATUS `[VERIFIED, PDF READ]` — filed by the supervisor and read 2026-08-06 (Addendum 32).** It was `[UNSOURCED]` for one morning. Reading it produced **four corrections**, only one of which was a confirmation:

1. **AMPLITUDE CONFIRMED.** *"the amplitude, standardized about the mean population size, was .871"* — and Figure 10 gives the full distribution: **Min=.406, Q1=.700, Median=.871, Q3=1.126, Max=1.570**. Our 0.871 is the MEDIAN of a wide spread, not a constant.
2. **PERIOD BAND FALSIFIED.** We carried **40–90 yr**, credited to Bergerud. Figure 9: **Min=23, Q1=33, Median=40.5, Q3=50, Max=67**, and **Bergerud is not cited anywhere in the thesis** (zero occurrences). The old band excluded everything below the median and ran 23 years past the longest cycle ever measured, so nearly every drawn world got a period longer than the median herd. **Corrected to 23–67.**
3. **"43-herd database" OVERSTATED.** 43 herds were collected; *"of the 43 herds, I only 19 were deemed cyclic via periodogram analysis."* **Both distributions are over 19 herds, and 56% of the database is NOT cyclic** — a fact that matters for a model applying a cycle to all steppe.
4. **IT IS AN UNDERGRADUATE THESIS, not the M.Sc. this entry claimed.** Not peer-reviewed. It is now the weakest anchor in the climate layer and the first that should be replaced if a published herd-cycle source is found.

**⚠ HAZARD THE DISTRIBUTION EXPOSES.** `_caribou_factor` is peak-pinned `(1 + a·cos)/(1 + a)`, whose trough `(1−a)/(1+a)` goes **NEGATIVE for a > 1**. The thesis's Q3 (1.126) and Max (1.570) are both above 1, so **half the observed herds sit above the value at which our form breaks.** Pinning the median is safe; a per-world draw from this distribution must clamp at a ≤ 1. Constructed as a test (`test_climate_health_ctb.py`) so the clamp is a known requirement, not a later bug report.

**Vors & Boyce 2009 remains ABSENT and is corroboration only** — a ~57% secular decline, not a cycle amplitude. Usher 2022 (which we do hold) stays rejected for this purpose: a human-famine figure, not a herd cycle.

**What was lifted — caribou herd-swing magnitude + period (C.4b, wired 2026-08-04, ON since 2026-08-06):** St. John assembled the largest caribou population database (**43 herds collected, 19 cyclic**) and found migratory-tundra population cycles with **median period 40.5 yr (observed range 23–67 yr — NOT the 40–90 this entry carried until the thesis was read)** and **amplitude 0.871 standardized about the mean** ⇒ peak ≈1.87× / trough ≈0.13× mean → a **~93% peak-to-trough (~87%-about-mean) drawdown**. ~~Bergerud established the 40–90 yr quasi-cycle (predator/forage-driven).~~ **RETRACTED 2026-08-06:** Bergerud is not cited in the thesis at all, and no Bergerud work was ever identified or filed. The 40–90 band had no source. Vors & Boyce 2009 corroborate a **~57% decline from max** across 58 circumpolar herds (modern, anthropogenically confounded → corroboration only, not the cycle anchor). **How used:** a 23–67 yr quasi-periodic DEPRESSION on `GRASS_STEPPE` **game** (the high-mobility migratory biome), peak-pinned. **Rejected:** Usher's 50–66% human-famine figure as the herd input (category error, v2 red-team); Vors & Boyce as the *cycle* amplitude (it's a secular decline).
**Citation tag:** [USED — caribou quasi-cycle period+amplitude (§4.1.9 C.4b, WIRED to GRASS_STEPPE meat)]

### Hamilton, S.K., Sippel, S.J., Melack, J.M. (2004). "Seasonal inundation patterns in two large savanna floodplains of South America: the Llanos de Moxos (Bolivia) and the Llanos del Orinoco (Venezuela and Colombia)." *Hydrological Processes* 18:2103–2116.
**What was lifted — llanos flood extremes (C.4c, NOT yet wired):** Llanos del Orinoco total inundated area ranges **1,278 – 105,454 km² (median 25,374)** — min ≈5% of median, max ≈4.2× median; wet-vs-dry water level swings up to ~15 m. **How used:** the *normal* seasonal flood is already Layer-1 (A_seas=0.60 llanos); the **extremes** (failed-flood drought year / over-flood year) are the catastrophe — modeled as the heavy TAIL of the Layer-2 interannual depression on `GRASS_LLANOS` forage (folds into Layer-2 per the v2 anti-double-count discipline, not a parallel Poisson). **Rejected:** the 15 m / 1278–105454 swing as a *catastrophe* (that span is the normal seasonal cycle — only its interannual tail is the shock).
**Citation tag:** [USED — llanos flood interannual-tail extremes / inundation range (§4.1.9 C.4c, WIRED two-sided to GRASS_LLANOS forage)]

### Castello, L., Isaac, V.J., Thapa, R. (2015). "Flood pulse effects on multispecies fishery yields in the Lower Amazon." *Royal Society Open Science* 2:150299. (PMC4680609, open access.)
**What was lifted — llanos flood AMPLITUDE lower bound + the two-sided basis (C.4c):** in this river-floodplain fishery, high/low water indices explain **~18%** of yield variance (effort ~62%); a 100% change in the water index moves single-species yields by **−15.6% to −20.2%** at the strong end (median effects −7.4% low-water / +4.1% high-water); 2–3 yr lag. **Crucially: "high and low waters exerted EQUAL forcing on yields"** — the empirical basis for modeling the llanos interannual as a **two-sided** `1−amp·|sin θ|` depression. **How used:** the ~15–20% per-extreme swing sets the **lower bound (0.15)** of the per-world `LLANOS_FLOOD_AMP` draw (a moderate extreme year, protein channel). **Rejected:** the effort-driven 62% (anthropogenic, not climate).
**Citation tag:** [USED — llanos flood amp lower bound + two-sided forcing (§4.1.9 C.4c)]

### Sarmiento, G., Pinillos, M., Pereira da Silva, M., Acevedo, D. (2004). "Effects of soil water regime and grazing on vegetation diversity and production in a hyperseasonal savanna in the Apure Llanos, Venezuela." *Journal of Tropical Ecology* 20:209–220. FILED `literature/` 2026-06-25.
**What was lifted — llanos flood AMPLITUDE upper bound, MEASURED (C.4c):** above-ground biomass measured monthly over two growth cycles in the actual Apure llanos. **1996 was an exceptional-flood year** (a dyke breach upstream put the savanna under a 50 cm water sheet Jul–Sep, ~3 mo; rainfall +350 mm above mean); **1997 was a normal year** (−100 mm). **TotalANPP (g m⁻², ungrazed natural plots): 1996 flood 265–418 vs 1997 normal 601–659** (range = three estimation methods) → an exceptional-flood-year above-ground production reduction of **−37 to −56%, central ~45%**. The abstract's **"both drought and water excess limit plant production, even more during wet years"** confirms the **two-sided** form holds for the plant/forage channel (the flood side is the more severe). **How used:** the measured flood-year production drop directly anchors the **upper bound (0.45)** of the per-world `LLANOS_FLOOD_AMP` draw — replacing the earlier interpretive km²→kcal estimate. **Rejected:** the grazed-plot values (livestock confound, though at this low stocking rate the difference was small); standing-biomass-at-a-date (confounded by phenology) in favour of TotalANPP.
**Citation tag:** [USED — llanos flood amp upper bound (MEASURED) + plant-channel two-sidedness (§4.1.9 C.4c)]

### Welcomme, R.L. (1979). *Fisheries Ecology of Floodplain Rivers.* Longman.
**What was lifted — corroborating llanos flood-pulse productivity (C.4c):** the **flood-pulse advantage** — floodplain fish yield scales with flood extent (~50 kg/ha flooded; failed-flood ⇒ large aquatic-protein loss). Corroborates the aquatic-protein side of the llanos flood shock (secondary to Sarmiento's direct plant-production measurement).
**Citation tag:** [USED — llanos flood aquatic-channel corroboration (§4.1.9 C.4c)]

### Binford, L.R. (2001). *Constructing Frames of Reference.* UC Press. & Testart, A. (1982). "The Significance of Food Storage Among Hunter-Gatherers." *Current Anthropology* 23(5):523–537. & Woodburn, J. (1982). "Egalitarian Societies." *Man* 17:431–451.
**What was lifted — the storage / delayed-return mechanic (§4.5.11; the morph trigger's first piece):** **Binford 2001** — storage is obligatory below **Effective Temperature ET = 15.25 °C** (an "overwintering tactic"; foragers take bulk in the productive months, live off stores in winter); plant-dependence threshold ET 12.75 °C; **packing threshold 9.1 persons/100 km² = our `BINFORD_PACKING_PER_KM2 = 0.091`** (cross-check ✓); `QSTOR` (quantity stored) is the environment-resolved measure (exact % in the print volume, not web-accessible → `storable_fraction=0.5` provisional). **Testart 1982** — food storage is the **prime mover**: seasonal/storable resources (salmon, acorns) → storage → sedentism + high density + social inequality. **Woodburn 1982** — immediate-return (no storage; sharing, equal access; *our four tropical calibration foragers*) vs delayed-return (storage → differential accumulation → breakdown of egalitarianism → complex HG). **How used:** storage enabled only in the overwintering zone (cell temp ≤ 15.25 °C, mapped onto the C.4a temperature field); glut banks overflow, winter draws it → the gate showed storage **doubles harsh-winter carrying capacity (188→380)**. **Rejected:** density-alone as the prime mover (it's storage/ET-gated, with density downstream); a personal sedentism *trait* (sedentism is emergent density+storage, not an individual disposition). **Deferred:** proto-ag yields (post-morph consequence, PA-1).
**Citation tag:** [USED — storage threshold (ET 15.25) + storable fraction + immediate/delayed-return (§4.5.11)]

### Water→aggregation / intercept-hunting survey (Climate C.5, MODEL_SPEC §4.1.9): Hawkes 1991 (Hadza); Pumé/Hiwi mobility; Binford continuum.
**What was lifted — the C.5 intercept-hunting anchor + the scoping that shaped it (web survey 2026-06-25, no new PDFs):** **(1) The boost magnitude (the build anchor)** — Hadza **intercept hunting** at night water-blinds returns **~745 kcal/hr** vs **~518 kcal/hr** encounter hunting (Hawkes et al. 1991, already in §4.1.5 / the game return-rate table) → `INTERCEPT_BOOST = 745/518 − 1 ≈ +44%`, applied as a late-dry-season meat boost at water. **(2) Threshold timing** — intercept hunting is practised **ONLY in the late dry season (Aug–Oct)** (§4.1.5), as shrinking water funnels game to permanent holes → modelled as a dryness threshold, not a continuous modifier. **(3) Corroboration that game concentrates at dry-season water** — Hiwi caiman **44→489 kg/km² (~11×)** (Hurtado & Hill 1987); savanna "dry-season shuffle" refugia; Ruaha ungulates crowd to surface water; Savanna Pumé/Hiwi move **5–6×/yr** to dry-season camps **sited at streams/lagoons**. **(4) The ALWAYS-ON baseline is already modelled** — `wateracc` is 55% of the terrain moisture term → NPP → forage+game (terrain.py:529), so "good hunting near water" exists year-round WITHOUT a climate layer; C.5 adds only the seasonal *peak*. **Survey verdict:** the *aggregation/intercept* phenomenon is well-anchored (→ built); the richer *logistical herd-following migration* is thin/under-documented (as §4.1.5/§4.1.8 flagged) → stays deferred to the open-biome stage. **Rejected:** modelling aggregation as a mean-conserved *redistribution cost* (wrong sign — intercept hunting is an adaptive BENEFIT); a continuous (non-threshold) seasonal modifier (§4.1.5 says threshold-like). Distance-scale note: daily foraging radius ~5–10 km (Western Mono) is sub-cell at 10 km/cell, so water proximity is the per-cell `wateracc` weight.
**Citation tag:** [USED — C.5 intercept-hunting boost magnitude/threshold (§4.1.9); always-on-baseline + Option-1-vs-2 scoping]

### Usher, P.J. (2022). "Caribou Crisis or Administrative Crisis? …" *(filed `literature/`.)*
**What was lifted — a CONFOUND CAVEAT (C.4 prep, NOT yet wired):** the 50–66% mid-20thC caribou-dependent *human* famine mortality is a downstream, COLONIALLY-CONFOUNDED outcome (administrative/policy failure), NOT a clean herd-crash magnitude. **How used:** when C.4 drives the field with a caribou shock, use the HERD swing (Bergerud/Zalatan ~5–10×, ~80% — to be filed) as the resource forcing; the human famine figure is an OUTCOME, not the input. **Rejected:** using 50–66% as the herd-crash amplitude (category error caught in v2 red-team).
**Citation tag:** [REFERENCE — caribou-crisis confound caveat (C.4 catastrophe prep)]

## Emergent-bands & social-structure anchors (Emergent Bands E.1–F.2 + E.3-proper, MODEL_SPEC §4.8; added 2026-06-29)

### Wobst, H.M. (1974). "Boundary Conditions for Paleolithic Social Systems: A Simulation Approach." *American Antiquity* 39(2):147–178.
**What was lifted — the minimum-viable band/connubium size (E.2 mating-access drive, §4.8.1):** a mating network ("connubium") must contain enough age-/sex-appropriate mates to avoid stochastic mate failure — the classic "magic numbers" of band society. **How used:** sets the E.2 `group_mate_min ≈ 25` target — a band below it is penalized in the movement utility (being a loner is mating-costly), so bands self-organize around the minimum-viable size rather than an imposed N. Also motivates the F.1/F.2 mate-gate (reproduction REQUIRES a co-resident band mate).
**[CORRECTION 2026-07-13 — the connubium number, verified against the primary lit]:** Wobst's **Minimum Equilibrium Size (MES)** = "the mean/median number of persons living in the intervening distance between two marriage partners." His 40 simulation runs (groups of 25, hex grid, 400 yr) returned **MES = 79–332** — the commonly-cited **175–475 is an *extrapolation*** to 1–2 hexagonal-cell tiers, NOT the direct result. CRUCIALLY the MES **depends on spatial arrangement + population density** (it is a mate-search *reach*, and it SHRINKS as residential units aggregate — a large village already contains the pool). The spatial-*independent* demographic floor is much smaller — see White 2017 MVP ~150. **Implication for our model:** the connubium target is the **~150 demographic floor** (with the *reach* left to emerge density-dependently via the Cut-2 ring-search), NOT a fixed ~475. The earlier `mate_search_min_eligible` calibration to reach ~475 (m*=50) anchored to the contested max-dispersal extrapolation and over-scattered the population (RESULTS R-67); re-anchored to MVP (m*≈15). The 500 is Birdsell's separate, contested "dialectal tribe," not Wobst's MES. **Source locations:** Wobst 1974 pp.152–169 (MES definition + simulation); White 2017 JASSS 20(4):9.
**Citation tag:** [USED — E.2 minimum band size (§4.8.1); F.1/F.2 mate-gate. Connubium-size anchor CORRECTED 2026-07-13 → MVP ~150 / MES-emergent, not 475]

### White, A.A. (2017). "A Model-Based Analysis of the Minimum Size of Demographically-Viable Hunter-Gatherer Populations." *JASSS* 20(4):9. (Open access, jasss.org/20/4/9.html.)
**What was lifted — the spatial-INDEPENDENT breeding-pool floor (connubium re-anchor, §4.8.1; RESULTS R-67):** a non-spatial ABM (geography deliberately removed → pure demographic viability) puts the **minimum viable population (MVP) at ~150** typically, ranging **40–150 by marriage rule**: most permissive (polygyny, no incest taboo) → 40; most restrictive (monogamy + incest taboo + marriage divisions) → 140. **How used:** the correct anchor for the connubium's DEMOGRAPHIC target (vs Wobst's density-dependent MES *reach*). Our config (monogamy + modest polygyny + patriclan exogamy) is at the restrictive end → **~140–150** → `mate_search_min_eligible` m*≈15 (a ~150-person breeding pool contains ~15 eligible males at φ≈0.1). Lets the spatial reach EMERGE (small in villages, wide in dispersed bands) rather than pinning it at the contested 475. **Note:** the paper does NOT model how sedentism/aggregation alters MVP — that coupling (villages localise mating) is our own mechanism, motivated by Wobst's density-dependence.
**Citation tag:** [USED — MVP ~150 demographic floor = the connubium re-anchor (§4.8.1; R-67)]

### Hamilton, W.D. (1971). "Geometry for the Selfish Herd." *Journal of Theoretical Biology* 31(2):295–311.
**What was lifted — risk-dilution / safety-in-numbers (E.1 safety drive, §4.8.1; F.2-mortality prep):** aggregation lowers an individual's predation/exposure risk (each animal reduces its "domain of danger" by clustering) — the canonical selfish-herd argument for grouping. **How used:** the E.1 movement multiplier `ypc ×= 1 + s_max·(1 − e^{−g/g_s})` — a saturating per-capita safety benefit of band size `g`, traded against the falling per-capita yield so an optimal band size emerges. F.2 tested wiring the same dilution into the *mortality schedule* (`enable_band_risk`) but SHELVED it (§4.8.6): a loner-mortality penalty culls rather than aggregates → a death spiral, not an optimum. Risk-dilution belongs in MOVEMENT (E.1); banding's fitness teeth are the F.1 mate-gate.
**Citation tag:** [USED — E.1 grouping safety drive (§4.8.1). The F.2 risk-dilution-as-mortality variant was tested & SHELVED (§4.8.6).]

### von Rueden, C.R. & Jaeggi, A.V. (2016). "Men's status and reproductive success in 33 nonindustrial societies: Effects of subsistence, marriage system, and reproductive ecology." *PNAS* 113(39):10824–10829. (PDF filed `literature/`.)
**What was lifted — the status→reproductive-success calibration target (§4.5.7, §4.8.5):** male status→RS meta-analytic **r ≈ 0.19** (288 associations, 46 studies, 33 societies; modest in humans vs r≈0.80 in nonhuman primates; ~equal across formidability/hunting/wealth/influence). **MARRIAGE-SYSTEM breakdown (PDF read, decisive for the F.3 full stack):** status→RS works through the **MATING/FERTILITY channel, not offspring survival**; it is marriage-system specific — status↔**wife quality** *only in MONOGAMOUS* societies (r≈0.15), status↔offspring-mortality *only in POLYGYNOUS* societies (r≈−0.08), and **polygyny is the main amplifier** (more mates → more children). **How used:** the calibration target for `mate_choice_strength` m — corr(prowess, surviving offspring | male) tuned to ≈0.19. **IFD substrate: m≈4** (R-19); **banded substrate: m≈5** (R-21, §4.8.5). **FULL-STACK consequence + RESOLUTION (run_3m, §4.8.12):** under the family stack the skew first collapsed to ~0 (two bugs: prowess prod-credit diluted by dependent sons, + too-fast prowess EMA). After fixing both (adult-producer credit; `prowess_decay` 0.10→0.05 = a persistent reputation, Smith 2004), the **realistic forager config (families + modest polygyny) lands status→RS ≈ 0.13** — which is the **marriage-system-appropriate value**: this paper's own breakdown puts MONOGAMOUS societies at r≈0.15 (wife-quality) and the 0.19 is the polygyny-inflated CROSS-system average. So the monogamy-dominant family model SHOULD sit ≈0.13–0.15, not 0.19; the earlier E.3 "0.19" was the idealised per-conception LOTTERY (any high-prowess male fathers any birth = polygyny-like). The skew is polygyny-carried here (strict monogamy ≈+0.03 — the model lacks the status→partner-fertility "wife-quality" channel, a noted future enrichment).
**Citation tag:** [USED — status→RS r≈0.19 calibration (§4.5.7 R-19 IFD m≈4; §4.8.5 R-21 banded m≈5)]

### Smith, E.A. (2004). "Why do good hunters have higher reproductive success?" *Human Nature* 15(4):343–364.
**What was lifted — reputation, not instantaneous yield, predicts RS (prowess design, §4.5.7/§4.8.5):** a hunter's social standing tracks his *accumulated reputation* for provisioning/skill, not any single day's return. **How used:** `prowess` is a slow **decaying EMA of relative meat intake**, not raw yield — so the achieved-status facet is a reputation. **E.3-proper consequence (§4.8.5):** because prowess (achieved) is independent of cred (lineage), the von Rueden status→RS correlation is *prowess-driven* and robust to flattening the lineage facet — the load-bearing role of within-band individualism turns out to be R-18 mortality-selection, not the RS skew.
**Citation tag:** [USED — prowess = reputation EMA (§4.5.7); prowess-driven RS skew (§4.8.5)]

### Kelly, R.L. (1995/2013). *The Lifeways of Hunter-Gatherers: The Foraging Spectrum.* Cambridge University Press.
**What was lifted — mobile foragers live off the land with carried/body reserve (founder mobile reserve, §4.8.3):** mobile band foragers bridge lean periods and inter-camp moves with carried provisions + body-fat stores rather than instantaneous daily intake. **How used:** motivates the `founder_buffer_steps` mobile-reserve device — founders carry a few steps' worth of kcal to survive the dispersal transient (the model's ~1-step wealth buffer alone cannot bridge a band moving to find viable cells). Also the general "a band of ~25 spans a multi-cell territory, not one cell" framing (with Binford 2001 packing). **Note:** a conceptual/ecological anchor; `founder_buffer_steps` itself is a provisional transient-bridge number, not a fitted value.
**Citation tag:** [REFERENCE — mobile-reserve rationale for the founder buffer (§4.8.3)]

## Persistent-families anchors (F.3 pair-bonds + family co-movement, MODEL_SPEC §4.8.7; added 2026-06-29)

### Hill, K.R., Walker, R.S., Božičević, M., et al. (2011). "Co-Residence Patterns in Hunter-Gatherer Societies Show Unique Human Social Structure." *Science* 331(6022):1286–1289.
**What was lifted — band composition (F.3 design target, §4.8.7):** across 32 present-day foraging societies, a residential band's adult members are **mostly NOT close kin** — primary kin (parents/offspring/siblings) are a minority; most co-residents are **distantly related or unrelated, linked through MARRIAGE** (affinal ties) and bilateral kinship. So a band = **multiple families + maturing/unrelated singles**, not an extended-kin clan. **How used:** the *validation target* for F.3 — pair-bonds + family co-movement should yield bands that are family-cored but multi-family and marriage-linked. (The current F.3a/b build produces nuclear-family-sized bands ~7; the multi-family ~25 band is the noted F.3c follow-on.) **Rejected:** the band-as-kin-group / lineage-clan model.
**Citation tag:** [REFERENCE — band-composition target (§4.8.7); multi-family marriage-linked bands]

### Marlowe, F.W. (2004). "Marital residence among foragers." *Current Anthropology* 45(2):277–284.
**What was lifted — marriage system + residence (F.3a, §4.8.7):** foragers are predominantly **monogamous** (modest polygyny among high-status males, ~the von Rueden 4–11%), with **serial monogamy** (re-pairing after death/divorce) and **MULTILOCAL / flexible** post-marital residence (not rigidly patri- or matrilocal — the classic "patrilocal band" is overstated). **How used:** sets the F.3a model — **monogamy + serial re-pairing** (widow/divorce → re-pair), the chosen pair-bond model; polygyny deferred to a later knob; residence handled as nuclear-family co-residence (the unit co-locates) rather than a fixed patri/matri rule.
**Citation tag:** [USED — F.3a monogamy + serial re-pairing (§4.8.7)]

### Kaplan, H., Hill, K., Lancaster, J., Hurtado, A.M. (2000). "A theory of human life history evolution: Diet, intelligence, and longevity." *Evolutionary Anthropology* 9(4):156–185.
**What was lifted — juvenile dependence span (F.3b maturity, §4.8.7):** the human "embodied-capital" life history has a **long juvenile dependence** — children are net energy consumers, provisioned by parents/kin, until ~**15–18 yr**, when foraging return rates reach adult levels. **How used:** `family_maturity_months ≈ 180` (15 yr) — the age at which a child **detaches** from the co-moving family unit (becomes an independent forager + enters the mating pool → exogamous dispersal). Complements the η(age) production ramp (§4.5.1) and the C.2b/B+ provisioning (§4.5.4/§4.5.7).
**Citation tag:** [USED — F.3b family-maturity / child-detachment age (§4.8.7)]

### Birdsell, J.B. (1953). "Some Environmental and Cultural Factors Influencing the Structuring of Australian Aboriginal Populations." *The American Naturalist* 87(834):171–207. DOI 10.1086/281776. — and Birdsell, J.B. (1968). "Some Predictions for the Pleistocene Based on Equilibrium Systems among Recent Hunter-Gatherers." In R.B. Lee & I. DeVore (eds.), *Man the Hunter*, Aldine, Chicago, pp. 229–240.
**What was lifted — the band "magic numbers" (F.3c-1, §4.8.8) — PDFs READ:** the **1953 paper** (verified text) gives the **horde / local group ≈ 40 persons** ("usually numbers about 40"), **exogamous, patrilineal & patrilocal** (Australian pattern: wife taken from outside, lives with husband's horde), nesting in the **dialectal *tribe* ≈ 500**. The famous "**band ≈ 25**" is the **1968** *Man the Hunter* chapter (the "magic numbers" 25/500). **How used:** the *target* emergent affiliation-band size (~25) for F.3c-1; ~500 is the next nesting level (cf. Wobst ~475; Hamilton 2007 community). **CAVEATS:** (a) the **~500** is CONTESTED — critics ("On the magic number 500: an expostulation"; Helm) flag questionable algebra + a biased sample, so 500 is a soft modal target, NOT a law. (b) Birdsell's Australian data is **patrilocal ~40-person hordes**; we instead use **~25 multilocal/flexible, mostly-non-kin bands** (Hill 2011 + Marlowe — the cross-cultural pattern; the "patrilocal band" is overstated). So Birdsell grounds the nested-LEVELS idea + the ~500, while the ~25 size & non-kin composition rest on Wobst/Kelly/Hill. **Status: FILED + verified (1953 PDF + Man the Hunter PDF read).**
**Citation tag:** [TARGET — band size ~25 (§4.8.8); ~500 contested; Birdsell's horde≈40/patrilocal differs from our flexible ~25 non-kin band]

### Hamilton, M.J., Milne, B.T., Walker, R.S., Burger, O., Brown, J.H. (2007). "The complex structure of hunter–gatherer social networks." *Proc. R. Soc. B* 274(1622):2195–2203. DOI 10.1098/rspb.2007.0564 (open access, PMC2706200).
**What was lifted — nested/self-similar social structure (F.3c, §4.8.8) — PDF READ:** from **1189 social groups across 339 HG societies**, HG population structure is **self-similar / fractal** with each successively higher level of organization exhibiting **a constant ratio close to 4** (verified text), holding within and across cultures/continents; the authors tie the branching ratio to **density-dependent reproduction in complex environments**. **How used:** justifies an explicit BAND level that bundles families + nests in a community — motivates the collective-identity vector + multi-family band; the ~4× ratio sets the rough level-sizes (family ~few → band ~15–30 → community ~50–150). **Status: FILED + verified (PDF read; ratio "close to 4" confirmed).**
**Citation tag:** [REFERENCE — nested band structure / ~4× scaling (§4.8.8)]

## Leader-coherence & size-repulsion anchors (Social-Evolution Stage 1, MODEL_SPEC §4.8.13; added 2026-07-01)

### Johnson, G.A. (1982). "Organizational Structure and Scalar Stress." In C. Renfrew, M.J. Rowlands & B.A. Segraves (eds.), *Theory and Explanation in Archaeology*, Academic Press, pp. 389–421. (PDF filed `literature/SiC_Games_D2_Johnson1982_OrgStructureScalarStress.pdf`, verified.)
**What was lifted — SCALAR STRESS (the size-repulsion mechanism, §4.8.13):** the foundational argument that as a group grows, person-to-person coordination links grow combinatorially → decision-making stress that overwhelms consensus above a span-of-control threshold (Johnson's ~6 *decision-making units*, NOT raw headcount). The crucial corollary the model uses: **scalar stress is what hierarchical/organizational structure exists to ABSORB** — so larger groups require hierarchy, and hierarchy relieves the size penalty. **How used:** the SHAPE (a rising, size-driven coordination cost) + the society-coupling (`REPULSION_SOCIETY_FACTOR`: full in egalitarian mobile bands, relieved in complex/stratified). **Rejected:** Johnson's ~6 as a literal band-size threshold (it's a decision-unit span, a different quantity — the midpoint is re-anchored to band scale, a bracket).
**Citation tag:** [MECHANISM — scalar stress → size repulsion; society-relief coupling (§4.8.13)]

### Alberti, G. (2014). "Modeling Group Size and Scalar Stress by Logistic Regression from an Archaeological Perspective." *PLoS ONE* 9(3):e91510. DOI 10.1371/journal.pone.0091510. (Open access; PDF filed `literature/SiC_Games_D1_Alberti2014_ScalarStressLogistic.pdf`, verified.)
**What was lifted — the LOGISTIC SHAPE of scalar-stress onset (§4.8.13):** a quantitative logistic-regression model of P(critical scalar stress) vs. community size — **p=0.50 at N≈127 (95% CI 122–132), p=0.99 at N≈158 (147–170)** (⇒ logistic width ≈6–7 people), converging on Dunbar's ~150. **How used:** the FUNCTIONAL FORM of `size_repulsion` = a logistic in band size (`1/(1+exp(−(N−mid)/width))`), width ~6 (`repulsion_width`). **Re-anchoring caveat (bracket, not fit):** Alberti's N≈127 is **village/settlement scale**, 4–6× our bands (25–45) — importing 127 literally would be a category error (cf. the rejected Usher human-famine% as a herd input). The logistic SHAPE transfers; the MIDPOINT is re-anchored to band scale (`repulsion_midpoint≈25`, the Wobst-minimal band) exactly as the regime °C→CC% and caribou period were re-scaled.
**Citation tag:** [MECHANISM — logistic scalar-stress form; village-scale numbers NOT portable (§4.8.13)]

### Layton, R., O'Hara, S., Bilsborough, A. (2012). "Antiquity and Social Functions of Multilevel Social Organization Among Human Hunter-Gatherers." *International Journal of Primatology* 33:1215–1245. DOI 10.1007/s10764-012-9634-z. (Accepted-MS PDF filed `literature/SiC_Games_D3_Layton2012_MultilevelSocialOrg.pdf`, verified.)
**What was lifted — the TWO-FORCE band-formation frame (§4.8.13):** the band is an evolved compromise between a cooperation pull (hunting + division of labour → aggregate) and a dispersal push (resource competition + mobility → fragment). **How used:** the theoretical justification for modelling `tolerable_size` as an explicit **cohesion − dispersion balance** (assabiyah + leader vs. size-repulsion) rather than a single hard threshold. **Status: FILED + verified. NO parametric anchor (theoretical framing only).**
**Citation tag:** [REFERENCE — cohesion↔dispersion two-force frame (§4.8.13)]

## Village fission/budding anchors (recovery + settlement-spread mechanism — SCOPING 2026-07-14)

**Filing status (2026-07-15):** Bandy 2004 + Wobst 1974 + Adler 1996 FILED (user); Alberti 2014 + Johnson 1982 already filed. Chagnon 1975 + Forge 1972 NOT OBTAINED — CORROBORATING ONLY, not load-bearing (the mechanism's quantitative anchors are Bandy + Alberti). No blocker to building.

### Bandy, M.S. (2004). "Fissioning, Scalar Stress, and Social Evolution in Early Village Societies." *American Anthropologist* 106(2):322–333. DOI 10.1525/aa.2004.106.2.322.
**What is being lifted (SCOPING — village budding mechanism):** early sedentary villages are INHERENTLY UNSTABLE — village FISSIONING is the predominant mechanism for resolving intra-village conflict (scalar stress, Johnson-style, rising ~quadratically with size). A village grows to a threshold, then a segment BUDS OFF to found a DAUGHTER village → the settlement system EXPANDS by budding, not just in-situ growth. Fission CEASES only when integrative institutions (regional ritual/hierarchy) emerge — the Bandy→Carneiro pathway (matches our Johnson scalar-stress→hierarchy). **Use (planned):** a village exceeding a scalar-stress fission threshold sheds a segment (led by a rival leader/lineage) onto a nearby storable site — the RECOVERY/settlement-spread mode the aggregation-only model lacks (R-68). **Status: FILED (literature/bandy2004.pdf) — the LOAD-BEARING source; exact thresholds/process to extract into MODEL_SPEC.md at build.**
**Citation tag:** [SCOPING — village fission/budding (recovery mechanism); FILED]

### Chagnon, N.A. (1975). "Genealogy, Solidarity, and Relatedness: Limits to Local Group Size and Patterns of Fissioning in an Expanding Population." *Yearbook of Physical Anthropology* 19:95–110.
**What is being lifted (SCOPING):** the canonical Yanomamö fission ethnography — villages fission along LINEAGE/LEADERSHIP cleavages; intra-village conflict rises sharply above **~200 inhabitants** → split; a large village develops SEVERAL competing headmen (from the largest patrilineages) and cleaves between them. Grounds the "internal leadership competition drives fission" mechanism (supervisor's hypothesis, confirmed). **Status: NOT OBTAINED (paywalled, no DOI). CORROBORATING ONLY — the ~200 threshold + leadership-cleavage driver are cited from secondary ethnographic summaries; the load-bearing fission anchors (Bandy 2004 + Alberti 2014) are FILED. Not a blocker.**
**Citation tag:** [SCOPING — Yanomamö fission ~200 / leadership-cleavage driver; secondary-cited]
**[SUPERSEDED IN PART, 2026-07-27 — see Alvard 2009 below.]** The "cleaves along LINEAGE lines" half of this entry
is contradicted by the one paper on this fight we actually hold. The ~200 size figure stands.

### Alvard, M. (2009). "Kinship and Cooperation: The Axe Fight Revisited." *Human Nature* 20:394–416.
**Status: FILED and READ (`literature/AlvardPaper2.pdf`; text at `literature/_alvard_text.txt`).** Obtained
2026-07-27 while checking the budding cleavage axis. **[VERIFIED — read directly, not summarised.]**

**What was lifted — THE CLEAVAGE AXIS OF VILLAGE FISSION.** Matrix-regression reanalysis of Chagnon's data on
the Mishimishimaböwei-teri axe fight (a village that had itself recently fissioned; the splinter group was
visiting when the fight broke out). Who sides with whom:

| predictor of faction affiliation | variance explained |
|---|---|
| **genetic kinship** | **~15%** |
| lineage membership | ~3% (p=0.01) |
| affinal (in-law) ties | ~2% (p<0.000) |

**The decisive result:** entered together, **lineage is no longer significant (p=0.281)** and adds no variance
over kinship alone — its univariate effect was covariance with relatedness ("lineage members are more closely
related than expected by chance"). The paper's own abstract: *"genetic kinship was the primary organizing
principle in the axe fight; affinal relations were also important, whereas lineage identity explained nothing."*
The CONTRAST case in the same paper — Lamalera whaling crews — is the reverse: there lineage explains ~10% and
kinship drops out. So lineage-assorted factions are real, but they are the Lamalera pattern, **not** the
Yanomamö fission pattern.

**Also lifted (village demography):** Yanomamö villages run **50 to ~250 individuals**; "solidarity begins to
deteriorate as village populations grow beyond 250 or so, and village fissioning often occurs"; splits are
"often related to mate competition". NOTE: the paper does **not** state a count of lineages per village — an
earlier "~2 major patrilineages" claim in this project came from a PNAS *profile* piece, not a paper, and is
**withdrawn as unsourced**.

**How used (PARAMETERS §21.8):** village budding now cleaves on KINSHIP (genome identity-by-state, genealogical
fallback) between the two highest-standing men, replacing the 2nd-largest-lineage split. Independent check: the
resulting village-size distribution moved into this paper's stated 50–250 band without being tuned for it.
**Citation tag:** [ANCHOR — village fission cleaves on kinship, NOT lineage; village size 50–250; VERIFIED]

### Forge, A. (1972). "Normative Factors in the Settlement Size of Neolithic Cultivators (New Guinea)." In P.J. Ucko, R. Tringham & G.W. Dimbleby (eds.), *Man, Settlement and Urbanism*, Duckworth, London, pp. 363–376.
**What is being lifted (SCOPING):** the classic face-to-face village size ceiling (~150–400 before segmentation is forced), a companion anchor to Alberti's logistic (P=0.5 at N≈127, 0.99 at N≈158, already FILED) and Yanomamö ~200 for the fission threshold. **Status: NOT OBTAINED (edited-volume chapter). REDUNDANT — superseded for our use by Alberti (N≈127–158, filed) + Yanomamö ~200. Not a blocker.**
**Citation tag:** [SCOPING — village-size fission ceiling ~150–400; superseded by Alberti/Yanomamö]

### Adler, M.A. (1996). Ancestral Pueblo population aggregation & abandonment — *Journal of World Prehistory* (filed as literature/adler1996.pdf; exact citation to confirm from PDF).
**What is being lifted (SCOPING, question-1 support):** collapse does NOT uniformly shrink villages — the settlement system CONTRACTS via COALESCENCE (survivors aggregate up into fewer, larger towns) OR regional ABANDONMENT; the Southwest cycled aggregation↔abandonment for centuries. So "% villages wiped in a crash" has no clean value — count drops, survivors concentrate. **Status: FILED (literature/adler1996.pdf).**
**Citation tag:** [SCOPING — crash = coalescence/contraction, not uniform wipeout; FILED]

### Colson, E. (1979). "In Good Years and in Bad: Food Strategies of Self-Reliant Societies." *Journal of Anthropological Research* 35(1):18–29. (PDF filed `literature/Colson - 1979 …Self-Reliant Societies.pdf`, verified 2026-07-01.)
**What was lifted — the M2 malnutrition-fission anchor (§4.8.14) — PDF READ:** Colson (drawing on Makah NW-Coast + Gwembe/Plateau Tonga fieldwork) lists the recurrent famine responses of self-reliant societies; the load-bearing passage: *"the shift to foods normally ignored, **the breakup into small family groups which comb the region**, the refusal to share food with others"* (and *"people wandered around the countryside, each small family by itself, hunting something to eat"*). **How used:** the **verbatim qualitative anchor for M2** — under severe realized scarcity a band FRAGMENTS into small dispersed family groups that spread over the territory (dispersal-as-famine-coping). Also anchors the review's point that sharing/cohesion cannot avert absolute deficit ("refusal to share" = cohesion breaks at the extreme), and the two-sided "make up in good years for the bad" framing (storage + mobility as complementary coping). **Direction + pattern only — NO quantitative malnutrition→fission threshold** (M2's trigger is anchored to the model's own starvation onset, R-32/R-33). **Status: FILED + verified (PDF read; the "breakup into small family groups" passage confirmed).**
**Citation tag:** [MECHANISM — famine → band fragmentation/dispersal (M2, §4.8.14)]

## The gathering — seasonal aggregation, marital residence & mobility anchors (Social-Evolution, MODEL_SPEC §4.8.18; added 2026-07-02)

### Mauss, M. & Beuchat, H. (1979 [1904–05]). *Seasonal Variations of the Eskimo: A Study in Social Morphology.* Routledge & Kegan Paul.
**What was lifted — the aggregation/dispersion social morphology (§4.8.18):** the foundational statement that forager social life OSCILLATES between a dispersed phase (small family units, subsistence-driven) and a concentrated phase (large multi-band gatherings with intensified ritual/social life). **How used:** the theoretical warrant for "the gathering" — a seasonal convening of bands that is the mate-market, distinct from the year-round dispersed subsistence phase. **Status: REFERENCE (framing); INLINE citation — PDF not filed. NO parametric anchor.**
**Citation tag:** [REFERENCE — seasonal aggregation/dispersion morphology (§4.8.18)]

### Steward, J.H. (1938). *Basin-Plateau Aboriginal Sociopolitical Groups.* Bureau of American Ethnology Bulletin 120.
**What was lifted:** the Great Basin Shoshone case — families disperse for most of the year and periodically **congregate at resource-abundant loci** (piñon groves, rabbit/antelope drives) where marriages are arranged. **How used:** the ethnographic model for pairing at ABUNDANT sites (`aggregation_season_threshold` + site selection on capacity). **Status: REFERENCE; INLINE — PDF not filed.**
**Citation tag:** [REFERENCE — congregation at abundant sites → marriage (§4.8.18)]

### Lee, R.B. (1979). *The !Kung San: Men, Women, and Work in a Foraging Society.* Cambridge University Press. — and Conkey, M.W. (1980). "The Identification of Prehistoric Hunter-Gatherer Aggregation Sites: The Case of Altamira." *Current Anthropology* 21(5):609–630.
**What was lifted:** !Kung wet-season aggregation at permanent waterholes (mate-finding + exchange) [Lee]; the archaeological signature of periodic large aggregations [Conkey — Altamira as an aggregation locus]. **How used:** corroborating breadth for the seasonal-aggregation mechanic (not Basin-specific). **Status: REFERENCE; INLINE — PDFs not filed.**
**Citation tag:** [REFERENCE — !Kung/Altamira aggregation corroboration (§4.8.18)]

### Ember, M. & Ember, C.R. (1971). "The Conditions Favoring Matrilocal versus Patrilocal Residence." *American Anthropologist* 73(3):571–594. DOI 10.1525/aa.1971.73.3.02a00040. — with Marlowe, F.W. (2004) & Hill et al. (2011) [filed above, §4.8.7].
**What was lifted — residence direction (§4.8.18):** the cross-cultural conditions that select virilocal (patrilocal) vs uxorilocal (matrilocal) post-marital residence. Marlowe 2004 gives forager residence frequencies; Hill 2011 the bilateral/flexible modern-forager pattern. **How used:** grounds the three wired residence options (`aggregation_residence` ∈ virilocal/uxorilocal/flexible) and the standing long-term study of residence→society; the egalitarian-floor ascribed-mate weight (0.25) also rests on family-swayed marriage being universal.

**CORRECTED 2026-07-22 — this entry previously named "warfare pattern, subsistence-labour division" as the conditions, as though both were supported. They are not co-equal, and the labour half is the paper's headline NEGATIVE.** Ember & Ember's result is that the traditional division-of-labour explanation was **not** supported; the determinant is WARFARE TYPE — **internal warfare favours patrilocal, purely external warfare favours matrilocal** (the latter conditional on matridominant labour division). Verified against the HRAF Explaining Human Culture summary "Residence and Kinship", which states outright that higher male subsistence contribution does *not* generally predict patrilocality. **Caveat that matters for this project specifically:** the labour effect DOES hold in the hunter-gatherer subset — among foragers and Native North American societies, higher male subsistence contribution does predict patrilocality. So for an HG→proto-agricultural model the labour route is live at the forager end and fades as subsistence intensifies.
**Consequence for the model:** an endogenous residence rule should key on CONFLICT PATTERN, not subsistence shares. We do not currently distinguish internal from external warfare (`claim_events` is cell contest, not war between vs within communities), so that distinction is the missing substrate, not the residence toggle itself.

**PARAMETRIC ANCHOR (added 2026-07-22, from the filed PDF — the "comparisons deferred" note is now discharged).** Verbatim abstract: the division-of-labour assumption — "The results did not support that assumption" — measured at φ = .05 (n.s.) for matrilocal and φ = .04 for patrilocal, worldwide (Tables II, III). The warfare result, Table XI (p.589), **controlling on level of political integration**:

| Political integration | Warfare | Matrilocal | Patrilocal |
|---|---|---|---|
| Local | purely external | 4 | 2 |
| Local | internal, or internal+external | **0** | **15** |
| Multilocal | purely external | 3 | 1 |
| Multilocal | internal, or internal+external | 1 | 14 |

Local: φ = .74, p = .003. Multilocal: φ = .68, p = .016 (both one-tail, Fisher's Exact). **Internal warfare → 29/30 patrilocal across both levels; purely external → 7/10 matrilocal.**

**THE EFFECT IS NOT SCALE-GATED — and a first reading here claimed it was.** The PDF text layer renders the local φ as ".14", which would have meant the mechanism barely operates at the acephalous scale this project models, and would have looked like a neat convergence with R-97's "cycles are state-scale". Rendering p.589 as an image shows **.74**: the association is if anything STRONGER at the local level. Recorded because the near-miss is the lesson — a garbled digit produced a conclusion that flattered an existing result, and the only thing that caught it was the φ/p pair being mutually impossible at the visible n.

**Consequence for SiC Games specifically:** the model implements ONLY internal conflict — `claim_events` is contest between neighbouring groups inside one world, with no external enemy. By Ember & Ember's finding that regime predicts patrilocal/virilocal residence at 15/15 (local integration), which is exactly the model's default `aggregation_residence="virilocal"`. **The default is the ethnographically correct rule for the conflict regime the substrate implements.** The R-102 uxorilocal arms are therefore a MECHANISM test (does the residence lever work, and what does it change downstream), NOT a realism comparison — an uxorilocal world under purely-internal warfare is a case the ethnographic record contains zero instances of.
**Status: REFERENCE → **ANCHORED**; PDF FILED 2026-07-22 (`literature/American Anthropologist - June 1971 - EMBER - ...pdf`). Table XI values verified by IMAGE render, not text extraction.**
**Citation tag:** [ANCHOR — marital residence from warfare pattern, not labour (§4.8.18; R-102)]

### Murdock, G.P., Textor, R., Barry, H. III, White, D.R., Gray, J.P. & Divale, W.T. (1999). *Ethnographic Atlas.* World Cultures 10:24–136 (codebook). — machine-readable via **D-PLACE** [Kirby, K.R. et al. (2016). "D-PLACE: A Global Database of Cultural, Linguistic and Environmental Diversity." *PLoS ONE* 11(7):e0158391. DOI 10.1371/journal.pone.0158391].
**What was lifted — THE CROSS-CULTURAL CATEGORISATION SCHEME (filed 2026-07-22, for #48):** coded ethnographic variables for **1,291 societies**, replacing this project's homegrown 3-way society classifier with the standard scheme. The variables that bear on open questions:
- **EA033 jurisdictional hierarchy beyond the local community** — the political-complexity TIERS, the scheme the project had been missing: Acephalous 45.5% / One level, petty chiefdoms 29.5% / Two levels, larger chiefdoms 14.0% / Three levels, states 7.2% / Four levels, large states 3.8% (n=1155).
- **EA043 descent major type** (n=1274): Patrilineal 46.3%, Bilateral 28.4%, Matrilineal 12.6%, Duolateral 4.1%, Mixed 3.9%, Ambilineal 3.8%.
- **EA012 marital residence** (n=1267): Patrilocal 50.4%, Virilocal 21.0%, Ambilocal 6.6%, Uxorilocal 6.5%, Neolocal 4.9%, Matrilocal 4.6%, Avunculocal 4.3% (+1.3% avuncu-variants).
- **EA042 dominant subsistence × EA043 descent** — the cross-tab that gives the classifier its missing third input: hunting 77% bilateral, gathering 70% bilateral, fishing 55% bilateral; extensive agriculture 51% patrilineal **and matriliny's peak at 19%**; intensive agriculture 55% patrilineal; **pastoralism 77% patrilineal** (the strongest single association in the table).
- **EA074/EA076 inheritance rule** (land n=856 / movable n=909) — for #47: land is Patrilineal-by-sons 41.4%, no inheritance of real property 26.1%, patrilineal-by-heirs 10.5%, matrilineal-by-heirs 7.0%, children 6.4%, children-less-for-daughters 5.0%, matrilineal-by-sister's-sons 3.6%.
- **EA073 hereditary succession** (n=937): Nonhereditary 34.0%, Son 32.8%, absence of office 11.6%, patrilineal heir 10.8%, matrilineal heir 6.8%, sister's son 3.9%.
- **EA066 class differentiation** (n=1109): absence of distinctions 48.5%, dual stratification 20.6%, wealth distinctions 19.6%, complex 7.8%, elite 3.6%.

**How used:** (1) anchors #48 — subsistence mode predicts descent strongly enough to be the classifier's third input, and the 19% matrilineal peak under *extensive* agriculture independently vindicates the existing `matrilineal_horticulturalist` preset's name; (2) EA033 places the model empirically — a world of villages and big men with no authority beyond the community is **Acephalous, 45.5% of the ethnographic record**, while states (EA033 3–4) are 11.0%, which is the cross-cultural warrant for R-97's "Turchin's cycles are a STATE-scale phenomenon, we built the Kachin"; (3) EA074/EA076 supersede BHM 2009's single β as the anchor for material inheritance, giving RULE and DISTRIBUTION by society rather than one transmission coefficient; (4) the avunculate is real but rare — avunculocal residence 5.6%, sister's-son succession 3.9%, sister's-son land inheritance 3.6% — supporting its treatment as a refinement rather than a prerequisite for matriliny.
**Status: DATA FILED — `literature/dplace_ea/` (variables/codes/societies/data.csv, D-PLACE dataset v3.0, CC-BY-NC-4.0, 121,355 data points). Kirby et al. 2016 PDF FILED (open access). Murdock 1967 *Ethnology* 6(2):109–236 summary FILED 2026-07-22 (`literature/murdock1967.pdf`). The World Cultures 1999 codebook is NOT filed and is NOT needed — it is the canonical citation for the code definitions, and those definitions are already carried in `dplace_ea/codes.csv`.**
**Citation tag:** [ANCHOR — cross-cultural categorisation: descent/residence/subsistence/hierarchy tiers (#48, #47)]

### Goody, J. (1976). *Production and Reproduction: A Comparative Study of the Domestic Domain.* Cambridge University Press (Cambridge Studies in Social Anthropology 17), pp. xiii+157.
**What it anchors — the DETERMINANT of the inheritance rule (#47, filed 2026-07-23).** Goody's thesis of **diverging devolution**: property transmitted to children of BOTH sexes (dowry-like, partible/equal) is tied to the **intensive** exploitation of land (plough/irrigation), stratification, and complex states; where land is worked **extensively** (hoe/swidden) property devolves **homogeneously** within a lineage/same-sex (bridewealth, consolidated). So the inheritance rule is not free — it is **regime-dependent on land intensity**. Goody built this on **Murdock's Ethnographic Atlas** — the same dataset filed above — so the D-PLACE cross-tab run here is a re-execution of his analysis on the modern coded version.

**EMPIRICAL VERIFICATION [VERIFIED — cross-tab computed 2026-07-23 on `dplace_ea/`]:** inheritance DISTRIBUTION for land (EA075) × agriculture intensity (EA028), and × dominant subsistence (EA042):
- **No agriculture / casual (foragers):** land is NOT inherited — *no inheritance of real property* 77–89%. Land is not property; nothing to bequeath. (Directly relevant: SiC Games at its forage stage should show ~no land inheritance — the model's "big men who can't bequeath" is ethnographically correct until land ownership exists.)
- **Extensive / shifting (abundant land, low investment):** **Primogeniture 49%** (concentrate to one heir), equal 33%.
- **Intensive:** **Equally distributed 55%**, primogeniture 31%.  **Intensive irrigated:** **Equal 70%**, primogeniture 21%.
- **Pastoral:** patrilineal-by-sons / equal-less-for-daughters (livestock = movable; BHM 2009 β_material 0.67, the MOST heritable wealth class).

**COUNTERINTUITIVE DIRECTION worth stating:** the naive "scarce land → primogeniture to avoid fragmentation" is BACKWARDS in the data — primogeniture is the EXTENSIVE (land-abundant) pattern; intensive/scarce land goes EQUAL/partible (Goody: diverging devolution provisions all heirs incl. daughters to hold status). So the concentrating "chiefly estate" route ethnographically is **extensive agriculture + primogeniture**, not intensive.
**Status: REFERENCE (theory) — PDF NOT filed; anchored by the D-PLACE cross-tab (in hand, [VERIFIED]). Goody used the same Murdock data, so the cross-tab IS the anchor.**
**Citation tag:** [ANCHOR — inheritance rule is regime-dependent on land intensity; diverging devolution (#47)]

### Binford, L.R. (2001). *Constructing Frames of Reference.* University of California Press. — with Kelly, R.L. (1995/2013) [filed above].
**What was lifted — the mobility ∝ 1/productivity gradient (R-39, mobility stage seam):** Binford's cross-cultural regularity that residential mobility (moves/yr, distance/move, annual range) SCALES INVERSELY with environmental productivity — foragers in marginal (low-NPP) habitats range farther and move more; Kelly's Foraging Spectrum gives the forager/collector logistical–residential axis. **How used:** the literature warrant for the NEXT stage — productivity-scaled movement range (`move_radius ≈ clamp(base·NPP_ref/local_NPP, 1, max)`) — diagnosed as the root cause of the savanna collapse (fixed r=1 diffusion cannot spread agents over sparse territory). **Status: REFERENCE (framing for the mobility stage); Kelly PDF filed, Binford INLINE. Parametric anchor TBD at build.**
**Citation tag:** [MECHANISM — mobility ∝ 1/productivity (R-39; mobility stage seam)]

## Aquatic-food fishery & river-thermal anchors (Biome-Climate + Aquatic-Food stage, blueprint …_BiomeClimate_AquaticFood; added 2026-07-03)

### River thermal regime by source — snowmelt / groundwater / lowland (web-sourced, 2026-07-03).
Van Vliet et al. / IOP (2021) "Greater vulnerability of snowmelt-fed river thermal regimes to a warming climate" (iopscience.iop.org/article/10.1088/1748-9326/abf393); Eawag "Thermal regime of lakes and rivers" (thermdis.eawag.ch); Hudson et al. (2023) "Thermal regimes of groundwater- and lake-fed headwater streams…" *L&O Letters* (doi 10.1002/lol2.10349).
**What was lifted — RIVER TEMPERATURE IS SOURCE-DEPENDENT (Q3):** snowmelt/montane-headwater rivers are COLD (<3 °C winter, <15 °C summer even alpine); lowland/pluvial rivers TRACK AIR temperature (warm in summer); spring/aquifer-fed streams are thermally STABLE/buffered (cold summer, warm winter). **How used:** the fishery signal's river temperature must be `T_river = f(headwater/source elevation)`, NOT local air temp — a salmon river can be cold at low latitude if it drains montane headwaters (Phase 1b). **Status: REFERENCE (web abstracts read; PDFs not filed). Parametric anchor (lapse + source routing) TBD at build.**
**Citation tag:** [MECHANISM — river temperature by source (Phase 1b)]

### Salmonid thermal tolerance — the cold-water fishery bound (web-sourced, 2026-07-03).
USDA Forest Service, Dunham et al. (2001) "Salmonid Behavior and Water Temperature" (research.fs.usda.gov/download/treesearch/23970.pdf); "Quantification of thermal impacts across freshwater life stages… anadromous salmonids" *Conservation Physiology* 10(1):coac013 (2022).
**What was lifted — anadromous salmon need COLD water:** optimum ~15.9 °C (Atlantic) / 16.5 °C (Chinook); stress begins >15.6 °C; growth range 6–22.5 °C; LETHAL >21–22.5 °C; angling closures at >20 °C. **How used:** the `coldness(T_river)` term of the aquatic-food field — `coldness = clamp((T_lethal−T_river)/(T_lethal−T_opt),0,1)`, T_opt≈16 °C, T_lethal≈21 °C. A warm savanna/lowland river fails; a cold montane-sourced river passes. **Status: REFERENCE (web abstracts read; PDFs not filed). Anchor: T_opt/T_lethal above.**
**Citation tag:** [PARAMETER — salmonid thermal cutoff T_opt≈16 / T_lethal≈21 °C (aquatic-food field)] — **BUILT** (`terrain.py::aquatic_food_field`, C7); methods MODEL_SPEC §4.3.9, constants PARAMETERS §19.6, finding RESULTS R-50/R-51.

### Ames, K.M. (1994). "The Northwest Coast: Complex Hunter-Gatherers, Ecology, and Social Evolution." *Annual Review of Anthropology* 23:209–229. — with Testart 1982 [filed above].
**What was lifted — storable aquatic surplus → forager complexity:** the paradigm that dense, STORABLE, seasonally-concentrated AQUATIC resources (NW-Coast salmon) underwrite delayed-return, ranked/stratified complex foragers — complexity is the exception, tied to this specific resource configuration, not to terrestrial productivity or seasonality per se. **How used:** the theoretical warrant for gating the society MORPH on an aquatic-food field rather than on biome/seasonality (R-46→R-48 → this stage). **Status: REFERENCE (framing); INLINE — PDF not filed.**
**Citation tag:** [REFERENCE — storable aquatic surplus → complexity (aquatic-food stage)] — the C8 aquatic capacity subsidy is **BUILT** (`capacity.py::NPPCapacityField(aquatic=True)`); methods MODEL_SPEC §4.3.10, finding RESULTS R-51 (subsidy alone insufficient — circumscription keystone).

## GD-1 finite resources — depletion, biome/season regrowth & central-place mobility (blueprint …_GD1_FiniteResources; added 2026-07-03, web-sourced)

### Coe, M.J., Cumming, D.H., Phillipson, J. (1976). "Biomass and production of large African herbivores in relation to rainfall and primary production." *Oecologia* 22:341–354.
**What was lifted — game STOCK & PRODUCTION ∝ rainfall/NPP:** standing herbivore biomass and secondary production in African savannas correlate strongly with mean annual rainfall and above-ground primary production. **How used:** the depletable-stock CEILING `K` scales with the (Miami-NPP) productivity already in the model — biome productivity sets the game stock; life-history sets the regrowth rate. **Status: REFERENCE (web abstract); PDF not filed.**
**Citation tag:** [MECHANISM — game stock/production ∝ NPP (GD-1 K)] — GD-1 **BUILT** (`capacity.py`, `enable_depletion=True`); methods MODEL_SPEC §4.3.11, finding RESULTS R-51.

### Cortés, E. (2016). "Perspectives on the intrinsic rate of population growth." *Methods in Ecology and Evolution* 7:1136–1145; + Southeast-Asian ungulate post-poaching recovery (muntjac r≈0.44, gaur r≈0.31).
**What was lifted — the REGROWTH RATE r:** intrinsic rate of increase r_max for medium ungulates ≈0.3–0.4/yr (recover in a few years); megafauna (elephant, sambar) far slower (decades) and deplete first. **How used:** the biome-specific logistic regrowth `r_biome` (GD-1 §2) — fast for small/grassland grazers, slow for forest megafauna. **Status: REFERENCE (web abstract); PDFs not filed. Anchor: r_max ≈0.3–0.4/yr medium ungulate.**
**Citation tag:** [PARAMETER — game regrowth r_biome (GD-1)] — **BUILT** as `R_BIOME_PER_YR`/`AQUATIC_R_PER_YR` (`capacity.py`); constants PARAMETERS §19.7, methods MODEL_SPEC §4.3.11.

### Central-place prey-depletion halos & marginal-value residential mobility — web-sourced 2026-07-03.
Central-place prey-depletion halos (biorxiv 2024.06.13.598783); "Measuring local depletion of terrestrial game vertebrates by central-place hunters in rural Amazonia" (PMC5645145); "Hunter-gatherer residential mobility and the marginal value of rainforest patches" (PMC5373393).
**What was lifted — the CAMP↔DEPLETION↔MOVE link:** a central-place camp depletes its foraging catchment (a hunt-out HALO, gradient with distance); when the catchment's marginal return drops below the regional average the camp RELOCATES — Charnov's marginal-value theorem at the camp scale. **How used:** the GD-1 residential-mobility mechanism (deplete-then-move) and the basis for EMERGENT sedentism (stay where regrowth+storage ≥ depletion). **Status: REFERENCE (web abstracts); PDFs not filed.**
**Citation tag:** [MECHANISM — central-place depletion halo + MVT residential mobility (GD-1 / camp)]

## Climate → NPP (the Miami model) — Economy-from-Climate stage anchor (added 2026-07-03)

### Lieth, H. (1972/1975). The MIAMI MODEL of climatic net primary productivity. (Lieth 1972 *Nature and Resources*; Lieth & Box in Lieth & Whittaker eds. 1975 *Primary Productivity of the Biosphere*, Springer.)
**What was lifted — NPP from temperature + precipitation (C3):** `NPP_T = 3000·[1+exp(1.315−0.119·T)]⁻¹` (T in °C), `NPP_P = 3000·[1−exp(−0.000664·P)]` (P in mm/yr), `NPP = min(NPP_T, NPP_P)` in g dry-matter/m²/yr — temperature-limited OR precipitation-limited, whichever is smaller. Coefficients fit by least-squares on 50 sites across 5 continents. **How used:** replaces the noise-moisture `npp = wet×elev_pen×slope_pen` with a physical climate→NPP model so productivity is temperature-aware (tundra low despite moisture) and precip-aware (desert low), feeding `npp_gm2` → Tallavaara capacity directly (Miami+Tallavaara are a coherent real-NPP pairing). **Status: VERIFIED AGAINST PRIMARY 2026-07-03** — PDF filed `literature/Lieth - 1975 - Modeling the Primary Productivity of the World.pdf`; the coefficients are eqs **(12-1)** `Y = 3000/(1+e^{1.315−0.119x})` (x = temperature °C) and **(12-2)** `Y = 3000(1−e^{−0.000664x})` (x = precipitation mm), p9 — matching the secondary sources (Lieth & Box PubMed 756053; Scurlock & Olson 2002; FAO Unasylva 114; Bernardi Miami-Model). **Anchor: eqs 12-1 / 12-2.**
**Citation tag:** [PARAMETER — Miami NPP(T,P) coefficients (Economy-from-Climate C3)] — **BUILT** (`terrain.py::miami_npp`, `mode="climate"`); methods MODEL_SPEC §4.3.6, constants PARAMETERS §19.4, finding RESULTS R-49.

---

### Köppen 10 °C warmest-month tree-line isotherm; cross-checked against Körner & Paulsen (2004), "A world-wide study of high altitude treeline temperatures," *J. Biogeography* 31:713–732.

**What was lifted — the alpine tree-line isotherm (orogenic mountain biome):** the classic **Köppen** boundary between forest and alpine/arctic tundra (ET) is the **10 °C WARMEST-MONTH mean AIR temperature** isotherm — where the warmest month averages below 10 °C, forest cannot grow; above the line is barren alpine. This is verified consistent with **Körner & Paulsen 2004**, whose worldwide logger campaign (46 sites, 68°N–42°S) found treelines sit at a **growing-season mean ROOT-ZONE (soil) temperature of 6.7 °C (±0.8)** — soil runs warmer than air over the growing season, and the growing-season mean is below the single warmest month, so **6.7 °C soil growing-season ≈ 10 °C air warmest-month**, the two anchors agree. **How used:** replaces the unanchored high∧steep mountain gate — the orogenic `alpine` biome is classified as **warmest-month mean air T < TREELINE_WARMEST_MONTH_C = 10.0 °C** (warmest-month ≈ annual-mean T + seasonal half-amplitude, both already computed with lapse-rate cooling). This makes the mountain biome an **elevation/temperature** property (cold-because-high, plateaus included), and correctly yields *less* alpine on the same range in warm climates (tropical tree-line is higher). **Correction 2026-07-08:** an earlier draft used 6.4 °C — Körner's *soil growing-season* value mis-slotted into the model's *air warmest-month* field. Web-verified and fixed to the Köppen 10 °C warmest-month air isotherm. **Status: REFERENCE (Köppen isotherm is textbook; Körner 2004 cross-check from the published abstract; PDFs not filed). Anchor: warmest-month air = 10 °C.**
**Citation tag:** [PARAMETER — alpine tree-line isotherm (orogenic mountain biome)] — **BUILT** (`terrain.py`, `orogenK`>0 classification); constants PARAMETERS §12.1, finding RESULTS §R-59.

---

## Bettencourt, L.M.A. (2013). "The Origins of Scaling in Cities." *Science* 340(6139):1438–1441. DOI 10.1126/science.1235823. (SFI working paper 12-09-014 filed `literature/SiC_Games_AGG1_Bettencourt2013_UrbanScaling.pdf` — OA institutional preprint. **[VERIFIED]** against the PDF text via pypdf 2026-07-05.)

**What was lifted — the agglomeration exponent for the returns-to-co-location `L(n)` (agglomeration-economics rework, blueprint …_AgglomerationEconomics):** urban socioeconomic outputs (GDP/GMP, wages, patents, crime) scale **SUPER-LINEARLY** with population, `Y = Y0·N^β`, **β ≈ 1.15** (paper's stated value; empirical Gross-Metropolitan-Product fit **β = 1.126 ± 0.023**, 95% CI, R²=0.96; theoretical **7/6 ≈ 1.167**). Material infrastructure scales **SUB-LINEARLY**, **β ≈ 0.85** (empirical **0.849 ± 0.038**, 95% CI, R²=0.65; theoretical **5/6 ≈ 0.833**); housing/jobs ≈ linear. **How used:** anchors the increasing-returns exponent in the agglomeration production function `Y(n)=R·L(n)`, `L(n)~n^α` for small n → **α ≈ 1.13–1.17 (≈1.15)**, NOT the P0 provisional guess α=1.5 (which over-nucleates). The catchment carrying-capacity then saturates `L(n)` (a subsistence village has a resource ceiling a modern city does not).

**CAVEAT (cross-domain borrowing — the "reinterpreting the data" honesty):** β≈1.15 is measured on **MODERN CITIES** (socioeconomic output), not subsistence fishing/farming villages. We borrow it as the closest *measured* agglomeration exponent, explicitly flagged — the true subsistence returns-to-co-location (weirs/terraces/defense/storage) may differ and is not directly measured. This is an inference, not a fitted subsistence value.

**Status: [VERIFIED] (PDF text, pypdf). Re-anchors agglomeration P0 α 1.5 → ~1.15 (theoretical 7/6; empirical 1.126±0.023).**

---

## Dyson-Hudson, R. & Smith, E.A. (1978). "Human Territoriality: An Ecological Reassessment." *American Anthropologist* 80(1):21–41. DOI 10.1525/aa.1978.80.1.02a00020. (Author OA copy filed `literature/SiC_Games_AGG2_DysonHudsonSmith1978_HumanTerritoriality.pdf` — from co-author E.A. Smith's UW faculty page; **PDF downloaded; content-verification pending a PDF-text tool, poppler absent in env.**)

**What was lifted — the ECONOMIC DEFENSIBILITY model (blueprint …_EconomicDefensibility; folded to catchment grain in …_AggregationSedentism):** territoriality/defense of a resource area is favoured when the resource is **DENSE + PREDICTABLE** (worth defending) and abandoned (open access) when sparse/unpredictable (defense cost > benefit) — the density×predictability quadrant. **How used:** the warrant for (a) the defensibility-index gate `D = density × predictability` (only dense-predictable reaches claimable — DE-10), and (b) re-based to the SETTLEMENT CATCHMENT in the aggregation-sedentism arc (a settled community defends its catchment; the contested-catchment case is the Carneiro follow-on). This is a CONCEPTUAL/mechanism anchor (a cost/benefit inequality), not a fitted number. **Retroactively grounds** the defensibility citations previously made from memory (the user's lit-fetch callout).

**Status: PDF FILED (author OA); mechanism (not a number) — no local value to verify.**

---

## Vita-Finzi, C. & Higgs, E.S. (1970). "Prehistoric Economy in the Mount Carmel Area of Palestine: Site Catchment Analysis." *Proceedings of the Prehistoric Society* 36:1–37. DOI 10.1017/S0079497X00013074. (Filed `literature/SiC_Games_AGG4_VitaFinziHiggs1970_SiteCatchment.pdf`. **[VERIFIED]** via pypdf 2026-07-05.)

**What was lifted — the site-catchment RADIUS (aggregation-sedentism / agriculture catchment, blueprints …_AggregationSedentism / …_AgricultureTier):** the "site exploitation territory" is defined by walking time from the site. **Hunter-gatherer / non-agricultural sites: ~10 km radius** (the 2-hour walking perimeter — "invariably lie comfortably within the 10 kilometre limit"). **Agricultural sites: 5 km radius** ("a circle with a radius of 5 kilometres, which we have taken as the economic [catchment]"; farming prosperity/return declines beyond ~3–4 km, topography appreciable between the 3 km and 5 km circle). **How used:** anchors `settle_catchment_radius` — in our 10 km cells, a **farming catchment ≈ 5 km = radius 0–1 cell**, an **HG catchment ≈ 10 km = radius 1 cell**; the built default `settle_catchment_radius=2` (≈20 km) is at/above the HG value → possibly trim to 1 for farming. **Status: [VERIFIED] — 5 km farm / 10 km HG.**

## Conklin, H.C. (1961). "The Study of Shifting Cultivation." *Current Anthropology* 2(1):27–61. DOI 10.1086/200161. (Filed `literature/SiC_Games_AGG5_Conklin1961_ShiftingCultivation.pdf`. Read via pypdf 2026-07-05.)

**What was lifted — the SWIDDEN crop→fallow cycle (agriculture tier Layer B soil, blueprint …_AgricultureTier):** the definitional/bibliographic anchor for shifting cultivation — integral vs partial swidden; the sequence clearing→cutting→burning→**cropping**→**fallowing**; **field-forest rotation** (a plot is cropped briefly, then fallowed to regenerate). **How used:** the conceptual warrant for Layer B1's PROGRESSIVE soil exhaustion under continuous cropping + slow FALLOW regrowth after abandonment (the swidden cycle), and the emergent relocation of Layer B3. **CAVEAT:** this is a *definitional review* — it does NOT give a single canonical crop/fallow duration (those are system-specific; the quantitative R-value synthesis is Ruthenberg 1971, NOT filed). The model's `soil_regrow_per_yr≈0.06` (~17 yr fallow) is a provisional bracket, not a Conklin-fitted value. **Status: FILED; CONCEPTUAL (no single fitted number here).**

## Ames, K.M. (1994). "The Northwest Coast: Complex Hunter-Gatherers, Ecology, and Social Evolution." *Annual Review of Anthropology* 23:209–229. DOI 10.1146/annurev.an.23.100194.001233. (Filed `literature/SiC_Games_AGG6_Ames1994_NorthwestCoast.pdf`. **[VERIFIED]** via pypdf 2026-07-05 — UPGRADES the prior reference-only citation.)

**What was lifted — NW-Coast VILLAGE SIZE + the storage→intensification→complexity chain (R-52/R-53; blueprint …_AggregationSedentism):** NW-Coast **villages/towns "ranging from only a few score to over a thousand people"** (~40 → 1000+ residents) — the multi-band-coalescence village-size benchmark; coast pre-contact population estimated **~188,000** (Boyd). Complexity driven by **salmon abundance + reliance on STORAGE + population-size thresholds** → intensification, sedentism, ranking; **owned resource rights** ranging from individuals to villages (the heritable-ownership → ascribed-rank bridge, deferred blueprint 5b/Q7). **How used:** grounds (a) the emergent village-size target (100s), (b) the fishery-stability + storage benchmark (R-53: NW-Coast villages stable for millennia), (c) the ownership→rank material basis. **Status: [VERIFIED] — village ~40–1000+; storage/salmon intensification.**

---

## Skill-by-age / embodied capital (forage-cap v2): Walker et al. 2002; Gurven, Kaplan & Gutierrez 2006; Koster et al. 2020

- **Walker, R. et al. (2002).** "Age-dependency in hunting ability among the Aché." *J. Hum. Evol.* 42:639–657. DOI 10.1006/jhev.2001.0541. (`literature/SiC_Games_SK1_Walker2002_HuntingAgeDependency.pdf`, **[VERIFIED]** pypdf.) Hunting outcomes **peak surprisingly LATE, significantly AFTER strength peaks** → productivity is **skill/embodied-capital-driven, not strength**.
- **Gurven, M., Kaplan, H. & Gutierrez, M. (2006).** "How long does it take to become a proficient hunter?" *J. Hum. Evol.* 51:454–470. DOI 10.1016/j.jhevol.2006.05.003. (`…SK2_Gurven2006…`, **[VERIFIED]** pypdf.) **Hunting success peaks age 35–50; other FORAGING & fishing peak ~age 20**; skill rises age 10→40.
- **Koster, J. et al. (2020).** "The life history of human foraging: cross-cultural and individual variation." *Sci. Adv.* 6:eaax9070. DOI 10.1126/sciadv.aax9070. (`…SK3_Koster2020…`, filed; cross-cultural age-productivity curves + individual variation.)

**What is lifted (forage-cap v2):** the per-person forage cap gets an **age-skill factor** — for FORAGE (not hunting) the productivity curve **peaks ~age 20** with a juvenile ramp (10→20) and gentle later decline (Gurven). The "hereditary" component is **embodied capital** (learned, age-accumulated, culturally transmitted parent→child — Walker: skill not strength) → modelled via the existing `cred`/lineage cultural-transmission machinery, NOT a genetic trait. Grounds `forage_cap(agent,cell) = forage_kcal·hours·age_skill(agent)`. MODEL_SPEC §4.8.21 / §4.1.

**Status: FILED; Walker + Gurven [VERIFIED] (forage peak ~20, hunting ~35–50, skill-driven); Koster filed. Grounds forage-cap v2 age-skill.**

---

## Settlement decision + band-fission payoff (village-nucleation arc): why settle, how find a place, why exceed band scale

**A) Why bands settle (sedentism):**
- **Binford, L. (1980).** "Willow smoke and dogs' tails: hunter-gatherer settlement systems…" *Am. Antiquity* 45:4–20. Forager↔COLLECTOR continuum: collectors REDUCE residential mobility, settle near concentrated key resources + forage logistically (temperate/boreal, patchy resources). [SEARCH-VERIFIED; PDF paywalled — TO-GRAB]
- **Testart, A. (1982).** "The significance of food storage among hunter-gatherers…" *Current Anthropology* 23:523–537 (+ **Woodburn 1982** immediate/delayed-return). STORAGE of seasonal glut → sedentism + density + inequality: storage converts a seasonal peak into year-round sustaining capacity. [SEARCH-VERIFIED; paywalled — TO-GRAB]

**B) How they find a place (site selection):**
- **Kennett, Anderson & Winterhalder (2006); Kennett (2005) Channel Islands; Jazwa/Winterhalder (2010)** *J. Anthropol. Archaeol.* — IDEAL FREE DISTRIBUTION applied to settlement: settle HIGHEST-suitability habitat first; density-dependent suitability decline pushes to next-best. **Habitat-suitability ranking = the site-appraisal mechanism — the SAME IFD our model runs, but evaluated at CATCHMENT scale.** [SEARCH-VERIFIED; PDFs paywalled/RG — TO-GRAB]
- **Vita-Finzi & Higgs (1970)** site catchment (already in MODEL_SPEC §4.8.21 as AGG4); **Orians & Pearson (1979)** central-place foraging; **Jochim (1976)** predictive settlement (water/arable/ecotone).

**C) Why exceed band scale — the FISSION PAYOFF (the >45 ceiling):**
- **Johnson, G. (1982).** "Organizational structure and scalar stress." SCALAR STRESS: in-group conflict/coordination cost rises super-linearly with n (~pairwise) → bands FISSION at ~25 ("magic numbers" 6 & 25). Remedies: fission, HIERARCHY (vertical decision-making DISSIPATES scalar stress), or ritual. When landscape fills/mobility limited → hierarchy evolves instead of fissioning. [SEARCH-VERIFIED; chapter paywalled — TO-GRAB]
- **Alberti, G. (2014).** "Modeling Group Size and Scalar Stress by Logistic Regression." *PLOS One* 9:e91510. Quantitative scalar-stress thresholds. (`literature/SiC_Games_SET3_Alberti_ScalarStress2014.pdf`, SAVED, 15 pp.)
- **Handley, C. & Mathew, S. (2020).** "Human large-scale cooperation as a product of competition between cultural groups." *Nat. Commun.* 11:702. Intergroup COMPETITION selects for large-scale in-group cooperation. (`literature/SiC_Games_SET2_Handley_CulturalGroupCompetition2020.pdf`, SAVED, 9 pp.)
- **Turchin (multilevel selection / asabiya); Carneiro (1970) circumscription.** WARFARE is the selective force overcoming the maintenance cost of large-scale cooperation; asabiya = capacity for collective action; large polities arise where interpolity competition is intense. **NOTE: the model's `assabiyah` seam IS Turchin's asabiya — its native driver in the lit is intergroup warfare (currently fed by surplus proxy).** [SEARCH-VERIFIED; Turchin escholarship PDF needs browser — TO-GRAB]

**Status: FILED. SAVED: Alberti 2014 (SET3), Handley & Mathew 2020 (SET2). TO-GRAB (paywalled/browser): Binford 1980, Testart 1982, Johnson 1982, Kennett/Winterhalder IFD-settlement, Turchin. Grounds the band-level catchment site-appraisal + cost-benefit fission ceiling (scalar-stress cost vs economic+military payoff vs hierarchy discount).**

---

## Storage calibration — stored fraction + granary duration (storage-realism recalibration, 2026-07-07)

- **Testart, A. (1982).** "The significance of food storage among hunter-gatherers." *Current Anthropology* 23:523–537. Storage-based HG; the stored seasonal resource is the *bulk* of subsistence through the lean. [SEARCH-VERIFIED; paywalled — TO-GRAB]
- **Halstead, P. & O'Shea, J. (eds.) (1989).** *Bad Year Economics: Cultural Responses to Risk and Uncertainty.* Cambridge UP. Four buffering strategies (mobility, diversity, STORAGE, exchange). Storage plays a DUAL role: **annually** it bridges the seasonal lean; **long-term** it balances good years against poor harvests. Halstead's "NORMAL SURPLUS" — farmers routinely overproduce so an average-to-poor year still suffices → a standing reserve of order **~1 year beyond annual need**. [SEARCH-VERIFIED; book — TO-GRAB]
- **Kuijt, I. (2009).** "What Do We Really Know about Food Storage, Surplus, and Feasting in Preagricultural Communities?" *Current Anthropology* 50:641–644 (+ Kuijt & Finlayson 2009 PNAS predomestication granaries). Pre-domestication storage was **small-scale**; scaled up sharply after domestication. [SEARCH-VERIFIED; paywalled — TO-GRAB]
- **Tushingham, S. & Bettinger, R. (2013).** "Why foragers choose acorns before salmon: storage, mobility, and risk in aboriginal California." *J. Anthropol. Archaeol.* 32:527–537. Stored acorns = the main plant-calorie source; Karuk salmon + acorn (both stored) > ½ the diet. [SEARCH-VERIFIED; paywalled — TO-GRAB]
- **Traditional grain storage (ethnographic/FAO):** ~50–70% of household production is stored (consumed over the year + seed); post-harvest storage **losses ~10–30%/yr** traditional (up to 50–60% worst-case, pests/spoilage). California acorn granaries held ~a year's supply (refilled each fall); NW-Coast stored salmon covered the ~5–7-month winter as the diet's bulk.

**CALIBRATION TARGETS (this survey):** (1) **stored fraction** of the seasonal surplus ≈ **0.5–0.8** (strongly-seasonal storers live mostly off stores); (2) **granary DURATION / capacity ≈ 1–2 years** of subsistence (Halstead normal-surplus: ~1 yr annual cycle + ~1 yr bad-year buffer; high-variance up to 2–3 yr); (3) **decay ≈ 10–30%/yr**; (4) qualitatively, the granary must run a strong ANNUAL FILL→DEPLETE CYCLE (fill at glut, draw down deeply through the lean to a reserve floor = the buffer), NOT stay full. Model mapping: reserve_full=130k ≈ 1.73 mo BURN (Cahill-anchored 2026-07-08; was 100k) ⇒ `store_capacity_reserves` for 1–2 yr = **~7–14** (default 3 ≈ 5 mo is far too low); `storable_fraction` 0.5→~0.7; `storage_decay` 0.05/mo (~46%/yr) → **~0.02/mo (~22%/yr)**. See RESULTS (pending), MODEL_SPEC §4.8.21.

**Status: FILED (all TO-GRAB, paywalled/book); targets SEARCH-VERIFIED. Grounds the storage recalibration.**

---

## Pre-run audit anchors (substrate scale run; 2026-07-08)

Anchors verified/added while auditing the run-A-critical constants (register: `SiC_Games_PreRun_Audit.md`; numbers:
`PARAMETERS.md`). Numbers repeated here so each has a lit home.

### Cahill, G.F. (1970). "Starvation in man." *New England Journal of Medicine* 282:668–675. (& Cahill 2006, *Annu. Rev. Nutr.* 26:1.)
**What was lifted — the starvation-bust threshold (`reserve_full_kcal` / `reserve_floor_kcal`):** a normal-composition
adult's total mobilizable fuel ≈ **166,000 kcal** for a 70 kg reference man (fat ~141k + protein ~24k + glycogen
~0.9k); survival is unusual once **fat < ~3 kg AND body protein depleted > 50%** (≈ 40% body-weight loss / BMI < 10–11),
rarely beyond ~3 months of total starvation. **How used:** the agent reserve (body-energy store, kcal) — `reserve_full
= 130,000` (scaled to a ~60 kg lean HG adult), `reserve_floor = 20,000` (the ~3 kg-fat death residual). The model burns
FLAT (no adaptive hypometabolism), so survival = (full−floor)/BURN = 110k/2500 ≈ **44 days** total starvation — the
lean-adult range (hunger-strike deaths ~45–61 d). Corrected 2026-07-08 from 100k (32 d = too fragile → exaggerated
bust; the exact quantity the substrate run measures). **Status: SEARCH-VERIFIED (Cahill figures widely cited; PDF not
filed). Anchor: full 130k / floor 20k / ~44 d runway.**
**Citation tag:** [PARAMETER — starvation reserve full/floor] — BUILT (`KcalEconomyConfig`); PARAMETERS §13.

### Bar-Yosef, O. (1998). "The Natufian culture in the Levant, threshold to the origins of agriculture." *Evolutionary Anthropology* 6:159–177.
**What was lifted — minimum-viable-settlement size (`settle_min_pool`):** Natufian settlements span **small (~dozens)
→ medium (100–150 people) → large**, the largest permanent hamlets up to several hundred. **How used:** `settle_min_pool
= 40` = the small-settlement lower bound (min aggregation to found/hold a settlement). The village-size CEILING
(`village_gain`, an unanchored tuning knob) should let villages LAND in **~50–150** — checked in run A, not pre-tuned.
**Status: SEARCH-VERIFIED (PDF not filed). Anchor: 40 (min) … 100–150 (medium).**
**Citation tag:** [PARAMETER — settle_min_pool] — BUILT; PARAMETERS §(settlement).

### Cordain, L., Miller, J.B., Eaton, S.B., et al. (2000). "Plant-animal subsistence ratios and macronutrient energy estimations in worldwide hunter-gatherer diets." *Am. J. Clin. Nutr.* 71:682–692.
**What was lifted — per-biome diet MEAT FRACTION (`MEAT_FRAC`, terrain.py; splits cell yield into forage vs meat):**
Table 2 mean subsistence dependence by primary living environment (n = 63 societies); *hunted* fraction of the
terrestrial diet = hunted/(plant+hunted) at class-interval midpoints, fished column dropped. **Values (re-derived
exact 2026-07-08):** subtropical rainforest / Aché 50.5/91 = **0.55**; desert / !Kung 40.5/91 = **0.45**; tropical
grassland / Hadza 30.5/81 = **0.38**; temperate grassland 60.5/91 = **0.66**. **Status: SEARCH-VERIFIED (Table 2
arithmetic re-checked; PDF not filed). Anchor: Table 2 midpoints.**
**Citation tag:** [PARAMETER — MEAT_FRAC per biome] — BUILT (`terrain.py`); MODEL_SPEC §4.5.5.

### Run-A demographic anchors already filed (re-verified this audit — pointers, not new)
- **Binford 2001** (Constructing Frames of Reference) — forager **packing threshold 9.098 persons/100 km² = 0.091/km²**
  (`BINFORD_PACKING_PER_KM2`, the stratification-morph trigger). Web-re-verified CORRECT 2026-07-08. (Binford entries
  already in this log.)
- **Pelletier 1994** (Nutrition Reviews 52:409) — malnutrition→mortality is multiplicative/exponential; `mu_max = 2.5`
  is a CONSERVATIVE capped max (severe malnutrition 5–8×; child data applied broadly). Plausible, provisional.
- **Siler / Aché** mortality (a1..b3), **Tallavaara 2018** capacity, **Miami NPP (Lieth)**, **Köppen/Körner** tree-line
  — all filed above; unchanged by this audit.

---

## Emergent settlement-hierarchy anchors (village/connubium/fertility mechanisms; 2026-07-08…09)

Anchors for the R-58…R-64 settlement-hierarchy mechanisms (PARAMETERS §21; VERIFICATION_LOG for dates). Johnson 1982
(scalar stress), Vita-Finzi & Higgs (site catchment), Testart 1982 (storage), Wobst (connubium 500), Binford packing,
Tallavaara capacity are all filed ABOVE — these are the ones new this session.

### Wiessner, P. (1977). "Hxaro: A regional system of reciprocity for reducing risk among the !Kung San." PhD diss., Univ. Michigan. (& Wiessner 1982, in *Politics and History in Band Societies*.)
**What was lifted — SOCIAL CAPITAL / STANDING (P6, `enable_standing`):** `hxaro` gift-exchange partnerships require
**≥ 1 year of reciprocal gifting before the bond is "firm"**; each person sits in a network of paths, and **that
network is the bad-year insurance** (risk pooled across the region). Status is relational and slow-built. **How used:**
standing = a tenure-built relational facet of `base_status` (accrues ~63%/yr, `standing_tenure_rate=0.083`) that is
largely LOST on leaving one's community (`standing_leave_penalty`) — so departure forfeits food share, granary draw,
and mating access. Drives SELECTIVE dispersal (low-standing leave, established stay). **Status: SEARCH-VERIFIED (PDF
not filed). Anchor: ~1 yr to "firm".**

### Bocquet-Appel, J.-P. (2011). "When the world's population took off: the springboard of the Neolithic Demographic Transition." *Science* 333:560–561.
**What was lifted — the NEOLITHIC DEMOGRAPHIC TRANSITION (`enable_sedentism_fertility`):** the shift to sedentism/
farming **roughly DOUBLED the birth rate** (the best-documented prehistoric demographic transition), via shorter birth
spacing. **How used:** society-dependent lactational refractory (`SEDENTISM_IBI_MONTHS`: egalitarian 30 → complex 22 →
stratified 14 mo ⇒ ~1.8× birth rate at the stratified end). **Status: SEARCH-VERIFIED (abstract; PDF not filed).
Anchor: ~2× birth-rate rise.**

### Sellen, D.W. & Mace, R. (1999/2007). "Fertility and mode of subsistence: a phylogenetic analysis." *Current Anthropology* 40:483 (& related weaning-age work).
**What was lifted — the MECHANISM of the NDT fertility rise:** cross-cultural, higher dependence on agriculture
associates with **shorter birth intervals / earlier weaning** (storable weaning foods → shorter lactational
amenorrhea) — the proximate driver behind Bocquet-Appel's transition. **How used:** the direction + magnitude of the
`SEDENTISM_IBI_MONTHS` ladder (mobile foragers ~44 mo / !Kung Howell → farming ~24 mo). **Status: SEARCH-VERIFIED (PDF
not filed).**

### Cahill / Bar-Yosef / Cordain / Köppen-Körner — filed under "Pre-run audit anchors" (above).

### Boehm, C. (1993). "Egalitarian Behavior and Reverse Dominance Hierarchy [and Comments and Reply]." *Current Anthropology* 34(3):227–254.
**Status: FILED + [VERIFIED] — full text read 2026-07-17** (`literature/Boehm - 1993 - Egalitarian Behavior and Reverse Dominance Hierarchy.pdf`, 28 pp; obtained via the gwern research archive, extracted with `pymupdf`).

**What was lifted — the LEVELING term for the elite layer (the condition that must be DEFEATED before elites can emerge).**
Boehm's thesis is that forager egalitarianism is **not** a passive absence of hierarchy or a self-organizing ecological
by-product, but an **actively and intentionally maintained** political achievement — the section is titled *"Intentional
Leveling"*, and the abstract argues egalitarian society is "explained" chiefly by self-organizing factors when in fact
"such societies are deliberately" egalitarian. The rank-and-file form a **reverse dominance hierarchy**: the coalition of
followers dominates would-be dominators.

**Sample: n = 48 societies** reporting intentional behavior to control leaders' negatively-evaluated tendencies (Table 1)
— 12 North America, 11 Central/South America, 9 Africa, 5 Asia, 4 New Guinea, 3 Australia, 2 Oceania, 2 Mediterranean/
Mideast. Subsistence: nomadic gatherers/hunters/herders + sedentary gardening or herding tribesmen; ~half bands/tribes
with low-key leadership, a good number big-man societies or chiefdoms.

**The escalating sanction ladder (section headings):** criticism → **ridicule** → **disobedience** → desertion/ostracism →
**assassination**.

**QUANTITATIVE ANCHORS (the modelable ones):**
- **38 of 48 societies (79%)** exhibit behaviors that "terminated relations with an overly assertive individual or removed
  him from a leadership role"; a further **28 instances** of manipulation by social pressure.
- **Assassination reported in 11 of 48 societies (23%)** — the lethal tail of the ladder.
- **Sanction TRIGGERS**, of 47 behaviors motivating negative sanctioning: **dominating others as leader (14)**, **being too
  aggressive (13)**, ineffectiveness/partiality/unresponsiveness as leader (10), **"lack of generosity or monopolizing
  resources" (5)**, moral transgressions (3), meanness (2). *"The great majority of these misbehaviours involve dominance
  or self-assertion."*

**How it will be used (elite layer):** the leveling term — an aggrandizer who accumulates (monopolizes resources) or
dominates triggers a sanction whose escalation is anchored on the ladder above (removal ~79%, lethal ~23% of societies).
Elites can only emerge where this leveling is **defeated** (storable/defensible surplus that cannot be shared out,
circumscription, or scale beyond gossip-policing). Complements Testart 1982 (storage as the enabler) and Hayden
(aggrandizers as the driver). NB the model already has a "Boehm gate" (`leader_society_weight`) — this is its anchor.

### Testart, A. (1982). "The Significance of Food Storage among Hunter-Gatherers: Residence Patterns, Population Densities, and Social Inequalities [and Comments and Reply]." *Current Anthropology* 23(5):523–537.
**Status: FILED + [VERIFIED] — full text read 2026-07-17** (`literature/Testart - 1982 - The Significance of Food Storage Among Hunter-Gatherers.pdf`, 15 pp). **Obtained from the author's own site**
(`alaintestart.com/UK/documents/storage.pdf` — self-archived OA; note the host's TLS cert mismatches, fetched over
plain HTTP). **This closes the long-standing "TO-GRAB (paywalled)" flag on Testart in this file** — every prior
Testart citation in the docs was SEARCH-VERIFIED only; they can now be checked against the primary text.

**What was lifted — the STORAGE prime-mover (the enabling condition of the elite layer).** Testart's thesis is that
*storing* hunter-gatherers form a distinct economic type from *non-storing* ones, and that three traits covary with
intensive seasonal storage: **(1) sedentism** (a stored stock must be guarded/returned to, so residence follows the
store, not the resource), **(2) high population density** — storing foragers reach "among the highest known levels of
population density" for hunter-gatherers — and **(3) socioeconomic inequality**. The California and Northwest Coast
peoples are the type cases, and they "depart significantly from the commonly accepted definition of hunter-gatherer
societies," which is Testart's challenge to treating agriculture as *the* milestone in social history: the break is
**storage**, not farming. He also contrasts the **food-sharing** norm of non-storing foragers (§"Food sharing among
nonstoring hunter-gatherers") with the differential accumulation storage permits — the same immediate- vs
delayed-return axis Woodburn 1982 draws.

**How it is used / will be used:** already the anchor for the storage + delayed-return mechanics (§4.5.11, the morph
trigger, the overwintering granary). For the **elite layer** it supplies the *enabling condition*: storable surplus is
what lets accumulation escape the sharing norm — i.e. the thing that **defeats Boehm's leveling** (see the Boehm 1993
entry above). Chain: **storable surplus (Testart) → accumulation escapes sharing → leveling defeated (Boehm) →
aggrandizer capture of redistribution (Hayden, TO-GRAB) → durable elite.**

### Sahlins, M. (1968). "Notes on the Original Affluent Society." In Lee & DeVore (eds.), *Man the Hunter*, pp. 85–89 (discussion 9b).
**Status: [VERIFIED] — full text read 2026-07-17.** **No new PDF needed: it is a chapter of the *Man the Hunter*
volume ALREADY filed** (`literature/richard-b-lee-irven-devore-man-the-hunter.pdf`, 602 pp; Sahlins' contribution at
the "Notes on the Original Affluent Society / Speaker: Sahlins" section).

**What was lifted — the BASELINE the elite layer has to overturn.** Sahlins' point is not that foragers are rich but
that they **deliberately run below productive capacity**: he sets out to explain "the inner meaning of **running below
capacity**" — picking up Washburn's suggestion that "a 20–30 per cent use of productive capacity may prove quite
adaptive over the long run" — against the textbook orthodoxy in which "the **specter of starvation stalks the
stalker**." Foragers *could* produce more and do not.

**Why it matters for the elite layer:** surplus is therefore **not a technical given that appears whenever resources
allow** — it is a social outcome. An aggrandizer must actively *mobilise production past the customary level*, and
Boehm 1993 supplies the enforcement that holds it at the customary level (leveling), while Testart 1982 supplies the
escape route (storable surplus that cannot be shared out). **Sahlins = the baseline · Boehm = the enforcement ·
Testart = the escape · Hayden = the driver.** Corrects a naive "resources → surplus → elites" chain: the resources
were already there.


---

### Borgerhoff Mulder, M., Bowles, S., Hertz, T., et al. (2009). "Intergenerational Wealth Transmission and the Dynamics of Inequality in Small-Scale Societies." *Science* 326(5953):682–688. `[VERIFIED]`
**Status: FILED + [VERIFIED] — Table 1 & Table 2 read 2026-07-18** (NIH-PA author manuscript, 18 pp; extracted with
`pymupdf`, Table 2 recovered by POSITIONAL extraction — the landscape table transposes under linear text dump).

**Why it is the anchor for the elite layer's levy rate.** No source gives a chiefly-due PERCENTAGE — Sahlins 1972
and Ames 1994 were both read directly for one and neither has it (a verified negative). So `leader_share_frac` is
anchored on its OUTCOME, the way `leveling_strength` is on Boehm 38/48 and status→RS on von Rueden r≈0.19.

**The mapping is unusually clean: BHM's three wealth classes ARE the model's three status facets,** and their
Table 1 confirms it by what was actually measured per class —
| BHM wealth class | What they measured (Table 1, HG rows) | Model facet |
|---|---|---|
| **Embodied** | Aché hunting returns, Aché/Hadza body weight, Hadza grip strength, Hadza foraging returns | `prowess` |
| **Relational** | Ju/'hoansi exchange partners, Lamalera food-share partners | `cred` |
| **Material** | Lamalera quality of housing, Lamalera boat shares | `material` |

**Table 2 — importance (α), transmission (β) and inequality by economic system:**
| System | α embodied | α relational | α material | β material | **α-weighted Gini** |
|---|---|---|---|---|---|
| Hunter-gatherer | 0.46 | 0.39 | **0.15** | 0.17 | **0.25** (SE 0.04) |
| Horticultural | 0.53 | 0.26 | 0.21 | 0.09 | 0.27 (SE 0.03) |
| Pastoral | 0.26 | 0.14 | **0.61** | 0.67 | 0.42 (SE 0.05) |
| Agricultural | 0.27 | 0.14 | **0.59** | 0.55 | 0.48 (SE 0.04) |

**What was lifted:** (1) the **α weights** — the empirical importance of each status facet BY SOCIETY TYPE, which
is the coupling-weight row of the capital/operator matrix; (2) the **Gini targets** for the α-weighted composite;
(3) the **β material** gradient (0.17 forager → 0.55–0.67 pastoral/agricultural) as the future anchor for material
heritability. **The load-bearing caution: for foragers material carries only 15% of the weight** — so an elite
layer that stratifies on material alone is over-weighting the one class the ethnography says matters least at that
stage. BHM's own thesis is that inequality tracks *which* wealth class matters and *how heritable* it is, not how
much any one man takes. NB their headline Ginis are the α-weighted COMPOSITE; per-class Ginis live in their Table
S5 (supplementary, not in the author manuscript) — so the model must be compared on the composite, not on
material alone. Their own note: "material wealth types ... display higher Gini coefficients."

### Sahlins, M. (1972). *Stone Age Economics*. Aldine-Atherton. `[VERIFIED]`
**Status: FILED + [VERIFIED] — read 2026-07-18** (`literature/Sahlins - Stone Age Economics.pdf`, 363 pp, full text
layer). Distinct from the already-filed Sahlins 1968 "Notes on the Original Affluent Society" (Lee & DeVore).

**What was lifted — the OFFICE-vs-ACHIEVEMENT distinction (p.209), which is the succession model.** Contrasting a
Melanesian big-man economy (Siuai) with a Northwest Coast chiefdom (Nootka): *"The thin line of difference is this:
the Nootka leader is an officeholder in a lineage (house group), his following is this corporate group, and his
central economic position is ascribed by right of chiefly due and chiefly obligation. So centricity is built into
the structure. In Siuai, it is a personal achievement. The following is an achievement — a result of generosity
bestowed — the leadership an achievement, and the whole structure will as such dissolve with the demise of the
pivotal big-man."* ⇒ the two succession regimes coded as `succession_dissolve` (see MODEL_SPEC §4.9.2).

**Corollary that constrains the levy itself (p.136–137):** the Melanesian big-man does NOT levy — he *mobilises*.
*"Deploying his resources carefully, the emerging leader uses wealth to place others in his debt ... he constructs
a following whose production may be harnassed to his ambition."* Whereas *"A Northwest Coast chieftain is a lineage
head, and in this capacity is necessarily accorded a certain right to group resources. He is not obliged to
establish a personal claim by the dynamic of an autoexploitation put at the others' disposal."* **So a levy on
band output (`leader_share_frac` > 0) is by construction the CHIEFLY regime, not the big-man one** — which is why
the same flag pairs naturally with `succession_dissolve=False`.

### Smith, E.A. & Codding, B.F. (2021). "Ecological variation and institutionalized inequality in hunter-gatherer societies." *PNAS* 118(13):e2016134118. `[VERIFIED]`
**Status: FILED + [VERIFIED] — full text read 2026-07-18** (open access via PMC8020663). Sample: **89 Pacific-coast
North American hunter-gatherer societies** (34 Northwest Coast + 55 California), scored on a Hierarchy Index (HI,
0–3) and a Resource Index (RI).

**Headline correlation CONFIRMED:** *"the correlation between HI and RI was nearly as high (r = 0.766, n = 17) as
for the full sample (**r = 0.881, n = 89**)"* — the second figure is the one this project cites. (Recorded because
a first pass over a summarised fetch reported the figure as ABSENT; it is present. One fetch summary is not
verification — read the numbers.)

**Full result set:**
| Statistic | Value | What it measures |
|---|---|---|
| **r (HI ~ RI), full sample** | **0.881** (n=89) | resource structure ↔ institutionalized hierarchy |
| r (HI ~ RI), high-fish California | 0.766 (n=17) | the same within a sub-sample |
| Random-forests variance explained | 86% | six-variable model |
| GAM deviance explained | 71% | best model |
| pSEM: RI → hierarchy | β_std **2.16**, P<0.0001 | direct effect |
| pSEM: fishing-site ownership → hierarchy | β_std **0.96**, P=0.043 | direct effect |
| pSEM: RI indirect (via fishing ownership) | 0.70, P=0.317 | n.s. — RI acts DIRECTLY |
| Effect size: Resource Index | **0.37** | largest predictor |
| Effect size: latitude / longitude | 0.35 / −0.22 | |
| Effect size: fishing-site OWNERSHIP | 0.13 | |
| Effect size: **NPP productivity** | **0.04** | essentially nil |
| Effect size: offensive raiding | −0.01 | essentially nil |

**Two findings that bear directly on this model.** (1) **NPP productivity has an effect size of 0.04 — raw
productivity does almost nothing**, while resource STRUCTURE (RI) carries the result. This independently
corroborates R-65's correction that *storability, not NPP, is the axis* (a claim that had over-reached on
cross-world %stratified). (2) **Fishing-site OWNERSHIP is a significant direct predictor** (β_std 0.96, P=0.043) —
the economic-defensibility channel (`enable_economic_defensibility`) measured in the ethnographic record, and the
same phenomenon as Hayden 1995's "spatially restricted resource locations ... fishing rocks, weirs" precondition
for a hereditary managerial class. Converges with Dyson-Hudson & Smith 1978 (already filed).

**Note on offensive raiding (−0.01):** warfare does NOT predict hierarchy in this sample — relevant if a future
stage reaches for a conflict-driven stratification route.

---

### D'Altroy, T.N. & Earle, T.K. (1985). "Staple Finance, Wealth Finance, and Storage in the Inka Political Economy [and Comments and Reply]." *Current Anthropology* 26(2):187–206. `[VERIFIED]`
**Status: FILED + [VERIFIED] — full text searched 2026-07-18** (`literature/408830614-Staple-Finance-Wealth-
Finance-and-Storag-pdf.pdf`, 21 pp, text layer). Obtained specifically to test whether a **direct levy rate**
exists that would supersede R-84b's outcome-based anchoring of `leader_share_frac`.

**VERIFIED NEGATIVE on the levy rate — this was the best remaining candidate and it does not carry one.** The
paper's contribution is *structural*, not rate-based: it dichotomises state finance into **staple finance** (the
mobilisation of subsistence/utilitarian goods) and **wealth finance** (manufacture and procurement of valuables
and primitive money), and shows the Inka state shifting between them. Obligation is expressed as **corvée labour
(mit'a) assessed per household on a rotating basis**, *not* as a percentage of a household's product — so there
is no "the chief takes X%" figure to lift. **`leader_share_frac`'s anchor therefore stands as R-84b left it**
(BHM composite Gini). Record this so the source is not re-fetched for the same purpose.

**What it DOES supply — a storage-decay anchor we currently mark [DESIGN]:** *"the loss rate for maize is about
30% per year"*. Our stored-food/`material_decay` handling is unanchored (0.002/step ≈ 2.4%/yr). Note the 30%
figure is for **stored grain**, so it anchors the granary/food-store sink, NOT durable prestige goods (hides,
boat shares), which should decay far more slowly — the two must not share a constant. Also: ~**79%** of storage
in the Upper Mantaro Valley is accounted for by state finance, and ~**50%** of that storage sits away from
settlements — relevant if a later stage models storage as a *sited* facility rather than a per-agent stock.

**Charter note (`MECHANISM_CHARTER.md`):** staple-vs-wealth finance is precisely a **Conversion (C)** distinction
— staple finance moves subsistence (an X operator on food), wealth finance converts production into durable
valuables (a C operator, production → material). That the ethnography draws the same line the type system does is
a useful corroboration of the typing.

### Borgerhoff Mulder et al. (2009) — Supporting Online Material `[VERIFIED]`
**Status: FILED + [VERIFIED] — Table S4 read 2026-07-18** (`literature/borgerhoff-mulder.som.pdf`, 46 pp).
Supplies the **per-wealth-type Ginis** that the main-text Table 2 aggregates away, which is what makes a
FACET-BY-FACET comparison possible instead of only the α-weighted composite.

**Table S4 — forager populations (Gini, SE, N):**
| Population | Wealth type | Class | Gini | Model facet |
|---|---|---|---|---|
| Aché | Hunting returns | E | 0.237 | `prowess` |
| Aché | Weight | E | 0.064 | — |
| Hadza | Weight | E | 0.079 | — |
| Hadza | Hunting & gathering returns | E | 0.339 | `prowess` |
| Hadza | Grip strength | E | 0.191 | — |
| Ju/'hoansi | Social networks | R | 0.216 | `cred` |
| Lamalera | Food-sharing partners | R | 0.263 | `cred` |
| Lamalera | **Quality of housing** | M | **0.241** | `material` |
| Lamalera | **Boat shares** | M | **0.474** | *no analogue* |
| Lamalera | RS | E | 0.296 | — |

**Model comparison (R-84b config, leveling ON, `leader_share_frac`=0.20):** `prowess` 0.24–0.26 vs the
returns-based embodied measures 0.237/0.339 ✓; `cred` 0.27 vs relational 0.216/0.263 ✓; `material` **0.237 vs
housing 0.241** ✓ — a near-exact match on the comparable category.

**The sharpened diagnosis this permits.** R-84b recorded model material Gini as "low" against the composite. It
is not: it matches **housing** (a consumption good) almost exactly. The entire gap is **boat shares (0.474) — a
PRODUCTIVE ASSET**, which the model has no analogue for. `material` is currently a consumption/prestige stock
only. **A means-of-production capital that raises its owner's yield is therefore a specific, identified gap** —
and the likely missing piece behind TARGETS T-5's agricultural arm (0.435 vs 0.48), since a productive asset is
also the natural thing to make heritable (BHM material β 0.17 forager → 0.55–0.67 agricultural).

### Hawkes et al. 1991 — text-layer copy filed (2026-07-18)
`literature/Hawkes-HuntingIncomePatterns-1991.pdf` and `literature/hawkes-1991-pdf.pdf` both carry full text
(~50k chars), replacing the image-only original for search purposes. The original scan is retained. No values
re-derived yet — the pooled savanna return rates in the Resource Return-Rate Table stand.

### Flannery, K. & Marcus, J. (2012). *The Creation of Inequality: How Our Prehistoric Ancestors Set the Stage for Monarchy, Slavery, and Empire*. Harvard University Press. `[FILED — all 24 chapters, text layers verified]`
**Status: FILED 2026-07-18** — supervisor supplied all 24 chapters individually (`literature/Flannery-*.pdf`,
591 pp total). **Text layers verified on every file; zero image-only**, so all are greppable (Rule 16 applies —
grep the specs first, then these).

**Not yet read.** Priority order for extraction when the elite layer next advances, with why:
1. **`Flannery-InequalitywithoutAgriculture-2012.pdf`** (ch. 5, p.66, 24 pp) — inequality among foragers WITHOUT
   farming. This is the stage the model is currently at; the direct check on R-83/R-84.
2. **`Flannery-RiseFallHereditary-2012.pdf`** (ch. 10, p.187, 24 pp) — hereditary inequality in farming
   societies, and note the **FALL**: documented cases of hereditary inequality COLLAPSING, which is the
   ethnographic counterpart to **H-CYCLES** (charter §5) and to DE-14's three negatives.
3. **`Flannery-TurnRankStratification-2012.pdf`** (ch. 16, p.313, 27 pp) — the rank→stratification mechanism,
   i.e. exactly what TARGETS **T-5's agricultural arm** (0.435 vs 0.48) is failing to produce.
4. **`Flannery-ThreeSourcesPower-2012.pdf`** (ch. 11, p.208, 22 pp) — a three-way power typology; a live test of
   whether the MECHANISM_CHARTER's operator categories match an independent anthropological decomposition.
5. **`Flannery-PrestigeEqualityFour-2012.pdf`** (ch. 9, p.153, 33 pp) — four Native American comparative cases;
   bears on **T-8**'s untested structural split (deposition in centralized vs desertion in mobile societies).

Remaining 19 chapters (Parts IV–V, kingdoms/empires/resistance) are beyond the model's current horizon and are
filed for later stages, not queued.

### Flannery & Marcus 2012 — EXTRACTION from the 5 priority chapters (read 2026-07-18) `[VERIFIED]`

**Ch. 11, "Three Sources of Power in Chiefly Societies" — Goldman's Polynesian triad, an INDEPENDENT
decomposition that matches the model's facets and then splits one of them.**
- **mana** — sacred life-force. *"people of high rank were automatically born with more mana"* ⇒ **ASCRIBED,
  heritable** = `cred`. The chief is the man with the most; so much that he is *tapu*.
- **tohunga** — *"expertise"*: administrative, diplomatic, ritual, or craft. *"individuals could increase their
  expertise through education, training, or apprenticeship"* ⇒ **ACHIEVED, learnable, SPECIALISED**.
- **toa** — bravery/martial prowess. Critically: *"A key aspect of toa was that it allowed for a certain degree
  of social mobility. A warrior of humble birth could rise in prominence to the point where he had to be taken
  seriously, even by chiefly individuals."* ⇒ **the COMMONER'S MOBILITY CHANNEL.**

⇒ **The model's single `prowess` scalar conflates tohunga and toa.** Goldman/Flannery separate them, and give
them different *social functions*: expertise is cultivated and attaches to a role; martial prowess is the route
by which low birth is overridden. This is the empirical basis for the specialization design (charter §8) and it
says a warrior facet is not decoration — it is the mobility mechanism. Emphasis varies by society (Maori/Tikopia
lean mana; Samoa/Easter Island lean expertise + force; Tonga/Hawaii, *the most unequal*, use "the entire
playbook") — i.e. the WEIGHTS differ by society type, exactly as BHM's α does.

**Ch. 10, "The Rise and Fall of Hereditary Inequality in Farming Societies" — the ethnographic anchor for
H-CYCLES, and a warning about our own elite layer.**
- **Kachin gumsa/gumlao cycling** (Leach): societies *"shifting back and forth"* between ranked (**gumsa**) and
  egalitarian (**gumlao**) modes. Flannery: *"hereditary inequality was repeatedly created, **lasted for a few
  generations**, and then collapsed."* ⇒ **a documented secular cycle, with a PERIOD of a few generations
  (~60–100 yr).**
- **The mechanism is a DELAYED negative feedback.** Ambitious leaders adopt prestige behaviour, and *"it only
  increased their followers' resentment and hastened their overthrow."* Resentment **accumulates** and the
  overthrow comes generations later — not the within-step correction our Boehm leveling applies. **This is
  precisely the lag H-CYCLES predicts, observed in the field.**
- **Friedman's ENDOGENOUS scenario** (Flannery prefers it to Leach's, which needs Shan princes to intervene):
  hereditary rank is created by a **LEGITIMACY REINTERPRETATION**, not by accumulation. Successful lineages were
  not credited with hard work — *"they believed that one only obtained good harvests through proper sacrifices to
  the nats. The key shift in social logic was therefore from 'They must have pleased the nats' to 'They must be
  descended from higher nats than we are.'"* Once descended from the ruling nats, the lineage controls the land
  and is *entitled to tribute*.
- **THE WARNING, aimed straight at our elite layer:** *"if feasting were all it took to produce hereditary
  inequality, there would have been no achievement-based societies left for anthropologists to study."*
  Competitive feasting *"instead of creating hereditary rank ... produced individual Big Men who had no way of
  bequeathing renown to their offspring."*
- **The gumlao vs gumsa premise lists are effectively two config states.** gumlao: all lineages equal; villages
  autonomous; **no tribute owed to the headman**; equal bride-price; all siblings equal; splits produce no
  senior/junior; **"Each headman is to be advised by a council of elders."** gumsa: lineages ranked; all
  settlements under one chief; **"Everyone who does not belong to the chief's lineage must pay him tribute,
  usually in the form of a thigh from every animal sacrificed"**; elite bride-price higher; **ultimogeniture**
  (all property to the youngest son, to push older sons out to found new lineages); splits produce senior/junior.
- **A third path: DEBT SLAVERY** via the mayu-dama bride-price system (a groom owed cattle, slit-gongs, swords).

**Ch. 16, "How to Turn Rank into Stratification" — power-balance devices, as an explicit premise list.**
Tongan premises 13–17: *"No Tongan dares assassinate his own chief, owing to the latter's high levels of mana"*;
assassins can be **hired from other islands**; *"Dividing authority, by creating a line of secular chiefs that
will coexist with sacred chiefs, makes political assassination more difficult"*; but *"Secular chiefs, however,
pose the threat of usurpation"*; and *"To reduce the risk of usurpation, the sacred chief should limit the land
(and other resources) allocated to the secular chief."* ⇒ a **sacred/secular office split** as an explicit
anti-assassination + anti-usurpation control, with **resource allocation as the balancing knob.** Compare
Tikopia (ch. 11): *"The simultaneous presence of four chiefs acted as a system of checks and balances,
preventing one ambitious leader from taking over all of Tikopia."*

**Ch. 5, "Inequality without Agriculture"** — the NW Coast/Nootka case at our current stage: salmon surplus
beyond immediate consumption, and a social ladder whose **bottom rung is slaves** (*"could be bought, sold,
mistreated, or even killed"*), acquired by raiding and by **debt** (enslaving women and children from debtor
villages). Not yet extracted in detail; queued with ch. 9 (T-8's untested deposition/desertion split).

### Big-man BASE RATE search — VERIFIED NEGATIVE (2026-07-20)

**Question:** R-86v found the model's father->son leadership LIFT (1.43) cannot be compared to Hayden's 75%
without knowing what fraction of New Guinea men were big men — Hayden reports a raw fraction, not a rate
relative to a base. Searched for that base rate across the sources most likely to carry it.

**Checked, all negative:**
- **Hayden 1995 itself** (`literature/hayden1995.pdf`, full text, 72pp) — the source of the 75% figure. No
  population-level base rate given anywhere in the paper; the only proportions present are unrelated (violent
  death rates, subsistence percentages).
- **Sahlins, *Stone Age Economics*** (full text, 363pp) — extensive QUALITATIVE big-man material (the
  "rubbish man" contrast; "the success of only a FEW and the inevitable failure of the MANY"; the Kapauku
  "fish-tail" bifurcate household distribution) but no quantified fraction. The Botukebo village table
  (Table 3.4, Pospisil 1963) is 16 HOUSEHOLDS' sweet-potato production intensity, not a census of big-men vs
  commoners.
- **Flannery & Marcus ch. 6** ("Agriculture and Achieved Renown") and **ch. 9** ("Prestige and Equality in Four
  Native American Societies") — both read in full; neither contains proportion/percentage language for
  achievement-based leadership frequency.
- **Web search** — no secondary source states the figure either. Sahlins' foundational 1963 paper ("Poor Man,
  Rich Man, Big-man, Chief") is the most likely original home of such a number but is paywalled
  (JSTOR/Cambridge); not pursued via a mirror (project policy on copyrighted works).

**Read as a finding, not just a gap:** anthropologists describe big-man status as a GRADIENT (poor man ->
rubbish man -> ordinary man -> big man; Sahlins) rather than a threshold category, which is plausibly WHY no
source quantifies "the base rate" — there is no agreed population to divide by. **Qualitatively, every source
that touches the question agrees big men were a small minority** ("only a few" vs "the many," Sahlins), which
bounds the true lift ABOVE our model's 1.43 without fixing a value — consistent with, not contradicting, R-86v's
finding that the model under-produces concentration relative to the ethnography, but not something a number
can be anchored to.

**Standing conclusion for T-6:** the raw-fraction comparison (age-matched model 0.769 vs Hayden's 0.75) remains
the only available like-for-like check. Do not re-search for this base rate without a new source; log this as
the prior attempt.

### Karmin, M., et al. (2015). "A recent bottleneck of Y chromosome diversity coincides with a global change in culture." *Genome Research* 25(4):459-466. `[VERIFIED, FILED]`

**Why this was sought:** R-86v found Hayden's 75% father-was-leader figure has no stated base rate, so no lift
is computable against it (verified negative, logged 2026-07-20). Searched for a DIFFERENTLY-anchored source on
leadership/lineage concentration - one with real quantitative statistics rather than a raw ethnographic
fraction.

**What it is:** a population-GENETICS study, not an ethnographic one - 456 Y-chromosome sequences from diverse
world populations, reconstructing male effective population size (Ne) through time via coalescent methods.
Categorically different evidence from anything else anchoring this project: hard demographic inference from DNA,
not observer report.

**The verified statistic** (confirmed via two independent fetches converging on the same figure - the general
web search and a direct WebFetch of the PMC full text, which returned the quote verbatim): *"a reduction at
around 8-4 kya when the female Ne is up to 17-fold higher than the male Ne."* I.e. at the bottleneck's peak,
**female effective population size ran up to 17x male effective population size** - a small number of male
lineages produced a hugely disproportionate share of descendants, while female-mediated lineages did not
collapse the same way. Regionally staggered, tracking "the earlier spread of farming in the Near East, East
Asia, and South Asia than in Europe." Explicitly NOT limited to one or a few haplotypes - a general pattern
across the male line, not a single dynasty's fluke.

**THE CONVERGENCE, found by checking our own prior results rather than assumed:** this is the SAME signature
already reported, independently and before this literature search, in the SiC Games Carbon-civilization deep-
time campaign (R-66, 2026-07-13): *"patriline-name-fixation not equal to genetic"* and *"autosomal genome stays
diverse (H about 0.88): non-patrilineal maternal alleles keep flowing even as one surname dominates."* Karmin's
whole point is the same shape - the collapse is MALE-LINEAGE-SPECIFIC, not a general population bottleneck
(which would show in autosomal/maternal signal too). The model produced this qualitative pattern on its own,
unprompted, months before this source was found to anchor it.

**Companion citations, not yet followed up:** Balaresque et al. 2015 ("Y-chromosome descent clusters and male
differential reproductive success") and Poznik et al. 2016 (*Nat Genet* 48:593-599) - both cited alongside
Karmin in von Rueden & Jaeggi 2016 for the same bottleneck literature; may sharpen the number or extend it to
specific societies rather than a global average.

**STATUS: FILED 2026-07-20** (`literature/Genome Res.-2015-Karmin-459-66.pdf`, supervisor-supplied) **and
PRIMARY-SOURCE VERIFIED** - the extracted PDF text was checked directly against the quote above, word for word:
*"the Y chromosome plot suggested a reduction at around 8-4 kya... when the female Ne is up to 17-fold higher
than the male Ne."* Confirms the two independent fetches used to first find this were both accurate.

**Two bonus citations found in Karmin's own bibliography while verifying - SHARPER statistics than the aggregate
17x Ne ratio, each a direct "top lineage(s) -> % of population" number:**

- **Zerjal, T., et al. (2003). "The Genetic Legacy of the Mongols." *American Journal of Human Genetics*
  72(3):717-721.** DOI 10.1086/367774. `[VERIFIED, FILED 2026-07-21]`
  (`literature/Zerjal et al. - 2003 - The Genetic Legacy of the Mongols.pdf`, 5 pp, supervisor-supplied after an
  automated fetch failed: PMC serves a bot-detection interstitial, which was not worked around; Cell Press
  returns HTML; and Europe PMC holds no XML full text since 2003 AJHG predates structured deposit.)

  **PRIMARY-SOURCE VERIFIED**, checked against the extracted text: *"It was found in **16 populations**
  throughout a large region of Asia, stretching from the Pacific to the Caspian Sea, and was present at high
  frequency: **~8% of the men** in this region carry it"*; *"a single male line, probably originating in
  Mongolia, has spread in the last **~1,000 years** to represent ~8% of the males in a region stretching from
  northeast China to Uzbekistan"*; *"about **16 million men, ~0.5% of the world's total**"*.

  **A UNIT DISTINCTION THAT MATTERS FOR T-9, and it is NOT the same statistic as Yan's.** Zerjal's 8% is ONE
  NAMED lineage — notable for its recent, rapid, geographically vast expansion — and is **not claimed to be the
  largest** in that region. Yan's 16% (Oα) IS the modal clade. So:
  - **Yan 16% -> `top_share`** (largest lineage share). Like-for-like.
  - **Zerjal 8% -> NOT `top_share`.** It anchors a different quantity: how far and how fast a SINGLE elite line
    can expand — 0 to ~8% of a continent in ~1,000 years. The model's comparable measurement is the growth
    trajectory of one ascribed lineage, not the maximum over lineages.
  Quoting Zerjal against `top_share` would repeat the top-1/top-3 mismatch this file already had to correct
  once. Three sources, three DIFFERENT measurements: Karmin = aggregate Ne ratio; Yan = modal clade share;
  Zerjal = single-dynasty expansion rate and reach. - ONE Y-chromosome lineage, dated to
  ~1000 years ago and attributed to Genghis Khan, is carried by **~8% of men across 16 populations spanning the
  Pacific to the Caspian Sea** (~0.5% of the world total). A single elite dynasty's capture, at continental
  scale and with a named historical figure - about as close as population genetics gets to a Hayden-style
  "one aggrandizer's lineage" statistic, but with a real percentage attached.
- **Yan, S., et al. (2014). "Y chromosomes of 40% Chinese descend from three Neolithic super-grandfathers."
  *PLoS ONE* 9(8):e105691.** `[VERIFIED, FILED 2026-07-21]`
  (`literature/yan2014_three_neolithic_super_grandfathers_PLoSONE.pdf`, 7 pp, fetched from PLoS open access and
  checked directly against the extracted text.)

  **PRIMARY-SOURCE VERIFIED, and it supplies a BETTER statistic than the headline.** Verbatim: *"three strong
  star-like Neolithic expansions at ~6 kya ... indicates that ~40% of modern Chinese are patrilineal descendants
  of only three super-grandfathers at that time"*, and crucially the **PER-CLADE BREAKDOWN**: *"encompass more
  than 40% of the present Han Chinese in total (estimated **16% for Oα, 11% for Oβ, and 14% for Oγ**)"*.

  **THIS RESOLVES A UNIT MISMATCH (D6) that had made the target unusable as stated.** The headline 40% is the
  top-THREE combined, while the model's `dynasties()["top_share"]` is the top-ONE — not interchangeable, and an
  earlier plot of ours drew 40% as a line against top-one before the mismatch was caught and the line removed.
  The breakdown gives the correctly-matched number: **largest single clade = 16%**. For reference the model's
  measured `top_share` is 0.154 (R-93/R-94) and 0.192 (R-96) — the same order, on a like-for-like unit. - **three founder
  lineages account for ~40% of Chinese men**, from star-like expansions dated to ~6000 years ago (Neolithic,
  linked to the spread of agriculture). A small-founder-set dominance statistic, one level up from Zerjal's
  single dynasty.

**Together the three give three anchors at three scales of the SAME phenomenon** (patrilineal fixation under
social stratification), all hard genetic data: one elite lineage's continental capture (Zerjal, ~8%), a
small founder set's national capture (Yan, 3 lineages -> 40%), and the aggregate population-wide Ne collapse
(Karmin, 17x). None require guessing a base rate the way Hayden's 75% did.

**Proposed use:** see TARGETS T-9 - a replacement/supplement for T-6 that compares the model's OWN existing
`dynasties()` diagnostic against these three, at the level each is actually comparable: `top_share` (largest
single lineage's fraction) against Zerjal's ~8%; the summed share of the top 3 lineages against Yan's ~40%;
and `eff_lineages` (inverse-Simpson effective count), egalitarian vs stratified, against Karmin's ~17x Ne ratio.
