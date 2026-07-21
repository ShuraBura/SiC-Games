"""R-91 — CONSISTENCY INVARIANTS over diagnostic snapshots: complain when two numbers cannot both be true.

WHY THIS EXISTS, and why it is NOT more D-series discipline. MECHANISM_CHARTER §10 (D1–D14) asks *"is this
measurement trustworthy?"*, and it works — in one session it caught an underpowered presence test, a sweep with
no positive control, and a 5x "population crash" that was single-seed RNG noise. It does NOT catch the failure
mode that produced the worst errors of R-89/R-90, because in those every number was INDIVIDUALLY CORRECT and the
RELATIONSHIP between them was impossible:

  * `ascribed_frac=1.0` (every lineage hereditarily ranked) printed beside `pct_stratified=11.5` (88% of people
    in bands classified "egalitarian_forager") — in the SAME log line, for hours, unnoticed. The society
    classifier `society_from_character(density, surplus_frac)` never reads ascription at all.
  * `legit_threshold=0.15` compares a lineage's SHARE of its band's feasting against a constant. Mean share is
    1/lineages_per_band, so the test only discriminates above ~6.7 lineages/band. Measured: 2.14. Nobody changed
    the parameter — the substrate drifted out from under it.
  * `cum_reversions` stopped incrementing at 4269 and never moved again for 5,650 steps, while `ascribed_frac`
    sat pinned at exactly 1.0. Read at a single timepoint, a frozen cumulative counter looks like a large number.

THE DESIGN POINT: more FIELDS do not help. That campaign log already printed ~20 per line and the contradiction
was in it the whole time. Passive reporting is exactly what failed. This module is ACTIVE — it returns
violations, and the harness prints them loudly, so a 90-minute run says something is incoherent at minute 3.

FOUR GENERIC CLASSES (each generalised from a real failure above, not invented):
  CONTRADICTION  two fields whose values are mutually impossible
  DOMAIN         a threshold applied to a SHARE/RATIO whose hidden denominator has drifted out of the range
                 where the threshold means what it was set to mean
  FROZEN         a cumulative counter that stopped advancing while its driver is still live
  STUCK          a field that should fluctuate, pinned to one value (or to a bound) for a long window

Pure functions over plain dicts — no model import — so this runs on archived trajectory JSON as easily as live,
and is directly unit-testable against the known failures (which is how it was validated; see tests).
"""
from __future__ import annotations

from dataclasses import dataclass

# Windows are in SNAPSHOTS, not steps. Deliberately generous: a real equilibrium plateaus too, and a checker
# that cries wolf gets ignored, which would reproduce the very failure it exists to prevent.
STUCK_WINDOW = 20        # ~500 steps at the campaign's LOGEVERY=25
FROZEN_WINDOW = 20
ABSORBING_WINDOW = 40    # lineage count legitimately plateaus; only a very long freeze is informative

# Fields that SHOULD move in a live system. Deliberately excludes pop/n_bands/etc., which plateau at a healthy
# equilibrium — flagging those would be noise.
STUCK_WATCH = ("ascribed_frac", "frac_gumsa", "leader_tenure_yr")


@dataclass(frozen=True)
class Violation:
    code: str
    kind: str          # CONTRADICTION | DOMAIN | FROZEN | STUCK
    message: str

    def __str__(self) -> str:
        return f"{self.kind}:{self.code} {self.message}"


def _tail_constant(rows: list[dict], key: str, window: int) -> bool:
    """True when `key` is present and byte-identical across the last `window` snapshots."""
    vals = [r.get(key) for r in rows[-window:]]
    if len(vals) < window or any(v is None for v in vals):
        return False
    return len(set(vals)) == 1


