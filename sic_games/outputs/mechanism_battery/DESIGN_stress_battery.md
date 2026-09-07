# Stress battery — design

**Purpose.** Batteries 1–5 ask *does each mechanism do anything* and *does the model hit its targets at one
configuration*. Neither asks **does it survive being pushed**, and neither maps the **envelope** over which a
benchmark actually holds. Every serious defect this project has found appeared at an extreme — the R-105 runaway
after 1,750 steps at high density, the cred ablation crash when a variable went to zero, the budding cascade at
400+ settlements. None of those is reachable by testing the middle of the range.

---

## Design rules — earned, not invented

Each rule below exists because ignoring it cost us something concrete this session. They are binding on every
stage.

| rule | what it cost when missing |
|---|---|
| **Verdicts need a precondition check.** A dead world is not a dead mechanism. | The catchment ceiling read VACUOUS in a world with **zero settlements** |
| **Null + positive control BEFORE any verdict.** | An audit returned "no defects" while structurally unable to find one |
| **Scope derived from the model, never a hand-list.** | 15 of 75 mechanisms were invisible to the audit for months |
| **Re-check every benchmark against LITERATURE.md first.** | Scored connubium 0/7 against a target the project had **retired two weeks earlier** |
| **Effect sizes need a null distribution.** | 18 "destructive interference" pairs; **0 survived** replication |
| **The instrument gets its own tests.** | The battery caught **three bugs in itself** before emitting a verdict |
| **Seeds must beat the known variance.** | R-65 documented **30× seed variance** in %stratified; 2 seeds cannot see past it |

---

## S1 — ABLATION SWEEP: every mechanism off, one at a time

75 mechanisms knocked out individually from a full-live baseline. Not liveness — **survival**.

**Checks per ablation:** completes without exception · population does not go extinct · no NaN/negative in any
tracked quantity · charter invariant for its type still holds.

**Why:** the `ZeroDivisionError` that made the cred ablation unrunnable was found *by accident*. An ablation is
the control you run to ask "how much of this result comes from X at all?" — if it cannot execute, every claim
that would have been checked against it is unchecked. There are 74 more ablations nobody has ever run.

**PASS:** 75/75 execute. Any crash is a defect, full stop.

---

## S2 — PARAMETER EXTREMES: each magnitude at its bounds

Every mechanism with a gain, run at the **min and max** of its documented range (and at 0 and 10× where no range
is documented — flagged as unbounded).

**Checks:** no runaway (population bounded by the land) · no collapse to extinction · quantities stay finite ·
the mechanism's invariant holds at both ends.

**Why:** R-105 was a *parameter regime* failure — superlinear returns with no ceiling. It was invisible at
typical settings and catastrophic at high density. Extremes are where sign errors and missing guards live.

**PASS:** no crash, no unbounded growth, no extinction at any bound. Findings are ranked by how far inside the
documented range the failure begins.

---

## S3 — WORLD ENVELOPE: degenerate and extreme worlds

| world | what it probes |
|---|---|
| 10 agents | small-number degeneracies (the R-82 trap: an operator on a unit of size 1–2 is inert by construction) |
| 30,000 agents | scaling, and the R-105 runaway regime |
| zero-productivity boreal | graceful extinction vs crash |
| maximum-productivity tropical | the runaway regime from the other side |
| fully circumscribed (patch 12) | no room to move — Carneiro's limit |
| unbounded (patch 60) | free dispersal |
| all-water / no-water | boundary handling |

**PASS:** every world either runs or dies *gracefully*. Extinction is a valid outcome; an exception is not.
Each mechanism reports which of these worlds satisfies its precondition — this is the **regime map** Battery 1
lacked, and it is what turns "INERT" into "untestable here, live there".

---

## S4 — BENCHMARK ENVELOPE: where each target holds, not whether it passed once

7 worlds × **5 seeds** × 3,000 steps, budding on and off. Each benchmark gets a **pass fraction and a range**,
not a binary.

| benchmark | band | source |
|---|---|---|
| band size | 25 [18–35] | Johnson / R-72 |
| settlement median | 100 [50–150] | Bar-Yosef; R-63/R-64 |
| village size | 50–250 | Alvard 2009 |
| connubium | 150 [79–332] | White 2017 MVP; Wobst simulated MES |
| `lineage_size_gini` | 0.51–0.68 | BHM 2009 |
| `lin_top_share` | 0.16 [0.08–0.30] | T-9 Karmin |
| `ascribed_frac` | 0.036–0.078 | EA true-elite — **currently 0/7** |
| BHM composite Gini | 0.25 ± 0.04 forager / 0.48 agricultural | T-5 |
| father–son big-man | ~0.75 | T-6 Hayden (met: 0.769) |
| desertion : deposition | ~65% desertion | T-8 Boehm (met: 62–74%) |
| T-7 ordering | structure range > productivity range | Smith & Codding |
| fission rate | 2–5×10⁻³ /large-village-yr | Bandy (met: 5.6×10⁻³) |
| status→RS | r ≈ 0.15–0.19 | von Rueden |
| orphan mortality | ×5.09 mother / ×3.05 father | R-74 |

**Every band is re-verified against LITERATURE.md at run time**, and a benchmark whose anchor has been retired
or superseded is **skipped with a note rather than scored** — the connubium-475 mistake, made unrepeatable.

**PASS:** each benchmark reports pass-fraction across arms plus the conditions under which it fails. A target
that holds in 5/7 worlds is more informative than one scored pass/fail at a single point.

**Free prediction to settle here** (sitting untested in TARGETS.md T-8): *"turning on settlement-scale
institutions should shift the model toward the deposition channel."* Pre-registered, tested by the
budding/settlement arms.

---

## S5 — CONSERVATION UNDER STRESS

The charter's operator invariants checked **continuously during** S1–S3 runs, not only in a flip test:
X conserves its quantity · P extracts ≤ availability · D is non-increasing · A moves no quantity · H acts only
at birth.

**Critically, per-capita.** Battery 2's conservation check produced a false positive by comparing totals when
the population had changed by 10%. Totals are not the invariant.

**PASS:** no violation outside float tolerance. A violation is located to the operator, not just reported.

---

## S6 — LONG-HORIZON DRIFT

2 seeds × 30,000 steps, tracking population, material stock, lineage count, settlement count, cred Gini for
**late-onset** instability.

**Why:** R-105's runaway sat quiet for **1,750 steps** before it tipped. Any battery that runs 400 steps is
structurally blind to it.

**PASS:** no quantity grows without bound; no metric goes flat-then-explodes. Ratchets that are *supposed* to
be monotone (legitimacy) are declared as such in advance so they are not misread as drift.

---

## Cost and order

| stage | runs | ~time |
|---|---|---|
| S1 ablation | 75 | 10 min |
| S2 extremes | ~80 | 15 min |
| S3 envelope | ~10 | 20 min |
| S5 conservation | (rides on S1–S3) | — |
| S4 benchmark envelope | 70 | 4 h |
| S6 long horizon | 2 | 4 h |

≈ 9 h, so it fits one unattended night. Order is deliberate: the cheap stages that find **crashes** run first,
so a defect is known before four hours of benchmark arms are spent on a broken substrate.

**Reporting:** every stage emits PASS / FAIL / **UNTESTABLE** with the unmet precondition named. Predictions
pre-registered before execution, including the ones expected to fail.
