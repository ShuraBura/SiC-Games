# SiC Games — Survey A: In-Hand Literature Review (Game + Forage, Static + Seasonal)

**Purpose:** Inventory what the project's existing PDFs actually deliver for (1) game return
rates by biome, (2) forage return rates by biome, and (3) the *seasonal* signal for each —
then identify gaps requiring an additional (Survey-A-fill) search. Literature only; no
implementation, no mechanic design.

**Method note:** the project "PDFs" are ZIP bundles of page-images + per-page OCR text. Several
bundles have empty or near-empty OCR (flagged below as not-machine-readable in this environment).
Read this session: Morin 2024, Janssen & Hill 2014, Hurtado & Hill 1987 (Hiwi), De Vynck 2016
(carbohydrate seasonality), plus the existing Forage Return-Rate Table.

---

## 1. FORAGE — static rates: COMPLETE (pre-existing)

The `SiC_Games_Forage_Return_Rate_Table.md` already delivers all eight biome cells in
kcal/forager-hr, validated to primary sources, with open design decisions logged (desert
sub-type split, mountain processing strategy, intertidal in/out of scope, fish unanchored).
**No further work needed on forage static rates.** It is the static-forage layer's anchor.

## 2. GAME — static rates: SUBSTANTIALLY IN HAND, needs biome-binning

Two anchors confirmed and quantified this session:

**Forest (Ache) — Janssen & Hill 2014.** Cooperative hunting is **net −4% on mean yield**
(2.82 vs 2.95 kg/day) but cuts the **zero-meat-day probability from 52% to 9%** (83% lower).
Optimal band 7–8 hunters moving nearly daily. → This is a *risk/return tradeoff*, NOT a
feasibility cliff. Confirms the corrected memory note. Forest game = cooperative hunting buys
variance reduction at a small mean cost.

**Savanna/grassland (communal drive) — Morin et al. 2024.** Ungulate communal-drive success
**67.2%** (85% CI 56.5–80.1) vs **42%** (CI 36.1–49.0) encounter. Ungulates have significantly
higher FID (flight initiation distance) for body size; herding/flocking species show ~**2×**
the communal-hunt advantage. Per-capita CDH return rates by species available (e.g. elephant
4,939 kcal/hr/capita; full per-hunt kcal/hr database in Table 1). → Grounds the **soft-gate
sigmoid** (steep-but-finite success gain from grouping), peaking for clustered, high-FID,
fast ungulates — i.e. savanna/edge prey.

**Gap (game static):** the literature gives return rates *per prey type / per hunt type*, not
yet *binned to the six terrain biomes* as kcal/hr. The hump-shaped game curve (peak at
savanna/edge, per the forage≠game principle) needs the per-prey rates mapped onto biomes.
This is an **extraction + binning task over papers already in hand** (Morin Table 1, J&H,
Hawkes Hadza, Ugan & Simms prey rank, Martu, Hiwi), not new searching. Fish/open-water game
is unanchored (same gap as the forage table's fish cell).

## 3. SEASONAL SIGNAL — now substantially covered (both flagged gaps obtained)

Both game anchors and the forage table are **static snapshots**. The seasonal layer is now
anchored by four sources, including the two previously not-readable (Hill 1984, Hadza 1991),
obtained this session. The picture is richer — and **revises the "forage ≠ game inversion"
principle**: the data span a spectrum of amplitudes, not a single anti-phase rule.

**Forest (Ache) — Hill et al. 1984 [PREVIOUSLY UNREADABLE, NOW IN HAND].** This is the
**low-seasonal-amplitude anchor**, and it overturns the prior assumption that forest tracks a
strong growing-season signal:
- **No lean season.** Total calories and *meat* calories do NOT differ significantly across
  yearly quarters (statistical tests could not distinguish them). Mean intake 3,827 kcal/
  consumer/day. Meat is 47–77% of calories year-round.
- Seasonal variance is in **species composition, not total calories.** Only honey (0.4–44%
  swing, peaks Q4 Oct–Dec) and vegetable items (6–45%, peak Q3) differ significantly by quarter.
  Q4 is a mild *fat* time (honey), not a lean time.
- **Game fat-driven caloric seasonality (~25% amplitude):** the authors recommend adjusting
  game kcal **+25% in Apr–May–Jun** (warm→cold transition, animals fattest). Wild ungulates
  ~2% fat (lean season) → ~10% (fat season); the Ache's small-bodied game (peccary, paca,
  armadillo) swings more. So forest game encounter rate is ~aseasonal but caloric *value* per
  kill carries a ~25% fat bump. Armadillos also dug from burrows mainly end-of-warm-season.

**Savanna (Hadza) — Hawkes et al. 1991 [PREVIOUSLY UNREADABLE, NOW IN HAND].** Fills savanna
game return rates by method + a dry-season-aggregation signal matching the Hiwi mechanism:
- Big-game encounter+scavenge ~**4.9 kg/hunter-day** (live mass), one animal every 29 hunter-
  days. By method: **intercept** (night, at water blinds) **7.5 kg/hunter-night ≈ 1.02 kg/hr**;
  encounter/scavenge **~0.71 kg/hr** all seasons, **~0.45 kg/hr** in late dry. Small game
  trivial (~0.062 kg/hunter-day, ~1% of tissue; post-encounter rates 0.23–0.66 kg/hr).
