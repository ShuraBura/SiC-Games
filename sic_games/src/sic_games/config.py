from __future__ import annotations

from pathlib import Path
from typing import Literal, Optional

import yaml
from pydantic import BaseModel, Field, model_validator


class WorldConfig(BaseModel):
    grid_size: tuple[int, int] = (50, 50)
    toroidal: bool = True
    sugar_peaks: list[tuple[int, int]] = [(10, 40), (40, 10)]
    max_sugar_capacity: int = Field(4, ge=1)
    band_width_k: int = Field(6, ge=1)
    growth_rate_alpha: int = Field(1, ge=1)


class AgentsConfig(BaseModel):
    initial_population: int = Field(250, ge=1)
    vision_dist: tuple[int, int] = (1, 6)
    metabolic_rate_dist: tuple[int, int] = (1, 4)
    max_age_dist: tuple[int, int] = (60, 100)
    initial_wealth_dist: tuple[int, int] = (5, 25)
    phi_mean: float = Field(0.5, ge=0.0, le=1.0)
    phi_std: float = Field(0.2, ge=0.0)
    # Stage 3.3 trait vector H_i additions
    psi_mean: float = Field(0.5, ge=0.0, le=1.0)
    psi_std: float = Field(0.2, ge=0.0)
    # Stage 4.4: Beta(a,b) distribution for ψ. When both > 0, overrides Normal(psi_mean, psi_std).
    psi_beta_a: float = Field(0.0, ge=0.0)
    psi_beta_b: float = Field(0.0, ge=0.0)
    c1_mean: float = Field(0.5, ge=0.0, le=1.0)
    c1_std: float = Field(0.2, ge=0.0)
    c2_mean: float = Field(0.5, ge=0.0, le=1.0)
    c2_std: float = Field(0.2, ge=0.0)


class DecisionConfig(BaseModel):
    strategy: Literal["greedy", "carbon", "si_bounded"] = "greedy"


class CarbonConfig(BaseModel):
    sigma_base: float = Field(0.5, gt=0.0)
    kappa: float = Field(2.0, ge=0.0)
    cred_scale: float = Field(10.0, gt=0.0)
    cred_decay: float = Field(0.01, gt=0.0, lt=1.0)
    matthew_alpha: float = Field(2.0, gt=0.0)
    epsilon: float = Field(0.01, gt=0.0)
    cred_bonus_per_participant: float = Field(1.0, ge=0.0)
    velocity_tau: int = Field(10, ge=0)
    velocity_scale: float = Field(1.0, gt=0.0)
    f_C: float = Field(0.25, ge=0.0, le=1.0)  # newborn Cred endowment fraction
    status_amplification_beta: float = Field(0.0, ge=0.0)  # β — Stage 3.2


class SiBoundedConfig(BaseModel):
    sigma_si: float = Field(1.238, gt=0.0)  # Si base exploration temperature; locked Stage 3.4 2D scan (σ_Si_eff = σ_Si + κ_Si·tanh(si_cred/C*_Si))
    # Stage 4.3: Si differential metabolism multiplier (β=5 default; C always β=1.0)
    beta_metabolism: float = Field(1.0, ge=1.0)
    # Stage 4.5 Task 3: per-agent wealth carrying cost (Si only).
    # k_carry=None (default) disables the mechanic — all prior Si configs unaffected.
    # When enabled: if agent.wealth > k_carry * metabolism, deduct phi_carry * excess each step.
    k_carry: Optional[float] = Field(None, gt=0.0)
    phi_carry: float = Field(0.02, gt=0.0, le=1.0)


class JointTaskConfig(BaseModel):
    distance_d: int = Field(1, ge=0)
    capacity_threshold: int = Field(4, ge=1)


class C2DefectionConfig(BaseModel):
    """Stage 5.2 Task 1: c2 joint-task defection hook (C only).

    enabled=False (default) preserves bit-identical behaviour to Stage 5.1.
    When enabled: C agents may defect from a joint task when their solo harvest
    exceeds their Matthew share. p_defect_i = c2_i in that case, else 0.
    """
    enabled: bool = False


