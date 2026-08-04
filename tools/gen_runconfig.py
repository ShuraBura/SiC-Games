"""Generate the authoritative run-configuration files from the config classes, comments and all.

WHY (R-106, 2026-08-04). This arc repeatedly failed on "what was actually on?". An audit found 27 of 79
mechanisms dark in the canonical preset and nobody knew; two conclusions were later retracted because a
control had been produced by a different build; and a mechanism audit scored 7 invalid verdicts because it
ablated flags that were already off. In every case the configuration was knowable only by reading Python
across four places at once: `DemographyConfig` field defaults, the preset functions in
`run_se0_controlled_climate.py`, the VILLAGE/ELITE overlay dicts, and the `C_*` environment knobs.

So the configuration becomes DATA: two TOML files that a run reads, that a human can diff, and that state for
every switch and every number what it does and where the value came from.

WHY GENERATED RATHER THAN HAND-WRITTEN. The provenance lives in the inline comments — lit anchors, R-numbers,
"[PROVISIONAL]", "[ANCHORED, Bandy 2004 p.330]". Retyping 281 fields would lose or corrupt that. This walks
the source, pulls each field's default AND its surrounding comment block, and emits them together, so the
files are correct the moment they exist. Re-run it whenever a field is added; `test_runconfig_sync.py` fails
if the files and the schema ever disagree.

Run:  py -3 tools/gen_runconfig.py
Out:  config/mechanisms.toml   (the enable_* switches)
      config/parameters.toml   (every calibrated value)
"""
import ast
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SRC = os.path.join(ROOT, "sic_games", "src", "sic_games")
OUTDIR = os.path.join(ROOT, "config")

# (module, class) pairs whose fields become run configuration.
TARGETS = [("demography.py", "DemographyConfig"), ("config.py", "SubstrateConfig"),
           ("config.py", "CarbonConfig"), ("config.py", "KcalEconomyConfig")]


def harvest(path, clsname):
    """Return [(field, default_src, type_src, doc)] preserving each field's comment block."""
    src = open(path, encoding="utf-8").read()
    lines = src.splitlines()
    tree = ast.parse(src)
    cls = next((n for n in ast.walk(tree)
                if isinstance(n, ast.ClassDef) and n.name == clsname), None)
    if cls is None:
        return []
    out = []
    for node in cls.body:
        if not isinstance(node, ast.AnnAssign) or not isinstance(node.target, ast.Name):
            continue
        name = node.target.id
        if name.startswith("_"):
            continue
        i0 = node.lineno - 1                       # 0-based line of the field
        # comment block immediately ABOVE, walking up through contiguous comment-only lines
        above = []
        j = i0 - 1
        while j >= 0 and lines[j].strip().startswith("#"):
            above.append(lines[j].strip().lstrip("#").strip())
            j -= 1
        above.reverse()
        # trailing inline comment on the field's own (possibly multi-line) definition
        seg = "\n".join(lines[i0:node.end_lineno])
        inline = [m.group(1).strip() for m in re.finditer(r"#\s*(.+)$", seg, re.M)]
        doc = " ".join(above + inline).strip()
        default = ast.get_source_segment(src, node.value) if node.value is not None else ""
        typ = ast.get_source_segment(src, node.annotation) or ""
        out.append((name, default, typ, doc))
    return out


def literal_default(default_src):
    """Extract the literal value from `Field(0.5, ge=0)` or a bare literal; None if not literal."""
    try:
        node = ast.parse(default_src, mode="eval").body
    except Exception:
        return None
    if isinstance(node, ast.Call) and getattr(node.func, "id", "") == "Field":
        if not node.args:
            return None
        node = node.args[0]
    try:
        return ast.literal_eval(node)
    except Exception:
        pass
    # Constant ARITHMETIC defaults, e.g. `Field(9.0 / 26.0)` (Boehm Table I is expressed as a ratio in the
    # source so the count it came from stays visible). literal_eval rejects BinOp, but leaving these out
    # would put two calibrated values back into the code — the exact problem these files exist to remove.
    # Evaluated in an empty namespace, so only literal arithmetic can succeed.
    try:
        if all(isinstance(n, (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Constant, ast.operator,
                              ast.unaryop)) for n in ast.walk(ast.Expression(body=node))):
            return eval(compile(ast.Expression(body=node), "<default>", "eval"), {"__builtins__": {}}, {})
    except Exception:
        pass
    return None


def toml_value(v):
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, str):
        return '"' + v.replace('"', '\\"') + '"'
    return repr(v)


def wrap(text, width=104, indent="# "):
    words, line, out = text.split(), "", []
    for w in words:
        if len(line) + len(w) + 1 > width:
            out.append(indent + line); line = w
        else:
            line = (line + " " + w).strip()
    if line:
        out.append(indent + line)
    return out


