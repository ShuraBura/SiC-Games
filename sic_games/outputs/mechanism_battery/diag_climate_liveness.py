"""Does each climate channel REACH THE WORLD? One campaign arm per channel, against a shared control.

`test_climate_channels.py` proves each channel behaves correctly as a field — right period, right depth, right
mask, refused when neutral. That is not the same as reaching the demography: `settle_tier2_yield` was
dimensionally correct and 0.012% of tier-1, and R-106's intake-mobility mode is wired, tested and never
selected. So each channel also has to move a running world.

Every arm is the same build, same session, same seed, same steps; the ONLY difference is one climate flag.
An arm that is byte-identical to the control has not reached the world, whatever the unit tests say.

Run:  py -3 -u diag_climate_liveness.py
Env:  L_STEPS (300) L_FOUNDERS (1500) L_SEEDS (0,1) L_PAR (6) L_MAXMIN (20)
"""
import json
import os
import statistics
import subprocess
import sys
import time

ROOT = r"C:\Users\syatom\Projects\SiC Games"
CAMP = os.path.join(ROOT, "sic_games", "outputs", "substrate_run")
LOGDIR = os.path.dirname(os.path.abspath(__file__))

STEPS = os.environ.get("L_STEPS", "300")
FOUNDERS = os.environ.get("L_FOUNDERS", "1500")
SEEDS = [s for s in os.environ.get("L_SEEDS", "0,1").split(",") if s]
PAR = int(os.environ.get("L_PAR", "6"))
MAXMIN = os.environ.get("L_MAXMIN", "20")

# Each channel, with the magnitudes it needs. The lottery would supply these, but naming them here keeps the
# arm reproducible and keeps the value under test visible rather than drawn.
CHANNELS = {
    "interannual":      dict(C_CLIM_ON="enable_interannual",
                             C_CLIMPARAM="interannual_amp=0.30,interannual_period=60"),
    # RECURRENCE, not duration, sets whether an excursion is ever SEEN. The lit value is 1000-2000 yr =
    # 12000-24000 steps; over a 300-step arm that is a ~2.5% chance of a single onset, and the first pass
    # duly reported the channel INERT when it had simply never fired. The onset rate here is shortened so the
    # arm tests the CHANNEL rather than the waiting time; the lit recurrence is what a long run should use.
    "regime_shift":     dict(C_CLIM_ON="enable_regime_shift",
                             C_CLIMPARAM="regime_amp=0.15,regime_duration=120,regime_recurrence=200"),
    "eccentricity":     dict(C_CLIM_ON="enable_eccentricity_mean", C_CLIMPARAM="mean_factor=1.15"),
    # GRASS_STEPPE is the TEMPERATE/arctic grass sub-biome, so a tropical world has zero steppe cells and the
    # herd swing cannot act there. That is about the world, not the mechanism — so this arm runs temperate.
    "caribou_swing":    dict(C_CLIM_ON="enable_caribou_swing",
                             C_CLIMPARAM="caribou_amp=0.871,caribou_period=600",
                             C_TERR="flat", C_CLIM="temperate"),
    "no_intercept":     dict(C_CLIM_OFF="enable_intercept_hunting"),
    "no_seasonality":   dict(C_CLIM_OFF="enable_seasonality"),
    # The flood rides the ENSO clock — it IS the llanos ENSO, not a parallel process — so its arm carries the
    # interannual channel and is scored against the interannual arm, not the plain control.
    "llanos_flood":     dict(C_CLIM_ON="enable_interannual,enable_llanos_flood",
                             C_CLIMPARAM="interannual_amp=0.30,interannual_period=60,llanos_flood_amp=0.40"),
}
BASELINE = {"llanos_flood": "interannual"}          # channel -> the arm it must differ from (control if absent)

STACK = dict(C_ALLON="1", C_SOIL="1", C_ABANDON="1", C_IMPROVED="0", C_GENEA="0")
# SAVANNA is the default world, not tropical. The savanna-keyed channels (C.5 intercept, C.4c llanos) are
# where the population is: measured 35.3% of agents on an eligible cell in flat-savanna against 0.0% in
# flat-tropical, and 52-67% of the capacity patch against 0-0.6%. A tropical world produces a false INERT
# for both — which is exactly what the first pass of this check reported.
WORLD = dict(C_TERR="flat", C_CLIM="savanna")


def head_sha():
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
                              capture_output=True, text=True).stdout.strip()
    except Exception:
        return ""


HEAD = head_sha()


def load(tag):
    p = os.path.join(CAMP, f"campaign_trajectory{tag}.json")
    if not os.path.exists(p):
        return None
    try:
        return json.load(open(p, encoding="utf-8"))
    except Exception:
        return None


