"""BATTERY 1 — float the INERT mechanisms, and keep "inert" separate from "untestable".

WHY A BATTERY AND NOT A CHECK (2026-07-26). The existing flag audit
(`outputs/phase1_biome_mortality/audit_flag_invariants.py`) returned "no defects" while being incapable of
finding one. Four measured faults, all of which this harness is built against:

  1. SCOPE WAS SELF-DECLARED — it iterated its own hand-maintained TYPES table (`flags = sorted(f for f in
     TYPES ...)`), so 15 of 75 mechanisms were invisible, including the entire accumulation stack.
     -> HERE: scope is enumerated from `DemographyConfig.model_fields`. The model is the denominator.
  2. DEAD KNOBS — 5 flags were flipped with their gain at a 0 default (`cred_seed_sigma`, `game_meat_frac`,
     `ascribed_mate_strength`, `bonded_mate_radius`, `prowess_decay`), i.e. turned "on" into inertness.
     -> HERE: every flag turned ON also receives its live MAGNITUDE, and a flag with a zero-defaulting gain and
        no magnitude is a HARNESS-FAIL, not a verdict.
  3. NO CONTROLS — a broken harness and a true null produce the same output. Measured tonight: the catchment
     ceiling read VACUOUS because the regime formed ZERO settlements, so a settlement-gated mechanism had no
     site to act on. That is not a dead mechanism; it is a dead world.
     -> HERE: every flag carries a NULL control (repeat the baseline: must be bit-identical) and a POSITIVE
        control (a known-live flip: must differ). No verdict is emitted for a flag whose controls failed.
  4. A REGIME THAT COULD NOT FIRE THE MECHANISMS — 120 steps, 300 agents, population DECLINING 300 -> 213,
     zero settlements, max cell occupancy 5.
     -> HERE: a long seeded run in a calibrated regime, plus a PRECONDITION probe per mechanism. If the unit a
        mechanism operates on never came into existence (no settlement, no pair-bond, no ascribed noble, no
        death), the verdict is UNTESTABLE with the unmet precondition named — never INERT.

VERDICTS
  LIVE        signature moved; controls passed. Reports which fields moved.
  INERT       signature bit-identical to baseline, controls passed, precondition SATISFIED. A real finding:
              the mechanism is wired in but does nothing in the regime the project actually runs.
  UNTESTABLE  precondition unmet — the mechanism's unit never existed. Says which one. NOT a defect.
  HARNESS     controls failed, or a magnitude is missing. The instrument, not the model.

Run:  py -3 -u sic_games/outputs/mechanism_battery/battery1_liveness.py        (from repo root)
Env:  B_STEPS (default 800) · B_N (600) · B_PATCH (24) · B_SEED (0) · B_WORKERS (6) · B_ONLY (csv of flags)
"""
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "sic_games", "outputs", "phase1_social_evolution"))
sys.path.insert(0, os.path.join(ROOT, "sic_games", "outputs", "phase1_biome_mortality"))

STEPS = int(os.environ.get("B_STEPS", "800"))
NAGENT = int(os.environ.get("B_N", "600"))
PATCH = int(os.environ.get("B_PATCH", "24"))
SEED = int(os.environ.get("B_SEED", "0"))
WORKERS = int(os.environ.get("B_WORKERS", "6"))
ONLY = [f for f in os.environ.get("B_ONLY", "").split(",") if f]

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "battery1_results.json")

# ── the baseline: THE PROJECT AS ACTUALLY RUN ───────────────────────────────────────────────────
# Charter §3.1: a mechanism's unit and context are part of its identity, so the baseline must be the live
# stack, not bare defaults. This is run_campaign.py's configuration (village substrate + ELITE_KW + the
# R-103 accumulation chain), i.e. everything the campaigns turn on, so a flip is tested in context.
VILLAGE = dict(enable_marriage_aggregation=True, enable_aggregation_sedentism=True,
               enable_catchment_ceiling=True, enable_aggl_ceiling=True, settle_catchment_radius=1,
               enable_settlement_scalar_stress=True, enable_landscape_packing=True,
               enable_cred_status=True, cred_seed_sigma=0.5, cred_inherit_sigma=0.1,
               enable_paternity=True, divorce_rate=0.004, enable_morph=True)
