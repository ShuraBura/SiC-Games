"""phase1_model.py — TerrainWorld: Mesa model for Phase 1.

Replaces the Sugarscape SugarField harvest path with terrain kcal economy.
C agents only. Si excluded (Phase 1 terrain path).

Economy (A-1, kcal):
  burn_per_step  = burn_kcal_per_day × days_per_month                     [NOMINAL]
  intake_per_step = rate_kcal_per_hr × foraging_hours_per_day × days/month [NOMINAL]
  reserve += intake − burn; death at reserve ≤ reserve_floor              [PLACEHOLDER MR-1]
  reserve capped at reserve_full                                            [PLACEHOLDER MR-1]

Sex-based stream selection (A-2):
  female default → forage_kcal stream; male default → game_kcal stream;
  switch only under deficit pressure (no new tunable). [non-rivalrous; CC-1 deferred]

Child age-gate (A-2, binary): below age_productive_min → intake = 0. [JV-1 seam]

Multi-occupancy rivalry (A-3, opt-in `substrate_cfg`, supervisor-directed 2026-06-16):
  The default Blueprint-A path is NON-rivalrous (each agent gets the full cell rate) and
  has no density-dependence, so reproduction would explode with no carrying capacity.
  When a `SubstrateConfig` is supplied (enabled), the model adopts the Stage-6.0a
  multi-occupancy substrate on the terrain field:
    - movement: `diffusion_select_target` (von-Neumann r=1, per-capita-yield utility,
      self-limiting — a mobbed rich cell offers a small share so it stops attracting).
    - harvest: the cell's total return rate S = forage_level(cell) is SPLIT among its
      occupants via `compute_harvest_shares` (κ=contest_exponent: 0 → even split /
      "Cred=1 for all"; κ>0 → share ∝ (φ+ε)^κ). Affinity/crowd hooks held neutral (=1).
  Density-dependence (hence a terrain-discovered carrying capacity ≈ Σ S_cell/burn over
  survivable cells) emerges from rivalry, NOT an imposed N_carry. This is a minimal
  PROVISIONAL preview of CC-1; S = forage-rate-as-cell-total under-estimates the true
  NPP-derived extractable rate (CC-1 deferred) — the *dynamics* are the finding, the
  absolute capacity is provisional. Forage-only (game stream off) for this shakedown.

Demographic layer (A-3, opt-in `reproduction=True`):
  Blueprint A shipped death-only. A minimal PROVISIONAL reproduction rule is added so the
  population can settle: eligible = alive, age ≥ repro_min_age, reserve ≥ birth_threshold;
  then reproduce with prob p_birth. On birth the parent pays birth_cost; the child is
  placed on the parent's cell (multi-occupancy; it disperses via diffusion), age 0,
  reserve = child_endowment. NOT the full C biparental/Cred reproduction (deferred to the
  Phase-1 demographic stage / RECAL). All repro params are [PROVISIONAL — shakedown].

Placement: pass `placement_positions` (a list of (x,y), len = n_agents) to use a
deterministic founder-cluster layout instead of random land sampling.
"""
from __future__ import annotations

import math
import random
from collections import Counter

import mesa

from sic_games.agents.base import BaseAgent
from sic_games.agents.costs import KcalBurnModel
from sic_games.agents.perception import LocalVisionPerception
from sic_games.agents.strategies.carbon import CarbonDecision
from sic_games.agents.traits import TraitVector
from sic_games.config import KcalEconomyConfig, LifeHistoryConfig, SubstrateConfig
from sic_games.demography import (
    DemographyConfig, density_mult, energetic_fertility_factor, is_fertile, sedentism_ibi, pathogen_mult, risk_mult, synergy_mult,
    society_from_character, SOCIETY_PRESETS, leader_society_weight, size_repulsion, mate_ascribed_weight,
    mobility_radius, footprint_radius,
)
from sic_games.group import GroupVector, NO_BAND
from sic_games.genome import Genome
from sic_games.substrate import compute_harvest_shares, diffusion_select_target, base_status
from sic_games.terrain import N, WorldFields, generate_world
from sic_games.terrain_field import TerrainField

_CELL_KM2 = 100.0   # CC-1: each cell = 100 km² (local density = cell occupancy / _CELL_KM2)

# Campaign genealogy CSV schema (enriched, append-only pure observer). x,y = event cell; rs facets = parity
# (female lifetime births) / n_fathered (male); society = the band's morph at the event.
GENEA_HEADER = ["step", "event", "uid", "mother_uid", "father_uid", "lineage", "band_id", "cred", "prowess",
                "wealth", "sex", "age", "parity", "n_fathered", "x", "y", "society"]


def _gini(xs) -> float:
    """Gini coefficient of a non-negative sequence (0 = even, →1 = concentrated). <2 items or zero-sum ⇒ 0."""
    import numpy as np
    a = np.sort(np.asarray([v for v in xs if v is not None], dtype=float))
    n = a.size
    if n < 2 or a.sum() <= 0:
        return 0.0
    return float((2.0 * np.sum(np.arange(1, n + 1) * a)) / (n * a.sum()) - (n + 1.0) / n)


def allocate_store_draw(weights: list[float], deficits: list[float], store: float) -> list[float]:
    """S.2 collective-granary draw: allocate `store` across claimants by `weights` (status^κ — the Hayden
    control-of-redistribution lever), each capped at its `deficits`. Single pass from the initial store; any
    leftover (from weight-rich but near-full claimants) stays in the granary. Equal weights ⇒ equal split
    (egalitarian, κ=0); skewed weights ⇒ high-status fill more of their reserve (κ>0 inequality). Pure/numeric."""
    wsum = sum(weights) or 1.0
    return [min(store * (w / wsum), d) for w, d in zip(weights, deficits)]


