# SiC Games — CC Directive: Consolidated Reconciliation + Relevance Triage + Guard Finalization

**Type:** Maintenance + decision-recording. No new mechanics, no model runs, no sweeps.
**Mode:** FIX-WITH-REVIEW. CC applies the tasks below and ends with a diff summary plus the
triage table for supervisor review. STOP-AND-REPORT items are reported, not auto-resolved.

**Authority rule:** PARAMETERS.md (recording the Sugarscape constitution) is the
human-authoritative source for locked parameter values. config.py defaults reconcile *to*
PARAMETERS.md, never the reverse.

**Prerequisites resolved (do not reopen):**
- C1-2 (σ_inherit) is a config-default fix, NOT a corrective sweep. Stage 5.2-era runs are
  not load-bearing. Do not launch, re-run, or sweep any model run under this directive.
- Stage 1c guard is finalized below (Task 7) — pure single-body ceiling, no conjunctive logic.

**Reads from:** the report CC produced from the Stage 1b/1c blueprint runs, and the lint
report `outputs/docs_lint_20260613/lint_report.md`.

---

## Task 1 — σ_inherit config default (C1-2 / C2-1 row 2)

PARAMETERS.md §7 locks σ_inherit = 0.10; `ReproductionConfig.inherit_sigma` defaults to 0.05.
Reconcile the default to **0.10**. Update MECHANISMS.md: σ_inherit OPEN/under-review → LOCKED,
citing PARAMETERS.md §7 / constitution (staleness fix, not a re-opening). No audit of past runs.

## Task 2 — Missing-YAML hardening (C2-1 root cause)

For all five C2-1 parameters: reconcile each config.py default to its PARAMETERS.md LOCKED
value (list every one in the diff: param, old → new, PARAMETERS.md ref).

Add a launch-time guard: when a run resolves config, any LOCKED parameter that would fall back
to a code default rather than an explicit YAML/config value is a **hard error**, not a silent
default. Report the mechanism and include a test demonstrating a run refuses to start under
that condition.

If the launcher emits no per-run resolved-config record, flag that in the diff (past runs can't
be audited for which value they used) — but do NOT build run-logging infrastructure here.

## Task 3 — Phase 1 terrain constants into PARAMETERS.md (C2-2)

Add a Phase 1 / Terrain section to PARAMETERS.md giving each terrain constant one canonical
home: value, lock status, config source. Must include world-dimension constants:
**1 cell = 100 km² (10 km × 10 km), map = 100×100 cells, world = 1,000,000 km².**
This closes the "is the world dimensionless?" class of confusion — one authoritative home.

`LARGE_BODY_CEILING`: record per Task 7 below (0.08, logged §DECISION).

## Task 4 — Single-home consolidation (C4-1)

Each fact gets ONE canonical home; other locations become pointers (not paraphrase — pointer,
to avoid re-introducing drift):
- **mtn_ceiling = 0.317** → canonical home PARAMETERS.md; flag as OPEN re-derivation item
  (§H-TERRAIN-ASYMMETRY). Other two docs reference it.
- **H1(ii) status** → canonical home HYPOTHESES.md (see Task 8 for its wording). Other
  locations reference it.
- **§DECISION-LAKE-BODY-GUARD rationale** → canonical home the decisions register
  (ROADMAP / §DECISION home). ARCHITECTURE references it.

## Task 5 — Snapshot-drift refresh (C5)

