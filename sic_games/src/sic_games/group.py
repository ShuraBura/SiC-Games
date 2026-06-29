"""group.py — the Carbon COLLECTIVE-IDENTITY VECTOR (the "hive-mind").

`GroupVector` is a per-agent vector of group affiliations — the vehicle for the Carbon collective (vs the Silicon
individual). v1 (F.3c-1) uses only the **band_id** cell (band membership / affiliation). The other cells are
reserved SEAMS, present but inert, for later stages:
  - `assabiyah` — Ibn Khaldun group solidarity / cohesion strength (will modulate the band-cohesion drive +
    fission/survival decisions; biome- and history-dependent).
  - `religion` — organized-religion id (deferred; biome-linked).
Inheritance: a newborn copies its mother's vector; marriage updates `band_id` per the residence rule. Keeping this
a small explicit struct (not a bare scalar) is the seam the supervisor asked for — band affiliation is the first
facet of a richer collective identity.
"""
from __future__ import annotations

from dataclasses import dataclass

NO_BAND = -1
NO_RELIGION = -1


@dataclass
class GroupVector:
    band_id: int = NO_BAND          # ACTIVE (F.3c-1): band affiliation
    assabiyah: float = 0.0          # SEAM: group solidarity / cohesion strength (inert in v1)
    religion: int = NO_RELIGION     # SEAM: organized-religion id (inert in v1)

    def inherit(self) -> "GroupVector":
        """A child's vector = a copy of the parent's (matrilineal at birth; band may change at marriage)."""
        return GroupVector(band_id=self.band_id, assabiyah=self.assabiyah, religion=self.religion)
