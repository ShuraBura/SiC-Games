"""SiC Games — deep-time CAMPAIGN harness (endogenous secular dynamics + full Turchin-layer instrumentation).

Grows one diverse temperate world for a long horizon on the VALIDATED R-64 settlement substrate (band→village→
stratified centres), with climate seasonal but NO regime forcing, so anything cyclic is ENDOGENOUS. Unlike
run_substrate_A (population/stratification/genetics only), this captures the full diagnostic surface so a single
long run answers the elite/dynasty, settlement-hierarchy, mating-network, and instability questions in one pass:

  TRAJECTORY (per C_LOGEVERY steps, JSON checkpoint):
    demography     pop, births, starv-deaths, mean-reserve, juvenile fraction, mean age
    structure      band/village size dist, %complex/%stratified, gini(cred)/gini(wealth), surplus, assabiyah
    ELITE/DYNASTY  n_lineages, top_share, size_gini, eff_lineages (inverse-Simpson), dominant-dynasty RS +
                   within-dynasty relatedness (genetic signature); male reproductive-skew gini (overproduction)
    SETTLEMENT     n settlements, median/max size, primate_ratio, zipf_slope (rank-size / urban hierarchy)
    MATING         connubium reach (median/p90 → Wobst ~475)
    INSTABILITY    defensibility claim_events (contest flow), cells owned  [Dyson-Hudson & Smith 1978]
    LEADERSHIP     band-leader identity turnover between snapshots
    GENETICS       heterozygosity + mean relatedness (N_e signal; computed offline from H-decay)   [C_GENEVERY]

  GENEALOGY (streamed to CSV, bounded memory): every birth/death as a GENEA_HEADER row (parentage, lineage/band,
    status, wealth, sex/age, COMPLETED RS, cell, society) — the substrate for offline dynasty/RS/relatedness
    reconstruction. Flushed + buffer-cleared every C_FLUSHEVERY steps.

Run:  py -3 -u sic_games/outputs/substrate_run/run_campaign.py            (from repo root)
Env:  C_FOUNDERS 3000 | C_STEPS 15000 | C_SEED 0 | C_LOGEVERY 25 | C_GENEVERY 200 | C_FLUSHEVERY 500
      C_TERR coastal | C_CLIM temperate | C_TAG "" | C_GENOME 1
      C_ELITE 0 — T-9 (2026-07-20): the R-82...R-87 elite/legitimacy stack (material capture, leader share,
      Boehm leveling, leader office, legitimacy ratchet, gumsa/gumlao delegitimation), at the values validated
      in those results. Bit-exact OFF when C_ELITE=0 (every enable_* it touches defaults False regardless).
      Lets this harness's PROVEN long-horizon substrate (R-58...R-66) test whether that stack changes DYNASTIC
      CONCENTRATION (dynasties()/eff_lineages/top_share) against Karmin/Zerjal/Yan (LITERATURE.md, TARGETS T-9) —
      a combination never run together before this.
"""
import sys, os, time, json, statistics, subprocess
from collections import Counter

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, "..", "phase1_social_evolution"))
sys.path.insert(0, os.path.join(HERE, "..", "biome_society_20260702"))
from run_biome_society import BURN, X0, Y0, PATCH, GRP
from run_se0_controlled_climate import emergent_village_demog
from sic_games.config import KcalEconomyConfig, SubstrateConfig, CarbonConfig
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world, world_lottery_climate
from sic_games.capacity import NPPCapacityField
from sic_games.climate import ClimateConfig, build_climate_field
from sic_games.invariants import check as invariant_check
from sic_games.demography import demography_health, spatial_health
from sic_games import runspec as _runspec

# ── A RUN IS A FILE (2026-08-07) ──────────────────────────────────────────────────────────────────────────
#     py -3 run_campaign.py --config config/runs/full_campaign.toml [--seed N]
#
# The file states EVERYTHING — how long, which world, every mechanism, every parameter. Nothing else decides
# what happened, and a run needing a reduction or adjustment gets its OWN file, discussed and written first.
#
# HOW IT ATTACHES, and why this way. The 61 `C_*` reads below run at import. Rather than rewrite 61 call sites
# (and risk missing one silently — the defect class this whole change exists to end), the spec's `[run]`
# section is injected into `os.environ` FIRST, so every existing read resolves to the file's value unchanged.
# The env vars stop being a user interface and become an internal detail. `[mechanisms]`/`[parameters]` are
# applied later, at the one place the config object is finalised.
#
# MIXING IS REFUSED, NOT MERGED. If a model-config knob is set alongside `--config`, the run STOPS. Merging is
# what broke the first attempt at this on 2026-08-06: the file replaced a config the knobs had already
# resolved, and `C_SOIL=0` silently came back True. There is no correct precedence here — a run configured two
# ways is a run nobody can describe afterwards.
_SPEC = None
if "--config" in sys.argv:
    _i = sys.argv.index("--config")
    _seed_over = None
    if "--seed" in sys.argv:
        _seed_over = int(sys.argv[sys.argv.index("--seed") + 1])
    _SPEC = _runspec.load(sys.argv[_i + 1], seed=_seed_over)

    # Model configuration may come from the file or from the knobs, never both.
    _MODEL_KNOBS = [k for k in os.environ if k.startswith("C_") and k not in (
        "C_TAG",)]          # C_TAG alone is harmless labelling and several harnesses set it globally
    if _MODEL_KNOBS:
        raise SystemExit(
            "--config was given AND these C_* knobs are set: " + ", ".join(sorted(_MODEL_KNOBS))
            + "\nA run is configured ONE way. Put the setting in the file, or drop --config.")

    _ENV_FROM_RUN = {"steps": "C_STEPS", "seed": "C_SEED", "founders": "C_FOUNDERS", "terrain": "C_TERR",
                     "climate": "C_CLIM", "patch": "C_PATCH", "tag": "C_TAG", "max_minutes": "C_MAXMIN",
                     "log_every": "C_LOGEVERY", "gen_every": "C_GENEVERY", "flush_every": "C_FLUSHEVERY",
                     "genealogy": "C_GENEA", "genome": "C_GENOME",
                     # The seed's three roles (runspec RUN_DEFAULTS). Absent from a run file ⇒ all three equal
                     # `seed` ⇒ every prior run is bit-exact.
                     "world_seed": "C_WORLD_SEED", "climate_seed": "C_CLIM_SEED",
                     "agent_seed": "C_AGENT_SEED",
                     "seed_layout": "C_SEED_LAYOUT", "seed_cluster_size": "C_SEED_CLUSTER"}
    for _k, _env in _ENV_FROM_RUN.items():
        _v = _SPEC.run[_k]
        os.environ[_env] = ("1" if _v else "0") if isinstance(_v, bool) else str(_v)

FOUNDERS  = int(os.environ.get("C_FOUNDERS", "3000"))
STEPS     = int(os.environ.get("C_STEPS", "15000"))
SEED      = int(os.environ.get("C_SEED", "0"))
# THE SEED IS THREE THINGS (runspec RUN_DEFAULTS, 2026-08-11). Default: all three = SEED, so nothing changes
# unless a run file pins one. Holding WORLD_SEED still while AGENT_SEED varies is the only way to measure PATH
# variance — with a single integer, two "seeds" are two different planets and the two variances are confounded.
WORLD_SEED  = int(os.environ.get("C_WORLD_SEED", str(SEED)))
CLIM_SEED   = int(os.environ.get("C_CLIM_SEED", str(SEED)))
AGENT_SEED  = int(os.environ.get("C_AGENT_SEED", str(SEED)))
LOGEVERY  = int(os.environ.get("C_LOGEVERY", "25"))
GENEVERY  = int(os.environ.get("C_GENEVERY", "200"))     # genome H/relatedness — O(N·L); sample less often
FLUSHEVERY = int(os.environ.get("C_FLUSHEVERY", "500"))  # genealogy CSV flush cadence (bounded memory)
TERR      = os.environ.get("C_TERR", "coastal")
CLIM      = os.environ.get("C_CLIM", "temperate")
TAG       = os.environ.get("C_TAG", "")
GENOME    = os.environ.get("C_GENOME", "1") == "1"
GENEALOG  = os.environ.get("C_GENEA", "1") == "1"        # genealogy CSV stream (off for long cycling runs → save disk/time)
BUD       = os.environ.get("C_BUD", "0") == "1"          # village budding (Bandy 2004): large villages shed rival-led daughters
LEGITTHR  = float(os.environ.get("C_LEGITTHR", "0.15"))  # ascription gate; swept to test ascribed_frac vs EA 3.6-7.8%
BUDHAZ    = os.environ.get("C_BUDHAZ", "0") == "1"       # emergent fission HAZARD (Alberti logistic x Bandy rate)
BUD_THR   = int(os.environ.get("C_BUD_THR", "150"))      # fission threshold (Bandy ~150 open → ~277 circumscribed)
IMPROVED  = os.environ.get("C_IMPROVED", "0") == "1"     # agriculture: cultivable land claimable where WORKED (needs C_DEFEND=1)
SOIL      = os.environ.get("C_SOIL", "0") == "1"         # Layer-B1 soil depletion + terrain-dependent (alluvial) renewal
                                                          #   → rain-fed SWIDDEN oscillator vs HYDRAULIC floodplain
DEFEND    = os.environ.get("C_DEFEND", "1") == "1"       # economic defensibility (Dyson-Hudson & Smith) → instability
                                                          #   signal. NOT in the R-64 validation; toggle off to match it.
CONNUBIUM = os.environ.get("C_CONNUBIUM", "cut1")        # cut1 = fixed-radius seasonal gathering; cut2 = adaptive reach + patriclan exogamy → Wobst ~475
# Cut-2 mate-search pool m*. WAS 50, "probe: m*=50 → median reach 496 ≈ Wobst" — and that anchor was
# RETRACTED by R-67 on 2026-07-13: Wobst 1974's Minimum Equilibrium Size from his own 40 runs is 79–332, and
# the cited 175–475 is an EXTRAPOLATION to 1–2 hex tiers. LITERATURE.md recorded the correction and the
# re-anchor — "re-anchored to MVP (m*≈15)", a ~150-person breeding pool holding ~15 eligible males at φ≈0.1 —
# and MARKER_MATRIX row 4 carries the band as 150 [79–332]. THE CODE NEVER FOLLOWED: this default stayed at
# the retired value for three weeks, so every Cut-2 run since has used the contested number, and battery 7
# measured the consequence (connubium_med 440–2387 against a band of [79, 332], 0/8 arms).
MSTAR     = int(os.environ.get("C_MSTAR", "15"))
ALLON     = os.environ.get("C_ALLON", "0") == "1"        # every BUILT mechanism runs unless explicitly ablated
# T-9: the R-82...R-87 elite/legitimacy stack — see module docstring. C_ALLON implies it when C_ELITE is not
# set, because the elite FLAGS alone are not the elite layer: their magnitudes (leveling_strength,
# material_hide_frac, leader_share_frac, legit_cred_gain/feast_frac, ...) live in ELITE_KW and default to 0.0.
# Before this, `C_ALLON=1` on its own switched ~10 elite mechanisms ON at ZERO STRENGTH — live in the config
# dump, dead in the world, and INERT in any ablation. Battery 7's full-stack arms were exactly that run.
ELITE     = os.environ.get("C_ELITE", "0") == "1" or (ALLON and "C_ELITE" not in os.environ)
BRANCH    = float(os.environ.get("C_BRANCH", "0"))       # R-90/R-92 per-birth SUB-BRANCH tag rate (0 = off, bit-exact)
SPLIT     = float(os.environ.get("C_SPLIT", "0"))        # R-92 per-member per-step lineage SEGMENTATION hazard
SPLITMIN  = int(os.environ.get("C_SPLITMIN", "8"))       # R-92 minimum viable segment (both sides)
RELLEGIT  = os.environ.get("C_RELLEGIT", "0") == "1"     # R-93 scale-free ascription test (share vs band mean)
RELMULT   = float(os.environ.get("C_RELMULT", "2.0"))    # R-93 crossing multiple of an average lineage share
RELRES    = os.environ.get("C_RELRES", "0") == "1"       # R-94 effect-size privilege (scale-free resentment)
RESEFF    = float(os.environ.get("C_RESEFF", "0.8"))     # R-94 reversion effect-size threshold (Cohen "large")
RESACC    = os.environ.get("C_RESACC", "0") == "1"       # R-95 resentment ACCUMULATES (vs merely tracking)
RESVIL    = os.environ.get("C_RESVIL", "0") == "1"       # R-95 the VILLAGE holds the grudge, not the band
RESYTR    = float(os.environ.get("C_RESYTR", "80"))      # R-95 yr to revolt at unit privilege [Leach ~60-100]
LOCASC    = os.environ.get("C_LOCASC", "0") == "1"       # R-96 rank held per (community, lineage), not globally
RANKHIER  = os.environ.get("C_RANKHIER", "0") == "1"     # R-98 ranked lineages unlock a rung of hierarchy
RANKFRAC  = float(os.environ.get("C_RANKFRAC", "0.15"))  # R-98 ascribed head-share counting as "ranked" (~1/7, Hill 2011)
RESIDENCE = os.environ.get("C_RESIDENCE", "")            # R-102 {virilocal|uxorilocal|flexible}; "" = preset default.
                                                          # [Ember & Ember 1971] filed as REFERENCE with "comparisons
                                                          # deferred" -- never swept until now.
MAXMIN    = float(os.environ.get("C_MAXMIN", "0"))       # wall-clock budget in MINUTES; 0 = unlimited.
                                                          # Runtime here scales with POPULATION, not steps: 3000
                                                          # steps cost 16 min at pop 6k (fs3kg) but 173 min at pop
                                                          # 39k (bio_swidden_true). So a rich world can silently
                                                          # turn a "15000-step run" into a multi-day one -- c1bud
                                                          # had to be KILLED at step 11200 ("impractically slow at
                                                          # 29k pop"). A budget converts that manual kill into a
                                                          # clean stop that still writes a valid trajectory.
INEQGATE  = os.environ.get("C_INEQGATE", "0") == "1"     # R-103 stratified requires UNEQUAL wealth (default OFF = bit-exact)
GINIMIN   = float(os.environ.get("C_GINIMIN", "0.40"))   # R-103 within-band cred-Gini floor for stratified [BHM 2009]
ENDOGAMY  = os.environ.get("C_ENDOGAMY", "0") == "1"     # R-103b Flannery class endogamy (assortative-by-cred mating);
ENDOG_A   = float(os.environ.get("C_ENDOG_A", "1.5"))    #   the mechanism that CUTS a noble/commoner break. Default OFF.
MATINHERIT = os.environ.get("C_MATINHERIT", "0") == "1"  # R-103d bequeath durable capital at death (default OFF = dissolves)
MATRULE   = os.environ.get("C_MATRULE", "primogeniture") # none|primogeniture|partible_equal|patrilineal_sons [Goody/EA]
LINTRIB   = os.environ.get("C_LINTRIBUTE", "0") == "1"   # R-103f per-lineage chiefly tribute (default OFF)
TRIBFRAC  = float(os.environ.get("C_TRIBFRAC", "0.15"))  # R-103f share of production the chief levies [gumsa a-thigh]
DELEGIT   = os.environ.get("C_DELEGIT", "1") == "1"      # R-103f test knob: gumsa/gumlao reversion (default ON, bit-exact)
SEED_LAYOUT = os.environ.get("C_SEED_LAYOUT", "cycle")   # "cycle" (legacy, bit-exact) | "cluster"
SEED_CLUSTER = int(os.environ.get("C_SEED_CLUSTER", "25"))
PATCHSZ   = int(os.environ.get("C_PATCH", "0"))          # R-103i CIRCUMSCRIPTION (Carneiro): capacity sub-window
                                                          # size; 0 = the validated default PATCH. NPPCapacityField
                                                          # masks capacity to (X0,Y0,size) with ZERO outside, so a
                                                          # smaller patch = bounded arable land the population
                                                          # cannot disperse out of. SELF-VERIFYING: meta's
                                                          # habitable_cells reports the realised bounded area.
