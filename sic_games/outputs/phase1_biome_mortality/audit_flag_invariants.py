"""CHARTER RETROFIT — differential audit of every `enable_*` flag against its declared operator type.

`docs/MECHANISM_CHARTER.md` §3 assigns each mechanism a TYPE whose INVARIANT is a test. This harness does the
black-box half of that audit without touching the model: for each flag, run the realistic preset and the same
config with that ONE flag flipped, from the same seed, and record what actually changed.

The baseline is the PRESET (not bare defaults) so that prerequisites are satisfied — flipping a flag whose
prerequisite is off would falsely read as vacuous (this is the trap that made R-82 look inert).

CORRECTION (R-85c, 2026-07-18): the first version flipped booleans only. Because most flags are paired with a
gain that defaults to 0, turning a flag ON left the mechanism inert and produced a spurious "dead knob" verdict
for seven flags that are in fact simply OFF in the forager preset and live in `emergent_village_demog()`. The
harness now sets a live MAGNITUDE whenever it turns a flag on. Read `baseline_on` in the output: only rows with
`baseline_on=True` are genuine ON→OFF tests of a mechanism the preset actually runs.

What the signature is checked for:
  · VACUOUS      — signature identical to baseline. A specification bug (DE-19), UNLESS declared gauge fixing.
  · A-VIOLATION  — a flag typed Affiliation that moved a conserved quantity (it may only change the graph).
  · O-VIOLATION  — a flag typed Observer that changed anything at all.
  · GRAPH-INERT  — a flag typed Affiliation that changed quantities but NOT the graph (wrong type, or wrong unit).
"""
import os
import sys
import json

sys.path.insert(0, os.path.normpath("sic_games/outputs/phase1_social_evolution"))
from run_se0_controlled_climate import realistic_forager_demog

from sic_games.capacity import NPPCapacityField
from sic_games.climate import ClimateField
from sic_games.config import CarbonConfig, KcalEconomyConfig, SubstrateConfig
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world, world_lottery_climate

