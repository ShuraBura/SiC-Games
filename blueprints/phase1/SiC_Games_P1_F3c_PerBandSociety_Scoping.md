# SiC Games P1 — F.3c: the band as a first-class entity + per-band society (SCOPING)

**Goal.** Two coupled gaps remain after F.3a/b (persistent families):
1. **Multi-family band.** F.3a/b produced *nuclear-family-sized* bands (~7, agent-weighted). Ethnographically a
   band is **multi-family, ~25, marriage-linked, mostly NON-kin** (Hill et al. 2011; Birdsell magic number). We
   need families to **affiliate** into a persistent ~25 band.
2. **Per-band society.** The morph (egalitarian→complex→stratified + κ + family knobs) currently attaches to the
   **cell**; it should attach to the **band** (the agent-based society the handoff deferred).

Status: SCOPING (lit survey → scope → red-team). Nothing built. Decisions pending supervisor sign-off.

---

## §1. Lit survey — what a band IS, how big, what holds it together, how society sits on it

| Quantity / claim | Value / form | Source | Status |
|---|---|---|---|
| **Band ("magic number")** | **~25** land-using/foraging group; nests in a **~500** dialectal tribe / connubium | Birdsell 1953/1968 (Man the Hunter) | NEW — needs filing/verification |
| Band ~25–50, ~7–8 foragers, multi-family | modal ~25, flexes seasonally | Wobst 1974; Kelly *Foraging Spectrum* | FILED (Wobst, Kelly cited) |
| **Band composition = mostly NON-kin, marriage-linked** | primary kin a minority; affines + distant kin dominate | **Hill et al. 2011** *Science* | FILED (§4.8.7) |
| **Nested, self-similar (fractal) social structure** | individual→family→band→community→tribe, **scaling ratio ≈ 3–4** (≈3.8): ~1→~4→~15→~50→~150→~500 | **Hamilton, Milne, Walker, Burger & Brown 2007** *Proc R Soc B* 274:2195 | NEW — needs filing/verification |
| **Fission–fusion** | bands aggregate (wet/abundant) & disperse (dry/lean); membership fluid; band is a *recognized* unit, not fixed | Kelly; Marlowe 2010 (Hadza camps ~mean 30, high turnover) | FILED (Kelly); Marlowe NEW |
| **What holds a band** | co-residence + kinship + **marriage ties** + reciprocal access/sharing networks (e.g. hxaro) | Hill 2011; Wiessner (Ju/'hoansi hxaro) | partial |
| **Exogamy / residence** | band-exogamous marriage; **multilocal/flexible** residence (not rigid patri/matrilocal) | Marlowe 2004 (cited) | FILED |
| **Band-level egalitarianism** | actively leveled (reverse dominance); hierarchy needs storage/packing (the morph ladder) | Boehm 1999; Testart/Binford (the morph) | partial |

**Survey synthesis (the design constraints these impose):**
- A band is a **level in a nested hierarchy** (Hamilton 2007), ~25, that **bundles multiple nuclear families**
  (F.3a/b) **+ unrelated/affinal members** — so it is NOT a lineage/clan (Hill 2011: mostly non-kin). The glue is
  **marriage + reciprocal access**, not common descent.
- Band membership is **fluid (fission–fusion)** but the band is a **persistent, recognized social unit** —
  i.e. it needs a stable *handle* even as members come and go. This is exactly what the F.2 diagnostic showed the
  emergent connected-component band LACKS (it is too fluid for persistent society to attach to).
- ⇒ the model needs **(a)** a band-affiliation that is persistent but exogamous/non-kin, sized ~25 by
  fission/fusion, and **(b)** society attached to that band.

---

## §2. Scope — design (minimal-first), two sub-steps

### F.3c-1 — the band as a persistent affiliation (the ~25 multi-family entity)
Introduce a lightweight **persistent band affiliation** `agent._band_id` (the stable handle society attaches to),
kept spatial by a **band-cohesion movement drive** rather than imposed teleporting — emergent dynamics, stable id.
- **Seed:** the initial seeded bands get distinct ids (already territory-clustered).
- **Inheritance:** a newborn takes its **mother's** `_band_id`.
- **Exogamy at marriage:** at pairing the **incoming spouse joins the partner's band** (so a band RECRUITS
  unrelated members each generation → stays non-kin, Hill 2011). Residence locus = **flexible** (join the
  larger/richer of the two bands — Marlowe multilocal), default the female's band (consistent with F.3b's
  mother-centred family). *(This is the key red-team lever — see §3.6.)*