HEIRSTAT  = os.environ.get("C_HEIRSTAT", "0") == "1"     # R-103e primogeniture heir = highest-CRED child (rank+estate together)
NOBLEXEMPT = os.environ.get("C_NOBLEXEMPT", "0") == "1"  # R-103e legitimate nobles EXEMPT from wealth-leveling (Flannery ch.16)
SEDFERT   = os.environ.get("C_SEDFERT", "1") == "1"      # sedentism->fertility boost. DEFAULT ON = bit-exact with
                                                          # every prior campaign. Exposed as an ablation knob for
                                                          # R-103: the flat-tropical 22x residence split is
                                                          # hypothesised to be a concentration->sedentism->fertility
                                                          # feedback; turning this OFF is the direct test.
BAND_SPLIT = 45                                           # village = a band grown past the fission cap (R-55)

# T-9 elite-stack values, at what R-82...R-87 validated. All [DESIGN] except leveling_strength (Boehm 38/48) and
# office_deposition_share/office_overreach_weight (Boehm Table I) and legit_feast/cred_gain/threshold (R-86
# calibrated to Hayden's 75%) — see PARAMETERS §22 and TARGETS T-6. resent_alpha uses R-88's better-measured
# 83-yr arm (correlation time ~22.6 yr on the log-linear estimator, D14) since R-88 found the lag itself does not
# govern the observed dynamics — band churn does — so the exact alpha is no longer the load-bearing choice here.
ELITE_KW = dict(
    enable_material_capture=True, material_hide_frac=0.07, material_decay=0.002, aggrandizer_frac=0.15,
    enable_leader_share=True, leader_share_frac=0.20,
    enable_leveling=True, leveling_strength=0.79, leveling_share=0.8,
    enable_leader_office=True, office_grievance_gain=0.05,
    enable_legitimacy=True, legit_feast_frac=0.25, legit_cred_gain=10.0, legit_threshold=LEGITTHR, legit_decay=0.02,
    enable_delegitimation=DELEGIT, resent_alpha=0.001, resent_threshold=0.5, resent_privilege_ref=10.0,
    enable_relative_legitimacy=RELLEGIT, legit_rel_multiplier=RELMULT,
    enable_relative_resentment=RELRES, resent_effect_threshold=RESEFF,
    enable_resentment_accumulator=RESACC, enable_village_resentment=RESVIL,
    resent_years_to_revolt=RESYTR, enable_local_ascription=LOCASC,
    enable_rank_hierarchy=RANKHIER, rank_hierarchy_frac=RANKFRAC,
) if ELITE else {}

PROG  = os.path.join(HERE, f"campaign_progress{TAG}.txt")
OUT   = os.path.join(HERE, f"campaign_trajectory{TAG}.json")
GENEA = os.path.join(HERE, f"campaign_genealogy{TAG}.csv")


def gini(xs):
    xs = sorted(v for v in xs if v is not None)
    n = len(xs)
    if n < 2:
        return 0.0
    s = sum(xs)
    if s <= 0:
        return 0.0
    cum = sum((i + 1) * v for i, v in enumerate(xs))
    return (2.0 * cum) / (n * s) - (n + 1.0) / n


def society_of(a, w):
    s = w._band_society.get(a._group.band_id)
    if s is None:
        s = w._cell_society.get(a.pos)
    return s or "egalitarian_forager"


def log(msg):
    with open(PROG, "a", encoding="utf-8") as fh:
        fh.write(msg + "\n"); fh.flush()
    print(msg, flush=True)



def _pctl(vals, qs):
    """Percentiles without numpy, on a possibly-empty list. Returns 0.0 for each q when empty and never
    raises: a diagnostic must not be the thing that stops a 15,000-step run."""
    if not vals:
        return [0.0 for _ in qs]
    v = sorted(vals)
    out = []
    for q in qs:
        i = int(round((q / 100.0) * (len(v) - 1)))
        out.append(v[max(0, min(i, len(v) - 1))])
    return out


