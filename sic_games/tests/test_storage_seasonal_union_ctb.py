"""CTB for the STORAGE UNION GATE (R-106, 2026-09-07).

THE DEFECT. The overwintering store is gated PURELY on temperature (cell mean temp <= storage_temp_threshold_c,
15.25 C). A hot-but-seasonal savanna (mean ~19.5 C) is excluded, so it can never build a granary and has ZERO
buffer for its deep dry season; the population collapses to the unbuffered dry-trough capacity (pop 600 -> ~110
despite HIGHER mean food than temperate). The seasonality gate (storage_seasonality_gated) fixes savanna but
excludes cold-but-low-amplitude boreal instead (e0 -> 1.7). The two gates are exclusive; neither serves both.

THE FIX. `enable_storage_seasonal_union`: the overwintering zone is the UNION of the two limbs -- store where the
cell is cold ENOUGH (Binford ET, meat) OR seasonal ENOUGH (Testart, plant glut; Ju/'hoansi mongongo through the
dry season). Fixes savanna without breaking boreal.

LOAD-BEARING is `test_MODEL_savanna_stores_only_with_the_union`: in a hot savanna world the granary holds food
WITH the union on and ~nothing with it off (the temperature limb never fires there). The cold-world regression
test pins that a boreal world is UNCHANGED (its temperature limb already fired).
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for p in (ROOT / "sic_games" / "src", ROOT / "sic_games" / "outputs" / "mechanism_battery",
          ROOT / "sic_games" / "outputs" / "phase1_social_evolution"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from sic_games.demography import DemographyConfig  # noqa: E402


def test_the_flag_defaults_off():
    assert DemographyConfig().enable_storage_seasonal_union is False


def _run(clim, union, steps=200, seed=0):
    import battery1_liveness as B1
    from sic_games import runconfig
    cfg = dict(runconfig.load(refresh=True).get("DemographyConfig", {}))
    cfg["enable_storage_seasonal_union"] = union
    w = B1._build(cfg, n=600, patch=24, terr="coastal", clim=clim, seed=seed)
    for _ in range(steps):
        w.step()
        if not w.agent_list:
            break
    store = sum((getattr(w, "_cell_store", {}) or {}).values())
    return store, len(w.agent_list)


def test_MODEL_savanna_stores_only_with_the_union():
    """LOAD-BEARING. A hot savanna world builds a granary WITH the union on and holds ~nothing with it off
    (the temperature limb never fires at ~19.5 C), and the stored buffer keeps more of the population alive."""
    store_off, pop_off = _run("savanna", False)
    store_on, pop_on = _run("savanna", True)
    assert store_off == 0.0 or store_off < store_on * 1e-3, (
        f"the temperature gate should leave the hot savanna un-stored (off={store_off:.0f} on={store_on:.0f})")
    assert store_on > 0.0, f"the union must let the seasonal savanna store its glut (store={store_on:.0f})"
    assert pop_on > pop_off, f"the dry-season buffer must keep more alive (on={pop_on} off={pop_off})"


def test_the_union_does_not_change_a_cold_world():
    """REGRESSION. A cold boreal world already stores via the temperature limb, so the union adds nothing:
    the granary and the population are unchanged (the seasonal limb does not fire in low-amplitude boreal)."""
    store_off, pop_off = _run("boreal", False)
    store_on, pop_on = _run("boreal", True)
    assert store_on == store_off and pop_on == pop_off, (
        f"the union must not change a cold world (store {store_off:.0f}->{store_on:.0f}, pop {pop_off}->{pop_on})")
