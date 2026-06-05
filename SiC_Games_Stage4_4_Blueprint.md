# SiC Games — Stage 4.4 Blueprint: Grid Rescaling + λ + ψ Redesign + Revised Sweep

**Version:** 1.0
**Intended consumer:** Claude Code (and the human supervisor).
**Scope:** Stage 4.4 only. Grid rescaling is a prerequisite that gates everything else.
**Prerequisite:** Stage 4.3 complete. Locked: β=2.0 (interim), τ_pool=0.05, γ=0.2,
ρ=0.3, dormancy params (k_dormant=1.0, τ_trickle=0.05, k_reactivate=3.0, T_dormant_max=50).
**ROADMAP:** `G:\My Drive\docs\SiC Games\ROADMAP.md`

---

## 0. North Star (read first, every session)

**Stage 4.4 goal:** fix the grid resource scale so the model is properly calibrated
for β=5 Si metabolism, then run the first clean H1(ii) test with all mechanics correct.

Three findings from Stage 4.3 share a single root cause — the grid (max_sugar=4,
growback α=1) was designed around C metabolism (~2.5/step) and cannot support
Si at β=5 (~12.5/step):

1. **β forced to 2.0** — β=5 produced permanent Si dormancy gridlock.
2. **C established starvation 2.19/step** (gate: ≤0.78) — τ_pool drains adult
   surplus on a grid too sparse to replenish it.
3. **Si dormancy rate 53%** — agents on a sparse grid hit the dormancy threshold
   routinely even at β=2.

One fix — rescale both max_sugar and growback α — resolves all three.

Additional tasks once grid is locked:
- **λ** (C wealth inheritance) — deferred twice, now included.
- **ψ redesign** — perfectly flat quartile distribution confirmed ψ has no
  discriminating power. Diagnose before redesigning.
- **Revised seasonal sweep** — first H1(ii) test with correct grid + β=5.

**What Stage 4.4 is not.** No Si pool (still disabled, toggle-ready per §1.5 of
Stage 4.3 blueprint). No Si Cred. No carrying costs (deferred to Stage 5 as
prerequisite for rational Si pooling). No multi-seed runs.

---

## 1. Task 0 — Grid rescaling

### 1.1 Rationale

Current grid: max_sugar=4, growback α=1. Mean harvest per step for a moving
agent in medium-density conditions: ~2–3 sugar units.

At β=5, Si mean metabolism = Uniform[1,4] mean × 5 = 2.5 × 5 = 12.5/step.
For Si to survive with 20% surplus: target harvest = 12.5 × 1.2 = 15/step.
Required scale factor: 15 / 2.5 ≈ 6×.

Scale BOTH max_sugar and α by the same factor k to preserve the grid's
spatial structure (peak gradients, two-peak topology) while uniformly
lifting resource density.

```yaml
# world config:
grid:
  max_sugar: 4 * k        # scaled
  growback_alpha: 1 * k   # scaled proportionally
  # peak positions, topology, toroidal wrapping: UNCHANGED
```

Scaling both together means cells fill faster AND hold more sugar — agents
get richer harvests without changing movement incentives.

### 1.2 Calibration procedure

**Step 1:** Run Si static null control (β=5, dormancy enabled, pool disabled)
at k=4, k=5, k=6 in order. Stop at first k where:
- N_active ∈ [150, 400] at t≥500
- dormancy_rate < 20% at t≥500
- permanent_dormancy_deaths ≤ 0.5/step

Record minimum viable k. Use this k for all subsequent Stage 4.4 runs.

**Step 2:** With locked k, run C static null control to verify C equilibrium
is not destabilised. C p_max will likely need reduction (richer grid → higher
birth rate at same p_max). Accept up to 4 C p_max adjustment attempts.

**Step 3:** Verify C established starvation ≤ 0.78/step at locked k and τ_pool=0.05.
If still failing: reduce τ_pool in steps of 0.01. Document. Accept up to 3 attempts.
This should resolve automatically with richer adults on a denser grid.