class DeffuantConfig(BaseModel):
    """Stage 5.2 Task 2: Deffuant bounded-confidence cultural updating (C only).

    enabled=False (default) preserves all prior behaviour exactly.
    When enabled, each C agent selects one C neighbour within the interaction
    radius and updates cultural traits toward them if |trait_i - trait_j| < epsilon.
    c1_i scales resistance: mu_eff = mu * (1 - c1_i); c1=1 → agent never updates.
    Prestige weight: w = cred_j / (cred_i + cred_j + eps_div).
    """
    enabled: bool = False
    epsilon: float = Field(0.2, ge=0.0, le=1.0)   # confidence bound; 0=no updates (gate)
    mu: float = Field(0.3, ge=0.0, le=1.0)         # base convergence rate; 0=no movement (gate)
    update_every: int = Field(1, ge=1)              # steps between updates
    traits: list[str] = Field(default_factory=lambda: ["c1", "c2", "psi"])
    cred_weight: str = "relative"                   # prestige bias form
    eps_div: float = Field(1e-6, gt=0.0)            # div-by-zero guard


class SubstrateConfig(BaseModel):
    """Stage 6.0a: multi-occupancy spatial substrate.

    enabled=False (default) preserves the one-agent-per-cell Epstein-Axtell
    substrate EXACTLY — existing configs/tests are untouched and route through
    the legacy code path. When enabled, cells may hold many agents; harvest is a
    per-cell split; movement may switch to local-gradient diffusion.

    Recovery gate (blueprint §7.1): enabled=True, k_cell=1, movement_mode='legacy',
    contest_exponent=0, move_cost_flat=0 must reproduce the legacy model bit-identically.
    Production multi-occupancy: enabled=True, k_cell=0 (unlimited), movement_mode='diffusion'.
    """
    enabled: bool = False
    cell_area_km2: float = Field(100.0, gt=0.0)        # §1 spatial scale: 1 cell = 100 km² (10×10 km)
    k_cell: int = Field(0, ge=0)                        # hard occupancy ceiling; 0 = unlimited (∞); 1 = recovery regime
    movement_mode: Literal["legacy", "diffusion"] = "legacy"  # legacy=vision-v cardinal arms; diffusion=von-Neumann r=1
    contest_exponent: float = Field(0.0, ge=0.0)       # κ: 0 = even split (scramble); 1 = Cred-weighted contest (C)
    move_cost_flat: float = Field(0.0, ge=0.0)         # flat energy cost per move; 0 = free (recovery)
    phi_epsilon: float = Field(1e-6, gt=0.0)           # contest denominator guard (φ+ε)


class RunConfig(BaseModel):
    n_steps: int = Field(1000, ge=1)
    metrics_every: int = Field(1, ge=1)
    k_density: int = Field(10, ge=1)   # c_spatial_density sampling period (Task 2 perf-fix B)
    k_moran: int = Field(10, ge=1)     # Moran's I W-matrix sampling period (Task 3 perf-fix C)
    output_dir: str = "outputs/stage1_baseline_seed42"
    si_reference_dir: str = ""  # path to a Stage 1 run dir for overlay plots (carbon only)
    c_reference_dir: str = ""   # path to a no-switch C run dir for three-way comparison table


class PopulationConfig(BaseModel):
    mode: Literal["fixed", "dynamic"] = "fixed"  # "fixed"=Stage 1 behavior, "dynamic"=Stage 4.1a+


class CarryingCostConfig(BaseModel):
    """Stage 4.5: density-dependent birth ceiling for C agents.

    p_birth_effective = p_max × DTM_factor × carry_discount(N_C)
    carry_discount(N_C) = max(0, 1 - alpha_carry × N_C / N_carry)

    enabled=False (default) preserves all prior behaviour.
    """
    enabled: bool = False
    N_carry: int = Field(400, gt=0)            # carrying capacity; start at upper gate
    alpha_carry: float = Field(1.0, gt=0.0)   # discount steepness; 1.0 = linear


