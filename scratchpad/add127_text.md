## Addendum 127 — The one-year harvest test: the gap survives on the anchor's own time scale for births and for children. Adults and starvation do respond, in the shock year, and Add.125's "no hidden onset spike" is corrected. No model change (2026-11-05, R-106)

**Why.** Add.126 compared a one-year anchor with a 30-year model mean, and left the time scale open. This test uses the anchor's
unit and the anchor's age bands. The rule for the result was written before the data.

**Method.** `scratchpad/bp_yr1.py`, `bp_yr1_run.py`, on the Add.124 canon, no model change. 3 worlds × 3 paired seeds; each run
takes 20 one-year shocks, 240 steps apart, from step 9,000 to step 13,800, alternately ×0.85 and ×0.70: 90 shocks at each depth.
One shock is too few: ages 1–9 give about 27 deaths per year per run. This replaces the single shock in the plan (`DR_LEN=12`).
Yearly raw counters are saved (`scratchpad/drought_logs/yr1_*.jsonl`). Baseline: years −4 to −2. Response window: years −1 to +1,
the model's two-year sum. Per 10%: e = Σ ln(r_k) / ln(m), response = 0.9^e − 1. CI: 95%, bootstrap of shocks within a world.
Analysis `scratchpad/bp_add127_checks.py`, `bp_add127_response.py`; evidence `docs/evidence/add127_response.json`.

**Instrument checks.**
- Control: every row before step 9,000 equals the stored `pair` run, 9/9. Two monitor columns are ignored, as in Add.125.
- Driver: the running sum of the multiplier rises by 12 × m in each shock year and by 12 otherwise, 9/9.
- Counters: yearly deaths equal `lt_deaths_total` at all 17 shared steps, 9/9.
- Timing: the shock first acts in the step that ends at count = onset. Year −1 holds one shocked month, so it is not in the baseline.
- Null floor: years +10 to +12 against the baseline, pooled: births +1.7 [+0.1, +3.4] and +1.9 [+0.2, +3.6]%. Deaths: every band
  includes zero, except ages 45–64 at ×0.85 (+3.7 [+0.3, +7.1]). The births offset can move the per-10% figure by about 2 points.
- Population against the stored control: the minimum is 0.90–0.99. Late means are 0.97–1.02, except `montane` seed 1, which ends
  at +29%. The prior rule asks for this to be reported. Without that run the pooled result does not change: births −15.7 and −14.8,
  ages 1–9 −6.1 and +0.8.

**Result, per 10% fall in food, two-year window.**

| rate | Scania, same year | Scania, two-year sum | model ×0.85 | model ×0.70 |
|---|---|---|---|---|
| births | 0.0 | −0.8 | −14.5 [−17.1, −12.1] | −13.6 [−14.7, −12.4] |
| deaths, ages 1–9 | +5.6 | +12.7 | −5.9 [−12.6, +1.2] | +0.8 [−2.2, +4.0] |
| deaths, ages 15–24 | +2.8 | +7.3 | +7.2 [−4.4, +19.8] | +2.0 [−3.0, +7.6] |

By world, births: temperate −18.5 and −18.6, savanna −17.6 and −17.6, montane −9.6 and −7.4. Ages 15–24 at ×0.85 run from −28.7
(savanna) to +25.7 (temperate), so that row has no reading by world.

**Verdict by the prior rule: the gap survives for births and for children.** The birth response is about 17× the Scania output
figure and about 3–8× the price figures (−1.8% Scania, −4% Orkney). The upper limit for ages 1–9 lies below the anchor's range at
both depths. The size is the same as in the 30-year mean (−8 to −14), so the gap is not a time-scale effect. The first limit of
Add.126 is closed.

**What the test adds.**
1. **Adults do respond.** Ages 15–24 are inside the anchor's range, with wide intervals. Ages 25–44 rise +8.6 and +7.8 per 10%. In
   the shock year, deaths at all ages rise +4.2 and +11.6%, and starvation deaths rise +33 and +64% (temperate ×0.70: +15% and
   +121%). All of it ends within one year. Children do not take part, so the deaths are not where the anchor puts them. Year +3 at
   ×0.70 for ages 1–9 shows +9.6% with no pattern around it; I do not read it.
2. **Births are a postponement in part.** Rate change in years −1, 0, +1: −6.8, −25.0, +12.3% at ×0.85; −12.4, −40.8, +17.4% at ×0.70.
3. **Births respond in the same month, with no change of body state.** Row 9,000 holds one shocked step, and the state before it is
   identical in the control and the Add.125 runs. Births, sum of 9 runs: control 235, ×0.85 127 (−46%), ×0.70 87 (−63%).
   `condition_mean` does not change at 4 decimals, in that step or in the shock year. `intake_ema_alpha` is 0.04, so the intake signal
   can move only 4% of the way to its new value in one step. This is stronger evidence than the elimination in Add.125 that the
   direct route `1 − fill^6` carries the response. It is still not an ablation.
4. **The model has no pregnancy state** (grep of `phase1_model.py` and `demography.py`). A birth is the conception event. A real shock
   cannot remove a birth that is due this month. So the same-year fall is too early as well as too large.

**Corrections (RESULTS is append-only; these replace the text named).**
1. **Add.125, "There is no hidden onset spike": FALSE.** There is a one-year spike. Its 6-year bins could not resolve it: +11.6% of
   one year is about +0.5 per 1000 per year in a 6-year mean. Add.125's result that mortality does not carry a 30-year contraction stands.
2. **Add.126, Reading 2,** said the mortality channel that moves is starvation. That stands. It did not show that the response is
   acute and adult. This addendum does.

**Limits.** Scania is agrarian, with markets, so this is direction and shape, not a target. The canon has no natural year-to-year
variation (`ENSO(amp=0.00)`, and the regime layer does not fire), so these shocks have no precedent in a run, while Scania's
elasticities come from normal-year variation. One planet, three seeds. The shocks alternate, so ×0.85 always follows ×0.70.

**Open, in order.**
1. **A design for both halves together (Opus).** Births must stop reading the ceiling in the same step, and child mortality must have
   a route from food: `condition` on shortfall frequency or flux (§21.9), a cause through disease, as the specs say. The brake regulates at
   r = 0 (Add.123), so e0 will move, and the design must say what replaces it.
2. A cause-of-death marker (MARKER_MATRIX #19 open item).

![Add.127: year-by-year response](evidence/add127_one_year_response.png)

![Add.127: response vs Scania](evidence/add127_response_vs_scania.png)

---

