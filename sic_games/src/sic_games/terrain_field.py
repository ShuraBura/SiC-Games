"""terrain_field.py — TerrainField: drop-in SugarField adapter for WorldFields.

Phase 1 Blueprint A: A1.4 live-loop migration.

TerrainField wraps WorldFields and exposes the same interface as SugarField so that
the existing perception path (LocalVisionPerception.build) works without modification.

Interface alignment:
  .level(x, y)   → forage_kcal per-step income for perception/movement decision
  .harvest(x, y) → same (non-rivalrous forage; non-destructive; rivalry deferred CC-1)
  .width          → terrain grid width (always N=100)
  .height         → terrain grid height (always N=100)

Additional methods:
  .forage_level(x, y) → per-step forage kcal income (explicit)
  .game_level(x, y)   → per-step game kcal income [PROVISIONAL; depletion OFF, GD-1 seam]

Index convention:
  Terrain arrays are (N,N) numpy [row, col] = [y, x].
  SugarField uses [x, y] (first dim = x). This adapter translates:
  TerrainField.level(x,y) → forage_kcal[y, x] * hours_per_step.
"""
from __future__ import annotations

from sic_games.terrain import N, WorldFields


class TerrainField:
    """Adapts WorldFields to the SugarField interface used by perception + harvest.

    hours_per_step = foraging_hours_per_day * days_per_month (from KcalEconomyConfig).
    All level/harvest values are in kcal/step (converted from kcal/hr at construction).
    """

    def __init__(self, fields: WorldFields, hours_per_step: float) -> None:
        self._fields = fields
        self._hours = float(hours_per_step)
        self.width: int = N
        self.height: int = N

    # ── SugarField-compatible interface ────────────────────────────────────

    def level(self, x: int, y: int) -> float:
        """Forage kcal income per step at (x,y). Used by perception for movement selection.

        Returns forage_kcal[y, x] * hours_per_step (kcal/step).
        """
        f = self._fields.forage_kcal
        if f is None:
            return 0.0
        return float(f[y, x]) * self._hours

    def harvest(self, x: int, y: int) -> float:
        """Non-rivalrous forage harvest at (x,y): returns per-step kcal income (no depletion).

        Each agent gets the full cell rate independently.
        Rivalry and depletion are deferred to CC-1 (DEFERRED_MECHANICS.md).
        [PROVISIONAL — non-rivalrous; rivalry deferred to CC-1]
        """
        return self.level(x, y)

    # ── Additional terrain methods ──────────────────────────────────────────

    def forage_level(self, x: int, y: int) -> float:
        """Explicit forage accessor (same as level; provided for clarity in step loops)."""
        return self.level(x, y)

    def game_level(self, x: int, y: int) -> float:
        """Game-as-stock seam: per-step game kcal income at (x,y).

        [PROVISIONAL — biome-scaled from return-rate table, pending CC-1 ceiling]
        Depletion OFF (GD-1 seam). Rivalry OFF (CC-1 seam).
        Returns 0 for wetland/mountain/water (UNANCHORED per game return-rate table).
        Interface: GD-1 and CC-1 write to the underlying game_kcal field and nowhere else.
        """
        g = self._fields.game_kcal
        if g is None:
            return 0.0
        return float(g[y, x]) * self._hours
