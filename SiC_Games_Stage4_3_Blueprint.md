# SiC Games — Stage 4.3 Blueprint: Differential Metabolism + Si Dormancy + Pool Carry-Over + Revised Sweep

**Version:** 1.1 (revised to replace Si starvation death with dormancy mechanic)
**Intended consumer:** Claude Code (and the human supervisor).
**Scope:** Stage 4.3 only. Three model fixes followed by the first valid H1(ii) test.
**Prerequisite:** Stage 4.2 complete. Locked: τ_pool=0.05, γ=0.2 (C only), γ=0 (Si).
**ROADMAP:** `G:\My Drive\docs\SiC Games\ROADMAP.md`

---

## 0. North Star (read first, every session)

**Stage 4.3 goal:** produce the first scientifically valid H1(ii) test.

Stage 4.2's H1(ii) assessment is invalid for two reasons:
1. **Equal metabolism.** C and Si ran on identical energy budgets. Si agents
   are silicon — empirically 5–60× more energy-hungry per decision than a
   biological brain (20W human brain vs ~1,200–6,000J per AI inference;
   Patterson et al. 2021, TechXplore 2025). Running Si at C's metabolism
   understates Si's energetic burden and artificially inflates Si resilience.
2. **Pool resets every step.** The no-carry-over pool cannot buffer multi-step
   troughs. This structurally disadvantages C (biparental, Allee-sensitive)
   under long-period seasonality, independent of any genuine C/Si difference.

Both must be corrected before H1(ii) means anything.

**Three model changes, in strict order:**
1. Introduce Si differential metabolism (β=5) and Si dormancy (replaces
   starvation death for Si agents entirely).
2. Add pool carry-over fraction ρ with pool cap.
3. Re-establish null controls and lock new P_max/P_fission values.

**Then science:**
4. T* search — find the critical seasonal period where C transitions from
   stable to collapsing.
5. Revised seasonal sweep — first valid H1(ii) assessment.
6. ψ_i death event logging — per-agent snapshots deferred from Stage 4.2.

**What Stage 4.3 is not.** No λ (wealth inheritance) — deferred to Stage 4.4.
No Si social energy sharing (reactivation by neighbor donation) — deferred to
Stage 5+ (requires its own blueprint). No τ_pool or β parameter sweeps —
deferred to Stage 5.x.

**Stage 4.2 H1(ii) result status:** treated as an artifact of equal metabolism
and absent carry-over. Not carried forward as a scientific result.
Stage 4.3 supersedes it.

---

## 1. Task 1 — Si differential metabolism + dormancy mechanic

### 1.1 Metabolism rationale

Human brain: ~20W continuous (~100J per ~5s decision).
Current AI inference: ~1,200–6,000J per response (OpenAI 2024; TechXplore 2025).
Neuromorphic silicon: ~200–500J (Davies et al. 2018, Loihi).
Empirical ratio: **5–60× more energy per decision** for silicon vs biological.

Default β = 5 (conservative; represents efficient near-future silicon).
Sweep {2, 5, 10} deferred to Stage 5.x.

```yaml
metabolism:
  beta_metabolism: 5.0   # Si only. C metabolism unchanged.
```

**CostModel hook:** the Stage 1 blueprint (§5.3) pre-built this abstraction
for exactly this purpose. Use it — do not hardcode the multiplier in BaseAgent.
Verify CostModel is active before implementing.

### 1.2 Si dormancy mechanic (replaces starvation death for Si)

**Design rationale:** Si agents do not starve — they suspend. A silicon system
without energy does not die; it enters a low-power dormant state. Death occurs
only when the environment cannot provide enough energy to reactivate within a
maximum dormancy window.

This is a Si-only mechanic. C agents continue to die from starvation as before.

**Dormancy trigger:** Si agent enters dormancy when:
$$w_i < k_{\text{dormant}} \times m_i$$

where $k_{\text{dormant}} = 1.0$ (agent cannot cover one step of metabolism).
Default: agent is flagged dormant instead of dying.

