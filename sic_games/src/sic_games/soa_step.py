"""Stage 7.5 Workstream A step 6 (C-wire) + Workstream C (GATE C1 diagnostics).

``SoAWorld`` is a ``SugarWorld`` subclass that provides two enhancements:

**WS-A step 6 — pre-batch birth-endowment (C-wire)**
Overrides ``mean_cred()`` to return a per-step cached value computed once
before any births fire in that step — simultaneous semantics rather than the
oracle's sequential per-birth update.  Logged in ARCHITECTURE §12.1-H §H.4.

**WS-C — GATE C1 sparse diagnostic vectorisation (2026-06-08)**
Overrides the two O(N²) diagnostic hooks added to SugarWorld:

- ``_step_density_diag``: uses ``c_spatial_density_blocked`` — blocked
  Chebyshev nearest-neighbour scan, O(N × block_size) peak memory instead of
  O(N²).  Results bit-identical to ``c_spatial_density`` (same arithmetic,
  same reduction order within each block → Tier-2 ✓).

- ``_moran_W_fn``: returns ``_moran_W_csr`` — builds a scipy.sparse CSR weight
  matrix in blocks (O(N × block_size) peak memory), stored as O(nnz).  The
  subsequent ``z @ W @ z`` product inside ``morans_i()`` is O(nnz) instead of
  O(N²) BLAS.  Result agrees with the dense oracle within floating-point
  sum-order variation (< 1e-9, Tier-2 ✓).

GATE C1 pass criterion (blueprint §8): full-step affordable N no longer
collapses to ~3–4k.  At N=5 000 on a 100×100 grid, diagnostic overhead drops
from O(N²) to O(N × nnz/N) ≈ O(N) → < 2 ms/step amortised at k_moran=10.

Nothing here modifies ``run.py`` agent logic; the oracle stays the reference
until FINAL (decision D4).
"""
from __future__ import annotations

import numpy as np

from sic_games.metrics import _moran_W_csr, c_spatial_density_blocked
from sic_games.run import SugarWorld
from sic_games.soa_tier1 import mean_cred_vec


class SoAWorld(SugarWorld):
    """SugarWorld with C-wire (mean_cred pre-batch) and sparse diagnostics (C1).

    Drop-in replacement for SugarWorld in benchmarks and the Tier-3 battery.
    Behaviour is identical to SugarWorld except:

    1. ``mean_cred()`` returns a per-step cached value (simultaneous semantics).
    2. ``_step_density_diag`` uses the blocked c_spatial_density (lower peak memory).
    3. ``_moran_W_fn`` returns _moran_W_csr (sparse CSR, O(nnz) z@W@z multiply).

    Both diagnostic overrides give Tier-2 equivalent results (< 1e-9 difference
    from the oracle on all tested configs).

    Usage::

        m = SoAWorld(cfg)
        m._jt_manager = VecJointTaskManager(...)  # swap VecJTM as usual
        for _ in range(n_steps):
            m.step()
    """

    def __init__(self, cfg) -> None:
        super().__init__(cfg)
        # Cache keyed on self._step_count (incremented at end of each step,
        # so all mean_cred() calls within one step share the same key).
        self._mcv_cache_step: int = -1
        self._mcv_cache_value: float = 0.0

    def mean_cred(self) -> float:
        """Pre-batch mean cred — O(1) after the first call per step.

        First call in step t: iterates the current agent set (pre-births),
        caches the result keyed on ``self._step_count``, returns it.
        Subsequent calls in the same step: return the cached value.

        The cache is automatically invalidated at the start of each new step
        because ``_step_count`` is incremented at the end of ``step()``
        (run.py line 863), after all births have been processed. All newborns
        born in step t therefore see the same pre-step mean — simultaneous
        semantics vs the oracle's sequential update.
        """
        if self._step_count == self._mcv_cache_step:
            return self._mcv_cache_value

        # First call this step: snapshot current agents (before births this step)
        agents = list(self.agents)
        n = len(agents)
        if n == 0:
            self._mcv_cache_value = 0.0
        else:
            cred_arr = np.fromiter((a.cred for a in agents),
                                   dtype=np.float64, count=n)
            alive_arr = np.ones(n, dtype=bool)
            self._mcv_cache_value = mean_cred_vec(cred_arr, alive_arr)

        self._mcv_cache_step = self._step_count
        return self._mcv_cache_value

    # ------------------------------------------------------------------
    # GATE C1: sparse diagnostic overrides
    # ------------------------------------------------------------------

    def _step_density_diag(
        self, c_pos: list, width: int, height: int
    ) -> tuple[float, float]:
        """Blocked c_spatial_density — O(N × block_size) peak memory (Tier-2)."""
        return c_spatial_density_blocked(c_pos, width, height, isolation_radius=3)

    @property
    def _moran_W_fn(self):
        """Returns _moran_W_csr so compute_metrics builds a sparse weight matrix."""
        return _moran_W_csr