- ARTIFACTS.md: refresh stale test count; add absent Phase 1 artifacts (Stage 1b/1c
  diagnostics, sweep outputs, this directive's outputs). Bring current.
- sic_games/CLAUDE.md: remove stale "PARAMETERS.md not yet extracted" text; replace with
  correct pointer (PARAMETERS.md exists and is authoritative).
- Any other C5 item: refresh to current state.

## Task 6 — Tag upgrades (C3-1)

The 6 [INLINE] entries in ARCHITECTURE.md §15.1: upgrade [INLINE] → [VERIFIED] ONLY where
LITERATURE.md actually backs the entry (per CLAUDE.md no-self-upgrading-citations rule).
For any lacking backing, leave [INLINE] and report which.

## Task 7 — Stage 1c guard finalization

The Stage 1c run confirmed the single-body statistic is well-behaved (guard no longer fires at
wK=0.80 where the old exterior guard did). Supervisor decision: the guard is a **pure
single-largest-body ceiling** — NOT conjunctive, no dominance/body-count condition. A single
body large enough to be sea-sized is rejected regardless of how many other lakes surround it
(surrounding ponds do not make a sea not-a-sea).

Set **LARGE_BODY_CEILING = 0.08** (config parameter, not a literal). Update PARAMETERS.md:
LARGE_BODY_CEILING provisional → logged value 0.08.

Log **§DECISION-LAKE-BODY-CEILING** (decisions register): a single connected water body
exceeding 0.08 of map area (≈80,000 km² at locked dimensions, just below Lake Superior's
~82,000 km²) is rejected as functionally an inland sea producing coastal dynamics this
continental arc does not implement. Conservative-side choice: reject below Superior scale, not
above. This is deferral, not exclusion — large-water dynamics committed to §STAGE-GEOSTRUCT.
The body-count / characteristic-size descriptors remain REPORTED context (to let the supervisor
see misfires) but are NOT guard inputs.

Confirm in the diff that the guard rejects on `largest_water_body_fraction > 0.08` and on
nothing else.

## Task 8 — H1(ii) recorded as re-test, not standing result

In HYPOTHESES.md (its canonical home per Task 4), record H1(ii) explicitly as
**pre-registered for re-test on the rebuilt terrain + resource infrastructure — NOT a standing
confirmed result.** The prior Sugarscape-era confirmation does not carry forward as a live
finding; it is superseded pending re-derivation on the new substrate. Remove any wording
elsewhere that asserts H1(ii) as currently confirmed (replace with a pointer to the
HYPOTHESES.md re-test status).

## Task 9 — Dormant-vs-active social-parameter triage

From the Phase 0 run outputs, sort every **social-dynamics locked parameter** into two buckets
by a single objective criterion: **did the mechanic this parameter governs produce events in
the Phase 0 runs?**

- **ACTIVE** (mechanic fired): the parameter was calibrated against real observed behaviour →
  guidepost. Retain locked; mark "confirm on new substrate" (sanity-check, not re-derive).
- **DORMANT** (mechanic never fired — e.g. the Cred-weighted contest / co-location-gated
  mechanics that were inert under the dead-density condition): the locked value was set against
  an inactive mechanic and is a placeholder, not a finding → see Task 10.

Determine firing from run outputs / event logs, not from prose or memory. If a parameter's
firing cannot be determined from the outputs, report it as INDETERMINATE (do not guess) — that
is itself a finding (the runs didn't log enough to tell).

Output: a triage table — parameter, governing mechanic, ACTIVE/DORMANT/INDETERMINATE, evidence
(which output/log shows firing or its absence). This table is a must-be-seen artifact for
supervisor review.

## Task 10 — Provisional declaration, DORMANT bucket only

For every DORMANT parameter from Task 9: mark it **PROVISIONAL — pending recalibration on the
rebuilt substrate** in PARAMETERS.md. Do NOT delete the value (it stays recorded); flag it as
not-live. ACTIVE parameters are untouched (remain locked guideposts). INDETERMINATE parameters
are NOT auto-marked — list them for supervisor decision (STOP-AND-REPORT).

Rationale to log: a parameter calibrated against a mechanic that never fired carries no
evidential weight for its value under activity; terrain is expected to make these mechanics fire
for the first time, so their values must be re-derived once active. This is the disciplined
scope of "retire pre-terrain locks" — suspend the dormant subset, keep the earned guideposts.

## Task 11 — Recalibration-stage forward stub (ROADMAP placeholder, do NOT build)

Add a ROADMAP entry: **§STAGE-RECAL** (DEFERRED, committed). After continental terrain + resource
ecology are built, a pre-registered, gated recalibration stage re-derives the PROVISIONAL
(dormant) parameter set on the new substrate and re-tests superseded hypotheses (incl. H1(ii)).
This stage — not document deliberation — is the adjudication step for pre-terrain locks. It must
be pre-registered (which parameters, calibration target per parameter, acceptance check) before
running; recalibration is NOT open knob-tuning. Document rewrites flow from this stage's results,
not from web search (web supplies calibration *anchors* only). Stub only — do not build now.

---

## Acceptance (directive done when)

1. Tasks 1–8, 10–11 applied; Task 9 triage table produced; STOP-AND-REPORT items reported.
2. Diff summary lists every file changed and, for Tasks 1–2, every parameter reconciled
   (param, old → new, PARAMETERS.md ref).
3. config.py defaults for all five C2-1 params match PARAMETERS.md LOCKED values.
4. Missing-YAML hard-error guard in place + test demonstrating refusal to start on LOCKED-default
   fallback.
5. World-dimension constants have a single canonical home in PARAMETERS.md.
6. Each C4-1 fact has one canonical home; others are pointers.
7. Guard rejects on `largest_water_body_fraction > 0.08` and nothing else; PARAMETERS.md +
   §DECISION-LAKE-BODY-CEILING updated.
8. H1(ii) recorded as re-test (Task 8); no doc asserts it as currently confirmed.
9. Task 9 triage table present with evidence column; DORMANT params marked PROVISIONAL (Task 10);
   INDETERMINATE params listed for supervisor, not auto-marked.
10. §STAGE-RECAL stub in ROADMAP.
11. No model run launched, re-run, or swept (assert: no new run outputs beyond the triage table).

## Explicit non-goals

- No corrective sweep, no re-run of any Stage 5.x / Phase 0 run.
- No new mechanics; no terrain/guard logic beyond setting the ceiling to 0.08.
- No conjunctive guard logic — single-body ceiling only.
- No recalibration executed — §STAGE-RECAL is a stub.
- No run-logging infrastructure build (flag absence if found).
- No paraphrasing of consolidated facts — pointers only.
- No auto-marking of INDETERMINATE parameters — supervisor decides those.
