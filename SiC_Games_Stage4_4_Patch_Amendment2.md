# SiC Games — Stage 4.4 Patch Amendment 2: Cluster Initialisation

**Version:** 1.0
**Parent:** Stage 4.4 Patch + Amendment 1 (wealth_init_scale_k)
**Scope:** One config parameter + Task 2 re-run. No other changes.
**Prerequisite:** Patch Amendment 1 complete. 164/164 tests passing.
  wealth_init_scale_k implemented (verify w_init_mean_t0 ≈ 60 — see §0 below).
**Output dir:** `outputs/stage44_patch_seed42/` (append as Task 2c)

---

## §0 — First: verify Amendment 1 was implemented correctly

The Task 2b report showed `w_init_mean_t0 = —` for all rows. This column
was a required verification check and must not be blank. Before any new
runs, read the Task 2b parquets and confirm:

```python
# From task2b parquet, any run, t=0:
mean_wealth_t0 = parquet[parquet.step == 0].mean_wealth.iloc[0]
# Expected: ≈ (20 + 100) / 2 = 60.0  (k=4, wealth_init_scale_k=True)
# If ≈ 15.0 instead: Amendment 1 did not take effect — fix before proceeding
```

Report the actual `mean_wealth_t0` value in §1 of the Task 2c report section.
If it is ≈ 15 (unscaled), fix the implementation before running Task 2c.
If it is ≈ 60 (scaled correctly), proceed.

---

## Change: cluster_init

### Rationale

The C population has no stable attractor in [150, 400] at k=4 because small-N
stochastic fluctuations drive it to extinction before it can establish. Cluster
initialisation seeds all C agents near a sugar peak at t=0, producing a dense
founding population that is demographically above the unstable lower equilibrium.
Agents move freely from t=1 onward — this is a warm-start, not a spatial
constraint.

### Config

```yaml
initialization:
  age_distribution:    "realistic"
  age_init_upper_frac: 0.25
  wealth_init_scale_k: true
  cluster_init:        true        # NEW
  cluster_peak_index:  0           # 0 = peak at (row=10, col=40); 1 = peak at (row=40, col=10)
  cluster_radius:      10          # Chebyshev radius around peak centre
```

`cluster_init: false` (default) preserves all prior behaviour. Prior configs
that omit the key are unaffected.

### Implementation

At t=0, instead of placing C agents at uniformly random unoccupied cells
across the full grid, place them at uniformly random unoccupied cells within
the Chebyshev ball of radius `cluster_radius` centred on the chosen peak:

```python
if config.initialization.cluster_init:
    peak = config.world.sugar_peaks[config.initialization.cluster_peak_index]
    # peak = (10, 40) for index 0
    candidate_cells = [
        (r, c)
        for r in range(grid_size)
        for c in range(grid_size)
        if chebyshev_toroidal(r, c, peak[0], peak[1], grid_size) <= cluster_radius
        and cell_is_unoccupied(r, c)
    ]
    place agent at random.choice(candidate_cells)
```

Peak (row=10, col=40) with radius=10 covers a 21×21 = 441-cell region. With
250 agents this gives ~57% initial occupancy — dense enough for reliable
biparental mate-finding from t=0.

**C only.** This directive applies to C null control configs only. Si agents
in any mixed or Si-only configs are always placed uniformly. Do not apply
cluster_init to Si placement.

**Newborn placement is unchanged.** Only the t=0 initialisation is affected.
New agents born during the run are placed at uniformly random unoccupied cells
across the full grid, as before.

### New test

Add to `tests/test_life_history.py`:

