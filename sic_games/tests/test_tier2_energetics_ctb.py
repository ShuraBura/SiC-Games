"""TIER 2 — ENERGETICS. CTB for the return-rate fields: do the verified anchors actually land in the world?

LADDER POSITION. Tier 2 is the base of everything above it — every demographic outcome, every band size, every
surplus and every material Gini is downstream of whether kcal in and kcal out compute correctly. It had ZERO
constructed-truth coverage before this file.

THE DISTINCTION THIS FILE EXISTS FOR. On 2026-08-06 the return-rate anchors were verified against their PDFs:
Hawkes 1991's 0.71 and 1.02 kg/hr convert to 518 and 745 kcal/hr exactly, Hill 1987's forest 5,541, Hurtado &
Hill's grassland 3,001. **That is a statement about the literature, not about the model.** Whether the code
consuming those numbers puts them into a world is a separate claim, and until this file nobody had checked it.

The constructed truth here is the anchor table itself: generate a world, and every biome's realized mean must
be the number the table says.
"""
import numpy as np
import pytest

from sic_games.terrain import (FORAGE_KCAL_TARGETS, GAME_KCAL_TARGETS, SHORE_BONUS_KCAL,
                               generate_world, world_lottery_climate)

BIOME = {0: "water", 1: "wetland", 2: "forest", 3: "savanna", 4: "grass", 5: "desert", 6: "mountain"}


def _world(climate="temperate", terrain="coastal", seed=0):
    return generate_world(world_lottery_climate(seed, terrain=terrain, climate=climate), mode="climate")


# ── the anchors, as they land in a world ──────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("seed", [0, 1, 2])
def test_game_return_rates_hit_their_anchored_means_exactly(seed):
    """GAME is rescaled per biome to the return-rate table and nothing is added afterwards, so the realized
    mean must equal the anchor to within rounding. This is where Hill 1987's forest 5,541 and Hurtado & Hill's
    grassland 3,001 actually enter the model."""
    f = _world(seed=seed)
    for code, target in GAME_KCAL_TARGETS.items():
        m = (f.biome == code)
        if not m.any():
            continue
        assert float(f.game_kcal[m].mean()) == pytest.approx(target, rel=0.02), BIOME[code]


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_forage_hits_its_anchored_mean_ON_NON_SHORE_CELLS(seed):
    """FORAGE is rescaled to the table and THEN the shore bonus is added, so the whole-biome mean OVERSHOOTS
    the anchor on any coastal world — desert reads ~1332 against a target of 1200.

    That is not a defect; it is the Bird 1997 intertidal bonus doing its job. But it means 'the forage field
    matches the anchor' is only true off-shore, and a reader comparing a biome mean to the table without that
    qualifier would conclude the rescale was broken."""
    f = _world(seed=seed)
    shore = f.is_shore.astype(bool)
    for code, target in FORAGE_KCAL_TARGETS.items():
        m = (f.biome == code) & ~shore
        if m.sum() < 20:
            continue
        assert float(f.forage_kcal[m].mean()) == pytest.approx(target, rel=0.05), BIOME[code]


def test_the_shore_bonus_is_additive_and_is_bird_1997s_number():
    """`forage_kcal += is_shore * SHORE_BONUS_KCAL` — additive, not multiplicative, so it does not scale with
    the biome's productivity. A shore desert cell and a shore forest cell get the same absolute bonus."""
    assert SHORE_BONUS_KCAL == pytest.approx(1491.5)
    f = _world()
    shore = f.is_shore.astype(bool)
    for code in (4, 5):
        on = (f.biome == code) & shore
        off = (f.biome == code) & ~shore
        if on.sum() < 5 or off.sum() < 20:
            continue
        lift = float(f.forage_kcal[on].mean()) - float(f.forage_kcal[off].mean())
        assert lift == pytest.approx(SHORE_BONUS_KCAL, rel=0.25), (BIOME[code], lift)


def test_an_unanchored_biome_reads_ZERO_and_that_is_a_gap_not_a_measurement():
    """Wetland and mountain GAME have no journal kcal/hr source, so they are absent from GAME_KCAL_TARGETS and
    the loop leaves those cells at 0.0. A zero here means 'nobody has anchored this', NOT 'measured to be
    empty of game' — the return-rate table says so explicitly and the field cannot distinguish them."""
    assert 1 not in GAME_KCAL_TARGETS and 6 not in GAME_KCAL_TARGETS
    f = _world(climate="savanna")
    for code in (1, 6):
        m = (f.biome == code)
        if m.any():
            assert float(f.game_kcal[m].max()) == 0.0, f"{BIOME[code]} game is unanchored and must read 0"


# ── THE REACHABILITY FINDING ──────────────────────────────────────────────────────────────────────────────

def test_the_canonical_world_contains_NO_SAVANNA_so_the_hawkes_anchor_is_unexercised():
    """THE TIER-2 FINDING (2026-08-07).

    `coastal-temperate` is the campaign's default world, and it contains **zero savanna cells**. So:

      * **Hawkes 1991's savanna game rate (518 kcal/hr)** — verified against the PDF on 2026-08-06 and one of
        the few anchors in this project checked to the unit — **never enters the canonical run.**
      * The same is true of the intercept-hunting boost (745/518), which is gated on savanna+llanos. That is
        exactly why `ClimateField.health()` reports `intercept=UNREACHABLE` on every temperate run, and why
        `llanos` reports the same: the sub-biome those channels need does not exist in this world.

    An anchor can be verified, correctly implemented, and still contribute nothing, because the WORLD does not
    contain the biome it describes. Verified + implemented + reachable are three claims, and the ladder tracks
    them separately for this reason."""
    temperate = _world(climate="temperate")
    assert (temperate.biome == 3).sum() == 0, "canonical world unexpectedly has savanna — update this finding"
    assert 3 in GAME_KCAL_TARGETS and GAME_KCAL_TARGETS[3] == 518.0, "the anchor exists but is unreachable here"

    savanna = _world(climate="savanna")
    assert (savanna.biome == 3).sum() > 500, "the savanna preset must actually produce savanna"
    m = (savanna.biome == 3)
    assert float(savanna.game_kcal[m].mean()) == pytest.approx(518.0, rel=0.02), (
        "on a world that HAS savanna, Hawkes' rate lands correctly — the anchor is fine, the world was wrong")


