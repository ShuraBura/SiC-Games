# Run report: stage2_carbon_seed42

**Seed:** 42 | **Steps:** 1000 | **Strategy:** carbon | **Date:** 2026-05-16

## TL;DR
- [✓] All success criteria met
- Final population: 250 | Final Gini: 0.46 | Mean dispersion: 17.8

## Success criteria
| Criterion | Status | Observed | Threshold |
|---|---|---|---|
| C population stable | ✓ | 250–250 | [200, 300] |
| Joint tasks firing (mean > 0 after step 100) | ✓ | 33.49/step | > 0 |
| Cred accumulating + stable (mean_cred > 0, gini_cred std < 0.05) | ✓ | mean_cred=9.477, gini_cred_std=0.0111 | mean_cred > 0 and std < 0.05 |
| No Cred monopoly (max_cred_fraction < 0.5 after t=100) | ✓ | max observed: 0.163 | < 0.5 |
| sigma > sigma_base (0.5) at steady state | ✓ | 1.0514 | > 0.5 |
| All new pytest tests pass | ✓ | pytest passed | all pass |
| Reproducibility (same seed) | ✓ | identical trace | identical |

## Key metrics (final 100 steps, mean ± std)
| Metric | Value |
|---|---|
| Population | 250.0 ± 0.0 |
| Mean wealth | 45.1 ± 1.8 |
| Gini wealth | 0.46 ± 0.014 |
| Spatial dispersion | 17.8 ± 0.87 |
| Deaths/step (starvation) | 2.9 |
| Deaths/step (senescence) | 2.4 |

### Stage 2 — Cred and joint-task metrics (final 100 steps)
| Metric | Value |
|---|---|
| Mean Cred | 9.477 ± 0.903 |
| Gini Cred | 0.834 ± 0.011 |
| Max Cred fraction | 0.069 |
| Mean sigma | 1.051 ± 0.029 |
| Joint tasks/step | 39.46 |
| Joint participants/step | 85.43 |

## Plots
![Population over time](plots/population.png)
![Gini over time](plots/gini.png)
![Spatial dispersion over time](plots/dispersion.png)
![Wealth distribution](plots/wealth_histogram.png)
![Final agent positions](plots/final_positions.png)
![Mean Cred over time](plots/mean_cred.png)
![Gini Cred over time](plots/gini_cred.png)
![Mean sigma over time](plots/mean_sigma.png)
![Joint task count over time](plots/joint_task_count.png)

## Comparison to Stage 1 (greedy-Si, same seed)
| Metric (final 100 steps) | Stage 1 (Si) | Stage 2 (C) | Δ |
|---|---|---|---|
| Mean wealth | 52.3 | 45.1 | -7.20 |
| Gini wealth | 0.47 | 0.46 | -0.01 |
| Spatial dispersion | 15.5 | 17.8 | +2.34 |
| Deaths/step (starvation) | 1.8 | 2.9 | +1.06 |
| Deaths/step (senescence) | 2.8 | 2.4 | -0.37 |
| Mean Cred | — | 9.477 | — |
| Gini Cred | — | 0.834 | — |
| Joint tasks/step | — | 39.46 | — |

## Notes
_No anomalies to report._

## Configuration
```yaml
agents:
  initial_population: 250
  initial_wealth_dist:
  - 5
  - 25
  max_age_dist:
  - 60
  - 100
  metabolic_rate_dist:
  - 1
  - 4
  phi_mean: 0.5
  phi_std: 0.2
  vision_dist:
  - 1
  - 6
carbon:
  cred_bonus_per_participant: 1.0
  cred_decay: 0.01
  cred_scale: 10.0
  epsilon: 0.01
  kappa: 2.0
  matthew_alpha: 1.5
  sigma_base: 0.5
  velocity_scale: 1.0
  velocity_tau: 10
decision:
  strategy: carbon
joint_task:
  capacity_threshold: 4
  distance_d: 1
run:
  metrics_every: 1
  n_steps: 1000
  output_dir: outputs/stage2_carbon_seed42
seed: 42
visualization:
  animate: true
  frames_per_save: 5
  save_static_plots: true
world:
  band_width_k: 6
  grid_size:
  - 50
  - 50
  growth_rate_alpha: 1
  max_sugar_capacity: 4
  sugar_peaks:
  - - 10
    - 40
  - - 40
    - 10
  toroidal: true
```
