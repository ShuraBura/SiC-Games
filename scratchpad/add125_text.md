## Addendum 125 — The drought test on the Add.124 canon, with exact age-specific mortality: the population contracts and recovers, but births carry all of it; mortality moves −1% to +6%, the condition signal does not respond to food, and Add.119's "weak positive check through the synergy" is RETRACTED (2026-11-04, R-106)

**Why.** Add.124 listed the drought test on the adopted canon as the next item. Add.119 recorded the limit of its own
instrument: crude rates, because a fall in births lowers the crude death rate by itself. This test removes that limit.

**Method.** `scratchpad/bp_drought.py` on the Add.124 canon, code `e262df9`, clean tree: 3 worlds × 3 paired seeds ×
yield ×0.85 and ×0.70 for 30 years (steps 9,000–9,360), to step 12,000; 18 runs. New: the wrapper saves the raw counters
at steps 9,000, 9,360 and 9,720 (pure observer). With the meta snapshot (7,500) and the final counters they give EXACT
period rates by year of age for pre (7,500–9,000), drought, after (9,360–9,720) and late (9,720–12,000).
ASDR = age-standardised death rate: the pre window's age shares applied to the window's m(x), so a fall in births cannot
move it. Analysis: `scratchpad/bp_add125_age_mortality.py`, `bp_add125_chain.py`, `bp_add125_chain2.py`,
`bp_add125_chain3.py`; evidence `docs/evidence/add125_drought_age.json`.

**Instrument checks.**
- Control: each run equals its stored `pair` run, row for row, before the onset, 18/18. Only the two monitor columns that
  the Add.124 re-score changed are ignored (`demog_in_band`, `demog_scored`).
- Positive control 1: the saved death totals equal the trajectory's `lt_deaths_total` at step 9,000 and lie between the
  bracketing rows at 9,360 and 9,720, 18/18.
- Positive control 2: the pre window's non-starvation hazard / de-warfared Siler is ×0.91–1.06 in every age band on every
  world, as in Add.122.
- Null floor: 2,600–4,700 deaths per run give a Poisson SE near ±0.5 per 1000 per year for one run, ±0.3 for the mean of
  3 seeds. The stored control runs have no counters at these steps, so the comparison for age-specific rates is
  the run's own pre window, not a paired control.

