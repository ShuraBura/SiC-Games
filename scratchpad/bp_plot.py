"""Plot the R-106 savanna band-provisioning diagnosis from the 3x3 low-noise panel.

Finding (9 cells/biome, canon, biome_seasonality ON, 600 agents, steps 400-800):
  Band provisioning is ZERO-SUM on total starvation hazard in BOTH biomes (temperate delta +0.01+/-0.07,
  savanna -0.00+/-0.14 per 1000 person-months). It does NOT reduce death; it RELOCATES it from children to
  adults everywhere (age +5.9+/-2.4y temperate z=2.4; +8.2+/-0.6y savanna z=12.8). Savanna is not special in
  the mechanism -- it is special in its baseline hazard (2.6x temperate) and near-ceiling band budget
  (surplus/deficit 40 vs 97; 4x more needy group-obs; dependency 1.20 vs 0.70). The donor-flow hypothesis is
  falsified (savanna donors LESS short at donation, 12.5% vs 44%). The e0 gain temperate showed in Addendum 75
  is the age-shift raising e0 where the death flux is small; savanna's 2.6x flux cancels it. It is the
  distributional Malthusian relocation law, not a defect in the provisioning rule.

Per-cell OFF/ON values are parsed from bp_probe_panel.log; group-level arrays from bp_arr_<clim>.npz.
"""
import os
import re
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SP = os.path.dirname(os.path.abspath(__file__))
COL = {"temperate": "#1f77b4", "savanna": "#d95f02"}
LINE = re.compile(r"(\w+) w\d+a\d+: OFF pop \d+ haz ([\d.]+)/kpm age ([\d.]+)y \| "
                  r"ON pop \d+ haz ([\d.]+)/kpm age ([\d.]+)y")
# per-biome group-level scalars from the panel log (surplus/deficit ratio, needy group-obs, dependency)
HEAD = {"temperate": dict(sd=97.4, groups=433, dep=0.70),
        "savanna":   dict(sd=40.3, groups=1711, dep=1.20)}


def parse_cells(clim):
    off_h, on_h, off_a, on_a = [], [], [], []
    for ln in open(os.path.join(SP, "bp_probe_panel.log"), encoding="utf-8"):
        m = LINE.match(ln.strip())
        if m and m.group(1) == clim:
            off_h.append(float(m.group(2))); off_a.append(float(m.group(3)))
            on_h.append(float(m.group(4))); on_a.append(float(m.group(5)))
    return map(np.array, (off_h, on_h, off_a, on_a))


def mse(v):
    return v.mean(), v.std(ddof=1) / np.sqrt(len(v))


