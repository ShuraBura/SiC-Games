# SiC Games — Stage 4.4 Diagnostic: C Null Control Failure

**Version:** 1.0
**Scope:** Targeted diagnostic only. No seasonal runs. No new mechanics.
**Prerequisite:** Stage 4.4 complete. Si null control passing. C null controls
all showing N=[0,0] at k=4 grid across p_max ∈ {0.02, 0.025, 0.03, 0.035, 0.04, 0.05}.
**ROADMAP:** `G:\My Drive\docs\SiC Games\ROADMAP.md`
**Output dir:** `outputs/stage44_diag_seed42/`

---

## 0. Problem statement

Stage 4.4 C null controls show **N=[0,0] with est_starv=0.0** across all
tested p_max values (0.02–0.05). The combination of N=[0,0] and zero
starvation is the critical signal:

- `est_starv=0.0` → agents are not dying from insufficient food
- `N=[0,0]` → population is going extinct anyway

This rules out simple resource starvation (which pool over-drain would produce).
The extinction is happening through some other mechanism. The most probable
candidates, in priority order:

**Hypothesis A — Allee collapse on sparse k=4 density:**
With richer sugar, agents spread out spatially. C requires biparental
reproduction with proximity radius r=3. If agents are sufficiently dispersed,
they cannot find mates. Birth rate falls below death rate → slow extinction
without starvation signal. This is the canonical Allee mechanism and is
consistent with est_starv=0.0.

**Hypothesis B — p_max too low for k=4 grid scale:**
p_max was re-calibrated assuming k=1 grid density. At k=4 density, a given
p_max may produce an absolute birth rate insufficient to replace natural
attrition. No starvation necessary — agents age out faster than they reproduce.

**Hypothesis C — Pool over-drain under k=4 conditions:**
Even with richer resources, τ_pool=0.05 may extract surplus in a way that
destabilises the adult wealth buffer. However, this should produce starvation,
not clean extinction — contradicted by est_starv=0.0. Lower priority, but
include as a control.

**Hypothesis D — λ-pool interaction:**
λ=0.1 transfers mean population wealth to newborns. On a declining population,
mean wealth may collapse, making λ boost negligible or creating some pathological
feedback. Also lower priority.

**The diagnostic isolates these hypotheses through a factorial design:**

| Run | Pool | λ | Prediction if H_A correct | Prediction if H_B correct |
|-----|------|---|--------------------------|--------------------------|
| A | Off | 0 | N=0 (Allee persists with no pool) | N>0 at higher p_max |
| B | On  | 0 | N=0 (Allee persists with pool) | N>0 at higher p_max with pool |
| C | Off | 0.1 | N=0 (Allee persists) | N>0 at higher p_max |
| D | On  | 0.1 | N=0 (matches Stage 4.4) | N>0 at higher p_max |

If Run A (no pool, no λ) produces N>0 at p_max ≥ 0.07, Hypothesis B is confirmed.
If Run A still shows N=0 across all p_max, Hypothesis A (Allee dispersal) dominates.

---

## 1. New diagnostic metric required

Before any runs: add a **spatial density diagnostic** to the C null control
output. Specifically, track:

```python
# Per step, compute:
mean_nearest_C_distance   # mean Chebyshev distance to nearest C agent for each active C agent
pct_isolated_C            # % of active C agents with zero C neighbours within radius r=3
```

This diagnostic directly tests the Allee dispersal hypothesis. If pct_isolated_C
is high (>40%) in early steps before collapse, Hypothesis A is confirmed.
Report this alongside N(t) for all diagnostic runs.

Also add: **N(t) time series at t=0,50,100,200,300,500** (not just final range).
When does the collapse happen? Immediate vs gradual tells us about the mechanism.

---

## 2. Run matrix

**All runs:** seed=42, 1000 steps, k_grid=4 (max_sugar=16, α=4), β_Si=5.

### Run A — C bare (pool off, λ=0)

p_max sweep: {0.03, 0.05, 0.07, 0.10, 0.15}

Pool disabled. λ=0. All other C mechanics active (biparental, η ramp, γ=0.2,
Cred economy). This is the isolation run for pure C viability on k=4 grid.

Record for each p_max:
- N(t) time series (t=0,50,100,200,300,500,1000)
- mean_nearest_C_distance at t=100, t=300
- pct_isolated_C at t=100, t=300
- est_starv (established starvation rate, mean t≥500)
- First step where N drops below 10 (if collapse occurs)

### Run B — C with pool, no λ

p_max sweep: {same values as best surviving Run A p_max ±0.01, plus 0.03 as anchor}

Pool enabled (τ_pool=0.05, ρ=0.3). λ=0. This isolates pool contribution.
Run only 3 p_max values: anchor at 0.03, and the two nearest viable values
from Run A.

Record same metrics as Run A.

### Run C — C with λ, no pool

p_max sweep: {same as Run B}

Pool disabled. λ=0.1. Isolates λ contribution.

### Run D — C full (pool + λ)

