# SiC Games — LITERATURE.md Update: J&H 2016 Stub → Verified

**Issued by:** Supervisor (via Claude chat)  
**Assigned to:** Claude Code  
**Date:** 2026-06-11  
**Scope:** Single LITERATURE.md entry update. No code changes. No simulation runs.

---

## Context

The J&H 2016 chapter (DOI 10.1007/978-3-319-31481-5_3) has been added to project files (`janssen2016.pdf`) and read in full this session. Findings below were extracted directly from the source.

**This directive is self-sufficient regardless of execution order relative to the F5 patch (task P4).** P4 adds a `[STUB]` entry for this DOI. This directive may run before or after P4:

- **If the F5 patch (P4) has already run:** a `[STUB]` entry for DOI 10.1007/978-3-319-31481-5_3 exists in LITERATURE.md. Replace it with the verified entry below.
- **If the F5 patch has not yet run, or P4 is skipped:** no entry for this DOI exists yet. Add the verified entry below directly (do not create then replace a stub — go straight to `[VERIFIED]`). If the F5 patch later runs, CC should treat P4 as already satisfied: check for an existing entry with this DOI before adding a stub, and skip stub creation if a `[VERIFIED]` entry is already present.

---

## Task — Add or upgrade J&H 2016 entry to verified

**Action:**

1. Open `LITERATURE.md`. Search for any entry with DOI 10.1007/978-3-319-31481-5_3.
   - If a `[STUB]` entry exists: this is the one to replace (continue to step 2).
   - If a `[VERIFIED]` entry already exists with this DOI: stop here, do not duplicate — flag in summary as "already complete, no action taken."
   - If no entry exists: this is the one to add fresh (continue to step 2, treating it as an addition rather than a replacement).
2. Add or replace with the following verified entry, adapted to whatever entry format LITERATURE.md uses (the content below is the required substance; formatting/headers should match surrounding entries):

   **Citation:**  
   Janssen, M.A. & Hill, K. (2016). An Agent-Based Model of Resource Distribution on Hunter-Gatherer Foraging Strategies: Clumped Habitats Favor Lower Mobility, but Result in Higher Foraging Returns. Chapter 3 in J.A. Barceló & F. Del Castillo (Eds.), *Simulating Prehistoric and Ancient Worlds* (Computational Social Sciences). Springer International Publishing, pp. 159–174. https://doi.org/10.1007/978-3-319-31481-5_3

   **CoMSES model codebase:** 4538

   **Status tag:** `[VERIFIED]`

   **Design/scope:** Extends Janssen & Hill (2014) by perturbing the Mbaracayu landscape along two axes: habitat clumpiness (three levels — 30%, 60% [original/natural], 90% same-vegetation neighbour fraction) and between-habitat prey-density variation (Original vs High, up to ~10x difference between richest [riparian] and poorest [meadow] habitat, total biomass held constant). Six landscape types result: O30, O60, O90, H30, H60, H90. 64,800 simulations total (100 runs × 108 camp-mobility configurations × 6 landscapes). All runs assume cooperative hunting with coordinated search (unlike 2014, which also modelled solitary foraging). Camp mobility strategies vary along two binary axes: targeted vs random relocation, and adaptive (threshold-based staying) vs non-adaptive (fixed-interval) movement.

   **Findings:**
   - **Optimal group size is robust at 7 hunters across all six landscapes** — unaffected by clumpiness or prey-variation manipulations, and consistent with the 7–8 hunter optimum established in J&H 2014.
   - **Mobility is largely stable under natural conditions**: moving camp every day remains optimal for the original (O-series) landscapes and for low/medium clumpiness, matching Ache ethnographic observation. Only under the most extreme condition (H90 — high prey-density variation + high clumpiness) does optimal mean camp-staying time rise meaningfully, to **2.1 days** (vs ~1 day baseline).
   - **Headline result is about targeting, not group size or raw mobility frequency.** In clumped, heterogeneous landscapes (H60/H90), camps that *target* high-return habitat types when relocating (vs random relocation direction) achieve **~30% higher return rates**. Combining targeted movement with adaptive staying thresholds yields up to **35% higher mean daily return** in the most patchy/variable environment (H90) relative to the natural dispersed environment (O60) — despite identical total prey biomass on the landscape.
   - **Quantitative anchor (Table 3.3):** O60 non-targeted/non-adaptive (≈ natural Ache pattern) = 2.835 kg/hunter/day, fraction no-meat days = 0.041. H90 targeted/adaptive = 3.836 kg/hunter/day, fraction no-meat days = 0.026. H90 targeted/non-adaptive = 3.789 kg/hunter/day, 0.032.
   - **Targeted movement can be worse than random** when habitats differ little and resources are highly dispersed (O30 condition) — targeting only pays off when habitat productivity differs substantially AND habitats are spatially clumped.
   - **No cost-of-movement term** in the model (hunters hunt en route to new camps regardless of distance/strategy), so mobility-strategy comparisons reflect foraging-return tradeoffs only, not travel cost.

   **Relevance to SiC Games:** Provides a literature-grounded mechanism by which terrain/biome clumpiness (relevant to the active terrain-generator work and habitability-conditional coexistence metric) translates into foraging-return differentials — specifically, the *payoff from spatial targeting* scales with both clumpiness and between-habitat productivity variance. This is a candidate mechanism for why C agents (with information-sharing / Cred-economy coordination) might outperform Si agents disproportionately in clumped/patchy terrain, independent of the existing seasonal-shock resilience finding (H1(ii)). Not yet incorporated into any hypothesis or build stage — flagged for awareness only.

3. Confirm the J&H 2014 entry (823–835, [VERIFIED] per the prior F2–F7 run) is unaffected by this edit.

**Acceptance check:**
```bash
grep "10.1007/978-3-319-31481-5_3" LITERATURE.md   # entry present, exactly once
grep "159–174\|159-174" LITERATURE.md               # page range present
grep -i "VERIFIED" LITERATURE.md | grep -i "4538\|2016"  # status is [VERIFIED]
```
First three return matches, with the DOI appearing exactly once (no duplicate stub + verified entries). If a `[STUB]` tag for this DOI still exists anywhere, the task is incomplete.

---

## Summary report

```
LITERATURE.md J&H 2016 UPDATE — COMPLETE
Date: 2026-06-11

Stub entry (DOI 10.1007/978-3-319-31481-5_3, CoMSES 4538) replaced with [VERIFIED] entry.
Findings logged: group-size robustness (7 hunters), mobility stability, targeted-movement
return gains (30%/35%), Table 3.3 quantitative anchors, no-movement-cost caveat.
J&H 2014 entry confirmed unaffected.

GATE: GREEN.
```

---

*End of directive.*