- **Intercept hunting is practiced ONLY in the late dry season (Aug–Oct)** at shrinking water
  sources — a second independent confirmation of dry-season prey aggregation around water as
  the savanna game mechanism (cf. Hiwi caiman 11× swing). Wet-season encounter: 1 animal/37
  days; late-dry encounter: 1/53 days but supplemented by high-yield intercept.
- (Collective-action / big-game-as-common-goods content — Hadza pay-off matrix, PD framing —
  is forward-relevant to the Cred/pool layer, NOT folded into the resource build.)

**Forage seasonality — De Vynck et al. 2016 (Cape Floristic Region, USO carbohydrates).**
Available USO species peak ~6-month window winter→early summer (Jul–Dec); lowest mid-summer→
early autumn (Jan–Apr); **the three summer months (Dec–Feb) most stressful (lean)**.

**Game + forage seasonality — Hurtado & Hill 1987 (Hiwi/Cuiva, Venezuelan llanos).** The
**high-seasonal-amplitude anchor**: ~90% of annual rain (~1665 mm) in wet season (May–Nov),
dry ~67 mm/month. **Wet = LEAN** (flood suppresses access/forage, Liebig's-Law framing);
**dry = game-fat** via aggregation (caiman 44 → 489 kg/km² wet→dry, ~11×).

### Structural finding (REVISED — replaces simple inversion)

The data give an **amplitude spectrum with biome-dependent lean-season cause**, not a single
forage/game anti-phase:
- **Forest (Ache): LOW amplitude.** Calories ~flat; variance is compositional; game carries a
  ~25% fat-value bump (Apr–Jun), encounter ~aseasonal. The flat anchor.
- **Llanos (Hiwi): HIGH amplitude.** Wet=lean (flood), dry=game-fat (aggregation). The sharp anchor.
- **Fynbos (De Vynck): forage lean in hot-dry summer.**
- **Savanna (Hadza): dry-season water-aggregation makes game accessible** (intercept method
  switches on); moderate amplitude.

Two design consequences:
1. The per-biome phenomenological curve must carry (a) amplitude, (b) phase, (c) **which season
   is lean and why** (flood / drought / cold / none), and (d) for game, whether the signal is in
   *encounter rate* vs *caloric value per kill* (forest = value-via-fat; savanna = access-via-
   aggregation). These are mechanistically different and should not be collapsed into one sine.
2. **Forest≈low and llanos≈high give the empirical amplitude range** the star-mechanics lottery
   (Survey B) should scale over. The Earth reference spans roughly flat → ~90%-rain-in-half-the-
   year; the alien-world amplitude knob extends/contracts within habitable-zone bounds from there.

---

## 4. GAPS requiring an additional search (Survey-A-fill)

1. **Game→biome binning** — mostly extraction from in-hand papers (now including the full Hill
   1984 Ache game table and the Hadza 1991 method-resolved rates); search only to fill biomes
   with no in-hand prey-rate. Likely remaining gap: **fish/open water** (unanchored in both the
   forage table and game sources). Tundra/boreal drive is covered by Morin (caribou).
2. **Seasonal amplitude/phase per biome** — now well-covered: forest (Ache, low-amplitude),
   llanos (Hiwi, high-amplitude), savanna (Hadza, dry-aggregation), fynbos (De Vynck, forage).
   The amplitude *range* (flat forest → sharp llanos) is established. Remaining: a temperate/
   high-latitude *cold-driven* lean-season anchor if the biome set needs one (current anchors
   are all low-latitude; cold-season scarcity is asserted in Hill 1984 only as the ungulate-fat
   mechanism, not a calorie collapse). Minor — search only if a boreal/alpine seasonal cell needs it.
3. **Game migration signal** (later seasonal-game stage, survey-only) — dry-season water-
   aggregation now confirmed in TWO systems (Hiwi, Hadza); broader ungulate seasonal *range
   shift* (true migration, not just aggregation) remains thin. Defer the search to when
   seasonal-game is scheduled.

## 5. Sources status (UPDATED — both prior gaps closed)

- **Ache seasonal-diet-variance** (Hill et al. 1984) — **NOW IN HAND** (re-uploaded, fully
  readable). Forest seasonal anchor resolved. Was the single most load-bearing gap.
- **Hawkes et al. 1991 (Hadza hunting income)** — **NOW IN HAND** (re-uploaded, fully readable).
  Savanna game return-rate + dry-season-intercept anchor resolved.
- Savanna activity-specific Hadza *forage* rates (Hawkes 1989) — still only figure data per the
  forage table; unchanged. (Hadza 1991 supplies *game* rates, not the forage gap.)

---

## 6. Recommendation (sequenced to the build)

- **Static-both stage (build next):** forage table is ready; game needs the biome-binning
  extraction pass (in-hand papers) + fill-search only for empty biomes (fish, possibly
  boreal). Deliver a Game Return-Rate Table mirroring the forage table's structure.
- **Seasonal-forage stage:** anchor on De Vynck (fynbos) + the forage-relevant Hiwi/llanos
  signal; phenomenological curve carrying amplitude/phase/lean-season-cause per biome.
- **Seasonal-game stage (later):** re-obtain the Ache forest seasonal source first (gap #2);
  add migration-signal search then, not now.
- **Star-mechanics seam (Survey B's job, not A):** the per-world lottery scales *amplitude*
  of these curves within habitable-zone bounds; the empirical curves here are the Earth
  reference shape. Lean-season *cause* (flood/drought/cold) is a biome property, amplitude is
  the star-modulated knob.

*Survey A complete except the flagged not-readable re-obtains (Ache seasonal, Hadza 1991).*
