"""CTB for R-103 RELATIONAL STRATIFICATION (R-106, 2026-09-05).

THE DEFECT. The society classifier calls a band `stratified_chiefdom` on `packed AND surplus >= 0.7` — pure
affluence, no inequality. It read a rich, between-band-EQUAL world as 36% stratified (between-band cred Gini
0.14). Stratification is a relation BETWEEN bands, not a property of one band.

THE FIX. `enable_relational_stratification`: the stratified verdict needs (a) the regional BETWEEN-band cred Gini
>= between_band_gini_min AND (b) this band in the top quantile of per-band mean cred.

LOAD-BEARING is `test_the_classifier_needs_an_unequal_region_and_a_top_band`: the pure function returns stratified
only when the region is unequal AND the band is at its top; a rich, equal region reads complex.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for p in (ROOT / "sic_games" / "src", ROOT / "sic_games" / "outputs" / "mechanism_battery",
          ROOT / "sic_games" / "outputs" / "phase1_social_evolution"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from sic_games.demography import DemographyConfig, society_from_character, BINFORD_PACKING_PER_KM2  # noqa: E402

PACKED = BINFORD_PACKING_PER_KM2 * 2.0   # comfortably above the packing threshold


def test_the_flag_defaults_off():
    assert DemographyConfig().enable_relational_stratification is False


def test_off_is_bit_exact_with_the_level_only_classifier():
    """With no relational args the classifier is the historical level-only one: packed + affluent -> stratified."""
    assert society_from_character(PACKED, 0.8) == "stratified_chiefdom"
    assert society_from_character(0.0, 0.0) == "egalitarian_forager"


def test_the_classifier_needs_an_unequal_region_and_a_top_band():
    """LOAD-BEARING. With the relational gate on (between_gini_min set), a packed affluent band is stratified ONLY
    when the region is unequal (between_gini >= min) AND the band is at the top. A rich EQUAL region is complex."""
    gmin = 0.35
    # equal region (below the threshold) -> complex, even at the top and even if internally rich
    assert society_from_character(PACKED, 0.8, between_gini=0.14, between_gini_min=gmin, band_is_top=True) \
        == "complex_forager"
    # unequal region AND a top band -> stratified
    assert society_from_character(PACKED, 0.8, between_gini=0.45, between_gini_min=gmin, band_is_top=True) \
        == "stratified_chiefdom"
    # unequal region but NOT a top band -> complex (it is subordinate, not a chiefly centre)
    assert society_from_character(PACKED, 0.8, between_gini=0.45, between_gini_min=gmin, band_is_top=False) \
        == "complex_forager"


def test_MODEL_relational_gate_removes_the_spurious_stratification():
    """In the affluent-egalitarian canonical world the level-only classifier reads ~36% stratified; the relational
    gate reads far fewer, because the between-band Gini sits below the threshold."""
    import battery1_liveness as B1
    from collections import Counter
    from sic_games import runconfig
    base = dict(runconfig.load(refresh=True).get("DemographyConfig", {}))
    def _strat_frac(relational):
        cfg = dict(base); cfg["enable_relational_stratification"] = relational
        w = B1._build(cfg, n=300, patch=60, terr="coastal", clim="temperate", seed=1)
        for _ in range(600):
            w.step()
            if not w.agent_list:
                break
        soc = Counter(w._band_society.values())
        tot = sum(soc.values())
        return (soc.get("stratified_chiefdom", 0) / tot) if tot else 0.0
    off = _strat_frac(False)
    on = _strat_frac(True)
    assert on < off, f"relational gate must cut the spurious stratification (on={on:.2f} off={off:.2f})"