ELITE = dict(
    enable_material_capture=True, material_hide_frac=0.07, material_decay=0.002, aggrandizer_frac=0.15,
    enable_leader_share=True, leader_share_frac=0.20,
    enable_leveling=True, leveling_strength=0.79, leveling_share=0.8,
    enable_leader_office=True, office_grievance_gain=0.05,
    enable_legitimacy=True, legit_feast_frac=0.25, legit_cred_gain=10.0, legit_threshold=0.15, legit_decay=0.02,
    enable_delegitimation=True, resent_alpha=0.001, resent_threshold=0.5, resent_privilege_ref=10.0,
    enable_relative_legitimacy=True, legit_rel_multiplier=2.0,
    enable_relative_resentment=True, resent_effect_threshold=0.8,
    enable_resentment_accumulator=True, enable_village_resentment=True,
    resent_years_to_revolt=80.0, enable_local_ascription=True,
    enable_rank_hierarchy=True, rank_hierarchy_frac=0.15,
    enable_lineage_branching=True, lineage_branch_rate=0.05,
    enable_lineage_split=True, lineage_split_rate=0.00003, lineage_split_min_segment=8,
    enable_material_inheritance=True, material_inheritance_rule="primogeniture", material_heir_by_status=True,
    enable_lineage_tribute=True, lineage_tribute_frac=0.15,
    enable_noble_leveling_exemption=True, noble_exemption_frac=1.0,
    enable_ascribed_mate_choice=True, ascribed_mate_strength=2.5,
)

# ── PRECONDITIONS: the UNIT a mechanism needs in existence before "no change" can mean anything ──
# Keyed to fields the run measures. This table is the direct product of tonight's finding — the ceiling was
# called inert in a world with zero settlements.
PRECOND = {
    "settlements": ("max_settlements", "no settlement ever formed"),
    "pairs": ("bonds", "no pair-bond ever formed"),
    "material": ("tot_material", "no durable material was ever produced"),
    "ascribed": ("n_ascribed", "no agent was ever ascribed (no noble stratum)"),
    "deaths": ("deaths", "nobody died (a death-triggered mechanism cannot fire)"),
    "births": ("births", "nobody was born (a birth-triggered mechanism cannot fire)"),
    "villages": ("n_villages", "no band ever exceeded the village threshold"),
    "lineages": ("n_lineages", "only one lineage exists (no lineage structure to act on)"),
    # A mechanism with a SIZE gate needs a unit that reached that size. Measured 2026-07-27: village budding
    # read INERT in this regime purely because the 600-agent world never grows a village to the fission
    # threshold of 170 - it fires at that same unmodified threshold in a larger world. "No village big enough"
    # is a dead WORLD, not a dead mechanism, and must not be reported as one.
    "big_village": ("max_village", "no village ever reached village_fission_threshold"),
}
NEEDS = {
    # settlement-gated
    "enable_catchment_ceiling": "settlements", "enable_aggl_ceiling": "settlements",
    "enable_settlement_scalar_stress": "settlements", "enable_village_budding": "big_village",
    "enable_village_scaling": "villages", "enable_sedentism_fertility": "settlements",
    "enable_emergent_abandonment": "settlements", "enable_site_appraisal": "settlements",
    "enable_aggregation_sedentism": "settlements",
    # pair-gated
    "enable_bonded_mating": "pairs", "enable_adaptive_connubium": "pairs",
    "enable_marriage_aggregation": "pairs", "enable_exogamy": "pairs",
    "enable_ascribed_mate_choice": "pairs", "enable_pair_bonds": "pairs",
    # material-gated
    "enable_leveling": "material", "enable_leader_share": "material",
    "enable_material_inheritance": "deaths", "enable_lineage_tribute": "material",
    "enable_noble_leveling_exemption": "material", "enable_material_capture": "material",
    # ascription-gated
    "enable_delegitimation": "ascribed", "enable_relative_legitimacy": "ascribed",
    "enable_relative_resentment": "ascribed", "enable_resentment_accumulator": "ascribed",
    "enable_village_resentment": "ascribed", "enable_local_ascription": "ascribed",
    "enable_rank_hierarchy": "ascribed", "enable_stratification_inequality_gate": "villages",
    # descent-gated
    "enable_lineage_split": "lineages", "enable_lineage_branching": "births",
    "enable_orphan_mortality": "deaths", "enable_infanticide": "births",
}

POSITIVE_CONTROL = "enable_game"     # measured live in every regime tried; flipping it must move the signature


def _magnitudes():
    import audit_flag_invariants as A
    return A.MAGNITUDE, getattr(A, "MAGNITUDE_EXEMPT", set())


_CACHE: dict = {}