HEADER = """# {title}
#
# GENERATED by tools/gen_runconfig.py from {sources}. Re-run that after adding a field.
# `tests/test_runconfig_sync.py` FAILS if this file and the config schema ever disagree, so the two
# cannot silently drift apart.
#
# THIS FILE IS AUTHORITATIVE FOR A RUN. Harnesses load it via `sic_games.runconfig.load()`; nothing is
# read from a Python preset. Edit values here, diff this file to see what changed between runs, and read
# the resolved manifest a run writes to confirm what actually executed.
#
{note}
"""


def emit(path, title, sources, note, entries):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(HEADER.format(title=title, sources=sources, note=note))
        for (cls, name, val, typ, doc) in entries:
            fh.write(f"\n[{name}]\n")
            fh.write(f"value = {toml_value(val)}\n")
            # `type` must be escaped like any other string: annotations such as Literal["npp","intake"]
            # contain quotes and emitting them raw produced invalid TOML that failed to parse at all.
            fh.write(f"owner = {toml_value(cls)}\n")
            fh.write(f"type  = {toml_value(' '.join(str(typ).split()))}\n")
            if doc:
                fh.write("\n".join(wrap(doc)) + "\n")
            else:
                fh.write("# (no provenance comment in source — UNDOCUMENTED, worth filling in)\n")


def resolved_canonical():
    """The values a CANONICAL run actually uses — obtained by RUNNING one, not by re-deriving it.

    This matters more than it sounds, and the first version got it subtly wrong. The class default for most
    `enable_*` fields is False, but a real run layers a preset and several overlays on top, so a file
    reporting class defaults would say `enable_agglomeration = false` while every campaign runs it true —
    worse than no file. The first version therefore emitted `emergent_village_demog() + VILLAGE + ELITE`,
    battery1's overlay stack. That was still a RE-DERIVATION of the configuration rather than the
    configuration itself, and it drifted: the overlay carried `divorce_rate = 0.004` over R-78's calibrated
    0.005, so the authoritative file stated a number no campaign has ever run (R-106 Addendum 21).

    So the generator now asks the campaign. `run_campaign.py` dumps its FULL resolved `DemographyConfig` into
    `meta.demography_config` (R-101), so a two-step run with `C_ALLON=1` — every built mechanism on, which is
    the standing rule — yields exactly what a canonical run uses, by construction, with no second copy of the
    resolution logic to fall out of step. It costs a few seconds when regenerating.
    """
    import json
    import subprocess
    import tempfile

    camp = os.path.join(ROOT, "sic_games", "outputs", "substrate_run", "run_campaign.py")
    tag = "_genconfig_probe"
    out = os.path.join(os.path.dirname(camp), f"campaign_trajectory{tag}.json")
    env = dict(os.environ, C_ALLON="1", C_TAG=tag, C_STEPS="2", C_FOUNDERS="150", C_MAXMIN="5",
               C_LOGEVERY="600", C_GENEA="0")
    with tempfile.TemporaryFile() as devnull:
        p = subprocess.run([sys.executable, "-u", camp], cwd=ROOT, env=env,
                           stdout=devnull, stderr=subprocess.PIPE, text=True)
    if p.returncode != 0 or not os.path.exists(out):
        raise SystemExit(f"could not run the canonical campaign to resolve its configuration "
                         f"(rc={p.returncode}) — refusing to emit a re-derived stack, which is what put a "
                         f"number no run has ever used into the authoritative file.\n{p.stderr[-2000:]}")
    with open(out, encoding="utf-8") as fh:
        cfg = json.load(fh)["meta"]["demography_config"]
    os.remove(out)
    return cfg


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    canon = resolved_canonical()
    flags, params, skipped = [], [], []
    for mod, cls in TARGETS:
        for (name, default_src, typ, doc) in harvest(os.path.join(SRC, mod), cls):
            val = canon.get(name, literal_default(default_src))
            if val is None:
                skipped.append(f"{cls}.{name} = {default_src}")
                continue
            (flags if name.startswith("enable_") else params).append((cls, name, val, typ, doc))
    emit(os.path.join(OUTDIR, "mechanisms.toml"),
         "MECHANISMS — every switch in the model, and whether this run uses it",
         ", ".join(f"{c}" for _, c in TARGETS),
         "# A mechanism that is `false` here does NOT run. An audit that ablates a mechanism already `false`\n"
         "# tests nothing — check this file before reading any ablation result.\n", flags)
    emit(os.path.join(OUTDIR, "parameters.toml"),
         "PARAMETERS — every calibrated value, with how it was determined",
         ", ".join(f"{c}" for _, c in TARGETS),
         "# Provenance tags carried over from the source comments. [PROVISIONAL] means the value is a working\n"
         "# bracket and NOT lit-anchored; [ANCHORED ...] cites the source it was derived from. Treat a\n"
         "# PROVISIONAL number as an open question, not a validated constant.\n", params)
    print(f"wrote {len(flags)} mechanisms -> config/mechanisms.toml")
    print(f"wrote {len(params)} parameters -> config/parameters.toml")
    if skipped:
        print(f"\n{len(skipped)} field(s) had non-literal defaults and were NOT emitted "
              f"(they must be handled in code):")
        for s in skipped:
            print("   ", s)


if __name__ == "__main__":
    main()
