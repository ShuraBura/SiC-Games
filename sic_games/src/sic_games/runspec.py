"""A RUN IS A FILE. One TOML per run, fully resolved, and nothing else decides what happened.

WHY (2026-08-07, supervisor decision). Configuration used to arrive in four layers — a Python preset, then
`C_ALLON`, then `C_EXTRA_ON/OFF`, then `C_PARAM` — across **61 environment variables**, with 15 harness scripts
setting them. Every layer was a chance for one to silently overwrite another, and there was no single place
that said what a run was. The cost is on the record:

  * 27 of 79 mechanisms were dark in the canonical preset and nobody knew
  * two conclusions were retracted because a control came from a different build
  * a mechanism audit produced 7 invalid verdicts by ablating flags that were already off
  * and on the day the file-loading path was first switched on, it silently DISCARDED every preset-style
    ablation: `C_SOIL=0` came back True, because the file replaced a config the knobs had already resolved

None of those are analysis mistakes. They are all "what was actually on?" mistakes, and they are what a layered
configuration buys you.

THE RULE. A run names one file. The file holds everything — how long, which world, every mechanism, every
parameter. A run that needs a reduction or an adjustment gets its OWN file, discussed and written first. There
is no way to nudge a run from the command line, because that is the affordance that produced the layers.

    py -3 run_campaign.py --config config/runs/full_campaign.toml

`--seed` is the single permitted override, because a seed sweep is the same experiment repeated rather than a
different one, and the seed used is recorded in the output either way.

FILE SHAPE — three sections, no inheritance at load time:

    [run]                       how the run executes
    steps = 2500
    seed = 0
    founders = 3000
    terrain = "coastal"
    climate = "temperate"

    [mechanisms]                every enable_* flag, all of them, explicitly
    enable_soil_depletion = false

    [parameters]                every calibrated value, all of them, explicitly
    cv_safe = 0.037

FULLY RESOLVED ON PURPOSE. The file is authored as base-plus-difference by `tools/make_runconfig.py`, but what
lands on disk lists every field. Inheritance resolved at LOAD time is how you get a file that reads one way and
runs another; inheritance resolved at AUTHORING time gives you both a DRY source and a self-contained record.
The run copies its resolved file into its own output directory, so a finished run carries the exact
configuration it used and a `diff` between two runs is a diff between two complete statements.
"""
from __future__ import annotations

import os
import shutil
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

# The execution settings, with the defaults that applied before runs became files. A run file SHOULD state all
# of them; these exist so an omission is a documented fallback rather than an AttributeError mid-run.
RUN_DEFAULTS: dict = {
    "steps": 15000, "seed": 0, "founders": 3000, "terrain": "coastal", "climate": "temperate",
    "patch": 0, "tag": "", "max_minutes": 0, "log_every": 25, "gen_every": 200, "flush_every": 500,
    "genealogy": True, "genome": True,
    # FOUNDER LAYOUT (2026-08-22). "cycle" is the historical rule -- one founder per land cell, cycling --
    # and stays the default so every prior run is bit-exact. "cluster" seeds capacity-sized groups instead.
    # WHY IT EXISTS: `phase1_model` F.1 requires a CO-RESIDENT adult male for any birth ("loners can't
    # reproduce"). The cycle layout puts ~1 founder per cell, so in a low-capacity world (arid 2.0 people per
    # cell, mountain 1.9) the founders are too dispersed to ever pair, no birth occurs, and senescence alone
    # empties the map -- biome_arid died at step 29 and biome_mountain at step 52 with deaths_starv = 0 and
    # intake at 1.2x requirement. That is a SEEDING artefact, not a statement about those environments.
    "seed_layout": "cycle",
    "seed_cluster_size": 25,
    # ── THE SEED IS THREE THINGS, and until 2026-08-11 one integer did all three jobs ──────────────────────
    # `seed` reaches the run at three independent places:
    #   world_seed    world_lottery_climate(seed) — DRAWS THE WORLD. relief, roughness, water fraction,
    #                 latitude and aridity are `rng.uniform(lo, hi)` over the preset ranges, and `seedStr`
    #                 drives the terrain noise grid. Changing it changes the PLANET.
    #   climate_seed  build_climate_field(..., seed=seed) — the climate realisation on that planet.
    #   agent_seed    TerrainWorld(seed=seed) — the agents' stochastic path.
    # (Founder placement is NOT a fourth: run_campaign lays founders out deterministically over land cells.)
    #
    # WHY IT MATTERS. With one integer there is NO PURE REPLICATE: two "seeds" are two different planets, so
    # "seed variance" has always meant WORLD variance and path variance has never been measured. Addendum 39
    # reported flat-control spreads of 46.7× / 5.5× / 2.7×, and the world's own carrying capacity varies only
    # ~2.5× across those same seeds — so most of that spread is NOT the world being bigger or smaller, and the
    # harness could not say what it was instead.
    #
    # Each defaults to None ⇒ take `seed`. Every existing run file therefore behaves exactly as before.
    "world_seed": None, "climate_seed": None, "agent_seed": None,
}


