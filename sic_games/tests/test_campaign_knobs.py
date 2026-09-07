"""The campaign's C_* knobs must actually reach the config — and must not break the run reaching them.

WHY THIS EXISTS (R-106, 2026-08-04). `run_campaign.py` is how every campaign, battery and sweep in this arc
gets its configuration, and its knobs are parsed inside a 150-line `main()`. The C_PARAM knob's first version
did this:

    for item in _pv:
        k, v = item.split("=", 1)

`k` was already bound, 90 lines earlier, to the TERRAIN KNOB DICT. Every C_PARAM run therefore died in the
`TerrainWorld` constructor with a bare `'str' object has no attribute 'get'` — 24 arms into a `cv_safe`
sweep, whose harness read the missing trajectories as "no arms" and printed a tidy empty table. The knob was
smoke-tested when it was written; the smoke test checked that the VALUE parsed, not that the RUN survived.

So these tests drive the actual script as a subprocess and assert both halves: the process exits 0 AND the
dumped `meta.demography_config` carries the requested value. A knob that parses but kills the run, or runs but
silently drops the override, fails here. Three steps and 150 founders, so the whole file is seconds.
"""
import json
import os
import subprocess
import sys

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
SCRIPT = os.path.join(ROOT, "sic_games", "outputs", "substrate_run", "run_campaign.py")
OUTDIR = os.path.dirname(SCRIPT)

# Small enough to run in a test, large enough that the world, the bands and the config dump are all real.
BASE = dict(C_STEPS="3", C_FOUNDERS="150", C_MAXMIN="3", C_LOGEVERY="600", C_GENEA="0",
            C_TERR="coastal", C_CLIM="temperate", C_SEED="0")


def _run(tag, **knobs):
    """Run the campaign to completion and return its dumped demography config."""
    env = dict(os.environ, **BASE, **knobs, C_TAG=tag)
    p = subprocess.run([sys.executable, "-u", SCRIPT], cwd=ROOT, env=env,
                       capture_output=True, text=True, timeout=600)
    return p, os.path.join(OUTDIR, f"campaign_trajectory{tag}.json")


def _config(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)["meta"]["demography_config"]


def test_c_param_reaches_the_config_and_the_run_survives():
    """The regression proper: the run must FINISH, not merely parse the knob."""
    p, out = _run("_t_knob_param", C_PARAM="cv_safe=0.052")
    assert p.returncode == 0, f"campaign died with C_PARAM set:\n{p.stdout[-3000:]}\n{p.stderr[-3000:]}"
    assert os.path.exists(out), "campaign exited 0 but wrote no trajectory"
    assert _config(out)["cv_safe"] == pytest.approx(0.052)


def test_c_param_takes_several_fields_and_parses_types():
    p, out = _run("_t_knob_param_multi", C_PARAM="cv_safe=0.06,band_split_size=50")
    assert p.returncode == 0, f"{p.stdout[-3000:]}\n{p.stderr[-3000:]}"
    cfg = _config(out)
    assert cfg["cv_safe"] == pytest.approx(0.06)
    # int field must arrive as an int, not the string "50" — pydantic would coerce, but the knob is what
    # declares the type, and a str reaching an int field elsewhere is how a sweep silently does nothing.
    assert cfg["band_split_size"] == 50


def test_c_param_rejects_an_unknown_field():
    """A typo must STOP the run. Silently ignoring it would make a swept arm identical to its control and
    read as a clean null — the failure mode this arc has already hit three times."""
    p, _ = _run("_t_knob_param_bad", C_PARAM="cv_saef=0.05")
    assert p.returncode != 0
    assert "unknown config field" in (p.stdout + p.stderr)


def test_c_extra_on_and_off_reach_the_config():
    # was `enable_band_risk`, deleted 2026-08-06; any live flag exercises the same C_EXTRA_ON path
    p, out = _run("_t_knob_extra", C_EXTRA_ON="enable_bud_hazard",
                  C_EXTRA_OFF="enable_landscape_packing")
    assert p.returncode == 0, f"{p.stdout[-3000:]}\n{p.stderr[-3000:]}"
    cfg = _config(out)
    assert cfg["enable_bud_hazard"] is True
    assert cfg["enable_landscape_packing"] is False


