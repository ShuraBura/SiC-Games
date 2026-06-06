# SiC Games — Targets (TARGETS.md)

**Purpose:** The home for **emergent behaviours the project is shooting for** — qualitative
phenomenology we hope the model produces — that are *not yet* formal predictions. This is the
deliberate counterpart to HYPOTHESES.md: a place for generative ideas to live honestly,
without masquerading as pre-registered predictions.
**Maintainer:** Supervisor curates; Claude Code maintains.
**Created:** 2026-06-05.

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

*End of TARGETS — seeded 2026-06-05. Graduate a target by moving it to HYPOTHESES with a test
spec; never mark a target "confirmed."*
