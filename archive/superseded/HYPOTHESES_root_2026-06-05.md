# SiC Games — Pre-registered Hypotheses

**Maintained by:** Claude Code, updated each stage. Supervisor approves new registrations.
**Protocol:** All hypotheses registered HERE and in ROADMAP.md before any run that
could test them. No HARKing. OPEN = registered, untested. IN PROGRESS = test underway.
SUPPORTED/REJECTED/NULL = outcome recorded with run reference.

\---

## §1 H1(ii) — Primary hypothesis (locked finding)

**Statement:** Si is more resilient than C under periodic resource shocks.
**Status: INVERTED (robust, 5/5 seeds at A=0.75, T=200). C survives; Si collapses.**
The inversion is structural (Si dormancy cliff at T > T\_dormant\_max). Not a model artifact.
**Reference:** Stage 5 report (outputs/stage5/report\_stage5.html). Si T\* ∈ (68,87), C T\* > 500.

\---

## §2 H-ORTHOGONALITY — C/Si home-range decomposition (OPEN, 2026-05-30)

**Statement:** The home-range distributions of C and Si agents occupy orthogonal
axes of the foraging×social movement space: C home-range is primarily shaped by the
social-pull (ψ proximity term); Si home-range is primarily shaped by foraging-pull
(sugar gradient). These two distributions are predicted to be non-parallel — a
difference-set, not just a scale difference — because the signals driving movement
are categorically different (C2 classification in MODEL\_SPEC §0).

**Prediction:** When movement is decomposed into foraging-pull vs social-pull
(OWE-13 diagnostic), the C foraging fraction will be significantly lower and the
social fraction significantly higher than in Si, across ⟨ρ⟩ and A conditions.
This is orthogonality, not merely a ranking.

**Test requirements:**

1. OWE-13 movement-decomposition diagnostic built and validated.
2. Matched C/Si runs at medium-⟨ρ⟩, static world (unshocked) — at least one density
where both populations survive to t≥2000 steps post-transient.
3. Per-step per-agent decomposition logged; population medians extracted.

**Status:** OPEN — pre-registration only. Test not run. Required diagnostic (OWE-13)
not yet built. No HARKing risk.

**Related:** OWE-8 (difference-set axis enumeration); MODEL\_SPEC §3 C2 flag on ψ;
MODEL\_SPEC §2.3 (ψ channel: cultural vs physical — unresolved; orthogonality test is
informative regardless of resolution).

\---

## §3 H-instinct-debt — Energy cost of culturally-mandated exploration (OPEN, 2026-05-30)

**Statement:** Cultural transmission (Deffuant) imposes an "instinct debt" on C
agents: the social-pull component of movement (ψ proximity term) draws agents away
from optimal foraging patches toward socially-valued locations. Under resource stress,
this instinct debt becomes a metabolic liability — C agents die at higher wealth
levels than Si agents (before they would starvation-starve) because the social pull
prevented them from reaching the nearest high-sugar cell.

**Prediction:** In deep troughs (seasonal A ≥ 0.75), the distribution of terminal
wealth at death is bimodal for C (one mode near-zero = true starvation; one mode at
2–5× metabolism = "instinct-debt death"), whereas Si deaths cluster near the dormancy
threshold k\_dormant × metabolism (= 1×metabolism = dormancy trigger). The C instinct-
debt mode is absent or suppressed in runs with ψ=0 or c2\_defection turned off.

**Test requirements:**

1. OWE-13 movement-decomposition diagnostic.
2. Terminal-wealth-at-death histogram logged per strategy per trough phase.
3. Matched C runs: default ψ vs ψ=0 (or ψ social term disabled).
4. ≥5 seeds to distinguish signal from demographic noise.

