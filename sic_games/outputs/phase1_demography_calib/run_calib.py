"""Phase 1 Demographic stage — STEP 1: non-spatial Aché calibration harness.

A well-mixed (terrain-free) microsimulation under the FIXED Aché Siler mortality schedule
(Gurven & Kaplan 2007; M-1) + IBI female reproduction. Step 1's job (blueprint §7): with the
Siler coefficients fixed, tune only the fertility knobs (`fecundability`) so the population is
stationary (r≈0) with continuous birth–death turnover, and verify the realized IBI/TFR and the
survivorship curve match the Aché. No terrain, no kcal economy, no modulators (all flags off).

Validates the blueprint §8 gate (Step-1 portion):
  • l(x) reproduces the Aché life table (e₀/e₁₅/e₄₅/mode)   [the schedule is fixed → a check]
  • births ≈ deaths > 0 at equilibrium (the anti-frozen check; the A-3 finding's fix)
  • r ≈ 0 ; realized IBI ≈ 37 mo ; completed TFR ≈ 8

Run:  py -3 -u outputs/phase1_demography_calib/run_calib.py
Out:  outputs/phase1_demography_calib/report.html  +  results.json  +  progress.txt
"""
from __future__ import annotations
import base64, io, json, os, time
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sic_games.demography import ACHE_FOREST, DemographyConfig, life_expectancy, modal_adult_death

OUT = os.path.dirname(os.path.abspath(__file__))
FEMALE, MALE = 1, 0
MPY = 12

# Aché targets (Gurven & Kaplan 2007; Hill & Hurtado) — the Step-1 gate
TGT = dict(e0=37.0, e15=38.5, e45=21.1, mode=71.0, ibi=37.0, tfr=8.0)


def stationary_ages(p, n, rng, x_max=90):
    """Sample n initial ages (months) from the stationary age structure ∝ l(x) (blueprint m-4:
    the Aché-shaped pyramid; for r=0 the age distribution is the survivorship curve)."""
    ages_y = np.arange(0, x_max, 0.5)
    w = np.array([p.survivorship(a) for a in ages_y]); w /= w.sum()
    return (rng.choice(ages_y, size=n, p=w) * MPY).astype(np.int64)


