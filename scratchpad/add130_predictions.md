# Add.130 predictions, fixed before the data (2026-11-06)

Run: 3 worlds × 2 seeds × flag off and on, control only, to step 3,000. Observer `bp_vlog.py`, from step 1,800. Observers only.

Terms.
- A village-year is one village in one year.
- A hungry village-year has a minimum store below 1 step of adult burn per head.
- A stranded death is a settled starvation death where the store left after the draw is at least the shortfall of the dead person.
- The shortfall is the floor minus the wealth at death.

## Static reading of the code, before any run

1. `allocate_store_draw` makes one pass: `min(store * w / wsum, d)`. A leftover stays in the store. With a status exponent above zero, a low-status person can get less than the deficit while the store is stocked.
2. `_settlement_hardship` is an EMA of `1 - soil`. It does not read food. The release from the residence pin reads only this value and the size repulsion. The size repulsion has its midpoint at 150 people.
3. `enable_hunger_dispersal` is false in the canon.

## Predictions

| # | Question | Prediction | The prediction fails if |
|---|---|---|---|
| P1 | Q3 | On temperate, flag on, stranded deaths are at least half of the settled adult starvation deaths | The share is below 0.5 |
| P2 | Q3 | Stranded adults sit low in the status order of the people who draw: median percentile below 0.25 | The median is 0.25 or more |
| P3 | Q2 | Hardship does not follow food: its rank correlation with the annual starvation rate is below 0.2 in size on each world | The size is 0.2 or more on any world |
| P4 | Q2 | The rate of exit from a hungry village-year is less than 2 × the rate from a fed village-year | The ratio is 2 or more on montane |
| P5 | Q1 | Hungry village-years have a need above the ceiling in the lean season, in at least 80% of cases on montane | The share is below 0.8 |
| P6 | Q1 | On montane, flag on, a shortage is the main cause, so stranded deaths are less than a third of settled deaths | The share is one third or more |
| P7 | Age 20 | Montane deaths at ages 15-25 sit low in the status order: median percentile below 0.25 | The median is 0.25 or more |

## Controls

- C1: each run equals the stored `_vc_` run of Add.129 at each trajectory row. The observer has no behaviour.
- C2: the deaths in the log equal the model count of starvation deaths in the window.
- C3: the births and the deaths in the flow log equal the model counts at each step.
- C4: `allocate_store_draw` strands a claimant in a small known case (the positive control).
- C5: the status percentile of all people who draw has a median near 0.5 (the null floor).
