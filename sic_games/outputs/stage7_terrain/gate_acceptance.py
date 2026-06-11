"""§7 Acceptance checks A7.1–A7.4 (blueprint §7).

A7.1 — Full forest gradient reachable
A7.2 — Coexistence band exists
A7.3 — No matrix-dominance artifact (grassland < savanna, grassland < 35%)
A7.4 — Game field unimodal (hump-shaped) in NPP; gameHumpPeak is diagnostic only

All checks are blocking (STOP on any red).
Emits §8 artifacts (forest-knob stacked bar + mosaic_mid biome PNG).
"""
import sys, pathlib, json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

ROOT = pathlib.Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT / "src"))

from sic_games.terrain import (
    generate_world, characterize_map,
    BIOME_WATER, BIOME_WETLAND, BIOME_FOREST, BIOME_SAVANNA,
    BIOME_GRASS, BIOME_DESERT, BIOME_MOUNTAIN,
)

OUT = pathlib.Path(__file__).parent
SEEDS = ['42', '7', '1001']
PASS = True


def fail(msg: str):
    global PASS
    PASS = False
    print(f"RED  {msg}")


def ok(msg: str):
    print(f"ok   {msg}")


def check_unimodal(F, bins=20, min_cells=3, min_bins=4, tol=0.03):
    """Check that mean-game-by-NPP-bin is unimodal (blueprint A7.4).
    Returns (pass_: bool, exempt: bool, peak_pos: float|None, note: str).
    Worlds with fewer than min_bins populated bins are exempt.
    """
    land = ~F.isWater.astype(bool)
    npp_land = F.npp[land]
    game_land = F.game[land]
    bin_vals = []
    for b in range(bins):
        lo = b / bins; hi = (b + 1) / bins
        mask = (npp_land >= lo) & (npp_land <= hi if b == bins - 1 else npp_land < hi)
        if mask.sum() >= min_cells:
            bin_vals.append((b, float(game_land[mask].mean())))
    if len(bin_vals) < min_bins:
        return True, True, None, f"exempt ({len(bin_vals)} populated bins < {min_bins})"
    indices = [b for b, _ in bin_vals]
    means   = [m for _, m in bin_vals]
    peak_i  = int(np.argmax(means))
    peak_pos = indices[peak_i] / bins
    for i in range(peak_i):
        if means[i + 1] < means[i] - tol:
            return False, False, peak_pos, (
                f"not ascending at bin {indices[i]}->{indices[i+1]}: "
                f"{means[i]:.3f}->{means[i+1]:.3f}")
    for i in range(peak_i, len(means) - 1):
        if means[i + 1] > means[i] + tol:
            return False, False, peak_pos, (
                f"not descending at bin {indices[i]}->{indices[i+1]}: "
                f"{means[i]:.3f}->{means[i+1]:.3f}")
    return True, False, peak_pos, "ok"


# ── A7.1 — Full forest gradient reachable ─────────────────────────────────

print("=== A7.1 Forest gradient ===")

fK_vals = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
# Reference from blueprint §7
ref_gradient = {
    0.0: dict(forest=0.0,  savanna=7.7,  grassland=76.7),
    0.2: dict(forest=0.0,  savanna=28.1, grassland=56.2),
    0.4: dict(forest=1.9,  savanna=61.2, grassland=21.2),
    0.6: dict(forest=11.9, savanna=72.4, grassland=0.0),
    0.8: dict(forest=37.9, savanna=46.5, grassland=0.0),
    1.0: dict(forest=73.8, savanna=10.5, grassland=0.0),
}

gradient_data = {}
forest_means = []
for fK in fK_vals:
    rows = []
    for s in SEEDS:
        knobs = dict(relief=0.4, rough=0.5, waterK=0.5, forestK=fK, aridK=0.35, seedStr=s)
        F = generate_world(knobs)
        v = characterize_map(F)
        rows.append(v['biomeFrac'])
    mean_frac = {b: np.mean([r[b] for r in rows]) for b in ('forest', 'savanna', 'grassland')}
    gradient_data[fK] = mean_frac
    forest_means.append(mean_frac['forest'])
    ref = ref_gradient[fK]
    for b in ('forest', 'savanna', 'grassland'):
        delta = abs(mean_frac[b] - ref[b])
        if delta > 3.0:
            fail(f"A7.1 fK={fK} {b}: got {mean_frac[b]:.1f}  ref {ref[b]:.1f}  delta={delta:.1f} pp")

# Forest must be monotonically increasing (allow ±1 pp noise)
for i in range(1, len(forest_means)):
    if forest_means[i] < forest_means[i-1] - 1.0:
        fail(f"A7.1 not monotone: fK={fK_vals[i]:.1f} forest {forest_means[i]:.1f} < "
             f"fK={fK_vals[i-1]:.1f} {forest_means[i-1]:.1f}")

