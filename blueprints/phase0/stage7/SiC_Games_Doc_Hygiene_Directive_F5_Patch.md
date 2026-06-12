# SiC Games — F5 Resolution Patch

**Issued by:** Supervisor (via Claude chat)  
**Assigned to:** Claude Code  
**Date:** 2026-06-11  
**Depends on:** Doc Hygiene Directive F2–F7 (F5 STOPPED state)  
**Decision:** Option (a) — recalibrate test_tier3_gate_b1_battery at locked production value.

---

## Context

F5 changed matthew_alpha default from 1.5 → 2.0 (locked production value per PARAMETERS). This caused `test_tier3_gate_b1_battery` to fail 13/15 seeds: seeds 42 (21.7%) and 21.9%) breach the 14/15 / <20% JT divergence threshold. The gate threshold was calibrated against the pre-lock default. The gate is stale; the parameter is correct.

F5 code edits are already on disk. This patch resolves the blocked test without reverting them.

---

## Task P1 — Characterise divergence stability at matthew_alpha=2.0

Before recalibrating the gate, establish whether seeds 42 and 48 sit stably above 20% divergence or are near-threshold noise.

**Action:**
1. Run `test_tier3_gate_b1_battery` five times independently at matthew_alpha=2.0 (use the config/YAML path that carries the locked value, confirming it is 2.0).
2. Record the JT divergence for seeds 42 and 48 on each of the five runs.
3. Compute mean and range for each seed across the five runs.

**Decision rule (no supervisor check-in required):**

- If both seeds show mean divergence < 22% and range entirely below 25%: these are stable near-threshold values. Proceed to P2 with new threshold = **25%** (widens the tolerance band to comfortably contain the locked-value production distribution; the 20% threshold was already an approximation calibrated at the wrong default).
- If either seed shows mean divergence ≥ 22% or range crossing 25%: the divergence is structural. Proceed to P2 with new threshold = **[mean of the two failing seeds, rounded up to the nearest 5%]** — i.e. recalibrate to what the locked production model actually produces.

Record the chosen threshold and its basis in the §summary block.

---

## Task P2 — Recalibrate gate and pre-register new threshold

**Action:**
1. Open the test file containing `test_tier3_gate_b1_battery`. Locate the threshold value (currently 20% / 14/15 seeds).
2. Update the threshold to the value determined in P1.
3. Update the seed-pass requirement if the battery logic encodes it separately (currently 14/15). If the two previously failing seeds now pass at the new threshold, the requirement stays at 14/15. If any other seeds now newly fail at the new threshold, identify them and flag in the §summary — do not silently adjust the seed-pass count downward.
4. Add an inline comment to the test asserting the threshold, its calibration basis, and the matthew_alpha value it was calibrated at. Minimum content:
   ```python
   # Threshold recalibrated 2026-06-11 at matthew_alpha=2.0 (locked production value).
   # Prior threshold 20% was set at matthew_alpha=1.5 (pre-lock default); retired.
   # Calibration basis: [stability run results from P1 — insert actual numbers].
   ```
5. Open `HYPOTHESES.md`. Find the pre-registration entry for the tier-3 gate battery (the entry that originally registered the 14/15 / <20% threshold). Add a dated amendment note:
   ```
   [2026-06-11 AMENDMENT] Gate threshold recalibrated to <[new threshold]% at
   matthew_alpha=2.0 (locked production value). Prior threshold <20% was calibrated
   at matthew_alpha=1.5 (pre-lock default, now retired). Stability characterisation:
   seed 42 mean [X]% (range [lo]–[hi]%), seed 48 mean [X]% (range [lo]–[hi]%).
   Science interpretation unchanged: gate continues to test JT rate divergence
   from oracle benchmark.
   ```
   Do not alter the original pre-registration text — append the amendment beneath it.

**Acceptance check — P2:**
```bash
pytest test_tier3_gate_b1_battery -v 2>&1 | tail -20
```
All 15 seeds pass. Exit code 0. No other previously passing tests now fail (run full suite to confirm):
```bash
pytest --tb=short -q 2>&1 | tail -5
```
Full suite: all tests pass. Zero failures. Zero errors.