**Prerequisite:** H-ORTHOGONALITY partially confirmed (if C social fraction is not
meaningfully higher than Si's, the instinct-debt mechanism has no pathway).

**Status:** OPEN — conceptual pre-registration. Not yet testable. Both OWE-13 and
the ψ=0 control run design are pending.

\---

## §4 H\_cc — C carry-discount counter-cyclical recovery (partially supported)

**Statement:** The carry\_discount birth ceiling (max(0, 1 − N\_C/N\_carry)) produces
a counter-cyclical birth boost during troughs: as N\_C falls during trough, the
discount decreases, P\_birth rises, accelerating recovery. C trough-recovery speed
is therefore faster than a DTM-formula-alone prediction.

**Registered:** Stage 4.5 patch (2026-05-28).
**Status:** Regression-supported at Stage 5 (single-seed). Pending multi-seed at
A=0.9 (5+ seeds). See ROADMAP Pre-registered Hypotheses table.

## §5 H-SUBSTRATE-6.0a — Multi-occupancy substrate viability (OPEN, 2026-06-03)



\*\*Statement:\*\* This is a substrate pre-registration, not a theory-bearing hypothesis.

It records the sanity readings committed before the Stage 6.0a §7.2–7.4 behavioural

numbers are seen, so a sane/insane substrate cannot be reinterpreted after the fact.

The generalised multi-occupancy substrate (resource-split harvest, Cred-weighted

contest for C, diffusion movement) is predicted to be a viable, physically-plausible

generalisation of the one-agent-per-cell model.



\*\*Pre-committed readings (state before the run):\*\*



1\. \*\*C viability (κ=0 and κ=1).\*\* N(t) settles to a stable band — neither extinction

&#x20;  nor unbounded growth — within the ≥2000-step run.

&#x20;  - Settles, both κ → substrate viable; proceed.

&#x20;  - Crashes to extinction or pins/explodes → substrate broken or per-capita-need vs

&#x20;    regrowth miscalibrated; blocking, investigate before 6.0b.



2\. \*\*Self-limiting density.\*\* Per-cell occupancy stabilises (per-capita intake →

&#x20;  metabolic break-even), not unbounded crowding or overcrowding-collapse to zero.



3\. \*\*Density vs ethnography (flat terrain).\*\* Steady-state persons/km²

&#x20;  (agents/cell ÷ 100) lands order \~0.1, within \~0.01–1.

&#x20;  - Inside band → scale calibration sane for 6.0b.

&#x20;  - Outside band → per-capita-need vs sugar-regrowth miscalibrated for the declared

&#x20;    100 km²/cell; calibration flag, investigate before 6.0b. (The full harsh/fertile

&#x20;    10–100× spread is a 6.0b target, NOT expected here.)



4\. \*\*Cred–wealth concentration (κ=1 only) — OBSERVE AND DEFER.\*\* Cov(φ,wealth) and the

&#x20;  Cred distribution are logged. A rising covariance with a collapsing Cred

&#x20;  distribution toward a single dominant high-φ lineage is recorded as a

&#x20;  \*\*Matthew-runaway flag\*\*. Per Stage 6.0a §7.2 / §10, 6.0a does NOT mitigate and this

&#x20;  pre-registration does NOT pre-commit an interpretation: the flag is observed, its

&#x20;  magnitude reported, and any design response (mitigation sub-stage vs accept) is a

&#x20;  deliberate post-review decision, not a pre-judged outcome. Logged as a measurement

&#x20;  commitment only.



5\. \*\*N\_carry / N ratio.\*\* The settled N and whether it sits in a viable band are

&#x20;  reported as evidence toward the deferred N\_carry reconciliation (design doc, not

&#x20;  6.0a). No threshold pre-committed; descriptive only.



\*\*Test reference:\*\* Stage 6.0a §7.2 (C-behavioural, κ=0 vs κ=1, ≥2000 steps), §7.3

(density validation), §7.4 (N\_carry flag). Recovery gate §7.1 already PASSED

bit-identically (243 tests green).



\*\*Status:\*\* OPEN — pre-registration only. §7.2 behavioural runs not yet executed.

\---

*End of HYPOTHESES.md — last updated 2026-05-30*

