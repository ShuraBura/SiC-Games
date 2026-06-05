# SiC Games — Repository Reorganization Blueprint

**Status:** DIRECTIVE for Claude Code (CC).
**Authored:** 2026-06-05 (supervisor, in chat).
**Obeys:** `DOCS_CHARTER.md` — the target `docs/` set and boundaries are defined there; this
blueprint only *moves files into* that structure. Where this blueprint and the charter
disagree, the charter wins.
**Prerequisite confirmed by supervisor:** full manual backup exists at
`G:\My Drive\docs\SiC Games\backup 06.05.2026 2.37 pm`. Remote repo exists (empty, private):
`github.com/ShuraBura/SiC-Games`.

---

## 0. Operating rules for this reorg (read first)

- **This is git-based, not raw Drive moves.** Every relocation is `git mv` + commit, so the
  whole reorg is revertible from history. This supersedes any earlier "copy-verify-remove"
  plan that assumed no version control.
- **Drive-sync hazard:** the working folder is a Google Drive Desktop sync target. Before the
  run, supervisor pauses Drive sync (or lets each commit's writes settle before the next).
  This avoids half-synced states and `(1)`-duplicate artifacts.
- **CC never hard-deletes.** Litter is *moved to `archive/`*, never `rm`-ed. The only
  "removal" is `git mv` (which preserves history) and, for the duplicate-doc merges, the
  superseded copy is moved to `archive/superseded/` with a note — not deleted.
- **Destructive/irreversible steps are gated.** Any step marked **[GATE]** stops and waits
  for explicit supervisor "go" in chat before proceeding. CC does not self-authorize past a
  gate.
- **Surface, don't guess.** Where two files claim to be the same doc, CC produces a diff and
  shows the supervisor the delta; the supervisor decides the authoritative content. CC does
  not auto-pick a winner.

---

## 1. Step 0 — establish the git baseline (do this before any move)

1. Initialise the working folder as a git repo (if not already) and set the remote to
   `github.com/ShuraBura/SiC-Games`.
2. Add a `.gitignore` covering: `*.bak*`, `.pytest_cache/`, `__pycache__/`, large run
   binaries if any (confirm with supervisor what under `outputs/` should be tracked vs
   ignored — default: track reports, ignore raw parquet/cache).
3. **Commit the current state AS-IS** — the messy tree, unmodified — as commit #1
   (`"baseline: pre-reorg state"`) and push. **This commit is the canonical restore point;
   every later move is visible as a diff against it.**
   - *Supervisor decision pending:* commit the **raw mess** first (recommended — truest
     baseline, cleanup visible in history) **or** sweep obvious litter into `archive/` first
     and commit a tidied baseline. Default = raw mess first.
4. **[GATE]** Confirm commit #1 is pushed and the GitHub repo shows the tree before any move.

> With commit #1 in place, the manual Drive backup + git history are two independent restore
> paths. CC has full latitude from here.

---

## 2. Target structure (per charter)

```
SiC-Games/                       ← repo root
├── README.md                    ← NEW: one screen; points to docs/INDEX.md
├── CLAUDE.md                    ← single master (see §5); supervisor places at code root
├── docs/                        ← the eleven charter homes, FLAT
│   ├── INDEX.md  ROADMAP.md  ARCHITECTURE.md  MECHANISMS.md  PARAMETERS.md
│   ├── TARGETS.md  HYPOTHESES.md  RESULTS.md  LITERATURE.md  ARTIFACTS.md  DEAD_ENDS.md
│   └── DOCS_CHARTER.md
├── blueprints/                  ← all work-commissioning docs, by stage, type-in-filename
│   ├── stage1/ … stage6/        ← Stage blueprints + their patches/amendments/diagnostics
│   ├── perf/                    ← Perf_Audit, Perf_Opt, Benchmark_Runtime, Stage6_0a_perf, JT_Fix_Benchmark
│   ├── owe/                     ← OWE1_AbsoluteScale, OWE1_1_FollowUp
│   ├── resource-ecology/        ← ResourceEcology_DesignDoc, Resource_Concept_Map, R0_* 
│   └── meta/                    ← doc-management directives (MODEL_SPEC_Extraction, ROADMAP_Table_Repair, ROADMAP_Update_Directive)
├── handoffs/                    ← chat_handoff, claude_code_handoff, Handoff_2026-06-02, STANDING_HANDOFF_2026-05-31, project_instructions
├── sic_games/                   ← CODE — internals UNTOUCHED (src tests configs outputs notebooks scripts)
├── origin/                      ← Carbon-Prototype V1.3 founding spec (both copies → confirm which is canonical)
└── archive/                     ← .bak files, v5.1.x backup folders, superseded/ (duplicate-doc losers)
```

**Note on blueprint grouping:** by-stage with the type kept in the filename (the hybrid).
Rationale: matches how the docs cross-reference ("see Stage 4.4 §1") and how work is done;
avoids the per-file "is this a patch or a blueprint?" judgment that by-type forces.
*Supervisor was deliberating by-stage vs by-type — confirm before §3 runs.* **[GATE]**

**Reports are NOT moved.** They stay at `sic_games/outputs/<stage>/…`; ARTIFACTS.md indexes
into them. Any `[CHAT-ONLY]` reports get committed into their stage's output subfolder.

---

## 3. Move map (git mv, after the §2 grouping gate)

CC executes as a sequence of `git mv` commits, one logical group per commit (so history is
legible):

1. **Create `docs/`** and `git mv` the eleven homes in from their three current locations:
   - from `Model/`: ARTIFACTS, INDEX, MODEL_SPEC (→ to be split, §6), and HYPOTHESES
     (→ merge, §4).
   - from project root (loose): ROADMAP, LITERATURE, and the loose HYPOTHESES (→ merge, §4).
   - Add `DOCS_CHARTER.md` (supervisor-provided) to `docs/`.
2. **Create `blueprints/`** with the subfolders in §2 and `git mv` every
   `SiC_Games_Stage*`, `*_Blueprint`, `*_Directive`, `*_Patch`, `*_Amendment*`,
   `*_Diagnostic`, `*_Feasibility`, `*_Benchmark`, `Perf_*`, `OWE*`, `R0_*`,
   `ResourceEcology_*`, `Resource_Concept_Map` into the matching subfolder. Keep filenames
   (including the `SiC_Games_` prefix) unchanged in this pass — renaming risks breaking
   internal cross-references and is a separate later pass.
3. **Create `handoffs/`** and `git mv` the handoff/instruction files in.
4. **Create `origin/`** and `git mv` the Carbon-Prototype V1.3 spec(s) in. There appear to
   be two copies (different icons → likely a Doc + an export); **diff/confirm which is
   canonical**, the other → `archive/superseded/`.
5. **Create `archive/`** and `git mv` the litter in: `ROADMAP.md.bak_pre_tablefix`,
   `MODEL_SPEC.md.bak_pre_fullextract`, and the `Model/v5.1.1_pre_sicred_redesign`,
   `v5.1.2_pre_cultural`, `v5.1_2026-05-28_0637` folders.
6. Commit + push after each group.

---

## 4. The HYPOTHESES triage (NOT a union-merge, and NOT a filename dedup) **[GATE]**

The two `HYPOTHESES.md` files have **diverged** — each holds entries the other lacks:
- One has the H1(ii) back-reference + **H-EMERGE-1** (emergent group structure).
- The other has H1(ii) + **H-ORTHOGONALITY, H-instinct-debt, H_cc, H-SUBSTRATE-6.0a**.

**Supervisor decision (2026-06-05): the entries are TRIAGED to their correct charter homes,
not piled into one file.** The earlier "union" plan is superseded. Most of the current
entries are not live pre-registrations — they are resolved findings or generative ideas with
no pending run — and parking those in an active "what we predict" file is the HARKing smell
this whole exercise is meant to remove. The test for staying in HYPOTHESES: **a pending run
could prove the entry wrong.** Anything that fails that test routes elsewhere.

The care about not silently dropping H-EMERGE-1 still holds — but the destination is a home,
not deletion. Required procedure:

1. CC produces a side-by-side of the two files and lists every unique entry per side (so
   nothing is lost track of before routing).
2. **Route each entry to its charter home per the triage table below.** Moves into RESULTS /
   TARGETS / DEAD_ENDS are *content relocations*, recorded append-only in the destination.

| Entry | Destination | Action |
|---|---|---|
| **H1(ii)** — C/Si resilience (resolved, inverted, 5/5 seeds) | **RESULTS.md** | State as established finding, cite the Stage 5 report. Note "originally registered as H1(ii); resolved." |
| **H-EMERGE-1** — emergent group structure | **HYPOTHESES.md (KEEP)** | Live: full test spec, terrain stage pending, falsifiable. Carry verbatim. |
| **H-SUBSTRATE-6.0a** — substrate viability | **HYPOTHESES.md (KEEP)** | Live: resolves against the incoming 6.0a report. Carry verbatim. |
| **H_cc** — carry-discount counter-cyclical recovery | **KEEP iff the multi-seed A=0.9 run is still planned; else RESULTS.md** (supervisor confirms) | If kept: live pending run. If not: move the single-seed "partially supported" result to RESULTS. |
| **H-ORTHOGONALITY** — home-range decomposition | **TARGETS.md** + one line in **DEAD_ENDS.md** | No scheduled run; near-implied by the C2 design. Deprioritized, not deleted. |
| **H-instinct-debt** — exploration energy cost | **TARGETS.md** | Contingent on OWE-13 being built and orthogonality holding; no run coming. Graduates later. |

3. **H1(ii) live remnant** — *if* OWE-14 (inversion re-confirmation at the recalibrated
   100×100 scale) is still planned, register ONE narrow new pre-reg in HYPOTHESES: "inversion
   replicates at calibrated 100×100, ≥3 seeds." Supervisor confirms whether OWE-14 is live.
4. The two H1(ii) statements differ in wording ("both seeds, t≈1500" vs "5/5 seeds,
   INVERTED"). CC flags the conflict; **supervisor reconciles the text** for the RESULTS entry
   — CC does not pick.
5. Both source `HYPOTHESES.md` files → `archive/superseded/HYPOTHESES_<source>_2026-06-05.md`
   after routing, with a one-line note pointing at where each entry went.
6. **[GATE]** Supervisor approves the triage routing (and the two confirmations: H_cc run
   status, OWE-14 status) before the source copies are archived. CC does not self-route the
   two conditional entries.

> Seeding note: TARGETS.md is stood up by the supervisor-provided TARGETS seed (orthogonality,
> instinct-debt, and the new microscale-cycles target). CC routes H-ORTHOGONALITY and
> H-instinct-debt *into* that seed rather than creating fresh stubs.

---

## 5. The CLAUDE.md reconciliation **[GATE]**

Two copies exist (project-root loose, and `sic_games/CLAUDE.md`); they almost certainly
differ (one predates the other). Supervisor's decision: **one master, placed at the code
root** (`sic_games/CLAUDE.md`), where CC auto-loads it from its working directory.
1. CC diffs the two copies and shows the supervisor the delta.
2. **Supervisor approves the merged master content** (location is settled; content is not).
3. Master master lives at `sic_games/CLAUDE.md`; the other copy → `archive/superseded/`.
4. The master carries the charter's update triggers (§2) as report-standards and **points
   into `docs/`** (e.g. "on a parameter lock, update `docs/PARAMETERS.md`"). It restates no
   doc content — pointers only.

---

## 6. The MODEL_SPEC split (per charter §2.1) — *separate follow-up, not this reorg*

Splitting `MODEL_SPEC.md` → `ARCHITECTURE.md` + `MECHANISMS.md`, standing up the new
`TARGETS.md`, and extracting `PARAMETERS.md` from the ROADMAP table are **content** work, not
file moves. They are their own `blueprints/meta/` directives, authored in chat after this
structural reorg lands. For *this* blueprint, `MODEL_SPEC.md` moves into `docs/` intact; the
split happens next.

---

## 7. Final fix-up + verification

1. **Rewrite `docs/INDEX.md`** to route to the new homes at their new paths (and to note
   ARCHITECTURE/MECHANISMS/TARGETS/PARAMETERS as the post-split targets, marked pending until
   §6 runs).
2. **Update `CLAUDE.md`** path references and triggers to the new layout.
3. **Grep the whole tree for stale path references** (cross-links between docs/blueprints
   that named old locations) and fix or flag them.
4. **Write `README.md`** — one screen: what the project is, how to run, "documentation:
   start at `docs/INDEX.md`."
5. **Produce a reconciliation report** (→ ARTIFACTS.md): what moved where, every duplicate
   resolved and how, the archived litter list, and any stale references found. 
6. **[GATE]** Supervisor reviews the archived-litter list and green-lights it (the litter
   stays in `archive/` regardless; this gate is just the record that supervisor saw it).
7. Final commit + push; confirm GitHub tree matches the §2 target.

---

## 8. Out of scope for this blueprint (named so they're not silently swept in)

- Renaming files to strip the `SiC_Games_` prefix (later pass; rename-risk to cross-links).
- The MODEL_SPEC split / PARAMETERS extraction (§6; separate `meta/` directives). **Note:**
  TARGETS.md is now *partially seeded by this reorg* via the §4 triage (orthogonality,
  instinct-debt routed in, plus the supervisor's microscale-cycles seed); its full content
  build still belongs to the `meta/` pass.
- The §7.1 recovery-gate patch, the stale "Stage 6 = statistics" ROADMAP renumbering, and
  applying the H-SUBSTRATE-6.0a entry — supervisor-owned content edits, tracked separately.
- Reading/landing the Stage 6.0a report — done after the homes are settled.

---

*End of Reorganization Blueprint — 2026-06-05. Gates at §1.4, §2 (grouping), §4 (triage +
H_cc / OWE-14 confirmations), §5, §7.6.*
