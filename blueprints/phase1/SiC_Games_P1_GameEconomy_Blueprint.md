# SiC Games · Phase 1 · **Game / Hunting Economy**

**Status:** DRAFT for red-team (2026-06-20). Supervisor directive: add game **before** calibrating
density-disease (R-13), so the calibration sits on the complete (forage + meat) economy.

---

## 1. Why this stage

The entire model to date is **forage-only** (`game_stream=False`). The demographic/biome economy uses a
single **NPP-derived carrying capacity** (`SubWindowCapacity`: `E = Tallavaara-density(NPP)·burn`), which is
*total* HG density → **game is only *implicit*** in it. The explicit game machinery exists but is unused by
the rivalrous path (terrain `game_kcal` field; `forage_level`/`game_level`; `_select_stream`).

Adding the explicit game stream is **triply motivated**:
1. **Economic realism** — meat is a major HG calorie source (Cordain 2000: animal-food fraction rises with
   latitude, ~25–35% tropics → ≥50% high-latitude). Calibrating δ on a forage-only economy bakes in numbers
   that shift once meat is in.
2. **The variance source we kept needing.** Game returns are **high-variance, feast/famine** (Hawkes 1991:
   small-game CV ≈ 2.24). This is the *stochastic-foraging-variance* lever untried since the R-7 fork and
   deferred at T-4 — the one thing that may give the inert modulators a sustained lean-dwelling population.
3. **The mobility fix.** Migratory game-following is the **resource-tracking driver R-8 found missing** — the
   model is *under*-mobile (0.93 moves/yr vs Binford ~10–40). Herd-following is Binford's logistical-collector
   end; adding it should restore realistic mobility.

## 2. Architecture decision — DECOMPOSE, don't add (no double-count)

The Tallavaara NPP-CC **already includes** game (total HG density). So game is NOT added on top (that
double-counts the carrying capacity). Instead **decompose** the per-cell capacity into two streams:

`E_cell = E_forage + E_game`, with the split set per biome by the **forage_kcal : game_kcal ratio** (the
terrain return-rate fields) and cross-checked against **Cordain 2000** animal-fraction-by-latitude. Total
`E_cell` (and the validated CC) is **preserved**; the two streams carry distinct dynamics. Forest leans
forage; savanna/steppe/arctic lean game.

## 3. Build stages

### G.1 — Two-stream economy (resident, aseasonal core)
Decompose `E_cell` into forage + game (§2). **Sex-divided production:** women harvest forage, men hunt game
(the existing `_select_stream` energy-balance logic: a man takes game if it beats his forage return, else
falls back — soft, not a hard lock). Validate the emergent **meat fraction by biome** against Cordain 2000.

### G.2 — High-variance game returns (the variance lever)
A hunter's per-step game yield is a **stochastic draw** (lognormal, CV from `game_kcal_std`/Hawkes ≈ 2.24),
not the deterministic mean. ⇒ feast/famine: most hunts fail, occasional large kills. This is what
band-sharing (G.4) evolved to buffer, and the candidate source of the per-agent nutritional variance the
modulators need (R-7/R-8/T-4). Forage stays low-variance.

### G.3 — Biome-specific complementary seasonality (anti-phase; §4.1.4/4.1.5)
Two *different* game mechanisms, NOT one sine (§4.1.5):
- **Forest (Aché): value-via-fat** — forage **flat** (Hill 1984: calories ~aseasonal); game encounter
  ~aseasonal, **kill value ×1.25 in the fat season** (Apr–Jun). Smooth multiplier on value.
- **Savanna/llanos (Hiwi/Hadza): access-via-aggregation** — forage **wet=lean, high amplitude** (Hurtado &
  Hill 1987: ~90% rain in wet half, flood suppresses access); game **dry-season aggregation**, a
  *threshold* encounter-rate jump (Hiwi caiman ~11× wet→dry; Hadza intercept-hunting Aug–Oct only).
