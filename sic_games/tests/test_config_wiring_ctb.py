"""CTB for `run_campaign.py --config` — the file must be the ONLY thing that configured the run.

This is the wiring, not the loader (`test_runspec_ctb.py` covers that). What it has to prove is narrower and
more important: that when a run names a file, nothing else got a vote.

THE FAILURE IT GUARDS AGAINST, which actually happened. On 2026-08-06 the first file-loading path merged the
file OVER a config the environment knobs had already resolved, and every preset-style ablation was silently
discarded — `C_SOIL=0` came back True. The run reported success, the banner said soil was on, and an
experiment asking "what does soil do?" would have compared the full stack against itself.

So the constructed cases are about PROVENANCE of each setting, not about whether the run finishes:
    --config alone            -> every value traceable to the file
    --config + a C_* knob     -> REFUSED, not merged
    --seed                    -> the one override, and it lands
    no --config               -> the legacy path still works, unchanged
    finished run              -> carries its own resolved config
"""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "sic_games" / "outputs" / "substrate_run" / "run_campaign.py"
OUTDIR = SCRIPT.parent
RUNS = ROOT / "config" / "runs"

pytestmark = pytest.mark.skipif(not (RUNS / "full_campaign.toml").exists(),
                                reason="reference run file not generated")


def _clean_env(**extra):
    """A --config run must start from an environment with NO C_* in it. Inheriting a stray knob from the
    parent shell is exactly the ambiguity this change removes, so the tests must not smuggle one in either."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("C_")}
    env.update(extra)
    return env


def _make(name, *args):
    p = subprocess.run([sys.executable, str(ROOT / "tools" / "make_runconfig.py"), name, *args],
                       cwd=ROOT, capture_output=True, text=True, timeout=180)
    assert p.returncode == 0, p.stdout + p.stderr
    return RUNS / f"{name}.toml"


def _run(cfg, *args, env=None):
    p = subprocess.run([sys.executable, "-u", str(SCRIPT), "--config", str(cfg), *args],
                       cwd=ROOT, env=env or _clean_env(), capture_output=True, text=True, timeout=600)
    return p


def _meta(tag):
    with open(OUTDIR / f"campaign_trajectory{tag}.json", encoding="utf-8") as fh:
        return json.load(fh)["meta"]


@pytest.fixture(scope="module")
def tiny():
    return _make("ctb_tiny", "--steps", "3", "--founders", "150",
                 "--why", "CTB fixture: shortest run that still builds a world and a config")


def test_a_config_run_takes_every_setting_from_the_file(tiny):
    from sic_games import runspec
    p = _run(tiny)
    assert p.returncode == 0, p.stdout[-3000:] + p.stderr[-3000:]
    meta = _meta("_ctb_tiny")
    spec = runspec.load(tiny)
    cfg = meta["demography_config"]
    diffs = {k: (cfg[k], v) for k, v in spec.config_values().items()
             if k in cfg and cfg[k] != v}
    assert not diffs, f"the run disagrees with its own config file: {dict(list(diffs.items())[:8])}"
    assert meta["steps"] == 3 and meta["founders"] == 150


def test_mixing_a_knob_with_a_config_is_REFUSED_not_merged(tiny):
    """THE REGRESSION, constructed. Merging is what silently discarded `C_SOIL=0`. There is no correct
    precedence between a file and a knob — a run configured two ways is one nobody can describe afterwards —
    so the only safe answer is to stop."""
    p = _run(tiny, env=_clean_env(C_SOIL="0"))
    assert p.returncode != 0
    assert "configured ONE way" in (p.stdout + p.stderr)
    assert "C_SOIL" in (p.stdout + p.stderr)


def test_the_refusal_names_every_offending_knob(tiny):
    p = _run(tiny, env=_clean_env(C_SOIL="0", C_ELITE="1"))
    out = p.stdout + p.stderr
    assert p.returncode != 0 and "C_SOIL" in out and "C_ELITE" in out


def test_seed_is_the_one_override_and_it_reaches_the_run(tiny):
    """PREMISE CHANGED BY DESIGN 2026-08-11 (commit `3153dea`). An overridden seed now goes into the TAG, so a
    seed-5 run writes `_ctb_tiny_s5`, not `_ctb_tiny`.

    This test was the one that caught the change, and how it failed is worth keeping: it read `_ctb_tiny` and
    got seed 0 — a STALE file from an earlier run, not the run it had just launched. That is precisely the
    defect the tag fix exists for. Before the fix the seed-5 run would have OVERWRITTEN `_ctb_tiny`, the
    assertion would have passed, and a seed sweep would still have destroyed itself silently. The old form of
    this test could not have detected the bug it appeared to cover."""
    p = _run(tiny, "--seed", "5")
    assert p.returncode == 0, p.stdout[-3000:] + p.stderr[-3000:]
    assert _meta("_ctb_tiny_s5")["seed"] == 5, "the override did not reach the run"


def test_an_overridden_seed_does_not_touch_the_unsuffixed_output(tiny):
    """The half that makes a sweep survivable: a seed-5 run must leave the seed-0 output alone. Asserted on the
    file's mtime, because 'the seed is still 0' would also hold if the file had been rewritten identically."""
    base = OUTDIR / "campaign_trajectory_ctb_tiny.json"
    assert _run(tiny).returncode == 0
    before = base.stat().st_mtime_ns
    assert _run(tiny, "--seed", "6").returncode == 0
    assert base.stat().st_mtime_ns == before, "a seeded arm overwrote the unseeded one — the collision is back"
    assert _meta("_ctb_tiny")["seed"] == 0