### 1.3 Si n_total demographic runaway

Stage 4.3 plots showed Si n_total growing from ~200 to ~800 over 1000 steps
while n_active stabilised. With dormancy, fission produces new agents faster
than permanent deaths remove them — dormant agents reactivate rather than dying,
so population accumulates.

Monitor in Stage 4.4: if n_total still growing at t=1000 with rescaled grid,
p_fission_Si may need reduction. The gate is n_active ∈ [150,400]; n_total
is informational but should not be unbounded.

### 1.4 Lock and record

Once both null controls pass all gates, record in ROADMAP.md:
- k_grid (scale factor)
- max_sugar = 4×k
- growback_alpha = k
- p_max_C (Stage 4.4)
- p_fission_Si (Stage 4.4)
- β_metabolism = 5.0 (confirm viable)
- τ_pool (Stage 4.4, if adjusted)

---

## 2. Task 1 — λ wealth inheritance (C only)

**Long-deferred. Introduced now.**

### 2.1 Mechanism

At birth, C offspring receive an additional wealth boost proportional to the
mean wealth of their parents, beyond the existing parental transfer τ_parent:

$$w_{\text{child}}(0) = w_{\text{init}} + \tau_{\text{parent}} \cdot
\frac{w_A + w_B}{2} + \lambda \cdot \bar{w}_C$$

where $\bar{w}_C$ is mean C population wealth at time of birth and
$\lambda = 0.1$ (default). This is a Cred-economy-adjacent mechanic: wealthier
C populations produce better-capitalised offspring, creating dynastic effects.

**C only.** Si wealth is earned individually via fission. λ=0 for Si.

```yaml
# C configs only:
reproduction:
  lambda_inheritance: 0.1   # fraction of mean population wealth at birth
```

### 2.2 Verification

Run C static null control with λ=0.1 added. Verify:
- N still ∈ [150, 400] at t≥500
- Established starvation still ≤ 0.78/step
- Wealth distribution: expect compression toward higher mean (wealthier offspring)
  but verify Gini doesn't collapse (λ should not eliminate wealth inequality)

If N overshoots [150,400]: reduce p_max_C by 0.005. Document. Max 2 adjustments.

---

## 3. Task 2 — ψ redesign

### 3.1 Diagnosis first (no runs)

Before redesigning, document exactly what ψ currently computes.

From `agents/carbon_decision.py` (or equivalent), extract and report:
1. How ψ_i is initialised at birth (distribution, range)
2. Where ψ_i enters the utility function (which term, what coefficient)
3. Whether ψ_i changes during an agent's lifetime or is fixed at birth
4. The actual range of ψ_i observed in Stage 4.3 C seasonal parquets
   (min, max, mean, std from death_events.parquet)

Stage 4.3 found ψ range [0.345, 0.655] — very narrow. If ψ is a fixed trait
drawn at birth from a narrow distribution and enters utility with a small
coefficient, it will be nearly uniform across agents and produce exactly
the flat quartile distribution observed. That is the expected bug.

Report diagnosis in §2 of the Stage 4.4 report before implementing any fix.

### 3.2 Redesign specification

ψ_i is designated in the ROADMAP as a "proximity utility term" — it should
modulate how much a C agent values being near other C agents vs. harvesting
in isolation. The intended behaviour:

- High-ψ agents are more social — they prefer cells with nearby C agents,
  even at some harvest cost. This creates clustering tendencies.
- Low-ψ agents are more solitary — pure harvesters, less social clustering.
- ψ should discriminate survival outcomes: under seasonal stress, socially
  clustered agents (high ψ) should benefit from proximity-pool support more
  than solitary agents (low ψ), creating a measurable starvation difference.

**Redesign:** make ψ_i a multiplicative weight on the proximity utility term
in the C decision function, with a wider effective range:

$$U_{ij}^C = w_R^{(i)} \cdot \widehat{\Delta\mathcal{R}}_{ij}
           + w_C^{(i)} \cdot \widehat{\Delta\mathcal{C}}_{ij}
           + \psi_i \cdot \widehat{\Delta P}_{ij}$$

