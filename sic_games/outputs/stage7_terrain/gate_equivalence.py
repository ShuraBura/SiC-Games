"""§6 Equivalence gate — 27 worlds × oracle battery.

Generates each world in Python and compares characterize_map() output to
the pre-computed oracle battery from the JS prototype.

Tolerances (pre-committed, blueprint §6):
  biomeFrac components  ±3 pp
  waterPct/riverPct/wetlandPct/hydratedPct  ±3 pp
  reliefEnvelopeM  ±5 %
  meanSlopeDeg  ±0.3°
  gameHumpPeak  ±0.05 (±1 bin of 20)

A SINGLE failure → non-zero exit (BLOCKING per Rule 11).
"""
import json, sys, pathlib

ROOT = pathlib.Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT / "src"))

from sic_games.terrain import generate_world, characterize_map

BATTERY_PATH = pathlib.Path(__file__).parent.parent.parent.parent / "SiC_Games_Terrain_Oracle_Battery.json"

BIOME_KEYS = ('forest', 'savanna', 'grassland', 'wetland', 'desert', 'mountain')
PCT_KEYS   = ('waterPct', 'riverPct', 'wetlandPct', 'hydratedPct')


def check_world(entry: dict) -> list[str]:
    """Returns list of failure strings (empty = pass)."""
    label = entry['label']
    seed  = entry['seed']
    knobs = {**entry['knobs'], 'seedStr': seed}
    ref   = entry['vector']

    F = generate_world(knobs)
    v = characterize_map(F)
    fails = []

    # biomeFrac ±3 pp
    for b in BIOME_KEYS:
        got = v['biomeFrac'].get(b, 0.0)
        exp = ref['biomeFrac'].get(b, 0.0)
        if abs(got - exp) > 3.0:
            fails.append(f"  biomeFrac[{b}]: got {got:.1f}  exp {exp:.1f}  delta {got-exp:+.1f} pp")

    # waterPct / riverPct / wetlandPct / hydratedPct ±3 pp
    for k in PCT_KEYS:
        got = v[k]; exp = ref[k]
        if abs(got - exp) > 3.0:
            fails.append(f"  {k}: got {got:.2f}  exp {exp:.2f}  delta {got-exp:+.2f} pp")

    # reliefEnvelopeM ±5%
    got_r = v['reliefEnvelopeM']; exp_r = ref['reliefEnvelopeM']
    if exp_r > 0 and abs(got_r - exp_r) / exp_r > 0.05:
        fails.append(f"  reliefEnvelopeM: got {got_r:.0f}  exp {exp_r:.0f}  delta {(got_r-exp_r)/exp_r*100:+.1f}%")

    # meanSlopeDeg ±0.3°
    got_s = v['meanSlopeDeg']; exp_s = ref['meanSlopeDeg']
    if abs(got_s - exp_s) > 0.3:
        fails.append(f"  meanSlopeDeg: got {got_s:.3f}  exp {exp_s:.3f}  delta {got_s-exp_s:+.3f}°")

    # gameHumpPeak ±0.05
    got_g = v['gameHumpPeak']; exp_g = ref['gameHumpPeak']
    if got_g is None or exp_g is None:
        if got_g != exp_g:
            fails.append(f"  gameHumpPeak: got {got_g}  exp {exp_g}")
    elif abs(got_g - exp_g) > 0.05:
        fails.append(f"  gameHumpPeak: got {got_g:.2f}  exp {exp_g:.2f}  delta {got_g-exp_g:+.2f}")

    return fails


def main():
    battery = json.loads(BATTERY_PATH.read_text())
    passed = 0; failed = 0
    all_fails = []

    for entry in battery:
        label = entry['label']; seed = entry['seed']
        tag   = f"{label}/seed={seed}"
        fails = check_world(entry)
        if fails:
            failed += 1
            all_fails.append((tag, fails))
            print(f"FAIL  {tag}")
            for f in fails:
                print(f)
        else:
            passed += 1
            print(f"pass  {tag}")

    print()
    print(f"Result: {passed}/{passed+failed} worlds pass")
    if failed:
        print(f"\nFAILED {failed} world(s) — BLOCKING STOP per blueprint §6 / Rule 11")
        print("Do NOT proceed without supervisor sign-off.")
        sys.exit(1)
    else:
        print("Equivalence gate GREEN — all 27 worlds within tolerance.")


if __name__ == '__main__':
    main()
