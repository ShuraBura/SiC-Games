# SiC Games — Stage 3.4 Directive: 2D Parameter Scan (κ × α)

**Version:** 1.0
**Applies to:** Stage 3.3 codebase (fully-formed agent: ψ_i active, biparental
reproduction, β=1.0, f_C=0.25).
**Scope:** Parameter scan only. No mechanism changes.

---

## Purpose

Lightweight joint scan of κ (sigma noise ceiling) × α (Matthew power exponent)
to confirm the current default point (κ=2.0, α=1.5) sits inside an acceptable
parameter valley, and to select the canonical (κ, α) pair that will be locked
for all subsequent stages. σ_Si is recalibrated to the mean_sigma of the selected
cell after supervisor chooses the canonical pair.

This is a 2D precursor to the full nD Latin hypercube scan planned for Stage 5.x
after Stage 4 perturbation objectives are available.

---

## Runs

3×3 grid search: κ ∈ {1.0, 2.0, 3.0} × α ∈ {1.0, 1.5, 2.0} = 9 cells.

| Cell | κ | α | Source |
|---|---|---|---|
| (1,1) | 1.0 | 1.0 | Fresh run |
| (1,2) | 1.0 | 1.5 | Fresh run |
| (1,3) | 1.0 | 2.0 | Fresh run |
| (2,1) | 2.0 | 1.0 | Fresh run |
| (2,2) | 2.0 | 1.5 | Load from `outputs/stage33_carbon_seed42/metrics.parquet` |
| (2,3) | 2.0 | 2.0 | Fresh run |
| (3,1) | 3.0 | 1.0 | Fresh run |
| (3,2) | 3.0 | 1.5 | Fresh run |
| (3,3) | 3.0 | 2.0 | Fresh run |

All runs: seed=42, 1000 steps, full Stage 3.3 agent (biparental, ψ_i active,
β=1.0, f_C=0.25). All other parameters unchanged from Stage 3.3 canonical.

**Critical:** cell (2,2) loads from confirmed Stage 3.3 parquet. Do not re-run it.

Output directories: `outputs/stage34_k{K}_a{A}_seed42/` for each fresh run.
Do not overwrite any Stage 3.3 outputs.

---

## Observables and target ranges

A cell is **in the valley** if all four observables are within range:

| Observable | Target range | Rationale |
|---|---|---|
| Gini Cred | [0.60, 0.85] | Matthew effect intact, no monopoly |
| Deaths/step (starvation) | [2.0, 3.5] | Exploration cost real but not catastrophic |
| Joint tasks/step | [20, 45] | Cred engine firing meaningfully |
| std(φ) | > 0.08 | Trait diversity preserved under biparental |

All observables measured over final 100 steps.

---

## Report format

Single report `outputs/stage34_scan_seed42/report.md`.

### Observable heatmaps (3×3 grid, κ on x-axis, α on y-axis)

One heatmap per observable — four total. Color scale: green = within range,
red = out of range. Label each cell with its value.

### Pass/fail overlay

A single 3×3 binary heatmap: green = all four observables in range (in valley),
red = at least one out of range. This is the primary visual deliverable.

### Full metrics table

| Cell | κ | α | Gini Cred | Starvation | Joint tasks | std(φ) | Mean sigma | Pass? |
|---|---|---|---|---|---|---|---|---|
| (1,1) | 1.0 | 1.0 | ? | ? | ? | ? | ? | ? |
| (1,2) | 1.0 | 1.5 | ? | ? | ? | ? | ? | ? |
| (1,3) | 1.0 | 2.0 | ? | ? | ? | ? | ? | ? |
| (2,1) | 2.0 | 1.0 | ? | ? | ? | ? | ? | ? |
| (2,2) | 2.0 | 1.5 | ? | ? | ? | ? | ? | ? |
| (2,3) | 2.0 | 2.0 | ? | ? | ? | ? | ? | ? |
| (3,1) | 3.0 | 1.0 | ? | ? | ? | ? | ? | ? |
| (3,2) | 3.0 | 1.5 | ? | ? | ? | ? | ? | ? |
| (3,3) | 3.0 | 2.0 | ? | ? | ? | ? | ? | ? |

Include mean_sigma for every cell — this becomes σ_Si for the selected canonical
cell after supervisor chooses.

### Cred trajectory diagnostic

For any cell where Gini Cred > 0.85 or mean_cred growth > 5% per 100 steps
after t=500: flag as potential runaway. Report growth rate for all nine cells.

---

## After the scan — supervisor decision

Supervisor selects the canonical (κ, α) cell. Selection guidance:

- Prefer a cell near the center of the passing region (not on the edge)
- If multiple cells pass, prefer lower κ (less extreme noise) and lower α
  (less winner-take-all) as the more conservative choice
- The mean_sigma of the selected cell becomes the new σ_Si for Stage 4

Claude Code does not select the canonical cell. It produces the report and
waits for supervisor instruction.

---

## Coding-agent directives

1. **Batch runner.** Implement a lightweight batch script
   `scripts/run_stage34_scan.py` that loops over the 8 fresh (κ, α) pairs,
   runs each, and saves outputs. This is not the full BatchRunner from Stage 5
   — it is a simple loop, not a parallel infrastructure.

2. **Load cell (2,2) from parquet.** Do not re-run Stage 3.3 canonical.

3. **Run order:** run cells in order of increasing κ, then α within each κ.
   Confirm cell (1,1) completes without population collapse before proceeding
   to the full grid.

4. **Heatmap visualization.** Use matplotlib with a diverging colormap. Pass/fail
   overlay uses binary green/red. Label each cell with its numeric value.

5. **No mechanism changes.** This is a parameter scan. If the coding agent
   finds itself modifying any mechanic, stop.

6. **Update ROADMAP.md** at completion: mark Stage 3.4 complete, record
   selected (κ, α) and new σ_Si once supervisor chooses.

---

## Out of scope

- Full nD Latin hypercube scan. → Stage 5.x.
- Any parameter other than κ and α.
- σ_Si update — follows after supervisor selects canonical cell.
- Stage 4 spec — follows after canonical cell selected and σ_Si locked.
- Any mechanism changes.