@dataclass
class RunSpec:
    """One run, completely described."""
    path: Path
    run: dict = field(default_factory=dict)
    mechanisms: dict = field(default_factory=dict)
    parameters: dict = field(default_factory=dict)

    @property
    def name(self) -> str:
        """The run's identity IS its filename. A trajectory tagged from the config it used cannot be
        mislabelled, which a hand-passed `C_TAG` could and did."""
        return self.path.stem

    def config_values(self) -> dict:
        """`[mechanisms]` and `[parameters]` merged — the flat field->value map the config classes take."""
        return {**self.mechanisms, **self.parameters}

    def archive_to(self, outdir) -> Path:
        """Copy the resolved file next to the run's own output. A finished run must carry its configuration;
        pointing at a shared file in the repo is not the same thing, because the repo moves on."""
        outdir = Path(outdir)
        outdir.mkdir(parents=True, exist_ok=True)
        dest = outdir / f"{self.name}.resolved.toml"
        shutil.copyfile(self.path, dest)
        return dest


def load(path, seed: int | None = None) -> RunSpec:
    """Read a run file. Unknown top-level sections and missing required ones both RAISE.

    Strictness is the point. A mistyped section that was silently ignored would produce a run with defaults
    everywhere and no complaint, which is the failure this file exists to end.
    """
    path = Path(path)
    if not path.exists():
        raise SystemExit(
            f"run config not found: {path}\n"
            f"A run is a file. Pick one from config/runs/, or write a new one with "
            f"`py -3 tools/make_runconfig.py` — do not improvise settings on the command line.")
    with open(path, "rb") as fh:
        raw = tomllib.load(fh)

    unknown = set(raw) - {"run", "mechanisms", "parameters", "meta"}
    if unknown:
        raise SystemExit(f"{path.name}: unknown section(s) {sorted(unknown)}; "
                         f"expected [run], [mechanisms], [parameters] (and optional [meta])")
    for required in ("run", "mechanisms", "parameters"):
        if required not in raw:
            raise SystemExit(f"{path.name}: missing required section [{required}]. A run file states "
                             f"EVERYTHING — a partial file would silently take defaults for the rest.")

    run = {**RUN_DEFAULTS, **raw["run"]}
    unknown_run = set(raw["run"]) - set(RUN_DEFAULTS)
    if unknown_run:
        raise SystemExit(f"{path.name}: unknown [run] key(s) {sorted(unknown_run)}")

    if seed is not None:
        run["seed"] = int(seed)     # the ONE permitted override; a seed sweep is one experiment repeated
    # Resolve the three roles AFTER any override, so `--seed N` still moves all three together (a sweep over
    # `seed` remains a sweep over whole worlds, which is what every existing harness expects). A run file that
    # states one of these explicitly PINS that role and is the only way to hold the world still.
    for _role in ("world_seed", "climate_seed", "agent_seed"):
        if run.get(_role) is None:
            run[_role] = int(run["seed"])
        else:
            run[_role] = int(run[_role])
    if not run.get("tag"):
        run["tag"] = f"_{path.stem}"
    if seed is not None and int(seed) != int(raw["run"].get("seed", RUN_DEFAULTS["seed"])):
        # THE TAG MUST CARRY THE OVERRIDDEN SEED, or a seed sweep silently overwrites itself.
        # Found 2026-08-08 by losing one. Every output path the harness builds is `<name><tag>.<ext>`, and the
        # tag came only from the file — so `--seed 1..7` over one config wrote SEVEN runs to the SAME four
        # files and left only the last. 28 completed runs, 4 surviving, no error anywhere. The comment two
        # lines above calls this override "a seed sweep is one experiment repeated"; the code made a sweep
        # impossible to keep. Intent and behaviour contradicted each other inside the module whose stated
        # purpose is to stop silent failures.
        # Suffix ONLY when the seed actually differs from the file's, so every existing run keeps its tag and
        # its output filename exactly as before.
        run["tag"] = f"{run['tag']}_s{int(seed)}"
    # SAME RULE FOR THE THREE ROLES. A decomposition sweep varies `agent_seed` alone across one pinned world;
    # without this every arm of it writes to one path and the sweep destroys itself exactly as the first one
    # did. Only roles STATED in the file get a suffix — a file that leaves them implicit is unchanged.
    for _role, _abbr in (("world_seed", "w"), ("climate_seed", "c"), ("agent_seed", "a")):
        if raw["run"].get(_role) is not None:
            run["tag"] = f"{run['tag']}_{_abbr}{run[_role]}"

    # EVERY KEY IS CHECKED AGAINST THE CONFIG CLASSES. Found by this module's own CTB: `build()` filters to
    # fields the class knows, so a typo like `cv_saef = 0.05` was silently DROPPED and the run used the
    # default — a swept arm identical to its control, reading as a clean null. That is the same defect
    # `C_PARAM` was hardened against in 2026-08-04, reintroduced by moving the configuration into a file.
    # A file may not fail quietly just because it is a file.
    from sic_games.climate import ClimateConfig
    from sic_games.config import SubstrateConfig
    from sic_games.demography import DemographyConfig
    # SubstrateConfig joined 2026-08-17. `build()` below was ALREADY generic over the three config modules, so
    # only this validation set was hardcoded to two -- which is why a run file could never name a substrate
    # field. The same DemographyConfig+ClimateConfig pair was hardcoded in FOUR places (here, gen_runconfig's
    # resolved_canonical, make_runconfig's field check, and run_campaign's build calls); the grouping drives
    # fell through every one of them.
    known = (set(DemographyConfig.model_fields) | set(ClimateConfig.model_fields)
             | set(SubstrateConfig.model_fields))
    for section in ("mechanisms", "parameters"):
        bad = sorted(k for k in raw[section] if k not in known)
        if bad:
            raise SystemExit(f"{path.name}: unknown field(s) in [{section}]: {bad}. "
                             f"A field no config class knows would be silently ignored, which makes the run "
                             f"identical to its control and read as a clean null.")
    misplaced = [k for k in raw["mechanisms"] if not k.startswith("enable_")]
    misplaced += [k for k in raw["parameters"] if k.startswith("enable_")]
    if misplaced:
        raise SystemExit(f"{path.name}: {sorted(misplaced)} are in the wrong section — [mechanisms] holds the "
                         f"enable_* switches, [parameters] holds the values.")

    return RunSpec(path=path, run=run, mechanisms=dict(raw["mechanisms"]),
                   parameters=dict(raw["parameters"]))


