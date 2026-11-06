"""A1 check: is the excess of village sum / ceiling above 1 a read-time effect of the observer?

Compare each village sum of pools with the ceiling read DURING the harvest. The harvest loop is the only reader that sets
`_diag_pool`, so record each value of the ceiling per site per step, and compare the sum with those values and with the value
read after the step. Membership comes from the map that the harvest used. No RNG, no behaviour.
"""
import os
import runpy
import sys

ROOT = r"C:\Users\syatom\Projects\SiC Games"
sys.path.insert(0, os.path.join(ROOT, "sic_games", "src"))
from sic_games.phase1_model import TerrainWorld   # noqa: E402

_cap = TerrainWorld._settlement_carrying_capacity
_step = TerrainWorld.step
seen = {}
st = dict(n=0, over_post=0, over_during=0, max_post=0.0, max_during=0.0, min_during_binding=9.0)


def cap(self, site):
    v = _cap(self, site)
    seen.setdefault(site, []).append(v)
    return v


def step(self, *a, **k):
    seen.clear()
    self._diag_pool = {}
    self._nearest_map = None
    pre = None
    out = _step(self, *a, **k)
    if self.step_count < 100:
        return out
    pool = self._diag_pool
    sums = {}
    for c, (S, _n) in pool.items():
        s = self._nearest_settlement(c)
        if s is not None:
            sums[s] = sums.get(s, 0.0) + S
    snap = {s: list(v) for s, v in seen.items()}
    for s, tot in sums.items():
        post = _cap(self, s)
        if post <= 0 or s not in snap:
            continue
        st["n"] += 1
        rp = tot / post
        st["max_post"] = max(st["max_post"], float(rp))
        st["over_post"] += int(rp > 1.001)
        vals = [v for v in snap[s] if v > 0]
        if rp >= 0.99 and vals:                                  # a village at its ceiling: does it equal a harvest read?
            st["binding"] = st.get("binding", 0) + 1
            st["binding_match"] = st.get("binding_match", 0) + int(min(abs(tot / v - 1.0) for v in vals) < 1e-9)
            st["above_all_reads"] = st.get("above_all_reads", 0) + int(tot > max(vals) * (1.0 + 1e-9))
            st["worst_above_all_reads"] = max(st.get("worst_above_all_reads", 0.0), float(tot / max(vals)))
    if self.step_count % 40 == 0:
        print("A1CHK", self.step_count, st, flush=True)
    return out


TerrainWorld._settlement_carrying_capacity = cap
TerrainWorld.step = step
runpy.run_path(os.path.join(ROOT, "sic_games", "outputs", "substrate_run", "run_campaign.py"), run_name="__main__")
