# SiC Games P1 — Ascribed-Status Mate-Choice (SCOPING + RED-TEAM)

**Goal.** Let **cred (ascribed lineage status)** earn a mating advantage — but **society-gated** (Boehm): ≈0 in
egalitarian bands, rising through complex → stratified, so *ascribed status buys marriage as a society stratifies*.
Currently mate-choice is **prowess-only** (`_do_pairing`), so the ascribed facet has no reproduction channel — which
is why the composite `cred·prowess → RS` collapses to ~0 (R-35). This adds the missing channel, gated to the regime
where the anthropology says it belongs, and reconnects von Rueden's **0.13 (egalitarian/achieved) → 0.19
(stratified/both)** gradient.

**Governing principle: FULL CUSTOMIZABILITY.** An independent opt-in flag, default OFF (= today's prowess-only,
bit-exact). Science-calibration change → supervisor sign-off before merge.

---

## Motivation (R-32 / R-34 / R-35 findings)

- **The composite status→RS is ~0 at 16 seeds** (95% CI [−0.035, +0.037]); the documented 0.13 (R-26, 6-seed) is
  not robust — it sat at the optimistic tail of a wide distribution.
- **Decomposition:** prowess (achieved) → RS **+0.10** [+0.06, +0.14] (significant, ≈ von Rueden); cred (ascribed)
  → RS **≈0** (measured −0.07, but the diagnostic showed this is a WEAK, seed-noisy, non-causal confound — cred has
  no mating channel, so it's noise around zero, not a real negative).
- **Root cause (by design):** `_do_pairing` weights `prowess ** mate_choice_strength` only; `base_status =
  (cred+ε)·(prowess+ε)` is used for the resource contest + R-18 survival, but NOT mating. A deliberate facet split
  (achieved→mating, ascribed→resources/survival) that is **regime-blind** — defensible for immediate-return
  egalitarian foragers, wrong for the **complex/stratified** bands the model morphs into (run: 84% complex-forager).

## Design

Mate-choice weight interpolates from `prowess` (egalitarian) to `base_status = cred·prowess` (stratified) via a
society gate:

```
w_x = ( prowess_x · cred_x^( a · sw(band) ) ) ^ mate_choice_strength
      sw(band) = MATE_ASCRIBED_WEIGHT[society]     # egalitarian 0 · complex ~0.5 · stratified 1.0  (bracketed)
      a        = ascribed_mate_strength            # global scale, UNANCHORED (sweep)
```
- **sw=0 (egalitarian / flag off):** `cred^0 = 1` → `prowess ** m` — **bit-exact to today**.
- **sw=1, a=1 (stratified):** `(prowess·cred) ** m = base_status ** m` — full Cobb-Douglas status drives mating.
- Applies in `_do_pairing` for both initial bonds AND polygynous wife-taking (same weight vector). Per-band via
  `_band_knob`/society, mirroring `mate_choice_strength` and the leader-coherence gate (architectural consistency).

Config: `enable_ascribed_mate_choice: bool = False`, `ascribed_mate_strength: float = 0.0` (a; sweep), plus a new
`MATE_ASCRIBED_WEIGHT` society dict in `demography.py` (parallels `LEADER_SOCIETY_WEIGHT`).

## Literature

- **von Rueden & Jaeggi 2016** (FILED) — the target: status→RS **0.19 cross-system** (inflated by stratified/
  polygynous societies where *ascribed* status marries), **monogamous ≈0.15**, **achieved-only** end ≈ what
  prowess gives now. Their composite status includes ascribed components.
- **Boehm 1999** — egalitarian bands LEVEL would-be ascribed status → the gate must be ≈0 there (a lineage name
  buys nothing among immediate-return foragers). Same gate logic as leader coherence.
- **Smith 2004** (FILED) / **Marlowe 2004** (FILED) — the *achieved* channel (good hunters → more/earlier wives):
  the egalitarian baseline already in the model (prowess), which this preserves.
- **Ascribed-marriage in complex/stratified foragers:** Colson 1979 (FILED — Makah NW-Coast ranked society);
  Kelly 1995 (FILED — delayed-return → rank); Ames & Maschner 1999 (NW-Coast ranked lineages / chiefly marriage —
  *to obtain*); Chagnon 1988 (Yanomamö — kin/lineage alliance drives marriage + RS — *to obtain*).

## RED-TEAM

1. **Recalibration (the big one).** The documented status→RS 0.13/0.19 (R-19/R-21/R-26) were measured
   **prowess-only**. Turning cred into mating CHANGES them — deliberately. → re-run the E.3 lottery + full-stack
   calibration with the flag on; report the NEW gradient; do not silently overwrite the old numbers (append a new
   result, mark the old as prowess-only).
2. **84%-complex over-shoot.** Complex-forager fires nearly everywhere in the current equilibrium, so even a
   moderate complex-weight makes cred bite population-wide. → calibrate `MATE_ASCRIBED_WEIGHT[complex]` modestly
   (or start stratified-only) so the effect scales with *genuine* stratification, not blanket complexity. Sweep.
3. **Cred variance sufficiency.** The cred homeostat bounds cred (~1–2, Gini ~0.17). If within-band cred spread is
   small, the channel is weak even at full gate. → check cred has enough live spread to produce a signal; report.
4. **Dynastic runaway.** cred → mating → heritable cred → concentration is a POSITIVE FEEDBACK (high-cred lineages
   monopolize marriage → cred concentrates → Gini climbs). The mean-1 homeostat + reversion should bound it, but
   verify no runaway (Gini explosion / N_e collapse). *NB this feedback IS the seed of dynastic concentration —
   a feature to harness later (Stage 3), but here it must stay bounded.*
5. **Polygyny interaction.** cred-in-mate-choice × modest polygyny → high-cred males take more wives → compounding.
   → calibrate jointly; watch #wives-Gini and N_e.
6. **Ablatable, default OFF.** flag off ⇒ `prowess ** m` exactly (bit-exact test).

## Validation / calibration targets

- **Flag OFF:** bit-exact to current (prowess→RS +0.10, cred→RS ~0, composite ~0). Locked by test.
- **Flag ON, society-gated:** cred→RS turns **positive** in complex/stratified bands; the composite status→RS
  **rises with stratification** — the target gradient (egalitarian ~0.10 achieved-only → stratified ~0.15–0.19
  both-facet, von Rueden). Report at HIGH SEED COUNT (R-34: status→RS needs ~16 seeds; ±0.1 at small samples).
- **Homeostat bounded** (no cred runaway — Gini stable, N_e healthy); eq_pop preserved.
- **Society gradient:** a monotone status→RS vs society-type curve is the headline deliverable.

## Sequencing

scope (this) → lit (obtain Ames/Chagnon; von Rueden/Boehm/Colson/Kelly filed) → RED-TEAM → implement (flag +
`MATE_ASCRIBED_WEIGHT` + `_do_pairing` weight) → **high-seed recalibration** (16 seeds, society-gradient) →
gate → commit. Ties into: the **status→RS reframe** (R-35 — restate as prowess→RS for the egalitarian/achieved
baseline, this adds the ascribed/stratified arm) and the **dynastic cycle** (Stage 3 — ascribed-marriage is a
dynastic-concentration mechanism). Non-blocking for CC-1; can run in parallel or after.
