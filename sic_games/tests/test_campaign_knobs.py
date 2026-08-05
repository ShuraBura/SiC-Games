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
    p, out = _run("_t_knob_extra", C_EXTRA_ON="enable_band_risk",
                  C_EXTRA_OFF="enable_landscape_packing")
    assert p.returncode == 0, f"{p.stdout[-3000:]}\n{p.stderr[-3000:]}"
    cfg = _config(out)
    assert cfg["enable_band_risk"] is True
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
    allowed = {"enable_infanticide",                     # documented UNIMPLEMENTED STUB
               "enable_genealogy_log",                   # observer, and C_GENEA=0 here
               "enable_bud_hazard",                      # alternate path to the legacy budding one
               "enable_stratification_inequality_gate",  # R-103, criterion known wrong
               "enable_band_risk",                       # measured DEAD END (F.2 run_3i death spiral)
               # A CANDIDATE under evaluation, not a built mechanism awaiting activation: a structural
               # change to assabiyah, measured and defensible but NOT adopted (Addendum 23). C_ALLON must
               # not adopt a model change by side effect.
               "enable_leaky_assabiyah"}
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
