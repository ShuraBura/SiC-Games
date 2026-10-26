"""Generate the DERIVED registries an auditor needs: docs/REGISTRY.md and docs/RESULTS_INDEX.md.

WHY (2026-10-26, audit preparation). `tools/doc_audit.py` found 51 of 125 mechanism flags (29 of them ON in canon)
named in no specification document, and 171 of 253 canonical parameters with no PARAMETERS.md row. Hand-written rows
for ~220 items would be new copies that drift. But every flag and parameter already carries its canonical value and
its provenance comment in `config/*.toml`, which `tools/gen_runconfig.py` generates from the code and
`tests/test_runconfig_sync.py` keeps in sync. So this tool derives ONE table from those sources and the audit
tables, and `tests/test_registry_sync.py` fails if the committed tables are stale.

SOURCES (nothing here is typed by hand):
  canon state / value  config/runs/full_campaign.toml   (what the canonical run executes)
  class default        the config classes (sic_games.demography / sic_games.config)
  description, tag     the comment block of each entry in config/mechanisms.toml / config/parameters.toml
  charter type         TYPES in sic_games/outputs/phase1_biome_mortality/audit_flag_invariants.py (parsed, not imported)
  ladder tier          "Tier membership" in docs/BENCHMARK_LADDER.md
  results index        the `## ` headings of docs/RESULTS.md (append-only, so line numbers of old entries are stable)

Run:  py -3 tools/gen_registry.py            (writes both files)
      py -3 tools/gen_registry.py --check    (exit 1 if a committed file differs from a fresh generation)
"""
from __future__ import annotations

import argparse
import ast
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "sic_games" / "src"))
OUT_REG = ROOT / "docs" / "REGISTRY.md"
OUT_RES = ROOT / "docs" / "RESULTS_INDEX.md"
TAGS = ["VERIFIED", "ANCHORED", "LIT-CALIBRATED", "CALIBRATED", "CALIBRATION", "LOCKED", "MEASURED", "DESIGN",
        "PROVISIONAL", "PLACEHOLDER", "FREE", "UNANCHORED", "BRACKETED", "OPEN"]
STATUS_WORDS = ["retracted", "superseded", "corrected", "corrects", "falsified", "rejected", "not adopted", "adopted",
                "held", "closed", "validated", "confirmed", "resolved", "fixed", "passes", "fails", "diagnosed",
                "diagnosis only", "not comparable", "artifact", "inert"]


def status_of(h: str) -> str:
    """Every status word in a heading, case-insensitive, in order of appearance ("not adopted" is not also "adopted")."""
    low, found = h.lower(), []
    for w in sorted(STATUS_WORDS, key=len, reverse=True):
        for m in re.finditer(r"\b" + re.escape(w) + r"\b", low):
            if not any(a <= m.start() < b for a, b, _ in found):
                found.append((m.start(), m.end(), w.upper()))
    seen, out = set(), []
    for _, _, w in sorted(found):
        if w not in seen:
            seen.add(w)
            out.append(w)
    return ", ".join(out)


def _toml(p):
    with open(p, "rb") as fh:
        return tomllib.load(fh)


def comment_blocks(path: Path) -> dict:
    """name -> list of comment lines that follow the entry's `type = ` line (the provenance block)."""
    out, cur = {}, None
    for line in path.read_text(encoding="utf-8").split("\n"):
        m = re.match(r"^\[([A-Za-z0-9_]+)\]\s*$", line)
        if m:
            cur = m.group(1)
            out[cur] = []
            continue
        if cur and line.startswith("#"):
            out[cur].append(line.lstrip("#").strip())
    return out


