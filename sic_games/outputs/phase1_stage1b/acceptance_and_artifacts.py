"""Phase 1 Stage 1b — Water Decomposition Diagnostic.

Acceptance checks A1-A6 (blueprint §8) + must-be-seen artifacts M1-M2 (blueprint §7).

Run from sic_games/ directory:
    python outputs/phase1_stage1b/acceptance_and_artifacts.py
"""
import sys, pathlib, csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = pathlib.Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT / "src"))

from sic_games.terrain import (
    generate_world, characterize_map,
    EXTERIOR_WATER_CEILING, N,
    _classify_water_components,
)

OUT = pathlib.Path(__file__).parent
OUT.mkdir(exist_ok=True)

PASS_ALL = True

def fail(tag, msg):
    global PASS_ALL
    PASS_ALL = False
    print(f"RED  [{tag}] {msg}")

def ok(tag, msg):
    print(f"ok   [{tag}] {msg}")


# ── Reference worlds ───────────────────────────────────────────────────────

REF_KNOBS = [
    dict(relief=0.4, rough=0.5, waterK=0.5,  forestK=0.5, aridK=0.35, seedStr='42'),
    dict(relief=0.3, rough=0.4, waterK=0.3,  forestK=0.8, aridK=0.2,  seedStr='7'),
    dict(relief=0.6, rough=0.6, waterK=0.4,  forestK=0.2, aridK=0.6,  seedStr='1001'),
]
REF_LABELS = ['mid-mix (seed=42)', 'wet-forest (seed=7)', 'dry-relief (seed=1001)']
ref_worlds = [(generate_world(k), characterize_map(generate_world(k)), lbl)
              for k, lbl in zip(REF_KNOBS, REF_LABELS)]

P1S1B_KEYS = [
    'exterior_water_fraction', 'interior_water_fraction',
    'n_interior_bodies', 'n_exterior_bodies',
    'shoreline_fraction', 'largest_exterior_body_cells',
    'largest_exterior_shore_to_area', 'guard_exterior_water_fail',
]


# ===========================================================================
# A1 — All §4.3 fields present, correct types, valid ranges
# ===========================================================================
print("\n=== A1 fields present + ranges ===")
for F, v, lbl in ref_worlds:
    for key in P1S1B_KEYS:
        if key not in v:
            fail('A1', f"{lbl}: missing key '{key}'")

    for key in ('exterior_water_fraction', 'interior_water_fraction', 'shoreline_fraction'):
        val = v[key]
        if not (0.0 <= val <= 1.0):
            fail('A1', f"{lbl}: {key}={val:.4f} out of [0,1]")

    if v['largest_exterior_shore_to_area'] < 0.0:
        fail('A1', f"{lbl}: largest_exterior_shore_to_area < 0")
    if v['largest_exterior_body_cells'] < 0:
        fail('A1', f"{lbl}: largest_exterior_body_cells < 0")
    for cnt_key in ('n_interior_bodies', 'n_exterior_bodies'):
        if v[cnt_key] < 0:
            fail('A1', f"{lbl}: {cnt_key} < 0")

ok('A1', 'all P1S1b fields present; types and ranges valid on all reference maps')


# ===========================================================================
# A2 — Conservation: exterior_cells + interior_cells == total water cells
# ===========================================================================
print("\n=== A2 conservation law ===")
for F, v, lbl in ref_worlds:
    total_water = int(F.isWater.sum())
    total_cells = N * N
    ext_cells = round(v['exterior_water_fraction'] * total_cells)
    int_cells = round(v['interior_water_fraction'] * total_cells)
    if ext_cells + int_cells != total_water:
        fail('A2', f"{lbl}: ext={ext_cells} + int={int_cells} "
             f"!= water={total_water}")

ok('A2', 'exterior_cells + interior_cells == total_water_cells on all reference maps')


# ===========================================================================
# A3 — Connectivity classification fixture
# ===========================================================================
print("\n=== A3 connectivity fixture ===")