if forest_means[0] >= 2.0:
    fail(f"A7.1 fK=0 forest {forest_means[0]:.1f}% >= 2%")
if forest_means[-1] <= 70.0:
    fail(f"A7.1 fK=1 forest {forest_means[-1]:.1f}% <= 70%")

if PASS:
    ok(f"A7.1 forest gradient {' '.join(f'{f:.1f}' for f in forest_means)}")

# ── A7.2 — Coexistence band ────────────────────────────────────────────────

print("\n=== A7.2 Coexistence band ===")

def derive_habitable_caps(dominance=50, steps=21, n_seeds=3):
    mid = dict(relief=0.5, rough=0.5, waterK=0.5, forestK=0.5, aridK=0.35)
    def sweep(axis, biome_key):
        cap = 1.0
        for s in range(steps):
            v = s / (steps - 1)
            dead = 0.0
            for k in range(n_seeds):
                kn = {**mid, axis: v, 'seedStr': f'env_{axis}_{s}_{k}'}
                F = generate_world(kn)
                cv = characterize_map(F)
                dead += cv['biomeFrac'].get(biome_key, 0.0) / n_seeds
            if dead > dominance:
                cap = v
                break
        return cap
    return sweep('aridK', 'desert'), sweep('relief', 'mountain')

arid_cap, relief_cap = derive_habitable_caps()
print(f"   habitable caps: aridity<={arid_cap:.2f}  relief<={relief_cap:.2f}")

# LHS over habitable box: 150 samples × 4 seeds
rng = np.random.default_rng(0xC0FFEE)
n_lhs = 150; n_seeds = 4; dims = 5
pts = np.empty((n_lhs, dims))
for d in range(dims):
    perm = rng.permutation(n_lhs)
    pts[:, d] = (perm + rng.random(n_lhs)) / n_lhs

caps = [relief_cap, 1.0, 1.0, 1.0, arid_cap]  # relief, rough, waterK, forestK, aridK
coex_count = 0
grass_accs = []; sav_accs = []
hump_peak_acc = []
uni_pass = 0; uni_fail = 0; uni_exempt = 0
uni_fail_examples = []

for s in range(n_lhs):
    u = pts[s]
    kn_base = dict(
        relief=u[0]*caps[0], rough=u[1], waterK=u[2],
        forestK=u[3], aridK=u[4]*caps[4],
    )
    seed_fracs = []
    for k in range(n_seeds):
        kn = {**kn_base, 'seedStr': f'sweep_{s}_{k}'}
        F = generate_world(kn)
        v = characterize_map(F)
        seed_fracs.append(v['biomeFrac'])
        # A7.4 diagnostic: record gameHumpPeak
        if v['gameHumpPeak'] is not None:
            hump_peak_acc.append(v['gameHumpPeak'])
        # A7.4 gate: unimodality
        is_uni, is_exempt, peak_pos, note = check_unimodal(F)
        if is_exempt:
            uni_exempt += 1
        elif is_uni:
            uni_pass += 1
        else:
            uni_fail += 1
            if len(uni_fail_examples) < 3:
                uni_fail_examples.append((kn['seedStr'], peak_pos, note))

    mean_frac = {b: np.mean([r[b] for r in seed_fracs])
                 for b in ('forest', 'savanna', 'grassland')}
    if mean_frac['forest'] >= 10.0 and mean_frac['savanna'] >= 10.0:
        coex_count += 1
    grass_accs.append(mean_frac['grassland'])
    sav_accs.append(mean_frac['savanna'])

coex_frac = coex_count / n_lhs
if coex_frac < 0.20:
    fail(f"A7.2 coexistence fraction {coex_frac:.3f} < 0.20")
else:
    ok(f"A7.2 coexistence fraction {coex_frac:.3f} >= 0.20 (ref ~0.29)")

# ── A7.3 — No matrix-dominance artifact ───────────────────────────────────

print("\n=== A7.3 No matrix-dominance ===")
mean_grass = np.mean(grass_accs)
mean_sav   = np.mean(sav_accs)
if mean_grass > mean_sav:
    fail(f"A7.3 mean grassland {mean_grass:.1f}% > mean savanna {mean_sav:.1f}%")
if mean_grass >= 35.0:
    fail(f"A7.3 mean grassland {mean_grass:.1f}% >= 35%")
if PASS:
    ok(f"A7.3 grassland {mean_grass:.1f}%  savanna {mean_sav:.1f}% (grass < sav, grass < 35%)")

