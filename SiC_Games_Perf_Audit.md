# SiC Games — Performance Audit + Optimisation Directive

**Version:** 1.0
**Scope:** Audit first, then apply only safe numerically-exact fixes.
  No behaviour changes. No new mechanics. No science.
**Constraint:** Every optimisation must produce bit-identical (or
  float-tolerance-identical) output to the pre-fix model at seed=42.
  An optimisation that changes the science is a bug, not a speedup.
**Output dir:** `outputs/perf_audit/`

---

## 0. Guiding principle

The science is locked. These optimisations change *how fast* the model
runs, never *what it computes*. The verification gate in Task 3 (numerical
equivalence at seed=42) is non-negotiable: any change that fails it is
reverted, regardless of how much faster it is.

Order: audit everything first (Task 0, no code changes), then apply fixes
in risk order (Task 1 known-safe, Task 2 audit-identified safe), then
verify (Task 3).

---

## 1. Task 0 — Performance audit (NO code changes)

### 1.1 Profile

Run `cProfile` on a representative workload:
```
B1 config: 100×100, N=500, seed=42, static world, C strategy, 200 steps
```
Save the profile. Report the top 20 functions by cumulative time and by
total (own) time. Two separate tables.

Also run `cProfile` on B0 (50×50, N=250, 200 steps) for comparison — some
bottlenecks only appear at scale, others are constant overhead.

### 1.2 Static review of hot paths

For every function appearing in the top-15 of either profile, inspect the
source and classify. Produce a ranked inventory table:

| # | Function | File | Current cost | Issue | Proposed fix | Est. speedup | Risk |
|---|---|---|---|---|---|---|---|
| 1 | growback | world.py | O(W×H) Python loop | per-cell Python iteration | numpy vectorise | grid exp 2.54→2.0 | LOW |
| ... | | | | | | | |

Risk levels:
- **LOW** — numpy vectorisation of an arithmetic loop, caching a static
  computation, replacing a list scan with a dict lookup. Numerically exact.
- **MED** — reordering operations, changing data structures used in
  RNG-adjacent code, anything that touches agent iteration order.
- **HIGH** — anything that could change RNG draw order, agent processing
  order, or floating-point accumulation order.

### 1.3 Specific things to check (report yes/no + detail for each)

**Vectorisation candidates:**
- Is growback a Python loop over cells? (known: yes)
- Is sugar shedding (seasonal trough) a Python loop over cells?
- Are metrics (Gini, dispersion, mean wealth, mean Cred) computed with
  numpy over arrays, or Python loops over the agent list?
- Is the capacity field recomputed each step, or cached at init?

**Algorithmic candidates:**
- Biparental partner search (proximity r=3): spatial-hashed or O(N²) scan?
  (The JT fix used a spatial hash — does partner search reuse it or
  re-scan?)
- Support pool proximity grouping: spatial-hashed or O(N²)?
- Is N_C (for carry_discount) computed once per step or recomputed per
  agent birth check?
- Vision scan: does each agent rebuild its candidate list from scratch,
  and is the toroidal distance computed inline per candidate?

**Caching candidates:**
- Toroidal distance / wrap computations: computed inline repeatedly, or
  precomputed offset tables?
- Moore/von-Neumann neighbour offsets: rebuilt per call or module constant?
- Config attribute access in hot loops: is `config.x.y.z` dereferenced
  inside per-agent loops (slow Python attribute chain) or hoisted out?

**Allocation candidates:**
- Per-step list/array allocations in the agent loop that could be
  preallocated and reused?
- Parquet metric buffering: does it accumulate in a growing Python list,
  and is memory bounded? (Benchmark showed no leak, but confirm the
  buffering strategy.)

**Spatial-index reuse:**
- The JT fix built a `pos→agent` hash. Is that hash rebuilt separately by
  partner search, pool grouping, and JT — three times per step? If so, a
  single shared spatial index built once per step would serve all three.

### 1.4 Audit deliverable

A ranked inventory (the table in §1.2) plus a short paragraph per
top-5 item explaining the issue and the fix. NO code changes in Task 0.
This is reconnaissance.

---

## 2. Task 1 — Growback numpy fix (known, LOW risk)

```python
# world.py growback — replace the Python loop:
world.sugar = np.minimum(world.sugar + alpha, world.effective_capacity)
```

Where `effective_capacity` is the seasonal-adjusted capacity (or
`max_capacity` in static world). Confirm this is already a numpy array;
if sugar/capacity are stored as nested Python lists, convert to numpy
arrays at init (this is itself part of the fix).

If sugar shedding (seasonal) is also a Python loop, vectorise it the
same way:
```python
world.sugar = np.minimum(world.sugar, world.effective_capacity)
```

Run full test suite after this change. All 198 tests must pass.

---

## 3. Task 2 — Apply audit-identified LOW-risk fixes only

