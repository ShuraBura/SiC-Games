# SiC Games — Session Handoff (2026-06-26)

**HEAD:** `0f39c2d` · **536 tests green** · pushed to `main`. Working tree clean (only stale run-output
artifacts uncommitted — ignore them).

This session built the **environmental + social substrate** for the Carbon civilization: climate → storage →
society morph → **emergent bands**, and settled a foundational modelling question (individualism vs lumping).
Everything is **flaggable, OFF by default**, so all prior validations are bit-exact untouched.

---

## ▶ RESUME POINT — E.3-proper (do this next)

The Carbon validations (R-18/19) must be re-confirmed on the new **banded** substrate. The lumping ablation
already showed the inequality engine *survives* bands (status→RS r≈0.48 with full individualism), but two things
must be fixed/finished, **in order**:

1. **Fix the bonded-mating turnover (PREREQUISITE).** With `enable_bonded_mating=True` on seeded bands the
   population is near-**frozen** (CoV≈0, births ~3–6/window vs ~15–30 on the IFD substrate). A band of ~25 should
   reproduce, so something over-suppresses it. **Diagnose** (mate availability within bands? fertility
   `fecundability` calibration? density-disease capping the dense bands below replacement?) and fix so
   generations turn over realistically. *A frozen population invalidates any downstream validation.*
2. **Re-calibrate `mate_choice_strength m`** to land status→RS **r ≈ 0.19** (von Rueden 2016) on bands — it's
   ~0.5 at m=4 now. Use the E.3 harness pattern (below).

Then (lower priority): retire the storage-**tethering** band-aid (bands are dense now → packing met → the morph
hinges on storage, not tethering); and the **per-band society + persistent pair-bonds (F.3)** arc — durable
pair-bonds → families → society attached to the band (the deferred "C", and the agent-based society definition).

---

## What was built this session (commit trail)

| Area | What | Commits |
|---|---|---|
| **Climate C.1–C.5** | seasonal(obliquity) · eccentricity+flux+ENSO · regime-shift(Markov telegraph) · catastrophe(sub-biome tag + caribou meat-crash + llanos flood) · intercept-hunting | cf74bda…6c65b36 |
| **Storage** (delayed-return) | collective per-cell granary; cred-weighted draw (Hayden inequality engine); spoilage. Binford ET≤15.25 / Testart / Woodburn. Doubles harsh-winter capacity | e8baf08, bdadf8a, 11c43f8, e2ab5a4 |
| **Society morph** (per-cell) | `society_from_character`/`morph_to_society` finally CALLED; settlement detector; egalitarian→complex→stratified; collapses under famine | a9ce4fa |
| **Emergent bands** | E.1 safety + E.2 mating movement drives; **F.1 bonded mating + band SEEDER** (per-biome, territory-spaced) → 96% in biome-diverse bands | abc5435, 67950d1 |
| **Lumping ablation** | `homogenize_cred` + `_n_fathered`; **individualism is LOAD-BEARING** | 0f39c2d |

---

## Key findings & decisions (do NOT re-litigate)

- **Individualism is load-bearing — DO NOT lump to band-as-unit.** Homogenizing within-band cred collapses the
  von Rueden status→RS skew 0.48→0.13. (A moment-tracking ensemble carrying the *variance* might preserve it, but
  that's most of the cost — not worth it.)
- **R-19 survives the move to bands** (full-individualism r≈0.48 ≈ IFD control 0.53). The inequality engine works
  on real bands. (Magnitude needs the m re-calibration above.)
- **Emergence reframed:** bands don't condense from a gas — bonded mating can't bootstrap them (no co-resident
  mates → no births). Real foragers START banded → the **seeder**; the drives then maintain/merge/split them.
- **Regime shift:** dense bands are **density-disease-regulated** (no starvation), unlike the sparse-IFD
  **starvation-limited** regime the original R-18 was validated in. The substrate changes which regulator binds.
- **Storage design (supervisor calls):** collective granary not individual (Hayden control-of-redistribution);
  draw is cred-weighted = the inequality engine; morph is **per-cell** (band = cell occupants; cell is the
  sharing unit); sedentism is emergent density+storage, **not a personal trait**; proto-ag yields **deferred**
  (DEFERRED_MECHANICS PA-1).
- **Bond pairing** previously stopped at B++ (no persistent pair-bonds); F.1 added a minimal **mate-gate**
  (births need a co-resident non-son adult male); persistent pair-bonds = F.3 (still deferred).

---

## Where things live / how to drive it

**Flags (all default OFF → bit-exact baseline):**
- `SubstrateConfig`: `group_safety_max`, `group_safety_scale`, `group_mate_min`, `group_mate_floor` (E.1/E.2 band drives).
- `DemographyConfig`: storage = `enable_storage`, `storable_fraction`, `store_capacity_reserves`,
  `storage_temp_threshold_c` (≈Binford ET 15.25 °C), `storage_decay`, `storage_tether_reserves`; morph =
  `enable_morph`, `morph_settle_steps`; bands = `enable_bonded_mating`; ablation = `homogenize_cred`.
- **Band seeding:** `seed_band_positions(fields, n, band_size=25, territory_radius=3)` → pass as
  `TerrainWorld(placement_positions=...)`. Generate matching fields with
  `generate_world({**_DEFAULT_KNOBS, "seedStr": f"world{seed}"})`.

**Code:** `phase1_model.py` (the loop: movement+grouping, harvest+storage+morph, births+bonded-mating;
`allocate_store_draw`, `seed_band_positions`, `_cell_store`/`_cell_society`/`_cell_settle`, `_n_fathered`).
`substrate.py` (`diffusion_select_target` grouping multiplier). `demography.py` (configs, `society_from_character`,
SOCIETY_PRESETS, BINFORD_PACKING_PER_KM2). `climate.py` (the C.1–C.5 ClimateField). Tests: `test_storage.py`,
`test_morph.py`, `test_bands.py`, `test_climate.py`.

**E.3 harness pattern** (rebuild as a script; lives in /tmp this session, not committed): seed bands → full
Carbon config (`enable_cred_status`, `cred_seed_sigma=0.6`, `enable_prowess_facet`, `enable_paternity`,
`mate_choice_strength=m`, `enable_game`, `game_meat_cv=2.24`, κ=1.5, `enable_bonded_mating`) → run ~1200 steps →
correlate male `cred*prowess` vs `_n_fathered` (Pearson). Arms: IFD / bands-full / bands-`homogenize_cred`.

**Docs:** `MODEL_SPEC.md` §4.1.9 (climate), §4.5.10–11 (morph + storage); `DEFERRED_MECHANICS.md` (PA-1 proto-ag);
`LITERATURE.md` (all anchors); blueprints `…_Climate_OrbitalLottery_…`, `…_Storage_Morph_…`, `…_EmergentBands_…`.

**Standing constraints:** commit messages end `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>`; science
changes need supervisor sign-off; failed gate = STOP; lit values → MODEL_SPEC + LITERATURE.md; thorough tables;
pattern = scope → lit-survey → red-team → implement step-by-step → gate → commit.
