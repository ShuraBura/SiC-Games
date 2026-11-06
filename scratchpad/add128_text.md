## Addendum 128 — The brake reads a ceiling that the harvest does not obey: villages harvest 1.7–3.6 × the ceiling, the stores stay full under five years of ×0.70, and no food route to child mortality can exist today. Design for review. No model change (2026-11-06, R-106)

**Why.** Add.127 left three questions for one design. How do births stop reading the ceiling in the same step? What route takes food to child mortality? What regulates at r = 0 if the brake weakens? Add.119's error was to claim a signal without a measurement. So each candidate signal is measured here before the design relies on it. The measurement changed the question.

**Method.** Three observer runs on the Add.124 canon. Each observer reads state, draws no RNG and writes no model attribute. Run 1 (`scratchpad/bp_design_signals.py`): 3 worlds × 2 seeds × control, ×0.85, ×0.70, one year, from step 1,764 to 1,836, shock at step 1,800. Run 2 (`bp_design_store.py`): 3 worlds × 2 seeds × control, ×0.70 for one year, ×0.70 for five years, to step 1,884. Run 3 (`bp_design_acct.py`): 3 worlds × 2 seeds, control, one year, with the existing diagnostic dict `_diag_pool`.

**Instrument checks.** The arms of each seed are identical up to step 1,800 (12/12 in run 1). The run 1 control population equals the stored `pair` run at each shared step (6/6). The run 2 control equals the run 1 control in population and births at each step (6/6). In run 3 the harvest taken is 0.55–0.89 of the supply, so the account closes.

### What the measurement shows

**1. No state of a child or a mother moves in the shock year.** At ×0.70 against the paired control (first figure): the child reserve and `condition` do not move. The intake EMA of the mother falls 4–9%, and the mothers sit far above any threshold: mean 8.6 / 2.8 / 6.9 × need, 10th percentile 1.38 / 0.91 / 2.11 (temperate / savanna / montane). The share of women with a reserve below the cap is about 2%, and it rises only from 1.7% to 2.2% on temperate. So `condition`, the intake EMA of the mother and a shortfall frequency on the reserve are all dead routes as they stand. Only `fill` (+38 to +41%), the brake factor (−41 to −79%) and the raw harvest (−14 to −20% at the median) move.

**2. The intake route for births has room on savanna only.** The median intake EMA of women at risk is 3.7 / 1.4 / 3.5 and the mean intake factor is 0.87 / 0.68 / 0.92. At ×0.70 the factor falls by 0.7–1.7%.

**3. The village store does not feel the shock.** The store cap is 20.8 steps of adult burn per head. It is a real buffer, and it is nearly full.

| | temperate | savanna | montane |
|---|---|---|---|
| Store per head, control | 20.2 | 17.4 | 19.5 |
| Store per head, year 4 of ×0.70 | 20.2 | 15.5 | 18.5 |
| People with the store ≥ 90% of cap, control | 95% | 54% | 77% |
| Median village harvest / need, control | 4.4 | 1.5 | 3.9 |
| Same, in the ×0.70 shock | 3.5 | 1.2 | 3.0 |

**4. The children who starve live outside the villages.** Over runs of the control arm, 88% / 88% / 96% of the starved children aged 1–9 lived outside every village (n = 65, 68, 159). Only 3% / 4% / 33% of all children live there. Inside a village, a child effectively meets no food shortage.

**5. The food account: the harvest does not obey the ceiling.** All values are per step in units of the ceiling, the 9-cell sum at the site that `fill` uses as its denominator. Annual mean over 6 runs.

