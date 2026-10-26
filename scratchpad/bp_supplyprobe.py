"""R-106 Add.110 — the SAVANNA SUPPLY GAP: why do some families stay where the mother gathers ~half her need?

WHAT IS KNOWN (Add.107/108 probes, real pipeline). Savanna children who starve are on SPARSE cells (median 8 people)
holding NO stored food, and their mothers harvest ~0.48 of need, so the mothers have no overflow to give. Living
savanna children are on CROWDED cells (median 70) holding a GRANARY (~467 body-reserves). Even living savanna mothers
can gather only ~half their need from forage at the savanna rate; the granary tops them up. So in savanna, survival
looks conditional on standing on a GRANARY CELL — the granary is banked only on storage-eligible cells, drawn ONLY by
the agents standing on that exact cell, and sized by its current occupancy.

THE QUESTION: why are some families NOT on a granary cell? Candidates this probe separates:
  PINNED-NO-STORE  a village member standing on (or pinned to) a site whose cell holds no stored food yet — e.g. a
                   young daughter village (food-viable sites are now canon) founded going into a lean season
  PINNED-ELSEWHERE a village member not on its site cell (the pin moves one cell per step)
  MOBILE-SPARSE    not in any village: a mobile family the movement rule left on a sparse, store-less cell
  and for each, how far the nearest stocked granary is, and how old the family's village is.

MEASURED for the MOTHER of each juvenile starvation death, and for a same-schedule sample of mothers of LIVING
juveniles: in a village? on its site cell? village age; store on her cell (body-reserves per head); distance to the
nearest stocked granary and to the nearest site; her cell's forage RATE cap / her need; occupancy; her intake / need;
at cap. Observer only (class-level wrappers, private RNG). Runs the CURRENT canon (food-viable sites + fathers 0.5).
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

FROM = int(os.environ.get("SP_FROM", "3000"))
EVERY = int(os.environ.get("SP_EVERY", "25"))
NSAMP = int(os.environ.get("SP_NSAMP", "300"))
OUT = os.environ["SP_OUT"]
DEATHS, LIVING = [], []
BORN: dict = {}
_rng = random.Random(97531)
_c = {"step": -1}

_orig_note = TerrainWorld._note_starvation_state
_orig_step = TerrainWorld.step


def _tdist(mask):
    """Torus chessboard distance to the nearest True cell (3x3 tiling, centre tile). Observer only."""
    if not mask.any():
        return np.full(mask.shape, 999)
    h, wd = mask.shape
    big = np.tile(mask, (3, 3))
    return distance_transform_cdt(~big, metric="chessboard")[h:2 * h, wd:2 * wd]


def _near_site(w, pos):
    """Nearest active site within settle_radius (torus Chebyshev, insertion-order tie-break) — a private copy of
    _nearest_settlement, so the probe never builds the model's own per-step cache."""
    rad = w._demog.settle_radius
    n = w._fields.isWater.shape[0]
    best, bd = None, rad + 1
    for s in w._settlement_sites:
        dx = abs(s[0] - pos[0]); dx = min(dx, n - dx)
        dy = abs(s[1] - pos[1]); dy = min(dy, n - dy)
        d = max(dx, dy)
        if d < bd:
            best, bd = s, d
    return best


def _maps(w):
    if _c["step"] != w.step_count:
        shp = w._fields.isWater.shape
        g = np.zeros(shp, dtype=bool)
        thr = 0.1 * w._reserve_full
        for (x, y), v in w._cell_store.items():
            if v > thr:
                g[y, x] = True
        s = np.zeros(shp, dtype=bool)
        for (x, y) in w._settlement_sites:
            s[y, x] = True
        _c["gdist"] = _tdist(g)
        _c["sdist"] = _tdist(s)
        occ: dict = {}
        for a in w.agent_list:
            occ[a.pos] = occ.get(a.pos, 0) + 1
        _c["occ"] = occ
        _c["idx"] = {id(a): i for i, a in enumerate(w.agent_list)}
        _c["step"] = w.step_count
    return _c


def _mother_rec(w, child, at_death):
    m = child._mother
    if m is None or not m.alive:
        return None
    c = _maps(w)
    d = w._demog
    x, y = m.pos
    site = _near_site(w, m.pos)
    occ = c["occ"].get(m.pos, 1)
    mcap = w._reserve_full * m.reserve_scale()
    if at_death:
        post = m.wealth if c["idx"].get(id(m), 1 << 30) > c["idx"].get(id(child), -1) else float(getattr(m, "_fed_reserve", m.wealth))
    else:
        post = float(getattr(m, "_fed_reserve", m.wealth))
    mreq = w._burn * m.consumption_factor()
    fk = getattr(w._fields, "forage_kcal", None)
    return dict(
        step=w.step_count, child_age=round(child.age / 12.0, 2),
        village=site is not None, on_site=(site is not None and m.pos == site),
        village_age=(w.step_count - BORN.get(site, w.step_count)) if site is not None else None,
        site_store=round(w._cell_store.get(site, 0.0) / w._reserve_full, 2) if site is not None else None,
        store_ph=round(w._cell_store.get(m.pos, 0.0) / w._reserve_full / max(occ, 1), 3),
        gdist=int(c["gdist"][y, x]), sdist=int(c["sdist"][y, x]),
        ratecap=round(float(fk[y, x]) * d.forage_cap_hours / mreq, 3) if (fk is not None and mreq > 0) else None,
        occ=int(occ),
        m_intake=round(m._last_intake / mreq, 3) if mreq > 0 else 0.0,
        m_at_cap=bool(post >= 0.999 * mcap))


def _note(self, a, occ_count, age_i):
    if self.step_count >= FROM and a.is_juvenile():
        r = _mother_rec(self, a, True)
        if r is not None:
            DEATHS.append(r)
    return _orig_note(self, a, occ_count, age_i)


def _step(self, *a, **k):
    before = set(self._settlement_sites)
    r = _orig_step(self, *a, **k)
    for s in set(self._settlement_sites) - before:
        BORN[s] = self.step_count
    for s in before - set(self._settlement_sites):
        BORN.pop(s, None)
    if self.step_count >= FROM and self.step_count % EVERY == 0:
        juv = [g for g in self.agent_list if g.is_juvenile() and g._mother is not None and g._mother.alive]
        pick = juv if len(juv) <= NSAMP else _rng.sample(juv, NSAMP)
        for g in pick:
            rec = _mother_rec(self, g, False)
            if rec is not None:
                LIVING.append(rec)
    return r


TerrainWorld._note_starvation_state = _note
TerrainWorld.step = _step
try:
    runpy.run_path(os.path.join(ROOT, "sic_games", "outputs", "substrate_run", "run_campaign.py"), run_name="__main__")
finally:
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(dict(deaths=DEATHS, living=LIVING, from_step=FROM), fh)
    print(f"SUPPLYPROBE wrote {len(DEATHS)} child deaths with a living mother, {len(LIVING)} living -> {OUT}", flush=True)
