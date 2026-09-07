# Unattended run plan — 2026-07-27, 07:45 → 18:00+ (~10.5 h minimum, extendable to 24 h)

**Pre-registered BEFORE any of these runs execute.** Every prediction and pass/fail line below is written now,
so a result cannot be reinterpreted after the fact. Where I expect a FAIL, that is stated as a prediction too —
a plan that predicts only successes is not a test.

## Why these four and not others

The session established that the substrate rungs (band size, settlement size) hit their benchmarks while the
elite/ascription layer misses them, that two mechanisms were on-but-dead in every campaign, and that budding —
now fixed — changes the settlement system substantially. The open questions that follow from that, in the order
their answers unblock other work:

| # | question | why now |
|---|---|---|
| 1 | Do the 18 destructive-pair candidates survive a null? | They are the only Battery 4 output still unusable; cheap to settle |
| 2 | Can `ascribed_frac` be brought into the EA band at all? | The one clean, systematic, world-independent benchmark miss |
| 3 | Does budding help or hurt the benchmarks? | It is a substrate change; every prior campaign ran without it |
| 4 | Does the fixed substrate cycle? | R-97's negative was measured with a leaking Malthusian brake AND no settlement-recovery mode. Both are now repaired |

---

## STAGE A (≈1 h, two tracks in parallel, 4 workers each)

### A1 — Interference null distribution
`battery4_interference.py`, 5 seeds × (10 singles + 45 pairs).

**The problem being fixed:** sub-additivity is not cancellation in a chaotic ABM — trajectory displacement does
not add linearly, so saturation and interference look identical at n=1. 18 pairs were flagged; none is usable.

- **PASS for a pair** = its displacement deficit exceeds the between-seed spread of the same measurement.
- **PREDICTION: fewer than 5 of the 18 survive.** Most are expected to be saturation artefacts.
- **`enable_nutrition_synergy` MASKED is exempt** — 0.0 is exact and already diagnosed to a code branch.

### A2 — `ascribed_frac` calibration sweep
`legit_threshold` ∈ {0.15, 0.25, 0.40, 0.60} × 2 seeds, coastal-temperate, 3000 steps.

- **Target: EA true-elite 3.6–7.8%** (`ascribed_frac` 0.036–0.078). Current: **0.19–0.38**, i.e. 3–10× too broad
  in all 7 engineered worlds.
- **PASS** = at least one setting lands in the band **while the elite survives** — noble lineage-size lift stays
  > 2.0. A setting that hits the band by abolishing the elite is a FAIL, and I expect that trap.
- **PREDICTION: the band is reachable near `legit_threshold` ≈ 0.4–0.6, but lineage lift falls below 2.0 there**
  — i.e. the two targets are in tension and the gate alone cannot fix it. If so, the ascription *criterion*
  needs changing, not its threshold.

---

## STAGE B (≈4 h, 6 concurrent arms) — budding A/B on the engineered world set

`battery5_worldset.py` extended: 7 worlds × budding {OFF, ON} × 2 seeds = 28 arms × 3000 steps.

Benchmarks, all from filed sources, scored as in Battery 5:

| benchmark | band | source | prediction |
|---|---|---|---|
| band size | 18–35 | Johnson / R-72 | HOLDS both arms (7/7 now) |
| settlement median | 50–150 | Bar-Yosef; R-63/R-64 | HOLDS both arms |
| **village size in 50–250** | — | **Alvard 2009** | **budding ON ≫ OFF** — the headline test |
| connubium | 79–332 | White 2017 MVP ≈150; Wobst simulated MES | ~4/7 both arms |
| `lineage_size_gini` | 0.51–0.68 | BHM 2009 | unchanged by budding |
| `lin_top_share` | 0.08–0.30 | T-9 Karmin | unchanged |
| `ascribed_frac` | 0.036–0.078 | EA | **FAIL both arms** (Stage A2 is the attempt on this) |
| T-7 ordering | structure range > productivity range | Smith & Codding | HOLDS on ≥2 of 3 proxies |

- **PRIMARY PASS**: budding ON puts markedly more villages in Alvard's 50–250 band than OFF, **without**
  degrading band size, settlement median, or the T-7 ordering.
- **PREDICTION**: it does — pilot at 1 seed gave 1/14 → 21/35 — **but** I expect `n_settlements` to roughly
  double, which may pull `lin_top_share` down as lineages spread thinner. That is the risk to watch.
- **FAIL** = budding fixes village size but breaks a rung that currently passes. That is a real possible
  outcome and would mean budding should stay off.

---

## STAGE C (≈4–5 h, 2 arms) — deep time on the repaired substrate

30,000 steps, `C_LOGEVERY=100` (≈300 snapshots, vs the 60–80 that made the last attempt underpowered),
budding ON, 2 seeds, coastal-temperate.

**Why the cycle question is worth reopening.** R-97's "no cycles" was a well-instrumented negative, but it was
measured on a substrate with (a) the carrying-capacity ceiling leaking — R-105, a hole in exactly the Malthusian
loop that generates secular cycles — and (b) no settlement-recovery mode, since budding never fired. Both are
now repaired. That does not predict cycles; it means the negative was taken with a compromised mechanism.

- **DISCIPLINE (R-97's own D1 rule): the detector is re-validated at 100-step spacing BEFORE any verdict** —
  inject known cycles into matched noise and confirm detection. An underpowered detector produces a worthless
  negative. No cycle verdict is emitted if that check fails.
- **PASS** = `ac_peak` above R-87's white-noise floor of **0.13** on `frac_gumsa`.
- **PREDICTION: still no cycles.** The structural argument stands — villages revolt on their own clocks with
  nothing coupling them, and neither fix creates a superordinate polity. I expect to confirm R-97 on a clean
  substrate, which is worth more than the original negative.
- Secondary, no prediction: does the wealth-in-people aristocracy persist over 30k steps, and does budding
  change the elite's trajectory.

---

## Operational

- Each stage writes results incrementally; completed arms are skipped on re-run, so a restart resumes.
- Stages run in order; a stage that crashes is logged and the next begins. No stage can block the others.
- Progress: `overnight_progress.txt`. Final report: `REPORT_overnight_2026-07-27.md`.
- **No population cap anywhere** — a cap would hide the phenomenon (standing instruction).
- If everything finishes early, Stage C's budget extends rather than adding new questions.
