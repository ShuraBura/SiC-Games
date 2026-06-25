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

import mesa

from sic_games.agents.base import BaseAgent
from sic_games.agents.costs import KcalBurnModel
from sic_games.agents.perception import LocalVisionPerception
from sic_games.agents.strategies.carbon import CarbonDecision
from sic_games.agents.traits import TraitVector
from sic_games.config import KcalEconomyConfig, LifeHistoryConfig, SubstrateConfig
from sic_games.demography import (
    DemographyConfig, density_mult, energetic_fertility_factor, is_fertile, pathogen_mult, risk_mult, synergy_mult,
)
from sic_games.substrate import compute_harvest_shares, diffusion_select_target, base_status
from sic_games.terrain import N, WorldFields, generate_world
from sic_games.terrain_field import TerrainField

_CELL_KM2 = 100.0   # CC-1: each cell = 100 km² (local density = cell occupancy / _CELL_KM2)

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
        self._carbon_cfg = carbon_cfg
        self._placement_positions = placement_positions
        self._substrate_cfg = substrate_cfg
        self._rivalrous = substrate_cfg is not None and substrate_cfg.enabled
        self._harvest_field = harvest_field if harvest_field is not None else self.terrain_field
        self._cell_store: dict[tuple[int, int], float] = {}   # collective band granary per cell (delayed-return; §4.5.11 S.1)

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

        self._init_agents(n_agents, kcal_cfg, lh_cfg)

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
            agent._lineage = fid                         # each founder seeds a unique lineage (patriline tracking)
            if self._demog is not None:
                agent.age = self._sample_founder_age()   # staggered founders (stationary ∝ l(x))
            if getattr(agent, "use_cred_status", False) and self._demog.cred_seed_sigma > 0.0:
                s = self._demog.cred_seed_sigma          # founder status ~ lognormal(median 1) → the heritable hierarchy
                agent.cred = math.exp(self.random.normalvariate(0.0, s))
            self.agent_list.append(agent)
            self.occupied.add(pos)   # set: founder stacking (many agents, one cell) is allowed

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
        agent._mother = None                      # C.2b mother-link (set at IBI birth) for provisioning
        agent._father = None                      # B+ step 4: father-link (set at IBI birth via mate-choice)
        agent._lineage = None                     # lineage-tracking ID (founder-seeded; patrilineal descent)
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
        self.starv_cred_this_step: list[float] = []   # diagnostic: cred of agents lost to starvation this step
        self.starv_status_this_step: list[float] = []  # diagnostic: combined status (cred·prowess) at starvation
        self.prov_young_maternal = 0.0   # diagnostic: kcal provisioned to <3-yr children by mother (Marlowe calib)
        self.prov_young_paternal = 0.0   # diagnostic: "" by father (male share = paternal/(maternal+paternal))
        self.mate_pairs_this_step: list[tuple[float, float]] = []   # (mother status, father status) — assortment

        if self._rivalrous:
            self._step_rivalrous()
        else:
            agents = list(self.agent_list)
            self.random.shuffle(agents)
            for agent in agents:
                if not agent.alive:
                    continue
                self._step_agent(agent)

        # Prune dead agents
        for a in self.agent_list:
            if not a.alive:
                self.occupied.discard(a.pos)
        self.agent_list = [a for a in self.agent_list if a.alive]

        # Demographic layer: births (opt-in)
        if self._demog is not None:
            self._do_births_ibi()
        elif self._reproduction:
            self._do_births()
        self.occupied = {a.pos for a in self.agent_list}

    def _step_rivalrous(self) -> None:
        """Stage-6.0a multi-occupancy substrate on the terrain field (forage-only).
        Diffusion movement (per-capita yield) → per-cell harvest split → metabolism."""
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

        # 2. diffusion movement (per-capita-yield, self-limiting)
        agents = list(self.agent_list)
        self.random.shuffle(agents)
        for agent in agents:
            old = agent.pos
            temp = None
            tfn = getattr(agent._decision, "temperature", None)
            if callable(tfn):
                temp = tfn(agent)
            target = diffusion_select_target(agent, tf, occ_count, occ_wsum, sc, agent.random, temp)
            if target != old and self._fields.isWater[target[1], target[0]] != 0:
                target = old   # terrain guard: never step onto water (diffusion is water-blind)
            if target != old:
                occ_count[old] -= 1
                if occ_count[old] == 0:
                    del occ_count[old]
                occ_count[target] = occ_count.get(target, 0) + 1
                if occ_wsum is not None:
                    wt = base_status(agent, phi_eps) ** kappa if agent.strategy == "carbon" else 1.0
                    occ_wsum[old] = occ_wsum.get(old, 0.0) - wt
                    occ_wsum[target] = occ_wsum.get(target, 0.0) + wt
                agent.pos = target
        self.occupied = set(occ_count.keys())

        # 3. per-cell harvest split (forage-only; S = cell total return rate, flow)
        occ_lists: dict[tuple[int, int], list[BaseAgent]] = {}
        for a in self.agent_list:
            occ_lists.setdefault(a.pos, []).append(a)
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
        store_cap_mult = demog.store_capacity_reserves if store_on else 0.0
        store_temp_thr = demog.storage_temp_threshold_c if store_on else 0.0
        provision_pool: dict = {}              # C.2b: mother → harvest overflow available to dependents
        for (cx, cy), occ in occ_lists.items():
            S = tf.level(cx, cy)
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
                f_sh = compute_harvest_shares(occ, (1.0 - meat_frac) * S, 0.0, phi_eps)
                m_sh = compute_harvest_shares(occ, meat_pool, kappa, phi_eps)
                shares = [f + m for f, m in zip(f_sh, m_sh)]
            else:
                shares = compute_harvest_shares(occ, S, kappa, phi_eps)
            msh = m_sh if game_on else [0.0] * len(occ)
            if sex_div > 0.0:
                # Step 3: sex-divided PRODUCTION credit (prowess signal only) — meat → male hunters, forage →
                # female gatherers. Independent of the Cred-weighted consumption share below.
                n_m = sum(1 for a in occ if a.sex == "male")
                male_credit = (meat_pool / n_m) if n_m else 0.0
                female_credit = ((1.0 - meat_frac) * S / (len(occ) - n_m)) if (len(occ) - n_m) else 0.0
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
                        banked = store_frac * overflow
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
                    deficits = [(a, self._reserve_full * a.reserve_scale() - a.wealth) for a in occ]
                    tot_def = sum(d for _, d in deficits if d > 0.0)
                    if tot_def > 0.0:
                        drawn = store if store < tot_def else tot_def
                        for a, d in deficits:
                            if d > 0.0:
                                a.wealth += drawn * (d / tot_def)            # need-proportional (S.1 egalitarian)
                        store -= drawn
                self._cell_store[key] = store

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
                    grp = [a for a in al if a.sex == sx and getattr(a, "_use_prowess", False)]
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
            a.age += 1
            if demog is not None:
                a.months_since_birth += 1
                if a.wealth <= a.reserve_floor * a.reserve_scale():   # C.2a age-scaled starvation floor
                    a.alive = False
                    self.deaths_starv_this_step += 1
                    self.starv_cred_this_step.append(a.cred)
                    self.starv_status_this_step.append(a.cred * getattr(a, "prowess", 1.0))
                else:
                    a2m = self._a2_mult(a, occ_count)     # Step-2 a2 modulators (1.0 if all flags off)
                    if a.random.random() < self._siler[a.sex].monthly_death_prob(a.age, a2m):
                        a.alive = False                   # Siler baseline+senescence
                        self.deaths_senesc_this_step += 1
            elif a.wealth <= a.reserve_floor:
                a.alive = False
                self.deaths_starv_this_step += 1
            elif a.age >= a.max_age:
                a.alive = False
                self.deaths_senesc_this_step += 1

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
        newborns: list[BaseAgent] = []
        for a in self.agent_list:
            if a.sex != "female":
                continue
            if not is_fertile(a.age, a.months_since_birth, cfg):
                continue
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
                child._lineage = a._lineage                                # default matriline (overridden to patriline if a father is assigned)
                if getattr(child, "use_cred_status", False):               # heritable lineage (cred)
                    si = cfg.cred_inherit_sigma
                    # MEAN-1 lognormal noise (E[noise]=1): mean-preserving, so inheritance adds no multiplicative
                    # upward bias across generations (red-team BLOCKER fix — `exp(N(0,σ))` had mean exp(σ²/2)>1).
                    noise = math.exp(self.random.normalvariate(-0.5 * si * si, si)) if si > 0.0 else 1.0
                    if paternity:
                        # mate-choice: prowess-weighted father (m=0 → random); bilateral lineage = blend of the
                        # parents' TOTAL standing (cred·prowess — folds the father's hunting record in).
                        if males:
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
                        child._lineage = father._lineage if father is not None else a._lineage   # patriline
                        if father is not None:
                            self.mate_pairs_this_step.append(
                                (a.cred * getattr(a, "prowess", 1.0), father.cred * getattr(father, "prowess", 1.0)))
                        t_mom = a.cred * getattr(a, "prowess", 1.0)
                        if father is not None:
                            pw = cfg.patriline_weight
                            base = (1.0 - pw) * t_mom + pw * (father.cred * getattr(father, "prowess", 1.0))
                        else:
                            base = t_mom                                   # matrilineal fallback (no adult males)
                    else:
                        base = a.cred                                      # step-1 matrilineal (paternity off)
                    # Mean-reversion toward a FIXED anchor (1.0 = founder median) — a TRUE contraction that bounds
                    # the no-decay lineage facet (red-team BLOCKER fix: the co-moving population mean was NOT a
                    # contraction → unbounded drift). ρ=0 ⇒ pure mean-1 multiplicative copy (R-18/step-1).
                    child.cred = (1.0 - cfg.lineage_reversion) * base * noise + cfg.lineage_reversion * 1.0
                child.wealth = self._reserve_full * child.reserve_scale()   # C.2a body-sized neonatal reserve
                newborns.append(child)
                self.births_this_step += 1
        self.agent_list.extend(newborns)

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
