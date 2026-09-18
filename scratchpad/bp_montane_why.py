"""R-106 Addendum 104 — why does MONTANE carry the largest villages (village_max 288, over Alvard's 250)?

Two rival explanations, which predict different things:
  (A) GOOD SPOT / POOR ALTERNATIVES. Mountain terrain makes forage PATCHY: a few rich valleys among poor slope,
      so people concentrate because nowhere else is worth going. Predicts: high forage inequality, occupied cells
      much richer than unoccupied, and FEW attractive empty cells.
  (B) MOVEMENT FRICTION. Alternatives are fine but mountains cost ~6.7x to cross, so people cannot spread.
      Predicts: plenty of GOOD EMPTY habitable land sitting unused.

Both read off the canonical spatial dumps (occupancy + forage on one grid, end of the 15000-step runs).
"""
import numpy as np

W = ["temperate", "savanna", "montane"]


def gini(v):
    v = np.sort(np.asarray(v, float))
    n = len(v)
    if n == 0 or v.sum() <= 0:
        return 0.0
    return (2.0 * np.sum((np.arange(1, n + 1)) * v)) / (n * v.sum()) - (n + 1.0) / n


rows = {}
for w in W:
    d = np.load(f"sic_games/outputs/substrate_run/campaign_spatial_scorecard99_{w}.npz")
    hab = d["habitable"].astype(bool) & (~d["water"].astype(bool))
    ppl = d["people"]
    forage = d["forage_kcal"]
    occ = hab & (ppl > 0)
    emp = hab & (ppl == 0)

    f_hab = forage[hab]
    f_occ = forage[occ]
    f_emp = forage[emp]
    # "attractive empty" = empty habitable cells at least as rich as the MEDIAN OCCUPIED cell
    thr = np.median(f_occ) if f_occ.size else 0.0
    good_empty = int(np.sum(f_emp >= thr))
    # the biggest single occupied cell, and where its forage sits in the habitable distribution
    iy, ix = np.unravel_index(np.argmax(ppl), ppl.shape)
    pct_of_top = float((f_hab < forage[iy, ix]).mean() * 100.0)

    rows[w] = dict(
        hab=int(hab.sum()), occ=int(occ.sum()), pop=int(ppl.sum()),
        land_use=100.0 * occ.sum() / max(hab.sum(), 1),
        f_gini=gini(f_hab), f_top10=float(np.sort(f_hab)[::-1][:max(1, len(f_hab)//10)].sum() / max(f_hab.sum(), 1e-9)),
        f_mean_hab=float(f_hab.mean()), f_mean_occ=float(f_occ.mean()) if f_occ.size else 0.0,
        f_mean_emp=float(f_emp.mean()) if f_emp.size else 0.0,
        ratio=float(f_occ.mean() / f_emp.mean()) if f_emp.size and f_emp.mean() > 0 else float("nan"),
        good_empty=good_empty, good_empty_frac=100.0 * good_empty / max(int(emp.sum()), 1),
        unused_forage=100.0 * f_emp.sum() / max(f_hab.sum(), 1e-9),
        max_cell=int(ppl.max()), max_cell_forage_pct=pct_of_top)

print(f"{'metric':42s}" + "".join(f"{w:>13s}" for w in W))
print("-" * 82)
FMT = [
    ("habitable cells", "hab", "{:.0f}"),
    ("occupied cells", "occ", "{:.0f}"),
    ("land use %", "land_use", "{:.1f}"),
    ("", None, None),
    ("FORAGE PATCHINESS (hypothesis A)", None, None),
    ("  forage Gini over habitable", "f_gini", "{:.3f}"),
    ("  top-10% cells hold % of forage", "f_top10", "{:.1%}"),
    ("", None, None),
    ("IS THE OCCUPIED SPOT BETTER?", None, None),
    ("  mean forage, OCCUPIED cells", "f_mean_occ", "{:.0f}"),
    ("  mean forage, EMPTY habitable", "f_mean_emp", "{:.0f}"),
    ("  ratio occupied / empty", "ratio", "{:.2f}x"),
    ("", None, None),
    ("ARE THERE GOOD ALTERNATIVES? (B)", None, None),
    ("  empty cells >= median occupied", "good_empty", "{:.0f}"),
    ("  ...as % of all empty habitable", "good_empty_frac", "{:.1f}%"),
    ("  % of habitable forage left UNUSED", "unused_forage", "{:.1f}%"),
    ("", None, None),
    ("  largest single cell (people)", "max_cell", "{:.0f}"),
    ("  its forage percentile", "max_cell_forage_pct", "{:.0f}th"),
]
for label, key, fmt in FMT:
    if key is None:
        print(label)
        continue
    print(f"{label:42s}" + "".join(f"{fmt.format(rows[w][key]):>13s}" for w in W))
