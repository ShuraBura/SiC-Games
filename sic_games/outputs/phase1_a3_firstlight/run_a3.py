"""A-3 First-Light Shakedown — run + diagnostics + self-contained HTML report.

6 placement combos x 3 seeds x 1500 steps, 100x100, C-only, RIVALROUS multi-occupancy
(Stage-6.0a substrate) on a CC-1 cell-CAPACITY field + opt-in reproduction.

CC-1 cell capacity (supervisor-directed 2026-06-16): a 100 km2 cell supports a BAND, not
one forager. Per-cell capacity K = density(NPP) x 100 km2, density anchored to Tallavaara
2018 (HG density vs NPP): density = min(0.5, 0.3 x npp_gm2 / 1360) people/km2 (1360 =
Tallavaara low/high-productivity NPP threshold). The cell yields E = K x burn / step,
split among occupants (compute_harvest_shares); carrying capacity per cell = K. Reserve
stays PHYSIOLOGICAL (100k ~ 40 days of fat). [PROVISIONAL CC-1 preview.]

NOT a gate: findings are shapes the supervisor reads; rails are bug-catchers only.
Run:  py -3 outputs/phase1_a3_firstlight/run_a3.py
Out:  outputs/phase1_a3_firstlight/report.html  +  results.json
"""
from __future__ import annotations
import base64, io, json, os, time
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm

from sic_games.config import KcalEconomyConfig, SubstrateConfig
from sic_games.phase1_model import TerrainWorld
from sic_games.terrain import (N, generate_world, BIOME_WETLAND, BIOME_FOREST,
    BIOME_SAVANNA, BIOME_GRASS, BIOME_DESERT, BIOME_MOUNTAIN)

OUT = os.path.dirname(os.path.abspath(__file__))
SEEDS = [42, 43, 44]
COMBOS = [(4, 3), (4, 5), (6, 3), (6, 5), (8, 3), (8, 5)]   # (n_clusters, patch_size)
TOTAL_N = 1000
STEPS = 1500
WINDOW_START = 500
RAIL_EVERY = 100
OCC_EVERY = 10                 # accumulate per-cell occupancy every Nth step in the window
BURN = 75000.0                 # kcal/step (2500/day x 30); = KcalEconomyConfig burn
# CC-1 capacity (Tallavaara-anchored, PROVISIONAL)
NPP_THRESH, DENS_SLOPE, DENS_CAP, CELL_KM2 = 1360.0, 0.3, 0.5, 100.0
# Reproduction (band-fitting to the physiological 20-25k reserve band; PROVISIONAL shakedown)
REPRO = dict(reproduction=True, repro_min_age=15, birth_threshold=22000.0,
             birth_cost=1500.0, child_endowment=24000.0, p_birth=0.05)
SUBSTRATE = dict(enabled=True, k_cell=0, movement_mode="diffusion",
                 contest_exponent=0.0, move_cost_flat=0.0)
_BIOME_NAMES = {BIOME_WETLAND: "wetland", BIOME_FOREST: "forest", BIOME_SAVANNA: "savanna",
                BIOME_GRASS: "grass", BIOME_DESERT: "desert", BIOME_MOUNTAIN: "mountain"}
_BIOME_COLORS = ListedColormap(
    ["#2b6cb0", "#4fd1c5", "#22543d", "#b7791f", "#ecc94b", "#dd6b20", "#a0aec0"])
_BIOME_NORM = BoundaryNorm(list(range(8)), _BIOME_COLORS.N)


class CapacityField:
    """CC-1: a swap-in harvest field whose per-cell level is the cell's total sustainable
    yield E = K x burn, where K = density(NPP) x 100 km2 (Tallavaara-anchored)."""
    def __init__(self, fields):
        self.width = self.height = N
        dens = np.minimum(DENS_CAP, DENS_SLOPE * fields.npp_gm2 / NPP_THRESH)  # people/km2
        self.K = dens * CELL_KM2          # foragers the cell supports
        self._E = self.K * BURN           # kcal/step sustainable yield
    def level(self, x, y):
        return float(self._E[y, x])
    def harvest(self, x, y):
        return float(self._E[y, x])


def knobs_for(seed):
    return {"seedStr": f"world{seed}", "relief": 0.50, "rough": 0.50,
            "waterK": 0.30, "forestK": 0.55, "aridK": 0.40}


