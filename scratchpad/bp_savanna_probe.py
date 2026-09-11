"""R-106 savanna adult-scarcity residual — PRE-transfer deficit-vs-surplus probe.

The handoff open item: band provisioning is COMPENSATED in savanna (adults share to death, adult mortality
0.027 -> 0.043, e0 stays ~22) while it works cleanly in temperate. The earlier probe read POST-transfer and
returned a paradox. This measures, PER food-sharing group and PER step, the quantities that drive the transfer
BEFORE any wealth moves:

  - juvenile STOCK deficit (total_need)                 what the mechanism must fill
  - adult STOCK surplus above keep*cap (pool)           what the mechanism treats as donatable
  - adult FLOW deficit  Sum max(0, burn*cf - intake)    the donors' OWN shortfall this step
  - dependency ratio, cap/burn buffer ratio

Hypothesis: the band-provisioning donor test is on STOCK (wealth > keep*cap), never on FLOW. In savanna the
donatable "surplus" is buffer the adult itself needs — the adults are in flow deficit — so the transfer
converts a juvenile stock deficit into adult starvation. In temperate the donors run a flow surplus, so the
reserve they give is genuinely spare.

Uses the CANON runconfig (NOT the impoverished battery base) and biome_seasonality=ON (Addendum 73). Low-noise
instrument: world seed fixed per panel cell, agent seed varied.
"""
import os
import sys
import numpy as np

ROOT = r"C:\Users\syatom\Projects\SiC Games"
sys.path.insert(0, os.path.join(ROOT, "sic_games", "src"))
sys.path.insert(0, os.path.join(ROOT, "sic_games", "outputs", "phase1_social_evolution"))
sys.path.insert(0, os.path.join(ROOT, "sic_games", "outputs", "phase1_biome_mortality"))
sys.path.insert(0, os.path.join(ROOT, "sic_games", "outputs", "mechanism_battery"))

from sic_games import runconfig
from run_se0_controlled_climate import emergent_village_demog
from sic_games.capacity import NPPCapacityField
from sic_games.climate import ClimateField, ClimateConfig, build_climate_field
from sic_games.config import CarbonConfig, KcalEconomyConfig, SubstrateConfig
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world, world_lottery_climate

# battery1's VILLAGE + ELITE overlay (the live stack); CANON overrides these where they differ.
import battery1_liveness as B

STEPS = int(os.environ.get("P_STEPS", "800"))
NAGENT = int(os.environ.get("P_N", "600"))
PATCH = int(os.environ.get("P_PATCH", "24"))
SAMPLE_FROM = int(os.environ.get("P_SAMPLE_FROM", "400"))   # equilibrium window start
SAMPLE_EVERY = int(os.environ.get("P_SAMPLE_EVERY", "10"))


def build(update, world_seed, agent_seed, n=NAGENT, patch=PATCH, terr="coastal", clim="temperate"):
    """Clone of battery1._build, but world_seed (the world lottery) and agent_seed (placement + stochastics)
    are DECOUPLED — the low-noise instrument. biome_seasonality forced ON (Addendum 73)."""
    k = world_lottery_climate(world_seed, terrain=terr, climate=clim)
    f = generate_world(k, mode="climate")
    base = NPPCapacityField(f, 75000.0, patch=(20, 20, patch), mode="tallavaara", aquatic=True, enable_depletion=True)
    cc = ClimateConfig().model_copy(update={"enable_seasonality": True, "enable_biome_seasonality": True})
    hf = build_climate_field(base, cc, fields=f, seed=world_seed)
    hf0 = NPPCapacityField(f, 75000.0, patch=(20, 20, patch), mode="tallavaara", aquatic=True, enable_depletion=True)
    land = [(x, y) for y in range(100) for x in range(100) if f.isWater[y, x] == 0 and hf0.level(x, y) > 0]
    d = (emergent_village_demog().model_copy(update=B.VILLAGE).model_copy(update=B.ELITE)
         .model_copy(update=update))
    return TerrainWorld(n_agents=n, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, game_stream=False,
                        seed=agent_seed, carbon_cfg=CarbonConfig(kappa=1.5),
                        substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                                      contest_exponent=1.5, move_cost_flat=0.0),
                        harvest_field=hf,
                        placement_positions=[land[i % len(land)] for i in range(n)], demography_cfg=d)