def snapshot(w, step, menarche, prev_leaders, last_con):
    al = w.agent_list
    pop = len(al)
    sizes = Counter(a._group.band_id for a in al)
    szv = list(sizes.values())
    # BAND SIZE IN ADULTS — the quantity MARKER_MATRIX #1's anchor actually names, and which the model has
    # never logged. Hill et al. 2011's figure is 28.2 ADULTS (32 societies); `band_med` above is ALL AGES.
    # The matrix already records the consequence: "the 23/25 all-ages pass is carried by excess children",
    # and on 2026-08-14 a run read band_med 23 against Birdsell ~25 and looked like a PASS on a population
    # that was 54% children -- about 11 adults, i.e. 0.4x the real anchor. Logging both ends that.
    _adult_m = getattr(w._demog, "menarche_months", 180) if getattr(w, "_demog", None) else 180
    _asz = Counter(a._group.band_id for a in al if a.age >= _adult_m)
    _aszv = list(_asz.values())
    villages = [n for n in szv if n > BAND_SPLIT]
    socs = Counter(society_of(a, w) for a in al)
    cred = [getattr(a, "cred", 1.0) for a in al]
    wealth = [a.wealth for a in al]
    ages = [a.age for a in al]
    # --- elite / dynasty layer -------------------------------------------------
    dyn = w.dynasties(top=5)
    top0 = dyn.get("top", [{}])[0] if dyn.get("top") else {}
    male_rs = [getattr(a, "_n_fathered", 0) for a in al if a.sex == "male" and a.age >= menarche]
    # --- settlement hierarchy --------------------------------------------------
    st = w.settlements()
    # --- mating network + instability + leadership -----------------------------
    con = last_con                                    # most-recent non-empty gathering reach (seasonal → sampled every step)
    ins = w.instability()
    cur_leaders = {bid: ld.unique_id for bid, ld in w.band_leaders().items()}
    common = set(cur_leaders) & set(prev_leaders)
    leader_turnover = round(sum(1 for b in common if cur_leaders[b] != prev_leaders[b]) / len(common), 3) if common else 0.0
    assab = list(w._band_assabiyah.values())
    # R-103 calibration diagnostic: per-band cred Gini, computed HERE independent of the gate so it is visible in
    # every run (gate on OR off). The stratified LABEL should sit on bands whose members are UNEQUAL — this lets
    # the report show whether it does. `strat_band_gini_med` is the median per-band Gini among stratified-labelled
    # bands; if it is LOW while pct_stratified is high, the label is decoupled from inequality (the diagnosed bug).
    _band_cred: dict = {}
    for a in al:
        _band_cred.setdefault(a._group.band_id, []).append(getattr(a, "cred", 1.0))
    _bg = {bid: gini(cs) for bid, cs in _band_cred.items() if len(cs) >= 5}
    _strat_bg = [_bg[bid] for bid in _bg if w._band_society.get(bid) == "stratified_chiefdom"]
    # R-103 re-diagnosis: WITHIN-band gini (_bg) did NOT separate genuine from artifact (all ~0.23). The real
    # axis is BETWEEN-band — do the stratified bands stand ABOVE the rest, or is everyone uniformly affluent?
    _band_mean = {bid: (sum(cs) / len(cs)) for bid, cs in _band_cred.items() if len(cs) >= 5}
    _between_gini = gini(list(_band_mean.values()))                     # inequality ACROSS band means
    _strat_ids = [bid for bid in _band_mean if w._band_society.get(bid) == "stratified_chiefdom"]
    _oth_ids = [bid for bid in _band_mean if bid not in _strat_ids]
    _strat_mu = (sum(_band_mean[b] for b in _strat_ids) / len(_strat_ids)) if _strat_ids else 0.0
    _oth_mu = (sum(_band_mean[b] for b in _oth_ids) / len(_oth_ids)) if _oth_ids else 0.0
    _strat_lift = round(_strat_mu / _oth_mu, 3) if _oth_mu > 0 else 0.0   # >1 ⇒ stratified bands really are richer
    # R-103b — FLANNERY'S BREAK. Rank is a CONTINUUM; stratification is a GAP between an endogamous noble stratum
    # and commoners (Flannery ch.16). Gini measures the continuum's SPREAD and cannot see the gap — so here we
    # measure, WITHIN each village, the noble/commoner cred separation as Cohen's d (reusing R-99's privilege
    # effect idea). d≈0 = one continuum (rank); d large = two separated strata (a real break). The mechanism that
    # should CUT the gap is class endogamy (enable_ascribed_mate_choice); this diagnostic runs regardless so ON/OFF
    # can be compared. `frac_bands_broken` = share of BANDS whose nobles stand a LARGE effect above commoners.
    _rk = w._rank_keys() if hasattr(w, "_rank_keys") else {}
    _asc = getattr(w, "_lineage_ascribed", set())
    _band_noble: dict = {}; _band_comm: dict = {}
    for a in al:
        (_band_noble if _rk.get(a) in _asc else _band_comm).setdefault(a._group.band_id, []).append(getattr(a, "cred", 1.0))

    def _cohen_d(x, y):
        if len(x) < 3 or len(y) < 3:
            return None
        mx, my = statistics.mean(x), statistics.mean(y)
        vx, vy = statistics.pvariance(x), statistics.pvariance(y)
        sp = ((vx + vy) / 2.0) ** 0.5
        return (mx - my) / sp if sp > 1e-9 else 0.0

    _dvals = []
    for bid in _band_mean:                     # villages with >=5 members
        d = _cohen_d(_band_noble.get(bid, []), _band_comm.get(bid, []))
        if d is not None:
            _dvals.append(d)
    _village_gap_d_med = round(statistics.median(_dvals), 3) if _dvals else 0.0
    _frac_villages_broken = round(sum(1 for d in _dvals if d >= 0.8) / len(_dvals), 3) if _dvals else 0.0
    # R-103c — WHAT IS AN ELITE MADE OF? Three currencies, three very different Flannery meanings:
    #   cred     = prestige/renown  → the BIG-MAN currency (achieved by feasting; Flannery ch.6/10)
    #   material = durable capital  → the CHIEF currency (accumulated + INHERITED estate; Flannery ch.16)
    #   food     = perishable reserve (wealth) → subsistence, neither
    # And two ways to be "elite": by LINEAGE (ascribed → should carry a HERITABLE estate if chiefs exist) vs by
    # OFFICE (current leader → a lifetime perquisite if big-men). A big-man regime shows a LEADER lift in cred but
    # NO ascribed-LINEAGE lift in material (nothing crosses generations). A chiefly regime shows a heritable
    # material lift on the noble LINEAGE. Lift = elite mean / commoner mean (1.0 = no advantage). This is the
    # instrument that was missing: every prior diagnostic read cred only, so material stratification was invisible.
    _mat = [getattr(a, "material", 0.0) for a in al]
    _ldr_ids = {ld.unique_id for ld in w.band_leaders().values()} if hasattr(w, "band_leaders") else set()
    _nob = [a for a in al if _rk.get(a) in _asc]; _com = [a for a in al if _rk.get(a) not in _asc]
    _lead = [a for a in al if a.unique_id in _ldr_ids]; _nonl = [a for a in al if a.unique_id not in _ldr_ids]

    def _lift(grp, ref, attr):
        if not grp or not ref:
            return 0.0
        rm = statistics.mean(getattr(a, attr, 0.0) for a in ref)
        return round(statistics.mean(getattr(a, attr, 0.0) for a in grp) / rm, 3) if rm > 1e-9 else 0.0
    # R-103g — WEALTH-IN-PEOPLE. Does the noble lineage hold more PEOPLE (the non-decaying, self-reproducing
    # accumulation form; Guyer; Nieboer-Domar: elites in LAND-ABUNDANT worlds control persons, not goods)? We have
    # measured every GOODS currency and found the lineage flat; this asks whether the chiefly elite has been
    # sitting in FOLLOWERS all along (the R-103c 'wrong currency' trap, one axis over). Diagnostic only, no mechanism.
    _lin_size: dict = {}
    for a in al:
        k = _rk.get(a)
        _lin_size[k] = _lin_size.get(k, 0) + 1

    def _people_lift(grp, ref, fn):
        if not grp or not ref:
            return 0.0
        rm = statistics.mean(fn(a) for a in ref)
        return round(statistics.mean(fn(a) for a in grp) / rm, 3) if rm > 1e-9 else 0.0
    _nm = [a for a in _nob if a.sex == "male" and a.age >= menarche]
    _cm = [a for a in _com if a.sex == "male" and a.age >= menarche]
    _lin_of = lambda a: _lin_size.get(_rk.get(a), 1)                 # size of the agent's lineage (corporate following)
    _wives_of = lambda a: len(getattr(a, "_wives", ()))
    _kids_of = lambda a: getattr(a, "_n_fathered", 0)
    # Regional density needs the HABITABLE area, which is the capacity patch's land — not the grid. The
    # campaign stashes it on the world at construction so the snapshot can reach it.
    _hab = getattr(w, "_habitable_cells", 0)
    _regional_dens = (pop / (_hab * 100.0)) if _hab else 0.0
    row = dict(
        step=step, pop=pop, births=w.births_this_step, deaths_starv=w.deaths_starv_this_step,
        mean_reserve=round(statistics.mean(wealth) / w._reserve_full, 3) if pop else 0,
        juv_frac=round(sum(1 for x in ages if x < 180) / pop, 3) if pop else 0,   # <15 yr (dependency proxy)
        mean_age_yr=round(statistics.mean(ages) / 12.0, 1) if pop else 0,
        n_bands=len(sizes), band_med=statistics.median(szv) if szv else 0, band_max=max(szv) if szv else 0,
        band_med_adults=statistics.median(_aszv) if _aszv else 0,   # vs Hill 2011's 28.2 ADULTS
        band_max_adults=max(_aszv) if _aszv else 0,
        # RENAMED from n_villages/village_med/village_max (R-106, 2026-08-04). These count BANDS with more
        # than `BAND_SPLIT` members — a social unit of any spatial extent — NOT settlements. `settle_med`
        # below is the settlement-site measure, and it is what MARKER_MATRIX scores against Bar-Yosef
        # 50-150. Two files already carried comments warning about the mix-up rather than fixing the name.
        n_bigbands=len(villages), bigband_med=round(statistics.median(villages), 1) if villages else 0,
        bigband_max=max(villages) if villages else 0,
        pct_complex=round(100 * socs.get("complex_forager", 0) / pop, 1) if pop else 0,
        pct_stratified=round(100 * socs.get("stratified_chiefdom", 0) / pop, 1) if pop else 0,
        # R-101: the THIRD rung was only ever implied by subtraction, which makes a cross-tab impossible
        pct_egalitarian=round(100 * socs.get("egalitarian_forager", 0) / pop, 1) if pop else 0,
        n_band_egal=sum(1 for v in w._band_society.values() if v == "egalitarian_forager"),
        n_band_complex=sum(1 for v in w._band_society.values() if v == "complex_forager"),
        n_band_strat=sum(1 for v in w._band_society.values() if v == "stratified_chiefdom"),
        gini_cred=round(gini(cred), 3), gini_wealth=round(gini(wealth), 3),
        band_cred_gini_med=round(statistics.median(_bg.values()), 3) if _bg else 0.0,   # R-103 calibration
        strat_band_gini_med=round(statistics.median(_strat_bg), 3) if _strat_bg else 0.0,
        n_strat_bands=len(_strat_bg),
        between_band_gini=round(_between_gini, 3),      # R-103: inequality ACROSS bands (the real discriminator?)
        strat_lift=_strat_lift,                         # stratified-band mean cred / other-band mean cred (>1 = real)
        # RENAMED from village_gap_d_med/frac_villages_broken/n_villages_gapd (R-106): the loop that builds
        # `_dvals` iterates over BANDS with >=5 members, not settlements. R-103b's Flannery claim about "the
        # share of villages with a noble/commoner break" is a per-BAND statistic.
        band_gap_d_med=_village_gap_d_med,              # R-103b Flannery: median noble/commoner Cohen's d per BAND
        frac_bands_broken=_frac_villages_broken,        #   share of BANDS with a LARGE (d>=0.8) noble/commoner break
        n_bands_gapd=len(_dvals),
        # R-103c elite currency breakdown — LINEAGE (ascribed) lift vs OFFICE (leader) lift, per currency
        noble_cred_lift=_lift(_nob, _com, "cred"), noble_material_lift=_lift(_nob, _com, "material"),
        noble_food_lift=_lift(_nob, _com, "wealth"),
        # R-103g wealth-in-PEOPLE: does the noble lineage hold more followers/wives/children than commoners?
        noble_lineage_size_lift=_people_lift(_nob, _com, _lin_of),
        noble_wives_lift=_people_lift(_nm, _cm, _wives_of), noble_fathered_lift=_people_lift(_nm, _cm, _kids_of),
        lineage_size_gini=round(gini(list(_lin_size.values())), 3),
        leader_cred_lift=_lift(_lead, _nonl, "cred"), leader_material_lift=_lift(_lead, _nonl, "material"),
        leader_food_lift=_lift(_lead, _nonl, "wealth"),
        gini_material=round(gini(_mat), 3), mean_material=round(statistics.mean(_mat), 2) if _mat else 0.0,
        frac_ascribed_pop=round(len(_nob) / pop, 3) if pop else 0.0,
        surplus_med=round(statistics.median(list(w._band_surplus.values())), 3) if w._band_surplus else 0,
        surplus_max=round(max(w._band_surplus.values()), 3) if w._band_surplus else 0,
        assab_med=round(statistics.median(assab), 3) if assab else 0,
        # elite / dynasty
        n_lineages=dyn.get("n_lineages", 0), lin_top_share=dyn.get("top_share", 0),
        lin_size_gini=dyn.get("size_gini", 0), eff_lineages=dyn.get("eff_lineages", 0),
        dom_dyn_rs=top0.get("rs"), dom_dyn_related=top0.get("relatedness"),
        male_rs_gini=round(gini(male_rs), 3),
        # R-90: the FILED Hill 2011 per-band target (~7 lineages/band, dom-share 0.38) — R-25 passed it, the
        # R-89 lineage collapse broke it, and it is the calibration read-out for lineage_branch_rate
        lineages_per_band=dyn.get("lineages_per_band", 0), dom_lineage_share=dyn.get("dom_lineage_share", 0),
        # settlement hierarchy
        n_settle=st.get("n", 0), settle_med=st.get("median", 0), settle_max=st.get("max", 0),
        bud_events=getattr(w, "bud_events", 0),   # CUMULATIVE fissions -> the realised rate, scored against
        #                                            Bandy's 2-5e-3 per large-village-year
        primate_ratio=st.get("primate_ratio"), zipf_slope=st.get("zipf_slope"),
        # mating + instability + leadership
        connubium_med=con.get("median"), connubium_p90=con.get("p90"),
        claim_events=ins.get("claim_events", 0), cells_owned=ins.get("n_owned", 0),
        leader_turnover=leader_turnover,
        # ── DIAGNOSTICS ADDED 2026-08-11 (task: diagnose the bistable-regime split, R-66/R-97 re-test). Every
        # field below was ALREADY COMPUTED by the model, every step, and discarded — group A is 12 counters that
        # existed since their own R-numbers; group B is two new FLOW counters (formed/released settlements,
        # bud_events per step, vs the pre-existing cumulative-only bud_events); group C summarizes soil/hardship
        # state that sat in per-site dicts nothing ever read. None of this changes model behaviour.
        # A — elite/instability/lineage flows, unconditional (initialized every step() regardless of which
        # flags are on, so these are always numeric, never None)
        deaths_senesc=w.deaths_senesc_this_step, deaths_orphan=w.deaths_orphan_this_step,
        leveling_events=w.leveling_events_this_step, depositions=w.depositions_this_step,
        desertions=w.desertions_this_step, challenges=w.challenges_this_step,
        feast_spend=round(w.feast_spend_this_step, 2), legitimated=w.legitimated_this_step,
        reversions=w.reversions_this_step, lineage_branches=w.lineage_branches_this_step,
        lineage_splits=w.lineage_splits_this_step, lineage_tribute=round(w.lineage_tribute_this_step, 2),
        # B — settlement FLOW (the stock n_settle already existed; the rate that produces it did not)
        settle_formed=w.settle_formed_this_step, settle_released=w.settle_released_this_step,
        bud_events_step=w.bud_events_this_step,          # per-step twin of the cumulative bud_events above
        frac_resident=st.get("frac_resident", 0.0),      # share of the WHOLE population living on a settlement site
    )
    # C — soil depletion (B1) + emergent-abandonment hardship memory, per settlement site. {} when neither flag
    # has ever fired; defaulted to 0.0 so the column stays numeric across the whole trajectory.
    _sh = w.settlement_health()
    row.update(
        soil_mean=_sh.get("soil_mean", 0.0), soil_min=_sh.get("soil_min", 0.0),
        soil_frac_depleted=_sh.get("soil_frac_depleted", 0.0),
        hardship_mean=_sh.get("hardship_mean", 0.0), hardship_max=_sh.get("hardship_max", 0.0),
    )
    # ── MARKER MATRIX (2026-07-27) ──────────────────────────────────────────────────────────────
    # These quantities were all COMPUTED by demography() and none of them reached a campaign
    # trajectory, so no long run has ever scored them. Several are anchored targets that have gone
    # unmeasured for the entire project; polygyny in particular sat 15x off Marlowe unnoticed
    # because nothing carried it forward. Cost is one demography() pass per snapshot, i.e. per
    # C_LOGEVERY steps, which is negligible beside the step loop.
    _dg = w.demography()
    # Realised life table + fertility schedule. Read defensively: several harnesses and tests drive an older
    # TerrainWorld, and a diagnostic must never be the thing that crashes a 15,000-step run.
    _lt = w.life_table() if hasattr(w, "life_table") else {}
    _fs = w.fertility_schedule() if hasattr(w, "fertility_schedule") else {}
    _sp = w.starvation_profile() if hasattr(w, "starvation_profile") else {}
    _vr = w.vital_rates() if hasattr(w, "vital_rates") else {}
    _fam = w.family_structure() if hasattr(w, "family_structure") else {}
    _mb = _lt.get("m_by_band", {})
    _sx = w.life_table_by_sex() if hasattr(w, "life_table_by_sex") else {}
    _cf = w.cohort_fertility() if hasattr(w, "cohort_fertility") else {}
    # Energy-signal distribution over WOMEN OF REPRODUCTIVE AGE — the population any energetic fertility
    # mechanism acts on. Read defensively: an older TerrainWorld, or a run with the intake signal off, must
    # not crash a 15,000-step campaign over a diagnostic.
    _dm = getattr(w, "_demog", None)
    _hi = getattr(_dm, "intake_fert_hi", 1.2) if _dm else 1.2
    _burn = getattr(w, "_burn", 0.0)
    _ema, _raw = [], []
    if _dm is not None:
        for _a in w.agent_list:
            if _a.sex != "female" or not (_dm.menarche_months <= _a.age < _dm.menopause_months):
                continue
            _ema.append(float(getattr(_a, "_intake_ema", 1.0)))
            _rq0 = _burn * _a.consumption_factor()
            _raw.append(float(_a._last_intake / _rq0) if _rq0 > 0 else 1.0)
    _iq = _pctl(_ema, (10, 50, 90))
    _rq = _pctl(_raw, (10, 50, 90))
    _elo = (sum(1 for v in _ema if v < _hi) / len(_ema)) if _ema else 0.0
    _rlo = (sum(1 for v in _raw if v < _hi) / len(_raw)) if _raw else 0.0
    row.update(
        # REPRODUCTION / MATING — the channel that drives every dynastic marker downstream
        frac_polygynous_m=round(_dg.get("frac_polygynous_m", 0.0), 4),   # Marlowe (Hadza) ~0.04
        mean_wives_married_m=round(_dg.get("mean_wives_married_m", 0.0), 3),
        frac_paired_adult_f=round(_dg.get("frac_paired_adult_f", 0.0), 3),
        # DEMOGRAPHIC ENGINE — a marker read on a steeply growing population means something
        # different from one read at stationarity, so these travel WITH the others by design.
        median_age_yr=round(_dg.get("median_age_yr", 0.0), 2),
        dependency_ratio=round(_dg.get("dependency_ratio", 0.0), 3),
        sex_ratio_m_f=round(_dg.get("sex_ratio_m_f", 0.0), 3),
        frac_child=round(_dg.get("frac_child", 0.0), 3),
        frac_motherless=round(_dg.get("frac_motherless", 0.0), 4),       # Aché ~0.02 (Hill & Hurtado)
        frac_fatherless=round(_dg.get("frac_fatherless", 0.0), 4),
        # AGE PYRAMID + MATING SUITABILITY (R-106, 2026-08-04). The SHAPE distinguishes a growing from a
        # declining population and the coarse child/adult/elder split cannot; and `frac_unpaired_adult` is
        # the φ that `LITERATURE.md` assumes is ≈0.1 when it derives `mate_search_min_eligible ≈ 15` from
        # White's ~150-person MVP. Nothing measured it — it is 0.012 — so the derivation went unchecked
        # (Addendum 25). These travel on every row so a marker is never read without the structure that
        # produced it.
        age_0_5=round(_dg.get("age_0_5", 0.0), 4),
        age_5_15=round(_dg.get("age_5_15", 0.0), 4),
        age_15_30=round(_dg.get("age_15_30", 0.0), 4),
        age_30_45=round(_dg.get("age_30_45", 0.0), 4),
        age_45_60=round(_dg.get("age_45_60", 0.0), 4),
        age_60_plus=round(_dg.get("age_60_plus", 0.0), 4),
        pyramid_base_ratio=round(_dg.get("pyramid_base_ratio", 0.0), 3),
        growth_regime=_dg.get("growth_regime", "n/a"),
        # THE REALISED SCHEDULES (R-106, 2026-08-12). The age pyramid above says WHAT the structure is; these
        # say WHY. The model is configured with ACHE_FOREST (e0 36.6 yr) and a ceiling TFR of 9, and the age
        # structure implies it realises e0 ~ 19 — so the two schedules are different objects and only the
        # realised one explains a run. Both cumulative over the run; difference two rows for a period rate.
        #   realised_e0        vs the CONFIGURED 36.6. A gap here IS the age-structure failure.
        #   realised_tfr       vs Hill & Hurtado Table 8.1's 8.031 [VERIFIED], ceiling 9.
        #   realised_ibi_med   vs Table 8.2's 37.6 forest / 49.4 contact / 34.4 reservation [VERIFIED].
        #   fert_factor_sat    the share of at-risk women whose fertility multiplier is ~1.0. Near 1.0 means
        #                      the energetic brake is decorative — the failure `enable_energetic_fertility`
        #                      already had, and the reason `enable_intake_fertility` replaced it.
        #   starv_share        how much of the mortality is the Malthusian brake rather than the life table.
        realised_e0=round(_lt.get("e0", 0.0), 2),
        realised_tfr=round(_fs.get("tfr", 0.0), 3),
        realised_ibi_med=round(_fs.get("ibi_median", float("nan")), 1),
        realised_ibi_mean=round(_fs.get("ibi_mean", float("nan")), 1),
        realised_ibi_n=int(_fs.get("ibi_n", 0)),
        fert_factor_mean=round(_fs.get("factor_mean", float("nan")), 4),
        fert_factor_sat=round(_fs.get("factor_saturated", float("nan")), 4),
        starv_share=round(_lt.get("starv_share", 0.0), 4),
        # THE a2 MODULATOR, FACTOR BY FACTOR. Only the PRODUCT was ever visible, and it runs ~2.2x the
        # configured Siler in the 5-15 band. `risk_mult` is anchored (accidents ~10% of HG deaths, so it
        # should sit near 1.1); `density_mult` was shown near-neutral once the ceiling was repaired; the
        # nutrition synergy is 1 + (mu_max-1)*(1-condition) with mu_max 2.5, so it reaches 2.5x at zero
        # body condition. Whichever of these carries the inflation is the next thing to fix, and the
        # product alone can never say which.
        a2_mean=round((w.a2_total_sum / w.a2_n) if getattr(w, "a2_n", 0) else float("nan"), 3),
        a2_risk_mean=round((w.a2_risk_sum / w.a2_n) if getattr(w, "a2_n", 0) else float("nan"), 3),
        a2_dens_mean=round((w.a2_dens_sum / w.a2_n) if getattr(w, "a2_n", 0) else float("nan"), 3),
        a2_syn_mean=round((w.a2_syn_sum / w.a2_n) if getattr(w, "a2_n", 0) else float("nan"), 3),
        condition_mean=round((w.a2_cond_sum / w.a2_n) if getattr(w, "a2_n", 0) else float("nan"), 4),
        a2_cap_hits=int(getattr(w, "a2_cap_hits", 0)),
        # ── THE STANDING DEMOGRAPHY PANEL (supervisor request 2026-08-13) ────────────────────────────────
        # "We cannot expect social dynamics to work when the demography is skewed." Today's example: band_med
        # read 23 against Birdsell ~25 and looked like a pass, on a population that was 54% CHILDREN — about
        # 11 adults against Hill 2011's 28.2 ADULTS. The marker read as passing while failing 2.5-fold,
        # because nothing scored the age structure beside it. These travel on EVERY row so that can't recur.
        #
        # ANCHORS, all Gurven & Kaplan 2007 Table 2, Aché forest [VERIFIED]:
        #   e15 = 38.5 remaining yr   e45 = 21.1   l(15) = 0.66   l(45) = 0.43   modal adult death = 71
        # e15 IS THE HEADLINE, NOT e0. e0 is dominated by infant mortality — the cross-forager e0 range is
        # 21-37 while e15 sits near 38 everywhere — so e0 alone confounds child with adult survival.
        # NOTE THE DENOMINATOR: the published "survival 15→45 = 0.43" is l(45) FROM BIRTH. Compare
        # `surv_to_45` against it; `surv_15_to_45_cond` (0.65) is the conditional and is NOT that anchor.
        e15=round(_lt.get("e15", float("nan")), 2),
        e45=round(_lt.get("e45", float("nan")), 2),
        surv_to_15=round(_lt.get("surv_to_15", float("nan")), 3),
        surv_to_45=round(_lt.get("surv_to_45", float("nan")), 3),
        surv_15_to_45_cond=round(_lt.get("surv_15_to_45_cond", float("nan")), 3),
        modal_adult_death=round(_lt.get("modal_adult_death", float("nan")), 1),
        # MORTALITY BY AGE GROUP — the hazard beside the population share the age pyramid already reports.
        m_0_1=round(_mb.get("0_1", float("nan")), 4), m_1_5=round(_mb.get("1_5", float("nan")), 4),
        m_5_15=round(_mb.get("5_15", float("nan")), 4), m_15_30=round(_mb.get("15_30", float("nan")), 4),
        m_30_45=round(_mb.get("30_45", float("nan")), 4), m_45_60=round(_mb.get("45_60", float("nan")), 4),
        m_60_plus=round(_mb.get("60_plus", float("nan")), 4),
        # VITAL RATES — per 1000 person-years, from the run's OWN exposure, so they cannot drift from the
        # life table beside them the way a hand-differenced growth rate can.
        cbr=round(_vr.get("cbr", float("nan")), 2), cdr=round(_vr.get("cdr", float("nan")), 2),
        r_pct_yr=round(_vr.get("r_pct_yr", float("nan")), 3),
        srb_male_frac=round(_vr.get("srb_male_frac", float("nan")), 4),   # vs the configured srb_male 0.512
        age_first_birth_yr=round(_vr.get("age_first_birth_yr", float("nan")), 2),
        # FAMILY STRUCTURE. frac_motherless and frac_fatherless are reported SEPARATELY above, so a child
        # that lost BOTH was counted once in each and never as itself — the highest-hazard group in the R-74
        # orphan work. And frac_unpaired_adult pools the widowed with the never-married, which are different
        # phenomena: near-universal marriage puts never-partnered-by-30 close to zero, widowhood is common.
        frac_both_parents_alive=round(_fam.get("frac_both_parents_alive", float("nan")), 4),
        frac_double_orphan=round(_fam.get("frac_double_orphan", float("nan")), 4),
        frac_partial_parent_link=round(_fam.get("frac_partial_parent_link", float("nan")), 4),
        frac_never_partnered_30=round(_fam.get("frac_never_partnered_30", float("nan")), 4),
        frac_widowed_adult=round(_fam.get("frac_widowed_adult", float("nan")), 4),
        frac_partnered_adult=round(_fam.get("frac_partnered_adult", float("nan")), 4),
        # SEX-SPLIT LIFE TABLE. The model runs a sex-split Siler and nothing checked the realised split; a
        # pooled table averages the two schedules and hides a sex-specific defect entirely.
        e0_female=round(_sx.get("e0_female", float("nan")), 2),
        e0_male=round(_sx.get("e0_male", float("nan")), 2),
        e15_female=round(_sx.get("e15_female", float("nan")), 2),
        e15_male=round(_sx.get("e15_male", float("nan")), 2),
        e0_gap_f_minus_m=round(_sx.get("e0_gap_f_minus_m", float("nan")), 2),
        # COHORT vs SYNTHETIC fertility. realised_tfr is synthetic; completed parity is what women actually
        # bore. They agree only at stationarity, so the DIVERGENCE reads whether the run is in steady state.
        completed_parity_mean=round(_cf.get("completed_parity_mean", float("nan")), 2),
        completed_parity_med=round(_cf.get("completed_parity_med", float("nan")), 1),
        frac_parity_zero=round(_cf.get("frac_parity_zero", float("nan")), 4),
        n_completed_parity=int(_cf.get("n_completed", 0)),
        # DEPENDENCY SPLIT — the halves move in opposite directions and the combined ratio hides it.
        dependency_child=round(_dg.get("dependency_child", float("nan")), 3),
        dependency_old=round(_dg.get("dependency_old", float("nan")), 3),
        # THE ENERGY SIGNAL'S OWN DISTRIBUTION (R-106, 2026-08-13). `fert_factor_sat` says the brake is
        # saturated; it cannot say BY HOW FAR, and that is what decides whether ANY energetic mechanism can
        # work. The physiological window is [intake_fert_lo, intake_fert_hi] = [1.0, 1.2], anchored to FAO/IOM
        # (pregnancy +11%, lactation +20%). If the signal sits at 3x that window, every mechanism keyed to it
        # pins at one end — which killed the fecundability brake and would equally kill a refractory keyed the
        # same way. BOTH forms travel: the EMA is what a mechanism reads, the RAW ratio is what the EMA erases.
        intake_ema_p10=round(_iq[0], 3), intake_ema_p50=round(_iq[1], 3), intake_ema_p90=round(_iq[2], 3),
        intake_raw_p10=round(_rq[0], 3), intake_raw_p50=round(_rq[1], 3), intake_raw_p90=round(_rq[2], 3),
        intake_raw_frac_below_hi=round(_rlo, 4), intake_ema_frac_below_hi=round(_elo, 4),
        # WHO STARVES, AND WHERE (R-106, 2026-08-13). Every field above samples the LIVING, so the starved
        # are absent from all of them — and a third of deaths are starvation in a population whose 10th
        # percentile eats 1.65x its requirement. `compute_harvest_shares` gives an occupant S/n, so intake is
        # set by LOCAL occupancy: `starv_occ_at_death` far above `starv_occ_of_living` means agents starve
        # because they CROWD (a DISTRIBUTION fault), the two equal means the cells are simply too poor or the
        # reserve too thin (a SUPPLY fault). `occ_of_living` is weighted per AGENT, not per cell.
        starv_occ_at_death=round(_sp.get("occ_at_death", float("nan")), 2),
        starv_occ_of_living=round(_sp.get("occ_of_living", float("nan")), 2),
        starv_age_at_death=round(_sp.get("age_at_death_yr", float("nan")), 2),
        starv_intake_at_death=round(_sp.get("intake_at_death", float("nan")), 3),
        starv_ema_at_death=round(_sp.get("ema_at_death", float("nan")), 3),
        starv_fedres_at_death=round(_sp.get("fedres_at_death", float("nan")), 3),   # reserve fraction step before death
        starv_frac_acute=round(_sp.get("frac_acute", float("nan")), 3),            # share of deaths that were 1-step crashes
        cells_occupied=int(_sp.get("cells_occupied", 0)),
        mean_occ_per_cell=round(_sp.get("mean_occ_per_cell", float("nan")), 2),
        lt_deaths_total=int(_lt.get("deaths", 0)),
        lt_exposure_py=round(_lt.get("exposure_py", 0.0), 1),
        adult_sex_ratio=round(_dg.get("adult_sex_ratio", 0.0), 3),
        frac_unpaired_adult=round(_dg.get("frac_unpaired_adult", 0.0), 4),
        frac_unpaired_adult_m=round(_dg.get("frac_unpaired_adult_m", 0.0), 4),
        operational_sex_ratio=round(_dg.get("operational_sex_ratio", 0.0), 3),
        # WEALTH CONCENTRATION — the direct test of "does material accrue to the elite"
        material_gini=round(_dg.get("material_gini", 0.0), 4),
        material_top10_share=round(_dg.get("material_top10_share", 0.0), 4),
        wealth_gini=round(_dg.get("wealth_gini", 0.0), 4),
        corr_cred_material=round(_dg.get("corr_cred_material", 0.0), 4),
        # TWO densities, because they answer different questions and only one is scoreable against the
        # ethnographic anchors. `occupied` is mean occupancy per SETTLED cell (local crowding); `regional`
        # is population over the HABITABLE LAND, which is what Hayden Fig. 6, Binford packing (0.091/km²)
        # and Tallavaara (0.1-0.5) all measure. The occupied measure runs a median 2.3x higher (up to 20x in
        # a dispersed savanna world) and moved the Hayden band in 6 of 8 long arms, so `hayden_stage` is
        # scored on the regional one.
        density_occupied_per_km2=round(_dg.get("density_occupied_per_km2", 0.0), 5),
        density_regional_per_km2=round(_regional_dens, 5),
        hayden_stage=w._hayden_stage(_regional_dens) if _regional_dens > 0 else "n/a",
        hayden_stage_occupied=_dg.get("hayden_stage_occupied", "n/a"),
    )
    # STATUS -> REPRODUCTIVE SUCCESS (von Rueden & Jaeggi: r ~= 0.19 cross-system, ~0.15 monogamous).
    # R-77 showed the model's old +0.170 was an ARTIFACT of 6x excess polygyny, so this must be
    # re-measured on the corrected stack rather than carried over.
    _m = [a for a in w.agent_list if a.sex == "male" and a.age >= menarche]
    if len(_m) > 8:
        _x = [getattr(a, "prowess", 1.0) for a in _m]
        _y = [float(getattr(a, "_n_fathered", 0)) for a in _m]
        _mx, _my = sum(_x) / len(_x), sum(_y) / len(_y)
        _sx = sum((v - _mx) ** 2 for v in _x) ** 0.5
        _sy = sum((v - _my) ** 2 for v in _y) ** 0.5
        row["status_rs_r"] = (round(sum((a - _mx) * (b - _my) for a, b in zip(_x, _y)) / (_sx * _sy), 4)
                              if _sx > 0 and _sy > 0 else None)
    else:
        row["status_rs_r"] = None
    if step % GENEVERY == 0 and GENOME:
        g = w.genetics(sample_pairs=1500)
        row["heterozygosity"] = round(g.get("heterozygosity", 0.0), 4)
        row["mean_relatedness"] = round(g.get("mean_relatedness", 0.0), 4)
    if ELITE:                                          # T-9: legitimacy/office readout, cheap (O(bands)/O(agents))
        lg = w.legitimacy()
        gs = w.gumsa_state()
        t = w.leader_tenure()
        row["ascribed_frac"] = round(lg.get("ascribed_frac_pop", 0.0), 3)
        row["frac_gumsa"] = round(gs.get("frac_gumsa", 0.0), 3)
        row["leader_tenure_yr"] = round(t.get("mean_years", 0.0), 1)
        row["leader_levy"] = round(w.leader_levy_this_step, 1)
        ld = w.leadership()                              # R-101: origins of rule, not just its duration
        row["office_lineages"] = ld["office_lineages"]
        row["office_top_share"] = ld["office_top_share"]
        row["office_dynastic"] = ld["office_dynastic"]
        row["office_repeat_lin"] = ld["office_repeat_lin"]
        row["mean_resentment"] = round(gs.get("mean_resentment", 0.0), 3)    # R-89: was invisible before —
        row["max_resentment"] = round(gs.get("max_resentment", 0.0), 3)      # couldn't tell "stuck" from "climbing"
    return row, cur_leaders


