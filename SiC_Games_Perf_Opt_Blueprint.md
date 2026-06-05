# SiC Games — Model Backup + Performance Optimisation Pass

**Version:** 1.0
**Scope:** Task 0 (backup + git tag) gates everything. Tasks 1–4 are the
  performance fixes. Task 5 is re-benchmark. Task 6 is report.
**Constraint:** Numerical equivalence gate applies after every fix. Any
  divergence → revert immediately, flag, stop.
**Output dir:** `outputs/perf_opt/`
**Backup dir:** `G:\My Drive\docs\SiC Games\Model\` (see Task 0)

---

## Task 0 — Backup and git tag (DO THIS FIRST, NOTHING ELSE UNTIL DONE)

### 0.1 Git tag

```bash
git add -A
git commit -m "perf: post-audit clean state — 198 tests, 38x speedup at B0"
git tag v5.1-postaudit-clean
git push origin main --tags
```

Confirm tag exists before proceeding:
```bash
git tag | grep v5.1
```
If push fails (no remote): tag locally, note it in the report. Do not skip the tag.

### 0.2 Directory name

```python
from datetime import datetime
stamp = datetime.now().strftime("%Y-%m-%d_%H%M")
backup_dir = rf"G:\My Drive\docs\SiC Games\Model\v5.1_{stamp}"
# Example: G:\My Drive\docs\SiC Games\Model\v5.1_2026-05-28_1430
```

### 0.3 What to copy

```
[repo root]/
  src/              → backup (full source)
  tests/            → backup (full test suite)
  configs/          → backup (all YAML configs)
  ROADMAP.md        → backup
  LITERATURE.md     → backup (if exists)
  pyproject.toml    → backup (or requirements.txt / setup.py)
  outputs/
    [each stage dir] → backup HTML report only, NOT parquets
```

Do not copy parquet files — large and reproducible. HTML reports only.

### 0.4 VERSION_NOTES.md

Create `VERSION_NOTES.md` in the backup root:

```markdown
# SiC Games Model — Version v5.1-postaudit-clean
**Date:** [datetime from 0.2]
**Git tag:** v5.1-postaudit-clean
**Test count:** 198 passing
**Python:** 3.14.3 | numpy 2.4.3

---

## What this version contains

### World
- 50×50 toroidal grid, 2 sugar peaks at relative positions (0.2,0.8) and (0.8,0.2)
- k_grid=4: max_sugar=16, growback_alpha=4
- Seasonal perturbation: amplitude A, period T, trough fraction tf
- Spatial hash (cell→agent) built once per step; reused by JT, pool, metrics

### C agent — full mechanic stack
- Softmax with Cred-coupled σ: σ_i = σ_base + κ·tanh(C_i/C*)
- Wealth-velocity behavioral mode switch (φ_i ceiling)
- Status amplification β=1.0
- Trait vector H_i = [φ_i, ψ_i, c1_i, c2_i]
  — ψ_i: active (pool proximity utility)
  — c1_i, c2_i: carried + inherited, NOT active (pending Stage 5.2)
- Joint-task mechanic, Matthew partition α=2.0
- Biparental reproduction (r=3, arithmetic mean + σ_inherit=0.05)
- f_C=0.25, λ=0.1, DTM birth, age-efficiency ramp η(a)
- Support pool τ_pool=0.05, ρ=0.3
- Carrying-cost birth ceiling: carry_discount = max(0, 1 − N_C/N_carry)
  N_carry=400, α_carry=1.0

### Si agent — full mechanic stack
- BoundedRationalSi, σ_Si=1.238
- Dormancy: k_dormant=1.0, τ_trickle=0.05, k_reactivate=3.0, T_dormant_max=50
- Fission reproduction, η=1.0 at birth
- Si Cred: surplus-based (r_cred=0.1), σ_Si_eff modulation κ_Si=0.5
- Si pool: enabled, τ_pool=0.05, ρ=0.3
- k_carry for Si: disabled

### Infrastructure
- BatchRunner with CRN (env_rng/agent_rng split), 4 workers
- Patch fixes: age_init_upper_frac=0.25, wealth_init_scale_k=True,
  cluster_init=True (C only, peak_index=0, radius=10)

### Locked parameters