def build(spec: RunSpec, owner: str = "DemographyConfig"):
    """A validated config object of `owner` from the spec, with the ON-but-dead check applied.

    Reuses `runconfig.dead_flags` rather than re-implementing it: a flag on with its magnitude at neutral reads
    as a live mechanism in every dump and does nothing in the world, and it must not become expressible again
    just because the configuration moved into a different file.
    """
    from sic_games import climate as _clim
    from sic_games import config as _cfgmod
    from sic_games import demography as _demog
    from sic_games import runconfig as _rc

    cls = getattr(_demog, owner, None) or getattr(_cfgmod, owner, None) or getattr(_clim, owner, None)
    if cls is None:
        raise SystemExit(f"runspec.build: unknown config class {owner!r}")

    values = {k: v for k, v in spec.config_values().items() if k in cls.model_fields}
    obj = cls(**values)
    dead = _rc.dead_flags({f: getattr(obj, f) for f in cls.model_fields}, set(cls.model_fields))
    if dead:
        raise SystemExit(f"{spec.path.name} has ON-but-dead mechanisms:\n  " + "\n  ".join(dead)
                         + "\n  Turn the flag off in the file to ablate, or give the magnitude a value.")
    return obj


def coverage(spec: RunSpec) -> list[str]:
    """Fields a config class knows about that the run file does NOT state. Should be empty: a resolved file
    lists everything, and a gap means the run would silently take a code default for that field."""
    from sic_games.climate import ClimateConfig
    from sic_games.demography import DemographyConfig

    stated = set(spec.config_values())
    missing = []
    for cls in (DemographyConfig, ClimateConfig):
        missing += [f for f in cls.model_fields if f not in stated]
    return sorted(missing)
