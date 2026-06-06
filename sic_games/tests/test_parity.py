"""Stage 7.5 Workstream A — parity harness tests.

Proves the equivalence-harness infrastructure (blueprint §7) end to end on the
trivial identity case and on deliberately injected mismatches, before any mechanic
migrates. The object model is the frozen oracle (decision D4).
"""
from __future__ import annotations

import numpy as np

from sic_games.config import Config
from sic_games.parity import (
    TIER_BIT,
    TIER_RTOL,
    TIER_STAT,
    assert_identity,
    compare,
    snapshot,
)
from sic_games.run import SugarWorld


def _small_model(n=30, steps=0):
    cfg = Config(
        agents={"initial_population": n},
        world={"grid_size": (12, 12), "sugar_peaks": [(2, 2), (9, 9)]},
        run={"n_steps": max(steps, 1)},
    )
    m = SugarWorld(cfg)
    for _ in range(steps):
        m.step()
    return m


def test_identity_roundtrip_fresh():
    m = _small_model(n=25)
    rep = assert_identity(m)
    assert rep.passed
    assert rep.n_a == rep.n_b == 25


def test_identity_roundtrip_after_steps():
    # population may have changed via deaths/replacement; identity must still hold
    m = _small_model(n=40, steps=10)
    rep = assert_identity(m)
    assert rep.passed


def test_compare_detects_bit_mismatch():
    m = _small_model(n=20)
    a = snapshot(m)
    b = snapshot(m)
    b.columns["wealth"][b.live_indices()[0]] += 1.0  # perturb one agent
    rep = compare(a, b)
    assert not rep.passed
    fails = rep.failures()
    assert any(d.column == "wealth" for d in fails)


def test_compare_rtol_tier_tolerates_small_fp():
    m = _small_model(n=20)
    a = snapshot(m)
    b = snapshot(m)
    # nudge wealth by < 1e-9 relative — Tier-2 should accept, Tier-1 should reject
    li = b.live_indices()
    b.columns["wealth"][li] *= (1.0 + 1e-12)
    rep_bit = compare(a, b, tiers={"wealth": TIER_BIT})
    rep_rtol = compare(a, b, tiers={"wealth": TIER_RTOL})
    bit_wealth = next(d for d in rep_bit.diffs if d.column == "wealth")
    rtol_wealth = next(d for d in rep_rtol.diffs if d.column == "wealth")
    # wealth starts > 0 in all agents, so the relative nudge is detectable bit-wise
    assert not bit_wealth.passed
    assert rtol_wealth.passed


def test_compare_rtol_tier_rejects_large_diff():
    m = _small_model(n=20)
    a = snapshot(m)
    b = snapshot(m)
    li = b.live_indices()
    b.columns["wealth"][li] *= 1.001  # 1e-3 relative >> 1e-9
    rep = compare(a, b, tiers={"wealth": TIER_RTOL})
    assert not rep.passed


def test_compare_stat_tier_skipped():
    m = _small_model(n=20)
    a = snapshot(m)
    b = snapshot(m)
    b.columns["c1"][b.live_indices()] += 0.5  # large change, but tier is statistical
    rep = compare(a, b, tiers={"c1": TIER_STAT})
    c1 = next(d for d in rep.diffs if d.column == "c1")
    assert c1.passed and "statistical" in c1.note


def test_compare_population_mismatch_fails():
    m = _small_model(n=20)
    a = snapshot(m)
    b = snapshot(m)
    b.kill(np.array([b.live_indices()[0]]))  # one fewer living agent
    rep = compare(a, b)
    assert not rep.passed
    assert rep.n_a != rep.n_b


def test_compare_order_independent_alignment():
    # shuffling slot order must not affect the comparison (aligned by unique_id)
    m = _small_model(n=25)
    a = snapshot(m)
    b = snapshot(m)
    n = b.n_slots
    perm = np.random.default_rng(0).permutation(n)
    for name, arr in b.columns.items():
        arr[:n] = arr[perm]
    rep = compare(a, b)
    assert rep.passed
