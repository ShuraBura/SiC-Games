"""R-106 Addendum 100 — the definitive scorecard: three full-length (15000-step) canonical campaigns, scored against
every corrected marker from the Add.86-99 audit arc. Reads the real campaign trajectory JSON (not the probe harness),
takes a SUSTAINED window (the last 15% of rows) per world to avoid the early-transient state visible in gini_cred /
n_bands / eff_lineages, and reports mean+/-SE per world plus the anchor comparison.
"""
import json
import statistics as st
import numpy as np

WORLDS = {
    "temperate": "sic_games/outputs/substrate_run/campaign_trajectory_scorecard99_temperate.json",
    "savanna":   "sic_games/outputs/substrate_run/campaign_trajectory_scorecard99_savanna.json",
    "montane":   "sic_games/outputs/substrate_run/campaign_trajectory_scorecard99_montane.json",
}

# (marker label, field, anchor text, lo, hi)  -- lo/hi None means no numeric band, just report
MARKERS = [
    ("#1 band size (mean-experienced adults/cell)", "band_experienced_adults", "Hill 2011 = 28.2", 12, 40),
    ("#3 village size (median)", "village_med", "Alvard 2009 = 50-250", 50, 250),
    ("#3 village size (max)", "village_max", "Alvard 2009 <= 250 (ceiling)", None, 250),
    ("#4 connubium reach (median)", "connubium_med", "Wobst equilibrium ~475 (floor: White MVP 150)", 150, None),
    ("#10 polygyny (of ALL men)", "frac_polygynous_all_m", "Marlowe ~0.04", 0.02, 0.06),
    ("#11 status->RS (age-controlled)", "status_rs_r_partial", "von Rueden monogamous ~0.15", 0.10, 0.20),
    ("#12 rank-size slope", "village_zipf", "Zipf ~ -1.0", -1.5, -0.6),
    ("#13 primacy", "village_primate", "~1 (no primate centre)", 1.0, 2.0),
    ("#14 material Gini (adults)", "material_gini_adults", "BHM 2009 HG = 0.36", 0.30, 0.42),
    ("#14 material Gini (within-cell)", "material_gini_within_cell", "Agta within-camp mean 0.23 [0-0.44]", 0.0, 0.44),
    ("#17 fission ceiling (community max)", "settle_community_max", "Alberti 158 / Alvard <=250", None, 250),
    ("#9 hierarchy index (gini_cred)", "gini_cred", "[PRE-REGISTERED, Add.99] not itself anchored", None, None),
    ("stratification classifier", "pct_stratified", "the R-103 known-broken gate (context only)", None, None),
]


def sustained(traj, field, frac=0.15):
    n = len(traj)
    window = traj[-max(1, int(n * frac)):]
    vals = [r[field] for r in window if r.get(field) is not None and r.get(field) == r.get(field)]
    return vals


def main():
    data = {w: json.load(open(p))["traj"] for w, p in WORLDS.items()}
    for w, traj in data.items():
        print(f"{w}: {len(traj)} snapshot rows, final pop={traj[-1].get('pop')}, "
              f"final step={traj[-1].get('step')}")
    print()
    print(f"{'marker':42s} {'temperate':>16s} {'savanna':>16s} {'montane':>16s}   anchor")
    print("-" * 130)
    for label, field, anchor, lo, hi in MARKERS:
        cells = []
        for w in WORLDS:
            vals = sustained(data[w], field)
            if not vals:
                cells.append("n/a")
                continue
            m = st.mean(vals)
            se = (st.stdev(vals) / (len(vals) ** 0.5)) if len(vals) > 1 else 0.0
            hit = ""
            if lo is not None and hi is not None:
                hit = " OK" if lo <= m <= hi else " MISS"
            elif hi is not None:
                hit = " OK" if m <= hi else " MISS"
            elif lo is not None:
                hit = " OK" if m >= lo else " MISS"
            cells.append(f"{m:.3f}+/-{se:.3f}{hit}")
        print(f"{label:42s} {cells[0]:>16s} {cells[1]:>16s} {cells[2]:>16s}   {anchor}")

    print()
    print("=== genetics + dynasty long-run summary (final sustained window) ===")
    for w, traj in data.items():
        het = sustained(traj, "heterozygosity")
        rel = sustained(traj, "mean_relatedness")
        eff = sustained(traj, "eff_lineages")
        dom = sustained(traj, "dom_lineage_share")
        rs = sustained(traj, "dom_dyn_rs")
        print(f"  {w:10s}  het={st.mean(het):.3f}  mean_relatedness={st.mean(rel):.3f}  "
              f"eff_lineages={st.mean(eff):.1f}  dom_lineage_share={st.mean(dom):.3f}  dom_dyn_rs={st.mean(rs):.2f}")


if __name__ == "__main__":
    main()