def test_c_allon_leaves_no_dark_mechanism_but_the_documented_four():
    """The supervisor rule is that every BUILT mechanism runs unless it is off for an ablation. C_ALLON is
    what enforces it, so with no other knob set the four documented exclusions are the ONLY flags allowed
    to stay off.

    This is the assertion that caught the real defect: C_ALLON used to skip every knob-controlled flag
    unconditionally, so ten mechanisms stayed dark behind their knobs' OFF defaults."""
    p, out = _run("_t_knob_allon", C_ALLON="1")
    assert p.returncode == 0, f"{p.stdout[-3000:]}\n{p.stderr[-3000:]}"
    cfg = _config(out)
    off = {k for k, v in cfg.items() if k.startswith("enable_") and v is not True}
    # `enable_infanticide` (dead stub) and `enable_band_risk` (measured death spiral, inert at its default)
    # were both on this list and are now DELETED — the exclusion list shrank by deletion, not by exception.
    allowed = {"enable_genealogy_log",                   # observer, and C_GENEA=0 here
               "enable_bud_hazard",                      # alternate path to the legacy budding one
               "enable_stratification_inequality_gate",  # R-103, criterion known wrong
               # Added 2026-08-06 by the ON-but-dead gate: C_ALLON was turning both ON at magnitude 0.0.
               # pathogen_gamma awaits its Cashdan sweep; malnutrition_fission_gain was the R-106 negative
               # control and its FLAG should have been off rather than its gain zeroed.
               "enable_terrain_pathogen",
               "enable_malnutrition_fission",
               # A CANDIDATE under evaluation, not a built mechanism awaiting activation: a structural
               # change to assabiyah, measured and defensible but NOT adopted (Addendum 23). C_ALLON must
               # not adopt a model change by side effect.
               "enable_leaky_assabiyah",
               # SETTLEMENT-RUNAWAY / HELD CANDIDATES retained as ablation controls. Full reasons are in
               # run_campaign.py's C_ALLON `_skip` set — one copy. `enable_emergent_village_founding` (the rule
               # that replaced them) and `enable_village_identity` (Addendum 54) are canonically ON and so absent.
               "enable_bud_site_separation", "enable_exclusive_village_membership",
               # `enable_bud_requires_occupancy` (adopted Addendum 53) is now SUPERSEDED by the settlement pair
               # (Addendum 61) and retired to dark — the colonizing path founds daughters with its own spacing.
               "enable_bud_requires_occupancy",
               # BUILT-but-HELD candidates (R-106), each with a measured hold reason in the _skip set:
               # hunger_dispersal (Colson famine flight; halves population, empties savanna), founding_delay
               # (marginal, trips the age-structure CTB via a startup transient, no lit anchor), and
               # village_catchment_spread (fixes over-clustering but the population runs away without a brake).
               "enable_hunger_dispersal", "enable_founding_delay", "enable_village_catchment_spread",
               # A model CORRECTION under evaluation: it changes realised mortality in every
               # run, so it stays dark until the supervisor adopts it (2026-08-13).
               "enable_density_reference",
               # A CANDIDATE under evaluation: it changes the fertility of every run (2026-08-14).
               "enable_energetic_refractory"}
    assert off <= allowed, f"C_ALLON left undocumented mechanisms dark: {sorted(off - allowed)}"


def test_c_allon_does_not_enable_a_flag_whose_scale_is_still_zero():
    """A flag turned on with its magnitude at 0 is ON-but-dead — it reads as a live mechanism in the config
    dump and as INERT in an ablation, which is how 3 of battery 7's 6 'inert' verdicts arose. C_ALLON
    supplies each of these its validated value; if a knob default ever leaks through instead, this fails."""
    p, out = _run("_t_knob_allon_scales", C_ALLON="1")
    assert p.returncode == 0, f"{p.stdout[-3000:]}\n{p.stderr[-3000:]}"
    cfg = _config(out)
    for flag, scale in [("enable_lineage_branching", "lineage_branch_rate"),
                        ("enable_lineage_split", "lineage_split_rate"),
                        ("enable_ascribed_mate_choice", "ascribed_mate_strength")]:
        if cfg[flag] is True:
            assert cfg[scale] > 0.0, f"{flag} is on but {scale}={cfg[scale]} — the mechanism cannot act"
    if cfg["enable_adaptive_connubium"] is True:
        # Cut-2's whole point is a LARGER mate-search pool; the cut-1 fallback is 3.
        assert cfg["mate_search_min_eligible"] > 3


