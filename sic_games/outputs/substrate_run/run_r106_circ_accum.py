"""R-106 — the circumscription gradient RE-RUN with the accumulation stack actually ON.

R-104 Phase 2 asked "does bounding the land wake the GOODS axis?" (Carneiro / Nieboer-Domar) and read a flat
material lift of 0.99-1.07 across a 5x reduction in habitable land. That reading is VOID: the R-104 `STACK`
omitted every flag that lets goods compound, so the arms ran with

    enable_material_inheritance = False   (the estate dissolves at death)
    enable_lineage_tribute      = False
    enable_noble_leveling_exemption = False
    enable_ascribed_mate_choice = False
    material_decay              = 0.002   (and what remains erodes)

i.e. material could not accumulate across generations BY CONSTRUCTION. A flat lift is the expected output of
that configuration and carries no information about circumscription. Those mechanisms were built default-off in
R-103d/e/f and were never added to the campaign stack.

This re-runs the same four patches with the accumulation stack ON, everything else matched to R-104 Phase 2, so
the comparison is the accumulation stack and nothing else. Arms run CONCURRENTLY (deterministic, seeded).

Run:  py -3 -u sic_games/outputs/substrate_run/run_r106_circ_accum.py       (from repo root)
"""
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))

PATCHES = [40, 30, 24, 18]                             # 1584 / 884 / 560 / 308 habitable cells (R-104 P2)

# R-104's STACK verbatim ...
STACK = dict(C_ELITE="1", C_BRANCH="0.05", C_SPLIT="0.00003", C_SPLITMIN="8",
             C_RELLEGIT="1", C_RELMULT="2.0", C_RELRES="1", C_RESACC="1", C_RESVIL="1",
             C_RESYTR="80", C_LOCASC="1", C_RANKHIER="1", C_GENEA="0", C_RESIDENCE="virilocal",
             C_DEFEND="1")
# ... plus the accumulation chain that was missing (roadmap links 2/3/4/6).
ACCUM = dict(C_MATINHERIT="1", C_MATRULE="primogeniture", C_HEIRSTAT="1",
             C_LINTRIBUTE="1", C_TRIBFRAC="0.15", C_NOBLEXEMPT="1", C_ENDOGAMY="1")

PROG = os.path.join(HERE, "r106_progress.txt")
KEYS = ("pop", "noble_material_lift", "gini_material", "mean_material", "noble_lineage_size_lift",
        "lineage_size_gini", "pct_stratified", "village_gap_d_med", "ascribed_frac", "surplus_med")


def log(m):
    with open(PROG, "a", encoding="utf-8") as f:
        f.write(m + "\n"); f.flush()
    print(m, flush=True)


if __name__ == "__main__":
    open(PROG, "w").close()
    t0 = time.time()
    log(f"R-106: circumscription x accumulation-stack-ON, patches {PATCHES} @ 5000 steps")
    log("  (R-104 P2 is the matched control: same patches, accumulation stack OFF)")

    procs = {}
    for P in PATCHES:
        tag = f"_r106_circ_p{P}"
        env = dict(os.environ, C_TAG=tag, C_TERR="coastal", C_CLIM="temperate", C_IMPROVED="0",
                   C_SEED="0", C_FOUNDERS="3000", C_PATCH=str(P), C_STEPS="5000",
                   C_MAXMIN="120", C_LOGEVERY="250", **STACK, **ACCUM)
        out = open(os.path.join(HERE, f"r106_stdout{tag}.txt"), "w", encoding="utf-8")
        procs[P] = (tag, subprocess.Popen([sys.executable, "-u", os.path.join(HERE, "run_campaign.py")],
                                          cwd=ROOT, env=env, stdout=out, stderr=subprocess.STDOUT, text=True), out)
        log(f"  launched patch {P}")

    for P, (tag, p, out) in procs.items():
        p.wait(); out.close()
        log(f"  finished patch {P} rc={p.returncode} (elapsed {(time.time()-t0)/60:.0f}m)")

    log("\n=== R-106 vs R-104 P2 (same patches, accumulation stack the ONLY difference) ===")
    for P in PATCHES:
        row = {}
        for name, tag in (("accum ON ", f"_r106_circ_p{P}"), ("accum OFF", f"_r104_circ_p{P}")):
            f = os.path.join(HERE, f"campaign_trajectory{tag}.json")
            if not os.path.exists(f):
                continue
            d = json.load(open(f, encoding="utf-8"))
            hc = d["meta"].get("habitable_cells", 0)
            r = d["traj"][-1]
            row[name] = (hc, r)
        log(f"\npatch {P}:")
        for name, (hc, r) in row.items():
            log(f"  {name} habitable={hc} density={r['pop']/hc:.2f}/cell  " +
                " ".join(f"{k}={r.get(k)}" for k in KEYS))

    log(f"\nR-106 DONE in {(time.time()-t0)/60:.0f} min")