def check(rows: list[dict], cfg: dict | None = None) -> list[Violation]:
    """Evaluate every invariant against the trajectory SO FAR; return violations for its latest point.

    `rows` is the ordered list of snapshot dicts. `cfg` carries the parameters whose validity domain matters
    (currently `legit_threshold`) — passed rather than imported so archived runs can be re-checked against the
    settings they actually used.
    """
    cfg = cfg or {}
    out: list[Violation] = []
    if not rows:
        return out
    cur = rows[-1]

    # ── CONTRADICTION: hereditary rank vs the society classifier ────────────────────────────────────────
    # If essentially every lineage is "descended from higher nats", the societies holding them cannot be
    # predominantly egalitarian foragers. These are computed by two subsystems that never speak:
    # `_lineage_ascribed` (R-86 legitimacy ratchet) and `society_from_character(density, surplus_frac)`.
    # CUTS ARE A JUDGEMENT CALL and are stated so they can be argued with: "essentially every" = 0.9,
    # "predominantly egalitarian" = fewer than a quarter of people in a ranked society.
    asc, strat = cur.get("ascribed_frac"), cur.get("pct_stratified")
    if asc is not None and strat is not None and asc >= 0.9 and strat < 25.0:
        out.append(Violation(
            "rank-vs-society", "CONTRADICTION",
            f"ascribed_frac={asc:.2f} (~all lineages hereditarily ranked) but only {strat:.1f}% of people are "
            f"in a stratified society — the society classifier does not read ascription"))

    # ── DOMAIN: a share-threshold whose hidden denominator has drifted ──────────────────────────────────
    # Ascription fires when a lineage's SHARE of its band's feasting exceeds `legit_threshold`. Mean share is
    # 1/lineages_per_band, so the test discriminates only while lineages_per_band > 1/legit_threshold. Below
    # that, the AVERAGE lineage clears the bar and "nobility" is universal by arithmetic, not by competition.
    # R-93: the rule applies ONLY to the absolute formulation. Under relative legitimacy the stock is already
    # normalised by the competing-lineage count, so there is no hidden denominator left to drift — firing here
    # would be a false positive against a fixed mechanism, and a checker that cries wolf is one that gets ignored.
    thr = None if cfg.get("relative_legitimacy") else cfg.get("legit_threshold")
    lpb = cur.get("lineages_per_band")
    if thr and lpb is not None and lpb > 0:
        need = 1.0 / thr
        if lpb < need:
            out.append(Violation(
                "share-threshold-degenerate", "DOMAIN",
                f"lineages_per_band={lpb:.2f} < 1/legit_threshold={need:.2f} — the mean lineage clears the "
                f"{thr:g} share bar automatically, so ascription no longer discriminates"))

    # ── FROZEN: a cumulative counter that stopped while its driver is live ──────────────────────────────
    # A monotone counter read at ONE timepoint looks like a big number whether or not it is still moving.
    # Reversions are only meaningful while there is something to revert (ascribed_frac > 0).
    if _tail_constant(rows, "cum_reversions", FROZEN_WINDOW) and (cur.get("ascribed_frac") or 0) > 0:
        out.append(Violation(
            "reversions-frozen", "FROZEN",
            f"cum_reversions stuck at {cur.get('cum_reversions')} for {FROZEN_WINDOW} snapshots while "
            f"ascribed_frac={cur.get('ascribed_frac')} — the reversion mechanism is dead, not quiet"))

    # ── STUCK: a field that should fluctuate, pinned ────────────────────────────────────────────────────
    for key in STUCK_WATCH:
        if _tail_constant(rows, key, STUCK_WINDOW):
            v = cur.get(key)
            at_bound = v in (0.0, 1.0)
            out.append(Violation(
                f"{key}-stuck", "STUCK",
                f"{key} pinned at {v}{' (a BOUND)' if at_bound else ''} for {STUCK_WINDOW} snapshots"))

    # ── STUCK (absorbing): lineage count that cannot recover ────────────────────────────────────────────
    # `_lineage` could only ever be lost, never founded (R-90), making fixation certain. A long-frozen count is
    # the signature of that absorbing state rather than of an equilibrium.
    if _tail_constant(rows, "n_lineages", ABSORBING_WINDOW):
        out.append(Violation(
            "lineages-absorbing", "STUCK",
            f"n_lineages fixed at {cur.get('n_lineages')} for {ABSORBING_WINDOW} snapshots — absorbing state, "
            f"not equilibrium (nothing can create a lineage)"))

    return out


def first_violations(rows: list[dict], cfg: dict | None = None) -> dict[str, dict]:
    """Earliest snapshot at which each violation code fires, by replaying the trajectory. This is the number
    that matters for the checker's whole purpose: how early would it have complained?"""
    seen: dict[str, dict] = {}
    for i in range(1, len(rows) + 1):
        for v in check(rows[:i], cfg):
            if v.code not in seen:
                seen[v.code] = {"step": rows[i - 1].get("step"), "kind": v.kind, "message": v.message}
    return seen


if __name__ == "__main__":                       # re-check any archived trajectory: py -3 -m sic_games.invariants FILE...
    import json, sys
    for path in sys.argv[1:]:
        with open(path) as fh:
            blob = json.load(fh)
        rows = blob.get("traj", blob) if isinstance(blob, dict) else blob
        meta = blob.get("meta", {}) if isinstance(blob, dict) else {}
        cfg = {"legit_threshold": 0.15} if meta.get("elite") else {}
        found = first_violations(rows, cfg)
        last = rows[-1].get("step") if rows else 0
        print(f"\n=== {path}  ({len(rows)} snapshots, to step {last}) ===")
        if not found:
            print("  no violations")
        for code, d in sorted(found.items(), key=lambda kv: kv[1]["step"] or 0):
            print(f"  step {d['step']:>6}  {d['kind']:<13} {code}")
            print(f"                {d['message']}")