| Parameter        | Value  | Locked at        |
|------------------|--------|------------------|
| k_grid           | 4      | Stage 4.4        |
| β_Si             | 5.0    | Stage 4.4        |
| p_fission_Si     | 0.28   | Stage 4.3        |
| p_max_C          | 0.12   | Stage 4.5 Task 1 |
| N_carry          | 400    | Stage 4.5 Task 0 |
| α_carry          | 1.0    | Stage 4.5 Task 0 |
| τ_pool           | 0.05   | Stage 4.3        |
| ρ                | 0.3    | Stage 4.3        |
| λ                | 0.1    | Stage 4.5 Task 1 |
| σ_Si             | 1.238  | Stage 3.4        |
| κ                | 2.0    | Stage 3.4        |
| α (Matthew)      | 2.0    | Stage 3.4        |
| β (status)       | 1.0    | Stage 3          |
| f_C              | 0.25   | Stage 3          |
| σ_inherit        | 0.05   | Stage 3          |
| age_init_upper_frac | 0.25 | Stage 4.4 patch |
| T_dormant_max    | 50     | Stage 4.3        |
| r_cred_Si        | 0.1    | Stage 5          |
| κ_Si             | 0.5    | Stage 5          |

### Key confirmed findings

- H1(ii) inversion ROBUST (5/5 seeds): C survives A=0.75 T=200; Si collapses.
- C survives A=0.9 at T=100 and T=200. C amplitude limit A* > 0.9.
- Si T* ∈ (68,87) at A=0.75. C T* > 500. Gap > 413 steps.
- H_cc pre-registered (Stage 4.5 patch): carry_discount counter-cyclical
  birth boost during troughs. Regression-supported at Stage 5.
- Si Cred does not rescue Si at A=0.75 collapse — inversion is structural.
- ψ co-evolution null at 3000 steps: σ_inherit=0.05 collapses Gini
  0.25→0.09 within 500 steps (biparental averaging).

### Performance (this version)

| Config | Grid  | N    | ms/step | LHS (300r, 4w) |
|--------|-------|------|---------|----------------|
| B0     | 50×50 | 250  | 13.1    | 0.1h           |
| B1     | 100×100 | 500 | 95.1  | 1.0h           |
| B2     | 100×100 | 1000 | 110.2 | 1.1h          |
| B3     | 150×150 | 1000 | 343.1 | 3.6h          |
| B4     | 150×150 | 2000 | 409.7 | 4.3h          |
| B5     | 200×200 | 1500 | 845.6 | 8.8h          |

Cumulative speedup from unoptimised baseline: B0 = 38×, B1 = 77×.

---

## Upcoming changes (next directives)

### Immediate: Performance Optimisation Pass (in progress)
- `mean_cred()` cache before birth loop
- `c_spatial_density` computed every 10 steps (diagnostic metric only)
- `_moran_W` weight matrix computed every 10 steps (diagnostic metric only)
- `_carbon_birth` spatial hash + sort-by-id
Expected: B1 ~65ms, B3 ~230ms, 200×200 LHS feasible.

### Stage 5.x
1. Si Cred redesign — counter-cyclical accumulation
2. Stage 5.2: c2 behavioral hook, Deffuant updating + c1 hook, σ_inherit sweep
3. Terrain topography: spatially varying resource abundance + metabolic cost
   (valley = low resource + low cost; peaks = high resource + high cost)
   Target grid: 100×100, N≈800
4. Stage 5.1: 5D LHS parameter sensitivity scan on full model

### Stage 6+
Statistical framework, power analysis, effect sizes.
Separate Si and C civilisations on matched worlds (CRN). No mixed populations.

---

## Known deferred items

- c1/c2 behavioral hooks (c2 → Stage 5.2; c1 → Deffuant pass)
- Deffuant cultural updating (Stage 5.2)
- ψ co-evolution (needs σ_inherit redesign — Stage 5.2)
- Inter-pool connectivity (Stage 6+)
- HiveMind (Stage 7+)
- Biparental Si reproduction (Stage 7+)
- Full nD LHS scan (Stage 5.1)
- Further perf optimisation if needed (backlog: perf_audit report §6)
```

---

## Task 1 — Fix D: `mean_cred()` cache in birth loop

**File:** `run.py`

Cache before the birth loop; replace all in-loop calls:

```python
# Before birth loop:
_cached_mean_cred   = self.mean_cred()
_cached_mean_wealth = self.mean_wealth()
# Replace self.mean_cred() / self.mean_wealth() calls inside loop
# with _cached_mean_cred / _cached_mean_wealth
```

Run full test suite. Run equivalence gate.

---

## Task 2 — Fix B: `c_spatial_density` periodic

**File:** `metrics.py`

```python
if step % self.config.metrics.k_density == 0:
    self._density_cache = c_spatial_density(agents, world)
return self._density_cache
```

Config addition:
```yaml
metrics:
  k_density: 10
  k_moran:   10
```

**Before applying — grep check (MANDATORY):**
```bash
grep -rn "c_spatial_density\|spatial_density" src/ --include="*.py" \
  | grep -v metrics.py | grep -v test_
