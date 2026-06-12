# SiC Games — Stage 6.0a-perf: Substrate Performance Reconnaissance

**Type:** Exploratory profiling-and-acceleration study. **Not** a verdict-by-assertion stage.
The deliverable **is** a report — this is the named exception to the run-to-green default,
because the thresholds to be discovered cannot be pre-committed (the point is to *find* the cost
surface, not assert it).

**Filing:** Side-numbered study hanging off Stage 6.0a (substrate, complete). It does **not**
advance the science spine — 6.0b (terrain) remains the next science step. This is a utility
reconnaissance pass about what the substrate can afford.

**Latitude:** CC has real decision latitude here — try several acceleration approaches, choose
sensible sweep points and window lengths, and decide which variants to pursue. The cage is
**documentation discipline**, not per-step approval. CC runs this to completion and reports; no
mid-run check-in.

---

## 0. Why this stage exists

The existing `SiC_Games_Perf_Audit.md` is **stale**: it profiled the one-agent-per-cell
Sugarscape paradigm with ~2000 agents. The current substrate (Stage 6.0a) is a different machine —
multi-occupancy, resource-split harvest, Cred-weighted contest, diffusion movement — with new
per-step costs that did not exist when the old audit ran. Its scaling exponents do not describe
the current code.

Separately, Stage 6.0a §7.2 showed the substrate settles at ~2 agents/cell — ~100× below the
ethnographic density the spatial scale was declared to produce. Correcting density to an
ethnographic / proto-agricultural target (a later calibration step) will require **far more agents
than the current ~2000-agent runs** — plausibly tens of thousands. The old runs were only
affordable *because* the substrate was too sparse. So before any density calibration or grid-size
decision, we need a fresh, honest read of the current architecture's cost surface and what agent
counts are reachable.

**This stage answers one question:** across grid size, total N, and per-cell occupancy, *where
does it start to hurt* — i.e. what scale points run at an acceptable ms/step and where does cost
become prohibitive? Reconnaissance to get a *feel*, not a committed config. Config selection and
any long-run drift characterisation are later, deliberate steps — explicitly **out of scope here**.

---

## 1. Scope

### In scope
1. Fresh profiling of the **current substrate** to find where per-step time actually goes now.
2. Implement and benchmark **cheap acceleration** on the hot paths: numpy-vectorisation and
   Numba (`@njit`). CC may try variants freely.
3. Measure how cost scales across three axes: **grid size, total N, and per-cell occupancy** —
   the occupancy axis is new under multi-occupancy and may dominate (contest/split are
   per-occupant-per-cell operations).
4. A scale sweep with a **two-tier ms/step cutoff** (§5) to map the affordable region.
5. A **forward assessment** (analysis, not implementation) of heavier acceleration paths.

### Out of scope (do NOT do in this stage)
- **No drift characterisation.** Do not run configs long to study whether ms/step climbs over a
  run's lifetime. That is a later forerun, performed once a candidate config is chosen. Here, runs
  go only to a short measurement window (§5).
- **No config selection.** Do not pick the grid/density/N the project will use. This stage informs
  that choice; it does not make it.
- **No heavy implementation.** Cython, GPU/JAX, and any array-based-scheduler / Mesa-replacement
  rewrite are **assessed and projected in the report only** — not built.
- **No science runs, no Si, no H1(ii) work.** Pure performance reconnaissance.

---

## 2. Acceleration latitude

CC may implement and benchmark, on any hot path it identifies (candidates: growback,
harvest-split, Cred-weighted contest, occupant-set / spatial-hash construction, diffusion
movement):

- **numpy vectorisation** — replace per-cell / per-agent Python loops with array operations. The
  growback vectorisation earmarked in the old audit (target: drop grid exponent toward ≤2.0) lands
  here. Same coding style as the existing codebase, no new heavy dependencies.
- **Numba (`@njit`)** — JIT-compile hot numerical functions. CC must *test* whether it applies
  cleanly given Mesa's object-oriented agents (it may not, on some paths); report where it works
  and where it doesn't rather than assuming.

CC chooses which variants to pursue and may iterate. Every variant that is **reported as a timing
result must have passed the plausibility rails (§3)** on the run that produced its timing —
otherwise the speedup is measuring a broken model and does not count.

