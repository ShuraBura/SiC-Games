"""F.2 band life-cycle DIAGNOSTICS — characterize the merge / split / collapse dynamics + the band-size
distribution the existing emergent-band mechanisms (E.1/E.2 grouping + F.1/F.2 bonded mating) produce, on the
corrected substrate (CC-1 capacity patch + bonded_mate_radius=1). No new mechanic — pure measurement (band-risk
mortality was shelved as a death spiral, run_3i).

A band = a spatially-connected component (TerrainWorld.bands()). Bands are tracked across steps by member
(agent-id) overlap:
  MERGE    — a now-band draws ≥2 members each from ≥2 distinct prev-bands.
  SPLIT    — a prev-band's members land in ≥2 distinct now-bands (≥2 each).
  COLLAPSE — a prev-band (size ≥ 5) has no successor sharing ≥3 members (it dissolved).
  FORM     — a now-band (size ≥ 5) has no predecessor sharing ≥3 members (coalesced from singletons/births).
Plus the steady-state size distribution vs the ethnographic band size (Wobst ~25 / Dunbar).
Run:  py -3 -u outputs/phase1_biome_mortality/run_3j_band_lifecycle.py
"""
from __future__ import annotations
import os, time, statistics
from collections import Counter

import sys as _sys
try:
    _sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from sic_games.config import KcalEconomyConfig, SubstrateConfig, CarbonConfig
from sic_games.demography import DemographyConfig, ACHE_FOREST_NATURAL as NAT
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world, N as GRID_N
import importlib.util as _iu
_p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "phase1_demography_step2", "run_2a_pre.py")
_s = _iu.spec_from_file_location("r2", _p); _r2 = _iu.module_from_spec(_s); _s.loader.exec_module(_r2)
SubWindowCapacity, knobs_for = _r2.SubWindowCapacity, _r2.knobs_for

OUT = os.path.dirname(os.path.abspath(__file__))
SEEDS = list(range(5))
STEPS, FOUNDERS, MATE_R = 1000, 300, 1
SAMPLE_EVERY = 20            # debounce: classify durable events between samples, not single-step boundary flicker
MIN_PERSIST_SAMPLES = 3      # a "real" band must persist ≥ this many samples (×SAMPLE_EVERY ≈ 60 steps / ~5 yr)
GRP = dict(group_safety_max=8.0, group_safety_scale=15.0, group_mate_min=15.0, group_mate_floor=0.2)


