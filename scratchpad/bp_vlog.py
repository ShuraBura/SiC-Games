"""R-106 Add.130: per-village log. Which villages run empty, why their people stay, and why adults starve beside a store.

No model change. This observer reads state, draws no RNG and writes no model attribute, except the documented `_diag_pool`.
It wraps `allocate_store_draw` to read each draw (the caller frame gives the claimants), and `_note_starvation_state` to read
each starvation death. From DR_FROM to the end. Three logs in design_logs:
  vlg<tag>.jsonl  one line per village-year (food account, store, flows, the pin, the food outside).
  dth<tag>.jsonl  one line per starvation death (the draw of that person, the store left, the status order).
  chk<tag>.jsonl  one line per step (model counts against logged counts).
"""
import bisect
import json
import os
import runpy
import sys

ROOT = r"C:\Users\syatom\Projects\SiC Games"
sys.path.insert(0, os.path.join(ROOT, "sic_games", "src"))
import sic_games.phase1_model as PM   # noqa: E402
from sic_games.phase1_model import TerrainWorld, N   # noqa: E402
from sic_games.demography import size_repulsion   # noqa: E402

FROM = int(os.environ.get("DR_FROM", "1800"))
TAG = os.environ.get("C_TAG", "")
LOG = os.path.join(ROOT, "scratchpad", "design_logs")
os.makedirs(LOG, exist_ok=True)
VOUT, DOUT, COUT = (os.path.join(LOG, f"{p}{TAG}.jsonl") for p in ("vlg", "dth", "chk"))
for p in (VOUT, DOUT, COUT):
    open(p, "w", encoding="utf-8").close()

_orig_alloc = PM.allocate_store_draw
_orig_hook = TerrainWorld._note_starvation_state
_orig_step = TerrainWorld.step

ON = False
draw = {}            # id(agent) -> this step's draw of that agent
vw = {}              # store key -> sorted weights of this draw
dacc = {}            # store key -> [unmet, left] this step
dead_log = []        # the deaths of this step
dep = {}             # id(mother) -> dependent children this step, built once per step
prev = {}            # unique_id -> site after the last step (None = mobile)
Y = {}               # site -> accumulators of this year
first = {}           # site -> first step seen
pgrid = [[[0] * 10 for _ in range(4)] for _ in range(2)]   # [cell, village][age class][status decile] person-steps in a draw
short = [[[0] * 10 for _ in range(4)] for _ in range(2)]   # the same, for a draw below the deficit


def rnd(x, n=3):
    return None if x is None else round(float(x), n)


def _alloc(weights, deficits, store):
    gives = _orig_alloc(weights, deficits, store)
    if ON:
        f = sys._getframe(1).f_locals
        needy, key = f["needy"], f["key"]
        vil = key in f["self"]._settlement_sites
        kap = f.get("kap_v") if vil else f.get("kappa_cell")
        wsum = sum(weights) or 1.0
        n = len(weights)
        for (a, d), w, g in zip(needy, weights, gives):
            draw[id(a)] = (key, d, w / wsum * n, g, store, n, kap, vil, w)
        vw[key] = sw = sorted(weights)
        for (a, d), w, g in zip(needy, weights, gives):      # the exposure by age class and status decile, the null for the deaths
            cl = 0 if a.age < 180 else (1 if a.age < 312 else (2 if a.age < 552 else 3))
            dc = min(9, int(10 * bisect.bisect_left(sw, w) / max(1, n - 1)))
            pgrid[int(vil)][cl][dc] += 1
            short[int(vil)][cl][dc] += (1 if g < d else 0)
        got = sum(gives)
        dacc[key] = (sum(deficits) - got, store - got)
    return gives


def _deps(self):
    if not dep:
        dep[0] = 0
        for c in self.agent_list:
            if c.is_juvenile():
                m = getattr(c, "_mother", None)
                if m is not None and m.alive:
                    dep[id(m)] = dep.get(id(m), 0) + 1
    return dep


def _hook(self, a, *args, **k):
    if ON:
        s = self._nearest_settlement(a.pos)
        key = s if s is not None else a.pos
        r = draw.get(id(a))
        flr = a.reserve_floor * a.reserve_scale()
        pct = None
        if r is not None and r[0] in vw:
            w = vw[r[0]]
            pct = bisect.bisect_left(w, r[8]) / max(1, len(w) - 1)
        rec = dict(st=self.step_count, s=list(s) if s is not None else None, age=a.age, sex=a.sex, inq=int(r is not None), vil=(int(r[7]) if r else None),
                   d=rnd(r[1], 1) if r else None, sh=rnd(r[2]) if r else None, g=rnd(r[3], 1) if r else None, st0=rnd(r[4], 1) if r else None, nn=(r[5] if r else None), kap=rnd(r[6]) if r else None,
                   pct=rnd(pct), left=rnd(self._cell_store.get(key, 0.0), 1), short=rnd(flr - a.wealth, 1), w=rnd(a.wealth, 1), flr=rnd(flr, 1),
                   cap=rnd(self._reserve_full * a.reserve_scale(), 1), need=rnd(self._burn * a.consumption_factor(), 1), last=rnd(a._last_intake, 1),
                   ema=rnd(getattr(a, "_intake_ema", None)), cond=rnd(getattr(a, "_condition", None)), cred=rnd(a.cred), prow=rnd(getattr(a, "prowess", None)),
                   dep=_deps(self).get(id(a), 0), strat=str(getattr(a, "strategy", "")))
        dead_log.append(rec)
    return _orig_hook(self, a, *args, **k)


