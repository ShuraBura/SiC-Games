"""R-106 design task after Add.127: measure the CANDIDATE SIGNALS before a design relies on them (Add.119's lesson).

No model change. Pure observer from DR_FROM to the end: each step it writes one JSON line of aggregates. It reads agent
state and the field, draws no RNG and writes no model attribute. One shock of DR_LEN steps at DR_ONSET, depth DR_MULT.
Before the onset the three arms of a seed are one identical run, so the arms are exactly paired at the onset.

Groups: W = women past menarche, before menopause, past the base refractory (a proxy for the women at risk);
C = children aged 1-9; A = adults aged 15-45.
Signals:
  fill, fd     the brake as coded: fill = village or cell fill; fd = clamp(1 - fill^exp).
  fd_ann       the same, with the capacity replaced by the mean of its last 12 steps (the brake with no season in it).
  ema, f_int   _intake_ema and the fertility factor clamp((ema - lo) / (hi - lo)).
  raw          last_intake / own need, this step.
  cond         _condition.
  unfed        share with a post-harvest reserve below the full cap: a shortfall FREQUENCY. Broken for children (reads 1.0).
  fed, trough  reserve fill post-harvest, and post-step (distance to the starvation floor), with low quantiles.
  m_ema        children only: the mother's _intake_ema (alive mothers).
  m_unfed      children only: share whose mother is below the cap.
"""
import json
import os
import runpy
import sys
from collections import deque

ROOT = r"C:\Users\syatom\Projects\SiC Games"
sys.path.insert(0, os.path.join(ROOT, "sic_games", "src"))
import sic_games.climate as CL   # noqa: E402
from sic_games.phase1_model import TerrainWorld   # noqa: E402

ONSET = int(os.environ.get("DR_ONSET", "1800"))
LEN = int(os.environ.get("DR_LEN", "12"))
MULT = float(os.environ["DR_MULT"])
FROM = int(os.environ.get("DR_FROM", "1764"))
OUT = os.path.join(ROOT, "scratchpad", "design_logs", f"sig{os.environ.get('C_TAG', '')}.jsonl")
os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, "w", encoding="utf-8").close()
_orig_build = CL.build_climate_field
_orig_step = TerrainWorld.step
_caps = {}


def q(xs, p):
    if not xs:
        return None
    s = sorted(xs)
    return s[min(len(s) - 1, int(p * len(s)))]


def mean(xs):
    return sum(xs) / len(xs) if xs else None


def _observe(self):
    cfg = self._demog
    tf = self._harvest_field
    ex = cfg.density_fert_exponent
    lo, hi = cfg.intake_fert_lo, cfg.intake_fert_hi
    fv = dict(self._dens_fert_fill_village)
    occ = {}
    for a in self.agent_list:
        occ[a.pos] = occ.get(a.pos, 0) + 1
    caps_now = {}
    for s in self._settlement_sites:
        c = self._settlement_carrying_capacity(s)
        caps_now[s] = c
        _caps.setdefault(s, deque(maxlen=12)).append(c)
    G = {k: dict(fill=[], fd=[], fd_ann=[], ema=[], f_int=[], raw=[], cond=[], unfed=[], fed=[], trough=[], n=0) for k in "WCA"}
    m_ema, m_unfed = [], []
    for a in self.agent_list:
        age = a.age
        grp = []
        if a.sex == "female" and cfg.menarche_months <= age < cfg.menopause_months and a.months_since_birth >= cfg.ibi_refractory_months:
            grp.append("W")
        if 12 <= age < 120:
            grp.append("C")
        if 180 <= age < 540:
            grp.append("A")
        if not grp:
            continue
        site = self._nearest_settlement(a.pos)
        if site is not None:
            fill = fv.get(site, 1.0)
            dq = _caps.get(site)
            cn = caps_now.get(site, 0.0)
            ratio = (cn / (sum(dq) / len(dq))) if dq and cn > 0 else 1.0
        else:
            food = tf.level(a.pos[0], a.pos[1])
            fill = (occ.get(a.pos, 1) * self._burn / food) if food > 0 else 1.0
            ratio = 1.0
        rs = a.reserve_scale()
        need = self._burn * a.consumption_factor()
        unf = 1.0 if a._fed_reserve < 0.999 * self._reserve_full * rs else 0.0
        flr, cap = a.reserve_floor * rs, self._reserve_full * rs
        fed = (a._fed_reserve - flr) / (cap - flr) if cap > flr else 1.0
        trough = (a.wealth - flr) / (cap - flr) if cap > flr else 1.0
        for k in grp:
            g = G[k]
            g["n"] += 1
            g["fill"].append(fill)
            g["fd"].append(max(0.0, 1.0 - fill ** ex) if fill > 0 else 1.0)
            fa = fill * ratio
            g["fd_ann"].append(max(0.0, 1.0 - fa ** ex) if fa > 0 else 1.0)
            g["ema"].append(a._intake_ema)
            f = (a._intake_ema - lo) / (hi - lo)
            g["f_int"].append(0.0 if f < 0 else (1.0 if f > 1 else f))
            g["raw"].append(a._last_intake / need if need > 0 else 1.0)
            g["cond"].append(a._condition)
            g["unfed"].append(unf)
            g["fed"].append(fed)
            g["trough"].append(trough)
        if "C" in grp:
            m = getattr(a, "_mother", None)
            if m is not None and m.alive:
                m_ema.append(m._intake_ema)
                m_unfed.append(1.0 if m._fed_reserve < 0.999 * self._reserve_full * m.reserve_scale() else 0.0)
    rec = dict(step=self.step_count, pop=len(self.agent_list), births=self.births_this_step,
               starv=list(self.lt_deaths_starv), deaths=list(self.lt_deaths), fert_factor=self.fert_factor_sum,
               fert_n=self.fert_factor_n, m_ema=mean(m_ema), m_ema_p10=q(m_ema, 0.1), m_unfed=mean(m_unfed), n_sites=len(self._settlement_sites))
    for k, g in G.items():
        rec[k] = dict(n=g["n"], **{f"{v}_m": mean(g[v]) for v in ("fill", "fd", "fd_ann", "ema", "f_int", "raw", "cond", "unfed", "fed", "trough")},
                      fill_p10=q(g["fill"], .1), fill_p50=q(g["fill"], .5), fill_p90=q(g["fill"], .9),
                      fill_gt1=mean([1.0 if x >= 1 else 0.0 for x in g["fill"]]), fed_p10=q(g["fed"], .1), trough_p10=q(g["trough"], .1), trough_p01=q(g["trough"], .01), raw_p10=q(g["raw"], .1), raw_p50=q(g["raw"], .5), ema_p10=q(g["ema"], .1), ema_p50=q(g["ema"], .5),
                      f_fd=mean([x * y for x, y in zip(g["f_int"], g["fd"])]))
    with open(OUT, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec) + "\n")


def _step(self, *a, **k):
    out = _orig_step(self, *a, **k)
    if self.step_count >= FROM:
        _observe(self)
    return out


def _build(*a, **k):
    field = _orig_build(*a, **k)
    field.regime_driver = CL.ClimateDriver.pulse(ONSET, LEN, MULT)
    print(f"DSIG: pulse(onset={ONSET}, len={LEN}, mult={MULT}), observer from {FROM}", flush=True)
    return field


CL.build_climate_field = _build
TerrainWorld.step = _step
runpy.run_path(os.path.join(ROOT, "sic_games", "outputs", "substrate_run", "run_campaign.py"), run_name="__main__")
