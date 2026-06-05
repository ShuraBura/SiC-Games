# SiC Games — Stage 4.1b Blueprint: Age-Efficiency Ramp + Initialization Fix

**Version:** 0.1
**Intended consumer:** Claude Code (and the human supervisor).
**Scope:** Stage 4.1b only. Two additions: realistic age initialization and
age-efficiency ramp η(a). No support pool, no Cred-modulated birth yet.
**Prerequisite:** Stage 4.1a complete. P_max_C=0.075, P_fission_Si=0.12 locked.

---

## 0. North Star (read first, every session)

**Stage 4.1b goal:** two targeted improvements to the variable population
substrate, both motivated by Stage 4.1a findings:

1. **Initialization fix:** replace all-age-zero startup with realistic age
   distribution. Eliminates the senescence wave artifact that inflated P_max
   requirements and adds noise to early-run dynamics.

2. **Age-efficiency ramp η(a):** agents outside the active foraging window
   harvest at reduced efficiency. Juveniles learn, elders decline. Motivated
   by Gurven & Kaplan (2006) Cobb-Douglas embodied capital model.

Additionally, **investigate the DTM formula self-regulation issue** identified
in Stage 4.1a: seasonal configs required manually higher P_max because the
wealth-relative birth formula doesn't automatically produce higher birth rates
under environmental stress. Diagnose and fix if possible without adding parameters.

**What Stage 4.1b is not.** No support pool (Stage 4.1c). No Cred-modulated
birth γ (Stage 4.2). No wealth inheritance λ > 0 (Stage 4.2). No Si Cred.
Two additions only, plus one formula investigation.

**Read ROADMAP.md C/Si distinction table before touching any agent code.**

**Failure modes to watch for:**
- Re-emergence of senescence wave: if initialization fix doesn't spread ages
  properly, the wave may reappear at t≈30-50 instead of t≈60-100. Check N(t)
  plot for early spikes.
- Juvenile starvation cascade: η_young=0.2 means newborns harvest at 20% 
  efficiency. If they can't accumulate wealth fast enough to pay metabolism,
  infant mortality dominates and birth rate can't compensate. Diagnostic:
  deaths_starvation_newborn spiking above 80% of total starvation deaths.
- η(a) breaking Si fission: Si fission produces a near-copy of parent. If
  parent is elderly (low η), offspring inherits parent age? No — offspring
  always starts at age=0. Confirm this in code.
- P_max drift from initialization fix: with realistic age distribution, the
  fraction of agents in reproductive window changes at t=0. This may shift
  the effective birth rate and destabilize the Stage 4.1a equilibrium. Monitor
  N(t) at t=500 — should still land in [150, 400].

---

## 1. What changes in Stage 4.1b

### 1.1 Initialization age distribution fix

**Current (broken):** all 250 agents initialize at age=0.

**Fixed:** each agent's starting age is drawn independently:

$$a_i(0) \sim \text{Uniform}\!\left[0,\; \lfloor \tau_{\max,i} / 2 \rfloor\right]$$

where τ_max,i is that agent's own max_age (drawn from [60, 100] as before).

**State at initialization:** all non-age attributes initialized as normal.
- Cred = f_C · mean_cred (but mean_cred=0 at t=0, so Cred=0 for all)
- Wealth drawn fresh from [w_min, w_max] regardless of age
- H_i traits drawn from canonical distributions
- wealth_velocity = 0

The behavioral inconsistency (old agents with no history) is accepted as a
startup transient. It burns off within ~100 steps as the population turns over.
A config flag preserves the old behavior for regression testing:

```yaml
initialization:
  age_distribution: "realistic"  # "realistic" (Stage 4.1b+) or "zero" (Stage 1-4.1a)
```

### 1.2 Age-efficiency ramp η(a)

Harvest efficiency is now age-dependent. For each agent at each step:

$$\eta(a_i) = \begin{cases}
\eta_{\min} + (1 - \eta_{\min}) \cdot \dfrac{a_i}{a_{\text{forage\_min}}} & a_i < a_{\text{forage\_min}} \\[6pt]
1.0 & a_{\text{forage\_min}} \le a_i \le a_{\text{forage\_max},i} \\[6pt]
1.0 - (1 - \eta_{\text{old}}) \cdot \dfrac{a_i - a_{\text{forage\_max},i}}{\tau_{\max,i} - a_{\text{forage\_max},i}} & a_i > a_{\text{forage\_max},i}
\end{cases}$$

where:
- $a_{\text{forage\_min}} = 15$ (fixed, same for all agents)
- $a_{\text{forage\_max},i} = \tau_{\max,i} - 10$ (per-agent, relative to their lifespan)
- $\eta_{\min} = 0.2$ (juvenile efficiency at birth — Kaplan: 10-40% of adult)
- $\eta_{\text{old}} = 0.4$ (elder efficiency at death — shallower than juvenile
  ramp, elders retain skill even as strength declines)

