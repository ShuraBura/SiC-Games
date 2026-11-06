## Addendum 129 — Stage A of Add.128: `enable_village_ceiling` makes the food account true and a food signal live, and children respond to a shock for the first time on two worlds; but A3 trips, montane regulates by starvation (e0 24, starvation share 0.52), and the flag stays dark. Stopped for review (2026-11-06, R-106)

**Why.** Add.128 found that a village harvests 1.7–3.6 × the ceiling that the brake reads. Stage A applies that ceiling to the village sum, and tests the result against rules that were fixed before the data.

**Build (`85b3017`).** `enable_village_ceiling`, default off, no new parameter. The harvest computes the pool of each occupied village cell before the loop, then scales the pools of one village pro rata, so that their sum does not exceed the ceiling at the site. The per-cell ceiling stays. The flag is in `_skip`, the audit types and prerequisites, `full_campaign.toml`, both allowed-dark lists and the ladder. Suite: 1,796 passed, 1 xfail. New file `test_village_ceiling.py`, with the positive control (the defect is visible with the flag off).

**Method.** 3 worlds × 2 seeds × 4 arms = 24 runs: flag off control; flag on control, ×0.70 for one year, ×0.70 for five years. To step 3,000 (250 years), shock at step 2,400, the three observers of Add.128 chained on one run (`scratchpad/bp_stageA.py`) from step 2,364. Life table: steps 1,200–3,000. **Limit:** this is 250 years and 2 seeds, not a Stage 2 scorecard at 15,000 steps. The numbers below are not marker verdicts.

### A1, instrument: PASS

- Flag off equals the stored `pair` run of Add.124 at each of 121 rows on all 6 runs, in population, births, starvation, villages and `gini_cred`. So the flag-off path is bit-exact in the real pipeline.
- The arms first split at the onset step on all 12 pairs.
- The observer read a village sum / ceiling up to 1.0116. A direct check (`bp_stageA_a1check.py`, savanna, 240 steps) compared the sum with the ceiling read during the harvest: of 1,686 village-steps at the ceiling, 1,680 equal a harvest-time read, none exceeds every read, and the worst ratio is 1 + 7×10⁻¹⁶. The excess is the time of the read, not a leak.

### A2, the food account against the arithmetic of Add.128

Control, flag off → on, in units of the ceiling.

| | temperate | savanna | montane |
|---|---|---|---|
| Supply | 2.65 → 0.91 | 1.77 → 0.88 | 3.53 → 0.96 |
| Harvest taken | 2.39 → 0.87 | 1.04 → 0.62 | 3.20 → 0.89 |
| Need | 0.44 → 0.36 | 0.52 → 0.38 | 0.69 → 0.41 |
| `fill` read by the brake | 1.27 → 1.08 | 1.08 → 0.74 | 2.09 → 0.90 |
| Store per head, mean (cap 20.8) | 20.3 → 17.3 | 16.8 → 11.9 | 19.1 → 10.6 |
| Store per head, 10th percentile | 19.9 → 10.0 | 10.0 → 3.0 | 16.3 → 0.65 |
| People with store ≥ 90% of cap | 95 → 58% | 48 → 19% | 71 → 21% |
| People with store < 1 step | 0 → 0% | 1 → 2% | 0 → 17% |

Three of my four predictions were wrong or incomplete, and the differences are the finding (A2 says that a difference is a finding):

| Prediction in Add.128 | Measured |
|---|---|
| Montane store drains under ×0.70 | Stronger than predicted: it is low in the **control**, with no shock |
| Savanna changes least | **Wrong.** Savanna has the largest population fall and a large store fall. A forage rate cap trims a share, and it does not protect a pool that is cut pro rata |
| Temperate keeps a full store, food will not bind | **Partly wrong.** The store stays high, but the share at the cap falls from 95% to 58% |
| Population need not change at first order, because the brake does not change | **Wrong.** I looked at the brake only and forgot the intake factor. See below |

**What I missed: the second regulator is live.** The intake EMA reads a woman's harvest, not the store. So it falls with the harvest, and the median falls 2.5 / 1.6 / 2.6 ×. The mean intake factor falls from 0.88 / 0.66 / 0.95 to 0.64 / 0.33 / 0.70. The brake factor rises at the same time, 0.18 / 0.28 / 0.16 to 0.27 / 0.65 / 0.48, because fewer people read a lower `fill`. So part of the regulation moved from the density limit to a food signal. Answer to Q3 of Add.128, now measured: food regulates births with the flag on.

### A3, the stop rules: TRIPPED. Stopped for review

Control, mean of 2 seeds, flag off → on. Population over steps 1,800–3,000.

| | temperate | savanna | montane | Rule |
|---|---|---|---|---|
| Population | 6,084 → 4,940 (**−19%**) | 3,656 → 2,404 (**−34%**) | 4,569 → 3,069 (**−33%**) | stop above 25% |
| By seed | −20, −18% | −37, −32% | −39, −24% | |
| e0 | 37.2 → 33.6 | 34.7 → 35.1 | 34.5 → **24.2** | band 21–37 |
| l(15) | 0.665 → 0.654 | 0.633 → 0.654 | 0.637 → **0.501** | band 0.45–0.66 |
| Survival 15→45 | 0.643 → 0.557 | 0.615 → 0.609 | 0.602 → **0.463** | |
| Starvation share | 0.19 → 0.32 | 0.27 → 0.33 | 0.24 → **0.52** | stop above 0.40 |
| Modal adult age at death | 73.5 → 74.0 | 74.0 → 71.5 | 74.0 → **20.0** | |

Two rules trip: population on two worlds, starvation share on montane. e0 stays in the band on all worlds, but a 10-year loss on montane and a modal adult death at age 20 are not an acceptable state, whatever the band says. The montane population number has a wide spread, because its flag-off control has a wide spread between seeds (5,191 against 3,947).

