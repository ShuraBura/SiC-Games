"""THE TWO FOOD MODELS MUST AGREE — a per-biome consistency diagnostic.

WHY THIS EXISTS (2026-08-08). This model carries **two independent descriptions of how much food a cell holds**,
and nothing ever compared them:

  * `NPPCapacityField(mode="tallavaara")` — an NPP → forager-density regression. Sets the CARRYING CAPACITY the
    demographic substrate relaxes toward.
  * `forage_kcal` + `game_kcal` — per-biome return rates from the literature table. This is what agents
    ACTUALLY EAT.

Neither knows about the other. A biome can be rich in one and poor in the other, and the run will look
sensible: the capacity field reports a healthy world while agents starve in it.

**MEASURED across four worlds.** The ratio capacity ÷ delivery clusters tightly for four biomes and is wildly
out for two:

    forest 2.2 · mountain 2.6 · grass 2.7 · desert 2.7   <- the CLUSTER
    wetland 14.0 · savanna 16.9                          <- OUTLIERS, ~6x the cluster

The cluster is a DEFINITIONAL offset, not a defect: Tallavaara gives an equilibrium density (what the land
sustains long-run) while the return-rate table gives a theoretical maximum harvest (what a forager could take
at the mean rate for the whole foraging day). Capacity exceeding delivery by ~2-3x everywhere is expected.

The two outliers are NOT that, and both trace to gaps the return-rate table already documents:

  * **savanna forage = 257.7 kcal/hr** — the Hadza *single-activity tuber* rate, which replaced a whole-diet
    aggregate (Marlowe 2010, 343-795). A single-activity post-encounter rate is being used as a whole-biome,
    whole-diet rate. Real foragers eat from many resources: the Hiwi's 2,043 cal/day comes from thirteen.
  * **wetland game = 0** — UNANCHORED, and the table says so explicitly ("a gap, not a measured zero").
    Mountain also has zero game but its forage (5,387) compensates, which is why it stays in the cluster.

CONSEQUENCE, measured on `world_savanna`: savanna is 48% of that world's land, and the world settles at **9%
of its trough-limited capacity** while temperate and montane reach 51% and 69%. The population is not
Malthusian-limited; it is limited by a food field that disagrees with the capacity field it is compared to.
"""
from __future__ import annotations

BIOME_NAMES = {0: "water", 1: "wetland", 2: "forest", 3: "savanna",
               4: "grass", 5: "desert", 6: "mountain"}

# The cluster measured across coastal-temperate, coastal-savanna, mountainous-savanna and mountainous-tropical.
# A biome outside this band is not necessarily wrong, but it is not explained by the definitional offset and
# must be looked at.
CLUSTER_LO, CLUSTER_HI = 1.5, 5.0

MIN_CELLS = 80          # below this a biome's mean is noise, not a measurement


def per_biome(fields, capacity_field, burn: float, hours_per_day: float = 6.0,
              days_per_step: int = 30, min_cells: int = MIN_CELLS) -> dict:
    """{biome_name: {...}} comparing NPP-derived capacity against return-rate delivery, per biome.

    `capacity` is persons/cell from the capacity field; `delivery` is persons/cell the return rates can feed
    at the mean rate for a full foraging day. Their RATIO is the diagnostic — the absolute values are on
    different definitions and are not meant to match.
    """
    import numpy as np

    biome = np.asarray(fields.biome)
    land = np.asarray(fields.isWater) == 0
    out: dict = {}
    for code, name in BIOME_NAMES.items():
        if code == 0:
            continue
        m = (biome == code) & land
        n = int(m.sum())
        if n < min_cells:
            continue
        lv = [capacity_field.level(x, y) for y in range(biome.shape[0]) for x in range(biome.shape[1])
              if m[y, x] and capacity_field.level(x, y) > 0]
        if not lv:
            continue
        capacity = (sum(lv) / len(lv)) / burn
        rate = float(fields.forage_kcal[m].mean()) + float(fields.game_kcal[m].mean())
        delivery = rate * hours_per_day * days_per_step / burn
        ratio = (capacity / delivery) if delivery > 0 else float("inf")
        out[name] = {
            "cells": n,
            "capacity_per_cell": round(capacity, 2),
            "delivery_per_cell": round(delivery, 2),
            "ratio": round(ratio, 1),
            "forage_kcal_hr": round(float(fields.forage_kcal[m].mean()), 0),
            "game_kcal_hr": round(float(fields.game_kcal[m].mean()), 0),
            "verdict": ("CONSISTENT" if CLUSTER_LO <= ratio <= CLUSTER_HI else
                        "STARVES" if ratio > CLUSTER_HI else "OVERFEEDS"),
        }
    return out


def complaints(report: dict) -> list[str]:
    """One line per biome whose two food models disagree beyond the definitional offset. Empty when clean, so
    a run only prints when there is something to say."""
    out = []
    for name, r in sorted(report.items(), key=lambda kv: -kv[1]["ratio"]):
        if r["verdict"] == "CONSISTENT":
            continue
        why = []
        if r["game_kcal_hr"] == 0:
            why.append("game UNANCHORED (0)")
        if r["forage_kcal_hr"] < 500:
            why.append(f"forage only {r['forage_kcal_hr']:.0f} kcal/hr")
        out.append(
            f"{name}: capacity {r['capacity_per_cell']}/cell vs delivery {r['delivery_per_cell']}/cell "
            f"= {r['ratio']}x ({r['verdict']}, {r['cells']} cells"
            + (f"; {', '.join(why)}" if why else "") + ")")
    return out