def main():
    biomes = ["temperate", "savanna"]
    cells = {b: parse_cells(b) for b in biomes}
    cells = {b: list(v) for b, v in cells.items()}
    arr = {b: dict(np.load(os.path.join(SP, f"bp_arr_{b}.npz"))) for b in biomes}
    x = np.arange(len(biomes))

    fig, ax = plt.subplots(2, 2, figsize=(12.5, 9))
    fig.suptitle("R-106 — band provisioning RELOCATES starvation child->adult (zero-sum on hazard, BOTH biomes); "
                 "it does not reduce it\n"
                 "(canon, biome_seasonality ON, 600 agents, steps 400-800, 3-world x 3-replicate low-noise panel, "
                 "mean +/- SE over 9 cells)", fontsize=10.5, fontweight="bold")

    # (a) HAZARD OFF vs ON, per biome, with SE. The correction: FLAT in both -> zero-sum.
    a = ax[0, 0]
    for i, b in enumerate(biomes):
        off_h, on_h, off_a, on_a = cells[b]
        mo, so = mse(off_h); mn, sn = mse(on_h)
        a.bar(i - 0.18, mo, width=0.36, yerr=so, capsize=4, color="#999999", label="OFF" if i == 0 else None)
        a.bar(i + 0.18, mn, width=0.36, yerr=sn, capsize=4, color=COL[b], label="ON" if i == 0 else None)
        d = on_h - off_h
        a.text(i, 0.30, f"delta {d.mean():+.2f}+/-{d.std(ddof=1)/np.sqrt(len(d)):.2f}\n"
               f"(z={d.mean()/(d.std(ddof=1)/np.sqrt(len(d))):.1f}, n.s.)", ha="center", fontsize=8.5)
    a.set_xticks(x); a.set_xticklabels(biomes)
    a.set_ylabel("starvation hazard /1000 person-months")
    a.set_ylim(0, 2.15)
    a.set_title("(a) total starvation is NOT reduced in either biome (zero-sum)", fontsize=9.5)
    a.legend(fontsize=8, loc="upper left")

    # (b) AGE OFF vs ON, per biome, with SE. Both rise -> relocation child->adult.
    a = ax[0, 1]
    for i, b in enumerate(biomes):
        off_h, on_h, off_a, on_a = cells[b]
        mo, so = mse(off_a); mn, sn = mse(on_a)
        a.bar(i - 0.18, mo, width=0.36, yerr=so, capsize=4, color="#999999")
        a.bar(i + 0.18, mn, width=0.36, yerr=sn, capsize=4, color=COL[b])
        d = on_a - off_a
        z = d.mean() / (d.std(ddof=1) / np.sqrt(len(d)))
        a.text(i + 0.18, mn / 2, f"+{d.mean():.1f}y\n(z={z:.0f})", ha="center", fontsize=8.5,
               color="white", fontweight="bold")
    a.set_ylim(0, 28)
    a.axhline(15, color="k", lw=0.8, ls=":")
    a.text(1.42, 15.4, "age 15 (child/adult)", fontsize=7.5, ha="right")
    a.set_xticks(x); a.set_xticklabels(biomes)
    a.set_ylabel("mean age of starvation deaths (yr)")
    a.set_title("(b) starvation moves from children to adults (both biomes)", fontsize=9.5)

    # (c) WHY savanna's relocation cannot help e0: higher baseline hazard AND lower band headroom.
    a = ax[1, 0]
    haz0 = [mse(cells[b][0])[0] for b in biomes]
    a.bar(x - 0.18, haz0, width=0.36, color=[COL[b] for b in biomes], alpha=0.55, label="baseline hazard /kpm")
    for i, b in enumerate(biomes):
        a.text(i - 0.18, haz0[i] + 0.03, f"{haz0[i]:.2f}", ha="center", fontsize=8.5)
    a2 = a.twinx()
    sd = [HEAD[b]["sd"] for b in biomes]
    a2.bar(x + 0.18, sd, width=0.36, color=[COL[b] for b in biomes], label="surplus/deficit")
    for i, b in enumerate(biomes):
        a2.text(i + 0.18, sd[i] + 2, f"{sd[i]:.0f}x\n({HEAD[b]['groups']} obs)", ha="center", fontsize=8)
    a.set_xticks(x); a.set_xticklabels(biomes)
    a.set_ylabel("baseline starvation hazard /1000 pm"); a2.set_ylabel("band donatable surplus / juv deficit")
    a.set_title("(c) savanna: 2.6x higher death flux + lower band headroom", fontsize=9.5)
    a.set_ylim(0, 2.2); a2.set_ylim(0, 120)

    # (d) dependency ratio of needy groups.
    a = ax[1, 1]
    for b in biomes:
        d = arr[b]
        dep = d["n_juv"] / np.maximum(d["n_adult"], 1)
        a.hist(dep, bins=np.linspace(0, 3, 31), alpha=0.5, color=COL[b], density=True,
               label=f"{b}  mean {HEAD[b]['dep']:.2f}")
    a.axvline(1.0, color="k", lw=0.8, ls=":")
    a.text(1.03, a.get_ylim()[1] * 0.9, "1 juvenile per adult", fontsize=7.5)
    a.set_xlabel("juveniles per adult in the food-sharing group")
    a.set_ylabel("density")
    a.set_title("(d) needy groups: savanna carries more dependents per donor", fontsize=9.5)
    a.legend(fontsize=8)

    fig.tight_layout(rect=(0, 0, 1, 0.93))
    out = os.path.join(SP, "bp_savanna_diagnosis.png")
    fig.savefig(out, dpi=130)
    print("wrote", out)


if __name__ == "__main__":
    main()