From the Task 0 inventory, apply **only** fixes marked LOW risk. For each:
1. Apply the change.
2. Run the full test suite (must stay green).
3. Note the change in the report with before/after reasoning.

**Do NOT apply MED or HIGH risk fixes in this directive.** Those are
catalogued in the report for a future optimisation pass with dedicated
verification. If a high-value fix is MED/HIGH risk, note its potential
speedup and flag it for supervisor decision — do not apply it.

**Shared spatial index:** if Task 0 finds that JT, partner search, and
pool grouping each build their own `pos→agent` hash, building one shared
index per step and passing it to all three is a LOW-risk fix *if and only
if* it does not change iteration order or RNG draws. Verify against the
equivalence gate before keeping it. If it changes any output, revert and
flag as MED.

---

## 4. Task 3 — Verification (numerical equivalence + re-benchmark)

### 4.1 Numerical equivalence gate (MANDATORY)

Before the audit fixes are applied, a reference run must exist from the
**current committed state** (JT spatial-hash fix in, no audit changes yet):
```
B0 reference: 50×50, N=250, seed=42, static world, C strategy, 500 steps
→ outputs/perf_audit/b0_reference_preaudit.parquet
```
Generate this BEFORE making any code changes in Tasks 1–2. If any audit
fix has already been applied to the working tree, stash it
(`git stash`), generate the reference, then restore (`git stash pop`).
The gate compares "JT-fix only" vs "JT-fix + audit fixes" — not against
the original pre-JT-fix code.

After all fixes, run the identical config and compare:
```
- N(t) identical at every step (exact integer match)
- mean_wealth, gini_wealth, mean_cred: identical to 1e-9 relative tolerance
- total deaths, births: exact integer match
- final agent positions: exact match
```

**If any metric diverges beyond tolerance:** a fix changed the science.
Bisect the applied fixes to find which one, revert it, re-flag as MED/HIGH.
Report the divergence. Do not proceed until equivalence holds.

This gate is why optimisations are applied one at a time with the suite
run between each — so the culprit is immediately identifiable.

### 4.2 Re-benchmark

Re-run B0, B1, B2, B3, B4, B5 in order. Same stopping rule as before:
abort any run exceeding 20 minutes, skip larger configs. Same scaling
rules (peak positions, band_width_k, N_carry proportional to grid area).
Report new ms/step and speedup vs the JT-fix-only baseline for each
config that ran.

---

## 5. Report format

HTML: `outputs/perf_audit/report_perf_audit.html`

### §0 — Audit inventory
The full ranked table from Task 0. Top-5 items each with a paragraph.

### §1 — Profile tables
Top-20 by cumulative time and by own time, for B0 and B1. Four tables.

### §2 — Fixes applied
List each LOW-risk fix applied, with the test-suite result after each.
State which MED/HIGH fixes were catalogued but deferred.

### §3 — Numerical equivalence
The equivalence gate result. State explicitly: "All metrics identical to
1e-9 tolerance — science unchanged" or the divergence and resolution.

### §4 — Timing comparison

| ID | Grid | N | JT-fix-only ms/step | +growback +audit ms/step | Speedup |
|---|---|---|---|---|---|
| B0 | 50×50 | 250 | 75.7 | ? | ?× |
| B1 | 100×100 | 500 | 388.3 | ? | ?× |
| B2 | 100×100 | 1000 | 425.5 | ? | ?× |
| B3 | 150×150 | 1000 | 1265.5 | ? | ?× |
| B4 | 150×150 | 2000 | — | ? | — |
| B5 | 200×200 | 1500 | — | ? | — |

### §5 — Updated scaling + feasibility
New grid exponent (target ≤ 2.0). New N exponent. Updated LHS wall-time
estimates. State which grid sizes are now LHS-feasible (< 4h, 300 runs,
4 workers) and which are science-run-only.

### §6 — Deferred optimisations
The MED/HIGH-risk items from the audit, with estimated speedups, for a
future pass. This becomes the backlog if more speed is needed later.

---

## 6. Success criteria

| Criterion | Target |
|---|---|
| Audit inventory produced | Ranked table, top-5 detailed |
| cProfile tables for B0 and B1 | Top-20 cumulative + own, each |
| Growback vectorised | Confirmed |
| Only LOW-risk fixes applied | MED/HIGH catalogued, not applied |
| Test suite green after every fix | 198 maintained throughout |
| Numerical equivalence holds | All metrics identical to 1e-9 |
| Grid exponent reported | Target ≤ 2.0 |
| B3 re-benchmarked | New ms/step stated |
| Deferred backlog documented | §6 present |

---

## 7. Out of scope

- MED/HIGH-risk optimisations (catalogued only)
- Any change to agent iteration order, RNG draw order, or FP accumulation order
- New mechanics, config changes, science changes
- Rewriting in Cython/numba/Julia (separate decision if ever needed)
- Parallelising the single-run inner loop (BatchRunner already parallelises across runs)

---

*End of Performance Audit + Optimisation Directive*
