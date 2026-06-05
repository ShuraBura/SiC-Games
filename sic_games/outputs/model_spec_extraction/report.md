# MODEL_SPEC Full Extraction Report

**Date:** 2026-05-29  
**Blueprint:** SiC_Games_MODEL_SPEC_Extraction_Blueprint.md  
**Backup:** `MODEL_SPEC.md.bak_pre_fullextract`  
**Status:** Delivered for supervisor review. The SPEC does not become authoritative until
the citations worklist (§C) is cleared.

---

## §A Stage → source-document map

| Stage / mechanic | Primary blueprint(s) | Report(s) |
|---|---|---|
| Stage 1 — world substrate, greedy Si | SiC_Games_Stage1_Blueprint.md | outputs/stage1_baseline_seed42/ |
| Stage 2 — C decision, Cred, JT | SiC_Games_Stage2_Blueprint.md | outputs/stage2_carbon_seed42/ |
| Stage 2.1 — mode switch (wealth velocity) | SiC_Games_Stage2_Patch_ModeSwitch.md | outputs/stage2_carbon_patched_seed42/ |
| Stage 2.2 — baseline fix, κ sweep | SiC_Games_Stage2.2_Directive.md | — |
| Stage 3 — BoundedRationalSi, f_C | SiC_Games_Stage3_Blueprint.md | outputs/stage3_si_bounded_seed42/ |
| Stage 3.1 — f_C sweep | SiC_Games_Stage3.1_Directive.md | — |
| Stage 3.2 — status amplification β | SiC_Games_Stage3.2_Blueprint.md | outputs/stage32_beta10_seed42/ |
| Stage 3.3 — trait vector H_i, biparental repro, Si Cred skeleton | SiC_Games_Stage3.3_Blueprint.md | outputs/stage3.3_seed42/ |
| Stage 3.4 — κ×α 2D scan, σ_Si=1.238 | SiC_Games_Stage3.4_Directive.md | outputs/stage34_k10_a20_seed42/ |
| Stage 4 — seasonal oscillation | SiC_Games_Stage4_Blueprint.md | outputs/stage4_c_null_seed42/ |
| Stage 4.1a — variable population, birth-death | SiC_Games_Stage4.1a_Blueprint.md | outputs/stage41a_*/ |
| Stage 4.1b — η(a) ramp, age init | SiC_Games_Stage4.1b_Blueprint.md, SiC_Games_Stage4.1b_Patch.md | — |
| Stage 4.1c — proximity support pool | SiC_Games_Stage4.1c_Blueprint.md, SiC_Games_Stage4_1c_Patch.md | outputs/stage41c_*/ |
| Stage 4.2 — τ_pool, γ, BUG-003, seasonal sweep | SiC_Games_Stage4_2_Blueprint.md | outputs/stage42_seed42/ |
| Stage 4.3 — Si β, dormancy, pool carry-over | SiC_Games_Stage4_3_Blueprint.md | outputs/stage43_seed42/ |
| Stage 4.4 — k_grid=4, β_Si=5, λ=0.1, ψ redesign | SiC_Games_Stage4_4_Blueprint.md + Patch + Amendments | outputs/stage44_seed42/ |
| Stage 4.4 Diag — C bistability | SiC_Games_Stage4_4_Diagnostic.md | outputs/stage44_diag_seed42/ |
| Stage 4.5 — carrying-cost, H_cc, T* | SiC_Games_Stage4_5_Blueprint.md, SiC_Games_Stage4_5_Patch.md | outputs/stage45_seed42/ |
| Stage 5 — multi-seed, A=0.9, Si Cred | SiC_Games_Stage5_Blueprint.md | outputs/stage5/report_stage5.html |
| Stage 5.1 — Si Cred near-dormancy redesign | SiC_Games_Stage5_1_Blueprint.md | outputs/stage51_sicred_redesign/report.html |
| Stage 5.2 — c2 defection, Deffuant, σ_inherit | SiC_Games_Stage5_2_Blueprint.md | outputs/stage52_cultural/report.html |
| Perf/JT fix | SiC_Games_JT_Fix_Benchmark.md, SiC_Games_Perf_Audit.md, SiC_Games_Perf_Opt_Blueprint.md | outputs/perf_audit/, outputs/perf_opt/ |