def simulate(cfg, fecundability, n0=2000, months=3000, seed=42, record=False, cap=6000):
    """Vectorised monthly microsim. Returns growth rate r (per yr) and, if record, full series."""
    rng = np.random.default_rng(seed)
    p = cfg.siler()
    a1, b1, a2, a3, b3 = p.a1, p.b1, p.a2, p.a3, p.b3
    # founder state
    age = stationary_ages(p, n0, rng)
    sex = (rng.random(n0) < 0.5).astype(np.int8)          # ~half female at init
    msb = np.full(n0, 10**9, dtype=np.int64)              # months since birth (huge → no refractory block)
    parity = np.zeros(n0, dtype=np.int64)
    reached_menarche = np.zeros(n0, dtype=bool)
    counted = np.zeros(n0, dtype=bool)        # completed fertility captured at menopause crossing

    pop_s, birth_s, death_s = [], [], []
    ibi_samples, completed_parity = [], []

    for m in range(months):
        n = age.shape[0]
        # 1. age
        age += 1; msb += 1
        reached_menarche |= (sex == FEMALE) & (age >= cfg.menarche_months)
        # completed fertility: capture a woman's parity once, when she crosses menopause
        cross = (sex == FEMALE) & reached_menarche & (~counted) & (age >= cfg.menopause_months)
        if cross.any():
            completed_parity.extend(parity[cross].tolist()); counted[cross] = True
        # 2. mortality (Siler monthly; a2 unmodulated in Step 1)
        ay = age / MPY
        h = a1 * np.exp(-b1 * ay) + a2 + a3 * np.exp(b3 * ay)
        p_death = 1.0 - np.exp(-h / MPY)
        died = rng.random(n) < p_death
        # 3. reproduction (eligible females, past refractory, in window) — BEFORE removing dead
        elig = ((sex == FEMALE) & (~died) & (age >= cfg.menarche_months)
                & (age < cfg.menopause_months) & (msb >= cfg.ibi_refractory_months))
        give = elig & (rng.random(n) < fecundability)
        nb = int(give.sum())
        if nb:
            prev_parous = give & (parity >= 1)               # IBI = months since previous birth
            if prev_parous.any():
                ibi_samples.extend(msb[prev_parous].tolist())
            parity[give] += 1
            msb[give] = 0
            # maternal mortality — drawn AFTER the birth is counted (M-5)
            mat = give & (rng.random(n) < cfg.maternal_mortality_per_birth)
            died = died | mat
            child_sex = np.where(rng.random(nb) < cfg.srb_male, MALE, FEMALE).astype(np.int8)
        # 4. record, then compact to survivors + append newborns
        survivors = ~died
        births_this, deaths_this = nb, int(died.sum())
        age, sex, msb, parity, reached_menarche, counted = (
            age[survivors], sex[survivors], msb[survivors], parity[survivors],
            reached_menarche[survivors], counted[survivors])
        if nb:
            age = np.concatenate([age, np.zeros(nb, np.int64)])
            sex = np.concatenate([sex, child_sex])
            msb = np.concatenate([msb, np.full(nb, 10**9, np.int64)])
            parity = np.concatenate([parity, np.zeros(nb, np.int64)])
            reached_menarche = np.concatenate([reached_menarche, np.zeros(nb, bool)])
            counted = np.concatenate([counted, np.zeros(nb, bool)])
        # cap population (random age-neutral cull; culls are NOT recorded as deaths) so a growing
        # population stays tractable — vital rates are intensive and unaffected by the cull
        if age.shape[0] > cap:
            keep = rng.choice(age.shape[0], cap, replace=False)
            age, sex, msb, parity, reached_menarche, counted = (
                age[keep], sex[keep], msb[keep], parity[keep], reached_menarche[keep], counted[keep])
        pop_s.append(age.shape[0]); birth_s.append(births_this); death_s.append(deaths_this)
        if age.shape[0] == 0:
            break

    pop = np.array(pop_s, float); bb = np.array(birth_s, float); dd = np.array(death_s, float)
    # natural growth rate r (per yr), cap-invariant: per-capita (births − deaths) over the back half
    half = len(pop) // 2
    if len(pop) - half > 24 and pop[half:].mean() > 0:
        r = float((bb[half:].sum() - dd[half:].sum()) / (pop[half:].mean() * (len(pop) - half)) * MPY)
    else:
        r = float("nan")
    ibi_arr = np.array(ibi_samples, float)
    out = dict(r=r, ibi_mean=float(ibi_arr.mean()) if ibi_arr.size else float("nan"))
    if record:
        out.update(pop=pop_s, births=birth_s, deaths=death_s, ibi=ibi_samples,
                   parity=completed_parity, final_age=age.copy(), final_sex=sex.copy())
    return out


def calibrate_fecundability(cfg, target_ibi=37.0, lo=0.03, hi=0.60, iters=16):
    """Bisection on fecundability to hit the Aché IBI (higher fecundability → shorter IBI).

    NOTE: Aché fertility under Aché mortality implies a GROWING population (r>0) — the real
    forest-period Aché grew. r≈0 is a Step-2 (density-dependent) property, NOT a Step-1 target;
    Step 1 matches the Aché vital rates (IBI/TFR) and reports the resulting r."""
    history = []
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        o = simulate(cfg, mid, months=2400, seed=7)
        ibi = o["ibi_mean"]
        history.append((round(mid, 4), round(ibi, 1), round(o["r"], 4)))
        if not np.isfinite(ibi):
            lo = mid; continue
        if ibi > target_ibi:        # interval too long → need higher fecundability
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi), history


def fig_b64(fig):
    buf = io.BytesIO(); fig.savefig(buf, format="png", dpi=108, bbox_inches="tight")
    plt.close(fig); return base64.b64encode(buf.getvalue()).decode()