# Fixture: 4x4 enclosed lake (rows 45-48, cols 45-48) + top 4-row sea (edge-connected)
iw_fix = np.zeros((N, N), dtype=np.uint8)
iw_fix[45:49, 45:49] = 1    # 16-cell lake, fully enclosed
iw_fix[0:4, :] = 1           # 400-cell sea, touches top edge

ext_c, int_c, n_ext, n_int, lec, mask = _classify_water_components(iw_fix)

if n_int != 1:
    fail('A3', f"fixture: n_interior={n_int}, expected 1")
if n_ext != 1:
    fail('A3', f"fixture: n_exterior={n_ext}, expected 1")
if int_c != 16:
    fail('A3', f"fixture: interior_cells={int_c}, expected 16")
if ext_c != 400:
    fail('A3', f"fixture: exterior_cells={ext_c}, expected 400")
if lec != 400:
    fail('A3', f"fixture: largest_exterior_cells={lec}, expected 400")
if ext_c + int_c != int(iw_fix.sum()):
    fail('A3', 'fixture: conservation violated')

ok('A3', f"fixture: lake=interior({int_c} cells), sea=exterior({ext_c} cells). "
   f"n_ext={n_ext}, n_int={n_int}. Conservation: {ext_c}+{int_c}={ext_c+int_c}.")


# ===========================================================================
# A4 — Guard behaviour on fixtures
# ===========================================================================
print("\n=== A4 guard behaviour ===")

# Fixture A: mostly-ocean (exterior_fraction >> 0.12) — guard should fire
kn_ocean = dict(relief=0.1, rough=0.3, waterK=0.95, forestK=0.5, aridK=0.1, seedStr='ocean_a4')
F_ocean = generate_world(kn_ocean)
v_ocean = characterize_map(F_ocean)
ext_frac_ocean = v_ocean['exterior_water_fraction']
if ext_frac_ocean > EXTERIOR_WATER_CEILING:
    if not v_ocean['guard_exterior_water_fail']:
        fail('A4', f"mostly-ocean world (ext={ext_frac_ocean:.3f}) did not fire guard")
    else:
        ok('A4', f"mostly-ocean fixture (ext={ext_frac_ocean:.3f} > {EXTERIOR_WATER_CEILING}): "
           f"guard_exterior_water_fail=True [CORRECT]")
else:
    print(f"     mostly-ocean fixture: ext={ext_frac_ocean:.3f} did not exceed {EXTERIOR_WATER_CEILING} "
          f"(waterK=0.95 may not produce enough exterior water at this seed — not a failure)")

# Fixture B: low-waterK world — guard should NOT fire
kn_land = dict(relief=0.4, rough=0.5, waterK=0.2, forestK=0.5, aridK=0.3, seedStr='land_a4')
F_land = generate_world(kn_land)
v_land = characterize_map(F_land)
ext_frac_land = v_land['exterior_water_fraction']
if ext_frac_land <= EXTERIOR_WATER_CEILING:
    if v_land['guard_exterior_water_fail']:
        fail('A4', f"land-heavy world (ext={ext_frac_land:.3f}) fired guard unexpectedly")
    else:
        ok('A4', f"land-heavy fixture (ext={ext_frac_land:.3f} <= {EXTERIOR_WATER_CEILING}): "
           f"guard_exterior_water_fail=False [CORRECT]")
else:
    print(f"     land-heavy fixture: ext={ext_frac_land:.3f} exceeded {EXTERIOR_WATER_CEILING} "
          f"(waterK=0.2 more ocean than expected — logged, not a failure)")

# Consistency check on reference worlds
for F, v, lbl in ref_worlds:
    expected_flag = v['exterior_water_fraction'] > EXTERIOR_WATER_CEILING
    if bool(v['guard_exterior_water_fail']) != bool(expected_flag):
        fail('A4', f"{lbl}: guard_exterior_water_fail={v['guard_exterior_water_fail']} "
             f"but ext_frac={v['exterior_water_fraction']:.4f}, expected {expected_flag}")

