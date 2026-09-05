"""The run-configuration files must not drift from the code, and must reproduce the canonical stack EXACTLY.

`config/mechanisms.toml` and `config/parameters.toml` are authoritative for a run (see
`sic_games/runconfig.py`). That is only safe if two things hold, and both are asserted here:

  1. COVERAGE — every field of every configured class appears in the files, and the files contain no field
     that does not exist. Otherwise a new mechanism could be added in code and silently never appear in the
     file a human reads before launching, which is the failure the files were built to end.

  2. FIDELITY — building from the files reproduces, field for field, the configuration a CANONICAL RUN
     actually uses: `run_campaign.py` with `C_ALLON=1`, read back from its own `meta.demography_config`.
     Comparing against a re-derived preset instead is what let `divorce_rate` drift — the file asserted
     0.004 while every campaign ran R-78's calibrated 0.005, and this test passed throughout (Addendum 21).
     The check is only worth anything if both sides come from the same place a result comes from.

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

OWNERS = ["DemographyConfig", "ClimateConfig", "SubstrateConfig", "CarbonConfig", "KcalEconomyConfig"]


def _canonical():
    """The configuration a CANONICAL run actually uses, read back from a run — not re-derived.

    This used to be `emergent_village_demog() + VILLAGE + ELITE`, battery1's overlay stack, and the fidelity
    check therefore compared the files against a SECOND copy of the configuration rather than against the
    configuration itself. The two drifted, exactly as a second copy does: the overlay carried
    `divorce_rate = 0.004` over R-78's calibrated 0.005, so the authoritative file asserted a number no
    campaign has ever run, and this test passed the whole time (R-106 Addendum 21).

    So it asks the campaign, the same way `tools/gen_runconfig.py` does — a two-step run with `C_ALLON=1`,
    whose dumped `meta.demography_config` is what a canonical run uses by construction.
    """
    import json
    import subprocess
    import tempfile
    camp = os.path.join(ROOT, "sic_games", "outputs", "substrate_run", "run_campaign.py")
    # PID-SUFFIXED. A fixed tag means two concurrent pytest runs write and read the same trajectory file and
    # clobber each other — observed as two spurious failures here that passed in isolation. The campaign's
    # output path is derived from C_TAG, so making the tag unique per process is the whole fix.
    tag = f"_t_runconfig_fidelity_{os.getpid()}"
    out = os.path.join(os.path.dirname(camp), f"campaign_trajectory{tag}.json")
    env = dict(os.environ, C_ALLON="1", C_TAG=tag, C_STEPS="2", C_FOUNDERS="150", C_MAXMIN="5",
               C_LOGEVERY="600", C_GENEA="0")
    with tempfile.TemporaryFile() as devnull:
        p = subprocess.run([sys.executable, "-u", camp], cwd=ROOT, env=env,
                           stdout=devnull, stderr=subprocess.PIPE, text=True, timeout=600)
    assert p.returncode == 0 and os.path.exists(out), \
        f"the canonical campaign would not run, so fidelity cannot be checked:\n{p.stderr[-2000:]}"
    try:
        with open(out, encoding="utf-8") as fh:
            return json.load(fh)["meta"]
    finally:
        for f in (out, out.replace("trajectory", "progress").replace(".json", ".txt")):
            try:
                os.remove(f)
            except OSError:
                pass


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


@pytest.mark.slow
@pytest.mark.parametrize("owner,meta_key", [("DemographyConfig", "demography_config"),
                                            ("SubstrateConfig", "substrate_config")])
def test_building_from_files_reproduces_the_canonical_run_exactly(owner, meta_key):
    """FIDELITY: the whole safety argument. If this drifts, a run no longer does what the file says.

    PARAMETRISED OVER OWNER CLASSES 2026-08-17, because checking only DemographyConfig left the exact hole it
    was built to close. `SubstrateConfig` was constructed inline at the campaign call site with `**GRP`
    imported from a 2026 one-off script, so `config/parameters.toml` stated `group_safety_max = 0.0` and
    `group_mate_min = 0.0` -- the grouping drives OFF -- while EVERY campaign ran them at 8.0 / 15.0. Those
    two multipliers impose a 20.6x penalty for leaving a band, against a terrain signal whose entire range is
    4.8x, so the authoritative file was silent about the strongest force in the model's spatial behaviour.
    One class-shaped blind spot, invisible to a per-field check.
    """
    import importlib
    mod = importlib.import_module("sic_games.demography" if owner == "DemographyConfig" else "sic_games.config")
    cls = getattr(mod, owner)
    from_files = runconfig.build(owner)
    canon = _canonical().get(meta_key, {})
    assert canon, f"the campaign does not dump {meta_key}; fidelity for {owner} cannot be checked"
    diffs = {f: (canon[f], getattr(from_files, f))
             for f in cls.model_fields
             if f in canon and canon[f] != getattr(from_files, f)}
    assert not diffs, (
        f"{len(diffs)} field(s) differ between what a canonical run uses and what the files say "
        f"(run, file): { {k: v for k, v in list(diffs.items())[:10]} }\n"
        f"Regenerate with: py -3 tools/gen_runconfig.py")


@pytest.mark.slow
def test_the_files_describe_the_stack_the_supervisor_rule_asks_for():
    """The standing rule is that every BUILT mechanism runs unless it is off for an ablation, so the
    authoritative file must show only the documented exclusions dark. A file that quietly listed 27 dark
    mechanisms is the situation these files were created to end."""
    canon = _canonical()["demography_config"]
    off = {k for k, v in canon.items() if k.startswith("enable_") and v is not True}
    # enable_infanticide + enable_band_risk were on this list and are now DELETED (2026-08-06): the
    # exclusion list shrank by deletion rather than by a longer excuse.
    allowed = {"enable_genealogy_log", "enable_bud_hazard",
               "enable_stratification_inequality_gate",
               # ON-but-dead at magnitude 0.0 until their calibration lands (2026-08-06, Charter §12)
               "enable_terrain_pathogen", "enable_malnutrition_fission",
               # A CANDIDATE under evaluation rather than a built mechanism awaiting activation — a
               # structural change to assabiyah that is measured and defensible but NOT adopted (Addendum
               # 23). C_ALLON must not adopt a model change by side effect.
               "enable_leaky_assabiyah",
               # SETTLEMENT-RUNAWAY CANDIDATES, measured and REJECTED (2026-08-12). Each was built while
               # diagnosing the budding runaway and each failed on measurement, so each stays dark and is
               # retained only as an ablation control. The reasons live in run_campaign.py's C_ALLON `_skip`
               # set; they are not repeated here so there is one copy to keep true.
               #   bud_site_separation          works, but imposes 50 km against a ~20 km filed anchor
               #   exclusive_village_membership no spacing on its own; raises churn
               # bud_requires_occupancy (Addendum 53) and village_identity (Addendum 54, after its
               # multi-biome A/B) were ADOPTED and are canonically ON, as is
               # `enable_emergent_village_founding` — so all three are deliberately absent here.
               "enable_bud_site_separation", "enable_exclusive_village_membership",
               # A model CORRECTION under evaluation: it changes realised mortality in every
               # run, so it stays dark until the supervisor adopts it (2026-08-13).
               "enable_density_reference",
               # A CANDIDATE under evaluation: it changes the fertility of every run (2026-08-14).
               "enable_energetic_refractory",
               # ACUTE-DISPERSAL / FOUNDING-DELAY candidates under evaluation (R-106, 2026-08-28..09-02),
               # built and CTB'd but EQUIVOCAL, so held dark until the supervisor adopts them. Reasons live
               # in run_campaign.py's C_ALLON `_skip` set (not repeated here — one copy to keep true):
               #   hunger_dispersal  improves the demography markers but roughly halves population and
               #                     empties the degenerate savanna; the loss is fertility, not death.
               #   founding_delay    marginal; trips the age-structure CTB through a startup transient; no
               #                     literature anchor for the delay length yet.
               "enable_hunger_dispersal", "enable_founding_delay",
               # VILLAGE CATCHMENT SPREAD (R-106, 2026-09-02): fixes over-clustering but removes the
               # density-disease Malthusian brake -> population runaway; held until a replacement brake is
               # built. Reason lives in run_campaign.py _skip.
               "enable_village_catchment_spread",
               # BUD-REQUIRES-OCCUPANCY superseded + retired (R-106, 2026-09-05, Addendum 61). The colonizing-
               # budding pair replaces it (founds daughters directly with density-scaled spacing); it trapped the
               # population at 2% of carrying capacity, so it is now dark. Reason in run_campaign.py _skip.
               # (colonizing_budding and village_density_disease were ADOPTED here -> canonically ON, so they are
               # deliberately absent from this allowed-dark set.)
               "enable_bud_requires_occupancy"}
    assert off <= allowed, f"undocumented mechanisms dark in the canonical run: {sorted(off - allowed)}"


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


def test_every_climate_channel_is_in_the_files():
    """The climate channels were `ClimateField` constructor kwargs rather than config fields, which is exactly
    how the whole variability apparatus — ENSO, the regime telegraph, caribou, llanos — stayed switched off in
    every run this project has done without anyone noticing (R-106). They are configuration now, so they must
    appear in the file a human reads before launching, on the same footing as the social mechanisms."""
    from sic_games.climate import ClimateConfig
    data = runconfig.load(refresh=True).get("ClimateConfig", {})
    missing = sorted(set(ClimateConfig.model_fields) - set(data))
    assert not missing, (f"climate field(s) absent from config/*.toml: {missing}\n"
                         f"Regenerate with: py -3 tools/gen_runconfig.py")
    for ch in ("enable_interannual", "enable_regime_shift", "enable_caribou_swing",
               "enable_llanos_flood", "enable_eccentricity_mean"):
        assert ch in data, f"{ch} must be individually listed so it can be checked on its own"


def test_climate_defaults_reproduce_the_historical_field():
    """Adopting ClimateConfig must not silently change any prior result. Its defaults have to rebuild the
    hand-written `ClimateField(base, a_seas=0.4, regime_driver=None)` that every campaign used."""
    from sic_games.climate import ClimateConfig
    c = ClimateConfig()
    assert c.a_seas == 0.40 and c.enable_seasonality is True
    assert c.enable_climate_lottery is False
    for ch, val in (("interannual_amp", 0.0), ("regime_amp", 0.0), ("caribou_amp", 0.0),
                    ("llanos_flood_amp", 0.0), ("mean_factor", 1.0)):
        assert getattr(c, ch) == val, f"{ch} default changed — prior runs are no longer reproducible"