def sig(d):
    """A compact signature of the run: the pop series plus a few marker medians."""
    t = d["traj"]
    return dict(pop=[r["pop"] for r in t],
                markers={k: statistics.median([r[k] for r in t[len(t) // 2:] if r.get(k) is not None] or [0])
                         for k in ("band_med", "n_bands", "deaths_starv", "density_per_km2")})


def run(arms):
    todo, running = list(arms), []
    while todo or running:
        while todo and len(running) < PAR:
            tag, env_over = todo.pop(0)
            # WORLD first, then the arm's own overrides on top — `dict(**a, **b)` raises on a duplicate key
            # rather than letting the later one win, so the merge has to be explicit.
            env = dict(os.environ, **STACK, **WORLD)
            env.update(env_over)
            env.update(C_TAG=tag, C_FOUNDERS=FOUNDERS, C_STEPS=STEPS, C_MAXMIN=MAXMIN,
                       C_LOGEVERY=str(max(10, int(STEPS) // 10)))
            out = open(os.path.join(LOGDIR, f"climlive{tag}.log"), "w")
            running.append((tag, subprocess.Popen([sys.executable, "-u",
                                                   os.path.join(CAMP, "run_campaign.py")],
                                                  cwd=ROOT, env=env, stdout=out,
                                                  stderr=subprocess.STDOUT), out))
            print(f"    launched {tag}", flush=True)
        time.sleep(8)
        for it in list(running):
            tag, p, o = it
            if p.poll() is not None:
                o.close(); running.remove(it)
                if p.returncode != 0:
                    tail = open(os.path.join(LOGDIR, f"climlive{tag}.log"), encoding="utf-8",
                                errors="replace").read()[-1200:]
                    raise SystemExit(f"arm {tag} failed rc={p.returncode}\n{tail}")


def main():
    print(f"[climate liveness] build {HEAD} | world {WORLD['C_TERR']}-{WORLD['C_CLIM']} | "
          f"{STEPS} steps x {len(SEEDS)} seed(s)")
    # A channel that overrides the world needs its OWN control in that world — comparing a temperate arm
    # against a tropical control would measure the world, not the channel.
    def world_of(over):
        return (over.get("C_TERR", WORLD["C_TERR"]), over.get("C_CLIM", WORLD["C_CLIM"]))

    ctl_tag = {}
    arms, seen = [], set()
    for sd in SEEDS:
        for name, over in [("", {})] + list(CHANNELS.items()):
            terr, clim = world_of(over)
            key = (terr, clim, sd)
            if key not in seen:
                seen.add(key)
                arms.append((f"_cl_ctl_{terr}_{clim}_s{sd}", dict(C_SEED=sd, C_TERR=terr, C_CLIM=clim)))
            if name:
                ctl_tag[(name, sd)] = f"_cl_ctl_{terr}_{clim}_s{sd}"
                arms.append((f"_cl_{name}_s{sd}", dict(C_SEED=sd, **over)))
    run(arms)

    print(f"\n{'channel':>16} {'seed':>5} {'identical?':>11} {'pop end':>9} {'vs base':>9}   markers moved")
    verdict = {}
    for name in CHANNELS:
        for sd in SEEDS:
            base_name = BASELINE.get(name)
            b = load(f"_cl_{base_name}_s{sd}") if base_name else load(ctl_tag[(name, sd)])
            a = load(f"_cl_{name}_s{sd}")
            if not a or not b:
                print(f"{name:>16} {sd:>5}   (missing arm)"); continue
            sa, sb = sig(a), sig(b)
            same = sa["pop"] == sb["pop"]
            moved = [k for k in sa["markers"]
                     if sb["markers"][k] and abs(sa["markers"][k] - sb["markers"][k])
                     / abs(sb["markers"][k]) > 0.02]
            d = (sa["pop"][-1] - sb["pop"][-1]) / max(1, sb["pop"][-1])
            print(f"{name:>16} {sd:>5} {'IDENTICAL' if same else 'differs':>11} "
                  f"{sa['pop'][-1]:>9} {d:>+8.1%}   {','.join(moved) if moved else '-'}")
            verdict.setdefault(name, []).append(not same)

    print("\n=== VERDICT ===")
    for name, res in verdict.items():
        ok = all(res)
        base = BASELINE.get(name, "control")
        print(f"  {name:>16}  {'REACHES THE WORLD' if ok else 'INERT — identical to ' + base}"
              f"   ({sum(res)}/{len(res)} seeds differ)")
    dead = [n for n, r in verdict.items() if not all(r)]
    if dead:
        print(f"\n{len(dead)} channel(s) do not reach the world: {', '.join(dead)}")
        print("That is the same class as an ON-but-dead flag — the field is correct and nothing reads it.")


if __name__ == "__main__":
    main()