class BirthCConfig(BaseModel):
    p_max: float = Field(0.02, gt=0.0, le=1.0)
    tau_sub: float = Field(5.0, gt=0.0)           # subsistence floor = metabolism * tau_sub
    r_stress: float = Field(0.75, gt=0.0)          # legacy: stress zone boundary = r_stress * mean_w
    k_stress: Optional[float] = None              # Stage 4.1b: stress zone = theta_sub + k_stress*metabolism
    r_wealth: float = Field(0.5, gt=0.0)           # prosperity decay scale (* mean wealth)
    rep_age_min: int = Field(15, ge=0)
    rep_age_max: Optional[int] = None              # None -> agent.max_age - 10
    # Stage 4.2: Cred-modulated birth (Turchin elite overproduction)
    # P_birth_i *= (1 + gamma * tanh(C_i / c_star_birth))
    gamma: float = Field(0.0, ge=0.0)             # 0 = no modulation; 0.2 = Stage 4.2 default
    c_star_birth: float = Field(10.0, gt=0.0)     # Cred scale for birth modulation (C*** = C* by default)
    # Stage 4.5: density-dependent birth ceiling (C only)
    carrying_cost: CarryingCostConfig = CarryingCostConfig()


class BirthSiConfig(BaseModel):
    p_fission_max: float = Field(0.02, gt=0.0, le=1.0)
    fission_wealth_mult: float = Field(1.5, gt=0.0)  # theta_fission = mean_wealth * mult
    rep_age_min: int = Field(15, ge=0)
    rep_age_max: Optional[int] = None


class ReproductionConfig(BaseModel):
    mode: Literal["random", "biparental"] = "random"
    parent_radius: int = Field(3, ge=1)
    inherit_sigma: float = Field(0.05, ge=0.0)
    coordinator: Literal["individual", "hivemind"] = "individual"
    lambda_inheritance: float = Field(0.0, ge=0.0, le=1.0)  # wealth inheritance (0=none)


class SiCredConfig(BaseModel):
    enabled: bool = False
    k_cred_band: float = Field(1.0, gt=0.0)          # near-dormancy band width (Stage 5.1)
    decay: float = Field(0.01, gt=0.0, lt=1.0)       # δ — matches C Cred decay
    # Stage 5 Task 3: Cred ceiling + σ modulation strength
    C_star_Si: float = Field(10.0, gt=0.0)            # Cred ceiling (matches C*)
    kappa_Si: float = Field(0.5, ge=0.0)              # σ modulation; 0.0 recovers Stage 4.5


class PerturbationConfig(BaseModel):
    type: Literal["null", "seasonal"] = "null"
    amplitude: float = Field(0.5, ge=0.0, le=1.0)
    period: int = Field(200, ge=1)
    # Stage 4.5 Task 4: asymmetric seasonal (Q17). trough_fraction = proportion of period
    # spent descending into the trough (slow descent, fast recovery).
    # 0.5 = symmetric (default, preserves prior behaviour).
    # 0.6 = trough phase 60% of period, peak recovery 40%.
    trough_fraction: float = Field(0.5, ge=0.0, le=1.0)


class VisualizationConfig(BaseModel):
    animate: bool = True
    frames_per_save: int = Field(5, ge=1)
    save_static_plots: bool = True
    agent_color: str = ""  # override strategy-derived color (e.g. "blue", "orange")


class InitializationConfig(BaseModel):
    age_distribution: Literal["zero", "realistic"] = "zero"  # "realistic" = Stage 4.1b+
    age_init_upper_frac: float = Field(0.5, gt=0.0, le=1.0)  # Stage 4.4 patch: upper bound for realistic age draw (default 0.5 = Stage 4.1b behaviour)
    wealth_init_scale_k: bool = False  # Stage 4.4 patch amendment: multiply initial_wealth_dist by k_grid (growth_rate_alpha) at t=0 only
    cluster_init: bool = False          # Stage 4.4 patch amendment 2: place t=0 agents in Chebyshev ball around a sugar peak
    cluster_peak_index: int = 0         # index into world.sugar_peaks
    cluster_radius: int = 10            # Chebyshev radius around peak centre


class LifeHistoryConfig(BaseModel):
    forage_age_min: int = Field(15, ge=0)           # active foraging window start
    forage_age_max_offset: int = Field(10, ge=0)    # a_forage_max = tau_max - offset
    eta_min: float = Field(0.2, ge=0.0, le=1.0)     # juvenile efficiency at birth
    eta_old: float = Field(0.4, ge=0.0, le=1.0)     # elder efficiency at max_age
    # Stage 4.3: Si fission offspring start fully capable (no juvenile ramp)
    eta_fission_offspring: float = Field(1.0, ge=0.0, le=1.0)


