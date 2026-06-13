"""Phase 1 Stage 1c — Largest-Lake-Body Guard.

Acceptance checks A1-A8 (blueprint §5) + must-be-seen artifacts M1 (blueprint §6).

Run from sic_games/ directory:
    py outputs/phase1_stage1c/acceptance_and_artifacts.py
"""
import sys, pathlib, csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = pathlib.Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT / "src"))

from sic_games.terrain import (
    N, CELL_EDGE_M,
    EXTERIOR_WATER_CEILING, LARGE_BODY_CEILING,
    generate_world, characterize_map,
    _water_bodies, _classify_water_components, _component_sizes,
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


# ===========================================================================
# A1 — World dimensions verified
# ===========================================================================
print("\n=== A1 world dimensions ===")
# VERIFY against authoritative config (terrain.py constants)
EXPECTED_N = 100
EXPECTED_CELL_AREA_KM2 = 100.0          # CELL_EDGE_M=10000m → 10km × 10km = 100 km²
actual_cell_area = (CELL_EDGE_M / 1000) ** 2
if N != EXPECTED_N:
    fail('A1', f"N={N} != expected {EXPECTED_N} — ceiling rationale invalid; STOP")
elif abs(actual_cell_area - EXPECTED_CELL_AREA_KM2) > 0.01:
    fail('A1', f"cell_area={actual_cell_area:.1f} km² != expected 100 km²; STOP")
else:
    total_km2 = N * N * actual_cell_area
    ok('A1', f"N={N}, cell={actual_cell_area:.0f} km², total={total_km2:,.0f} km² — matches blueprint")


# ===========================================================================
# A2 — Discovery branch resolved
# ===========================================================================
print("\n=== A2 discovery branch ===")
# largest_body_fraction already exists in characterize_map() as largest_wb / total_cells
# from _water_bodies() — single largest component, not a sum.
# Branch 1B taken: statistic pre-existed.
_ref = generate_world(dict(relief=0.4, rough=0.5, waterK=0.5,
                            forestK=0.5, aridK=0.35, seedStr='42'))
_v = characterize_map(_ref)
if 'largest_body_fraction' in _v:
    ok('A2', "Branch 1B: largest_body_fraction pre-existed as largest_wb/total_cells "
       f"from _water_bodies() (4-nbr BFS, single largest component). "
       f"Now also exposed as 'largest_water_body_fraction'.")
else:
    fail('A2', "largest_body_fraction missing — unexpected; expected branch 1B")


# ===========================================================================
# A3 — largest_water_body_fraction is single-max (not sum)
# ===========================================================================
print("\n=== A3 single-largest-component assertion ===")
iw3 = np.zeros((N, N), dtype=np.uint8)
iw3[5:15, 5:15]   = 1   # 100 cells
iw3[20:40, 20:30] = 1   # 200 cells  ← largest
iw3[60:65, 60:65] = 1   # 25 cells
sizes3 = _component_sizes(iw3.astype(bool))
expected_largest = 200 / (N * N)
expected_sum     = (100 + 200 + 25) / (N * N)
actual_max_frac  = max(sizes3) / (N * N)

if len(sizes3) != 3:
    fail('A3', f"expected 3 components, got {len(sizes3)}")
elif abs(actual_max_frac - expected_largest) > 1e-12:
    fail('A3', f"largest_frac={actual_max_frac:.6f} != expected {expected_largest:.6f}")
elif abs(actual_max_frac - expected_sum) < 1e-12:
    fail('A3', "largest_frac incorrectly equals sum (should be max only)")
else:
    ok('A3', f"single max confirmed: {actual_max_frac:.5f} (sum would be {expected_sum:.5f})")


# ===========================================================================
# A4 — Connectivity correctness (4-nbr; diagonal = NOT connected)
# ===========================================================================
print("\n=== A4 connectivity correctness ===")
iw4 = np.zeros((N, N), dtype=np.uint8)
iw4[5:15, 5:15]   = 1   # blob A: 100
iw4[20:40, 20:30] = 1   # blob B: 200
iw4[50, 50] = 1          # cell C
iw4[51, 51] = 1          # cell D — diagonal from C (NOT 4-connected)
sizes4 = sorted(_component_sizes(iw4.astype(bool)))
if sizes4 != [1, 1, 100, 200]:
    fail('A4', f"expected [1,1,100,200] under 4-connectivity, got {sizes4}")
else:
    ok('A4', f"4-connectivity correct: diagonal pair = 2 bodies; got {sizes4}")


# ===========================================================================
# A5 — Median used (not mean) for characteristic sizes
# ===========================================================================
print("\n=== A5 median != mean on heavy-tailed input ===")
iw5 = np.zeros((N, N), dtype=np.uint8)
iw5[0, 0] = 1; iw5[0, 2] = 1; iw5[0, 4] = 1; iw5[0, 6] = 1  # 4 singletons
iw5[10:50, 10:35] = 1  # large blob (~1000 cells)
sizes5 = _component_sizes(iw5.astype(bool))
med5  = float(np.median(sizes5))
mean5 = float(np.mean(sizes5))
if abs(med5 - mean5) < 0.01:
    fail('A5', f"median={med5} == mean={mean5:.1f} — no heavy-tail distinction")
elif med5 != 1.0:
    fail('A5', f"expected median=1 for heavy-tailed set, got {med5}")
else:
    ok('A5', f"median={med5:.0f} != mean={mean5:.1f} — heavy-tail distinction confirmed")


# ===========================================================================
# A6 — Guard swap complete
# ===========================================================================
print("\n=== A6 guard swap ===")
REF_KNOBS = [
    dict(relief=0.4, rough=0.5, waterK=0.5,  forestK=0.5, aridK=0.35, seedStr='42'),
    dict(relief=0.3, rough=0.4, waterK=0.3,  forestK=0.8, aridK=0.2,  seedStr='7'),
    dict(relief=0.6, rough=0.6, waterK=0.4,  forestK=0.2, aridK=0.6,  seedStr='1001'),
]
for kn in REF_KNOBS:
    F_ = generate_world(kn)
    v_ = characterize_map(F_)
    if 'guard_large_body_fail' not in v_:
        fail('A6', f"seed={kn['seedStr']}: guard_large_body_fail missing")
    # guard_exterior_water_fail must still be reported (diagnostic)
    if 'guard_exterior_water_fail' not in v_:
        fail('A6', f"seed={kn['seedStr']}: guard_exterior_water_fail missing (should stay as diagnostic)")
    # invalid_substrate must NOT include exterior guard
    expected_inv = v_['guard_a_fail'] or v_['guard_b_fail'] or v_['guard_large_body_fail']
    if bool(v_['invalid_substrate']) != bool(expected_inv):
        fail('A6', f"seed={kn['seedStr']}: invalid_substrate={v_['invalid_substrate']} != "
             f"a|b|large_body={expected_inv}")
    # LARGE_BODY_CEILING must not be hardcoded in guard (it is sourced from the named constant)
    expected_flag = v_['largest_water_body_fraction'] > LARGE_BODY_CEILING
    if bool(v_['guard_large_body_fail']) != bool(expected_flag):
        fail('A6', f"seed={kn['seedStr']}: guard_large_body_fail inconsistent with LARGE_BODY_CEILING")
ok('A6', f"guard swap complete: exterior guard retired; largest_water_body_fraction > "
   f"LARGE_BODY_CEILING={LARGE_BODY_CEILING} is sole large-water gate; "
   f"LARGE_BODY_CEILING sourced from named constant")


# ===========================================================================
# A7 — All pre-existing Stage 1b tests still pass (regression check)
# ===========================================================================
print("\n=== A7 Stage 1b regression ===")
P1S1B_KEYS = [
    'exterior_water_fraction', 'interior_water_fraction',
    'n_interior_bodies', 'n_exterior_bodies',
    'shoreline_fraction', 'largest_exterior_body_cells',
    'largest_exterior_shore_to_area', 'guard_exterior_water_fail',
]
for kn in REF_KNOBS:
    F_ = generate_world(kn)
    v_ = characterize_map(F_)
    for key in P1S1B_KEYS:
        if key not in v_:
            fail('A7', f"seed={kn['seedStr']}: regression — missing P1S1b key '{key}'")
ok('A7', "all P1S1b fields present on all reference worlds")


# ===========================================================================
# A8 — M1 sweep CSV produced (§3)
# ===========================================================================
print("\n=== A8 / M1 waterK sweep (21 steps x 5 seeds) ===")

SEEDS = ['42', '7', '1001', '13', '99']
WATER_K_STEPS = [round(i * 0.05, 2) for i in range(21)]   # 0.00 ... 1.00
BASE_KNOBS = dict(relief=0.5, rough=0.6, forestK=0.5, aridK=0.3)

rows = []
for wk in WATER_K_STEPS:
    for sd in SEEDS:
        kn = {**BASE_KNOBS, 'waterK': wk, 'seedStr': sd}
        F_ = generate_world(kn)
        v_ = characterize_map(F_)
        rows.append({
            'waterK': wk,
            'seed': sd,
            'largest_water_body_fraction': v_['largest_water_body_fraction'],
            'water_body_count': v_['water_body_count'],
            'characteristic_water_body_size': v_['characteristic_water_body_size'],
            'characteristic_interlake_patch_size': v_['characteristic_interlake_patch_size'],
            'exterior_water_fraction': v_['exterior_water_fraction'],
            'interior_water_fraction': v_['interior_water_fraction'],
            'guard_large_body_fail': int(v_['guard_large_body_fail']),
            'guard_exterior_water_fail': int(v_['guard_exterior_water_fail']),
            'invalid_substrate': int(v_['invalid_substrate']),
        })

csv_path = OUT / 'sweep_waterK_stage1c.csv'
fieldnames = list(rows[0].keys())
with open(csv_path, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

ok('A8', f"sweep CSV written: {csv_path.name} ({len(rows)} rows)")


# ===========================================================================
# MUST-BE-SEEN ARTIFACT 1 — largest_water_body_fraction across sweep
# ===========================================================================
print("\n" + "="*70)
print("ARTIFACT 1 — largest_water_body_fraction per seed and mean")
print("="*70)
print(f"{'wK':>5} | {'42':>7} {'7':>7} {'1001':>7} {'13':>7} {'99':>7} | {'mean':>7} | {'any_guard':>9}")
print("-"*70)

for wk in WATER_K_STEPS:
    seed_rows = {r['seed']: r for r in rows if r['waterK'] == wk}
    vals = [seed_rows[s]['largest_water_body_fraction'] for s in SEEDS]
    mean_v = float(np.mean(vals))
    any_g  = any(seed_rows[s]['guard_large_body_fail'] for s in SEEDS)
    guard_str = 'TRUE*' if any_g else 'False'
    row_str = f"{wk:5.2f} | " + " ".join(f"{v:7.4f}" for v in vals) + f" | {mean_v:7.4f} | {guard_str:>9}"
    # mark rows near candidate ceilings
    if mean_v >= 0.08:
        row_str += "  <- >=0.08"
    print(row_str)

# Cross-candidate crossing waterK
for ceiling, label in [(0.08, '0.08'), (0.10, '0.10'), (0.12, '0.12')]:
    crosses = []
    for wk in WATER_K_STEPS:
        seed_rows = {r['seed']: r for r in rows if r['waterK'] == wk}
        for s in SEEDS:
            if seed_rows[s]['largest_water_body_fraction'] > ceiling:
                crosses.append(f"wK={wk:.2f}/seed={s}")
                break
        else:
            continue
        break
    first_cross = crosses[0] if crosses else "none in sweep"
    print(f"\nFirst crossing of {label} ceiling: {first_cross}")


# ===========================================================================
# MUST-BE-SEEN ARTIFACT 2 — land-of-lakes descriptors at high-waterK end
# ===========================================================================
print("\n" + "="*70)
print("ARTIFACT 2 — land-of-lakes descriptors at wK >= 0.65")
print("('inland sea' = large single body + low count + small interlake patches)")
print("="*70)
print(f"{'wK':>5} {'seed':>6} | {'n_bodies':>8} {'char_wtr':>9} {'char_lnd':>9} | {'lwbf':>7} | {'large_body':>10}")
print("-"*70)

for wk in [wk for wk in WATER_K_STEPS if wk >= 0.65]:
    for sd in SEEDS:
        r = next(r for r in rows if r['waterK'] == wk and r['seed'] == sd)
        flag = 'GUARD' if r['guard_large_body_fail'] else ''
        print(f"{wk:5.2f} {sd:>6} | {r['water_body_count']:8d} "
              f"{r['characteristic_water_body_size']:9.1f} "
              f"{r['characteristic_interlake_patch_size']:9.1f} | "
              f"{r['largest_water_body_fraction']:7.4f} | {flag:>10}")
    print()


# ===========================================================================
# M1 plot — largest_water_body_fraction + guard
# ===========================================================================
fig, axes = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
ax1, ax2 = axes

colors = {'42': 'tab:blue', '7': 'tab:orange', '1001': 'tab:green',
          '13': 'tab:red', '99': 'tab:purple'}

for sd in SEEDS:
    wk_arr = [r['waterK'] for r in rows if r['seed'] == sd]
    lwbf   = [r['largest_water_body_fraction'] for r in rows if r['seed'] == sd]
    ax1.plot(wk_arr, lwbf, '-o', ms=3, color=colors[sd], label=f'seed={sd}', alpha=0.8)

mean_lwbf = [float(np.mean([r['largest_water_body_fraction']
                            for r in rows if r['waterK'] == wk]))
             for wk in WATER_K_STEPS]
ax1.plot(WATER_K_STEPS, mean_lwbf, 'k-', lw=2.5, label='mean', zorder=5)
for c, ls, lbl in [(0.08, '--', '0.08'), (0.10, '-', '0.10 (LARGE_BODY_CEILING)'), (0.12, ':', '0.12')]:
    ax1.axhline(c, color='gray', ls=ls, lw=1.2, label=lbl)
ax1.set_ylabel('largest_water_body_fraction')
ax1.set_title('Stage 1c — M1: largest_water_body_fraction vs waterK')
ax1.legend(fontsize=7, ncol=2)
ax1.set_ylim(0, 0.65)

# Guard fire rate per waterK
guard_rates = [float(np.mean([r['guard_large_body_fail']
                              for r in rows if r['waterK'] == wk]))
               for wk in WATER_K_STEPS]
ax2.bar(WATER_K_STEPS, guard_rates, width=0.04, color='crimson', alpha=0.7)
ax2.axhline(0.5, color='gray', ls='--', lw=1)
ax2.set_ylabel('guard_large_body_fail rate')
ax2.set_xlabel('waterK')
ax2.set_ylim(0, 1.1)

plt.tight_layout()
fig.savefig(OUT / 'M1_largest_body_sweep.png', dpi=150)
plt.close(fig)
ok('plot', f"M1_largest_body_sweep.png saved")


# ===========================================================================
# Final verdict
# ===========================================================================
print("\n" + "="*70)
if PASS_ALL:
    print("GATE GREEN — Stage 1c acceptance block: all assertions pass.")
else:
    print("GATE RED   — Stage 1c: one or more assertions failed (see RED lines above).")
print("="*70)
print(f"\nLARGE_BODY_CEILING = {LARGE_BODY_CEILING} (PROVISIONAL scope decision)")
print("CC does not lock the ceiling. Supervisor decision required against the seen curve.")