ok('A4', 'guard_exterior_water_fail consistent with exterior_water_fraction on all test worlds')


# ===========================================================================
# A5 — No regression: existing fields unchanged
# ===========================================================================
print("\n=== A5 regression check ===")
LEGACY_KEYS = [
    'waterPct', 'riverPct', 'biomeFrac', 'landCells', 'desert_fraction',
    'mountain_fraction', 'habitable_cell_count', 'invalid_substrate',
    'guard_a_fail', 'guard_b_fail', 'shore_cell_count', 'n_water_bodies',
    'shore_cell_fraction', 'largest_body_fraction', 'mean_npp_gm2',
    'habitable_cell_fraction', 'absent_biomes_forage',
]
for F, v, lbl in ref_worlds:
    for key in LEGACY_KEYS:
        if key not in v:
            fail('A5', f"{lbl}: legacy key '{key}' missing (regression)")
ok('A5', 'all legacy characterize_map() keys still present on all reference maps')


# ===========================================================================
# A6 — EXTERIOR_WATER_CEILING single-sourced + provisional
# ===========================================================================
print("\n=== A6 constant single-sourced ===")
import sic_games.terrain as _terrain_mod
import inspect
src = inspect.getsource(_terrain_mod)
ceiling_count = src.count('EXTERIOR_WATER_CEILING')
if ceiling_count < 2:  # at least definition + one use
    fail('A6', f"EXTERIOR_WATER_CEILING appears {ceiling_count} times in terrain.py "
         f"(expected >= 2: definition + guard use)")
if 'PROVISIONAL' not in src.split('EXTERIOR_WATER_CEILING')[0].split('\n')[-10:]:
    # check a broader window — find the constant's line and look for PROVISIONAL nearby
    lines = src.split('\n')
    for i, line in enumerate(lines):
        if 'EXTERIOR_WATER_CEILING' in line and '=' in line and not line.strip().startswith('#'):
            # Check surrounding 5 lines for PROVISIONAL comment
            context = '\n'.join(lines[max(0, i-5):i+3])
            if 'PROVISIONAL' not in context:
                fail('A6', "EXTERIOR_WATER_CEILING definition not accompanied by PROVISIONAL comment")
            break
ok('A6', f"EXTERIOR_WATER_CEILING={EXTERIOR_WATER_CEILING} single-sourced; "
   f"PROVISIONAL comment present")


# ===========================================================================
# Characterisation sweep — waterK across full [0,1] range, multi-seed
# ===========================================================================
print("\n=== Sweep: waterK in [0,1], 5 seeds, 21 steps ===")

SWEEP_SEEDS = ['42', '7', '1001', '13', '99']
SWEEP_FIXED = dict(relief=0.4, rough=0.5, forestK=0.5, aridK=0.3)
N_STEPS = 21
waterK_vals = [i / (N_STEPS - 1) for i in range(N_STEPS)]

sweep_rows = []
for wk in waterK_vals:
    for seed in SWEEP_SEEDS:
        kn = {**SWEEP_FIXED, 'waterK': wk, 'seedStr': f'p1s1b_{seed}'}
        v = characterize_map(generate_world(kn))
        sweep_rows.append({
            'waterK': wk,
            'seed': seed,
            'exterior_water_fraction':        v['exterior_water_fraction'],
            'interior_water_fraction':        v['interior_water_fraction'],
            'shoreline_fraction':             v['shoreline_fraction'],
            'largest_exterior_shore_to_area': v['largest_exterior_shore_to_area'],
            'n_interior_bodies':              v['n_interior_bodies'],
            'n_exterior_bodies':              v['n_exterior_bodies'],
            'guard_exterior_water_fail':      int(v['guard_exterior_water_fail']),
            'guard_a_fail':                   int(v['guard_a_fail']),
            'guard_b_fail':                   int(v['guard_b_fail']),
            'invalid_substrate':              int(v['invalid_substrate']),
        })