**Dormant state behavior:**
- No movement.
- No active harvesting.
- No pool contribution or pool draw.
- No reproduction.
- **Passive trickle absorption:** agent absorbs sugar from its current cell
  at rate $\tau_{\text{trickle}} \times \text{sugar\_at\_cell}$ per step.
  Default $\tau_{\text{trickle}} = 0.05$ (5% of what an active agent would
  harvest from that cell). This represents minimal maintenance power draw —
  solar panel trickle, residual field energy.
- Dormant agent does not consume cell sugar competitively (trickle draw is
  passive and does not trigger the cell's harvest/growback cycle).

**Reactivation:** dormant agent reactivates when:
$$w_i \geq k_{\text{reactivate}} \times m_i$$

Default $k_{\text{reactivate}} = 3.0$ (agent has 3 steps of metabolic reserve
before resuming active behavior).

**Permanent death:** if agent has been dormant for $> T_{\text{dormant\_max}}$
steps without reactivating, the agent dies permanently.
Default $T_{\text{dormant\_max}} = 50$ steps.

**Rationale for T_dormant_max:** a Si agent stranded on a permanently depleted
cell with zero trickle income cannot recover regardless of waiting. 50 steps
is long enough to survive a seasonal trough (trough duration ≈ T/2; at T=100,
trough ≈ 50 steps) but not indefinite.

New config parameters (Si configs only):
```yaml
dormancy:
  enabled: true               # Si only; false for C (C uses starvation death)
  k_dormant: 1.0              # wealth threshold for entering dormancy (× metabolism)
  tau_trickle: 0.05           # passive absorption rate while dormant
  k_reactivate: 3.0           # wealth threshold for reactivation (× metabolism)
  t_dormant_max: 50           # max dormancy steps before permanent death
```

### 1.3 N counting with dormancy

Two population counts tracked per step for Si:

| Metric | Definition |
|---|---|
| `n_total_si` | All Si agents (active + dormant) |
| `n_active_si` | Si agents in active (non-dormant) state |
| `n_dormant_si` | Si agents currently dormant |

**N gate for Si null controls uses `n_active_si`.** A Si population where most
agents are dormant is not "surviving" in the same sense as C. The [150,400]
gate applies to active agents only.

For H1(ii) comparison plots: show both n_total_si and n_active_si as separate
series. Use n_active_si for survival assessment.

### 1.4 Si fission offspring start at η=1.0

The η(a) age-efficiency ramp was designed for biological organisms with a
developmental juvenile phase. It does not apply to silicon fission. When a
Si agent fissions, the offspring is a full-capability compute unit immediately —
there is no warmup or growth period.

**Change:** Si fission offspring initialize with η=1.0 (not η_min).
The η(a) juvenile ramp is C-only from Stage 4.3 onwards.

```yaml
# Si config only:
life_history:
  eta_fission_offspring: 1.0   # Si fission offspring start fully capable
```

Consequences:
- Si agents have no juvenile phase — all Si agents forage at full efficiency
  from birth.
- "Juvenile starvation %" becomes a C-only metric.
- Si null control tuning changes (no juvenile drag on Si population).

### 1.5 Si pool — disabled by default, toggle-ready

**Design status: open question, disabled for Stage 4.3.**

The rationale for C's pool is clear: protect juveniles and elders who cannot
forage effectively. Si has neither (η=1.0 at fission, dormancy for scarcity).
So the *welfare* rationale doesn't apply.

However, there is a separate *efficiency* rationale worth preserving for
future investigation. In times of plenty, Si agents harvest more than they
metabolize. What happens to that surplus? Currently it accumulates as
personal wealth — hoarding by default. But a purely rational agent with no
carrying-cost advantage to hoarding might just as well dispose of surplus
into a shared local buffer. Not altruism — load balancing. The multi-agent
literature supports this: local surplus redistribution has been shown to
promote collective resilience even among self-interested agents without
social norms or reciprocity (Bilancioni et al. 2024; emergent "tolerated
theft" behavior in MARL, Agapiou et al. 2023).

If Si pooling were enabled, it would look different from C's pool:
- **Contribution:** any active Si agent contributes flat τ_pool_si × surplus
  above k_reserve. No Cred scaling. No status reward.
- **Draw eligibility:** any Si agent below k_draw × metabolism — including
  dormant agents (pool draw could accelerate reactivation).
- **No carry-over interaction:** Si pool carry-over uses same ρ as C pool
  if both are active; or Si can have its own ρ_si parameter.

**To enable Si pooling in a future stage**, set:

```yaml
# Si configs — default (Stage 4.3):
support_pool:
  enabled: false          # disabled; no Si pool contribution or draw

# Si configs — when enabling Si surplus pool experiment:
support_pool:
  enabled: true
  tau_pool_si: 0.05       # flat contribution rate; no Cred scaling
  k_reserve: 5.0          # metabolic reserve before contributing
  k_draw: 3.0             # draw eligibility threshold (× metabolism)
  draw_eligible: "all"    # Si: any agent may draw (not just non-active)
  dormant_can_draw: true  # dormant Si agents may draw to accelerate reactivation
  rho_carryover: 0.3      # same carry-over fraction as C pool
  k_pool_cap: 20          # same cap formula as C pool
```

**Implementation requirement (now):** the pool code must support the Si
config parameters above even though they are disabled in Stage 4.3. Do not
hard-code pool logic as C-only. Use `enabled` flag to gate behavior.
The toggle must work without code changes — config only.

**For Stage 4.3:** Si pool is off. Pool diagnostics are C-only.
The Si pool experiment is flagged for Stage 5+ with the research context
above as motivation.

### 1.6 Summary: C vs Si model distinctions (Stage 4.3)

| Feature | C | Si |
|---|---|---|
| Reproduction | Biparental, Allee effect | Fission, single parent |
| Offspring η at birth | η_min=0.3 (juvenile ramp) | η=1.0 (immediately capable) |
| Energy scarcity response | Pool draw (juveniles/elders) | Dormancy (any agent) |
| Death from energy | Starvation death | Permanent dormancy only |
| Pool | Active (τ_pool=0.05, ρ=0.3) | Disabled (toggle-ready) |
| Cred economy | Active (γ=0.2 birth boost) | None |
| Metabolism | Uniform[1,4] | Uniform[1,4] × β=5 |

**Current stage:** C uses social redistribution; Si uses individual dormancy.
**Open question:** whether rational Si surplus pooling emerges or is
beneficial — deferred to Stage 5+ with literature context preserved above.

---

## 2. Task 2 — Pool carry-over (ρ parameter)

### 2.1 Mechanism

Replace the step-reset pool with a carry-over fraction:

$$\text{pool}_{t+1} = \rho \cdot \text{leftover}_t + \text{contributions}_{t+1}$$

where $\text{leftover}_t = \text{pool}_t - \text{drawn}_t$.

$\rho = 0$ recovers current behavior exactly. Default $\rho = 0.3$.

**Pool cap (prevents unbounded accumulation):**

$$\text{pool}_t \leq k_{\text{cap}} \times N_{\text{active}} \times \bar{m}$$

where $k_{\text{cap}} = 20$ and $\bar{m}$ is mean active agent metabolism.
Contributions exceeding the cap are returned to contributors proportionally.

```yaml
support_pool:
  rho_carryover: 0.3     # fraction of unused pool carried to next step
  k_pool_cap: 20         # pool cap in units of N_active × mean_metabolism
```

### 2.2 Wealth accounting

Carry-over is deferred redistribution, not new wealth. Add a conservation test:
sum of all agent wealth + pool balance must be conserved across steps
(within floating point tolerance). This test must pass before any runs.

### 2.3 Interpretation

ρ > 0 makes the pool a **buffering institution** — pre-accumulates reserves
during peaks, draws them down during troughs. Ecologically: a communal granary
with finite storage (k_cap).

Note: pool cap uses N_active_C (active C agents only) since Si agents
are not pool participants.

---

## 3. Task 3 — Null control re-establishment

**Runs:** C static and Si static. Seed=42, 1000 steps.
**Locked inputs:** τ_pool=0.05, γ=0.2 (C), β=5.0, ρ=0.3, dormancy enabled (Si).

### 3.1 C static

C mechanics unchanged. Start at p_max_C = 0.07. Accept up to 3 attempts.

### 3.2 Si static

β=5 metabolism + dormancy changes Si equilibrium significantly.
Si agents go dormant more in early steps; pool is less active.
Start at p_fission_Si = 0.50. Accept up to 5 attempts.

Monitor both n_active_si and n_total_si. N gate applies to n_active_si.
Also check: dormancy_rate at t≥500 < 20% (most Si agents should be active
at steady state in a static resource environment).

### 3.3 Gate criteria

| Criterion | C static | Si static |
|---|---|---|
| n_active ∈ [150,400] at t≥500 | ✓ (N) | ✓ (n_active_si) |
| Juvenile starvation < 60% | ✓ (C-only metric) | n/a |
| Established starvation ≤ 0.78/step | ✓ | n/a |
| Si permanent dormancy deaths ≤ 0.5/step | n/a | ✓ |
| Si dormancy_rate < 20% at t≥500 | n/a | ✓ |
| Pool unmet mean < 20% at t≥500 | ✓ (C-only) | n/a |

**Si starvation gate replaced entirely** by permanent dormancy deaths and
dormancy rate. There is no β-scaled starvation threshold for Si — dormancy
supersedes the starvation mechanic.

### 3.4 Lock values

Record in ROADMAP.md once both pass:
- p_max_C (Stage 4.3)
- p_fission_Si (Stage 4.3)
- β_metabolism = 5.0
- ρ_carryover = 0.3
- k_pool_cap = 20
- k_dormant = 1.0, τ_trickle = 0.05, k_reactivate = 3.0, T_dormant_max = 50

---

## 4. Task 4 — T* search (C seasonal only)

**Goal:** find critical period T* where C transitions from stable to collapsing.

Stage 4.2: C stable at T=50,100; collapses at T=200. T* ∈ (100, 200).
Carry-over (ρ=0.3) may shift T* upward. C metabolism unchanged so Allee
dynamics are affected only by improved pool buffering.

**Runs:** C seasonal only. A=0.5. p_max_C = locked value. Seed=42, 1000 steps.

Binary search, max 3 runs:

| Step | T | If stable | If collapse |
|---|---|---|---|
| 1 | 150 | → try T=175 | → try T=125 |
| 2 | 175 or 125 | → T* ∈ (175,200) or (125,150) | → narrow further |
| 3 | bracket only | — | — |

Report T* as a range ≤ ±25 steps. State whether carry-over shifted T*
relative to Stage 4.2 (expected: upward shift).

---

## 5. Task 5 — Revised seasonal sweep (H1(ii))

Eight runs. All use locked model from Tasks 1–3.

| Run ID | A | T | Agent |
|---|---|---|---|
| 4.3-C-A05-T200 | 0.5 | 200 | C |
| 4.3-Si-A05-T200 | 0.5 | 200 | Si |
| 4.3-C-A075-T200 | 0.75 | 200 | C |
| 4.3-Si-A075-T200 | 0.75 | 200 | Si |
| 4.3-C-A05-T100 | 0.5 | 100 | C |
| 4.3-Si-A05-T100 | 0.5 | 100 | Si |
| 4.3-C-A05-T050 | 0.5 | 50 | C |
| 4.3-Si-A05-T050 | 0.5 | 50 | Si |

For Si runs: report both n_total_si and n_active_si.
Survival criterion: n_active_si remains > 10 for > 50 consecutive steps.

### 5.1 H1(ii) assessment (mandatory — CC must write this)

After all 8 runs, write a substantive assessment (minimum 150 words) covering:

- Which agent survives at each (A, T) combination (using n_active for Si)
- Whether dormancy changes Si's seasonal resilience profile vs Stage 4.2
- Whether the C pool (carry-over) + C biparental structure outperforms
  Si dormancy + Si individual resilience under any tested conditions
- Whether the crossover period (C better at short T, Si at long T) persists,
  shifts, or disappears with the corrected model
- A clear statement on H1(ii): supported, null, or mixed, with explanation

**Do not write "see table." Write the assessment.**

---

## 6. Task 6 — ψ_i death event logging

Add `death_events.parquet` to every run:

| Column | Type | Description |
|---|---|---|
| `step` | int | Step of death or permanent dormancy |
| `cause` | str | "starvation" (C) / "permanent_dormancy" (Si) / "senescence" |
| `age` | int | Agent age |
| `wealth` | float | Wealth at death |
| `psi` | float | ψ_i at death (C only; NaN for Si) |
| `cred` | float | Cred at death (C only; NaN for Si) |
| `agent_type` | str | "C" or "Si" |
| `season_phase` | int | 1=peak, 0=trough |
| `dormancy_duration` | int | Steps spent dormant before permanent death (Si only; 0 otherwise) |

ψ quartile analysis on C seasonal (A=0.5, T=200) as per Stage 4.2 plan.
If ψ flat across quartiles: flag for ψ redesign in Stage 4.4 (Q25).

---

## 7. New metrics

| Metric | Definition |
|---|---|
| `n_active_si` | Si agents in active state per step |
| `n_dormant_si` | Si agents in dormant state per step |
| `dormancy_rate` | n_dormant_si / n_total_si per step |
| `reactivations_per_step` | Si agents that reactivated this step |
| `permanent_dormancy_deaths` | Si agents that exceeded T_dormant_max |
| `mean_dormancy_duration` | Mean steps dormant per dormancy event (t≥500) |
| `pool_carryover_balance` | Pool balance carried from previous step |
| `pool_cap_clipped` | Wealth returned to contributors due to pool cap |
| `trickle_absorbed_per_step` | Total wealth absorbed by dormant Si agents |

---

## 8. Runs summary

| Priority | Task | Runs | Gate |
|---|---|---|---|
| 1 | Tasks 1–2 | Code only | Task 3 |
| 2 | Task 3 | C static + Si static (up to 8 tuning) | Tasks 4–6 |
| 3 | Task 4 | C seasonal ×3 max (T* search) | Informational |
| 4 | Task 5 | 8 seasonal runs | H1(ii) |
| 5 | Task 6 | Parquet read from Task 5 | No new runs |

Total new runs: up to **19 max** (8 tuning + 3 T* + 8 sweep).

---

## 9. Report format

All plots embedded per Standing Rule 11.
Figures to `outputs/stage43_seed42/figures/`.

### §0 Model changes
β_metabolism, dormancy mechanic, ρ_carryover. Rationale for each.
Dormancy parameter table (k_dormant, τ_trickle, k_reactivate, T_dormant_max).

### §1 Null control re-establishment
Tuning history. Locked values. N(t) plots (n_active and n_total for Si overlaid).
Dormancy diagnostics: dormancy_rate, mean_dormancy_duration at t≥500.
Pool diagnostics with carryover_balance visible.

### §2 T* search
Table of runs and outcomes. T* range stated. Comparison to Stage 4.2 T*.

### §3 Revised seasonal sweep (H1(ii))
8-run comparison table including n_active_si, n_dormant_si, dormancy_rate.
**Substantive H1(ii) assessment** (≥150 words, mandatory).

### §4 ψ_i death event analysis
Quartile starvation table (C seasonal A=0.5 T=200). Interpretation.

### Plots (mandatory, embedded)

```markdown
![N(t) null controls — C and Si active](figures/n_timeseries_null_controls.png)
![Si dormancy diagnostics — null control](figures/dormancy_diagnostics_si_static.png)
![Pool diagnostics C static](figures/pool_diagnostics_c_static.png)
![Pool diagnostics Si static](figures/pool_diagnostics_si_static.png)
![T* search N(t)](figures/n_timeseries_tstar_search.png)
![N(t) amplitude sweep](figures/n_timeseries_amplitude_sweep.png)
![N(t) period sweep](figures/n_timeseries_period_sweep.png)
![Si dormancy rate — seasonal runs](figures/dormancy_rate_seasonal.png)
![ψ starvation by quartile](figures/psi_starvation_quartile.png)
```

---

## 10. Success criteria

| Criterion | Target |
|---|---|
| β=5 implemented via CostModel | Confirmed in tests, Si only |
| Dormancy mechanic implemented | Passive trickle, reactivation, T_dormant_max |
| Wealth conservation test passes | pool + all agent wealth conserved per step |
| Pool carry-over implemented | ρ=0.3, cap active |
| C static null control passes | N_active ∈ [150,400], est. starvation ≤ 0.78/step |
| Si static null control passes | N_active ∈ [150,400], dormancy_rate < 20%, perm. deaths ≤ 0.5/step |
| T* bracketed | ≤ ±25 steps |
| Sweep complete | All 8 runs |
| H1(ii) assessment written | ≥150 words, substantive |
| ψ diagnostic reported | Quartile table present |
| Tests pass | Full suite after every code change |
| Reproducibility | seed=42 |
| ROADMAP updated | `G:\My Drive\docs\SiC Games\ROADMAP.md` |

---

## 11. Tests

Add to `tests/test_dormancy.py`:

1. **Dormancy trigger:** Si agent at wealth < k_dormant × metabolism → dormant flag set.
2. **No active behavior while dormant:** dormant agent does not move, harvest, reproduce, or contribute to pool.
3. **Trickle absorption:** dormant agent on cell with sugar S absorbs τ_trickle × S per step. Wealth increases.
4. **Reactivation:** dormant agent reaching k_reactivate × metabolism → active flag restored.
5. **Permanent death:** agent dormant for T_dormant_max+1 steps without reactivating → removed.
6. **C agent unaffected:** C agent at same wealth threshold → starvation death (not dormancy).
7. **Dormancy disabled for C:** verify dormancy.enabled=false in C configs.
8. **Wealth conservation:** one step with mixed active/dormant agents → total wealth conserved.
9. **Pool cap return:** contributions exceeding cap → excess returned to contributors proportionally.

---

## 12. Coding-agent directives

1. **Use CostModel for β.** Do not hardcode Si metabolism multiplier in BaseAgent.
   β applies to Si only — never to C agents.

2. **Dormancy is Si-only.** C agents die from starvation as before.
   Check agent type before applying dormancy logic. If C agent is flagged
   dormant by any code path, that is a bug — halt and report.

3. **N gate uses n_active_si.** All pass/fail assessments for Si use active
   agent count. n_total_si is tracked but not gated.

4. **Trickle does not consume cell sugar competitively.** Passive absorption
   does not trigger the cell's harvest or growback cycle. It is a read, not
   a write, on cell sugar.

5. **Wealth conservation test must pass before any runs.** Pool carry-over
   changes wealth flow — verify conservation in a unit test before proceeding
   to null control runs.

6. **Death event log is mandatory.** `death_events.parquet` must exist for
   every run. Include dormancy_duration column for Si.

7. **H1(ii) assessment is mandatory.** §3 must contain ≥150 words of
   substantive prose. "See table" is not acceptable per Rule 10.

8. **Embed all plots — hard requirement.** Run `generate_figures.py`
   after all parquets are written. Save every figure to
   `outputs/stage43_seed42/figures/`. Then open report.md and verify
   every `![...](figures/...)` reference resolves to an existing file
   on disk before closing the task. If any image file is missing,
   generate it — do not submit a report with broken image references.
   A report with missing or unembedded figures is **incomplete** and
   must not be uploaded.

9. **Update ROADMAP.md** at completion:
   `G:\My Drive\docs\SiC Games\ROADMAP.md`
   Mark Stage 4.3 complete. Record all locked values. Update Stage 4.4
   entry: λ wealth inheritance + Si social reactivation (Stage 5+) +
   ψ redesign if quartile analysis flat.

---

## 13. Deferred

- Si surplus pool experiment (toggle `support_pool.enabled: true` in Si
  configs; config parameters already specified in §1.5). Research question:
  does rational surplus disposal improve Si collective resilience? Does
  dormant-agent pool draw accelerate reactivation meaningfully?
  → Stage 5+. Config toggle requires no code changes.
- λ > 0 (wealth inheritance, C only). → Stage 4.4.
- ψ redesign (if quartile analysis flat). → Stage 4.4 (Q25 resolution).
- β sweep {2, 5, 10}. → Stage 5.x.
- ρ sweep {0.1, 0.3, 0.5}. → Stage 5.x.
- τ_trickle as sweep parameter. → Stage 5.x.
- T_dormant_max sensitivity. → Stage 5.x.
- Amplitude asymmetry (longer trough than peak). → Stage 4.4.
- Multi-seed runs. → Stage 5+.