def test_c_allon_brings_the_elite_magnitudes_with_the_elite_flags():
    """The elite FLAGS are not the elite layer. Their magnitudes live in ELITE_KW and default to 0.0, so
    `C_ALLON=1` alone used to enable ~10 elite mechanisms at zero strength — live in the config dump, dead in
    the world. C_ALLON now implies C_ELITE unless C_ELITE is explicitly set."""
    p, out = _run("_t_knob_allon_elite", C_ALLON="1")
    assert p.returncode == 0, f"{p.stdout[-3000:]}\n{p.stderr[-3000:]}"
    cfg = _config(out)
    for flag, scale in [("enable_leveling", "leveling_strength"),
                        ("enable_material_capture", "material_hide_frac"),
                        ("enable_leader_share", "leader_share_frac"),
                        ("enable_legitimacy", "legit_cred_gain"),
                        ("enable_rank_hierarchy", "rank_hierarchy_frac")]:
        assert cfg[flag] is True, f"{flag} should be on under C_ALLON"
        assert cfg[scale] > 0.0, f"{flag} is on but {scale}={cfg[scale]} — the mechanism cannot act"


def test_c_elite_zero_still_ablates_the_elite_layer_under_c_allon():
    """The mirror: an explicit C_ELITE=0 is an ablation and must survive C_ALLON — and it must leave the
    elite layer OFF, not on at zero strength. Half-ablating it (flags on, magnitudes 0) is the worst of both:
    the config dump says the mechanism ran and the world says it did nothing."""
    p, out = _run("_t_knob_allon_noelite", C_ALLON="1", C_ELITE="0")
    assert p.returncode == 0, f"{p.stdout[-3000:]}\n{p.stderr[-3000:]}"
    cfg = _config(out)
    assert cfg["leveling_strength"] == 0.0
    for flag in ("enable_leveling", "enable_material_capture", "enable_leader_share",
                 "enable_legitimacy", "enable_rank_hierarchy"):
        assert cfg[flag] is False, f"{flag} left ON under C_ELITE=0 — with its magnitude at 0 it is dead"


def test_an_explicitly_set_knob_still_beats_c_allon():
    """C_ALLON must not resurrect a deliberate ablation — otherwise no mechanism could be tested against
    the full stack at all."""
    p, out = _run("_t_knob_allon_ablate", C_ALLON="1", C_SOIL="0", C_BUD="0")
    assert p.returncode == 0, f"{p.stdout[-3000:]}\n{p.stderr[-3000:]}"
    cfg = _config(out)
    assert cfg["enable_soil_depletion"] is False
    assert cfg["enable_alluvial_renewal"] is False
    assert cfg["enable_village_budding"] is False


def _health(out):
    with open(out, encoding="utf-8") as fh:
        return json.load(fh)["meta"]["climate_health"]


def test_climate_runs_by_default_and_reports_its_own_health():
    """DEFAULT FLIPPED 2026-08-06. Climate variability used to be off unless `C_CLIMATE=1`, which meant the
    whole layer sat out every experiment this project ran while reading as built — including four searches
    for Malthusian and secular cycles conducted with the slow driver switched off.

    DEFAULT FLIPPED BACK 2026-08-22, by the supervisor: "let's set Earth climate as a default condition for
    now. The variations belong to a later stage, when everything works well already." The baseline is now
    Earth -- a_seas 0.4, seasonality live, every variability channel off -- and variability is opted INTO
    with C_CLIMATE=1.

    THE GUARD THIS TEST EXISTS FOR IS UNCHANGED, and is what matters: the layer must not sit dark while
    reading as built. So it now asserts the channels come LIVE WHEN ENABLED, rather than that they are on by
    default. `season` is the one channel guaranteed live on any world, so it is still the assertion that
    fails loudly if the layer is ever silently unplugged."""
    p, out = _run("_t_clim_default", C_CLIMATE="1")
    assert p.returncode == 0, f"{p.stdout[-3000:]}\n{p.stderr[-3000:]}"
    h = _health(out)
    assert h, "the run carried no climate_health block"
    assert h["season"]["verdict"] == "LIVE"
    assert h["interannual"]["verdict"] in ("LIVE", "RARE"), h["interannual"]
    assert h["season"]["min"] < 1.0, "a live seasonal channel must depress the field somewhere"