def _new():
    return dict(n=0, heads=0, ad=0, ch=0, need=0.0, intake=0.0, cap=0.0, cap_min=1e30, cap_max=0.0, pool=0.0, nc_max=0.0, nc_lean=0.0, sph=0.0, sph_min=1e30, sph_end=0.0, fill=0.0, nf=0,
                hard=0.0, soil=0.0, born=0, dead=0, ds_inf=0, ds_ch=0, ds_ad=0, ds_str=0, out_mob=0, out_vil=0, out_diss=0, in_mob=0, in_vil=0, unmet=0.0, left=0.0, stranded=0.0, alt={}, pc_lean=0.0, cap_lean=0.0)


def _alts(self, occ, tag):
    """The best food per person on the rings 3, 4, 5 around each site, outside each village: level / (n + 1), under the forage rate cap."""
    tf = self._harvest_field
    W, H = getattr(tf, "width", N), getattr(tf, "height", N)
    nm = self._nearest_map or {}
    fc = self._forage_cap_field()
    wat = self._fields.isWater
    b = self._burn
    for s, y in Y.items():
        if s not in self._settlement_sites:
            continue
        sx, sy = s
        best = {3: 0.0, 4: 0.0, 5: 0.0}
        for R in (3, 4, 5):
            for dy in range(-R, R + 1):
                for dx in range(-R, R + 1):
                    if max(abs(dx), abs(dy)) != R:
                        continue
                    c = ((sx + dx) % W, (sy + dy) % H)
                    if c in nm or wat[c[1], c[0]] != 0:
                        continue
                    v = tf.level(c[0], c[1]) / (occ.get(c, 0) + 1)
                    if fc is not None:
                        v = min(v, float(fc[c[1], c[0]]))
                    if v > best[R]:
                        best[R] = v
        y["alt"][tag] = {str(R): rnd(v / b) for R, v in best.items()}


def _observe(self):
    burn = self._burn
    t = self.step_count
    sites = self._settlement_sites
    now, H_, occ = {}, {}, {}
    for a in self.agent_list:
        s = self._nearest_settlement(a.pos)
        now[a.unique_id] = s
        occ[a.pos] = occ.get(a.pos, 0) + 1
        if s is None:
            continue
        v = H_.setdefault(s, [0, 0, 0, 0.0, 0.0])
        v[0] += 1
        if a.age >= 180:
            v[1] += 1
        else:
            v[2] += 1
        v[3] += burn * a.consumption_factor()
        v[4] += a._last_intake
    pool = {}
    for c, (S, _n) in (self._diag_pool or {}).items():
        s = self._nearest_settlement(c)
        if s is not None:
            pool[s] = pool.get(s, 0.0) + S
    for s, v in H_.items():
        y = Y.get(s)
        if y is None:
            y = Y[s] = _new()
            first.setdefault(s, t)
        h = max(1, v[0])
        cap = self._settlement_carrying_capacity(s)
        sph = self._cell_store.get(s, 0.0) / (h * burn)
        y["n"] += 1
        y["heads"] += v[0]
        y["ad"] += v[1]
        y["ch"] += v[2]
        y["need"] += v[3]
        y["intake"] += v[4]
        y["cap"] += cap
        y["cap_min"] = min(y["cap_min"], cap)
        y["cap_max"] = max(y["cap_max"], cap)
        y["pool"] += pool.get(s, 0.0)
        if cap > 0:
            y["nc_max"] = max(y["nc_max"], v[3] / cap)
        y["sph"] += sph
        y["sph_min"] = min(y["sph_min"], sph)
        y["sph_end"] = sph
        f = self._dens_fert_fill_village.get(s)
        if f is not None:
            y["fill"] += f
            y["nf"] += 1
        y["hard"] += self._settlement_hardship.get(s, 0.0)
        y["soil"] += self._settlement_soil.get(s, 1.0)
        if t % 12 == 6:
            y["nc_lean"] = v[3] / cap if cap > 0 else None
            y["pc_lean"] = v[4] / (h * burn)
            y["cap_lean"] = cap
        if s in dacc:
            un, le = dacc[s]
            y["unmet"] += un
            y["left"] += le
            y["stranded"] += min(max(un, 0.0), max(le, 0.0))
    nb = ng = 0
    for u, s in now.items():
        if u not in prev:
            nb += 1
            if s is not None and s in Y:
                Y[s]["born"] += 1
        else:
            p = prev[u]
            if p != s:
                if p is not None and p in Y:
                    k = "out_diss" if p not in sites else ("out_mob" if s is None else "out_vil")
                    Y[p][k] += 1
                if s is not None and s in Y:
                    Y[s]["in_mob" if p is None else "in_vil"] += 1
    for u, p in prev.items():
        if u not in now:
            ng += 1
            if p is not None and p in Y:
                Y[p]["dead"] += 1
    prev.clear()
    prev.update(now)
    for r in dead_log:
        if r["s"] is not None:
            y = Y.get(tuple(r["s"]))
            if y is not None:
                k = "ds_inf" if r["age"] < 12 else ("ds_ch" if r["age"] < 180 else "ds_ad")
                y[k] += 1
                y["ds_str"] += int(r["left"] >= r["short"])
    if dead_log:
        with open(DOUT, "a", encoding="utf-8") as fh:
            for r in dead_log:
                fh.write(json.dumps(r) + "\n")
    with open(COUT, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(dict(st=t, pop=len(self.agent_list), births=self.births_this_step, ds=self.deaths_starv_this_step, dn=self.deaths_senesc_this_step, logged=len(dead_log),
                                 nb=nb, ng=ng, mob=sum(1 for s in now.values() if s is None), nv=len(H_))) + "\n")
    dead_log.clear()
    if t % 12 == 6:
        _alts(self, occ, "lean")
    if t % 12 == 0:
        _alts(self, occ, "yr")
        _flush(self, t)