**Heavier paths — ASSESS, do not implement.** In the report, give a reasoned projection of the
achievable ceiling under each of: Cython, GPU/JAX, and a full array-based "agents as matrix rows"
restructuring (replacing per-agent Python objects). Enough analysis to judge whether
proto-agricultural density is reachable on the cheap paths alone or would require one of these.
This is the input to a later architecture decision made in the design chat, not here.

---

## 3. Validity: plausibility rails (the only validity judgment)

A run is **valid** if it behaves like a semi-correctly-working model. There is **no comparison to
any previous model version** — the old model had different dynamics (different agent count,
one-agent-per-cell) and is not a reference for anything here. Validity is judged solely against
these instinct-grounded rails:

1. **Population stays in a finite band** — no explosion to the N_carry ceiling held indefinitely,
   no collapse to extinction within the measurement window.
2. **Density settles** — per-cell occupancy does not diverge (no unbounded crowding) and does not
   collapse to zero.
3. **No single-cell pile-up** — population does not concentrate into one or a handful of cells
   (a sign of a broken movement or harvest path).
4. **Conservation holds** — sugar harvested equals sugar removed from the world each step (no
   creation/destruction leak); within floating-point tolerance.
5. **No NaNs / no infinities** in wealth, Cred, position, or population.

If CC identifies an additional rail that a working model should obviously satisfy, it may add it
and document the addition. Do **not** over-engineer the rail set — these five plus any obvious
omission are enough. A run that fails a rail is logged as **invalid**; its timing is not reported
as a valid data point, and the failure itself is recorded (it may indicate an acceleration bug or
a scale regime where the model misbehaves — both are findings).

---

## 4. Measurement protocol

For each scale point in the sweep (§5), measure:

- **ms/step** — the primary quantity. Mean and a dispersion measure (SD or IQR) over the
  measurement window, excluding an initial warm-up of the first few steps (CC chooses warm-up
  length, documents it).
- **Per-hot-path breakdown** — where the ms/step goes (profile the substrate; `cProfile` or
  equivalent on a representative config; CC chooses which configs get the full profile, documents
  the choice). At minimum, profile one cheap config and one expensive config so the breakdown's
  *change* with scale is visible.
- **Peak and mean per-cell occupancy** reached in the window (so the occupancy axis is measured,
  not just configured).
- **Plausibility-rail status** (§3) — pass, or which rail failed.

### Scaling exponents
From the sweep, fit and report the cost exponent along each of the three axes **independently**,
under multi-occupancy:
- **Grid exponent** — ms/step vs grid cells, N and occupancy held roughly fixed.
- **N exponent** — ms/step vs total N, grid and occupancy held roughly fixed.
- **Occupancy exponent** — ms/step vs agents-per-cell, grid and N held roughly fixed. **This is
  the new axis and the one most likely to gate proto-ag density** — report it carefully.

CC chooses how to hold axes fixed and documents the design. Approximate fits are fine — this is a
feel for the surface, not a precision measurement.

---

## 5. Scale sweep and the two-tier cutoff

### Sweep
Climb the scale points to map where cost becomes prohibitive. CC chooses sensible rungs and
documents them; suggested spans:
- **Total N:** rungs from current (~2k) climbing through ~10k, ~30k, ~60k, ~100k.
- **Grid:** ~30×30 up to 100×100.
- **Occupancy:** from ~1/cell up to the proto-agricultural regime (~100/cell), set by the
  N-vs-grid combination.

CC may choose the cross-product sensibly (it need not run every combination — enough points to fit
the three exponents and find the hurt threshold along each axis). Document which points were run
and why.

### Cutoff — measured in ms/step, NOT wall-clock
Run each config only to a **measurement window** (a few hundred steps — enough for a stable
ms/step estimate; CC chooses the exact length and documents it). Do not run configs to completion;
cut at the window once the rate is stable.

Two-tier cut:

1. **Rate-ceiling cut (default ~300 ms/step).** If a config's mean ms/step over the window exceeds
   **~300 ms/step** (generous default; CC may be instructed to adjust), the config is judged
   **past-ceiling** — too slow to be viable at scale. Run it just long enough for a stable estimate
   (the measurement window), record the rate, and mark that rung as the feasibility limit along
   that axis. Stop climbing further along that axis.

