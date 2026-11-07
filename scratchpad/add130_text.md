## Addendum 130 — the per-village log: settled people starve beside a stocked store because the draw makes one status-weighted pass, in the canon as well as with `enable_village_ceiling`; on montane the hungry villages sit on cells that cannot bank; movers do not read hunger. Observers only, nothing adopted (2026-11-06, R-106)

**Why.** Add.129 stopped Stage A with three open questions. Q1: which villages run empty? Q2: why do their people stay? Q3: why do adults starve beside a store? This addendum answers them with observers only. No flag changed, and the canon does not change.

**Method.** `scratchpad/bp_vlog.py` wraps `allocate_store_draw` and `_note_starvation_state`, and reads each draw and each starvation death. It writes one line per village-year and one line per death. 3 worlds × 2 seeds × flag off and on = 12 runs, control only, to step 3,000, log from step 1,800. Seven predictions were fixed before the run (`scratchpad/add130_predictions.md`). A *hungry* village-year has a minimum store below 1 step of adult burn per head. A *stranded* death is a settled starvation death where the store left after the draw is at least the shortfall of the dead person. **Limit:** this is 100 years of log, 2 seeds and no counterfactual. It shows where the food was at each death. It does not show what a changed rule would do.

### Controls: all pass

- C1: all 12 runs equal the stored Add.129 runs at each of 121 rows.
- C2: the deaths in the log equal the model count at every step (46,134 deaths).
- C3: births and deaths in the flow log equal the model counts at every step.
- C4: the code strands a claimant in a small known case (weights 100 and 1, store 50: the second claimant gets 0.495 of a deficit of 100).
- C5: person-steps in a draw have their median in the sixth status decile on all worlds, so the status order has a fair baseline. The hazards below use that exposure.

### Scorecard of the predictions

| # | Prediction | Measured | Verdict |
|---|---|---|---|
| P1 | Temperate, flag on: stranded ≥ 0.5 of settled adult deaths | 1.000 | Pass |
| P2 | Stranded adults: median status percentile < 0.25 | 0.009 | Pass |
| P3 | Hardship rank correlation with starvation below 0.2 in size on each world | −0.17, −0.02, **−0.23** | **Fails on montane.** The sign is negative, so more hardship goes with less starvation. The claim that hardship does not read food stands. The number as written fails |
| P4 | Exit from a hungry village-year < 2 × exit from a fed one | 0.78 × on montane | Pass |
| P5 | Montane hungry village-years: need above the ceiling in the lean season in ≥ 80% | 6.8% | **Fails badly** |
| P6 | Montane: a shortage is the main cause, stranded < one third of settled deaths | 0.93 per death, 0.90 by the strict test | **Fails** |
| P7 | Montane ages 15–25: median status percentile < 0.25 | 0.025 | Pass, but it does not explain age 20. See below |

### Q3: why adults starve beside a store. Answered

`allocate_store_draw` is one pass: `min(store * w / wsum, d)`. A person with a low weight gets a small share of the store, and that share is not raised when other people are filled. The leftover stays in the store. The exponent is 1.5 in nearly all draws at a death, and the weight is a product of three status facets, so the shares are very unequal.

| Settled starvation, flag off → on | temperate | savanna | montane |
|---|---|---|---|
| Share of all starvation deaths that are in a draw | 55 → 82% | 24 → 70% | 27 → 80% |
| Stranded, per death | 0.999 → 1.000 | 0.97 → 0.97 | 0.996 → 0.93 |
| Strict: the store left covers all deaths of that village-step | 0.999 → 1.000 | 0.96 → 0.97 | 0.996 → 0.90 |
| Deaths in the lowest status decile | 93 → 93% | 93 → 84% | 98 → 59% |
| Adults: share of an equal split that the dead person got (median) | 0.009 → 0.024 | 0.013 → 0.042 | 0.009 → 0.033 |
| Adults: shortfall, in steps of their own need (median) | 0.07 → 0.09 | 0.06 → 0.06 | 0.08 → 0.08 |
| Adults: store left per claimant, in steps (median) | 21 → 6.5 | 9.4 → 2.2 | 23 → 1.4 |

So the median adult dies less than a tenth of one step short, beside a store of many steps, after a draw of 1–4% of an equal split. With the flag on, adults in the lowest status decile carry 70–230 starvation deaths per 1,000 per year. From the fourth decile up, their hazard is about 1 per 1,000 or less on temperate and savanna (first figure).

**This is in the canon, not only under the flag.** With the flag off, every world has a settled starvation that is almost all stranded: 3,564 of 3,566 deaths on temperate, with a median store of 21 steps per claimant left. The specification says that the draw "surfaces as a winter-wealth differential, not death", and the registry says that `allocate_store_draw` "already prevents starvation". Both statements are false as measured. Add.129 attributed the over-response of adults to the hard starvation step. That reading needs this addition: the people at the step are chosen by the draw.

### Q1: which villages run empty. Partly answered

Hungry village-years are 0.6 / 3.2 / 14.8% of all village-years with the flag on, and they hold 12 / 46 / 71% of settled starvation. On montane they are not over the ceiling. Need / ceiling is 0.52, the mean intake is 1.88 × need, and they are larger than fed villages (median 194 against 94 people). So the mean food is sufficient, and P5 is wrong.

