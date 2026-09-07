"""CTB for the run-file loader — a run is a file, and the file must be the only thing that decides.

WHAT THIS GUARDS. Configuration used to arrive in four layers across 61 environment variables, and every
"what was actually on?" failure in this project came from one layer silently overwriting another. The single
file removes the layers; these tests remove the ways a file could quietly fail to mean what it says.

The constructed cases are the failure modes, not the happy path:
    a partial file          must RAISE, never silently default the rest
    a mistyped section      must RAISE, never be ignored
    a mistyped key          must RAISE
    an ON-but-dead flag     must RAISE, same rule as everywhere else
    a resolved file         must state EVERY field, so nothing takes a code default
"""
import textwrap

import pytest

from sic_games import runspec

MINIMAL = """
[run]
steps = 10

[mechanisms]
enable_soil_depletion = false

[parameters]
cv_safe = 0.037
"""


def _write(tmp_path, text, name="arm.toml"):
    p = tmp_path / name
    p.write_text(textwrap.dedent(text), encoding="utf-8")
    return p


def test_a_run_file_loads_its_three_sections(tmp_path):
    s = runspec.load(_write(tmp_path, MINIMAL))
    assert s.run["steps"] == 10
    assert s.mechanisms["enable_soil_depletion"] is False
    assert s.parameters["cv_safe"] == 0.037


def test_the_runs_identity_is_its_filename(tmp_path):
    """A trajectory tagged from the config it used cannot be mislabelled. A hand-passed tag could, and did."""
    s = runspec.load(_write(tmp_path, MINIMAL, "ablation_soil_off.toml"))
    assert s.name == "ablation_soil_off"
    assert s.run["tag"] == "_ablation_soil_off"


def test_a_missing_section_RAISES_rather_than_defaulting_the_rest(tmp_path):
    """THE CENTRAL GUARANTEE. A partial file that silently took defaults for everything else would recreate
    the exact ambiguity the single file exists to end — a run that looks configured and mostly is not."""
    for missing, text in [("mechanisms", "[run]\nsteps=1\n[parameters]\ncv_safe=0.03\n"),
                          ("parameters", "[run]\nsteps=1\n[mechanisms]\nenable_soil_depletion=false\n"),
                          ("run", "[mechanisms]\nenable_soil_depletion=false\n[parameters]\ncv_safe=0.03\n")]:
        with pytest.raises(SystemExit) as e:
            runspec.load(_write(tmp_path, text, f"missing_{missing}.toml"))
        assert missing in str(e.value)


def test_an_unknown_section_RAISES(tmp_path):
    """A mistyped `[mechanism]` (singular) that was ignored would run the canonical defaults and report
    success — the shape of every silent-override bug this project has hit."""
    with pytest.raises(SystemExit) as e:
        runspec.load(_write(tmp_path, MINIMAL + "\n[mechanism]\nenable_leveling = false\n"))
    assert "unknown section" in str(e.value)


def test_an_unknown_run_key_RAISES(tmp_path):
    with pytest.raises(SystemExit) as e:
        runspec.load(_write(tmp_path, "[run]\nsteps=1\nstpes=99\n[mechanisms]\n[parameters]\n"))
    assert "unknown [run] key" in str(e.value)


def test_a_mistyped_PARAMETER_name_RAISES_rather_than_being_dropped(tmp_path):
    """FOUND BY THIS FILE'S OWN FIRST RUN. `build()` filters to fields the class knows, so `cv_saef = 0.05`
    was silently discarded and the run used the default — a swept arm identical to its control, reading as a
    clean null. `C_PARAM` was hardened against exactly this in 2026-08-04 and moving the configuration into a
    file reintroduced it. A file may not fail quietly just because it is a file."""
    with pytest.raises(SystemExit) as e:
        runspec.load(_write(tmp_path, "[run]\nsteps=1\n[mechanisms]\n[parameters]\ncv_saef = 0.05\n"))
    assert "unknown field" in str(e.value) and "cv_saef" in str(e.value)


def test_a_mistyped_MECHANISM_name_RAISES(tmp_path):
    with pytest.raises(SystemExit) as e:
        runspec.load(_write(tmp_path, "[run]\nsteps=1\n[mechanisms]\nenable_levelling = false\n[parameters]\n"))
    assert "enable_levelling" in str(e.value)