def band_positions_patch(fields, cap, n, band_size=25, sep=4):
    cells = sorted(((cap.level(x, y), x, y) for y in range(GRID_N) for x in range(GRID_N)
                    if fields.isWater[y, x] == 0 and cap.level(x, y) > 0), reverse=True)
    sites, pos = [], []
    for (_, x, y) in cells:
        if len(sites) >= max(1, n // band_size):
            break
        if all(max(abs(x - px), abs(y - py)) >= sep for (px, py) in sites):
            sites.append((x, y)); pos.extend([(x, y)] * band_size)
    i = 0
    while len(pos) < n and sites:
        pos.append(sites[i % len(sites)]); i += 1
    return pos[:n]


def _overlap(a, b):
    return len(a & b)


def classify(prev, now):
    """prev, now = lists of member-id sets (size ≥ 2). Returns (merge, split, collapse, form) counts."""
    merge = split = collapse = form = 0
    for nb in now:
        if len(nb) >= 5 and sum(1 for pb in prev if _overlap(pb, nb) >= 2) >= 2:
            merge += 1
        if len(nb) >= 5 and max((_overlap(pb, nb) for pb in prev), default=0) < 3:
            form += 1
    for pb in prev:
        if len(pb) >= 5 and sum(1 for nb in now if _overlap(pb, nb) >= 2) >= 2:
            split += 1
        if len(pb) >= 5 and max((_overlap(pb, nb) for nb in now), default=0) < 3:
            collapse += 1
    return merge, split, collapse, form


def run_one(seed):
    fields = generate_world(knobs_for(seed)); cap = SubWindowCapacity(fields)
    pos = band_positions_patch(fields, cap, FOUNDERS)
    demog = DemographyConfig(
        siler_a1=NAT.a1, siler_b1=NAT.b1, siler_a2=NAT.a2, siler_a3=NAT.a3, siler_b3=NAT.b3,
        enable_density_disease=True, dens_delta=3.0, dens_rho_half=0.2,
        enable_cred_status=True, cred_seed_sigma=0.5, cred_inherit_sigma=0.1,
        enable_bonded_mating=True, bonded_mate_radius=MATE_R)
    w = TerrainWorld(n_agents=FOUNDERS, kcal_cfg=KcalEconomyConfig(), terrain_knobs=knobs_for(seed),
                     game_stream=False, seed=seed, carbon_cfg=CarbonConfig(kappa=1.0),
                     substrate_cfg=SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                                                   contest_exponent=1.0, move_cost_flat=0.0, **GRP),
                     harvest_field=cap, placement_positions=pos, demography_cfg=demog)
    uid_state = [0]
    def uid(a):                                                  # stable per-agent id (id() can be reused after death)
        u = getattr(a, "_uid", None)
        if u is None:
            u = uid_state[0]; uid_state[0] += 1; a._uid = u
        return u
    t0 = int(0.5 * STEPS)
    ev = Counter()
    raw_sizes, raw_awt, singlocc = [], [], []
    pst_sizes, pst_awt, pst_frac = [], [], []                    # persistence-filtered (sustained co-residence)
    prev = None
    n_transitions = 0
    lineages: dict = {}                                          # lid -> {"members": set, "age_samples": int}
    next_lid = 0
    for step in range(STEPS):
        w.step()
        if step % SAMPLE_EVERY != 0:
            continue
        # Everything below runs on the DEBOUNCED sample (every SAMPLE_EVERY steps), where a membership change is a
        # REAL merge/split, not single-step connectivity flicker — so lineage continuity is meaningful.
        comps_all = [set(uid(a) for a in b) for b in w.bands()]
        comps = [c for c in comps_all if len(c) >= 2]
        if prev is not None:                                     # durable merge/split/collapse events
            m, s, c, f = classify(prev, comps)
            ev["merge"] += m; ev["split"] += s; ev["collapse"] += c; ev["form"] += f
            n_transitions += 1
        prev = comps
        # band lineage continuity (across samples): a component inherits the prev lineage it shares the most
        # members with (≥ half of that lineage retained), age++; else NEW band (age 0). A band is REAL only once
        # its lineage has survived ≥ MIN_PERSIST_SAMPLES samples — drops transient splinters AND momentary glue.
        new_lin, used = {}, set()
        for C in sorted(comps, key=len, reverse=True):           # big bands claim their lineage first (merges)
            best_lid, best_ov = None, 0
            for lid, L in lineages.items():
                if lid in used:
                    continue
                ov = len(C & L["members"])
                if ov > best_ov:
                    best_ov, best_lid = ov, lid
            if best_lid is not None and best_ov >= 0.5 * len(lineages[best_lid]["members"]):
                new_lin[best_lid] = {"members": C, "age_samples": lineages[best_lid]["age_samples"] + 1}
                used.add(best_lid)
            else:
                new_lin[next_lid] = {"members": C, "age_samples": 0}; next_lid += 1
        lineages = new_lin
        persistent = [L["members"] for L in lineages.values() if L["age_samples"] >= MIN_PERSIST_SAMPLES]
        if step >= t0 and w.agent_list:
            n_alive = len(w.agent_list)
            sz = [len(b) for b in comps_all]; tot = sum(sz)
            raw_sizes.extend(n for n in sz if n >= 2)
            raw_awt.append(sum(n * n for n in sz) / tot if tot else 0.0)
            singlocc.append(sum(n for n in sz if n == 1) / tot if tot else 0.0)
            psz = [len(p) for p in persistent]; ptot = sum(psz)
            pst_sizes.extend(psz)
            pst_awt.append(sum(n * n for n in psz) / ptot if ptot else 0.0)
            pst_frac.append(ptot / n_alive if n_alive else 0.0)  # frac of the live pop in a PERSISTENT band
    span_steps = max(1, n_transitions * SAMPLE_EVERY)
    def per100(k): return 100.0 * ev[k] / span_steps
    def m_(xs): return statistics.mean(xs) if xs else 0.0
    return dict(
        pop=len(w.agent_list),
        raw_median=statistics.median(raw_sizes) if raw_sizes else 0.0, raw_awt=m_(raw_awt),
        raw_max=max(raw_sizes) if raw_sizes else 0, singleton_frac=m_(singlocc),
        pst_median=statistics.median(pst_sizes) if pst_sizes else 0.0, pst_mean=m_(pst_sizes),
        pst_awt=m_(pst_awt), pst_max=max(pst_sizes) if pst_sizes else 0, pst_frac=m_(pst_frac),
        merge=per100("merge"), split=per100("split"), collapse=per100("collapse"), form=per100("form"))


def main():
    t0 = time.time()
    rows = [run_one(s) for s in SEEDS]
    agg = {k: statistics.mean([r[k] for r in rows]) for k in rows[0]}
    pst_steps = MIN_PERSIST_SAMPLES * SAMPLE_EVERY
    print(f"F.2 band life-cycle (CC-1 patch + bonded r={MATE_R}, {len(SEEDS)} seeds × {STEPS} steps, tail half; "
          f"persistence filter ≥{pst_steps} steps)")
    print(f"  RAW (instantaneous component):  median {agg['raw_median']:.1f} | agent-weighted {agg['raw_awt']:.1f} "
          f"| max {agg['raw_max']:.0f} | solo frac {agg['singleton_frac']:.2f}")
    print(f"  PERSISTENT (sustained ≥{pst_steps} steps): median {agg['pst_median']:.1f} | mean {agg['pst_mean']:.1f} "
          f"| agent-weighted {agg['pst_awt']:.1f} | max {agg['pst_max']:.0f} | pop-in-persistent-band {agg['pst_frac']:.2f}")
    print(f"  life-cycle events / 100 steps: merge {agg['merge']:.1f} | split {agg['split']:.1f} | "
          f"collapse {agg['collapse']:.1f} | form {agg['form']:.1f}")
    print(f"  Wobst/Dunbar ~25 ⇒ persistent agent-weighted band = {agg['pst_awt']:.0f}  [{time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
