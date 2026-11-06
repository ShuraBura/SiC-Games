"""R-106 design task: third observer run. The FOOD ACCOUNT of a village: does the harvest obey the ceiling that the brake reads?

No model change. Sets the existing diagnostic dict `_diag_pool` (documented: no behaviour) and reads state; draws no RNG.
Hypothesis to test: the ceiling applies per cell, so each occupied cell of a village has its own pool, and the village total
is several times the ceiling (the 9-cell sum at the site) that the brake reads.

For each step, one JSON line. Summed over villages, and medians over villages:
  heads, need     members; their own need (burn x consumption factor), no dependent load.
  cap             _settlement_carrying_capacity(site), the brake denominator.
  sum25           the sum of cell yield over the settle_radius window.
  S_site, S_oth   pool S after the ceiling, at the site cell and at the other occupied cells of the village.
  lev_oth         the bare cell yield at those other cells (S_oth - lev_oth = bonus, agglomeration).
  intake          sum of _last_intake of the members.
  cells           occupied cells per village.
  fill            the brake fill, unweighted and person weighted.
  need_cap_med    median over villages of need / cap: the fill that a true village ceiling would read.
  sup_cap_med     median over villages of (S_site + S_oth) / cap.
Outside villages: heads and need of mobile agents, and their pool.
"""
import json
import os
import runpy
import sys

ROOT = r"C:\Users\syatom\Projects\SiC Games"
sys.path.insert(0, os.path.join(ROOT, "sic_games", "src"))
from sic_games.phase1_model import TerrainWorld, N   # noqa: E402

FROM = int(os.environ.get("DR_FROM", "1764"))
OUT = os.path.join(ROOT, "scratchpad", "design_logs", f"acc{os.environ.get('C_TAG', '')}.jsonl")
os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, "w", encoding="utf-8").close()
_orig_step = TerrainWorld.step


def med(xs):
    s = sorted(xs)
    return s[len(s) // 2] if s else None


def _observe(self):
    tf = self._harvest_field
    burn = self._burn
    rs = self._demog.settle_radius
    W = getattr(tf, "width", N)
    H = getattr(tf, "height", N)
    V = {}
    mob = dict(heads=0, need=0.0, intake=0.0)
    for a in self.agent_list:
        s = self._nearest_settlement(a.pos)
        nd = burn * a.consumption_factor()
        if s is None:
            mob["heads"] += 1
            mob["need"] += nd
            mob["intake"] += a._last_intake
            continue
        v = V.setdefault(s, dict(heads=0, need=0.0, intake=0.0, cells=set()))
        v["heads"] += 1
        v["need"] += nd
        v["intake"] += a._last_intake
        v["cells"].add(a.pos)
    pool = self._diag_pool or {}
    S_site = S_oth = lev_oth = cap = sum25 = need = heads = intake = 0.0
    rnc, rsc, cells, fills, fw = [], [], [], [], 0.0
    for s, v in V.items():
        c = self._settlement_carrying_capacity(s)
        sx, sy = s
        t25 = 0.0
        for dy in range(-rs, rs + 1):
            for dx in range(-rs, rs + 1):
                t25 += tf.level((sx + dx) % W, (sy + dy) % H)
        ss = pool.get(s, (0.0, 0))[0]
        so = lo = 0.0
        for cell, (S, n) in pool.items():
            if cell != s and self._nearest_settlement(cell) == s:
                so += S
                lo += tf.level(cell[0], cell[1])
        S_site += ss
        S_oth += so
        lev_oth += lo
        cap += c
        sum25 += t25
        need += v["need"]
        heads += v["heads"]
        intake += v["intake"]
        cells.append(len(v["cells"]))
        f = self._dens_fert_fill_village.get(s)
        if f is not None:
            fills.append(f)
            fw += f * v["heads"]
        if c > 0:
            rnc.append(v["need"] / c)
            rsc.append((ss + so) / c)
    rec = dict(step=self.step_count, pop=len(self.agent_list), n_v=len(V), heads=heads, need=need, intake=intake, cap=cap, sum25=sum25, S_site=S_site, S_oth=S_oth, lev_oth=lev_oth,
               cells_med=med(cells), fill_med=med(fills), fill_pw=(fw / heads if heads else None), need_cap_med=med(rnc), sup_cap_med=med(rsc), mob=mob)
    with open(OUT, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec) + "\n")


def _step(self, *a, **k):
    if self.step_count >= FROM - 1:
        self._diag_pool = {}
    out = _orig_step(self, *a, **k)
    if self.step_count >= FROM:
        _observe(self)
    return out


TerrainWorld.step = _step
runpy.run_path(os.path.join(ROOT, "sic_games", "outputs", "substrate_run", "run_campaign.py"), run_name="__main__")
