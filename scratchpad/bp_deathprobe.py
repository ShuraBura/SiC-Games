"""R-106 Add.107 — WHO STARVES, AND WHAT DID THEY LACK? Per-death probe on the REAL campaign pipeline.

WHERE THE ARC STANDS. The crowding-mortality hypothesis (Add.105/106) is REFUTED on the canonical pipeline: the
starving die on LESS crowded cells than the living experience (occupancy ratio 0.51 / 0.34 / 0.87), after a
high intake EMA (1.6-3.8x need), with near-zero intake at death (0.03-0.13x). Every living adult sits at a
reserve fill of 0.423 = (reserve_full - BURN) / reserve_full: a well-fed agent tops up to the anchored Cahill cap
(130,000 kcal ~ 44 days) and one month's burn leaves 0.47 months above the death floor. The body buffer is
physiologically CORRECT; the model's design puts the multi-month buffer in the GRANARY — which is banked only on
storage-eligible cells (<= 15.25 C OR seasonal amplitude >= 0.25), drawn only by agents standing on THAT cell,
and capped by that cell's CURRENT occupancy.

HYPOTHESIS UNDER TEST: the starving die AWAY FROM STORED FOOD — on cells with no granary — so a single lean month
exhausts the ~1.5-month body buffer. Competing explanations the same records separate:
  - juvenile left without its provider (family head absent / dead)
  - outside any village (no sharing network)
  - a food-poor cell (low cell food per head)
Each field is recorded for the DYING and for a same-schedule sample of the LIVING, so a difference is a
difference, not a base rate.

OBSERVER DISCIPLINE. Two class-level wrappers, no model edit: `_note_starvation_state` (called at the moment of a
starvation death) and `step` (samples the living every 25 steps). The living sample uses its OWN random.Random, so
the model's RNG stream is untouched. Nothing here writes model state.
"""
import json
import os
import random
import runpy
import sys

ROOT = r"C:\Users\syatom\Projects\SiC Games"
sys.path.insert(0, os.path.join(ROOT, "sic_games", "src"))
from sic_games.phase1_model import TerrainWorld   # noqa: E402

FROM = int(os.environ.get("DP_FROM", "3000"))
EVERY = int(os.environ.get("DP_EVERY", "25"))
NSAMP = int(os.environ.get("DP_NSAMP", "200"))
OUT = os.environ["DP_OUT"]
DEATHS: list = []
LIVING: list = []
_rng = random.Random(987654)            # private — never the model's RNG

_orig_note = TerrainWorld._note_starvation_state
_orig_step = TerrainWorld.step


def _record(w, a, occ):
    d = w._demog
    x, y = a.pos
    thr_t = getattr(d, "storage_temp_threshold_c", 15.25)
    thr_s = getattr(d, "storage_seasonality_threshold", 0.25)
    samp = getattr(w, "_seasonal_amp", None)
    owz = bool(w._fields.temperature[y, x] <= thr_t
               or (samp is not None and samp[y, x] >= thr_s))
    head = w._family_head(a)
    if head is None:
        hs = "none"
    elif head.pos == a.pos:
        hs = "here"
    else:
        hs = "away"
    req = w._burn * a.consumption_factor()
    cap = w._reserve_full * a.reserve_scale()
    tf = w._harvest_field
    return dict(
        step=w.step_count, age_yr=round(a.age / 12.0, 2), juv=bool(a.is_juvenile()), sex=a.sex,
        head=hs, village=w._nearest_settlement(a.pos) is not None, owz=owz,
        store=round(w._cell_store.get(a.pos, 0.0) / w._reserve_full, 3),      # in BODY-RESERVE units
        occ=int(occ), food_pc=round(tf.level(x, y) / max(occ, 1) / w._burn, 3),
        intake=round((a._last_intake / req) if req > 0 else 0.0, 3),
        ema=round(float(getattr(a, "_intake_ema", 0.0)), 3),
        fedres=round(float(getattr(a, "_fed_reserve", 0.0)) / cap, 3) if cap > 0 else 0.0)


def _note(self, a, occ_count, age_i):
    if self.step_count >= FROM:
        DEATHS.append(_record(self, a, occ_count.get(a.pos, 1)))
    return _orig_note(self, a, occ_count, age_i)


def _step(self, *args, **kw):
    r = _orig_step(self, *args, **kw)
    if self.step_count >= FROM and self.step_count % EVERY == 0 and self.agent_list:
        occ: dict = {}
        for a in self.agent_list:
            occ[a.pos] = occ.get(a.pos, 0) + 1
        pick = self.agent_list if len(self.agent_list) <= NSAMP else _rng.sample(self.agent_list, NSAMP)
        for a in pick:
            LIVING.append(_record(self, a, occ[a.pos]))
    return r


TerrainWorld._note_starvation_state = _note
TerrainWorld.step = _step
try:
    runpy.run_path(os.path.join(ROOT, "sic_games", "outputs", "substrate_run", "run_campaign.py"),
                   run_name="__main__")
finally:
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(dict(deaths=DEATHS, living=LIVING, from_step=FROM), fh)
    print(f"DEATHPROBE wrote {len(DEATHS)} deaths, {len(LIVING)} living samples -> {OUT}", flush=True)
