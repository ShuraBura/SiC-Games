# PENDING_CC — chat-side delta buffer (append-only, NON-AUTHORITATIVE)

> Append-only. Each entry is `[PENDING]` until CC drains it into its home-target (then `[DRAINED <date>]`, struck-through, never deleted). On conflict with a home, CC tags `[CONFLICT]` and surfaces to supervisor — never resolves unilaterally. The eleven `docs/` homes are the sole authority.

Format: `- [PENDING] <date> | <type> | <statement> | home-target: <doc>`
type ∈ {decision, deferral, hypothesis-sketch, sequencing, correction, flag}

## Entries

- [PENDING] 2026-06-14 | correction | σ_inherit (locked 0.10, Stage 5.2) may have RUN at 0.05 through Stage 5.2-era sims via config mismatch — i.e. locked value possibly UNEXERCISED. UNCONFIRMED. CC: check Stage 5.2-era YAML; log value found + UNEXERCISED-or-false verdict. | home-target: PARAMETERS §7
- [PENDING] 2026-06-14 | flag | The inbound 2026-06-14 chat handoff (static-game blueprint / seasonal-forage next / p_female / kcal energy-balance / DEFERRED_MECHANICS.md / 430 tests / "CC returned green") does NOT match committed repo state (frontier = Phase 1 Stage 1c, 2026-06-13). Must not be inherited as fact by future chats. | home-target: none (flag only)
- [PENDING] 2026-06-14 | deferral | "DORMANT–UNWIRED / build-or-cut" framing for τ_parent=0.0 and k_pool_cap=0.0 is a chat-side idea, uncommitted. Register for supervisor decision at recal-time; do not action. | home-target: PARAMETERS §6 / ROADMAP
- [PENDING] 2026-06-14 | decision | Context-sync system adopted: derived fact-file + this buffer live in non-canonical context/, NOT as charter homes (DOCS_CHARTER §1.3 closed set preserved). | home-target: docs/INDEX.md (pointer) + CLAUDE.md (rules 14/15)