where $\widehat{\Delta P}_{ij}$ is the estimated proximity benefit of moving
to cell $j$ — defined as the number of C agents within r_pool radius of cell $j$,
normalised. High-ψ agents weight this proximity term strongly; low-ψ agents ignore it.

**ψ_i distribution:** draw from Beta(2, 2) at birth (range [0,1], peaked at 0.5,
wider spread than current). This gives meaningful high-ψ and low-ψ populations.

**Do NOT change ψ for Si.** ψ_i is carried in Si trait vector but hook is deferred.

### 3.3 Verification

Run C static null control with redesigned ψ. Verify:
- Population stability unchanged
- ψ distribution at steady state (mean, std, Gini) reported
- Repeat ψ quartile starvation analysis on C seasonal (A=0.5, T=200) run
  from Task 3 sweep. Expect Q1 (low-ψ, solitary) to show higher starvation
  than Q4 (high-ψ, social) during trough phases.

If quartile distribution is still flat after redesign: flag for Stage 5
(ψ may require agent-level co-evolution to discriminate, not just trait
distribution change).

---

## 4. Task 3 — Revised seasonal sweep (H1(ii))

Using the fully locked Stage 4.4 model (k_grid, β=5, τ_pool, λ=0.1, ψ redesigned),
run the complete seasonal sweep. This is the **third attempt at H1(ii)** and should
be the first with all mechanics correct.

| Run ID | A | T | Agent |
|---|---|---|---|
| 4.4-C-A05-T200 | 0.5 | 200 | C |
| 4.4-Si-A05-T200 | 0.5 | 200 | Si |
| 4.4-C-A075-T200 | 0.75 | 200 | C |
| 4.4-Si-A075-T200 | 0.75 | 200 | Si |
| 4.4-C-A05-T100 | 0.5 | 100 | C |
| 4.4-Si-A05-T100 | 0.5 | 100 | Si |
| 4.4-C-A05-T050 | 0.5 | 50 | C |
| 4.4-Si-A05-T050 | 0.5 | 50 | Si |

For Si runs: report n_active and n_total separately. Survival on n_active.

### 4.1 T* re-search (C only, if C survives any seasonal run)

If C survives at any T in the sweep, re-run T* binary search from that point.
If C collapses at all conditions: accept as structural Allee fragility under
current parameter set and document. Do not over-tune p_max to rescue C.

### 4.2 H1(ii) assessment (mandatory, ≥150 words)

Write substantive assessment covering:
- Which agent survives at each (A, T) — using n_active for Si
- Whether λ + richer grid changed C's resilience profile
- Whether redesigned ψ affected C starvation patterns (trough vs peak)
- Whether Si's dormancy advantage persists or C's social mechanics narrow the gap
- Clear verdict: H1(ii) supported / null / mixed, with explanation

**Do not write "see table."**

---

## 5. New metrics

| Metric | Definition |
|---|---|
| `lambda_inheritance` | Mean inheritance boost per birth event (C only) |
| `psi_mean`, `psi_gini` | ψ distribution statistics per step |
| `psi_proximity_utility` | Mean ψ_i × ΔP_ij contribution to utility per step |
| `k_grid` | Locked grid scale factor (report header) |

---

## 6. Report format (HTML — mandatory from this stage)

**Standing Rule update: reports are now HTML, not markdown.**

Reason: markdown image references require co-located figures directory to render.
HTML with base64-encoded images is self-contained and renders anywhere.

CC must generate `report.html` (not `report.md`) for Stage 4.4 onwards.
All figures embedded as base64 `<img>` tags. No external file dependencies.

```python
# In generate_figures.py:
import base64

def embed_figure(path):
    with open(path, 'rb') as f:
        data = base64.b64encode(f.read()).decode()
    return f'<img src="data:image/png;base64,{data}" style="max-width:100%">'
```

Report structure: standard HTML with embedded CSS for readability.
Figures appear inline at point of reference.