# ── A7.4 — Game field unimodal in NPP ─────────────────────────────────────
# Blueprint §7 rev2: assert unimodality (shape), not peak-position (statistic).
# gameHumpPeak is recorded as a diagnostic, NOT gated.

print("\n=== A7.4 Game field unimodal in NPP ===")
total_uni = uni_pass + uni_fail + uni_exempt
if uni_fail > 0:
    fail(f"A7.4 unimodality: {uni_fail}/{total_uni} worlds FAILED "
         f"(pass={uni_pass}  exempt={uni_exempt})")
    for tag, peak, note in uni_fail_examples:
        print(f"   example fail: {tag}  peak={peak}  {note}")
else:
    ok(f"A7.4 unimodality: {uni_pass}/{total_uni} pass  {uni_exempt} exempt  0 fail")
    if hump_peak_acc:
        pmin = min(hump_peak_acc); pmax = max(hump_peak_acc)
        pmean = float(np.mean(hump_peak_acc))
        print(f"   gameHumpPeak (diagnostic only): "
              f"min={pmin:.2f}  max={pmax:.2f}  mean={pmean:.2f}")

# ── §8 Artifacts ─────────────────────────────────────────────────────────

print("\n=== §8 Emitting artifacts ===")

# 1. Forest-knob gradient stacked bar
fig, ax = plt.subplots(figsize=(7, 4))
labels = [str(fK) for fK in fK_vals]
f_vals = [gradient_data[fK]['forest']    for fK in fK_vals]
s_vals = [gradient_data[fK]['savanna']   for fK in fK_vals]
g_vals = [gradient_data[fK]['grassland'] for fK in fK_vals]
x = np.arange(len(fK_vals))
ax.bar(x, g_vals, color='#aab969', label='grassland')
ax.bar(x, s_vals, bottom=g_vals, color='#ba9628', label='savanna/woodland')
ax.bar(x, f_vals, bottom=[g+s for g,s in zip(g_vals, s_vals)], color='#175020', label='forest')
ax.set_xticks(x); ax.set_xticklabels(labels)
ax.set_xlabel('forestK knob'); ax.set_ylabel('% of land')
ax.set_title('A7.1 Forest-knob gradient (mean of 3 seeds)')
ax.legend(loc='upper left')
ax.set_ylim(0, 105)
plt.tight_layout()
fig.savefig(OUT / 'a71_forest_gradient.png', dpi=120)
plt.close(fig)
print("   saved a71_forest_gradient.png")

# 2. mosaic_mid biome map (seed 42)
BIOME_RGB = {
    BIOME_WATER:    (24,  72, 120),
    BIOME_WETLAND:  (29, 158, 117),
    BIOME_FOREST:   (23,  80,  30),
    BIOME_SAVANNA:  (186,150,  40),
    BIOME_GRASS:    (170,185, 105),
    BIOME_DESERT:   (216,170, 120),
    BIOME_MOUNTAIN: (120,118, 112),
}
BIOME_NAME = {
    BIOME_WATER: 'water', BIOME_WETLAND: 'wetland', BIOME_FOREST: 'forest',
    BIOME_SAVANNA: 'savanna/woodland', BIOME_GRASS: 'grassland',
    BIOME_DESERT: 'desert', BIOME_MOUNTAIN: 'mountain',
}
F_mm = generate_world(dict(relief=0.4, rough=0.5, waterK=0.5, forestK=0.5, aridK=0.35, seedStr='42'))
img = np.zeros((100, 100, 3), dtype=np.uint8)
for b, rgb in BIOME_RGB.items():
    mask = (F_mm.biome == b)
    img[mask] = rgb

fig, ax = plt.subplots(figsize=(5, 5))
ax.imshow(img, origin='upper', interpolation='nearest')
ax.set_title('mosaic_mid seed=42 — biome map')
ax.axis('off')
patches = [mpatches.Patch(color=tuple(c/255 for c in BIOME_RGB[b]), label=BIOME_NAME[b])
           for b in sorted(BIOME_RGB)]
ax.legend(handles=patches, bbox_to_anchor=(1.01, 1), loc='upper left', fontsize=8)
plt.tight_layout()
fig.savefig(OUT / 'mosaic_mid_seed42_biome.png', dpi=120, bbox_inches='tight')
plt.close(fig)
print("   saved mosaic_mid_seed42_biome.png")

# ── Final verdict ─────────────────────────────────────────────────────────

print()
if PASS:
    print("All §7 checks GREEN — stage 7 terrain generator complete.")
else:
    print("FAIL — one or more §7 checks failed. BLOCKING STOP per Rule 11.")
    sys.exit(1)
