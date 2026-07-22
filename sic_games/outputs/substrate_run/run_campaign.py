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
    enable_legitimacy=True, legit_feast_frac=0.25, legit_cred_gain=10.0, legit_threshold=0.15, legit_decay=0.02,
    enable_delegitimation=True, resent_alpha=0.001, resent_threshold=0.5, resent_privilege_ref=10.0,
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
        gini_cred=round(gini(cred), 3), gini_wealth=round(gini(wealth), 3),
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
        primate_ratio=st.get("primate_ratio"), zipf_slope=st.get("zipf_slope"),
        # mating + instability + leadership
        connubium_med=con.get("median"), connubium_p90=con.get("p90"),
        claim_events=ins.get("claim_events", 0), cells_owned=ins.get("n_owned", 0),
        leader_turnover=leader_turnover,
    )
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
    base = NPPCapacityField(f, BURN, patch=(X0, Y0, PATCH), mode="tallavaara", aquatic=True, enable_depletion=True)
    base0 = NPPCapacityField(f, BURN, patch=(X0, Y0, PATCH), mode="tallavaara", aquatic=True, enable_depletion=True)
    land = [(x, y) for y in range(100) for x in range(100) if f.isWater[y, x] == 0 and base0.level(x, y) > 0]
    cap = ClimateField(base, a_seas=0.4, regime_driver=None)      # seasonal, NO regime forcing (endogenous only)
    pos = [land[i % len(land)] for i in range(FOUNDERS)]
    cut2 = (CONNUBIUM == "cut2")
    demog = emergent_village_demog().model_copy(update=dict(
        enable_landscape_packing=True, enable_sedentism_fertility=True,
        enable_marriage_aggregation=True, enable_aggregation_sedentism=True,
        enable_catchment_ceiling=True, enable_settlement_scalar_stress=True, settle_catchment_radius=1,
        enable_economic_defensibility=DEFEND,
        enable_adaptive_connubium=cut2, mate_search_min_eligible=(MSTAR if cut2 else 3),
        enable_exogamy=cut2, exogamy_degree="lineage",
        enable_village_budding=BUD, village_fission_threshold=BUD_THR,
        enable_improved_land=IMPROVED,
        enable_soil_depletion=SOIL, enable_alluvial_renewal=SOIL,
        enable_emergent_abandonment=(SOIL and os.environ.get("C_ABANDON", "0") == "1"),
        enable_genome=GENOME, genome_loci=48, enable_genealogy_log=GENEALOG,
        enable_lineage_branching=(BRANCH > 0.0), lineage_branch_rate=BRANCH,
        enable_lineage_split=(SPLIT > 0.0), lineage_split_rate=SPLIT, lineage_split_min_segment=SPLITMIN,
        **ELITE_KW))
    w = TerrainWorld(n_agents=FOUNDERS, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, game_stream=False, seed=SEED,
                     carbon_cfg=CarbonConfig(kappa=1.5),
                     substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                                   contest_exponent=1.5, move_cost_flat=0.0, **GRP),
                     harvest_field=cap, placement_positions=pos, demography_cfg=demog)
    menarche = demog.menarche_months
    meta = dict(sha=sha, seed=SEED, founders=FOUNDERS, steps=STEPS, world=f"{TERR}-{CLIM}",
                habitable_cells=len(land), reserve_full=w._reserve_full, band_split=BAND_SPLIT,
                genome=GENOME, genea_csv=os.path.basename(GENEA), connubium=CONNUBIUM,
                m_star=(MSTAR if cut2 else 3), defend=DEFEND, elite=ELITE, rellegit=RELLEGIT,
                legit_threshold=ELITE_KW.get("legit_threshold"))
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
    genea_rows += w.flush_genealogy(GENEA)               # final flush
    log(f"DONE step={step} in {(time.time()-t0)/60:.1f} min -> {OUT} ; genealogy rows={genea_rows} -> {GENEA}")


if __name__ == "__main__":
    main()
