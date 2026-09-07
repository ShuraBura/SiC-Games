"""R-104 — OVERNIGHT: seed replication → circumscription gradient → deep time.

PHASE 1 (priority, ~9.5h) — SEED REPLICATION. Every result in the R-103 arc is n=1 per cell, including the
headline wealth-in-people finding (noble lineage_size_lift 3.3-5.8x). This puts ERROR BARS on it for the first
time, and settles the R-103h anomaly (coastal-tropical+agri inverted to 1.11x on a single seed).
  5 seeds x 3 cells, FIXED 5000-step horizon so every arm is compared at the SAME step (D15: R-103h's wall-clock
  budget truncated arms at 2250-14075 steps, which quietly invalidates cross-arm comparison).

PHASE 2 (~2.5h) — CIRCUMSCRIPTION GRADIENT (Carneiro). R-103h could not wake the GOODS axis with improved_land
because worked land is not scarcity. TRUE circumscription = a bounded capacity window (NPPCapacityField masks
capacity to a sub-window, ZERO outside) so the population cannot disperse out. Smoke test: patch 18 => 308
habitable cells (vs 1584), density 8.8/cell, and stratification leapt to 69.7%. This walks the gradient to see
whether bounding the land makes MATERIAL finally concentrate (Nieboer-Domar: elites hold goods only where labour
cannot walk away).

PHASE 3 (leftover hours) — DEEP TIME. Every R-103h arm truncated; the stack has never run deep. Is the
aristocracy stable, does it ratchet, does it collapse?

Safe unsupervised: runs only, no new model mechanism. C_PATCH is SELF-VERIFYING (meta.habitable_cells reports the
realised bounded area). Sleep-aware compute budget per arm. Phases ordered so the priority completes first.
"""
import os, subprocess, sys, time, json, statistics

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))

SEEDS = [0, 1, 2, 3, 4]
STEPS_P1 = os.environ.get("R104_STEPS", "5000")       # a horizon EVERY arm reaches inside budget => comparable
MAXMIN_P1 = os.environ.get("R104_MAXMIN", "60")       # backstop; should not bind at 5000 steps

# (cell, terr, clim, improved_land)
CELLS = [
    ("base_ctemp_forage", "coastal", "temperate", "0"),   # R-64 validated world -> error bar on the headline
    ("ctrop_forage",      "coastal", "tropical",  "0"),   # the anomaly's CONTROL
    ("ctrop_agri",        "coastal", "tropical",  "1"),   # the R-103h ANOMALY (lift inverted to 1.11 on 1 seed)
]
PATCHES = [40, 30, 24, 18]                            # phase 2: 1584 / 884 / ~560 / 308 habitable cells

STACK = dict(C_ELITE="1", C_BRANCH="0.05", C_SPLIT="0.00003", C_SPLITMIN="8",
             C_RELLEGIT="1", C_RELMULT="2.0", C_RELRES="1", C_RESACC="1", C_RESVIL="1",
             C_RESYTR="80", C_LOCASC="1", C_RANKHIER="1", C_GENEA="0", C_RESIDENCE="virilocal", C_DEFEND="1")

PROG = os.path.join(HERE, "r104_progress.txt")
KEYS = ("noble_lineage_size_lift", "lineage_size_gini", "noble_material_lift",
        "noble_cred_lift", "pct_stratified", "gini_material", "pop")


def log(m):
    with open(PROG, "a", encoding="utf-8") as f:
        f.write(m + "\n"); f.flush()
    print(m, flush=True)


def run(tag, **env_over):
    env = dict(os.environ, C_TAG=tag, C_FOUNDERS="3000", **STACK, **env_over)
    r = subprocess.run([sys.executable, "-u", os.path.join(HERE, "run_campaign.py")],
                       cwd=ROOT, env=env, capture_output=True, text=True)
    if r.returncode != 0:
        log(f"      rc={r.returncode} STDERR: {r.stderr.strip()[-300:]}")
        return None
    try:
        d = json.load(open(os.path.join(HERE, f"campaign_trajectory{tag}.json"), encoding="utf-8"))
        return d["meta"], d["traj"][-1]
    except Exception as e:
        log(f"      (readback failed: {e})")
        return None