def _flush(self, t):
    tf = self._harvest_field
    W, H = getattr(tf, "width", N), getattr(tf, "height", N)
    fk = getattr(self._fields, "forage_kcal", None)
    wat = self._fields.isWater
    b = self._burn
    rc = self._demog.settle_catchment_radius
    with open(VOUT, "a", encoding="utf-8") as fh:
        for s, y in Y.items():
            n = max(1, y["n"])
            sx, sy = s
            land = fsum = 0
            for dy in range(-rc, rc + 1):
                for dx in range(-rc, rc + 1):
                    c = ((sx + dx) % W, (sy + dy) % H)
                    if wat[c[1], c[0]] == 0:
                        land += 1
                        fsum += float(fk[c[1], c[0]]) if fk is not None else 0.0
            ss = size_repulsion(y["heads"] / n, self._demog.settlement_ss_gain, self._demog.settlement_ss_midpoint, self._demog.settlement_ss_width, self._cell_society.get(s))
            fh.write(json.dumps(dict(st=t, s=[sx, sy], age=t - first[s], n=y["n"], alive=int(s in self._settlement_sites), heads=rnd(y["heads"] / n, 1), ad=rnd(y["ad"] / n, 1), ch=rnd(y["ch"] / n, 1),
                                     need=rnd(y["need"] / n, 0), intake=rnd(y["intake"] / n, 0), cap=rnd(y["cap"] / n, 0), cap_min=rnd(y["cap_min"], 0), cap_max=rnd(y["cap_max"], 0), pool=rnd(y["pool"] / n, 0),
                                     nc_max=rnd(y["nc_max"]), nc_lean=rnd(y["nc_lean"]), pc_lean=rnd(y["pc_lean"]), cap_lean=rnd(y["cap_lean"], 0), sph=rnd(y["sph"] / n, 2), sph_min=rnd(y["sph_min"], 2), sph_end=rnd(y["sph_end"], 2),
                                     fill=rnd(y["fill"] / y["nf"]) if y["nf"] else None, hard=rnd(y["hard"] / n, 4), soil=rnd(y["soil"] / n), ss=rnd(ss, 4), born=y["born"], dead=y["dead"],
                                     ds_inf=y["ds_inf"], ds_ch=y["ds_ch"], ds_ad=y["ds_ad"], ds_str=y["ds_str"], out_mob=y["out_mob"], out_vil=y["out_vil"], out_diss=y["out_diss"], in_mob=y["in_mob"], in_vil=y["in_vil"],
                                     unmet=rnd(y["unmet"] / b, 1), left=rnd(y["left"] / b, 1), stranded=rnd(y["stranded"] / b, 1), alt=y["alt"], land=land, fk=rnd(fsum / max(1, land), 1))) + "\n")
    Y.clear()
    with open(os.path.join(LOG, f"grd{TAG}.json"), "w", encoding="utf-8") as fh:
        json.dump(dict(st=t, pgrid=pgrid, short=short), fh)


def _step(self, *a, **k):
    global ON
    if self.step_count >= FROM - 1:
        ON = True
        self._diag_pool = {}
        draw.clear()
        vw.clear()
        dacc.clear()
        dep.clear()
    out = _orig_step(self, *a, **k)
    if self.step_count == FROM - 1:
        prev.clear()
        prev.update({x.unique_id: self._nearest_settlement(x.pos) for x in self.agent_list})
    elif self.step_count >= FROM:
        _observe(self)
    return out


assert _orig_alloc([100.0, 1.0], [1.0, 100.0], 50.0) == [1.0, 50.0 / 101.0], "C4 the known case"
PM.allocate_store_draw = _alloc
TerrainWorld._note_starvation_state = _hook
TerrainWorld.step = _step
runpy.run_path(os.path.join(ROOT, "sic_games", "outputs", "substrate_run", "run_campaign.py"), run_name="__main__")
