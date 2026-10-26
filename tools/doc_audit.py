"""Documentation audit — machine checks that a human auditor would otherwise do by hand.

WHY (2026-10-26, audit preparation). The project keeps its facts in prose documents (docs/) and its executable
truth in code + config (sic_games/src, config/). Prose drifts. This tool checks the places where drift can be
detected mechanically, and prints a report. It changes nothing.

CHECKS
  1. PATHS     — every file path a live document names (in backticks or a markdown link) must exist.
  2. PARAMS    — every PARAMETERS.md table row whose name is a canonical parameter: its bold value must equal the
                 value the canonical run uses (config/runs/full_campaign.toml [parameters]).
  3. FLAGS     — every canonical mechanism flag (full_campaign.toml [mechanisms]) must be named in at least one
                 specification document (MECHANISMS.md, MODEL_SPEC.md, MECHANISM_CHARTER.md, PARAMETERS.md).
  4. FRESHNESS — the date of the last commit that touched each live document.

ORDER OF PRECEDENCE that the checks assume: code > config/runs/full_campaign.toml (what the canonical run
executes) > config/*.toml (generated from the code) > docs/. A doc value that disagrees with the run file is a
documentation defect, not a model defect — unless the doc records a value the supervisor decided and the run
file does not carry it, which is the case to look for by hand.

Run:  py -3 tools/doc_audit.py [--check paths|params|flags|fresh] [--all-paths]
Exit code 0 always (a report, not a gate).
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LIVE_DOCS = sorted([*ROOT.glob("docs/*.md"), ROOT / "README.md", ROOT / "CLAUDE.md", ROOT / "sic_games" / "CLAUDE.md"])
SPEC_DOCS = ["MECHANISMS.md", "MODEL_SPEC.md", "MECHANISM_CHARTER.md", "PARAMETERS.md"]
# places a bare relative path may be resolved against (docs are written from several vantage points)
BASES = [ROOT, ROOT / "docs", ROOT / "sic_games", ROOT / "sic_games" / "src", ROOT / "sic_games" / "src" / "sic_games",
         ROOT / "sic_games" / "outputs", ROOT / "sic_games" / "tests", ROOT / "literature"]
PATH_RE = re.compile(r"`([^`\s]+?\.(?:py|md|toml|json|png|csv|yaml|yml|html|pdf))(?::\d+)?`|\]\(([^)\s#]+?)(?:#[^)]*)?\)")


def run_file():
    with open(ROOT / "config" / "runs" / "full_campaign.toml", "rb") as fh:
        return tomllib.load(fh)


def check_paths(all_paths: bool):
    print("\n=== 1. PATHS — files named by live documents that do not exist")
    tracked = set(subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True).stdout.split("\n"))
    names = {Path(t).name for t in tracked if t}
    # every file on disk (tracked or not), for suffix matching of "…_Name.md" abbreviations
    disk = [q.name for q in ROOT.rglob("*") if q.is_file() and ".git" not in q.parts]
    n_bad = 0
    for doc in LIVE_DOCS:
        if not doc.exists():
            continue
        missing = []
        for i, line in enumerate(doc.read_text(encoding="utf-8", errors="replace").split("\n"), 1):
            for m in PATH_RE.finditer(line):
                p = (m.group(1) or m.group(2) or "").strip()
                if not p or p.startswith(("http", "mailto:")) or "*" in p or "<" in p or "{" in p:
                    continue
                p = p.replace("\\", "/").lstrip("./") if not p.startswith("../") else p
                if p.startswith(("…", "...")):          # "…_Storage_Morph_Scoping.md" = an abbreviated blueprint name
                    suf = p.lstrip("….")
                    if any(n.endswith(suf) for n in disk):
                        continue
                cand = [b / p for b in BASES] + [doc.parent / p]
                if any(c.exists() for c in cand):
                    continue
                if not all_paths and "/" not in p and Path(p).name in names:
                    continue                      # a bare filename that exists somewhere in the repo
                missing.append((i, p))
        if missing:
            n_bad += len(missing)
            print(f"  {doc.relative_to(ROOT)}: {len(missing)} missing")
            for i, p in missing[:25]:
                print(f"      line {i}: {p}")
            if len(missing) > 25:
                print(f"      ... and {len(missing) - 25} more")
    print(f"  TOTAL missing references: {n_bad}")


def _num(s):
    b = re.search(r"\*\*([^*]+)\*\*", s)
    if b and "=" in b.group(1):                  # "**9/26 = 0.346**": the value is after the "="
        s = "**" + b.group(1).split("=")[-1].strip() + "**"
    m = re.search(r"\*\*\s*([-+]?[\d][\d\s,_]*\.?\d*(?:[eE][-+]?\d+)?)", s)
    if not m:
        return None
    t = m.group(1).replace(" ", "").replace(",", "").replace("_", "").replace(" ", "")
    try:
        return float(t)
    except ValueError:
        return None


def check_params():
    print("\n=== 2. PARAMS — PARAMETERS.md bold values vs the canonical run file")
    params = run_file()["parameters"]
    text = (ROOT / "docs" / "PARAMETERS.md").read_text(encoding="utf-8").split("\n")
    seen, bad, ok = set(), [], 0
    for i, line in enumerate(text, 1):
        if not line.startswith("|") or line.startswith("|--") or line.startswith("| Name"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 2:
            continue
        ids = re.findall(r"[A-Za-z_][A-Za-z0-9_]*", cells[0].replace("`", ""))
        name = next((x for x in ids if x in params), None)
        if name is None:
            continue
        doc_v = _num(cells[1])
        canon = params[name]
        if doc_v is None or isinstance(canon, (bool, str)):
            continue
        seen.add(name)
        if abs(doc_v - float(canon)) > 2e-3 * max(1e-9, abs(float(canon))):   # docs round to ~3 digits
            bad.append((i, name, cells[1][:60], canon))
        else:
            ok += 1
    for i, name, dv, cv in bad:
        print(f"  line {i:4d}  {name:34s} doc {dv!r:62s} canon {cv}")
    print(f"  rows checked: {ok + len(bad)}; agree: {ok}; DISAGREE: {len(bad)}; canonical parameters never named "
          f"in a PARAMETERS.md table row: {len(set(params) - seen)} of {len(params)}")


def check_flags():
    print("\n=== 3. FLAGS — canonical mechanism flags no specification document names")
    mech = run_file()["mechanisms"]
    blob = "\n".join((ROOT / "docs" / d).read_text(encoding="utf-8") for d in SPEC_DOCS)
    none = [f for f in mech if f not in blob]
    on_none = [f for f in none if mech[f]]
    print(f"  flags: {len(mech)} ({sum(bool(v) for v in mech.values())} ON in canon); named in no spec doc: {len(none)}"
          f" ({len(on_none)} of them ON)")
    for f in none:
        print(f"      {'ON ' if mech[f] else 'off'}  {f}")


def check_fresh():
    print("\n=== 4. FRESHNESS — last commit touching each live document")
    for doc in LIVE_DOCS:
        if not doc.exists():
            continue
        out = subprocess.run(["git", "log", "-1", "--format=%cs %h", "--", str(doc.relative_to(ROOT))], cwd=ROOT,
                             capture_output=True, text=True).stdout.strip()
        print(f"  {out or 'untracked':20s} {doc.relative_to(ROOT)}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", choices=["paths", "params", "flags", "fresh"])
    ap.add_argument("--all-paths", action="store_true", help="also report bare filenames that exist elsewhere")
    a = ap.parse_args()
    if a.check in (None, "fresh"):
        check_fresh()
    if a.check in (None, "paths"):
        check_paths(a.all_paths)
    if a.check in (None, "params"):
        check_params()
    if a.check in (None, "flags"):
        check_flags()
