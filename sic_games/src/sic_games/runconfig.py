"""Load a run's configuration from `config/*.toml` — the authoritative, human-readable source.

WHY THIS MODULE EXISTS (R-106, 2026-08-04). Configuration used to be knowable only by reading Python in four
places at once: `DemographyConfig` field defaults, the preset functions, the VILLAGE/ELITE overlay dicts, and
the `C_*` environment knobs. That cost this arc three separate failures — 27 of 79 mechanisms were dark and
nobody knew; two conclusions were retracted because a control came from a different build; and a mechanism
audit produced 7 invalid verdicts by ablating flags that were already off. None of those are analysis
mistakes. They are all "what was actually on?" mistakes.

So: `config/mechanisms.toml` and `config/parameters.toml` state every switch and every calibrated value
together with what it does and where the number came from. A run loads them, and writes back a resolved
manifest, so the configuration is inspectable BEFORE a run and verifiable AFTER it.

    from sic_games import runconfig
    cfgs = runconfig.load()                      # {"DemographyConfig": {...}, "SubstrateConfig": {...}, ...}
    demog = runconfig.build("DemographyConfig")  # a validated DemographyConfig
    print(runconfig.manifest())                  # the on/off summary to read before launching

Overrides are explicit and recorded, so an ablation still shows up in the manifest rather than hiding:

    demog = runconfig.build("DemographyConfig", overrides={"enable_soil_depletion": True})
"""
from __future__ import annotations

import os
import tomllib

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, "..", "..", ".."))
CONFIG_DIR = os.environ.get("SIC_CONFIG_DIR") or os.path.join(_ROOT, "config")
MECHANISMS = os.path.join(CONFIG_DIR, "mechanisms.toml")
PARAMETERS = os.path.join(CONFIG_DIR, "parameters.toml")

_CACHE: dict | None = None


def _read(path):
    if not os.path.exists(path):
        raise SystemExit(
            f"run configuration missing: {path}\n"
            f"These files are authoritative for a run and are generated from the config classes by\n"
            f"    py -3 tools/gen_runconfig.py\n"
            f"Refusing to fall back to in-code defaults, because a silent fallback is exactly the failure "
            f"this module exists to prevent.")
    with open(path, "rb") as fh:
        return tomllib.load(fh)


def load(refresh: bool = False) -> dict:
    """Return {owner_class: {field: value}} parsed from the TOML files."""
    global _CACHE
    if _CACHE is not None and not refresh:
        return _CACHE
    out: dict = {}
    for path in (MECHANISMS, PARAMETERS):
        for name, entry in _read(path).items():
            if not isinstance(entry, dict) or "value" not in entry:
                continue
            out.setdefault(entry.get("owner", "DemographyConfig"), {})[name] = entry["value"]
    _CACHE = out
    return out


def docs(field: str) -> str:
    """The provenance comment for a field, as written in the TOML (comments are not parsed by tomllib, so
    this reads the raw text)."""
    for path in (MECHANISMS, PARAMETERS):
        if not os.path.exists(path):
            continue
        lines = open(path, encoding="utf-8").read().splitlines()
        for i, ln in enumerate(lines):
            if ln.strip() == f"[{field}]":
                doc = [x.lstrip("# ").rstrip() for x in lines[i + 1:]
                       if x.startswith("#")] if i + 1 < len(lines) else []
                j, acc = i + 1, []
                while j < len(lines) and not lines[j].startswith("["):
                    if lines[j].startswith("#"):
                        acc.append(lines[j].lstrip("# ").rstrip())
                    j += 1
                return " ".join(acc)
    return ""