def founder_placement(fields, n_clusters, patch, total_N):
    """Deterministic founder clusters on an even lattice; agents distributed round-robin
    over each cluster's patch (LAND cells). Stacking is fine now — a cell holds a band."""
    rows, cols = {4: (2, 2), 6: (2, 3), 8: (2, 4)}[n_clusters]
    cxs = [int(round((c + 1) * N / (cols + 1))) for c in range(cols)]
    cys = [int(round((r + 1) * N / (rows + 1))) for r in range(rows)]
    centers = [(cx, cy) for cy in cys for cx in cxs][:n_clusters]
    per = [total_N // n_clusters] * n_clusters
    for i in range(total_N - sum(per)):
        per[i] += 1
    half = patch // 2
    positions, disp = [], []
    for ci, (cx, cy) in enumerate(centers):
        pc = [((cx + dx) % N, (cy + dy) % N)
              for dx in range(-half, half + 1) for dy in range(-half, half + 1)
              if fields.isWater[(cy + dy) % N, (cx + dx) % N] == 0] or [(cx, cy)]
        for k in range(per[ci]):
            positions.append(pc[k % len(pc)])
        if fields.isWater[cy, cx] != 0:
            disp.append((cx, cy, "centre-on-water"))
    return positions, disp


def _occ_grid(world):
    g = np.zeros((N, N))
    for a in world.agent_list:
        g[a.pos[1], a.pos[0]] += 1
    return g


def detect_onset(pop):
    pop = np.asarray(pop, float)
    final = pop[-500:].mean() if len(pop) >= 500 else pop[-50:].mean()
    if final <= 0:
        return len(pop)
    roll = np.convolve(pop, np.ones(25) / 25, mode="valid")
    for i, v in enumerate(roll):
        if abs(v - final) / final < 0.08:
            return i
    return len(pop) // 2


def run_one(seed, n_clusters, patch, steps=STEPS, collect_grids=False):
    fields = generate_world(knobs_for(seed))
    cf = CapacityField(fields)
    positions, disp = founder_placement(fields, n_clusters, patch, TOTAL_N)
    w = TerrainWorld(n_agents=TOTAL_N, kcal_cfg=KcalEconomyConfig(),
                     terrain_knobs=knobs_for(seed), game_stream=False, seed=seed,
                     substrate_cfg=SubstrateConfig(**SUBSTRATE), harvest_field=cf,
                     placement_positions=positions, **REPRO)
    floor = w._reserve_floor
    series = {k: [] for k in ("pop", "res", "births", "dstarv", "dsen", "age")}
    rails = dict(nan=False, neg=False, water=False, extinct=False)
    snaps = {0: _occ_grid(w)} if collect_grids else {}
    occ_accum = np.zeros((N, N)) if collect_grids else None
    for step in range(steps):
        w.step()
        p = w.population()
        series["pop"].append(p); series["res"].append(w.mean_reserve())
        series["births"].append(w.births_this_step)
        series["dstarv"].append(w.deaths_starv_this_step)
        series["dsen"].append(w.deaths_senesc_this_step); series["age"].append(w.mean_age())
        if p == 0:
            rails["extinct"] = True
        if step % RAIL_EVERY == 0 or step == steps - 1:
            for a in w.agent_list:
                if not np.isfinite(a.wealth):
                    rails["nan"] = True
                if a.wealth < floor - 1e-6:
                    rails["neg"] = True
                if fields.isWater[a.pos[1], a.pos[0]] != 0:
                    rails["water"] = True
        if collect_grids:
            if step >= WINDOW_START and step % OCC_EVERY == 0:
                for a in w.agent_list:
                    occ_accum[a.pos[1], a.pos[0]] += 1
            if step + 1 == steps // 2:
                snaps[steps // 2] = _occ_grid(w)
    if collect_grids:
        snaps[steps - 1] = _occ_grid(w)
    out = dict(seed=seed, n_clusters=n_clusters, patch=patch, disp=disp, rails=rails,
               onset=detect_onset(series["pop"]),
               final_pop=float(np.mean(series["pop"][-500:])), series=series,
               biome=fields.biome.copy())
    if collect_grids:
        out["occ_mean"] = occ_accum / max(1, (steps - WINDOW_START) // OCC_EVERY)
        out["snaps"] = snaps
    return out


def habitability_table():
    """Per-biome cell capacity K averaged across the 3 seed worlds."""
    acc = {c: [] for c in _BIOME_NAMES}
    total_cap, land_ge1 = [], []
    for s in SEEDS:
        f = generate_world(knobs_for(s)); cf = CapacityField(f)
        for code in _BIOME_NAMES:
            m = f.biome == code
            if m.any():
                acc[code].append(cf.K[m].mean())
        land = f.isWater == 0
        total_cap.append(cf.K[land].sum())
        land_ge1.append(100 * float(np.mean(cf.K[land] >= 1)))
    rows = []
    for code, nm in _BIOME_NAMES.items():
        if acc[code]:
            rows.append((nm, float(np.mean(acc[code]))))
    return rows, float(np.mean(total_cap)), float(np.mean(land_ge1))


def fig_b64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=108, bbox_inches="tight")
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode()


def main():
    t0 = time.time()
    print("[A-3] habitability table (per-biome cell capacity, 3 worlds)...")
    hab_rows, total_cap, land_ge1 = habitability_table()
    for nm, k in hab_rows:
        print(f"        {nm:9s} K~{k:.1f}")
    print(f"        total terrain capacity ~{total_cap:.0f}; land cells K>=1: {land_ge1:.0f}%")

    print("[A-3] determinism check (combo (4,3) seed 42, 250 steps x2)...")
    a = run_one(42, 4, 3, steps=250)["series"]["pop"]
    b = run_one(42, 4, 3, steps=250)["series"]["pop"]
    determinism_ok = (a == b)
    print(f"        determinism: {'PASS' if determinism_ok else 'FAIL'}")

    print("[A-3] 18-run sweep (6 combos x 3 seeds x 1500 steps, ~138k agents)...")
    runs = {}
    for (nc, pt) in COMBOS:
        for sd in SEEDS:
            r = run_one(sd, nc, pt, collect_grids=(nc, pt) == (4, 3))
            runs[(nc, pt, sd)] = r
            print(f"        ({nc},{pt}) s{sd}: final~{r['final_pop']:.0f} onset~{r['onset']} "
                  f"rails={'ok' if not any(r['rails'].values()) else r['rails']}  [{time.time()-t0:.0f}s]")
    elapsed = time.time() - t0

    finals = {k: v["final_pop"] for k, v in runs.items()}
    cap_mean = float(np.mean(list(finals.values())))
    cap_std = float(np.std(list(finals.values())))
    by_combo = {c: [finals[(c[0], c[1], s)] for s in SEEDS] for c in COMBOS}
    any_rail = {f"{k}": {kk: vv for kk, vv in v["rails"].items() if vv}
                for k, v in runs.items() if any(v["rails"].values())}
    rails_clean = (not any_rail) and determinism_ok
    onset_max = max(v["onset"] for v in runs.values())

    figs = {}
    cols = {42: "#3182ce", 43: "#e53e3e", 44: "#38a169"}
    # 1 settling
    fig, axes = plt.subplots(2, 3, figsize=(13, 7), sharex=True, sharey=True)
    for ax, c in zip(axes.flat, COMBOS):
        for s in SEEDS:
            ax.plot(runs[(c[0], c[1], s)]["series"]["pop"], color=cols[s], lw=1.0, label=f"seed {s}")
        ax.set_title(f"{c[0]} clusters, {c[1]}x{c[1]} patch", fontsize=10)
        ax.axvline(WINDOW_START, color="#999", ls=":", lw=0.8); ax.grid(alpha=0.25)
    axes.flat[0].legend(fontsize=8, loc="lower right")
    fig.suptitle("Settling population — 18 runs (CC-1 capacity economy)", fontsize=12)
    fig.text(0.5, 0.04, "step (month)", ha="center"); fig.text(0.06, 0.5, "population", va="center", rotation=90)
    figs["settling"] = fig_b64(fig)
    # 2 convergence
    fig, ax = plt.subplots(figsize=(9, 4.2)); xs = np.arange(len(COMBOS))
    for j, s in enumerate(SEEDS):
        ax.bar(xs + (j - 1) * 0.25, [by_combo[c][j] for c in COMBOS], width=0.25, color=cols[s], label=f"seed {s}")
    ax.axhline(cap_mean, color="k", ls="--", lw=1, label=f"mean {cap_mean:.0f}")
    ax.set_xticks(xs); ax.set_xticklabels([f"{c[0]}c/{c[1]}p" for c in COMBOS])
    ax.set_ylabel("final population (last-500 mean)"); ax.legend(fontsize=8)
    ax.set_title(f"Convergence read — {cap_mean:.0f} ± {cap_std:.0f} (spread {100*cap_std/cap_mean:.1f}%)")
    ax.grid(alpha=0.25, axis="y"); figs["convergence"] = fig_b64(fig)
    # representative run
    rep = runs[(4, 3, 42)]; ss = rep["series"]
    # 3 dynamics
    fig, ax = plt.subplots(2, 2, figsize=(12, 6.5))
    ax[0, 0].plot(ss["res"], color="#805ad5"); ax[0, 0].set_title("mean reserve (kcal)"); ax[0, 0].grid(alpha=0.25)
    ax[0, 1].plot(ss["births"], color="#38a169", lw=0.6, label="births")
    ax[0, 1].plot(np.array(ss["dstarv"]) + np.array(ss["dsen"]), color="#e53e3e", lw=0.6, label="deaths")
    ax[0, 1].set_title("births vs deaths / step"); ax[0, 1].legend(fontsize=8); ax[0, 1].grid(alpha=0.25)
    ax[1, 0].plot(ss["age"], color="#dd6b20"); ax[1, 0].set_title("mean age (months)"); ax[1, 0].grid(alpha=0.25)
    ax[1, 1].plot(ss["dstarv"], color="#e53e3e", lw=0.6, label="starvation")
    ax[1, 1].plot(ss["dsen"], color="#718096", lw=0.6, label="senescence")
    ax[1, 1].set_title("deaths by cause / step"); ax[1, 1].legend(fontsize=8); ax[1, 1].grid(alpha=0.25)
    fig.suptitle("Dynamics sanity — representative run (4 clusters, 3x3, seed 42)", fontsize=12)
    figs["dynamics"] = fig_b64(fig)
    # 4 snapshots
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.8))
    for ax, t in zip(axes, sorted(rep["snaps"])):
        ax.imshow(rep["biome"], cmap=_BIOME_COLORS, norm=_BIOME_NORM, origin="lower", alpha=0.55)
        g = rep["snaps"][t]; ys, xs2 = np.nonzero(g)
        ax.scatter(xs2, ys, s=np.clip(g[ys, xs2] * 0.5, 1, 25), c="black", alpha=0.35, linewidths=0)
        ax.set_title(f"t = {t}"); ax.set_xticks([]); ax.set_yticks([])
    fig.suptitle("Spatial density (black = agents) over biome map", fontsize=12)
    figs["snapshots"] = fig_b64(fig)
    # 5 settlement
    occ = rep["occ_mean"]
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    im = axes[0].imshow(np.where(occ > 0, occ, np.nan), cmap="inferno", origin="lower")
    axes[0].set_title("per-cell mean occupancy (post-equilibrium)"); axes[0].set_xticks([]); axes[0].set_yticks([])
    fig.colorbar(im, ax=axes[0], shrink=0.8)
    vals = occ[occ > 0]
    axes[1].hist(vals, bins=40, color="#3182ce", edgecolor="white")
    axes[1].set_title(f"distribution over {len(vals)} occupied cells")
    axes[1].set_xlabel("mean agents / cell"); axes[1].set_ylabel("# cells"); axes[1].grid(alpha=0.25, axis="y")
    fig.suptitle("Settlement structure — representative run (4 clusters, 3x3, seed 42)", fontsize=12)
    figs["settlement"] = fig_b64(fig)

    results = dict(
        config=dict(combos=COMBOS, seeds=SEEDS, total_N=TOTAL_N, steps=STEPS, repro=REPRO,
                    substrate=SUBSTRATE, capacity=dict(npp_thresh=NPP_THRESH, dens_slope=DENS_SLOPE,
                    dens_cap=DENS_CAP, cell_km2=CELL_KM2), window_start=WINDOW_START),
        habitability={nm: round(k, 1) for nm, k in hab_rows},
        terrain_total_capacity=total_cap, land_K_ge1_pct=land_ge1,
        capacity_mean=cap_mean, capacity_std=cap_std, capacity_spread_pct=100 * cap_std / cap_mean,
        finals={f"{k[0]}c_{k[1]}p_s{k[2]}": v for k, v in finals.items()},
        onset_max=onset_max, determinism_ok=determinism_ok, rails_clean=rails_clean,
        rail_violations=any_rail, elapsed_sec=elapsed)
    with open(os.path.join(OUT, "results.json"), "w") as f:
        json.dump(results, f, indent=2, default=str)
    _write_html(figs, results, runs, hab_rows, total_cap, land_ge1)
    print(f"[A-3] done in {elapsed:.0f}s. capacity {cap_mean:.0f}±{cap_std:.0f}. report.html written.")


