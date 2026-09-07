# R-103d design note — material inheritance × property substrate (registration, pre-build)

**Status: REGISTERED, not yet built. Awaiting approval.** Predictions committed BEFORE running (charter D1).

## Question

Does bequeathing durable capital across generations convert the model's **big men** (office-advantage, non-heritable — R-103c) into **chiefs** (lineage-advantage, a heritable estate)? And is a **property substrate** (ownable land / durable estate) a *precondition* — i.e. does inheritance do nothing until there is something ownable to inherit?

## Why two axes (both lit-anchored)

- **Axis 1 — inheritance RULE.** Goody 1976 (filed) + the D-PLACE EA075×EA028 cross-tab: the rule is regime-dependent. Primogeniture *concentrates* (one heir), partible/equal *dissipates* (split each generation). "None" = today's model.
- **Axis 2 — property SUBSTRATE.** EA: foragers do **not** inherit land (77–89% "no inheritance") — land isn't property. So hereditary material stratification may *require* land ownership (`enable_improved_land`, already in the model) or a storable-glut estate (Flannery ch.5, NW Coast). The R-103c finding — big men who can't bequeath — may be *ethnographically correct* until this substrate is on.

## The mechanism to build (default OFF, bit-exact)

New config (`demography.py`):
- `enable_material_inheritance: bool = False`  — OFF ⇒ material dissolves at death exactly as now (bit-exact).
- `material_inheritance_rule: str = "primogeniture"` — enum: `none | primogeniture | partible_equal | patrilineal_sons`.
- (later) `material_inheritance_auto: bool` — pick the rule per village from its subsistence regime (Goody), the "varies by biome" mode. NOT in this sweep; noted.

At death, if `material > 0`: find heirs among the decedent's children (`_father`/`_mother` reverse index, built per step), transfer per rule —
- `primogeniture` → whole estate to ONE heir (eldest surviving child; tie-break deterministic);
- `partible_equal` → split equally among all surviving children;
- `patrilineal_sons` → split equally among surviving sons;
- no heirs → estate dissolves (as now).

Implementation note: needs a parent→children lookup (the model has child→parent only). Build once per step or maintain incrementally; deaths are the trigger, so O(deaths) with an index.

## The grid (each cell one run; predictions committed)

| # | inheritance | substrate | PREDICTION (committed) |
|---|---|---|---|
| 1 | none | forage-only | big-man baseline: noble_material_lift ≈ 1.0, no break. **[null / reproduces R-103c]** |
| 2 | none | improved_land ON | still big-man (nothing bequeathed). **[substrate-alone control]** |
| 3 | primogeniture | forage-only | **KEY TEST** — probably STILL no break: nothing ownable to concentrate. If a break appears here, the "needs substrate" hypothesis is wrong. |
| 4 | primogeniture | improved_land ON | **THE HYPOTHESIS** — estate concentrates in a lineage → noble_material_lift > 1, village_gap_d rises, a chiefly break. |
| 5 | partible_equal | improved_land ON | weaker / no break — splitting dissipates the estate each generation (Goody's intensive-agri pattern). |

Cells 1–2 are controls; 3 isolates axis-2; 4 is the target; 4-vs-5 isolates axis-1 (concentrate vs dissipate).

## Worlds & horizon

- **Worlds:** coastal-temperate (R-64 baseline) + one where `improved_land` bites (cultivable terrain — likely `flat`/`hilly` temperate; confirm cultivability at build). Keep to 2 worlds to bound cost.
- **Horizon:** 3000 steps (~10 generations — an estate needs generations to compound; R-103c/endogamy showed 250 steps is far too short). Flat/rich arms compute-capped (`C_MAXMIN`).
- **Cost** (from the derived law ~0.8 min / 1k-steps / 1k-agents): 5 cells × 2 worlds × ~3000 steps at pop 3–7k ≈ 10–25 min each ⇒ ~2–4 h sequential. Bounded.

## What we measure (diagnostics already wired, R-103c)

Primary: `noble_material_lift` (does the LINEAGE now hold more material? the chief signal), `noble_cred_lift`. Break: `village_gap_d_med`, `frac_villages_broken`. Support: `gini_material`, `mean_material`, `frac_ascribed_pop`, `pct_stratified`.

**Success criterion:** a cell where `noble_material_lift` rises durably above 1.0 (heritable estate) AND `village_gap_d` grows a real gap — i.e. chiefs emerge — versus the flat baseline. Registered as: cell 4 succeeds, cells 1–2 stay flat.

## Known caveats / companion levers (not in this sweep)

- **Nobility breadth.** ascribed_frac 25–44% is too broad (EA true-elite few %). BUT if inheritance concentrates material into a FEW lineages, a *material* elite can form even under a broad label — watch whether the material break is carried by a small subset. Ascription-tightening is a separate lever, flagged not built.
- **`improved_land` couples to the economy** (needs `C_DEFEND=1`, cultivable terrain) and was NOT in the R-64 validation — so cells with it on are not directly comparable to R-64's 9–16%; they test the mechanism, not the baseline.
- **Descent.** primogeniture/patrilineal assume the patriline; under a matrilineal descent rule (#48) heirs would be sisters' sons (the avunculate). Out of scope here; the rule enum leaves room.
