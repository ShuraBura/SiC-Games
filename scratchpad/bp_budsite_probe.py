"""R-106 Add.107 part 2 — does colonizing budding found daughter villages OFF THE FOOD PATCH?

FROM THE PER-DEATH PROBE: in temperate and montane the starving die on cells whose food per head is EXACTLY 0,
in small groups, mostly without a family head. Capacity is ZERO outside the patch (`capacity.py`: E[~mask] = 0)
and depletion cannot reach zero (stock clipped at B_FLOOR = 0.05), so food == 0 means OFF THE PATCH, not
eaten bare. The founding rule reads `_founding_pot_field()` = S_pot x storable >= settle_persist_threshold and
NEVER the harvest field — and S_pot is non-zero over far more land than the food patch.

HYPOTHESIS: buds found daughters off the patch; the emigrants arrive with no forage, no granary and ~0.5 month of
body reserve, and starve. Also a second cause of the Add.105 settlement churn.

RECORDED (class-level observers, private RNG, no model state written):
  every BUD SITE   (new sites created inside `_maintain_village_budding`): on/off patch, founded step, lifetime
  every OTHER new site (occupancy founding etc.): same, for contrast
  every STARVATION DEATH: on/off patch, whether its nearest settlement is a bud site and its age, Chebyshev distance
                          to the patch and to the nearest stocked granary
  a LIVING sample on the same fields, same schedule
"""
import json
import os
import random
import runpy
import sys

import numpy as np
from scipy.ndimage import distance_transform_cdt

ROOT = r"C:\Users\syatom\Projects\SiC Games"
sys.path.insert(0, os.path.join(ROOT, "sic_games", "src"))
from sic_games.phase1_model import TerrainWorld   # noqa: E402

FROM = int(os.environ.get("BP_FROM", "3000"))
EVERY = int(os.environ.get("BP_EVERY", "25"))
NSAMP = int(os.environ.get("BP_NSAMP", "200"))
OUT = os.environ["BP_OUT"]

SITES: dict = {}          # site -> {born, bud, on_patch, died}
DEATHS: list = []
LIVING: list = []
_rng = random.Random(24680)
_cache = {"step": -1, "gdist": None, "pdist": None, "patch": None}

_orig_bud = TerrainWorld._maintain_village_budding
_orig_note = TerrainWorld._note_starvation_state
_orig_step = TerrainWorld.step


def _patch_mask(w):
    if _cache["patch"] is None:
        base = getattr(w._harvest_field, "_base", w._harvest_field)
        E = getattr(base, "_base_E", None)
        if E is None:
            E = getattr(base, "_E")
        _cache["patch"] = np.asarray(E) > 0.0
        # Chebyshev distance to the nearest ON-PATCH cell (0 on the patch)
        _cache["pdist"] = distance_transform_cdt(~_cache["patch"], metric="chessboard")
    return _cache["patch"]


def _granary_dist(w):
    if _cache["step"] != w.step_count:
        g = np.zeros_like(_patch_mask(w), dtype=bool)
        thr = 0.1 * w._reserve_full
        for (x, y), v in w._cell_store.items():
            if v > thr:
                g[y, x] = True
        _cache["gdist"] = (distance_transform_cdt(~g, metric="chessboard") if g.any()
                           else np.full(g.shape, 999, dtype=int))
        _cache["step"] = w.step_count
    return _cache["gdist"]


def _bud(self, *a, **k):
    before = set(self._settlement_sites)
    r = _orig_bud(self, *a, **k)
    pm = _patch_mask(self)
    for s in set(self._settlement_sites) - before:
        SITES[s] = dict(born=self.step_count, bud=True, on_patch=bool(pm[s[1], s[0]]), died=None)
    return r


def _rec(w, a, occ):
    pm = _patch_mask(w)
    x, y = a.pos
    ns = w._nearest_settlement(a.pos)
    info = SITES.get(ns) if ns is not None else None
    return dict(step=w.step_count, juv=bool(a.is_juvenile()),
                on_patch=bool(pm[y, x]), patch_dist=int(_cache["pdist"][y, x]),
                granary_dist=int(_granary_dist(w)[y, x]),
                village=ns is not None,
                in_bud_village=bool(info and info["bud"]),
                bud_village_on_patch=(info["on_patch"] if info and info["bud"] else None),
                village_age=((w.step_count - info["born"]) if info else None),
                occ=int(occ))


def _note(self, a, occ_count, age_i):
    if self.step_count >= FROM:
        DEATHS.append(_rec(self, a, occ_count.get(a.pos, 1)))
    return _orig_note(self, a, occ_count, age_i)


def _step(self, *a, **k):
    before = set(self._settlement_sites)
    r = _orig_step(self, *a, **k)
    after = set(self._settlement_sites)
    pm = _patch_mask(self)
    for s in after - before:                       # founded by any path; buds were already tagged
        SITES.setdefault(s, dict(born=self.step_count, bud=False, on_patch=bool(pm[s[1], s[0]]), died=None))
    for s in before - after:
        if s in SITES and SITES[s]["died"] is None:
            SITES[s]["died"] = self.step_count
    if self.step_count >= FROM and self.step_count % EVERY == 0 and self.agent_list:
        occ: dict = {}
        for ag in self.agent_list:
            occ[ag.pos] = occ.get(ag.pos, 0) + 1
        pick = self.agent_list if len(self.agent_list) <= NSAMP else _rng.sample(self.agent_list, NSAMP)
        for ag in pick:
            LIVING.append(_rec(self, ag, occ[ag.pos]))
    return r


TerrainWorld._maintain_village_budding = _bud
TerrainWorld._note_starvation_state = _note
TerrainWorld.step = _step
try:
    runpy.run_path(os.path.join(ROOT, "sic_games", "outputs", "substrate_run", "run_campaign.py"),
                   run_name="__main__")
finally:
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(dict(sites=[dict(site=list(k), **v) for k, v in SITES.items()],
                       deaths=DEATHS, living=LIVING, from_step=FROM,
                       patch_cells=int(_cache["patch"].sum()) if _cache["patch"] is not None else None), fh)
    print(f"BUDPROBE wrote {len(SITES)} sites, {len(DEATHS)} deaths, {len(LIVING)} living -> {OUT}", flush=True)
