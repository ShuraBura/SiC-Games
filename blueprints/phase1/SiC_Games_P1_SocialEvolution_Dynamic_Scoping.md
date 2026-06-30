# SiC Games P1 — Dynamic Social Evolution (SCOPING + RED-TEAM)

**Goal.** Turn the *static-but-rich* Carbon social architecture (families → bands → per-band society → assabiyah)
into a **dynamically rising-and-falling** one, driven by a **varying world**. The architecture is complete and
validated; what's missing is (i) the world actually *varying* in the social runs (climate seams exist but aren't
wired in), and (ii) the social *responses* to good/bad times / leaders / belief.

**Governing principle (supervisor 2026-06-29): FULL CUSTOMIZABILITY.** Every mechanism below is an **independent
opt-in flag** (default OFF, bit-exact when off), so any piece that doesn't pan out — or needs more lit /
benchmarking — can be switched off without touching the rest. The social-evolution layer is a *bundle of
ablatable flags*, not a monolith.

**Sequencing (dependency-driven):** Stage 0 (climate integration) FIRST — the dynamic social pieces are *inert on
a static world* (the Ibn Khaldun cycle is "cohesion responds to good vs bad times"; there are no varying times
yet). Then 1→4. Each stage: scope → lit → **RED-TEAM** → implement → gate → commit.

---

## Stage 0 — Climate INTEGRATION (the enabling wire)  `[prerequisite]`
**Scope.** Run the social/full-stack model on a **`ClimateField`-modulated CC-1 capacity** (the `ClimateField`
already wraps a base field and multiplies by season·interannual·regime + the catastrophe layers) instead of the
*static* `SubWindowCapacity`. Then seasonality / regime shifts / ENSO / caribou-crash / llanos-flood actually
drive surplus + adversity, and the already-built couplings (F.3c-3 `season_aggregation`, the storage overwinter
gate, the morph) come alive. No new mechanic — a **wiring + re-validation**.
**Lit.** The orbital-lottery anchors (Berger 1978, Timmermann 2018, Wanner 2008, St. John 2022, Hamilton 2004 —
all FILED); the layers are already gate-validated in isolation (test_climate).
**RED-TEAM.**
1. **Mean-capacity drift.** `ClimateField` multiplies by season∈[1−a,1] etc. — does the *time-mean* capacity drop
   vs the static field → a spuriously lower eq_pop? → check/renormalise so the mean K is preserved (compare
   eq_pop static vs climate-mean).
2. **Catastrophe → extinction / fission-fusion thrash.** A regime shift or caribou-crash could crash a band →
   cascade. → confirm eq_pop survives the regime cycle (it did in the isolated gate, but not with the full social
   stack on); watch band-count stability through a catastrophe.
3. **Timescale mismatch.** Season period ~12 steps vs slow social adjustment (fission/fusion, assabiyah). The
   season coupling may stay weak (as seen). That's acceptable — regime shifts (multi-generation plateaus) are the
   social-relevant variation, not the annual cycle.
4. **Determinism / seeding.** `ClimateField` carries its own RNG (the telegraph) — confirm reproducibility.
**Gate.** Full stack coheres on the varying world (eq_pop ~stable, bands ~25 non-kin, status→RS ~0.13 preserved),
AND a regime/ENSO downturn now visibly depresses surplus/assabiyah and a recovery restores them.

---

## Stage 1 — Leader coherence  `[enable_leader_coherence]`
**Scope.** A band's cohesion gets a bonus from its **top-status member** (highest cred·prowess): the
`tolerable_size` (and/or assabiyah) is lifted by the leader's status, and the bonus **collapses when the leader
dies** → a fission spike. The cleanest, most benchmarkable extra coherence source.
**Lit.** Hooper, Kaplan & Boone 2010 (leadership in collective action); von Rueden et al. (leaders/influence);
Glowacki & von Rueden 2015; **Boehm 1999** (reverse-dominance — egalitarian bands LEVEL leaders, so the effect is
*weak* in egalitarian society, stronger in complex/stratified).
**RED-TEAM.**
1. **Distinct from assabiyah?** Assabiyah = solidarity-from-success; leader-coherence = charismatic/organisational.
   Must be ADDITIVE + separately ablatable, not a relabel. → separate term in `tolerable_size`.
2. **Boehm constraint.** In egalitarian forager bands leaders are weak → leader-coherence must SCALE with the
   band's society type (≈0 egalitarian, rising complex→stratified) or it's ahistorical. Tie to `_band_society`.
3. **Magnitude unanchored.** The size of the leader→cohesion effect is not measured → BRACKET it; report
   sensitivity, don't fit.
4. **Over-stable mega-bands.** A strong leader could prevent all fission → unrealistic size. → keep `band_split_size`
   the hard cap.
**Benchmark.** **Leader death → fission spike** (testable signature); leader-coherence raises mean band size only
in complex/stratified bands, not egalitarian ones.

---