def run_one(clim, world_seed, agent_seed, bp_on):
    canon = dict(runconfig.load()["DemographyConfig"])       # THE canonical config (avoids the battery-base trap)
    canon["enable_band_provisioning"] = bp_on
    canon["band_provision_self_keep"] = 0.5                  # the calibrated value under study
    w = build(canon, world_seed, agent_seed, clim=clim)

    rows = []                       # per-group PRE-transfer records (only on sampled steps, only when bp_on)
    d_starv = d_senesc = 0          # deaths by cause, over the sample window (mortality signal)
    se0 = ag0 = None                # starv_events / starv_age_sum snapshot at window start
    pm = 0                          # person-months of exposure in the window (for a hazard, not a raw count)
    for t in range(STEPS):
        sample = bp_on and t >= SAMPLE_FROM and (t % SAMPLE_EVERY == 0)
        if sample:
            w._bp_probe = []
        w.step()
        if not w.agent_list:
            break
        if sample and w._bp_probe:
            rows.extend(w._bp_probe)
        w._bp_probe = None
        if t == SAMPLE_FROM:
            se0 = getattr(w, "starv_events", 0); ag0 = getattr(w, "starv_age_sum", 0.0)
        if t >= SAMPLE_FROM:
            d_starv += getattr(w, "deaths_starv_this_step", 0)
            d_senesc += getattr(w, "deaths_senesc_this_step", 0)
            pm += len(w.agent_list)
    # window starvation deaths + their MEAN AGE (does provisioning shift starvation from juveniles to adults?)
    se = getattr(w, "starv_events", 0) - (se0 or 0)
    ag = getattr(w, "starv_age_sum", 0.0) - (ag0 or 0.0)
    return dict(rows=rows, d_starv=d_starv, d_senesc=d_senesc, final_pop=len(w.agent_list),
                starv_n=se, pm=pm, starv_haz_k=(1000.0 * se / pm) if pm else float("nan"),
                starv_mean_age_yr=(ag / se / 12.0) if se else float("nan"))


DUMP = os.environ.get("P_DUMP", "")            # if set, save active-group arrays per biome to <DUMP>_<clim>.npz


def summarize(clim, cells, age_off=None, age_on=None):
    """Aggregate PRE-transfer group-records across a panel of (world,agent) cells for one biome."""
    all_rows = []
    for c in cells:
        all_rows.extend(c["rows"])
    if not all_rows:
        print(f"  {clim}: no sampled group-records (no provisioning fired)")
        return
    # keep only groups that actually had a juvenile deficit — the groups the mechanism acts on
    act = [r for r in all_rows if r["juv_deficit"] > 0.0 and r["n_adult"] > 0]
    n = len(act)
    juv_def = np.array([r["juv_deficit"] for r in act])
    surplus = np.array([r["adult_surplus"] for r in act])
    flow_def = np.array([r["adult_flow_deficit"] for r in act])
    n_adult = np.array([r["n_adult"] for r in act], float)
    n_juv = np.array([r["n_juv"] for r in act], float)
    n_af = np.array([r["n_adult_flow_deficit"] for r in act], float)
    cap_over_burn = np.array([r["cap_over_burn_sum"] for r in act])
    # phantom surplus: groups that donate (surplus>0) while their donor adults are themselves short (flow_def>0)
    donating = surplus > 0.0
    phantom = donating & (flow_def > 0.0)
    print(f"\n  === {clim.upper()} === active groups (juv deficit present) = {n}")
    print(f"  dependency ratio  n_juv/n_adult   mean {np.average(n_juv/n_adult):.2f}")
    print(f"  cap/burn buffer   per adult       mean {np.sum(cap_over_burn)/np.sum(n_adult):.2f}")
    print(f"  juv STOCK deficit / step-group    mean {juv_def.mean():.1f}")
    print(f"  adult STOCK surplus (donatable)   mean {surplus.mean():.1f}   "
          f"(ratio surplus/deficit = {surplus.sum()/juv_def.sum():.2f})")
    print(f"  adult FLOW deficit (own shortfall) mean {flow_def.mean():.1f}   "
          f"(ratio flowdef/surplus = {flow_def.sum()/max(surplus.sum(),1e-9):.2f})")
    print(f"  groups donating from surplus              {donating.mean()*100:.0f}%")
    print(f"  ... of those, donors in FLOW deficit too  {phantom.sum()/max(donating.sum(),1):.2%}  "
          f"<-- 'phantom surplus' = buffer the adult needs")
    print(f"  frac of donor adults in flow deficit      {np.sum(n_af)/np.sum(n_adult):.2%}")
    if DUMP:
        np.savez(f"{DUMP}_{clim}.npz", juv_def=juv_def, surplus=surplus, flow_def=flow_def,
                 n_adult=n_adult, n_juv=n_juv, n_adult_flow_def=n_af, cap_over_burn=cap_over_burn,
                 age_off=np.array([age_off if age_off is not None else np.nan]),
                 age_on=np.array([age_on if age_on is not None else np.nan]))
        print(f"  [dumped {DUMP}_{clim}.npz]")


