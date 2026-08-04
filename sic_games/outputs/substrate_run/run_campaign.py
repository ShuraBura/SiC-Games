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
from sic_games.climate import ClimateField
from sic_games.invariants import check as invariant_check

FOUNDERS  = int(os.environ.get("C_FOUNDERS", "3000"))
STEPS     = int(os.environ.get("C_STEPS", "15000"))
SEED      = int(os.environ.get("C_SEED", "0"))
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
MSTAR     = int(os.environ.get("C_MSTAR", "50"))         # Cut-2 mate-search pool m* (probe: m*=50 → median reach 496 ≈ Wobst)
ELITE     = os.environ.get("C_ELITE", "0") == "1"        # T-9: the R-82...R-87 elite/legitimacy stack — see module docstring
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


def snapshot(w, step, menarche, prev_leaders, last_con):
    al = w.agent_list
    pop = len(al)
    sizes = Counter(a._group.band_id for a in al)
    szv = list(sizes.values())
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
    # can be compared. `frac_villages_broken` = share of villages whose nobles stand a LARGE effect above commoners.
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
    row = dict(
        step=step, pop=pop, births=w.births_this_step, deaths_starv=w.deaths_starv_this_step,
        mean_reserve=round(statistics.mean(wealth) / w._reserve_full, 3) if pop else 0,
        juv_frac=round(sum(1 for x in ages if x < 180) / pop, 3) if pop else 0,   # <15 yr (dependency proxy)
        mean_age_yr=round(statistics.mean(ages) / 12.0, 1) if pop else 0,
        n_bands=len(sizes), band_med=statistics.median(szv) if szv else 0, band_max=max(szv) if szv else 0,
        n_villages=len(villages), village_med=round(statistics.median(villages), 1) if villages else 0,
        village_max=max(villages) if villages else 0,
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
        village_gap_d_med=_village_gap_d_med,           # R-103b Flannery: median noble/commoner Cohen's d per village
        frac_villages_broken=_frac_villages_broken,     #   share of villages with a LARGE (d>=0.8) noble/commoner break
        n_villages_gapd=len(_dvals),
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
    )
    # ── MARKER MATRIX (2026-07-27) ──────────────────────────────────────────────────────────────
    # These quantities were all COMPUTED by demography() and none of them reached a campaign
    # trajectory, so no long run has ever scored them. Several are anchored targets that have gone
    # unmeasured for the entire project; polygyny in particular sat 15x off Marlowe unnoticed
    # because nothing carried it forward. Cost is one demography() pass per snapshot, i.e. per
    # C_LOGEVERY steps, which is negligible beside the step loop.
    _dg = w.demography()
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
        # WEALTH CONCENTRATION — the direct test of "does material accrue to the elite"
        material_gini=round(_dg.get("material_gini", 0.0), 4),
        material_top10_share=round(_dg.get("material_top10_share", 0.0), 4),
        wealth_gini=round(_dg.get("wealth_gini", 0.0), 4),
        corr_cred_material=round(_dg.get("corr_cred_material", 0.0), 4),
        density_per_km2=round(_dg.get("density_per_km2", 0.0), 5),
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
    try:
        sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"],
                                      cwd=os.path.join(HERE, "..", "..", "..")).decode().strip()
    except Exception:
        sha = "?"
    k = world_lottery_climate(SEED, terrain=TERR, climate=CLIM)
    f = generate_world(k, mode="climate")
    _patch = (X0, Y0, PATCHSZ if PATCHSZ > 0 else PATCH)     # R-103i: shrink ⇒ circumscription
    base = NPPCapacityField(f, BURN, patch=_patch, mode="tallavaara", aquatic=True, enable_depletion=True)
    base0 = NPPCapacityField(f, BURN, patch=_patch, mode="tallavaara", aquatic=True, enable_depletion=True)
    land = [(x, y) for y in range(100) for x in range(100) if f.isWater[y, x] == 0 and base0.level(x, y) > 0]
    cap = ClimateField(base, a_seas=0.4, regime_driver=None)      # seasonal, NO regime forcing (endogenous only)
    pos = [land[i % len(land)] for i in range(FOUNDERS)]
    cut2 = (CONNUBIUM == "cut2")
    demog = emergent_village_demog().model_copy(update=dict(
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
            "enable_infanticide",                    # documented UNIMPLEMENTED STUB (no logic reads it)
            "enable_genealogy_log",                  # observer/logging, not a dynamic; costly
            "enable_bud_hazard",                     # mutually-exclusive alternate to the legacy budding path
            "enable_stratification_inequality_gate", # R-103: criterion known wrong, parked for supervisor call
        }
        # Flags a C_* knob above already decides. `model_fields_set` cannot be used for this: the preset
        # itself is built with model_copy(), so 74 fields are already "set" and the guard would swallow
        # nearly everything. This list is explicit and auditable instead -- an ablation (e.g. C_SOIL=0)
        # must not be silently re-enabled by C_ALLON.
        _knob_controlled = {
            "enable_sedentism_fertility", "enable_aggl_ceiling", "enable_economic_defensibility",
            "enable_ascribed_mate_choice", "enable_material_inheritance", "enable_noble_leveling_exemption",
            "enable_lineage_tribute", "enable_adaptive_connubium", "enable_exogamy",
            "enable_village_budding", "enable_improved_land", "enable_soil_depletion",
            "enable_alluvial_renewal", "enable_emergent_abandonment", "enable_genome",
            "enable_lineage_branching", "enable_lineage_split",
        }
        demog = demog.model_copy(update={
            f: True for f in type(demog).model_fields
            if f.startswith("enable_") and f not in _skip and f not in _knob_controlled
            and not getattr(demog, f)})
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
    w = TerrainWorld(n_agents=FOUNDERS, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, game_stream=False, seed=SEED,
                     carbon_cfg=CarbonConfig(kappa=1.5),
                     substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                                   contest_exponent=1.5, move_cost_flat=0.0, **GRP),
                     harvest_field=cap, placement_positions=pos, demography_cfg=demog)
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
    meta = dict(sha=sha, seed=SEED, founders=FOUNDERS, steps=STEPS, world=f"{TERR}-{CLIM}",
                terrain=TERR, climate=CLIM, patch_size=(PATCHSZ if PATCHSZ > 0 else PATCH),
                habitable_cells=len(land), reserve_full=w._reserve_full, band_split=BAND_SPLIT,
                genome=GENOME, genea_csv=os.path.basename(GENEA), genealogy_on=GENEALOG,
                connubium=CONNUBIUM, m_star=(MSTAR if cut2 else 3), defend=DEFEND, elite=ELITE,
                rellegit=RELLEGIT, legit_threshold=ELITE_KW.get("legit_threshold"),
                residence=getattr(demog, "aggregation_residence", None),
                patriline_weight=getattr(demog, "patriline_weight", None),
                demography_config=_full_cfg)
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
    log(f"campaign: sha={sha} world={TERR}-{CLIM} founders={FOUNDERS} steps={STEPS} "
        f"habitable={len(land)} connubium={CONNUBIUM}{'(m*='+str(MSTAR)+')' if cut2 else ''} "
        f"defend={DEFEND} improved={IMPROVED} budding={BUD}{'(thr'+str(BUD_THR)+')' if BUD else ''} "
        f"elite={ELITE} genome={GENOME} genealogy={'ON' if GENEALOG else 'OFF'} flush/{FLUSHEVERY}")
    traj = []
    prev_leaders: dict = {}
    last_con: dict = {}
    genea_rows = 0
    seen_violations: set = set()          # R-91: log each contradiction once, on first appearance
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
            # R-91: complain about CONTRADICTIONS as they appear, rather than printing yet another field.
            # Only the FIRST occurrence of each code is logged — a violation that persists is one event, and a
            # checker that repeats itself every snapshot is one that gets ignored.
            for v in invariant_check(traj, {"legit_threshold": ELITE_KW.get("legit_threshold"),
                                            "relative_legitimacy": RELLEGIT} if ELITE else {}):
                if v.code not in seen_violations:
                    seen_violations.add(v.code)
                    log(f"  !! [{step}] {v}")
            with open(OUT, "w", encoding="utf-8") as fh:
                json.dump(dict(meta=meta, traj=traj), fh)     # crash-safe trajectory checkpoint
            el = time.time() - t0
            eta = el / step * (STEPS - step)
            elite_str = (f" | asc={row['ascribed_frac']} gumsa={row['frac_gumsa']} "
                        f"tenure={row['leader_tenure_yr']}y levy={row['leader_levy']} "
                        f"resent(mean/max)={row['mean_resentment']}/{row['max_resentment']} "
                        f"revs={row['cum_reversions']}") if ELITE else ""
            log(f"[{step:5d}/{STEPS}] pop={row['pop']:6d} bd={row['n_bands']:4d} vil={row['n_villages']}"
                f"(med{row['village_med']}) strat={row['pct_stratified']}% giniC={row['gini_cred']} "
                f"dyn:eff={row['eff_lineages']} top={row['lin_top_share']} nlin={row['n_lineages']} "
                f"lpb={row['lineages_per_band']}/dom={row['dom_lineage_share']} mRSg={row['male_rs_gini']} "
                f"set={row['n_settle']}(mx{row['settle_max']},prim{row['primate_ratio']}) "
                f"con={row['connubium_med']} inst={row['claim_events']} ldT={row['leader_turnover']}"
                f"{elite_str} | {el/60:.1f}m eta{eta/60:.0f}m")
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
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(dict(meta=meta, traj=traj), fh)
    log(f"DONE step={step} in {(time.time()-t0)/60:.1f} min -> {OUT} ; genealogy rows={genea_rows} -> {GENEA}")


if __name__ == "__main__":
    main()
