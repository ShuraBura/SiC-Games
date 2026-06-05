# SiC Games — OWE-1.1 Follow-Up Directive (Home-Range Estimator Fix + N_carry Scale Calibration)

**Version:** 1.0
**Type:** Micro-directive. Two cheap follow-ups on the existing OWE-1 machinery, plus
  one disclosure request. Reuses the calibration run setup; minimal new compute.
**Depends on:** OWE-1 report (`outputs/owe1_calibration/report_owe1.html`) and
  `owe1_calibration.py`.
**Out of scope:** No new mechanics. No re-running the full matrix. Tasks B may change
  ONE locked-adjacent parameter (`N_carry`) — this is an authorised scale-calibration,
  flagged as such, NOT a silent retune (see §B.4).

---

## Task A — Home-range estimator: lifetime track vs contemporaneous range

**Why:** The OWE-1 report computed median home-range as cells occupied **over the agent's
entire lifetime** (~56 cells), then compared it to the ~100 km² forager **home-range**
benchmark — and found a 56× overshoot. But a lifetime-accumulated track is NOT the same
quantity as a contemporaneous home-range. At monthly resolution an agent lives ~25–30 yr
(~300–360 steps) and accumulates occupied cells across decades, including relocation/drift.
Forager ~100 km² home-range is the territory used *contemporaneously* (within a
season-to-year), not a lifetime migration track. The 56× may be largely a denominator
mismatch, not a real mobility finding. This task tests that.

### A.1 First, disclose the current estimator (no compute)

Report verbatim from `owe1_calibration.py`:
1. The exact home-range estimator definition (convex hull? distinct-cell count? over what
   time window — lifetime, fixed window, rolling window?).
2. Confirm whether the ~56-cell figure is lifetime-accumulated or windowed.
3. Paste the estimator function so the measured quantity is unambiguous.

Also: **surface `owe1_calibration.py` itself** — the supervisor cannot see it
(it is drive-side only). Report its location and the home-range + cell-size sections.

### A.2 Recompute as a contemporaneous (rolling-window) range

Re-measure home-range on the SAME reference config (C, static, medium-⟨ρ⟩, seed=42,
already-run trajectory if cached; else re-run — it is ~0.1 h). Define:

- **Annual window:** distinct cells occupied within each rolling 12-step window.
- **Seasonal window:** distinct cells occupied within each rolling 3-step window
  (report both; the right comparison depends on whether the ~100 km² benchmark is
  annual-territory or seasonal-range — report both, let supervisor pick).