The figures/ directory should still be generated (for local use), but the
deliverable uploaded to supervisor is a single self-contained `report.html`.

---

## 7. Runs summary

| Priority | Task | Runs | Gate |
|---|---|---|---|
| 1 | Task 0: Grid calibration | Si static ×3 + C static ×4 (tuning) | Tasks 1–3 |
| 2 | Task 1: λ verification | C static ×1 (±2 p_max adjustments) | Task 3 |
| 3 | Task 2: ψ redesign | C static ×1 (verification) | Task 3 |
| 4 | Task 3: Seasonal sweep | 8 runs | H1(ii) |

Total new runs: up to **18 max** (7 tuning + 3 ψ/λ + 8 sweep).

---

## 8. Success criteria

| Criterion | Target |
|---|---|
| β=5 viable with rescaled grid | Si static: N_active ∈ [150,400], dormancy_rate < 20% |
| C null control passes all gates | est_starv ≤ 0.78/step, N ∈ [150,400] |
| Si n_total not unbounded | n_total stable or slowly declining by t=1000 |
| λ=0.1 active and stable | C null control unchanged by λ addition |
| ψ redesign discriminating | Quartile starvation not flat (Q1≠Q4 by ≥5%) |
| Sweep complete | All 8 runs |
| H1(ii) assessment written | ≥150 words, substantive |
| Report is HTML | Single self-contained report.html with embedded figures |
| Tests pass | Full suite after every code change |
| ROADMAP updated | All locked values recorded |

---

## 9. Coding-agent directives

1. **Grid rescaling first, everything else gates on it.** Do not run λ or ψ
   verification until null controls pass with rescaled grid.

2. **Scale max_sugar AND α by the same k.** Do not scale only one. The
   relationship max_sugar/α = 4 should be preserved to maintain growback timing.

3. **β=5 is the target.** β=2.0 was an interim calibration workaround.
   The empirically motivated value is β=5. Confirm viable at Stage 4.4's
   rescaled grid. If still not viable at k≤6, flag explicitly and document
   the grid limit — do not silently accept β=2.

4. **Diagnose ψ before redesigning.** Report current implementation in §2
   before writing any new ψ code. If ψ is a fixed trait with a narrow range
   and a small coefficient, the fix is clear; if it's something else, the
   diagnosis changes the redesign.

5. **λ is C-only.** Check C/Si distinction table. Never apply λ to Si.

6. **HTML report with embedded figures.** Generate report.html. Verify all
   figures render by opening the file in a browser before submitting.
   A report with broken or missing images is incomplete per Rule 10.

7. **H1(ii) assessment is mandatory.** ≥150 words of substantive prose in §3.
   Do not write "see table."

8. **Update ROADMAP.md** at completion:
   `G:\My Drive\docs\SiC Games\ROADMAP.md`
   Mark Stage 4.4 complete. Record k_grid, β=5 confirmation, locked p_max_C,
   p_fission_Si, λ=0.1. Add Standing Rule 13 (HTML reports).
   Update Stage 4.5 entry: Si carrying costs + Si pool experiment (toggle).

---

## 10. Standing rule additions (CC to add to ROADMAP)

**Rule 13: Reports are HTML from Stage 4.4 onwards.**
Generate `report.html` with all figures embedded as base64 `<img>` tags.
The deliverable is a single self-contained file. The figures/ directory is
still generated for local use but is not the primary deliverable.

---

## 11. Deferred

- Si pool experiment (carrying costs → rational surplus pooling). → Stage 4.5.
  Prerequisite: add CostModel carrying cost parameter k_carry (excess wealth
  above k_carry × metabolism incurs small penalty). Toggle-ready in CostModel.
- Si carrying costs as sweep parameter. → Stage 5.x.
- β sweep {2, 5, 10}. → Stage 5.x.
- ρ sweep. → Stage 5.x.
- Amplitude asymmetry. → Stage 4.5.
- Multi-seed runs. → Stage 5+.
- Si Cred economy. → Stage 5+.