**Result 1 — the population contracts and recovers (the supervisor's requirement is met).**

| world, depth | minimum pop ratio to control | recovery to 0.95 after the drought (yr) | TFR pre → drought → after | ASDR pre → drought (per 1000/yr) | change | crude deaths − control (per 1000/yr) |
|---|---|---|---|---|---|---|
| temperate ×0.85 | 0.87–0.88 | 20–39 | 3.76 → 3.09 → 4.50 | 26.4 → 27.2 | +2.9% | +0.3 |
| temperate ×0.70 | 0.73–0.76 | 47–51 | 3.76 → 2.25 → 5.54 | 26.4 → 27.9 | +5.9% | +0.6 |
| savanna ×0.85 | 0.89–0.90 | 20–37 | 4.14 → 3.43 → 4.60 | 29.6 → 29.4 | −0.8% | −1.1 |
| savanna ×0.70 | 0.74–0.77 | 41–51 | 4.14 → 2.57 → 5.45 | 29.6 → 29.9 | +1.0% | −1.0 |
| montane ×0.85 | 0.85–0.93 | 8–95 | 4.11 → 3.55 → 4.35 | 29.4 → 29.6 | +0.7% | −0.6 |
| montane ×0.70 | 0.83–0.85 | 74–147 | 4.11 → 3.08 → 4.53 | 29.4 → 30.0 | +2.2% | −0.7 |

The pre TFR is the period value of Add.122. All 18 runs recover. Land use falls 2–10% against control; the number of
villages falls at most 2%, so the population thins inside its villages and does not abandon them.

**Result 2 — mortality does not carry the contraction.** Only temperate shows a clear ASDR rise above the null floor (+0.8 and +1.5 per 1000 per
year); montane ×0.70 is marginal (+0.65); the other cells are inside it. By age
at ×0.70, the mean ratio drought / pre is ×0.89–1.09 in every band on every world. Ages 1–15 FALL in savanna (×0.89–0.91).
The non-starvation part of the ASDR is flat (−0.8 to +0.3 per 1000 per year). The starvation part moves −0.2 to +1.4.
After the drought the ASDR falls 2.5–11% below pre, and most of that fall is starvation, which falls by up to a third:
the smaller population has more food per head. There is no hidden onset spike. In
savanna the first 6 years show +1.5 and +2.6 per 1000 per year against control, but the seed range includes zero, and
the rate then falls below control. The other worlds show less.

**Result 3 — why mortality does not respond: `condition` is flat.** At ×0.70, median intake (EMA) falls 14–19% against
control, but `condition_mean` stays at 0.992 (savanna 0.989 → 0.988). The synergy is linear in condition, so the mean
fixes it: f_syn ≈ 1.012–1.018 for children. The cause is in the signal. `condition` reads the reserve fill, and the reserve
refills to its cap at each harvest, so an agent above its need reads "full" whatever its surplus. `enable_intake_fertility`
has this comment for the same reason: the reserve "re-saturates at the cap for ~99% of agents and so carries no signal".
Add.118's fix put the constant on its correct scale (0.32 → 0.99). It did NOT make the constant a signal.

**Result 4 — what carries the contraction: the density brake on births.** Period TFR is one function of the mean
fertility factor across all worlds, depths and windows (36 points, r = 0.99 on log scales, rms 4%, TFR ∝ factor^0.69).
The factor falls from 0.17–0.18 to 0.09–0.12 at ×0.70. The factor is intake × density. The intake part can fall only to
≥ ×0.86–0.96, from `intake_ema_frac_below_hi` (a bound; that column covers all past-menarche agents, not only women at
risk). The remainder is the density brake `1 − fill^6`, where `fill = people·burn / catchment ceiling`. The ceiling sums
`tf.level`, so the drought enters directly: at a fixed population a ×0.70 yield multiplies fill^6 by 8.5. The release
works the same way: at population ×0.75, fill^6 falls to ×0.18, and TFR rises to 5.5, above pre.
**This is an inference by elimination, not an ablation.** The route through the energetic refractory is not separated.

**Retractions and corrections (RESULTS is append-only; these replace the text named).**
1. **Add.119 Reading 1, "The mechanism is the synergy: with `enable_condition_full_scale`, condition responds to food": FALSE.**
   `condition_mean` in the Add.119 `all4` runs at ×0.70: 0.9914 → 0.9913 temperate, 0.9884 → 0.9884 savanna, 0.9908 →
   0.9908 montane. I did not measure condition when I wrote that sentence.
2. **Add.119's "weak positive check": not supported.** The flat-to-rising crude rate of `all4` was most likely a composition
   effect. `all4` kept the low infant mortality of the pooled orphan divisor, so a fall in births removed fewer deaths.
   `pair` restores the infant hazard, and the crude response goes negative again in savanna and montane. This reading is
   consistent with the numbers but not measured: the `all4` runs have no age-specific counters.
3. **Add.119 Reading 4, "The fixes make mortality ABLE to respond to food", and Add.124 "the synergy is now live": FALSE**
   for the same reason.
4. **Add.119 Reading 3** expected the true age-specific rise to be larger than the crude rate shows. It is larger, but
   small: +0.4 to +1.4 per 1000 per year above the crude change.

**What this does not settle.**
- Is births-only contraction wrong? The specs hold no anchor for the split between mortality and fertility under a food
  shock (`grep` for Galloway, Lee, positive check, preventive check in MODEL_SPEC, PARAMETERS, ROADMAP, BENCHMARK_LADDER:
  nothing). The density brake exists by design to regulate before starvation. Its exponent 6.0 was calibrated on the
  stationary e0–density frontier (R-106, 2026-09-06), never on a shock.
- The brake reads the catchment ceiling directly. No energy signal or body state stands between the ceiling and the
  conception. That is a modelling choice to examine, whatever the anchor says.
- One planet, three demographic seeds, one drought shape.

**Open, in the recommended order:** (1) find an anchor for the mortality/fertility split under a food shock in foragers or
pre-industrial records; (2) if the anchor asks for a mortality response, rebase `condition` on the energy flux
(`_intake_ema`), the fix already made for fertility, with a Stage 2 and a drought test, because e0 will move; (3) an
ablation that holds the brake's ceiling at its pre-drought value, to prove Result 4. No model change in this addendum.

![Add.125: mortality, age, signals, fertility](evidence/add125_drought_on_canon.png)

![Add.125: population](evidence/add125_drought_population.png)

---

