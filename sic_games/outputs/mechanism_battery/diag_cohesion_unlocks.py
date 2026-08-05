"""Does restoring the cohesion headroom actually make the four dead mechanisms live?

R-106 Addendum 22: `cohesion_frac` is the ONLY consumer of the assabiyah, leader, repulsion and malnutrition
terms, and it is pinned at 1.0 for every led band — so `enable_size_repulsion`, `enable_dynamic_bands`,
`enable_malnutrition_fission` and the leader-coherence term are structurally inert AT ANY MAGNITUDE.

Restoring the headroom is only worth adopting if those mechanisms come back. So each is ABLATED out of the
stack twice: once under the baseline (where the prediction is "no change", because the clamp swallows it) and
once under the candidate (where the prediction is "changes the world"). A mechanism that stays identical
under BOTH is dead for some other reason.

`enable_malnutrition_fission` is the built-in negative control: its `malnutrition_fission_gain` is 0.0, so it
must stay INERT under both — if it moves, the instrument is measuring noise rather than the mechanism.

Run:  py -3 -u diag_cohesion_unlocks.py
Env:  U_STEPS (300) U_N (1500) U_SEEDS (0,1)
"""
import os
import sys

ROOT = r"C:\Users\syatom\Projects\SiC Games"
for _p in (os.path.join(ROOT, "sic_games", "src"),
           os.path.join(ROOT, "sic_games", "outputs", "phase1_social_evolution"),
           os.path.join(ROOT, "sic_games", "outputs", "mechanism_battery")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import battery1_liveness as B1                                        # noqa: E402
from sic_games import runconfig                                       # noqa: E402

STEPS = int(os.environ.get("U_STEPS", "300"))
N = int(os.environ.get("U_N", "1500"))
SEEDS = [int(s) for s in os.environ.get("U_SEEDS", "0,1").split(",") if s]

CANDIDATE = {"enable_leaky_assabiyah": True, "cohesion_leader_weight": 0.25}
# Everything whose ONLY consumer is cohesion_frac, plus the negative control.
ABLATE = ["enable_size_repulsion", "enable_dynamic_bands", "enable_emergent_band_size",
          "enable_malnutrition_fission"]


def sig(over, seed):
    stack = dict(runconfig.load().get("DemographyConfig", {}))
    stack.update(over)
    s, _, _ = B1.signature(stack, steps=STEPS, n=N, patch=30, terr="coastal", clim="temperate", seed=seed)
    return s


def main():
    print(f"[cohesion unlocks] n={N} steps={STEPS} seeds={SEEDS}")
    print(f"[cohesion unlocks] candidate = {CANDIDATE}\n")
    print(f"{'mechanism ablated':>32} {'under baseline':>15} {'under candidate':>16}")
    for flag in ABLATE:
        verdict = {}
        for label, base in (("baseline", {}), ("candidate", CANDIDATE)):
            diffs = 0
            for sd in SEEDS:
                on = sig(dict(base), sd)
                off = sig(dict(base, **{flag: False}), sd)
                diffs += (on != off)
            verdict[label] = diffs
        b, c = verdict["baseline"], verdict["candidate"]
        fmt = lambda d: ("LIVE %d/%d" % (d, len(SEEDS))) if d else "inert 0/%d" % len(SEEDS)
        note = ""
        if not b and c:
            note = "   <- UNLOCKED by the fix"
        elif not b and not c:
            note = "   (dead for another reason)"
        print(f"{flag.replace('enable_',''):>32} {fmt(b):>15} {fmt(c):>16}{note}", flush=True)
    print("\nmalnutrition_fission is the NEGATIVE CONTROL: its gain is 0.0, so it must read inert under both.")
    print("A mechanism inert under the baseline and LIVE under the candidate is one the clamp was swallowing.")


if __name__ == "__main__":
    main()