def main():
    open(PROG, "w").close()
    if os.path.exists(GENEA):
        os.remove(GENEA)                                 # fresh genealogy stream per run
    # PROVENANCE. Addendum 19 retracted two conclusions because a control had been produced by a different
    # build, and the fix was to record `meta.sha` and gate on it. But HEAD alone does not identify a build when
    # the tree is DIRTY: a run started from uncommitted edits records the parent commit, so a sha gate accepts
    # it as the same build as a run of the committed code. That is the same hole, one level down. Record the
    # dirty bit too, and say so loudly — a swept arm from a dirty tree is not reproducible from its sha.
    _repo = os.path.join(HERE, "..", "..", "..")
    try:
        sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=_repo).decode().strip()
        dirty = bool(subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=no"],
                                             cwd=_repo).decode().strip())
    except Exception:
        sha, dirty = "?", True
    if dirty:
        print(f"campaign: !! WORKING TREE DIRTY at {sha} -- this arm is NOT identified by its sha and must "
              f"not be paired against an arm from a clean tree. Commit before running a comparison.",
              flush=True)
    k = world_lottery_climate(WORLD_SEED, terrain=TERR, climate=CLIM)   # the PLANET
    # RUNOFF-WEIGHTED RIVERS ADOPTED (2026-08-22). The river pass allocated `flow = ones()` -- one unit per
    # cell regardless of rainfall -- so `isRiver` was pure drainage AREA with no water balance and, measured
    # across 20 worlds, DESERTS CAME OUT 1.63x WETTER THAN FORESTS (0.075 vs 0.046). That propagated:
    # aquatic_food scored desert rivers as cold anadromous fisheries, S_pot ranked desert 0.413 > grass 0.404
    # > forest 0.259, and villages settled the desert at 2.5x enrichment. Weighting the accumulation by
    # Budyko (1974) runoff -- VERIFIED and filed, parameter-free -- reverses that to forest 0.283 > grass
    # 0.228 > desert 0.171 and the river ratio to 0.49.
    k["runoff_rivers"] = True
    f = generate_world(k, mode="climate")
    _patch = (X0, Y0, PATCHSZ if PATCHSZ > 0 else PATCH)     # R-103i: shrink ⇒ circumscription
    base = NPPCapacityField(f, BURN, patch=_patch, mode="tallavaara", aquatic=True, enable_depletion=True)
    base0 = NPPCapacityField(f, BURN, patch=_patch, mode="tallavaara", aquatic=True, enable_depletion=True)
    land = [(x, y) for y in range(100) for x in range(100) if f.isWater[y, x] == 0 and base0.level(x, y) > 0]

    # EMPTY, AND THAT IS THE POINT. `enable_caribou_swing` sat here from 2026-08-06 morning as the one channel
    # excluded for being UNVERIFIABLE — its amplitude and period were credited to a thesis nobody could open.
    # The supervisor filed it the same afternoon, it was read, and it VERIFIED the amplitude while FALSIFYING
    # the period band (we carried 40–90 yr; the observed range is 23–67). Corrected and switched on the same
    # day (Addendum 32). Any future entry here needs a reason from MECHANISM_CHARTER §12's list of four.
    _CLIMATE_UNSOURCED: set = set()

    # CLIMATE (R-106). This line used to be `ClimateField(base, a_seas=0.4, regime_driver=None)`, which took
    # the constructor's 0.0 default for every other channel — so the ENSO interannual, the regime telegraph,
    # the caribou herd swing and the llanos flood were built, unit-tested, and NEVER IN A RUN. Every result
    # this project has produced had a fixed seasonal sine and white noise, and no multi-year environmental
    # variability at any timescale, which is why the no-cycles findings need the narrower reading.
    #   C_CLIMATE=0   the FLAT-CLIMATE CONTROL: fixed seasonal sine, no interannual variability at any
    #                 timescale. This is what every run before 2026-08-06 used, so it is the arm that
    #                 reproduces the historical results and the one a climate ablation compares against.
    #   C_CLIM_ON / C_CLIM_OFF   comma-separated channel names, for testing one at a time
    #   C_CLIMPARAM   field=value for the climate values, like C_PARAM for demography
    #
    # DEFAULT FLIPPED 2026-08-06: climate is now ON unless explicitly controlled off. The old default was the
    # flat world, which meant the entire variability layer sat out every experiment this project ran while
    # reading as "built" — including four separate searches for Malthusian and secular cycles conducted with
    # the slow environmental driver switched off. A control has to be CHOSEN, not inherited by default.
    clim = ClimateConfig()
    # EARTH CLIMATE IS THE DEFAULT (2026-08-22, supervisor: "let's set Earth climate as a default condition
    # for now. The variations belong to a later stage, when everything works well already.")
    # This default was "1" -- every climate channel ON -- on the reasoning quoted above that a control must be
    # CHOSEN rather than inherited. That reasoning stands, and the choice has now been made the other way:
    # the baseline is Earth and variability is opted INTO with C_CLIMATE=1.
    # WHY IT MATTERS, measured: a_seas is drawn per world from an obliquity lottery, eps ~ U[0,60] deg, and
    # seed 0 -- which EVERY canonical run uses -- draws eps 50.7 deg giving a_seas 0.779, the second highest
    # of twelve seeds against a median 0.464 and Earth 0.4. At 0.779 an arid cell yields 0.44 BURN at the
    # seasonal trough against a lone adult's requirement of 1.0, so the world cannot feed anyone for part of
    # every year and four separate mechanism-level fixes failed against that floor. The amplitude is also NOT
    # anchored: `obliquity_to_amplitude` calls itself "a PROVISIONAL bounding heuristic ... NOT a
    # sunlight-to-food transfer function". ClimateConfig's own class defaults ARE the Earth baseline
    # (a_seas 0.4, every variability channel off), so this simply stops overriding them.
    if os.environ.get("C_CLIMATE", "0") == "1":
        clim = clim.model_copy(update={f: True for f in type(clim).model_fields
                                       if f.startswith("enable_") and f not in _CLIMATE_UNSOURCED})
    for _var, _on in (("C_CLIM_ON", True), ("C_CLIM_OFF", False)):
        _names = [s.strip() for s in os.environ.get(_var, "").split(",") if s.strip()]
        if _names:
            _bad = [f for f in _names if f not in type(clim).model_fields]
            if _bad:
                raise SystemExit(f"{_var}: unknown climate field(s) {_bad}")
            clim = clim.model_copy(update={f: _on for f in _names})
            print(f"campaign: {_var} {'enabled' if _on else 'disabled'} {','.join(_names)}", flush=True)
    _cp = [s.strip() for s in os.environ.get("C_CLIMPARAM", "").split(",") if s.strip()]
    if _cp:
        _cu = {}
        for _item in _cp:
            _key, _val = _item.split("=", 1)
            _key = _key.strip()
            if _key not in type(clim).model_fields:
                raise SystemExit(f"C_CLIMPARAM: unknown climate field {_key!r}")
            _ann = type(clim).model_fields[_key].annotation
            _cu[_key] = {int: int, float: float, bool: lambda s: s.lower() in ("1", "true")}.get(
                _ann, str)(_val.strip())
        clim = clim.model_copy(update=_cu)
        print("campaign: C_CLIMPARAM " + ", ".join(f"{a}={b}" for a, b in _cu.items()), flush=True)
    # `fields=f` supplies the GRASS sub-biome masks C.4b/C.4c need; without them those layers are inert at
    # any amplitude, and `build_climate_field` raises rather than running them dead.
    cap = build_climate_field(base, clim, fields=f, seed=CLIM_SEED)   # the climate realisation
    if SEED_LAYOUT == "cluster":
        # CAPACITY-AWARE CLUSTER SEEDING. Two constraints pull opposite ways and both must hold:
        #   MATE GATE   phase1_model F.1 requires a co-resident adult male for a birth, so founders spread
        #               one-per-cell can never reproduce -- the cycle layout's failure mode in poor worlds.
        #   CAPACITY    a cell that feeds 2 people cannot host a band of 25, or everyone starves at step 1.
        # So: group founders into clusters of `seed_cluster_size` (the band anchor), and lay each cluster over
        # as many neighbouring cells as its own local capacity requires -- tight enough to mate, thin enough
        # to eat. Cells are taken best-capacity-first, so clusters land on the ABUNDANT ground.
        _rank = sorted(land, key=lambda c: -cap.level(c[0], c[1]))
        _head = {c: max(1, int(cap.level(c[0], c[1]) // BURN)) for c in _rank}
        _free = dict(_head)
        pos = []
        _ci = 0
        while len(pos) < FOUNDERS and _ci < len(_rank):
            _cx, _cy = _rank[_ci]; _ci += 1
            if _free.get((_cx, _cy), 0) <= 0:
                continue
            _near = sorted((c for c in _rank
                            if max(abs(c[0] - _cx), abs(c[1] - _cy)) <= 3 and _free.get(c, 0) > 0),
                           key=lambda c: -cap.level(c[0], c[1]))
            # ROUND-ROBIN, ONE PER CELL FIRST -- not fill-to-capacity. Filling each cell to its headroom put
            # 21 founders on the single richest arid cell and the probe went extinct at step 18, FASTER than
            # the one-per-cell layout's step 29. The mate gate's own comment says a band "spreads ~1/cell over
            # its territory", and `bonded_mate_radius = 1` means a mother needs an unrelated adult male inside
            # her 3x3. So the target is a COMPACT BLOCK AT ~1/CELL: every member has neighbours inside the
            # mate radius, while local density stays far below what the cell can feed.
            _placed = 0
            for _c in _near:                       # ONE PASS, at most ONE founder per cell
                if _placed >= SEED_CLUSTER or len(pos) >= FOUNDERS:
                    break
                if _free.get(_c, 0) <= 0:
                    continue
                pos.append(_c)
                _free[_c] = 0                      # this cell is spent for seeding purposes
                _placed += 1
        if len(pos) < FOUNDERS:                       # world too small to hold them within capacity
            pos.extend(land[i % len(land)] for i in range(FOUNDERS - len(pos)))
        _occ = {}
        for _c in pos:
            _occ[_c] = _occ.get(_c, 0) + 1
        log(f"campaign: seed_layout=cluster -> {len(pos)} founders on {len(_occ)} cells "
            f"(max {max(_occ.values())}/cell, clusters of {SEED_CLUSTER})")
    else:
        pos = [land[i % len(land)] for i in range(FOUNDERS)]
    cut2 = (CONNUBIUM == "cut2")
    demog = emergent_village_demog().model_copy(update=dict(
        # SCALED FAMILY FOOTPRINT ADOPTED (2026-08-22). `comove_footprint = 0` is "exact snap": every
        # co-moving family collapses onto ONE cell, so the annual pairing gate halved the occupied-cell count
        # in a single step (110 -> 75, occupancy 1.07 -> 1.56). Two competing explanations were falsified
        # first -- ablating the annual drought shock and ablating band_cohesion each left it untouched.
        # `comove_footprint_scaled` gives k proportional to 1/NPP on the Kelly/Binford shape already used by
        # mobility_radius, which is k = 0 on EVERY rich world (bit-exact with the exact snap) and k = 2-3
        # only where the land is poor. It was built, anchored and dark.
        comove_footprint_scaled=True,
        enable_landscape_packing=True, enable_sedentism_fertility=SEDFERT,
        enable_marriage_aggregation=True, enable_aggregation_sedentism=True,
        enable_catchment_ceiling=True, enable_settlement_scalar_stress=True, settle_catchment_radius=1,
        enable_aggl_ceiling=(os.environ.get("C_AGGLCEIL", "1") == "1"),   # R-105 bugfix; C_AGGLCEIL=0 reproduces the gap
        enable_economic_defensibility=DEFEND,
        enable_stratification_inequality_gate=INEQGATE, stratification_gini_min=GINIMIN,   # R-103
        enable_ascribed_mate_choice=ENDOGAMY, ascribed_mate_strength=(ENDOG_A if ENDOGAMY else 0.0),  # R-103b endogamy
        enable_material_inheritance=MATINHERIT, material_inheritance_rule=MATRULE,   # R-103d bequest
        material_heir_by_status=HEIRSTAT,                                            # R-103e estate follows rank
        enable_noble_leveling_exemption=NOBLEXEMPT,                                  # R-103e ch.16 exemption
        enable_lineage_tribute=LINTRIB, lineage_tribute_frac=TRIBFRAC,               # R-103f chiefly tribute
        enable_adaptive_connubium=cut2, mate_search_min_eligible=(MSTAR if cut2 else 3),
        enable_exogamy=cut2, exogamy_degree="lineage",
        enable_village_budding=BUD, enable_bud_hazard=BUDHAZ, village_fission_threshold=BUD_THR,
        enable_improved_land=IMPROVED,
        enable_soil_depletion=SOIL, enable_alluvial_renewal=SOIL,
        enable_emergent_abandonment=(SOIL and os.environ.get("C_ABANDON", "0") == "1"),
        enable_genome=GENOME, genome_loci=48, enable_genealogy_log=GENEALOG,
        enable_lineage_branching=(BRANCH > 0.0), lineage_branch_rate=BRANCH,
        enable_lineage_split=(SPLIT > 0.0), lineage_split_rate=SPLIT, lineage_split_min_segment=SPLITMIN,
        # R-102: post-marital residence. Applied HERE and not in ELITE_KW because residence is a property of the
        # SUBSTRATE, not of the elite layer -- an elite-off arm still has one, and burying it inside the elite
        # dict would silently pin every non-elite run to the preset default.
        **({"aggregation_residence": RESIDENCE} if RESIDENCE else {}),
        **ELITE_KW))
    # C_ALLON (R-106 Addendum 12, 2026-07-31): the supervisor rule is that every BUILT mechanism runs unless it
    # is off for an ablation. An audit found 27 of 79 `enable_*` flags dark in the canonical preset, and only
    # ~10 of them have a C_* knob here, so a campaign could not exercise the rest at all. C_ALLON=1 turns on
    # every remaining built mechanism EXCEPT four with stated reasons; it is applied LAST so an explicit C_*
    # knob above always wins. Default off => byte-identical to every prior campaign.
    if os.environ.get("C_ALLON", "0") == "1":
        _skip = {
            # `enable_infanticide` used to be skipped here as a "documented UNIMPLEMENTED STUB". The flag is
            # DELETED (2026-08-06) — it needed no special case once it stopped existing.
            "enable_genealogy_log",                  # observer/logging, not a dynamic; costly
            # §12 UNDER EVALUATION — added 2026-08-06 by the ON-but-dead gate, which caught C_ALLON turning
            # both of these ON while their magnitudes sat at 0.0. They had been reading as live mechanisms in
            # every config dump since the audit began. Neither gets an invented value here:
            #   pathogen_gamma          has a real anchor (Cashdan 2014 biome disease-ecology) and its own
            #                           comment says "sweep low/mid/high". The sweep has never been run;
            #                           picking a number without it is the exact sin this arc documents.
            #   malnutrition_fission_gain  was deliberately zeroed to serve as the R-106 NEGATIVE CONTROL, and
            #                           behaved correctly as one. The flag should have been off, not the gain.
            "enable_terrain_pathogen",
            "enable_malnutrition_fission",
            "enable_bud_hazard",                     # mutually-exclusive alternate to the legacy budding path
            "enable_stratification_inequality_gate", # R-103: criterion known wrong, parked for supervisor call
            # `enable_band_risk` used to be skipped here as a MEASURED DEAD END: loner-mortality does not
            # produce an optimal band size, it culls (pop 281->64, mean band 56->5 -- a death spiral, F.2
            # prototype run_3i). Its magnitude defaulted to 0.0 behind a `> 0.0` guard, so C_ALLON was turning
            # it ON into a no-op -- "on" in the dump, inert in every ablation. DELETED 2026-08-06: a flag whose
            # only two states are "does nothing" and "kills the population" is not a flag. The finding is kept
            # in DemographyConfig where the fields used to be.
            # A CANDIDATE UNDER EVALUATION, not a built mechanism awaiting activation. `enable_leaky_assabiyah`
            # changes assabiyah from a constant-leak integrator (no interior fixed point — bang-bang by
            # construction) to a leaky one whose fixed point tracks surplus. It is measured and defensible
            # (RESULTS Addendum 23) but NOT adopted, and it only restores the cohesion headroom in company
            # with an unanchored `cohesion_leader_weight`. C_ALLON turning it on would have adopted a
            # structural model change by side effect — which is the exact class of accident this whole audit
            # has been about. Remove this line when the supervisor adopts it.
            "enable_leaky_assabiyah",
            # SETTLEMENT-RUNAWAY CANDIDATES UNDER EVALUATION (2026-08-12). Four rules built while diagnosing
            # the budding runaway; NONE is adopted, and each is measured but not yet chosen, so C_ALLON must
            # not enable them by side effect — the same accident `enable_leaky_assabiyah` is excluded for.
            #   enable_bud_site_separation           WORKS but imposes 5 cells = 50 km, against Vita-Finzi &
            #                                        Higgs 1970's ~10 km forager catchment radius (~20 km for
            #                                        disjoint catchments). Rejected on the anchor; retained
            #                                        only as the "geometry alone" ablation control.
            #   enable_exclusive_village_membership  removes the mutual subsidy as designed, but produces NO
            #                                        spacing on its own and raises churn (buds 978 -> 1366).
            #   enable_bud_requires_occupancy        ADOPTED (R-106 Addendum 53, 2026-08-26). Closes the
            #                                        budding bypass so village spacing is EMERGENT from
            #                                        disjoint catchments (no distance constant); matches the
            #                                        imposed bud_site_separation rule bit-for-bit and raises
            #                                        population. Removed from this set -> canonically ON.
            #   enable_village_identity              ADOPTED (R-106 Addendum 54, 2026-08-28) after the
            #                                        multi-biome A/B its hold was gated on. In tropical,
            #                                        temperate AND boreal every marker moves the same way:
            #                                        median age 21.7/17.5/16.0 -> 26.4/18.8/20.7, TFR into
            #                                        band, l15 up, starvation down, and merged villages of
            #                                        ~90-107 replace the 45-bands artifact. It does not drain
            #                                        population: temperate and boreal were LEAKING without it
            #                                        (-104, -105 on the tail) and are healthy with it (+259,
            #                                        +6). Removed from this set -> canonically ON.
            # bud_site_separation stays as the imposed-geometry ablation control, mutually exclusive in spirit
            # with the adopted emergent spacing.
            "enable_bud_site_separation",
            "enable_exclusive_village_membership",
            # ACUTE-DISPERSAL / FOUNDING-DELAY CANDIDATES UNDER EVALUATION (R-106, 2026-08-28..09-02). Both
            # are BUILT and CTB'd but EQUIVOCAL, so C_ALLON must not adopt them by side effect (the same
            # accident excluded above). Each has a measured reason to hold:
            #   enable_hunger_dispersal   Colson-1979 famine flight: a low reserve breaks the residence pin.
            #                             It improves the demography markers (connubium re-forms, IBI toward
            #                             anchor) and resolves the packing paradox, but roughly HALVES the
            #                             canonical population and empties the degenerate savanna world. The
            #                             loss is fertility (band fragmentation), not death. Not yet chosen.
            #   enable_founding_delay     hold pioneer founding a startup generation so founders spread first.
            #                             Marginal on the demography and trips the age-structure CTB through a
            #                             startup transient; no literature anchor for the delay length yet.
            # Remove a line here when the supervisor adopts that mechanism.
            "enable_hunger_dispersal",
            "enable_founding_delay",
            # VILLAGE CATCHMENT SPREAD candidate under evaluation (R-106, 2026-09-02). BUILT + CTB'd and it
            # fixes the over-clustering cleanly (peak single-cell occupancy stays ~70 at pop 5,000, vs 150-300
            # packed) by dispersing settled members across the village territory. BUT the density-disease hazard
            # at packed cells was the de-facto Malthusian brake: spreading the bodies removes it and population
            # RUNS AWAY (571 -> 5,134 by step 1,200, accelerating, no plateau, density still below anchor).
            # Over-clustering and the population ceiling are coupled through the density channel; the spread
            # needs a replacement brake before it can be adopted. HELD until that is built + validated.
            "enable_village_catchment_spread",
            # SETTLEMENT PAIR ADOPTED (R-106, 2026-09-05, docs/RESULTS Addendum 61). `enable_colonizing_budding`
            # and `enable_village_density_disease` are removed from this set -> canonically ON. Together they give
            # dispersed settlement (spacing ~2.3 cells) at a STATIONARY population (small-world plateau confirmed)
            # with realistic village size and sound genealogy. Neither works alone: colonizing runs away without
            # the village-scaled disease brake; the disease brake alone stays trapped-sparse without colonization.
            # `enable_bud_requires_occupancy` (adopted Addendum 53) is SUPERSEDED by the pair — the colonizing path
            # founds daughters directly with its own density-scaled spacing, so occupancy-gating is retired here
            # (it trapped the population at 2% of carrying capacity).
            "enable_bud_requires_occupancy",
            # AGE-GRADED NUTRITION SYNERGY adopted (R-106, 2026-09-05, Addendum 64). Removed from this set ->
            # canonically ON. Adults use the attenuated malnutrition-mortality synergy (community-dwelling adult
            # HR ~1.3 vs Pelletier child 2.5). A/B: adult mortality 15-45 fell 21%, e0 +0.8; the rest is absorbed
            # by Malthusian growth (the deep e0 gap is the food ceiling, not this calibration).
            # R-103 RELATIONAL STRATIFICATION adopted (R-106, 2026-09-05, Addendum 62). Removed from this set
            # -> canonically ON. The between-band inequality gate replaces the level-only classifier that
            # over-counted stratified villages (36% at between-band Gini 0.14). Stratification now emerges only
            # at maturity, when the regional between-band Gini crosses 0.30 (calibrated to the model's range).
            # A MODEL CORRECTION UNDER EVALUATION (2026-08-13). `enable_density_reference` re-references
            # density_mult so the anchor density returns 1.0 -- the invariant risk_mult and pathogen_mult
            # already hold and this one silently broke. It is measured and principled, but adopting it
            # changes the realised mortality of EVERY run, so C_ALLON must not take it by side effect.
            # Remove this line when the supervisor adopts it.
            #
            # `enable_density_reference` AND `enable_energetic_refractory` WERE REMOVED FROM THIS LIST on
            # 2026-08-15, by supervisor challenge: "you build stuff, flag them off, then wonder why things
            # don't work." Both had been parked here reflexively rather than for a stated reason.
            #   density_reference is a BUG FIX -- density_mult lacked the reference normalisation that
            #     risk_mult and pathogen_mult both hold. The carrying-capacity ceiling bug of 2026-08-14 was
            #     fixed DIRECTLY with no flag at all, so flagging an equally clear correction was simply
            #     inconsistent.
            #   energetic_refractory is anchored (Ellison 2008, Toba C-peptide) and brought realised_tfr
            #     INTO band. A mechanism that moves a marker into band should not sit dark because a bracket
            #     endpoint has not been swept yet; the sweep is a refinement, not a precondition.
            # THE STANDING RULE THIS RESTORES is the one at the head of this block: every BUILT mechanism
            # runs unless it is off for an ablation. This list is for genuine ALTERNATIVES and KNOWN-BROKEN
            # candidates -- not a place to defer a decision the evidence already supports. The audit that
            # created C_ALLON found 27 of 79 flags dark and nobody knew; adding to that pile silently is the
            # failure it exists to prevent.
        }
        # Flags a C_* knob above decides, mapped to the env var(s) that decide them, PLUS the companion
        # parameters that have to move with the flag for it to mean anything.
        #
        # THE BUG THIS REPLACES (2026-08-04). The first version was a flat set of names that C_ALLON skipped
        # UNCONDITIONALLY, so a knob's DEFAULT silently overrode "everything on". `C_ALLON=1` on its own left
        # ten mechanisms dark — adaptive_connubium, exogamy, ascribed_mate_choice, material_inheritance,
        # noble_leveling_exemption, lineage_tribute, lineage_branching, lineage_split, improved_land,
        # emergent_abandonment — because their knobs default to off. Battery 7's "full stack" arms passed only
        # C_ALLON=1, so that is the stack its results describe; `connubium_med` failed there with the adaptive
        # connubium switched OFF. The rule now is the intended one: an EXPLICITLY SET knob wins (an ablation is
        # respected), an UNSET knob does not (a default is not an ablation).
        #
        # `model_fields_set` cannot be used for this: the preset is itself built with model_copy(), so 74
        # fields are already "set" and the guard would swallow nearly everything. This table is explicit.
        _knob_controlled = {
            "enable_sedentism_fertility":      (("C_SEDFERT",), {}),
            "enable_aggl_ceiling":             (("C_AGGLCEIL",), {}),
            "enable_economic_defensibility":   (("C_DEFEND",), {}),
            "enable_genome":                   (("C_GENOME",), {}),
            "enable_village_budding":          (("C_BUD",), {}),
            "enable_material_inheritance":     (("C_MATINHERIT",), {}),
            "enable_noble_leveling_exemption": (("C_NOBLEXEMPT",), {}),
            "enable_lineage_tribute":          (("C_LINTRIBUTE",), {}),
            "enable_soil_depletion":           (("C_SOIL",), {}),
            "enable_alluvial_renewal":         (("C_SOIL",), {}),
            # Abandonment is the swidden half of soil: without it soil depletes and villages never relocate
            # (R-71's frozen-settlement case), so it follows C_SOIL as well as its own knob.
            "enable_emergent_abandonment":     (("C_SOIL", "C_ABANDON"), {}),
            # Improved land needs defensibility to claim worked cells (the guard below already warns).
            "enable_improved_land":            (("C_IMPROVED",), {}),
            # COMPANION PARAMETERS. A flag whose scale stays at its off-value is ON-but-dead — the exact
            # defect class this arc keeps finding — so C_ALLON supplies each one's validated value:
            #   ascribed_mate_strength  C_ENDOG_A's default (R-103b)
            #   mate_search_min_eligible  Cut-2's m*=50 (probe: median reach 496 ≈ Wobst 475)
            #   lineage_branch/split rates  the R-90/R-92 elite-stack values; their knob defaults are 0.0,
            #                               i.e. "off", so inheriting the default would enable a dead flag.
            "enable_ascribed_mate_choice":     (("C_ENDOGAMY",), {"ascribed_mate_strength": ENDOG_A}),
            "enable_adaptive_connubium":       (("C_CONNUBIUM",), {"mate_search_min_eligible": MSTAR}),
            "enable_exogamy":                  (("C_CONNUBIUM",), {"exogamy_degree": "lineage"}),
            "enable_lineage_branching":        (("C_BRANCH",), {"lineage_branch_rate": 0.05}),
            "enable_lineage_split":            (("C_SPLIT",), {"lineage_split_rate": 0.00003,
                                                               "lineage_split_min_segment": 8}),
        }
        # The T-9 elite layer is governed as a BLOCK by C_ELITE, because its magnitudes live together in
        # ELITE_KW. C_ALLON implies C_ELITE (see the ELITE definition above), so these are already True by the
        # time this runs; listing them here is what makes an explicit `C_ELITE=0` a real ABLATION — without
        # it C_ALLON would switch each flag back on at its 0.0 default, i.e. on-but-dead, which is worse than
        # either state.
        for _ef in ("enable_material_capture", "enable_leader_share", "enable_leveling",
                    "enable_leader_office", "enable_legitimacy", "enable_delegitimation",
                    "enable_relative_legitimacy", "enable_relative_resentment",
                    "enable_resentment_accumulator", "enable_village_resentment",
                    "enable_local_ascription", "enable_rank_hierarchy"):
            _knob_controlled[_ef] = (("C_ELITE",), {})
        _on: dict = {}
        for _flag in type(demog).model_fields:
            if not _flag.startswith("enable_") or _flag in _skip or getattr(demog, _flag):
                continue
            _envs, _companions = _knob_controlled.get(_flag, ((), {}))
            if any(e in os.environ for e in _envs):
                continue                       # an explicitly set knob is an ablation; C_ALLON respects it
            _on[_flag] = True
            _on.update(_companions)
        if _on:
            demog = demog.model_copy(update=_on)
        _newflags = sorted(f for f in _on if f.startswith("enable_"))
        print(f"campaign: C_ALLON enabled {len(_newflags)} mechanism(s): "
              f"{','.join(f.replace('enable_', '') for f in _newflags)}", flush=True)
        _still_off = sorted(f for f in type(demog).model_fields
                            if f.startswith("enable_") and not getattr(demog, f))
        print(f"campaign: C_ALLON left {len(_still_off)} OFF: "
              f"{','.join(f.replace('enable_', '') for f in _still_off)}", flush=True)
    # ── C_CFGSRC — THE FILES AS THE SOURCE OF TRUTH (R-106 step B, 2026-08-06) ────────────────────────────
    # Until now `config/*.toml` MIRRORED a run: `tools/gen_runconfig.py` executes this script with C_ALLON=1
    # and records the resolved `meta.demography_config`. The files were authoritative to READ and powerless to
    # SET, so "edit the file, get that run" was not actually true.
    #
    #   C_CFGSRC=files   the run's base config is LOADED from config/*.toml; C_PARAM / C_EXTRA_ON /
    #                    C_EXTRA_OFF still apply on top, so an ablation is still expressible
    #   C_CFGSRC=preset  (default) the historical Python-preset path, bit-exact
    #
    # MEASURED EQUIVALENCE: the file and a `C_ALLON=1` run agree on **all 279 fields, zero differences**, so
    # loading the file reproduces the canonical arm exactly. `test_config_is_load_bearing.py` pins that.
    #
    # WHY `preset` IS STILL THE DEFAULT, and this is a decision for the supervisor rather than a technical
    # gap: a PLAIN run and the canonical file differ in **52 fields** — the whole elite layer, village budding,
    # soil depletion, intake fertility and ~30 other flags are off in a plain run and on in the file. Flipping
    # the default would silently convert every ad-hoc run, probe and quick check into the full canonical stack.
    # That is arguably what "nothing stays off" implies, but it changes what every existing invocation does,
    # which is a scientific call and not a refactor.
    if os.environ.get("C_CFGSRC", "preset") == "files":
        from sic_games import runconfig as _rc0
        demog = _rc0.build("DemographyConfig")
        print(f"campaign: C_CFGSRC=files — base config LOADED from {_rc0.CONFIG_DIR} "
              f"(C_PARAM/C_EXTRA_* still apply on top)", flush=True)

    # C_EXTRA_ON: comma-separated `enable_*` names to turn on, for ATTRIBUTING an all-on effect to a subset.
    # Addendum 12 measured all-on scoring worse on 3 of 6 markers, and 23 flags cannot be attributed from one
    # contrast; this enables group bisection (one group added on top of the baseline at a time). UNKNOWN NAMES
    # RAISE rather than being ignored -- a typo here would silently run the baseline and read as a clean null,
    # which is the exact failure mode this arc has already hit three times. Default unset => no-op.
    _extra = [s.strip() for s in os.environ.get("C_EXTRA_ON", "").split(",") if s.strip()]
    if _extra:
        _bad = [f for f in _extra if f not in type(demog).model_fields]
        if _bad:
            raise SystemExit(f"C_EXTRA_ON: unknown config field(s) {_bad}")
        demog = demog.model_copy(update={f: True for f in _extra})
        print(f"campaign: C_EXTRA_ON enabled {len(_extra)} flag(s): {','.join(_extra)}", flush=True)
    # C_EXTRA_OFF: the mirror of C_EXTRA_ON, applied AFTER it — turn named `enable_*` flags OFF. This is what
    # a mechanism AUDIT needs: ablate one flag OUT of the full stack and see whether the world changes, which
    # is the only way to tell a LIVE mechanism from an INERT one in the context it actually runs in. Unknown
    # names RAISE for the same reason as C_EXTRA_ON: a typo would silently leave the full stack intact and
    # every mechanism would score INERT — a clean, wrong, and very convincinganswer.
    _off = [s.strip() for s in os.environ.get("C_EXTRA_OFF", "").split(",") if s.strip()]
    if _off:
        _bad = [f for f in _off if f not in type(demog).model_fields]
        if _bad:
            raise SystemExit(f"C_EXTRA_OFF: unknown config field(s) {_bad}")
        demog = demog.model_copy(update={f: False for f in _off})
        print(f"campaign: C_EXTRA_OFF disabled {len(_off)} flag(s): {','.join(_off)}", flush=True)
    # C_PARAM: "field=value,field=value" for NUMERIC calibration, the counterpart of C_EXTRA_ON/OFF for the
    # 231 non-flag parameters. Needed because re-fitting a calibrated constant (e.g. `cv_safe`, documented as
    # "the ONE fitted scale") against its own anchor is ordinary work, and adding a bespoke C_* knob per
    # parameter is how the configuration became unreadable in the first place. Unknown fields RAISE, values
    # are parsed to the field's declared type, and the whole set is ECHOED so a swept run cannot be mistaken
    # for a default one. Unset => no-op.
    _pv = [s.strip() for s in os.environ.get("C_PARAM", "").split(",") if s.strip()]
    if _pv:
        _upd = {}
        # NB the underscore names: this loop runs INSIDE `main()`, where `k` is already bound to the terrain
        # knob dict (line ~402) and `f` to the generated WorldFields. The first version used `k, v = ...`,
        # which rebound the terrain knobs to the string "cv_safe" — and since `k` is not read again until the
        # TerrainWorld constructor 30 lines later, every C_PARAM run died there with a bare
        # `'str' object has no attribute 'get'`, 24 arms deep into a sweep. Loop variables in a long function
        # body are not free.
        for _item in _pv:
            if "=" not in _item:
                raise SystemExit(f"C_PARAM: expected field=value, got {_item!r}")
            _key, _val = _item.split("=", 1)
            _key = _key.strip()
            if _key not in type(demog).model_fields:
                raise SystemExit(f"C_PARAM: unknown config field {_key!r}")
            ann = type(demog).model_fields[_key].annotation
            try:
                _upd[_key] = {int: int, float: float, bool: lambda s: s.lower() in ("1", "true")}.get(
                    ann, str)(_val.strip())
            except Exception as _e:
                raise SystemExit(f"C_PARAM: cannot parse {_val!r} for {_key} ({ann}): {_e}")
        demog = demog.model_copy(update=_upd)
        print("campaign: C_PARAM " + ", ".join(f"{a}={b}" for a, b in _upd.items()), flush=True)
    # AGGLOMERATION SHAPE knobs (R-106 Addendum 14). The production form is the measured driver of the spatial
    # concentration, so it must be sweepable from a campaign to confirm a single-seed result on the full
    # worlds x seeds envelope (MARKER_MATRIX binding rule 3). Unset => untouched/bit-exact.
    #   C_AGGLMODE  "point" (Bettencourt, per-capita rises without bound) | "catchment" (congestible common-
    #               pool, per-capita peaks then falls ~1/n; DEAD_ENDS DE-11, kept for comparison)
    #   C_AGGLHALF  the catchment saturation scale; C_AGGLBETA the point-mode exponent.
    _agmode = os.environ.get("C_AGGLMODE", "")
    if _agmode:
        if _agmode not in ("point", "catchment"):
            raise SystemExit(f"C_AGGLMODE: expected 'point' or 'catchment', got {_agmode!r}")
        demog = demog.model_copy(update=dict(aggl_mode=_agmode))
    if os.environ.get("C_AGGLHALF"):
        demog = demog.model_copy(update=dict(aggl_half=float(os.environ["C_AGGLHALF"])))
    if os.environ.get("C_AGGLBETA"):
        demog = demog.model_copy(update=dict(aggl_beta=float(os.environ["C_AGGLBETA"])))
    if _agmode or os.environ.get("C_AGGLHALF") or os.environ.get("C_AGGLBETA"):
        print(f"campaign: agglomeration shape mode={demog.aggl_mode} beta={demog.aggl_beta} "
              f"half={demog.aggl_half}", flush=True)
    # ── THE RUN FILE SUPPLIES THE MODEL, WHOLE ─────────────────────────────────────────────────────────────
    # Applied at the END, and it REPLACES rather than merges. Everything above — the preset, C_ALLON, the
    # C_EXTRA/C_PARAM overlays — is the layered path, and it cannot have contributed anything here because
    # mixing was refused at import. So this is not "the file wins a precedence contest"; it is the only
    # source that ran. `runspec.build` re-applies the ON-but-dead check, so a file cannot express an inert
    # mechanism that the knob path would have refused.
    if _SPEC is not None:
        demog = _runspec.build(_SPEC, "DemographyConfig")
        clim = _runspec.build(_SPEC, "ClimateConfig")
        # R-106 (2026-08-17): SubstrateConfig comes from the RUN FILE too. It used to be hardcoded at the
        # construction site with `**GRP` imported from a 2026 one-off script, so the four grouping-drive
        # parameters -- the single strongest force in the model's spatial behaviour, worth a 20.6x penalty for
        # leaving a band -- could not be stated or varied by a run file at all. Verified bit-exact against the
        # hardcoded construction before this line was added.
        # REFUSE, DO NOT SILENTLY SUBSTITUTE. Run files authored before 2026-08-17 predate SubstrateConfig
        # being in the schema, so building one from them yields CLASS defaults: enabled=False,
        # contest_exponent=0.0, group_safety_max=0.0. That would not merely change the grouping drives -- it
        # would switch the substrate OFF entirely and silently invalidate the arm, while the run looked
        # perfectly healthy and carried a config file that "described" it. Caught before any arm was run.
        _sub_missing = [f for f in ("enabled", "contest_exponent", "group_safety_max", "group_mate_min")
                        if f not in _SPEC.parameters and f not in _SPEC.mechanisms]
        if _sub_missing:
            raise SystemExit(
                f"{_SPEC.path.name} predates SubstrateConfig in the run schema and does not state "
                f"{', '.join(_sub_missing)}.\n"
                f"Building one anyway would give enabled=False and contest_exponent=0.0 -- the substrate "
                f"OFF -- and the run would look perfectly healthy.\n"
                f"Regenerate it:  py -3 tools/make_runconfig.py {_SPEC.path.stem} ...")
        _SUB = _runspec.build(_SPEC, "SubstrateConfig")
        _missing = _runspec.coverage(_SPEC)
        if _missing:
            raise SystemExit(f"{_SPEC.path.name} does not state {len(_missing)} field(s): {_missing[:8]} — "
                             f"a resolved run file lists EVERY field, or the run silently takes a code "
                             f"default for the rest. Regenerate with tools/make_runconfig.py.")
        cap = build_climate_field(base, clim, fields=f, seed=CLIM_SEED)   # the climate realisation
        print(f"campaign: CONFIG = {_SPEC.path} ({_SPEC.name}) — "
              f"{len(_SPEC.mechanisms)} mechanisms, {len(_SPEC.parameters)} parameters, "
              f"0 unstated", flush=True)

    # ON-BUT-DEAD GATE (2026-08-06, MECHANISM_CHARTER §12). The config is now FINAL — check it before a single
    # step runs. A flag that is on while the magnitude it acts through sits at neutral reads as a live
    # mechanism in the dump and does nothing in the world; it produced 3 of battery 7's 6 "inert" verdicts and
    # cost R-85 a whole follow-up study. Ablate by turning the FLAG off, never by zeroing the magnitude.
    from sic_games import runconfig as _rc
    _dead = _rc.dead_flags({_f: getattr(demog, _f) for _f in type(demog).model_fields},
                           set(type(demog).model_fields))
    if _dead:
        raise SystemExit("campaign: ON-but-dead mechanism(s) in the final config:\n  " + "\n  ".join(_dead)
                         + "\n  Turn the flag off to ablate, or give the magnitude a value.")

    w = TerrainWorld(n_agents=FOUNDERS, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, game_stream=False, seed=AGENT_SEED,
                     carbon_cfg=CarbonConfig(kappa=1.5),
                     substrate_cfg=(_SUB if _SPEC is not None else
                                    SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                                    contest_exponent=1.5, move_cost_flat=0.0,
                                                    enable_capacity_scaled_grouping=True, **GRP)),
                     harvest_field=cap, placement_positions=pos, demography_cfg=demog)
    w._habitable_cells = len(land)   # the denominator for regional density (read by snapshot)
    menarche = demog.menarche_months
    # R-101: dump the FULL demography config, not a curated subset. A finished run must carry enough to answer
    # questions nobody asked before it started — the previous 16 hand-picked keys omitted residence,
    # patriline_weight and the society preset, so a post-hoc question about descent or residence could not even
    # establish which setting the run had used.
    try:
        _full_cfg = demog.model_dump()
    except Exception:
        _full_cfg = {k: getattr(demog, k) for k in dir(demog) if not k.startswith("_")}
    _full_cfg = {k: v for k, v in _full_cfg.items() if isinstance(v, (int, float, str, bool, type(None)))}
    # R-106 (2026-08-17): DUMP THE RESOLVED SubstrateConfig TOO. `tools/gen_runconfig.py` derives
    # config/parameters.toml by ASKING A CANONICAL RUN what it uses (resolved_canonical), and it looks the
    # answer up per owner class. Only `demography_config` was ever dumped, so SubstrateConfig fell back to
    # CLASS DEFAULTS -- and the file has therefore stated `group_safety_max = 0.0` and `group_mate_min = 0.0`,
    # i.e. the grouping drives OFF, while every campaign has run them at 8.0/15.0 via the hardcoded `**GRP`.
    # Those two multipliers make leaving a band of 30 cost 20.6x in perceived yield against a terrain signal
    # whose whole range is 4.8x, so the file was silent about the single strongest force in the model's
    # spatial behaviour. Dumping it here fixes the generator's blind spot with the mechanism it already uses,
    # rather than a second copy of the resolution logic. Same class of defect as the climate channels.
    _sub_cfg = {k: v for k, v in w._substrate_cfg.model_dump().items()
                if isinstance(v, (int, float, str, bool, type(None)))} if getattr(w, "_substrate_cfg", None) else {}
    meta = dict(sha=sha, tree_dirty=dirty, climate_config=clim.model_dump(), substrate_config=_sub_cfg,
                seed=SEED, founders=FOUNDERS, steps=STEPS, world=f"{TERR}-{CLIM}",
                terrain=TERR, climate=CLIM, patch_size=(PATCHSZ if PATCHSZ > 0 else PATCH),
                habitable_cells=len(land), reserve_full=w._reserve_full, band_split=BAND_SPLIT,
                genome=GENOME, genea_csv=os.path.basename(GENEA), genealogy_on=GENEALOG,
                connubium=CONNUBIUM, m_star=(MSTAR if cut2 else 3), defend=DEFEND, elite=ELITE,
                rellegit=RELLEGIT, legit_threshold=ELITE_KW.get("legit_threshold"),
                residence=getattr(demog, "aggregation_residence", None),
                patriline_weight=getattr(demog, "patriline_weight", None),
                demography_config=_full_cfg,
                # A FINISHED RUN CARRIES ITS OWN CONFIGURATION. Naming the repo file is not enough — the repo
                # moves on and the run does not — so the resolved file is copied next to the output and its
                # name recorded here. `run_config=None` marks a run from the legacy knob path.
                run_config=(_SPEC.name if _SPEC else None),
                run_config_archived=(os.path.basename(_SPEC.archive_to(HERE)) if _SPEC else None))
    # KNOWN-INERT COMBINATIONS. A flag switched on without its companion does nothing while LOOKING enabled --
    # R-85c's lesson ("distinguish 'does nothing when I turn it on' from 'does nothing'") and charter D4. This is
    # a mechanical guard rather than another rule to remember, because D4 already existed and was still missed:
    # a biome comparison was run with C_SOIL=1 and C_ABANDON=0, and the two arms came out BYTE-IDENTICAL for
    # 1000 steps because soil depletion without abandonment produces no rotation at all (R-71: n_settle frozen
    # 12-16 vs 25 churning).
    if SOIL and os.environ.get("C_ABANDON", "0") != "1":
        log("  !! CONFIG: C_SOIL=1 with C_ABANDON=0 -- soil depletes but villages never relocate, so there is "
            "NO swidden rotation. R-71 measured this as the frozen-settlement case. Set C_ABANDON=1 for swidden.")
    if SPLIT > 0.0 and BRANCH <= 0.0:
        log("  !! CONFIG: C_SPLIT>0 with C_BRANCH=0 -- segmentation cleaves along the heritable _subclan tag, so "
            "with no branching every lineage is one undivided group and NOTHING can ever split. Set C_BRANCH>0.")
    if LOCASC and not RESVIL:
        log("  !! CONFIG: C_LOCASC=1 with C_RESVIL=0 -- band-keyed local rank produces NO ascription at all "
            "(the stock resets on band fission ~10yr but needs ~50yr to mature). Set C_RESVIL=1.")
    if IMPROVED and not DEFEND:
        log("  !! CONFIG: C_IMPROVED=1 needs C_DEFEND=1 -- worked land cannot be claimed without defensibility.")
    # THE BANNER READS OFF `demog`, NOT OFF THE ENV VARS. It used to print CONNUBIUM/BUD/ELITE/IMPROVED —
    # the env-derived variables — which was fine while a knob was the only way to set those flags. C_ALLON can
    # now enable a mechanism whose knob is unset, so the banner was reporting "budding=False connubium=cut1"
    # on runs whose config had `enable_village_budding=True` and `enable_adaptive_connubium=True`. The one
    # line a human reads before a run must not be able to disagree with the config that run uses.
    _adaptive = getattr(demog, "enable_adaptive_connubium", False)
    _budding = getattr(demog, "enable_village_budding", False)
    log(f"campaign: sha={sha} world={TERR}-{CLIM} founders={FOUNDERS} steps={STEPS} "
        f"habitable={len(land)} "
        f"connubium={'cut2(m*=' + str(demog.mate_search_min_eligible) + ')' if _adaptive else 'cut1'} "
        f"defend={demog.enable_economic_defensibility} improved={demog.enable_improved_land} "
        f"budding={_budding}{'(thr' + str(demog.village_fission_threshold) + ')' if _budding else ''} "
        f"elite={demog.enable_legitimacy} soil={demog.enable_soil_depletion} "
        f"genome={demog.enable_genome} genealogy={'ON' if demog.enable_genealogy_log else 'OFF'} "
        f"flush/{FLUSHEVERY}")
    _cl_on = sorted(f.replace("enable_", "") for f in type(clim).model_fields
                    if f.startswith("enable_") and getattr(clim, f))
    log(f"campaign: climate a_seas={cap.a_seas:.3f} ENSO(amp={cap.interannual_amp:.2f},"
        f"per={cap.interannual_period}) regime(amp={cap.regime_amp:.2f},dur={cap.regime_duration},"
        f"rec={cap.regime_recurrence}) caribou(amp={cap.caribou_amp:.2f},per={cap.caribou_period}) "
        f"llanos={cap.llanos_flood_amp:.2f} | on: {','.join(_cl_on)}")
    traj = []
    prev_leaders: dict = {}
    last_con: dict = {}
    genea_rows = 0
    seen_violations: set = set()          # R-91: log each contradiction once, on first appearance
    _last_sick: dict = {}                 # climate-health complaints, logged only when the set changes
    cum_reversions = 0                                   # R-89: summed every step, not just at LOGEVERY —
    t0 = time.time()                                      # a reversion can fire and re-ascribe within one gap
    # SLEEP-AWARE BUDGET (2026-07-22). The budget must meter COMPUTE, not wall-clock: the machine suspended
    # mid-run today and 25.4 min of wall time elapsed across 50 steps that normally cost 0.2 min, which would
    # have silently robbed a later arm of ~17% of its step count for no work done. We cannot use process CPU
    # time either (child work, IO waits), so instead we sum the per-STEP deltas and DISCOUNT any delta that
    # is implausible against the run's own recent pace — the run calibrates its own normal. (Metering was
    # per-SNAPSHOT until R-105, which made the check unreachable inside a slow LOGEVERY block; see below.)
    last_t = t0
    deltas: list = []          # recent per-STEP wall deltas (seconds); the pace reference
    compute_s = 0.0            # summed deltas with suspensions discounted — what the budget spends
    suspended_s = 0.0          # total time attributed to suspension (reported, never charged)
    for step in range(1, STEPS + 1):
        w.step()
        if not w.agent_list:
            log(f"[{step}] EXTINCT"); break
        cum_reversions += w.reversions_this_step
        c = w.connubium()
        if c:
            last_con = c                                 # seasonal gathering fires every aggregation_period steps
        if step % FLUSHEVERY == 0:
            genea_rows += w.flush_genealogy(GENEA)       # append + clear buffer (bounded memory)
        if step % LOGEVERY == 0 or step == 1:
            row, prev_leaders = snapshot(w, step, menarche, prev_leaders, last_con)
            if ELITE:
                row["cum_reversions"] = cum_reversions
            traj.append(row)
            # THE DEMOGRAPHY VERDICT LINE (supervisor request 2026-08-14). Modelled on the climate health
            # line, which found three dark channels on its first run. Every demographic failure of the last
            # two days was visible in numbers already printed here; what was missing was a line that SAID
            # so. Printed only when something is out of band, or once at the first snapshot, so a healthy
            # run stays quiet and an unhealthy one cannot be scrolled past.
            _dh = demography_health(row)
            row["demog_in_band"] = _dh["n_scored"] - _dh["n_out"]
            row["demog_scored"] = _dh["n_scored"]
            row["demog_structure_ok"] = _dh["structure_ok"]
            # THE SPATIAL SANITY CHECK (R-106, 2026-08-16). Compare the population to the MAP, every run.
            # The R-106 arc spent a week on mortality and then fertility while the population used 14% of its
            # land, sat 4.8x BELOW Binford packing regionally and 1.4x ABOVE it locally, and ate 2.7x
            # requirement. Every input was already in this row. Nothing multiplied `pop` by anything and
            # compared it to the map. This is that multiplication, and it needs NO new anchor — it uses
            # Binford's filed 0.091 twice, once per side.
            _sp = spatial_health(pop=row.get("pop", 0) or 0,
                                 habitable_cells=getattr(w, "_habitable_cells", 0),
                                 cells_occupied=row.get("cells_occupied", 0) or 0,
                                 n_bands=row.get("n_bands", 0) or 0)
            row["spatial_regional_per_km2"] = _sp["regional_per_km2"]
            row["spatial_local_per_km2"] = _sp["local_per_km2"]
            row["spatial_land_use_frac"] = _sp["land_use_frac"]
            row["spatial_km2_per_band"] = _sp["km2_per_band"]
            row["spatial_paradox"] = _sp["paradox"]
            row["spatial_band_below_catchment"] = _sp["band_below_catchment"]
            if _sp["paradox"] or _sp["band_below_catchment"]:
                # Loud, because being scrolled past is exactly how this went unseen for a week.
                _bits = []
                if _sp["paradox"]:
                    _bits.append(f"PACKED AND SPARSE AT ONCE (local {_sp['local_per_km2']:.3f} > 0.091 "
                                 f"> regional {_sp['regional_per_km2']:.4f} /km2) on "
                                 f"{100 * _sp['land_use_frac']:.1f}% of the land")
                if _sp["band_below_catchment"]:
                    _bits.append(f"band commands {_sp['km2_per_band']:.0f} km2, inside its own 314 km2 "
                                 f"catchment (Vita-Finzi & Higgs)")
                log("  !! SPATIAL: " + "; ".join(_bits)
                    + " -- the population is NOT food-limited, it is failing to disperse; any "
                      "carrying-capacity reading of this run is void")
            # DATA GUARD. In the first steps the life table has seen almost no exposure and the founder
            # cohort sits in two enormous bands, so the panel reads band_med_adults 207 and TFR 0 — verdicts
            # that are arithmetically correct and completely meaningless. A monitor that cries wolf during
            # the transient is a monitor people learn to scroll past, which is the failure this line exists
            # to prevent. 500 person-years is roughly one founder cohort living one year; below it the
            # scoring is suppressed and the reason is said out loud rather than silently skipped.
            _py = row.get("lt_exposure_py", 0.0) or 0.0
            if _py < 500.0:
                if step <= LOGEVERY:
                    log(f"  ~~ demography: not scored yet ({_py:.0f} person-years of exposure; "
                        f"needs 500 before the panel means anything)")
            elif _dh["n_out"]:
                log("  ~~ " + _dh["banner"])
            # R-91: complain about CONTRADICTIONS as they appear, rather than printing yet another field.
            # Only the FIRST occurrence of each code is logged — a violation that persists is one event, and a
            # checker that repeats itself every snapshot is one that gets ignored.
            for v in invariant_check(traj, {"legit_threshold": ELITE_KW.get("legit_threshold"),
                                            "relative_legitimacy": RELLEGIT} if ELITE else {}):
                if v.code not in seen_violations:
                    seen_violations.add(v.code)
                    log(f"  !! [{step}] {v}")
            # CLIMATE HEALTH, carried in every checkpoint (2026-08-06). Not "was the channel configured on"
            # — the banner already says that, and saying it was how four channels stayed inert while reading
            # as live — but whether each one ACTUALLY MOVED THE FIELD in this run, and how hard. Verdicts:
            # OFF / UNREACHABLE (mask empty) / NEVER-FIRED (clock never came round) / RARE / LIVE.
            meta["climate_health"] = cap.health() if hasattr(cap, "health") else None
            with open(OUT, "w", encoding="utf-8") as fh:
                json.dump(dict(meta=meta, traj=traj), fh)     # crash-safe trajectory checkpoint
            el = time.time() - t0
            eta = el / step * (STEPS - step)
            elite_str = (f" | asc={row['ascribed_frac']} gumsa={row['frac_gumsa']} "
                        f"tenure={row['leader_tenure_yr']}y levy={row['leader_levy']} "
                        f"resent(mean/max)={row['mean_resentment']}/{row['max_resentment']} "
                        f"revs={row['cum_reversions']}") if ELITE else ""
            log(f"[{step:5d}/{STEPS}] pop={row['pop']:6d} bd={row['n_bands']:4d} bigbd={row['n_bigbands']}"
                f"(med{row['bigband_med']}) strat={row['pct_stratified']}% giniC={row['gini_cred']} "
                f"dyn:eff={row['eff_lineages']} top={row['lin_top_share']} nlin={row['n_lineages']} "
                f"lpb={row['lineages_per_band']}/dom={row['dom_lineage_share']} mRSg={row['male_rs_gini']} "
                f"set={row['n_settle']}(mx{row['settle_max']},prim{row['primate_ratio']}) "
                f"con={row['connubium_med']} inst={row['claim_events']} ldT={row['leader_turnover']}"
                f"{elite_str} | {el/60:.1f}m eta{eta/60:.0f}m")
            # Only the channels that are NOT healthy get printed, and only when the set of complaints changes.
            # A diagnostic that prints "all fine" every snapshot is one nobody reads by step 500.
            _ch = meta.get("climate_health") or {}
            _sick = {c: v["verdict"] for c, v in _ch.items()
                     if v.get("verdict") in ("UNREACHABLE", "NEVER-FIRED", "RARE")}
            if _sick and _sick != _last_sick:
                _last_sick = _sick
                log("  ~~ climate: " + ", ".join(f"{c}={v}" for c, v in sorted(_sick.items()))
                    + "  (configured ON but not moving the field)")
        # ── BUDGET, metered EVERY STEP (R-105 fix) ──────────────────────────────────────────────────
        # This block used to live inside the snapshot branch, so it could only fire once per LOGEVERY
        # steps. With C_LOGEVERY=250 (every overnight campaign) a single block can cost HOURS at high
        # population, and neither the compute budget nor the 3x wall backstop could interrupt it — the
        # backstop was unreachable by construction. Per-step metering also gives the suspension detector
        # a finer signal: a machine sleep is ONE oversized step delta, whereas genuinely slow compute is
        # many moderately-sized ones. The snapshot-level version could not tell those apart at all.
        _now = time.time()
        _d = _now - last_t
        last_t = _now
        if deltas:
            _win = deltas[-100:]                     # ~a few LOGEVERY blocks; adapts as pop (and pace) grows
            _med = sorted(_win)[len(_win) // 2]
            # Suspension looks like a delta far outside the run's own recent pace. The threshold is
            # RELATIVE because the true pace varies hugely with population, so any absolute cutoff would
            # be wrong in one regime or the other. The +120s floor also keeps the once-per-LOGEVERY
            # snapshot+JSON-dump cost (seconds) from being misread as a suspension at a fast pace.
            if _d > max(3.0 * _med, _med + 120.0):
                suspended_s += _d - _med
                log(f"  [{step}] SUSPENSION: {_d/60:.1f}m elapsed vs {_med/60:.2f}m pace — "
                    f"charging pace, not wall (budget protected)")
                _d = _med
        deltas.append(_d)
        compute_s += _d
        # Budget spends COMPUTE. The wall-clock backstop at 3x is a safety net: if the discount logic ever
        # misjudged a genuine slowdown as suspension it could otherwise run unbounded, and an arm that
        # never terminates is worse than one that stops early. NOTE: no population cap — a cap would hide
        # the very phenomenon a runaway is evidence of (explicit call, 2026-07-26). Time is the only limit.
        if MAXMIN > 0:
            wall_s = _now - t0
            if compute_s / 60.0 >= MAXMIN or wall_s / 60.0 >= 3.0 * MAXMIN:
                _why = "COMPUTE" if compute_s / 60.0 >= MAXMIN else "WALL-BACKSTOP"
                log(f"  [{step}] BUDGET {MAXMIN:.0f}m reached at step {step}/{STEPS} [{_why}] — "
                    f"compute={compute_s/60:.1f}m wall={wall_s/60:.1f}m suspended={suspended_s/60:.1f}m")
                break
    genea_rows += w.flush_genealogy(GENEA)               # final flush
    # Persist the OUTCOME, not just the intent: `meta["steps"]` is what was ASKED for, so a truncated run would
    # otherwise look like a complete one to any offline reader. D15's lesson generalised — record the denominator.
    meta["steps_completed"] = step
    meta["truncated"] = step < STEPS
    # Now that the budget can stop MID-block (R-105), steps_completed can run ahead of the last trajectory row
    # by up to LOGEVERY-1 steps. Record which step the last row actually describes, so cross-arm comparison
    # uses the row's denominator and not the loop's.
    meta["last_snapshot_step"] = traj[-1]["step"] if traj else 0
    meta["wall_minutes"] = round((time.time() - t0) / 60.0, 1)
    meta["compute_minutes"] = round(compute_s / 60.0, 1)
    meta["suspended_minutes"] = round(suspended_s / 60.0, 1)
    # THE AGE-SPECIFIC ARRAYS, ONCE, AT THE END (R-106, 2026-08-13). The per-row fields carry the life-table
    # SCALARS (e0, TFR, IBI, starvation share), which is what a trajectory needs. They cannot answer the
    # question that actually decides an age-structure failure: WHICH AGES carry the excess hazard. Without
    # the arrays a finished run can only be compared against a UNIFORMLY scaled Siler schedule, and a uniform
    # scaling barely moves a stable age distribution — so the comparison misses precisely the age-graded
    # distortion it is meant to find. Measured: an arm with TFR 8.41 and realised e0 17.7 should sit at
    # frac_child ~0.45 under a uniform scaling but sits at 0.543, and the residual is unattributable without
    # these. One row of ~700 integers per run, written once.
    # THE SPATIAL DUMP, ONCE, AT THE END (R-106, 2026-08-16). Every aggregate this project logs — pop,
    # cells_occupied, n_settle — collapses the map to a scalar. That is how a population sitting on 14% of its
    # land in a ~20x-overlapping carpet of settlement windows went a week without anyone seeing the shape of
    # it. Four 100x100 arrays per run, written once, so the arrangement can be LOOKED AT rather than inferred
    # from ratios. Reconstructing the world in a separate probe script was the alternative and was rejected:
    # rebuilding world construction by hand is exactly how the test fixtures diverged from the model earlier
    # in this arc.
    try:
        import numpy as _np
        _W = getattr(w.terrain_field, "width", 100)
        _H = getattr(w.terrain_field, "height", 100)
        _people = _np.zeros((_H, _W), dtype=_np.int32)
        for _a in w.agent_list:
            _px, _py = _a.pos
            _people[_py % _H, _px % _W] += 1
        _sites = _np.zeros((_H, _W), dtype=_np.int8)
        for (_sx, _sy) in getattr(w, "_settlement_sites", ()):
            _sites[_sy % _H, _sx % _W] = 1
        # `f` and `land` are the world as MAIN built it. An earlier attempt read these off `w.terrain_field`
        # with getattr fallbacks and silently wrote three all-zero arrays — the fallback hid the wrong
        # attribute name instead of failing. Read the real handles, and assert they are not empty.
        _biome = _np.asarray(f.biome)
        _forage = _np.asarray(f.forage_kcal, dtype=float)
        _water = _np.asarray(f.isWater, dtype=_np.int8)
        _hab = _np.zeros((_H, _W), dtype=_np.int8)
        for (_hx, _hy) in land:
            _hab[_hy % _H, _hx % _W] = 1
        # THE FIELD VILLAGES ARE ACTUALLY SITED ON (added 2026-08-17, supervisor's question).
        # Settlement founding judges S_pot = max(aquatic_food, cultivability), NOT forage_kcal. Every spatial
        # claim in this arc so far -- corr(forage,people) = +0.12, "65% of the best land is empty" -- was
        # measured against forage_kcal. That is the right yardstick for INDIVIDUAL forager movement, because
        # the movement rule reads per-capita forage yield. It is the WRONG yardstick for VILLAGE SITING: a
        # village on a salmon choke point or fertile alluvium can sit on mediocre forage land and be
        # correctly placed. Without these two arrays the question cannot even be asked.
        _aq = _np.asarray(getattr(f, "aquatic_food", _np.zeros((_H, _W))), dtype=float)
        _cult = _np.asarray(getattr(f, "cultivability", _np.zeros((_H, _W))), dtype=float)
        _spot = _np.maximum(_aq, _cult)
        assert _hab.sum() > 0 and _forage.max() > 0, "spatial dump read an empty terrain — wrong handle"
        _spath = OUT.replace("campaign_trajectory_", "campaign_spatial_").replace(".json", ".npz")
        _np.savez_compressed(_spath, people=_people, sites=_sites, biome=_biome,
                             forage_kcal=_forage, habitable=_hab, water=_water,
                             aquatic_food=_aq, cultivability=_cult, s_pot=_spot,
                             step=_np.int64(step))
        meta["spatial_dump"] = os.path.basename(_spath)
        log(f"  spatial dump -> {_spath}  (people {int(_people.sum())} on {int((_people > 0).sum())} cells, "
            f"{int(_sites.sum())} sites)")
    except Exception as _e:                      # a diagnostic must never lose a finished run
        log(f"  !! spatial dump failed ({_e}) — the run itself is unaffected")

    if hasattr(w, "raw_demographic_counters"):
        _c = w.raw_demographic_counters()
        meta["life_table_final"] = {k: _c[k] for k in
                                    ("lt_exposure", "lt_deaths", "lt_deaths_starv", "lt_deaths_senesc")}
        meta["fertility_final"] = {k: _c[k] for k in ("fert_births", "fert_exposure", "ibi_hist")}
        meta["fertility_final"].update(fert_factor_sum=_c["fert_factor_sum"],
                                       fert_factor_n=_c["fert_factor_n"],
                                       fert_factor_sat=_c["fert_factor_sat"])
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(dict(meta=meta, traj=traj), fh)
    log(f"DONE step={step} in {(time.time()-t0)/60:.1f} min -> {OUT} ; genealogy rows={genea_rows} -> {GENEA}")


if __name__ == "__main__":
    main()
