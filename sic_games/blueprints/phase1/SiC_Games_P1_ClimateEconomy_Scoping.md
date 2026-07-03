# SiC Games — Phase 1 — Economy-from-Climate rebuild (Miami NPP + structured precip + Whittaker biome + aquatic)

**Status:** SCOPED + RED-TEAMED 2026-07-03. Option B (the deep, first-principles substrate). SUBSUMES the aquatic-food stage (`…_BiomeClimate_AquaticFood_Scoping.md` S1–S6 becomes the tail of this). Foundational — needs supervisor sign-off; built as an OPT-IN world-generation MODE so it does NOT invalidate the legacy substrate/results.
**Founding-goal connection:** the project's original aim was **realistic food yield, spatio-temporally**. Today NPP = a fractal-NOISE moisture field × terrain penalties, with **no temperature** and no real rainfall; biome is a label; food-rates are biome-keyed lookup tables. This stage makes the **food economy emerge from climate**: insolation → temperature + precipitation → NPP (Miami) → yield, with biome a descriptive byproduct.

## 1. The first-principles causal chain (what B builds)
```
INSOLATION (latitude, obliquity ε, month)
  ├─► TEMPERATURE  T(cell,month) = T_lat(lat) − LAPSE·elev + maritime(dist_water) + T_seasamp(lat,continentality)·wave(month)
  └─► PRECIPITATION P(cell,month) = P_bands(|lat|: ITCZ-wet, subtropical-dry, midlat-wet) × orographic(windward/leeward) × maritime × wave(month)
        ↓
     NPP = MIAMI(T, P) = min( NPP_T(T), NPP_P(P) )        [Lieth 1975]  — per-cell, seasonally pulsing
        ↓
     BIOME = WHITTAKER(T_annual, P_annual)                — DESCRIPTIVE label only (reporting)
     YIELD = f(NPP)  [terrestrial forage + game]  +  AQUATIC_FOOD  [fisheries]   — retire biome-keyed tables
        ↓
     CAPACITY (Tallavaara density from NPP_gm2 + aquatic subsidy)
        ↓
     AGENTS / SOCIETY (unchanged mechanics)
```
Key point: **NPP becomes real g/m²/yr from T×P**, which is exactly the x-axis Tallavaara's density regression expects — so Miami-NPP + Tallavaara-capacity is a *coherent physical pairing* (today we feed Tallavaara a noise proxy).

## 2. Components
- **C1 Temperature** `T(cell,month)`: latitude gradient (have) + **elevation lapse** (−6.5 °C/km) + **maritime moderation** (near large water → milder mean, smaller seasonal amplitude) + **seasonal cycle** (amplitude ∝ |latitude|·continentality, scaled by obliquity ε — the existing orbital knob). One insolation driver → temperature season AND (C3) NPP season AND the salmon window (kills RT-D double-season).
- **C2 Precipitation** `P(cell,month)`: **latitudinal bands** (Hadley/ITCZ: wet ~0°, dry subtropics ~30°, wet mid-lat ~50°, dry poles) + **orographic** (prevailing-wind windward wet / leeward rain-shadow via elevation gradient) + **maritime** (moisture supply near water) + **monsoonal season** (wet season in the high-sun half) + a retained NOISE component for organic texture (RT-7). Replaces the bare `moist` noise field. Lit: standard climatology (Hadley cells, orographic precip). NOT an atmospheric GCM — a parameterized pattern.
- **C3 NPP = Miami** (Lieth 1972/1975): `NPP_T = 3000·[1+e^{1.315−0.119·T}]⁻¹` (T °C), `NPP_P = 3000·[1−e^{−0.000664·P}]` (P mm/yr), `NPP = min(NPP_T, NPP_P)` [g dry-matter/m²/yr]. **Coefficients VERIFIED (2026-07-03) from multiple open secondary sources** (Lieth & Box PubMed 756053; Scurlock & Olson 2002; FAO Unasylva 114; Bernardi Miami-Model) — fit by least-squares on 50 sites/5 continents. Primary Lieth PDF pending (SciHub skill not available this session). Per-cell from annual T,P; seasonal pulse from monthly T,P (growing-season). Replaces `npp = wet×elev_pen×slope_pen`. Temperature-limited (cold→low even if wet = tundra) AND precip-limited (dry→low = desert). Feeds `npp_gm2` directly (no ×3400 fudge).
- **C4 Biome = Whittaker** (T_annual × P_annual → label): descriptive tag for reporting only; retire the npp/forestness classifier. No mechanic reads the label.
- **C5 Retire biome-keyed yield tables:** terrestrial forage yield = f(NPP); game biomass = f(NPP) (Coe et al. ungulate-NPP, already a noted anchor) — replace `FORAGE_KCAL_TARGETS`/`GAME_KCAL_TARGETS`/`GAME_MOBILITY`. (Capacity already uses NPP, so forage_kcal was dormant; the live consumer is the game stream.)
- **C6 River-source temperature + C7 aquatic-food field + wire into capacity + C8 morph-from-density** = the aquatic-food stage (prior blueprint S2/S4/S5/S6), now sitting on real climate. Coastal super-density → Binford packing → `stratified` reachable (the dynastic-arc prerequisite).