def own_comments() -> dict:
    """field -> its OWN comment lines from the source: the contiguous `#` lines directly above the field (stopping at a
    blank line or code) plus its inline comment. Unlike config/*.toml, a field never inherits a neighbour's block
    (gen_runconfig attaches a preceding group comment to later fields as a "channel note, inherited", which gave 10
    flags another field's description — found 2026-10-26)."""
    out = {}
    for src in ("demography.py", "config.py", "climate.py"):
        path = ROOT / "sic_games" / "src" / "sic_games" / src
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        lines = text.split("\n")
        tree = ast.parse(text)
        for cls in [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]:
            for node in cls.body:
                if not (isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name)):
                    continue
                name, ln = node.target.id, node.lineno - 1
                block, j = [], ln - 1
                while j >= 0 and lines[j].strip().startswith("#"):
                    block.insert(0, lines[j].strip().lstrip("#").strip())
                    j -= 1
                inline = lines[ln].split("#", 1)[1].strip() if "#" in lines[ln] else ""
                out.setdefault(name, block + ([inline] if inline else []))
    return out


def describe(own_lines, toml_lines, n=170):
    """The field's own comment; else the group comment gen_runconfig attached, MARKED as inherited (it may describe a
    neighbour — 10 flags had another field's description that way)."""
    if own_lines:
        return first_sentence(own_lines, n)
    inh = [x.replace("(channel note, inherited)", "").strip() for x in toml_lines]
    return "*(no own comment; inherited group comment:)* " + first_sentence(inh, n - 40) if any(inh) else         "*(no comment in the source)*"


def first_sentence(lines, n=170):
    txt = " ".join(x for x in lines if x and not set(x) <= set("─-=—"))
    txt = re.sub(r"\s+", " ", txt).strip()
    txt = txt.replace("|", "/")
    return (txt[:n].rsplit(" ", 1)[0] + " …") if len(txt) > n else txt


def tag_of(lines):
    txt = " ".join(lines)
    for t in TAGS:
        if re.search(r"\[" + re.escape(t) + r"b", txt) or re.search(r"b" + re.escape(t) + r"b", txt):
            return t
    return "untagged"


def charter_types() -> dict:
    src = (ROOT / "sic_games" / "outputs" / "phase1_biome_mortality" / "audit_flag_invariants.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", "") == "TYPES" for t in node.targets):
            return ast.literal_eval(node.value)
    return {}


def ladder_tiers() -> dict:
    txt = (ROOT / "docs" / "BENCHMARK_LADDER.md").read_text(encoding="utf-8")
    sec = txt.split("## Tier membership", 1)[-1]
    out, tier = {}, None
    for line in sec.split("\n"):
        m = re.match(r"^- \*\*(\d+) ([^*]+)\*\*", line)
        if m:
            tier = f"{m.group(1)} {m.group(2).strip()}"
        elif line.startswith("## "):
            break
        if tier:
            for name in re.findall(r"`([a-z0-9_]+)`", line):
                out.setdefault("enable_" + name, tier)
    return out


def class_defaults() -> dict:
    from sic_games import demography, config as cfgmod
    out = {}
    for mod in (demography, cfgmod):
        for name in dir(mod):
            cls = getattr(mod, name)
            fields = getattr(cls, "model_fields", None)
            if isinstance(fields, dict) and isinstance(cls, type):
                for f, info in fields.items():
                    out.setdefault(f, info.default)
    return out


def fmt(v):
    if isinstance(v, float):
        return f"{v:.6g}"
    return str(v)


