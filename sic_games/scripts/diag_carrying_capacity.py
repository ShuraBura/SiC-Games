"""How many agents can ONE cell feed? S/burn over land cells, vs the seeder's 25/cell."""
from __future__ import annotations
import numpy as np
from sic_games.config import KcalEconomyConfig
from sic_games.phase1_model import TerrainWorld, seed_band_positions, _DEFAULT_KNOBS
from sic_games.terrain import generate_world

kcfg = KcalEconomyConfig()
burn = kcfg.burn_kcal_per_day * kcfg.days_per_month
print(f"burn/step = {burn:.0f} kcal")

w = TerrainWorld(n_agents=1, kcal_cfg=kcfg, seed=7, game_stream=False)
tf = w.terrain_field
fields = w._fields
land = fields.isWater == 0
ys, xs = np.where(land)
S = np.array([tf.level(int(x), int(y)) for x, y in zip(xs, ys)])
ratio = S / burn   # max occupants a cell can feed at even split (each gets S/n >= burn -> n <= S/burn)
print(f"land cells: {len(S)}")
print(f"S/burn (cell carrying capacity, even split): "
      f"min={ratio.min():.2f} median={np.median(ratio):.2f} mean={ratio.mean():.2f} "
      f"p90={np.percentile(ratio,90):.2f} max={ratio.max():.2f}")
print(f"cells that can feed >=5: {(ratio>=5).sum()}  >=10: {(ratio>=10).sum()}  >=25: {(ratio>=25).sum()}")

# What cells does the seeder actually pick, and their capacity?
pos = seed_band_positions(fields, 250, band_size=25, territory_radius=3)
from collections import Counter
band_cells = list(Counter(pos))
bratio = np.array([tf.level(x, y) / burn for (x, y) in band_cells])
print(f"\nseeder picked {len(band_cells)} band cells, band_size~25 stacked each")
print(f"  their S/burn: min={bratio.min():.2f} median={np.median(bratio):.2f} max={bratio.max():.2f}")
print(f"  => each seeded band of 25 needs S/burn>=25; only {(bratio>=25).sum()} of {len(band_cells)} qualify")
