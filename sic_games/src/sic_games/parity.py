"""Stage 7.5 Workstream A — the parity / equivalence harness (blueprint §7).

The validation spine of the array restructure. The object model stays frozen as
the **reference oracle** (decision D4); every mechanic migrates against it under
one of three gates chosen by the mechanic's interaction structure (blueprint §3):

  * **Tier 1 — bit-identical.** Per-agent independent updates (cred decay, the σ
    formula, metabolism/wealth/age, η(a), DTM P_birth, dormancy flags, …): the
    array result must match the oracle exactly.
  * **Tier 2 — numerical tolerance (rtol≈1e-9).** Reductions/segment ops where FP
    associativity shifts the last bits (mean_cred, mean_wealth, harvest-split,
    Gini) — the same 1e-9 the 2026-05-28 audit used.
  * **Tier 3 — pre-registered statistical equivalence.** Order-dependent mechanics
    (Deffuant, JT contest, biparental endowment) where simultaneous ≠ sequential
    is a deliberate semantics choice; compared distributionally across ≥10 seeds.

This module provides the *infrastructure*: snapshot the oracle into an
`AgentArray`, and diff two snapshots / a snapshot-vs-array column by column at a
chosen tier. It migrates no mechanic itself — the per-mechanic comparisons and the
Tier-3 multi-seed battery build on top of these primitives.

Nothing here mutates the oracle; `snapshot` is read-only.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from sic_games.soa import ALL_COLUMNS, AgentArray

# Tier labels
TIER_BIT = "bit"          # exact equality (Tier 1)
TIER_RTOL = "rtol"        # np.allclose at rtol (Tier 2)
TIER_STAT = "stat"        # distributional (Tier 3) — handled by the multi-seed battery

_DEFAULT_RTOL = 1e-9
_DEFAULT_ATOL = 0.0


def snapshot(model, capacity: int | None = None) -> AgentArray:
    """Read-only snapshot of the oracle's living agents into an AgentArray."""
    return AgentArray.from_oracle(model, capacity=capacity)


@dataclass
class ColumnDiff:
    column: str
    passed: bool
    tier: str
    max_abs: float
    max_rel: float
    n_mismatch: int
    note: str = ""


@dataclass
class ParityReport:
    """Per-column parity result for one comparison."""

    diffs: list[ColumnDiff]
    n_a: int
    n_b: int

    @property
    def passed(self) -> bool:
        return self.n_a == self.n_b and all(d.passed for d in self.diffs)

    def failures(self) -> list[ColumnDiff]:
        return [d for d in self.diffs if not d.passed]

    def summary(self) -> str:
        head = f"parity {'PASS' if self.passed else 'FAIL'} (n_a={self.n_a}, n_b={self.n_b})"
        if self.passed:
            return head
        lines = [head]
        for d in self.failures():
            lines.append(
                f"  [{d.tier}] {d.column}: n_mismatch={d.n_mismatch} "
                f"max_abs={d.max_abs:.3e} max_rel={d.max_rel:.3e} {d.note}".rstrip()
            )
        return "\n".join(lines)


def _live_column(arr: AgentArray, name: str, order: np.ndarray) -> np.ndarray:
    return arr.columns[name][order]


def compare(
    arr_a: AgentArray,
    arr_b: AgentArray,
    tiers: dict[str, str] | None = None,
    default_tier: str = TIER_BIT,
    rtol: float = _DEFAULT_RTOL,
    atol: float = _DEFAULT_ATOL,
    columns: tuple[str, ...] = ALL_COLUMNS,
    sort_by: str = "unique_id",
) -> ParityReport:
    """Diff two AgentArrays column by column at the per-column declared tier.

    Agents are aligned by `sort_by` (default unique_id) so the comparison is
    order-independent — exactly the property the keyed-RNG scheme (D2) is meant to
    deliver. `tiers` maps column name → TIER_BIT / TIER_RTOL; columns absent from
    the map use `default_tier`. TIER_STAT columns are recorded as skipped here
    (the distributional battery compares those separately).
    """
    tiers = tiers or {}
    la = arr_a.live_indices()
    lb = arr_b.live_indices()
    n_a, n_b = la.size, lb.size

    if n_a != n_b:
        # Population mismatch is itself a failure; still report per-column on the
        # overlap is meaningless without alignment, so short-circuit.
        return ParityReport(
            diffs=[ColumnDiff("__population__", False, TIER_BIT, float("nan"),
                              float("nan"), abs(n_a - n_b), "live-count mismatch")],
            n_a=n_a, n_b=n_b,
        )

    # Align both by sort key.
    ka = arr_a.columns[sort_by][la]
    kb = arr_b.columns[sort_by][lb]
    oa = la[np.argsort(ka, kind="stable")]
    ob = lb[np.argsort(kb, kind="stable")]

    diffs: list[ColumnDiff] = []
    for name in columns:
        tier = tiers.get(name, default_tier)
        a = _live_column(arr_a, name, oa).astype(np.float64)
        b = _live_column(arr_b, name, ob).astype(np.float64)
        adiff = np.abs(a - b)
        denom = np.maximum(np.abs(a), np.abs(b))
        with np.errstate(divide="ignore", invalid="ignore"):
            rel = np.where(denom > 0, adiff / denom, 0.0)
        max_abs = float(adiff.max()) if adiff.size else 0.0
        max_rel = float(rel.max()) if rel.size else 0.0

        if tier == TIER_STAT:
            diffs.append(ColumnDiff(name, True, tier, max_abs, max_rel, 0, "skipped (statistical)"))
            continue
        if tier == TIER_RTOL:
            ok = np.allclose(a, b, rtol=rtol, atol=atol)
            n_mis = int((adiff > (atol + rtol * np.abs(b))).sum())
        else:  # TIER_BIT
            mism = a != b
            ok = not bool(mism.any())
            n_mis = int(mism.sum())
        diffs.append(ColumnDiff(name, bool(ok), tier, max_abs, max_rel, n_mis))

    return ParityReport(diffs=diffs, n_a=n_a, n_b=n_b)


def assert_identity(model, **kwargs) -> ParityReport:
    """Sanity check the harness itself: two snapshots of the same model are bit-equal.

    The trivial identity case proves the snapshot + diff path works end to end
    before any mechanic is migrated (the §4.1 "harness can run oracle-vs-array and
    diff per-column" precondition). Raises AssertionError with the report summary
    on any mismatch.
    """
    a = snapshot(model, **kwargs)
    b = snapshot(model, **kwargs)
    rep = compare(a, b)
    assert rep.passed, rep.summary()
    return rep
