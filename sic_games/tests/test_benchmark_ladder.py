"""`docs/BENCHMARK_LADDER.md` is a hand-maintained list of all 86 mechanisms. Charter P4 gives a second copy
two options — tested, or deleted — and this is the test.

IT DRIFTED BEFORE IT WAS COMMITTED. The first draft invented five flags that do not exist (`band_cohesion`,
`divorce`, `patriline_weight`, `pressure_mobility`, and the already-deleted `band_risk`) and missed eight that
do (`agglomeration`, `band_affiliation`, `band_family_knobs`, `dynamic_bands`, `forage_cap`, `game`,
`productivity_mobility`, `village_scaling`). A ladder that governs the order of work cannot be approximately
right about what is on it: a mechanism placed in no tier is a mechanism nobody benchmarks.
"""
import re
from pathlib import Path

import pytest

from sic_games.climate import ClimateConfig
from sic_games.demography import DemographyConfig

LADDER = Path(__file__).resolve().parents[2] / "docs" / "BENCHMARK_LADDER.md"

pytestmark = pytest.mark.skipif(not LADDER.exists(), reason="ladder not written yet")

# Deleted 2026-08-06. They may be NAMED in the ladder's prose (a reader of older results needs to know where
# they sat) but they must not be placed in a tier, because they no longer exist to benchmark.
_DELETED = {"band_risk", "infanticide"}


def _real() -> set:
    return {f[len("enable_"):] for f in
            list(DemographyConfig.model_fields) + list(ClimateConfig.model_fields)
            if f.startswith("enable_")}


def _listed() -> set:
    """Flags placed in a tier — the bullet list under '## Tier membership', stopping at the footnote."""
    body = LADDER.read_text(encoding="utf-8").split("## Tier membership", 1)[1]
    body = body.split("`band_risk` and `infanticide` were", 1)[0]
    return set(re.findall(r"`([a-z0-9_]+)`", body))


def test_every_mechanism_is_placed_in_a_tier():
    """A mechanism in no tier is a mechanism nobody benchmarks — it would sit ON in every run, outside the
    schedule of work, which is the state the ladder exists to end."""
    missing = sorted(_real() - _listed())
    assert not missing, f"{len(missing)} mechanism(s) are in the code but in no tier: {missing}"


def test_the_ladder_names_no_mechanism_that_does_not_exist():
    """The other direction, and the one that caught five invented names. A tier listing a flag that was never
    built reads as coverage that cannot happen."""
    phantom = sorted(_listed() - _real() - _DELETED)
    assert not phantom, f"{len(phantom)} name(s) in the ladder are not real flags: {phantom}"


def test_deleted_mechanisms_are_not_placed_in_a_tier():
    """`band_risk` and `infanticide` are gone. Naming them in the prose is right; scheduling them for
    benchmarking is not."""
    assert not (_listed() & _DELETED), "a deleted mechanism is listed in a tier"


def test_no_mechanism_is_placed_in_two_tiers():
    """The ladder's rule is that a mechanism sits at the LOWEST tier it depends on. Two placements would make
    'every tier beneath it is validated' ambiguous, which is the one thing the ordering has to be clear about.
    """
    body = LADDER.read_text(encoding="utf-8").split("## Tier membership", 1)[1]
    body = body.split("`band_risk` and `infanticide` were", 1)[0]
    tiers = re.split(r"\n- \*\*\d+ ", body)[1:]
    seen: dict = {}
    dupes = []
    for i, block in enumerate(tiers, 1):
        for f in re.findall(r"`([a-z0-9_]+)`", block):
            if f in seen:
                dupes.append(f"{f}: tiers {seen[f]} and {i}")
            seen[f] = i
    assert not dupes, dupes


def test_the_ladder_states_the_rule_it_is_for():
    """The table is the cheap part; the ordering rule is the point. If the rule is ever edited away the
    document becomes a coverage report, which this project already has two of."""
    text = LADDER.read_text(encoding="utf-8")
    assert "every tier beneath it is validated" in text
    assert "diagnosed at tier N or below" in text
    assert "An anchor verified is not a mechanism validated" in text
