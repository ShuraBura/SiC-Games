"""Plot the spatial state of a finished run: TERRAIN | PEOPLE | SETTLEMENTS, side by side.

    py -3 sic_games/outputs/substrate_run/plot_spatial.py fert_sedoff_s0 [claim_both ...]

Reads `campaign_spatial_<tag>.npz` (written by run_campaign at the end of every run) and emits
`campaign_spatial_<tag>.png`. One row per run, so arms stack for comparison.

WHY THE PANELS ARE WHAT THEY ARE. The question these maps exist to answer is not "how many people" -- every
aggregate already says that -- but "WHY are they standing there". So the terrain panel shows `forage_kcal`,
the quantity the movement rule actually reads, not a pretty biome map. Empty habitable land is drawn in a
colour that reads as ABSENCE rather than as low density, because the finding these maps illustrate is that
86% of the available land is unused (R-106, 2026-08-16).
"""
from __future__ import annotations

import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt          # noqa: E402
import numpy as np                        # noqa: E402
from matplotlib.colors import LogNorm, ListedColormap   # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
CELL_KM2 = 100.0
PACK = 0.091          # Binford 2001 packing threshold, persons/km²  [FILED]
PACK_PER_CELL = PACK * CELL_KM2          # = 9.1 people in a 100 km² cell


def _load(tag):
    p = os.path.join(HERE, f"campaign_spatial_{tag}.npz")
    if not os.path.exists(p):
        raise SystemExit(f"no spatial dump for '{tag}' at {p}\n"
                         f"Run the arm first — the dump is written at the end of a run.")
    return np.load(p)


def plot(tags, out=None):
    n = len(tags)
    fig, axes = plt.subplots(n, 3, figsize=(17.5, 6.2 * n), squeeze=False)
    for r, tag in enumerate(tags):
        d = _load(tag)
        people, sites = d["people"], d["sites"]
        forage, hab = d["forage_kcal"], d["habitable"]
        water = d["water"] if "water" in d.files else np.zeros_like(hab)
        step = int(d["step"])
        pop, occ = int(people.sum()), int((people > 0).sum())
        n_hab, n_sites = int(hab.sum()), int(sites.sum())

        # CROP to the capacity patch. The habitable land is a ~40x40 window inside a 100x100 grid (R-103i
        # circumscription), so an uncropped panel is 84% blank and the arrangement — the thing these maps
        # exist to show — is too small to read.
        hy, hx = np.nonzero(hab)
        m = 3
        y0, y1 = max(0, hy.min() - m), min(hab.shape[0], hy.max() + 1 + m)
        x0, x1 = max(0, hx.min() - m), min(hab.shape[1], hx.max() + 1 + m)
        crop = (slice(y0, y1), slice(x0, x1))
        ext = (x0, x1, y0, y1)

        # ── 1. TERRAIN: the return rate the movement rule reads, with water and non-patch land masked ──
        ax = axes[r][0]
        ax.imshow(np.zeros_like(hab[crop], dtype=float), cmap=ListedColormap(["#e8e8e8"]),
                  origin="lower", interpolation="nearest", extent=ext, vmin=0, vmax=1)
        show = np.where(hab > 0, forage, np.nan)[crop]
        im = ax.imshow(show, cmap="YlGn", origin="lower", interpolation="nearest", extent=ext)
        ax.imshow(np.where(water > 0, 1.0, np.nan)[crop], cmap=ListedColormap(["#9ecae1"]),
                  origin="lower", interpolation="nearest", extent=ext, vmin=0, vmax=1)
        plt.colorbar(im, ax=ax, fraction=0.046, label="forage kcal / forager-hr")
        ax.set_title(f"{tag}  —  TERRAIN\n{n_hab} habitable cells = {n_hab * CELL_KM2:,.0f} km²"
                     f"   (grey = outside capacity patch, blue = water)", fontsize=9)

        # ── 2. PEOPLE: log scale, because the whole point is a few cells hold everyone ──
        ax = axes[r][1]
        ax.imshow(np.where(hab > 0, 0.0, np.nan)[crop], cmap=ListedColormap(["#f0f0f0"]),
                  origin="lower", interpolation="nearest", extent=ext, vmin=0, vmax=1)
        pp = np.where(people > 0, people, np.nan)
        im = ax.imshow(pp[crop], cmap="inferno_r", origin="lower", interpolation="nearest",
                       extent=ext, norm=LogNorm(vmin=1, vmax=max(2, people.max())))
        plt.colorbar(im, ax=ax, fraction=0.046, label="people per 100 km² cell")
        land_use = occ / n_hab if n_hab else float("nan")
        local = pop / (occ * CELL_KM2) if occ else float("nan")
        regional = pop / (n_hab * CELL_KM2) if n_hab else float("nan")
        ax.set_title(f"PEOPLE  —  step {step}\npop {pop:,} on {occ}/{n_hab} cells "
                     f"({100 * land_use:.1f}% of the land)\n"
                     f"local {local:.3f}/km² vs regional {regional:.4f}/km²   "
                     f"(Binford packing {PACK})", fontsize=9)

        # ── 3. SETTLEMENTS over the same people field, so overlap is visible ──
        ax = axes[r][2]
        ax.imshow(np.where(hab > 0, 0.0, np.nan)[crop], cmap=ListedColormap(["#f0f0f0"]),
                  origin="lower", interpolation="nearest", extent=ext, vmin=0, vmax=1)
        ax.imshow(pp[crop], cmap="Greys", origin="lower", interpolation="nearest",
                  extent=ext, norm=LogNorm(vmin=1, vmax=max(2, people.max())), alpha=0.55)
        sy, sx = np.nonzero(sites)
        ax.scatter(sx + 0.5, sy + 0.5, s=14, facecolors="none", edgecolors="#d62728", linewidths=0.9,
                   label=f"{n_sites} settlement sites")
        # Alvard 50-250 bounds how many villages a population of this size can have -- no new anchor.
        lo, hi = pop / 250.0, pop / 50.0
        verdict = "OK" if lo <= n_sites <= hi else ("TOO MANY" if n_sites > hi else "too few")
        ax.legend(loc="upper right", fontsize=7, framealpha=0.85)
        ax.set_title(f"SETTLEMENTS  —  {n_sites} sites\n"
                     f"Alvard 50–250 allows {lo:.0f}–{hi:.0f} for pop {pop:,}  →  {verdict}\n"
                     f"each site persists on a 25-cell window ⇒ windows overlap", fontsize=9)

        for ax in axes[r]:
            ax.set_xticks([]); ax.set_yticks([])
    fig.tight_layout()
    out = out or os.path.join(HERE, f"campaign_spatial_{'_vs_'.join(tags)}.png")
    fig.savefig(out, dpi=125, bbox_inches="tight")
    print(f"wrote {out}")
    return out


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    plot(sys.argv[1:])