# charter §4 classification: flag -> primary type
TYPES = {
    "enable_productivity_mobility": "T", "enable_terrain_move_cost": "T", "enable_emergent_abandonment": "T",
    "enable_site_appraisal": "T", "enable_landscape_packing": "T",
    "enable_game": "P", "enable_agriculture": "P", "enable_agglomeration": "P", "enable_forage_cap": "P",
    "enable_catchment_ceiling": "P", "enable_resource_storability": "P", "enable_improved_land": "P",
    "enable_alluvial_renewal": "P",
    "enable_soil_depletion": "D",
    "enable_storage": "X", "enable_store_anchor": "X", "enable_provisioning": "X", "enable_leveling": "X",
    "enable_leader_share": "X",
    "enable_cred_status": "C", "enable_prowess_facet": "C", "enable_ascribed_mate_choice": "C",
    "enable_material_capture": "C", "enable_standing": "C",
    "enable_cred_renorm": "GAUGE",
    "enable_pair_bonds": "A", "enable_bonded_mating": "A", "enable_marriage_aggregation": "A",
    "enable_exogamy": "A", "enable_adaptive_connubium": "A", "enable_band_affiliation": "A",
    "enable_dynamic_bands": "A", "enable_emergent_band_size": "A", "enable_size_repulsion": "A",
    "enable_malnutrition_fission": "A", "enable_resource_directed_fusion": "A",
    "enable_aggregation_sedentism": "A", "enable_settlement_scalar_stress": "A", "enable_village_scaling": "A",
    "enable_village_budding": "A", "enable_morph": "A", "enable_economic_defensibility": "A",
    "enable_leader_office": "A", "enable_leader_coherence": "A", "enable_band_family_knobs": "A",
    "enable_orphan_mortality": "N", "enable_energetic_fertility": "N", "enable_sedentism_fertility": "N",
    "enable_life_history": "N", "enable_condition": "N", "enable_nutrition_synergy": "N",
    "enable_terrain_risk": "N", "enable_density_disease": "N", "enable_terrain_pathogen": "N",
    "enable_band_risk": "N", "enable_infanticide": "N",
    "enable_genome": "H", "enable_paternity": "H",
    "enable_tier2_shock": "F",
    "enable_genealogy_log": "O",
    # ── RETROFIT 2026-07-26 (R-105/R-106) ───────────────────────────────────────────────────────
    # The table above was frozen at R-85 (2026-07-18). Everything built since — the whole
    # legitimacy/resentment arc (R-86…R-99), the R-103 accumulation stack, and the R-105 fix — was
    # NEVER CLASSIFIED, so 15 of 75 flags had no invariant and the audit could not see them. That
    # blind spot has a cost on the record: R-104's circumscription gradient ran with
    # `enable_material_inheritance`/`_lineage_tribute`/`_noble_leveling_exemption` all OFF and its
    # "material stays flat" reading was void — the mechanisms under test were disabled.
    # Types per MECHANISM_CHARTER §3. The three marked PROVISIONAL are judgement calls made during
    # the retrofit and want the author's confirmation (§3.1 puts the declaration in the docstring).
    "enable_aggl_ceiling": "P",                    # bounds field→agent extraction: Σ extracted ≤ availability
    "enable_legitimacy": "C",                      # achieved cred → ascribed rank (capital → capital)
    "enable_delegitimation": "C",                  # the reverse conversion (gumsa → gumlao)
    "enable_relative_legitimacy": "C",             # same conversion, scale-free criterion
    "enable_local_ascription": "C",                # same conversion, per-community scoping
    "enable_rank_hierarchy": "C",                  # ranked lineages → a rung of hierarchy
    "enable_relative_resentment": "C",             # PROVISIONAL — grievance state feeding delegitimation
    "enable_resentment_accumulator": "C",          # PROVISIONAL — ditto, accumulating rather than tracking
    "enable_village_resentment": "C",              # PROVISIONAL — ditto, held by the village unit
    "enable_stratification_inequality_gate": "C",  # inequality state → society label (label feeds κ, so not O)
    "enable_lineage_branching": "H",               # copies a lineage tag across a BIRTH event
    "enable_lineage_split": "A",                   # segments the lineage graph; must move no quantity
    "enable_bud_hazard": "A",                      # fission rule for the settlement graph (2026-07-27)
    "enable_wealth_obligation": "C",               # material -> a claim on another agent's output (Sahlins)
    "enable_material_inheritance": "X",            # dead → heirs; Σ material conserved
    "enable_lineage_tribute": "X",                 # commoners → chiefly lineage; Σ material conserved
    "enable_noble_leveling_exemption": "X",        # modifies who the leveling exchange takes from
}
# ENRICHED BASELINE. The bare preset has the whole elite layer OFF, so flipping e.g. `enable_leveling` alone
# would do nothing for want of MATERIAL and read as VACUOUS — precisely the prerequisite false-negative that made
# R-82 look inert. The baseline therefore turns the prerequisite CHAINS on so each flag is flipped in a live
# context. (Charter §3.1: "unit" and context are part of a mechanism's identity.)
ENRICH = dict(
    enable_material_capture=True, material_hide_frac=0.07, material_capture_frac=0.0,
    material_decay=0.002, aggrandizer_frac=0.15,
    enable_leveling=True, leveling_strength=0.79, leveling_share=0.8,
    enable_leader_share=True, leader_share_frac=0.20,
    enable_leader_office=True, office_grievance_gain=0.05,
    enable_economic_defensibility=True,
    enable_aggregation_sedentism=True,
)
# RETROFIT 2026-07-26. The elite/accumulation arc needs its own prerequisites live or all 15 newly-classified
# flags read as VACUOUS for want of context — the same false-negative ENRICH exists to prevent. NOTE: this
# CHANGES THE BASELINE, so verdicts here are not directly comparable to the R-85 run; the whole audit is
# re-run rather than patched. Values are run_campaign.py's ELITE_KW (i.e. how the project actually runs it).
ENRICH.update(
    enable_cred_status=True, cred_seed_sigma=0.5, cred_inherit_sigma=0.1,
    enable_band_affiliation=True, enable_morph=True,
    enable_agglomeration=True, aggl_mode="point", aggl_beta=1.15, aggl_tier2=5.0,
    enable_catchment_ceiling=True,
    enable_legitimacy=True, legit_feast_frac=0.25, legit_cred_gain=10.0, legit_threshold=0.15, legit_decay=0.02,
    enable_delegitimation=True, resent_alpha=0.001, resent_threshold=0.5, resent_privilege_ref=10.0,
    enable_lineage_branching=True, lineage_branch_rate=0.05,
)

