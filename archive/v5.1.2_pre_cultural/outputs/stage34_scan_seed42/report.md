# Stage 3.4 — 2D Parameter Scan: kappa x alpha

**Date:** 2026-05-17  
**Seed:** 42  
**Steps:** 1000  
**Grid:** kappa in {1.0, 2.0, 3.0} x alpha in {1.0, 1.5, 2.0}  
**Cell (2,2):** loaded from `outputs/stage3.3_seed42/metrics.parquet` (no re-run)

## Pass/fail criteria

| Observable | Target range |
|---|---|
| Gini Cred | [0.60, 0.85] |
| Deaths/step (starvation) | [2.0, 3.5] |
| Joint tasks/step | [20, 45] |
| std(phi) | > 0.08 |

## Full metrics table (tail 100 steps)

| Cell | kappa | alpha | Gini Cred | Starvation | Joint tasks | std(phi) | Mean sigma | Pass? |
|---|---|---|---|---|---|---|---|---|
| (1,1) | 1.0 | 1.0 | 0.6729 | 2.6200 | 30.00 | 0.1144 | 0.9063 | PASS |
| (1,2) | 1.0 | 1.5 | 0.6988 | 2.9000 | 35.08 | 0.0985 | 0.8959 | PASS |
| (1,3) | 1.0 | 2.0 | 0.7009 | 3.1000 | 36.65 | 0.1044 | 0.9001 | PASS |
| (2,1) | 2.0 | 1.0 | 0.6756 | 3.0000 | 30.21 | 0.1085 | 1.2899 | PASS |
| (2,2)* | 2.0 | 1.5 | 0.6849 | 2.9000 | 33.33 | 0.1111 | 1.3244 | PASS |
| (2,3) | 2.0 | 2.0 | 0.7005 | 3.3000 | 30.96 | 0.1016 | 1.2379 | PASS |
| (3,1) | 3.0 | 1.0 | 0.6758 | 3.4400 | 33.02 | 0.0967 | 1.7298 | PASS |
| (3,2) | 3.0 | 1.5 | 0.7046 | 3.1900 | 29.97 | 0.0950 | 1.5543 | PASS |
| (3,3) | 3.0 | 2.0 | 0.7028 | 3.1500 | 27.26 | 0.0922 | 1.5456 | PASS |

\* Cell (2,2) = confirmed Stage 3.3 biparental anchor (kappa=2.0, alpha=1.5).

## Cred trajectory diagnostic (t=500-1000)

Growth rate = percent change in mean_cred per 100 steps over t=500-1000.
Flag threshold: Gini Cred > 0.85 OR growth > 5% per 100 steps.

| Cell | kappa | alpha | Growth rate (%/100 steps) | Flag? |
|---|---|---|---|---|
| (1,1) | 1.0 | 1.0 | -20.99 | - |
| (1,2) | 1.0 | 1.5 | -5.85 | - |
| (1,3) | 1.0 | 2.0 | -20.94 | - |
| (2,1) | 2.0 | 1.0 | -13.08 | - |
| (2,2)* | 2.0 | 1.5 | 10.20 | FLAG |
| (2,3) | 2.0 | 2.0 | -17.87 | - |
| (3,1) | 3.0 | 1.0 | -5.48 | - |
| (3,2) | 3.0 | 1.5 | -12.34 | - |
| (3,3) | 3.0 | 2.0 | 1.72 | - |

## Plots

- `heatmap_passfail.png` — primary pass/fail overlay
- `heatmap_gini_cred.png` — Gini Cred heatmap
- `heatmap_deaths.png` — starvation deaths/step heatmap
- `heatmap_jt.png` — joint tasks/step heatmap
- `heatmap_std_phi.png` — std(phi) heatmap

## Canonical cell selection

Supervisor selects canonical (kappa, alpha) from above. The mean_sigma of the
selected cell becomes the new sigma_Si for Stage 4.
Claude Code does not select the canonical cell.