def baseline_cfg():
    """THE config the worlds are actually built from. A flag's 'current value' MUST be read from this and not
    from bare `DemographyConfig()` — the first version read defaults, so e.g. `enable_game` (default False,
    preset True) 'flipped' to True when it was already True, and the flip was a silent no-op. The C2 positive
    control caught it before any verdict was emitted; without the control every flag would have read INERT."""
    from run_se0_controlled_climate import emergent_village_demog
    return emergent_village_demog().model_copy(update=VILLAGE).model_copy(update=ELITE)


def _build(update, seed=SEED, n=NAGENT, patch=PATCH, terr="coastal", clim="temperate"):
    from run_se0_controlled_climate import emergent_village_demog
    from sic_games.capacity import NPPCapacityField
    from sic_games.climate import ClimateField
    from sic_games.config import CarbonConfig, KcalEconomyConfig, SubstrateConfig
    from sic_games.phase1_model import TerrainWorld
    from sic_games.terrain import generate_world, world_lottery_climate
    k = world_lottery_climate(seed, terrain=terr, climate=clim)
    f = generate_world(k, mode="climate")
    hf = ClimateField(NPPCapacityField(f, 75000.0, patch=(20, 20, patch), mode="tallavaara", aquatic=True,
                                       enable_depletion=True), a_seas=0.5)
    hf0 = NPPCapacityField(f, 75000.0, patch=(20, 20, patch), mode="tallavaara", aquatic=True,
                           enable_depletion=True)
    land = [(x, y) for y in range(100) for x in range(100) if f.isWater[y, x] == 0 and hf0.level(x, y) > 0]
    d = emergent_village_demog().model_copy(update=VILLAGE).model_copy(update=ELITE).model_copy(update=update)
    return TerrainWorld(n_agents=n, kcal_cfg=KcalEconomyConfig(), terrain_knobs=k, game_stream=False, seed=seed,
                        carbon_cfg=CarbonConfig(kappa=1.5),
                        substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                                      contest_exponent=1.5, move_cost_flat=0.0),
                        harvest_field=hf, placement_positions=[land[i % len(land)] for i in range(n)],
                        demography_cfg=d)


def signature(update, steps=STEPS, **world):
    """Run one world; return a rich signature + the precondition probes + wall seconds."""
    t0 = time.time()
    w = _build(update, **world)
    births = deaths = 0
    max_settle = 0
    max_village = 0
    for _ in range(steps):
        w.step()
        if not w.agent_list:
            break
        births += getattr(w, "births_this_step", 0)
        deaths += getattr(w, "deaths_starv_this_step", 0) + getattr(w, "deaths_senesc_this_step", 0)
        max_settle = max(max_settle, len(getattr(w, "_settlement_sites", []) or []))
    # largest VILLAGE (settlement neighbourhood), vs the fission threshold - the size gate budding needs
    _sep = getattr(w._demog, "settle_radius", 2)
    _ca: dict = {}
    for _a in w.agent_list:
        _ca.setdefault(_a.pos, 0)
        _ca[_a.pos] += 1
    for (_sx, _sy) in (getattr(w, "_settlement_sites", {}) or {}):
        _v = sum(_ca.get((_sx + dx, _sy + dy), 0)
                 for dx in range(-_sep, _sep + 1) for dy in range(-_sep, _sep + 1))
        max_village = max(max_village, _v)
    al = w.agent_list
    bands: dict = {}
    lin: set = set()
    # The lineage tag is `_lineage` (phase1_model:403) and ascription is a WORLD-level set of ascribed lineage
    # ids `_lineage_ascribed` (phase1_model:339) — NOT an agent attribute. The first version probed
    # `a.lineage_id` and `a.ascribed`, neither of which exists, so both probes read a constant (1 lineage, 0
    # ascribed) regardless of the model. That would have marked the whole legitimacy arc UNTESTABLE on a
    # measurement artifact — the same error class this battery exists to catch.
    asc_lin = set(getattr(w, "_lineage_ascribed", ()) or ())
    for a in al:
        bands[a._group.band_id] = bands.get(a._group.band_id, 0) + 1
        lin.add(getattr(a, "_lineage", None))
    sig = dict(
        final_pop=len(al),
        pop_hash=hash(tuple(sorted(bands.values()))),
        tot_wealth=round(sum(getattr(a, "wealth", 0.0) for a in al), 6),
        tot_material=round(sum(getattr(a, "material", 0.0) for a in al), 6),
        tot_cred=round(sum(getattr(a, "cred", 0.0) for a in al), 6),
        pos_hash=hash(tuple(sorted(a.pos for a in al))),
        bonds=sum(1 for a in al if getattr(a, "_partner", None) is not None),
        n_settlements=len(getattr(w, "_settlement_sites", []) or []),
        n_ascribed=sum(1 for a in al if getattr(a, "_lineage", None) in asc_lin),
        n_ascribed_lineages=len(asc_lin),
        n_villages=sum(1 for v in bands.values() if v > getattr(w._demog, "band_split_size", 45)),
        n_lineages=len(lin),
        # LAND TENURE (added 2026-07-27). The signature had 13 fields and none of them was ownership, so a
        # mechanism whose whole job is to change who owns which cell — `enable_improved_land`,
        # `enable_economic_defensibility` — could do exactly that and still read INERT. The instrument could
        # not see the quantity the mechanism moves. Same class as the settle_med/village_med mix-up.
        n_owned=len(getattr(w, "_cell_owner", {}) or {}),
        n_claims=len(getattr(w, "_cell_claim", {}) or {}),
        births=births, deaths=deaths,
    )
    probes = dict(max_settlements=max_settle, bonds=sig["bonds"], tot_material=sig["tot_material"],
                  n_ascribed=sig["n_ascribed"] or sig["n_ascribed_lineages"], deaths=deaths, births=births,
                  n_villages=sig["n_villages"], n_lineages=sig["n_lineages"],
                  max_village=(max_village if max_village >= getattr(w._demog, "village_fission_threshold", 170)
                               else 0))
    return sig, probes, round(time.time() - t0, 1)