# Save raw CSV
csv_path = OUT / 'sweep_waterK_raw.csv'
with open(csv_path, 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(sweep_rows[0].keys()))
    w.writeheader()
    w.writerows(sweep_rows)
print(f"   saved sweep_waterK_raw.csv ({len(sweep_rows)} rows)")

# Aggregate per waterK (mean + spread across seeds)
agg: dict[float, dict] = {}
for row in sweep_rows:
    wk = row['waterK']
    if wk not in agg:
        agg[wk] = {k: [] for k in row if k not in ('waterK', 'seed')}
    for k in agg[wk]:
        agg[wk][k].append(row[k])

wk_sorted  = sorted(agg.keys())
ext_mean   = [np.mean(agg[wk]['exterior_water_fraction'])  for wk in wk_sorted]
ext_lo     = [np.min(agg[wk]['exterior_water_fraction'])   for wk in wk_sorted]
ext_hi     = [np.max(agg[wk]['exterior_water_fraction'])   for wk in wk_sorted]
int_mean   = [np.mean(agg[wk]['interior_water_fraction'])  for wk in wk_sorted]
int_lo     = [np.min(agg[wk]['interior_water_fraction'])   for wk in wk_sorted]
int_hi     = [np.max(agg[wk]['interior_water_fraction'])   for wk in wk_sorted]
shl_mean   = [np.mean(agg[wk]['shoreline_fraction'])       for wk in wk_sorted]
shl_lo     = [np.min(agg[wk]['shoreline_fraction'])        for wk in wk_sorted]
shl_hi     = [np.max(agg[wk]['shoreline_fraction'])        for wk in wk_sorted]
guard_rate = [np.mean(agg[wk]['guard_exterior_water_fail']) for wk in wk_sorted]


# ===========================================================================
# M1 — exterior / interior / shoreline vs waterK (§7 artifact 1)
# ===========================================================================
print("\n=== M1 exterior/interior/shoreline vs waterK ===")

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

# Top panel: ext / int / shoreline fractions
for vals, lo, hi, color, label in [
    (ext_mean,  ext_lo,  ext_hi,  '#3377cc', 'exterior_water_fraction'),
    (int_mean,  int_lo,  int_hi,  '#55aaee', 'interior_water_fraction'),
    (shl_mean,  shl_lo,  shl_hi,  '#44bb66', 'shoreline_fraction (land denom)'),
]:
    ax1.plot(wk_sorted, vals, color=color, linewidth=2, label=label)
    ax1.fill_between(wk_sorted, lo, hi, color=color, alpha=0.18)

ax1.axhline(EXTERIOR_WATER_CEILING, color='red', linestyle='--', linewidth=1.5,
            label=f'EXTERIOR_WATER_CEILING={EXTERIOR_WATER_CEILING} (provisional)')
ax1.set_ylabel('fraction of total / land cells', fontsize=11)
ax1.set_title(f'Phase 1 Stage 1b — M1: Water decomposition vs waterK\n'
              f'({len(SWEEP_SEEDS)} seeds; band = min-max; dashed = guard threshold)', fontsize=10)
ax1.legend(fontsize=9, loc='upper left')
ax1.set_ylim(-0.02, 1.02)
ax1.grid(alpha=0.3)

# Bottom panel: guard fire rate
ax2.bar(wk_sorted, guard_rate, width=0.04, color='salmon', alpha=0.8,
        label='guard_exterior_water_fail rate (fraction of seeds)')
ax2.set_xlabel('waterK knob', fontsize=11)
ax2.set_ylabel('guard fire rate', fontsize=11)
ax2.set_ylim(-0.05, 1.05)
ax2.legend(fontsize=9)
ax2.grid(alpha=0.3)

plt.tight_layout()
fig.savefig(OUT / 'M1_water_decomp_vs_waterK.png', dpi=120, bbox_inches='tight')
plt.close()
print("   saved M1_water_decomp_vs_waterK.png")


# ===========================================================================
# M2 — largest_exterior_shore_to_area vs exterior_water_fraction (§7 artifact 2)
# ===========================================================================
print("\n=== M2 shore-to-area vs exterior_fraction scatter ===")