**Gaps (mechanics referenced in ROADMAP with no findable dedicated blueprint):**
- Wealth inheritance λ activation: referenced in Stage 4.4 as "0.1 activated" but no standalone blueprint; Stage 4.1a defines λ=0 default. Source: ROADMAP entry and Stage 4.4 blueprint mentions it as active.
- ψ Beta(2,2) redesign: described in Stage 4.4 blueprint §ψ redesign; no standalone document.
- p_max_C_bare / p_max_C_final tuning: found in Stage 4.5 blueprint; documented as found.

---

## §B Section-by-section coverage summary

| SPEC § | What was added | Primary source(s) |
|---|---|---|
| §0 | Verbatim from pilot | Pilot v0.1 |
| §1 | Extended: ψ init dist updated to Beta(2,2) (Stage 4.4); C/Si Cred rows; wealth velocity; dormancy fields; world state variables | Stage 1, 2, 4.3, 4.4, 5/5.1 |
| §2 | Verbatim from pilot; σ_inherit value updated to 0.10 | Pilot; Stage 5.2 |
| §3 | New. Decision/σ economy full table + narrative | Stage 2, 2.1, 3.2, 3.4, 5.1 |
| §4 | New. Joint task + Matthew partition + c2 defection hook | Stage 2, 3.4, 5.2 |
| §5 | New. C Cred and Si Cred economies, BUG-003 | Stage 2, 3, 3.2, 4.1c, 4.2, 5, 5.1 |
| §6 | New. Pool L1–L2–L3, carry-over, τ_pool tension | Stage 4.1c, 4.2, 4.3 |
| §7 | Pilot §3 renumbered; extended with birth-death, η(a), carrying-cost | Stage 3.3, 4.1a, 4.1b, 4.2, 4.5 |
| §8 | New. WorldPerturbation, SeasonalOscillation, T* analysis | Stage 4, 4.2, 4.5 |
| §9 | New. World substrate, k_grid rescale rationale | Stage 1, 4.4 |
| §10 | Verbatim from pilot | Pilot v0.1 |
| §11 | New. Per-step metrics, R6 terminal-state fields, standing rules | ROADMAP R1–R12; Stage 5.2 |
| §12 | Pilot §5 renumbered verbatim; no new entries (no documented rationale found for new mechanics beyond what blueprints state) | Pilot |
| §13 | Pilot §5.2 renumbered verbatim | Pilot |
| §14 | New (pointer only; no values) | Blueprint §4 |
| §15 | Pilot §6 extended with discrepancies, new gaps, Stage 5.2 open items | Pilot; this extraction |

---

## §C Citations-to-verify worklist

All items that require supervisor clearance before any tag can be upgraded to `[VERIFIED]`.
**A long list here is the expected and correct outcome** — LITERATURE.md covers only Stage 5 Si Cred.

### Already `[VERIFIED]` (in LITERATURE.md — no action required)

| Citation | SPEC section | LITERATURE.md location |
|---|---|---|
| Epstein & Axtell (1996) — Sugarscape substrate | §1.2, §9 | Stage 5 Task 3 ("provides the resource-harvesting substrate") |
| Axelrod (1984) — Evolution of Cooperation | §5.3 | Stage 5 Task 3 ("self-referential performance-feedback loop") |
| Brock & Hommes (1997) — Boltzmann decision rule | §3.2 | Stage 5 Task 3 ("standard in the ABM literature") |
| Nowak & May (1992) — spatial prisoner's dilemma | §5.3 (rejected) | Stage 5 Task 3 ("rejected for Si Cred") |

### `[INLINE]` — cited in blueprints, not yet in LITERATURE.md

