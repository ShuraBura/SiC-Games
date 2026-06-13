# SiC Games — Phase 1 Stage 1b: Correction & Deferral

**Type:** Correction (retract a wrong finding) + one data glance + roadmap deferral entry.
No generator change. No new mechanic. Minimal-footprint stage.
**Hands to:** Claude Code (CC). Run straight through; block only on a failed acceptance check.

---

## 1. Why this stage exists

Stage 1b's M2 analysis produced a finding, **§H-NO-COASTAL-MORPHOLOGY**, that is **wrong** and must be
retracted. It claimed the generator produces no coastal morphology, inferred from
`largest_exterior_shore_to_area` (s2a) collapsing to ~0.1–0.2 as exterior fraction grows. That inference is
invalid: s2a is shoreline ÷ body-area, so a large sea with a genuinely long coast scores **low** s2a because
the denominator (body area) is large — not because the coast is short. The supervisor confirms by direct
observation that high-water maps **do** exhibit large edge seas with long coastlines. s2a measured
crinkliness-per-unit-water, not coastline length; it was the wrong construct for "coastal." The finding is
retracted, not amended.

Separately, the supervisor has made a strategic scope decision (see §3): the current arc stays **continental**
(lakes only, no ocean/sea coast), and geographic-structure generation (coastlines, archipelagos) is
**deferred to a named future stage**, to be built only alongside the dynamics that give it meaning.

---

## 2. Tasks (do now)

### Task 2.1 — Retract §H-NO-COASTAL-MORPHOLOGY
In whatever document it was logged to, mark §H-NO-COASTAL-MORPHOLOGY **RETRACTED** with a dated note:
> RETRACTED (Stage 1b correction). The finding inferred absence of coastal morphology from low
> `largest_exterior_shore_to_area`. That inference is invalid: s2a = shoreline / body-area, so a large
> exterior sea with a long coastline scores low s2a due to large body-area, not short coast. Direct map
> observation confirms long coastlines do occur at high water abundance. s2a is the wrong construct for
> coastline length; superseded by an absolute-shoreline measure if/when coastal generation is built
> (deferred — see §STAGE-GEOSTRUCT). No claim about generator coastal capability is currently logged.

Do NOT delete the original entry; mark it retracted with the reason, preserving the record (never bury
adverse results — including our own retracted ones).

### Task 2.2 — M1 glance: lock the 0.12 threshold
Query the **existing** M1 sweep data (no re-run). Report two values and their separation:
- the `waterK` at which `interior_water_fraction` peaks (immediately before its collapse as bodies merge);
- the `waterK` at which `exterior_water_fraction` crosses 0.12.

Purpose: confirm the 0.12 guard crossing sits **clear of** the mid-`waterK` interior-collapse/merge regime
(where interior↔exterior classification is fragile). If the two `waterK` values are well separated, the
0.12 guard is clean and is **LOCKED** (remove "provisional" status on `EXTERIOR_WATER_CEILING`). If they
coincide (crossing falls inside the merge transition), do NOT auto-adjust — STOP and report; threshold
revision is a supervisor decision.

### Task 2.3 — s2a status note
Add a one-line comment at the `largest_exterior_shore_to_area` definition site noting it is retained as a
crinkliness measure but is **not** a coastline-length measure, and must not be used to infer presence/absence
of coastal morphology. The correct coastal statistic (absolute exterior shoreline) is deferred to
§STAGE-GEOSTRUCT.

---

## 3. Roadmap deferral entry (log to ROADMAP.md and/or the spec backlog)

### §STAGE-GEOSTRUCT — Geographic-structure generation (DEFERRED, stage number TBD)

**Status:** Deferred. Committed to the roadmap as a destination; not scheduled. Do NOT build now.

**Scope decision (supervisor, this session):**
- The current arc stays **continental**: interior water (lakes) only; no ocean/sea coast; no exterior
  coastline. The `EXTERIOR_WATER_CEILING = 0.12` guard enforces this by intent — excluding coastal/ocean
  worlds is the desired behaviour for the current arc, not a conflict.
- Geographic-structure generation is a large deliverable in its own right and is deferred to its own
  stage, to be built **only alongside the dynamics that make geographic structure meaningful** (seafaring /
  tier-3 offshore resources, regional connectivity, traversal). Terrain-without-mechanic is not built
  ahead of its mechanic (consistent with §DECISION-NO-RIVERS).

**Contemplated content (reference map, not a build commitment):**
- Two distinct world generators beyond the continental generator:
  1. **Continental-margin / long-coastline generator** — decouples sea extent from the single
     water-abundance knob; produces a controllable long ocean coastline with land behind it. Requires
     independent control of *exterior* water morphology (the deferred "Problem 2": e.g. a boundary-distance
     bias in the elevation primitive so low ground concentrates against chosen map edges, rather than
     exterior sea emerging incidentally from `waterK`).
  2. **Archipelago generator** — multiple land bodies separated by sea; high coastline, fragmented land.
- These feed existing forage/resource dynamics plus future offshore/seafaring dynamics when those stages
  arrive.

**Diagnostics this stage will require (deferred with it):**
- Replace/supplement `largest_exterior_shore_to_area` with **absolute exterior shoreline length** (and a
  minimum-exterior-body-size gate to denoise sub-5-cell edge puddles), since s2a is confirmed unfit for
  coastline measurement.
- Target-statistic benchmarks for generate-to-spec: coastline-length distribution, land-body-count and
  body-size distributions, exterior/interior split. These make the generator build **assertable** (CC can
  iterate to convergence against target statistics; the supervisor benchmarks execution) — terrain
  generation to spec is a bounded, checkable problem suitable for an iterative CC session.

**Methodological boundary (pre-registered):**
- World *generation* (terrain to spec) is assertable and CC-iterable against target statistics.
- The *dynamics* that make geographic features meaningful (seafaring, traversal, regional shock response)
  are model science and are NOT one-prompted or iterated-to-convergence. Each enters as its own
  pre-registered stage with its own hypothesis and gate. The geostruct terrain sits inert as substrate,
  pre-registered as analytically inert, until its dynamics stage arrives.
- Rationale logged: generated dynamics have no visible correctness criterion; a plausible-looking emergent
  pattern can be an initialisation/implementation artifact indistinguishable from real dynamics without a
  pre-registered benchmark. This is why generation may be iterated but dynamics may not.

---

## 4. Acceptance block (must all pass)

1. §H-NO-COASTAL-MORPHOLOGY is marked RETRACTED with the §2.1 note; original entry preserved, not deleted.
2. M1 glance (§2.2) reports both `waterK` values and their separation; threshold status updated
   (LOCKED if separated, STOP-and-report if coincident).
3. s2a status comment (§2.3) present at the definition site.
4. §STAGE-GEOSTRUCT entry (§3) logged to ROADMAP.md / backlog with full scope, contemplated content,
   deferred diagnostics, and methodological boundary.
5. No code behaviour change: all existing tests still pass; no field value, denominator, or guard threshold
   value is altered (the 0.12 constant's *value* is unchanged; only its provisional/locked *status label*
   updates per §2.2).

## 5. Stopping rule

Run straight through. The only blocking STOP is §2.2 finding the 0.12 crossing coincides with the merge
regime — that is a supervisor decision, report and STOP. Otherwise complete and report green.

## 6. Definition of done

Finding retracted (record preserved), threshold locked (or escalated), s2a annotated, §STAGE-GEOSTRUCT
on the roadmap as a committed-but-unscheduled deferral, tests green. Next stage after this is the
co-location/social-productivity gateway mechanic (separate blueprint).
