"""Score finished arms against the SPATIAL pass criteria, and against each other.

    py -3 sic_games/outputs/substrate_run/spatial_report.py claim_both disp_radius disp_attr0 disp_coh0

Reads `campaign_spatial_<tag>.npz` (arrangement) and `campaign_trajectory_<tag>.json` (rates), so one call
covers both halves of the standing report rule: the spatial sanity check AND the demography panel.

THE CRITERIA ARE FIXED BEFORE THE ARMS RUN, and are recorded here rather than in prose so a later reader can
see they were not chosen after seeing the numbers (R-106, 2026-08-16):

    spatial_paradox        True  -> False
    land used              13.4% -> > 50%
    km2 per band           214   -> > 314   (one Vita-Finzi & Higgs catchment)
    corr(forage, people)   +0.12 -> > +0.50
    top-decile occupied    34.6% -> > 80%

Only `0.091` (Binford packing) and `314 km2` (Vita-Finzi & Higgs) are FILED anchors. The land-use, correlation
and top-decile thresholds are ENGINEERING TARGETS for a dispersal fix, not ethnographic bands, and are labelled
so throughout -- per binding rule 2 of MARKER_MATRIX.md, an unfiled number must never read as an anchor.
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CELL_KM2 = 100.0
PACK = 0.091          # Binford 2001 packing threshold, persons/km2   [FILED ANCHOR]
CATCH = 314.0         # Vita-Finzi & Higgs 1970, 10 km HG catchment   [FILED ANCHOR]
# Engineering targets for the dispersal fix. NOT anchors.
T_LAND_USE, T_CORR, T_TOPDEC = 0.50, 0.50, 0.80


def _spatial(tag):
    p = os.path.join(HERE, f"campaign_spatial_{tag}.npz")
    if not os.path.exists(p):
        return None
    d = np.load(p)
    people, forage, hab = d["people"], d["forage_kcal"], d["habitable"]
    m = hab > 0
    occ = (people > 0) & m
    pop = int(people[m].sum())
    n_hab, n_occ = int(m.sum()), int(occ.sum())
    thr = np.quantile(forage[m], 0.9)
    top = m & (forage >= thr)
    return {
        "pop": pop, "n_hab": n_hab, "n_occ": n_occ,
        "land_use": n_occ / n_hab if n_hab else float("nan"),
        "regional": pop / (n_hab * CELL_KM2) if n_hab else float("nan"),
        "local": pop / (n_occ * CELL_KM2) if n_occ else float("nan"),
        "corr": float(np.corrcoef(forage[m].ravel(), people[m].ravel())[0, 1]),
        "topdec_occ": float((people[top] > 0).sum() / top.sum()) if top.sum() else float("nan"),
        "sites": int(d["sites"].sum()),
        "step": int(d["step"]),
    }


def _traj(tag, keys, last=120):
    p = os.path.join(HERE, f"campaign_trajectory_{tag}.json")
    if not os.path.exists(p):
        return {}
    rows = json.load(open(p, encoding="utf-8"))["traj"][-last:]
    out = {}
    for k in keys:
        v = [r[k] for r in rows if isinstance(r.get(k), (int, float))]
        out[k] = sum(v) / len(v) if v else float("nan")
    return out


def report(tags):
    S = {t: _spatial(t) for t in tags}
    missing = [t for t, v in S.items() if v is None]
    if missing:
        print(f"!! no spatial dump for: {', '.join(missing)} (run the arm first)\n")
    tags = [t for t in tags if S[t] is not None]
    if not tags:
        raise SystemExit("nothing to report")
    w = max(12, max(len(t) for t in tags) + 1)

    print("SPATIAL PASS CRITERIA  (fixed before the arms ran)")
    print(f"  {'':<22}" + "".join(f"{t:>{w}}" for t in tags) + "     target")
    rows = [
        ("pop", lambda s: f"{s['pop']:,}", ""),
        ("n_bands_sites", lambda s: f"{s['sites']}", ""),
        ("land used", lambda s: f"{100 * s['land_use']:.1f}%", f"> {100 * T_LAND_USE:.0f}%  [target]"),
        ("regional /km2", lambda s: f"{s['regional']:.4f}", f"~{PACK} [Binford]"),
        ("local /km2", lambda s: f"{s['local']:.3f}", f"< {PACK} [Binford]"),
        ("km2 per site", lambda s: f"{s['n_occ'] * CELL_KM2 / max(1, s['sites']):.0f}",
         f"> {CATCH:.0f} [V-F & Higgs]"),
        ("corr(forage,people)", lambda s: f"{s['corr']:+.3f}", f"> +{T_CORR:.2f} [target]"),
        ("top-decile occupied", lambda s: f"{100 * s['topdec_occ']:.1f}%", f"> {100 * T_TOPDEC:.0f}%  [target]"),
    ]
    for lab, fn, tgt in rows:
        print(f"  {lab:<22}" + "".join(f"{fn(S[t]):>{w}}" for t in tags) + f"     {tgt}")

    print("\n  PACKING PARADOX (packed AND sparse at once => not food-limited, failing to disperse)")
    line = ""
    for t in tags:
        s = S[t]
        par = (s["local"] > PACK * 1.10) and (s["regional"] < PACK / 1.10)
        line += f"{('PARADOX' if par else 'ok'):>{w}}"
    print(f"  {'verdict':<22}" + line + "     False")

    print("\nDEMOGRAPHY PANEL  (standing rule -- every report carries it)")
    keys = [("e15", "e15", "~35"), ("realised_tfr", "TFR", "5.0-8.0"),
            ("realised_ibi_med", "IBI med", "37.6"), ("cbr", "CBR /1k", "45-55"),
            ("surv_to_15", "l15", "0.55-0.60"), ("m_0_1", "m 0-1", "~0.20"),
            ("m_30_45", "m 30-45", ".005-.010"), ("starv_share", "starv share", ""),
            ("median_age_yr", "median age", "~20"), ("age_60_plus", "%60+", "~0.10"),
            ("band_med_adults", "band_med_ad", "28.2 adults"),
            ("frac_double_orphan", "%dbl orphan", ""), ("settle_med", "settle_med", "50-250")]
    T = {t: _traj(t, [k for k, _, _ in keys]) for t in tags}
    print(f"  {'':<22}" + "".join(f"{t:>{w}}" for t in tags) + "     anchor")
    for k, lab, anch in keys:
        vals = [T[t].get(k, float("nan")) for t in tags]
        if all(v != v for v in vals):
            continue
        print(f"  {lab:<22}" + "".join(f"{v:>{w}.4g}" for v in vals) + f"     {anch}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    report(sys.argv[1:])
