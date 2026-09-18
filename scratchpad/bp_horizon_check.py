"""R-106 Addendum 101 — THE DECISIVE TEST for the Add.100 divergences.

Every Add.86-99 conclusion was measured on an 800-step probe. Add.100's full 15000-step campaign disagrees on
#11 (status->RS) and #17 (fission ceiling). Two candidate causes: (a) the probe HARNESS differs from the real
campaign, or (b) the probe HORIZON (800 steps = 67 yr) caught a transient that had not equilibrated.

These are separable. Read the CAMPAIGN's own trajectory AT step ~800 and compare it to the probe's published
number. Same pipeline, same config, same horizon => any remaining gap is harness; agreement at 800 with
divergence later => the probe measured a transient, and the horizon is the whole story.

Reports, per world and per marker: value at step ~800, the sustained late value, and the published probe value.
"""
import json
import statistics as st

WORLDS = {
    "temperate": "sic_games/outputs/substrate_run/campaign_trajectory_scorecard99_temperate.json",
    "savanna":   "sic_games/outputs/substrate_run/campaign_trajectory_scorecard99_savanna.json",
    "montane":   "sic_games/outputs/substrate_run/campaign_trajectory_scorecard99_montane.json",
}

# marker -> (field, {world: published 800-step probe value}, source addendum)
PROBE = {
    "#11 status->RS (age-ctrl)": ("status_rs_r_partial", {"temperate": 0.157, "savanna": 0.143}, "Add.94"),
    "#17 community max":         ("settle_community_max", {"temperate": 155.0, "savanna": 200.0}, "Add.93"),
    "#1 band experienced adults": ("band_experienced_adults", {"temperate": 33.3, "savanna": 22.9}, "Add.91/93"),
    "#3 village median":          ("village_med", {"temperate": 44.0, "savanna": 74.0}, "Add.95"),
    "#14 material gini adults":   ("material_gini_adults", {"temperate": 0.386, "savanna": 0.357}, "Add.92"),
    "#14 within-cell gini":       ("material_gini_within_cell", {"temperate": 0.28, "savanna": 0.26}, "Add.98"),
    "#10 polygyny (all men)":     ("frac_polygynous_all_m", {"temperate": 0.022, "savanna": 0.029}, "Add.91"),
    "#9 gini_cred":               ("gini_cred", {}, "-"),
    "pop":                        ("pop", {}, "-"),
}


def at_step(traj, field, target=800, tol=40):
    """Mean of rows whose step is within tol of target (the probe's horizon)."""
    vals = [r[field] for r in traj
            if abs(r.get("step", -1) - target) <= tol and r.get(field) is not None and r.get(field) == r.get(field)]
    return st.mean(vals) if vals else None


def sustained(traj, field, frac=0.15):
    n = len(traj)
    w = traj[-max(1, int(n * frac)):]
    vals = [r[field] for r in w if r.get(field) is not None and r.get(field) == r.get(field)]
    return st.mean(vals) if vals else None


def main():
    data = {w: json.load(open(p))["traj"] for w, p in WORLDS.items()}
    print("Campaign trajectory read AT the probe's horizon (step ~800) vs LATE (sustained window).")
    print("If campaign@800 ~= probe, the harness agrees and the HORIZON explains the divergence.\n")
    for label, (field, probe_vals, src) in PROBE.items():
        print(f"{label}   [{field}]  (probe source: {src})")
        for w in WORLDS:
            a800 = at_step(data[w], field)
            late = sustained(data[w], field)
            pv = probe_vals.get(w)
            def f(x):
                return "n/a" if x is None else f"{x:.3f}"
            note = ""
            if pv is not None and a800 is not None:
                d = abs(a800 - pv) / max(abs(pv), 1e-9)
                note = f"   probe={pv:.3f}  |campaign@800-probe|={d*100:.0f}%"
            print(f"    {w:10s} @800={f(a800):>8s}   late={f(late):>8s}{note}")
        print()


if __name__ == "__main__":
    main()
