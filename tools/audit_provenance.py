"""Provenance coverage over `config/parameters.toml` — how many of the run's numbers say where they came from.

WHY (2026-08-06, Addendum 29). The Bar-Yosef and Timmermann retractions were both the same shape: a number
carried a citation nobody had checked. `tools/verify_anchor.py` checks the ones that name a source. This
answers the prior question — how many name one at all — and turns the answer into a ratchet, so the share
that does can go up and not down.

The classes, in the order they are tested (the order matters: "UNANCHORED" contains "ANCHORED", and testing
the wrong one first reports a fake clean sweep — which it did on the first run of this audit):

    UNANCHORED    explicitly declared to have no literature source. An HONEST state, not a gap.
    ANCHORED      cites a source in the project's tag form
    PROVISIONAL   a declared working bracket, open by construction
    CITES-A-YEAR  names a paper-and-year but carries no tag, so verify_anchor.py cannot see it
    COMMENTED     explained, but no source named
    UNDOCUMENTED  nothing at all

Run:  py -3 tools/audit_provenance.py
"""
from __future__ import annotations

import collections
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PARAMS = ROOT / "config" / "parameters.toml"

# ORDER IS LOAD-BEARING — most specific first. UNANCHORED must precede ANCHORED.
CLASSES = [
    ("UNANCHORED", lambda c: "UNANCHORED" in c),
    ("ANCHORED", lambda c: "ANCHORED" in c),
    ("PROVISIONAL", lambda c: "PROVISIONAL" in c),
    ("CITES-A-YEAR", lambda c: bool(re.search(r"\b(19|20)\d\d\b", c))),
    ("COMMENTED", lambda c: bool(c.strip())),
    ("UNDOCUMENTED", lambda c: True),
]


def classify(comment: str) -> str:
    if "UNDOCUMENTED" in comment:
        return "UNDOCUMENTED"
    return next(name for name, test in CLASSES if test(comment))


def audit(path: Path = PARAMS) -> dict[str, list[tuple[str, str]]]:
    """Return {class: [(owner, param), ...]} over every parameter block in the file."""
    out: dict[str, list[tuple[str, str]]] = collections.defaultdict(list)
    for block in re.split(r"\n(?=\[)", path.read_text(encoding="utf-8")):
        m = re.match(r"\[([a-z0-9_]+)\]", block)
        if not m:
            continue
        owner = (re.search(r'owner = "(\w+)"', block) or [None, "?"])[1]
        comment = "\n".join(l for l in block.splitlines() if l.startswith("#"))
        out[classify(comment)].append((owner, m.group(1)))
    return dict(out)


def main() -> int:
    try:
        sys.stdout.reconfigure(errors="replace")
    except AttributeError:
        pass
    res = audit()
    total = sum(len(v) for v in res.values())
    print(f"{total} parameters in {PARAMS.relative_to(ROOT)}\n")
    for name, _ in CLASSES:
        n = len(res.get(name, []))
        if n:
            print(f"  {n:>4}  {100 * n / total:>5.1f}%  {name}")

    named = sum(len(res.get(k, [])) for k in ("ANCHORED", "PROVISIONAL", "CITES-A-YEAR", "UNANCHORED"))
    print(f"\n{named}/{total} ({100 * named / total:.0f}%) declare a source or declare that they have none")

    for name in ("UNDOCUMENTED", "UNANCHORED"):
        rows = res.get(name, [])
        if rows:
            print(f"\n{name} ({len(rows)}):")
            for owner, param in rows:
                print(f"   {owner:<20} {param}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
