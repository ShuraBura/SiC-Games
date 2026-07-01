"""Social-Evolution Stage 1 — LEADER COHERENCE benchmark: the leader-death -> fission-spike signature.

Mechanism (phase1_model.py::_maintain_bands, demography.py): a band's top-status member (highest cred*prowess)
lends a SECOND, additive cohesion term on top of assabiyah, Boehm-gated by the band's society type (0 in
egalitarian bands -- they actively LEVEL leaders; rising in complex/stratified bands). Unit-level correctness
(gating, Boehm scaling, additive-not-a-relabel, the hard split_size cap) is locked in tests/test_bands.py. THIS
harness checks the mechanism's signature in the full dynamic system: does removing a band's leader visibly
un-glue it, more than removing a random member would?

Design (same diff-in-diff discipline as run_se0/R-28): run the SAME seeded trajectory in two arms up to a
scripted intervention step T (bit-identical until then -- the placebo check). At T, for every band currently
classified complex_forager/stratified_chiefdom (the ONLY bands where the Boehm gate lets leader coherence do
anything), kill either:
  LEADER arm:   that band's current top-status member (`w.band_leaders()`), or
  PLACEBO arm:  a random adult member of the SAME band (same count of deaths, same bands hit) -- the matched
                control for "losing any one adult perturbs the band" vs. "losing SPECIFICALLY its leader does".
Track band_count + band_awt for a POST window; the benchmark signature is band_count rising / band_awt falling
MORE in the LEADER arm than the PLACEBO arm (a bigger fission response to the leader-specific loss).

Run:  py -3 -u outputs/phase1_social_evolution/run_se1_leader_coherence.py
"""
from __future__ import annotations
import os, sys, time, math, statistics
from collections import Counter

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from sic_games.config import KcalEconomyConfig, SubstrateConfig, CarbonConfig
from sic_games.demography import DemographyConfig
from sic_games.phase1_model import TerrainWorld
import importlib.util as _iu
_p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "run_se0_controlled_climate.py")
_s = _iu.spec_from_file_location("se0", _p); _se0 = _iu.module_from_spec(_s); _s.loader.exec_module(_se0)
realistic_forager_demog, band_positions_patch = _se0.realistic_forager_demog, _se0.band_positions_patch
from sic_games.terrain import N as GRID_N, generate_world
import importlib.util as _iu2
_p2 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "phase1_demography_step2", "run_2a_pre.py")
_s2 = _iu2.spec_from_file_location("r2", _p2); _r2 = _iu2.module_from_spec(_s2); _s2.loader.exec_module(_r2)
SubWindowCapacity, knobs_for = _r2.SubWindowCapacity, _r2.knobs_for

GRP = dict(group_safety_max=8.0, group_safety_scale=15.0, group_mate_min=15.0, group_mate_floor=0.2)
COMPLEX_TYPES = ("complex_forager", "stratified_chiefdom")   # the ONLY types the Boehm gate lets leader coherence bite


def _build_world(seed, demog, founders=300):
    fields = generate_world(knobs_for(seed)); base = SubWindowCapacity(fields)
    pos = band_positions_patch(fields, base, founders)
    w = TerrainWorld(n_agents=founders, kcal_cfg=KcalEconomyConfig(), terrain_knobs=knobs_for(seed),
                     game_stream=False, seed=seed, carbon_cfg=CarbonConfig(kappa=1.5),
                     substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                                   contest_exponent=1.5, move_cost_flat=0.0, **GRP),
                     harvest_field=base, placement_positions=pos, demography_cfg=demog)
    return w


def _cohort_fragmentation(cohort_ids, w):
    """How fragmented is a targeted band's original cohort now? Among its SURVIVING members, the number of
    distinct band_ids they occupy (1 = still one band; >1 = the cohort split/dispersed). Returns (n_distinct,
    n_survivors); a cohort with 0 survivors is reported as (0, 0)."""
    id_to_agent = {id(a): a for a in w.agent_list}
    survivors = [id_to_agent[i] for i in cohort_ids if i in id_to_agent]
    if not survivors:
        return 0, 0
    return len({a._group.band_id for a in survivors}), len(survivors)


