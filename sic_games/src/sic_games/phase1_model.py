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
    DemographyConfig, MONTHS_PER_YEAR, density_mult, energetic_fertility_factor, energetic_refractory, is_fertile, sedentism_ibi,
    pathogen_mult, risk_mult, synergy_mult,
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



RESENT_EFFECT_CAP = 5.0   # R-94: a uniform-ish band can give an enormous effect size off a tiny absolute gap;
                          # cap so one degenerate band cannot dominate the EMA
_RANK_LADDER = {"egalitarian_forager": "complex_forager",      # R-98: rank promotes ONE rung, never further
                "complex_forager": "stratified_chiefdom",
                "stratified_chiefdom": "stratified_chiefdom"}
LEGIT_RELAX = 0.02   # R-86: per-step relaxation rate of cred toward its legitimacy-set target
                     # (~50-step approach). A RATE; the magnitude is `legit_cred_gain`.

# ── REALISED DEMOGRAPHIC INSTRUMENTS (R-106, 2026-08-12) ──────────────────────────────────────────────────
# WHY THESE EXIST. The model is CONFIGURED with a Siler schedule (ACHE_FOREST, e0 = 36.6 yr) and a fertility
# schedule (expected IBI 38.3 months, ceiling TFR 9). Nothing ever measured the schedules it actually
# REALISES. When they were finally derived from the age structure, the run was realising e0 ~ 19 yr — a
# little over half the calibration — which is what drives `frac_child` to 0.60 against a verified [0.287,
# 0.454] and `dependency_ratio` to 1.81 against [0.598, 0.899]. The excess is monotone in age (0-5 runs
# 1.17x the predicted share, 60+ runs 0.59x), so it is an age-graded mortality distortion; and it CANNOT be
# a fertility effect, because reproducing the observed age structure would need TFR ~14.3, well beyond the
# model's own arithmetic ceiling of 9.
#
# The rule this obeys is the project's own: validate the instrument before turning any knob. A configured
# schedule and a realised schedule are two different objects, and only the second one explains a run.
# Everything here is a PURE OBSERVER — no RNG draws, no read-back into any dynamic — so every prior run
# stays bit-exact and no flag gates it.
LT_MAX_AGE_YR = 100    # life-table / ASFR bands, ONE YEAR wide; ages at or above this fold into the last bin
IBI_HIST_MAX = 120     # realised-IBI histogram span in months (10 yr); the final bin is the 120+ overflow


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
            # `lh_eta_juvenile_exponent` is a PASSTHROUGH only — the value's home is LifeHistoryConfig; this is
            # the sole route to reach the auto-built one, since callers that set `enable_life_history` never
            # construct an lh_cfg themselves.
            self._lh_cfg = LifeHistoryConfig(
                forage_age_min=180, forage_age_max_offset=120,
                eta_min=getattr(demography_cfg, "lh_eta_min", 0.2),
                eta_juvenile_exponent=getattr(demography_cfg, "lh_eta_juvenile_exponent", 1.0))
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
        self._between_band_gini: float | None = None           # R-103 relational: regional between-band cred Gini (set in morph when on)
        self._band_settle: dict[int, int] = {}                 # F.3c-2 per-band settlement timer (hysteresis)
        self._band_surplus: dict[int, float] = {}              # F.3c-3 per-band surplus_frac (from the morph detector)
        self._band_cred_gini: dict[int, float] = {}            # R-103 per-band cred Gini (inequality gate; empty unless on)
        self.obligation_grants = 0                             # CUMULATIVE wealth->obligation grants
        self.bud_events = 0                                    # CUMULATIVE village fissions (not per-step): the
        #   realised rate, to be compared back against Bandy's 2-5e-3 per large-village-year
        self._founding_pot_cache = None                        # storability-weighted founding potential (cached)
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
        self._settlement_hardship: dict[tuple[int, int], float] = {}  # emergent abandonment: per-SITE EMA of remembered hardship (the village's memory)
        self._aggl_R_cache = None                                 # agglomeration: cached intensive catchment-resource field R(c) = tier2·Σ_catchment S_pot (catchment mode)
        self._aggl_point_cache = None                             # agglomeration: cached POINT base A_cell = tier2·S_pot·cv_ref (point-superlinear mode, Branch A)
        self._village_home_cache = None                           # catchment spread: per-step cache site → (cells, cum-weights, total) for the home-cell lottery
        self._village_pop_cache = None                            # village-scaled disease: per-step cache site → village population
        self._village_pop_step = -1
        self._forage_cap_cache = None                             # per-person forage cap field = forage_kcal · forage_cap_hours (absent ⇒ no cap)
        self._village_band: dict[tuple[int, int], int] = {}       # settlement site → its stable village band_id (village identity)
        self._village_bands: set[int] = set()                     # band_ids that ARE settled villages → exempt from band fission
        self._meat_frac_cache = None                              # per-cell diet meat fraction from terrain.MEAT_FRAC (absent ⇒ the scalar game_meat_frac)
        self._meat_cv_cache = None                                # per-cell day-to-day meat CV from terrain.MEAT_CV (absent ⇒ terrain.HUNT_CV)
        self._diag_pool = None                                    # DIAGNOSTIC: set to {} to record per-cell (S, occupancy) each harvest; None ⇒ off
        self._move_cost_cache = None                              # Stage 1b terrain move cost field = move_cost_kcal · cost (absent ⇒ free movement)
        self._site_cache = None                                   # Stage 1c catchment site-suitability field (central-place appraisal; absent ⇒ off)
        self._orphan_e_cache = None                               # R-74: endogenous E[mult] divisor (per-step cache)
        self._orphan_e_step = -1
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
        self._next_lineage_id: int = 0                         # R-90: lineage-id allocator for BRANCHING (new named
        # lines founded post-hoc). Bumped past the founder block below, since founders take ids 0..n_agents-1.
        self._next_subclan_id: int = 0                         # R-92: allocator for heritable sub-branch tags
        self._next_band_id: int = 0                            # band-id allocator. Initialised UNCONDITIONALLY: the
        # F.3c-1 seeding block below re-zeroes it under `enable_band_affiliation` (bit-exact), but `_maintain_leader_office`
        # runs OUTSIDE that guard and allocates from it on a desertion-with-nowhere-to-go — so with affiliation OFF the
        # attribute simply did not exist and the office crashed. Found by the charter flag audit, not by the R-84 tests,
        # because every R-84 test world sets enable_band_affiliation=True.
        self._band_office: dict[int, int] = {}                 # R-84: band_id → INCUMBENT leader unique_id (the office, held across steps)
        self._office_since: dict[int, int] = {}                # R-84: leader uid → step he took office (tenure is clocked on the MAN, not the band)
        self._tenures_closed: list[int] = []                   # R-84: completed tenure lengths in steps (the tenure diagnostic)
        self._ever_leader: set[int] = set()                    # R-84: every uid that has ever held office (for the Hayden 75% father-son test)
        self._lineage_office_count: dict = {}                  # R-101: how many times each LINEAGE has TAKEN office.
        # A count, not a set: 'has this lineage held office before' is TRUE BY CONSTRUCTION for anyone currently
        # holding it, so the set version could only ever return 1.0. Repeat acquisitions are the real signal.
        self._lineage_legit: dict[int, float] = {}             # R-86: per-LINEAGE legitimacy stock (Friedman); mirrors _band_surplus
        self._band_resentment: dict[int, float] = {}           # R-87: slow per-band resentment EMA (the LAG that H-CYCLES rides on)
        self._lineage_ascribed: set[int] = set()               # R-86: lineages that CROSSED — 'descended from higher nats'.
        # The RATCHET. Once believed, descent is not re-earned each season; this is what separates ascribed rank
        # from a Big Man's contingent renown, and a decaying stock alone reproduced only the latter.
        self._office_end: dict[str, int] = {"death": 0, "collision": 0, "deposed": 0}  # R-84: WHY tenures end
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
        # ── realised life table + realised fertility schedule (see LT_MAX_AGE_YR above) ──────────────────
        # CUMULATIVE over the run, never reset, so a period rate is obtained by differencing two snapshots.
        # That is deliberate: a trailing window stored in the model would need a window length, and the
        # length would become a parameter nobody anchored. Differencing leaves the choice to the analysis.
        self.lt_exposure: list[int] = [0] * LT_MAX_AGE_YR       # person-months lived, by integer age (years)
        self.lt_deaths: list[int] = [0] * LT_MAX_AGE_YR         # deaths, by integer age
        self.lt_deaths_starv: list[int] = [0] * LT_MAX_AGE_YR   # ...of which the starvation floor
        self.lt_deaths_senesc: list[int] = [0] * LT_MAX_AGE_YR  # ...of which Siler / orphan / max-age
        # SEX-SPLIT EXPOSURE AND DEATHS. The model runs a SEX-SPLIT Siler (`_sex_split`, female higher a1,
        # male higher a3, crossover in adolescence) and nothing has ever checked the realised split. Male
        # exposure is (lt_exposure - lt_exposure_f), so only the female arrays are carried.
        self.lt_exposure_f: list[int] = [0] * LT_MAX_AGE_YR
        self.lt_deaths_f: list[int] = [0] * LT_MAX_AGE_YR
        self.fert_exposure: list[int] = [0] * LT_MAX_AGE_YR     # woman-months lived (the ASFR denominator)
        self.fert_births: list[int] = [0] * LT_MAX_AGE_YR       # births by MOTHER's integer age (numerator)
        self.ibi_hist: list[int] = [0] * (IBI_HIST_MAX + 1)     # realised months between successive births
        # The fertility MULTIPLIER actually applied, sampled over women who passed the age+IBI gate. This is
        # the direct test of whether an energetic brake bites: `enable_energetic_fertility` was found dead
        # because the reserve it reads re-saturates at the cap for ~99% of agents, and `enable_intake_
        # fertility` was built to replace it. Whether the replacement carries signal has never been measured.
        self.fert_factor_sum: float = 0.0
        self.fert_factor_n: int = 0
        self.fert_factor_sat: int = 0                           # count with multiplier >= 0.999 (no brake)
        # WHO STARVES, AND WHERE. Every other intake diagnostic samples the LIVING, so the starved never
        # appear in it. See `_note_starvation_state`. Sums, not samples: O(1) per death.
        self.starv_events: int = 0
        self.starv_occ_sum: float = 0.0        # occupancy of the cell, at the moment of death
        self.starv_age_sum: float = 0.0        # age in months
        self.starv_intake_sum: float = 0.0     # last intake / own requirement
        self.starv_ema_sum: float = 0.0        # the smoothed signal a fertility brake would have read
        # ACUTE vs CHRONIC (2026-08-25): _fed_reserve is the agent's post-harvest reserve THIS step. A high
        # value the step before death = an ACUTE one-step crash (was fine, share collapsed); a low value = a
        # CHRONIC decline (dwelt near the floor). Distinguishes "flee an emergency" from "slow starvation".
        self.starv_fedres_sum: float = 0.0     # _fed_reserve at death, as a fraction of the reserve cap
        self.starv_acute_n: int = 0            # deaths where _fed_reserve was > 50% of cap the step before
        self.starv_by_age: list[int] = [0] * LT_MAX_AGE_YR
        # FLOW RATES AND THEIR TWO MISSING INPUTS. CBR, CDR and r all fall out of the arrays above, but two
        # quantities do not and both have anchors. The realised SEX RATIO AT BIRTH checks that `srb_male`
        # (0.512) survives the birth path — a drift here would bias every adult sex ratio and marriage-market
        # marker downstream. The AGE AT FIRST BIRTH is the cohort entry point that `menarche_months` and
        # `fecundability` jointly imply, and nothing measured it.
        self.births_male: int = 0
        self.births_female: int = 0
        self.first_birth_age_sum: float = 0.0     # mother's age in MONTHS at her parity-1 birth
        self.first_birth_n: int = 0
        # a2-modulator decomposition (see _a2_mult). Cumulative sums; mean = sum / a2_n.
        self.a2_n: int = 0
        self.a2_risk_sum: float = 0.0
        self.a2_dens_sum: float = 0.0
        self.a2_syn_sum: float = 0.0
        self.a2_total_sum: float = 0.0
        self.a2_cond_sum: float = 0.0
        # diag (2026-08-11): the settlement-founding/budding methods are called directly (no step()) by several
        # existing tests, and by any future caller that wants the founding logic without a full step. Pre-seeded
        # here for the same reason as the three counters above — step()'s own reset block still zeroes these
        # every step, so this line changes no run's behaviour and only fixes reads BEFORE the first step().
        self.settle_formed_this_step: int = 0
        self.settle_released_this_step: int = 0
        self.bud_events_this_step: int = 0

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
            agent._subclan = fid                         # R-92: and its first sub-branch
            if fid >= self._next_lineage_id:             # R-90: keep the branch allocator clear of founder ids
                self._next_lineage_id = fid + 1
            if fid >= self._next_subclan_id:
                self._next_subclan_id = fid + 1
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
        agent.material = 0.0                       # R-82 Stage A: the DURABLE capital cell (granary leftover
                                                   # captured; persists, unlike burned `wealth`)
        # R-82: AGGRANDIZER type (Hayden 1995) — an ambition/strategy trait held by a MINORITY, present in every
        # society and INDEPENDENT of inherited cred. Aggrandizers exist everywhere; the gate decides if they act.
        _af = getattr(self._demog, "aggrandizer_frac", 0.0) if self._demog is not None else 0.0
        agent.aggrandizer = 1.0 if (_af > 0.0 and self.random.random() < _af) else 0.0
        agent._use_prowess = (agent.use_cred_status and getattr(self._demog, "enable_prowess_facet", False))
        agent._founder_store = 0.0                 # founder mobile-reserve (set for founders in _init_agents); 0 for newborns
        agent._creditor = None                     # C: standing obligation — who holds a claim on his output
        agent._debt = 0.0                          #    remaining claim, in material units
        agent._partner = None                      # F.3a: a FEMALE's husband link (None = unpaired). Males use _wives.
        agent._wives = set()                       # F.3a: a MALE's wives (≥1 ⇒ married; >1 ⇒ polygynous)
        agent._group = GroupVector()               # F.3c collective-identity vector (band_id assigned below / inherited)
        agent._mother = None                      # C.2b mother-link (set at IBI birth) for provisioning
        agent._father = None                      # B+ step 4: father-link (set at IBI birth via mate-choice)
        agent._lineage = None                     # lineage-tracking ID (founder-seeded; patrilineal descent)
        agent._subclan = None                     # R-92: heritable SUB-branch tag within the lineage. Inherited
        # patrilineally exactly like `_lineage`, so members sharing a tag ARE a descent group BY CONSTRUCTION —
        # which is what makes a genealogically coherent split possible without walking ancestor chains (measured:
        # live patriline chains in this model are at most 2 deep, so chain-walking cannot find a real sub-clade).
        agent._genome = None                      # neutral-marker genome (population genetics; founder-seeded / inherited when enabled)
        # P6 social capital: relational standing — accrues with tenure among co-resident band, lost on leaving (Wiessner hxaro)
        agent._use_standing = self._demog is not None and getattr(self._demog, "enable_standing", False)
        agent._standing = (self._demog.standing_floor if agent._use_standing else 0.0)
        agent._standing_band = None               # band the standing was built in (change ⇒ outsider penalty)
        agent._condition = 1.0                    # S0 body-condition / immune competence (EMA of nutrition)
        agent._last_intake = 0.0                  # this step's gathered kcal (set during harvest)
        # Intake-based energetic fertility: slow EMA of intake/requirement. Starts NEUTRAL (at `intake_fert_hi`
        # ⇒ factor 1.0) so founders carry no startup penalty, and it only accumulates from menarche — before
        # that a child's GATHERED intake understates what it EATS, because juveniles are provisioned.
        agent._intake_ema = (self._demog.intake_fert_hi if self._demog is not None else 1.0)
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
        self.deaths_orphan_this_step = 0              # R-74 diag: deaths carrying an elevated kin/orphan hazard
        self.leveling_events_this_step = 0            # R-82 diag: Boehm sanctions applied to material-monopolizers
        self.leader_levy_this_step = 0.0              # R-83 diag: durable output levied by band leaders
        self.lineage_tribute_this_step = 0.0         # R-103f diag: durable output levied by CHIEFLY lineages
        self._hides_this_step = {}                    # R-83: per-agent durable output this step (for the levy)
        self.depositions_this_step = 0                # R-84 diag: leaders removed by DEPOSITION (Boehm, 9/48)
        self.desertions_this_step = 0                 # R-84 diag: followers who WALKED AWAY (Boehm, 17/48 — the commoner channel)
        self.challenges_this_step = 0                 # R-84 diag: deposition ATTEMPTS (a challenge can fail ⇒ incumbent survives)
        self.feast_spend_this_step = 0.0              # R-86 diag: material spent on sacrifices/feasts
        self.legitimated_this_step = 0                # R-86 diag: agent-steps receiving the legitimated-lineage cred boost
        self.reversions_this_step = 0                 # R-87 diag: bands reverting gumsa → gumlao this step
        self.lineage_branches_this_step = 0           # R-90 diag: births founding a NEW named descent line
        self.lineage_splits_this_step = 0             # R-92 diag: lineages SEGMENTING into two named sub-clades
        self.settle_formed_this_step = 0              # diag (2026-08-11): NEW settlement sites founded this step
        self.settle_released_this_step = 0            # diag: settlement sites DISSOLVED (hysteresis timer expired)
        self.bud_events_this_step = 0                 # diag: village-budding fissions this step (bud_events is cumulative)
        self._orphan_e_cache = None                   # R-74: per-step cache of the endogenous E[mult] divisor
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

        # R-103d MATERIAL INHERITANCE (default OFF ⇒ this whole block is skipped, bit-exact). Built ONCE before the
        # prune: a parent→living-children index, so a dying agent's durable estate can be bequeathed rather than
        # dissolving. This is the 'bequeathing' step big-men lack (Flannery ch.10). Heirs are children still ALIVE
        # (a child dying the same step does not inherit — the estate goes to survivors).
        _inh_rule = getattr(self._demog, "material_inheritance_rule", "none") if self._demog is not None else "none"
        _heirs_of = None
        if getattr(self._demog, "enable_material_inheritance", False) and _inh_rule != "none":
            _heirs_of = {}
            for c in self.agent_list:
                if c.alive:
                    if c._father is not None:
                        _heirs_of.setdefault(c._father, []).append(c)
                    if c._mother is not None:
                        _heirs_of.setdefault(c._mother, []).append(c)

        # Prune dead agents. `agent.remove()` deregisters the corpse from Mesa's `self.agents`
        # AgentSet too — without it, dead agents linger frozen at their death cell and any metric
        # read off `self.agents` (e.g. the band tests) silently counts CORPSES as live population.
        # The dynamics already run off `agent_list` (live), so this is a measurement-correctness fix.
        for a in self.agent_list:
            if not a.alive:
                if _heirs_of is not None and getattr(a, "material", 0.0) > 0.0:
                    self._bequeath(a, _heirs_of.get(a, ()), _inh_rule,
                                   by_status=getattr(self._demog, "material_heir_by_status", False))
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

        # Demographic layer: divorce (R-78) → polygyny attrition (R-76) → pairing (F.3a) → births (opt-in)
        if self._demog is not None:
            self._do_divorce()
            self._do_polygyny_attrition()
            if getattr(self._demog, "enable_pair_bonds", False):
                self._connubium_sizes = []        # CONNUBIUM diag: reset; the pairing method refills for this phase
                if getattr(self._demog, "enable_adaptive_connubium", False):
                    self._do_connubium()          # Cut 2: per-seeker expanding search to eligibility (emergent scale)
                elif getattr(self._demog, "enable_marriage_aggregation", False):
                    self._do_gathering()          # seasonal cross-band gathering replaces daily within-band pairing
                else:
                    self._do_pairing()
            if getattr(self._demog, "enable_band_affiliation", False):
                # Village identity runs BEFORE band maintenance so a merged village is already in place when
                # fusion/fission run, and the fission branch can see it in `_village_bands` and skip it.
                if getattr(self._demog, "enable_village_identity", False):
                    self._maintain_village_identity()
                self._maintain_bands()
                if getattr(self._demog, "enable_village_budding", False):
                    self._maintain_village_budding()   # Bandy 2004: large village sheds a rival-led daughter (relocates)
            self._maintain_leader_office()        # R-84: tenure the office; Boehm deposition (9) / desertion (17)
            self._do_obligations()                # C: wealth -> obligation -> a claim on production (Sahlins)
            self._do_births_ibi()
            self._do_lineage_split()   # R-92: named lines SEGMENT into sub-clades (after births, so newborns
                                       # are already placed in their father's line and can be carried by a split)
        elif self._reproduction:
            self._do_births()
        self.occupied = {a.pos for a in self.agent_list}
        self._update_standing()          # P6: tenure builds standing; leaving/isolation forfeits it (ready for next harvest)

    def _bequeath(self, dead, heirs, rule, by_status=False) -> None:
        """R-103d — transfer a dead agent's durable `material` estate to heirs by the inheritance `rule`.
        No eligible heir ⇒ the estate DISSOLVES (unchanged from the default OFF path), so a lineage that fails to
        reproduce loses its capital — the mechanism cannot manufacture wealth, only redistribute it across a real
        parent→child link. Deterministic tie-break by unique_id so runs stay reproducible.

        R-103e `by_status`: primogeniture sends the estate to the highest-CRED (status) heir rather than the eldest,
        so wealth and rank pass TOGETHER (Flannery ch.16 chiefly primogeniture) instead of the estate leaking to a
        random child who does not carry the lineage's standing."""
        heirs = [h for h in heirs if h.alive]
        if rule == "patrilineal_sons":
            heirs = [h for h in heirs if h.sex == "male"]
        if not heirs:
            return
        est = dead.material
        if rule == "primogeniture":                          # whole estate to ONE heir
            key = (lambda h: (getattr(h, "cred", 1.0), h.age, h.unique_id)) if by_status else (lambda h: (h.age, h.unique_id))
            max(heirs, key=key).material += est
        else:                                                # partible_equal / patrilineal_sons: split equally
            per = est / len(heirs)
            for h in heirs:
                h.material += per
        dead.material = 0.0

    def _update_defensibility_claims(self) -> None:
        """Economic-defensibility (Dyson-Hudson & Smith 1978) claim maintenance. A cell is CLAIMABLE when its
        resource is dense+predictable (aquatic_food/S_pot ≥ defensibility_min — aquatic is high-π by construction,
        the diffuse interior ≈ 0 so it never qualifies). A band that LEAD-occupies a claimable cell with ≥
        defensibility_claim_min members builds a claim (+1/step); at ≥ defensibility_claim_dwell it OWNS the cell.
        The incumbent owner keeps priority while present; a challenger erodes the claim (−1); ownership LAPSES
        (hysteresis) when the claim decays to 0. Aquatic is claimable by construction; with `enable_improved_land`
        CULTIVABLE land is ALSO claimable where WORKED (inside an active settlement's catchment) — the agrarian path."""
        D = getattr(self._fields, "aquatic_food", None)
        if D is None:
            return
        dmin = self._demog.defensibility_min
        dwell = self._demog.defensibility_claim_dwell
        claim_min = self._demog.defensibility_claim_min
        # IMPROVED-LAND (agriculture): cultivable cells become claimable where actively WORKED — a settlement's catchment.
        # "You own what you've cleared" (Testart), not any fertile wilderness cell. worked=None ⇒ aquatic-only (bit-exact).
        cult = getattr(self._fields, "cultivability", None) if getattr(self._demog, "enable_improved_land", False) else None
        worked = None
        if cult is not None and self._settlement_sites:
            rad = self._demog.settle_radius
            worked = set()
            for (sx, sy) in self._settlement_sites:
                for dx in range(-rad, rad + 1):
                    for dy in range(-rad, rad + 1):
                        worked.add(((sx + dx) % N, (sy + dy) % N))
        cell_bands: dict[tuple[int, int], dict[int, int]] = {}
        for a in self.agent_list:
            x, y = a.pos
            if D[y, x] >= dmin or (worked is not None and (x, y) in worked and cult[y, x] >= dmin):
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

    def _village_home_cell(self, agent, site: tuple[int, int]) -> tuple[int, int]:
        """CATCHMENT SPREAD (`enable_village_catchment_spread`): a deterministic HOME cell for a settled member,
        inside the village's membership territory (settle_radius), drawn ∝ each land cell's yield so richer cells
        hold more dwellings. STABLE per agent (a fixed hash of unique_id ⇒ the same home every step, so the member
        converges to it and stays — no thrashing). Every home is within settle_radius, so `_nearest_settlement`
        still returns this site next step and membership is preserved. Purely a POSITION: the harvest regroups the
        member back to the site, so food is untouched — only the physical footprint / density spreads."""
        if self._village_home_cache is None:
            self._village_home_cache = {}
        entry = self._village_home_cache.get(site)
        if entry is None:
            rad = self._demog.settle_radius
            tf = self._harvest_field
            water = self._fields.isWater
            sx, sy = site
            cells = []
            cum = []
            acc = 0.0
            for dy in range(-rad, rad + 1):
                for dx in range(-rad, rad + 1):
                    cx = (sx + dx) % N
                    cy = (sy + dy) % N
                    if water[cy, cx] != 0:
                        continue
                    w = tf.level(cx, cy)
                    acc += w if w > 0.0 else 0.0
                    cells.append((cx, cy))
                    cum.append(acc)
            if not cells or acc <= 0.0:                       # degenerate: no land yield in reach → keep the site
                entry = ([site], [1.0], 1.0)
            else:
                entry = (cells, cum, acc)
            self._village_home_cache[site] = entry
        cells, cum, tot = entry
        if len(cells) == 1:
            return cells[0]
        # deterministic ∝-weight pick: a fixed hash of the agent id into [0, tot)
        h = (int(agent.unique_id) * 2654435761 + 1013904223) & 0xFFFFFFFF
        x = (h / 4294967296.0) * tot
        for i, c in enumerate(cum):                           # first bucket whose cumulative weight exceeds x
            if x < c:
                return cells[i]
        return cells[-1]

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

    def _founding_pot_field(self):
        """The potential a SITE is judged on, as distinct from what it YIELDS. See
        `DemographyConfig.enable_storable_founding`.

        OFF  -> `_s_pot_field()`, i.e. max(aquatic, cultivability) on raw terrain. Bit-exact.
        ON   -> that, times `_storable_frac_field()` — the per-cell storable fraction already computed from
                the local {grain, fish, forage, game} mix with Testart's STORABILITY_BY_RESOURCE. A dense
                wild-cereal stand and a salmon choke point both score; a fresh-forage cell does not.

        This is the criterion Hayden 1995 names and the one that survives BOTH the Levantine sedentism-first
        case and the Mesoamerican mobile-farming counter-case. It introduces no new number: every constant it
        uses is already filed and already in use elsewhere in the model.
        """
        sp = self._s_pot_field()
        if sp is None or self._demog is None:
            return sp
        if not getattr(self._demog, "enable_storable_founding", False):
            return sp
        if self._founding_pot_cache is None:
            sf = self._storable_frac_field()
            self._founding_pot_cache = sp if sf is None else sp * sf
        return self._founding_pot_cache

    def _forage_cap_field(self):
        """Per-person forage cap = forage_kcal · forage_cap_hours (the biome return-rate × work hours — the most one
        forager can harvest). Cached. None if no forage_kcal field."""
        if self._forage_cap_cache is None:
            fk = getattr(self._fields, "forage_kcal", None)
            if fk is None:
                return None
            self._forage_cap_cache = fk * self._demog.forage_cap_hours
        return self._forage_cap_cache

    def _biome_meat_frac_field(self):
        """PER-CELL diet meat fraction `mf` from `terrain.MEAT_FRAC` (Cordain 2000 Table 2). Cached (static).
        None if the flag is off or there is no biome field, in which case the caller keeps the scalar.

        A biome ABSENT from MEAT_FRAC (wetland) takes the configured scalar `game_meat_frac`, NOT zero — the dict
        omits wetland deliberately, and a 0.0 would assert that wetland foragers eat no meat. Water cells never
        hold occupants, so their value is never read; they take the scalar too rather than a special case."""
        if self._meat_frac_cache is None:
            biome = getattr(self._fields, "biome", None)
            if biome is None:
                return None
            import numpy as np
            from sic_games.terrain import MEAT_FRAC
            out = np.full(biome.shape, float(self._demog.game_meat_frac), dtype=float)
            for b, m in MEAT_FRAC.items():
                out[biome == b] = float(m)
            self._meat_frac_cache = out
        return self._meat_frac_cache

    def _biome_meat_cv_field(self):
        """PER-CELL day-to-day meat CV from `terrain.MEAT_CV` (cchunts; Hawkes 1991 for the Hadza). Cached.

        A biome ABSENT from MEAT_CV (grass, mountain, wetland — no calibration people) takes `terrain.HUNT_CV`
        = 2.11, which is terrain.py's own documented rule for that case and is a MEASURED biome-invariant value,
        not a filler. It is not the scalar `game_meat_cv`, because that scalar's historical value (0.73) is the
        anchor R-72/R-73 retired — a SPATIAL cross-cell spread used as a TEMPORAL per-step draw."""
        if self._meat_cv_cache is None:
            biome = getattr(self._fields, "biome", None)
            if biome is None:
                return None
            import numpy as np
            from sic_games.terrain import HUNT_CV, MEAT_CV
            out = np.full(biome.shape, float(HUNT_CV), dtype=float)
            for b, c in MEAT_CV.items():
                out[biome == b] = float(c)
            self._meat_cv_cache = out
        return self._meat_cv_cache

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

    def _order_females_for_pairing(self, females) -> None:
        """R-77 wife-quality ordering, in place. Off ⇒ a plain shuffle (bit-exact; the RNG-order contract
        "shuffle → polygyny-gate → choose" is preserved because this consumes exactly one draw per female,
        as `shuffle` effectively does).

        von Rueden & Jaeggi (33 societies): in MONOGAMOUS societies status→RS runs through **wife quality
        (r=0.15)**, defined as "wife's age or interbirth interval". So the most fertile women pair FIRST and,
        choosing prowess-weighted, take the highest-status men — the status↔wife-youth assortment EMERGES
        from mutual choice instead of being imposed.

        Ordering is Efraimidis–Spirakis weighted sampling without replacement (key = u^(1/w), sort desc),
        which is a Plackett–Luce draw: a strict youth sort would be deterministic and unrealistic.
        """
        cfg = self._demog
        wq = getattr(cfg, "wife_quality_strength", 0.0) if cfg is not None else 0.0
        if wq <= 0.0:
            self.random.shuffle(females)
            return
        span = max(1.0, float(cfg.menopause_months - cfg.menarche_months))

        def _key(f):
            rem = max(0.0, float(cfg.menopause_months - f.age)) / span   # remaining fertile fraction ∈ [0,1]
            w = max(1e-9, rem) ** wq
            u = self.random.random()
            return u ** (1.0 / w)                                        # higher w ⇒ higher key ⇒ pairs sooner

        females.sort(key=_key, reverse=True)

    def _do_divorce(self) -> None:
        """Baseline bond dissolution (serial monogamy): each step, a paired female dissolves her bond with
        probability `divorce_rate` and re-enters the pairing pool.

        R-78 — fires EVERY step, on ALL pairing paths. It PREVIOUSLY lived inside the three pairing methods,
        and in `_do_gathering`/`_do_connubium` it sat AFTER the annual seasonal gate (`step % aggregation_period
        != 0: return`), so under `enable_marriage_aggregation` — the canonical village stack — it fired only on
        gathering steps: ~`aggregation_period`× (=12×) rarer than the "per-step" the config documents, and
        rarer still on seasonal worlds where the abundance-window gate trims it further (R-75, task_9804e99a).
        Measured consequence: `frac_parents_divorced` 0.014 vs the Aché 0.14. Now it is one home with one meaning.
        Polygynous bonds face THIS plus `polygyny_attrition` (Marlowe: polygynous marriages "less enduring").
        0 = lifelong unless widowed ⇒ bit-exact (no draw fires). Iterates a snapshot: mutates `_wives`/`_partner`.
        """
        cfg = self._demog
        rate = getattr(cfg, "divorce_rate", 0.0)
        if rate <= 0.0:
            return
        for a in list(self.agent_list):
            if a.sex == "female" and a._partner is not None and self.random.random() < rate:
                a._partner._wives.discard(a)
                a._partner = None

    def _do_polygyny_attrition(self) -> None:
        """R-76 — the polygyny stock's missing OUTFLOW. Marlowe (*The Hadza*): "When a man does have 2 wives,
        the women usually live in different camps, and **polygynous marriages are less enduring**."

        Without this, polygyny only fills: `polygyny_rate` gates whether a married male is CONSIDERED, he then
        wins prowess-weighted, and the bond never ends — so the rate cannot set the level (a 150× rate change
        moved realized polygyny only 9.2%→25.3%, and Marlowe's ~4% of men was unreachable). With an outflow,
        inflow-vs-attrition equilibrates and the rate becomes a real control.

        Fires EVERY step, like `_do_divorce` (R-78). Only wives of a husband holding >1 wife are exposed:
        dissolving a monogamous bond is `divorce_rate`'s job, not this.
        Off (0.0) ⇒ bit-exact. Iterates a snapshot: the pass mutates `_wives`/`_partner`.
        """
        cfg = self._demog
        rate = getattr(cfg, "polygyny_attrition", 0.0)
        if rate <= 0.0:
            return
        for a in list(self.agent_list):
            if a.sex != "female":
                continue
            h = a._partner
            if h is None or len(h._wives) <= 1:          # monogamous or unpaired → not this mechanism
                continue
            if a.random.random() < rate:
                h._wives.discard(a)
                a._partner = None                        # she re-enters the pairing pool (serial monogamy)

    def _orphan_status(self, a):
        """(mother_dead, father_dead, divorced) for agent `a`. Parent links are set at IBI birth; a dead
        parent's object survives the prune with `alive=False`, so the reference stays readable.
        `divorced` follows Table 13.1's footnote — it is defined ONLY when both parents are living, and
        means the mother is no longer bonded to this child's father (she re-paired, or the bond dissolved:
        the Aché `pianjambyre`, "neglected by its provider after a parent initiates sexual relations with
        a new partner"). Unknown parentage (founders) ⇒ no effect, never an assumed orphan."""
        m = getattr(a, "_mother", None)
        f = getattr(a, "_father", None)
        m_dead = m is not None and not m.alive
        f_dead = f is not None and not f.alive
        divorced = False
        if m is not None and f is not None and not m_dead and not f_dead:
            divorced = getattr(m, "_partner", None) is not f
        return m_dead, f_dead, divorced

    def _orphan_lethal(self, a) -> bool:
        """Hill & Hurtado: "mother's death in the first year of a child's life leads to mortality in 100%
        of the cases in our sample" — an unweaned infant cannot survive losing its mother."""
        cfg = self._demog
        if cfg is None or not getattr(cfg, "enable_orphan_mortality", False):
            return False
        if not getattr(cfg, "orphan_infant_mother_lethal", False) or a.age >= MONTHS_PER_YEAR:
            return False
        m = getattr(a, "_mother", None)
        return m is not None and not m.alive

    def _orphan_mult(self, a) -> float:
        """R-74 kin/orphan multiplier on the TOTAL age-specific hazard (Hill & Hurtado Table 13.1).
        Normalised by E[mult] at the Aché mean values so the population-mean hazard is preserved and the
        mechanism REDISTRIBUTES mortality onto orphans rather than adding a second helping of it on top of
        the a1 that already contains these deaths ("infanticide KEPT"). Off ⇒ 1.0 (bit-exact)."""
        cfg = self._demog
        if cfg is None or not getattr(cfg, "enable_orphan_mortality", False):
            return 1.0
        if a.age > cfg.orphan_max_age_years * MONTHS_PER_YEAR:
            return 1.0                                    # Table 13.1's window is ages 0–9
        m_dead, f_dead, divorced = self._orphan_status(a)
        mult = 1.0
        if m_dead:
            mult *= cfg.orphan_mult_mother_dead
        if f_dead:
            mult *= cfg.orphan_mult_father_dead
        if divorced:
            mult *= cfg.orphan_mult_divorced
        if cfg.orphan_normalize:
            mult /= self._orphan_e_mult_live()
        return mult

    def _orphan_e_mult_live(self) -> float:
        """E[mult] over THIS population's own children — the double-count divisor, computed ENDOGENOUSLY
        once per step and cached.

        Why not the fixed Aché constant (Table 13.1's 0.98/0.95/0.14 ⇒ 1.499)? Because this model is
        **fertility-pinned** (R-16): held at r=0 its equilibrium e₀ is ~28, not the Aché's 36.5 — the Aché
        had TFR≈8 AND e₀≈36.5, i.e. NRR>1, a GROWING population. A stationary population must therefore
        orphan MORE children (measured: ~10% motherless vs the Aché's ~2% exposure, and the analytic
        confirms it — a2_mult≈3 ⇒ 10.7%). Dividing by a constant fitted to a growing population's orphan
        rate would hand every intact child an unearned discount (or, here, a net penalty) and move eq_pop
        by tens of percent — measured −47% before this fix.
        Normalising by the population's OWN mean makes the channel exactly **compositional**: WHO dies is
        orphan-graded, HOW MANY stays fertility-pinned. That is the same split R-16/R-18 established for
        the Cred hierarchy, and it is the honest one here — the Siler a1 already contains these deaths
        ("infanticide KEPT"), so the mechanism must redistribute them, not add more."""
        if self._orphan_e_cache is not None and self._orphan_e_step == self.step_count:
            return self._orphan_e_cache
        cfg = self._demog
        tot = n = 0.0
        maxm = cfg.orphan_max_age_years * MONTHS_PER_YEAR
        for a in self.agent_list:
            if a.age > maxm:
                continue
            if getattr(a, "_mother", None) is None and getattr(a, "_father", None) is None:
                continue                                   # founders / unknown parentage: not in the risk set
            m_dead, f_dead, divorced = self._orphan_status(a)
            m = 1.0
            if m_dead:
                m *= cfg.orphan_mult_mother_dead
            if f_dead:
                m *= cfg.orphan_mult_father_dead
            if divorced:
                m *= cfg.orphan_mult_divorced
            tot += m; n += 1.0
        e = (tot / n) if n > 0 else 1.0
        self._orphan_e_cache = e
        self._orphan_e_step = self.step_count
        return e

    def _return_cv_field(self):
        """Emergent-band-size v3: per-cell **DAY-TO-DAY** return CV — the variance a band pools away by sharing.

        Sourced from `terrain.RETURN_CV` (derived from Cordain 2000 MEAT_FRAC via the two measured stream CVs;
        see terrain.py). Deliberately NOT from FORAGE/GAME_KCAL_STD: those are **spatial** (cross-cell) spreads
        feeding the lognormal cell-value draw — reusing them here was a category error (v1/v2), since a spread
        across 7 species' means says nothing about one forager's day-to-day luck. Cached."""
        if self._cv_cache is None:
            from sic_games.terrain import RETURN_CV, GATHER_CV
            biome = getattr(self._fields, "biome", None)
            if biome is None:
                return None
            import numpy as np
            # Biomes absent from RETURN_CV have no diet anchor ⇒ fall back to pure gathering (the low-variance
            # floor), never to a made-up middle: an unanchored biome should not manufacture a pooling incentive.
            cv = np.full(biome.shape, float(GATHER_CV), dtype=float)
            for code in np.unique(biome):
                c = RETURN_CV.get(int(code))
                if c is not None:
                    cv[biome == code] = float(c)
            self._cv_cache = cv
        return self._cv_cache

    def _band_optimum_field(self):
        """Emergent-band-size v3: per-cell risk-pooling optimum g* = CV/cv_safe (LINEAR, unclamped — see
        DemographyConfig). Used as the group_safety AGGREGATION scale in movement (agents cluster up to g*)
        and, per band, as the scalar-stress midpoint + fission-threshold base. Cached. None if no CV field."""
        if self._band_opt_cache is None:
            cv = self._return_cv_field()
            if cv is None:
                return None
            self._band_opt_cache = cv / self._demog.cv_safe
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
        # WORKED-LAND YIELD (see `enable_worked_land_yield`). OFF: sum the whole catchment, so the full
        # tier-2 unlock arrives the instant the site exists — no clearing, no ramp. ON: sum only the cells
        # somebody actually OWNS, so the yield RAMPS as claims mature (+1/step to defensibility_claim_dwell)
        # and spreads outward as the village grows. The lag is emergent from the clearing process; no delay
        # parameter is introduced. Tier-1 is untouched, so settling on a wild stand still pays at once.
        worked_only = (self._demog is not None
                       and getattr(self._demog, "enable_worked_land_yield", False))
        for dy in range(-rad, rad + 1):
            for dx in range(-rad, rad + 1):
                cell = ((sx + dx) % N, (sy + dy) % N)
                if worked_only and cell not in self._cell_owner:
                    continue
                tot += sp[cell[1], cell[0]]
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

    def _catchment_foraging_pressure(self, occ_count: dict) -> dict:
        """CATCHMENT-FORAGING DEPLETION (`enable_catchment_depletion`): the depletion pressure map that follows
        where food is TAKEN, not where agents stand. A settled villager (a member within settle_radius of a
        site) forages the site's catchment, so its one forager-unit is spread over the catchment cells ∝ each
        cell's yield (richer cells hunted harder); a mobile agent forages the cell it stands on. So a big
        village hunts down its catchment, the depletable stock there falls, and the carrying-capacity ceiling
        (Σ depletable cell yield) drops with it — the central-place depletion the standing-occupancy map lacks."""
        if not self._settlement_sites:
            return occ_count
        tf = self._harvest_field
        rad = self._demog.settle_catchment_radius
        weights: dict = {}                                   # site -> [(cell, normalized yield weight), ...]
        for s in self._settlement_sites:
            cells, tot = [], 0.0
            for dy in range(-rad, rad + 1):
                for dx in range(-rad, rad + 1):
                    c = ((s[0] + dx) % N, (s[1] + dy) % N)
                    y = float(tf.level(c[0], c[1])); cells.append((c, y)); tot += y
            weights[s] = ([(c, y / tot) for c, y in cells] if tot > 0.0
                          else [(c, 1.0 / len(cells)) for c, _ in cells])
        fmap: dict = {}
        for a in self.agent_list:
            s = self._nearest_settlement(a.pos)
            if s is not None:                                # a settled villager forages the catchment
                for (c, w) in weights[s]:
                    fmap[c] = fmap.get(c, 0.0) + w
            else:                                            # a mobile band forages where it stands
                fmap[a.pos] = fmap.get(a.pos, 0.0) + 1.0
        return fmap

    def _maintain_settlements(self) -> None:
        """Aggregation-sedentism lifecycle: an active settlement PERSISTS while ≥ settle_min_pool people are within
        settle_radius of its site (membership is emergent proximity — robust to band fission/fusion); otherwise its
        hysteresis timer decays and it DISSOLVES (the pool disperses back to mobile bands). Formation is seasonal (in
        `_do_gathering`); this runs every step to hold or release.

        EXCLUSIVE MEMBERSHIP (`enable_exclusive_village_membership`, 2026-08-12). The block sum below counts every
        person inside a site's (2·settle_radius+1) window, and windows OVERLAP whenever sites are closer than
        that — so two neighbouring villages each count the SAME people toward their own survival threshold.
        Measured: ~110 settlements at a median nearest-neighbour spacing of 1.0 cell, mean on-site occupancy
        15.8 against a 40-person requirement, i.e. a dense cluster of individually-unviable sites propping each
        other up. That mutual subsidy is the engine of the budding runaway.

        ON ⇒ each agent is counted for exactly ONE village, the nearest (`_nearest_settlement`, the model's own
        membership test, with its existing deterministic tie-break). Villages then COMPETE for members instead
        of sharing them, and settlement spacing becomes EMERGENT: a village sited too near another cannot
        assemble its own pool, so it dissolves. No distance constant is imposed anywhere — the earlier
        geometric rule (`enable_bud_site_separation`) hard-coded 2·settle_radius+1 = 50 km against a filed
        anchor of ~20 km for disjoint hunter-gatherer catchments (Vita-Finzi & Higgs 1970: ~10 km site
        exploitation radius, the two-hour walk), and is retained default-OFF only as an ablation control.
        Default OFF ⇒ block sum ⇒ bit-exact."""
        if not self._settlement_sites:
            return
        rad = self._demog.settle_radius
        min_pool = self._demog.settle_min_pool
        exclusive = getattr(self._demog, "enable_exclusive_village_membership", False)
        if exclusive:
            claimed: dict = {}
            for a in self.agent_list:
                s = self._nearest_settlement(a.pos)
                if s is not None:
                    claimed[s] = claimed.get(s, 0) + 1
        occ: dict = {}                                    # PERF: cell → occupancy; sum each site's neighbourhood
        for a in self.agent_list:                         # instead of O(agents·n_sites) torus-distance checks
            occ[a.pos] = occ.get(a.pos, 0) + 1
        for site in list(self._settlement_sites):
            sx, sy = site
            if exclusive:
                n = claimed.get(site, 0)          # each person counted for ONE village only → no mutual subsidy
            else:
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
                    self.settle_released_this_step += 1
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
        occ: dict = {}                                         # PERF: cell → occupancy, then sum each site's
        for a in self.agent_list:                              # neighbourhood — O(agents + n_sites·rad²), not
            occ[a.pos] = occ.get(a.pos, 0) + 1                 # O(agents·n_sites). Bit-exact (same counts).
        counts: dict[tuple[int, int], int] = {}
        for (sx, sy) in self._settlement_sites:
            n = 0
            for dx in range(-rad, rad + 1):
                for dy in range(-rad, rad + 1):
                    n += occ.get(((sx + dx) % N, (sy + dy) % N), 0)
            counts[(sx, sy)] = n
        dep = cfg.soil_deplete_frac / 12.0                     # per-step exhaustion at pressure 1
        # ALLUVIAL RENEWAL — renewal is TERRAIN-dependent, not uniform: a FLOODPLAIN farm is re-fertilised in place by
        # the annual flood silt (the Nile was cropped ~5,000 yr without fallow) while RAIN-FED dryland exhausts.
        # `wateracc` is the alluvial signal (the same one cultivability_field uses). OFF ⇒ allu_r=0 ⇒ every farm
        # depletes (bit-exact). ⇒ two regimes: rain-fed SWIDDEN (cycles) vs HYDRAULIC floodplain (stable).
        allu_on = getattr(cfg, "enable_alluvial_renewal", False)
        allu_r = (cfg.alluvial_renew_per_yr / 12.0) if allu_on else 0.0
        wacc = getattr(self._fields, "wateracc", None) if allu_on else None
        active_farm = set()
        for s in self._settlement_sites:
            if aq is not None and aq[s[1], s[0]] >= cult[s[1], s[0]]:
                continue                                       # aquatic-dominant → a FISHERY, exempt (R-53)
            active_farm.add(s)
            pressure = counts.get(s, 0) / carry if carry > 0 else 0.0
            # SWIDDEN: continuous cropping EXHAUSTS the soil (no regrowth while farmed) → progressive decline to the
            # floor → yield crashes → bust/relocate. (Landesque capital, B2, is what damps this to a sustainable
            # equilibrium — the intensification path.) Regrowth happens only on FALLOW (below) — UNLESS the site is
            # ALLUVIAL, where the flood renews it IN PLACE (the hydraulic regime: dense, stable, fallow-free).
            soil = self._settlement_soil.get(s, 1.0) - dep * pressure
            if wacc is not None:
                soil += allu_r * float(wacc[s[1], s[0]]) * (1.0 - soil)   # flood silt restores toward 1 ∝ alluviality
            self._settlement_soil[s] = min(1.0, max(0.05, soil))
        for s in list(self._settlement_soil):                  # FALLOW: abandoned (or non-farm) sites heal slowly
            if s not in active_farm:
                soil = self._settlement_soil[s] + r * (1.0 - self._settlement_soil[s])
                if soil >= 0.999:
                    self._settlement_soil.pop(s, None)
                else:
                    self._settlement_soil[s] = soil
        # EMERGENT ABANDONMENT — the village's REMEMBERED FORTUNES: a slow per-SITE EMA of hardship (1 − realized field
        # productivity), attached to the PLACE (members churn; the place persists). Slow ⇒ one bad year cannot move it;
        # only CHRONIC decline does — which is what the elders would actually notice. Read by the residence pin.
        # Fisheries/alluvial keep soil ≈1 ⇒ hardship ≈0 ⇒ they never abandon (the permanent hydraulic village).
        if getattr(cfg, "enable_emergent_abandonment", False):
            am = 1.0 / max(1.0, cfg.settlement_memory_yr * 12.0)     # memory window (yr → steps) ⇒ EMA weight
            for s in self._settlement_sites:
                h = 1.0 - self._settlement_soil.get(s, 1.0)
                self._settlement_hardship[s] = (1.0 - am) * self._settlement_hardship.get(s, 0.0) + am * h
            for s in list(self._settlement_hardship):                # forget sites that have dissolved
                if s not in self._settlement_sites:
                    self._settlement_hardship.pop(s, None)

    def _step_rivalrous(self) -> None:
        """Stage-6.0a multi-occupancy substrate on the terrain field (forage-only).
        Diffusion movement (per-capita yield) → per-cell harvest split → metabolism."""
        self._nearest_map = None                      # PERF: rebuild the cell→nearest-settlement map fresh this step
        self._village_home_cache = None               # catchment spread: rebuild the home-cell lottery fresh (yields drift with depletion)
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
            # RANK BY THE RESOURCE THAT MAKES THE CELL WORTH HOLDING (2026-07-27). This scored every owned cell
            # by `aquatic_food` alone, so a WORKED CULTIVABLE cell — the entire point of `enable_improved_land`
            # — was valued at its AQUATIC value (≈0 in the interior) when choosing the band's central place.
            # Measured: improved_land added 40 claimable worked cells inside settlement catchments, and none of
            # them could ever win the tether. The agrarian path could be owned but never became a centre, which
            # is why the mechanism read inert. S_pot = max(aquatic, cultivability) is the model's OWN notion of
            # site potential (`_s_pot_field`, already used by the settlement catchment yield), so this uses the
            # same quantity rather than inventing one. improved_land OFF ⇒ aquatic-only ⇒ bit-exact.
            aqf = self._fields.aquatic_food
            _rank_f = aqf
            if getattr(self._demog, "enable_improved_land", False):
                _sp = self._s_pot_field()
                if _sp is not None:
                    _rank_f = _sp
            best: dict[int, tuple[float, tuple[int, int]]] = {}
            for c, b in cell_owner.items():
                val = float(_rank_f[c[1], c[0]])
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
        # R-106 Addendum 13: scales the PERCEIVED co-location premium only; realized production (the harvest-side
        # `S += aggl_R·(n^β − n)`) is untouched, so attraction and subsistence are independently tunable. 1.0 ⇒ bit-exact.
        aggl_at = getattr(self._demog, "aggl_attraction_weight", 1.0) if aggl_on else 1.0
        # Per-person forage cap (solitude fix): a forager harvests at most forage_kcal·work_hours, not the whole cell.
        # CAPACITY-SCALED GROUPING (R-106, 2026-08-22) lives on SubstrateConfig with the other E.1/E.2
        # grouping parameters, not on DemographyConfig -- same owner as the drives it bounds.
        capgrp_on = getattr(self._substrate_cfg, "enable_capacity_scaled_grouping", False)
        cap_on = self._demog is not None and getattr(self._demog, "enable_forage_cap", False)
        fcap = self._forage_cap_field() if cap_on else None
        # R-106 (2026-08-15): the CLAIM WEIGHT on the cell split. `need` claims in proportion to what an
        # occupant needs (Kaplan 2000); `eta_w` claims in proportion to what an occupant can actually
        # harvest. Both OFF ⇒ `_claim()` returns None ⇒ the historical S/n split, bit-exact. See
        # `DemographyConfig.enable_need_weighted_shares` for why an age-blind split produces the age-blind
        # excess hazard that holds e15 at 16 against a forager anchor of ~35.
        need_w = self._demog is not None and getattr(self._demog, "enable_need_weighted_shares", False)
        eta_w = self._demog is not None and getattr(self._demog, "enable_eta_weighted_shares", False)

        def _claim(occ_c):
            """Per-occupant claim weight, or None for the historical even split."""
            if need_w and eta_w:
                return [a.consumption_factor() * a.eta() for a in occ_c]
            if need_w:
                return [a.consumption_factor() for a in occ_c]
            if eta_w:
                return [a.eta() for a in occ_c]
            return None
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
        abandon_on = settle_on and getattr(self._demog, "enable_emergent_abandonment", False)
        abandon_gain = self._demog.abandon_hardship_gain if abandon_on else 0.0
        # ACUTE FAMINE DISPERSAL: a starving settler breaks the residence pin THIS step (Colson 1979).
        hunger_flee_on = settle_on and getattr(self._demog, "enable_hunger_dispersal", False)
        hunger_flee_frac = self._demog.hunger_flee_reserve_frac if hunger_flee_on else 0.0
        # CATCHMENT SPREAD: settled members pin to a HOME cell across the catchment (physical footprint spreads),
        # while the harvest regroups them at the site (food bit-exact). See `enable_village_catchment_spread`.
        spread_on = settle_on and getattr(self._demog, "enable_village_catchment_spread", False)
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
        # §4.8.19 productivity-scaled mobility: per-agent STRIDE from the STATIC local NPP (Kelly/Binford ∝1/NPP),
        # or (R-106 Addendum 6) from the agent's own live intake/requirement EMA when `mobility_pressure_source
        # ="intake"` — density-aware, since a crowded cell dilutes it regardless of nominal fertility.
        mobility_on = self._demog is not None and getattr(self._demog, "enable_productivity_mobility", False)
        mobility_source = getattr(self._demog, "mobility_pressure_source", "npp") if mobility_on else "npp"
        npp_gm2 = getattr(self._fields, "npp_gm2", None) if (mobility_on and mobility_source != "intake") else None
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
            if site is not None and abandon_on:
                # EMERGENT ABANDONMENT: chronic REMEMBERED hardship erodes the village's hold. Released ⇒ this agent's
                # ordinary IFD drive decides — it stays anyway if nowhere nearby is better, or drifts out if it is; the
                # pool then drains below settle_min_pool and the settlement dissolves by the EXISTING rule → fallow →
                # budding re-settles. No global knowledge is used: only the site's own remembered fortunes.
                att = 1.0 - abandon_gain * self._settlement_hardship.get(site, 0.0)
                if att < 1.0 and agent.random.random() > att:
                    site = None
            if site is not None and hunger_flee_on:
                # ACUTE FAMINE DISPERSAL (Colson 1979): a low reserve breaks the pin THIS step so the agent's
                # IFD drive can take the better per-capita cell one stride away (diagnosed: 99% of the hungry
                # have one). The chronic abandonment valve above is too slow for the one-step crash that kills.
                _flr = agent.reserve_floor * agent.reserve_scale()
                _cap = self._reserve_full * agent.reserve_scale()
                _rfrac = (agent.wealth - _flr) / (_cap - _flr) if _cap > _flr else 1.0
                if _rfrac < hunger_flee_frac:
                    site = None
            if site is not None and settle_ss_on:
                # Johnson scalar stress: an over-crowded settlement repels this agent (prob rises with village pop,
                # dissipated by the site's society). Repelled ⇒ fall through to normal diffusion (leave/don't join).
                soc = self._cell_society.get(site) or self._band_society.get(agent._group.band_id)
                ss = size_repulsion(settle_pop.get(site, 0), self._demog.settlement_ss_gain,
                                    self._demog.settlement_ss_midpoint, self._demog.settlement_ss_width, soc)
                if ss > 0.0 and agent.random.random() < ss:
                    site = None
            if site is not None:
                dest = self._village_home_cell(agent, site) if spread_on else site
                target = self._toward(agent.pos, dest)
                if target != agent.pos and self._fields.isWater[target[1], target[0]] == 0:
                    _shift(agent, agent.pos, target)
                continue
            ct = band_centroid.get(agent._group.band_id) if coh_str > 0.0 else None
            agent_coh = coh_str
            mr = 1
            if mobility_on:
                if mobility_source == "intake":
                    mr = mobility_radius(getattr(agent, "_intake_ema", 1.0), self._demog)
                else:
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
                                             aggl_mode=aggl_mode, aggl_attract=aggl_at,
                                             forage_cap=fcap, move_cost_field=mcf,
                                             site_field=sfield, band_opt_field=band_opt,
                                             home_cells=hcells, foreign_status_mult=fmult,
                                             store_field=st_field, store_gain=st_gain, store_horizon=st_hor,
                                             cap_group=capgrp_on, burn=self._burn)
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
            key = a.pos
            if spread_on:
                # CATCHMENT SPREAD: a settled member's dwelling is on a catchment cell (its `pos`), but the village
                # forages its catchment as ONE economic unit — so for the harvest it is regrouped to its site. This
                # reproduces the no-spread grouping (everyone at the site) EXACTLY ⇒ food/society/mating bit-exact;
                # only occ_count (physical density, built from `pos` above) carries the spread.
                s = self._nearest_settlement(a.pos)
                if s is not None:
                    key = s
            occ_lists.setdefault(key, []).append(a)
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
        # PER-BIOME two-stream (Addendum 37): swap the two scalars above for per-cell fields read from the
        # anchored dicts. Flags off ⇒ both fields are None ⇒ the scalars are used ⇒ bit-exact.
        mf_field = (self._biome_meat_frac_field()
                    if game_on and getattr(demog, "enable_biome_meat_frac", False) else None)
        cv_field = (self._biome_meat_cv_field()
                    if game_on and getattr(demog, "enable_biome_meat_cv", False) else None)
        sex_div = demog.sex_division if (demog is not None and game_on) else 0.0   # step 3: prowess-signal only
        # Storage (delayed-return): glut-capture params; gated on the overwintering zone (cell temp ≤ threshold).
        store_on = demog is not None and demog.enable_storage
        # R-82 Stage A: aggrandizer capture of the granary leftover into the durable `material` cell.
        # R-82b: material now derives from GAME (hides), so it no longer depends on storage/the granary.
        mat_on = demog is not None and getattr(demog, "enable_material_capture", False)
        mat_frac = demog.material_capture_frac if mat_on else 0.0
        mat_inv_min = getattr(demog, "material_invulnerability_min", 0.0) if mat_on else 0.0
        mat_hide = getattr(demog, "material_hide_frac", 0.0) if mat_on else 0.0
        lead_share = (demog.leader_share_frac
                      if (demog is not None and getattr(demog, "enable_leader_share", False)) else 0.0)
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
        # R-63 resource ceiling. NOT gated on `settle_on` — see the `_cap_here` block below, which has a
        # branch written specifically for the AGGLOMERATION bonus at NON-settlement cells (R-105). While this
        # read `settle_on and ...`, that branch was unreachable in exactly the configuration it exists for: a
        # world with agglomeration on and settlement off had NO ceiling at all, so the superlinear
        # `A_cell·(n^β − n)` term ran unbounded — R-105's own note calls it "an unbounded increasing-returns
        # loop with no Malthusian limit (R-104: pop 3259→97551, zero starvation)".
        #
        # MEASURED 2026-08-13, the first arms ever run with settlement off: pop 2916 → 24,727 and climbing at
        # step 3000 of 15000, per-capita intake RISING with density (2.37 → 6.76x requirement), 221 occupants
        # per cell, 1.72x the Binford packing anchor. Malthusian dynamics are impossible in that state because
        # there is no capacity to overshoot.
        #
        # BIT-EXACT FOR EVERY RUN IN THE PROJECT'S HISTORY: when `settle_on` is True this expression is
        # unchanged, and every arm before 2026-08-13 ran with `enable_aggregation_sedentism = True`. Only the
        # settlement-off path, which had never been exercised, behaves differently — and it was broken.
        ceiling_on = getattr(self._demog, "enable_catchment_ceiling", False)

        def _forage_excl(occ_c, total, kap, mask):
            """Split `total` (κ=kap) among NON-excluded occupants only; excluded get 0. Redistributes the
            excluded juveniles' share to the actual foragers (so the mother keeps her undiluted share)."""
            idx = [i for i, e in enumerate(mask) if not e]
            if not idx:
                return [0.0] * len(occ_c)
            sub_occ = [occ_c[i] for i in idx]
            # The claim weight must be subset the SAME way, or the excluded juveniles' weights would be
            # charged against foragers who are not in `sub_occ` and Σ shares would no longer be `total`.
            sub = compute_harvest_shares(sub_occ, total, kap, phi_eps, claim=_claim(sub_occ))
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
            # R-105: the ceiling must cover the AGGLOMERATION bonus too. It was gated on settlement sites only,
            # so the superlinear (n**aggl_a - n) term at NON-settlement cells was UNCAPPED — an unbounded
            # increasing-returns loop with no Malthusian limit (R-104: pop 3259→97551, zero starvation).
            _cap_here = (settle_on and (cx, cy) in self._settlement_sites) or (
                aggl_on and aggl_R is not None and getattr(self._demog, "enable_aggl_ceiling", False))
            if ceiling_on and _cap_here:
                S = min(S, self._settlement_carrying_capacity((cx, cy)))         # R-63: a village can't out-produce its catchment
            if self._diag_pool is not None:      # DIAGNOSTIC ONLY (no behaviour): S after every bonus + the
                self._diag_pool[(cx, cy)] = (S, len(occ))   # ceiling, vs occupancy — is dS/dn super- or sub-linear?
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
                # PER-BIOME (Addendum 37): the cell's own diet split and its own meat variance, where anchored.
                mf_c = float(mf_field[cy, cx]) if mf_field is not None else meat_frac
                cv_c = float(cv_field[cy, cx]) if cv_field is not None else meat_cv
                meat_pool = mf_c * S
                if hasattr(tf, "meat_factor"):
                    meat_pool *= tf.meat_factor(cx, cy)   # C.4b caribou herd-swing: meat-only depression on GRASS_STEPPE
                if cv_c > 0.0 and meat_pool > 0.0:
                    # G.3: band-level correlated stochastic meat — ONE mean-preserving lognormal draw per cell
                    # (shared by all occupants). Ordinary bad-streak variance; the regime where the share rule
                    # decides who crosses the floor (Carbon scoping). One model-RNG draw → deterministic.
                    sig = math.sqrt(math.log(1.0 + cv_c * cv_c))
                    meat_pool = math.exp(self.random.normalvariate(math.log(meat_pool) - 0.5 * sig * sig, sig))
                # ENERGY CONSERVATION: the forage stream is the COMPLEMENT of the same `mf_c` used for the meat
                # pool. If these two ever read different fractions the cell silently creates or destroys kcal.
                # The SAME claim weight goes on BOTH streams. Weighting one and not the other would make the
                # forage and meat splits disagree about who is present, which is the same class of error the
                # `mf_c` energy-conservation note above guards against.
                cl = _claim(occ)
                f_sh = (_forage_excl(occ, (1.0 - mf_c) * S, 0.0, excl_mask) if excl_mask
                        else compute_harvest_shares(occ, (1.0 - mf_c) * S, 0.0, phi_eps, claim=cl))
                m_sh = compute_harvest_shares(occ, meat_pool, kappa_cell, phi_eps, claim=cl)
                shares = [f + m for f, m in zip(f_sh, m_sh)]
            else:
                shares = (_forage_excl(occ, S, kappa_cell, excl_mask) if excl_mask
                          else compute_harvest_shares(occ, S, kappa_cell, phi_eps, claim=_claim(occ)))
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
            # R-82b: MATERIAL comes from GAME (hides/bone/sinew), not the granary. Durable goods in a forager
            # economy are the byproduct of HUNTING, produced ∝ meat taken; stored food is eaten or rots.
            # PRODUCTION is everyone's (∝ own meat share ⇒ couples material to prowess, the achieved facet);
            # CAPTURE is the aggrandizer's — Hayden's move is to claim a share of the GROUP's hides beyond his
            # own take (debt/feast obligation). Gated: capture needs an abundant, un-drawn-down stock.
            if mat_on and game_on and mat_hide > 0.0:
                hides = [mat_hide * m for m in msh]
                pool = sum(hides)
                if pool > 0.0:
                    B = 1.0
                    Barr = getattr(tf, "_B", None)      # ClimateField.__getattr__ delegates to the base field
                    if Barr is not None:
                        try:
                            B = float(Barr[cy, cx])
                        except Exception:
                            B = 1.0
                    aw = [getattr(a, "aggrandizer", 0.0) for a in occ]
                    asum = sum(aw)
                    if mat_frac > 0.0 and asum > 0.0 and B >= mat_inv_min:
                        take = mat_frac * pool          # the aggrandizers' claim on the group's durable output
                        for a, wi in zip(occ, aw):
                            if wi > 0.0:
                                self._credit_material(a, take * (wi / asum))
                        for a, h in zip(occ, hides):    # the remainder stays with whoever produced it
                            self._credit_material(a, (1.0 - mat_frac) * h)
                    else:
                        for a, h in zip(occ, hides):
                            self._credit_material(a, h)
                    if lead_share > 0.0:                    # R-83: record this step's output for the band levy
                        for a, h in zip(occ, hides):
                            self._hides_this_step[a] = self._hides_this_step.get(a, 0.0) + h
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
                a._last_intake = intake        # DIAGNOSTIC ONLY (no behaviour): the reserve cap below discards
                #   surplus, so post-harvest wealth cannot reveal how far intake EXCEEDED burn. Measured: ~99%
                #   of agents re-saturate at the cap every step, i.e. intake ≥ burn, with the excess invisible.
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
                    if getattr(self._demog, "enable_stratification_inequality_gate", False):   # R-103
                        target = society_from_character(density, surplus_frac,
                                                        wealth_gini=_gini([getattr(a, "cred", 1.0) for a in occ]),
                                                        gini_min=self._demog.stratification_gini_min)
                    else:
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
            ineq_gate = getattr(self._demog, "enable_stratification_inequality_gate", False)   # R-103 v1 (within-band)
            relational = getattr(self._demog, "enable_relational_stratification", False)       # R-103 v2 (between-band)
            _collect_cred = ineq_gate or relational
            band_creds: dict[int, list] = {}                       # per-band cred sample for either inequality gate
            for (cx, cy), occ in occ_lists.items():
                for a in occ:
                    bid = a._group.band_id
                    band_members[bid] = band_members.get(bid, 0) + 1
                    band_cells.setdefault(bid, set()).add((cx, cy))
                    band_cell_n[(bid, (cx, cy))] = band_cell_n.get((bid, (cx, cy)), 0) + 1
                    if _collect_cred:
                        band_creds.setdefault(bid, []).append(getattr(a, "cred", 1.0))
            land_pack = getattr(self._demog, "enable_landscape_packing", False)   # R-61: landscape vs band-member density
            self._band_surplus = {}
            self._band_cred_gini = {}                        # R-103: per-band cred Gini (populated only when the gate is on)
            # R-98: per-band ascribed head-count for the rank->hierarchy unlock. Computed once here
            # rather than per band, and skipped entirely when the flag is off (=> bit-exact).
            rank_on = self._demog is not None and getattr(self._demog, "enable_rank_hierarchy", False)
            rank_frac = self._demog.rank_hierarchy_frac if rank_on else 0.0
            asc_n: dict = {}
            if rank_on and self._lineage_ascribed:
                _rk = self._rank_keys()
                for _a in self.agent_list:
                    if _rk[_a] in self._lineage_ascribed:
                        _b = _a._group.band_id
                        asc_n[_b] = asc_n.get(_b, 0) + 1
            # REGIONAL-DENSITY basis for the classifier (R-106, 2026-08-24): each band's fair share of the
            # whole habitable range, = habitable_km2 / n_bands. This is the scale Binford's 0.091/km2
            # threshold is defined at; the occupied-cell footprint below is a LOCAL density that reads every
            # crowded band as packed. Off => the legacy occupied-cell basis, bit-exact.
            reg_dens_on = getattr(self._demog, "enable_society_regional_density", False)
            _hab_km2 = getattr(self, "_habitable_cells", 0) * _CELL_KM2
            _range_km2 = (_hab_km2 / len(band_members)) if (reg_dens_on and band_members and _hab_km2 > 0) else 0.0
            # R-103 RELATIONAL: the regional BETWEEN-band inequality (Gini of per-band mean cred) and the top-
            # quantile threshold, computed ONCE. A band is a chiefly centre only in an unequal region AND at its top.
            _band_mean_cred: dict = {}
            _between_gini = None
            _top_thr = None
            if relational and band_creds:
                _band_mean_cred = {b: (sum(v) / len(v)) for b, v in band_creds.items()}
                _means = sorted(_band_mean_cred.values())
                _between_gini = _gini(_means)
                self._between_band_gini = _between_gini              # diagnostic (regional inequality this step)
                _qi = min(len(_means) - 1, int(self._demog.strat_top_quantile * len(_means)))
                _top_thr = _means[_qi]
            for bid, n in band_members.items():
                footprint_km2 = len(band_cells[bid]) * _CELL_KM2
                # LANDSCAPE population density (all agents on the band's cells / area = the Binford quantity) when on;
                # else the legacy band-members/footprint (a band's density over its own range).
                head = sum(len(occ_lists[c]) for c in band_cells[bid]) if land_pack else n
                if _range_km2 > 0.0:
                    density = n / _range_km2                 # members over the band's SHARE of the range
                else:
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
                if relational:                                  # R-103 v2: stratified needs an UNEQUAL region + a top band
                    _bm = _band_mean_cred.get(bid, 0.0)
                    target = society_from_character(
                        density, surplus_frac,
                        between_gini=_between_gini, between_gini_min=self._demog.between_band_gini_min,
                        band_is_top=(_top_thr is None or _bm >= _top_thr))
                elif ineq_gate:                                 # R-103 v1: stratified requires UNEQUAL within-band cred
                    _wg = _gini(band_creds.get(bid, ()))
                    self._band_cred_gini[bid] = _wg
                    target = society_from_character(density, surplus_frac,
                                                    wealth_gini=_wg, gini_min=self._demog.stratification_gini_min)
                else:
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
                # R-98's one-rung promotion was applied here and is SUPERSEDED by R-99's graded weight; see
                # DEAD_ENDS DE-22. It promoted the whole village on a threshold of one ranked lineage in seven,
                # which measured 70.6% stratified against R-64's validated 9-16%.
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
        intake_fert_on = demog is not None and getattr(demog, "enable_intake_fertility", False)
        # R-106 Addendum 6: mobility-pressure mode reads the SAME `_intake_ema` fertility computes, so keep the
        # EMA live for it too even when the fertility mechanism itself is off — the two stay independently
        # ablatable (flip either flag alone) while sharing one signal, not two parallel computations of it.
        mobility_wants_intake = (demog is not None and getattr(demog, "enable_productivity_mobility", False)
                                  and getattr(demog, "mobility_pressure_source", "npp") == "intake")
        # The energetic refractory reads the same intake EMA, so it must also switch the signal on — a
        # mechanism gated on a signal nobody computes is the "ON but dead" failure this project keeps finding.
        refrac_on = demog is not None and getattr(demog, "enable_energetic_refractory", False)
        intake_signal_on = intake_fert_on or mobility_wants_intake or refrac_on
        i_alpha = demog.intake_ema_alpha if intake_signal_on else 0.0
        i_menarche = demog.menarche_months if intake_signal_on else 0
        # §4.6.7 metabolic down-regulation: under a draining reserve, burn falls toward a floor (Keys 1950).
        downreg_on = demog is not None and getattr(demog, "enable_metabolic_downreg", False)
        dr_max = demog.metabolic_downreg_max if downreg_on else 0.0
        dr_span = demog.metabolic_downreg_span if downreg_on else 1.0
        dep_load = {}
        if intake_fert_on and getattr(demog, "enable_dependent_load", False):
            # A mother's real energy budget covers her juveniles' UNMET need, not just her own maintenance.
            # Using the child's own gathered intake makes the load fall as it learns to feed itself — no
            # explicit weaning schedule is imposed. (Blurton Jones; Kaplan provisioning.)
            for c in self.agent_list:
                if not c.is_juvenile():
                    continue
                m = getattr(c, "_mother", None)
                if m is None or not m.alive:
                    continue
                _deficit = self._burn * c.consumption_factor() - c._last_intake
                if _deficit > 0.0:
                    dep_load[m] = dep_load.get(m, 0.0) + _deficit
        for a in self.agent_list:
            a._fed_reserve = a.wealth        # post-harvest reserve = nutritional status (synergy/fertility read THIS)
            if intake_signal_on and a.age >= i_menarche:
                # Energy FLUX, not stored reserve (Ellison). Gathered intake over this step's own maintenance
                # requirement; the reserve level cannot carry this because it re-saturates at the cap.
                _req = self._burn * a.consumption_factor() + dep_load.get(a, 0.0)
                _ratio = (a._last_intake / _req) if _req > 0.0 else 1.0
                a._intake_ema = (1.0 - i_alpha) * a._intake_ema + i_alpha * _ratio
            _burn_a = self._burn * a.consumption_factor()   # C.1 age-scaled maintenance (1.0 if lh_config off)
            if downreg_on:
                # §4.6.7: a draining reserve turns the metabolism down (Keys 1950). frac = reserve fill in
                # [0,1]; full reserve -> d=0 (bit-exact for the well-fed). Buffers a transient crash; a true
                # chronic deficit below the reduced burn still kills, so real scarcity is unbuffered.
                _flr = a.reserve_floor * a.reserve_scale()
                _cap = self._reserve_full * a.reserve_scale()
                _frac = (a.wealth - _flr) / (_cap - _flr) if _cap > _flr else 1.0
                _frac = 0.0 if _frac < 0.0 else (1.0 if _frac > 1.0 else _frac)
                _burn_a *= 1.0 - dr_max * min(1.0, (1.0 - _frac) / dr_span)
            a.wealth -= _burn_a
            if mcf is not None and getattr(a, "_moved_this_step", False):
                a.wealth -= float(mcf[a.pos[1], a.pos[0]])     # Stage 1b: realized terrain move cost (drain movers)
                a._moved_this_step = False
            if cond_on:                      # S0: slow EMA of nutritional status → body condition / immune competence
                # SAMPLED AT THE TROUGH (2026-07-27). This EMA used to read `_fed_reserve`, i.e. wealth
                # POST-harvest but PRE-burn — the PEAK of the metabolic cycle. `_frac` clamps at 1.0, so any
                # agent whose harvest topped it up read "completely fed", and the EMA of a near-constant 1.0
                # stayed at 1.0. Measured: mean `_condition` 0.9998 (min 0.974) in a crowded BOREAL world, so
                # the mortality multiplier it feeds was ~1.0002 and `enable_nutrition_synergy` was silently
                # DEAD whenever `enable_condition` was on (ablation displacement 0.3468 -> 0.0000). Reading
                # wealth after maintenance + movement costs is the trough, so a real deficit is visible.
                # `_fed_reserve` is deliberately NOT changed: energetic fertility and the legacy synergy
                # branch read it, and both want the post-harvest value.
                _rs = a.reserve_scale()
                _lo = a.reserve_floor * _rs; _span = self._reserve_full * _rs - _lo
                _frac = (a.wealth - _lo) / _span if _span > 0 else 1.0
                _frac = 0.0 if _frac < 0.0 else (1.0 if _frac > 1.0 else _frac)
                a._condition = (1.0 - c_alpha) * a._condition + c_alpha * _frac
            a.age += 1
            # Realised life table (pure observer). Exposure is accrued AFTER the age increment so that a
            # death recorded later in this same iteration lands in the SAME one-year bin as the exposure
            # that earned it; accruing before would shift deaths up by ~1/12 yr against their denominator
            # and bias every hazard low. An agent that dies this step still contributes its full month —
            # the standard life-table half-month refinement is not worth a second code path here.
            _lt_i = int(a.age // MONTHS_PER_YEAR)
            if _lt_i >= LT_MAX_AGE_YR:
                _lt_i = LT_MAX_AGE_YR - 1
            self.lt_exposure[_lt_i] += 1
            if a.sex == "female":
                self.fert_exposure[_lt_i] += 1
                self.lt_exposure_f[_lt_i] += 1
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
                    self.lt_deaths[_lt_i] += 1; self.lt_deaths_f[_lt_i] += (a.sex == "female"); self.lt_deaths_starv[_lt_i] += 1
                    self._note_starvation_state(a, occ_count, _lt_i)   # WHO starves, and where (see below)
                    self._note_band_starv(a)                          # M2: attribute this starvation death to its band
                    self.starv_cred_this_step.append(a.cred)
                    self.starv_status_this_step.append(a.cred * getattr(a, "prowess", 1.0))
                elif self._orphan_lethal(a):              # R-74: mother lost in year 1 ⇒ 100% (Hill & Hurtado)
                    a.alive = False
                    self.deaths_senesc_this_step += 1
                    self.lt_deaths[_lt_i] += 1; self.lt_deaths_f[_lt_i] += (a.sex == "female"); self.lt_deaths_senesc[_lt_i] += 1
                    self.deaths_orphan_this_step += 1
                else:
                    a2m = self._a2_mult(a, occ_count)     # Step-2 a2 modulators (1.0 if all flags off)
                    om = self._orphan_mult(a)             # R-74: kin/orphan hazard multiplier (1.0 if off)
                    if a.random.random() < self._siler[a.sex].monthly_death_prob(a.age, a2m, om):
                        a.alive = False                   # Siler baseline+senescence
                        self.deaths_senesc_this_step += 1
                        self.lt_deaths[_lt_i] += 1; self.lt_deaths_f[_lt_i] += (a.sex == "female"); self.lt_deaths_senesc[_lt_i] += 1
                        if om > 1.0:
                            self.deaths_orphan_this_step += 1   # diag: died while carrying an elevated kin hazard
                    elif a.age >= a.max_age:              # hard lifespan cap (Siler-tail backstop; was DEAD CODE
                        a.alive = False                   # under demog — the elif below is only reached when
                        self.deaths_senesc_this_step += 1  # demog is None, so ancient agents slipped through to 1111)
                        self.lt_deaths[_lt_i] += 1; self.lt_deaths_f[_lt_i] += (a.sex == "female"); self.lt_deaths_senesc[_lt_i] += 1
            elif a.wealth <= a.reserve_floor:
                a.alive = False
                self.deaths_starv_this_step += 1
                self.lt_deaths[_lt_i] += 1; self.lt_deaths_f[_lt_i] += (a.sex == "female"); self.lt_deaths_starv[_lt_i] += 1
                self._note_band_starv(a)
            elif a.age >= a.max_age:
                a.alive = False
                self.deaths_senesc_this_step += 1
                self.lt_deaths[_lt_i] += 1; self.lt_deaths_f[_lt_i] += (a.sex == "female"); self.lt_deaths_senesc[_lt_i] += 1

        # GD-1: advance the depletable resource stock (deplete by this step's foraging pressure, regrow at the
        # biome/season rate). No-op unless the harvest field has depletion enabled. `season` from the climate field
        # if present (growing-season pulse), else aseasonal.
        if hasattr(tf, "deplete_and_regrow"):
            season = tf.season() if hasattr(tf, "season") else 1.0
            press = (self._catchment_foraging_pressure(occ_count)
                     if getattr(self._demog, "enable_catchment_depletion", False) else occ_count)
            tf.deplete_and_regrow(press, season)

    def _note_starvation_state(self, a, occ_count: dict, age_i: int) -> None:
        """Record the state of an agent AT THE MOMENT IT STARVES (pure observer).

        WHY THIS EXISTS. Every intake diagnostic in this model samples agents that are ALIVE at the snapshot,
        so the starved are invisible to all of them — survivorship bias. Measured consequence: at a population
        of 8338 (0.58x Binford density) the median woman takes in 5.3x her requirement and the TENTH percentile
        still takes in 1.65x, while a third of all deaths are starvation. Those two facts cannot both describe
        a food shortage, and no diagnostic that samples survivors can tell which of them is misleading.

        THE CANDIDATE THIS SEPARATES. `compute_harvest_shares` is RIVALROUS: an occupant receives S/n, the
        cell yield divided by the number standing on it. So intake is set by LOCAL occupancy, not by global
        density, and agents that cluster can starve in a crowded cell while the map average stays high. If
        that is the mechanism, the mean occupancy at a starvation death will be far ABOVE the occupancy an
        average agent experiences. If the two match, crowding is not the cause and the yield of the cell is.

        Sums rather than samples, so the cost is O(1) per death and nothing is retained per agent.
        """
        self.starv_events += 1
        self.starv_occ_sum += float(occ_count.get(a.pos, 1))
        self.starv_age_sum += float(a.age)
        req = self._burn * a.consumption_factor()
        self.starv_intake_sum += (a._last_intake / req) if req > 0.0 else 0.0
        self.starv_ema_sum += float(getattr(a, "_intake_ema", 0.0))
        _cap = self._reserve_full * a.reserve_scale()
        _fr = (float(getattr(a, "_fed_reserve", 0.0)) / _cap) if _cap > 0.0 else 0.0
        self.starv_fedres_sum += _fr
        if _fr > 0.5:                          # was more than half-full last step -> acute crash, not slow decline
            self.starv_acute_n += 1
        if age_i < LT_MAX_AGE_YR:
            self.starv_by_age[age_i] += 1

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
        lbr = (cfg.lineage_branch_rate                          # R-90: per-birth new-named-line prob (0 ⇒ inert)
               if getattr(cfg, "enable_lineage_branching", False) else 0.0)
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
        # Resolved here as well as in `_step_rivalrous` (which uses it to switch the intake EMA on) because
        # the two live in different methods; a name defined in one is not visible in the other.
        refrac_on = getattr(cfg, "enable_energetic_refractory", False)
        newborns: list[BaseAgent] = []
        for a in self.agent_list:
            if a.sex != "female":
                continue
            # THE REFRACTORY, resolved in one place so the two mechanisms COMPOSE instead of racing.
            # `sedentism_ibi` sets the society BASE (30 egalitarian → 22 complex); `energetic_refractory`
            # then STRETCHES whatever base applies by the woman's own energy shortfall. Written as a single
            # expression because the previous shape — an if/elif with the eligibility test duplicated in each
            # branch — is how a third mechanism would end up applied on one path and not the other.
            if refrac_on or sed_fert:
                if sed_fert:
                    soc = self._band_society.get(a._group.band_id) or self._cell_society.get(a.pos)
                    ibi_m = float(sedentism_ibi(soc, cfg.ibi_refractory_months))
                else:
                    ibi_m = float(cfg.ibi_refractory_months)
                if refrac_on:
                    ibi_m = energetic_refractory(ibi_m, a._intake_ema, cfg)
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
            if getattr(cfg, "enable_intake_fertility", False):
                # SUPERSEDES the reserve branch: births scale with sustained energy BALANCE, not stored reserve
                # (which re-saturates at the cap for ~99% of agents and so carries no signal). 0 at maintenance,
                # full at maintenance + the lactation increment.
                _sp = cfg.intake_fert_hi - cfg.intake_fert_lo
                _f = 1.0 if _sp <= 0.0 else (a._intake_ema - cfg.intake_fert_lo) / _sp
                p_birth *= 0.0 if _f < 0.0 else (1.0 if _f > 1.0 else _f)
            elif cfg.enable_energetic_fertility:               # births scale with NUTRITIONAL status (post-harvest)
                _rs = a.reserve_scale()                        # C.2a age-scaled floor/full
                p_birth *= energetic_fertility_factor(a._fed_reserve, a.reserve_floor * _rs, self._reserve_full * _rs)
            # Realised fertility schedule (pure observer). Sampled HERE — past the age gate, the IBI gate and
            # the mate gate — so the denominator is "women actually at risk of conception this step", which is
            # what makes the multiplier interpretable. Sampling over all women would dilute it with the
            # refractory and the pre-menarche, and a brake that never bites would look like one that does.
            _ff = (p_birth / cfg.fecundability) if cfg.fecundability > 0.0 else 1.0
            self.fert_factor_sum += _ff
            self.fert_factor_n += 1
            if _ff >= 0.999:
                self.fert_factor_sat += 1
            if a.random.random() < p_birth:
                # Recorded BEFORE months_since_birth is cleared: after the reset the realised interval is gone.
                # Parity 0 is excluded because her counter measures time since menarche, not since a birth.
                if a.parity >= 1:
                    _ibi = int(a.months_since_birth)
                    self.ibi_hist[_ibi if _ibi < IBI_HIST_MAX else IBI_HIST_MAX] += 1
                _mi = int(a.age // MONTHS_PER_YEAR)
                self.fert_births[_mi if _mi < LT_MAX_AGE_YR else LT_MAX_AGE_YR - 1] += 1
                if a.parity == 0:                 # recorded BEFORE the increment: this birth is her first
                    self.first_birth_age_sum += float(a.age)
                    self.first_birth_n += 1
                a.months_since_birth = 0
                a.parity += 1
                csex = "male" if a.random.random() < cfg.srb_male else "female"
                if csex == "male":
                    self.births_male += 1
                else:
                    self.births_female += 1
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
                # R-92: the SUB-BRANCH tag, inherited patrilineally exactly like `_lineage` (matriline fallback
                # when no father was resolved), so a shared tag always means a shared descent group.
                _f = getattr(child, "_father", None)
                child._subclan = _f._subclan if _f is not None else a._subclan
                # R-90 BRANCHING, RESHAPED (R-92). It used to mint a whole new LINEAGE here, which made every new
                # line a SINGLETON — and a lineage of one usually dies, so it produced a churn of ephemeral names:
                # measured n_lineages 5→32 while eff_lineages FELL 3.4→1.8 and top_share ROSE 0.42→0.73. Count up,
                # substance down. It now seeds a new SUB-CLAN instead, where starting at one member is harmless:
                # the tag either grows into a real body of kin or vanishes unnoticed. Only once it HAS grown can
                # `_do_lineage_split` promote it to a full lineage — so new lineages are born viable, not tiny.
                # `lbr == 0.0` ⇒ no RNG draw at all ⇒ the stream is untouched ⇒ bit-exact.
                if lbr > 0.0 and self.random.random() < lbr:
                    child._subclan = self._next_subclan_id
                    self._next_subclan_id += 1
                    self.lineage_branches_this_step += 1
                newborns.append(child)
                self.births_this_step += 1
        self.agent_list.extend(newborns)
        if self._genealogy_log is not None:               # Stage 2: observer log (after birth, parents/lineage set)
            for c in newborns:
                self._log_genea("birth", c)

        # R-83 (elite step 1): LEADER SHARE — "managerial rights" over the BAND's corporate output.
        # The band owns the sites (`_cell_owner` is corporate); the leader does not own them, he CONTROLS the
        # product — Hayden's "managerial rights over the resource locations and facilities of the group". Each
        # band's current leader (recomputed from cred·prowess, so the office is contingent and deposable —
        # Boehm) levies `leader_share_frac` of that step's durable output from his band-mates.
        # This runs at BAND level (~25 agents) deliberately: R-82b's per-CELL capture had 1–2 agents and no
        # group to skim (1.14×). The corporate unit is the band.
        if (self._demog is not None and getattr(self._demog, "enable_leader_share", False)
                and self._demog.leader_share_frac > 0.0 and self._hides_this_step):
            lf = self._demog.leader_share_frac
            leaders = self.band_leaders()
            by_band: dict = {}
            for a, h in self._hides_this_step.items():
                if a.alive and h > 0.0:
                    by_band.setdefault(a._group.band_id, []).append((a, h))
            for bid, rows in by_band.items():
                lead = leaders.get(bid)
                if lead is None or not lead.alive:
                    continue
                levy = 0.0
                for a, h in rows:
                    if a is lead:
                        continue                            # the leader keeps his own production
                    take = lf * h
                    if take > a.material:                   # never levy more than he actually holds
                        take = a.material
                    if take > 0.0:
                        a.material -= take
                        levy += take
                if levy > 0.0:
                    lead.material += levy
                    self.leader_levy_this_step += levy

        # R-103f PER-LINEAGE (CHIEFLY) TRIBUTE — the wealth-finance channel that builds a HEREDITARY estate rather
        # than an office hoard. The CHIEF of a band = the highest cred·prowess member of an ASCRIBED lineage there
        # (defined by legitimacy+rank, NOT by winning the office contest — so the estate survives office turnover
        # and is bequeathed within the lineage). Every member NOT of the chief's lineage pays `lineage_tribute_frac`
        # of this step's durable production to the chief. One winner per band ⇒ concentrates even when ascription is
        # broad. Default OFF ⇒ skipped, bit-exact. [Friedman; Earle wealth finance; gumsa 'a thigh' ≈ DM-F6]
        if (self._demog is not None and getattr(self._demog, "enable_lineage_tribute", False)
                and self._demog.lineage_tribute_frac > 0.0 and self._hides_this_step and self._lineage_ascribed):
            tf = self._demog.lineage_tribute_frac
            rk = self._rank_keys()
            prod_by_band: dict = {}
            for a, h in self._hides_this_step.items():
                if a.alive and h > 0.0:
                    prod_by_band.setdefault(a._group.band_id, []).append((a, h))
            members_by_band: dict = {}
            for a in self.agent_list:
                if rk.get(a) in self._lineage_ascribed:
                    members_by_band.setdefault(a._group.band_id, []).append(a)
            for bid, rows in prod_by_band.items():
                asc_here = members_by_band.get(bid)
                if not asc_here:
                    continue                                    # no ascribed lineage present ⇒ no chief, no tribute
                chief = max(asc_here, key=lambda a: a.cred * getattr(a, "prowess", 1.0))
                chief_lin = rk.get(chief)
                trib = 0.0
                for a, h in rows:
                    if rk.get(a) == chief_lin:
                        continue                                # the chief's own lineage does not pay itself
                    take = tf * h
                    if take > a.material:
                        take = a.material
                    if take > 0.0:
                        a.material -= take
                        trib += take
                if trib > 0.0:
                    chief.material += trib
                    self.lineage_tribute_this_step += trib
        self._hides_this_step = {}

        # R-82 Stage A: BOEHM LEVELING — the reverse-dominance coalition. Co-residents sanction whoever holds
        # conspicuously more material than the local norm and force him to disgorge it to them (Boehm's sanction
        # against "monopolizing resources", executed as Hayden's redistributive feast). Deliberately NOT
        # abundance-gated — capture is, leveling isn't, so ABUNDANCE ALONE decides which force wins.
        if self._demog is not None and getattr(self._demog, "enable_leveling", False):
            lev_s = self._demog.leveling_strength
            lev_sh = self._demog.leveling_share
            # R-103e — the SAME legitimacy exemption the overreach-deposition path uses (line ~3146), applied here
            # to the WEALTH-DISGORGEMENT. This is the coupling that was missing: without it a levied estate is
            # stripped back to the local norm every step, so an ascribed noble could hold OFFICE (deposition-exempt)
            # yet never ACCUMULATE (still disgorged). A legitimate noble's material is "his by right" (Flannery
            # ch.16 / Friedman), so his excess is not conspicuous/sanctionable. OFF ⇒ `_lx_rk` is None ⇒ bit-exact.
            _lx_on = getattr(self._demog, "enable_noble_leveling_exemption", False)
            _lx_frac = getattr(self._demog, "noble_exemption_frac", 1.0) if _lx_on else 0.0
            _lx_rk = self._rank_keys() if _lx_on else None
            if lev_s > 0.0 and lev_sh > 0.0:
                by_cell: dict = {}
                for a in self.agent_list:
                    by_cell.setdefault(a.pos, []).append(a)
                for occ_l in by_cell.values():
                    if len(occ_l) < 2:
                        continue                                  # no coalition of one
                    mats = [a.material for a in occ_l]
                    mean_m = sum(mats) / len(mats)
                    if mean_m <= 0.0:
                        continue
                    for a in occ_l:
                        excess = a.material - mean_m
                        if excess <= 0.0:
                            continue
                        if _lx_rk is not None and _lx_rk.get(a) in self._lineage_ascribed:
                            excess *= (1.0 - _lx_frac)            # legitimate accumulation is not sanctioned
                            if excess <= 0.0:
                                continue                          # fully exempt (frac=1.0) ⇒ no disgorgement
                        # conspicuousness = how far above the local norm he stands (Boehm: it is the VISIBLE
                        # self-assertion that draws sanction, not absolute wealth)
                        p = lev_s * (excess / mean_m)
                        if p > 1.0:
                            p = 1.0
                        if a.random.random() < p:
                            share = excess * lev_sh
                            a.material -= share
                            others = [x for x in occ_l if x is not a]
                            per = share / len(others)
                            for x in others:
                                x.material += per
                            self.leveling_events_this_step += 1

        # R-86 DM-F1: the LEGITIMACY channel — lineages buy ritual standing with material, and sustained
        # standing converts into HERITABLE cred (achieved → ascribed). Placed after leveling (you feast with
        # what survived the coalition) and before cred renorm (so the mean is re-pinned after the injection).
        self._do_legitimacy()
        self._do_delegitimation()   # R-87: the gumsa → gumlao reversion (the lagged counterforce)

        # R-82 Stage A: durable-capital depreciation. `material` is a STOCK (that is the point — it persists
        # where `wealth` is burned), but nothing is imperishable: stores rot, prestige goods are given away in
        # feasts, herds die. 0 ⇒ imperishable (bit-exact).
        if self._demog is not None and getattr(self._demog, "material_decay", 0.0) > 0.0:
            keep = 1.0 - self._demog.material_decay
            for a in self.agent_list:
                if a.material > 0.0:
                    a.material *= keep

        # R-81: renormalise cred to population-mean 1 (fix the homeostat mean-inflation). Dynamics-neutral for
        # the relative (cred)^κ / normalised-mate weights; re-tightens the inheritance homeostat. Off ⇒ bit-exact.
        if self._demog is not None and getattr(self._demog, "enable_cred_renorm", False):
            cr = [a.cred for a in self.agent_list if getattr(a, "use_cred_status", False)]
            if cr:
                mc = sum(cr) / len(cr)
                if mc > 0.0:
                    for a in self.agent_list:
                        if getattr(a, "use_cred_status", False):
                            a.cred /= mc

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

    # ── Demographic diagnostics (R-75) ───────────────────────────────────────────────────────────
    # A standing read-out of every demographic marker, groupable by village/band, so drift is caught
    # rather than discovered. Motivation: R-74 spent a session chasing a "3.4× orphan excess" that turned
    # out to be R-16's fertility-pinning — visible immediately had the orphan-exposure markers been on a
    # dashboard next to e₀. Pure measurement: reads live state, mutates nothing, costs one pass.

    #: Age-class boundaries in YEARS. child<15 = pre-menarche (`menarche_months`=180); elder≥60 follows the
    #: Aché cause-of-death tables (Table 5.1's classes are 0–3 / 4–14 / 15–59 / 60+).
    _AGE_CHILD_YR, _AGE_ELDER_YR = 15.0, 60.0

    @staticmethod
    def _gini(v: list) -> float:
        """Gini of a non-negative vector; 0 for an empty/all-zero vector (no fake inequality)."""
        v = sorted(x for x in v)
        n = len(v); s = sum(v)
        if n == 0 or s <= 0.0:
            return 0.0
        return (2.0 * sum((i + 1) * x for i, x in enumerate(v))) / (n * s) - (n + 1.0) / n

    @staticmethod
    def _top_share(v: list, frac: float) -> float:
        """Share of the total held by the top `frac` of holders (0 if nothing is held)."""
        v = sorted(v, reverse=True)
        s = sum(v)
        if not v or s <= 0.0:
            return 0.0
        return sum(v[:max(1, int(len(v) * frac))]) / s

    @staticmethod
    def _corr(xs: list, ys: list) -> float:
        import math as _m
        n = len(xs)
        if n < 3:
            return float("nan")
        mx = sum(xs) / n; my = sum(ys) / n
        sx = _m.sqrt(sum((x - mx) ** 2 for x in xs)); sy = _m.sqrt(sum((y - my) ** 2 for y in ys))
        return (sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (sx * sy)) if sx > 0 and sy > 0 else float("nan")

    def _demog_markers(self, pop: list) -> dict:
        """Markers for one group of live agents. `nan` where a denominator is empty — never a fake 0."""
        import statistics as _st
        _gini = self._gini; _top_share = self._top_share; _corr = self._corr
        n = len(pop)
        if n == 0:
            return {"n": 0}
        males = [a for a in pop if a.sex == "male"]
        females = [a for a in pop if a.sex == "female"]
        ages = [a.age / MONTHS_PER_YEAR for a in pop]
        child = [a for a in pop if a.age < self._AGE_CHILD_YR * MONTHS_PER_YEAR]
        elder = [a for a in pop if a.age >= self._AGE_ELDER_YR * MONTHS_PER_YEAR]
        adult = [a for a in pop if self._AGE_CHILD_YR * MONTHS_PER_YEAR <= a.age
                 < self._AGE_ELDER_YR * MONTHS_PER_YEAR]
        adult_f = [a for a in females if a.age >= self._AGE_CHILD_YR * MONTHS_PER_YEAR]
        paired_f = [a for a in adult_f if getattr(a, "_partner", None) is not None]
        wives = [len(getattr(a, "_wives", ())) for a in males
                 if a.age >= self._AGE_CHILD_YR * MONTHS_PER_YEAR]
        married_m = [w for w in wives if w > 0]
        # Orphan EXPOSURE among the 0–9 risk set — the Hill & Hurtado Table 13.1 covariates. Agents of
        # unknown parentage (founders) are excluded: they are not in the risk set, and counting them as
        # non-orphans would dilute the marker toward 0 early in a run.
        risk = [a for a in pop if a.age <= 9 * MONTHS_PER_YEAR
                and not (getattr(a, "_mother", None) is None and getattr(a, "_father", None) is None)]
        md = fd = dv = 0
        for a in risk:
            m_dead, f_dead, divorced = self._orphan_status(a)
            md += m_dead; fd += f_dead; dv += divorced
        nr = len(risk)
        nan = float("nan")
        # R-82 markers read defensively: a diagnostic must never crash on a partially-populated agent
        # (synthetic stand-ins in tests, or an agent built before a later stage's attributes existed).
        _mat = [getattr(a, "material", 0.0) for a in pop]
        _aggr = [getattr(a, "aggrandizer", 0.0) for a in pop]
        _cells = {getattr(a, "pos", None) for a in pop} - {None}
        _dens = (n / (len(_cells) * _CELL_KM2)) if _cells else nan
        return {
            "n": n,
            "n_male": len(males), "n_female": len(females),
            "sex_ratio_m_f": (len(males) / len(females)) if females else nan,
            "mean_age_yr": _st.mean(ages), "median_age_yr": _st.median(ages),
            "frac_child": len(child) / n, "frac_adult": len(adult) / n, "frac_elder": len(elder) / n,
            "dependency_ratio": (len(child) + len(elder)) / len(adult) if adult else nan,
            # SPLIT, because the two halves move in OPPOSITE directions and the combined ratio hides it: a
            # high-fertility runaway raises the child half while thinning the old half, so a ratio can sit
            # "only" 1.5x its anchor while both components are far out. Measured 2026-08-14: child 1.32 and
            # old-age 0.01 against a combined 1.33 — essentially all of it is children, which the combined
            # number does not say.
            "dependency_child": (len(child) / len(adult)) if adult else nan,
            "dependency_old": (len(elder) / len(adult)) if adult else nan,
            "frac_paired_adult_f": (len(paired_f) / len(adult_f)) if adult_f else nan,
            "mean_wives_married_m": (_st.mean(married_m) if married_m else nan),
            "frac_polygynous_m": (sum(1 for w in married_m if w > 1) / len(married_m)) if married_m else nan,
            # Table 13.1 covariates — compare against mother alive 0.98 / father alive 0.95 / divorced 0.14
            "n_risk_0_9": nr,
            "frac_motherless": (md / nr) if nr else nan,
            "frac_fatherless": (fd / nr) if nr else nan,
            "frac_parents_divorced": (dv / nr) if nr else nan,
            # R-82 Stage A — the MATERIAL capital cell. The test of whether status gets material teeth:
            # `material_gini` should RISE and persist (vs wealth_gini, which the sharing economy flattens),
            # and `corr_cred_material` should be strongly positive (vs corr(cred, wealth) ≈ 0).
            "material_mean": _st.mean(_mat),
            "material_gini": _gini(_mat),
            "material_top10_share": _top_share(_mat, 0.10),
            "wealth_gini": _gini([getattr(a, "wealth", 0.0) for a in pop]),
            "corr_cred_material": _corr([getattr(a, "cred", 1.0) for a in pop], _mat),
            # capture must key on the AGGRANDIZER trait, not inherited cred (R-82 spec fix)
            "frac_aggrandizer": sum(1 for a in _aggr if a > 0.0) / n,
            "corr_aggr_material": _corr(_aggr, _mat),
            # LOCAL CROWDING — population over the cells that are OCCUPIED, i.e. mean occupancy per settled
            # cell. RENAMED from `density_per_km2` (R-106, 2026-08-04) because it was being compared against
            # Hayden 1995 Fig. 6, Binford packing (0.091/km²) and Tallavaara (0.1-0.5), all of which are
            # REGIONAL densities over territory. Measured on eight long arms, this measure runs 1.7-20x
            # (median 2.3x) above the regional one and moved the Hayden band in 6 of 8. It is the right
            # measure for a per-band or per-village view — those have no territory — and the wrong one to
            # score an ethnographic density anchor with. The campaign row carries
            # `density_regional_per_km2` beside it, and scores `hayden_stage` on THAT.
            "density_occupied_per_km2": _dens,
            "hayden_stage_occupied": self._hayden_stage(_dens) if _dens == _dens else "n/a",
            **self._age_structure(pop, males, females, adult),
        }

    #: Age-pyramid classes in YEARS, [lo, hi). Finer than the child/adult/elder split above because the
    #: SHAPE is the signal — a growing population is broad-based and a declining one is not, and the coarse
    #: three-class view cannot tell those apart. The 0–4 / 5–14 split follows Hill & Hurtado's Aché classes
    #: (Table 5.1: 0–3 / 4–14 / 15–59 / 60+); 15–29 / 30–44 / 45–59 splits the reproductive span so the
    #: female cohorts that actually bear can be seen separately from those aging out of it.
    _PYRAMID = ((0, 5), (5, 15), (15, 30), (30, 45), (45, 60), (60, 200))

    @classmethod
    def _age_structure(cls, pop: list, males: list, females: list, adult: list) -> dict:
        """The age pyramid, the mating-suitability ratios, and the growth-regime call.

        WHY (R-106, supervisor request 2026-08-04). The existing markers carry `median_age_yr`,
        `sex_ratio_m_f` and a coarse child/adult/elder split, which is enough to notice that something is
        wrong and not enough to say what. Three things were missing and each cost time this arc:

        * **the pyramid itself** — the shape is what distinguishes a growing from a declining population, and
          three classes cannot show it;
        * **mating suitability** — `frac_unpaired_adult` is the φ that `LITERATURE.md` assumes is ≈0.1 when it
          derives `mate_search_min_eligible ≈ 15` from White's ~150-person MVP. Nothing measured it, so the
          assumption went unchecked for three weeks (Addendum 25);
        * **the operational sex ratio** — the ratio of mate-seeking males to receptive females is what sets
          how far the connubium search has to reach, and the reach was 11–75% of the whole population.

        `sex_ratio_m_f` above is over the WHOLE population including children; the mating-relevant ratios are
        adult-only, which is why they are separate keys rather than a refinement of that one.
        """
        nan = float("nan")
        n = len(pop)
        if n == 0:
            return {}
        M = MONTHS_PER_YEAR
        out: dict = {}
        for lo, hi in cls._PYRAMID:
            k = f"age_{lo}_{hi if hi < 200 else 'plus'}"
            out[k] = sum(1 for a in pop if lo * M <= a.age < hi * M) / n

        adult_m = [a for a in males if a.age >= cls._AGE_CHILD_YR * M]
        adult_f = [a for a in females if a.age >= cls._AGE_CHILD_YR * M]
        unpaired_m = [a for a in adult_m if not getattr(a, "_wives", ())]
        unpaired_f = [a for a in adult_f if getattr(a, "_partner", None) is None]
        out["adult_sex_ratio"] = (len(adult_m) / len(adult_f)) if adult_f else nan
        # φ — the share of the WHOLE population that is an unpaired adult. This is the conversion factor
        # between a mate-search pool counted in eligible partners and one counted in persons.
        out["frac_unpaired_adult"] = (len(unpaired_m) + len(unpaired_f)) / n
        out["frac_unpaired_adult_m"] = (len(unpaired_m) / len(adult_m)) if adult_m else nan
        # OSR (operational sex ratio): mate-SEEKING males per receptive female. >1 ⇒ males compete and the
        # search must reach further; the classic driver of mating-system structure.
        out["operational_sex_ratio"] = (len(unpaired_m) / len(unpaired_f)) if unpaired_f else nan

        # The pyramid's own shape ratio: the under-15 base against the 15–44 reproductive middle. Broad base
        # ⇒ expansive. Reported RAW beside the label so the label is never the load-bearing thing.
        base = out["age_0_5"] + out["age_5_15"]
        mid = out["age_15_30"] + out["age_30_45"]
        out["pyramid_base_ratio"] = (base / mid) if mid > 0 else nan
        out["growth_regime"] = cls._growth_regime(out["pyramid_base_ratio"],
                                                   len(adult) and (len(pop) - len(adult)) / len(adult))
        return out

    @staticmethod
    def _growth_regime(base_ratio: float, dep: float) -> str:
        """Classify the pyramid as expansive / stationary / constrictive, in `_hayden_stage`'s pattern.

        The base/reproductive-middle ratio is the standard shape statistic: a stationary population with flat
        mortality across the reproductive span has roughly as many people in its 15-yr child classes as in the
        30-yr middle, so the ratio sits near 1; a broad-based growing pyramid runs well above it, a
        narrow-based ageing one well below.

        **[PROVISIONAL] cut-offs 0.8 / 1.5** — conventional pyramid shape classes, NOT lit-anchored to a
        forager series. They are reported alongside the raw ratio precisely so the label can be ignored. The
        project's own age-structure anchors are `median_age_yr` ≈ 20 (Aché) and `frac_child` ≈ 40%
        (MARKER_MATRIX #4/#5), and those — not this label — are what a run should be scored on.
        """
        if base_ratio != base_ratio:
            return "n/a"
        if base_ratio >= 1.5:
            return "expansive"
        if base_ratio >= 0.8:
            return "stationary"
        return "constrictive"

    @staticmethod
    def _hayden_stage(dens: float) -> str:
        """Classify a local population density (people/km²) into Hayden 1995 Fig. 6's transegalitarian bands
        (VERIFIED from the page image, p.77): Egalitarian .01–<.1 · Despots .1–.2 · Reciprocators .2–1.0 ·
        Entrepreneurs 1.0–10.0 (Chiefs: no density given). The benchmark the elite layer must land in."""
        if dens < 0.01:
            return "sub-egalitarian"
        if dens < 0.1:
            return "egalitarian"
        if dens < 0.2:
            return "despot"
        if dens < 1.0:
            return "reciprocator"
        if dens < 10.0:
            return "entrepreneur"
        return "above-Hayden-range"

    def life_table(self, since: dict | None = None) -> dict:
        """The life table the run ACTUALLY REALISED, from accumulated exposure and deaths (pure observer).

        This is the counterpart to the Siler schedule the run was CONFIGURED with, and the two are different
        objects: R-106 measured a run realising e0 ~ 19 yr against a configured ACHE_FOREST e0 of 36.6.
        Nothing had ever compared them, so an age-structure failure could not be attributed to a hazard.

        Cumulative over the run by default. Pass `since` — an earlier return of `raw_demographic_counters()`
        — to obtain a PERIOD life table over the interval instead, which is how a run's early transient is
        kept out of its steady-state schedule.

        Returns `m` (central death rate per person-year, by single year of age), `q` (probability of dying
        within the year), `l` (survivorship from age 0), `e0`, and the starvation share of deaths. Bins with
        no exposure return 0.0 for `m` rather than NaN, so `l` stays defined across gaps in a small run.
        """
        ex, de = self.lt_exposure, self.lt_deaths
        ds, dn = self.lt_deaths_starv, self.lt_deaths_senesc
        if since is not None:
            ex = [a - b for a, b in zip(ex, since["lt_exposure"])]
            de = [a - b for a, b in zip(de, since["lt_deaths"])]
            ds = [a - b for a, b in zip(ds, since["lt_deaths_starv"])]
            dn = [a - b for a, b in zip(dn, since["lt_deaths_senesc"])]
        m: list[float] = []
        for i in range(LT_MAX_AGE_YR):
            py = ex[i] / MONTHS_PER_YEAR          # person-months -> person-YEARS of exposure
            m.append((de[i] / py) if py > 0.0 else 0.0)
        # Actuarial conversion assuming deaths fall uniformly through the year (a(x) = 1/2). At the monthly
        # step size the approximation costs far less than the sampling noise in any run we do.
        # CLAMPED TO 1.0. The actuarial conversion q = m/(1 + m/2) exceeds 1 whenever m > 2 deaths per
        # person-year, and a probability above 1 drives l(x) NEGATIVE. Measured 2026-08-14 on the short
        # test runs, which have almost no exposure: l(15) came back as -0.091 and l(25) as -0.500. A real
        # 15,000-step arm never approaches m = 2 so no scored result was affected, but a survivorship that
        # can go negative is not a survivorship, and every quantity built on it (e0, e15, surv_to_15) would
        # inherit the sign. The CTB battery missed it because every constructed case fed a plausible hazard.
        q = [min(1.0, mi / (1.0 + 0.5 * mi)) if mi > 0.0 else 0.0 for mi in m]
        l = [1.0]
        for i in range(LT_MAX_AGE_YR):
            l.append(l[-1] * (1.0 - q[i]))
        e0 = sum(0.5 * (l[i] + l[i + 1]) for i in range(LT_MAX_AGE_YR))
        td = sum(de)
        # ── REMAINING EXPECTANCY AT AGE x, and the survivorships that go with it ─────────────────────────
        # WHY e0 IS THE WRONG HEADLINE. e0 is dominated by infant mortality, which is why the cross-forager
        # e0 range is 21-37 while e15 sits near 38 everywhere. Foragers are conventionally compared on e15,
        # and Gurven & Kaplan 2007's Aché-forest row gives all of these [VERIFIED, LITERATURE.md]:
        #   e0 = 37   e15 = 38.5 remaining yr   e45 = 21.1   l(15) = 0.66   l(45)/l(15) = 0.43
        #   modal adult death = 71 (forest) / 78 (settled);  cross-HG modal adult death avg 72
        # They were on file unused while this arc reported e0 alone.
        def _ex(x: int) -> float:
            """Remaining expectancy at exact age x: Σ person-years lived beyond x, per survivor at x."""
            if x >= LT_MAX_AGE_YR or l[x] <= 0.0:
                return float("nan")
            return sum(0.5 * (l[i] + l[i + 1]) for i in range(x, LT_MAX_AGE_YR)) / l[x]
        # MODAL ADULT DEATH AGE — the mode of the death distribution ABOVE 20, not of all deaths. Including
        # childhood would return the infant peak every time and the anchor (71) would look absurd. `d(x)` is
        # the life-table death density l(x)-l(x+1), so this is a property of the SCHEDULE, not of the run's
        # age composition — which is what makes it comparable to a published life table.
        _dx = [l[i] - l[i + 1] for i in range(LT_MAX_AGE_YR)]
        _adult = _dx[20:]
        modal_adult = (20 + max(range(len(_adult)), key=lambda i: _adult[i])) if any(_adult) else float("nan")
        # ── MORTALITY BY AGE GROUP (supervisor request 2026-08-13) ───────────────────────────────────────
        # The single-year `m` array is the honest object but is unreadable in a banner. These bands are the
        # ones the age pyramid already uses, so a hazard and a population share can be read side by side.
        bands = [(0, 1), (1, 5), (5, 15), (15, 30), (30, 45), (45, 60), (60, LT_MAX_AGE_YR)]
        m_band, d_band, e_band = {}, {}, {}
        for lo, hi in bands:
            key = f"{lo}_{hi}" if hi < LT_MAX_AGE_YR else f"{lo}_plus"
            py = sum(ex[lo:hi]) / MONTHS_PER_YEAR
            m_band[key] = (sum(de[lo:hi]) / py) if py > 0 else 0.0
            d_band[key] = sum(de[lo:hi])
            e_band[key] = py
        return {"m": m, "q": q, "l": l[:-1], "e0": e0,
                "e15": _ex(15), "e45": _ex(45),
                # BOTH SURVIVORSHIPS, EXPLICITLY NAMED. LITERATURE.md records "survival-to-15 = 0.66,
                # survival 15→45 = 0.43" for the Aché forest period, and the second label is ambiguous:
                # fed the published ACHE_FOREST coefficients this estimator returns l(15) = 0.66 exactly and
                # a CONDITIONAL 15→45 of 0.65, whose product 0.66 × 0.65 = 0.43 is the published figure. So
                # 0.43 is survival to 45 FROM BIRTH, not conditional on reaching 15. Scoring the conditional
                # against it would mark a correct schedule as wrong by 50% — the "right number, wrong
                # denominator" failure this project has now made five times. Both travel, named for what
                # they are, so no future reader has to reconstruct which one the anchor means.
                "surv_to_15": l[15], "surv_to_45": l[45],
                "surv_15_to_45_cond": (l[45] / l[15]) if l[15] > 0 else float("nan"),
                "modal_adult_death": modal_adult,
                "m_by_band": m_band, "deaths_by_band": d_band, "exposure_by_band": e_band,
                "deaths": td, "exposure_py": sum(ex) / MONTHS_PER_YEAR,
                "deaths_starv": sum(ds), "deaths_senesc": sum(dn),
                "starv_share": (sum(ds) / td) if td else 0.0}

    def fertility_schedule(self, since: dict | None = None) -> dict:
        """The fertility schedule the run ACTUALLY REALISED: ASFR, TFR, realised IBI (pure observer).

        ASFR is a rate per woman-YEAR and a step is a MONTH, so exposure is divided by 12. TFR is the sum of
        the single-year ASFRs — the synthetic-cohort measure, which is what Hill & Hurtado Tables 8.1/8.2
        state (8.031 forest) and so the only one comparable to the anchor. Like `life_table`, cumulative by
        default and differenceable via `since`.

        `factor_mean` and `factor_saturated` describe the fertility MULTIPLIER actually applied to women at
        risk. They exist because an energetic brake that never bites is indistinguishable from an absent one
        in every other diagnostic: `enable_energetic_fertility` read a reserve that re-saturated at the cap
        for ~99% of agents, and `enable_intake_fertility` replaced it without the replacement ever being
        measured. `factor_saturated` near 1.0 means the brake is decorative.
        """
        bi, ex = self.fert_births, self.fert_exposure
        hist = self.ibi_hist
        fsum, fn, fsat = self.fert_factor_sum, self.fert_factor_n, self.fert_factor_sat
        if since is not None:
            bi = [a - b for a, b in zip(bi, since["fert_births"])]
            ex = [a - b for a, b in zip(ex, since["fert_exposure"])]
            hist = [a - b for a, b in zip(hist, since["ibi_hist"])]
            fsum -= since["fert_factor_sum"]; fn -= since["fert_factor_n"]; fsat -= since["fert_factor_sat"]
        asfr: list[float] = []
        for i in range(LT_MAX_AGE_YR):
            wy = ex[i] / MONTHS_PER_YEAR
            asfr.append((bi[i] / wy) if wy > 0.0 else 0.0)
        n_ibi = sum(hist)
        med = mean = float("nan")
        if n_ibi:
            half, run = n_ibi / 2.0, 0
            for months, c in enumerate(hist):
                run += c
                if run >= half:
                    med = float(months)
                    break
            mean = sum(months * c for months, c in enumerate(hist)) / n_ibi
        return {"asfr": asfr, "tfr": sum(asfr),
                "births": sum(bi), "woman_years": sum(ex) / MONTHS_PER_YEAR,
                "ibi_median": med, "ibi_mean": mean, "ibi_n": n_ibi,
                "factor_mean": (fsum / fn) if fn else float("nan"),
                "factor_saturated": (fsat / fn) if fn else float("nan"), "factor_n": fn}

    def life_table_by_sex(self) -> dict:
        """e0 and e15 computed separately for females and males (pure observer).

        The model runs a SEX-SPLIT Siler — `_sex_split` gives females the higher infant term a1 and males the
        higher Gompertz a3, putting the crossover in adolescence as the Aché monograph reports — and nothing
        has ever checked that the realised split matches. A pooled life table cannot: it averages the two
        schedules and hides a sex-specific defect entirely. The sex GAP is the quantity to watch, since it is
        a structural prediction of the configuration rather than a free parameter.
        """
        def _tab(ex_arr, de_arr):
            l, out = [1.0], []
            for i in range(LT_MAX_AGE_YR):
                py = ex_arr[i] / MONTHS_PER_YEAR
                mi = (de_arr[i] / py) if py > 0 else 0.0
                qi = min(1.0, mi / (1.0 + 0.5 * mi)) if mi > 0 else 0.0   # clamp: see life_table()
                l.append(l[-1] * (1.0 - qi))
            def ex_at(x):
                if l[x] <= 0.0:
                    return float("nan")
                return sum(0.5 * (l[i] + l[i + 1]) for i in range(x, LT_MAX_AGE_YR)) / l[x]
            return ex_at(0), ex_at(15), l
        ex_m = [t - f for t, f in zip(self.lt_exposure, self.lt_exposure_f)]
        de_m = [t - f for t, f in zip(self.lt_deaths, self.lt_deaths_f)]
        f0, f15, lf = _tab(self.lt_exposure_f, self.lt_deaths_f)
        m0, m15, lm = _tab(ex_m, de_m)
        return {"e0_female": f0, "e0_male": m0, "e15_female": f15, "e15_male": m15,
                "e0_gap_f_minus_m": f0 - m0, "e15_gap_f_minus_m": f15 - m15,
                "exposure_py_female": sum(self.lt_exposure_f) / MONTHS_PER_YEAR,
                "exposure_py_male": sum(ex_m) / MONTHS_PER_YEAR}

    def cohort_fertility(self) -> dict:
        """COMPLETED parity of women past menopause — the cohort measure, against the synthetic TFR.

        `realised_tfr` is a SYNTHETIC-cohort rate: it sums current age-specific rates over a hypothetical
        woman who lives through today's schedule. Completed parity is what real women actually bore. The two
        agree only in a stationary population, so their DIVERGENCE is a direct read on whether the run is in
        steady state — which is exactly what nobody could see when the population ran away on 2026-08-14 and
        the synthetic TFR sat flat at 10.5 throughout.

        Scored on women past `menopause_months` because their parity is final; including younger women would
        mix completed with in-progress careers and read as a spurious decline.
        """
        cfg = self._demog
        meno = cfg.menopause_months if cfg is not None else 504
        done = [a for a in self.agent_list if a.sex == "female" and a.age >= meno]
        n = len(done)
        if not n:
            return {"completed_parity_mean": float("nan"), "completed_parity_med": float("nan"),
                    "n_completed": 0, "frac_parity_zero": float("nan")}
        par = sorted(int(getattr(a, "parity", 0)) for a in done)
        return {"completed_parity_mean": sum(par) / n,
                "completed_parity_med": float(par[n // 2]),
                "n_completed": n,
                # Childlessness is a real ethnographic quantity and a sensitive one: a pairing or fertility
                # mechanism that silently excludes a subgroup shows up here before it shows up in the mean.
                "frac_parity_zero": sum(1 for p in par if p == 0) / n}

    def vital_rates(self, since: dict | None = None) -> dict:
        """Crude birth and death rates, intrinsic growth, realised sex ratio at birth, mean age at first birth.

        WHY THESE AND NOT JUST `pop`. A population count says WHERE the model is; the flows say WHY. r read
        off two population counts also conflates growth with the sampling interval, which is how this arc
        differenced 2/3-of-run windows by hand for a week. CBR - CDR is the same number computed from the
        run's own exposure, so it cannot drift from the life table beside it.

        Cumulative by default; pass a `raw_demographic_counters()` mark as `since` for a period rate.

        Rates are per 1000 person-years, the demographic convention, so they compare directly to published
        crude rates. `r_pct_yr` is a percentage per year — the same units as the Lotka r used elsewhere.
        """
        bi, de, ex = self.fert_births, self.lt_deaths, self.lt_exposure
        bm, bf = self.births_male, self.births_female
        fbs, fbn = self.first_birth_age_sum, self.first_birth_n
        if since is not None:
            bi = [a - b for a, b in zip(bi, since["fert_births"])]
            de = [a - b for a, b in zip(de, since["lt_deaths"])]
            ex = [a - b for a, b in zip(ex, since["lt_exposure"])]
            bm -= since.get("births_male", 0); bf -= since.get("births_female", 0)
            fbs -= since.get("first_birth_age_sum", 0.0); fbn -= since.get("first_birth_n", 0)
        py = sum(ex) / MONTHS_PER_YEAR
        nb, nd = sum(bi), sum(de)
        cbr = (1000.0 * nb / py) if py > 0 else float("nan")
        cdr = (1000.0 * nd / py) if py > 0 else float("nan")
        tot_b = bm + bf
        return {"cbr": cbr, "cdr": cdr, "r_pct_yr": (cbr - cdr) / 10.0,
                "births": nb, "deaths": nd, "person_years": py,
                "srb_male_frac": (bm / tot_b) if tot_b else float("nan"),
                "births_male": bm, "births_female": bf,
                "age_first_birth_yr": (fbs / fbn / MONTHS_PER_YEAR) if fbn else float("nan"),
                "first_birth_n": fbn}

    def family_structure(self) -> dict:
        """Who has parents, and who never paired. Pure observer over the live population.

        TWO GAPS THIS FILLS, both requested 2026-08-13.

        JOINT ORPHANHOOD. `frac_motherless` and `frac_fatherless` are reported SEPARATELY, so a child that
        has lost BOTH is counted once in each and never as itself. That is the group with the highest hazard
        in Hill & Hurtado's Table 13.1 material (the R-74 orphan work found child mortality is
        orphan-CONDITIONED, x5.09 for a lost mother), so it is exactly the cell that must not be invisible.
        Scored over children only, since an adult's parents dying is not orphanhood.

        NEVER-PARTNERED. `frac_unpaired_adult` counts the CURRENTLY unpaired, which pools the widowed, the
        divorced and the never-married. Those are different phenomena: in foragers, near-universal marriage
        means never-partnered-by-30 should be close to zero, while widowhood is common. Pooling them makes a
        broken pairing mechanism indistinguishable from ordinary mortality.
        """
        cfg = self._demog
        adult_m = cfg.menarche_months if cfg is not None else 180
        pop = self.agent_list
        n = len(pop)
        nan = float("nan")
        if not n:
            return {k: nan for k in ("frac_both_parents_alive", "frac_one_parent_alive", "frac_double_orphan",
                                     "n_children", "frac_never_partnered_30", "frac_widowed_adult",
                                     "frac_partnered_adult", "n_adults_30")}
        # A MISSING LINK IS "UNKNOWN", NOT "DEAD" — and the first version of this method got that wrong.
        # `_father` is None whenever paternity was never assigned (the flag is off, or the child predates it),
        # and counting those as bereaved FABRICATES orphans: the smoke run reported 8.6% double-orphans that
        # were mostly children with no recorded father at all. `_orphan_status` has always had this right
        # (`m_dead = m is not None and not m.alive`), so this now follows it, and uses the same RISK SET the
        # existing frac_motherless/frac_fatherless use — children with at least one KNOWN parent link.
        kids = [a for a in pop if a.age < adult_m
                and not (getattr(a, "_mother", None) is None and getattr(a, "_father", None) is None)]
        both = one = none = 0
        for c in kids:
            m = getattr(c, "_mother", None); f = getattr(c, "_father", None)
            m_known, f_known = m is not None, f is not None
            m_dead = m_known and not m.alive
            f_dead = f_known and not f.alive
            dead = m_dead + f_dead
            known = m_known + f_known
            if dead == 0:
                both += 1                       # no KNOWN parent is dead
            elif dead < known:
                one += 1                        # one known parent dead, another known parent alive
            else:
                none += 1                       # every known parent is dead
        nk = len(kids)
        n_unknown = sum(1 for c in kids
                        if getattr(c, "_mother", None) is None or getattr(c, "_father", None) is None)
        # 30 yr, not menarche: by 30 a forager who was ever going to marry has. Reading it at 15 would score
        # the ordinary pre-marital years as a pairing failure.
        thirty = 30 * MONTHS_PER_YEAR
        ad30 = [a for a in pop if a.age >= thirty]
        never = sum(1 for a in ad30 if not getattr(a, "_ever_partnered", False))
        adults = [a for a in pop if a.age >= adult_m]
        def _paired(a):
            return (getattr(a, "_partner", None) is not None) or bool(getattr(a, "_wives", ()))
        wid = sum(1 for a in adults if getattr(a, "_ever_partnered", False) and not _paired(a))
        na = len(adults)
        return {"frac_both_parents_alive": (both / nk) if nk else nan,
                "frac_one_parent_alive": (one / nk) if nk else nan,
                "frac_double_orphan": (none / nk) if nk else nan,
                "n_children": nk,
                # COVERAGE, so the reader can see how much of the risk set rests on a partial link. A high
                # value here means the orphan fractions are computed on one parent for most children and the
                # "double" category is correspondingly under-observed — a caveat, not a defect.
                "frac_partial_parent_link": (n_unknown / nk) if nk else nan,
                "frac_never_partnered_30": (never / len(ad30)) if ad30 else nan,
                "n_adults_30": len(ad30),
                "frac_widowed_adult": (wid / na) if na else nan,
                "frac_partnered_adult": (sum(1 for a in adults if _paired(a)) / na) if na else nan}

    def starvation_profile(self) -> dict:
        """Compare the state of agents that STARVED against the state of the agents that lived (pure observer).

        This is the instrument the survivor-sampled diagnostics could not be. `compute_harvest_shares` divides
        a cell's yield S among its n occupants, so intake is set by LOCAL occupancy. The discriminating
        comparison is therefore `occ_at_death` against `occ_of_living`:

          occ_at_death >> occ_of_living  -> agents starve because they CROWD, and the map average is a
                                            survivor artefact. The fault is DISTRIBUTION.
          occ_at_death ~= occ_of_living  -> crowding is not it; the cells themselves are too poor, or the
                                            reserve is too thin to cross a trough. The fault is SUPPLY.

        `occ_of_living` is occupancy weighted BY AGENT, not by cell — an agent's experience of crowding is
        what its own cell holds, so a per-cell mean would understate it exactly where the agents are.
        """
        n = self.starv_events
        occ: dict = {}
        for a in self.agent_list:
            occ[a.pos] = occ.get(a.pos, 0) + 1
        live_n = len(self.agent_list)
        occ_live = (sum(occ[a.pos] for a in self.agent_list) / live_n) if live_n else float("nan")
        cells = len(occ)
        return {"starv_events": n,
                "occ_at_death": (self.starv_occ_sum / n) if n else float("nan"),
                "occ_of_living": occ_live,
                "age_at_death_yr": (self.starv_age_sum / n / MONTHS_PER_YEAR) if n else float("nan"),
                "intake_at_death": (self.starv_intake_sum / n) if n else float("nan"),
                "ema_at_death": (self.starv_ema_sum / n) if n else float("nan"),
                "fedres_at_death": (self.starv_fedres_sum / n) if n else float("nan"),   # reserve fraction the step before death
                "frac_acute": (self.starv_acute_n / n) if n else float("nan"),           # share of deaths that were one-step crashes
                "cells_occupied": cells,
                "mean_occ_per_cell": (live_n / cells) if cells else float("nan"),
                "starv_by_age": list(self.starv_by_age)}

    def raw_demographic_counters(self) -> dict:
        """A copy of every cumulative demographic counter, for differencing into a PERIOD rate later.

        Copies rather than references: a caller holding a live list would silently see it keep accumulating,
        and the resulting "period" table would be the cumulative one wearing a period's name.
        """
        return {"step": self.step_count,
                "lt_exposure": list(self.lt_exposure), "lt_deaths": list(self.lt_deaths),
                "lt_deaths_starv": list(self.lt_deaths_starv),
                "lt_deaths_senesc": list(self.lt_deaths_senesc),
                "fert_births": list(self.fert_births), "fert_exposure": list(self.fert_exposure),
                "ibi_hist": list(self.ibi_hist), "fert_factor_sum": self.fert_factor_sum,
                "fert_factor_n": self.fert_factor_n, "fert_factor_sat": self.fert_factor_sat}

    def demography(self, by: str | None = None) -> dict:
        """Demographic snapshot of the live population.

        `by=None`     → one marker dict for the whole population.
        `by="band"`   → {band_id: markers} (the F.3c affiliation — the social unit).
        `by="village"`→ {site: markers} for agents inside an active settlement's catchment, plus the
                        residual under key `None` (the mobile hinterland — NOT a village; kept visible
                        because a village-only view hides half the population, R-69's "shock hits the
                        hinterland while the storing village rides through").

        Population STOCK only. Flow rates (CBR/CDR, deaths by cause) are per-step counters — read
        `deaths_starv_this_step` / `deaths_senesc_this_step` / `deaths_orphan_this_step` /
        `births_this_step`, or the per-band tallies in `_band_starv_this_step`.
        """
        if by is None:
            return self._demog_markers(self.agent_list)
        groups: dict = {}
        if by == "band":
            for a in self.agent_list:
                groups.setdefault(a._group.band_id, []).append(a)
        elif by == "village":
            for a in self.agent_list:
                groups.setdefault(self._nearest_settlement(a.pos), []).append(a)
        else:
            raise ValueError(f"demography(by=): expected None | 'band' | 'village', got {by!r}")
        return {k: self._demog_markers(v) for k, v in groups.items()}

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

    def _rank_units(self) -> dict:
        """R-96 — agent → the COMMUNITY that grants and revokes its rank.

        The settlement when village-scale resentment is on (Leach's gumlao premises describe villages with
        headmen and councils), else the band. Shared by `_do_legitimacy`, `_do_delegitimation` and the
        diagnostics so all four cannot drift apart on what a community is."""
        vil = self._demog is not None and getattr(self._demog, "enable_village_resentment", False)
        out = {}
        for a in self.agent_list:
            if vil:
                site = self._nearest_settlement(a.pos)
                out[a] = ("v", site) if site is not None else ("b", a._group.band_id)
            else:
                out[a] = a._group.band_id
        return out

    def _rank_keys(self) -> dict:
        """R-96 — agent → the key under which its lineage's rank is held.

        GLOBAL mode (default): the lineage id, so a lineage is noble everywhere at once. LOCAL mode: the pair
        (community, lineage), so it is noble IN A PLACE. Polymorphic on purpose — every consumer indexes the
        same sets and dicts either way, so OFF is bit-exact rather than a parallel code path."""
        if self._demog is None or not getattr(self._demog, "enable_local_ascription", False):
            return {a: getattr(a, "_lineage", None) for a in self.agent_list}
        units = self._rank_units()
        return {a: (units[a], getattr(a, "_lineage", None)) for a in self.agent_list}

    def _do_legitimacy(self) -> None:
        """DM-F1 / R-86 — THE LEGITIMACY CHANNEL: how ACHIEVED success becomes ASCRIBED rank.

        TYPE **C (Conversion)** · UNIT **LINEAGE** (patriline, competing within a band) · INVARIANT **DEBITED**
        (the sacrifice SPENDS material) · ANCHOR [Flannery & Marcus 2012 ch.10, VERIFIED].

        Flannery's warning is that our elite layer's premise cannot produce hereditary rank: *"if feasting were
        all it took to produce hereditary inequality, there would have been no achievement-based societies left
        for anthropologists to study"* — feasting *"produced individual Big Men who had no way of bequeathing
        renown to their offspring."* R-83/R-84 measured exactly that (leaders 3.68× ahead, father-was-leader
        53–69%, no transmission), so the model is a CORRECT achievement-based society and needs a different
        mechanism for heredity.

        Friedman's endogenous scenario supplies it, and it is a REINTERPRETATION rather than an accumulation:
        success was not credited to labour but to ritual standing — *"they believed that one only obtained good
        harvests through proper sacrifices to the nats. The key shift in social logic was therefore from 'They
        must have pleased the nats' to 'They must be descended from higher nats than we are.'"* Once held to
        descend from the ruling spirits, the lineage controls the land and *"was also entitled to receive
        tribute from other lineages."*

        Implemented in three parts:
          1. **FEAST (debited).** Each lineage spends `legit_feast_frac` of its members' material on sacrifices.
          2. **STANDING (relative, and local).** Legitimacy is an EMA of the lineage's SHARE of its band's total
             feasting — Friedman's "most prestigious sacrifices" is a comparison among co-resident lineages, not
             an absolute. A share is in [0,1], so the stock is bounded by construction and the threshold is
             directly interpretable ("sustains more than half its band's ritual expenditure").
          3. **CONVERSION.** Above `legit_threshold` the lineage's members get a per-step multiplicative boost to
             `cred` — which is HERITABLE, so achieved standing becomes ascribed rank. The boost is a sustained
             force against the cred homeostat's restoring pull, so it reaches an equilibrium spread rather than
             compounding without bound.

        Off ⇒ returns before touching anything ⇒ bit-exact."""
        cfg = self._demog
        if cfg is None or not getattr(cfg, "enable_legitimacy", False):
            return
        ff = cfg.legit_feast_frac
        if ff <= 0.0:
            return
        # A FEAST IS AN EVENT, NOT A CONTINUOUS BLEED (2026-07-27). This spent `legit_feast_frac` of every
        # lineage's material EVERY STEP: at 0.25 that is ~97% of the durable stock per year. Measured over 900
        # steps the sacrifice drain was 740 BILLION against a tribute return of 1.1 billion — 673:1 — and a
        # standing stock of only 3.2 billion. The elite was therefore, by construction, the set of agents who
        # had burned their wealth to buy rank, which is why `noble_material_lift` sat at ~1.0 under every
        # other remedy tried (zero decay, no leveling, narrowed elite, return-on-capital).
        # The status side does NOT depend on the rate: legitimacy is an EMA of a lineage's SHARE of its band's
        # feasting, and a share is invariant to scaling everyone's spend. So the frequency was free for status
        # and decisive for wealth. Feasts are gatherings — sacrifices happen AT them — so the spend now fires
        # on the gathering cadence. Same class as R-75's divorce-rate bug: a per-event rate applied per step.
        # `feast_every` = 0 restores the old per-step behaviour for comparison.
        _fe = getattr(cfg, "feast_every", 0) or 0
        if _fe > 0 and (self.step_count % _fe) != 0:
            return
        # R-96: feasting, and the standing it buys, are reckoned WITHIN a community — the same community that
        # can later revoke the rank. Grouping and revocation must share a unit or a lineage can be ennobled by
        # one body and stripped by another.
        _local = getattr(cfg, "enable_local_ascription", False)
        _units = self._rank_units() if _local else None
        by_band: dict = {}
        for a in self.agent_list:
            lid = getattr(a, "_lineage", None)
            if lid is not None:
                unit = _units[a] if _local else a._group.band_id
                by_band.setdefault(unit, {}).setdefault(lid, []).append(a)

        alpha = cfg.legit_decay                       # EMA weight: legitimacy tracks long-run ritual standing
        rel_legit = getattr(cfg, "enable_relative_legitimacy", False)   # R-93: scale-free crossing test
        for unit, lins in by_band.items():
            spend, total = {}, 0.0
            guests = [a for ms in lins.values() for a in ms]
            for lid, ms in lins.items():
                s = 0.0
                for a in ms:
                    take = ff * a.material
                    if take > 0.0:
                        a.material -= take            # DEBITED — belief is bought, not asserted
                        s += take
                spend[lid] = s
                total += s
            if total <= 0.0:
                continue
            # A FEAST IS AN EXCHANGE, NOT A SINK. Flannery: the sponsor "could sponsor the most prestigious
            # sacrifices AND FEED THE MOST VISITORS" — the material goes to the guests. Destroying it instead
            # (the first cut) inflated the material Gini by ~0.18 through a pure drain, a confound that had
            # nothing to do with legitimacy. Conserved within the band ⇒ the X invariant holds here.
            per = total / len(guests)
            for a in guests:
                a.material += per
            self.feast_spend_this_step += total
            for lid, s in spend.items():
                share = s / total
                key = (unit, lid) if _local else lid
                if rel_legit:
                    # R-93: scale by how many lineages are actually competing here, so the stock is a RELATIVE
                    # share — 1.0 means "exactly what an average lineage contributed", independent of how many
                    # lineages the band happens to hold. Without this the mean share is 1/len(lins), so a fixed
                    # threshold silently stops discriminating once diversity falls below 1/threshold.
                    share *= len(lins)
                self._lineage_legit[key] = (1.0 - alpha) * self._lineage_legit.get(key, 0.0) + alpha * share

        thr = cfg.legit_rel_multiplier if rel_legit else cfg.legit_threshold
        cg = cfg.legit_cred_gain
        # THE RATCHET — this is the whole mechanism, and getting it wrong was the first two cuts' error.
        # Friedman's key shift is "from 'They must have PLEASED the nats' to 'They must be DESCENDED FROM higher
        # nats than we are.'" A decaying legitimacy stock that must be continually re-earned by feasting is the
        # FORMER — still achievement-based, and Flannery is explicit that achievement alone "produced individual
        # Big Men who had no way of bequeathing renown to their offspring." Measured: with a decaying stock,
        # father-was-leader stayed at baseline (59-67% vs 65%) at every gain up to 20.
        # So crossing the threshold ASCRIBES the lineage permanently: descent, once believed, is not contingent
        # on this year's harvest. `_lineage_ascribed` is the ratchet; the EMA above only decides who crosses.
        for lid, v in self._lineage_legit.items():
            if v > thr:
                self._lineage_ascribed.add(lid)
        # NB the ratchet is recorded BEFORE the cred-gain guard below: whether a lineage is believed to descend
        # from the nats is a fact about the society, not about how strongly we convert that belief into cred.
        # (First cut had it after the guard, so `n_ascribed` silently read 0 whenever legit_cred_gain was 0.)
        if cg <= 0.0 or thr >= 1.0:
            return

        # RELAXATION TOWARD A TARGET, not a compounding multiplier. The first cut multiplied cred by
        # (1 + cg·excess) every step; that is an unbounded force against the homeostat's restoring pull and it
        # WINS — measured cred Gini 0.968–0.988, i.e. one lineage holding essentially everything (the R-66
        # winner-take-all failure mode). Same lesson as R-81: a sustained multiplicative push beats a
        # contraction. Relaxing toward a target is bounded by construction.
        _keys = self._rank_keys()
        for a in self.agent_list:
            if _keys[a] in self._lineage_ascribed:
                a.cred += LEGIT_RELAX * ((1.0 + cg) - a.cred)
                self.legitimated_this_step += 1

    def _privilege_effect(self, ms, rkeys) -> float:
        """R-99 — how far this community's RANKED stand above its COMMONERS, in units of its own cred spread.

        ZERO WHEN THERE IS NO DISTINCTION, IN EITHER DIRECTION. No ranked lineage present is obviously flat; so
        is a community where EVERY lineage is ranked, because binary ascription cannot express a gradient among
        nobles. That second case is the R-89 degeneracy, and forcing 0.0 here closes it rather than leaving the
        back door open via a population-wide fallback — "nobility universal, i.e. meaningless" (R-87's own note).

        SHARED by `_do_delegitimation` (resentment from below) and the leader-weight gate (organisational
        capacity above), deliberately: they are two consequences of ONE measured quantity, and a second copy
        would drift. Scale-free by construction, so it carries no hidden denominator (charter D15)."""
        asc = [a for a in ms if rkeys[a] in self._lineage_ascribed]
        oth = [a for a in ms if rkeys[a] not in self._lineage_ascribed]
        if not asc or not oth:
            return 0.0
        n1, n2 = len(asc), len(oth)
        s1 = sum(a.cred for a in asc); s2 = sum(a.cred for a in oth)
        q1 = sum(a.cred * a.cred for a in asc); q2 = sum(a.cred * a.cred for a in oth)
        nv = n1 + n2
        mu = (s1 + s2) / nv
        var = max(0.0, (q1 + q2) / nv - mu * mu)     # clamp: cancellation can go slightly negative
        sd = var ** 0.5
        if sd <= 1e-9:
            return 0.0                                # uniform community: no DISCERNIBLE privilege
        return min(max(0.0, s1 / n1 - s2 / n2) / sd, RESENT_EFFECT_CAP)

    def _do_lineage_split(self) -> None:
        """R-92 — LINEAGE SEGMENTATION: an existing named line splits into two real sub-clades.

        TYPE **N (Novelty)** · UNIT **LINEAGE** · INVARIANT conserves membership exactly (every agent keeps a
        lineage; the two segments partition the old one) · ANCHOR the RATE is calibrated against
        [Hill et al. 2011, FILED] via MODEL_SPEC §4.8.8 (~7 lineages/band, dominant-lineage share 0.38).

        WHY THIS REPLACES R-90's PER-BIRTH BRANCHING. That minted SINGLETONS, and a lineage of one usually dies,
        so it produced a churn of ephemeral names: n_lineages rose 5→32 while eff_lineages FELL 3.4→1.8 and
        top_share ROSE 0.42→0.73. Count up, substance down. Real haplogroup trees segment — the sub-clade
        inherits an existing body of members, so both halves persist and both stay spread across bands, which is
        what per-band diversity actually needs.

        THE CLEAVAGE IS GENEALOGICAL, not random. A random half would not be a descent group at all, and it
        would put close kin into different lineages — which matters because `_lineage` is also the patriclan
        EXOGAMY unit (`exogamy_degree="lineage"`). The cleavage is the heritable `_subclan` tag: inherited
        patrilineally exactly like `_lineage`, so agents sharing a tag ARE a descent group by construction.

        WHY NOT WALK ANCESTOR CHAINS, which was the first cut and does not work. Splitting off "the live
        patrilineal descendants of an apical ancestor" is the textbook definition of a sub-clade, but it is not
        computable here: MEASURED, live `_father` chains in this model reach a maximum depth of 2 (median 1) even
        after 400 steps, because a chain terminates at the first ancestor born without an assigned father and
        early births largely lack one (father-link rate 19% at step 80, rising to 74% by step 400). Deep ancestry
        exists only in the offline genealogy CSV, never in memory. So the sub-clade has to be CARRIED as an
        inherited tag rather than reconstructed on demand — which is also, conveniently, exactly what a
        Y-haplogroup label is.

        HAZARD SCALES WITH SIZE (`rate·n`) — the Yule process, which is what generates the skewed lineage-size
        distributions real haplogroup data shows. It applies no CEILING: a big lineage segments more often, but
        nothing bounds how large it may become, so `top_share` remains a free measurement. This is the specific
        distinction from the size-TRIGGERED segmentation rejected in R-90, which would have made `top_share` an
        artifact of the trigger and destroyed the statistic T-9 compares against Zerjal 2003 / Yan 2014.

        DEGENERATE SPLITS ARE SKIPPED, not forced: if either side would fall below `lineage_split_min_segment`
        the draw is spent and nothing happens. That both avoids re-creating the singleton problem and makes the
        apical ancestor effectively selected from mid-tree, without needing to rank candidates.

        Off (or rate 0) ⇒ returns before any RNG draw ⇒ bit-exact."""
        cfg = self._demog
        if cfg is None or not getattr(cfg, "enable_lineage_split", False):
            return
        rate = cfg.lineage_split_rate
        if rate <= 0.0:
            return
        min_seg = cfg.lineage_split_min_segment

        groups: dict = {}
        for a in self.agent_list:
            lid = getattr(a, "_lineage", None)
            if lid is not None:
                groups.setdefault(lid, []).append(a)

        for lid, ms in sorted(groups.items()):          # sorted ⇒ deterministic iteration order
            n = len(ms)
            if n < 2 * min_seg:
                continue
            if self.random.random() >= min(1.0, rate * n):
                continue
            subs: dict = {}
            for x in ms:
                subs.setdefault(getattr(x, "_subclan", None), []).append(x)
            if len(subs) < 2:
                continue                                 # one undivided descent group — nothing to segment along
            # The LARGEST sub-branch that leaves both sides viable secedes. Largest-first is the ethnographic
            # shape (a lineage segments along its major cleavage, not a random twig) and it is what makes the
            # daughter line born big enough to persist — the whole point of the R-90 correction.
            for _, seg in sorted(((len(v), k) for k, v in subs.items()), reverse=True):
                seg = subs[seg]
                if len(seg) < min_seg or n - len(seg) < min_seg:
                    continue
                new_id = self._next_lineage_id
                self._next_lineage_id += 1
                for x in seg:
                    x._lineage = new_id
                self.lineage_splits_this_step += 1
                break                                    # one segmentation per lineage per step

    def _do_delegitimation(self) -> None:
        """R-87 / DM-F1 stage 2 — the gumsa → gumlao COLLAPSE, and the H-CYCLES test.

        TYPE **C (Conversion, reverse)** · UNIT **BAND** · INVARIANT changes only ascription + cred, never a
        conserved quantity · ANCHOR [Leach via Flannery ch.10, VERIFIED].

        WHY IT IS REQUIRED, not optional. R-86's ratchet works — father-was-leader 76% vs Hayden's 75% — but a
        ratchet with no reverse has no equilibrium: `ascribed_frac_pop` runs to 0.70–0.85 and nobility becomes
        universal, i.e. meaningless. The model derived the need for this before the ethnography was consulted
        for it.

        THE MECHANISM IS A LAG, and that is the whole point. Boehm-style leveling (R-82) corrects excess WITHIN
        THE STEP, which is exactly why it caps inequality instead of overshooting it. Here, resentment
        ACCUMULATES: prestige-seeking "only increased their followers' resentment and hastened their overthrow",
        and the result is that hereditary inequality "lasted for A FEW GENERATIONS, and then collapsed." So
        `resent_alpha` is a generational EMA (~20 yr), and it is the delayed negative feedback that
        MECHANISM_CHARTER §5 identifies as the missing ingredient for oscillation — the model's three failures
        to cycle (DE-14) all being instantaneous-feedback systems.

        WHY PER BAND. Leach's gumlao premise 1 is "All lineages are considered equal" — the reversion is a
        whole-community flip, not one family losing face. A per-lineage collapse would also average away in
        aggregate; a synchronized one can actually show as a cycle.

        HYSTERESIS. After a flip the band's lineages must rebuild legitimacy from zero (~50+ steps of feasting)
        and resentment restarts, so a band cannot chatter between modes.

        R-89 FIX. A band that random-walks to 100% ascribed has no live commoner ("oth") left to found privilege
        on, and the original code let resentment merely decay in that case — a ONE-WAY DOOR, since ascription
        only grows (R-86) and nothing else could ever push the band back out. Measured: a 4000-step pilot hit
        this within 2625 steps and then sat pinned at ascribed_frac=1.0 for the remaining 34% of the run (R-89).
        Fix: fall back to the population-wide commoner mean when a band has none of its own — the wider society
        is still a real point of comparison even for a village that has gone entirely gumsa (Leach's Kachin
        Hills were never uniformly ranked). Bands that still have live commoners are unaffected byte-for-byte.

        Off ⇒ returns before touching anything ⇒ bit-exact."""
        cfg = self._demog
        if cfg is None or not getattr(cfg, "enable_delegitimation", False):
            return
        alpha = cfg.resent_alpha
        rel_res = getattr(cfg, "enable_relative_resentment", False)      # R-94: effect-size privilege
        acc = getattr(cfg, "enable_resentment_accumulator", False)       # R-95: build up, do not merely track
        ytr = cfg.resent_years_to_revolt
        thr = cfg.resent_effect_threshold if rel_res else cfg.resent_threshold
        ref = cfg.resent_privilege_ref

        # R-95: WHO HOLDS THE GRUDGE. Default: the band — but R-88 measured band lifetime at 10.2 yr median
        # against a grudge needing 700-1600 yr to mature, so the memory outlived its container by ~40-100x and
        # band fission reset it to zero. Leach's gumlao premises describe VILLAGES (autonomous, with headmen and
        # councils), not 25-person residential bands. Keyed by SETTLEMENT SITE, following R-71's precedent
        # exactly: the place remembers while its members churn. Agents outside any settlement keep the band.
        vil = getattr(cfg, "enable_village_resentment", False)
        rkeys = self._rank_keys()                # R-96: rank is held per community when local ascription is on
        members: dict = {}
        pop_oth_cred = []
        for a in self.agent_list:
            if vil:
                site = self._nearest_settlement(a.pos)
                key = ("v", site) if site is not None else ("b", a._group.band_id)
            else:
                key = a._group.band_id
            members.setdefault(key, []).append(a)
            if rkeys[a] not in self._lineage_ascribed:
                pop_oth_cred.append(a.cred)
        # R-89: population-wide commoner baseline, used only when a band has ascribed members but none of its
        # own commoners left. Ultimate fallback (no commoner alive anywhere) is the model's own default cred.
        pop_m_o = (sum(pop_oth_cred) / len(pop_oth_cred)) if pop_oth_cred else 1.0
        # R-94: population fallback SUMS, computed once per step and reused by every band that has no
        # commoners of its own — see the perf note in the effect-size branch below.
        pop_oth_n = len(pop_oth_cred)
        pop_oth_s = sum(pop_oth_cred)
        pop_oth_q = sum(v * v for v in pop_oth_cred)
        if pop_oth_n == 0:
            pop_oth_n, pop_oth_s, pop_oth_q = 1, 1.0, 1.0        # matches the pop_m_o=1.0 ultimate fallback

        for bid, ms in members.items():
            asc = [a for a in ms if rkeys[a] in self._lineage_ascribed]
            oth = [a for a in ms if rkeys[a] not in self._lineage_ascribed]
            if not asc:
                # no ranked lineage in this band ⇒ nothing to resent; let it cool
                self._band_resentment[bid] = self._band_resentment.get(bid, 0.0) * (1.0 - alpha)
                continue
            # PRIVILEGE = how far the ascribed stand above the commoners on the heritable facet. This is what
            # ascription actually confers, so it is what gets resented.
            m_a = sum(a.cred for a in asc) / len(asc)
            m_o = (sum(a.cred for a in oth) / len(oth)) if oth else pop_m_o
            if rel_res:
                # R-94: privilege as an EFFECT SIZE — the gap in units of the band's OWN spread. Scale-free, so
                # it does not care whether cred sits near 1 or near 11, which is exactly what broke the ratio
                # form when R-93 turned ascription from universal into a minority. Threshold is then anchorable
                # on Cohen (0.8 = "large") rather than invented.
                # POOLED SPREAD FROM RUNNING SUMS, never by materialising the list. The first cut rebuilt
                # `asc + pop_oth_cred` per band whenever a band had no commoners of its own — O(pop) per band
                # per step, i.e. ~1.4M operations a step at campaign scale, and it made the run 3-4x slower at a
                # LOWER population. The population sums are hoisted above and reused.
                n1 = len(asc)
                s1 = sum(a.cred for a in asc)
                q1 = sum(a.cred * a.cred for a in asc)
                if oth:
                    n2 = len(oth)
                    s2 = sum(a.cred for a in oth)
                    q2 = sum(a.cred * a.cred for a in oth)
                else:
                    n2, s2, q2 = pop_oth_n, pop_oth_s, pop_oth_q
                nv = n1 + n2
                mu = (s1 + s2) / nv
                var = max(0.0, (q1 + q2) / nv - mu * mu)     # clamp: catastrophic cancellation can go slightly <0
                sd = var ** 0.5
                # sd≈0 means the band is uniform: no DISCERNIBLE privilege to resent, whatever the means say.
                priv = 0.0 if sd <= 1e-9 else min(max(0.0, (m_a - m_o) / sd), RESENT_EFFECT_CAP)
            else:
                priv = 0.0 if m_o <= 0.0 else max(0.0, (m_a - m_o) / m_o) / ref
            # R-95: ACCUMULATE, as this mechanism's own docstring has always claimed it does. An EMA TRACKS —
            # it converges to whatever it is fed, so a threshold at or above the typical privilege can never be
            # crossed at ANY horizon (measured R-94: the grudge rose to 0.796 against a threshold of 0.800 and
            # stopped, 1 revolt in 3000 years). Accumulating makes TIME-TO-REVOLT the anchored quantity — which
            # is Leach's actual claim, "a few generations" — and retires the threshold as a free parameter:
            # it is fixed at 1.0, because `resent_years_to_revolt` already sets the scale. Privilege scales the
            # rate, so twice the gap boils over in half the time.
            if acc:
                r = self._band_resentment.get(bid, 0.0) + priv / ytr
                fired = r >= 1.0
            else:
                r = (1.0 - alpha) * self._band_resentment.get(bid, 0.0) + alpha * priv
                fired = r >= thr
            if fired:
                # THE REVERSION. Every lineage present loses ascription; the band is gumlao again.
                # R-96: strip only THIS community's rank. Under the global set this discarded the lineage
                # everywhere, so one village's revolt de-ranked it in every other village — measured R-95 at
                # ~7% of all lineages per revolt, which annihilated nobility instead of cycling it.
                for a in ms:
                    self._lineage_ascribed.discard(rkeys[a])
                    self._lineage_legit.pop(rkeys[a], None)
                self._band_resentment[bid] = 0.0
                self.reversions_this_step += 1
            else:
                self._band_resentment[bid] = r

        if vil:                                  # R-95: forget the grudge of a village that no longer exists,
            live = set(members)                  # exactly as R-71 forgets a dissolved site's remembered hardship
            for k in list(self._band_resentment):
                if k not in live:
                    self._band_resentment.pop(k, None)
        if getattr(cfg, "enable_local_ascription", False):
            # R-96: and forget the RANK of a community that no longer exists, or the sets grow without bound
            # across a long campaign as villages come and go.
            livek = set(rkeys.values())
            self._lineage_ascribed.intersection_update(livek)
            for k in list(self._lineage_legit):
                if k not in livek:
                    self._lineage_legit.pop(k, None)

    def gumsa_state(self) -> dict:
        """R-87 diagnostic: the ranked/egalitarian regime split. `frac_gumsa` is the fraction of bands holding at
        least one ascribed lineage — the series whose oscillation H-CYCLES predicts. Pure observer."""
        if self._demog is None or not getattr(self._demog, "enable_legitimacy", False):
            return {"n_bands": 0, "frac_gumsa": 0.0, "mean_resentment": 0.0, "max_resentment": 0.0}
        members: dict = {}
        for a in self.agent_list:
            members.setdefault(a._group.band_id, []).append(a)
        if not members:
            return {"n_bands": 0, "frac_gumsa": 0.0, "mean_resentment": 0.0, "max_resentment": 0.0}
        rk = self._rank_keys()
        ranked = sum(1 for ms in members.values()
                     if any(rk[a] in self._lineage_ascribed for a in ms))
        rs = [self._band_resentment.get(b, 0.0) for b in members]
        return {
            "n_bands": len(members),
            "frac_gumsa": ranked / len(members),
            "mean_resentment": sum(rs) / len(rs),
            "max_resentment": max(rs),
        }

    def legitimacy(self) -> dict:
        """R-86 diagnostic: the per-lineage legitimacy stock. `n_legit` counts lineages over the threshold —
        Friedman's "descended from higher nats". Pure observer."""
        if self._demog is None or not getattr(self._demog, "enable_legitimacy", False):
            return {"n_lineages": 0, "n_legit": 0, "n_ascribed": 0, "ascribed_frac_pop": 0.0, "mean": 0.0, "max": 0.0, "legit_frac_pop": 0.0}
        rk = self._rank_keys()                   # R-96: a key is a lineage id, or (community, lineage) when local
        live = set(rk.values())
        vals = [v for k, v in self._lineage_legit.items() if k in live]
        thr = self._demog.legit_threshold
        over = {k for k, v in self._lineage_legit.items() if v > thr and k in live}
        pop = len(self.agent_list)
        asc = {k for k in self._lineage_ascribed if k in live}
        return {
            "n_lineages": len(vals),
            "n_legit": len(over),
            "n_ascribed": len(asc),
            "ascribed_frac_pop": (sum(1 for a in self.agent_list if rk[a] in asc) / len(self.agent_list))
                                 if self.agent_list else 0.0,
            "mean": (sum(vals) / len(vals)) if vals else 0.0,
            "max": max(vals) if vals else 0.0,
            "legit_frac_pop": (sum(1 for a in self.agent_list
                                   if getattr(a, "_lineage", None) in over) / pop) if pop else 0.0,
        }

    def _maintain_leader_office(self) -> None:
        """R-84 CHALLENGE-SUCCESSION — leadership as a TENURED OFFICE, and the two ways it is lost.

        THE DEFECT: `band_leaders()` recomputed argmax(cred·prowess) every step, so there was no incumbency, no
        tenure, and a leader was never *removed* — he merely stopped being the maximum. The ethnography is the
        reverse: leadership is HELD, and lost to a SANCTION.

        ANCHOR [Boehm 1993 Table I, VERIFIED — columns counted across the 48-society survey]: DESERTION 17 vs
        DEPOSITION 9. The commonest end of a bad leader is that his following WALKS AWAY, not a challenge-and-
        defeat duel — so deposition is the MINORITY channel here (`office_deposition_share` = 9/26). The two
        TRIGGERS come from Boehm's 47 coded motivations: OVERREACH ("dominating others as leader" 14 + "lack of
        generosity or monopolizing resources" 5 = 19) and FAILURE TO DELIVER ("ineffectiveness, partiality, or
        unresponsiveness in a leadership role" 10) ⇒ `office_overreach_weight` = 19/29.

        SUCCESSION on the holder's death is two regimes [Sahlins 1972:209]: the Nootka chief's position is
        "ascribed by right of chiefly due" so "centricity is built into the structure" and the office outlives
        him; the Siuai big-man's following is "an achievement ... and the whole structure will as such dissolve
        with the demise of the pivotal big-man" (`succession_dissolve`).

        THE LOOP: overreach is read off the leader's own `material` relative to his band — exactly what
        `leader_share_frac` inflates. A greedier levy raises the sanction hazard on the man taking it.
        Off ⇒ returns before any RNG draw ⇒ bit-exact."""
        cfg = self._demog
        if cfg is None or not getattr(cfg, "enable_leader_office", False):
            return
        members: dict[int, list] = {}
        for a in self.agent_list:
            members.setdefault(a._group.band_id, []).append(a)
        live = {a.unique_id: a for a in self.agent_list}
        merit = lambda a: a.cred * getattr(a, "prowess", 1.0)
        margin, dep_p = cfg.office_challenge_margin, cfg.office_deposition_share
        w_over, gain, dissolve = cfg.office_overreach_weight, cfg.office_grievance_gain, cfg.succession_dissolve
        # R-103e legitimacy EXEMPTION from wealth-leveling (Flannery ch.16 / Friedman). OFF ⇒ `_exempt` stays a
        # no-op and this is bit-exact. ON ⇒ an ASCRIBED leader's material-overreach is scaled by (1-frac); rank
        # keys are computed ONCE here, not per band.
        _exempt_on = getattr(cfg, "enable_noble_leveling_exemption", False)
        _exempt_frac = getattr(cfg, "noble_exemption_frac", 1.0) if _exempt_on else 0.0
        _exempt_rk = self._rank_keys() if _exempt_on else None

        # CARRY THE OFFICE WITH THE MAN. band_ids churn on every fusion/fission, so an office keyed to the BAND
        # is vacated constantly by bookkeeping rather than by politics — measured: tenure capped at ~4 yr even
        # with sanctions off, i.e. the churn, not death, was ending careers. A leader whose band merged or split
        # has not stopped being a leader; he holds office in whatever band he now sits in (first claim wins; a
        # collision between two carried leaders is settled by the ordinary challenge below). Tenure is therefore
        # clocked on the MAN (`_office_since` keyed by uid), which is also what "held office until he died" means.
        carried: dict[int, int] = {}
        holders = [live[u] for u in self._band_office.values() if u in live]
        holders.sort(key=merit, reverse=True)             # a COLLISION (two leaders fused into one band) is
        for a in holders:                                 # settled by MERIT — not by dict order, which was
            if a._group.band_id not in carried:           # ending 106 of 135 tenures as pure bookkeeping
                carried[a._group.band_id] = a.unique_id
        still = set(carried.values())
        for uid, since in list(self._office_since.items()):
            if uid not in still:                          # died, or lost a collision ⇒ his tenure closes here
                self._tenures_closed.append(self.step_count - since)
                self._office_end["death" if live.get(uid) is None else "collision"] += 1
                del self._office_since[uid]
        self._band_office = carried

        adult = cfg.menarche_months                       # the model's producer-age threshold (as §prod-credit)
        for bid in sorted(members):                       # deterministic order ⇒ reproducible RNG stream
            ms = [x for x in members[bid] if x.age >= adult]   # ELIGIBILITY: office is held by ADULTS. Without
            if not ms:                                    # this a high-cred CHILD could hold office — measured
                continue                                  # mean leader age 23.5 yr vs adult mean 34.1.
            uid = self._band_office.get(bid)
            inc = live.get(uid) if uid is not None else None
            if inc is not None and inc.age < adult:
                inc = None                                # (cannot arise once seated, but keeps the invariant)
            if inc is None:
                cand = max(ms, key=merit)
                if dissolve:
                    # BIG-MAN REGIME (Sahlins' Siuai): the following was built by ONE man's generosity and does
                    # not transfer. A successor must stand clear of his NEAREST RIVAL by `margin` — where two
                    # contenders are close the band simply stays leaderless, which is the ethnographic
                    # interregnum. (Against the band MEAN this bar is trivially cleared by the max of ~25 draws.)
                    rivals = sorted((merit(x) for x in ms if x is not cand), reverse=True)
                    if not rivals or rivals[0] <= 0.0 or merit(cand) < (1.0 + margin) * rivals[0]:
                        continue                          # no one stands clear ⇒ band stays LEADERLESS
                self._band_office[bid] = cand.unique_id
                self._office_since[cand.unique_id] = self.step_count
                self._ever_leader.add(cand.unique_id)
                _cl = getattr(cand, '_lineage', None)
                self._lineage_office_count[_cl] = self._lineage_office_count.get(_cl, 0) + 1
                continue

            others = [x for x in ms if x is not inc]
            if not others:
                continue
            # OVERREACH (Boehm 19/29) — how far the leader's own durable holding stands above his band's norm.
            mo = sum(x.material for x in others) / len(others)
            over = 0.0 if mo <= 0.0 else (inc.material - mo) / mo
            over = 0.0 if over < 0.0 else (1.0 if over > 1.0 else over)
            if _exempt_rk is not None and _exempt_rk.get(inc) in self._lineage_ascribed:
                over *= (1.0 - _exempt_frac)      # R-103e: a legitimate noble's accumulation is HIS BY RIGHT
            # FAILURE TO DELIVER (Boehm 10/29) — the band's own hardship is what a leader is judged on. NOT
            # exempted: a noble is still deposed for famine, only his WEALTH ceases to be a grievance.
            ineff = min(self._band_starv_ema.get(bid, 0.0), 1.0)
            p = gain * (w_over * over + (1.0 - w_over) * ineff)
            if p <= 0.0:
                continue
            if self.random.random() >= min(p, 1.0):
                continue
            if self.random.random() < dep_p:
                # DEPOSITION (the minority channel): a challenger must clear the incumbent by `margin`, so a
                # challenge can FAIL and the incumbent survives it — "until he dies or is challenged AND
                # DEFEATED". Attempts are counted separately from successes: Boehm's 9:17 is the ratio of
                # sanctions ATTEMPTED (what a society practises), not of leaders actually unseated.
                self.challenges_this_step += 1
                chal = max(others, key=merit)
                if merit(chal) > (1.0 + margin) * merit(inc):
                    since = self._office_since.pop(inc.unique_id, None)
                    if since is not None:
                        self._tenures_closed.append(self.step_count - since)
                    self._band_office[bid] = chal.unique_id
                    self._office_since[chal.unique_id] = self.step_count
                    self._ever_leader.add(chal.unique_id)
                    _hl = getattr(chal, '_lineage', None)
                    self._lineage_office_count[_hl] = self._lineage_office_count.get(_hl, 0) + 1
                    self._office_end["deposed"] += 1
                    self.depositions_this_step += 1
            else:
                # DESERTION (the MAJORITY channel): a follower walks away rather than unseat him — he joins the
                # nearest other band ("an entire dissatisfied lineage might simply go away"), or founds his own.
                quitter = self.random.choice(others)
                qx, qy = quitter.pos
                pool = [b for b in members if b != bid and members[b]]
                if pool:
                    def _cd2(b):
                        g = members[b]
                        cx = sum(x.pos[0] for x in g) / len(g); cy = sum(x.pos[1] for x in g) / len(g)
                        return (cx - qx) ** 2 + (cy - qy) ** 2
                    nb = min(pool, key=_cd2)
                    members[nb].append(quitter)
                else:
                    nb = self._next_band_id; self._next_band_id += 1
                    members[nb] = [quitter]
                quitter._group.band_id = nb
                members[bid].remove(quitter)
                self.desertions_this_step += 1

    def leader_tenure(self) -> dict:
        """R-84 diagnostic: how long leaders actually HOLD office. `mean`/`median` are over completed tenures
        (steps ⇒ months); `open_mean` covers sitting incumbents; `vacant` counts bands with no office-holder
        (only non-zero under `succession_dissolve` — Sahlins' big-man structure that dissolved with its man).
        Pure observer."""
        if self._demog is None or not getattr(self._demog, "enable_leader_office", False):
            return {"n_closed": 0, "mean": 0.0, "median": 0.0, "mean_years": 0.0, "open_mean": 0.0,
                    "n_bands": 0, "n_held": 0, "vacant": 0, "father_was_leader": float("nan")}
        closed = list(self._tenures_closed)
        bids = {a._group.band_id for a in self.agent_list}
        sitting = set(self._band_office.values())
        open_t = [self.step_count - s for u, s in self._office_since.items() if u in sitting]
        held = len([b for b in self._band_office if b in bids])
        srt = sorted(closed)
        # HAYDEN 1995 [VERIFIED]: "About 75% of New Guinea Entrepreneur Big Men had fathers that were also Big
        # Men." The office is NOT inherited here — so any father-son continuity must EMERGE from the heritable
        # status capital (cred) that wins it, which is precisely Hayden's mechanism (he transmits moka partners
        # and wives, not the position). This is the validation target, not an input.
        sons = [a for a in self.agent_list if a.unique_id in self._ever_leader
                and getattr(a, "_father", None) is not None]
        fwl = (sum(1 for a in sons if a._father.unique_id in self._ever_leader) / len(sons)) if sons else float("nan")
        seated = set(self._band_office.values())
        ages = [a.age / 12.0 for a in self.agent_list if a.unique_id in seated]
        return {
            "father_was_leader": fwl,
            "n_scored": len(sons),
            "ends": dict(self._office_end),
            "leader_age": (sum(ages) / len(ages)) if ages else 0.0,
            "n_closed": len(closed),
            "mean": (sum(closed) / len(closed)) if closed else 0.0,
            "median": (srt[len(srt) // 2]) if srt else 0.0,
            "mean_years": (sum(closed) / len(closed) / 12.0) if closed else 0.0,
            "open_mean": (sum(open_t) / len(open_t)) if open_t else 0.0,
            "n_bands": len(bids),
            "n_held": held,
            "vacant": len(bids) - held,
        }

    def leadership(self) -> dict:
        """R-101 — WHO rules, and whether office runs in families. Pure observer.

        Built because the campaign could report `leader_tenure_yr` but nothing about the ORIGINS of leaders, so
        no post-hoc question about dynastic capture of office was answerable from a finished run.

          office_lineages     distinct lineages currently holding a band office
          office_top_share    largest lineage's share of those offices — dynastic CAPTURE of office, which is a
                              different thing from `lin_top_share` (share of PEOPLE): a small lineage can hold
                              most offices, and that is precisely the interesting case
          office_dynastic     share of current leaders whose lineage has taken office MORE THAN ONCE — office
                              running in families rather than individuals. Counted, not set-membership: "has
                              held office before" is true by construction for a sitting leader and could only
                              ever report 1.0
          office_repeat_lin   share of offices held by lineages holding more than one simultaneously
        """
        leaders = self.band_leaders()
        if not leaders:
            return {"n_leaders": 0, "office_lineages": 0, "office_top_share": 0.0,
                    "office_dynastic": 0.0, "office_repeat_lin": 0.0}
        lins = [getattr(a, "_lineage", None) for a in leaders.values()]
        n = len(lins)
        c = Counter(lins)
        cnt = self._lineage_office_count
        return {
            "n_leaders": n,
            "office_lineages": len(c),
            "office_top_share": round(c.most_common(1)[0][1] / n, 3),
            "office_dynastic": round(sum(1 for l in lins if cnt.get(l, 0) > 1) / n, 3),
            "office_repeat_lin": round(sum(v for v in c.values() if v > 1) / n, 3),
        }

    def band_leaders(self) -> dict[int, "BaseAgent"]:
        """Public diagnostic (Stage 1 leader coherence): map each live band_id (the affiliation `_group.band_id`,
        NOT the spatial `bands()` grouping) to its leader. Used by the leader-coherence benchmark to identify —
        and, in a controlled experiment, force-remove — a band's leader at a scripted step (set `.alive = False`;
        the model's own death-pruning cleans it up next `step()`), and to track leader-identity turnover.

        With `enable_leader_office` (R-84) this returns the sitting OFFICE-HOLDER, and a band whose office is
        VACANT is simply absent from the map — so a dissolved big-man following levies nothing. Without it, the
        legacy behaviour: the current highest cred·prowess member, recomputed fresh every step."""
        members: dict[int, list] = {}
        for a in self.agent_list:
            members.setdefault(a._group.band_id, []).append(a)
        if self._demog is not None and getattr(self._demog, "enable_leader_office", False):
            live = {a.unique_id: a for a in self.agent_list}
            out: dict[int, "BaseAgent"] = {}
            for bid in members:
                uid = self._band_office.get(bid)
                inc = live.get(uid) if uid is not None else None
                if inc is not None and inc._group.band_id == bid:
                    out[bid] = inc
            return out
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
        # R-90: the PER-BAND lineage composition. It was described as the read-out for a "FILED Hill 2011
        # target (~7 lineages/band, dominant-lineage share 0.38)" — **RETRACTED 2026-08-06: Hill et al.
        # 2011 contains no lineage data whatsoever** (Addendum 28). The DIAGNOSTIC is fine and still
        # measured on the right unit; it simply has no anchor to be scored against.
        # UNIT: the AFFILIATION band (`_group.band_id`), the same unit R-25 validated on — NOT the spatial
        # `bands()` partition (D6: the unit is part of the statistic). Bands of 1 are excluded from the
        # dominant-share mean, where the share is trivially 1.0 and would bias it upward.
        by_band: dict = {}
        for a in al:
            by_band.setdefault(a._group.band_id, []).append(a)
        lpb, doms = [], []
        for ms in by_band.values():
            lc = Counter(getattr(a, "_lineage", None) for a in ms)
            lpb.append(len(lc))
            if len(ms) > 1:
                doms.append(lc.most_common(1)[0][1] / len(ms))
        return dict(n_lineages=len(groups), top_share=round(sizes[0] / pop, 3),
                    size_gini=round(_gini(sizes), 3), eff_lineages=round(eff, 1), top=rows,
                    lineages_per_band=round(float(np.mean(lpb)), 2) if lpb else 0.0,
                    dom_lineage_share=round(float(np.mean(doms)), 3) if doms else 0.0)

    def settlements(self) -> dict:
        """Per-settlement panel (campaign — urban hierarchy + lifespans). For each maintained settlement site with
        live occupants: count, society (dominant band's morph), catchment yield, mean cred, dominant lineage.
        Aggregate rank-size: primate_ratio (largest ÷ 2nd), zipf_slope (OLS of ln size vs ln rank; ≈ −1 = Zipf),
        median/max. `frac_resident` = the share of the WHOLE population living on a settlement site — the direct
        measure of how sedentary the run is, and the one distinguishing "many people, no settlements" (the
        model still calls that pop 0 residents) from "few people, mostly settled". Pure observer."""
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
        total = len(self.agent_list)
        return dict(n=len(panel), median=int(np.median(sizes)), max=sizes[0], primate_ratio=primate,
                    zipf_slope=round(zipf, 2) if zipf is not None else None,
                    frac_resident=round(sum(sizes) / total, 3) if total else 0.0,
                    panel=sorted(panel, key=lambda q: q["n"], reverse=True))

    def settlement_clusters(self) -> dict:
        """CONNECTED-COMPONENT settlement sizes — the CLEAN counterpart to `settlements()` (R-106, 2026-08-25).

        `settlements()` counts agents standing on the exact site cell (`a.pos in sites`), so a village spread
        over adjacent cells is fragmented across several sites and each reads a fraction of the true size.
        `settle_med` has therefore been ~11 against Alvard's verified 50-250, and markers #3/#12/#13 were
        flagged PROVISIONAL because of it.

        Here the sites are clustered by adjacency (two sites within `settle_radius` join one cluster, union-
        find), and the cluster's size is EVERY agent whose cell is within `settle_radius` of any of its sites
        -- the whole community, counted once. Pure observer; no behaviour, no RNG.
        """
        sites = list(self._settlement_sites)
        if not sites:
            return {}
        r = int(getattr(self._demog, "settle_radius", 2))
        # union-find over sites that are within (2r) Chebyshev of each other -> one village per component
        parent = {s: s for s in sites}
        def find(a):
            while parent[a] != a:
                parent[a] = parent[parent[a]]; a = parent[a]
            return a
        for i, si in enumerate(sites):
            for sj in sites[i + 1:]:
                if max(abs(si[0] - sj[0]), abs(si[1] - sj[1])) <= 2 * r:
                    parent[find(si)] = find(sj)
        comp_sites: dict = {}
        for s in sites:
            comp_sites.setdefault(find(s), []).append(s)
        # each agent belongs to the component whose ANY site is within r of its cell; counted once (nearest)
        comp_n: dict = {c: 0 for c in comp_sites}
        for a in self.agent_list:
            ax, ay = a.pos
            best = None
            for c, cs in comp_sites.items():
                d = min(max(abs(ax - sx), abs(ay - sy)) for sx, sy in cs)
                if d <= r and (best is None or d < best[0]):
                    best = (d, c)
            if best is not None:
                comp_n[best[1]] += 1
        sizes = sorted((n for n in comp_n.values() if n > 0), reverse=True)
        if not sizes:
            return {}
        import numpy as np
        total = len(self.agent_list)
        return dict(n_clusters=len(sizes), cluster_med=int(np.median(sizes)), cluster_max=sizes[0],
                    cluster_min=sizes[-1], resident_frac=round(sum(sizes) / total, 3) if total else 0.0)

    def settlement_health(self) -> dict:
        """Soil (B1 depletion) and hardship (emergent-abandonment memory) state across settlement sites. {} when
        neither dict carries anything — the flags are off, or no site has existed long enough to accumulate
        state. Pure observer; reads `_settlement_soil` / `_settlement_hardship`, writes nothing."""
        out: dict = {}
        if self._settlement_soil:
            vals = list(self._settlement_soil.values())
            out["soil_mean"] = round(sum(vals) / len(vals), 3)
            out["soil_min"] = round(min(vals), 3)
            out["soil_frac_depleted"] = round(sum(1 for v in vals if v < 0.2) / len(vals), 3)
        if self._settlement_hardship:
            vals = list(self._settlement_hardship.values())
            out["hardship_mean"] = round(sum(vals) / len(vals), 3)
            out["hardship_max"] = round(max(vals), 3)
        return out

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
        self._order_females_for_pairing(females)   # R-77: wife-quality order (off ⇒ shuffle, bit-exact)
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
            f._ever_partnered = True; male._ever_partnered = True   # pure observer (never-partnered marker)
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
        self._order_females_for_pairing(females)   # R-77: wife-quality order (off ⇒ shuffle, bit-exact)
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
            f._ever_partnered = True; male._ever_partnered = True   # pure observer (never-partnered marker)
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
        # FOUNDING DELAY: no NEW settlement before the startup wander period ends (existing sites unaffected —
        # maintenance/holding is in `_maintain_settlements`). Lets the founders spread before villages nucleate.
        if (getattr(self._demog, "enable_founding_delay", False)
                and self.step_count < self._demog.settle_founding_delay_steps):
            return
        cfg = self._demog
        aqf = self._founding_pot_field()  # FOUNDING judgement -> storability-weighted (see _founding_pot_field)
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
        # PERF (R-106 Addendum 18): cell → occupancy ONCE, then sum each candidate's neighbourhood, instead of
        # a torus-distance scan of EVERY agent for EVERY candidate site. The old form was O(agents · sites) —
        # up to 40 sites × ~9k agents = 360k distance calls per invocation. Profiled at pop 9k it cost ~5% of
        # step time (`_torus_cheby` 730k calls over 15 steps; the genexpr 0.68 s self), and both dropped out of
        # the top-28 after this change. It is worth fixing because it grows with population, NOT because it
        # dominated — the step is led by `_step_rivalrous` and `diffusion_select_target`.
        # `_maintain_settlements` already carries this exact optimisation with the same comment; this
        # site-founding path was simply missed.
        # BIT-EXACT: a Chebyshev ball of radius `rad` on the torus is precisely the (2·rad+1)² wrapped cells,
        # so the count is identical — only the way of computing it changes.
        occ_cnt: dict = {}
        for a in self.agent_list:
            occ_cnt[a.pos] = occ_cnt.get(a.pos, 0) + 1
        if getattr(cfg, "enable_emergent_village_founding", False):
            # ── EMERGENT FOUNDING (supervisor spec 2026-08-12) ────────────────────────────────────────────
            # "People leave the village. They are a roving band now. They travel until they find a suitable
            #  place for a village that is more attractive than being a roving band — just like any village
            #  forms. So a fitting cell with proto-ag or fishing potential, out of catchment range of other
            #  villages."
            # ONE RULE FOR EVERY VILLAGE. No bud path, no ranked candidate list, no 40-site cap, and no
            # `aggregation_site_sep`. Measured reason the list had to go: it takes storable cells sorted by
            # S_pot DESCENDING and stops at 40, so `sep` silently governed HOW MUCH OF THE MAP was eligible,
            # not how far apart villages ended up. At sep=2 (20 km, the ethnographic figure) all 40 candidates
            # fell inside a 9x79 sliver of the single best ridge and ZERO villages formed anywhere.
            # The three conditions, evaluated WHERE PEOPLE ACTUALLY ARE:
            #   1. a fitting cell   — S_pot >= settle_persist_threshold (proto-ag / fishing potential)
            #   2. enough people    — settle_min_pool within settle_radius, the existing viability gate
            #   3. its own land     — outside every existing village's catchment
            # (3) is anchored, not invented: Vita-Finzi & Higgs 1970 [VERIFIED] put the forager site
            # exploitation territory at a ~10 km radius (the two-hour walk; Lee's !Kung agree), which is
            # `settle_catchment_radius` = 1 cell. Two Chebyshev catchments of radius r are disjoint exactly
            # when their centres are more than 2r apart. NOTE the discretisation inflates this: disjoint
            # circles of radius 10 km need centres 20 km apart, but disjoint 3x3 cell blocks need 30 km.
            # Deterministic: occupied cells are visited in sorted order, and earlier foundings constrain later
            # ones within the same step. Default OFF => the ranked-candidate path above => bit-exact.
            cr = cfg.settle_catchment_radius
            for (x, y) in sorted(occ_cnt):
                if float(aqf[y, x]) < thr:
                    continue                                   # 1. not a fitting site
                near = sum(occ_cnt.get(((x + dx) % N, (y + dy) % N), 0)
                           for dx in range(-rad, rad + 1) for dy in range(-rad, rad + 1))
                if near < cfg.settle_min_pool:
                    continue                                   # 2. not enough people to be a village
                if any(max(abs(x - ox), abs(y - oy)) <= 2 * cr
                       for (ox, oy) in self._settlement_sites):
                    continue                                   # 3. inside another village's catchment
                self._settlement_sites[(x, y)] = cfg.settle_release_steps
                self.settle_formed_this_step += 1
            return
        for (sx, sy) in sites:
            near = sum(occ_cnt.get(((sx + dx) % N, (sy + dy) % N), 0)
                       for dx in range(-rad, rad + 1) for dy in range(-rad, rad + 1))
            if near >= cfg.settle_min_pool:
                if (sx, sy) not in self._settlement_sites:
                    self.settle_formed_this_step += 1
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
        # FOUNDING DELAY: suppressed during the startup wander period (no sites exist yet then, so nothing to refresh).
        _fdelay = getattr(cfg, "enable_founding_delay", False) and self.step_count < cfg.settle_founding_delay_steps
        if getattr(cfg, "enable_aggregation_sedentism", False) and not _fdelay:
            aqf = self._founding_pot_field()  # FOUNDING judgement -> storability-weighted (see _founding_pot_field)
            rad = cfg.settle_radius
            for si in pools:                      # sites that pooled ≥1 band this gathering
                site = sites[si]
                if aqf is not None and aqf[site[1], site[0]] < cfg.settle_persist_threshold:
                    continue                       # not a persistent-abundant (storable) site
                near = sum(1 for a in self.agent_list
                           if self._torus_cheby(a.pos[0], a.pos[1], site[0], site[1]) <= rad)
                if near >= cfg.settle_min_pool:    # a real multi-band aggregation within the cluster → found/refresh
                    if site not in self._settlement_sites:
                        self.settle_formed_this_step += 1
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

    def _maintain_village_identity(self) -> None:
        """Co-residence dissolves band identity: long-settled bands MERGE into one village community.

        Fills the level Birdsell names and the model lacks — band ~25 nests in a larger local group, but
        nothing in the code ever merged co-resident bands, so a 204-person settlement held 45 of them.

        An agent accrues tenure at whichever settlement is within `settle_radius` (`_nearest_settlement`, the
        model's own membership test). Past `village_identity_months` it adopts that village's band_id. Moving
        away resets the clock, so this is PER-AGENT tenure: newcomers are not instantly absorbed, and a
        dissolving settlement releases its members without special-casing.

        THE VILLAGE ID IS AN EXISTING band_id, never a minted one — the modal band among the first qualifying
        cohort, tie-broken by lowest id so it is deterministic. Stored per site in `_village_band` so the
        identity is stable across steps rather than flipping with the modal count.

        COUPLING THAT MAKES THIS WORK OR THRASH. `_maintain_bands` spatially SPLITS any band above
        `band_split_size` (45). A merged village of ~200 would be torn apart on the very step it forms, so
        `_village_bands` (rebuilt here each step) is skipped by that fission branch. This is the existing
        `tolerable_size` idea taken to its conclusion: a SEDENTARY village tolerates a size a mobile band does
        not. The exemption lasts exactly as long as the settlement does — the set is rebuilt from live sites,
        so an abandoned village's band immediately becomes fissionable again.

        Default OFF ⇒ never called ⇒ bit-exact. No RNG."""
        cfg = self._demog
        thr = cfg.village_identity_months
        qualified: dict = {}
        for a in self.agent_list:
            site = self._nearest_settlement(a.pos)
            if site is None:
                a._cores_site = None
                a._cores_steps = 0
                continue
            if getattr(a, "_cores_site", None) != site:
                a._cores_site = site                      # arrived somewhere new → tenure restarts
                a._cores_steps = 1
            else:
                a._cores_steps = getattr(a, "_cores_steps", 0) + 1
            if a._cores_steps >= thr:
                qualified.setdefault(site, []).append(a)
        live = set(self._settlement_sites)
        for site in [s for s in self._village_band if s not in live]:
            del self._village_band[site]                  # settlement gone → its identity is not preserved
        self._village_bands = set()
        for site, members in qualified.items():
            vid = self._village_band.get(site)
            if vid is None:
                counts = Counter(a._group.band_id for a in members)
                top = max(counts.values())
                vid = min(b for b, n in counts.items() if n == top)   # modal, tie-broken by lowest id
                self._village_band[site] = vid
            for a in members:
                a._group.band_id = vid
            self._village_bands.add(vid)

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
            # R-99: per-band graded rank weight, computed once for this pass. None => feature off, and nothing
            # is computed at all, so OFF stays bit-exact.
            rank_w = None
            _rk = None
            _ref = 1.0
            if (self._demog is not None and getattr(self._demog, "enable_rank_hierarchy", False)
                    and self._lineage_ascribed):
                _ref = max(1e-9, self._demog.resent_effect_threshold)   # Cohen "large" — reused, not reinvented
                _rk = self._rank_keys()
                rank_w = {}
            for bid, ms in members.items():
                surplus = self._band_surplus.get(bid, 0.0)
                a_prev = self._band_assabiyah.get(bid, 0.0)
                # LEAKY form (R-106): the leak is proportional to the LEVEL, so the fixed point
                # a* = gain·s/(gain·s + decay) sits strictly inside (0,1) and tracks surplus. The default
                # constant-leak form has no interior fixed point and saturates at a bound whatever the
                # parameters — see `enable_leaky_assabiyah`. Off ⇒ bit-exact.
                if getattr(cfg, "enable_leaky_assabiyah", False):
                    a_new = min(1.0, max(0.0, a_prev + cfg.assabiyah_gain * surplus * (1.0 - a_prev)
                                         - cfg.assabiyah_decay * a_prev))
                else:
                    a_new = min(1.0, max(0.0, a_prev + cfg.assabiyah_gain * surplus - cfg.assabiyah_decay))
                new_assab[bid] = a_new
                for a in ms:                                   # mirror onto the collective-identity vector
                    a._group.assabiyah = a_new
                society = self._band_society.get(bid)
                if rank_w is not None:
                    rank_w[bid] = min(1.0, self._privilege_effect(ms, _rk) / _ref)

                leader_term = 0.0
                if leader_on and leader_gain > 0.0:
                    statuses = [a.cred * getattr(a, "prowess", 1.0) for a in ms]
                    mean_status = sum(statuses) / len(statuses)
                    top_status = max(statuses)
                    ratio = top_status / (mean_status + 1e-9)          # ≥1; 1 = no distinct leader
                    # The 1e-9 guards the RATIO's denominator but not the ratio when it is itself a divisor.
                    # With `enable_cred_status=False` every cred is 0 ⇒ top_status 0 ⇒ ratio 0.0 ⇒
                    # ZeroDivisionError, so the cred ABLATION could not be run at all (found by the mechanism
                    # battery, 2026-07-26). Zero status spread means no distinct leader, which is strength 0 —
                    # the same value the ratio→1 limit gives. Bit-exact wherever any cred is non-zero.
                    leader_strength = (1.0 - 1.0 / ratio) if ratio > 0.0 else 0.0
                    weight = leader_society_weight(society)            # Boehm gate
                    if rank_w is not None:
                        # R-99: RANK IS AN ALTERNATIVE ROUTE TO HIERARCHY, taken as a MAX rather than a sum —
                        # Testart's storable-surplus road and Leach's ranked-lineage road are two ways to the
                        # same organisational capacity, not two additive bonuses. Normalised by
                        # `resent_effect_threshold` (Cohen's "large", already in the config for resentment), so
                        # a community whose nobles stand a LARGE effect above its commoners earns the full
                        # stratified weight and no NEW constant is introduced.
                        weight = max(weight, rank_w.get(bid, 0.0))
                    leader_term = leader_gain * weight * leader_strength
                new_leader[bid] = leader_term

                # EMERGENT BAND SIZE v3: the risk-pooling optimum for THIS band's local return variance.
                # g* = mean-cell-CV / cv_safe (linear, unclamped). It is the band's tolerable-size SCALE:
                # it centres the scalar-stress logistic (below) and floors the fission threshold.
                g_star = None
                if cvf is not None and ms:
                    mean_cv = sum(float(cvf[a.pos[1], a.pos[0]]) for a in ms) / len(ms)
                    g_star = mean_cv / cfg.cv_safe

                repulsion = 0.0
                if repulsion_on and rep_gain > 0.0:
                    # THE fix: Johnson scalar stress is centred on g*, not a hardcoded 25. A band living on
                    # high-variance returns has more to gain from pooling, so it tolerates crowding to a larger
                    # size before the coordination cost bites — which is how the CV finally reaches the term
                    # that actually SETS band size (v1/v2 only raised a ceiling; corr(g*,size) was −0.22).
                    repulsion = size_repulsion(len(ms), rep_gain, g_star if g_star is not None else rep_mid,
                                               rep_width, society)
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
                # `cohesion_leader_weight` scales the leader's share of the [0,1] budget. At the default 1.0
                # this is the historical expression, bit-exact; below 1.0 it stops the leader term (measured
                # 0.41–1.64, median 0.78) from saturating the sum on its own — see `enable_leaky_assabiyah`.
                cohesion_frac = min(1.0, max(0.0, a_new + cfg.cohesion_leader_weight * leader_term
                                             - repulsion - malnutrition))
                base_b = g_star if g_star is not None else base      # emergent base = the risk-pooling optimum
                # `max(0, ...)`: guards the degenerate case g* > cap (a mis-set cv_safe) from inverting the
                # headroom's sign. It is NOT a clamp on g* — with the anchored RETURN_CV, g* spans 19–38 < cap.
                split_thr[bid] = base_b + max(0.0, cap - base_b) * cohesion_frac
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
        # FISSION (above the split threshold → spatial median split). VILLAGE BANDS ARE EXEMPT: a band that is
        # a settled village (see `_maintain_village_identity`) is no longer a mobile band and must not be cut
        # back to band_split_size, or the merge it just performed is undone on the same step. The exemption is
        # scoped to LIVE settlements — `_village_bands` is rebuilt each step from current sites, so an
        # abandoned village becomes fissionable again immediately. Empty set ⇒ no-op ⇒ bit-exact.
        _vb = getattr(self, "_village_bands", ())
        for bid in [b for b, ms in members.items()
                    if b not in _vb and len(ms) > split_thr.get(b, cfg.band_split_size)]:
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

    def _credit_material(self, a, amt: float) -> None:
        """Route new durable output through any standing OBLIGATION before it reaches its producer.

        TYPE C (Conversion) · INVARIANT: material is CONSERVED here — what the debtor does not keep, the
        creditor receives. Off ⇒ `a.material += amt`, i.e. bit-exact with the previous behaviour.

        This is the repayment half of Sahlins' loop: the creditor's earlier grant bought a claim on the
        debtor's production, so the debtor's hides pay it down until the debt is discharged."""
        if amt <= 0.0:
            a.material += amt
            return
        cfg = self._demog
        if cfg is not None and getattr(cfg, "enable_wealth_obligation", False):
            cr = getattr(a, "_creditor", None)
            debt = getattr(a, "_debt", 0.0)
            if cr is not None and debt > 0.0:
                if not getattr(cr, "alive", False):
                    a._creditor, a._debt = None, 0.0        # a debt dies with the creditor; it is personal
                else:
                    take = min(amt * cfg.obligation_return_frac, debt)
                    cr.material += take
                    a._debt = debt - take
                    amt -= take
                    if a._debt <= 1e-9:
                        a._creditor, a._debt = None, 0.0
        a.material += amt

    def _do_obligations(self) -> None:
        """WEALTH → OBLIGATION. A man with a durable surplus feeds a hungry band-mate and thereby acquires a
        claim on his production (Sahlins 1963: "uses wealth to place others in his debt ... he constructs a
        following whose production may be harnassed to his ambition").

        TYPE C (Conversion) · UNIT agent pair · INVARIANT DEBITED — the grant SPENDS the creditor's material.

        Why this exists: `material` was a terminal stock with no investment channel, so it could not compound
        and never concentrated (noble lift 0.87–1.04 under every other remedy tried). The conversion rate is
        the inverse of the model's OWN production relation (material = material_hide_frac × meat kcal), so no
        new exchange rate is invented. Off ⇒ returns before any state change or RNG draw ⇒ bit-exact."""
        cfg = self._demog
        if cfg is None or not getattr(cfg, "enable_wealth_obligation", False):
            return
        hide = getattr(cfg, "material_hide_frac", 0.0)
        if hide <= 0.0:
            return                                          # no material economy ⇒ nothing to lend
        kcal_per_material = 1.0 / hide
        bands: dict = {}
        for a in self.agent_list:
            bands.setdefault(a._group.band_id, []).append(a)
        for ms in bands.values():
            if len(ms) < 3:
                continue
            mean_mat = sum(getattr(a, "material", 0.0) for a in ms) / len(ms)
            if mean_mat <= 0.0:
                continue
            # CREDITORS: a durable surplus well above the band's own mean. DEBTORS: in food deficit and not
            # already bound — Sahlins' recipient is someone who needs what the creditor can give.
            floor = None
            creditors = [a for a in ms
                         if getattr(a, "material", 0.0) >= cfg.obligation_min_ratio * mean_mat]
            if not creditors:
                continue
            # DEBTORS ARE RELATIVELY, NOT ABSOLUTELY, NEEDY. The first version required `wealth < reserve
            # floor` and NEVER FIRED: measured 0 of 1515 agents below the floor, with wealth/floor at p01
            # 2.68, p10 2.72, median 2.74 — the whole population sits ~2.7x the floor with a 2% spread. This
            # model has almost no subsistence inequality, so absolute destitution does not exist and a
            # mechanism keyed to it cannot act. Sahlins' client is not starving either; he is someone for whom
            # a patron's help is worth an obligation. Relative position within his own band is the faithful
            # criterion — and it keeps the mechanism honest, since it can only ever bind the poorer half.
            free = [a for a in ms
                    if getattr(a, "_creditor", None) is None and getattr(a, "_debt", 0.0) <= 0.0]
            if not free:
                continue
            _w = sorted(a.wealth for a in free)
            med_w = _w[len(_w) // 2]
            debtors = [a for a in free if a.wealth < med_w]
            if not debtors:
                continue
            creditors.sort(key=lambda x: (-x.material, x.unique_id))     # deterministic
            debtors.sort(key=lambda x: (x.wealth, x.unique_id))
            for cr, db in zip(creditors, debtors):
                if cr is db:
                    continue
                grant = cr.material * cfg.obligation_grant_frac
                if grant <= 0.0:
                    continue
                cr.material -= grant                                     # DEBITED
                db.wealth += grant * kcal_per_material                   # arrives as food, which he can use
                db._creditor = cr
                db._debt = grant * cfg.obligation_premium                # the gift binds: claim > grant
                self.obligation_grants += 1

    @staticmethod
    def _kin_affinity(a, b) -> float:
        """Kinship between two agents — the village-fission cleavage axis (Alvard 2009; see the call site).

        Uses the model's OWN relatedness measure (genome identity-by-state) when genomes are live, so nothing
        new is invented. Genealogical fallback when they are not, in decreasing closeness: shared parent or
        parent-child 0.5, same patriline 0.25, otherwise 0. Symmetric, and deterministic — no RNG."""
        if a is b:
            return 1.0
        ga, gb = getattr(a, "_genome", None), getattr(b, "_genome", None)
        if ga is not None and gb is not None:
            return ga.relatedness(gb)
        am, af = getattr(a, "_mother", None), getattr(a, "_father", None)
        bm, bf = getattr(b, "_mother", None), getattr(b, "_father", None)
        if ((am is not None and am is bm) or (af is not None and af is bf)
                or am is b or af is b or bm is a or bf is a):
            return 0.5                                              # siblings, or parent and child
        la, lb = getattr(a, "_lineage", None), getattr(b, "_lineage", None)
        if la is not None and la == lb:
            return 0.25                                             # same patriline, no closer tie known
        return 0.0

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
        aqf = self._founding_pot_field()  # FOUNDING judgement -> storability-weighted (see _founding_pot_field)
        if aqf is None or not self._settlement_sites:
            return
        thr_base = cfg.village_fission_threshold; circ_gain = cfg.village_circumscription_gain
        haz_on = getattr(cfg, "enable_bud_hazard", False)   # emergent hazard vs the legacy size threshold
        minf = cfg.village_bud_min_faction
        R = cfg.village_bud_search_radius; persist = cfg.settle_persist_threshold; sep = cfg.settle_radius
        hf = self._harvest_field; W = getattr(hf, "width", N); H = getattr(hf, "height", N)
        # COLONIZING BUDDING (see enable_colonizing_budding): found daughters on empty land, spaced by a
        # density-scaled separation d(K)=clamp(round(sqrt(V_target/K_local)),1,3) cells. K_local is the cell's
        # Tallavaara carrying capacity (persons/cell). If the field has none, fall back to a fixed 2-cell sep.
        colonize = getattr(cfg, "enable_colonizing_budding", False)
        _Kf = getattr(getattr(hf, "_base", hf), "_K_persons", None) if colonize else None
        _Vt = cfg.bud_spacing_village_target if colonize else 0.0
        def _bud_sep(xx, yy):
            if not colonize:
                return (2 * sep + 1) if getattr(cfg, "enable_bud_site_separation", False) else (sep + 1)
            if _Kf is None:
                return 2
            k = float(_Kf[yy, xx])
            return 3 if k <= 0.0 else int(min(3, max(1, round(math.sqrt(_Vt / k)))))
        cell_agents: dict = {}
        for a in self.agent_list:
            cell_agents.setdefault(a.pos, []).append(a)
        occ = {c: len(v) for c, v in cell_agents.items()}
        for (sx, sy) in list(self._settlement_sites):
            village = [a for dx in range(-sep, sep + 1) for dy in range(-sep, sep + 1)
                       for a in cell_agents.get((sx + dx, sy + dy), ())]
            bids = Counter(a._group.band_id for a in village)
            _u = None
            if haz_on:
                # ── EMERGENT HAZARD (2026-07-27) — see DemographyConfig for the provenance of every term.
                # P(critical scalar stress | size) is Alberti 2014's FITTED logistic, so the steepness is a
                # published number with a CI rather than a knob. The ceiling rate is Bandy's own event counts.
                _z = cfg.bud_hazard_b0 + cfg.bud_hazard_b1 * len(village)
                p_size = 1.0 / (1.0 + math.exp(-_z)) if -700 < _z < 700 else (0.0 if _z <= 0 else 1.0)
                ceil_step = cfg.bud_hazard_per_yr / cfg.bud_steps_per_year
                # EXACT EARLY-OUT. Every modifier below is ≤ 1, so p_size·ceiling is an upper bound on the
                # true hazard. Drawing ONCE and testing the bound first is distribution-identical to testing
                # the full hazard, and it means the expensive part (catchment scan, site search, kinship)
                # runs ~1e-4 of the time instead of every village every step. That cost was what made the
                # previous version 70 s/step at 400+ settlements.
                _u = self.random.random()
                if _u >= p_size * ceil_step:
                    continue
            elif len(village) <= thr_base:          # legacy path: below the open-landscape threshold
                continue
            if not haz_on and "stratified" in str(self._band_society.get(bids.most_common(1)[0][0], "")):
                continue                                            # integrated village → fission suppressed (Bandy)
            # CLEAVE ON KINSHIP, NOT LINEAGE (2026-07-27). This used to split off the SECOND-LARGEST LINEAGE.
            # Alvard 2009 (literature/AlvardPaper2.pdf), reanalysing Chagnon's Mishimishimaböwei-teri axe fight
            # — a village that had itself just fissioned — finds factions assort by GENETIC KINSHIP (~15% of
            # variance) and NOT by lineage: lineage alone explains ~3%, and once kinship is controlled it is no
            # longer significant (p=0.281), its solo effect being mere covariance with relatedness. The paper's
            # own summary: "lineage identity explained nothing". Lineage-assorted factions are Alvard's LAMALERA
            # (whaling-crew) pattern, not the Yanomamö fission one.
            # Measured cost of the old rule: a 475-person village here held 126 lineages, largest 8.2%, so no
            # lineage bloc could reach the required share and budding NEVER fired at any village size.
            # Chagnon's mechanism is competing headmen — the village splits between its two highest-standing
            # men, each keeping those more closely related to him.
            adults = [a for a in village if a.age >= cfg.menarche_months] or list(village)
            if len(adults) < 2:
                continue                                            # nobody to compete → no cleavage
            adults.sort(key=lambda x: (getattr(x, "cred", 0.0) * getattr(x, "prowess", 1.0), x.unique_id),
                        reverse=True)
            head, rival = adults[0], adults[1]                      # incumbent headman vs his rival
            faction = [a for a in village
                       if self._kin_affinity(a, rival) > self._kin_affinity(a, head)]
            # A village with no real cleavage yields only the rival himself (everyone else is equidistant
            # between the two men), and one person is not a daughter village. Two is the minimum bloc that can
            # carry a fission; `village_bud_min_faction` (default 0) can impose a share requirement on top.
            if len(faction) < 2 or len(faction) < minf * len(village):
                continue                                            # no rival bloc to carry a fission
            if colonize:
                # VIABLE EMIGRANT BLOC: the median kinship faction is ~2 (most villagers are equidistant from the
                # two leaders), too small to seed a village and the source of the 2-person-village churn. Top the
                # bloc up to a viable founding party — the villagers most drawn to the rival (kin first), sized to
                # the EXCESS above the fission threshold, floored at settle_min_pool, capped at half the village so
                # the parent keeps a majority. So budding sheds a real emigrant party that founds a viable daughter.
                _ranked = sorted(village, key=lambda a: (self._kin_affinity(a, rival) - self._kin_affinity(a, head),
                                                         a.unique_id), reverse=True)
                _bloc = min(len(village) // 2, max(cfg.settle_min_pool, len(village) - thr_base))
                faction = _ranked[:_bloc]
                if len(faction) < cfg.settle_min_pool:
                    continue                                        # cannot seed a viable daughter → no bud
            # NEAREST open storable daughter site (its distance = the relocation cost that drives circumscription)
            # MINIMUM SEPARATION. The original `sep + 1` = 3 cells is SMALLER than the hold window, which is the
            # (2·settle_radius+1) = 5-cell block `_maintain_settlements` counts for `settle_min_pool`. Two sites
            # 3 cells apart therefore share 10 of their 25 catchment cells, and each counts the OTHER's people
            # toward its own 40-person survival test. Measured consequence: ~110 settlements at a mean spacing
            # of 3.79 cells, mean on-site occupancy 15.8 against a 40-person requirement — a dense cluster of
            # individually-unviable sites propping each other up, which is the engine of the budding runaway
            # (2026-08-12 investigation). With `enable_bud_site_separation` the daughter must sit at least
            # 2·settle_radius+1 away, so the two catchments are DISJOINT and a daughter has to hold its own
            # pool to survive. Default OFF ⇒ `sep + 1` ⇒ bit-exact.
            best, bestd = None, R + 1
            for yy in range(max(0, sy - R), min(H, sy + R + 1)):
                for xx in range(max(0, sx - R), min(W, sx + R + 1)):
                    d = max(abs(xx - sx), abs(yy - sy))
                    _ms = _bud_sep(xx, yy)                          # density-scaled when colonizing; else the legacy sep
                    if d < _ms or d >= bestd or float(aqf[yy, xx]) < persist:
                        continue                                    # own catchment, farther than best, or not storable
                    if (xx, yy) in self._settlement_sites or occ.get((xx, yy), 0) >= cfg.settle_min_pool:
                        continue                                    # already an occupied settlement → not open
                    if (colonize or _ms > sep + 1) and any(
                            max(abs(xx - ox), abs(yy - oy)) < _ms
                            for (ox, oy) in self._settlement_sites):
                        continue    # DISJOINTNESS IS GLOBAL, NOT JUST PARENT-DAUGHTER. The first version of
                        #             this rule constrained only the distance back to the PARENT, so a daughter
                        #             could still be sited one cell from some OTHER village. Measured: with the
                        #             rule on, median nearest-neighbour spacing was still 1.0 cell and 94% of
                        #             the population stayed resident — the catchment overlap, and so the mutual
                        #             propping, survived untouched. A site must clear EVERY existing settlement.
                    best, bestd = (xx, yy), d
            if best is None:
                continue         # CIRCUMSCRIBED (no open site in reach) → no bud → village grows + stratifies (Bandy → morph)
            if haz_on:
                # ── THE MODIFIERS. Bandy names each direction; the weights are DESIGN and each is bounded in
                # [0,1], so they can only ever DAMP the anchored ceiling, never inflate it.
                # DEPLETION (favours) — "factors that would appear to favour fissioning include resource
                # depletion". `_band_surplus` is the morph detector's per-band stored-food fraction, i.e.
                # literally whether the economy is working. Full granaries ⇒ depletion 0 ⇒ no reason to split,
                # which is the whole point of making this emergent.
                _tot = sum(bids.values())
                _sur = sum(self._band_surplus.get(b, 0.0) * n for b, n in bids.items()) / _tot if _tot else 0.0
                depletion = 1.0 - (0.0 if _sur < 0.0 else (1.0 if _sur > 1.0 else _sur))
                # CAPITAL (discourages) — "high levels of investment in landscape (nonportable) capital". The
                # share of the village's own catchment it has claimed. Naturally in [0,1]; no invented scale.
                _cat = [((sx + dx) % W, (sy + dy) % H)
                        for dx in range(-sep, sep + 1) for dy in range(-sep, sep + 1)]
                capital = (sum(1 for c in _cat if c in self._cell_owner) / len(_cat)) if _cat else 0.0
                # INTEGRATION (discourages) — Johnson's second branch, now GRADED rather than a hard gate:
                # institutions that manage conflict make fissioning "not necessary".
                _soc = str(self._band_society.get(bids.most_common(1)[0][0], ""))
                integration = 1.0 if "stratified" in _soc else (0.5 if "complex" in _soc else 0.0)
                # ── POLARIZATION: Bandy's "high level of internal conflict", the half that was missing ──
                # MATE COMPETITION (Alvard/Chagnon: villages splinter over women). Share of adult men with no
                # wife — the pool of men with a reason to force a split.
                _adult_m = [a for a in village if a.sex == "male" and a.age >= cfg.menarche_months]
                mate_comp = ((sum(1 for a in _adult_m if not getattr(a, "_wives", ()))
                              / len(_adult_m)) if _adult_m else 0.0)
                # LEADERSHIP RIVALRY (Chagnon: competing headmen). How close the rival stands to the
                # incumbent, using the pair the cleavage already picked. 1 = two equals, 0 = uncontested.
                _mh = getattr(head, "cred", 0.0) * getattr(head, "prowess", 1.0)
                _mr = getattr(rival, "cred", 0.0) * getattr(rival, "prowess", 1.0)
                rivalry = (_mr / _mh) if _mh > 0 else 0.0
                rivalry = 0.0 if rivalry < 0.0 else (1.0 if rivalry > 1.0 else rivalry)
                # GRIEVANCE: the existing resentment stock, which measures privilege as an EFFECT SIZE and is
                # therefore a gap rather than a level. Normalised by the reversion threshold it feeds.
                _thr = getattr(cfg, "resent_threshold", 0.5) or 0.5
                # KEY THE GRUDGE THE WAY THE GRUDGE IS KEYED. Under `enable_village_resentment` (R-95) the
                # stock is held per SETTLEMENT SITE as ("v", site) — "the place remembers while its members
                # churn" — not per band. The first version of this looked it up by band_id and read 0.0000 for
                # every village while `_band_resentment` held 51 live entries peaking at 0.637, so the whole
                # grievance driver was silently dead. Same class of error as reading `_lineage_ascribed`
                # directly instead of through `_rank_keys()`: the structure is polymorphic, so the consumer
                # must use the same key the producer used.
                if getattr(cfg, "enable_village_resentment", False):
                    _res = self._band_resentment.get(("v", (sx, sy)), 0.0)
                else:
                    _res = (sum(self._band_resentment.get(b, 0.0) * n for b, n in bids.items()) / _tot
                            if _tot else 0.0)
                grievance = min(1.0, max(0.0, _res / _thr))
                # ALTERNATIVE SUFFICIENT CAUSES ⇒ MAX, not product. Multiplying would mean that adding a
                # second reason to fission makes fission RARER, which is backwards.
                drive = max(cfg.bud_w_depletion * depletion,
                            cfg.bud_w_mate_competition * mate_comp,
                            cfg.bud_w_rivalry * rivalry,
                            cfg.bud_w_grievance * grievance)
                haz = (p_size * ceil_step * drive
                       * ((1.0 - cfg.bud_w_capital) + cfg.bud_w_capital * (1.0 - capital))
                       * ((1.0 - cfg.bud_w_integration) + cfg.bud_w_integration * (1.0 - integration))
                       # CIRCUMSCRIPTION (discourages) — same anchored gain as the legacy threshold-rise
                       # (Bandy: 170 open → 277 circumscribed ⇒ +60%), now damping the hazard instead.
                       / (1.0 + circ_gain * bestd / R))
                if _u >= haz:
                    continue
            else:
                # Bandy fission COST: the threshold RISES with relocation distance — base → ~+60% circumscribed
                if len(village) <= thr_base * (1.0 + circ_gain * bestd / R):
                    continue                                        # not large enough to justify the relocation
            new_id = self._next_band_id; self._next_band_id += 1     # BUD: rival faction migrates + founds the daughter
            for a in faction:
                a._group.band_id = new_id; a.pos = best
            # THE BUD-FOUNDING BYPASS. `_found_settlements_by_occupancy` requires settle_min_pool (40) people
            # within settle_radius before a settlement exists — an emergent, occupancy-gated rule. Budding
            # skipped it entirely and CREATED a site outright, so a faction of two (the measured median, since
            # the kinship cleavage excludes the 97% of villagers equidistant from both leaders) founded a full
            # settlement. That is the generator of the runaway: ~1,700 settlements manufactured out of pairs of
            # people in 400 steps, after which no downstream rule could produce physical spacing — five were
            # tried and measured, and all five failed (min-faction share silenced budding; village identity was
            # inert; parent-only separation did nothing; global separation worked but imposed 50 km against a
            # ~20 km filed anchor; exclusive membership raised churn instead of spacing).
            # ON ⇒ the bud RELOCATES its faction and splits the band, but founds no site. The daughter becomes
            # a settlement only if people actually gather there, through the existing occupancy rule — so
            # SPACING IS EMERGENT and no distance constant is introduced anywhere. Default OFF ⇒ bit-exact.
            # COLONIZING BUDDING founds the daughter DIRECTLY (it supersedes enable_bud_requires_occupancy) — the
            # viable emigrant bloc + the density-scaled spacing above are what keep it from the 2-person-village
            # runaway that made direct founding unusable before.
            if colonize or not getattr(cfg, "enable_bud_requires_occupancy", False):
                if best not in self._settlement_sites:
                    self.settle_formed_this_step += 1
                self._settlement_sites[best] = cfg.settle_release_steps
            self.bud_events += 1               # counts BOTH paths (was hazard-only — legacy-path budding read 0 always)
            self.bud_events_this_step += 1     # per-step twin of the cumulative counter above

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

    def _village_pop(self, site: tuple[int, int], occ_count: dict) -> int:
        """VILLAGE-SCALED DISEASE: the population within settle_radius of `site` (the settled community). Cached
        per step (many agents share a site), keyed by the model's step counter."""
        if self._village_pop_cache is None or self._village_pop_step != self.step_count:
            self._village_pop_cache = {}
            self._village_pop_step = self.step_count
        v = self._village_pop_cache.get(site)
        if v is None:
            rad = self._demog.settle_radius
            sx, sy = site
            v = sum(occ_count.get(((sx + dx) % N, (sy + dy) % N), 0)
                    for dx in range(-rad, rad + 1) for dy in range(-rad, rad + 1))
            self._village_pop_cache[site] = v
        return v

    def _a2_mult(self, a, occ_count) -> float:
        """Step-2 baseline-mortality (a2) multiplier from the live modulators (1.0 if all flags off) —
        the only Siler term the world modulates. Capped (red-team n-1). Pathogen OFF in 2b.

        PER-FACTOR OBSERVERS (R-106, 2026-08-14). The product was measured at ~2.2x the configured Siler in
        the 5-15 band, but only the PRODUCT was ever visible, so which of the three factors carries it was
        unknown. Addendum 43 showed the density term is near-neutral once the carrying-capacity ceiling is
        repaired, which leaves terrain risk and the nutrition synergy — and nothing measured either alone.
        Each is a plain running sum; no RNG, no read-back.
        """
        cfg = self._demog
        m = 1.0
        _f_risk = _f_dens = _f_syn = 1.0
        if cfg.enable_terrain_risk:
            _f_risk = risk_mult(float(self._fields.risk[a.pos[1], a.pos[0]]), self._risk_ref, cfg.risk_cap)
            m *= _f_risk
        if cfg.enable_density_disease:
            # VILLAGE-SCALED (spread-invariant) disease for a settled agent: its density is the VILLAGE population
            # over the village territory, so dispersing dwellings does not evade the brake. Mobile agents keep the
            # single-cell form. Default OFF ⇒ single-cell everywhere ⇒ bit-exact.
            if getattr(cfg, "enable_village_density_disease", False):
                _site = self._nearest_settlement(a.pos)
                if _site is not None:
                    _rad = cfg.settle_radius
                    _area = ((2 * _rad + 1) ** 2) * _CELL_KM2
                    rho = self._village_pop(_site, occ_count) / _area
                else:
                    rho = occ_count.get(a.pos, 1) / _CELL_KM2
            else:
                rho = occ_count.get(a.pos, 1) / _CELL_KM2       # agents/km²
            # `dens_rho_ref` only when the flag is on; 0.0 reproduces the historical form bit-exactly.
            _rref = cfg.dens_rho_ref if getattr(cfg, "enable_density_reference", False) else 0.0
            _f_dens = density_mult(rho, cfg.dens_delta, cfg.dens_rho_half, _rref)
            m *= _f_dens
        # (F.2 band risk-dilution was a fourth multiplier here; deleted 2026-08-06 — a death spiral at any live
        # setting and inert at its default. See DemographyConfig, where the finding is kept.)
        if cfg.enable_terrain_pathogen:                        # S2 biome disease-ecology (Cashdan; NPP proxy)
            m *= pathogen_mult(float(self._fields.npp[a.pos[1], a.pos[0]]), self._pathogen_npp_ref,
                               cfg.pathogen_gamma, cfg.pathogen_cap)
        if cfg.enable_nutrition_synergy:
            # AGE-GRADED: adults (past menarche) are more malnutrition-robust than children, so they use the
            # attenuated synergy cap. Default (flag off) ⇒ cfg.mu_max at every age ⇒ bit-exact.
            _mu = (cfg.synergy_mu_max_adult
                   if (getattr(cfg, "enable_synergy_age_grade", False) and a.age >= cfg.menarche_months)
                   else cfg.mu_max)
            if cfg.enable_condition:                           # S0: disease potentiated by SUSTAINED condition (EMA)
                _f_syn = 1.0 + (_mu - 1.0) * (1.0 - a._condition)
            else:                                              # legacy: instantaneous post-harvest reserve
                _rs = a.reserve_scale()                        # C.2a age-scaled floor/full
                _f_syn = synergy_mult(a._fed_reserve, a.reserve_floor * _rs, self._reserve_full * _rs, _mu)
            m *= _f_syn
        self.a2_n += 1
        self.a2_risk_sum += _f_risk
        self.a2_dens_sum += _f_dens
        self.a2_syn_sum += _f_syn
        self.a2_cond_sum += float(getattr(a, "_condition", 1.0))
        if m > cfg.a2_cap:
            self.a2_cap_hits += 1
            self.a2_total_sum += cfg.a2_cap
            return cfg.a2_cap
        self.a2_total_sum += m
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
