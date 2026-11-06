"""R-106 design task: second observer run. Measure the VILLAGE STORE as a food signal, and who starves relative to it.

No model change. Pure observer from DR_FROM to the end; reads state, draws no RNG and writes no model attribute. The first
observer (bp_design_signals.py) showed that no individual state moves under a one-year shock: reserve, condition and the
mother intake EMA are flat, and only fill and the raw harvest move. The store cap is 12 reserves per head (about 16
months of burn), so the store is the candidate buffer. The first run did not record it.

Each step, one JSON line. Groups by head: C (ages 1-9), I (age < 1), A (ages 15-45), all (everyone).
  mobile    share outside every village (no site); they reach only a cell store.
  sph       store per head of the village of the agent, in steps of an adult burn: mean, p10, p50, p90.
  sph0      share living where the store is below one step of burn per head.
  sfull     share living where the store is above 90% of its cap.
  raw_lt1   share of women at risk, and of the mothers of children, with harvest below their own need this step.
Per village (unweighted): v_n, v_sph_p10/p50/p90, v_sup = village harvest / village need this step (p10, p50).
Starvation, per death (through the model starvation hook): age, mobile or not, sph of the village, fill, mother alive.
"""
import json
import os
import runpy
import sys

ROOT = r"C:\Users\syatom\Projects\SiC Games"
sys.path.insert(0, os.path.join(ROOT, "sic_games", "src"))
import sic_games.climate as CL   # noqa: E402
from sic_games.phase1_model import TerrainWorld   # noqa: E402

ONSET = int(os.environ.get("DR_ONSET", "1800"))
LEN = int(os.environ.get("DR_LEN", "12"))
MULT = float(os.environ["DR_MULT"])
FROM = int(os.environ.get("DR_FROM", "1764"))
OUT = os.path.join(ROOT, "scratchpad", "design_logs", f"sto{os.environ.get('C_TAG', '')}.jsonl")
os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, "w", encoding="utf-8").close()
_orig_build = CL.build_climate_field
_orig_step = TerrainWorld.step
_hook_name = "_note_starvation_state"
_orig_hook = getattr(TerrainWorld, _hook_name)
_dead = []


def q(xs, p):
    if not xs:
        return None
    s = sorted(xs)
    return s[min(len(s) - 1, int(p * len(s)))]


def mean(xs):
    return sum(xs) / len(xs) if xs else None


def _hook(self, a, *args, **k):
    if self.step_count >= FROM - 1:
        s = self._nearest_settlement(a.pos)
        nv = getattr(self, "_v_heads", {}).get(s, 0) if s is not None else 0
        st = self._cell_store.get(s if s is not None else a.pos, 0.0)
        m = getattr(a, "_mother", None)
        _dead.append(dict(age=a.age, mob=1 if s is None else 0, sph=st / (max(1, nv) * self._burn),
                          fill=self._dens_fert_fill_village.get(s) if s is not None else None,
                          mom=1 if (m is not None and m.alive) else 0))
    return _orig_hook(self, a, *args, **k)


def _heads(self):
    h = {}
    for a in self.agent_list:
        s = self._nearest_settlement(a.pos)
        h[s] = h.get(s, 0) + 1
    self._v_heads = h


def _observe(self):
    cfg = self._demog
    h = self._v_heads
    burn = self._burn
    G = {k: [] for k in ("all", "C", "I", "A")}
    mob = {k: [] for k in G}
    raw_w, raw_m = [], []
    sup, need = {}, {}
    for a in self.agent_list:
        age = a.age
        s = self._nearest_settlement(a.pos)
        grp = ["all"]
        if age < 12:
            grp.append("I")
        if 12 <= age < 120:
            grp.append("C")
        if 180 <= age < 540:
            grp.append("A")
        sph = self._cell_store.get(s, 0.0) / (max(1, h.get(s, 1)) * burn) if s is not None else None
        for k in grp:
            mob[k].append(1.0 if s is None else 0.0)
            if sph is not None:
                G[k].append(sph)
        nd = burn * a.consumption_factor()
        if s is not None:
            sup[s] = sup.get(s, 0.0) + a._last_intake
            need[s] = need.get(s, 0.0) + nd
        if a.sex == "female" and cfg.menarche_months <= age < cfg.menopause_months and a.months_since_birth >= cfg.ibi_refractory_months:
            raw_w.append(1.0 if a._last_intake < nd else 0.0)
        if 12 <= age < 120:
            m = getattr(a, "_mother", None)
            if m is not None and m.alive:
                raw_m.append(1.0 if m._last_intake < burn * m.consumption_factor() else 0.0)
    capsteps = cfg.store_capacity_reserves * self._reserve_full / burn
    rec = dict(step=self.step_count, pop=len(self.agent_list), births=self.births_this_step, capsteps=capsteps,
               raw_lt1_w=mean(raw_w), raw_lt1_m=mean(raw_m))
    for k, xs in G.items():
        rec[k] = dict(n=len(mob[k]), mobile=mean(mob[k]), sph_m=mean(xs), sph_p10=q(xs, .1), sph_p50=q(xs, .5), sph_p90=q(xs, .9),
                      sph0=mean([1.0 if x < 1.0 else 0.0 for x in xs]), sfull=mean([1.0 if x >= 0.9 * capsteps else 0.0 for x in xs]))
    vs = [self._cell_store.get(s, 0.0) / (max(1, h.get(s, 1)) * burn) for s in need]
    vu = [sup[s] / need[s] for s in need if need[s] > 0]
    rec.update(v_n=len(vs), v_sph_p10=q(vs, .1), v_sph_p50=q(vs, .5), v_sph_p90=q(vs, .9), v_sup_p10=q(vu, .1), v_sup_p50=q(vu, .5), dead=list(_dead))
    _dead.clear()
    with open(OUT, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec) + "\n")


def _step(self, *a, **k):
    if self.step_count >= FROM - 2:
        _heads(self)
    out = _orig_step(self, *a, **k)
    if self.step_count >= FROM:
        _heads(self)
        _observe(self)
    return out


def _build(*a, **k):
    field = _orig_build(*a, **k)
    field.regime_driver = CL.ClimateDriver.pulse(ONSET, LEN, MULT)
    print(f"DSTO: pulse(onset={ONSET}, len={LEN}, mult={MULT}), observer from {FROM}, hook {_hook_name}", flush=True)
    return field


CL.build_climate_field = _build
TerrainWorld.step = _step
setattr(TerrainWorld, _hook_name, _hook)
runpy.run_path(os.path.join(ROOT, "sic_games", "outputs", "substrate_run", "run_campaign.py"), run_name="__main__")
