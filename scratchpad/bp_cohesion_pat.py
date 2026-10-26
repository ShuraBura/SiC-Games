"""Did paternal_provision_frac 0.5 (Add.109) move the test_cohesion_headroom facts? Same world/stack/steps as the test,
paternal 0.0 (positive control: must reproduce the pre-adoption PASS) against 0.5."""
import os
import statistics
import sys

ROOT = r"C:\Users\syatom\Projects\SiC Games"
sys.path.insert(0, os.path.join(ROOT, "sic_games", "src"))
sys.path.insert(0, os.path.join(ROOT, "sic_games", "outputs", "mechanism_battery"))
import battery1_liveness as B1   # noqa: E402

STACK = dict(enable_emergent_band_size=True, enable_resource_directed_fusion=True,
             enable_dynamic_bands=True, enable_band_affiliation=True,
             enable_size_repulsion=True, enable_village_scaling=True,
             enable_malnutrition_fission=True)
WORLD = dict(n=1200, patch=30, terr="coastal", clim="temperate")

SEEDS = [int(x) for x in os.environ.get("CH_SEEDS", "%d" % B1.SEED).split(",")]
for seed, pat in [(s_, p_) for s_ in SEEDS for p_ in (0.0, 0.5)]:
    w = B1._build(dict(STACK, paternal_provision_frac=pat), seed=seed, **WORLD)
    for _ in range(200):
        w.step()
    cfg = w._demog
    members = {}
    for a in w.agent_list:
        members.setdefault(a._group.band_id, []).append(a)
    rows = []
    for bid, ms in members.items():
        if len(ms) < 2:
            continue
        a_val = float(w._band_assabiyah.get(bid, 0.0))
        lead = float(w._band_leader_term.get(bid, 0.0))
        raw = a_val + lead - float(w._band_repulsion.get(bid, 0.0)) - float(w._band_malnutrition.get(bid, 0.0))
        rows.append(dict(a=a_val, lead=lead, raw=raw, surp=float(w._band_surplus.get(bid, 0.0))))
    led = [r for r in rows if r["lead"] > 0]
    loose = [r for r in led if min(1.0, max(0.0, r["raw"])) < 0.999]
    ratio = cfg.assabiyah_decay / cfg.assabiyah_gain
    print(f"seed {seed} paternal {pat}: bands {len(rows)}, led {len(led)}, led-but-loose {len(loose)} "
          f"(raw of loose {[round(r['raw'], 3) for r in loose][:8]}); above fixed point "
          f"{sum(r['surp'] > ratio for r in rows)}/{len(rows)}; median assabiyah "
          f"{statistics.median(r['a'] for r in rows):.3f}; median surplus {statistics.median(r['surp'] for r in rows):.3f}; "
          f"median raw {statistics.median(r['raw'] for r in rows):.3f}; pop {len(w.agent_list)}", flush=True)
