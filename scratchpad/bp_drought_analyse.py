"""Analyse the R-106 Add.117 drought test (bp_drought_run.py) against the paired canon runs (Stage-2 `riskvg` arm).

1. CONTROL: a drought run must equal its paired canon run row for row before the onset (driver = 1.0 = default).
2. CONTRACTION: population ratio drought / control over time; depth (minimum ratio), its step, recovery (first step
   after the drought ends at which the ratio is back to >= 0.95 and stays there for 10 rows).
3. HOW: per window (pre = 8000-9000, drought = 9000-9360, after = 9360-10360, late = 11000-12000), per year:
   deaths from the cumulative death counter, births = Δpop + Δdeaths (closed population), mean starvation deaths per
   logged step, land use, villages, mean reserve — drought arm vs control.
Writes drought_summary.json and the figure bp_drought.png.
"""
import json
import os
import statistics as st

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = r"C:\Users\syatom\Projects\SiC Games"
OUT = os.path.join(ROOT, "sic_games", "outputs", "substrate_run")
W = ["temperate", "savanna", "montane"]
MULTS = ["085", "070"]
ONSET, END = 9000, 9360
WIN = {"pre": (8000, 9000), "drought": (9000, 9360), "after": (9360, 10360), "late": (11000, 12000)}


def load(path):
    return json.load(open(path, encoding="utf-8"))["traj"]


def by_step(traj):
    return {r["step"]: r for r in traj}


def window_stats(tr, a, b):
    rows = [r for r in tr if a <= r["step"] <= b]
    if len(rows) < 2:
        return None
    r0, r1 = rows[0], rows[-1]
    yrs = (r1["step"] - r0["step"]) / 12.0
    dd = r1["lt_deaths_total"] - r0["lt_deaths_total"]
    dp = r1["pop"] - r0["pop"]
    mp = st.mean(r["pop"] for r in rows)
    return dict(pop=mp, deaths_py=dd / yrs / mp * 1000, births_py=(dp + dd) / yrs / mp * 1000,
                starv_step=st.mean(r.get("deaths_starv", 0) for r in rows),
                land_use=st.mean(r.get("spatial_land_use_frac", 0) for r in rows),
                villages=st.mean(r.get("n_villages", 0) for r in rows),
                reserve=st.mean(r.get("mean_reserve", 0) for r in rows))


summary = {}
fig, axes = plt.subplots(2, 3, figsize=(17, 8.5), sharex=True)
cols = {"ctl": "#4a6fa5", "085": "#e0a01f", "070": "#c0392b"}
for j, w in enumerate(W):
    ctl = {s: load(os.path.join(OUT, f"campaign_trajectory_s2_{w}_riskvg_s{s}.json")) for s in (0, 1, 2)}
    for m in MULTS:
        runs = {}
        for s in (0, 1, 2):
            p = os.path.join(OUT, f"campaign_trajectory_dr_{w}_m{m}_s{s}.json")
            if os.path.exists(p):
                runs[s] = load(p)
        if not runs:
            continue
        ctl_ok, ratios, rec = [], [], []
        for s, tr in runs.items():
            c = by_step(ctl[s])
            pre = [r for r in tr if r["step"] < ONSET]
            same = all(json.dumps(r, sort_keys=True) == json.dumps(c.get(r["step"]), sort_keys=True) for r in pre)
            ctl_ok.append(same)
            steps = [r["step"] for r in tr if r["step"] in c]
            ratio = np.array([by_step(tr)[t]["pop"] / c[t]["pop"] for t in steps])
            ratios.append((steps, ratio))
            after = [(t, r) for t, r in zip(steps, ratio) if t >= END]
            rt = None
            for i in range(len(after) - 10):
                if all(x >= 0.95 for _, x in after[i:i + 10]):
                    rt = after[i][0]
                    break
            rec.append(rt)
        mins = [(float(r.min()), st_[int(r.argmin())]) for st_, r in ratios]
        win = {k: {"drought": [window_stats(runs[s], *v) for s in runs], "control": [window_stats(ctl[s], *v) for s in runs]}
               for k, v in WIN.items()}
        summary[f"{w}|{m}"] = dict(control_identical_before_onset=ctl_ok, min_ratio=mins,
                                   recovery_step=rec, windows=win)
        # figure
        steps = ratios[0][0]
        mean_ratio = np.mean([r for _, r in ratios], axis=0)
        axes[1, j].plot(steps, mean_ratio, color=cols[m], lw=1.6, label=f"yield ×0.{m[1:]}")
        mean_pop = np.mean([[by_step(runs[s])[t]["pop"] for t in steps] for s in runs], axis=0)
        axes[0, j].plot(steps, mean_pop, color=cols[m], lw=1.4, label=f"drought: yield ×0.{m[1:]}")
    steps_c = [r["step"] for r in ctl[0] if r["step"] <= 12000]
    mean_c = np.mean([[by_step(ctl[s])[t]["pop"] for t in steps_c] for s in ctl], axis=0)
    axes[0, j].plot(steps_c, mean_c, color=cols["ctl"], lw=1.4, label="canon (no drought)")
    for ax in axes[:, j]:
        ax.axvspan(ONSET, END, color="#999999", alpha=0.25, zorder=0)
        ax.set_xlim(7000, 12000)
        ax.grid(alpha=0.3)
    axes[0, j].set_title(f"{w}: population (mean of 3 paired seeds)", fontsize=10)
    axes[1, j].axhline(1.0, color="#333333", lw=0.8)
    axes[1, j].axhline(0.95, color="#333333", lw=0.6, ls=":")
    axes[1, j].set_title(f"{w}: population, drought ÷ paired control", fontsize=10)
    axes[1, j].set_xlabel("step (month); grey = the 30-year drought")
axes[0, 0].legend(fontsize=8)
axes[1, 0].legend(fontsize=8)
fig.suptitle("R-106 Add.117 — drought test on the canon: all cell yields ×0.85 or ×0.70 for 30 years (steps 9000–9360), "
             "then normal; paired against the canon runs of the same seeds", fontsize=10)
fig.tight_layout(rect=(0, 0, 1, 0.95))
fig.savefig(os.path.join(ROOT, "scratchpad", "bp_drought.png"), dpi=105)
json.dump(summary, open(os.path.join(ROOT, "scratchpad", "drought_summary.json"), "w", encoding="utf-8"), indent=1,
          default=str)
for k, v in summary.items():
    print(f"\n== {k}: control identical before onset: {v['control_identical_before_onset']}")
    print("   min ratio (value, step):", [(round(a, 3), b) for a, b in v["min_ratio"]], "  recovery step:", v["recovery_step"])
    for wn in WIN:
        d = [x for x in v["windows"][wn]["drought"] if x]
        c = [x for x in v["windows"][wn]["control"] if x]
        if not d:
            continue
        f = lambda xs, key: st.mean(x[key] for x in xs)
        print(f"   {wn:8s} pop {f(d,'pop'):7.0f} vs {f(c,'pop'):7.0f} | deaths/1000/yr {f(d,'deaths_py'):5.1f} vs {f(c,'deaths_py'):5.1f}"
              f" | births/1000/yr {f(d,'births_py'):5.1f} vs {f(c,'births_py'):5.1f} | starv/step {f(d,'starv_step'):5.1f} vs {f(c,'starv_step'):5.1f}"
              f" | land {f(d,'land_use'):.3f} vs {f(c,'land_use'):.3f} | villages {f(d,'villages'):4.1f} vs {f(c,'villages'):4.1f}")
print("\nwrote scratchpad/bp_drought.png and drought_summary.json")
