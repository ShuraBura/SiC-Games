# Stage 4.1a — Variable Population

**Date:** 2026-05-17  
**Seed:** 42  
**Steps:** 1000  
**P_max_C (birth_c.p_max):** 0.075  
**P_fission_Si (birth_si.p_fission_max):** 0.12  

## Success criteria

| Criterion | Result |
|---|---|
| Null controls quasi-stationary [150,400] by t=500 | PASS |
| No Si biparental reproduction | PASS (C/Si dispatch test in test_variable_population.py) |
| Seasonal signal visible in N(t) | see plot |
| Carrying capacity respected | see carrying_capacity plots |
| Tests pass | PASS (123 tests) |
| Reproducibility | confirmed seed=42 |

## Null control summary

| Metric | C static | Si static |
|---|---|---|
| N mean (t>=500) | 344.3 | 284.5 |
| N min (all) | 168 | 153 |
| N max (all) | 394 | 350 |
| N range (t>=500) | [298, 394] | [255, 339] |
| Total births | 7660 | 5669 |
| Total deaths | 7547 | 5639 |
| Mean wealth (t>=500) | 39.4011 | 43.7628 |
| Carrying capacity est (t>=500) | 2202.6 | 2135.8 |

## Seasonal summary

| Metric | C seasonal | Si seasonal |
|---|---|---|
| N mean (t>=500) | 241.0 | 254.2 |
| N min (all) | 167 | 128 |
| N max (all) | 333 | 390 |

## P_max tuning notes

Blueprint default P_max=0.02 gives ~1.25 births/step at N=250 vs ~5.3 deaths/step → collapse.
Three failure modes encountered during tuning:

1. **Collapse (P_max too low)**: births can't offset deaths. Affects C at 0.02, 0.04; Si at 0.02.
2. **Biparental Allee effect (C only)**: at N<100, density ~0.04, ~38% agents lack a partner
   within Chebyshev r=3 → births cease → cascade collapse (C P_max=0.04).
3. **Initial cohort senescence wave**: all 250 initial agents have age=0; those with max_age≈60
   die together at t≈60-100. Senescence spike 6-9/step requires P_max≥~0.075 to buffer.

**C tuning history**: 0.02→collapse, 0.04→collapse (Allee+wave), 0.09→N_eq=602 (too high),
  0.085→N_eq≈480 (too high), 0.075→N_eq∈[298,394] **PASS**.

**Si tuning history**: 0.02→collapse, 0.12→N_eq∈[255,339] **PASS** (0.15 exploded N_eq=1067).

**Seasonal configs**: seasonal troughs (A=0.5) suppress food enough that static P_max values
  cause collapse. Seasonal configs use independently-tuned higher P_max values:
  C_seasonal P_max=0.10; Si_seasonal P_fission=0.15.

## Reproducibility

All runs: seed=42. Re-run `py -m sic_games.stage41a` to reproduce.