# ── ON-BUT-DEAD DETECTION ───────────────────────────────────────────────────────────────────────────────
# A flag that is TRUE while the magnitude it acts through sits at its neutral value is the single most
# expensive bug class in this project's history: it reads as a live mechanism in every config dump and as
# INERT in every ablation. It produced 3 of battery 7's 6 "inert" verdicts, and R-85's gate scan missed two
# more because the zero lived one level deeper, inside a field builder rather than at the reader line.
#
# `climate.py`'s `build_climate_field` already refuses this for climate channels. This is the same rule for
# demography, applied at the CANONICAL BUILD PATH only — not in a pydantic validator — because unit tests
# legitimately construct half-configured objects, and a rule that fires there would be turned off within a
# week. What a RUN loads is what has to be honest.
#
# NOTE ON ABLATION: you ablate a mechanism by turning its FLAG off, not by zeroing its magnitude. Zeroing the
# magnitude leaves the flag advertising a mechanism that is not running, which is the whole problem.
FLAG_MAGNITUDES = {
    "enable_terrain_pathogen": ("pathogen_gamma",),
    "enable_malnutrition_fission": ("malnutrition_fission_gain",),
    "enable_site_appraisal": ("site_gain",),
    "enable_terrain_move_cost": ("move_cost_kcal",),
    "enable_leader_coherence": ("leader_coherence_gain",),
    "enable_size_repulsion": ("repulsion_gain",),
    "enable_lineage_branching": ("lineage_branch_rate",),
    "enable_lineage_split": ("lineage_split_rate",),
    "enable_ascribed_mate_choice": ("ascribed_mate_strength",),
}
# A magnitude's neutral value is not always 0 — a multiplier's no-op is 1.0. Same trap `neutral` handles in
# climate.py; a bare falsy check would wave a 1.0 multiplier through as "configured".
NEUTRAL = {"cohesion_leader_weight": 1.0}


def dead_flags(values: dict, known: set | None = None) -> list[str]:
    """Flags that are ON while every magnitude they act through is neutral. Returns human-readable strings."""
    out = []
    for flag, mags in FLAG_MAGNITUDES.items():
        if known is not None and flag not in known:
            continue
        if values.get(flag) is not True:
            continue
        present = [m for m in mags if m in values]
        if present and all(values[m] == NEUTRAL.get(m, 0) for m in present):
            out.append(f"{flag} is ON but {', '.join(f'{m}={values[m]}' for m in present)} "
                       f"— the mechanism cannot act")
    return out


def build(owner: str = "DemographyConfig", overrides: dict | None = None, strict: bool = False):
    """Construct a validated config object of `owner` from the files, plus explicit overrides."""
    from sic_games import climate as _clim
    from sic_games import config as _cfgmod
    from sic_games import demography as _demog
    cls = getattr(_demog, owner, None) or getattr(_cfgmod, owner, None) or getattr(_clim, owner, None)
    if cls is None:
        raise SystemExit(f"runconfig.build: unknown config class {owner!r}")
    values = dict(load().get(owner, {}))
    unknown = [k for k in (overrides or {}) if k not in cls.model_fields]
    if unknown:
        raise SystemExit(f"runconfig.build({owner}): unknown override field(s) {unknown}")
    values.update(overrides or {})
    obj = cls(**values)
    if strict:
        dead = dead_flags({k: getattr(obj, k) for k in cls.model_fields}, set(cls.model_fields))
        if dead:
            raise SystemExit("run configuration has ON-but-dead mechanisms:\n  " + "\n  ".join(dead)
                             + "\nTurn the FLAG off to ablate, or give the magnitude a value. A flag that is "
                               "on with a neutral magnitude reads as live everywhere and does nothing.")
    return obj


def manifest(owner: str = "DemographyConfig", overrides: dict | None = None) -> str:
    """A human-readable on/off summary — print this before a run so the configuration is on the record."""
    values = dict(load().get(owner, {}))
    values.update(overrides or {})
    flags = sorted(k for k in values if k.startswith("enable_"))
    on = [f for f in flags if values[f] is True]
    off = [f for f in flags if values[f] is not True]
    lines = [f"run configuration [{owner}] from {CONFIG_DIR}",
             f"  mechanisms ON  : {len(on)}",
             f"  mechanisms OFF : {len(off)}"]
    if overrides:
        lines.append(f"  OVERRIDES      : " + ", ".join(f"{k}={v}" for k, v in sorted(overrides.items())))
    lines.append("  OFF: " + ", ".join(f.replace("enable_", "") for f in off))
    return "\n".join(lines)