def test_a_setting_in_the_wrong_section_RAISES(tmp_path):
    """`[mechanisms]` holds switches, `[parameters]` holds values. Letting them mix would make the file's own
    structure meaningless and hide an ON-but-dead pairing from a reader scanning one section."""
    with pytest.raises(SystemExit) as e:
        runspec.load(_write(tmp_path, "[run]\nsteps=1\n[mechanisms]\ncv_safe = 0.03\n[parameters]\n"))
    assert "wrong section" in str(e.value)


def test_a_missing_file_says_what_to_do(tmp_path):
    with pytest.raises(SystemExit) as e:
        runspec.load(tmp_path / "nope.toml")
    assert "A run is a file" in str(e.value)


def test_seed_is_the_only_permitted_override(tmp_path):
    """A seed sweep is one experiment repeated, not a different experiment — so the seed may come from the
    command line and NOTHING else may. Every other setting has to be written down first."""
    p = _write(tmp_path, MINIMAL)
    assert runspec.load(p).run["seed"] == 0
    assert runspec.load(p, seed=7).run["seed"] == 7
    # and the loader exposes no other override path
    import inspect
    assert set(inspect.signature(runspec.load).parameters) == {"path", "seed"}


def test_an_ON_but_dead_flag_in_a_run_file_RAISES(tmp_path):
    """The same rule as everywhere else. Moving configuration into a file must not make an inert mechanism
    expressible again — you ablate by turning the FLAG off, never by zeroing the magnitude."""
    text = MINIMAL + "\nenable_terrain_pathogen = true\n"     # lands in [parameters]? no — put it properly
    p = _write(tmp_path, """
        [run]
        steps = 10
        [mechanisms]
        enable_terrain_pathogen = true
        [parameters]
        pathogen_gamma = 0.0
        """)
    with pytest.raises(SystemExit) as e:
        runspec.build(runspec.load(p), "DemographyConfig")
    assert "ON-but-dead" in str(e.value)
    assert text  # (the malformed variant above is deliberately unused; kept to document the wrong shape)


def test_the_shipped_reference_file_states_every_field():
    """A RESOLVED file lists everything. A gap means the run silently takes a code default for that field,
    which is the difference between a record and a summary."""
    from pathlib import Path
    ref = Path(__file__).resolve().parents[2] / "config" / "runs" / "full_campaign.toml"
    if not ref.exists():
        pytest.skip("reference run file not generated yet")
    s = runspec.load(ref)
    assert runspec.coverage(s) == [], "the reference file does not state every config field"
    assert s.run["steps"] > 0 and s.run["founders"] > 0


def test_the_reference_file_matches_the_canonical_config_exactly():
    """The run file is generated FROM `config/*.toml`. If they ever disagree, the file that runs is not the
    file the provenance tooling checks — and `verify_anchor.py` / `audit_provenance.py` would be auditing a
    configuration nothing uses."""
    from pathlib import Path

    from sic_games import runconfig
    ref = Path(__file__).resolve().parents[2] / "config" / "runs" / "full_campaign.toml"
    if not ref.exists():
        pytest.skip("reference run file not generated yet")
    spec = runspec.load(ref)
    from_spec = runspec.build(spec, "DemographyConfig")
    from_files = runconfig.build("DemographyConfig")
    diffs = {f: (getattr(from_spec, f), getattr(from_files, f))
             for f in type(from_files).model_fields
             if getattr(from_spec, f) != getattr(from_files, f)}
    assert not diffs, f"run file and canonical config disagree: {dict(list(diffs.items())[:8])}"


def test_the_resolved_file_is_archived_next_to_the_run(tmp_path):
    """A finished run must CARRY its configuration. Pointing at a shared file in the repo is not the same
    thing, because the repo moves on and the run does not."""
    p = _write(tmp_path, MINIMAL, "arm_x.toml")
    out = tmp_path / "outdir"
    dest = runspec.load(p).archive_to(out)
    assert dest.exists() and dest.name == "arm_x.resolved.toml"
    assert dest.read_text(encoding="utf-8") == p.read_text(encoding="utf-8")


# ── the seed-sweep collision (found 2026-08-08 by losing a sweep) ─────────────────────────────────────────