**Application:** η(a_i) multiplies the sugar harvested this step:

```python
harvest = sugar_at_cell * agent.eta()
agent.wealth += harvest
world.set_sugar(cell, 0)   # cell is fully depleted regardless of η
```

The cell is still fully depleted — η reduces what the agent receives, not
what is taken from the world. This prevents partial harvesting bookkeeping
complexity and is biologically reasonable (inefficient harvesters waste food).

**For Si agents:** same η(a) formula applies. Fission offspring start at age=0
with η=η_min=0.2 — they are juveniles. This is correct.

**Literature basis:** Gurven & Kaplan (2006) "Longevity Among Hunter-Gatherers."
Aggregate production curve approximated as piecewise linear per above.
Log in LITERATURE.md.

### 1.3 New config parameters

```yaml
initialization:
  age_distribution: "realistic"   # "realistic" or "zero"

life_history:
  forage_age_min: 15              # active foraging window minimum
  forage_age_max_offset: 10      # a_forage_max = tau_max - this offset
  eta_min: 0.2                    # juvenile efficiency at birth
  eta_old: 0.4                   # elder efficiency at death
```

### 1.4 DTM formula investigation

Stage 4.1a required P_max=0.10 for C seasonal vs 0.075 for C static —
a 33% increase needed manually. This is a design smell: the DTM formula
should produce higher birth rates under stress automatically.

**Diagnosis task:** run C static and C seasonal with identical P_max=0.075
and measure the birth rate time series. If birth rate in the seasonal run is
naturally higher during troughs (stress zone firing more), the formula is
self-regulating and the manual P_max adjustment was unnecessary. If birth
rate is similar, the formula is not responding to stress as intended.

**Likely cause:** r_stress=0.75 means the stress zone activates when
w_i < 0.75 × mean_w. Under seasonal stress, mean_w drops AND individual w
drops proportionally — the relative threshold stays similar. The stress zone
fires at similar rates regardless of absolute resource level.

**Fix if confirmed:** replace wealth-relative threshold with metabolism-relative
threshold for the stress zone lower bound. An agent is in the stress zone when
their wealth surplus above subsistence is low — regardless of what the
population mean is doing:

$$\text{stress zone}: \theta_{\text{sub}} \le w_i < \theta_{\text{sub}} + \Delta_{\text{stress}}$$

where $\Delta_{\text{stress}} = k_{\text{stress}} \times \text{agent metabolism}$
(default $k_{\text{stress}} = 10$). This makes the stress zone absolute rather
than relative — agents with low surplus above subsistence reproduce at P_max
regardless of whether the population mean is high or low.

**If the diagnosis shows the formula IS self-regulating:** document this and
accept the manual seasonal P_max as a permanent tuning decision. Do not change
the formula.

**Do not change the formula without first running the diagnosis.** Report
diagnosis results in the Stage 4.1b report before any formula change.

---

## 2. New metrics

| Metric | Definition |
|---|---|
| `mean_eta` | mean η(a_i) over living agents — population harvest efficiency |
| `frac_juvenile` | fraction of agents with a_i < a_forage_min |
| `frac_elder` | fraction of agents with a_i > a_forage_max_i |
| `frac_active` | fraction in active foraging window |
| `deaths_starvation_juvenile` | starvation deaths among agents with a < a_forage_min |
| `deaths_starvation_elder` | starvation deaths among agents with a > a_forage_max |
| `mean_init_age` | mean age at t=0 — verify initialization fix |

---

## 3. Runs to execute

Four runs in strict order — same structure as Stage 4.1a:

| Run | Config | Purpose |
|---|---|---|
| 1 | `stage41b_c_static_seed42.yaml` | C null control — realistic init + η(a) |
| 2 | `stage41b_si_static_seed42.yaml` | Si null control |
| 3 | `stage41b_c_seasonal_seed42.yaml` | C seasonal — primary H1(ii) run |
| 4 | `stage41b_si_seasonal_seed42.yaml` | Si seasonal |

**Additionally:** one diagnostic run before Run 1:

| Run | Config | Purpose |
|---|---|---|
| 0 | `stage41b_c_static_zeroinit_seed42.yaml` | C static with age_distribution="zero" |

Run 0 uses zero initialization to confirm η(a) alone doesn't break Stage 4.1a
equilibrium. Compare N(t) from Run 0 vs Stage 4.1a C static. If N(t) deviates
significantly (>20% from Stage 4.1a equilibrium), η(a) is the cause — investigate
before proceeding.

Runs 1+2 gate Runs 3+4 as before.

**Seasonal P_max values:** use Stage 4.1a tuned values (C=0.10, Si=0.15)
unless the DTM diagnosis shows they're unnecessary, in which case test with
matched P_max=0.075/0.12.

---

## 4. Primary comparison table (report format)