# MAGNITUDES. **A BOOLEAN FLIP IS NOT ENABLING A MECHANISM.** Most flags are paired with a gain that DEFAULTS TO
# ZERO, so flipping the flag True while leaving the gain at 0 produces no change — and reads as a dead mechanism.
# The first version of this harness did exactly that and produced a spurious "7 dead knobs" finding (retracted;
# see RESULTS R-85c). Values below are the live ones used by `emergent_village_demog()` and the stage harnesses,
# so a flag turned ON here is turned on the way the project actually runs it.
MAGNITUDE = {
    "enable_leader_coherence": {"leader_coherence_gain": 2.0},
    "enable_size_repulsion": {"repulsion_gain": 0.3},
    "enable_village_scaling": {"village_gain": 5.0},
    "enable_site_appraisal": {"site_gain": 0.3, "site_radius": 2, "site_lambda": 1.0},
    "enable_terrain_move_cost": {"move_cost_kcal": 750.0},          # 0.01·BURN ≈ a 10 km move
    "enable_malnutrition_fission": {"malnutrition_fission_gain": 2.0},
    "enable_terrain_pathogen": {"pathogen_gamma": 1.0},
    "enable_leveling": {"leveling_strength": 0.79, "leveling_share": 0.8},
    "enable_leader_share": {"leader_share_frac": 0.20},
    "enable_leader_office": {"office_grievance_gain": 0.05},
    "enable_material_capture": {"material_hide_frac": 0.07},
    # RETROFIT 2026-07-26 — R-85c's lesson applied to the elite arc. `lineage_branch_rate`,
    # `lineage_split_rate`, `legit_cred_gain` and `legit_feast_frac` ALL default to 0.0, so flipping
    # their flags without a magnitude would have reproduced the retracted "dead knob" finding exactly.
    # Values are the live ones from run_campaign.py's ELITE_KW / the R-104 STACK.
    "enable_legitimacy": {"legit_feast_frac": 0.25, "legit_cred_gain": 10.0, "legit_threshold": 0.15,
                          "legit_decay": 0.02},
    "enable_delegitimation": {"resent_alpha": 0.001, "resent_threshold": 0.5, "resent_privilege_ref": 10.0},
    "enable_relative_legitimacy": {"legit_rel_multiplier": 2.0},
    "enable_relative_resentment": {"resent_effect_threshold": 0.8},
    "enable_village_resentment": {"resent_years_to_revolt": 80.0},
    "enable_rank_hierarchy": {"rank_hierarchy_frac": 0.15},
    "enable_lineage_branching": {"lineage_branch_rate": 0.05},
    "enable_lineage_split": {"lineage_split_rate": 0.00003, "lineage_split_min_segment": 8},
    "enable_lineage_tribute": {"lineage_tribute_frac": 0.15},
    "enable_material_inheritance": {"material_inheritance_rule": "primogeniture"},
    "enable_noble_leveling_exemption": {"noble_exemption_frac": 1.0},
    "enable_stratification_inequality_gate": {"stratification_gini_min": 0.40},
    # ALSO RETROFIT 2026-07-26 — five entries R-85c's own fix MISSED. Each of these flags pairs with a gain that
    # defaults to 0 while the project runs it non-zero, so this harness has been flipping them dead ever since.
    # Found by `tests/test_mechanism_audit_coverage.py`, which now fails if a new one appears.
    "enable_ascribed_mate_choice": {"ascribed_mate_strength": 2.5},   # default 0.0, presets 2.5
    "enable_bonded_mating": {"bonded_mate_radius": 1},                # default 0,   presets 1
    "enable_cred_status": {"cred_seed_sigma": 0.5, "cred_inherit_sigma": 0.1},   # default 0.0 ⇒ all cred equal
    "enable_game": {"game_meat_frac": 0.55, "game_meat_cv": 0.73},    # default 0.0 ⇒ no meat stream at all
    "enable_prowess_facet": {"prowess_decay": 0.05},                  # default 0.0, adopted value 0.05
}
# Flags whose only prefix-matching parameter is legitimately 0 in the project — no magnitude is missing.
# `enable_paternity` carries the `_father` link (R-74); `paternal_provision_frac` is 0.0 in EVERY preset, so a
# zero default is the live value rather than a dead knob.
MAGNITUDE_EXEMPT = {"enable_paternity"}