def _write_spec(tmp_path, seed=0, tag=None):
    """A minimal but VALID run file, built from the real base configs so it states every field."""
    import pathlib as _pl
    import subprocess
    import sys as _sys
    repo = _pl.Path(__file__).resolve().parents[2]
    subprocess.run([_sys.executable, str(repo / "tools" / "make_runconfig.py"), "ctb_seedtag",
                    "--steps", "3", "--founders", "150", "--seed", str(seed),
                    "--why", "CTB fixture: the seed-sweep tag collision"],
                   cwd=repo, check=True, capture_output=True)
    return repo / "config" / "runs" / "ctb_seedtag.toml"


def test_overriding_the_seed_puts_the_seed_in_the_TAG(tmp_path):
    """THE DEFECT. Every output path the harness builds is `<name><tag>.<ext>` and the tag came only from the
    file, so `--seed 1..7` over one config wrote SEVEN runs to the SAME four files and left only the last.
    28 completed runs, 4 surviving, and no error anywhere — the comment on the override itself calls it
    "a seed sweep is one experiment repeated"."""
    p = _write_spec(tmp_path, seed=0)
    tags = {runspec.load(p, seed=s).run["tag"] for s in (1, 2, 3)}
    assert len(tags) == 3, f"seeds collide on one tag: {tags} — a sweep would overwrite itself"
    assert all(t.endswith(f"_s{s}") for s, t in zip((1, 2, 3), sorted(tags)))


def test_NOT_overriding_the_seed_leaves_the_tag_untouched(tmp_path):
    """The back-compat half, and the reason the suffix is conditional: every run that does not use `--seed`
    must keep the exact filename it had before, or prior outputs stop matching their configs."""
    p = _write_spec(tmp_path, seed=0)
    assert runspec.load(p).run["tag"] == runspec.load(p, seed=0).run["tag"] == "_ctb_seedtag"


def test_the_seed_itself_is_still_overridden(tmp_path):
    """The tag change must not disturb what the override is FOR."""
    p = _write_spec(tmp_path, seed=0)
    assert runspec.load(p, seed=5).run["seed"] == 5


# ── the seed is three things (2026-08-11) ─────────────────────────────────────────────────────────────────

def _spec_with(tmp_path, body):
    """Write a run file by copying a REAL resolved one and appending [run] keys, so it stays complete."""
    import pathlib as _pl
    src = _pl.Path(__file__).resolve().parents[2] / "config" / "runs" / "full_campaign.toml"
    text = src.read_text(encoding="utf-8")
    head, rest = text.split("[mechanisms]", 1)
    p = tmp_path / "split.toml"
    p.write_text(head.rstrip() + "\n" + body + "\n\n[mechanisms]" + rest, encoding="utf-8")
    return p


def test_the_three_roles_default_to_the_plain_seed(tmp_path):
    """BACK-COMPAT, and it is the whole safety argument: a run file that says nothing about the roles must
    behave exactly as it did when one integer did all three jobs."""
    s = runspec.load(_spec_with(tmp_path, ""), seed=3)
    assert s.run["world_seed"] == s.run["climate_seed"] == s.run["agent_seed"] == 3


def test_a_stated_role_is_PINNED_and_the_others_still_follow_the_seed(tmp_path):
    """The point of the split: hold the WORLD still and let the path vary. Before this, two 'seeds' were two
    different planets — `world_lottery_climate(seed)` draws relief, roughness, water, latitude and aridity
    from the preset ranges — so path variance could not be measured at all."""
    s = runspec.load(_spec_with(tmp_path, "world_seed = 0"), seed=5)
    assert s.run["world_seed"] == 0, "a stated role must not be overridden by --seed"
    assert s.run["climate_seed"] == 5 and s.run["agent_seed"] == 5


def test_each_stated_role_lands_in_the_TAG(tmp_path):
    """Same lesson as the seed-tag collision, applied before it can bite: a decomposition sweep varies
    agent_seed alone over one pinned world, and without a distinguishing tag every arm writes to one path."""
    tags = {runspec.load(_spec_with(tmp_path, f"world_seed = 0\nagent_seed = {a}")).run["tag"]
            for a in (1, 2, 3)}
    assert len(tags) == 3, f"agent-seed arms collide on one tag: {tags}"
    assert all("_w0_a" in t for t in tags), tags


def test_an_UNSTATED_role_does_not_touch_the_tag(tmp_path):
    """The suffix must be earned. A file that leaves the roles implicit keeps its original output filename."""
    assert runspec.load(_spec_with(tmp_path, "")).run["tag"] == "_split"
