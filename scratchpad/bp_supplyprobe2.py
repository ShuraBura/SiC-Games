"""R-106 Add.110 probe 2 — WHY is the starving child's mother off the stocked cell? Pinned, released, or blind?

Probe 1 found: on all three worlds the starving child's mother stands on a cell with NO stored food, with stored
food at most ONE cell away (usually the village site). In canon a village member inside settle_radius (2) is PINNED:
each step it moves one cell toward the site. Mothers are family ROOTS (they move themselves). So a mother who stays
off the site must be RELEASED from the pin — by emergent abandonment (p = abandon_hardship_gain x the site's
remembered hardship) or by settlement scalar stress (p = size_repulsion(village pop)). A released member runs the
ordinary IFD choice, which values a cell's store ONLY if the member's band is present there (substrate.py:280), while
the granary DRAW does not check band membership.

Recorded per mother (child death / same-schedule living sample), all observer-only (no RNG draw, no model cache):
  branch     'ifd' if diffusion_select_target ran for her this step, else 'pinned' (or 'none' = no site in reach)
  p_ab, p_ss the two release probabilities for her site, from the model's own state and formula
  ifd_to_stock  a released mother's chosen cell holds stored food
  stock_nbr     a stocked cell within 1 (Chebyshev) of her; band_on_stock: her band is present on one of them
  site_stock    her site cell holds stored food; band_on_site: her band is present on the site cell
"""
import json
import os
import random
import runpy
import sys

ROOT = r"C:\Users\syatom\Projects\SiC Games"
sys.path.insert(0, os.path.join(ROOT, "sic_games", "src"))
import sic_games.phase1_model as PM   # noqa: E402
from sic_games.phase1_model import TerrainWorld   # noqa: E402

FROM = int(os.environ.get("SP_FROM", "3000"))
EVERY = int(os.environ.get("SP_EVERY", "25"))
NSAMP = int(os.environ.get("SP_NSAMP", "300"))
OUT = os.environ["SP_OUT"]
DEATHS, LIVING = [], []
IFD: dict = {}          # id(agent) -> chosen target, THIS step
_rng = random.Random(97531)
_c = {"step": -1}

_orig_note = TerrainWorld._note_starvation_state
_orig_step = TerrainWorld.step
_orig_dst = PM.diffusion_select_target


def _dst(agent, *a, **k):
    t = _orig_dst(agent, *a, **k)
    IFD[id(agent)] = t
    return t


def _near_site(w, pos):
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
        cells_by_band: dict = {}
        occ: dict = {}
        for a in w.agent_list:
            cells_by_band.setdefault(a._group.band_id, set()).add(a.pos)
            occ[a.pos] = occ.get(a.pos, 0) + 1
        vpop: dict = {}
        for a in w.agent_list:
            s = _near_site(w, a.pos)
            if s is not None:
                vpop[s] = vpop.get(s, 0) + 1
        _c.update(step=w.step_count, bands=cells_by_band, occ=occ, vpop=vpop,
                  idx={id(a): i for i, a in enumerate(w.agent_list)})
    return _c


def _stocked(w, cell):
    return w._cell_store.get(cell, 0.0) > 0.01 * w._reserve_full


def _mother_rec(w, child):
    m = child._mother
    if m is None or not m.alive:
        return None
    c = _maps(w)
    d = w._demog
    n = w._fields.isWater.shape[0]
    x, y = m.pos
    home = c["bands"].get(m._group.band_id, set())
    site = _near_site(w, m.pos)
    p_ab = p_ss = 0.0
    if site is not None:
        if getattr(d, "enable_emergent_abandonment", False):
            p_ab = min(1.0, max(0.0, d.abandon_hardship_gain * w._settlement_hardship.get(site, 0.0)))
        if getattr(d, "enable_settlement_scalar_stress", False):
            soc = w._cell_society.get(site) or w._band_society.get(m._group.band_id)
            p_ss = PM.size_repulsion(c["vpop"].get(site, 0), d.settlement_ss_gain, d.settlement_ss_midpoint,
                                     d.settlement_ss_width, soc)
    nbrs = [((x + dx) % n, (y + dy) % n) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if (dx or dy)]
    snb = [q for q in nbrs if _stocked(w, q)]
    tgt = IFD.get(id(m))
    mreq = w._burn * m.consumption_factor()
    return dict(
        village=site is not None, on_site=(site is not None and m.pos == site),
        branch=("ifd" if tgt is not None else ("pinned" if site is not None else "none")),
        p_ab=round(p_ab, 3), p_ss=round(float(p_ss), 3),
        ifd_to_stock=(bool(_stocked(w, tgt)) if tgt is not None else None),
        own_stock=bool(_stocked(w, m.pos)),
        stock_nbr=bool(snb), band_on_stock=any(q in home for q in snb),
        site_stock=(bool(_stocked(w, site)) if site is not None else None),
        band_on_site=(site in home if site is not None else None),
        occ=int(c["occ"].get(m.pos, 1)),
        m_intake=round(m._last_intake / mreq, 3) if mreq > 0 else 0.0)


def _note(self, a, occ_count, age_i):
    if self.step_count >= FROM and a.is_juvenile():
        r = _mother_rec(self, a)
        if r is not None:
            DEATHS.append(r)
    return _orig_note(self, a, occ_count, age_i)


def _step(self, *a, **k):
    IFD.clear()
    r = _orig_step(self, *a, **k)
    if self.step_count >= FROM and self.step_count % EVERY == 0:
        juv = [g for g in self.agent_list if g.is_juvenile() and g._mother is not None and g._mother.alive]
        pick = juv if len(juv) <= NSAMP else _rng.sample(juv, NSAMP)
        for g in pick:
            rec = _mother_rec(self, g)
            if rec is not None:
                LIVING.append(rec)
    return r


PM.diffusion_select_target = _dst
TerrainWorld._note_starvation_state = _note
TerrainWorld.step = _step
try:
    runpy.run_path(os.path.join(ROOT, "sic_games", "outputs", "substrate_run", "run_campaign.py"), run_name="__main__")
finally:
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(dict(deaths=DEATHS, living=LIVING, from_step=FROM), fh)
    print(f"SUPPLYPROBE2 wrote {len(DEATHS)} deaths, {len(LIVING)} living -> {OUT}", flush=True)