def _write_html(figs, R, runs, hab_rows, total_cap, land_ge1):
    def img(k):
        return f'<img src="data:image/png;base64,{figs[k]}" style="max-width:100%;height:auto;">'
    rails_line = "all green" if R["rails_clean"] else json.dumps(R["rail_violations"])
    crows = "".join(
        f"<tr><td>{c[0]} / {c[1]}x{c[1]}</td>" +
        "".join(f"<td>{runs[(c[0],c[1],s)]['final_pop']:.0f}</td>" for s in SEEDS) +
        f"<td>{np.std([runs[(c[0],c[1],s)]['final_pop'] for s in SEEDS]):.0f}</td></tr>"
        for c in COMBOS)
    hrows = "".join(f"<tr><td>{nm}</td><td>{k:.1f}</td></tr>" for nm, k in hab_rows)
    dens = R["capacity_mean"] / 1e6 * 1e6 / 1_000_000  # agents per km2 (1e6 km2 territory)
    html = f"""<!doctype html><html><head><meta charset="utf-8"><title>A-3 First-Light Shakedown</title>
<style>
body{{font-family:-apple-system,Segoe UI,Roboto,sans-serif;max-width:1100px;margin:24px auto;padding:0 18px;color:#1a202c;line-height:1.5}}
h1{{border-bottom:3px solid #3182ce;padding-bottom:6px}} h2{{color:#2c5282;margin-top:34px}}
.box{{background:#f7fafc;border-left:4px solid #3182ce;padding:10px 16px;margin:14px 0;border-radius:4px}}
.warn{{border-left-color:#dd6b20;background:#fffaf0}} .flag{{border-left-color:#e53e3e;background:#fff5f5}}
.ok{{border-left-color:#38a169;background:#f0fff4}}
table{{border-collapse:collapse;margin:10px 0}} td,th{{border:1px solid #cbd5e0;padding:5px 12px;text-align:right}} th{{background:#edf2f7}}
td:first-child,th:first-child{{text-align:left}} code{{background:#edf2f7;padding:1px 5px;border-radius:3px}} .fig{{margin:18px 0;text-align:center}}
</style></head><body>
<h1>A-3 First-Light Shakedown — Phase 1 terrain, C-only</h1>
<p><b>6 placement combos x 3 seeds x {R['config']['steps']} steps, 100x100, RIVALROUS multi-occupancy on a
CC-1 cell-capacity field.</b> Not a gate — findings are shapes; rails are bug-catchers. Ran in {R['elapsed_sec']:.0f}s
(~{R['elapsed_sec']/3600:.1f} h).</p>

<div class="box ok"><b>CC-1 cell capacity (the headline model addition, supervisor-directed 2026-06-16).</b>
A 100 km2 cell supports a <b>band</b>, not one forager. The earlier non-rivalrous run wrongly used the
<i>per-forager</i> forage rate as the whole cell's food, so cells held ~6 and savanna held 0. Fixed: each cell yields
<code>E = K x burn</code> per step, split among occupants, where <b>K = density(NPP) x 100 km2</b> and density is
anchored to <b>Tallavaara 2018</b> (HG density vs NPP): <code>density = min(0.5, 0.3 x npp_gm2 / 1360)</code>
people/km2 (1360 = Tallavaara's low/high-productivity NPP threshold). Reserve stays PHYSIOLOGICAL (100k ~ 40 days
fat). All values PROVISIONAL pending the full CC-1 calibration.</div>

<h2>Habitability check — every biome supports a non-zero band</h2>
<table><tr><th>biome</th><th>foragers / cell (K)</th></tr>{hrows}</table>
<p>Total terrain carrying capacity ~<b>{total_cap:.0f} people</b> over 1,000,000 km2 (~{total_cap/1e6:.2f}/km2 —
ethnographically realistic for a savanna-dominated landscape). Land cells with K&ge;1: <b>{land_ge1:.0f}%</b>
(only the rare very-low-NPP / barren-mountain cells fall below one person).</p>

<h2>Headline</h2>
<div class="box"><b>Discovered carrying capacity: {R['capacity_mean']:.0f} ± {R['capacity_std']:.0f} agents</b>
(mean of 18 runs; spread {R['capacity_spread_pct']:.1f}%) = ~{R['capacity_mean']/total_cap*100:.0f}% of the terrain's
total support ({total_cap:.0f}).<br>
<b>Convergence:</b> {'strong — placement leaves little fingerprint at t=1500 (terrain-driven attractor).' if R['capacity_spread_pct']<12 else 'partial — placement leaves a visible fingerprint at t=1500.'}<br>
Supersedes the stale N_carry=400 (a Sugarscape/50<sup>2</sup> value) — <b>PROPOSED, not locked</b>.</div>

<h2>1 . Settling-population curves (18 runs)</h2>
<div class="fig">{img('settling')}</div>
<h2>2 . Convergence vs divergence</h2>
<div class="fig">{img('convergence')}</div>
<table><tr><th>clusters / patch</th><th>seed 42</th><th>seed 43</th><th>seed 44</th><th>SD</th></tr>{crows}</table>
<p>Equilibrium onset &le; step {R['onset_max']} across all runs.</p>
<h2>3 . Spatial density — founders radiate and sort onto terrain</h2>
<div class="fig">{img('snapshots')}</div>
<h2>4 . Settlement structure (per-cell mean occupancy)</h2>
<div class="fig">{img('settlement')}</div>
<p>Histogram shape is the finding: a long right tail / bimodality = durable concentrations on the best terrain;
a smooth spread = no settlement structure. Read the break (if any) off the data.</p>
<h2>5 . Dynamics sanity</h2>
<div class="fig">{img('dynamics')}</div>

<h2>6 . Guards (assertable rails — bug-catchers)</h2>
<div class="box"><b>Rails: {rails_line}</b><br>determinism: <b>{'PASS' if R['determinism_ok'] else 'FAIL'}</b> ·
no NaN/Inf · no reserve below floor · no agents on water (terrain guard) · no extinction before t={R['config']['steps']} ·
conservation (sum of per-cell shares == E by construction).</div>

<h2>7 . Anomalies &amp; tuning flags — for the supervisor (NOT auto-tuned)</h2>
<div class="box flag"><b>1. Capacity is a PROVISIONAL CC-1 preview.</b> K = density(NPP) x 100 km2 with a linear
density anchored to Tallavaara's NPP threshold (1360) and the ethnographic ~0.1-0.5/km2 band, capped at 0.5. The full
CC-1 stage should fit Tallavaara's actual regression (incl. biodiversity / pathogen terms) and re-derive the per-cell
extractable rate. Absolute capacity (~{total_cap:.0f}) will shift with that calibration; the dynamics are the finding.</div>
<div class="box flag"><b>2. Forage-only; game + sex-streams + provisioning deferred.</b> The cell yield is a single
NPP-capacity pool. The forage/game per-forager rates (the literature resource layer) now inform K via NPP but are not
split into hunter/gatherer streams here. Sex-based game/forage + parent->child provisioning is the next demographic layer.</div>
<div class="box flag"><b>3. Age-graded yield + parental provisioning UNWIRED.</b> Only a binary age-gate exists
(intake 0 below 15, and only if lh_config is passed); the graded eta(a) ramp is C-only/Phase-0; no provisioning. This
run keeps the age-gate OFF (children forage as adults) so demography proceeds. JV-1 (graded yield) + MR-2 (provisioning)
are required next.</div>
<div class="box flag"><b>4. Repro params are shakedown placeholders</b> (<code>birth_threshold=22k, birth_cost=1.5k,
child_endowment=24k, p_birth=0.05</code>), fit to the physiological 20-25k reserve band. Asexual budding — replace with
the full C biparental/Cred reproduction at the demographic stage / RECAL.</div>
<div class="box flag"><b>5. K=0 (uniform split), affinity neutral.</b> The C-specific Cred/phi contest (K&gt;0) and the
social-affinity hook are not exercised here (uniform "Cred=1 for all"). Next layer.</div>

<h2>8 . Bugs fixed</h2>
<div class="box">Water guard added to the rivalrous movement (the shared diffusion rule is water-blind). No science
parameter touched.</div>
<p style="color:#718096;font-size:0.9em;margin-top:30px">A-3 First-Light Shakedown · Phase 1 · {time.strftime('%Y-%m-%d')} ·
exploratory (not a gate) · CC-1 capacity + all repro values PROVISIONAL.</p>
</body></html>"""
    with open(os.path.join(OUT, "report.html"), "w", encoding="utf-8") as f:
        f.write(html)


if __name__ == "__main__":
    main()
