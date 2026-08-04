"""The run-configuration files must not drift from the code, and must reproduce the canonical stack EXACTLY.

`config/mechanisms.toml` and `config/parameters.toml` are authoritative for a run (see
`sic_games/runconfig.py`). That is only safe if two things hold, and both are asserted here:

  1. COVERAGE — every field of every configured class appears in the files, and the files contain no field
     that does not exist. Otherwise a new mechanism could be added in code and silently never appear in the
     file a human reads before launching, which is the failure the files were built to end.

  2. FIDELITY — building from the files reproduces the canonical preset (`emergent_village_demog` + VILLAGE +
     ELITE) field for field. The files were GENERATED from that stack, so any difference means the generator,
     the loader or the preset has moved and the two have drifted apart.

If this test fails after adding a field, regenerate: `py -3 tools/gen_runconfig.py`.
"""
import os
import sys

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
for p in (os.path.join(ROOT, "sic_games", "outputs", "phase1_social_evolution"),
          os.path.join(ROOT, "sic_games", "outputs", "mechanism_battery")):
    if p not in sys.path:
        sys.path.insert(0, p)

from sic_games import runconfig  # noqa: E402
from sic_games.demography import DemographyConfig  # noqa: E402

OWNERS = ["DemographyConfig", "SubstrateConfig", "CarbonConfig", "KcalEconomyConfig"]


def _canonical():
    from battery1_liveness import ELITE, VILLAGE
    from run_se0_controlled_climate import emergent_village_demog
    return emergent_village_demog().model_copy(update=VILLAGE).model_copy(update=ELITE)


def test_files_exist_and_parse():
    data = runconfig.load(refresh=True)
    assert data, "no configuration parsed — the files are the authoritative source and must not be empty"
    assert "DemographyConfig" in data


def test_every_demography_field_is_in_the_files():
    """COVERAGE: a mechanism that exists in code but not in the file is invisible to the human check."""
    data = runconfig.load(refresh=True).get("DemographyConfig", {})
    missing = sorted(set(DemographyConfig.model_fields) - set(data))
    assert not missing, (
        f"{len(missing)} field(s) exist in DemographyConfig but not in config/*.toml: {missing[:12]}"
        f"{' ...' if len(missing) > 12 else ''}\nRegenerate with: py -3 tools/gen_runconfig.py")


def test_files_contain_no_field_that_left_the_code():
    data = runconfig.load(refresh=True).get("DemographyConfig", {})
    stale = sorted(set(data) - set(DemographyConfig.model_fields))
    assert not stale, (f"config/*.toml still lists field(s) removed from the code: {stale}\n"
                       f"Regenerate with: py -3 tools/gen_runconfig.py")


def test_all_79_mechanisms_are_listed():
    data = runconfig.load(refresh=True).get("DemographyConfig", {})
    code_flags = {f for f in DemographyConfig.model_fields if f.startswith("enable_")}
    file_flags = {f for f in data if f.startswith("enable_")}
    assert code_flags == file_flags, f"mechanism set differs: {code_flags ^ file_flags}"


@pytest.mark.parametrize("owner", OWNERS)
def test_owner_classes_build_from_the_files(owner):
    obj = runconfig.build(owner)
    assert obj is not None


def test_building_from_files_reproduces_the_canonical_stack_exactly():
    """FIDELITY: the whole safety argument. If this drifts, a run no longer does what the file says."""
    from_files = runconfig.build("DemographyConfig")
    canon = _canonical()
    diffs = {f: (getattr(canon, f), getattr(from_files, f))
             for f in DemographyConfig.model_fields
             if getattr(canon, f) != getattr(from_files, f)}
    assert not diffs, (
        f"{len(diffs)} field(s) differ between the canonical preset and the config files "
        f"(preset, file): { {k: v for k, v in list(diffs.items())[:10]} }\n"
        f"Regenerate with: py -3 tools/gen_runconfig.py")


def test_overrides_are_validated_and_visible():
    """An ablation must be explicit and must appear in the manifest, never silently applied."""
    with pytest.raises(SystemExit):
        runconfig.build("DemographyConfig", overrides={"enable_not_a_real_flag": True})
    m = runconfig.manifest("DemographyConfig", overrides={"enable_soil_depletion": True})
    assert "OVERRIDES" in m and "enable_soil_depletion" in m


def test_manifest_reports_the_dark_set():
    m = runconfig.manifest("DemographyConfig")
    assert "mechanisms ON" in m and "mechanisms OFF" in m
    assert "OFF:" in m, "the manifest must name the mechanisms that will NOT run"
