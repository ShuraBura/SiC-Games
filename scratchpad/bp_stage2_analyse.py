"""R-106 Add.106 STAGE 2 analysis — canon vs `enable_density_fill_matched_radius` on the three canonical worlds.

INSTRUMENT. The life table is computed by the MODEL'S OWN `TerrainWorld.life_table`, called unbound on the raw
counters the campaign dumped (it reads only lt_exposure / lt_deaths / lt_deaths_starv / lt_deaths_senesc from
self). Nothing is re-implemented, so the fourth-and-fifth-time measurement error of this arc cannot recur here.

POSITIVE CONTROL (validate the instrument before believing it): the CUMULATIVE table rebuilt from the final
counters must reproduce the last trajectory row's `realised_e0`, which the campaign computed live. If it does not,
the period numbers below are not trustworthy and the script says so.

PERIOD TABLE: final counters minus the snapshot at C_LT_SNAP_STEP = the life table over the equilibrium window
only, free of the founding transient that every row's cumulative `realised_e0` carries.

REPORTED per world, mean over paired demographic seeds, plus the paired difference:
  e0 (period)             vs the Ache anchor 36.6 — THE ADOPTION QUESTION
  surv_to_15 (period)     vs the Ache anchor 0.66
  starvation share        (period)
  population, villages, village median (Bar-Yosef 40-150), land use — sustained window (rows after the snapshot)
"""
import glob
import json
import os
import re
import statistics as st
import sys
from types import SimpleNamespace

ROOT = r"C:\Users\syatom\Projects\SiC Games"
sys.path.insert(0, os.path.join(ROOT, "sic_games", "src"))
from sic_games.phase1_model import TerrainWorld   # noqa: E402

OUTDIR = os.path.join(ROOT, "sic_games", "outputs", "substrate_run")
PATTERN = os.environ.get("S2_PATTERN", "campaign_trajectory_s2_*.json")
E0_ANCHOR = 36.6
SURV15_ANCHOR = 0.66
KEYS = ("lt_exposure", "lt_deaths", "lt_deaths_starv", "lt_deaths_senesc")


def lt_from(counters, since=None):
    fake = SimpleNamespace(**{k: list(counters[k]) for k in KEYS})
    return TerrainWorld.life_table(fake, since=since)


def load(path):
    d = json.load(open(path, encoding="utf-8"))
    meta, traj = d["meta"], d["traj"]
    fin = meta.get("life_table_final")
    snap = meta.get("life_table_snap")
    snap_step = meta.get("life_table_snap_step")
    if fin is None:
        return None, "no life_table_final in meta"
    cum = lt_from(fin)
    live_e0 = traj[-1].get("realised_e0")
    control_ok = live_e0 is not None and abs(round(cum["e0"], 2) - live_e0) < 0.02
    out = dict(control_ok=control_ok, cum_e0=cum["e0"], live_e0=live_e0,
               final_step=traj[-1].get("step"), final_pop=traj[-1].get("pop"))
    if snap is None:
        out["period"] = False
        return out, "no life_table_snap (C_LT_SNAP_STEP unset?)"
    per = lt_from(fin, since={k: snap[k] for k in KEYS})
    win = [r for r in traj if (r.get("step") or 0) > snap_step]

    def wmean(f):
        v = [r[f] for r in win if r.get(f) is not None and r.get(f) == r.get(f)]
        return st.mean(v) if v else float("nan")
    out.update(period=True, snap_step=snap_step,
               e0=per["e0"], surv15=per["surv_to_15"], starv=per["starv_share"],
               # ZERO-SUM CHECK (Add.76): does feeding children just move deaths to adults? Period death rates by age.
               m_1_15=_mrate(per, ("1_5", "5_15")), m_15_45=_mrate(per, ("15_30", "30_45")),
               e15=per["e15"], l45=per["surv_to_45"],
               pop=wmean("pop"), n_vill=wmean("n_villages"), vill_med=wmean("village_med"),
               land_use=wmean("spatial_land_use_frac"))
    return out, None


def _mrate(per, keys):
    """Pooled period death rate over the named age bands (deaths / person-years)."""
    d = sum(per["deaths_by_band"].get(k, 0.0) for k in keys)
    e = sum(per["exposure_by_band"].get(k, 0.0) for k in keys)
    return d / e if e > 0 else float("nan")


def ms(v):
    v = [x for x in v if x == x]
    if not v:
        return float("nan"), 0.0
    return st.mean(v), (st.stdev(v) / len(v) ** 0.5 if len(v) > 1 else 0.0)