def main():
    biomes = os.environ.get("P_BIOMES", "temperate,savanna").split(",")
    worlds = [int(x) for x in os.environ.get("P_WORLDS", "0,1").split(",")]
    agents = [int(x) for x in os.environ.get("P_AGENTS", "0,1").split(",")]
    print(f"PRE-TRANSFER PROBE | {NAGENT} agents, patch {PATCH}, {STEPS} steps | "
          f"sample steps>={SAMPLE_FROM} every {SAMPLE_EVERY} | worlds {worlds} x agents {agents}", flush=True)
    def paired(vals):
        """mean +/- SE of a per-cell paired delta (ddof=1)."""
        v = np.array([x for x in vals if np.isfinite(x)])
        if len(v) < 2:
            return (float(v.mean()) if len(v) else float("nan"), float("nan"), len(v))
        return float(v.mean()), float(v.std(ddof=1) / np.sqrt(len(v))), len(v)

    for clim in biomes:
        cells = []
        d_haz, d_age = [], []        # per-cell ON-OFF paired deltas
        off_haz, on_haz, off_age_l, on_age_l = [], [], [], []
        off_sn = on_sn = 0.0
        for ws in worlds:
            for as_ in agents:
                off = run_one(clim, ws, as_, bp_on=False)
                on = run_one(clim, ws, as_, bp_on=True)
                cells.append(on)
                off_sn += off["starv_n"]; on_sn += on["starv_n"]
                d_haz.append(on["starv_haz_k"] - off["starv_haz_k"])
                d_age.append(on["starv_mean_age_yr"] - off["starv_mean_age_yr"])
                off_haz.append(off["starv_haz_k"]); on_haz.append(on["starv_haz_k"])
                off_age_l.append(off["starv_mean_age_yr"]); on_age_l.append(on["starv_mean_age_yr"])
                print(f"  {clim} w{ws}a{as_}: OFF pop {off['final_pop']} haz {off['starv_haz_k']:.2f}/kpm "
                      f"age {off['starv_mean_age_yr']:.1f}y | ON pop {on['final_pop']} "
                      f"haz {on['starv_haz_k']:.2f}/kpm age {on['starv_mean_age_yr']:.1f}y "
                      f"groups {len(on['rows'])}", flush=True)
        mh, sh, nh = paired(d_haz)
        ma, sa, na = paired(d_age)
        oh, _, _ = paired(off_haz); onh, _, _ = paired(on_haz)
        oa, _, _ = paired(off_age_l); ona, _, _ = paired(on_age_l)
        print(f"  === {clim} PAIRED ON-OFF across {nh} cells ===")
        print(f"    starvation HAZARD /1000 person-months: OFF {oh:.2f} -> ON {onh:.2f} | "
              f"delta {mh:+.2f} +/- {sh:.2f}  ({'NOT reduced (z=%.1f)'%(mh/sh) if sh and abs(mh)<2*sh else 'reduced' if mh<0 else 'raised'})")
        print(f"    mean starvation AGE (yr):              OFF {oa:.1f} -> ON {ona:.1f} | "
              f"delta {ma:+.1f} +/- {sa:.1f}  ({'z=%.1f'%(ma/sa) if sa else ''})")
        summarize(clim, cells, age_off=oa, age_on=ona)


if __name__ == "__main__":
    main()