def _baseline():
    if "base" not in _CACHE:
        _CACHE["base"] = signature({})
    return _CACHE["base"]


def assess(flag):
    """One mechanism: flip it, run controls, return a verdict."""
    from sic_games.demography import DemographyConfig
    MAG, EXEMPT = _magnitudes()
    base_sig, probes, base_s = _baseline()
    cfg = baseline_cfg()
    cur = getattr(cfg, flag, None)
    if cur is None:
        return dict(flag=flag, verdict="HARNESS", note="flag not on DemographyConfig")

    upd = {flag: (not cur)}
    if not cur:                                   # turning ON: a live magnitude is mandatory
        mag = MAG.get(flag)
        if mag:
            upd.update(mag)
        elif flag not in EXEMPT:
            stem = flag[len("enable_"):][:6]
            gains = {k: getattr(cfg, k) for k in DemographyConfig.model_fields
                     if not k.startswith("enable_") and k.startswith(stem)
                     and isinstance(getattr(cfg, k), (int, float)) and not isinstance(getattr(cfg, k), bool)}
            if gains and all(v == 0 for v in gains.values()):
                return dict(flag=flag, verdict="HARNESS", baseline_on=cur,
                            note=f"no MAGNITUDE and every gain defaults to 0 ({gains}) — would audit a dead knob")

    try:
        flip_sig, _, flip_s = signature(upd)
    except Exception as e:
        return dict(flag=flag, verdict="CRASH", baseline_on=cur, note=f"{type(e).__name__}: {e}")

    changed = sorted(k for k in base_sig if base_sig[k] != flip_sig[k])
    need = NEEDS.get(flag)
    unmet = None
    if need:
        key, why = PRECOND[need]
        if not probes.get(key):
            unmet = why
    if unmet is None:
        # CONFIG PREREQUISITES, not just world units. A flag whose chain is OFF in the baseline has nothing to
        # act on no matter how the world turns out - measured 2026-07-27: `enable_improved_land` read INERT
        # here only because `enable_economic_defensibility` is off in the campaign baseline, and it is
        # demonstrably live once that chain is on. Reuses the audit's PREREQ table rather than a second list.
        try:
            import audit_flag_invariants as _A
            _missing = [p for p in _A.PREREQ.get(flag, ()) if not getattr(cfg, p, False)]
        except Exception:
            _missing = []
        if _missing:
            unmet = f"prerequisite(s) OFF in the baseline config: {', '.join(_missing)}"

    if changed:
        verdict = "LIVE"
    elif unmet:
        verdict = "UNTESTABLE"
    else:
        verdict = "INERT"
    return dict(flag=flag, verdict=verdict, baseline_on=cur, changed=changed,
                unmet_precondition=unmet, secs=flip_s, base_secs=base_s,
                delta_secs=round(flip_s - base_s, 1))


