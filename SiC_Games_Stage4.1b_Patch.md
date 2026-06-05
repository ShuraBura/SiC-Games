# SiC Games — Stage 4.1b Patch: η Formula Fix + Matched P_max Test

**Version:** 1.0
**Applies to:** Stage 4.1b codebase.
**Scope:** Two tasks only. No new mechanics.

---

## Context

Two issues identified in Stage 4.1b report review:

1. **η formula implementation error.** The blueprint specified:
   $$\eta(a) = \eta_{\min} + (1 - \eta_{\min}) \cdot \frac{a}{a_{\min}} \quad a < a_{\min}$$
   giving η(0) = η_min = 0.3 at birth. The implementation used:
   $$\eta(a) = \eta_{\min} \cdot \frac{a}{a_{\min}}$$
   giving η(0) ≈ 0.02 at birth. This caused near-zero juvenile foraging
   efficiency and is the primary driver of the 77-85% juvenile starvation rate.
   The implemented formula is wrong. Fix it to match the blueprint.

2. **Unmatched P_max across configs.** C static uses P_max=0.12, C seasonal
   uses 0.14, Si static 0.14, Si seasonal 0.17. H1(ii) comparisons between
   C and Si seasonal are confounded by different birth rates. Test whether
   matched P_max values are viable after the η fix.

---

## Task 1 — Fix η formula

### Change required

In `agents/base.py` (or wherever η(a) is computed), replace:

```python
# WRONG — currently implemented
if age < forage_age_min:
    eta = eta_min * (age / forage_age_min)
```

with:

```python
# CORRECT — matches blueprint
if age < forage_age_min:
    eta = eta_min + (1 - eta_min) * (age / forage_age_min)
```

Verify: η(0) = eta_min = 0.3, η(forage_age_min) = 1.0. Run the existing
`test_life_history.py::test_eta_formula_correctness` — it should now pass
where it previously failed (or was passing against the wrong formula).

**If the test was written against the wrong formula** (i.e., it tested
η(0)≈0.02 and passed), fix the test to match the blueprint before fixing
the code. The test is the spec; if the test was wrong, fix test first,
then code.

### Re-run null controls

After fixing η, re-run C static and Si static null controls with the
**Stage 4.1b P_max values** (C: 0.12, Si: 0.14). Report:

| Metric (t≥500) | 4.1b original | 4.1b patched |
|---|---|---|
| N mean (C) | 306.8 | ? |
| N mean (Si) | 269.7 | ? |
| Juv starvation % (C) | 84.7% | ? |
| Juv starvation % (Si) | 77.3% | ? |
| Mean η (C) | 0.847 | ? |
| Mean η (Si) | 0.856 | ? |

Expected: juvenile starvation drops substantially (target < 60%).
If it does not drop below 60%, document why and accept as structural
pending Stage 4.1c support pool. Do not further tune η_min.

---

## Task 2 — Matched P_max test

### Purpose

With k_stress=10 active and η formula corrected, test whether C seasonal
and Si seasonal can both run stably at the same P_max value. If yes,
Stage 4.2 amplitude sweep uses matched birth rates — clean H1(ii) comparison.
If no, document the structural reason (Allee threshold vs fission) and
accept different P_max as a permanent feature of the C/Si comparison.

### Protocol

Run four configs at matched P_max = 0.14 (the Stage 4.1b C seasonal value):

| Run | Config | P_max / P_fission |
|---|---|---|
| A | C static patched | 0.14 |
| B | Si static patched | 0.14 |
| C | C seasonal patched | 0.14 |
| D | Si seasonal patched | 0.14 |

Report N range (t≥500) for each. Success = all four maintain N ∈ [150, 400].

If Si at P_max=0.14 overshoots (N > 400 sustained): try 0.13. If Si collapses
at 0.14: matched P_max is not viable — document and accept asymmetry.

**Do not run more than 3 P_max values for Si in this task.** If matched
P_max is not found within {0.13, 0.14, 0.15}, accept asymmetry and move on.
The goal is a quick feasibility check, not exhaustive tuning.

---

## Report format

Single patch report `outputs/stage41b_patch_seed42/report.md`:

### η formula fix verification

| Check | Expected | Observed | Pass? |
|---|---|---|---|
| η(0) = eta_min = 0.3 | 0.3 | ? | ? |
| η(forage_age_min) = 1.0 | 1.0 | ? | ? |
| η(tau_max) = eta_old = 0.4 | 0.4 | ? | ? |
| test_eta_formula_correctness | PASS | ? | ? |

### Null control comparison (patched η)

| Metric (t≥500) | 4.1b original | 4.1b patched |
|---|---|---|
| N mean (C) | 306.8 | ? |
| N mean (Si) | 269.7 | ? |
| Juv starvation % (C) | 84.7% | ? |
| Juv starvation % (Si) | 77.3% | ? |
| Mean η (C) | 0.847 | ? |
| Mean η (Si) | 0.856 | ? |

### Matched P_max test

| Run | P_max | N range (t≥500) | N mean | Pass [150,400]? |
|---|---|---|---|---|
| A — C static | 0.14 | ? | ? | ? |
| B — Si static | 0.14 | ? | ? | ? |
| C — C seasonal | 0.14 | ? | ? | ? |
| D — Si seasonal | 0.14 | ? | ? | ? |

### Conclusion

One of:
- **Matched P_max viable:** all four runs pass at P_max=0.14. Stage 4.2
  uses P_max=0.14 for both C and Si.
- **Matched P_max not viable:** Si collapses or overshoots at 0.14.
  Structural asymmetry documented. Stage 4.2 uses C: 0.14, Si: [tuned value].
  H1(ii) comparisons note the birth rate difference as a confound.

---

## Coding-agent directives

1. **Fix test before code if test was wrong.** Check whether
   `test_eta_formula_correctness` was testing the correct formula.
   If it passed against η(0)≈0.02, it was testing the wrong thing.
   Fix the test assertion first, confirm it fails, then fix the code,
   confirm it passes.

2. **No other code changes.** This patch touches one formula and
   runs parameter tests. Nothing else changes.

3. **Load Stage 4.1b parquets for reference.** Do not re-run Stage 4.1b
   configs — compare against cached parquets only.

4. **Report completeness rule applies.** Every criterion needs a number,
   not just PASS/FAIL. Every tuning attempt documented. No "see plot"
   without accompanying numbers.

5. **Update ROADMAP.md** at completion: record patched η_min values,
   matched P_max conclusion, and update Stage 4.1b status to
   "✓ Complete (patched)".

---

## Out of scope

- Support pool. → Stage 4.1c.
- Cred-modulated birth. → Stage 4.2.
- Any other parameter tuning beyond P_max matching test.
- Multi-seed ensemble. → Stage 4.2+ after parameters locked.