**The banking gate picks them.** A cell banks only if it is cold (≤ 15.25 °C) or seasonal (amplitude ≥ 0.25), by design (Binford, Testart). Warm aseasonal forest is shut. Joined by the site cell of the village:

| Montane | Share of people | Hungry village-years | Median store | Starvation per head per year |
|---|---|---|---|---|
| Gate open, flag off → on | 72 → 70% | 0.1 → 4.8% | 20 → 17 | 0.003 → 0.013 |
| Gate shut, flag off → on | 27 → 30% | 0 → **44%** | 19 → **2.0** | 0.000 → **0.042** |

With the flag on, shut sites hold 30% of the people and 58% of settled starvation. Each of these 1,100 village-years has at least one open cell within `settle_radius`, so with the flag off the surplus of the open cells fills the store. The flag scales those pools, and the store falls. That last step is an inference, because I did not log the bank per cell. The site cell is only a proxy for the village. In the canon, savanna has a small extreme case: 79 shut village-years (0.5% of people), store 0, and 34% of the settled starvation of that world. Temperate has no shut land, so its starvation is the draw alone.

Montane deaths are therefore two things at once. The store is low (55% of deaths below 1 step per claimant), and the status order still chooses who dies, but less sharply: the hazard now falls gradually over the deciles, and children carry it in all deciles (first figure).

### Q2: why people stay. The question was wrong as asked

The static suspect was that the pin holds people, because `_settlement_hardship` reads `1 − soil`, not food. Half of this is right. Hardship does not read food. But the pin does not hold them either. On montane the hungry villages have hardship 0.77 and size repulsion 0.64, and 1.09 people per head move out each year.

The village keeps its size because the flows balance: 1.13 in against 1.09 out per head per year on montane, 0.40 against 0.35 on savanna. The rates in hungry villages are within about 20% of the rates in fed villages on those worlds. Most movers go to another village. Only 0.14 per head per year go to mobile life on montane. Temperate hungry villages differ: few people move (0.13 per head per year).

So movers do not read hunger. Add.129's sentence "people do not leave a hungry village" should read: people leave at the usual rate, and others replace them at the usual rate. The food outside is larger on two worlds: the best cell on rings 3–5 gives 3.4 / 0.55 / 4.2 burns per person against 0.68 / 0.64 / 1.3 inside. That is a bound for one extra person, not a yield for a group. I measured flows, not the decision. The link from the movement rule to the flows is an inference from the code.

### Age 20

P7 passes, but status does not explain the age. Dead adults have the same low status at all ages, and the hazard in the lowest decile is flat with age on montane (219, 203, 226 per 1,000 per year at 15–25, 26–45, 46+). A flat hazard on a falling survivorship curve puts the most deaths at the youngest adult ages. So modal age 20 is likely the signature of an age-blind cause, not a cause specific to young adults. This is an inference.

### Reading

The three questions have a shared answer. Food is present, and rules decide who gets it. The draw strands low-status people beside a stock, and this happens in the canon. The banking gate removes the buffer of warm villages when the surplus ends. Movers do not respond to hunger.

This changes the order of work from Add.129. The village ceiling exposed the draw rule, but the draw rule is older and sits in the canon. Its effect on e0, on the starvation share and on the shock response is unknown, because this addendum has no counterfactual. Any such test must watch the markers that status carries: #11 status→RS, #14 material Gini and `gini_cred`. Canon temperate already sits above the top of the e0 band (Add.124), so a gain there is not free.

### Options for the next step

| Option | Verdict |
|---|---|
| A. Design a staged test of a draw with no stranded food: same status order, and the leftover goes on to unfilled claimants until the store or the deficits end. No new parameter. Held dark, tested with the village ceiling off and on, with stop rules fixed first | **Recommended** |
| B. Keep the draw as the Hayden mechanism, and correct the specification and the registry | Possible, but then the model says that a village lets people die beside food, which the specification denies |
| C. Change the banking gate | Rejected for now. The gate is anchored, and the draw must be understood first |
| D. Make movement read hunger | Hold. Add.78 found that hunger dispersal crashes temperate e0. Retest only after A |
| E. Stage B of Add.128 | Hold, for the same reason as in Add.129 |

**Corrections.**
1. Add.129's "people do not leave a hungry village" is wrong as written for montane and savanna. Exit stays near the usual rate, and entry replaces it.
2. Add.129's "real village famine" on montane is half right. The store is low, but mean intake is about twice need, and 90% of settled deaths pass the strict stranded test.
3. My P5 and P6 were wrong. I expected a shortage over the ceiling.
4. MODEL_SPEC §4.5.11 ("not death") and the registry entry of `enable_store_anchor` ("already prevents starvation") are false as measured. I will correct them with the decision on the draw.

**Open, for the supervisor.** Choose the next step. Nothing is adopted, and the canon does not change.

![Add.130: starvation hazard by status decile](evidence/add130_status_hazard.png)

![Add.130: the store left at each settled starvation death](evidence/add130_store_at_death.png)

![Add.130: the banking gate on montane](evidence/add130_gate.png)

![Add.130: flows and the food outside](evidence/add130_flows.png)

---