For each window definition, report population **median** and **IQR** of the per-agent
windowed range (take each agent's median-over-its-windows, then population median).

### A.3 Re-derive cell-size under the corrected estimator

For each window definition, solve ℓ (km/cell) so median windowed range × ℓ² = ~100 km².
Report ℓ and the **consistency factor** (committed ~10 km / solved ℓ) for each.

**Report, do not force.** State plainly whether the cell-size inconsistency
- shrinks toward consistency (→ the OWE-1 56× was an estimator-definition artifact, and the
  finding is downgraded), or
- persists (→ genuine model-vs-ethnography mobility tension, finding stands).

Update OWE-1 report §3 with the corrected result and label the original lifetime-based
56× explicitly as superseded-or-confirmed.

---

## Task B — N_carry scale calibration to target population

**Why / authorisation:** Supervisor decision (2026-05-31). `N_carry` was set in Stage 4.5
Task 0 as a **numerical-stability scale parameter** (top of the hand-set viability band
[150,400] on the 50×50 world), NOT a realistic ecological estimate. It is therefore
legitimate to set it to a target population. The 100×100 world needs a larger population
to realise the intended 20–60 ethnographic bands; the current N_carry=400 (model constant)
produced settled N≈754 on 100×100, too thin (and dangerous for trough-phase finite-size
contamination, OWE-12). Target: **settled N ≈ 2000–3000.**

### B.1 Determine the N_carry → settled-N mapping on 100×100 (measure, do not guess)

The mapping is NOT 1:1 and is world-size dependent (on 50×50, ceiling≈settled; on 100×100
with harness-1600, settled was 0.47× ceiling, because lower density delays the discount and
starvation/age-mortality cap first). So **sweep N_carry and measure settled-N**:

Reference: C, static, medium-⟨ρ⟩, seed=42, 2000 steps, settled-N measured at t≥1500.

| Run | N_carry (model constant) | init N | Report |
|---|---|---|---|
| B1 | 1600 | 2000 | settled N, settled/ceiling ratio |
| B2 | 3000 | 3000 | settled N, ratio |
| B3 | 4500 | 3500 | settled N, ratio |
| B4 | 6000 | 4000 | settled N, ratio |

(Adjust upper rungs if B2 already overshoots target.) Fit settled-N vs N_carry; report the
N_carry that yields **settled N ≈ 2500** (midpoint of target). Init N should start at or
slightly below the expected settled band so there is boom headroom (the carrying-cost
mechanic absorbs mild overshoot gracefully per OWE-1, but avoid gross overshoot).

### B.2 Recalibration check (MANDATORY — the standing-constraint cost)

Raising N_carry is rate-adjacent: `p_max_C`, `alpha_carry`, and the starvation balance were
co-tuned at N_carry=400 so N settled cleanly with `est_starv ≤ 0.78/step`. At the new
N_carry, re-confirm at the chosen value:
- Population **settles cleanly** (reaches a quasi-steady band, does not run away or oscillate
  divergently) at t≥1500.
- `est_starv ≤ 0.78/step` still holds (or report the new value — if starvation rises sharply,
  the birth rate cannot fill the larger ceiling and `p_max_C`/`alpha_carry` need a note for
  supervisor, NOT an auto-retune).
- Report whether the settling is as clean as the N_carry=400 baseline or degraded.

### B.3 H1(ii) inversion re-confirmation flag (do NOT run, flag only)

The headline H1(ii) inversion finding was established at N_carry=400. A move to ~2500 is a
large scale change. **Flag for supervisor:** the inversion must be re-confirmed at the new
N_carry (≥3 seeds, C vs Si, before trusting H1(ii) at the new scale) — this is a separate
authorised run, not part of this micro-directive. Register as **OWE-14: re-confirm H1(ii)
inversion at calibrated N_carry** in ROADMAP Owed.

### B.4 Scientific-honesty note (write into MODEL_SPEC §9.3)

Record explicitly: **N_carry is a calibration choice (scale-setting), not an emergent
prediction.** The absolute population is set by the supervisor to realise the intended band
structure; what remains emergent and is the actual finding is the **C-vs-Si difference** at
the shared, pre-committed N_carry. N_carry must be set ONCE, shared across both arms, and
locked BEFORE examining the H1(ii) comparison at the new scale (philosophy-of-science:
locking before looking, as the original findings were locked).

---

## Task C — Standard run-length confirmation (no compute)

Supervisor decision (2026-05-31): **standard run-length = 12,000 steps** (1000 yr, ~4
secular cycles), transient exclusion **~500 steps** declared up front (~3.8 productive
cycles, clears the ≥3-cycle bar for cycle-length/amplitude estimation). 24,000 held in
reserve only if cycle-length estimation proves noisy. Record this in ROADMAP as the locked
standard run-length for the H-EMERGE-1 / sweep campaign.

---

## Report

Append to `outputs/owe1_calibration/report_owe1_followup.html` (or extend the existing
report with a clearly-marked OWE-1.1 section):

- **§A** estimator disclosure (verbatim function + file location); annual & seasonal
  windowed median home-range; re-derived ℓ + consistency factor each; verdict
  (artifact-downgraded vs finding-stands).
- **§B** N_carry → settled-N sweep table + fit; recommended N_carry for settled≈2500;
  recalibration-check result (clean settle? est_starv?); the chosen locked N_carry.
- **§C** confirmation of locked run-length + transient in ROADMAP.
- **Doc updates:** MODEL_SPEC §9.3 N_carry-as-calibration note; OWE-14 registered in
  ROADMAP Owed; run-length locked in ROADMAP. Idempotent + conflict-surfacing merge as
  before (stop and report on any contradiction; no auto-resolution).

---

## Success criteria

| Criterion | Target |
|---|---|
| Estimator disclosed verbatim + file surfaced | supervisor can see what was measured |
| Home-range recomputed (annual + seasonal windows) | medians + IQRs reported |
| Cell-size consistency re-derived | factor stated each window; artifact vs finding verdict |
| N_carry→settled-N mapping measured | sweep table + fit; not guessed |
| N_carry for settled≈2500 identified | single recommended value |
| Recalibration check run | clean-settle + est_starv reported at chosen N_carry |
| H1(ii) re-confirmation flagged (OWE-14) | registered, NOT run |
| N_carry-as-calibration honesty note | in MODEL_SPEC §9.3 |
| Run-length locked | 12k steps / 500 transient in ROADMAP |

---

*End of OWE-1.1 Follow-Up Directive — 2026-05-31.*