class SupportPoolConfig(BaseModel):
    enabled: bool = False
    r_pool: int = Field(5, ge=1)                  # proximity radius (Stage 5+ spatial pools)
    tau_parent: float = Field(0.1, ge=0.0, le=1.0) # parental wealth transfer fraction
    tau_pool: float = Field(0.1, ge=0.0, le=1.0)   # active-adult contribution fraction (C)
    k_reserve: float = Field(5.0, gt=0.0)           # metabolic steps kept before contributing
    k_draw: float = Field(3.0, gt=0.0)              # metabolic steps covered by pool draw
    tau_cred: float = Field(0.5, ge=0.0)            # C only: Cred scaling of contribution
    tau_cred_reward: float = Field(0.1, ge=0.0)     # C only: Cred reward for above-base contribution
    # Stage 4.3: carry-over and pool cap
    rho_carryover: float = Field(0.0, ge=0.0, le=1.0)  # fraction of unused pool carried to next step (0 = Stage 4.1c behavior)
    k_pool_cap: float = Field(0.0, ge=0.0)              # cap in units of N_active_C × mean_metabolism; 0 = no cap
    # Stage 4.3+: Si pool parameters (toggle-ready; disabled in Stage 4.3)
    tau_pool_si: float = Field(0.05, ge=0.0, le=1.0)    # Si flat contribution rate (no Cred scaling)
    dormant_can_draw: bool = False                       # Si only: dormant agents may draw from pool


class DormancyConfig(BaseModel):
    """Stage 4.3: Si dormancy mechanic. Si agents suspend instead of dying from energy shortage.
    Enabled in Si configs only. C agents always use starvation death (dormancy.enabled=False).
    """
    enabled: bool = False
    k_dormant: float = Field(1.0, gt=0.0)      # wealth < k_dormant × metabolism → enter dormancy
    tau_trickle: float = Field(0.05, ge=0.0)   # passive absorption rate (fraction of cell sugar) while dormant
    k_reactivate: float = Field(3.0, gt=0.0)   # wealth ≥ k_reactivate × metabolism → reactivate
    t_dormant_max: int = Field(50, ge=1)        # max dormancy steps before permanent death


class Config(BaseModel):
    seed: int = 42
    world: WorldConfig = WorldConfig()
    agents: AgentsConfig = AgentsConfig()
    decision: DecisionConfig = DecisionConfig()
    carbon: CarbonConfig = CarbonConfig()
    si_bounded: SiBoundedConfig = SiBoundedConfig()
    joint_task: JointTaskConfig = JointTaskConfig()
    c2_defection: C2DefectionConfig = C2DefectionConfig()
    deffuant: DeffuantConfig = DeffuantConfig()
    substrate: SubstrateConfig = SubstrateConfig()
    population: PopulationConfig = PopulationConfig()
    birth_c: BirthCConfig = BirthCConfig()
    birth_si: BirthSiConfig = BirthSiConfig()
    reproduction: ReproductionConfig = ReproductionConfig()
    si_cred: SiCredConfig = SiCredConfig()
    dormancy: DormancyConfig = DormancyConfig()
    perturbation: PerturbationConfig = PerturbationConfig()
    initialization: InitializationConfig = InitializationConfig()
    life_history: LifeHistoryConfig = LifeHistoryConfig()
    support_pool: SupportPoolConfig = SupportPoolConfig()
    run: RunConfig = RunConfig()
    visualization: VisualizationConfig = VisualizationConfig()

    @model_validator(mode="after")
    def _check_peaks_in_grid(self) -> "Config":
        w, h = self.world.grid_size
        for x, y in self.world.sugar_peaks:
            if not (0 <= x < w and 0 <= y < h):
                raise ValueError(f"Sugar peak ({x},{y}) outside grid {w}x{h}")
        return self


def load_config(path: str | Path) -> Config:
    with open(path) as f:
        raw = yaml.safe_load(f)
    return Config.model_validate(raw)