```python
def test_cluster_init_placement():
    """cluster_init=True places all agents within cluster_radius of the peak."""
    peak = (10, 40)
    radius = 10
    agents = initialise(N=250, cluster_init=True, cluster_peak_index=0,
                        cluster_radius=radius, seed=42)
    for a in agents:
        dist = chebyshev_toroidal(a.row, a.col, peak[0], peak[1], grid_size=50)
        assert dist <= radius, (
            f"Agent at ({a.row},{a.col}) is distance {dist} from peak — "
            f"exceeds cluster_radius={radius}"
        )

def test_cluster_init_false_is_uniform():
    """cluster_init=False (default) distributes agents across full grid."""
    agents = initialise(N=250, cluster_init=False, seed=42)
    rows = [a.row for a in agents]
    cols = [a.col for a in agents]
    # Both halves of the grid should be occupied
    assert any(r < 25 for r in rows) and any(r >= 25 for r in rows)
    assert any(c < 25 for c in cols) and any(c >= 25 for c in cols)
```

Run full test suite. All 164 prior tests must still pass; suite should reach
166 after this change.

---

## Task 2c — p_max sweep with cluster_init=True

Re-run the same 6-value p_max sweep with all three fixes active:

| Fix | Value |
|---|---|
| age_init_upper_frac | 0.25 |
| wealth_init_scale_k | true |
| cluster_init | true, cluster_peak_index=0, cluster_radius=10 |

All other parameters unchanged from Task 2a/2b: seed=42, 1000 steps,
k_grid=4, pool OFF, λ=0.

**Same gate:** N ∈ [150, 400] at t≥500, est_starv ≤ 0.78/step.

**Same stopping rule:** run in ascending p_max order (0.03, 0.04, 0.05,
0.06, 0.065, 0.07). Stop after the first overshoot (N > 400 sustained).

### Additional metrics for Task 2c

Beyond the standard columns, record:

| Metric | t= | Purpose |
|---|---|---|
| `pct_isolated_C` | 0, 50, 100, 300 | Confirm cluster disperses naturally |
| `spatial_dispersion_C` | 0, 50, 100, 300, 500 | Dispersal rate |
| `w_init_mean_t0` | 0 | Confirm wealth scaling active (expect ≈ 60) |
| `mean_age_t0` | 0 | Confirm age-init active (expect ≈ 10) |

`pct_isolated_C` at t=0 should be near 0% (dense cluster). By t=200–300 it
should approach the Task 2a/2b values (~5–10%), confirming the cluster has
dispersed and the population is operating under the same steady-state spatial
regime as prior runs. If `pct_isolated_C` at t=300 is still < 2%, the cluster
has not dispersed — note this and report it, but do not treat it as a failure.

---

## Report addendum

Append **§2c** to `report_patch.html`.

Required content:
1. Amendment 1 verification: `w_init_mean_t0` value from Task 2b parquet.
   State explicitly: "Amendment 1 implemented correctly / incorrectly."
2. Task 2c sweep table — same columns as Task 2a/2b plus the four new metrics.
3. `pct_isolated_C` dispersal table: t=0, 50, 100, 300 for the passing p_max
   (or for p_max=0.05 if none pass).
4. If a p_max passes the gate: state locked value and proceed-to-Task-3
   declaration.
5. If no p_max passes: state which mechanism is still blocking (with numbers)
   and escalate. Do not attempt further parameter changes.

N(t) overlay figure for Task 2c runs (separate from 2a and 2b).

---

## If Task 2c finds a passing p_max

Proceed immediately to Task 3 (Runs B/C/D) from the original patch blueprint,
with all three fixes active in every Task 3 config. The locked p_max from
Task 2c bare (Run A) is the anchor for Task 3.

---

## ROADMAP update

If Task 2c passes, update the Stage 4.4 Patch row to include:
```
cluster_init=True (peak_index=0, radius=10).
```
Add `cluster_init` to the locked parameters table, noting it applies to
C null control and C seasonal configs only.

---

## Out of scope

All prior out-of-scope items still apply. Additionally:
- Do not adjust cluster_radius without supervisor approval.
- Do not apply cluster_init to Si configs.
- Do not run seasonal configs yet — Task 3 first.

---

*End of Stage 4.4 Patch Amendment 2*
