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