@pytest.mark.parametrize("climate,expect_savanna", [("temperate", False), ("boreal", False),
                                                    ("savanna", True), ("tropical", True)])
def test_which_worlds_can_exercise_the_savanna_anchored_layer(climate, expect_savanna):
    """Pinned so the set is a measurement rather than a memory. Any result about intercept hunting, the llanos
    flood, or the savanna game rate is a claim about THESE worlds only."""
    # bool() is load-bearing: numpy returns np.bool_, which is never `is True`
    assert bool((_world(climate=climate).biome == 3).sum() > 0) is expect_savanna


def test_the_biome_a_target_names_is_the_biome_the_field_scales():
    """The mapping is by integer code, and a silent off-by-one would rescale the wrong biome to the wrong
    anchor while every mean still looked plausible. Constructed against the code table."""
    assert BIOME[2] == "forest" and GAME_KCAL_TARGETS[2] == 5541.0     # Hill 1987 pursuit-weighted
    assert BIOME[3] == "savanna" and GAME_KCAL_TARGETS[3] == 518.0     # Hawkes 1991 [CONVERTED]
    assert BIOME[4] == "grass" and GAME_KCAL_TARGETS[4] == 3001.0      # Hurtado & Hill 1987
    assert BIOME[3] == "savanna" and FORAGE_KCAL_TARGETS[3] == 257.7   # Hadza tuber


# ── the collective granary (S.2) — a pure function with an explicit contract ──────────────────────────────

from sic_games.phase1_model import allocate_store_draw  # noqa: E402


def test_equal_weights_split_the_store_equally():
    """kappa = 0 is the EGALITARIAN case and it has to be exactly equal, not approximately — this is the
    control arm every Hayden control-of-redistribution result is measured against."""
    out = allocate_store_draw([1.0] * 4, [100.0] * 4, 80.0)
    assert out == pytest.approx([20.0] * 4)


def test_skewed_weights_give_the_high_status_claimant_proportionally_more():
    """kappa > 0 is the inequality lever: the draw is proportional to status^kappa."""
    out = allocate_store_draw([3.0, 1.0], [100.0, 100.0], 80.0)
    assert out == pytest.approx([60.0, 20.0])


def test_a_claimant_is_capped_at_its_own_deficit():
    """Nobody draws more than they need. A near-full claimant with a huge weight cannot hoard the granary."""
    out = allocate_store_draw([9.0, 1.0], [5.0, 100.0], 100.0)
    assert out[0] == pytest.approx(5.0), "capped at the deficit, not the 90.0 its weight would buy"
    assert out[1] == pytest.approx(10.0)


def test_the_draw_NEVER_exceeds_the_store_which_is_the_conservation_property():
    """The economy's floor. Sum of `store * w/wsum` is exactly `store`, and every term is then min'd
    downward, so the total drawn can only be <= store. If this ever failed the granary would create kcal."""
    import random
    rng = random.Random(0)
    for _ in range(200):
        n = rng.randint(1, 8)
        w = [rng.random() * 10 for _ in range(n)]
        d = [rng.random() * 50 for _ in range(n)]
        s = rng.random() * 100
        out = allocate_store_draw(w, d, s)
        assert sum(out) <= s + 1e-9, (w, d, s, out)
        assert all(o >= 0.0 for o in out)
        assert all(o <= dd + 1e-9 for o, dd in zip(out, d))


def test_it_is_a_SINGLE_PASS_so_a_capped_claimants_surplus_stays_in_the_granary():
    """THE PROPERTY MOST LIKELY TO BE MISREAD. The docstring says it and the arithmetic confirms it: a
    weight-rich but nearly-full claimant leaves its unused allocation IN THE STORE rather than passing it to
    the hungry. So the granary routinely delivers LESS than both the store available and the deficit
    outstanding, and a run can show hungry agents beside a non-empty granary without that being a bug.

    Constructed because 'the store was not empty, so nobody should have starved' is exactly the wrong
    inference to draw from a trajectory."""
    out = allocate_store_draw([9.0, 1.0], [1.0, 100.0], 100.0)
    assert out == pytest.approx([1.0, 10.0])
    assert sum(out) == pytest.approx(11.0)
    assert 100.0 - sum(out) == pytest.approx(89.0), "89 kcal stay in the granary beside an unmet deficit"


def test_an_empty_store_draws_nothing_and_zero_weights_do_not_divide_by_zero():
    assert allocate_store_draw([1.0, 1.0], [10.0, 10.0], 0.0) == pytest.approx([0.0, 0.0])
    out = allocate_store_draw([0.0, 0.0], [10.0, 10.0], 8.0)     # `wsum or 1.0` guard
    assert out == pytest.approx([0.0, 0.0])


def test_no_claimants_is_not_an_error():
    assert allocate_store_draw([], [], 50.0) == []