def main():
    files = sorted(glob.glob(os.path.join(OUTDIR, PATTERN)))
    if not files:
        print(f"no files match {PATTERN} in {OUTDIR}")
        return
    res: dict = {}
    print("POSITIVE CONTROL — cumulative e0 rebuilt from the dumped counters vs the campaign's live value")
    bad = 0
    for f in files:
        m = re.search(r"campaign_trajectory_s2_(\w+?)_(canon|fix|viable|bandprov|both|pat|vgran|sticky|risk|riskvg)_s(\d+)\.json$", os.path.basename(f))
        tag = os.path.basename(f)
        r, err = load(f)
        if r is None:
            print(f"  {tag}: SKIP ({err})")
            continue
        flag = "ok" if r["control_ok"] else "MISMATCH"
        bad += 0 if r["control_ok"] else 1
        print(f"  {tag:52s} rebuilt {r['cum_e0']:6.2f}  live {r['live_e0']}  -> {flag}"
              + (f"   [{err}]" if err else ""))
        if m and r.get("period"):
            w, arm, s = m.group(1), m.group(2), int(m.group(3))
            res.setdefault(w, {}).setdefault(arm, {})[s] = r
    if bad:
        print(f"\n!! {bad} run(s) FAILED the positive control — period numbers are NOT trustworthy.")
        return
    print("  all controls pass — the offline life table reproduces the campaign's own.\n")

    rows = [("e0", "e0, PERIOD (Ache 36.6)", "{:.2f}"),
            ("surv15", "survival to 15, PERIOD (Ache 0.66)", "{:.3f}"),
            ("starv", "starvation share, PERIOD", "{:.3f}"),
            ("e15", "#20 adult e15 (band 28.6-42.5)", "{:.2f}"),
            ("l45", "#21 survival to 45 (band 0.26-0.43)", "{:.3f}"),
            ("m_1_15", "death rate age 1-15 (/py), PERIOD", "{:.4f}"),
            ("m_15_45", "death rate age 15-45 (/py) ZERO-SUM?", "{:.4f}"),
            ("pop", "population (sustained)", "{:.0f}"),
            ("n_vill", "villages (sustained)", "{:.1f}"),
            ("vill_med", "village median (Bar-Yosef 40-150)", "{:.1f}"),
            ("land_use", "land use frac (sustained)", "{:.3f}")]
    for w in ("temperate", "savanna", "montane"):
        ARM = os.environ.get("S2_ARM", "fix")
        BASE = os.environ.get("S2_BASE", "canon")
        if w not in res or BASE not in res[w] or ARM not in res[w]:
            print(f"== {w}: incomplete")
            continue
        seeds = sorted(set(res[w][BASE]) & set(res[w][ARM]))
        print(f"== {w.upper()}  (n={len(seeds)} paired demographic seeds, planet fixed)")
        print(f"   {'metric':38s}{'canon':>12s}{'fix':>12s}{'paired diff':>24s}")
        for k, label, fmt in rows:
            a = [res[w][BASE][s][k] for s in seeds]
            b = [res[w][ARM][s][k] for s in seeds]
            ma = ms(a)[0]; mb = ms(b)[0]
            md, ed = ms([y - x for x, y in zip(a, b)])
            z = (md / ed) if ed > 0 else float("nan")
            star = " *" if ed > 0 and abs(z) >= 2 else ""
            print(f"   {label:38s}{fmt.format(ma):>12s}{fmt.format(mb):>12s}"
                  f"{(fmt.format(md) + ' +/- ' + fmt.format(ed) + f' ({z:+.1f}se)' + star):>24s}")
        # ANCHORS BY BIOME (MARKER_MATRIX #18/#19, Gurven & Kaplan 2007 Table 2, verify_anchor.py). Band e0 21-37,
        # l15 0.45-0.66; savanna's biome match is the Hiwi (llanos) 27 / 0.53; no temperate forager in the table.
        # (Scoring every world against Ache 36.6 was the error corrected 2026-09-23.)
        ca, fa = (ms([res[w][a][s]["e0"] for s in seeds])[0] for a in (BASE, ARM))
        cl, fl = (ms([res[w][a][s]["surv15"] for s in seeds])[0] for a in (BASE, ARM))
        band = lambda v, lo, hi: "IN" if lo <= v <= hi else ("UNDER" if v < lo else "OVER")
        pt = {"savanna": " | Hiwi 27 / 0.53"}.get(w, "")
        print(f"   -> #18 e0 (band 21-37): canon {ca:.2f} {band(ca, 21, 37)}, {ARM} {fa:.2f} {band(fa, 21, 37)}"
              f"   #19 l15 (band 0.45-0.66): canon {cl:.3f} {band(cl, 0.45, 0.66)}, {ARM} {fl:.3f} "
              f"{band(fl, 0.45, 0.66)}{pt}\n")


if __name__ == "__main__":
    main()