def run_event_study(seed, demog, t_burn=900, checkpoints=(20, 50, 100, 200), arm="leader"):
    """Run to t_burn (deterministic), apply the leader/placebo intervention once, then track — for each targeted
    band's ORIGINAL member cohort — how fragmented it becomes at each checkpoint. This is the band-specific
    signature (does losing the leader split THAT band?), not a population aggregate. Returns per-cohort
    fragmentation trajectories, or None if no complex/stratified band was found by t_burn."""
    w = _build_world(seed, demog)
    for _ in range(t_burn):
        w.step()
        if not w.agent_list:
            return None

    complex_bids = {bid for bid, soc in w._band_society.items() if soc in COMPLEX_TYPES}
    members: dict[int, list] = {}
    for a in w.agent_list:
        members.setdefault(a._group.band_id, []).append(a)
    complex_bids = {b for b in complex_bids if len(members.get(b, [])) >= 8}   # need a band big enough to split
    if not complex_bids:
        return None

    w._rng_for_placebo = __import__("random").Random(2000 + seed)   # independent of the model's own RNG stream
    leaders = w.band_leaders()
    cohorts = []   # (target_agent, frozenset(member ids)) per targeted band
    for bid in complex_bids:
        cohort_ids = frozenset(id(a) for a in members[bid])
        if arm == "leader":
            target = leaders[bid]
        else:  # placebo: a random ADULT member of the same band, excluding the leader (matched count, same bands)
            adults = [a for a in members[bid] if a is not leaders[bid] and a.age >= demog.menarche_months]
            pool = adults or [x for x in members[bid] if x is not leaders[bid]]
            if not pool:
                continue
            target = w._rng_for_placebo.choice(pool)
        cohorts.append((target, cohort_ids))
    for (target, _) in cohorts:
        target.alive = False   # the model's own death-pruning (top of step()) cleans up occupied/bonds/remove()

    frag = {c: [] for c in checkpoints}   # checkpoint step → list of (n_distinct_bands) per surviving cohort
    step = 0
    for _ in range(max(checkpoints)):
        w.step(); step += 1
        if not w.agent_list:
            break
        if step in frag:
            for (_, cohort_ids) in cohorts:
                nd, nsurv = _cohort_fragmentation(cohort_ids, w)
                if nsurv > 0:
                    frag[step].append(nd)
    return dict(frag=frag, n_targeted=len(cohorts))


def main():
    t0 = time.time()
    SEEDS = [0, 1, 2, 3, 4, 5]
    T_BURN = 900
    CHECKPOINTS = (20, 50, 100, 200)
    demog = realistic_forager_demog()
    # Stage 1b repulsion ON — the counterweight that pulls cohesion_frac off the assabiyah ceiling so leader
    # coherence has headroom to matter (see R-29: without it, assabiyah saturates and the leader term is clamped).
    demog = demog.model_copy(update=dict(
        enable_leader_coherence=True, leader_coherence_gain=1.5,
        enable_size_repulsion=True, repulsion_gain=1.0, repulsion_midpoint=25.0, repulsion_width=6.0))

    print(f"Leader-coherence COHORT event study — {len(SEEDS)} seeds, burn={T_BURN}, "
          f"leader_coherence_gain={demog.leader_coherence_gain}, repulsion_gain={demog.repulsion_gain}")
    print("Signature: does killing a band's LEADER fragment its member cohort more than killing a random adult?\n")
    rows = {"leader": [], "placebo": []}
    for seed in SEEDS:
        for arm in ("leader", "placebo"):
            r = run_event_study(seed, demog, t_burn=T_BURN, checkpoints=CHECKPOINTS, arm=arm)
            if r is not None:
                rows[arm].append(r)
        print(f"  seed {seed}: {'ok' if rows['leader'] and rows['leader'][-1] else 'no usable band'}   [{time.time()-t0:.0f}s]")

    for arm in ("leader", "placebo"):
        if not rows[arm]:
            print(f"[{arm}] no usable runs (no complex/stratified band ≥8 by t_burn — try a longer burn-in)")
            return
    print(f"\n{min(len(rows['leader']), len(rows['placebo']))} usable seed(s); "
          f"mean cohorts targeted per event: {statistics.mean(r['n_targeted'] for r in rows['leader']):.1f}")

    def frag_at(rows_arm, cp):
        # mean over seeds of (mean distinct-bands-per-surviving-cohort at checkpoint cp)
        per_seed = [statistics.mean(r["frag"][cp]) for r in rows_arm if r["frag"].get(cp)]
        return statistics.mean(per_seed) if per_seed else float("nan")

    print(f"\n  cohort fragmentation = mean # distinct bands a bereaved band's original members occupy")
    print(f"  {'checkpoint':<14}{'leader':>10}{'placebo':>10}{'Δ(leader−placebo)':>20}")
    for cp in CHECKPOINTS:
        lf, pf = frag_at(rows["leader"], cp), frag_at(rows["placebo"], cp)
        print(f"  +{cp:<13}{lf:>10.3f}{pf:>10.3f}{lf-pf:>+20.3f}")
    print("\n  Read: Δ > 0 means the LEADER-bereaved cohort fragments into more bands than the random-adult-\n"
          "  bereaved cohort — the leader-death→fission signature, measured on the SAME bands with matched\n"
          "  death counts, so the gap is attributable to WHO died (the leader), not how many.")


if __name__ == "__main__":
    main()
