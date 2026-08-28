"""Score village_identity A/B across biomes against the three predictions registered before the runs.

    py -3 sic_games/outputs/substrate_run/biome_ab_report.py temp bore sav

For each biome it reads campaign_trajectory_id_<b>_{on,off}.json and reports, at EQUILIBRIUM (last 20% of
rows) unless stated:

  P1  n_bands COLLAPSES with identity on        (the 45-bands artifact ends)
  P2  age structure moves toward the anchors    (frac_child -> ~0.40, median age -> ~20)
  P3  population is STABLE, not leaking         (tail births ~= deaths; trend flat)

A biome where P1 fails, or where the tail is still trending down, falsifies "identity is biome-general".
Purely descriptive; the anchors quoted are the filed ones (frac_child ~0.40, median ~20 Ache).
"""
from __future__ import annotations
import json, os, statistics as st, sys

HERE = os.path.dirname(os.path.abspath(__file__))


def _rows(tag):
    p = os.path.join(HERE, f"campaign_trajectory_{tag}.json")
    if not os.path.exists(p):
        return None
    return json.load(open(p, encoding="utf-8"))["traj"]


def _m(rows, k):
    v = [r.get(k) for r in rows if isinstance(r.get(k), (int, float))]
    return st.mean(v) if v else float("nan")


def _summary(tag):
    r = _rows(tag)
    if not r:
        return None
    tail = r[int(len(r) * 0.8):]
    births = sum(x.get("births", 0) for x in tail)
    dpop = tail[-1]["pop"] - tail[0]["pop"]
    deaths = births - dpop
    pops = [x["pop"] for x in tail]
    return {
        "final_step": r[-1]["step"],
        "pop": _m(tail, "pop"),
        "pop_trend": tail[-1]["pop"] - tail[0]["pop"],
        "pop_min": min(pops), "pop_max": max(pops),
        "births": births, "deaths": deaths, "net": births - deaths,
        "n_bands": _m(tail, "n_bands"),
        "band_med_adults": _m(tail, "band_med_adults"),
        "e15": _m(tail, "e15"), "tfr": _m(tail, "realised_tfr"),
        "m_0_1": _m(tail, "m_0_1"), "l15": _m(tail, "surv_to_15"),
        "median_age": _m(tail, "median_age_yr"),
        "settle_med": _m(tail, "settle_med"),
        "starv": _m(tail, "starv_share"),
    }


def report(biomes):
    print("VILLAGE IDENTITY A/B ACROSS BIOMES  (equilibrium = last 20% of rows)")
    rows = [("pop", "pop", "{:.0f}"), ("pop trend (tail)", "pop_trend", "{:+.0f}"),
            ("births tail", "births", "{:.0f}"), ("deaths tail", "deaths", "{:.0f}"),
            ("net (b-d)", "net", "{:+.0f}"),
            ("n_bands  [P1]", "n_bands", "{:.1f}"), ("band_med_adults", "band_med_adults", "{:.1f}"),
            ("median age [P2]", "median_age", "{:.1f}"), ("e15", "e15", "{:.1f}"),
            ("TFR", "tfr", "{:.2f}"), ("m_0_1", "m_0_1", "{:.3f}"), ("l15", "l15", "{:.3f}"),
            ("settle_med", "settle_med", "{:.1f}"), ("starv share", "starv", "{:.3f}")]
    for b in biomes:
        on, off = _summary(f"id_{b}_on"), _summary(f"id_{b}_off")
        print(f"\n--- {b} ---")
        if not on or not off:
            print(f"  incomplete (on={'ok' if on else 'MISSING'} off={'ok' if off else 'MISSING'})")
            continue
        print(f"  {'':<20}{'identity ON':>14}{'identity OFF':>14}     note")
        for lab, k, fmt in rows:
            print(f"  {lab:<20}{fmt.format(on[k]):>14}{fmt.format(off[k]):>14}")
        p1 = on["n_bands"] < 0.6 * off["n_bands"]
        p3 = abs(on["net"]) <= max(40, 0.05 * on["births"])
        print(f"  P1 bands collapse : {'PASS' if p1 else 'FAIL'}"
              f"   ({off['n_bands']:.0f} -> {on['n_bands']:.0f})")
        print(f"  P3 stable (b~=d)  : {'PASS' if p3 else 'FAIL'}"
              f"   (net {on['net']:+.0f} on {on['births']:.0f} births)")
        if on["pop"] < 300:
            print("  !! WORLD IS NEAR-DEAD (pop < 300) -- this biome cannot test identity")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    report(sys.argv[1:])