## 3. The tractability decision — a MIGRATION toggle, not permanent parallelism (RT-8)
The climate economy is built behind a world-generation toggle `generate_world(…, mode="legacy" | "climate")`, but this is a **migration scaffold, NOT a permanent fork**. The toggle exists only to make the transition safe and provable:
- **A/B validation** — run the SAME social config on legacy vs climate worlds and confirm the validated social results (status→RS, bands, morph) still hold; that is how we PROVE EFC didn't silently break the science.
- **Non-destructive build** — existing tests/results stay green while EFC is developed.
- **Fallback + bisectability** — if EFC fails GATE 1 we haven't destroyed legacy; if a result shifts we know substrate vs mechanic.

**End state: once EFC is validated AND performs, it becomes the DEFAULT and legacy is DEPRECATED** (kept as a frozen reference to reproduce old results, or retired). Legacy-default is temporary — it holds only until sign-off, then the default flips to `climate` and legacy is marked deprecated. So the sequence is: toggle-during-migration → validate → flip default to EFC → deprecate legacy. This converts "re-validate the entire model at once" (intractable) into "validate the new substrate, then cut over" (bounded).

## 4. Ordered build + gates (each step ablatable; gate = re-validate before proceeding)
1. **C1 Temperature** (lat+elev+maritime+season) — inert (only storage-gate/grass read T). No gate.
2. **C2 Precipitation** field — inert until NPP reads it. No gate (validate the pattern looks Earth-like: wet equator, dry 30°, rain-shadow deserts).
3. **C3 NPP = Miami(T,P)** under `mode="climate"` — **GATE 1**: NPP distribution realistic (biome-appropriate magnitudes); Tallavaara capacity sane; a demographic smoke-test (does a world sustain a population like the legacy substrate?).
4. **C4 Whittaker biome** (descriptive) + **C5 retire yield tables** (yield=f(NPP)) — **GATE 2**: biome map Earth-like (latitude bands + rain-shadow); game-stream yields sane vs the old tables; world-lottery archetypes reworked to CLIMATE parameters (a "desert world" = hot+dry climate) and still produce diverse worlds.
5. **C6 river-source T** (routing) — inert. No gate (validate montane-fed rivers cold, lowland warm).
6. **C7 aquatic-food field + C8 wire into capacity** — **GATE 3**: interior bit-exact (aquatic=0 inland); coastal density rises without runaway; agents cluster on productive water (Gap-B fixed).
7. **C9 morph from aquatic-subsidized density** (retire R-46/47/48 heuristic; `stratified` reachable) — **GATE 4**: biome→society pattern correct (cold productive coasts/rivers → complex/stratified; warm tropics + interior desert → egalitarian) — WITHOUT tuning to biome labels (RT-E).