2. **Early-abort (pathological).** If a config is so slow it **cannot reach the measurement window
   in reasonable time** (per-step cost so high that accumulating a few-hundred-step statistic is
   itself impractical), abort **before** completing the window and record it as **hard-infeasible**.
   The rate is so far past viable that the precise number does not matter — the fact that it can't
   reach the window is the finding.

No projection-based skipping: configs are *attempted* and cut on *measured* rate, not skipped on a
predicted rate. (Projection trustworthiness is a later-forerun question, out of scope here.)

---

## 6. Mandatory instrumentation — incremental flushed logging

Every run — window-completed, ceiling-cut, or early-aborted — must leave a **readable trail**, so a
cut or killed run is as diagnostic as a completed one.

Each run writes an **incremental log, flushed to disk every logging interval** (not buffered to
end-of-run), containing per interval: timestamp, step number, current N, windowed ms/step, peak
per-cell occupancy, and memory if cheap to capture. If a run is killed or aborts, the log up to
that point survives and shows the ms/step-vs-step trail and where it bogged down.

This is non-negotiable: an unattended sweep that hits a pathological config must leave behind *why*
it was pathological (was cost climbing with occupancy? with N? a sudden spike?), or the
reconnaissance loses its most useful data.

---

## 7. Report — must-be-seen artifacts

HTML report `outputs/stage6_0a_perf/report_stage6_0a_perf.html`, all plots embedded. This report
*is* the deliverable; it carries shape that no threshold captures. Sections:

1. **Cost surface / feasibility table.** Every scale point run: grid, N, mean & peak occupancy,
   ms/step (mean + dispersion), plausibility-rail status, and cut-status
   (window-completed / ceiling-cut / hard-infeasible). This table is the headline — it shows where
   it starts to hurt across all three axes.
2. **Profiling breakdown** of where per-step time goes per hot path under the current substrate,
   for at least one cheap and one expensive config, so the breakdown's *shift* with scale is
   visible.
3. **The three scaling exponents** — grid, N, occupancy — each with the data it was fit from, and a
   plain-language read of which axis dominates.
4. **Acceleration-variant table** — every numpy/Numba variant tried, its speedup, where it applied
   and where it didn't (e.g. Numba paths that wouldn't compile against Mesa agents), and its
   plausibility-rail status.
5. **Forward assessment of heavier paths** — projected achievable ceiling under Cython, GPU/JAX,
   and array-based-scheduler restructuring; a reasoned judgment on whether proto-agricultural
   density (~100 agents/cell at a usable grid) is reachable on cheap paths alone or needs one of
   these. (Analysis only — nothing implemented.)

From 1–5 the report concludes with the **feel**: roughly which (grid, occupancy, total-N) region
is affordable at ≤~300 ms/step, and whether proto-ag density sits inside or outside it. No
config is selected — that is the next conversation.

---

## 8. Notes for CC

- **Code location.** The substrate source is in your working repo; this blueprint names hot paths
  by mechanic (growback, harvest-split, contest, occupant-set construction, diffusion movement)
  rather than by file — locate them in the current code.
- **Roadmap reconciliation (doc update on completion).** The roadmap's "Stage 6 = statistical
  framework" entry is **stale** — the resource-ecology arc has taken over the Stage 6 namespace.
  On completion, note in ROADMAP.md that this study is filed as **6.0a-perf** (utility, off the
  science spine; 6.0b terrain remains the next science step), and flag that the old
  "Stage 6 = statistics" entry needs renumbering to wherever statistics now belongs. Do not
  silently overwrite it — flag it for supervisor resolution.
- **No mid-run check-in.** Run the sweep to completion and report. The only thing that stops a
  *config* is the §5 cutoff; the *stage* runs straight through to the §7 report.
- **Document every choice you make** under the latitude granted (sweep points, window length,
  warm-up, which configs get full profiling, any added plausibility rail). The postmortem value of
  this stage depends on the choices being legible.

---

## 9. Acceptance (stage is done when)

This stage's "acceptance" is the report existing and being complete, not a green check — it is the
named exception. The stage is done when the report contains all six §7 elements, every run in the
sweep has a recorded cut-status and rail-status, and every reported timing came from a
rail-passing run. The cost-surface table and the three exponents are the load-bearing outputs.

---

*End of blueprint — Stage 6.0a-perf. Reconnaissance only: get the feel, do not choose the config.*