| Claim as stated in SPEC | SPEC section | Asserted source | Blueprint citing it | Current tag |
|---|---|---|---|---|
| Bounded-confidence opinion dynamics (confidence bound ε, convergence μ) | §3.3 | Deffuant et al. (2000), *Mixing beliefs among interacting agents* | Stage 3.3 §0; Stage 5.2 §3 | `[INLINE]` |
| HK alternative bounded-confidence form | §3.3 | Hegselmann & Krause (2002) | Stage 3.3 §0 | `[INLINE]` |
| Prestige bias in cultural transmission; dual inheritance | §3.3, §2.2 | Boyd & Richerson (1985), ch. 5 | Stage 3.3 §0; ROADMAP | `[INLINE]` |
| Elite overproduction → secular cycles; Turchin cliodynamics | §7.2 | Turchin (2003) | ROADMAP; Stage 4.1a North Star | `[INLINE]` |
| Sugarscape cultural transmission chapter specifically | §1.2 | Epstein & Axtell (1996), ch. 3 | Stage 3.3 §0 | `[INLINE]` (substrate `[VERIFIED]`; cultural chapter not confirmed) |
| Cultural diversity and noise non-monotonic effect | §1.2 | Axelrod (1997); Klemm et al. (2003) | Stage 1 §1.4 | `[INLINE]` |
| Age-efficiency ramp; Cobb-Douglas embodied capital | §7.2 | Gurven & Kaplan (2006), *Longevity Among Hunter-Gatherers* | Stage 4.1b §1.2 | `[INLINE]` |
| Si energy budget: neuromorphic silicon ~200–500J/decision | §9.2 | Davies et al. (2018), Loihi paper | Stage 4.3 §1.1 | `[INLINE]` |
| Evolutionary game theory framing (c2 defection, ESS) | §4.2 | No paper cited explicitly | Stage 5.2 North Star | `[INLINE]` (general framing only; no specific paper in blueprint) |

### `[UNVERIFIED]` — Claude's attribution, not found in any blueprint