**The key property: forage and game are ANTI-PHASE in seasonal biomes → game fills the forage trough** (the
two-stream economy is *more* robust than forage-only). **Retro-correction:** R-6/R-10 imposed uniform forage
seasonality (`s_min=0.4`) on what should have been a *forest* (flat) — that seasonal child-mortality was
partly an artifact; seasonal stress is a savanna/llanos phenomenon. Seasonal amplitude per biome (the
`§4.1.6` star-mechanics seam bounds the per-world draw; Earth anchors forest≈flat … llanos≈high).

### G.4 — Band-wide meat sharing (the meat tier)
**Game (meat) is shared BAND-WIDE** (cell-pooled / camp-level) — the high-variance-buffering reciprocity
(Kaplan & Hill 1985; Gurven 2004) — while **forage stays household/mother-linked** (the C.2b/S1 tier). So
the two sharing topologies we identified (LIT-RESOLVED in §4.5.4) finally both exist: plant=kin, meat=band.
This smooths individual hunting variance (G.2) at the band level — the realistic buffer.

### G.5 — Migratory game + following (open biomes; the R-8 fix)
**Lit-anchored, biome-gated.** A **moving game resource** (a herd field that translates seasonally across
the terrain) in **open biomes only** (steppe/plains/tundra/savanna — migratory megafauna); resident in
closed forest. Agents **follow** it (logistical mobility — move camp to intercept). **Anchors:** Binford
1978/1980 (Nunamiut caribou hunters = the forager-collector model's logistical end), plains bison
(pedestrian + equestrian), Eurasian reindeer; **Binford 2001** for mobility rates/radii by
biome/effective-temperature. **Biome-specific rates + radii** (caribou ~100s km; bison shorter). **Addresses
R-8** (resource-tracking restores realistic moves/yr). Couples to the movement model — the largest, most
coupled piece; built last.

### Then — calibrate density-disease (δ) on the complete economy
With G.1–G.5 in, calibrate δ to the forager e₀ (~32–37) + density (Tallavaara) + diet (Cordain), then re-run
the multi-biome mortality sweep (R-12/R-13 path).

## 4. Validation / gates
- **Meat fraction by biome** vs Cordain 2000 (animal-food % by latitude/environment).
- **Mobility** (with G.5) vs Binford 2001 moves/yr by biome — the R-8 check.
- **Variance** (G.2+G.4): does band-shared high-variance game produce a sustained lean-dwelling fraction the
  modulators can act on (the R-7/T-4 question), or does band-sharing fully buffer it?
- 444-suite green throughout (opt-in flags); determinism with the new RNG draws (G.2) pre-seeded.

## 5. Red-team targets
RT-1: the decompose-the-CC split (forage:game ratio) — is preserving the Tallavaara total correct, or does
explicit game change the *effective* CC (e.g., variance + sharing alter realized intake)? RT-2: G.2's
stochastic draws — determinism / per-agent RNG / does band-sharing (G.4) cancel the variance before the
modulators see it (re-creating the R-7 wash-out)? RT-3: sex-division — does it interact with the IBI/female
fertility + provisioning (men provision via meat) correctly, no double-count with forage provisioning? RT-4:
G.5 migration — scope/complexity; the moving-resource + following is a real movement-model change; can it be
biome-gated cleanly and is the mobility anchor (Binford) identifiable? RT-5: seasonality — two mechanisms
(fat-value vs aggregation) not collapsed; anti-phase implemented; forest stays flat. RT-6: the whole stage
is large — is the G.1→G.5 sequence right, and what is the minimal subset needed *before* the δ calibration
vs deferrable after?

## 6. Out of scope / deferred
Pastoralism / herd *management* (HG following only); intra-herd predator-prey dynamics (herd is an exogenous
moving field); the full star-mechanics seasonal lottery (use Earth biome anchors); inter-band competition
over herds (→ the C-vs-Si conflict subsystem).