| | temperate | savanna | montane |
|---|---|---|---|
| Pool at the site cell | 0.82 | 0.53 | 0.74 |
| Bare yield, other occupied cells | 0.68 | 0.90 | 1.22 |
| Agglomeration bonus, other occupied cells | 1.13 | 0.30 | 1.61 |
| **Total supply** | **2.63** | **1.73** | **3.57** |
| Harvest taken | 2.33 | 0.96 | 3.18 |
| **Need of the members** | **0.43** | **0.50** | **0.71** |
| Need in the lean month | 0.56 | 0.68 | 0.91 |
| **Fill that the brake reads** (person weighted) | **1.22** | **1.02** | **2.40** |
| Need / supply | 0.16 | 0.29 | 0.20 |

The docstring of `_settlement_carrying_capacity` says that a village's total food "is capped at this". PARAMETERS §21.7 says "a village can't out-produce its land". The code does not do this. It applies `S = min(S, cap)` cell by cell, and each occupied cell has its own overlapping 9-cell ceiling (R-105 extended this form to non-site cells). A village occupies about 7–10 cells, so it collects several ceilings.

**6. Both sides of the ratio are wrong.** On the supply side, the village has 1.7–3.6 × the ceiling. On the demand side, `fill` reads 2.0–3.4 × the true need ratio. Its numerator counts heads at adult burn over the 25-cell window, and its denominator covers 9 cells. I did not measure the split between these causes. Add.106 found the radius part, and `enable_density_fill_matched_radius` is held dark. Together, the brake reads 1.0–2.4 while the true need / supply is 0.16–0.29.

### The diagnosis

The three questions are one defect. The brake is not a food signal. It is a density limit, calibrated on the e0–density frontier, with the climate multiplier inside its denominator. So a shock shuts the brake in the same step while nobody has less to eat. That explains Add.125–127: births over-respond, children do not respond, and `condition` is flat. A food route to child mortality is absent because in a village the food shortage itself is absent. This agrees with Add.105 ("not food-limited") and gives the mechanism at village scale.

### Answers to the three questions

**Q3, what regulates at r = 0.** Today the brake regulates, at a density set by a false reading of the ceiling. Food does not regulate. A slower brake keeps the same long-run regulator, because an EMA conserves the time mean of the factor. Food becomes a second regulator only where need approaches supply.

**Q1, how births stop reading the ceiling.** With an EMA of the brake factor, per site, with time constant τ. An offline test on the logged series gives the two-year birth response per 10% yield: τ 1.4 yr −2.6 to −12%, τ 5 yr −1.1 to −4.8%, τ 10 yr −0.6 to −2.6%, τ 20 yr −0.3 to −1.4%. Scania is −0.8% by output and −1.8% to −4% by price. So τ of 5–10 years fits. This is arithmetic on a logged series, not a model run. A linear estimate gives a damping ratio of 0.57–0.81 for these τ, with birth rate 0.035/yr and a measured factor elasticity near −2.2, and it ignores age structure. But a slow brake alone has a danger: in a long drought nothing would then contract the population for about τ years, because food does not bind. So the food account must come first.

**Q2, the route from food to child mortality.** None can be honest until a shortage exists. A child term on `fill` would fit the Scania shape, but children would then die of hunger beside a full store. That repeats the error of Add.119 in a new form, and I do not recommend it. The specs ask for a route through disease and `condition` (§21.9, Pelletier). After the food account is repaired, the first step is to measure again which signal is live. The candidates, in order: store per head, the frequency of steps with village supply below need, and `condition` on that frequency.

### Options

| Option | What it does | Verdict |
|---|---|---|
| A. Slow brake + child term on `fill` | Fits the shape. Stores stay full | **Rejected**: a false mechanism |
| B. Village ceiling, then slow brake, then measure the child route | Makes `fill`'s denominator true, then removes the same-step read | **Recommended** |
| C. B + `enable_density_fill_matched_radius` at once | Food binds on all worlds, the population rises | Second step, decided on the result of B |
| D. Ceiling over the 25-cell window | Raises the ceiling × 2.6–3.0 | **Rejected**: radius 1 is anchored (Vita-Finzi), `settle_radius` is not, and food binds even less |