def seed_band_positions(fields, n_agents: int, band_size: int = 25, territory_radius: int = 3,
                        quality_frac: float = 0.5, rng=None) -> list[tuple[int, int]] | None:
    """Realistic BANDED initial placement (foragers start in bands, not a gas): ~band_size-person kin bands at
    good-but-not-best, TERRITORY-spaced sites, allocated PER BIOME by carrying capacity — so marginal biomes
    (desert, mountain) get fewer-but-NON-ZERO bands (desert dwellers + mountain clans) while rich biomes get
    many. Sites are SAMPLED from the viable set (≥ quality_frac of the biome's best), not the argmax, so bands
    have slack to wander. Returns a `placement_positions` list (len = n_agents); None if degenerate."""
    import numpy as np
    import random as _random
    rng = rng or _random.Random(0)
    val = np.asarray(fields.forage_kcal, dtype=float)              # carrying-capacity proxy [y,x]
    biome = np.asarray(fields.biome)
    land = np.asarray(fields.isWater) == 0
    n_bands = max(1, n_agents // band_size)
    cap = {int(b): float(val[land & (biome == b)].sum()) for b in np.unique(biome[land])}
    cap = {b: c for b, c in cap.items() if c > 0.0}
    if not cap:
        return None
    total = sum(cap.values())
    alloc = {b: max(1, round(n_bands * c / total)) for b, c in cap.items()}   # ∝ capacity, floor 1 per biome
    placed: list[tuple[int, int]] = []
    positions: list[tuple[int, int]] = []
    for b in sorted(alloc, key=lambda k: -cap[k]):                 # rich biomes claim sites first
        mask = land & (biome == b)
        vmax = float(val[mask].max())
        ys, xs = np.where(mask & (val >= quality_frac * vmax))     # viable (good-but-not-best) cells
        viable = list(zip(xs.tolist(), ys.tolist()))
        rng.shuffle(viable)
        cnt = 0
        for (x, y) in viable:
            if cnt >= alloc[b]:
                break
            if all(max(abs(x - px), abs(y - py)) >= territory_radius for (px, py) in placed):
                placed.append((x, y))
                positions.extend([(x, y)] * band_size)
                cnt += 1
    i = 0
    while len(positions) < n_agents and placed:                   # pad to n_agents (⇒ slightly larger bands)
        positions.append(placed[i % len(placed)]); i += 1
    return positions[:n_agents]

def seed_band_positions_spread(fields, n_agents: int, hours_per_step: float, burn: float,
                               band_size: int = 25, territory_radius: int = 3, spread_radius: int = 2,
                               target_fill: float = 1.0, quality_frac: float = 0.5, rng=None):
    """Capacity-gated BANDED seeding (the founder-die-off fix): same per-biome, territory-spaced band SITES as
    `seed_band_positions`, but each band's members are SPREAD over the viable cells in its territory (Chebyshev
    `spread_radius`) instead of all stacked on the site cell — because one 100 km² cell feeds only ~1–8 foragers
    (Binford packing), so a 25-stacked band starves instantly. Each territory cell takes up to
    `max(1, floor(target_fill · S_cell/burn))` members (its carrying capacity); members beyond the territory's
    capacity spill onto its best cells (the founder mobile-reserve covers the transient overload). Returns a
    `placement_positions` list (len = n_agents); None if degenerate."""
    import numpy as np
    import random as _random
    rng = rng or _random.Random(0)
    forage = np.asarray(fields.forage_kcal, dtype=float)
    cap = forage * hours_per_step / burn               # agents each cell can feed (S/burn) [y,x]
    biome = np.asarray(fields.biome)
    land = np.asarray(fields.isWater) == 0
    n_bands = max(1, n_agents // band_size)
    bcap = {int(b): float(cap[land & (biome == b)].sum()) for b in np.unique(biome[land])}
    bcap = {b: c for b, c in bcap.items() if c > 0.0}
    if not bcap:
        return None
    total = sum(bcap.values())
    alloc = {b: max(1, round(n_bands * c / total)) for b, c in bcap.items()}
    placed_sites: list[tuple[int, int]] = []
    positions: list[tuple[int, int]] = []
    H, W = cap.shape
    for b in sorted(alloc, key=lambda k: -bcap[k]):
        mask = land & (biome == b)
        vmax = float(cap[mask].max())
        ys, xs = np.where(mask & (cap >= quality_frac * vmax))
        viable = list(zip(xs.tolist(), ys.tolist()))
        rng.shuffle(viable)
        cnt = 0
        for (sx, sy) in viable:
            if cnt >= alloc[b]:
                break
            if not all(max(abs(sx - px), abs(sy - py)) >= territory_radius for (px, py) in placed_sites):
                continue
            # gather this band's territory cells (land), best-capacity first
            terr = []
            for dy in range(-spread_radius, spread_radius + 1):
                for dx in range(-spread_radius, spread_radius + 1):
                    x, y = sx + dx, sy + dy
                    if 0 <= x < W and 0 <= y < H and land[y, x]:
                        terr.append((float(cap[y, x]), x, y))
            terr.sort(reverse=True)
            # fill each cell to its capacity (target_fill · S/burn), then spill the remainder onto the best cells
            remaining = band_size
            for (c, x, y) in terr:
                if remaining <= 0:
                    break
                k = min(remaining, max(1, int(c * target_fill)))
                positions.extend([(x, y)] * k)
                remaining -= k
            i = 0
            while remaining > 0 and terr:                 # spill overflow onto best cells (buffer covers it)
                _, x, y = terr[i % len(terr)]
                positions.append((x, y)); remaining -= 1; i += 1
            placed_sites.append((sx, sy))
            cnt += 1
    if not positions:
        return None
    i = 0
    while len(positions) < n_agents:
        positions.append(positions[i]); i += 1
    return positions[:n_agents]


# Default terrain knobs (production 100×100 grid)
_DEFAULT_KNOBS: dict = {
    "seedStr": "world42",
    "relief": 0.50,
    "rough": 0.50,
    "waterK": 0.30,
    "forestK": 0.55,
    "aridK": 0.40,
}



class TerrainWorld(mesa.Model):
    """Mesa model: C agents on a terrain kcal economy.

    Death-only by default (Blueprint A). Set `reproduction=True` for the A-3
    demographic layer. No SugarField in the C harvest path.
    """

    def __init__(
        self,
        n_agents: int,
        kcal_cfg: KcalEconomyConfig,
        terrain_knobs: dict | None = None,
        carbon_cfg=None,
        lh_cfg: LifeHistoryConfig | None = None,
        game_stream: bool = True,
        seed: int = 42,
        placement_positions: list[tuple[int, int]] | None = None,
        substrate_cfg: SubstrateConfig | None = None,
        harvest_field=None,   # CC-1: swap the rivalrous cell yield (default = terrain_field forage)
        # ── A-3 demographic layer (opt-in; PROVISIONAL shakedown params) ──
        reproduction: bool = False,
        repro_min_age: int = 15,
        birth_threshold: float = 80_000.0,
        birth_cost: float = 40_000.0,
        child_endowment: float = 40_000.0,
        p_birth: float = 0.10,
        # ── Demographic-stage core (opt-in): Siler mortality + IBI reproduction ──
        demography_cfg: DemographyConfig | None = None,
        # Founder MOBILE RESERVE (band-cohesion fix): each FOUNDER carries a private provision store of
        # `founder_buffer_steps × burn` kcal, drawn down to cover any per-step shortfall during the founding
        # transient (while the seeded band disperses over its territory to viable cells). Models the carried/
        # body-fat reserve a real band lives off the land with — the ~1-step wealth buffer alone can't bridge it.
        # Founder-only + decaying ⇒ no effect on steady state or prior validations. 0 = off (bit-exact).
        founder_buffer_steps: float = 0.0,
    ) -> None:
        super().__init__(seed=seed)

        knobs = terrain_knobs or {**_DEFAULT_KNOBS, "seedStr": f"world{seed}"}
        self._fields: WorldFields = generate_world(knobs)
        self._hours_per_step = kcal_cfg.foraging_hours_per_day * kcal_cfg.days_per_month
        self.terrain_field = TerrainField(self._fields, self._hours_per_step)
        self._kcal_cfg = kcal_cfg
        self._burn = kcal_cfg.burn_kcal_per_day * kcal_cfg.days_per_month
        self._reserve_full = kcal_cfg.reserve_full_kcal
        self._reserve_floor = kcal_cfg.reserve_floor_kcal
        self._game_stream = game_stream
        self._lh_cfg = lh_cfg
        # Newborn→adult life-history: if enable_life_history and no explicit lh_cfg, auto-build the MONTH-scaled
        # canonical (the class defaults are legacy YEARS — forage_age_min=15 would ramp childhood over 15 months).
        if self._lh_cfg is None and demography_cfg is not None and getattr(demography_cfg, "enable_life_history", False):
            self._lh_cfg = LifeHistoryConfig(forage_age_min=180, forage_age_max_offset=120)
        self._carbon_cfg = carbon_cfg
        self._placement_positions = placement_positions
        self._founder_buffer_steps = founder_buffer_steps
        self._substrate_cfg = substrate_cfg
        self._rivalrous = substrate_cfg is not None and substrate_cfg.enabled
        self._harvest_field = harvest_field if harvest_field is not None else self.terrain_field
        self._cell_store: dict[tuple[int, int], float] = {}   # collective band granary per cell (delayed-return; §4.5.11 S.1)
        self._cell_society: dict[tuple[int, int], str] = {}    # S.4 per-cell morphed society type (absent ⇒ egalitarian_forager)
        self._cell_settle: dict[tuple[int, int], int] = {}     # S.4 per-cell settlement timer (hysteresis)
        self._band_society: dict[int, str] = {}                # F.3c-2 per-BAND society type (keyed by band_id)
        self._band_settle: dict[int, int] = {}                 # F.3c-2 per-band settlement timer (hysteresis)
        self._band_surplus: dict[int, float] = {}              # F.3c-3 per-band surplus_frac (from the morph detector)
        self._cell_owner: dict[tuple[int, int], int] = {}      # econ-defensibility: owned cell → owner band_id (absent ⇒ open access)
        self._cell_claim: dict[tuple[int, int], tuple[int, int]] = {}  # econ-defensibility: cell → (claim strength, claimant band_id)
        self._claim_events_this_step: int = 0                  # instability diagnostic: defensibility contest events this step
        self._diag_rng = random.Random(1_234_567)              # dedicated RNG for read-outs ⇒ diagnostics never perturb self.random
        self._settlement_sites: dict[tuple[int, int], int] = {}   # aggregation-sedentism: active settlement site → hysteresis timer
        self._nearest_map: dict | None = None                     # PERF: cached cell→nearest-settlement map (per step); None = stale
        self._tier2_shock: float = 1.0                            # Layer 2b: current-year REGIONAL tier-2 yield shock multiplier (1.0 = no shock)
        self._shock_x: float = 0.0                                # Layer 2b: AR(1) latent (log-space, mean 0) driving the shock regime
        self._spot_cache = None                                   # agriculture: cached S_pot field = max(aquatic_food, cultivability?)
        self._settlement_soil: dict[tuple[int, int], float] = {}  # Layer B1: per-FARM-site soil stock ∈[0.05,1] (absent ⇒ 1, no depletion)
        self._aggl_R_cache = None                                 # agglomeration: cached intensive catchment-resource field R(c) = tier2·Σ_catchment S_pot (catchment mode)
        self._aggl_point_cache = None                             # agglomeration: cached POINT base A_cell = tier2·S_pot·cv_ref (point-superlinear mode, Branch A)
        self._forage_cap_cache = None                             # per-person forage cap field = forage_kcal · forage_cap_hours (absent ⇒ no cap)
        self._move_cost_cache = None                              # Stage 1b terrain move cost field = move_cost_kcal · cost (absent ⇒ free movement)
        self._site_cache = None                                   # Stage 1c catchment site-suitability field (central-place appraisal; absent ⇒ off)
        self._cv_cache = None                                     # emergent-band-size: per-cell foraging-return CV (biome σ/μ) for risk-pooling optimum
        self._band_opt_cache = None                               # emergent-band-size v3: per-cell risk-pooling optimum band g*(CV) — drives movement aggregation
        self._connubium_sizes: list[int] = []                     # CONNUBIUM diag: distinct-adult size of each mating pool that produced ≥1 marriage (last pairing phase)
        self._storable_frac_cache = None                          # resource-dependent per-cell storable fraction (Testart; absent ⇒ scalar)
        self._seasonal_amp = None                              # §4.5.10 cached per-cell biome seasonal-amplitude field (storability-gated morph)
        self._band_assabiyah: dict[int, float] = {}            # F.3c-3 per-band solidarity (Ibn Khaldun; drives tolerable size)
        self._band_leader_term: dict[int, float] = {}          # Stage 1: per-band leader-coherence contribution (diagnostic)
        self._band_repulsion: dict[int, float] = {}            # Stage 1b: per-band size-repulsion (scalar stress; diagnostic)
        self._band_malnutrition: dict[int, float] = {}         # M2: per-band malnutrition-fission pressure (diagnostic)
        self._band_starv_this_step: dict[int, int] = {}        # M2: starvation deaths per band THIS step (band_id → count)
        self._band_starv_ema: dict[int, float] = {}            # M2: EMA of per-band per-capita starvation rate (the M2 signal)
        # Stage 2 genealogy logger: a flat append-only event buffer (None ⇒ off). Pure observer (write-after-step).
        self._genealogy_log: list | None = (
            [] if (demography_cfg is not None and getattr(demography_cfg, "enable_genealogy_log", False)) else None)

        # demographic layer
        self._reproduction = reproduction
        self._repro_min_age = repro_min_age
        self._birth_threshold = birth_threshold
        self._birth_cost = birth_cost
        self._child_endowment = child_endowment
        self._p_birth = p_birth
        # demographic-stage core (opt-in): sex-specific Siler + IBI; modulators OFF here (2a-pre).
        self._demog = demography_cfg
        if demography_cfg is not None:
            self._siler = {"female": demography_cfg.siler("female"),
                           "male": demography_cfg.siler("male")}
            self._siler_both = demography_cfg.siler()
            land = self._fields.isWater == 0
            self._risk_ref = float(self._fields.risk[land].mean())  # mean land risk (normalization)
            # S2 pathogen reference NPP (Aché-forest biome → neutral); config 0 → mean land NPP of this terrain
            self._pathogen_npp_ref = (demography_cfg.pathogen_npp_ref if demography_cfg.pathogen_npp_ref > 0.0
                                      else float(self._fields.npp[land].mean()))
            self.a2_cap_hits = 0   # red-team m-4: agent-steps where the a2_eff cap binds

        self.agent_list: list[BaseAgent] = []
        self.occupied: set[tuple[int, int]] = set()
        self.step_count: int = 0
        # per-step demographic counters (read by diagnostics each step)
        self.births_this_step: int = 0
        self.deaths_starv_this_step: int = 0
        self.deaths_senesc_this_step: int = 0

        self._init_agents(n_agents, kcal_cfg, self._lh_cfg)   # self._lh_cfg = the (possibly auto-built) canonical lh

    # ── Initialisation ─────────────────────────────────────────────────────

    def _init_agents(
        self,
        n: int,
        kcal_cfg: KcalEconomyConfig,
        lh_cfg: LifeHistoryConfig | None,
    ) -> None:
        if self._placement_positions is not None:
            positions: list[tuple[int, int]] = list(self._placement_positions)
        else:
            land_cells = [
                (x, y)
                for y in range(N)
                for x in range(N)
                if self._fields.isWater[y, x] == 0
            ]
            n_place = min(n, len(land_cells))
            positions = self.random.sample(land_cells, n_place)

        for fid, pos in enumerate(positions):
            sex = "female" if self.random.random() < kcal_cfg.p_female else "male"
            agent = self._make_agent(sex=sex, lh_cfg=lh_cfg)
            agent.pos = pos
            if self._founder_buffer_steps > 0.0:         # carried mobile reserve for the founding transient
                agent._founder_store = self._founder_buffer_steps * self._burn
            agent._lineage = fid                         # each founder seeds a unique lineage (patriline tracking)
            if self._demog is not None and getattr(self._demog, "enable_genome", False):
                agent._genome = Genome.founder(self.random, loci=self._demog.genome_loci)   # unique founder signature
            if self._demog is not None:
                agent.age = self._sample_founder_age()   # staggered founders (stationary ∝ l(x))
            if getattr(agent, "use_cred_status", False) and self._demog.cred_seed_sigma > 0.0:
                s = self._demog.cred_seed_sigma          # founder status ~ lognormal(median 1) → the heritable hierarchy
                agent.cred = math.exp(self.random.normalvariate(0.0, s))
            self.agent_list.append(agent)
            self.occupied.add(pos)   # set: founder stacking (many agents, one cell) is allowed

        # F.3c-1: seed founder band affiliations by the initial spatial clusters (the seeded territory-bands).
        if self._demog is not None and getattr(self._demog, "enable_band_affiliation", False):
            self._next_band_id = 0
            for band in self.bands(self._demog.bonded_mate_radius):
                for a in band:
                    a._group.band_id = self._next_band_id
                self._next_band_id += 1

    def _sample_founder_age(self) -> int:
        """Staggered founder age (months) ∝ survivorship l(x) — the stationary / young pyramid."""
        if not hasattr(self, "_founder_age_pool"):
            p = self._siler_both
            ages = list(range(0, 90 * 12, 6))
            wts = [p.survivorship(a / 12.0) for a in ages]
            self._founder_age_pool = (ages, wts)
        ages, wts = self._founder_age_pool
        return int(self.random.choices(ages, weights=wts, k=1)[0])

    def _make_agent(self, sex: str, lh_cfg: LifeHistoryConfig | None) -> BaseAgent:
        from sic_games.agents.strategies.greedy import GreedyMaximizer

        decision: object
        if self._carbon_cfg is not None:
            decision = CarbonDecision(
                sigma_base=self._carbon_cfg.sigma_base,
                kappa=self._carbon_cfg.kappa,
                cred_scale=self._carbon_cfg.cred_scale,
                matthew_alpha=self._carbon_cfg.matthew_alpha,
                epsilon=self._carbon_cfg.epsilon,
                cred_bonus_per_participant=self._carbon_cfg.cred_bonus_per_participant,
                velocity_scale=self._carbon_cfg.velocity_scale,
                beta=self._carbon_cfg.status_amplification_beta,
            )
        else:
            decision = GreedyMaximizer()

        cost = KcalBurnModel(
            burn_kcal_per_day=self._kcal_cfg.burn_kcal_per_day,
            days_per_month=self._kcal_cfg.days_per_month,
        )

        agent = BaseAgent(
            model=self,
            vision=3,
            metabolism=1,        # unused in kcal economy; kept for compatibility
            max_age=self._kcal_cfg.lifespan_months,  # in steps=months (1 step=1 month LOCKED)
            initial_wealth=self._reserve_full,
            decision_logic=decision,
            perception_builder=LocalVisionPerception(),
            cost_model=cost,
            traits=TraitVector(phi=0.5, psi=0.5, c1=0.5, c2=0.5),
            strategy="carbon" if self._carbon_cfg else "greedy",
            lh_config=lh_cfg,
            reserve_floor=self._reserve_floor,
            sex=sex,
        )
        agent.months_since_birth = 10**9   # IBI counter (huge → first birth not blocked by refractory)
        agent.parity = 0
        # Carbon-on-substrate: when ON, the meat/contest weight reads `cred` (status), not `φ` (status_of hook).
        agent.use_cred_status = (self._carbon_cfg is not None and self._demog is not None
                                 and getattr(self._demog, "enable_cred_status", False))
        # Cred-vector (B+): `cred` = lineage facet; `prowess` = achieved facet (earned in step 2, EMA centered
        # at 1 = neutral reputation). The prowess facet joins the multiplicative contest weight only when
        # enabled (else lineage-only = R-18 exact; a uniform prowess cancels in the share ratio).
        agent.prowess = 1.0
        agent._use_prowess = (agent.use_cred_status and getattr(self._demog, "enable_prowess_facet", False))
        agent._founder_store = 0.0                 # founder mobile-reserve (set for founders in _init_agents); 0 for newborns
        agent._partner = None                      # F.3a: a FEMALE's husband link (None = unpaired). Males use _wives.
        agent._wives = set()                       # F.3a: a MALE's wives (≥1 ⇒ married; >1 ⇒ polygynous)
        agent._group = GroupVector()               # F.3c collective-identity vector (band_id assigned below / inherited)
        agent._mother = None                      # C.2b mother-link (set at IBI birth) for provisioning
        agent._father = None                      # B+ step 4: father-link (set at IBI birth via mate-choice)
        agent._lineage = None                     # lineage-tracking ID (founder-seeded; patrilineal descent)
        agent._genome = None                      # neutral-marker genome (population genetics; founder-seeded / inherited when enabled)
        # P6 social capital: relational standing — accrues with tenure among co-resident band, lost on leaving (Wiessner hxaro)
        agent._use_standing = self._demog is not None and getattr(self._demog, "enable_standing", False)
        agent._standing = (self._demog.standing_floor if agent._use_standing else 0.0)
        agent._standing_band = None               # band the standing was built in (change ⇒ outsider penalty)
        agent._condition = 1.0                    # S0 body-condition / immune competence (EMA of nutrition)
        agent._fed_reserve = self._reserve_full   # post-harvest reserve = nutritional status; synergy /
        #   energetic-fertility read THIS, not the post-burn trough (= reserve_full − burn for any fed agent)
        return agent

    # ── Step ───────────────────────────────────────────────────────────────

    def step(self) -> None:
        self.step_count += 1
        if hasattr(self._harvest_field, "set_step"):     # climate: advance the time-varying field clock (C.1)
            self._harvest_field.set_step(self.step_count)
        self.births_this_step = 0
        self.deaths_starv_this_step = 0
        self.deaths_senesc_this_step = 0
        self._band_starv_this_step = {}               # M2: reset per-band starvation-death tally for this step
        self.starv_cred_this_step: list[float] = []   # diagnostic: cred of agents lost to starvation this step
        self.starv_status_this_step: list[float] = []  # diagnostic: combined status (cred·prowess) at starvation
        self.prov_young_maternal = 0.0   # diagnostic: kcal provisioned to <3-yr children by mother (Marlowe calib)
        self.prov_young_paternal = 0.0   # diagnostic: "" by father (male share = paternal/(maternal+paternal))
        self.mate_pairs_this_step: list[tuple[float, float]] = []   # (mother status, father status) — assortment
        self._claim_events_this_step = 0             # instability diagnostic: reset the defensibility-contest flow

        if self._rivalrous:
            self._step_rivalrous()
        else:
            agents = list(self.agent_list)
            self.random.shuffle(agents)
            for agent in agents:
                if not agent.alive:
                    continue
                self._step_agent(agent)

        # Prune dead agents. `agent.remove()` deregisters the corpse from Mesa's `self.agents`
        # AgentSet too — without it, dead agents linger frozen at their death cell and any metric
        # read off `self.agents` (e.g. the band tests) silently counts CORPSES as live population.
        # The dynamics already run off `agent_list` (live), so this is a measurement-correctness fix.
        for a in self.agent_list:
            if not a.alive:
                self.occupied.discard(a.pos)
                self._log_genea("death", a)                # Stage 2: observer log (band_id/lineage at death)
                # F.3a bond dissolution on death: a dead WIFE leaves her husband's _wives; a dead HUSBAND widows
                # ALL his wives (they re-enter the pairing pool — serial monogamy / re-marriage).
                if a._partner is not None:
                    a._partner._wives.discard(a); a._partner = None
                for w in a._wives:
                    w._partner = None
                a._wives.clear()
                a.remove()
        self.agent_list = [a for a in self.agent_list if a.alive]

        # Demographic layer: pairing (F.3a) then births (opt-in)
        if self._demog is not None:
            if getattr(self._demog, "enable_pair_bonds", False):
                self._connubium_sizes = []        # CONNUBIUM diag: reset; the pairing method refills for this phase
                if getattr(self._demog, "enable_adaptive_connubium", False):
                    self._do_connubium()          # Cut 2: per-seeker expanding search to eligibility (emergent scale)
                elif getattr(self._demog, "enable_marriage_aggregation", False):
                    self._do_gathering()          # seasonal cross-band gathering replaces daily within-band pairing
                else:
                    self._do_pairing()
            if getattr(self._demog, "enable_band_affiliation", False):
                self._maintain_bands()
                if getattr(self._demog, "enable_village_budding", False):
                    self._maintain_village_budding()   # Bandy 2004: large village sheds a rival-led daughter (relocates)
            self._do_births_ibi()
        elif self._reproduction:
            self._do_births()
        self.occupied = {a.pos for a in self.agent_list}
        self._update_standing()          # P6: tenure builds standing; leaving/isolation forfeits it (ready for next harvest)

    def _update_defensibility_claims(self) -> None:
        """Economic-defensibility (Dyson-Hudson & Smith 1978) claim maintenance. A cell is CLAIMABLE when its
        resource is dense+predictable (aquatic_food/S_pot ≥ defensibility_min — aquatic is high-π by construction,
        the diffuse interior ≈ 0 so it never qualifies). A band that LEAD-occupies a claimable cell with ≥
        defensibility_claim_min members builds a claim (+1/step); at ≥ defensibility_claim_dwell it OWNS the cell.
        The incumbent owner keeps priority while present; a challenger erodes the claim (−1); ownership LAPSES
        (hysteresis) when the claim decays to 0. Resource-agnostic: reads aquatic_food now, cultivability later."""
        D = getattr(self._fields, "aquatic_food", None)
        if D is None:
            return
        dmin = self._demog.defensibility_min
        dwell = self._demog.defensibility_claim_dwell
        claim_min = self._demog.defensibility_claim_min
        cell_bands: dict[tuple[int, int], dict[int, int]] = {}
        for a in self.agent_list:
            x, y = a.pos
            if D[y, x] >= dmin:
                d = cell_bands.setdefault((x, y), {})
                b = a._group.band_id
                d[b] = d.get(b, 0) + 1
        for cell in set(cell_bands) | set(self._cell_claim):
            bands = cell_bands.get(cell, {})
            owner = self._cell_owner.get(cell)
            strength, who = self._cell_claim.get(cell, (0, None))
            # who qualifies to hold this step: the incumbent owner if still present, else the leading band
            holder = None
            if owner is not None and bands.get(owner, 0) >= claim_min:
                holder = owner
            elif bands:
                lead = max(bands, key=bands.get)
                if bands[lead] >= claim_min:
                    holder = lead
            if holder is not None and (who is None or who == holder):
                strength += 1; who = holder
            elif holder is not None:            # a challenger erodes the accrued claim, then takes it over
                strength -= 1
                self._claim_events_this_step += 1   # instability: an active contest over a defensible cell
                if strength <= 0:
                    strength, who = 1, holder
            else:                               # nobody qualifies → decay
                strength -= 1
            if who is not None and strength >= dwell:
                self._cell_owner[cell] = who
            if strength <= 0:
                self._cell_claim.pop(cell, None)
                self._cell_owner.pop(cell, None)
            else:
                self._cell_claim[cell] = (min(strength, dwell + 6), who)  # cap ⇒ ~6-step release hysteresis

    def _torus_cheby(self, ax: int, ay: int, bx: int, by: int) -> int:
        """Chebyshev distance on the toroidal grid."""
        dx = abs(ax - bx); dy = abs(ay - by)
        return max(min(dx, N - dx), min(dy, N - dy))

    def _nearest_settlement(self, pos: tuple[int, int]) -> tuple[int, int] | None:
        """The active settlement within settle_radius of `pos` (nearest, tie-broken by settlement INSERTION order);
        None if outside all. PERF: reads a per-step cell→nearest-settlement map (built once in O(n_sites·rad²))
        instead of scanning EVERY settlement for EVERY agent — the old O(agents·n_sites) that dominated runtime once
        budding creates hundreds of settlements. Bit-exact: the map's tie-break = first-inserted site at the minimum
        (torus-Chebyshev) distance, identical to the old scan."""
        if getattr(self, "_nearest_map", None) is None:
            self._nearest_map = self._build_nearest_map()
        return self._nearest_map.get(pos)

    def _build_nearest_map(self) -> dict:
        """cell → nearest active settlement (within settle_radius). Each site stamps its (2·rad+1)² neighbourhood,
        earlier sites winning distance ties (insertion order) — so a lookup reproduces the old nearest-scan exactly."""
        rad = self._demog.settle_radius
        best: dict = {}                                          # cell → (site, dist)
        for site in self._settlement_sites:                     # insertion order preserves the tie-break
            sx, sy = site
            for dx in range(-rad, rad + 1):
                for dy in range(-rad, rad + 1):
                    d = dx if dx >= 0 else -dx
                    ady = dy if dy >= 0 else -dy
                    if ady > d:
                        d = ady
                    cell = ((sx + dx) % N, (sy + dy) % N)
                    cur = best.get(cell)
                    if cur is None or d < cur[1]:               # strictly closer wins; ties keep the earlier site
                        best[cell] = (site, d)
        return {c: v[0] for c, v in best.items()}

    def _toward(self, pos: tuple[int, int], site: tuple[int, int]) -> tuple[int, int]:
        """One cardinal step from `pos` toward `site` on the torus (larger axis first); stays if blocked by water.
        Layer 2 residence pin: settled members converge onto the SINGLE site cell (a village « one 100 km² cell)."""
        x, y = pos; sx, sy = site
        if (x, y) == (sx, sy):
            return pos
        def _dir(a, b):
            raw = (b - a) % N
            return 0 if raw == 0 else (1 if raw <= N - raw else -1)
        dxs, dys = _dir(x, sx), _dir(y, sy)
        dxd = min((sx - x) % N, (x - sx) % N); dyd = min((sy - y) % N, (y - sy) % N)
        water = self._fields.isWater
        cands = []
        if dxd >= dyd and dxs: cands.append(((x + dxs) % N, y))
        if dys: cands.append((x, (y + dys) % N))
        if dxd < dyd and dxs: cands.append(((x + dxs) % N, y))
        for (nx, ny) in cands:
            if water[ny, nx] == 0:
                return (nx, ny)
        return pos

    def _s_pot_field(self):
        """RESOURCE-AGNOSTIC settlement-resource potential S_pot. = aquatic_food (fishery); with enable_agriculture,
        = max(aquatic_food, cultivability) so FARMING villages form on fertile land via the same machinery. Cached
        (static fields). Default (no agriculture) ⇒ aquatic_food ⇒ bit-exact."""
        if self._spot_cache is None:
            aq = getattr(self._fields, "aquatic_food", None)
            if aq is None:
                return None
            if self._demog is not None and getattr(self._demog, "enable_agriculture", False):
                cult = getattr(self._fields, "cultivability", None)
                if cult is not None:
                    import numpy as np
                    self._spot_cache = np.maximum(aq, cult)
                else:
                    self._spot_cache = aq
            else:
                self._spot_cache = aq
        return self._spot_cache

    def _forage_cap_field(self):
        """Per-person forage cap = forage_kcal · forage_cap_hours (the biome return-rate × work hours — the most one
        forager can harvest). Cached. None if no forage_kcal field."""
        if self._forage_cap_cache is None:
            fk = getattr(self._fields, "forage_kcal", None)
            if fk is None:
                return None
            self._forage_cap_cache = fk * self._demog.forage_cap_hours
        return self._forage_cap_cache

    def _move_cost_field(self):
        """Stage 1b per-cell terrain MOVE COST (kcal) = move_cost_kcal · cost, where `cost` ∈[0.15,1] is the terrain
        traversal difficulty (slope/elev-driven, water=1). Perceived in the IFD utility and drained at metabolism when
        an agent moves. Cached. None if no cost field."""
        if self._move_cost_cache is None:
            ct = getattr(self._fields, "cost", None)
            if ct is None:
                return None
            self._move_cost_cache = ct * self._demog.move_cost_kcal
        return self._move_cost_cache

    def _site_suitability_field(self):
        """Stage 1c catchment SITE-VALUE field (central-place appraisal). value(c) = Σ_{|d|≤radius} S_pot(c')·
        exp(−λ·dist·(0.5+cost(c'))) — catchment resource potential discounted by cost-distance (rugged/far cells
        contribute less). Normalized to [0,1] and scaled by site_gain·BURN → a PERCEIVED per-cell central-place bonus
        (a static gradient toward prime real-estate; Kennett-Winterhalder IFD-suitability). Cached. None if no S_pot/cost."""
        if self._site_cache is None:
            sp = self._s_pot_field()
            ct = getattr(self._fields, "cost", None)
            if sp is None or ct is None:
                return None
            import numpy as np
            r = self._demog.site_radius
            lam = self._demog.site_lambda
            acc = np.zeros_like(sp)
            for dy in range(-r, r + 1):
                for dx in range(-r, r + 1):
                    d = max(abs(dx), abs(dy))
                    if d == 0:
                        acc += sp                               # the site cell itself (no travel)
                        continue
                    rsp = np.roll(np.roll(sp, dy, axis=0), dx, axis=1)
                    rct = np.roll(np.roll(ct, dy, axis=0), dx, axis=1)
                    acc += rsp * np.exp(-lam * d * (0.5 + rct))  # far/rugged catchment cells contribute less
            mx = float(acc.max())
            norm = acc / mx if mx > 0 else acc
            self._site_cache = self._demog.site_gain * self._burn * norm
        return self._site_cache

    def _return_cv_field(self):
        """Emergent-band-size: per-cell foraging-return CV = σ/μ of the total (forage+game) return, from the per-biome
        Return-Rate Tables (FORAGE/GAME_KCAL TARGETS+STD). Drives the risk-pooling optimum band g*=(CV/cv_safe)². Cached."""
        if self._cv_cache is None:
            from sic_games.terrain import (FORAGE_KCAL_TARGETS, FORAGE_KCAL_STD, GAME_KCAL_TARGETS, GAME_KCAL_STD,
                                           DEFAULT_STD_FRAC)
            biome = getattr(self._fields, "biome", None)
            if biome is None:
                return None
            import numpy as np
            cv = np.full(biome.shape, 0.5, dtype=float)
            for code in np.unique(biome):
                fm = FORAGE_KCAL_TARGETS.get(int(code), 0.0); fs = FORAGE_KCAL_STD.get(int(code), DEFAULT_STD_FRAC * fm)
                gm = GAME_KCAL_TARGETS.get(int(code), 0.0); gs = GAME_KCAL_STD.get(int(code), DEFAULT_STD_FRAC * gm)
                tot_m = fm + gm
                if tot_m > 0:
                    cv[biome == code] = math.sqrt(fs * fs + gs * gs) / tot_m   # combined return CV (independent forage+game)
            cv_min = getattr(self._demog, "cv_min", 0.0)                       # v2: floor the CV (correct 10%-default data gaps)
            if cv_min > 0.0:
                np.maximum(cv, cv_min, out=cv)
            self._cv_cache = cv
        return self._cv_cache

    def _band_optimum_field(self):
        """Emergent-band-size v3: per-cell risk-pooling optimum band g* = clamp((CV/cv_safe)², band_size_min,
        band_split_size). Used as the group_safety AGGREGATION saturation scale in movement (so agents cluster UP TO
        g* — high-variance biomes grow bigger bands) AND as the fission-threshold floor. Cached. None if no CV field."""
        if self._band_opt_cache is None:
            cv = self._return_cv_field()
            if cv is None:
                return None
            import numpy as np
            cfg = self._demog
            g = (cv / cfg.cv_safe) ** 2
            self._band_opt_cache = np.clip(g, float(cfg.band_size_min), float(cfg.band_split_size))
        return self._band_opt_cache

    def _storable_frac_field(self):
        """Resource-dependent per-cell storable fraction (Testart): weighted average of the local resource mix's
        storabilities = Σ(resource·s_r)/Σ(resource) over {grain=cultivability, fish=aquatic, forage, game}. Grain/
        fishing cells → high (accumulate granaries → sedentism); fresh-forage cells → low (can't store → mobile).
        Cached. None if no cultivability/forage. Falls back to the scalar storable_fraction where the mix is empty."""
        if self._storable_frac_cache is None:
            from sic_games.demography import STORABILITY_BY_RESOURCE as SB
            f = self._fields
            cult = getattr(f, "cultivability", None)
            forage = getattr(f, "forage", None)
            if cult is None or forage is None:
                return None
            import numpy as np
            aq = getattr(f, "aquatic_food", None)
            game = getattr(f, "game", None)
            aq = aq if aq is not None else np.zeros_like(cult)
            game = game if game is not None else np.zeros_like(cult)
            num = cult * SB["grain"] + aq * SB["fish"] + forage * SB["forage"] + game * SB["game"]
            den = cult + aq + forage + game
            sf = np.full_like(cult, self._demog.storable_fraction, dtype=float)
            np.divide(num, den, out=sf, where=den > 0)          # scalar fallback where the resource mix is empty (water)
            self._storable_frac_cache = sf
        return self._storable_frac_cache

    def _aggl_R_field(self):
        """Agglomeration: the intensive CATCHMENT-resource field R(c) = aggl_tier2 · Σ_{catchment} (S_pot · cv_ref),
        where S_pot ∈ [0,1] is the cultivability/aquatic GATE and cv_ref = forage_kcal · forage_cap_hours is the
        per-person REALIZABLE yield (kcal — the same scale as the forage cap). So R lives in realistic harvest units
        and aggl_tier2 is a dimensionless INTENSIFICATION MULTIPLE (~1–5: intensive land yields a few× foraging per
        area). Cached (static). None if no S_pot or forage_kcal.

        [Bug-fix 2026-07: the previous form multiplied S_pot by `harvest_field.level()`, which returns kcal CAPACITY
        (~10^6), not a 0–1 fraction — so R blew up to ~54M (≈18×S) and the intensive term SWAMPED the forage cap,
        re-rewarding lone/spread agents (L(1)·54M ≈ 900k ≫ cap). Anchoring to cv_ref restores L(1)≈0.]"""
        if self._aggl_R_cache is None:
            sp = self._s_pot_field()
            fk = getattr(self._fields, "forage_kcal", None)
            if sp is None or fk is None:
                return None
            import numpy as np
            cv_ref = fk * self._demog.forage_cap_hours           # per-person realizable yield (kcal) — the cap's scale
            weighted = sp * cv_ref                               # cultivability-gated realizable yield (kcal)
            r = self._demog.aggl_catchment_radius
            acc = np.zeros_like(weighted)
            for dy in range(-r, r + 1):
                for dx in range(-r, r + 1):
                    acc += np.roll(np.roll(weighted, dy, axis=0), dx, axis=1)
            self._aggl_R_cache = self._demog.aggl_tier2 * acc
        return self._aggl_R_cache

    def _aggl_point_base_field(self):
        """POINT agglomeration base A_cell = aggl_tier2 · S_pot · cv_ref (Bettencourt-correct, Branch A). The cell's OWN
        intensive output scales super-linearly with its occupancy: O(n) = A_cell·n^β ⇒ per-capita A_cell·n^(β-1) RISES
        with co-location (β>1). A_cell is a SINGLE cell (a POINT return — no catchment convolution), cultivability-gated,
        in cap-kcal units so aggl_tier2 is a dimensionless intensification multiple. Cached. None if no S_pot/forage_kcal."""
        if self._aggl_point_cache is None:
            sp = self._s_pot_field()
            fk = getattr(self._fields, "forage_kcal", None)
            if sp is None or fk is None:
                return None
            cv_ref = fk * self._demog.forage_cap_hours           # per-person realizable yield (kcal) — the cap's scale
            self._aggl_point_cache = self._demog.aggl_tier2 * sp * cv_ref
        return self._aggl_point_cache

    def _settlement_catchment_yield(self, site: tuple[int, int]) -> float:
        """Layer 2: the settlement-UNLOCKED intensive tier-2 yield, pooled over the catchment (residence ≠ foraging).
        RESOURCE-AGNOSTIC — reads S_pot (= max(aquatic_food, cultivability)). Gated: only settlement sites get it,
        so a mobile band passing a reach gets only the tier-1 cell return (explains GATE-3)."""
        sp = self._s_pot_field()
        if sp is None:
            return 0.0
        rad = self._demog.settle_catchment_radius
        sx, sy = site; tot = 0.0
        for dy in range(-rad, rad + 1):
            for dx in range(-rad, rad + 1):
                tot += sp[(sy + dy) % N, (sx + dx) % N]
        return self._demog.settle_tier2_yield * tot

    def _settlement_carrying_capacity(self, site: tuple[int, int]) -> float:
        """R-63 resource ceiling: the sustainable food a settlement's CATCHMENT can yield = Σ of the harvest field's
        cell yield over the catchment. A village's total food (forage + tier-2 + agglomeration) is capped at this — it
        cannot out-produce its land. Cached per step (the field is set_step'd)."""
        tf = self._harvest_field
        rad = self._demog.settle_catchment_radius
        sx, sy = site
        tot = 0.0
        W = getattr(tf, "width", N); H = getattr(tf, "height", N)
        for dy in range(-rad, rad + 1):
            for dx in range(-rad, rad + 1):
                tot += tf.level((sx + dx) % W, (sy + dy) % H)
        return self._demog.catchment_ceiling_mult * tot

    def _maintain_settlements(self) -> None:
        """Aggregation-sedentism lifecycle: an active settlement PERSISTS while ≥ settle_min_pool people are within
        settle_radius of its site (membership is emergent proximity — robust to band fission/fusion); otherwise its
        hysteresis timer decays and it DISSOLVES (the pool disperses back to mobile bands). Formation is seasonal (in
        `_do_gathering`); this runs every step to hold or release."""
        if not self._settlement_sites:
            return
        rad = self._demog.settle_radius
        min_pool = self._demog.settle_min_pool
        occ: dict = {}                                    # PERF: cell → occupancy; sum each site's neighbourhood
        for a in self.agent_list:                         # instead of O(agents·n_sites) torus-distance checks
            occ[a.pos] = occ.get(a.pos, 0) + 1
        for site in list(self._settlement_sites):
            sx, sy = site
            n = 0
            for dx in range(-rad, rad + 1):
                for dy in range(-rad, rad + 1):
                    n += occ.get(((sx + dx) % N, (sy + dy) % N), 0)
            if n >= min_pool:
                self._settlement_sites[site] = self._demog.settle_release_steps    # refresh
            else:
                self._settlement_sites[site] -= 1
                if self._settlement_sites[site] <= 0:
                    self._settlement_sites.pop(site, None)
        self._nearest_map = None                          # settlements may have dissolved → invalidate the cache

    def _update_standing(self) -> None:
        """P6 social capital. Standing accrues with TENURE among co-resident band-mates (Wiessner 1977: ~1 yr of
        reciprocal `hxaro` exchange before a partnership is 'firm'; the network is the bad-year insurance) and is
        largely LOST on leaving the community — a band change, or isolation from one's band. Because `base_status`
        weights the harvest contest, the granary draw AND mate choice, departure is a real FITNESS cost: the village
        anchor. Dispersal therefore becomes SELECTIVE (low-standing juniors forfeit little and leave; established/
        high-standing stay). Off ⇒ no-op (bit-exact)."""
        cfg = self._demog
        if cfg is None or not getattr(cfg, "enable_standing", False):
            return
        r, pen, fl = cfg.standing_tenure_rate, cfg.standing_leave_penalty, cfg.standing_floor
        bc: dict[tuple, int] = {}                       # (band_id, cell) → members present
        for a in self.agent_list:
            k = (a._group.band_id, a.pos)
            bc[k] = bc.get(k, 0) + 1
        for a in self.agent_list:
            b = a._group.band_id
            if a._standing_band != b:                   # joined / changed community → arrive an outsider
                a._standing = max(fl, a._standing * pen)
                a._standing_band = b
                continue
            x, y = a.pos
            near = -1                                   # 3×3 co-band members, excluding self
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    near += bc.get((b, (x + dx, y + dy)), 0)
            if near > 0:
                a._standing += r * (1.0 - a._standing)  # embedded → hxaro ties deepen (saturating)
            else:
                a._standing = max(fl, a._standing * pen)   # isolated from the community → ties lapse

    def _update_settlement_soil(self) -> None:
        """Layer B1 soil depletion: a FARM settlement (cultivability > aquatic at its site) degrades a per-site SOIL
        stock under farming pressure (members/catchment carrying); tier-2 farm yield × soil (applied in the harvest).
        Slow fallow regrowth — a DEPLETED site recovers only over a long fallow (whether still settled or abandoned,
        so an abandoned field heals for later re-settlement). FISHERIES (aquatic-dominant) are exempt → soil stays 1
        → R-53 stable villages unchanged. Soil ∈ [SOIL_FLOOR=0.05, 1]."""
        cfg = self._demog
        cult = getattr(self._fields, "cultivability", None)
        if cult is None:
            return
        aq = getattr(self._fields, "aquatic_food", None)
        rad = cfg.settle_radius
        r = cfg.soil_regrow_per_yr / 12.0
        carry = cfg.soil_carry_per_cell * (2 * cfg.settle_catchment_radius + 1) ** 2
        counts: dict[tuple[int, int], int] = {}
        for a in self.agent_list:
            ax, ay = a.pos
            for s in self._settlement_sites:
                if self._torus_cheby(ax, ay, s[0], s[1]) <= rad:
                    counts[s] = counts.get(s, 0) + 1
        dep = cfg.soil_deplete_frac / 12.0                     # per-step exhaustion at pressure 1
        active_farm = set()
        for s in self._settlement_sites:
            if aq is not None and aq[s[1], s[0]] >= cult[s[1], s[0]]:
                continue                                       # aquatic-dominant → a FISHERY, exempt (R-53)
            active_farm.add(s)
            pressure = counts.get(s, 0) / carry if carry > 0 else 0.0
            # SWIDDEN: continuous cropping EXHAUSTS the soil (no regrowth while farmed) → progressive decline to the
            # floor → yield crashes → bust/relocate. (Landesque capital, B2, is what damps this to a sustainable
            # equilibrium — the intensification path.) Regrowth happens only on FALLOW (below).
            soil = self._settlement_soil.get(s, 1.0) - dep * pressure
            self._settlement_soil[s] = min(1.0, max(0.05, soil))
        for s in list(self._settlement_soil):                  # FALLOW: abandoned (or non-farm) sites heal slowly
            if s not in active_farm:
                soil = self._settlement_soil[s] + r * (1.0 - self._settlement_soil[s])
                if soil >= 0.999:
                    self._settlement_soil.pop(s, None)
                else:
                    self._settlement_soil[s] = soil

    def _step_rivalrous(self) -> None:
        """Stage-6.0a multi-occupancy substrate on the terrain field (forage-only).
        Diffusion movement (per-capita yield) → per-cell harvest split → metabolism."""
        self._nearest_map = None                      # PERF: rebuild the cell→nearest-settlement map fresh this step
        sc = self._substrate_cfg
        kappa = sc.contest_exponent
        phi_eps = sc.phi_epsilon
        tf = self._harvest_field   # CC-1 capacity field (or terrain forage if none)

        # 1. occupancy maps
        occ_count: dict[tuple[int, int], int] = {}
        occ_wsum: dict[tuple[int, int], float] | None = {} if kappa > 0.0 else None
        for a in self.agent_list:
            occ_count[a.pos] = occ_count.get(a.pos, 0) + 1
            if occ_wsum is not None:
                wt = base_status(a, phi_eps) ** kappa if a.strategy == "carbon" else 1.0
                occ_wsum[a.pos] = occ_wsum.get(a.pos, 0.0) + wt

        # 1b. Economic-defensibility claim maintenance (Dyson-Hudson & Smith): update which bands OWN which
        # defensible cells from the CURRENT occupancy, so movement (step 2) reads a fresh owner map. Off ⇒ owner=None.
        def_on = (self._demog is not None and getattr(self._demog, "enable_economic_defensibility", False)
                  and getattr(self._fields, "aquatic_food", None) is not None)
        if def_on:
            self._update_defensibility_claims()
            cell_owner = self._cell_owner
            def_excl = self._demog.defensibility_exclusion
            def_teth = self._demog.defensibility_tether
            # CONSOLIDATE (Stage A): each band's PRIMARY reach = its RICHEST owned cell (tether target), so members
            # converge on ONE central place rather than scattering across every plot the band happens to hold.
            aqf = self._fields.aquatic_food
            best: dict[int, tuple[float, tuple[int, int]]] = {}
            for c, b in cell_owner.items():
                val = float(aqf[c[1], c[0]])
                cur = best.get(b)
                if cur is None or val > cur[0] or (val == cur[0] and c < cur[1]):
                    best[b] = (val, c)
            band_primary = {b: c for b, (_, c) in best.items()}
        else:
            cell_owner, def_excl, def_teth, band_primary = None, 1.0, 1.0, None

        # 1c. Aggregation-sedentism: hold/release active settlements (formed seasonally in _do_gathering), then the
        # movement below pins members within a settlement's radius onto its site (cohesion → site, pool scale).
        # Agglomeration economics (grand-unification rework): the intensive catchment-resource field + curve params,
        # passed into IFD (perceived) and added in the harvest (realized). aggl_on=False ⇒ R_field=None ⇒ bit-exact.
        aggl_on = self._demog is not None and getattr(self._demog, "enable_agglomeration", False)
        aggl_mode = getattr(self._demog, "aggl_mode", "point") if aggl_on else "point"
        # POINT (Bettencourt-correct): A_cell·n^(β-1) per capita on the cell's OWN output. CATCHMENT (falsified): R·L(n)/n.
        aggl_R = (self._aggl_point_base_field() if aggl_mode == "point" else self._aggl_R_field()) if aggl_on else None
        aggl_a = (self._demog.aggl_beta if aggl_mode == "point" else self._demog.aggl_alpha) if aggl_on else 1.15
        aggl_h = self._demog.aggl_half if aggl_on else 100.0
        # Per-person forage cap (solitude fix): a forager harvests at most forage_kcal·work_hours, not the whole cell.
        cap_on = self._demog is not None and getattr(self._demog, "enable_forage_cap", False)
        fcap = self._forage_cap_field() if cap_on else None
        # Stage 1b terrain move cost: perceived in IFD (move_cost_field) + drained at metabolism for movers. Off ⇒ None.
        tmc_on = self._demog is not None and getattr(self._demog, "enable_terrain_move_cost", False)
        mcf = self._move_cost_field() if tmc_on else None
        # Stage 1c catchment site-appraisal: a static central-place suitability gradient perceived in IFD. Off ⇒ None.
        site_on = self._demog is not None and getattr(self._demog, "enable_site_appraisal", False)
        sfield = self._site_suitability_field() if site_on else None
        # emergent band size v3: the per-cell risk-pooling optimum g*(CV) drives the group_safety AGGREGATION scale
        # (agents cluster up to g* → high-variance biomes grow bigger bands). Off ⇒ fixed group_safety_scale.
        eb_on = self._demog is not None and getattr(self._demog, "enable_emergent_band_size", False)
        band_opt = self._band_optimum_field() if eb_on else None
        # P6 STANDING: the cells where each band is present = "home" (co-residence). Moving off them means arriving as
        # an outsider with a newcomer's contest weight → a smaller share. Only bites under a contest (kappa>0).
        standing_on = self._demog is not None and getattr(self._demog, "enable_standing", False) and kappa > 0.0
        # P1 store anchor: the band's COLLECTIVE granary the mover would abandon (Testart delayed-return).
        store_on = self._demog is not None and getattr(self._demog, "enable_store_anchor", False)
        st_field = self._cell_store if store_on else None
        st_gain = self._demog.store_anchor_gain if store_on else 0.0
        st_hor = self._demog.store_anchor_horizon if store_on else 24.0
        # "home" = the cells where the agent's band is present. Needed by BOTH P6 (newcomer contest weight) and P1
        # (no claim on a stranger's granary).
        home_by_band: dict[int, set] = {}
        if standing_on or store_on:
            for a in self.agent_list:
                home_by_band.setdefault(a._group.band_id, set()).add(a.pos)

        settle_on = self._demog is not None and getattr(self._demog, "enable_aggregation_sedentism", False)
        # B (R-63): settlement scalar stress — per-site village population, so an over-crowded egalitarian village
        # repels newcomers (Johnson 1982; dissipated by the site's society factor). Precompute the site populations.
        settle_ss_on = settle_on and getattr(self._demog, "enable_settlement_scalar_stress", False)
        settle_pop: dict = {}
        if settle_ss_on:
            srad = self._demog.settle_radius
            for a in self.agent_list:
                s = self._nearest_settlement(a.pos)
                if s is not None:
                    settle_pop[s] = settle_pop.get(s, 0) + 1
        if settle_on:
            self._maintain_settlements()
            if getattr(self._demog, "enable_soil_depletion", False):
                self._update_settlement_soil()   # Layer B1: farm sites degrade their soil (fisheries exempt)
            # Layer 2b SHOCK: redraw the REGIONAL tier-2 yield multiplier once per year (mean-preserving lognormal —
            # same draw as game meat-cv); a low year = a bad run/drought that storage must buffer. Held within the year.
            if getattr(self._demog, "enable_tier2_shock", False) and self.step_count % self._demog.aggregation_period == 0:
                cv = self._demog.shock_cv
                if cv > 0.0:
                    sig2 = math.log(1.0 + cv * cv)                  # target STATIONARY log-variance (marginal CV = shock_cv, any ρ)
                    rho = self._demog.shock_rho
                    eps = self.random.normalvariate(0.0, math.sqrt(sig2 * (1.0 - rho * rho)))
                    self._shock_x = rho * self._shock_x + eps       # AR(1): ρ=0 ⇒ IID (bit-identical to the prior draw)
                    self._tier2_shock = math.exp(self._shock_x - 0.5 * sig2)   # mean-preserving
                else:
                    self._tier2_shock = 1.0

        # 2. diffusion movement (per-capita-yield, self-limiting)
        # (Storage-tethering RETIRED 2026-06-29: the band-aid that froze stocked bands in place to force packing
        # is superseded by the emergent-bands grouping drives + bonded mating — the morph now fires from emergent
        # density+storage alone, validated in run_3h. MODEL_SPEC §4.8.5.)
        fam_move = self._demog is not None and getattr(self._demog, "enable_pair_bonds", False)
        # Central-place co-movement fixes (R-41): anticipation (root foresees its family) + footprint (followers
        # scatter near the head rather than exact-snap). Build the per-root follower count once.
        anticipate = fam_move and getattr(self._demog, "comove_anticipate", False)
        footprint = getattr(self._demog, "comove_footprint", 0) if fam_move else 0
        footprint_scaled = fam_move and getattr(self._demog, "comove_footprint_scaled", False)
        footprint_on = footprint > 0 or footprint_scaled
        fp_npp = getattr(self._fields, "npp_gm2", None) if footprint_scaled else None
        followers_by_root: dict = {}
        if anticipate:
            for a in self.agent_list:
                h = self._family_head(a)
                if h is not None:
                    followers_by_root[h] = followers_by_root.get(h, 0) + 1
        # §4.8.19 productivity-scaled mobility: per-agent STRIDE from the STATIC local NPP (Kelly/Binford ∝1/NPP).
        mobility_on = self._demog is not None and getattr(self._demog, "enable_productivity_mobility", False)
        npp_gm2 = getattr(self._fields, "npp_gm2", None) if mobility_on else None
        water_mask = self._fields.isWater if mobility_on else None
        # F.3c-1 band cohesion: pull each mover (family-root / unpaired adult) toward its band's centroid.
        coh_str = (self._demog.band_cohesion if (self._demog is not None
                   and getattr(self._demog, "enable_band_affiliation", False)) else 0.0)
        band_centroid: dict[int, tuple[int, int]] = {}
        if coh_str > 0.0:
            sums: dict[int, list] = {}
            for a in self.agent_list:
                s = sums.setdefault(a._group.band_id, [0, 0, 0])
                s[0] += a.pos[0]; s[1] += a.pos[1]; s[2] += 1
            band_centroid = {b: (round(s[0] / s[2]), round(s[1] / s[2])) for b, s in sums.items()}
        agents = list(self.agent_list)
        self.random.shuffle(agents)

        def _shift(agent, old, target):                  # move agent old→target, keeping occ_count/occ_wsum in sync
            occ_count[old] -= 1
            if occ_count[old] == 0:
                del occ_count[old]
            occ_count[target] = occ_count.get(target, 0) + 1
            if occ_wsum is not None:
                wt = base_status(agent, phi_eps) ** kappa if agent.strategy == "carbon" else 1.0
                occ_wsum[old] = occ_wsum.get(old, 0.0) - wt
                occ_wsum[target] = occ_wsum.get(target, 0.0) + wt
            agent.pos = target
            if mcf is not None:
                agent._moved_this_step = True                # Stage 1b: flag movers for the terrain move-cost drain

        for agent in agents:
            if fam_move and self._family_head(agent) is not None:
                continue                                 # F.3b: family followers don't move independently
            old = agent.pos
            temp = None
            tfn = getattr(agent._decision, "temperature", None)
            if callable(tfn):
                temp = tfn(agent)
            # Layer 2 RESIDENCE PIN: a settled member steps onto the SINGLE settlement site cell (residence ≠ foraging);
            # its food comes from the catchment tier-2 (harvest step), not the cell it stands on. Mobile agents diffuse.
            site = self._nearest_settlement(agent.pos) if settle_on else None
            if site is not None and settle_ss_on:
                # Johnson scalar stress: an over-crowded settlement repels this agent (prob rises with village pop,
                # dissipated by the site's society). Repelled ⇒ fall through to normal diffusion (leave/don't join).
                soc = self._cell_society.get(site) or self._band_society.get(agent._group.band_id)
                ss = size_repulsion(settle_pop.get(site, 0), self._demog.settlement_ss_gain,
                                    self._demog.settlement_ss_midpoint, self._demog.settlement_ss_width, soc)
                if ss > 0.0 and agent.random.random() < ss:
                    site = None
            if site is not None:
                target = self._toward(agent.pos, site)
                if target != agent.pos and self._fields.isWater[target[1], target[0]] == 0:
                    _shift(agent, agent.pos, target)
                continue
            ct = band_centroid.get(agent._group.band_id) if coh_str > 0.0 else None
            agent_coh = coh_str
            mr = 1
            if mobility_on:
                local_npp = float(npp_gm2[old[1], old[0]]) if npp_gm2 is not None else 0.0
                mr = mobility_radius(local_npp, self._demog)
            extra = followers_by_root.get(agent, 0) if anticipate else 0
            hcells, fmult = None, 1.0
            if standing_on or store_on:
                hcells = home_by_band.get(agent._group.band_id)    # your community's cells
            if standing_on:                                   # P6: price the standing you'd forfeit by leaving
                st = agent._standing
                st_after = max(self._demog.standing_floor, st * self._demog.standing_leave_penalty)
                fmult = ((st_after + phi_eps) / (st + phi_eps)) ** kappa
            target = diffusion_select_target(agent, tf, occ_count, occ_wsum, sc, agent.random, temp, ct, agent_coh,
                                             move_radius=mr, water=water_mask, extra_occupants=extra,
                                             cell_owner=cell_owner,
                                             agent_band=(agent._group.band_id if def_on else None),
                                             owner_exclusion=def_excl, owner_tether=def_teth,
                                             band_primary=band_primary,
                                             R_field=aggl_R, aggl_alpha=aggl_a, aggl_half=aggl_h,
                                             aggl_mode=aggl_mode, forage_cap=fcap, move_cost_field=mcf,
                                             site_field=sfield, band_opt_field=band_opt,
                                             home_cells=hcells, foreign_status_mult=fmult,
                                             store_field=st_field, store_gain=st_gain, store_horizon=st_hor)
            if target != old and self._fields.isWater[target[1], target[0]] != 0:
                target = old   # terrain guard: never step onto water (diffusion is water-blind)
            if target != old:
                _shift(agent, old, target)
        if fam_move:
            # F.3b nuclear-family co-movement: followers (dependent children + bonded males) snap to their head's
            # final cell, so the family forages + co-resides as a unit. Central-place FOOTPRINT (fix ii): if
            # comove_footprint>0, a follower instead takes the LOWEST-occupancy land cell within that Chebyshev
            # radius of the head (a dispersed camp, not a stack) — so co-residence doesn't over-subscribe one cell.
            w_grid, h_grid = self._fields.isWater.shape[1], self._fields.isWater.shape[0]
            for agent in self.agent_list:
                head = self._family_head(agent)
                if head is None:
                    continue
                if settle_on and self._nearest_settlement(head.pos) is not None:
                    tgt = head.pos                          # Layer 2: a SETTLED family STACKS on the site cell (the
                    if agent.pos != tgt:                    # village), overriding the footprint scatter → packs
                        _shift(agent, agent.pos, tgt)
                    continue
                if footprint_on:
                    hx, hy = head.pos
                    # scaled ⇒ per-family radius from the HEAD's local NPP (biome-scaled monthly range); else fixed
                    fp = (footprint_radius(float(fp_npp[hy, hx]) if fp_npp is not None else 0.0, self._demog)
                          if footprint_scaled else footprint)
                    if fp <= 0:
                        tgt = head.pos
                        if agent.pos != tgt:
                            _shift(agent, agent.pos, tgt)
                        continue
                    best, best_occ = None, None
                    for dy in range(-fp, fp + 1):
                        for dx in range(-fp, fp + 1):
                            cx, cy = (hx + dx) % w_grid, (hy + dy) % h_grid
                            if self._fields.isWater[cy, cx] != 0:
                                continue
                            oc = occ_count.get((cx, cy), 0)
                            # deterministic: prefer lower occupancy, tie-break toward the head cell (smaller Chebyshev)
                            key = (oc, max(abs(dx), abs(dy)))
                            if best_occ is None or key < best_occ:
                                best_occ, best = key, (cx, cy)
                    tgt = best if best is not None else head.pos
                else:
                    tgt = head.pos
                if agent.pos != tgt:
                    _shift(agent, agent.pos, tgt)
        self.occupied = set(occ_count.keys())

        # 3. per-cell harvest split (forage-only; S = cell total return rate, flow)
        occ_lists: dict[tuple[int, int], list[BaseAgent]] = {}
        for a in self.agent_list:
            occ_lists.setdefault(a.pos, []).append(a)
        # ABLATION (lumping = band-as-unit): flatten the within-BAND status DISTRIBUTION to the band mean. The band
        # is the mate-gate NEIGHBOURHOOD, not a single 100 km² cell — on the IFD substrate a band spreads ~1/cell
        # over its territory, so a per-cell flatten would be a no-op (`_band_groups` partitions occupied cells into
        # spatially-connected bands). `homogenize_cred` flattens the lineage facet HERE; `homogenize_prowess`
        # flattens the achieved facet AFTER its EMA update below (else the EMA re-differentiates it within the step).
        if self._demog is not None and getattr(self._demog, "homogenize_cred", False):
            for members in self._band_groups(occ_lists, getattr(self._demog, "bonded_mate_radius", 0)):
                mc = sum(a.cred for a in members) / len(members)
                for a in members:
                    a.cred = mc
        demog = self._demog
        provisioning = demog is not None and demog.enable_provisioning
        pat_prov = (demog is not None and getattr(demog, "enable_paternity", False)
                    and demog.paternal_provision_frac > 0.0)   # B+ step 5: paternal provisioning
        game_on = demog is not None and demog.enable_game and demog.game_meat_frac > 0.0
        meat_frac = demog.game_meat_frac if game_on else 0.0
        meat_cv = demog.game_meat_cv if game_on else 0.0
        sex_div = demog.sex_division if (demog is not None and game_on) else 0.0   # step 3: prowess-signal only
        # Storage (delayed-return): glut-capture params; gated on the overwintering zone (cell temp ≤ threshold).
        store_on = demog is not None and demog.enable_storage
        store_frac = demog.storable_fraction if store_on else 0.0
        # Resource-dependent storability (Testart): per-cell storable fraction from the local grain/fish/forage/game mix.
        sfrac_field = (self._storable_frac_field() if (store_on and getattr(demog, "enable_resource_storability", False))
                       else None)
        store_cap_mult = demog.store_capacity_reserves if store_on else 0.0
        store_temp_thr = demog.storage_temp_threshold_c if store_on else 0.0
        store_decay = demog.storage_decay if store_on else 0.0
        # Storability-gated morph (§4.5.10): gate the store on biome SEASONAL AMPLITUDE (Testart storability) rather
        # than the constant-placeholder temperature. Cache the per-cell amplitude field once.
        store_seas_gated = store_on and getattr(demog, "storage_seasonality_gated", False)
        store_seas_thr = demog.storage_seasonality_threshold if store_seas_gated else 0.0
        # SEASONAL-AQUATIC-GLUT MORPH (§4.5.10 v3): storage stays a broad survival BUFFER (marginal biomes cache for
        # the lean season → survive), but COMPLEXITY (surplus→complex) requires a dense STORABLE resource = a SEASONAL
        # AQUATIC GLUT — high water access (coast/river/lake) AND high seasonality (the anadromous run / seasonal
        # fishery that must be stored through the lean season; NW-Coast salmon — Testart/Ames). glut = mean(wateracc)
        # × mean(seasonal_amplitude): an ASEASONAL watery forest (Mbuti, amp 0.05) stays EGALITARIAN despite rivers, a
        # DRY seasonal desert (Ju) stays egalitarian for lack of water; only a SEASONAL-WATERY band (montane salmon
        # rivers) morphs complex — the real driver. SEPARATES survival-storage from complexity.
        morph_aq_gated = demog is not None and demog.enable_morph and getattr(demog, "morph_aquatic_gated", False)
        morph_aq_thr = demog.morph_aquatic_threshold if morph_aq_gated else 0.0
        morph_npp_floor = demog.morph_npp_floor if morph_aq_gated else 0.0
        if (store_seas_gated or morph_aq_gated) and self._seasonal_amp is None:
            from sic_games.climate import seasonal_amplitude_field
            self._seasonal_amp = seasonal_amplitude_field(self._fields.biome)
        if store_decay > 0.0 and self._cell_store:
            # S.3 spoilage/maintenance: every granary loses a fraction each step (incl. abandoned ones → no
            # stale free stores for wanderers, RT free-rider); prune the negligible remainder.
            for k in list(self._cell_store):
                s = self._cell_store[k] * (1.0 - store_decay)
                if s > 1.0:
                    self._cell_store[k] = s
                else:
                    del self._cell_store[k]
        morph_on = demog is not None and demog.enable_morph    # S.4 society morph
        settle_T = demog.morph_settle_steps if morph_on else 0
        # F.3c-2: when band affiliation is on, SOCIETY attaches to the BAND (band_id), not the cell — the morph
        # detector runs per-band (below) and a cell's contest κ is read from its occupants' BAND society.
        band_society_on = morph_on and getattr(demog, "enable_band_affiliation", False)
        band_kappa = {b: SOCIETY_PRESETS[s]["kappa"] for b, s in self._band_society.items()} if band_society_on else {}
        provision_pool: dict = {}              # C.2b: mother → harvest overflow available to dependents
        # Central-place PROVISIONING-EXCLUSION (fix iii): a JUVENILE follower takes NO forage share (Kaplan:
        # children are provisioned, not self-extracting) → it doesn't dilute the mother's cell; its subsistence
        # comes from the (now larger) provision pool + the band-pooled meat. Adults keep foraging normally.
        excl_on = fam_move and getattr(self._demog, "comove_provision_exclude", False)
        ceiling_on = settle_on and getattr(self._demog, "enable_catchment_ceiling", False)   # R-63 resource ceiling

        def _forage_excl(occ_c, total, kap, mask):
            """Split `total` (κ=kap) among NON-excluded occupants only; excluded get 0. Redistributes the
            excluded juveniles' share to the actual foragers (so the mother keeps her undiluted share)."""
            idx = [i for i, e in enumerate(mask) if not e]
            if not idx:
                return [0.0] * len(occ_c)
            sub = compute_harvest_shares([occ_c[i] for i in idx], total, kap, phi_eps)
            out = [0.0] * len(occ_c)
            for j, i in enumerate(idx):
                out[i] = sub[j]
            return out

        for (cx, cy), occ in occ_lists.items():
            excl_mask = None
            if excl_on:
                excl_mask = [(a.is_juvenile() and self._family_head(a) is not None) for a in occ]
                if not any(excl_mask):
                    excl_mask = None
            S = tf.level(cx, cy)
            if settle_on and (cx, cy) in self._settlement_sites:
                # Layer 2 catchment tier-2 (2b: × yearly shock; B1: × per-site soil — farms degrade it, fisheries stay 1)
                S += (self._settlement_catchment_yield((cx, cy)) * self._tier2_shock
                      * self._settlement_soil.get((cx, cy), 1.0))
            if aggl_on and aggl_R is not None:
                # AGGLOMERATION: REALIZED intensive output added to the cell pool, matching the movement-perceived
                # per-capita → increasing returns are real, no over-subscription death.
                no = len(occ)
                if aggl_mode == "point":
                    S += float(aggl_R[cy, cx]) * (no ** aggl_a - no)         # premium O(n)-baseline = A_cell·(n^β-n) → split n → A_cell·(n^(β-1)-1) each
                else:
                    na = no ** aggl_a
                    S += float(aggl_R[cy, cx]) * (na / (na + aggl_h ** aggl_a))  # catchment R·L(n) (falsified)
            if ceiling_on and settle_on and (cx, cy) in self._settlement_sites:
                S = min(S, self._settlement_carrying_capacity((cx, cy)))         # R-63: a village can't out-produce its catchment
            # S.4: the CURRENT society sets the contest exponent (egalitarian κ=0 … stratified κ=2) for this step's
            # meat pool + store draw; the detector below updates it for next step. Per-band (F.3c-2) reads the
            # cell-occupants' band society; else per-cell (the original S.4).
            if band_society_on:
                kappa_cell = band_kappa.get(occ[0]._group.band_id, kappa)
            else:
                kappa_cell = SOCIETY_PRESETS[self._cell_society[(cx, cy)]]["kappa"] if (cx, cy) in self._cell_society else kappa
            if game_on:
                # Two-stream economy (§4.5.5 / blueprint v2): forage = household (literal κ=0); meat =
                # band-pooled, Cred-weighted at κ>0 (the Carbon mechanism on high-variance game). Energy-
                # conserving: at κ=0 forage+meat == single stream (exact back-compat + the inertness gate);
                # at κ>0 meat redistributes toward high-Cred Carbon agents while forage stays equal.
                meat_pool = meat_frac * S
                if hasattr(tf, "meat_factor"):
                    meat_pool *= tf.meat_factor(cx, cy)   # C.4b caribou herd-swing: meat-only depression on GRASS_STEPPE
                if meat_cv > 0.0 and meat_pool > 0.0:
                    # G.3: band-level correlated stochastic meat — ONE mean-preserving lognormal draw per cell
                    # (shared by all occupants). Ordinary bad-streak variance; the regime where the share rule
                    # decides who crosses the floor (Carbon scoping). One model-RNG draw → deterministic.
                    sig = math.sqrt(math.log(1.0 + meat_cv * meat_cv))
                    meat_pool = math.exp(self.random.normalvariate(math.log(meat_pool) - 0.5 * sig * sig, sig))
                f_sh = (_forage_excl(occ, (1.0 - meat_frac) * S, 0.0, excl_mask) if excl_mask
                        else compute_harvest_shares(occ, (1.0 - meat_frac) * S, 0.0, phi_eps))
                m_sh = compute_harvest_shares(occ, meat_pool, kappa_cell, phi_eps)
                shares = [f + m for f, m in zip(f_sh, m_sh)]
            else:
                shares = (_forage_excl(occ, S, kappa_cell, excl_mask) if excl_mask
                          else compute_harvest_shares(occ, S, kappa_cell, phi_eps))
            if cap_on and fcap is not None:
                # PER-PERSON FORAGE CAP: a forager harvests at most forage_kcal·work_hours (the biome return-rate);
                # the surplus of a lightly-occupied cell is UNharvested (removes the S/n lone-agent over-reward).
                cv = float(fcap[cy, cx])
                if game_on:
                    f_sh = [f if f <= cv else cv for f in f_sh]
                    shares = [f + m for f, m in zip(f_sh, m_sh)]
                else:
                    shares = [s if s <= cv else cv for s in shares]
            msh = m_sh if game_on else [0.0] * len(occ)
            if sex_div > 0.0:
                # Step 3: sex-divided PRODUCTION credit (prowess signal only) — meat → male hunters, forage →
                # female gatherers. Independent of the Cred-weighted consumption share below. The credit is split
                # among PRODUCERS (non-juvenile adults), NOT all occupants — so a hunter's reputation is not diluted
                # by co-resident DEPENDENT children (incl. his own sons); that dilution corrupted prowess as a
                # status signal under co-residence/families (full-stack finding, MODEL_SPEC §4.8.12).
                adult = demog.menarche_months                  # producer-age threshold (lh_config-independent)
                n_m = sum(1 for a in occ if a.sex == "male" and a.age >= adult)
                n_f = sum(1 for a in occ if a.sex == "female" and a.age >= adult)
                male_credit = (meat_pool / n_m) if n_m else 0.0
                female_credit = ((1.0 - meat_frac) * S / n_f) if n_f else 0.0
            if store_seas_gated:
                in_owz = self._seasonal_amp[cy, cx] >= store_seas_thr   # storability: seasonal biome → store (Testart)
            else:
                in_owz = store_on and self._fields.temperature[cy, cx] <= store_temp_thr   # overwintering zone (Binford ET)
            cell_contrib = 0.0
            for a, sh, m in zip(occ, shares, msh):
                intake = a.eta() * sh          # C.1 graded production (η=1 if lh_config off; binary gate → graded)
                a._meat_intake = a.eta() * m   # B+ step 2: per-agent meat intake → the prowess (reputation) signal
                if sex_div > 0.0:
                    a._prod_credit = a.eta() * (male_credit if a.sex == "male" else female_credit)
                total = a.wealth + intake
                cap = self._reserve_full * a.reserve_scale()                 # C.2a age-scaled cap
                a.wealth = min(total, cap)
                overflow = total - cap
                if overflow > 0.0:
                    # S.1 collective storage (delayed-return): in the overwintering zone the storable fraction of
                    # the otherwise-wasted overflow is ENFORCED into the band granary; the remainder stays giveable.
                    if in_owz and store_frac > 0.0:
                        sf = float(sfrac_field[cy, cx]) if sfrac_field is not None else store_frac
                        banked = sf * overflow
                        cell_contrib += banked
                        overflow -= banked
                    if (provisioning or pat_prov) and overflow > 0.0:        # remaining overflow → giveable to dependents
                        provision_pool[a] = provision_pool.get(a, 0.0) + overflow
            # S.1 collective band granary: bank the contribution (capped at band-scaled capacity), then DRAW it
            # down to top occupants toward their reserve caps in the lean season — the band lives off the store
            # through winter. S.1 draw is need-proportional (egalitarian); S.2 makes it cred-weighted (inequality).
            if in_owz:
                key = (cx, cy)
                store = self._cell_store.get(key, 0.0) + cell_contrib
                cap_cell = store_cap_mult * self._reserve_full * len(occ)     # granary cap scales with band size
                if store > cap_cell:
                    store = cap_cell
                if store > 0.0:
                    needy = [(a, self._reserve_full * a.reserve_scale() - a.wealth) for a in occ]
                    needy = [(a, d) for a, d in needy if d > 0.0]
                    if needy:
                        # S.2 cred-weighted draw = the Hayden control-of-redistribution inequality engine: the
                        # granary is allocated by status^κ (the SAME base_status/κ as the meat pool), capped at
                        # each agent's deficit. κ=0 → equal shares (egalitarian draw); κ>0 → high-cred fill more
                        # of their reserve → ride out winter → differential survival → inequality. Bounded
                        # (graded, deficit-capped) — low-cred get a SMALLER share, not zero (RT-2: no annihilation).
                        weights = [base_status(a, phi_eps) ** kappa_cell if a.strategy == "carbon" else 1.0
                                   for a, _ in needy]                       # carbon → cred-weighted; else equal
                        gives = allocate_store_draw(weights, [d for _, d in needy], store)
                        for (a, _), g in zip(needy, gives):
                            a.wealth += g
                            store -= g
                self._cell_store[key] = store
                if morph_on and not band_society_on:
                    # S.4 settlement detector → society_from_character (the morph hook, finally called). A cell
                    # that stays packed (≥ Binford) with a defendable store for ~settle_T steps (≈1 generation)
                    # morphs egalitarian→complex→stratified; it DE-morphs when surplus/density collapse (the
                    # settle timer = hysteresis, so it holds through a bad year, not flickers). Per-cell → local.
                    density = len(occ) / _CELL_KM2
                    surplus_frac = store / cap_cell if cap_cell > 0.0 else 0.0
                    target = society_from_character(density, surplus_frac)
                    c0 = self._cell_settle.get(key, 0)
                    c = min(settle_T, c0 + 1) if target != "egalitarian_forager" else max(0, c0 - 1)
                    if c >= settle_T:
                        self._cell_society[key] = target          # morph / escalate (complex→stratified)
                        self._cell_settle[key] = c
                    elif c <= 0:
                        self._cell_society.pop(key, None)         # de-morph → egalitarian baseline
                        self._cell_settle.pop(key, None)
                    else:
                        self._cell_settle[key] = c                # hysteresis band: hold the current society
        if morph_on and not band_society_on:
            # Abandoned settlements collapse: a morphed cell that is no longer occupied this step decays its
            # settle timer toward 0 and reverts to egalitarian (the band is gone / dispersed — sustained
            # collapse, with the same hysteresis as a morph). Without this, abandoned cells freeze their label.
            for key in list(self._cell_society):
                if key not in occ_lists:
                    c = self._cell_settle.get(key, 0) - 1
                    if c <= 0:
                        self._cell_society.pop(key, None)
                        self._cell_settle.pop(key, None)
                    else:
                        self._cell_settle[key] = c
        if band_society_on:
            # F.3c-2 PER-BAND settlement detector: a band morphs egalitarian→complex→stratified on its OWN
            # aggregate character — density = members / occupied-FOOTPRINT area (D3: a tight band reads as packed
            # even on a large territory), surplus = the band's pooled cell granaries / its band-scaled capacity.
            # Same hysteresis (settle_T). Bands not seen this step decay toward egalitarian (dispersed/extinct).
            band_members: dict[int, int] = {}
            band_cells: dict[int, set] = {}
            band_cell_n: dict[tuple, int] = {}              # (bid, cell) → THIS band's members on that cell
            for (cx, cy), occ in occ_lists.items():
                for a in occ:
                    bid = a._group.band_id
                    band_members[bid] = band_members.get(bid, 0) + 1
                    band_cells.setdefault(bid, set()).add((cx, cy))
                    band_cell_n[(bid, (cx, cy))] = band_cell_n.get((bid, (cx, cy)), 0) + 1
            land_pack = getattr(self._demog, "enable_landscape_packing", False)   # R-61: landscape vs band-member density
            self._band_surplus = {}
            for bid, n in band_members.items():
                footprint_km2 = len(band_cells[bid]) * _CELL_KM2
                # LANDSCAPE population density (all agents on the band's cells / area = the Binford quantity) when on;
                # else the legacy band-members/footprint (a band's density over its own range).
                head = sum(len(occ_lists[c]) for c in band_cells[bid]) if land_pack else n
                density = head / footprint_km2 if footprint_km2 > 0 else 0.0
                # R-60 fix: the band's SHARE of each (possibly shared) cell granary, not the whole-cell granary — the
                # per-cell cap scales with TOTAL occupancy, so summing whole granaries / band-only members gave
                # surplus_frac ≈ 6-14 (gate inert). Share = cell_store · (band members on cell / total occ) ⇒ 0..1.
                store_share = 0.0
                for c in band_cells[bid]:
                    tot = len(occ_lists[c])
                    if tot > 0:
                        store_share += self._cell_store.get(c, 0.0) * (band_cell_n[(bid, c)] / tot)
                cap_band = store_cap_mult * self._reserve_full * n
                surplus_frac = store_share / cap_band if cap_band > 0.0 else 0.0
                self._band_surplus[bid] = surplus_frac          # F.3c-3: feeds assabiyah + tolerable size
                target = society_from_character(density, surplus_frac)
                if morph_aq_gated and target != "egalitarian_forager":
                    # complexity requires a STORABLE SEASONAL AQUATIC GLUT in a PRODUCTIVE setting (salmon-river /
                    # Nile-floodplain signature). TWO conditions on the band's cells:
                    #   (a) seasonal aquatic glut  = mean(wateracc × seasonal_amplitude) ≥ morph_aq_thr
                    #       (aseasonal watery forest [Mbuti] fails on seasonality);
                    #   (b) productive setting     = mean(npp_gm2) ≥ morph_npp_floor
                    #       — the true-desert vs river-desert (Nile) distinguisher: a desert OASIS is a poor setting
                    #       (npp_gm2≈400, a waterhole not a fishery) → egalitarian; a productive floodplain/river
                    #       (npp_gm2≳550) can be complex. (Diagnosed R-47: wateracc/seasonality DON'T separate desert
                    #       — it has the highest of both; only absolute productivity does.)
                    cells = band_cells[bid]; nc = len(cells)
                    glut = sum(self._fields.wateracc[cy, cx] * self._seasonal_amp[cy, cx] for (cx, cy) in cells) / nc
                    mean_npp = sum(self._fields.npp_gm2[cy, cx] for (cx, cy) in cells) / nc
                    if glut < morph_aq_thr or mean_npp < morph_npp_floor:
                        target = "egalitarian_forager"
                c0 = self._band_settle.get(bid, 0)
                c = min(settle_T, c0 + 1) if target != "egalitarian_forager" else max(0, c0 - 1)
                if c >= settle_T:
                    self._band_society[bid] = target
                    self._band_settle[bid] = c
                elif c <= 0:
                    self._band_society.pop(bid, None)
                    self._band_settle.pop(bid, None)
                else:
                    self._band_settle[bid] = c
            for bid in list(self._band_society):              # gone bands (extinct/merged) decay to egalitarian
                if bid not in band_members:
                    c = self._band_settle.get(bid, 0) - 1
                    if c <= 0:
                        self._band_society.pop(bid, None); self._band_settle.pop(bid, None)
                    else:
                        self._band_settle[bid] = c

        # Mother-linked provisioning: dependent children (age < forage_age_min) draw their deficit from
        # their mother. C.2b tier = the mother's wasted harvest overflow. S1 tier = the mother also dips
        # into her own reserve down to `provision_self_keep`·(her cap) — child-priority shortfall-sharing,
        # so in a lean season the child dwells at a mild deficit (→ condition degrades → graded disease)
        # instead of being cut off and starving, with the mother absorbing the deeper end.
        if provisioning or pat_prov:
            self_keep_frac = demog.provision_self_keep
            pat_frac = demog.paternal_provision_frac if pat_prov else 0.0
            for child in self.agent_list:
                if not child.is_juvenile():
                    continue
                need = self._reserve_full * child.reserve_scale() - child.wealth
                if need <= 0.0:
                    continue
                young = child.age < 36   # Marlowe critical period (<3 yr): male provisioning-share target ~58%
                m = child._mother
                if provisioning and m is not None and m.alive:
                    ov = provision_pool.get(m, 0.0)          # tier 1: mother's wasted overflow (free to give)
                    g = min(need, ov)
                    if g > 0.0:
                        child.wealth += g; provision_pool[m] = ov - g; need -= g
                        if young: self.prov_young_maternal += g
                    if need > 0.0 and self_keep_frac < 1.0:  # tier 2 (S1): mother's reserve above self_keep
                        res_av = m.wealth - self_keep_frac * self._reserve_full * m.reserve_scale()
                        if res_av > 0.0:
                            g2 = min(need, res_av)
                            child.wealth += g2; m.wealth -= g2; need -= g2
                            if young: self.prov_young_maternal += g2
                # tier 3 (B+ step 5): father gives `pat_frac` of HIS overflow against the child's RESIDUAL need
                # (after the maternal tiers) — conserved (otherwise-wasted overflow, like tier 1), so no
                # double-feed (RT-2); bites on the constrained-mother / orphan cohort (Marlowe).
                if need > 0.0 and pat_frac > 0.0:
                    f = child._father
                    if f is not None and f.alive:
                        fov = provision_pool.get(f, 0.0) * pat_frac
                        g3 = min(need, fov)
                        if g3 > 0.0:
                            child.wealth += g3; provision_pool[f] = provision_pool.get(f, 0.0) - g3; need -= g3
                            if young: self.prov_young_paternal += g3

        # Prowess facet dynamics (B+ step 2): achieved status = a slow decaying EMA of RELATIVE meat intake
        # (reputation, not instantaneous — Smith 2004). Relative (mean-pinned) ⇒ runaway-safe by construction
        # (mean prowess → ~1); the independent skill/luck component comes from the G.3 meat draws.
        if demog is not None and demog.enable_prowess_facet and demog.prowess_decay > 0.0:
            al = self.agent_list
            lam = demog.prowess_decay
            if sex_div > 0.0:
                # sex-specific PRODUCTION credit, normalized WITHIN sex (each sex's prowess centered ~1; male
                # prowess = hunting reputation, decoupled from the Cred-weighted consumption share → independent
                # of lineage). Female prowess (forage) is lower-variance — expected (male hunting = the facet).
                for sx in ("male", "female"):
                    # PRODUCERS only (adults ≥ menarche): juveniles don't hunt → excluding them keeps their prowess
                    # at baseline (not decayed by ~0 credit) and stops them dragging the producer mean (§4.8.12 fix).
                    grp = [a for a in al if a.sex == sx and a.age >= demog.menarche_months
                           and getattr(a, "_use_prowess", False)]
                    sigs = [getattr(a, "_prod_credit", 0.0) for a in grp]
                    mm = (sum(sigs) / len(sigs)) if sigs else 0.0
                    if mm > 0.0:
                        for a in grp:
                            a.prowess = (1.0 - lam) * a.prowess + lam * (getattr(a, "_prod_credit", 0.0) / mm)
            else:
                grp = [a for a in al if getattr(a, "_use_prowess", False)]   # normalize over prowess-agents only
                mm = sum(getattr(a, "_meat_intake", 0.0) for a in grp) / len(grp) if grp else 0.0
                if mm > 0.0:
                    for a in grp:
                        a.prowess = (1.0 - lam) * a.prowess + lam * (getattr(a, "_meat_intake", 0.0) / mm)

        # ABLATION (full band-as-unit lump): flatten the achieved PROWESS facet within the band AFTER its EMA
        # update — so next step's mate-choice + contest see a band-uniform prowess (a per-step start flatten would
        # be re-differentiated by the EMA above). With homogenize_cred this erases ALL within-band status variance.
        if demog is not None and getattr(demog, "homogenize_prowess", False):
            for members in self._band_groups(occ_lists, getattr(demog, "bonded_mate_radius", 0)):
                mp = sum(getattr(a, "prowess", 1.0) for a in members) / len(members)
                for a in members:
                    a.prowess = mp

        # GD-1 depletion (opt-in): the harvest field draws down its per-cell stock under harvest
        # pressure and regrows it. No-op for non-depletable fields (the default), so existing
        # behaviour + tests are unchanged.
        if hasattr(tf, "consume"):
            tf.consume(occ_count)

        # 4. metabolism: burn + age + mortality (cause-attributed)
        demog = self._demog
        cond_on = demog is not None and demog.enable_condition
        c_alpha = demog.condition_alpha if cond_on else 0.0
        for a in self.agent_list:
            a._fed_reserve = a.wealth        # post-harvest reserve = nutritional status (synergy/fertility read THIS)
            if cond_on:                      # S0: slow EMA of nutritional status → body condition / immune competence
                _rs = a.reserve_scale()
                _lo = a.reserve_floor * _rs; _span = self._reserve_full * _rs - _lo
                _frac = (a._fed_reserve - _lo) / _span if _span > 0 else 1.0
                _frac = 0.0 if _frac < 0.0 else (1.0 if _frac > 1.0 else _frac)
                a._condition = (1.0 - c_alpha) * a._condition + c_alpha * _frac
            a.wealth -= self._burn * a.consumption_factor()   # C.1 age-scaled maintenance (1.0 if lh_config off)
            if mcf is not None and getattr(a, "_moved_this_step", False):
                a.wealth -= float(mcf[a.pos[1], a.pos[0]])     # Stage 1b: realized terrain move cost (drain movers)
                a._moved_this_step = False
            a.age += 1
            if a._founder_store > 0.0:
                # Founder mobile reserve: cover any shortfall from carried provisions so a founder survives the
                # dispersal transient (lifts wealth just over the floor; the store decays as it is consumed).
                floor_w = a.reserve_floor * a.reserve_scale()
                if a.wealth <= floor_w:
                    g = min(a._founder_store, floor_w - a.wealth + 1.0)
                    a.wealth += g
                    a._founder_store -= g
            if demog is not None:
                a.months_since_birth += 1
                if a.wealth <= a.reserve_floor * a.reserve_scale():   # C.2a age-scaled starvation floor
                    a.alive = False
                    self.deaths_starv_this_step += 1
                    self._note_band_starv(a)                          # M2: attribute this starvation death to its band
                    self.starv_cred_this_step.append(a.cred)
                    self.starv_status_this_step.append(a.cred * getattr(a, "prowess", 1.0))
                else:
                    a2m = self._a2_mult(a, occ_count)     # Step-2 a2 modulators (1.0 if all flags off)
                    if a.random.random() < self._siler[a.sex].monthly_death_prob(a.age, a2m):
                        a.alive = False                   # Siler baseline+senescence
                        self.deaths_senesc_this_step += 1
                    elif a.age >= a.max_age:              # hard lifespan cap (Siler-tail backstop; was DEAD CODE
                        a.alive = False                   # under demog — the elif below is only reached when
                        self.deaths_senesc_this_step += 1  # demog is None, so ancient agents slipped through to 1111)
            elif a.wealth <= a.reserve_floor:
                a.alive = False
                self.deaths_starv_this_step += 1
                self._note_band_starv(a)
            elif a.age >= a.max_age:
                a.alive = False
                self.deaths_senesc_this_step += 1

        # GD-1: advance the depletable resource stock (deplete by this step's foraging pressure, regrow at the
        # biome/season rate). No-op unless the harvest field has depletion enabled. `season` from the climate field
        # if present (growing-season pulse), else aseasonal.
        if hasattr(tf, "deplete_and_regrow"):
            season = tf.season() if hasattr(tf, "season") else 1.0
            tf.deplete_and_regrow(occ_count, season)

    def _note_band_starv(self, a) -> None:
        """M2: tally a starvation death against the agent's band (band_id → count this step)."""
        bid = getattr(getattr(a, "_group", None), "band_id", None)
        if bid is not None:
            self._band_starv_this_step[bid] = self._band_starv_this_step.get(bid, 0) + 1

    def _log_genea(self, event: str, a) -> None:
        """Genealogy logger (pure observer): append one GENEA_HEADER-schema record per birth/death — parentage,
        lineage/band, status (cred + prowess), wealth, sex/age, COMPLETED reproductive success (parity / n_fathered),
        cell, and band society. `event` ∈ {'birth','death'}. Missing parents → uid −1. No RNG, no read-back — so
        DEATH rows carry each agent's completed life-history (the RS/dynasty substrate for offline analysis)."""
        if self._genealogy_log is None:
            return
        g = getattr(a, "_group", None)
        bid = getattr(g, "band_id", None) if g is not None else None
        self._genealogy_log.append((
            self.step_count, event, a.unique_id,
            getattr(getattr(a, "_mother", None), "unique_id", -1),
            getattr(getattr(a, "_father", None), "unique_id", -1),
            getattr(a, "_lineage", None), bid,
            round(getattr(a, "cred", 0.0), 4), round(getattr(a, "prowess", 1.0), 4),
            round(getattr(a, "wealth", 0.0), 1), getattr(a, "sex", ""), int(getattr(a, "age", 0)),
            int(getattr(a, "parity", 0)), int(getattr(a, "_n_fathered", 0)),
            a.pos[0], a.pos[1], self._band_society.get(bid, "") if bid is not None else "",
        ))

    def dump_genealogy(self, path: str) -> int:
        """Write the whole genealogy buffer to a CSV, OVERWRITING (offline analysis substrate; short runs/tests).
        For long campaigns use flush_genealogy() to append+clear and keep memory bounded. Returns record count."""
        if not self._genealogy_log:
            return 0
        import csv
        with open(path, "w", newline="", encoding="utf-8") as f:
            wr = csv.writer(f)
            wr.writerow(GENEA_HEADER)
            wr.writerows(self._genealogy_log)
        return len(self._genealogy_log)

    def flush_genealogy(self, path: str) -> int:
        """APPEND the buffered genealogy rows to `path` and CLEAR the buffer — bounded memory for long campaigns
        (call every N steps). Writes the header once, when the file is first created. Returns rows flushed."""
        if not self._genealogy_log:
            return 0
        import csv, os
        new = not os.path.exists(path)
        with open(path, "a", newline="", encoding="utf-8") as f:
            wr = csv.writer(f)
            if new:
                wr.writerow(GENEA_HEADER)
            wr.writerows(self._genealogy_log)
        n = len(self._genealogy_log)
        self._genealogy_log.clear()
        return n

    def _step_agent(self, agent: BaseAgent) -> None:
        tf = self.terrain_field

        # 1. Perceive + decide (movement uses forage signal for navigation)
        perception = agent._perception.build(agent, tf, self.occupied)
        target = agent._decision.select_target(agent, perception, agent.random)
        old_pos = agent.pos
        if target != old_pos:
            self.occupied.discard(old_pos)
            self.occupied.add(target)
            agent.pos = target

        x, y = agent.pos

        # 2. A2.4 child age-gate: binary [JV-1: graded curve deferred]
        if agent.is_juvenile():
            rate_step = 0.0
        else:
            # 3. A2.2 sex-based stream selection (game_stream only if enabled)
            if self._game_stream:
                forage_step = tf.forage_level(x, y)
                game_step = tf.game_level(x, y)
                rate_step = self._select_stream(agent.sex, forage_step, game_step)
            else:
                rate_step = tf.forage_level(x, y)   # A-1 forage-only path

        # 4. Intake + reserve cap [PLACEHOLDER MR-1]
        agent.wealth = min(agent.wealth + rate_step, self._reserve_full)

        # 5. Burn + age + mortality (with cause attribution)
        agent.wealth -= self._burn
        agent.age += 1
        if agent.wealth <= agent.reserve_floor:
            agent.alive = False
            self.deaths_starv_this_step += 1
            self._note_band_starv(agent)
        elif agent.age >= agent.max_age:
            agent.alive = False
            self.deaths_senesc_this_step += 1

    def _select_stream(self, sex: str, forage_step: float, game_step: float) -> float:
        """A2.2 energy-balance stream selection. No new tunable beyond A-1 placeholders."""
        burn = self._burn
        if sex == "male":
            if game_step >= burn:
                return game_step
            if forage_step > game_step:
                return forage_step
            return game_step
        else:
            if forage_step >= burn:
                return forage_step
            if game_step > forage_step:
                return game_step
            return forage_step

    # ── Demographic layer (A-3) ──────────────────────────────────────────────

    def _do_births(self) -> None:
        """Asexual, reserve-gated reproduction [PROVISIONAL shakedown]. Child is placed on
        the parent's cell (multi-occupancy allowed); density-dependence comes from rivalry
        (crowded cells → small per-capita share → starvation), not from space. The child
        disperses next step via diffusion movement. Deterministic agent_list order."""
        newborns: list[BaseAgent] = []
        for agent in self.agent_list:
            if agent.age < self._repro_min_age:
                continue
            if agent.wealth < self._birth_threshold:
                continue
            if self.random.random() < self._p_birth:
                agent.wealth -= self._birth_cost
                sex = "female" if self.random.random() < self._kcal_cfg.p_female else "male"
                child = self._make_agent(sex=sex, lh_cfg=self._lh_cfg)
                child.pos = agent.pos
                child.wealth = self._child_endowment
                child.age = 0
                newborns.append(child)
                self.births_this_step += 1
        self.agent_list.extend(newborns)
        if self._genealogy_log is not None:               # Stage 2: observer log (after birth, parents/lineage set)
            for c in newborns:
                self._log_genea("birth", c)

    def _do_births_ibi(self) -> None:
        """Demographic-stage reproduction: female-only, IBI-gated (Siler+IBI core). Maternal folded
        into the all-cause female schedule (approach (ii)); the energetic fertility modifier is OFF
        here (2a-pre strict stability test). Child on the parent's cell; disperses via diffusion."""
        cfg = self._demog
        # B+ step 4 paternity setup (once/step): candidate fathers + mate-choice weights + the lineage
        # mean-reversion target. Fertility itself is UNCHANGED (female-IBI) — this only assigns WHO fathers
        # and how lineage propagates (R-14 reopened minimally).
        paternity = getattr(cfg, "enable_paternity", False)
        males = None; m_w = None; m_status = None
        assort = getattr(cfg, "assortative_strength", 0.0)
        if paternity:
            males = [x for x in self.agent_list if x.sex == "male" and x.age >= cfg.menarche_months]
            mexp = cfg.mate_choice_strength
            if males and (mexp > 0.0 or assort > 0.0):
                m_w = [(getattr(x, "prowess", 1.0) + 1e-6) ** mexp for x in males]   # prowess^m base
            if males and assort > 0.0:
                m_status = [x.cred * getattr(x, "prowess", 1.0) for x in males]      # B++ assortment status
        # F.1 bonded mating: a co-resident adult male is REQUIRED for a birth → loners can't reproduce. Precompute
        # the adult males per cell (kin-avoidance applied per-mother below).
        bonded = getattr(cfg, "enable_bonded_mating", False)
        pair_bonds = getattr(cfg, "enable_pair_bonds", False)   # F.3a: the durable partner gates + fathers
        loc = getattr(cfg, "enable_band_family_knobs", False)   # F.3c-2b: per-band lineage/descent knobs
        affil = getattr(cfg, "enable_band_affiliation", False)  # F.3a: band-level co-residence for the husband (polygyny)
        mate_r = getattr(cfg, "bonded_mate_radius", 0)
        males_by_cell: dict[tuple[int, int], list] = {}
        if bonded and not pair_bonds:
            for x in self.agent_list:
                if x.sex == "male" and x.age >= cfg.menarche_months:
                    males_by_cell.setdefault(x.pos, []).append(x)

        def _has_band_mate(mother) -> bool:
            # F.2: an unrelated (non-son) adult male co-resident in the band — the mother's cell (radius 0) or,
            # since a band spreads ~1/cell over its territory, anywhere within Chebyshev `mate_r` of her.
            mx, my = mother.pos
            for dx in range(-mate_r, mate_r + 1):
                for dy in range(-mate_r, mate_r + 1):
                    for m in males_by_cell.get((mx + dx, my + dy), ()):
                        if m._mother is not mother:
                            return True
            return False
        sed_fert = getattr(cfg, "enable_sedentism_fertility", False)   # NDT: society-dependent birth-spacing
        newborns: list[BaseAgent] = []
        for a in self.agent_list:
            if a.sex != "female":
                continue
            if sed_fert:
                soc = self._band_society.get(a._group.band_id) or self._cell_society.get(a.pos)
                ibi_m = sedentism_ibi(soc, cfg.ibi_refractory_months)   # sedentary/complex → shorter IBI → higher fertility
                if not (cfg.menarche_months <= a.age < cfg.menopause_months and a.months_since_birth >= ibi_m):
                    continue
            elif not is_fertile(a.age, a.months_since_birth, cfg):
                continue
            if pair_bonds:
                partner = a._partner                           # F.3a: needs a living, co-resident husband
                if partner is None or not partner.alive:
                    continue
                if affil:
                    if partner._group.band_id != a._group.band_id:
                        continue                               # husband in a different band (polygyny → band-level)
                elif max(abs(a.pos[0] - partner.pos[0]), abs(a.pos[1] - partner.pos[1])) > mate_r:
                    continue                                   # husband not co-resident (F.3a/b cell-neighbourhood)
            elif bonded and not _has_band_mate(a):
                continue   # F.1/F.2: no co-resident non-son adult male in the band ⇒ no mate ⇒ no birth
            p_birth = cfg.fecundability
            if cfg.enable_energetic_fertility:                 # births scale with NUTRITIONAL status (post-harvest)
                _rs = a.reserve_scale()                        # C.2a age-scaled floor/full
                p_birth *= energetic_fertility_factor(a._fed_reserve, a.reserve_floor * _rs, self._reserve_full * _rs)
            if a.random.random() < p_birth:
                a.months_since_birth = 0
                a.parity += 1
                csex = "male" if a.random.random() < cfg.srb_male else "female"
                child = self._make_agent(sex=csex, lh_cfg=self._lh_cfg)
                child.pos = a.pos
                child.age = 0
                child._mother = a                                          # C.2b mother-link for provisioning
                child._group = a._group.inherit()                          # F.3c-1: newborn inherits the mother's band affiliation
                child._lineage = a._lineage                                # default matriline (overridden to patriline if a father is assigned)
                if getattr(child, "use_cred_status", False):               # heritable lineage (cred)
                    si = cfg.cred_inherit_sigma
                    # MEAN-1 lognormal noise (E[noise]=1): mean-preserving, so inheritance adds no multiplicative
                    # upward bias across generations (red-team BLOCKER fix — `exp(N(0,σ))` had mean exp(σ²/2)>1).
                    noise = math.exp(self.random.normalvariate(-0.5 * si * si, si)) if si > 0.0 else 1.0
                    if paternity:
                        # mate-choice: prowess-weighted father (m=0 → random); bilateral lineage = blend of the
                        # parents' TOTAL standing (cred·prowess — folds the father's hunting record in).
                        if pair_bonds:
                            father = a._partner                # F.3a: the durable partner IS the father (no lottery)
                        elif males:
                            if assort > 0.0 and m_status is not None:
                                # B++ assortment: prowess^m × similarity-to-mother (Gaussian in log-status)
                                li = math.log(a.cred * getattr(a, "prowess", 1.0) + 1e-9)
                                ww = [m_w[k] * math.exp(-assort * (math.log(m_status[k] + 1e-9) - li) ** 2)
                                      for k in range(len(males))]
                                father = self.random.choices(males, weights=ww, k=1)[0]
                            elif m_w is not None:
                                father = self.random.choices(males, weights=m_w, k=1)[0]
                            else:
                                father = self.random.choice(males)
                        else:
                            father = None
                        child._father = father
                        if father is not None:
                            father._n_fathered = getattr(father, "_n_fathered", 0) + 1   # E.3: male RS (children fathered)
                        child._lineage = father._lineage if father is not None else a._lineage   # patriline
                        if father is not None:
                            self.mate_pairs_this_step.append(
                                (a.cred * getattr(a, "prowess", 1.0), father.cred * getattr(father, "prowess", 1.0)))
                        t_mom = a.cred * getattr(a, "prowess", 1.0)
                        if father is not None:
                            pw = self._band_knob(a._group.band_id, "patriline_weight") if loc else cfg.patriline_weight
                            base = (1.0 - pw) * t_mom + pw * (father.cred * getattr(father, "prowess", 1.0))
                        else:
                            base = t_mom                                   # matrilineal fallback (no adult males)
                    else:
                        base = a.cred                                      # step-1 matrilineal (paternity off)
                    # Mean-reversion toward a FIXED anchor (1.0 = founder median) — a TRUE contraction that bounds
                    # the no-decay lineage facet (red-team BLOCKER fix: the co-moving population mean was NOT a
                    # contraction → unbounded drift). ρ=0 ⇒ pure mean-1 multiplicative copy (R-18/step-1).
                    lr = self._band_knob(a._group.band_id, "lineage_reversion") if loc else cfg.lineage_reversion
                    child.cred = (1.0 - lr) * base * noise + lr * 1.0
                child.wealth = self._reserve_full * child.reserve_scale()   # C.2a body-sized neonatal reserve
                if a._genome is not None:                                   # neutral genome: Mendelian ½/½ (uniparental if father unresolved)
                    child._genome = Genome.inherit(a._genome, getattr(child._father, "_genome", None),
                                                   self.random, mutation=cfg.genome_mutation)
                newborns.append(child)
                self.births_this_step += 1
        self.agent_list.extend(newborns)
        if self._genealogy_log is not None:               # Stage 2: observer log (after birth, parents/lineage set)
            for c in newborns:
                self._log_genea("birth", c)

    def morph_to_society(self, name: str) -> None:
        """Evolving-society hook: re-bundle the family/status knobs to a new society preset mid-run — swaps the
        demographic config + the substrate `contest_exponent` (κ). Drive it from `society_from_character` on the
        band's measured character (Binford packing density / Testart surplus; MODEL_SPEC §4.5.10). In the current
        forage-only model the equilibrium density sits at/below the packing threshold, so a transition stays
        inert until a surplus/storage mechanic lifts density past it — the hook is wired, the trigger awaits."""
        from sic_games.demography import society_knobs
        kappa, fam = society_knobs(name)
        cp = getattr(self._demog, "model_copy", None)
        self._demog = self._demog.model_copy(update=fam) if cp else self._demog.copy(update=fam)
        sc = self._substrate_cfg
        scp = getattr(sc, "model_copy", None)
        self._substrate_cfg = (sc.model_copy(update={"contest_exponent": kappa}) if scp
                               else sc.copy(update={"contest_exponent": kappa}))
        self._society = name

    def connubium(self) -> dict:
        """CONNUBIUM diagnostic: the realized mating-pool reach — distinct unpaired adults in each pool that produced a
        marriage this pairing phase. Under real exogamy the pool must span many bands to hold enough non-kin mates, so
        this size is the emergent mating-network scale (validate median → Wobst ~475). Empty until a pairing phase runs.
        (Cut-1 proxy = the existing band/gathering pool size; Cut-2's search-to-eligibility gives the true catchment.)"""
        import numpy as np
        s = self._connubium_sizes
        if not s:
            return {}
        a = np.array(s)
        return dict(n_pools=len(s), median=float(np.median(a)), mean=float(a.mean()),
                    p90=float(np.quantile(a, 0.9)), max=int(a.max()))

    def genetics(self, sample_pairs: int = 2000) -> dict:
        """Population-genetics read-out (requires enable_genome): expected heterozygosity H (drift/Nₑ signal — decays
        ~1/Nₑ per generation), mean pairwise relatedness (realized inbreeding level), and coverage. Empty if off."""
        from sic_games.genome import expected_heterozygosity, mean_pairwise_relatedness
        gs = [a._genome for a in self.agent_list if getattr(a, "_genome", None) is not None]
        if not gs:
            return {}
        return dict(n_with_genome=len(gs),
                    heterozygosity=expected_heterozygosity(gs),
                    mean_relatedness=mean_pairwise_relatedness(gs, self._diag_rng, sample_pairs))

    def bands(self, radius: int | None = None) -> list[list]:
        """Public band identifier (F.2 diagnostics): the live population partitioned into spatially-connected
        BANDS — cells linked when Chebyshev-adjacent within `radius` (default = the configured bonded_mate_radius,
        the operative band extent) are one band. Returns a list of agent-lists INCLUDING singletons (unlike the
        internal `_band_groups`, which drops them for the lumping flatten). The unit for merge/split/collapse
        tracking + the size distribution."""
        if radius is None:
            radius = getattr(self._demog, "bonded_mate_radius", 1) if self._demog is not None else 1
        radius = max(0, radius)
        occ_lists: dict[tuple[int, int], list] = {}
        for a in self.agent_list:
            occ_lists.setdefault(a.pos, []).append(a)
        if radius == 0:
            return list(occ_lists.values())
        cellset = set(occ_lists)
        parent = {c: c for c in cellset}

        def find(c):
            while parent[c] != c:
                parent[c] = parent[parent[c]]
                c = parent[c]
            return c

        for (x, y) in cellset:
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    nb = (x + dx, y + dy)
                    if nb in cellset:
                        parent[find((x, y))] = find(nb)
        groups: dict[tuple[int, int], list] = {}
        for c, occ in occ_lists.items():
            groups.setdefault(find(c), []).extend(occ)
        return list(groups.values())

    def band_leaders(self) -> dict[int, "BaseAgent"]:
        """Public diagnostic (Stage 1 leader coherence): map each live band_id (the affiliation `_group.band_id`,
        NOT the spatial `bands()` grouping) to its current highest cred·prowess member. Used by the
        leader-coherence benchmark to identify — and, in a controlled experiment, force-remove — a band's leader
        at a scripted step (set `.alive = False`; the model's own death-pruning cleans it up next `step()`), and
        to track leader-identity turnover."""
        members: dict[int, list] = {}
        for a in self.agent_list:
            members.setdefault(a._group.band_id, []).append(a)
        return {bid: max(ms, key=lambda a: a.cred * getattr(a, "prowess", 1.0)) for bid, ms in members.items()}

    def dynasties(self, top: int = 15, sample_pairs: int = 400) -> dict:
        """Lineage/dynasty read-out (campaign — Turchin elite layer). Groups the live population by patriline
        `_lineage`. Aggregate: n_lineages; top_share (largest lineage ÷ pop); size_gini (dynastic concentration);
        eff_lineages (inverse-Simpson Hill number — the effective count of co-existing lineages, falls as dynasties
        consolidate). Per top-`top` lineage: size, mean cred/prowess/wealth, mean COMPLETED reproductive success
        (female parity / male n_fathered), and — with genome on — within-lineage mean relatedness (the genetic
        signature of a dynasty). Pure observer (uses the diagnostic RNG ⇒ never perturbs the model stream)."""
        import numpy as np
        al = self.agent_list
        if not al:
            return {}
        groups: dict = {}
        for a in al:
            groups.setdefault(getattr(a, "_lineage", None), []).append(a)
        pop = len(al)
        sizes = sorted((len(v) for v in groups.values()), reverse=True)
        p = np.asarray(sizes, dtype=float) / pop
        eff = float(1.0 / np.sum(p * p))
        from sic_games.genome import mean_pairwise_relatedness
        rows = []
        for lin, ms in sorted(groups.items(), key=lambda kv: len(kv[1]), reverse=True)[:top]:
            gs = [a._genome for a in ms if getattr(a, "_genome", None) is not None]
            rows.append(dict(
                lineage=lin, n=len(ms),
                cred=round(float(np.mean([getattr(a, "cred", 1.0) for a in ms])), 3),
                prowess=round(float(np.mean([getattr(a, "prowess", 1.0) for a in ms])), 3),
                wealth=round(float(np.mean([getattr(a, "wealth", 0.0) for a in ms])), 1),
                rs=round(float(np.mean([getattr(a, "parity", 0) if a.sex == "female"
                                        else getattr(a, "_n_fathered", 0) for a in ms])), 2),
                relatedness=(round(mean_pairwise_relatedness(gs, self._diag_rng, sample_pairs), 3)
                             if len(gs) >= 2 else None)))
        return dict(n_lineages=len(groups), top_share=round(sizes[0] / pop, 3),
                    size_gini=round(_gini(sizes), 3), eff_lineages=round(eff, 1), top=rows)

    def settlements(self) -> dict:
        """Per-settlement panel (campaign — urban hierarchy + lifespans). For each maintained settlement site with
        live occupants: count, society (dominant band's morph), catchment yield, mean cred, dominant lineage.
        Aggregate rank-size: primate_ratio (largest ÷ 2nd), zipf_slope (OLS of ln size vs ln rank; ≈ −1 = Zipf),
        median/max. Pure observer."""
        import numpy as np
        sites = set(self._settlement_sites)
        if not sites:
            return {}
        occ_by_site: dict = {}
        for a in self.agent_list:
            if a.pos in sites:
                occ_by_site.setdefault(a.pos, []).append(a)
        panel = []
        for s, ms in occ_by_site.items():
            bids = Counter(a._group.band_id for a in ms)
            lins = Counter(getattr(a, "_lineage", None) for a in ms)
            panel.append(dict(pos=s, n=len(ms),
                              society=self._band_society.get(bids.most_common(1)[0][0], "egalitarian_forager"),
                              catchment=round(self._settlement_catchment_yield(s), 1),
                              cred=round(float(np.mean([getattr(a, "cred", 1.0) for a in ms])), 3),
                              dom_lineage=lins.most_common(1)[0][0]))
        if not panel:
            return {}
        sizes = sorted((q["n"] for q in panel), reverse=True)
        primate = round(sizes[0] / sizes[1], 2) if len(sizes) > 1 else None
        zipf = (float(np.polyfit(np.log(np.arange(1, len(sizes) + 1)), np.log(np.asarray(sizes, float)), 1)[0])
                if len(sizes) >= 3 else None)
        return dict(n=len(panel), median=int(np.median(sizes)), max=sizes[0], primate_ratio=primate,
                    zipf_slope=round(zipf, 2) if zipf is not None else None,
                    panel=sorted(panel, key=lambda q: q["n"], reverse=True))

    def instability(self) -> dict:
        """Sociopolitical-instability read-out (campaign). Economic-defensibility (Dyson-Hudson & Smith 1978)
        contest activity: claim_events = challenger-erosion events over defensible cells THIS step (the instability
        FLOW); n_owned = cells currently under a standing ownership claim; n_claims = active (incl. contested)
        claims. A proxy for Turchin's instability variable, grounded in the defensibility mechanism. Pure observer."""
        return dict(claim_events=self._claim_events_this_step,
                    n_owned=len(self._cell_owner), n_claims=len(self._cell_claim))

    def _family_head(self, a) -> "BaseAgent | None":
        """F.3b nuclear-family movement: the agent's MOVEMENT ANCHOR, or None if it moves independently. A dependent
        child (age < family_maturity_months, living mother) follows its MOTHER; a bonded adult male follows his
        female PARTNER. Adult females + unpaired/mature agents are roots (None). No multi-level chains: a child's
        mother is always an adult root (she must be ≥ menarche to have borne it)."""
        cfg = self._demog
        mat = cfg.family_maturity_months
        m = a._mother
        if a.age < mat and m is not None and m.alive:
            return m
        if a.sex == "male" and a._wives:
            alive_wives = [w for w in a._wives if w.alive]
            if len(alive_wives) == 1:
                return alive_wives[0]       # monogamous husband co-moves with his wife (F.3b)
            # polygynous husband (>1 wife) is a ROOT — wives are mother-anchored cores in his band
        return None

    def _do_pairing(self) -> None:
        """F.3a serial monogamy (+ modest polygyny): match unpaired adults WITHIN each band (mate-gate
        neighbourhood) into durable bonds, prowess-weighted (mate_choice_strength), kin-avoiding (not son/father).
        Widowed/divorced agents re-enter the pool automatically. With polygyny_rate>0 an already-married male can
        take additional wives (≤ max_wives), prowess-weighted → high-status males accumulate wives (von Rueden).
        (Superseded by `_do_gathering` when `enable_marriage_aggregation`.)"""
        cfg = self._demog
        if cfg.divorce_rate > 0.0:
            for a in self.agent_list:
                if a.sex == "female" and a._partner is not None and self.random.random() < cfg.divorce_rate:
                    a._partner._wives.discard(a); a._partner = None
        affil = getattr(cfg, "enable_band_affiliation", False)
        band_sizes = Counter(a._group.band_id for a in self.agent_list) if affil else None
        # PERF Tier 0: mate within the SOCIAL band_id (fission-capped ~25–45) → O(n), not the spatial bands() clump
        # which balloons to O(clump²) under agglomeration. Off ⇒ spatial pool (bit-exact).
        if affil and getattr(cfg, "mate_within_band_id", False):
            pools: dict = {}
            for a in self.agent_list:
                pools.setdefault(a._group.band_id, []).append(a)
            groups = pools.values()
        else:
            groups = self.bands(cfg.bonded_mate_radius)
        for band in groups:
            females = [a for a in band if a.sex == "female" and a._partner is None and a.age >= cfg.menarche_months]
            males = [a for a in band if a.sex == "male" and a.age >= cfg.menarche_months]
            if not females or not males:
                continue
            self._pair_from_pool(females, males, "flexible", 0.0, band_sizes)

    def _pair_from_pool(self, females, males, residence, rank_homogamy, band_sizes) -> None:
        """Pair a POOL of unpaired females with candidate males (kin-avoiding, prowess·cred-weighted). `residence`:
        virilocal (bride→groom's band), uxorilocal (groom→bride's band), flexible (smaller→larger — the F.3a default).
        `rank_homogamy` ≥0 adds like-cred assortment. Shared by the daily within-band `_do_pairing` (flexible, 0.0 =
        bit-exact) and the regional `_do_gathering` (cross-band). RNG order preserved: shuffle → polygyny-gate → choose."""
        cfg = self._demog
        mexp = cfg.mate_choice_strength
        loc = getattr(cfg, "enable_band_family_knobs", False)
        poly = getattr(cfg, "polygyny_rate", 0.0)
        max_wives = getattr(cfg, "max_wives", 1)
        asc_on = getattr(cfg, "enable_ascribed_mate_choice", False)
        asc_a = getattr(cfg, "ascribed_mate_strength", 0.0)
        affil = band_sizes is not None
        exog = getattr(cfg, "enable_exogamy", False)                 # CONNUBIUM: real kin/clan prohibition
        exog_deg = getattr(cfg, "exogamy_degree", "lineage")
        exog_clan = exog and exog_deg in ("lineage", "cousin")       # patriclan (same _lineage) exogamy
        exog_cousin = exog and exog_deg == "cousin"                  # genetic cousin+ (needs genome)
        r_star = getattr(cfg, "exogamy_relatedness", 0.125)
        pool_n = len(females) + sum(1 for m in males if not m._wives)   # CONNUBIUM diag: distinct unpaired adults in reach
        paired_here = 0
        self.random.shuffle(females)
        for f in females:
            fm, ff = (f._mother, f._father) if exog else (None, None)
            avail = []
            for x in males:
                if x._mother is f or x is f._father:                 # kin-avoidance (not son / father)
                    continue
                if exog and self._exogamy_blocks(f, x, fm, ff, exog_clan, exog_cousin, r_star):
                    continue                                         # sibling/half-sib, patriclan, or genetic cousin+
                if not x._wives:
                    avail.append(x)
                elif poly > 0.0 and len(x._wives) < max_wives and self.random.random() < poly:
                    avail.append(x)
            if not avail:
                continue
            m_f = self._band_knob(f._group.band_id, "mate_choice_strength") if loc else mexp
            if m_f > 0.0:
                g = asc_a * mate_ascribed_weight(self._band_society.get(f._group.band_id)) if asc_on else 0.0
                if g > 0.0:
                    w = [((getattr(x, "prowess", 1.0) + 1e-6) * (getattr(x, "cred", 1.0) + 1e-6) ** g) ** m_f for x in avail]
                else:
                    w = [(getattr(x, "prowess", 1.0) + 1e-6) ** m_f for x in avail]
                if rank_homogamy > 0.0:                              # like-cred assortment (rank homogamy)
                    fc = getattr(f, "cred", 1.0) + 1e-6
                    w = [wi * math.exp(-rank_homogamy * abs(math.log((getattr(x, "cred", 1.0) + 1e-6) / fc)))
                         for wi, x in zip(w, avail)]
                male = self.random.choices(avail, weights=w, k=1)[0]
            else:
                male = self.random.choice(avail)
            f._partner = male; male._wives.add(f)
            paired_here += 1
            if affil:
                fb, mb = f._group.band_id, male._group.band_id
                if fb != mb:
                    if residence == "virilocal":                    # bride joins the groom's band + lineage
                        band_sizes[fb] -= 1; band_sizes[mb] += 1; f._group.band_id = mb
                    elif residence == "uxorilocal":                 # groom joins the bride's band
                        band_sizes[mb] -= 1; band_sizes[fb] += 1; male._group.band_id = fb
                    elif band_sizes[mb] > band_sizes[fb]:           # flexible: smaller → larger (F.3a default)
                        band_sizes[fb] -= 1; band_sizes[mb] += 1; f._group.band_id = mb
                    else:
                        band_sizes[mb] -= 1; band_sizes[fb] += 1; male._group.band_id = fb
        if paired_here:                                             # CONNUBIUM diag: record the reach of a pool that mated
            self._connubium_sizes.append(pool_n)

    def _exogamy_blocks(self, f, x, fm, ff, clan, cousin, r_star) -> bool:
        """Single source of truth for the exogamy prohibition (Cut 1/2): True ⇒ male `x` is a forbidden mate for
        female `f`. `fm`/`ff` = f's parents; `clan`/`cousin` = active-degree flags. Sibling/half-sib (shared parent),
        patriclan (same `_lineage`), and — at cousin degree — genome relatedness > r*. (Parent-child is handled by the
        caller's base check.) Used by both `_pair_from_pool` and the adaptive `_do_connubium`."""
        if (fm is not None and x._mother is fm) or (ff is not None and x._father is ff):
            return True                                              # sibling / half-sib
        if clan and x._lineage is not None and x._lineage == f._lineage:
            return True                                              # patriclan
        if cousin and f._genome is not None and x._genome is not None and x._genome.relatedness(f._genome) > r_star:
            return True                                              # genetic cousin+
        return False

    def _do_connubium(self) -> None:
        """Cut 2 — ADAPTIVE connubium (replaces the fixed-radius gathering when `enable_adaptive_connubium`). Each
        unpaired female expands a Chebyshev search ring-by-ring until she has ≥ m* eligible non-kin males in reach (or
        the travel cap), then pairs prowess-weighted. The realized reach self-organizes to the connubium scale — a
        kin-homogeneous region forces a wider search (bigger connubium); a diverse one a smaller. `connubium()` then
        records the TOTAL population (all ages) within each realized reach = the mating-network size (Wobst ~500)."""
        cfg = self._demog
        if self.step_count % cfg.aggregation_period != 0:
            return
        hf = self._harvest_field
        if hasattr(hf, "season") and hf.season() < cfg.aggregation_season_threshold:
            return
        if cfg.divorce_rate > 0.0:
            for a in self.agent_list:
                if a.sex == "female" and a._partner is not None and self.random.random() < cfg.divorce_rate:
                    a._partner._wives.discard(a); a._partner = None
        affil = getattr(cfg, "enable_band_affiliation", False)
        band_sizes = Counter(a._group.band_id for a in self.agent_list) if affil else None
        exog = getattr(cfg, "enable_exogamy", False)
        deg = getattr(cfg, "exogamy_degree", "lineage")
        clan = exog and deg in ("lineage", "cousin"); cousin = exog and deg == "cousin"
        r_star = getattr(cfg, "exogamy_relatedness", 0.125)
        m_star = cfg.mate_search_min_eligible; max_r = cfg.mate_search_max_radius
        mexp = cfg.mate_choice_strength; menarche = cfg.menarche_months
        poly = getattr(cfg, "polygyny_rate", 0.0); max_wives = getattr(cfg, "max_wives", 1)
        # spatial index: cell → agents (rebuilt this gathering)
        cell: dict = {}
        for a in self.agent_list:
            cell.setdefault(a.pos, []).append(a)
        W = getattr(hf, "width", N); H = getattr(hf, "height", N)
        females = [a for a in self.agent_list if a.sex == "female" and a._partner is None and a.age >= menarche]
        self.random.shuffle(females)
        for f in females:
            fx, fy = f.pos
            fm, ff = f._mother, f._father
            eligible: list = []; reach_pop = 0
            for r in range(0, max_r + 1):                            # expand the search ring by ring
                x0, x1 = max(0, fx - r), min(W - 1, fx + r)
                y0, y1 = max(0, fy - r), min(H - 1, fy + r)
                for cy in range(y0, y1 + 1):
                    on_y = (cy == fy - r or cy == fy + r)
                    for cx in range(x0, x1 + 1):
                        if r > 0 and not on_y and cx != fx - r and cx != fx + r:
                            continue                                 # only the new cells at Chebyshev distance r
                        for a in cell.get((cx, cy), ()):             # count population in reach; collect eligible males
                            reach_pop += 1
                            if a.sex == "male" and a.age >= menarche and a is not f:
                                if a._mother is f or a is f._father:
                                    continue                          # parent-child (base kin)
                                if exog and self._exogamy_blocks(f, a, fm, ff, clan, cousin, r_star):
                                    continue
                                if (not a._wives) or (poly > 0.0 and len(a._wives) < max_wives and self.random.random() < poly):
                                    eligible.append(a)
                if len(eligible) >= m_star:
                    break
            if not eligible:
                continue
            if mexp > 0.0:
                w = [(getattr(x, "prowess", 1.0) + 1e-6) ** mexp for x in eligible]
                male = self.random.choices(eligible, weights=w, k=1)[0]
            else:
                male = self.random.choice(eligible)
            f._partner = male; male._wives.add(f)
            if affil and f._group.band_id != male._group.band_id:    # virilocal: bride joins groom's band
                band_sizes[f._group.band_id] -= 1; band_sizes[male._group.band_id] += 1
                f._group.band_id = male._group.band_id
            self._connubium_sizes.append(reach_pop)                  # total network pop within realized reach
        if getattr(cfg, "enable_aggregation_sedentism", False):     # Cut-2 founds settlements itself (gathering is bypassed)
            self._found_settlements_by_occupancy()

    def _found_settlements_by_occupancy(self) -> None:
        """Settlement founding for the adaptive-connubium path (Cut 2), DECOUPLED from the gathering's mating pools:
        scan persistent-abundant (storable) candidate sites and found/refresh one wherever ≥ settle_min_pool agents
        cluster within settle_radius. Occupancy-driven (Binford collectors settle where people persistently aggregate
        on storable resources), independent of the mating calendar — the gathering path founds the same way but keyed
        to the pools it just built. Reuses the identical gates (settle_persist_threshold / settle_min_pool /
        settle_radius / settle_release_steps) and the top-S_pot min-separated candidate set, so the two paths agree.
        No RNG → the daily _maintain_settlements handles hold/release exactly as for the gathering path."""
        cfg = self._demog
        aqf = self._s_pot_field()
        if aqf is None:
            return
        hf = self._harvest_field
        W = getattr(hf, "width", N); H = getattr(hf, "height", N)
        sep = cfg.aggregation_site_sep
        thr = cfg.settle_persist_threshold
        cands = sorted(((aqf[y, x], x, y) for y in range(H) for x in range(W) if aqf[y, x] >= thr), reverse=True)
        sites: list = []
        for (_, x, y) in cands:
            if all(max(abs(x - sx), abs(y - sy)) >= sep for (sx, sy) in sites):
                sites.append((x, y))
            if len(sites) >= 40:
                break
        rad = cfg.settle_radius
        for (sx, sy) in sites:
            near = sum(1 for a in self.agent_list if self._torus_cheby(a.pos[0], a.pos[1], sx, sy) <= rad)
            if near >= cfg.settle_min_pool:
                self._settlement_sites[(sx, sy)] = cfg.settle_release_steps

    def _do_gathering(self) -> None:
        """Seasonal marriage-aggregation ('the gathering'): every `aggregation_period` steps, in the abundance
        window, dispersed bands converge on abundant SITES; unpaired adults pair ACROSS the bands sharing a site
        (the regional connubium); then disperse. Replaces the daily within-band `_do_pairing`. Isolated bands (no
        site in range) get no gathering → may die (realistic)."""
        cfg = self._demog
        if self.step_count % cfg.aggregation_period != 0:            # not a gathering step
            return
        hf = self._harvest_field
        if hasattr(hf, "season") and hf.season() < cfg.aggregation_season_threshold:
            return                                                  # not the abundance window (static fields: no season → always fire)
        if cfg.divorce_rate > 0.0:
            for a in self.agent_list:
                if a.sex == "female" and a._partner is not None and self.random.random() < cfg.divorce_rate:
                    a._partner._wives.discard(a); a._partner = None
        affil = getattr(cfg, "enable_band_affiliation", False)
        band_sizes = Counter(a._group.band_id for a in self.agent_list) if affil else None
        members: dict = {}
        for a in self.agent_list:
            members.setdefault(a._group.band_id, []).append(a)
        if not members:
            return
        # aggregation SITES: top-capacity cells, min-separated (≈ one abundant gathering-place per region)
        W = getattr(hf, "width", N); H = getattr(hf, "height", N)
        sep = cfg.aggregation_site_sep
        cands = sorted(((hf.level(x, y), x, y) for y in range(H) for x in range(W) if hf.level(x, y) > 0.0), reverse=True)
        sites: list = []
        for (_, x, y) in cands:
            if all(max(abs(x - sx), abs(y - sy)) >= sep for (sx, sy) in sites):
                sites.append((x, y))
            if len(sites) >= 40:
                break
        if not sites:
            return
        # assign each band to its NEAREST site within `aggregation_radius` → connubium pools (bands sharing a site)
        r2 = cfg.aggregation_radius ** 2
        pools: dict = {}
        for bid, ms in members.items():
            n = len(ms); cx = sum(a.pos[0] for a in ms) / n; cy = sum(a.pos[1] for a in ms) / n
            best, bestd = None, r2
            for i, (sx, sy) in enumerate(sites):
                d = (cx - sx) ** 2 + (cy - sy) ** 2
                if d <= bestd:
                    bestd = d; best = i
            if best is not None:
                pools.setdefault(best, []).append(bid)
        for bids in pools.values():
            pool = [a for bid in bids for a in members[bid]]
            females = [a for a in pool if a.sex == "female" and a._partner is None and a.age >= cfg.menarche_months]
            males = [a for a in pool if a.sex == "male" and a.age >= cfg.menarche_months]
            if females and males:
                self._pair_from_pool(females, males, cfg.aggregation_residence, cfg.aggregation_rank_homogamy, band_sizes)
        # Aggregation-sedentism (Layer 1): a pool at a PERSISTENT-ABUNDANT site that reaches settle_min_pool FOUNDS /
        # refreshes a settlement — the gathering that stops dispersing. Held + released each step by _maintain_settlements.
        if getattr(cfg, "enable_aggregation_sedentism", False):
            aqf = self._s_pot_field()            # S_pot = max(aquatic, cultivability) → farming sites qualify too
            rad = cfg.settle_radius
            for si in pools:                      # sites that pooled ≥1 band this gathering
                site = sites[si]
                if aqf is not None and aqf[site[1], site[0]] < cfg.settle_persist_threshold:
                    continue                       # not a persistent-abundant (storable) site
                near = sum(1 for a in self.agent_list
                           if self._torus_cheby(a.pos[0], a.pos[1], site[0], site[1]) <= rad)
                if near >= cfg.settle_min_pool:    # a real multi-band aggregation within the cluster → found/refresh
                    self._settlement_sites[site] = cfg.settle_release_steps

    def _band_knob(self, band_id: int, name: str) -> float:
        """F.3c-2b: the per-band value of a family knob = the GLOBAL config (egalitarian baseline) + the additive
        DELTA of the band's society preset from the egalitarian preset. An egalitarian/un-morphed band returns the
        global value EXACTLY (preserves the E.3 calibration); a morphed band deviates by its society's signature."""
        glob = getattr(self._demog, name)
        soc = self._band_society.get(band_id)
        if soc is None or soc == "egalitarian_forager":
            return glob
        val = glob + (SOCIETY_PRESETS[soc][name] - SOCIETY_PRESETS["egalitarian_forager"][name])
        if name in ("patriline_weight", "lineage_reversion", "paternal_provision_frac"):
            return min(1.0, max(0.0, val))
        return max(0.0, val)

    def _maintain_bands(self) -> None:
        """F.3c-1 emergent band fission/fusion (hysteretic) on the affiliation band_id. FUSION: a band below
        `band_merge_size` joins its nearest neighbour band. FISSION: a band above its split threshold splits along
        its wider spatial axis at the median — a SPATIAL cut (cuts across lineages → keeps bands non-kin, Hill
        2011). F.3c-3: with `enable_dynamic_bands` the split threshold is the CONDITION-DEPENDENT `tolerable_size`
        = base + (hard_cap − base)·assabiyah (rich/high-solidarity bands stay together larger), not a constant."""
        cfg = self._demog
        members: dict[int, list] = {}
        for a in self.agent_list:
            members.setdefault(a._group.band_id, []).append(a)

        def _centroid(ms):
            n = len(ms)
            return (sum(a.pos[0] for a in ms) / n, sum(a.pos[1] for a in ms) / n)

        # F.3c-3 dynamic: update per-band ASSABIYAH (success→solidarity) and the condition-dependent split threshold.
        dynamic = getattr(cfg, "enable_dynamic_bands", False)
        split_thr: dict[int, float] = {}
        if dynamic:
            base, cap = cfg.band_base_tolerable, cfg.band_split_size
            # EMERGENT BAND SIZE: the tolerable FLOOR per band = risk-pooling optimum g*=(mean-cell-CV/cv_safe)²,
            # clamped [band_size_min, cap]; replaces the hardcoded band_base_tolerable. Off ⇒ scalar base (bit-exact).
            emergent_bs = getattr(cfg, "enable_emergent_band_size", False)
            cvf = self._return_cv_field() if emergent_bs else None
            # (RETIRED 2026-07-01, DE-7: the F.3c-3 `season_aggregation` factor scaled tolerable headroom by
            # seasonal abundance → lean-season *fission*. It was mis-signed — moderate lean should not fission
            # (Cashdan/Hawkes) — AND inert (the threshold is dormant, R-31). Superseded by M2 malnutrition fission,
            # which handles the only legitimate resource→fission role via REALIZED starvation.)
            # Stage 1 leader coherence: a SECOND, additive cohesion source (Boehm-gated by society type), read
            # FRESH each step from current membership (no accumulated state) so a leader's death/removal drops it
            # immediately — the benchmark signature is an instant cohesion drop, not a decayed one.
            leader_on = getattr(cfg, "enable_leader_coherence", False)
            leader_gain = getattr(cfg, "leader_coherence_gain", 0.0)
            # Stage 1b size-driven repulsion (Johnson scalar stress): a DISPERSIVE term subtracted from cohesion.
            repulsion_on = getattr(cfg, "enable_size_repulsion", False)
            rep_gain = getattr(cfg, "repulsion_gain", 0.0)
            rep_mid = getattr(cfg, "repulsion_midpoint", 25.0)
            rep_width = getattr(cfg, "repulsion_width", 6.0)
            # M2 malnutrition fission: a band losing members to REALIZED starvation gets a DISPERSIVE term
            # (dispersal-in-response-to-death). Signal = EMA of the band's per-capita starvation-death rate.
            mal_on = getattr(cfg, "enable_malnutrition_fission", False)
            mal_gain = getattr(cfg, "malnutrition_fission_gain", 0.0)
            mal_rate = getattr(cfg, "malnutrition_starv_rate", 0.05)
            mal_alpha = getattr(cfg, "malnutrition_ema_alpha", 0.3)
            starv_step = self._band_starv_this_step
            new_assab: dict[int, float] = {}
            new_leader: dict[int, float] = {}
            new_repulsion: dict[int, float] = {}
            new_malnutrition: dict[int, float] = {}
            new_starv_ema: dict[int, float] = {}
            for bid, ms in members.items():
                surplus = self._band_surplus.get(bid, 0.0)
                a_prev = self._band_assabiyah.get(bid, 0.0)
                a_new = min(1.0, max(0.0, a_prev + cfg.assabiyah_gain * surplus - cfg.assabiyah_decay))
                new_assab[bid] = a_new
                for a in ms:                                   # mirror onto the collective-identity vector
                    a._group.assabiyah = a_new
                society = self._band_society.get(bid)

                leader_term = 0.0
                if leader_on and leader_gain > 0.0:
                    statuses = [a.cred * getattr(a, "prowess", 1.0) for a in ms]
                    mean_status = sum(statuses) / len(statuses)
                    top_status = max(statuses)
                    ratio = top_status / (mean_status + 1e-9)          # ≥1; 1 = no distinct leader
                    leader_strength = 1.0 - 1.0 / ratio                # self-normalizing, saturating ∈ [0,1)
                    weight = leader_society_weight(society)            # Boehm gate
                    leader_term = leader_gain * weight * leader_strength
                new_leader[bid] = leader_term

                repulsion = 0.0
                if repulsion_on and rep_gain > 0.0:
                    repulsion = size_repulsion(len(ms), rep_gain, rep_mid, rep_width, society)
                new_repulsion[bid] = repulsion

                # M2: update the band's per-capita starvation-rate EMA (this step's starvation deaths / pre-death
                # band size), then a saturating dispersion pressure. Off ⇒ 0 (bit-exact). REACTIVE to realized death.
                starv_ct = starv_step.get(bid, 0)
                pre_n = len(ms) + starv_ct                             # pre-death band size (survivors + starved)
                rate = starv_ct / pre_n if pre_n > 0 else 0.0
                ema = (1.0 - mal_alpha) * self._band_starv_ema.get(bid, 0.0) + mal_alpha * rate
                new_starv_ema[bid] = ema
                malnutrition = 0.0
                if mal_on and mal_gain > 0.0:
                    malnutrition = mal_gain * min(1.0, ema / mal_rate)  # saturates at the reference starvation rate
                new_malnutrition[bid] = malnutrition

                # cohesion − dispersion, clamped: a large band (high repulsion / malnutrition) needs strong
                # assabiyah+leader to stay whole; the [0,1] clamp keeps band_split_size the hard cap and can't push
                # tolerable below base_tolerable (the Wobst floor) — so malnutrition fissions ONLY bands > base
                # (large ones), small bands untouched. Off ⇒ repulsion+malnutrition 0 ⇒ min(1, a+l), bit-exact.
                cohesion_frac = min(1.0, max(0.0, a_new + leader_term - repulsion - malnutrition))
                base_b = base
                if cvf is not None and ms:                          # emergent floor = risk-pooling optimum from band CV
                    mean_cv = sum(float(cvf[a.pos[1], a.pos[0]]) for a in ms) / len(ms)
                    g_star = (mean_cv / cfg.cv_safe) ** 2
                    base_b = min(max(g_star, float(cfg.band_size_min)), float(cap))
                split_thr[bid] = base_b + (cap - base_b) * cohesion_frac
                # Stage 1 SUPRA-BAND SCALING: net payoff ABOVE saturation (unclamped − 1) adds village headroom beyond
                # the hard cap (Johnson: hierarchy+payoff overcome scalar stress). Since a_new≤1, net>1 REQUIRES the
                # leader term ⇒ villages need hierarchy. Off ⇒ no headroom ⇒ hard cap, bit-exact.
                if getattr(cfg, "enable_village_scaling", False) and cfg.village_gain > 0.0:
                    net_raw = a_new + leader_term - repulsion - malnutrition
                    if net_raw > 1.0:
                        split_thr[bid] += cfg.village_gain * (cap - base) * (net_raw - 1.0)
            self._band_assabiyah = new_assab
            self._band_leader_term = new_leader
            self._band_repulsion = new_repulsion
            self._band_malnutrition = new_malnutrition
            self._band_starv_ema = new_starv_ema

        # FUSION (small band joins another band). Default = NEAREST neighbour. F: resource-directed — the RICHEST
        # (`_band_surplus`) neighbour within `fusion_search_radius` (a starving remnant merges into a well-provisioned
        # band; Wiessner hxaro), falling back to nearest if none is in range. Off ⇒ nearest, bit-exact.
        rdf_on = getattr(cfg, "enable_resource_directed_fusion", False)
        rdf_r2 = getattr(cfg, "fusion_search_radius", 25.0) ** 2
        for bid in [b for b, ms in members.items() if len(ms) < cfg.band_merge_size]:
            if len(members) <= 1:
                break
            cx, cy = _centroid(members[bid])
            others = [b for b in members if b != bid]
            _d2 = lambda b: (lambda c: (c[0] - cx) ** 2 + (c[1] - cy) ** 2)(_centroid(members[b]))
            if rdf_on:
                nearby = [b for b in others if _d2(b) <= rdf_r2]
                nb = max(nearby, key=lambda b: self._band_surplus.get(b, 0.0)) if nearby else min(others, key=_d2)
            else:
                nb = min(others, key=_d2)
            for a in members[bid]:
                a._group.band_id = nb
            members[nb].extend(members.pop(bid))
        # FISSION (above the split threshold → spatial median split)
        for bid in [b for b, ms in members.items() if len(ms) > split_thr.get(b, cfg.band_split_size)]:
            ms = members[bid]
            xs = [a.pos[0] for a in ms]; ys = [a.pos[1] for a in ms]
            if (max(xs) - min(xs)) >= (max(ys) - min(ys)):
                med = sorted(xs)[len(xs) // 2]; side = lambda a: a.pos[0] >= med
            else:
                med = sorted(ys)[len(ys) // 2]; side = lambda a: a.pos[1] >= med
            new_id = self._next_band_id; self._next_band_id += 1
            for a in ms:
                if side(a):
                    a._group.band_id = new_id

    def _maintain_village_budding(self) -> None:
        """Bandy 2004 / Chagnon 1975 VILLAGE FISSIONING — the ethnographic settlement-SPREAD/recovery mode. A VILLAGE
        (the multi-band cluster within settle_radius of a settlement site) grown past `village_fission_threshold`
        sheds its RIVAL faction — the SECOND-largest lineage bloc (Chagnon: fission along the lineage/leadership
        cleavage) — which RELOCATES to a nearby available STORABLE site and founds a DAUGHTER village (new band_id).
        So settlements PROPAGATE by budding, not only by aggregating scattered individuals (the mode aggregation-only
        lacked — R-68), and re-spread across the landscape after a crash. Fission is SUPPRESSED once the village
        STRATIFIES (integrative institutions — Bandy → the Carneiro fork; the existing morph grows those villages
        instead). CIRCUMSCRIPTION (Bandy p.330): the fission threshold RISES with the relocation distance to the nearest
        OPEN site — base ~170 (open landscape) → ~277 (circumscribed) — so budding self-limits as the landscape fills,
        and where no open site is in reach the village grows + stratifies. Operates on the SETTLEMENT (not band_id),
        so the band~25 fission scale is untouched. No RNG
        (deterministic cleavage + siting). Default OFF ⇒ never called (bit-exact)."""
        cfg = self._demog
        aqf = self._s_pot_field()
        if aqf is None or not self._settlement_sites:
            return
        thr_base = cfg.village_fission_threshold; circ_gain = cfg.village_circumscription_gain
        minf = cfg.village_bud_min_faction
        R = cfg.village_bud_search_radius; persist = cfg.settle_persist_threshold; sep = cfg.settle_radius
        hf = self._harvest_field; W = getattr(hf, "width", N); H = getattr(hf, "height", N)
        cell_agents: dict = {}
        for a in self.agent_list:
            cell_agents.setdefault(a.pos, []).append(a)
        occ = {c: len(v) for c, v in cell_agents.items()}
        for (sx, sy) in list(self._settlement_sites):
            village = [a for dx in range(-sep, sep + 1) for dy in range(-sep, sep + 1)
                       for a in cell_agents.get((sx + dx, sy + dy), ())]
            if len(village) <= thr_base:            # below even the open-landscape threshold → can't fission
                continue
            bids = Counter(a._group.band_id for a in village)
            if "stratified" in str(self._band_society.get(bids.most_common(1)[0][0], "")):
                continue                                            # integrated village → fission suppressed (Bandy)
            lin_ct = Counter(getattr(a, "_lineage", None) for a in village)
            top = [l for l, _ in lin_ct.most_common(2) if l is not None]
            if len(top) < 2:
                continue                                            # single-lineage village → no cleavage line
            faction = [a for a in village if getattr(a, "_lineage", None) == top[1]]
            if len(faction) < minf * len(village):
                continue                                            # rival bloc too small to carry a fission
            # NEAREST open storable daughter site (its distance = the relocation cost that drives circumscription)
            best, bestd = None, R + 1
            for yy in range(max(0, sy - R), min(H, sy + R + 1)):
                for xx in range(max(0, sx - R), min(W, sx + R + 1)):
                    d = max(abs(xx - sx), abs(yy - sy))
                    if d < sep + 1 or d >= bestd or float(aqf[yy, xx]) < persist:
                        continue                                    # own catchment, farther than best, or not storable
                    if (xx, yy) in self._settlement_sites or occ.get((xx, yy), 0) >= cfg.settle_min_pool:
                        continue                                    # already an occupied settlement → not open
                    best, bestd = (xx, yy), d
            if best is None:
                continue         # CIRCUMSCRIBED (no open site in reach) → no bud → village grows + stratifies (Bandy → morph)
            # Bandy fission COST: the threshold RISES with relocation distance — base (open) → ~+60% when circumscribed
            if len(village) <= thr_base * (1.0 + circ_gain * bestd / R):
                continue                                            # not large enough to justify relocation at this cost
            new_id = self._next_band_id; self._next_band_id += 1     # BUD: rival faction migrates + founds the daughter
            for a in faction:
                a._group.band_id = new_id; a.pos = best
            self._settlement_sites[best] = cfg.settle_release_steps

    def _band_groups(self, occ_lists: dict, radius: int) -> list[list]:
        """Partition occupied cells into spatially-connected BANDS for the lumping ablation. radius≤0 ⇒ each cell
        is its own band (per-cell); radius≥1 ⇒ cells linked when Chebyshev-adjacent within `radius` (the mate-gate
        neighbourhood) are one band (union-find). Returns the member-lists with >1 agent (singletons can't lump)."""
        if radius <= 0:
            return [occ for occ in occ_lists.values() if len(occ) > 1]
        cellset = set(occ_lists)
        parent = {c: c for c in cellset}

        def find(c):
            while parent[c] != c:
                parent[c] = parent[parent[c]]
                c = parent[c]
            return c

        for (x, y) in cellset:
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    nb = (x + dx, y + dy)
                    if nb in cellset:
                        parent[find((x, y))] = find(nb)
        bands: dict[tuple[int, int], list] = {}
        for c, occ in occ_lists.items():
            bands.setdefault(find(c), []).extend(occ)
        return [m for m in bands.values() if len(m) > 1]

    def _a2_mult(self, a, occ_count) -> float:
        """Step-2 baseline-mortality (a2) multiplier from the live modulators (1.0 if all flags off) —
        the only Siler term the world modulates. Capped (red-team n-1). Pathogen OFF in 2b."""
        cfg = self._demog
        m = 1.0
        if cfg.enable_terrain_risk:
            m *= risk_mult(float(self._fields.risk[a.pos[1], a.pos[0]]), self._risk_ref, cfg.risk_cap)
        if cfg.enable_density_disease:
            rho = occ_count.get(a.pos, 1) / _CELL_KM2           # agents/km²
            m *= density_mult(rho, cfg.dens_delta, cfg.dens_rho_half)
        if cfg.enable_band_risk and cfg.band_risk_penalty > 0.0:
            # F.2 band risk-dilution: a sub-band group faces elevated biome (accident/predation) risk, scaled by
            # the cell's own incident rate; a full band (g ≥ band_risk_size) → factor 1 (anchored baseline).
            x0, y0 = a.pos
            r = cfg.bonded_mate_radius
            g = sum(occ_count.get((x0 + dx, y0 + dy), 0)
                    for dx in range(-r, r + 1) for dy in range(-r, r + 1))   # band size (mate-gate neighbourhood)
            biome_risk = (float(self._fields.risk[y0, x0]) / self._risk_ref) if self._risk_ref > 0.0 else 1.0
            loner = max(0.0, 1.0 - g / cfg.band_risk_size)
            m *= 1.0 + cfg.band_risk_penalty * biome_risk * loner
        if cfg.enable_terrain_pathogen:                        # S2 biome disease-ecology (Cashdan; NPP proxy)
            m *= pathogen_mult(float(self._fields.npp[a.pos[1], a.pos[0]]), self._pathogen_npp_ref,
                               cfg.pathogen_gamma, cfg.pathogen_cap)
        if cfg.enable_nutrition_synergy:
            if cfg.enable_condition:                           # S0: disease potentiated by SUSTAINED condition (EMA)
                m *= 1.0 + (cfg.mu_max - 1.0) * (1.0 - a._condition)
            else:                                              # legacy: instantaneous post-harvest reserve
                _rs = a.reserve_scale()                        # C.2a age-scaled floor/full
                m *= synergy_mult(a._fed_reserve, a.reserve_floor * _rs, self._reserve_full * _rs, cfg.mu_max)
        if m > cfg.a2_cap:
            self.a2_cap_hits += 1
            return cfg.a2_cap
        return m

    # ── Diagnostics ──────────────────────────────────────────────────────────

    def population(self) -> int:
        return len(self.agent_list)

    def mean_reserve(self) -> float:
        if not self.agent_list:
            return 0.0
        return sum(a.wealth for a in self.agent_list) / len(self.agent_list)

    def mean_age(self) -> float:
        if not self.agent_list:
            return 0.0
        return sum(a.age for a in self.agent_list) / len(self.agent_list)

    def any_alive_below_floor(self) -> bool:
        return any(a.wealth < self._reserve_floor for a in self.agent_list)