p_max sweep: {0.03, + best viable from Run A}

Pool enabled, λ=0.1. Replicates Stage 4.4 conditions exactly. Should reproduce
Stage 4.4 N=[0,0] at p_max=0.03.

---

## 3. Decision tree after runs

### If Run A shows survival (N∈[150,400]) at p_max ≥ 0.07:

**Conclusion:** Hypothesis B confirmed. p_max was simply too low for k=4 grid
scale. C is viable on k=4 when p_max is properly calibrated.

**Action:** Proceed to Stage 4.4 null control re-lock:
- Lock p_max_C at the minimum Run A value passing N gate [150,400]
- Run B/C/D to verify pool and λ don't break this
- If pool breaks it: reduce τ_pool in steps of 0.01 (max 3 attempts)
- Re-run Stage 4.4 seasonal sweep with corrected p_max_C
- This is **Stage 4.4 Patch** — no new mechanics, just parameter fix

### If Run A shows N=0 at all p_max values:

**Conclusion:** Hypothesis A (Allee dispersal) likely. The k=4 grid is
spreading agents out past the mating radius.

Check pct_isolated_C diagnostic to confirm. If pct_isolated_C > 40% before
collapse: Allee dispersal confirmed.

**Action:** Two options — decide with supervisor before implementing:
1. **Expand parent_radius** from r=3 to r=5 at k=4 grid (preserves spatial
   structure, adjusts for denser/larger effective territory)
2. **Cluster initialisation**: seed C agents in one quadrant at t=0 to get
   above Allee threshold, then let disperse naturally

**Do not implement either without supervisor approval.** Report findings and wait.

### If Run A shows partial survival (some p_max survive, some don't):

**Conclusion:** Mix of B and A effects. Report the phase transition clearly.
Record the minimum viable p_max. Supervisor decides whether to adjust r or p_max.

---

## 4. Report format

HTML, single self-contained file: `outputs/stage44_diag_seed42/report_diag.html`

Required sections:
1. **§0 Hypothesis summary** — brief statement of each hypothesis
2. **§1 Spatial density diagnostic** — pct_isolated_C and mean_nearest_C_distance
   for Run A at p_max=0.03 and best surviving p_max. Plot N(t) with collapse
   annotation.
3. **§2 Run matrix results** — table: Run A/B/C/D × p_max → N range, est_starv,
   pct_isolated_C, collapse step
4. **§3 Conclusion** — which hypothesis is confirmed, with evidence
5. **§4 Recommended action** — from decision tree above

All figures embedded as base64. No external dependencies.

---

## 5. Success criteria

This diagnostic is complete when:
1. At least one hypothesis is **confirmed or ruled out** with evidence from
   spatial diagnostics and N(t) time series
2. A clear recommended action is stated (parameter fix, radius fix, or escalate)
3. Run D reproduces Stage 4.4 null control failure at p_max=0.03 (confirms
   diagnostic runs are in the right regime)
4. Report is HTML and uploaded

This diagnostic is **not** complete if the report only shows N=[0,0] without
spatial diagnosis or N(t) time series. The question is not just *that* C is
dying but *why*.

---

## 6. Coding-agent directives

1. **Add spatial diagnostic first.** Do not run simulations until
   mean_nearest_C_distance and pct_isolated_C are instrumented and tested.
   These metrics are the core of this diagnostic.

2. **Run A before B/C/D.** Run A is the baseline isolation. Only proceed to
   B/C/D after Run A results are known — the p_max values for B/C/D depend on A.

3. **p_max=0.03 is always included** as anchor in every run series, even if
   it shows N=[0,0]. This keeps comparability with Stage 4.4.

4. **Do not add new mechanics.** This is a diagnostic, not a new stage.
   No terrain, no β_move, no Si pool changes.

5. **Do not tune to rescue C.** If C cannot survive at k=4 with current
   parent_radius r=3, report that. The answer may be that r needs to scale
   with k, which is a design decision not an implementation decision.

6. **Report collapse timing.** The step at which N first drops below 10
   matters. Immediate collapse (t<50) vs gradual extinction (t>500) are
   mechanistically different — note this explicitly for each run.

7. **Tests must pass.** Run full test suite after adding spatial diagnostic.
   The new metrics should have a unit test verifying correct computation
   on a known small grid before any production runs.

8. **Update ROADMAP.md** at completion: record diagnostic findings and
   recommended action in a new "Stage 4.4 Diagnostic" row in the status table.

---

## 7. What this diagnostic is NOT

- Not a fix. It identifies the cause.
- Not a seasonal run. No seasonal perturbations.
- Not a new mechanic test. λ and pool are already implemented — they are
  treated as on/off factors here, not new code.
- Not a re-run of Stage 4.4. It's a lower-dimensional factorial design
  that isolates the failure mode.

Maximum new runs: **15** (5 Run A + 3 Run B + 3 Run C + 4 Run D).
Most will be short if collapse is fast.

---

*End of Stage 4.4 Diagnostic Blueprint*