def test_the_run_carries_its_own_resolved_config(tiny):
    """A finished run must be self-describing. Naming the repo file is not enough: the repo moves on and the
    run does not, so the resolved file is copied next to the output."""
    assert _run(tiny).returncode == 0
    meta = _meta("_ctb_tiny")
    assert meta["run_config"] == "ctb_tiny"
    archived = OUTDIR / meta["run_config_archived"]
    assert archived.exists()
    assert archived.read_text(encoding="utf-8") == Path(tiny).read_text(encoding="utf-8")


def test_the_trajectory_is_tagged_from_the_filename(tiny):
    """The run's identity IS its config's name, so a trajectory cannot be mislabelled by a hand-passed tag."""
    assert (OUTDIR / "campaign_trajectory_ctb_tiny.json").exists()


def test_an_ablation_file_actually_ablates():
    """The point of the whole scheme: a stated difference must show up in the run. If this passes while
    `test_mixing...` also passes, then the file is both sufficient and exclusive."""
    cfg = _make("ctb_ablate_soil", "--steps", "3", "--founders", "150",
                "--off", "enable_soil_depletion,enable_alluvial_renewal",
                "--why", "CTB: prove a stated difference reaches the run")
    p = _run(cfg)
    assert p.returncode == 0, p.stdout[-3000:] + p.stderr[-3000:]
    c = _meta("_ctb_ablate_soil")["demography_config"]
    assert c["enable_soil_depletion"] is False and c["enable_alluvial_renewal"] is False
    # and the canonical arm has them ON, so the ablation is a real contrast rather than a no-op
    from sic_games import runconfig
    assert runconfig.build("DemographyConfig").enable_soil_depletion is True


def test_the_legacy_knob_path_still_runs_untouched():
    """Nothing is converted yet. Until every harness moves, the env path must keep working exactly as it did —
    a migration that breaks the old road before the new one is finished is how a project loses a week."""
    env = _clean_env(C_STEPS="3", C_FOUNDERS="150", C_MAXMIN="3", C_LOGEVERY="600",
                     C_GENEA="0", C_TAG="_ctb_legacy", C_SEED="0")
    p = subprocess.run([sys.executable, "-u", str(SCRIPT)], cwd=ROOT, env=env,
                       capture_output=True, text=True, timeout=600)
    assert p.returncode == 0, p.stdout[-3000:] + p.stderr[-3000:]
    assert _meta("_ctb_legacy")["run_config"] is None, "a legacy run must be marked as having no config file"


def test_a_nonexistent_config_stops_the_run_with_advice():
    p = _run(ROOT / "config" / "runs" / "does_not_exist.toml")
    assert p.returncode != 0
    assert "A run is a file" in (p.stdout + p.stderr)
