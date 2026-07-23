"""R-103d — material inheritance x property substrate sweep (registered design: R103_material_inheritance_design.md).

Does bequeathing durable capital convert BIG MEN (office advantage) into CHIEFS (heritable lineage estate)?
And does it need a property SUBSTRATE (ownable land) to bite? 6 cells in ONE cultivable world (coastal-tropical:
high cultivability so improved_land bites, moderate pop unlike flat-tropical). Predictions committed in the note.
"""
import os, subprocess, sys, time, json

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))

TERR, CLIM = "coastal", "tropical"
STEPS = os.environ.get("R103D_STEPS", "3000")
FOUNDERS = os.environ.get("R103D_FOUNDERS", "3000")
MAXMIN = os.environ.get("R103D_MAXMIN", "30")

# R-103e grid: the full mechanism is inheritance(primogeniture)+heir-by-status ON throughout; the SWEEP axes are
# EXEMPTION (legitimacy waives wealth-leveling — the load-bearing ch.16 device) x SUBSTRATE (improved_land).
# (cell, inherit, heir_by_status, exempt, improved_land)
CELLS = [
    ("1_baseline",         "0", "0", "0", "0"),   # nothing — big-man baseline (reproduces R-103c)
    ("2_inh_only",         "1", "1", "0", "0"),   # inheritance+heirstat, no protection, no land → leveling wins
    ("3_exempt_noland",    "1", "1", "1", "0"),   # protection WITHOUT an ownable estate → concentrate?
    ("4_land_noexempt",    "1", "1", "0", "1"),   # ownable estate WITHOUT protection → still deposed?
    ("5_FULL",             "1", "1", "1", "1"),   # FULL MECHANISM: exemption + substrate → chiefs?
]

STACK = dict(C_ELITE="1", C_BRANCH="0.05", C_SPLIT="0.00003", C_SPLITMIN="8",
             C_RELLEGIT="1", C_RELMULT="2.0", C_RELRES="1", C_RESACC="1", C_RESVIL="1",
             C_RESYTR="80", C_LOCASC="1", C_RANKHIER="1", C_GENEA="0", C_RESIDENCE="virilocal",
             C_DEFEND="1", C_MATRULE="primogeniture")   # improved_land needs defensibility on

PROG = os.path.join(HERE, "r103d_progress.txt")


def log(m):
    with open(PROG, "a", encoding="utf-8") as f:
        f.write(m + "\n"); f.flush()
    print(m, flush=True)


if __name__ == "__main__":
    open(PROG, "w").close()
    log(f"R-103d inheritance x substrate: {len(CELLS)} cells x {STEPS} steps in {TERR}-{CLIM}")
    t0 = time.time()
    done = []
    for i, (cell, inh, heir, exe, imp) in enumerate(CELLS, 1):
        tag = f"_r103d_{cell}"
        env = dict(os.environ, C_TAG=tag, C_TERR=TERR, C_CLIM=CLIM, C_STEPS=STEPS, C_FOUNDERS=FOUNDERS,
                   C_MAXMIN=MAXMIN, C_MATINHERIT=inh, C_HEIRSTAT=heir, C_NOBLEXEMPT=exe, C_IMPROVED=imp, **STACK)
        log(f"[{i}/{len(CELLS)}] {cell:16s} inh={inh} heir={heir} exempt={exe} land={imp}  (elapsed {(time.time()-t0)/60:.0f}m)")
        r = subprocess.run([sys.executable, "-u", os.path.join(HERE, "run_campaign.py")],
                           cwd=ROOT, env=env, capture_output=True, text=True)
        if r.returncode != 0:
            log(f"      rc={r.returncode} STDERR: {r.stderr.strip()[-300:]}"); continue
        try:
            m = json.load(open(os.path.join(HERE, f"campaign_trajectory{tag}.json"), encoding="utf-8"))
            row = m["traj"][-1]; done.append((cell, row))
            log(f"      steps={m['meta'].get('steps_completed')} pop={row['pop']} "
                f"noble_matl_lift={row.get('noble_material_lift')} leader_matl_lift={row.get('leader_material_lift')} "
                f"gini_matl={row.get('gini_material')} village_gap_d={row.get('village_gap_d_med')} "
                f"frac_broken={row.get('frac_villages_broken')}")
        except Exception as e:
            log(f"      (readback failed: {e})")
    log(f"\nR-103d DONE in {(time.time()-t0)/60:.0f} min")
    log("SUMMARY — does the LINEAGE hold a heritable estate? (noble_material_lift > 1 = chief signal)")
    for cell, row in done:
        log(f"   {cell:18s} noble_matl={row.get('noble_material_lift')}  gap_d={row.get('village_gap_d_med')}  "
            f"broken={row.get('frac_villages_broken')}  strat={row.get('pct_stratified')}%")
