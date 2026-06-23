# SiC Games — Glossary

Plain-language definitions of the symbols, abbreviations, and terms used across the docs, blueprints, commit
messages, and RESULTS log. Keep this current — when a new term enters the model, define it here.

## Model parameters / knobs
- **κ (kappa, "contest_exponent")** — status-weighting strength of resource sharing & competition. **κ=0** =
  everyone shares/competes equally (egalitarian = **Silicon**); **κ>0** = higher-status agents get more (the
  hierarchy = **Carbon**). Weight is `(status+ε)^κ`. Bigger κ ⇒ steeper advantage to the top.
  *(Note: a separate `carbon_cfg.kappa` controls the movement-temperature coupling — held at 0 in Tier-1 to
  isolate the meat effect. Same Greek letter, different knob.)*
- **δ (delta)** — density-disease strength. The free lever that regulates population: disease mortality rises
  with local crowding (`1+δ·ρ/(ρ+ρ_half)`), holding growth ≈0 below the food ceiling. Provisional δ≈3.
- **CV** — coefficient of variation = (standard deviation)/(mean). Unitless "burstiness." CV=0 = constant;
  forest meat CV≈0.73; savanna meat CV≈2.24 (feast/famine — most hunts ~0, rare big kills).
- **K** — carrying capacity: the maximum population the environment's food supports. "near K" = the population
  is pressed against the food limit (where crowding/competition bites).
- **meat_frac** — fraction of diet from hunted game (vs gathered plants), per biome (Cordain 2000). Forest 0.55.
- **ε (epsilon, phi_epsilon)** — a tiny constant guarding `(status+ε)^κ` against zero.

## Demographic terms
- **e₀** — life expectancy at birth (mean years lived). e₁₅ = remaining life expectancy at age 15.
- **Siler** — the 3-term mortality model used (infant + background + senescent hazard vs age). Aché-anchored.
- **IBI** — inter-birth interval: months between a mother's successive births (lactational spacing). Aché ≈37.
- **TFR** — total fertility rate: lifetime births per woman. Aché ≈8.
- **NPP** — net primary productivity: plant growth rate = the food base the carrying capacity is built on.
- **fertility-pinned** — at equilibrium (population steady, growth≈0) total deaths must equal total births, so
  e₀ is set by the *fertility* schedule, not the mortality coefficients (R-16).
- **compositional vs aggregate** — *aggregate* = how many die (pinned at equilibrium). *compositional* = **which**
  agents die. A status hierarchy changes the composition (who) without moving the aggregate (how many) — R-18.
- **period life table** — mortality measured from deaths-per-person-year in each age band at one moment;
  decouples e₀ from the growth-rate confound.

## Strategy / Carbon–Silicon terms
- **Carbon** — the hierarchical civilization type: status (Cred)-weighted sharing & competition (κ>0).
- **Silicon** — the egalitarian type: equal sharing (κ=0). The eventual comparison; deferred for now.
- **Cred** — an agent's accumulated **status/prestige** (the hierarchy variable). Seeded + heritable in Tier-1.
- **φ (phi)** — an agent trait (the Cred-*seeking* weight). Distinct from `cred` (accumulated status). The
  meat/contest weight reads `cred` under the Carbon-substrate flag, else `φ` (the `status_of` hook).
- **anti-fragility (R-1)** — the project's thesis: under stress a Carbon hierarchy protects its high-Cred core
  (fast recovery) while egalitarian Silicon crashes together (the "dormancy cliff").
- **Matthew / status amplification (β)** — rich-get-richer feedback on status (deferred to Tier-2).

## Build stages / labels
- **G.1 / G.2 / G.3** — game-economy build stages: G.1 = forage+meat diet split (Cordain); G.2 = κ-weighting on
  the meat stream (band-pooled); G.3 = stochastic (lognormal) meat returns.
- **Tier-1 / Tier-2** — Carbon-on-substrate stages. Tier-1 = the *passive* advantage (Cred-weighted meat →
  compositional survival gradient). Tier-2 = the *active* individualism (leadership: high-Cred lead the band to
  high-reward cells) + earned Cred.
- **D1 / D3** — design decisions in the Carbon scoping: D1 = the `status_of` hook (weight by cred not φ); D3 =
  heritable Cred (founder seeding + noisy lineage copy at birth).
- **R-<n>** — a numbered finding in `docs/RESULTS.md` (e.g. R-16 fertility-pinning, R-18 Carbon validation).
- **RT-<n>** — a red-team target/finding in a blueprint's review section.
- **S0 / S1 / C.2b** — provisioning/condition sub-mechanics (body-condition EMA; child-priority shortfall
  sharing; mother→child provisioning).

## Code / method terms
- **rivalrous path (`_step_rivalrous`)** — the demographic model's step: diffusion movement → per-cell harvest
  split → metabolism/mortality. (The other path, `_step_agent`, is the older non-demographic one.)
- **harvest_field** — the per-cell food yield the rivalrous path harvests (the NPP carrying-capacity field).
- **compute_harvest_shares** — splits a cell's yield among occupants; equal at κ=0, `(status+ε)^κ`-weighted at κ>0.
- **occ_wsum / w_self** — the Cred-weighted terms in the **movement contest** (competition for which cell to
  occupy). The "second κ channel" alongside the harvest split (the R-18 caveat).
- **status_of(agent)** — returns `cred` under the carbon flag, else `φ` — the single hook that makes the
  hierarchy bite on meat & movement.
- **drift-controlled** — comparing κ>0 vs κ=0 runs with **identical random seeds**, so the only difference is κ
  (any divergence is the κ effect, not seed noise).
- **ablation** — switching **off** one component at a time to measure its contribution (e.g. κ on harvest only
  vs movement only, to apportion the R-18 advantage between the two channels).
- **t / t-stat** — significance: (effect mean)/(standard error). |t|≳2 ≈ p<0.05; ≳2.9 ≈ p<0.01 (N≈20 seeds).
