"""run.py — backward-compatibility re-export (D4 archival, 2026-06-08).

SugarWorld has been archived to sic_games.oracle (D4 decision,
ARCHITECTURE.md §H.6; GATE FINAL PASS 2026-06-08).  This module exists
solely to preserve the historic import path:

    from sic_games.run import SugarWorld   # still works

New code should prefer the canonical archive location:

    from sic_games.oracle import SugarWorld

SoAWorld (sic_games.soa_step) is the active production model.
"""
from __future__ import annotations

from sic_games.oracle import (  # noqa: F401  (re-export for backward compat)
    SugarWorld,
    _EMPTY_BLOCKED,
    _NEWBORN_AGE_CUTOFF,
)

__all__ = ["SugarWorld", "_NEWBORN_AGE_CUTOFF", "_EMPTY_BLOCKED"]