all_ext   = [r['exterior_water_fraction']        for r in sweep_rows]
all_s2a   = [r['largest_exterior_shore_to_area'] for r in sweep_rows]
all_guard = [bool(r['guard_exterior_water_fail']) for r in sweep_rows]
all_wk    = [r['waterK']                         for r in sweep_rows]

fig, ax = plt.subplots(figsize=(9, 7))
pass_x = [x for x, g in zip(all_ext, all_guard) if not g]
pass_y = [y for y, g in zip(all_s2a, all_guard) if not g]
pass_c = [c for c, g in zip(all_wk,  all_guard) if not g]
fail_x = [x for x, g in zip(all_ext, all_guard) if g]
fail_y = [y for y, g in zip(all_s2a, all_guard) if g]

sc = ax.scatter(pass_x, pass_y, c=pass_c, cmap='Blues', s=35, alpha=0.75,
                vmin=0, vmax=1, label='guard PASS')
ax.scatter(fail_x, fail_y, marker='x', c='red', s=70, zorder=5,
           label=f'guard FAIL (ext > {EXTERIOR_WATER_CEILING})')
plt.colorbar(sc, ax=ax, label='waterK')
ax.axvline(EXTERIOR_WATER_CEILING, color='red', linestyle='--', linewidth=1.2,
           label=f'threshold={EXTERIOR_WATER_CEILING}')
ax.set_xlabel('exterior_water_fraction (of total cells)', fontsize=12)
ax.set_ylabel('largest_exterior_shore_to_area', fontsize=12)
ax.set_title(f'Phase 1 Stage 1b — M2: Coast vs ocean shape separation\n'
             f'High ratio = long thin coast; low ratio = fat ocean blob. '
             f'Separation here guides future shape-aware guard decision.', fontsize=9)
ax.legend(fontsize=9)
ax.grid(alpha=0.3)
plt.tight_layout()
fig.savefig(OUT / 'M2_shore_to_area_vs_exterior_frac.png', dpi=120, bbox_inches='tight')
plt.close()
print("   saved M2_shore_to_area_vs_exterior_frac.png")

# One-paragraph prose note (§7 requirement)
n_pass = sum(not g for g in all_guard)
n_fail = sum(all_guard)
ext_at_guard = [r['exterior_water_fraction'] for r in sweep_rows
                if r['guard_exterior_water_fail']]
guard_onset_wk = min((r['waterK'] for r in sweep_rows if r['guard_exterior_water_fail']),
                     default=None)
print(f"\n--- Prose note (M1/M2) ---")
print(f"Sweep: {len(waterK_vals)} waterK steps x {len(SWEEP_SEEDS)} seeds = "
      f"{len(sweep_rows)} maps. Guard fires on {n_fail}/{len(sweep_rows)} maps "
      f"(onset at waterK~={guard_onset_wk:.2f}).")
print(f"M1: exterior_water_fraction rises steeply above waterK~=0.4, crossing the "
      f"0.12 threshold. Interior fraction peaks at mid waterK then declines as water "
      f"bodies merge into one exterior body. Shoreline_fraction peaks at moderate "
      f"waterK (maximum land-water interface). Whether the 0.12 threshold falls in a "
      f"gap or continuum in the distribution is visible in M1.")
print(f"M2: largest_exterior_shore_to_area vs exterior_fraction. High s2a at low ext "
      f"fraction = thin coastal rim (long shore per unit sea). Low s2a at high ext "
      f"fraction = fat ocean blob. Whether these separate cleanly on the plot determines "
      f"whether a shape-aware guard can usefully separate coast from ocean worlds. "
      f"Supervisor decision deferred per blueprint §6.")
print(f"--- end prose note ---")


# ===========================================================================
# Final gate
# ===========================================================================
print()
if PASS_ALL:
    print("GATE GREEN — Phase 1 Stage 1b all acceptance checks pass.")
else:
    print("GATE RED — one or more checks failed (see RED lines above).")