## Stage 2 — Genealogy / lineage logger  `[enable_genealogy_log]`
**Scope.** Opt-in **append-only logging** of each birth/death with `(id, _mother, _father, _lineage, band_id,
step, cred)` to disk, for OFFLINE analysis. **No runtime dynamics change** — a pure observer.
**Lit.** N/A (analysis infrastructure).
**RED-TEAM.**
1. **Memory.** Do NOT build a live in-memory tree (unbounded). Append to a file; analyse offline. O(births+deaths).
2. **Observer-only.** Must not alter the RNG stream or dynamics → write after the step, read nothing back.
3. **id reuse.** Use a stable per-agent uid (monotonic counter), not `id()`.
**Benefit / benchmark.** Enables lineage-extinction curves, time-to-MRCA, dynasty depth vs assabiyah, who-fathered
dynasties — the analytic substrate for Stage 3. (Names = cosmetic; deferred to a viewer, not built here.)

---

## Stage 3 — Ibn Khaldun dynastic cycle  `[enable_dynastic_cycle]`
**Scope.** Assabiyah doesn't only RISE with surplus — it **DECAYS with sustained luxury / size / sedentism**: a
band that grows large + rich + stratified erodes its solidarity → weakens → fissions/collapses → a leaner
high-assabiyah group rises. Adds a luxury-decay term to the assabiyah update so cohesion **oscillates** (rise →
prosperity → decay → collapse → renewal).
**Lit.** **Ibn Khaldun** (*Muqaddimah*); **Turchin** (cliodynamics; *Secular Cycles*, Turchin & Nefedov 2009 —
the formal asabiya model). **NB the lit is AGRARIAN-STATE scale**, not foragers.
**RED-TEAM.**
1. **Applicability.** Foragers don't have dynasties/states — the cycle is an AGRARIAN-state phenomenon. → gate to
   **morphed (complex/stratified) bands only**; egalitarian forager bands don't run the cycle. Frame as the
   model's *post-sedentism* behaviour, NOT a forager claim.
2. **Benchmark is qualitative.** No quantitative fit available — the deliverable is a PATTERN (does assabiyah
   oscillate? do big-rich-stratified bands collapse and reform?). Report the pattern + period; do not claim a
   calibrated cycle length.
3. **Degenerate regimes.** Luxury-decay could give *perpetual collapse* (no society persists) or be *inert*. →
   sweep the decay/recovery rates for the window where cycles actually emerge; if none, SHELVE (like F.2 risk-mort).
4. **Most speculative → fully optional**, default OFF, clearly framed as mechanism-exploration.
**Gate.** On complex/stratified bands, assabiyah + band size show a rise-and-fall cycle (not monotonic, not flat),
without destabilising the overall population.

---

## Stage 4 — Condition-dependent polygyny  `[enable_dynamic_polygyny]`
**Scope.** `polygyny_rate(band) = f(surplus, society, biome)` instead of a constant — rich/stratified/storage-
surplus bands → more polygyny → status→RS drifts up toward the polygynous 0.19+; egalitarian foragers stay near
0.13. Different bands sit at different status→RS — an emergent marriage-system gradient.
**Lit.** **Borgerhoff Mulder** (wealth→polygyny; the *polygyny threshold* model); von Rueden & Jaeggi 2016
(polygyny by subsistence — pastoralists ≫ foragers); Marlowe (forager polygyny ~modest). **Well-anchored.**
**RED-TEAM.**
1. **Sex-ratio / bachelor surplus.** Polygyny → unmated low-status males. Realistic, but watch for instability
   (a bachelor underclass crashing pairing). Cap `max_wives`; monitor unmated-male fraction.
2. **Double-driving.** Polygyny gated on surplus/society which already drive κ + family-knobs — confirm it adds a
   distinct gradient, not a tautology.
3. **Benchmark — GOOD.** Does polygyny rise with band wealth/surplus matching the cross-cultural gradient, and does
   status→RS rise toward ~0.19 in the wealthiest (pastoralist-like) bands? TESTABLE against von Rueden's
   marriage-system breakdown.

---

## Later / parking lot (lit-and-benchmark-gated; NOT scheduled)
- **Coherence-types VECTOR** (adversity / prosperity / leader / belief, with per-agent affinities) — the richest
  idea, the weakest anchoring (no data on per-agent affinity weights). Generalise Stage 1's single leader-source
  only if it pays off. Frame strictly as mechanism-exploration.
- **Religion** (`_group.religion` seam) → assabiyah amplifier, biome-linked (Norenzayan "big gods" → larger
  cohesive polities). Natural second coherence source after leader.
- **Wife-quality channel** (status→partner fertility/survival) — the missing von Rueden MONOGAMOUS r≈0.15 route;
  would let strict monogamy reach ~0.15 without polygyny.
- **CL-1** (real spatial/seasonal solar-forced T/humidity field) + **climate→pathogen** wiring — the big separate
  terrain/climate stage (deferred; touches the terrain generator).

## Customizability summary (the flags)
`(Stage 0 = config choice of harvest field, not a flag.)` `enable_leader_coherence` · `enable_genealogy_log` ·
`enable_dynastic_cycle` · `enable_dynamic_polygyny` — each independent, default OFF, ablatable. Plus the parking-lot
flags when/if built. Every stage gated on its own benchmark; any that fails its gate is SHELVED (default-OFF +
caveat) like F.2 risk-mortality, not deleted.