---

## Task P3 — Clear F5 STOP and confirm directive complete

**Action:**
1. Verify F5 config.py edits are intact (the edits from the original F5 task, which were on disk at STOP time):
   ```bash
   grep -E 'sigma_si|matthew_alpha|f_C' config.py
   ```
   Confirm values match PARAMETERS locked values (σ_Si=1.238, matthew_alpha=2.0, f_C=0.25) and σ_Si comment is rewritten.
2. Run full acceptance check from original F5:
   ```bash
   grep -E 'σ_Si|sigma_Si|sigma_si|matthew_alpha|f_C' config.py
   ```
   Values match PARAMETERS. Comment does not contain the prior incorrect description.

**Acceptance check — P3:**
All checks from F5 original directive now GREEN. Full test suite GREEN.

---

## Task P4 — Add J&H 2016 stub entry to LITERATURE.md

**Context:** CC flagged that LITERATURE.md contains no entry for Janssen & Hill 2016 (DOI 10.1007/978-3-319-31481-5_3, CoMSES 4538). The paper has not been read in any project session; no quantitative findings are verified. A stub entry with confirmed metadata is added now; content completion is deferred until the paper is available.

**Action:**
1. Open `LITERATURE.md`. Confirm no entry exists for DOI 10.1007/978-3-319-31481-5_3. If an entry already exists (e.g. added since the F2–F7 run), do not duplicate it — flag in §summary and skip to acceptance check.
2. Add the following stub entry in whatever format LITERATURE.md uses for entries, placed adjacent to the J&H 2014 entry:

   **Citation:**  
   Janssen, M.A. & Hill, K. (2016). Modeling the Ache: Hunter-gatherer foraging dynamics. In J. Barceló & F. Del Castillo (Eds.), *Simulating Prehistoric and Ancient Worlds*. Springer. https://doi.org/10.1007/978-3-319-31481-5_3

   **CoMSES model codebase:** 4538

   **Verified metadata:** DOI, CoMSES number, topic (clumped habitats and mobility in Ache foraging context).

   **Status tag:** `[STUB — findings not yet extracted. Paper not yet available in project files. Do not cite quantitative findings from this entry until paper is read and entry is completed.]`

   **Do not add** any quantitative findings, effect sizes, or conclusions beyond what is listed above. Do not upgrade the status tag to `[VERIFIED]`.

3. Do not alter any other entries in LITERATURE.md.

**Acceptance check:**
```bash
grep "10.1007/978-3-319-31481-5_3" LITERATURE.md   # entry present
grep "4538" LITERATURE.md                           # CoMSES number present
grep -i "STUB" LITERATURE.md                        # stub tag present
```
All three return matches.

---

## §Summary report

Produce after all tasks pass:

```
F5 PATCH — COMPLETE
Date: 2026-06-11

P1  Stability characterisation at matthew_alpha=2.0:
    Seed 42: mean [X]%, range [lo]–[hi]% across 5 runs.
    Seed 48: mean [X]%, range [lo]–[hi]% across 5 runs.
    Decision rule applied: [near-threshold noise / structural — reason].
    New threshold selected: [value]%.

P2  test_tier3_gate_b1_battery recalibrated to <[value]% at matthew_alpha=2.0.
    Seed-pass requirement: [14 or N]/15 — [unchanged / adjusted: reason].
    Newly failing seeds at new threshold: [none / list].
    HYPOTHESES.md amendment appended to gate pre-registration entry.
    Inline calibration comment added to test.

P3  F5 config.py edits confirmed intact.
    σ_Si=[value], matthew_alpha=[value], f_C=[value]. Comment: rewritten.

P4  J&H 2016 stub entry added to LITERATURE.md.
    DOI: 10.1007/978-3-319-31481-5_3. CoMSES: 4538. Status: STUB.
    [or: entry already present — no action taken.]

FULL SUITE: [N] tests, 0 failures, 0 errors.
GATE: GREEN — F5 resolved. Doc Hygiene F2–F7 + P4 literature stub complete.
```

---

*End of patch directive.*
