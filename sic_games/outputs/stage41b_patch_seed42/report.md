# Stage 4.1b Patch — η Formula Audit + Matched P_max Test

**Date:** 2026-05-17  
**Seed:** 42  **Steps:** 1000  
**Applies to:** Stage 4.1b codebase (no other changes).  

---

## 1. Background

The Stage 4.1b report contained this sentence in §7:

> *At birth, η(0) = η_min × (0/15) = 0. η_min only sets the floor at age 0 conceptually — the ramp formula starts at 0 when a=0 regardless of η_min.*

This was a **report text error**. The actual code in `agents/base.py` line 123 reads:

```python
return self._eta_min + (1.0 - self._eta_min) * a / a_min
```

This is the correct blueprint formula. At a=0 it returns eta_min = 0.3, not 0.
The 84.7% juvenile starvation rate was computed with the correct formula; it is a
real structural finding, not a formula artifact.

---

## 2. Task 1 — η Formula Audit

### 2.1 Formula verification

Live values from `BaseAgent.eta()` with η_min=0.3, η_old=0.4, a_min=15, max_age=80:

| Age | Observed η | Expected η | Formula | Pass? |
|---|---|---|---|---|
| a=0 | 0.300000 | 0.300000 | η_min (birth floor) | ✓ |
| a=1 | 0.346667 | 0.346667 | η_min + (1-η_min)×1/15 | ✓ |
| a=7 | 0.626667 | 0.626667 | η_min + (1-η_min)×7/15 | ✓ |
| a=14 | 0.953333 | 0.953333 | η_min + (1-η_min)×14/15 | ✓ |
| a=15 | 1.000000 | 1.000000 | 1.0 (active) | ✓ |
| a=70 | 1.000000 | 1.000000 | 1.0 (active boundary) | ✓ |
| a=71 | 0.940000 | 0.940000 | 1-(1-η_old)×1/10 | ✓ |
| a=80 | 0.400000 | 0.400000 | η_old (elder floor) | ✓ |

**Overall formula check:** PASS

### 2.2 Test suite

| Test | Result |
|---|---|
| `test_eta_formula_correctness` | PASS (η(0)=0.3, η(15)=1.0, η(80)=0.4) |
| `test_eta_boundary_values` | PASS |
| All 7 life-history tests | PASS (130/130 total) |

### 2.3 Null control comparison — Stage 4.1b original vs patched

Since the formula was correct in Stage 4.1b, the 'patched' values are identical
to the original. The comparison is a reference baseline for Task 2.

| Metric (t≥500) | 4.1b C (P=0.12) | 4.1b Si (P=0.14) |
|---|---|---|
| N mean | 306.8 | 269.7 |
| N range (t≥500) | [231, 376] | [218, 330] |
| Mean η | 0.847 | 0.856 |
| Juv starvation % | 84.7% | 77.3% |

**Note on juvenile starvation:** 77–85% is a structural consequence of the initial
wealth floor (Uniform[5,25]) combined with the juvenile η ramp. Even at η(0)=0.3,
an agent with wealth=5 and metabolism=4 net-loses wealth every step until age ~5
(when η(5)=0.3+(0.7×5/15)=0.53, and 4-sugar cell yields 0.53×4=2.1 < 4). The
agent cannot break even until η(a)×cell_sugar > metabolism — roughly age 9–10 on
a full cell, later on partial cells. With initial wealth=5 and metabolism=4, the
agent exhausts its endowment at ~step 3–5 before reaching break-even age.
Resolution: Stage 4.1c parental wealth transfer.

---

## 3. Task 2 — Matched P_max Test (P_max = 0.14)

Purpose: test whether C and Si can both run stably at P_max=0.14 to enable
unconfounded H1(ii) comparisons in Stage 4.2.

| Run | Config | P_max | Source | Gate [150,400] | N range (t≥500) | N mean | Juv starv% |
|---|---|---|---|---|---|---|---|
| A — C static | c_static | 0.14 | new run | FAIL | [468, 631] | 556.3 | 83.9% |
| B — Si static | si_static | 0.14 | Stage 4.1b cache | PASS | [218, 330] | 269.7 | 77.3% |
| C — C seasonal | c_seasonal | 0.14 | Stage 4.1b cache | PASS | [262, 400] | 318.8 | 82.4% |
| D — Si seasonal | si_seasonal | 0.14 | new run | FAIL | [0, 8] | 0.6 | 63.5% |

### 3.1 Tuning history

**C static:** Stage 4.1b used P_max=0.12 → N∈[231,376]. Raising to 0.14
increases birth rate in the prosperity zone. Expected N to rise.

**C static at 0.14:** N range=[468, 631], mean=556.3.
Gate: FAIL.

**Si seasonal:** Stage 4.1b used P_fission=0.17 → N∈[160,351].
Lowering to 0.14 may cause collapse if below the mortality threshold.

**Si seasonal at 0.14:** N range=[0, 8], mean=0.6.
Gate: FAIL.

---

## 4. Conclusion

**MATCHED P_MAX NOT VIABLE — failing: C static, Si seasonal. Structural asymmetry accepted.**

Not all runs at P_max=0.14 passed the population gate.
The birth-rate asymmetry between C and Si is structural:
- C biparental Allee effect requires higher P_max to escape the N<100 density trap.
- Si asexual fission has no Allee threshold but a different mortality balance.
Stage 4.2 documents this as a confound when comparing C vs Si seasonal dynamics.

The structural asymmetry originates from two independent causes:

1. **C static vs C seasonal gap (0.12 → 0.14):** Seasonal troughs suppress births enough
   that C seasonal needs a higher P_max to survive trough phases. At P=0.14 static, the
   prosperity-zone suppression is insufficient and C overshoots (N_mean=556).

2. **Si static vs Si seasonal gap (0.14 → 0.17):** Seasonal troughs increase starvation
   for Si without an Allee buffer. Si seasonal at 0.14 is below the fission rate needed
   to offset trough mortality.

**Locked values for Stage 4.2** (carried forward from Stage 4.1b confirmed runs):

| Config | Parameter | Value |
|---|---|---|
| C static | birth_c.p_max | 0.12 |
| Si static | birth_si.p_fission_max | 0.14 |
| C seasonal | birth_c.p_max | 0.14 |
| Si seasonal | birth_si.p_fission_max | 0.17 |

H1(ii) seasonal comparisons (C seasonal vs Si seasonal) are conducted at P_max=0.14 vs
P_fission=0.17 respectively. This difference must be noted as a confound in all
Stage 4.2 reports.

---

## 5. ROADMAP impact

- Stage 4.1b status → **✓ Complete (patched)**: η formula confirmed correct,
  report text corrected.
- Matched P_max conclusion recorded above.
- Stage 4.1c: parental wealth transfer — structural fix for juvenile starvation.

---

## 6. Reproducibility

All runs: seed=42. Re-run `py -m sic_games.stage41b_patch` to reproduce.
Parquets cached. Clear to force re-simulation.
130 tests passing: `py -m pytest tests/ -q`.