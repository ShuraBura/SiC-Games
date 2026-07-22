"""Morning check for the overnight T-9 matched pair. One command, no arguments.

    py -3 sic_games/outputs/substrate_run/check_t9_overnight.py

Reports, in order of what would kill the result:
  1. did both arms FINISH, and did the harness flag any config or consistency violation
  2. is the substrate still sane -- stratification against R-64's validated 9-16%, villages against Bar-Yosef
  3. the T-9 comparison itself, egalitarian vs stratified, against the three FILED genetic anchors
  4. the cycle test, now with 5x the window R-97 had

Deliberately prints the ARM CONFIG beside every number (charter D3/D16): the world and flags are part of the
finding, not run trivia.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ARMS = [("egalitarian (elite OFF)", "t9_egal"), ("stratified (full stack)", "t9_strat")]

# FILED + primary-verified anchors. NB the units differ and are NOT interchangeable -- see LITERATURE/TARGETS.
YAN_MODAL_CLADE = 0.16        # largest single clade, like-for-like with top_share
HILL_LPB = 7.0                # ~7 lineages per band
R64_STRAT = (9.0, 16.0)       # validated sustained stratification band
BARYOSEF = (50, 150)          # village size


def load(tag):
    p = os.path.join(HERE, f"campaign_trajectory_{tag}.json")
    if not os.path.exists(p):
        return None, None
    b = json.load(open(p))
    return b.get("traj", []), b.get("meta", {})


def prog_flags(tag):
    p = os.path.join(HERE, f"campaign_progress_{tag}.txt")
    if not os.path.exists(p):
        return ["progress file missing"], False
    lines = open(p, encoding="utf-8", errors="replace").read().splitlines()
    return [l.strip() for l in lines if "!!" in l], any("DONE step=" in l for l in lines)


def main():
    print("=" * 100)
    print("OVERNIGHT T-9 MATCHED PAIR — morning check")
    print("=" * 100)

    data = {}
    for lab, tag in ARMS:
        tr, meta = load(tag)
        flags, done = prog_flags(tag)
        data[lab] = (tr, meta, flags, done)
        last = tr[-1]["step"] if tr else 0
        print(f"\n[{lab}]  tag={tag}")
        print(f"  finished: {'YES' if done else 'NO — still running or died'}   reached step {last}")
        if meta:
            print(f"  world={meta.get('world')} founders={meta.get('founders')} seed={meta.get('seed')} "
                  f"elite={meta.get('elite')} defend={meta.get('defend')} rellegit={meta.get('rellegit')}")
        if flags:
            print(f"  !! {len(flags)} FLAG(S) RAISED — read these before anything else:")
            for f in flags[:12]:
                print(f"     {f}")
        else:
            print("  no config or consistency violations")

    if not all(d[0] for d in data.values()):
        print("\nAt least one arm has no trajectory; stopping.")
        return

    # ── 2. substrate sanity ─────────────────────────────────────────────────────────────────────────
    print("\n" + "-" * 100)
    print("SUBSTRATE SANITY (does the long run still reproduce the validated baseline?)")
    print(f"{'arm':>26} {'strat% mean(last 1/3)':>22} {'vs R-64 9-16%':>15} {'vil_med':>9} {'vs Bar-Yosef':>14}")
    for lab, _ in ARMS:
        tr = data[lab][0]
        cut = tr[-1]["step"] * 2 // 3
        v = [r["pct_stratified"] for r in tr if r["step"] >= cut]
        m = sum(v) / len(v)
        vm = tr[-1]["village_med"]
        ok_s = "IN BAND" if R64_STRAT[0] <= m <= R64_STRAT[1] else ("HIGH" if m > R64_STRAT[1] else "LOW")
        try:
            ok_v = "in range" if BARYOSEF[0] <= float(vm) <= BARYOSEF[1] else "OUT OF RANGE"
        except (TypeError, ValueError):
            ok_v = "?"
        print(f"{lab:>26} {m:>22.1f} {ok_s:>15} {str(vm):>9} {ok_v:>14}")

    # ── 3. the T-9 comparison ───────────────────────────────────────────────────────────────────────
    print("\n" + "-" * 100)
    print("T-9 — DYNASTIC CONCENTRATION, egalitarian vs stratified (the point of the run)")
    print(f"{'arm':>26} {'n_lineages':>11} {'eff_lineages':>13} {'top_share':>10} {'lin/band':>9} {'pop':>7}")
    for lab, _ in ARMS:
        r = data[lab][0][-1]
        print(f"{lab:>26} {r['n_lineages']:>11} {r['eff_lineages']:>13.1f} {r['lin_top_share']:>10.3f} "
              f"{r.get('lineages_per_band', 0):>9.2f} {r['pop']:>7}")
    print(f"\n  ANCHORS (filed + primary-verified; UNITS DIFFER, do not cross-compare):")
    print(f"    Yan 2014   modal clade  {YAN_MODAL_CLADE:.2f}   <- like-for-like with top_share")
    print(f"    Hill 2011  lineages/band {HILL_LPB:.1f}")
    print(f"    Zerjal 2003 ~8% is ONE NAMED lineage's expansion, NOT the modal share — do not compare to top_share")
    print(f"    Karmin 2015 female Ne up to 17x male Ne — aggregate, no direct model analogue in this table")

    # ── 4. cycles, with 5x R-97's window ────────────────────────────────────────────────────────────
    print("\n" + "-" * 100)
    print("CYCLES (R-97 found none at 3k; this window is 5x longer)")
    try:
        sys.path.insert(0, HERE)
        from probe_r97_cycles import period_of, NULL_P95, SAMPLE_EVERY
        for lab, _ in ARMS:
            tr = data[lab][0]
            s = [r.get("frac_gumsa", 0.0) for r in tr]
            p, a = period_of(s, sample_every=SAMPLE_EVERY)
            verdict = ("CYCLE clears null" if (p and a > NULL_P95)
                       else ("below null floor" if p else "no turning point"))
            print(f"{lab:>26}  period={str(p) if p else '-':>7}  ac_peak={a:>7.3f}  (null {NULL_P95})  {verdict}")
        print("\n  NB re-run the D1 positive control at THIS length before trusting a negative"
              "\n  (probe_r97_cycles.py does it inline) — a longer series changes the detector's power.")
    except Exception as e:
        print(f"  cycle check unavailable: {e}")

    print("\n" + "=" * 100)


if __name__ == "__main__":
    main()
