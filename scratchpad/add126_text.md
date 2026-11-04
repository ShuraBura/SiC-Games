## Addendum 126 — The anchor for the drought response: real populations answer a food shock with DEATHS as well as births, the model answers with births alone, and its birth response is about ten times too large. Direction only, no model change; the time scales differ, so a one-year test comes next (2026-11-04, R-106)

**Why.** Add.125 asked if a contraction carried by births alone is a defect, and said the specs held no anchor. That
statement was too strong. My grep used four names. A wider search of the specs and the literature follows.

**What the project's own specs already said (correction to Add.125).**
- MODEL_SPEC (cause-of-death section, Hill & Hurtado 1996; Hill, Hurtado & Walker 2007): the Aché table has no nutritional
  category, and the Hiwi nutritional row is about 0 before contact. The spec's reading: nutritional stress acts through
  disease, not through direct starvation, and child starvation should calibrate to about 0.
- R-32 and MODEL_SPEC §4.8.14: `_condition` is a survivor-biased signal that stays pinned under scarcity.
- PARAMETERS §21.9: `_condition` is near-uniform, there is no chronic-malnutrition state to detect, and it should stay off
  until it reads shortfall FREQUENCY, not reserve LEVEL. §21.10 made that move for fertility only.

So Add.118's `condition_full_scale` rescaled a known constant, Add.119's claim contradicted the record, and Add.125
rediscovered R-32. In the canon, starvation is 17–29% of all deaths and is the only mortality channel that moves with
food (Add.125), and the disease channel that the anchors name is the one that is flat. MARKER_MATRIX #19 already lists
"no cause-of-death marker yet" as open.

**The anchor** (`docs/LITERATURE.md`, Dribe, Olsson & Svensson 2010, Table 3): Scania, about 400 parishes, 1749–1859,
annual, elasticity to grain OUTPUT, the nearest analogue of the model's yield.

| rate | same year | lag year | 10% less output, same year | two-year sum |
|---|---|---|---|---|
| births | −0.001 (n.s.) | +0.082 | 0.0% | −0.8% |
| deaths, ages 1–9 | −0.521 | −0.612 | +5.6% | +12.7% |
| deaths, ages 15–24 | −0.261 | −0.404 | +2.8% | +7.3% |

**The model on the same scale**, 30-year window (`scratchpad/bp_add126_anchor.py`,
`docs/evidence/add126_response_vs_scania.json`); % change in the rate for a 10% fall in yield:

| rate | temperate | savanna | montane | Scania, one-year shock |
|---|---|---|---|---|
| births | −11.9 to −14.1 | −11.5 to −13.2 | −8.2 to −9.1 | −0.8 |
| deaths, ages 1–15 | +0.4 to +1.6 | −2.2 to −3.2 | −1.3 to −3.5 | +5.6 to +12.7 (ages 1–9) |
| deaths, ages 15–45 | +2.6 to +3.6 | −1.5 to +1.0 | −0.9 to −0.5 | +2.8 to +7.3 (ages 15–24) |

First 6.25 years against the paired control, nearest in the existing runs to a short shock: births −18 to −35% at ×0.85
and −33 to −64% at ×0.70. Deaths: −4 to +4%, and the seed ranges include zero except in temperate, where they fall.

**The other sources agree on direction; they differ on size.**
- Responses to PRICE, per 10% (a price is not a food supply): births −1.5% (Scania), −4% lagged, p = 0.06 (Orkney, Jennings,
  Quaranta & Bengtsson 2017). Child deaths +3 to +20% (Orkney +20%, and the same paper's review: Italy +11%, Sweden +4% for
  real wages, Belgium +3%). Infants do not respond in Orkney (−2.9%, n.s.).
- Galloway 1988 and Lee 1990, abstracts only: births fall and deaths rise with grain prices in pre-industrial Europe;
  fertility dips and rebounds. I hold no numbers from these two.
- Dyson 1993, South Asia: conceptions fall promptly and almost universally; the rise in deaths is less certain and depends
  on disease, migration, relief and rain.
- de Waal, Taffesse & Carruth 2006, Ethiopia 2002–03: no measurable rise in child mortality in the general population. A
  real drought can pass without a mortality response.
- China 1959–61 (Cai & Wang 2010, official statistics): deaths 10.8 → 25.3 per 1000, births 34 → 18 per 1000, then 43.4 in
  1963. This is the worst famine on record. The model's first years at ×0.70 cut births by as much with no rise in deaths.
- No source gives a direct forager measurement of this split. The search found no replicated test.

**Reading.**
1. **What the model gets right:** contraction and recovery; births respond first (Dyson); the rebound above normal (Lee;
   China 43.4); infants do not respond (Orkney; Scania per the Lund paper).
2. **What the model gets wrong, by this anchor:** the birth response is about 10 times too large on the same axis. Ages
   1–15 do not rise, and in savanna and montane they fall. The carrier is the wrong one: the anchor has mortality carrying
   more than births, and the mortality channel in the model that moves is starvation, not disease.
3. **So births-only contraction is a defect, in size and in channel,** subject to the limits below. The Add.123 finding
   stands that the density brake is what regulates at r = 0; this addendum says that the same brake over-responds to a shock.

**Limits. Do not read these numbers as a calibration target.**
- **Time scale.** Scania is a one-year deviation. The model's table is a 30-year mean, in which the population has time to
  adjust. The comparison of the columns is therefore not like with like. The 6-year numbers are closer but not equal.
- **Population.** Scania is agrarian, with markets, in the historical record. Foragers can move and share. The anchor gives
  direction and shape, not a target.
- **Linearity.** Elasticities from normal-year variation need not hold at −30%.
- Abstracts only for Galloway, Lee and Dyson. The Scania and Cai & Wang numbers are read from the chapters, Table 3 and the
  introduction.

**Open, in order.**
1. **One-year harvest test on the canon,** the same unit as the anchor: `DR_LEN=12`, ×0.85 and ×0.70, yearly counters, no
   model change. It decides if the 10× gap survives on the anchor's own time scale.
2. **If it does, a design for both halves together:** `condition` reads shortfall frequency or flux (§21.9); the brake is
   weakened or fed through intake instead of the ceiling. The two cannot be separated, because the brake regulates at
   r = 0 (Add.123) and e0 will move.
3. A cause-of-death marker (MARKER_MATRIX #19 open item), so the starvation share is scored.

![Add.126: response to a food shock, model vs Scania](evidence/add126_response_vs_scania.png)

---