**Arithmetic for option B at the present population (not a model run).** With supply = ceiling, need / supply is 0.43 / 0.50 / 0.71, and 0.62 / 0.72 / 1.01 at ×0.70. In the lean month at ×0.70 it is 0.80 / 0.97 / 1.30. The store needs about 0.6 burn per head per step of surplus to stay at cap, because `storage_decay` is 0.02 and `storable_fraction` is 0.7. So the expected result is: the montane store falls and drains under ×0.70; savanna changes least, because the forage rate cap already limits its harvest to 0.96 of the ceiling; temperate keeps a full store, and food will not bind there without option C. Population need not change at first order, because the brake does not change.

**Note about the anchor.** A store of 16 months should absorb a one-year shock. Scania had no such store. So a weak child response to one year may be correct for this society, and the five-year arm is the fairer test. Scania stays a comparator for direction and shape only.

### Plan, with the rule fixed before the data

**Stage A, one flag: `enable_village_ceiling` (name provisional), default off, no new parameter.** Scale the pools of a village pro rata, so that their sum does not exceed the ceiling at the site. Held dark through the standard list. Test: 3 worlds × 2 seeds × control, ×0.70 one year, ×0.70 five years, to step 3,000, shock at step 2,400, with the three observers.
- A1. Flag off is bit-exact. Flag on: the village sum of pools ÷ ceiling ≤ 1 at each step.
- A2. Store and need / supply: compare with the arithmetic above, world by world. A difference is a finding, not a failure.
- A3. Stop for review if the population moves more than 25%, if e0 leaves its band, or if the starvation share rises above 0.40. Add.123 found e0 19–21 when intake regulates alone, and the hard starvation step (§21.10) is the likely reason.
- A4. Agents read a perceived food per head that this flag does not change. Check emigration and fission for a side effect.

**Stage B, one flag: slow brake, τ 5–10 years, per site.** A new site takes the current value. Test: the one-year test of Add.127 and the 30-year drought of Add.125. Contraction must still pass.

**Stage C: the child route.** Repeat the signal measurement on A + B. Build a route only on a signal that moves.

**Stage D: full Stage 2,** 3 worlds × 3 seeds × 15,000 steps, on the marker set, before any adoption.

### Other findings, not in the design

- **Settled people starve beside a stocked store.** In the ×0.70 year, starvation inside villages rises from 35 to 73 deaths on temperate, 7 to 22 on savanna and 9 to 36 on montane (2 seeds), mostly adults, and on temperate in the lean months. Only 6 of those 131 deaths were in a village with less than one step of store per head. The cause is not known. One candidate is an agent that enters a village after the harvest.
- **Starved children outside villages:** 55–70% have no living mother. Refugee and orphan children outside the store are a separate route.
- Observer limits: `unfed` in run 1 reads 1.0 for children (corrected in run 2), and `_intake_ema` is the constant start value for a child because it is not updated before menarche.

### Corrections

1. Add.125–127 treated the brake as a read of food limits. It is not. Add.125's "contraction PASS" stands as a result, but its mechanism is a density limit with climate in the denominator.
2. The premise of Add.127's open item 1, "a route from food", assumed a food shortage in the village. None exists.
3. PARAMETERS §21.7 and the docstring are not true as coded. I will correct them when a flag is adopted, not before.
4. In chat today I compared raw two-year percentages with the per-10% anchor. The per-10% values above replace that, and τ moves from 10–20 years to 5–10 years. I also gave r·τ ≈ 0.2 as the stability number, which omits the gain of the brake. The damping ratio above replaces it.

**Open, for the supervisor.** Approve Stage A, or choose another option. Nothing is adopted and the canon does not change.

![Add.128: the signals in the shock year](evidence/add128_signals.png)

![Add.128: the store, the harvest, and who starves](evidence/add128_store.png)

![Add.128: the food account](evidence/add128_food_account.png)

---