# Known prerequisite chains: if a flag's prereq is not satisfied in the arm, "no change" is UNINFORMATIVE
# rather than a spec bug. Reported separately so a false VACUOUS is never called a defect.
PREREQ = {
    "enable_leveling": ("enable_material_capture",), "enable_leader_share": ("enable_material_capture",),
    "enable_leader_office": ("enable_band_affiliation",), "enable_improved_land": ("enable_economic_defensibility",),
    "enable_alluvial_renewal": ("enable_soil_depletion",), "enable_soil_depletion": ("enable_agriculture",),
    "enable_village_budding": ("enable_aggregation_sedentism",),
    "enable_catchment_ceiling": ("enable_aggregation_sedentism",),
    "enable_settlement_scalar_stress": ("enable_aggregation_sedentism",),
    "enable_sedentism_fertility": ("enable_aggregation_sedentism",),
    "enable_adaptive_connubium": ("enable_pair_bonds",), "enable_marriage_aggregation": ("enable_pair_bonds",),
    "enable_bonded_mating": ("enable_pair_bonds",), "enable_exogamy": ("enable_band_affiliation",),
    "enable_emergent_band_size": ("enable_band_affiliation",), "enable_dynamic_bands": ("enable_band_affiliation",),
    "enable_band_family_knobs": ("enable_band_affiliation",), "enable_size_repulsion": ("enable_band_affiliation",),
    "enable_malnutrition_fission": ("enable_band_affiliation",),
    "enable_resource_directed_fusion": ("enable_band_affiliation",),
    "enable_leader_coherence": ("enable_band_affiliation",),
    "enable_paternity": ("enable_cred_status",),          # the _father gating discovered in R-74
    "enable_ascribed_mate_choice": ("enable_cred_status",), "enable_prowess_facet": ("enable_cred_status",),
    "enable_cred_renorm": ("enable_cred_status",), "enable_material_capture": ("enable_game",),
    # RETROFIT 2026-07-26 — the elite arc's chains. Without these, every flag below reads "no change"
    # for want of a prerequisite and would be miscalled a spec bug.
    "enable_aggl_ceiling": ("enable_agglomeration", "enable_catchment_ceiling", "enable_aggregation_sedentism"),
    "enable_legitimacy": ("enable_cred_status",),
    "enable_delegitimation": ("enable_legitimacy",),
    "enable_relative_legitimacy": ("enable_legitimacy",),
    "enable_local_ascription": ("enable_legitimacy",),
    "enable_rank_hierarchy": ("enable_legitimacy",),
    "enable_relative_resentment": ("enable_delegitimation",),
    "enable_resentment_accumulator": ("enable_delegitimation",),
    "enable_village_resentment": ("enable_delegitimation",),
    "enable_material_inheritance": ("enable_material_capture",),
    "enable_lineage_tribute": ("enable_material_capture", "enable_legitimacy"),
    "enable_noble_leveling_exemption": ("enable_leveling", "enable_legitimacy"),
    "enable_lineage_split": ("enable_lineage_branching",),
    "enable_bud_hazard": ("enable_village_budding",),
    "enable_wealth_obligation": ("enable_material_capture",),
    "enable_stratification_inequality_gate": ("enable_morph",),
}

# conserved-quantity fields: an A-typed flag must NOT move these
QUANT = ("tot_wealth", "tot_material", "pop_traj", "final_pop", "births", "deaths")
GRAPH = ("band_sig", "n_bonds", "n_settlements")


def signature(seed=0, steps=120, n=300, flip=None):
    k = world_lottery_climate(seed, terrain="coastal", climate="temperate")
    f = generate_world(k, mode="climate")
    hf = ClimateField(NPPCapacityField(f, 75000.0, patch=(20, 20, 60), mode="tallavaara", aquatic=True,
                                       enable_depletion=True), a_seas=0.5)
    hf0 = NPPCapacityField(f, 75000.0, patch=(20, 20, 60), mode="tallavaara", aquatic=True, enable_depletion=True)
    land = [(x, y) for y in range(100) for x in range(100) if f.isWater[y, x] == 0 and hf0.level(x, y) > 0]
    d = realistic_forager_demog().model_copy(update=ENRICH)
    if flip is not None:
        cur = getattr(d, flip, None)
        if cur is None:
            return None
        upd = {flip: (not cur)}
        if not cur:                                   # turning a flag ON must also give it a LIVE magnitude,
            upd.update(MAGNITUDE.get(flip, {}))       # else the zero-default gain makes it read as inert
        d = d.model_copy(update=upd)
    w = TerrainWorld(n_agents=n, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, game_stream=False, seed=seed,
                     carbon_cfg=CarbonConfig(kappa=1.5),
                     substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                                   contest_exponent=1.5, move_cost_flat=0.0),
                     harvest_field=hf, placement_positions=[land[i % len(land)] for i in range(n)],
                     demography_cfg=d)
    traj, births, deaths = [], 0, 0
    for t in range(steps):
        w.step()
        if not w.agent_list:
            break
        births += getattr(w, "births_this_step", 0)
        deaths += getattr(w, "deaths_starv_this_step", 0) + getattr(w, "deaths_senesc_this_step", 0)
        if t % 10 == 0:
            traj.append(len(w.agent_list))
    al = w.agent_list
    bands: dict = {}
    for a in al:
        bands[a._group.band_id] = bands.get(a._group.band_id, 0) + 1
    return {
        "pop_traj": tuple(traj),
        "final_pop": len(al),
        "tot_wealth": round(sum(getattr(a, "wealth", 0.0) for a in al), 6),
        "tot_material": round(sum(getattr(a, "material", 0.0) for a in al), 6),
        "band_sig": tuple(sorted(bands.values())),
        "n_bonds": sum(1 for a in al if getattr(a, "_partner", None) is not None),
        "n_settlements": len(getattr(w, "_settlement_sites", []) or []),
        "births": births,
        "deaths": deaths,
        "pos_hash": hash(tuple(sorted((a.pos for a in al)))),
    }


