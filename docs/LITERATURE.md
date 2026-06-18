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

### Tallavaara, M., Eronen, J.T. & Luoto, M. (2018). "Productivity, biodiversity, and pathogens influence the global hunter-gatherer population density." *PNAS* 115(6):1232–1237. Data/script: Zenodo record 1069787.

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
- Cross-HG: e₀ 21–37; modal adult death avg 72; adaptive lifespan 68–78.

**Use:** Siler coefficients FIXED as constants (M-1), converted per-month (÷12). G&K Table 2 is both-sexes; sex-specific + maternal-removed (M-3) fits to come from Hill & Hurtado.

**Provenance:** extracted from the open-access PDF (Table 2) via pdfplumber word-coordinate reconstruction (table rendered RTL), cross-checked two independent ways. PDF now filed in `literature/` (`Gurven and Kaplan - 2007 - Longevity...pdf`) — treat as confirmed; spot-check at final lock.

**Citation tag:** [USED — demographic Siler anchor (M-1); coefficients pending re-verification vs filed PDF]