def ci(vals):
    """mean +/- 95% CI (t~2.78 at n=5, df=4). Returns the string the report needs."""
    if not vals:
        return "n/a"
    m = statistics.mean(vals)
    if len(vals) < 2:
        return f"{m:.3f} (n=1)"
    sd = statistics.stdev(vals)
    h = 2.776 * sd / (len(vals) ** 0.5)
    return f"{m:.3f} +/- {h:.3f} (sd {sd:.3f}, n={len(vals)})"


if __name__ == "__main__":
    open(PROG, "w").close()
    t0 = time.time()
    log(f"R-104 overnight: P1 replication {len(SEEDS)}x{len(CELLS)} @ {STEPS_P1} steps | "
        f"P2 circumscription {len(PATCHES)} | P3 deep time")

    # ── PHASE 1 — seed replication ──────────────────────────────────────────────────────────────────
    log("\n=== PHASE 1: SEED REPLICATION ===")
    p1: dict = {c[0]: {k: [] for k in KEYS} for c in CELLS}
    for cell, terr, clim, imp in CELLS:
        for sd in SEEDS:
            tag = f"_r104_{cell}_s{sd}"
            log(f"[P1] {cell:20s} seed={sd}  (elapsed {(time.time()-t0)/60:.0f}m)")
            got = run(tag, C_TERR=terr, C_CLIM=clim, C_IMPROVED=imp, C_SEED=str(sd),
                      C_STEPS=STEPS_P1, C_MAXMIN=MAXMIN_P1, C_LOGEVERY="250")
            if not got:
                continue
            meta, row = got
            for k in KEYS:
                if row.get(k) is not None:
                    p1[cell][k].append(row[k])
            log(f"      steps={meta.get('steps_completed')} pop={row['pop']} "
                f"linLift={row.get('noble_lineage_size_lift')} linGini={row.get('lineage_size_gini')} "
                f"matl={row.get('noble_material_lift')} strat={row.get('pct_stratified')}%")
        log(f"  --> {cell}: linLift {ci(p1[cell]['noble_lineage_size_lift'])}")

    log("\n=== PHASE 1 SUMMARY (mean +/- 95% CI over seeds) ===")
    for cell, *_ in CELLS:
        log(f"  {cell}")
        for k in ("noble_lineage_size_lift", "lineage_size_gini", "noble_material_lift", "pct_stratified"):
            log(f"      {k:26s} {ci(p1[cell][k])}")

    # ── PHASE 2 — circumscription gradient ──────────────────────────────────────────────────────────
    log("\n=== PHASE 2: CIRCUMSCRIPTION GRADIENT (Carneiro; does bounding the land wake the GOODS axis?) ===")
    for P in PATCHES:
        tag = f"_r104_circ_p{P}"
        log(f"[P2] patch={P}  (elapsed {(time.time()-t0)/60:.0f}m)")
        got = run(tag, C_TERR="coastal", C_CLIM="temperate", C_IMPROVED="0", C_SEED="0",
                  C_PATCH=str(P), C_STEPS=STEPS_P1, C_MAXMIN=MAXMIN_P1, C_LOGEVERY="250")
        if not got:
            continue
        meta, row = got
        hc = meta.get("habitable_cells", 0)
        log(f"      habitable={hc} density={row['pop']/hc:.2f}/cell pop={row['pop']} "
            f"| GOODS matl={row.get('noble_material_lift')} giniMatl={row.get('gini_material')} "
            f"| PEOPLE linLift={row.get('noble_lineage_size_lift')} | strat={row.get('pct_stratified')}%")

    # ── PHASE 3 — deep time (uses whatever hours remain) ────────────────────────────────────────────
    log("\n=== PHASE 3: DEEP TIME ===")
    for tag, mm in (("_r104_deep_forage", "240"),):
        log(f"[P3] {tag} (budget {mm}m)  (elapsed {(time.time()-t0)/60:.0f}m)")
        got = run(tag, C_TERR="coastal", C_CLIM="temperate", C_IMPROVED="0", C_SEED="0",
                  C_STEPS="30000", C_MAXMIN=mm, C_LOGEVERY="250")
        if got:
            meta, row = got
            log(f"      steps={meta.get('steps_completed')} trunc={meta.get('truncated')} pop={row['pop']} "
                f"linLift={row.get('noble_lineage_size_lift')} linGini={row.get('lineage_size_gini')} "
                f"strat={row.get('pct_stratified')}%")

    log(f"\nR-104 DONE in {(time.time()-t0)/60:.0f} min")