- **Cohesion (movement):** a family-mother's diffusion utility gains a **band-cohesion term** — a pull toward her
  band's centroid / band-mates — composed with (not replacing) the per-capita-yield food term, so the band
  co-resides as ~25 while food stays the dominant force (§3.3).
- **Fission/fusion (emergent, hysteretic):** band > `band_split` (~40–50, the upper "community" rung) → split into
  two ~25 (by sub-cluster/lineage); band < `band_min` (~8–10) → merge into the nearest band (adopt its id).
  Different thresholds = hysteresis (no thrash). Target emergent band ~25 (Birdsell/Wobst).
- **Validate:** emergent band-size distribution centred ~25; band composition mostly non-kin + marriage-linked
  (Hill 2011 — measure kin fraction); durable-band fraction (F.2 metric, now 0.41) rises further.

### F.3c-2 — per-band society (relocate the morph)
- Re-key `_cell_society`/`_cell_settle`/the morph from **cell** → **`_band_id`** (`_band_society`).
- The band's **aggregate** character drives `society_from_character`: band **density** (members / territory-area)
  vs Binford packing; band **surplus** (band granary / capacity). → the band's society type → its **κ** (meat/
  store contest exponent) + **family knobs** (mate_choice_strength, assortment, patriline_weight, paternal
  provision) read **per band** by reproduction (localizing the currently-global config — the deferred per-cell
  family-knob localization, now per-band).
- Storage: the granary becomes **per-band** (or stays per-cell, aggregated to the band for the surplus signal — a
  decision, §3.5).
- **Validate:** the egal→complex→stratified ladder fires on band character (not cell); a stratified band shows the
  expected κ/inequality signature; warm/mobile bands stay egalitarian (Testart/Woodburn geography preserved).

**Build order:** F.3c-1 (band entity + ~25 + non-kin composition) → gate → F.3c-2 (per-band society) → gate.

---

## §3. Red team — failure modes & design tensions (the decisions)

1. **Affiliation ↔ spatial drift.** A persistent `_band_id` can decouple from spatial reality (a "band" scattered
   across the map) if cohesion is too weak. → cohesion drive must keep band-mates co-resident; the band_id is
   authoritative, but a *sanity re-sync* (a member separated from its band for N steps defects to the local band)
   prevents ghost bands. **Risk:** two definitions of "band" (affiliation vs connected component) diverge.
2. **Fission/fusion thrashing.** Split≈merge thresholds → oscillation. → hysteresis (split ~45, merge <10) + a
   settle timer (like the morph). **Risk:** unstable band counts; mitigated by the gap.
3. **Cohesion vs family foraging (movement over-constraint).** F.3b already pulls children+father to the mother;
   F.3c adds a pull toward the band centroid. Stacking biases can override the food gradient → families forage
   sub-optimally → starve. → **food must stay the dominant term** (cohesion a bounded multiplier, like E.1/E.2);
   validate eq_pop is preserved. **Risk:** carrying-capacity loss.