def main():
    prog = os.path.join(os.path.dirname(__file__), "progress_flag_audit.txt")
    base = signature()
    flags = sorted(f for f in TYPES if hasattr(realistic_forager_demog(), f))
    rows = []
    for i, fl in enumerate(flags, 1):
        with open(prog, "w") as fh:
            fh.write(f"{i}/{len(flags)} {fl}\n")
            fh.flush()
        try:
            sig = signature(flip=fl)
        except Exception as e:                       # a CRASH is itself an audit finding — record and continue
            print(f"{i:3d}/{len(flags)} {fl:38s} [{TYPES[fl]}] -> *** CRASH *** {type(e).__name__}: {e}", flush=True)
            rows.append({"flag": fl, "type": TYPES[fl], "baseline_on": None,
                         "changed": ["CRASH"], "unmet_prereq": [], "error": f"{type(e).__name__}: {e}"})
            continue
        if sig is None:
            continue
        diff = sorted(kk for kk in base if base[kk] != sig[kk])
        cfg0 = realistic_forager_demog().model_copy(update=ENRICH)
        unmet = [p for p in PREREQ.get(fl, ()) if not getattr(cfg0, p, False)]
        rows.append({"flag": fl, "type": TYPES[fl], "baseline_on": getattr(cfg0, fl),
                     "changed": diff, "unmet_prereq": unmet})
        print(f"{i:3d}/{len(flags)} {fl:38s} [{TYPES[fl]}] -> "
              f"{','.join(diff) if diff else '*** NO CHANGE ***'}", flush=True)

    out = os.path.join(os.path.dirname(__file__), "flag_audit.json")
    with open(out, "w") as fh:
        json.dump({"baseline": {k: str(v) for k, v in base.items()}, "rows": rows}, fh, indent=1)

    print("\n" + "=" * 78)
    print("VERDICTS (charter §3 invariants)")
    print("=" * 78)
    for r in rows:
        ch, ty = set(r["changed"]), r["type"]
        v = []
        if "CRASH" in ch:
            print(f"  {r['flag']:38s} [{ty}] :: *** CRASH *** {r.get('error','')}")
            continue
        if not ch:
            if r["unmet_prereq"]:
                v.append(f"no-change BUT PREREQ UNMET {r['unmet_prereq']} — uninformative, not a defect")
            else:
                v.append("VACUOUS — spec bug (DE-19) unless gauge" if ty != "GAUGE"
                         else "gauge OK (invariance is the point)")
        else:
            if ty == "GAUGE":
                v.append("GAUGE-VIOLATION — changed an observable")
            if ty == "O" and ch:
                v.append("O-VIOLATION — observer mutated state")
            if ty == "A":
                if ch & set(QUANT):
                    v.append(f"A-VIOLATION — moved conserved quantity: {sorted(ch & set(QUANT))}")
                if not (ch & set(GRAPH)):
                    v.append("GRAPH-INERT — typed A but changed no graph field")
        if v:
            # was r['preset'] — a KeyError on the first row that produced a verdict, i.e. the reporting
            # path only ever ran when the audit found NOTHING. Fixed in the 2026-07-26 retrofit.
            print(f"  {r['flag']:38s} [{ty}] baseline_on={str(r['baseline_on']):5s} :: {' | '.join(v)}")
    print("\nWrote", out)


if __name__ == "__main__":
    main()
