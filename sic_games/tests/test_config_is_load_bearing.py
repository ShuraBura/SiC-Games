"""`config/*.toml` can now SET a run, not merely describe one — R-106 step B, 2026-08-06.

THE ASYMMETRY THIS CLOSES. `tools/gen_runconfig.py` produces the files by executing `run_campaign.py` with
`C_ALLON=1` and recording the resolved `meta.demography_config`. So the files were a faithful RECORD of a run
and had no power to CAUSE one: "edit the file and you get that run" was not true, and a reader who assumed it
was would have been wrong in a way nothing would have told them.

`C_CFGSRC=files` makes the file the base configuration. The equivalence below is what makes that safe: the
file and the canonical run agree on every field, so loading it reproduces the canonical arm exactly rather
than approximately.

WHAT IS DELIBERATELY *NOT* DONE HERE. `preset` remains the default. A plain run and the file differ in 52
fields — the whole elite layer, budding, soil, intake fertility — so flipping the default would convert every
ad-hoc invocation into the full canonical stack. That is a scientific decision, not a refactor, and it is
recorded as such rather than taken quietly.
"""
import json
import os
import subprocess
import sys

import pytest

from sic_games import runconfig
from sic_games.demography import DemographyConfig

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
SCRIPT = os.path.join(ROOT, "sic_games", "outputs", "substrate_run", "run_campaign.py")
OUTDIR = os.path.dirname(SCRIPT)
BASE = dict(C_STEPS="3", C_FOUNDERS="150", C_MAXMIN="3", C_LOGEVERY="600", C_GENEA="0",
            C_TERR="coastal", C_CLIM="temperate", C_SEED="0")


def _run(tag, **knobs):
    env = dict(os.environ, **BASE, **knobs, C_TAG=tag)
    p = subprocess.run([sys.executable, "-u", SCRIPT], cwd=ROOT, env=env,
                       capture_output=True, text=True, timeout=600)
    out = os.path.join(OUTDIR, f"campaign_trajectory{tag}.json")
    assert p.returncode == 0, f"{p.stdout[-3000:]}\n{p.stderr[-3000:]}"
    with open(out, encoding="utf-8") as fh:
        return json.load(fh)["meta"]["demography_config"]


def test_the_file_reproduces_the_canonical_run_field_for_field():
    """THE EQUIVALENCE THAT MAKES THE INVERSION SAFE. Loading the file must give the same configuration the
    canonical run resolves to — not close, identical. If these ever diverge, `C_CFGSRC=files` silently runs
    something other than what the canonical arm ran, which is worse than not offering the option."""
    from_file = runconfig.build("DemographyConfig")
    from_run = _run("_t_cfg_allon", C_ALLON="1")
    diffs = {f: (from_run[f], getattr(from_file, f)) for f in DemographyConfig.model_fields
             if f in from_run and from_run[f] != getattr(from_file, f)}
    assert not diffs, f"{len(diffs)} field(s) differ (run, file): {dict(list(diffs.items())[:10])}"


def test_loading_from_files_gives_the_canonical_configuration():
    """`C_CFGSRC=files` must actually reach the run — the failure mode being a knob that parses and is then
    ignored, which this project has hit three times."""
    cfg = _run("_t_cfg_files", C_CFGSRC="files")
    from_file = runconfig.build("DemographyConfig")
    for f in ("enable_leveling", "enable_village_budding", "enable_legitimacy", "leveling_strength"):
        assert cfg[f] == getattr(from_file, f), f"{f} did not come from the file"


def test_an_explicit_knob_still_beats_the_file():
    """The files set the BASE; an ablation must still be expressible on top, or no controlled experiment can
    be run from a file-driven config."""
    cfg = _run("_t_cfg_files_ablate", C_CFGSRC="files", C_EXTRA_OFF="enable_leveling",
               C_PARAM="cv_safe=0.061")
    assert cfg["enable_leveling"] is False
    assert cfg["cv_safe"] == pytest.approx(0.061)


def test_the_default_is_still_the_preset_path_and_differs_from_the_file():
    """THE DECISION LEFT OPEN, pinned as a measurement so it cannot drift unnoticed. A plain run is NOT the
    canonical configuration; it has the elite layer and several substrate mechanisms off. This test documents
    the gap rather than blessing it — when the supervisor flips the default, this is the test to invert."""
    plain = _run("_t_cfg_plain")
    from_file = runconfig.build("DemographyConfig")
    diffs = [f for f in DemographyConfig.model_fields
             if f in plain and plain[f] != getattr(from_file, f)]
    assert len(diffs) > 20, (
        "the plain run now matches the file — if the default was intentionally flipped, update this test; "
        "if not, something changed the preset")
    assert plain["enable_leveling"] is False, "the plain arm still runs without the elite layer"


def test_the_files_refuse_to_be_silently_absent():
    """A missing config file must stop the run, not fall back to in-code defaults. A silent fallback would
    recreate exactly the 'what was actually on?' failure the files exist to end."""
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        env = dict(os.environ, SIC_CONFIG_DIR=d)
        p = subprocess.run([sys.executable, "-c",
                            "from sic_games import runconfig; runconfig.load(refresh=True)"],
                           cwd=ROOT, env=env, capture_output=True, text=True, timeout=120)
        assert p.returncode != 0
        assert "run configuration missing" in (p.stdout + p.stderr)