```
Any hit outside metrics.py/tests → stop, flag HIGH risk, do not apply.

Run full test suite. Run equivalence gate.
Note in report: "c_spatial_density sampled every 10 steps from this version."

---

## Task 3 — Fix C: `_moran_W` periodic

**File:** `metrics.py`

```python
if step % self.config.metrics.k_moran == 0:
    W = _moran_W(positions, world)
    self._moran_cache = {
        'phi': morans_i(phi_values, W),
        'psi': morans_i(psi_values, W),
        'c1':  morans_i(c1_values,  W),
        'c2':  morans_i(c2_values,  W),
    }
return self._moran_cache
```

**Before applying — grep check (MANDATORY):**
```bash
grep -rn "moran\|_moran_W" src/ --include="*.py" \
  | grep -v metrics.py | grep -v test_
```
Any hit outside metrics.py/tests → stop, flag HIGH risk, do not apply.

Run full test suite. Run equivalence gate.
Note in report: "Moran's I sampled every 10 steps from this version."

---

## Task 4 — Fix A: `_carbon_birth` sorted spatial hash

**File:** `agents/reproduction.py` and `run.py`

Build `cell_to_agent` dict once in `run.py` step loop; pass to JT and
reproduction coordinator. In `_carbon_birth`, replace O(N) chebyshev scan:

```python
# Build candidate list from spatial hash — O(r_parent²):
candidates = []
for dr in range(-r_parent, r_parent + 1):
    for dc in range(-r_parent, r_parent + 1):
        if max(abs(dr), abs(dc)) <= r_parent:   # Chebyshev condition
            r = (focal.row + dr) % world.height
            c = (focal.col + dc) % world.width
            neighbour = spatial_hash.get((r, c))
            if neighbour is not None and neighbour.id != focal.id:
                candidates.append(neighbour)

# CRITICAL — sort by id before rng.choice() to preserve determinism:
candidates.sort(key=lambda a: a.id)
partner = rng.choice(candidates) if candidates else None
```

New tests:
```python
def test_partner_scan_matches_naive():
    """Spatial hash + sort gives same candidate set as O(N) scan, 100 random configs."""

def test_partner_scan_toroidal():
    """Edge agent finds partner across toroidal boundary."""

def test_partner_sort_deterministic():
    """Same state + same seed → same partner choice across runs."""
```

Run full test suite (target ≥203). Run equivalence gate.
Gate MUST pass — sort-by-id preserves exact partner selection at seed=42.
If gate fails: sort is missing or boundary bug. Bisect immediately, do not proceed.

---

## Task 5 — Re-benchmark B0–B5

Same configs and stopping rules as previous benchmarks (abort > 20 min,
skip larger). Report new ms/step for each config that ran.

---

## Task 6 — Report

HTML: `outputs/perf_opt/report_perf_opt.html`

### §0 — Backup confirmation
Backup dir full path. Git tag. Datetime. File count. Confirm VERSION_NOTES.md written.

### §1 — Fixes applied
One row per fix: fix name, file, tests after, equivalence result (✓ / FAIL+detail).
All four must show ✓.

### §2 — Timing comparison

| ID | Grid | N | JT+audit ms/step | +opt ms/step | Further speedup |
|----|------|---|------------------|--------------|-----------------|
| B0 | 50×50 | 250 | 13.1 | ? | ?× |
| B1–B5 | … | … | … | ? | ?× |

### §3 — Updated scaling + feasibility
New grid exponent (target ≤2.0). New N exponent.
LHS wall-time estimates for all configs. Explicit list of LHS-feasible grids.

### §4 — Metric sampling frequency declaration

| Metric | Every N steps | Type |
|---|---|---|
| c_spatial_density | 10 | Diagnostic (logged only) |
| Moran's I (φ,ψ,c1,c2) | 10 | Diagnostic (logged only) |
| All other metrics | 1 | Unchanged |

### §5 — VERSION_NOTES.md updated
Confirm backup dir updated with post-opt performance table and sampling table.

---

## Abort conditions

Stop and report to supervisor immediately if:
- Git tag cannot be confirmed (local or remote)
- Backup directory cannot be created (permissions, disk full, path error)
- Any grep check finds metric functions called outside metrics.py in non-test code
- Equivalence gate fails and cause not identified in ≤2 bisection attempts

---

## Success criteria

| Criterion | Target |
|---|---|
| Git tag confirmed | v5.1-postaudit-clean |
| Backup dir created with VERSION_NOTES.md | Full path in §0 |
| All four fixes applied | Each ✓ in §1 |
| Test suite green throughout | 198 → ≥203 after Task 4 |
| Equivalence gate passes all fixes | Bit-identical population/positions |
| B1 post-opt ms/step < 75 | LHS < 0.8h |
| B3 post-opt ms/step < 250 | LHS < 2.5h |
| Sampling frequency table present | §4 |
| VERSION_NOTES.md updated in backup | Confirmed in §5 |

---

*End of Model Backup + Performance Optimisation Blueprint*