4. **Per-band density vs the packing threshold (the morph trigger).** Binford packing (0.091/km²) is a PER-AREA
   density; a band of 25 over its ~300–800 km² territory sits **at/below** packing (§4.5.10's standing caveat). If
   per-band density rarely crosses packing, the per-band morph is **inert** (opposite of the per-cell version that
   over-fired via tethering). → reconcile: use **band packing within its OCCUPIED footprint** (members / occupied-
   cell-area), or treat the band's aggregation itself as the packing signal. **Risk:** the relocation makes the
   morph never (or always) fire — needs a defined band-density metric.
5. **Per-band storage grain.** The granary is per-cell (S.1). Per-band society wants a band-level surplus signal.
   → either move the granary to the band, or aggregate per-cell stores within the band for the surplus read.
   **Risk:** double-moving a built mechanic; keep per-cell granary, aggregate for the signal (less disruptive).
6. **Bands become KIN-CLANS (contradicts Hill 2011).** If `_band_id` is matrilineally inherited AND the male
   always joins the female's band, a band drifts toward a single matrilineage — *mostly kin*, the OPPOSITE of the
   ethnography. → **exogamy must import unrelated spouses every generation** + **fission must cut across lineages**
   (split by space, not lineage). Measure the **within-band kin fraction** and tune exogamy/fission to keep bands
   mostly non-kin. **This is the central validation** (Hill 2011) and the key residence decision (D2).
7. **Emergent vs imposed (the supervisor's standing preference).** A full `_band_id` registry + fission/fusion is
   *imposed* structure — against the "let it emerge" grain that worked for F.2 merge/split/collapse. The HYBRID
   (persistent id as a stable handle + emergent cohesion/fission/fusion) is the compromise: the dynamics emerge,
   the id only provides society's anchor. **Alternative (lighter): emergent-only** — strengthen the grouping
   drives to aggregate families to ~25 and attach society to the F.2 lineage-tracked component (no band_id). Risk:
   fluid components are a shaky society anchor (the F.2 finding) and ~25 via tuning is uncertain.

---

## §4. Decisions — LOCKED (supervisor 2026-06-29)
- **D1 — approach: hybrid persistent affiliation + emergent dynamics.** BUT the affiliation is **NOT a scalar
  band_id** — it is a **COLLECTIVE-IDENTITY VECTOR** `agent._group` (the Carbon "hive-mind"): band_id is ONE cell;
  the others are **reserved seams** for later — **`assabiyah`** (Ibn Khaldun group-solidarity / cohesion strength),
  **`religion`** (organized religion), … with **biome differences** feeding in. v1 builds the vector + assigns
  `band_id` (+ a neutral `assabiyah` cell); the rest are documented inert seams. (This is the C-collective vehicle
  the project has been pointing at; band affiliation is its first facet.)
- **D2 — residence: FLEXIBLE / multilocal** — the incoming spouse joins the larger/richer of the two bands (default
  the mother's when tied); mixes lineages across bands → bands stay mostly non-kin (Hill 2011).
- **D3 — band density = members / occupied-footprint area** (a tight band reads as packed even on a large
  territory; the morph fires on real aggregation).
- **D4 — build order: F.3c-1 then F.3c-2, gate each.**

### Group-identity vector (the seam to build)
`GroupVector` (per agent, `agent._group`): `band_id:int` (ACTIVE — the affiliation) · `assabiyah:float` (SEAM —
group solidarity/cohesion, neutral default, will later modulate the cohesion drive + survive/​fission decisions) ·
`religion:int|None` (SEAM — deferred; biome-linked) · room for more. Inheritance: newborn copies the mother's
vector; marriage merges per D2 (band_id ← chosen band; assabiyah/religion later). Only `band_id` is read in F.3c.

## §5. Validation plan (gates)
- F.3c-1: emergent band size centred **~25** (Birdsell/Wobst); **within-band kin fraction LOW** (Hill 2011); durable-
  band fraction ↑; eq_pop preserved (cohesion didn't starve them); band counts stable (no fission/fusion thrash).
- F.3c-2: the egal→complex→stratified ladder fires on **band** character; warm/mobile bands stay egalitarian; a
  stratified band shows the κ/inequality signature; per-band family knobs read correctly.
