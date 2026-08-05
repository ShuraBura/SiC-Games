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


def build(owner: str = "DemographyConfig", overrides: dict | None = None):
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
    return cls(**values)


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