| Claim as stated in SPEC | SPEC section | Asserted source | Current tag |
|---|---|---|---|
| Dual inheritance theory (cultural vs genetic channels) | §2.2 | Richerson & Boyd (2005), *Not by Genes Alone* | `[UNVERIFIED]` |
| Price-equation selection decomposition | §10 | Price (1970, 1972); Frank (1995/1997/2012) | `[UNVERIFIED]` |
| ODD protocol (this document's frame) | Header | Grimm et al. (2006, 2010, 2020) | `[UNVERIFIED]` |
| Matthew Effect (cumulative advantage in science) | §4.2 | Merton (1968) | `[UNVERIFIED]` |

---

## §D Discrepancies

| ID | Discrepancy | Files | Action |
|---|---|---|---|
| D1 | τ_trickle: CLAUDE.md says 0.05 (Stage 4.3 original), ROADMAP rationale says "raised to 0.3." Stage 5+ configs confirm 0.3. CLAUDE.md is stale for this parameter. | CLAUDE.md, ROADMAP.md, Stage 5 configs | Flagged; not fixed. CLAUDE.md τ_trickle row should be updated to 0.3 in a future cleanup pass. |
| D2 | p_fission_Si: CLAUDE.md says 0.28 (Stage 4.3 lock). ROADMAP shows 0.065 for Stage 4.4+ (β=5, k=4). Stage 5+ configs used 0.065. CLAUDE.md not updated at Stage 4.4. | CLAUDE.md, ROADMAP.md | Flagged; not fixed. Operative value for Stage 5+ is 0.065. |
| D3 | No discrepancy found for σ_inherit; CLAUDE.md correctly shows 0.10 at Stage 5.2. | — | Clean. |
| D4 | BUG-003 documented: all Stage 4.1c parquets have cred_pool_contribution=0.0. Pool Cred-scaling metrics from Stage 4.1c are invalid. Already in ROADMAP bug history and §5.3 of this SPEC. | Stage 4.1c parquets | Documented; data cannot be retroactively corrected. |

---

## §E Classification calls

**C2 mechanics (civilization-dependent signal or meaning — the dangerous category):**

| Mechanism | Classification | Justification |
|---|---|---|
| σ / decision noise | **C2** | Same softmax form; σ driven by JT-dominance Cred (C) vs near-dormancy reputation (Si). Wiring Si to C's Cred signal would produce a status-seeking individualist. |
| C Cred 𝒞_i | **C2** | Accumulates via joint-task Matthew partition (C); completely absent for Si. Not just a parameter=0 situation — Si has a *different* Cred economy (si_cred). |
| Si Cred si_cred_i | **C2** | Near-dormancy survival signal (Si); no equivalent for C. Binary accumulation from stress, not dominance. |
| ψ proximity preference | **C2** | C: proximity-to-agents (c_proximity signal). Si: proximity-to-foraging-spots (unimplemented signal). Same trait slot, different environmental referent. |
| Pool contribution (L2) | **C2** | C: Cred-scaled (τ_cred·tanh(𝒞/C*)); Si: flat τ_pool only. Same pool machinery, different contribution function. |
| Utility function | **C2** | C: U = w_R·ΔR + w_C·ΔCred; Si: U = ΔR only. Cred-seeking term is C-specific. |
| Deffuant cred_weight | **C2 (potential)** | C uses relative Cred weight; Si (when activated) specified as "unweighted egalitarian" — but Si's Cred is a different signal anyway. Flagged for resolution when Si Deffuant is activated. |

**C3 mechanics:**

| Mechanism | Classification | Justification |
|---|---|---|
| HiveMind coordinator | **C3 seam** | Decision *locus* shifts from individual to collective — not a parameter on the individual-level mechanism. Correctly isolated behind coordinator interface. |

**C1 close calls (confirmed C1):**

| Mechanism | Classification | Note |
|---|---|---|
| Parent count (2 vs 1) | **C1** | Same reproduction machinery; number of parents is a parameter. |
| Birth rule (DTM vs fission) | **C1** | Same P(birth) framework; wealth threshold vs wealth-dependent DTM are both wealth-gated functions. |
| η(a) ramp | **C1** | C: piecewise ramp. Si: η=1.0 always (η_min=1.0 for Si). Parameter difference on shared cost computation. |

---

## §F OPEN-item confirmation

Each contested item from blueprint §2.3, confirmed present with OPEN/PROPOSED/pinned status in v0.2:

| Item | Status in SPEC | Location |
|---|---|---|
| §5.1-A cultural/physical dual-inheritance split | **PROPOSED, not implemented** | §2.2, §12.1-A |
| §5.1-D σ_inherit calibration target = c1/c2, not ψ | **OPEN/under review; corrective directive pending** | §7.2, §12.1-D, §15.3 |
| §2.3 ψ's channel (cultural vs physical) | **OPEN** | §2.3, §15.3 item 1 |
| Physical-channel mixing rule | **OPEN** | §2.2, §15.3 item 2 |
| Asabiyyah locus | **OPEN** | §12.1-C, §15.3 item 3 |
| Physical-inheritance control design | **OPEN** | §12.1-A, §15.3 item 4 |
| C** = C* pinning (ROADMAP Q11) | **Pinned/deferred** | §3.1 (C** = C* row), §15.3 item 6 |

All seven OPEN/PROPOSED items preserved. None resolved, dropped, or quietly settled. ✓

---

## §G Faithfulness-gate results

### G.1 Pilot content preserved

Pilot sections §0 (How to read), §2.1 (Current inheritance state), §2.2 (Dual-inheritance narrative), §2.3 (ψ channel), §3.1–§3.3 (Reproduction), §4 (Selection measurement), §5.1-A through §5.1-E (Design-log entries), and §5.2 (Architecture seams) are all preserved verbatim in the v0.2 SPEC under their renumbered section headings (§0, §2.1, §2.2, §2.3, §7 pilot content, §10, §12.1-A through §12.1-E, §13).

Section numbers renumbered: pilot §1→§1, §2→§2, §3→§7, §4→§10, §5→§12, §5.2→§13, §6→§15. Content unchanged.

One update to pilot content (correct per this extraction): §1.1 ψ init distribution updated from "N(0.5, 0.2²)" to "Beta(2,2) (Stage 4.4+); prior: N(0.5, 0.2²)" — this is a factual correction reflecting the Stage 4.4 ψ redesign, not a content invention. σ_inherit in §2.1 updated from 0.05 to 0.10 reflecting Stage 5.2 lock.

### G.2 `[VERIFIED]` tag audit

All four `[VERIFIED]` tags in the output correspond to LITERATURE.md entries:

| VERIFIED claim | SPEC location | LITERATURE.md entry |
|---|---|---|
| Epstein & Axtell (1996) substrate | §1.2, §9 | Stage 5 Task 3, "Epstein & Axtell (1996)" section |
| Axelrod (1984) performance-feedback loop | §5.3 | Stage 5 Task 3, "Axelrod (1984)" section |
| Brock & Hommes (1997) Boltzmann form | §3.2 | Stage 5 Task 3, "Bounded-rationality models..." section |
| Nowak & May (1992) spatial PD | §5.3 | Stage 5 Task 3, "Nowak & May (1992)" section |

No `[VERIFIED]` tag appears without a LITERATURE.md backing entry. ✓

### G.3 OPEN-item presence

All seven contested items from blueprint §2.3 confirmed present with correct status (see §F above). ✓

---

*End of extraction report — 2026-05-29.*