def build_registry() -> str:
    run = _toml(ROOT / "config" / "runs" / "full_campaign.toml")
    mech_c = comment_blocks(ROOT / "config" / "mechanisms.toml")
    par_c = comment_blocks(ROOT / "config" / "parameters.toml")
    par_meta = _toml(ROOT / "config" / "parameters.toml")
    types, tiers, defaults = charter_types(), ladder_tiers(), class_defaults()
    own = own_comments()
    L = ["# REGISTRY — every mechanism flag and every parameter of the canonical run (DERIVED)",
         "",
         "> **GENERATED by `tools/gen_registry.py` — do not edit by hand.** `tests/test_registry_sync.py` fails when this",
         "> file is stale. It is a derived VIEW, not a home: each column is read from its source (see the tool's docstring).",
         "> Canon = `config/runs/full_campaign.toml`, which is what a canonical run executes. Where this table and a prose",
         "> doc disagree, the run file is what ran; the prose doc is the defect to report.",
         "",
         "Charter types (MECHANISM_CHARTER.md): S state · F flow · T territory/spatial · P production · D demographic ·",
         "X exchange · C culture · A affiliation · N hazard · H homeostat · O observer. `—` = no type assigned yet.",
         ""]
    mech = run["mechanisms"]
    on = sum(bool(v) for v in mech.values())
    L += [f"## 1. Mechanism flags — {len(mech)} flags, {on} ON in canon, {len(mech) - on} OFF", "",
          "OFF in canon = held for evaluation, rejected but kept as an instrument, or an alternative form; the flag's own",
          "comment (first words below = the field's OWN source comment; full text at the field in `demography.py`)",
          "says which. `run_campaign.py` `_skip` lists the ones `C_ALLON` must not switch on.", "",
          "| flag | canon | class default | type | ladder tier | description (first words of the provenance comment) |",
          "|---|---|---|---|---|---|"]
    for f in sorted(mech):
        L.append(f"| `{f}` | {'**ON**' if mech[f] else 'off'} | {fmt(defaults.get(f, '?'))} | {types.get(f, '—')} | "
                 f"{tiers.get(f, '—')} | {describe(own.get(f), mech_c.get(f, []))} |")
    params = run["parameters"]
    counts = {}
    rows = []
    for p in sorted(params):
        lines = own.get(p) or []
        t = tag_of(lines) if lines else (tag_of(par_c.get(p, [])) + "*")
        if t == "untagged*":
            t = "untagged"
        counts[t] = counts.get(t, 0) + 1
        owner = par_meta.get(p, {}).get("owner", "?")
        d = defaults.get(p, "?")
        diff = "" if (d == "?" or fmt(d) == fmt(params[p])) else " ≠"
        rows.append(f"| `{p}` | {fmt(params[p])} | {fmt(d)}{diff} | {owner} | {t} | {describe(lines, par_c.get(p, []), 140)} |")
    L += ["", f"## 2. Parameters — {len(params)} in the canonical run", "",
          "Provenance tag = the first recognised tag in the field's own comment (" + ", ".join(TAGS) + "); a `*` = the tag "
          "comes from an inherited group comment, not the field's own. Counts: " +
          ", ".join(f"{k} {v}" for k, v in sorted(counts.items(), key=lambda kv: -kv[1])) + ".",
          "A `≠` marks a canon value that differs from the class default (set by the canon builder or the run file).",
          "**`untagged` and `PROVISIONAL` values are open questions, not validated constants.**", "",
          "| parameter | canon | class default | owner | tag | provenance comment (first words) |",
          "|---|---|---|---|---|---|"] + rows
    return "\n".join(L) + "\n"


def build_results_index() -> str:
    lines = (ROOT / "docs" / "RESULTS.md").read_text(encoding="utf-8").split("\n")
    L = ["# RESULTS_INDEX — every entry of docs/RESULTS.md (DERIVED)", "",
         "> **GENERATED by `tools/gen_registry.py` — do not edit by hand.** RESULTS.md is append-only, so the line number",
         "> of an entry never changes once written. `status` = every status word in the heading, case-insensitive (" +
         ", ".join(STATUS_WORDS) + "); read the entry before relying on it — later entries correct earlier ones,",
         "> and a correction is recorded in the LATER entry (search RESULTS.md for the R-/Addendum number).", "",
         "| line | entry | status | heading |", "|---|---|---|---|"]
    for i, line in enumerate(lines, 1):
        if not line.startswith("## "):
            continue
        h = line[3:].strip()
        m = re.match(r"(R-\d+(?:/R-\d+)?|Addendum \d+)", h)
        entry = m.group(1) if m else "—"
        st = status_of(h)
        L.append(f"| {i} | {entry} | {st} | {h.replace('|', '/')[:200]} |")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    want = {OUT_REG: build_registry(), OUT_RES: build_results_index()}
    if a.check:
        stale = [p for p, t in want.items() if not p.exists() or p.read_text(encoding="utf-8") != t]
        for p in stale:
            print(f"STALE: {p.relative_to(ROOT)} — run py -3 tools/gen_registry.py")
        sys.exit(1 if stale else 0)
    for p, t in want.items():
        p.write_text(t, encoding="utf-8", newline="\n")
        print(f"wrote {p.relative_to(ROOT)} ({t.count(chr(10))} lines)")
