"""Threshold sweep for the aquatic-gated morph (R-47): how does complexity rarity + survival vary with the
wateracc cutoff? Picks the canonical morph_aquatic_threshold. Reports %complex + survival per biome per threshold.

Run:  py -3 -u outputs/biome_society_20260702/run_morph_aquatic_sweep.py
"""
import sys, os, statistics, time
from collections import Counter
sys.path.insert(0, os.path.dirname(__file__))
from run_biome_society import realistic_forager_demog, capacity_aware_seed, BURN, X0, Y0, PATCH, FOUNDERS, GRP
from sic_games.config import KcalEconomyConfig, SubstrateConfig, CarbonConfig
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import generate_world, world_lottery, WORLD_ARCHETYPE_ORDER
from sic_games.capacity import NPPCapacityField

SEEDS, STEPS = 3, 1300
THRESHOLDS = [0.50, 0.55, 0.60, 0.65, 0.70]


def run(arch, seed, thr):
    knobs = world_lottery(seed * 5, archetype=arch); fields = generate_world(knobs)
    cap = NPPCapacityField(fields, BURN, patch=(X0, Y0, PATCH), mode="tallavaara")
    pos = capacity_aware_seed(cap, BURN, FOUNDERS)
    demog = realistic_forager_demog().model_copy(update=dict(morph_aquatic_gated=True, morph_aquatic_threshold=thr))
    w = TerrainWorld(n_agents=FOUNDERS, kcal_cfg=KcalEconomyConfig(), terrain_knobs=knobs, game_stream=False, seed=seed,
        carbon_cfg=CarbonConfig(kappa=1.5), substrate_cfg=SubstrateConfig(enabled=True, k_cell=0,
            movement_mode="diffusion", contest_exponent=1.5, move_cost_flat=0.0, **GRP),
        harvest_field=cap, placement_positions=pos, demography_cfg=demog)
    for _ in range(STEPS):
        w.step()
        if not w.agent_list:
            return None
    al = w.agent_list; bids = {a._group.band_id for a in al}
    soc = Counter(w._band_society.get(b) for b in bids); n = sum(soc.values()) or 1
    return dict(pop=len(al), cplx=(soc.get("complex_forager", 0) + soc.get("stratified_chiefdom", 0)) / n)


def main():
    t0 = time.time()
    print(f"AQUATIC-MORPH THRESHOLD SWEEP — %complex per biome ({SEEDS} seeds × {STEPS} steps)\n")
    header = "  " + "biome".ljust(9) + "".join(f"thr={t:.2f}".rjust(12) for t in THRESHOLDS)
    print(header)
    for arch in WORLD_ARCHETYPE_ORDER:
        cells = []
        for thr in THRESHOLDS:
            rows = [r for r in (run(arch, s, thr) for s in range(SEEDS)) if r]
            if not rows:
                cells.append("extinct".rjust(12)); continue
            cplx = statistics.mean(r["cplx"] for r in rows) * 100
            surv = len(rows)
            cells.append(f"{cplx:.0f}% ({surv}/{SEEDS})".rjust(12))
        print("  " + arch.ljust(9) + "".join(cells) + f"   [{time.time()-t0:.0f}s]")
    print("\n  Read: pick the threshold where complexity is rare + water-linked (montane/forest carry it) and no biome")
    print("  loses survival. Higher threshold → rarer complexity.")


if __name__ == "__main__":
    main()
