"""R-106 Add.108 — WHY DO CHILDREN STARVE BESIDE THEIR MOTHERS ON FOOD-RICH CELLS? (savanna / montane)

FROM THE PER-DEATH PROBE: in savanna the starving are children (median age 7), 73% with the mother on the same cell,
on cells holding 2.0x need per head, with intake 0.08x. Provisioning (phase1_model, "Mother-linked provisioning") has
three tiers after the child's own small foraging share:
    tier 1  the mother's harvest OVERFLOW (what she brings in beyond topping up her own reserve cap)
    tier 2  the mother's reserve above `provision_self_keep` x cap   — canon provision_self_keep = 1.0 => OFF
    tier 3  paternal_provision_frac x the father's overflow          — canon paternal_provision_frac = 0.0 => OFF
and `enable_band_provisioning` is OFF (Add.75, not adopted). PARAMETERS.md records provision_self_keep 1.0 as
"OPEN / KEPT ... band-level supersedes" — left at 1.0 because band provisioning was to replace it, which never
happened. So a child is fed ONLY from the mother's overflow.

HYPOTHESIS: mothers of starving children have NO overflow (their post-provisioning reserve is below the cap, so
tier 1 gave nothing) while holding a reserve they do not share (tier 2 off). A contributing cause would be the forage
RATE cap (intake <= forage_kcal x forage_cap_hours), which binds only in savanna and limits how far a mother's harvest
can exceed her own need.

MEASURED at each JUVENILE starvation death, and for a same-schedule sample of LIVING juveniles:
  mother alive / on the same cell / number of her dependent juveniles
  mother's reserve fill AFTER provisioning   (< 1.0 => no overflow => tier 1 gave the child nothing)
  mother's reserve she would share under a child-priority rule (fill above 0.5 of her cap)
  mother's intake / her need; the forage rate cap on her cell / her need
  child age, the child's own intake / its need
LOOP ORDER. Provisioning runs before the metabolism loop; the death check runs inside it, in agent_list order. So at
a child's death the mother's POST-PROVISIONING reserve is `m.wealth` if she comes later in the list (not yet burned)
and `m._fed_reserve` (set at the start of her own iteration) if she came earlier. Both are handled.
Observer only: class-level wrappers, private RNG, no model state written.
"""
import json
import os
import random
import runpy
import sys

ROOT = r"C:\Users\syatom\Projects\SiC Games"
sys.path.insert(0, os.path.join(ROOT, "sic_games", "src"))
from sic_games.phase1_model import TerrainWorld   # noqa: E402

FROM = int(os.environ.get("CP_FROM", "3000"))
EVERY = int(os.environ.get("CP_EVERY", "25"))
NSAMP = int(os.environ.get("CP_NSAMP", "300"))
OUT = os.environ["CP_OUT"]
DEATHS, LIVING = [], []
_rng = random.Random(13579)
_cache = {"step": -1, "idx": None, "deps": None}

_orig_note = TerrainWorld._note_starvation_state
_orig_step = TerrainWorld.step


def _per_step(w):
    if _cache["step"] != w.step_count:
        _cache["idx"] = {id(a): i for i, a in enumerate(w.agent_list)}
        deps: dict = {}
        for a in w.agent_list:
            m = a._mother
            if a.is_juvenile() and m is not None and m.alive:
                deps[id(m)] = deps.get(id(m), 0) + 1
        _cache["deps"] = deps
        _cache["step"] = w.step_count
    return _cache["idx"], _cache["deps"]


def _rec(w, c, occ, at_death):
    d = w._demog
    fk = getattr(w._fields, "forage_kcal", None)
    idx, deps = _per_step(w)
    creq = w._burn * c.consumption_factor()
    r = dict(step=w.step_count, age_yr=round(c.age / 12.0, 2), occ=int(occ),
             child_intake=round(c._last_intake / creq, 3) if creq > 0 else 0.0)
    m = c._mother
    if m is None or not m.alive:
        r.update(mother="dead_or_none")
        return r
    mcap = w._reserve_full * m.reserve_scale()
    if at_death:
        # post-provisioning reserve, respecting the metabolism loop order
        post = m.wealth if idx.get(id(m), 1 << 30) > idx.get(id(c), -1) else float(getattr(m, "_fed_reserve", m.wealth))
    else:
        post = float(getattr(m, "_fed_reserve", m.wealth))      # end of step: set this step for every agent
    mreq = w._burn * m.consumption_factor()
    x, y = m.pos
    rate_cap = (float(fk[y, x]) * d.forage_cap_hours) if fk is not None else float("nan")
    r.update(mother="alive", same_cell=(m.pos == c.pos),
             m_fill=round(post / mcap, 3) if mcap > 0 else 0.0,
             m_at_cap=bool(post >= 0.999 * mcap),
             m_shareable=round(max(0.0, post - 0.5 * mcap) / creq, 3) if creq > 0 else 0.0,   # child-months
             m_intake=round(m._last_intake / mreq, 3) if mreq > 0 else 0.0,
             m_ratecap=round(rate_cap / mreq, 3) if mreq > 0 else 0.0,
             m_cf=round(m.consumption_factor(), 3),
             m_deps=int(deps.get(id(m), 0)))
    return r


def _note(self, a, occ_count, age_i):
    if self.step_count >= FROM and a.is_juvenile():
        DEATHS.append(_rec(self, a, occ_count.get(a.pos, 1), True))
    return _orig_note(self, a, occ_count, age_i)


def _step(self, *a, **k):
    r = _orig_step(self, *a, **k)
    if self.step_count >= FROM and self.step_count % EVERY == 0:
        juv = [ag for ag in self.agent_list if ag.is_juvenile()]
        if juv:
            occ: dict = {}
            for ag in self.agent_list:
                occ[ag.pos] = occ.get(ag.pos, 0) + 1
            pick = juv if len(juv) <= NSAMP else _rng.sample(juv, NSAMP)
            for ag in pick:
                LIVING.append(_rec(self, ag, occ[ag.pos], False))
    return r


TerrainWorld._note_starvation_state = _note
TerrainWorld.step = _step
try:
    runpy.run_path(os.path.join(ROOT, "sic_games", "outputs", "substrate_run", "run_campaign.py"), run_name="__main__")
finally:
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(dict(deaths=DEATHS, living=LIVING, from_step=FROM), fh)
    print(f"CHILDPROBE wrote {len(DEATHS)} juvenile starvation deaths, {len(LIVING)} living juveniles -> {OUT}", flush=True)
