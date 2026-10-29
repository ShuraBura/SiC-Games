"""R-106 Add.119 diagnosis: the period NON-STARVATION death rate by age, divided by the Aché Siler rate (the
schedule the model is built on). Exposure counters are person-MONTHS (the model's life_table divides by 12).
Positive control: the model's own life_table e0 must equal the e0 rebuilt here from the same counters."""
import glob, json, math, os, sys
sys.path.insert(0, os.path.join("sic_games", "src"))
from types import SimpleNamespace
from sic_games.phase1_model import TerrainWorld
OUT = "sic_games/outputs/substrate_run"
a1, b1, a2, a3, b3 = ((0.1611, 0.6775, 0.00813, 3.781e-5, 0.1025) if os.environ.get("SIL") == "natural" else (0.157, 0.721, 0.013, 4.8e-5, 0.103))
h = lambda t: a1 * math.exp(-b1 * t) + a2 + a3 * math.exp(b3 * t)
H = lambda t: (a1 / b1) * (1 - math.exp(-b1 * t)) + a2 * t + (a3 / b3) * (math.exp(b3 * t) - 1)
BANDS = [(0, 1), (1, 2), (2, 5), (5, 10), (10, 15), (15, 30), (30, 45), (45, 60), (60, 75)]


def siler_m(lo, hi, n=400):
    xs = [lo + (i + .5) * (hi - lo) / n for i in range(n)]
    return sum(math.exp(-H(x)) * h(x) for x in xs) / sum(math.exp(-H(x)) for x in xs)


K = ("lt_exposure", "lt_deaths", "lt_deaths_starv", "lt_deaths_senesc")
print("non-starvation period m(x) / Siler m(x); mean of 3 seeds")
print("Siler m:", " ".join(f"{lo}-{hi}:{siler_m(lo, hi):.4f}" for lo, hi in BANDS))
for w in ("temperate", "savanna", "montane"):
    for arm in os.environ.get("ARMS", "riskvg,cond,all4").split(","):
        rows = []
        for p in sorted(glob.glob(f"{OUT}/campaign_trajectory_s2_{w}_{arm}_s*.json")):
            m = json.load(open(p, encoding="utf-8"))["meta"]
            F, S = m["life_table_final"], m["life_table_snap"]
            lt = TerrainWorld.life_table(SimpleNamespace(**{k: list(F[k]) for k in K}), since={k: S[k] for k in K})
            r = []
            for lo, hi in BANDS:
                d = sum((F["lt_deaths"][a] - S["lt_deaths"][a]) - (F["lt_deaths_starv"][a] - S["lt_deaths_starv"][a])
                        for a in range(lo, hi))
                e = sum(F["lt_exposure"][a] - S["lt_exposure"][a] for a in range(lo, hi)) / 12.0
                r.append(d / e / siler_m(lo, hi))
            rows.append((lt["e0"], r))
        mean = [sum(x[1][i] for x in rows) / len(rows) for i in range(len(BANDS))]
        print(f"{w[:4]} {arm:6s} e0 {sum(x[0] for x in rows) / len(rows):5.2f} | "
              + " ".join(f"{lo}-{hi}:{v:.2f}" for (lo, hi), v in zip(BANDS, mean)))
