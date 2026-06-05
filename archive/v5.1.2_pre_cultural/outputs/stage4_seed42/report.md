# Stage 4 — Seasonal Oscillation (A=0.5, T=200)

**Date:** 2026-05-17  
**Seed:** 42  
**Steps:** 1000  
**Oscillation:** A=0.5, T=200  
**Canonical C params:** kappa=2.0, alpha=2.0 (cell 2,3 from Stage 3.4)  
**sigma_Si:** 1.238 (recalibrated from Stage 3.4 cell 2,3 mean_sigma)

## Success criteria

| Criterion | Result |
|---|---|
| Oscillation confirmed firing | pass |
| Si survives season 1 (N>150) | pass |
| C survives season 1 (N>150) | pass |
| Null controls within 5% of Stage 3 | see null-control table below |
| Seasonal signal visible in N(t) | see survival plot |

## Null-control verification (gate check)

| Metric | Si null | Si Stage 3 ref | C null | C Stage 3.4 ref |
|---|---|---|---|---|
| Mean wealth | 40.4699 | 44.8193 | 42.4978 | 42.4978 |
| Gini wealth | 0.4660 | 0.4739 | 0.4697 | 0.4697 |
| Deaths/step | 3.4300 | 2.9600 | 3.3000 | 3.3000 |

**Si null deviation note:** Si null shows 9.7% lower mean_wealth and 15.9% higher starvation vs Stage 3 Si reference. This is expected and is NOT an infrastructure regression. Three intentional changes separate Stage 4 Si null from Stage 3 Si: (1) sigma_Si raised from 1.051 to 1.238, (2) biparental reproduction activated, (3) psi_i proximity term active. Higher sigma_Si increases exploration noise, increasing starvation. C null matches Stage 3.4 reference exactly (0.0% on all metrics) because the config is identical — confirming the WorldPerturbation infrastructure introduces no regression for C.

## Primary comparison table (final 100 steps unless noted)

| Metric | Stage 3 Si static | Stage 4 Si seasonal | Stage 3 C static | Stage 4 C seasonal |
|---|---|---|---|---|
| Mean wealth | 44.8193 | 32.0210 | 42.4978 | 29.3631 |
| Gini wealth | 0.4739 | 0.4298 | 0.4697 | 0.4583 |
| Spatial dispersion | 18.2520 | 17.5911 | 18.3235 | 18.1232 |
| Deaths/step (starvation) | 2.9600 | 3.9900 | 3.3000 | 4.8000 |
| Deaths/step (newborn) | 2.0400 | 3.1800 | 2.3800 | 3.7900 |
| Deaths/step (established) | 0.9200 | 0.8100 | 0.9200 | 1.0100 |
| Population trough min (all time) | — | 250 | — | 250 |
| Mean cred | — | — | 8.9861 | 11.1964 |
| Gini cred | — | — | 0.7005 | 0.7057 |
| Mean sigma | 1.0510 | 1.2380 | 1.2379 | 1.3199 |
| Joint tasks/step | 27.7200 | 34.1800 | 30.9600 | 35.7400 |
| std(phi) | n/a | 0.0986 | 0.1016 | 0.0960 |
| Moran's I (c1) | n/a | -0.0012 | -0.0056 | -0.0184 |

## Seasonal starvation per season

| Season | Si seasonal | C seasonal |
|---|---|---|
| 1 (t=1-200) | 933.0 | 955.0 |
| 2 (t=201-400) | 941.0 | 993.0 |
| 3 (t=401-600) | 976.0 | 872.0 |
| 4 (t=601-800) | 934.0 | 986.0 |
| 5 (t=801-1000) | 848.0 | 1007.0 |

## Moran's I trajectory under stress (early t<=200 vs late t>800)

| Trait | Si null | Si seasonal | C null | C seasonal |
|---|---|---|---|---|
| c1 | -0.0046 -> -0.0019 | 0.0069 -> -0.0006 | 0.0041 -> -0.0081 | 0.0015 -> -0.0125 |
| phi | 0.0021 -> 0.0013 | -0.0064 -> 0.0009 | 0.0134 -> -0.0029 | -0.0073 -> -0.0032 |

Note: in Stage 3.3 static world, Moran's I was near zero for all traits.
An increase under seasonal stress would indicate stress-driven spatial clustering.

## Plots

- `survival_plot.png` — PRIMARY: N(t) with trough shading for C and Si
- `morans_i_c1.png` — spatial trait clustering under seasonal stress
- `capacity_verification.png` — oscillation firing check (first 400 steps)
- `starvation.png` — starvation deaths with trough shading

## H1(ii) preliminary assessment

C and Si have equal minimum population (250): inconclusive.

**A=0.5 is below the population-stress threshold.** Both populations maintain N=250 throughout all 1000 steps — no population dips occur during troughs. The oscillation drives very high starvation turnover (~950 deaths/season vs ~660 in static), but replacement fully compensates. This means A=0.5, T=200 is sufficient to stress individual agents (higher mortality) but not sufficient to stress the population-level dynamics (N(t) unchanged).

**Key Stage 4.2 direction:** Increase A toward 0.75 to find the amplitude at which N(t) begins to dip during troughs. H1(ii) requires differential survival — if both C and Si maintain N=250 at all tested amplitudes, the comparison cannot be made. The starvation data hint that C seasonal has slightly higher per-season deaths in seasons 2, 4, and 5 (993, 986, 1007) vs Si (941, 934, 848), but this is high-variance and not statistically conclusive at one seed.

**Moran's I at A=0.5:** Remains near zero in all conditions (range -0.019 to +0.007). The spatial clustering hypothesis requires higher amplitude stress where agents are genuinely forced toward surviving sugar patches.

Stage 4.2 amplitude sweep required for statistical assessment (Stage 6).

## Reproducibility

All four runs used seed=42. Re-run `py -m sic_games.stage4` to reproduce.