**The three worlds are three different results.**

- **Savanna is a clean result.** Population falls by a third, but e0 and l(15) rise and starvation deaths per year fall (31 → 22). Regulation moves to births through the intake factor (0.33).
- **Temperate loses e0 through adults.** Survival 15→45 falls 0.643 → 0.557 and settled adult starvation rises 8.7 → 20.1 per year (2 seeds). These adults die beside a stocked store: median 5.5 steps per head, and only 8% of settled deaths are below 1 step. This is the unexplained finding of Add.128, now 2.3 × larger, and it may carry the whole e0 loss.
- **Montane has real village famine.** Settled starvation rises 7.5 → 54.7 per year. Settled children aged 1–9 rise 0.15 → 13.1. Now 62% of settled deaths are below 1 step of store (flag off: 1%). The mean store is 10.6 and the 10th percentile is 0.65, so some villages are empty and others are not. I have no per-village log, so I do not yet know which villages run empty, or why they keep their people.

### A4, side effects of an unchanged perceived food

| Control, off → on | temperate | savanna | montane |
|---|---|---|---|
| Villages | 53 → 47 | 28 → 24 | 22 → 21 |
| Median village size | 98 → 85 | 112 → 93 | 121 → 107 |
| Mobile share | 2.2 → 2.3% | 2.9 → 1.4% | 20.1 → 18.6% |
| Bands | 104 → 72 | 57 → 20 | 119 → 88 |
| `gini_cred` | 0.53 → 0.51 | 0.37 → 0.41 | 0.41 → 0.45 |

Village size stays in the Bar-Yosef band. **People do not leave a hungry village:** the mobile share does not rise on any world. That agrees with the flag, because the movement rule reads a perceived food that the flag does not change. This is a candidate cause of the montane famine, not a proven one. I measured stocks here, not flows. The fall in the band count on savanna is large and I did not expect it. The cut in S also reaches prowess and hides, through the meat and forage credit. Stage D must check those markers.

### The shock: what moved for the first time

Flag on, ×0.70 for five years, arm / control over the first two years, as a per-10% value of yield (Scania: direction and shape only). Counts are from 2 seeds.

| Per 10%, two-year | temperate | savanna | montane | Scania |
|---|---|---|---|---|
| Deaths 1–9 | +1.0 (93 / 90) | **+22** (83 / 42) | **+22** (278 / 141) | +12.7 |
| Deaths 15–44 | +14.5 (321 / 203) | +34 (161 / 59) | +31 (316 / 127) | +7.3 (ages 15–24) |
| Births | −24 | −9.0 | −13 | −0.8 (price route −1.8 to −4) |

- **Children respond to food on two worlds.** Add.127 found no response on any world. This is the route that Add.128 said could not exist without a shortage.
- **Adults respond too much.** They respond more than children on all worlds, which is against the Scania shape. The hard starvation step (§21.10) is the likely reason, because no disease route carries the risk.
- **Births still over-respond:** −9 to −24 per 10%, against −0.8 by output and −1.8 to −4 by price. The same-step read of the brake is still there, as the step in the births panel of the shock figure shows. That is Stage B's job.
- **A slow food route for births exists.** In years 3–5 of the five-year shock, the intake factor falls 4.9 / 10.9 / 13.4%, with no new parameter. In year 1 it does not move (−1.9 / +3.0 / −0.2%), because it is an EMA.
- **`condition` and child reserves stay flat.** Child `condition` changes by 0.3% or less. So the child deaths arrive by the hard step, not by the disease route that §21.9 specifies. This is the open half of Q2.
- **The population contracts and recovers.** The minimum against the control is −12 / −10 / −17% near year 5. Births rebound above the control, deaths fall below it for years 6–10, the store recovers, and by years 11–20 the population is within 2% of the control. The one-year shock costs 3–5% of the population, and the store falls by about one step, as Add.128 expected.

### Reading

The diagnosis of Add.128 holds: a true ceiling makes a food signal where none existed. The store moves, the intake factor regulates, and children respond. But the ceiling alone is not safe. It moves the model toward the failure of Add.123: where food binds, the regulator is the hard starvation step, and people cannot leave. The flag is not adoptable as it stands, and I do not recommend Stage B now. Stage B removes the only fast brake, and on montane that brake is what holds the food signal back from more famine.

### Options for the next step

| Option | Verdict |
|---|---|
| A. Diagnose before any new flag: observers only, flag on, per-village log. Which villages run empty, why their people stay, and why temperate adults starve beside a store | **Recommended** |
| B. Build Stage B now | Rejected: it weakens the fast brake while starvation regulates montane |
| C. Add `enable_density_fill_matched_radius` | Hold: `fill` still reads about 2–3 × need, but a looser brake sends more people into a binding food limit |
| D. Scale the ceiling (`catchment_ceiling_mult` > 1) | Rejected for now: a tuned knob with no diagnosis. The ceiling on steep land may be too low, but that is a claim to measure |

**Corrections.**
1. Add.128's "population need not change at first order" is wrong. It omitted the intake factor.
2. Add.128's "savanna changes least" is wrong.
3. Add.128's "temperate will not bind without option C" is partly wrong.
4. Add.128 said that a slow brake alone is unsafe because food does not bind. With the flag on food binds, so that reason changes. The new reason is above.

**Open, for the supervisor.** Choose the next step. Nothing is adopted, and the canon does not change.

![Add.129: population over the run](evidence/add129_population.png)

![Add.129: the gates, the store and who starves](evidence/add129_gates.png)

![Add.129: the shock, annual, flag on](evidence/add129_shock.png)

---