def main():
    from sic_games.demography import DemographyConfig
    flags = ONLY or sorted(k for k in DemographyConfig.model_fields if k.startswith("enable_"))
    print(f"BATTERY 1 — liveness of {len(flags)} mechanisms | regime: {NAGENT} agents, patch {PATCH}, "
          f"{STEPS} steps, seed {SEED} | {WORKERS} workers", flush=True)

    # ── CONTROLS FIRST. No verdict is trustworthy until the instrument is. ──────────────────────
    print("\nCONTROLS", flush=True)
    b1, probes, s1 = signature({})
    b2, _, _ = signature({})
    null_ok = (b1 == b2)
    print(f"  C1 NULL      baseline run twice -> {'IDENTICAL (PASS)' if null_ok else '*** DIFFERS (FAIL) ***'}"
          f"   [{s1}s per run]", flush=True)
    pos_cfg = baseline_cfg()
    p_upd = {POSITIVE_CONTROL: (not getattr(pos_cfg, POSITIVE_CONTROL))}
    p_sig, _, _ = signature(p_upd)
    pos_ok = (p_sig != b1)
    print(f"  C2 POSITIVE  flip {POSITIVE_CONTROL} -> "
          f"{'DIFFERS (PASS)' if pos_ok else '*** IDENTICAL (FAIL — harness detects nothing) ***'}", flush=True)
    print(f"  PRECONDITIONS in the baseline regime: {probes}", flush=True)
    if not (null_ok and pos_ok):
        print("\n*** CONTROLS FAILED — no verdicts emitted. Fix the instrument first. ***")
        json.dump(dict(controls=dict(null=null_ok, positive=pos_ok), probes=probes, rows=[]),
                  open(OUT, "w"), indent=1)
        return
    dead_units = [f"{k}={v}" for k, v in probes.items() if not v]
    if dead_units:
        print(f"  NOTE: units that never came into existence -> {dead_units}\n"
              f"        mechanisms needing them will be UNTESTABLE, not INERT.", flush=True)

    # CRASH-SAFE / RESUMABLE. The machine restarts on a schedule outside our control, so results are flushed
    # after EVERY flag and an existing result file is resumed rather than overwritten. A restart costs at most
    # the one flag in flight.
    done: dict = {}
    if os.path.exists(OUT):
        try:
            prev = json.load(open(OUT, encoding="utf-8"))
            done = {r["flag"]: r for r in prev.get("rows", []) if r.get("verdict") not in (None, "CRASH")}
            if done:
                print(f"  RESUMING: {len(done)} flags already have verdicts in {os.path.basename(OUT)}",
                      flush=True)
        except Exception:
            done = {}
    todo = [f for f in flags if f not in done]

    def flush(rows_now):
        with open(OUT, "w", encoding="utf-8") as fh:
            json.dump(dict(controls=dict(null=null_ok, positive=pos_ok), probes=probes,
                           regime=dict(n=NAGENT, patch=PATCH, steps=STEPS, seed=SEED),
                           complete=len(rows_now) == len(flags), rows=rows_now), fh, indent=1)

    t0 = time.time()
    rows = list(done.values())
    flush(rows)
    with ProcessPoolExecutor(max_workers=WORKERS) as ex:
        for i, r in enumerate(ex.map(assess, todo), 1):
            rows.append(r)
            flush(rows)                                   # every flag, not at the end
            tag = {"LIVE": "live", "INERT": "*** INERT ***", "UNTESTABLE": "untestable",
                   "HARNESS": "!! HARNESS", "CRASH": "!! CRASH"}.get(r["verdict"], r["verdict"])
            extra = (f" ({r.get('unmet_precondition')})" if r["verdict"] == "UNTESTABLE"
                     else f" [{len(r.get('changed') or [])} fields]" if r["verdict"] == "LIVE"
                     else f" {r.get('note','')}")
            print(f"{i:3d}/{len(todo)} {r['flag']:40s} {tag}{extra}", flush=True)

    flush(rows)
    print("\n" + "=" * 78)
    for v in ("INERT", "UNTESTABLE", "HARNESS", "CRASH", "LIVE"):
        got = [r["flag"] for r in rows if r["verdict"] == v]
        print(f"{v:11s} {len(got):3d}" + ("  " + ", ".join(got) if v != "LIVE" and got else ""))
    print(f"\n{time.time()-t0:.0f}s -> {OUT}")


if __name__ == "__main__":
    main()