| Metric (t≥500) | Stage 4.1a C static | Stage 4.1b C static | Stage 4.1a Si static | Stage 4.1b Si static |
|---|---|---|---|---|
| N mean | 344.3 | ? | 284.5 | ? |
| N min | 168 | ? | 153 | ? |
| N max | 394 | ? | 350 | ? |
| Mean wealth | 39.4 | ? | 43.8 | ? |
| Mean eta | — | ? | — | ? |
| Frac juvenile | — | ? | — | ? |
| Frac elder | — | ? | — | ? |
| Deaths starvation juvenile | — | ? | — | ? |
| Deaths starvation elder | — | ? | — | ? |

### DTM diagnosis table

| Metric | C static P_max=0.075 | C seasonal P_max=0.075 |
|---|---|---|
| Mean birth rate (all steps) | ? | ? |
| Mean birth rate (trough steps only) | — | ? |
| Mean birth rate (peak steps only) | — | ? |
| Stress zone firing rate (all steps) | ? | ? |
| Stress zone firing rate (trough steps) | — | ? |

If trough birth rate > peak birth rate without P_max adjustment: formula
is self-regulating. If similar: formula needs fix.

---

## 5. Success criteria

1. **Initialization fix confirmed.** mean_init_age at t=0 is approximately
   mean_max_age/4 ≈ 20 steps. No senescence wave spike in N(t) at t≈60-100.

2. **η(a) does not collapse juvenile population.** deaths_starvation_juvenile
   < 60% of total starvation deaths. If above 60%, η_min=0.2 is too low —
   raise to 0.3 and document.

3. **Equilibrium preserved.** Stage 4.1b C static N mean (t≥500) within 20%
   of Stage 4.1a value (344.3 ± 69). If outside range, η(a) has shifted the
   carrying capacity — investigate and document.

4. **DTM diagnosis completed.** Report must include the DTM diagnosis table
   regardless of result. Do not skip even if formula appears self-regulating.

5. **Tests pass.**

6. **Reproducibility** confirmed for all runs.

---

## 6. Tests

`tests/test_life_history.py`:

1. **η formula correctness:** for known (age, a_forage_min, a_forage_max,
   tau_max, eta_min, eta_old), verify η(a) matches analytic formula at
   a=0, a_forage_min-1, a_forage_min, a_forage_max, a_forage_max+1, tau_max.

2. **η at boundaries:** verify η(0) = eta_min, η(a_forage_min) = 1.0,
   η(tau_max) ≈ eta_old.

3. **Cell fully depleted regardless of η:** verify world sugar = 0 after
   harvest even when η < 1.

4. **Si offspring age=0:** verify fission offspring always start at age=0
   with η=eta_min, regardless of parent age.

5. **Initialization age distribution:** run 1000-agent initialization with
   age_distribution="realistic", verify mean age ≈ mean_max_age/4, verify
   no agent initialized older than their own max_age/2.

6. **Zero initialization regression:** verify age_distribution="zero" produces
   all agents at age=0, recovering Stage 4.1a behavior.

---

## 7. Coding-agent directives

1. **Run 0 (diagnostic) before Run 1.** Confirm η(a) alone doesn't break
   equilibrium before combining with initialization fix.

2. **DTM diagnosis is mandatory.** Run C static and C seasonal at matched
   P_max=0.075 for diagnosis only. Report birth rate time series by trough
   vs peak phase. This is a diagnostic run — do not save as a canonical output.

3. **η applies to harvest only.** It does not affect movement, joint-task
   participation, Cred accumulation, or any other mechanic. One multiplication
   at harvest time.

4. **Do not change the DTM formula before running diagnosis.** Diagnosis first,
   fix only if confirmed broken.

5. **Si offspring always age=0.** Check this explicitly — fission produces
   a near-copy but age is never copied. Age is a lifecycle attribute, not
   a trait.

6. **LITERATURE.md:** log Gurven & Kaplan (2006) with the key finding:
   production at age 15 = 10-40% of adult, peak at 35-45, elder decline
   shallower than juvenile ramp. Note that η_min=0.2 and η_old=0.4 are
   calibrated from this empirical record.

7. **Update ROADMAP.md** at completion: mark Stage 4.1b complete, record
   DTM diagnosis result, update P_max locked values if seasonal mismatch
   is resolved.

---

## 8. Deferred

- Support pool (Level 2+3). → Stage 4.1c.
- Cred-modulated birth γ. → Stage 4.2.
- Wealth inheritance λ > 0. → Stage 4.2.
- Si Cred economy. → Stage 5+.
- Allee effect mitigation (if desired). → Design decision pending.
  Currently treated as emergent feature, not a bug.
- n_mvp_threshold metric. → Add to Stage 4.1c alongside support pool
  (pool affects Allee dynamics).
- Elder knowledge bonus for Si (vision bonus at high age). → Stage 5+.
- Inter-pool connectivity. → Stage 5+.
