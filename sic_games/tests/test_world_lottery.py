"""World-lottery — a diverse per-world knob ensemble (forest/savanna/desert/montane/mixed). Locks: (1) determinism
(same seed → same knobs); (2) archetype cycling covers all types; (3) drawn knobs stay in the archetype's ranges;
(4) forced-archetype override; (5) generate_world accepts the lottery knobs."""
from __future__ import annotations

from sic_games.terrain import world_lottery, generate_world, WORLD_ARCHETYPES, WORLD_ARCHETYPE_ORDER


def test_deterministic():
    assert world_lottery(3) == world_lottery(3)                       # same seed → identical knobs
    assert world_lottery(3)["seedStr"] != world_lottery(4)["seedStr"]


def test_archetype_cycling_covers_all_types():
    got = {world_lottery(s)["archetype"] for s in range(len(WORLD_ARCHETYPE_ORDER))}
    assert got == set(WORLD_ARCHETYPE_ORDER)                          # seeds 0..N-1 cover every archetype
    assert world_lottery(0)["archetype"] == world_lottery(len(WORLD_ARCHETYPE_ORDER))["archetype"]   # cycles


def test_knobs_within_archetype_ranges():
    for seed in range(15):
        k = world_lottery(seed)
        ranges = WORLD_ARCHETYPES[k["archetype"]]
        for knob, (lo, hi) in ranges.items():
            assert lo <= k[knob] <= hi, (seed, knob, k[knob])


def test_forced_archetype():
    for arch in WORLD_ARCHETYPE_ORDER:
        assert world_lottery(0, archetype=arch)["archetype"] == arch


def test_generate_world_accepts_lottery_knobs():
    # a forest and a desert draw both build (extra 'archetype' key is ignored by generate_world)
    for arch in ("forest", "desert"):
        f = generate_world(world_lottery(0, archetype=arch))
        assert f.npp_gm2 is not None and f.biome is not None
