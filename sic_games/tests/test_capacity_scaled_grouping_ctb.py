"""CTB for CAPACITY-SCALED GROUPING (R-106, 2026-08-22).

THE DEFECT. The E.1 safety and E.2 mate-access drives multiply perceived per-capita yield by the POST-MOVE
GROUP SIZE, with no reference to what the ground can feed:

    E.1  ypc *= 1 + group_safety_max * (1 - exp(-g / group_safety_scale))
    E.2  ypc *= group_mate_floor + (1 - group_mate_floor) * min(1, g / group_mate_min)

So aggregating is rewarded identically at every productivity. That is harmless where there is slack and fatal
where there is none, which is why it only surfaced on a SINGLE-BIOME test and never on the mixed world.

THE ARITHMETIC THAT PINS IT. A cell is stable when occupancy equals its yield under the depletion model:

    occ = B* x K = (1 - DEPLETE_FRAC * occ / K) * K     =>     occ_max = K / (1 + DEPLETE_FRAC)

    world     K/cell   occ_max   measured occ   outcome
    arid         2.0      1.33           1.40   EXTINCT inside 60 steps, 95% starvation, ZERO births
    mountain     1.9      1.27           1.23   EXTINCT
    forest      36.3     24.20          ~14     fine
    temperate   24.6     16.40          ~14     fine

Arid dies by a margin of 0.07 people per cell. The ethnographic anchor for that world is 0.005/km2 = 0.5 per
cell (Long 1971, Cane 1990; LITERATURE.md), which clears occ_max by 2.7x -- so the WORLD is habitable and the
BEHAVIOUR is what kills it.

THE FIX INTRODUCES NO NEW PARAMETER: the group size that earns a benefit is capped at S / BURN, the cell's own
food over the maintenance requirement. Both already exist.
"""
import math
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "sic_games" / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "sic_games" / "src"))

from sic_games.config import SubstrateConfig  # noqa: E402
from sic_games.substrate import diffusion_select_target  # noqa: E402

BURN = 75_000.0
# The campaign's live grouping values (GRP, imported by run_campaign).
GRP = dict(group_safety_max=8.0, group_safety_scale=15.0, group_mate_min=15.0, group_mate_floor=0.2)


class _Field:
    """A uniform sugar field: every cell holds `level` kcal."""

    def __init__(self, level, n=8):
        self.width = self.height = n
        self._lv = level

    def level(self, x, y):
        return self._lv


class _Agent:
    strategy = "si"
    phi = 1.0

    def __init__(self, pos=(4, 4)):
        self.pos = pos


def _sc(**over):
    return SubstrateConfig(enabled=True, k_cell=0, movement_mode="diffusion",
                           contest_exponent=0.0, move_cost_flat=0.0, **{**GRP, **over})


def _choose(K, occ_cur, occ_nbr, capped, burn=BURN):
    """The REAL movement decision, not a re-implementation. Returns the cell the agent picks.

    An earlier version of this file computed the grouping multiplier with a local helper that duplicated the
    capping logic. It passed 14/14 -- and passed just as happily with the mechanism PERTURBED OUT of
    substrate.py, because it was testing its own copy. That is the same second-copy failure this project has
    been finding all week, committed inside the test written to catch it. Every assertion below now goes
    through `diffusion_select_target`.
    """
    fld = _Field(K * BURN)
    occ = {(4, 4): occ_cur, (5, 4): occ_nbr}
    return diffusion_select_target(_Agent((4, 4)), fld, occ, None, _sc(), rng=None, temperature=None,
                                   cap_group=capped, burn=burn)


# ─────────────────────────── the load-bearing quantity ────────────────────────────────────────────────

def test_a_rich_cell_is_UNAFFECTED_because_the_cap_never_binds():
    """NEGATIVE CONTROL, and the one that decides interpretability. Forest feeds 36.3 people per cell, so no
    plausible band reaches the cap and the CHOICE must be identical either way. Measured across 72
    rich-world configurations: 0 changed. If a rich world moved, the mechanism would be altering behaviour
    everywhere rather than only where land is scarce, and every prior result would be in question."""
    changed = [(K, c, n) for K in (24.6, 36.3, 50.0) for c in (2, 4, 8, 15, 25, 40) for n in (0, 1, 2, 3)
               if _choose(K, c, n, capped=False) != _choose(K, c, n, capped=True)]
    assert not changed, f"the cap bit on rich land in {len(changed)} cases, e.g. {changed[:3]}"