## 5. Red-team
- **RT-1 [TOTAL blast radius] — dominant risk.** Miami-NPP changes the capacity substrate → in principle every NPP-dependent result (R-2…R-48) differs. **Mitigation = §3: opt-in mode.** Legacy frozen+valid; climate validated fresh. Without this, B is intractable. WITH it, B is bounded. This mitigation is load-bearing — if we can't cleanly gate legacy vs climate, DON'T do B.
- **RT-2 [Miami↔Tallavaara coherence] — actually a PRO.** Tallavaara's regression expects real NPP g/m²/yr; today it's fed a noise proxy. Miami gives real NPP → the capacity becomes properly grounded. Argues FOR B. (Watch: Miami's absolute scale must land in Tallavaara's fitted range, else recalibrate the anchor.)
- **RT-3 [precip calibration].** Latitude-band positions/amplitudes, prevailing wind, orographic strength = new constants. Lit-anchored (Hadley/ITCZ) but PROVISIONAL; mis-set → unrealistic NPP/biomes. Mitigate: validate the precip+biome map against Earth expectations (deserts at 30°, rainforest at equator) before trusting downstream.
- **RT-4 [seasonal NPP].** Miami is annual. Seasonal NPP needs a monthly/growing-season model → more complexity; must reconcile with the existing `ClimateField.season()` food-modulation (they should become ONE emergent thing, not additive). Risk of double-seasonality (mirror of RT-D).
- **RT-5 [world-lottery redefinition].** Archetypes become climate-parameterized (latitude, obliquity, precip band). Full rework of world-generation control; risk of degenerate worlds (all desert/ocean) if climate knobs mis-set → need guardrails + the GATE-2 diversity check.
- **RT-6 [loss of direct control / emergent surprises].** Everything emergent → you can't hand-place a biome; worlds are whatever climate yields. Could surprise (an archetype that won't produce its biome). Mitigate: parameter search to map climate-knobs → intended archetypes; keep a legacy escape hatch.
- **RT-7 [striping].** Latitude-banded precip could make worlds look artificially striped. Keep a noise component in precip + let orography/terrain break bands.
- **RT-8 [tractability] — see §3.** THE enabling mitigation.
- **RT-9 [runtime] — none.** All one-time at generation (vectorized + one-time routing); zero per-step. Confirmed.
- **RT-10 [over-abstraction / ROI].** Do forager social dynamics NEED Miami, or is it gilding? Payoff = (a) climate-responsiveness for the deep-time/ice-age/orbital dynamics on the roadmap, (b) coherent biomes, (c) grounding Tallavaara, (d) the founding realistic-yield goal, (e) seasonal NPP emerges (retires the a_seas knob). Justified IF deep-time climate is a real destination; premature if the near-term need is only the morph fix (→ then option A suffices). **This is the honest go/no-go: B pays off over the long arc, not just the current morph.**
- **RT-11 [validation of "emergence"].** Must show the climate substrate reproduces KNOWN patterns *without* tuning: Earth-like biome banding; Tallavaara density; and the social results (status→RS, bands, morph) hold. If we tune the climate to force a target, it's not first-principles (mirror of RT-E).
- **RT-12 [scope creep guard].** B is an economy rebuild, not a stage. Enforce §4 step-by-step with gates; do NOT let it sprawl into a full GCM (atmospheric dynamics are explicitly OUT — parameterized precip only).

## 6. Recommendation
B is the principled substrate and delivers the founding goal, and RT-9 (runtime) + RT-1-mitigated (opt-in mode) make it feasible without invalidating prior work. **Go — as an opt-in `mode="climate"` world-generation path**, built C1→C9 with GATES 1–4, legacy default until sign-off. The load-bearing enabler is §3 (opt-in mode); the load-bearing risk is RT-1 (blast radius) and RT-4 (seasonal NPP reconciliation). Constants (lapse, precip bands, Miami coeffs, salmon cutoffs, aquatic weights) PROVISIONAL → per-step sweeps + supervisor sign-off. Stop-and-decide after **GATE 1** (Miami NPP): if the climate NPP substrate can't sustain populations comparably to legacy, the economy rebuild is not viable and we fall back to option A.