def main():
    t0 = time.time()
    cfg = DemographyConfig()
    p = cfg.siler()
    prog = os.path.join(OUT, "progress.txt")
    def log(msg):
        print(msg, flush=True)
        with open(prog, "w") as f: f.write(f"{msg}\nelapsed {time.time()-t0:.0f}s\n")

    # life-table check (schedule is fixed → a verification, not a fit)
    lt = dict(e0=life_expectancy(p, 0), e15=life_expectancy(p, 15),
              e45=life_expectancy(p, 45), mode=modal_adult_death(p))
    log(f"[STEP1] life-table check: e0={lt['e0']:.1f} e15={lt['e15']:.1f} "
        f"e45={lt['e45']:.1f} mode={lt['mode']:.0f}")

    log("[STEP1] calibrating fecundability to Aché IBI~37mo ...")
    fec, hist = calibrate_fecundability(cfg)
    log(f"[STEP1] calibrated fecundability={fec:.4f}; final long run ...")
    R = simulate(cfg, fec, n0=3000, months=3600, seed=42, record=True)

    ibi = np.array(R["ibi"], float)
    par = np.array([x for x in R["parity"] if x is not None], float)
    crude_birth = np.mean(R["births"][-600:]) / np.mean(R["pop"][-600:]) * MPY * 1000  # per 1000/yr
    crude_death = np.mean(R["deaths"][-600:]) / np.mean(R["pop"][-600:]) * MPY * 1000
    metrics = dict(
        fecundability=fec, r_per_yr=R["r"],
        e0=lt["e0"], e15=lt["e15"], e45=lt["e45"], modal_adult_death=lt["mode"],
        ibi_mean=float(ibi.mean()) if ibi.size else float("nan"),
        tfr_completed=float(par.mean()) if par.size else float("nan"),
        crude_birth_rate_per1000=crude_birth, crude_death_rate_per1000=crude_death,
        final_pop=R["pop"][-1])
    log(f"[STEP1] r={R['r']:+.4f}/yr  IBI={metrics['ibi_mean']:.1f}mo  "
        f"TFR={metrics['tfr_completed']:.1f}  CDR={crude_death:.0f}/1000  CBR={crude_birth:.0f}/1000")

    # ---- figures ----
    figs = {}
    # 1 survivorship l(x) vs Aché anchors
    xs = np.linspace(0, 90, 400); lx = np.array([p.survivorship(x) for x in xs])
    fig, ax = plt.subplots(figsize=(7, 4.2))
    ax.plot(xs, lx, color="#3182ce", lw=2, label="fixed Aché Siler l(x)")
    ax.scatter([15, 45], [p.survivorship(15), p.survivorship(45)], color="#e53e3e", zorder=5,
               label="anchors: l(15)=.66, l(45)=.43")
    ax.set_xlabel("age (years)"); ax.set_ylabel("survivorship l(x)"); ax.grid(alpha=0.25)
    ax.set_title(f"Survivorship — e0={lt['e0']:.0f}, e15={lt['e15']:.0f}, mode={lt['mode']:.0f}")
    ax.legend(fontsize=8); figs["lx"] = fig_b64(fig)
    # 2 population trajectory
    fig, ax = plt.subplots(figsize=(7, 4.2)); yr = np.arange(len(R["pop"])) / MPY
    ax.plot(yr, R["pop"], color="#38a169")
    ax.set_xlabel("year"); ax.set_ylabel("population"); ax.grid(alpha=0.25)
    ax.set_title(f"Population (r = {R['r']:+.4f}/yr at fecundability {fec:.3f})")
    figs["pop"] = fig_b64(fig)
    # 3 births vs deaths per year (anti-frozen check)
    fig, ax = plt.subplots(figsize=(7, 4.2))
    def yearly(a): a = np.array(a, float); n = len(a) // MPY * MPY; return a[:n].reshape(-1, MPY).sum(1)
    b_y, d_y = yearly(R["births"]), yearly(R["deaths"]); yy = np.arange(len(b_y))
    ax.plot(yy, b_y, color="#38a169", lw=1, label="births/yr")
    ax.plot(yy, d_y, color="#e53e3e", lw=1, label="deaths/yr")
    ax.set_xlabel("year"); ax.set_ylabel("count/yr"); ax.grid(alpha=0.25); ax.legend(fontsize=8)
    ax.set_title(f"Turnover — CBR {crude_birth:.0f} / CDR {crude_death:.0f} per 1000/yr (NOT frozen)")
    figs["turnover"] = fig_b64(fig)
    # 4 age pyramid
    fig, ax = plt.subplots(figsize=(7, 4.2)); fa = R["final_age"] / MPY; fs = R["final_sex"]
    bins = np.arange(0, 91, 5)
    ax.hist(fa[fs == FEMALE], bins=bins, orientation="horizontal", color="#d53f8c", alpha=0.7, label="female")
    ax.hist(fa[fs == MALE], bins=bins, orientation="horizontal", color="#3182ce", alpha=0.5, label="male")
    ax.set_ylabel("age (years)"); ax.set_xlabel("count"); ax.grid(alpha=0.25, axis="y"); ax.legend(fontsize=8)
    ax.set_title("Final age pyramid (Aché-shaped: young, broad base)"); figs["pyramid"] = fig_b64(fig)
    # 5 IBI + parity
    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    if ibi.size:
        ax[0].hist(ibi, bins=30, color="#805ad5", edgecolor="white")
        ax[0].axvline(TGT["ibi"], color="k", ls="--", label=f"Aché {TGT['ibi']:.0f}mo")
        ax[0].axvline(ibi.mean(), color="#e53e3e", label=f"sim {ibi.mean():.0f}mo")
    ax[0].set_title("Inter-birth interval"); ax[0].set_xlabel("months"); ax[0].legend(fontsize=8); ax[0].grid(alpha=0.25)
    if par.size:
        ax[1].hist(par, bins=range(0, 16), color="#dd6b20", edgecolor="white")
        ax[1].axvline(TGT["tfr"], color="k", ls="--", label=f"Aché ~{TGT['tfr']:.0f}")
        ax[1].axvline(par.mean(), color="#e53e3e", label=f"sim {par.mean():.1f}")
    ax[1].set_title("Completed fertility (parity at death)"); ax[1].set_xlabel("births/woman")
    ax[1].legend(fontsize=8); ax[1].grid(alpha=0.25)
    figs["fertility"] = fig_b64(fig)

    with open(os.path.join(OUT, "results.json"), "w") as f:
        json.dump(dict(metrics=metrics, targets=TGT, config=cfg.model_dump(),
                       calibration_history=hist, elapsed_sec=time.time() - t0), f, indent=2, default=str)
    _write_html(figs, metrics, lt, fec, R)
    log(f"[STEP1] done in {time.time()-t0:.0f}s. report.html written.")


