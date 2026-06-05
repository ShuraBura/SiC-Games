# SiC Games — Stage 6.0a Patch: Recovery-Gate Treatment of Movement

**Patches:** `SiC_Games_Stage6_0a_Substrate_Blueprint.md` v1.0, §7.1 (and a one-line note in §4.1).
**Reason:** §4.1 changes movement in two independent ways — (a) removes the unoccupied filter
(substrate semantics, what the recovery gate is meant to cover), and (b) restricts the candidate
set from the current vision-`v∈{1..6}` perception radius to the von-Neumann r=1 neighbourhood (a
deliberate behavioural change: diffusion, not navigation). The current committed model moves by
argmax over a vision-`v` candidate set, so an r=1 candidate set **cannot** bit-reproduce it, even
under `K_cell=1, κ=0`, neutral hooks. The recovery gate as written (§7.1) demands bit-identity
against the committed model and therefore collides with the r=1 restriction. This patch resolves
the collision.

**Ruling:** Hold the candidate set at the current vision-`v` rule *inside the recovery regime
only*. The recovery gate validates the **substrate** (multi-occupancy, harvest-split, hash→occupant-set
refactor, candidate-set occupancy semantics) by forcing the single-occupancy limit where it must
coincide with the committed model. The r=1 diffusion restriction is a **separate model decision**,
validated behaviourally in §7.2 — never claimed bit-identical. The two regimes use different
candidate-set rules *by design*; this is correct, because they test different things.

---

## Replacement text for §7.1

Replace the existing §7.1 block with the following.

### 7.1 Recovery gate (MANDATORY, blocking) — replaces the usual equivalence gate

Resource-split changes the core harvest rule, so "feature-off = bit-identical" is impossible at
the substrate level. The honest gate is **recovery in the single-occupancy limit**: prove the new
substrate is a correct *generalisation* of the current committed model, by forcing the regime
where it must coincide.

**Scope of this gate.** It validates the **substrate refactor only**: multi-occupancy machinery,
the harvest-split path, the spatial-hash → occupant-set conversion (§2.2 — the highest-risk
silent-regression site), and removal of the unoccupied *filter* from the candidate set. It does
**not** validate the r=1 diffusion restriction (§4.1), which is a deliberate behavioural change
validated separately in §7.2. Do not fold a behavioural change into the correctness baseline.

**Candidate-set rule in the recovery regime.** Hold the candidate set at the **current committed
vision-`v` rule** (the stock cardinal-arms / perception-radius candidate set) for the recovery run
*only*. Removing the unoccupied filter is in scope and must hold under the gate; shrinking the
candidate set to r=1 is **not** — it would make bit-identity against the committed model
impossible for reasons unrelated to the substrate. So: stock candidate-set geometry, unoccupied
filter removed, single occupancy forced.

Force single occupancy via a temporary hard ceiling `K_cell = 1` (the saturation ceiling at its
hard limit — same machinery a saturation penalty would use), with κ=0, move_cost=0, affinity=1,
crowd_response=1, **and candidate set held at vision-`v`**. In this regime:

```
Recovery run: 100×100, locked science N (read & assert), seed=42, C, static world, 500 steps,
              K_cell=1, κ=0, move_cost_flat=0, terrain off,
              candidate set = current vision-v rule (NOT r=1), unoccupied filter removed
→ compare against a reference run from the current committed model, same config.
```

Compare: N(t) exact integer match every step; mean_wealth, gini, mean_cred to 1e-9; births,
deaths exact; final positions exact. **Divergence → halt, report.** (Likely cause: split or
candidate-set occupancy change leaking into the K_cell=1 path, or an RNG-draw-order change from
removing the unoccupied filter — guard so draw order is preserved in the recovery regime.)

Then **lift the ceiling** (`K_cell = ∞`) **and switch the candidate set to the live r=1 von
Neumann rule** for the real multi-occupancy runs below.

**Report requirement (anti-confusion).** State explicitly in the report's recovery-gate section
that the recovery regime uses the vision-`v` candidate set while the live multi-occupancy runs
(§7.2 onward) use r=1, and that this is intentional: the gate validates the substrate, not the
r=1 restriction. This prevents the two-regime difference from later being misread as an
inconsistency.

---

## One-line addition to §4.1

Append to the end of the §4.1 vision-range sanity note:

> **Recovery-gate interaction:** the r=1 candidate set is the *live* rule. The §7.1 recovery gate
> deliberately does **not** use it — it holds the candidate set at the current vision-`v` rule so
> the substrate refactor can be proven bit-identical against the committed model. r=1 is validated
> behaviourally in §7.2, not under the bit-identity gate. See the §7.1 patch.

---

## What this does NOT change

- §7.2 behavioural check is unchanged in spirit: it already runs the live r=1 diffusion model and
  interprets N-trajectory / density / aggregate stats against pre-registration. r=1's validation
  lives here, as plausibility, not bit-identity.
- No change to κ settings, move-cost defaults, neutral hooks, or any other gate.
- The 1e-9 / integer-exact / exact-final-position bar on the substrate is **retained in full** —
  this patch protects it, it does not weaken it.

---

*End of patch — 2026-06-03. Apply to §7.1 and §4.1 of Stage 6.0a Substrate Blueprint v1.0.*
