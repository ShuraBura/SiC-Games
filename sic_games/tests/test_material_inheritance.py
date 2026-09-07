"""R-103d — MATERIAL INHERITANCE: bequeath durable capital at death, the missing 'bequeathing' step.

Flannery ch.10: competitive feasting "produced individual Big Men who had no way of bequeathing renown to their
offspring." R-103c measured exactly that — the model's elite advantage lives in the OFFICE (current leader), not
the LINEAGE, because material dies with the agent. This mechanism transfers it to heirs so a lineage can compound
a heritable estate (the big-man → chief step). Rule is regime-dependent [Goody 1976; D-PLACE EA075×EA028].

Tests target `_bequeath` directly (the transfer logic) with light stand-ins, plus the config default.
"""
import pytest
from sic_games.demography import DemographyConfig
from sic_games.phase1_model import TerrainWorld


class _A:
    """Minimal heir/decedent stand-in carrying only what `_bequeath` reads/writes."""
    _uid = 0

    def __init__(self, material=0.0, age=0, sex="male", alive=True, cred=1.0):
        self.material = material
        self.age = age
        self.sex = sex
        self.alive = alive
        self.cred = cred
        _A._uid += 1
        self.unique_id = _A._uid


# _bequeath is a plain method (reads only its args + writes .material) → bind it unbound.
_bequeath = TerrainWorld._bequeath


def _run(dead_material, heirs, rule, by_status=False):
    dead = _A(material=dead_material)
    _bequeath(None, dead, heirs, rule, by_status=by_status)   # self is unused inside _bequeath
    return dead


def test_config_default_off():
    c = DemographyConfig()
    assert c.enable_material_inheritance is False
    assert c.material_inheritance_rule == "primogeniture"
    # R-103e new toggles must also default off/inert (bit-exact protection)
    assert c.material_heir_by_status is False
    assert c.enable_noble_leveling_exemption is False
    assert c.noble_exemption_frac == 1.0


def test_by_status_primogeniture_picks_highest_cred_not_eldest():
    """R-103e: with heir-by-status ON, the estate follows RANK — the highest-cred child, even if younger."""
    eldest_low = _A(age=400, cred=0.5)
    younger_high = _A(age=120, cred=3.0)
    _run(100.0, [eldest_low, younger_high], "primogeniture", by_status=True)
    assert younger_high.material == 100.0 and eldest_low.material == 0.0


def test_by_status_off_still_picks_eldest():
    """Default (by_status off) keeps age-primogeniture — so the flag is what changes it, nothing else."""
    eldest_low = _A(age=400, cred=0.5)
    younger_high = _A(age=120, cred=3.0)
    _run(100.0, [eldest_low, younger_high], "primogeniture", by_status=False)
    assert eldest_low.material == 100.0 and younger_high.material == 0.0


def test_primogeniture_gives_whole_estate_to_eldest():
    young, old = _A(age=120), _A(age=400)
    dead = _run(100.0, [young, old], "primogeniture")
    assert old.material == 100.0 and young.material == 0.0
    assert dead.material == 0.0                       # estate emptied


def test_partible_splits_equally_among_all_children():
    a, b, c = _A(), _A(), _A()
    _run(90.0, [a, b, c], "partible_equal")
    assert a.material == b.material == c.material == 30.0


def test_patrilineal_sons_splits_among_sons_only():
    son1, son2, daughter = _A(sex="male"), _A(sex="male"), _A(sex="female")
    _run(80.0, [son1, son2, daughter], "patrilineal_sons")
    assert son1.material == son2.material == 40.0
    assert daughter.material == 0.0                   # daughters excluded under this rule


def test_no_eligible_heir_dissolves_estate():
    """No surviving child (or, under patrilineal_sons, no son) ⇒ estate is LOST, exactly as the OFF path. The
    mechanism can only redistribute across a real parent→child link, never manufacture or preserve wealth in a
    vacuum — a lineage that fails to reproduce loses its capital."""
    daughter = _A(sex="female")
    dead = _run(50.0, [daughter], "patrilineal_sons")     # only a daughter → no eligible son
    assert daughter.material == 0.0 and dead.material == 50.0   # NOT transferred; caller lets it dissolve
    dead2 = _run(50.0, [], "primogeniture")               # no children at all
    assert dead2.material == 50.0


def test_dead_heirs_excluded():
    """A child who died the same step does not inherit — the estate goes to survivors only."""
    alive, corpse = _A(age=100, alive=True), _A(age=400, alive=False)
    _run(100.0, [alive, corpse], "primogeniture")
    assert alive.material == 100.0 and corpse.material == 0.0   # eldest is dead → skipped, goes to survivor


def test_primogeniture_tie_break_is_deterministic():
    """Equal ages must resolve by unique_id, so a run is reproducible."""
    a, b = _A(age=200), _A(age=200)
    _run(100.0, [a, b], "primogeniture")
    winner = a if a.unique_id > b.unique_id else b
    loser = b if winner is a else a
    assert winner.material == 100.0 and loser.material == 0.0