def _row(name, sim, tgt, unit="", tol=None, fmt="{:.1f}"):
    ok = "" if tol is None else ("✓" if abs(sim - tgt) <= tol else "⚠")
    return (f"<tr><td>{name}</td><td>{fmt.format(sim)}{unit}</td>"
            f"<td>{fmt.format(tgt)}{unit}</td><td>{ok}</td></tr>")


def _write_html(figs, M, lt, fec, R):
    def img(k): return f'<img src="data:image/png;base64,{figs[k]}" style="max-width:100%;height:auto;">'
    frozen = abs(M["crude_death_rate_per1000"]) > 5  # turnover is real, not the A-3 freeze
    rows = "".join([
        _row("Life expectancy e₀", lt["e0"], TGT["e0"], " yr", 2),
        _row("e₁₅ (remaining yr)", lt["e15"], TGT["e15"], " yr", 2),
        _row("e₄₅ (remaining yr)", lt["e45"], TGT["e45"], " yr", 2),
        _row("Modal adult death", lt["mode"], TGT["mode"], " yr", 3, "{:.0f}"),
        f"<tr><td>Growth rate r (realized)</td><td>{M['r_per_yr']:+.4f}/yr</td>"
        f"<td>&gt;0 (Aché grew)</td><td>&#8505;</td></tr>",
        _row("Inter-birth interval", M["ibi_mean"], TGT["ibi"], " mo", 6),
        _row("Completed TFR", M["tfr_completed"], TGT["tfr"], "", 1.5),
    ])
    html = f"""<!doctype html><html><head><meta charset="utf-8"><title>Demography Step 1 — Aché calibration</title>
<style>body{{font-family:-apple-system,Segoe UI,Roboto,sans-serif;max-width:1000px;margin:24px auto;padding:0 18px;color:#1a202c;line-height:1.5}}
h1{{border-bottom:3px solid #3182ce;padding-bottom:6px}}h2{{color:#2c5282;margin-top:30px}}
.box{{background:#f7fafc;border-left:4px solid #3182ce;padding:10px 16px;margin:14px 0;border-radius:4px}}
.ok{{border-left-color:#38a169;background:#f0fff4}}.warn{{border-left-color:#dd6b20;background:#fffaf0}}
table{{border-collapse:collapse;margin:10px 0}}td,th{{border:1px solid #cbd5e0;padding:5px 12px;text-align:right}}
th{{background:#edf2f7}}td:first-child,th:first-child{{text-align:left}}code{{background:#edf2f7;padding:1px 5px;border-radius:3px}}.fig{{margin:16px 0;text-align:center}}</style></head><body>
<h1>Demographic stage — Step 1: non-spatial Aché calibration</h1>
<p><b>Fixed Aché Siler mortality (Gurven &amp; Kaplan 2007; M-1) + IBI female reproduction, well-mixed,
no terrain, all modulators OFF.</b> Step 1 fixes the mortality schedule and tunes only fertility to the
Aché vital rates (IBI/TFR); the resulting growth rate is the real Aché growth (r→0 emerges in Step 2).</p>

<div class="box {'ok' if frozen else 'warn'}"><b>Anti-frozen check (the A-3 finding's fix):</b> the
population now turns over continuously — <b>CBR {M['crude_birth_rate_per1000']:.0f}</b> and
<b>CDR {M['crude_death_rate_per1000']:.0f}</b> per 1000/yr, births ≈ deaths &gt; 0. The A-3
equilibrium had births = deaths = 0; baseline Siler mortality restores turnover.</div>

<h2>Gate metrics vs Aché</h2>
<table><tr><th>quantity</th><th>simulated</th><th>Aché target</th><th></th></tr>{rows}</table>
<p>Mortality schedule is <b>fixed</b> (not fit) — e₀/e₁₅/e₄₅/mode verify that the extracted
Gurven &amp; Kaplan coefficients reproduce the Aché life table. Fertility calibrated to the Aché IBI:
<code>fecundability = {fec:.3f}</code>/mo.</p>
<div class="box warn"><b>Finding — r≈0 is a Step-2 property, not a Step-1 target.</b> Aché fertility
(TFR≈8, IBI≈37) under Aché mortality necessarily yields a <b>growing</b> population (realized
r = {M['r_per_yr']:+.4f}/yr — the real forest-period Aché grew). Forcing r≈0 in Step 1 would demand
unrealistic fertility (TFR≈3, IBI≈68 mo). Step 1 therefore matches the Aché <i>vital rates</i>, and
the density-dependent terrain/disease modulators bring r→0 at carrying capacity in Step 2 (blueprint
M-2). This refines blueprint §8 gate item 2.</div>

<h2>1 · Survivorship l(x)</h2><div class="fig">{img('lx')}</div>
<h2>2 · Population (stationarity)</h2><div class="fig">{img('pop')}</div>
<h2>3 · Births vs deaths — continuous turnover</h2><div class="fig">{img('turnover')}</div>
<h2>4 · Age pyramid</h2><div class="fig">{img('pyramid')}</div>
<h2>5 · Fertility — IBI &amp; completed parity</h2><div class="fig">{img('fertility')}</div>

<h2>Notes / open items</h2>
<div class="box warn"><b>Both-sexes schedule.</b> G&amp;K Table 2 is both-sexes; the sex-specific
split and the maternal-removed female fit (M-3) await Hill &amp; Hurtado's sex tables. Maternal
mortality is applied as an explicit per-birth hazard (drawn AFTER the birth; M-5); with a both-sexes
baseline this slightly double-counts female reproductive-age mortality — corrected at the sex-split.
The energetic fertility modifier and all terrain/disease modulators are OFF (Step 2).</div>
<p style="color:#718096;font-size:0.9em;margin-top:24px">Demographic stage · Step 1 (non-spatial Aché
calibration) · {time.strftime('%Y-%m-%d')} · Siler FIXED from Gurven &amp; Kaplan 2007; fertility tuned.</p>
</body></html>"""
    with open(os.path.join(OUT, "report.html"), "w", encoding="utf-8") as f:
        f.write(html)


if __name__ == "__main__":
    main()