def test_on_poor_land_an_over_capacity_group_stops_holding_the_agent():
    """THE MECHANISM, read off the real decision. Arid feeds 2.0 people. With 15 crammed onto that cell and an
    empty neighbour, the UNCAPPED agent stays -- the grouping reward outweighs the collapsed per-capita share
    -- and the CAPPED agent leaves, because a band the land cannot feed earns no further benefit."""
    stay = _choose(2.0, occ_cur=15, occ_nbr=0, capped=False)
    leave = _choose(2.0, occ_cur=15, occ_nbr=0, capped=True)
    assert stay == (4, 4), "uncapped, the agent should stay on the crowded arid cell"
    assert leave != (4, 4), "capped, the agent should leave a cell holding 15 people on food for 2"


@pytest.mark.parametrize("K", [1.0, 2.0, 3.0, 5.0])
def test_the_effect_appears_across_poor_worlds_not_just_one_lucky_case(K):
    """A single discriminating configuration could be an artefact of one arithmetic coincidence."""
    assert _choose(K, 15, 0, capped=False) != _choose(K, 15, 0, capped=True),         f"K={K}: the cap changed nothing with 15 agents on land for {K}"


def test_a_small_group_within_capacity_is_left_alone_even_on_poor_land():
    """The cap must bite only ABOVE capacity. A group the arid cell CAN feed must behave as before, or the
    mechanism is suppressing aggregation in general rather than over-aggregation."""
    for occ_cur in (1, 2):
        assert _choose(2.0, occ_cur, 0, capped=False) == _choose(2.0, occ_cur, 0, capped=True),             f"the cap changed a within-capacity group of {occ_cur} on arid land"


def test_burn_zero_disables_the_cap_even_when_the_flag_is_on():
    """Guard against a caller that forgets to pass BURN: S/0 must not divide, and the mechanism must fall back
    to the historical behaviour rather than cap at something meaningless."""
    assert _choose(2.0, 15, 0, capped=True, burn=0.0) == _choose(2.0, 15, 0, capped=False, burn=0.0)


# ─────────────────────────── the flag reaches the real decision ───────────────────────────────────────

def test_the_flag_defaults_off_and_is_declared_on_the_grouping_owner():
    """It belongs with the drives it bounds, so an ablation names one owner rather than two."""
    sc = SubstrateConfig()
    assert sc.enable_capacity_scaled_grouping is False
    assert "enable_capacity_scaled_grouping" in SubstrateConfig.model_fields


def test_the_movement_rule_accepts_the_arguments_so_the_wiring_cannot_be_stale():
    """REACHABILITY. This project's own audit found 27 of 79 flags dark; a perfect helper reached by nobody is
    the standard failure. Assert the signature the model calls with."""
    import inspect
    sig = inspect.signature(diffusion_select_target)
    assert "cap_group" in sig.parameters and "burn" in sig.parameters
    assert sig.parameters["cap_group"].default is False, "must default to the historical behaviour"
    assert sig.parameters["burn"].default == 0.0


@pytest.mark.parametrize("capped", [False, True])
def test_the_movement_rule_still_returns_a_legal_cell_in_both_states(capped):
    """A mechanism that crashes or returns off-grid coordinates on poor ground would be caught here rather
    than 15,000 steps into a campaign."""
    fld = _Field(2.0 * BURN)
    agent = _Agent((4, 4))
    got = diffusion_select_target(agent, fld, {(4, 4): 3}, None, _sc(), rng=None, temperature=None,
                                  cap_group=capped, burn=BURN)
    assert isinstance(got, tuple) and len(got) == 2
    assert 0 <= got[0] < fld.width and 0 <= got[1] < fld.height



# ─────────────────────────── the arithmetic this mechanism exists to satisfy ──────────────────────────

@pytest.mark.parametrize("K,occ_max", [(2.0, 1.3333), (1.9, 1.2667), (24.6, 16.40), (36.3, 24.20)])
def test_the_stability_ceiling_is_K_over_one_plus_deplete_frac(K, occ_max):
    """Pins the arithmetic the whole mechanism is aimed at, so a change to DEPLETE_FRAC cannot silently move
    the target. B* = 1 - DEPLETE_FRAC * occ/K, and a cell is stable when occ = B* x K."""
    from sic_games.capacity import DEPLETE_FRAC
    assert K / (1.0 + DEPLETE_FRAC) == pytest.approx(occ_max, rel=1e-3)


def test_the_ethnographic_arid_density_clears_the_ceiling():
    """The filed anchor is ~0.005/km2 (Long 1971 1-per-200km2, Cane 1990 1-per-170km2), which on 100 km2 cells
    is 0.5 people per cell. It must sit BELOW the arid stability ceiling, or the target itself is impossible
    and no behavioural fix could reach it."""
    from sic_games.capacity import DEPLETE_FRAC
    occ_max = 2.0 / (1.0 + DEPLETE_FRAC)
    assert 0.5 < occ_max, "the anchored arid density exceeds what the depletion model can sustain"
    assert occ_max / 0.5 > 2.0, "expected at least 2x headroom at the anchored density"
