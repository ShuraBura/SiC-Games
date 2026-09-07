"""Score a run against the SUPERVISOR'S CRITERION: do villages prefer lush land over arid?

    py -3 sic_games/outputs/substrate_run/biome_report.py base_s0 [other_tag ...]

Stated by the supervisor 2026-08-17: "Successful test means rational population maps, where villages prefer
lush forest location to arid areas."

WHY THIS IS ITS OWN TOOL. Every spatial claim in this arc was scored against `forage_kcal`. Village siting is
governed by `S_pot = max(aquatic_food, cultivability)`, and the two are UNCORRELATED (+0.027) -- so the
existing report cannot answer this question at all. A biome breakdown is the only framing in which "lush
forest versus arid" is even expressible, because it is a statement about WHERE, not about a scalar.

THE TEST, stated before the run so it cannot be chosen to fit:
  PASS  people and sites are ENRICHED (>1) in forest/wetland and DEPLETED (<1) in desert.
  FAIL  either is enriched in desert, or forest is depleted.
Enrichment = (share of people in biome b) / (share of habitable cells in biome b). 1.0 = indifferent.
"""
from __future__ import annotations

import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
BIOME = {0: "water", 1: "wetland", 2: "forest", 3: "savanna", 4: "grass", 5: "desert", 6: "mountain"}
LUSH, ARID = ("forest", "wetland"), ("desert", "savanna")


def report(tags):
    for tag in tags:
        p = os.path.join(HERE, f"campaign_spatial_{tag}.npz")
        if not os.path.exists(p):
            print(f"!! no spatial dump for {tag}")
            continue
        d = np.load(p)
        if "s_pot" not in d.files:
            print(f"!! {tag} predates the S_pot dump -- re-run it; siting cannot be scored against forage")
            continue
        people, sites, biome = d["people"], d["sites"], d["biome"]
        spot, forage, hab = d["s_pot"], d["forage_kcal"], d["habitable"]
        m = hab > 0
        tot_p, tot_s, tot_c = people[m].sum(), sites[m].sum(), m.sum()
        print(f"\n=== {tag}  (step {int(d['step'])})  pop {int(tot_p):,}  sites {int(tot_s)} ===")
        print(f"  {'biome':<10}{'cells':>7}{'%land':>7}{'people':>8}{'%pop':>7}"
              f"{'ENRICH':>8}{'sites':>7}{'siteENR':>9}{'S_pot':>7}{'forage':>8}")
        rows = {}
        for code, name in BIOME.items():
            b = m & (biome == code)
            n = int(b.sum())
            if n == 0:
                continue
            pp, ss = int(people[b].sum()), int(sites[b].sum())
            share_c, share_p = n / tot_c, (pp / tot_p if tot_p else 0)
            share_s = ss / tot_s if tot_s else 0
            enr = share_p / share_c if share_c else float("nan")
            senr = share_s / share_c if share_c else float("nan")
            rows[name] = (enr, senr, n, share_c)
            print(f"  {name:<10}{n:>7}{100*share_c:>6.1f}%{pp:>8}{100*share_p:>6.1f}%"
                  f"{enr:>8.2f}{ss:>7}{senr:>9.2f}{spot[b].mean():>7.3f}{forage[b].mean():>8.0f}")
        print("\n  ENRICHMENT = share of people (or sites) / share of habitable cells.  1.00 = indifferent.")
        # SCORING GUARD -- BY STATISTICAL POWER, NOT BY CELL COUNT (2026-08-22).
        # First attempt used a flat "skip biomes under 30 cells / 5% of land". That was WRONG in a way worth
        # recording: it silently turned the mixed world's headline FAIL into a PASS by skipping its 19 desert
        # cells -- the exact finding the tool was built to surface. An arbitrary threshold that erases a real
        # result is worse than no guard.
        # The right question is not "how much land" but "could this deviation be chance". Under a Poisson
        # null of indifferent placement, expected = pop * share_of_land, and z = (obs - exp) / sqrt(exp).
        #   base_s0 desert : 19 cells, expected 33 people, observed 66  -> z = +5.7   REAL, must be scored
        #   savanna forest : 11 cells, expected 1.7,       observed 0   -> z = -1.3   noise, must be skipped
        MIN_EXPECTED, Z_CRIT = 10.0, 2.0
        scorable, skipped = {}, []
        for name, (enr, senr, ncells, share_c) in rows.items():
            exp = tot_p * share_c
            if exp < MIN_EXPECTED:
                skipped.append(f"{name}(exp {exp:.1f})")
                continue
            obs = enr * exp
            scorable[name] = (enr, senr, (obs - exp) / (exp ** 0.5))
        if skipped:
            print(f"  NOT SCORED -- too few people expected for any deviation to mean anything: "
                  f"{', '.join(sorted(skipped))}")
        verdict, why = "PASS", []
        for name in LUSH:
            if name in scorable and scorable[name][0] < 1.0 and scorable[name][2] < -Z_CRIT:
                verdict = "FAIL"
                why.append(f"{name} enrichment {scorable[name][0]:.2f} (z={scorable[name][2]:+.1f})")
        for name in ARID:
            if name in scorable and scorable[name][0] > 1.0 and scorable[name][2] > Z_CRIT:
                verdict = "FAIL"
                why.append(f"{name} enrichment {scorable[name][0]:.2f} (z={scorable[name][2]:+.1f})")
        if not any(n in scorable for n in LUSH + ARID):
            verdict = "NOT SCORABLE"
            why = ["no lush or arid biome carries enough people in this world to score"]
        print(f"  CRITERION (lush enriched, arid depleted): {verdict}"
              + ("   -- " + "; ".join(why) if why else ""))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    report(sys.argv[1:])