def test_the_caribou_channel_is_on_now_that_its_thesis_is_filed():
    """This assertion was `== "OFF"` for one morning (2026-08-06). The caribou amplitude and period were
    credited to a thesis nobody could open, so the channel was excluded by name while everything else ran.

    The supervisor filed it the same afternoon. Reading it CONFIRMED the amplitude (.871, the median of the 19
    cyclic herds among 43 collected) and FALSIFIED the period band we had carried — 40–90 yr, credited to a
    Bergerud who is not cited in the thesis at all, against an observed 23–67. Corrected and switched on.

    Asserted as "not OFF" rather than "LIVE" because the channel is steppe-masked: on a world with no steppe
    the honest verdict is UNREACHABLE, and that is a property of the world, not a regression.

    RUN WITH C_CLIMATE=1 from 2026-08-22: the Earth baseline is now the default and variability is opted into.
    The point of this test is that the channel is not silently unplugged WHEN ASKED FOR -- which is exactly
    what it caught in the first place -- not that it runs in every campaign."""
    p, out = _run("_t_clim_caribou", C_CLIMATE="1")
    assert p.returncode == 0, f"{p.stdout[-3000:]}\n{p.stderr[-3000:]}"
    assert _health(out)["caribou"]["verdict"] != "OFF", (
        "caribou was switched on when its source was filed; OFF means it got unplugged again")


def test_the_EARTH_BASELINE_is_the_default_and_carries_no_variability():
    """PINS THE NEW DEFAULT (2026-08-22) so it cannot drift back unnoticed, the same way the old one did.

    WHY IT WAS CHANGED, measured: `a_seas` is drawn per world from an obliquity lottery, eps ~ U[0,60] deg.
    Seed 0 -- which EVERY canonical run uses -- draws eps 50.7 deg giving a_seas 0.779, the SECOND HIGHEST of
    twelve seeds against a median of 0.464 and Earth's 0.4. At 0.779 an arid cell yields 0.44 BURN at the
    seasonal trough against a lone adult's requirement of 1.0, so the world cannot feed anyone for part of
    every year and four separate mechanism-level fixes failed against that floor. The amplitude is also not
    anchored: `obliquity_to_amplitude` calls itself "a PROVISIONAL bounding heuristic ... NOT a
    sunlight-to-food transfer function"."""
    p, out = _run("_t_clim_earth")
    assert p.returncode == 0, p.stdout[-3000:] + p.stderr[-3000:]
    with open(out, encoding="utf-8") as fh:
        c = json.load(fh)["meta"]["climate_config"]
    assert c["a_seas"] == 0.4, f"the Earth baseline is a_seas 0.4, got {c['a_seas']}"
    assert c["enable_seasonality"] is True, "Earth has seasons -- seasonality must stay live"
    for ch in ("enable_climate_lottery", "enable_interannual", "enable_regime_shift",
               "enable_caribou_swing", "enable_llanos_flood", "enable_eccentricity_mean"):
        assert c[ch] is False, f"{ch} is on by default; variability is opted INTO with C_CLIMATE=1"


def test_the_flat_climate_control_is_still_reachable():
    """A control has to be CHOOSABLE. `C_CLIMATE=0` reproduces the pre-2026-08-06 world — fixed seasonal
    sine, no interannual variability at any timescale — which is the arm every historical result used and
    the one a climate ablation compares against."""
    p, out = _run("_t_clim_control", C_CLIMATE="0")
    assert p.returncode == 0, f"{p.stdout[-3000:]}\n{p.stderr[-3000:]}"
    h = _health(out)
    assert h["interannual"]["verdict"] == "OFF"
    assert h["regime"]["verdict"] == "OFF"
    assert h["eccentricity"]["verdict"] == "OFF"
