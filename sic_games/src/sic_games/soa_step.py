"""Stage 7.5 Workstream A step 6 — pre-batch birth-endowment (C-wire).

``SoAWorld`` is a ``SugarWorld`` subclass that overrides ``mean_cred()`` to
return a **per-step cached value** computed once before any births fire in that
step, implementing the sanctioned Tier-3 semantic declared in blueprint §3 and
§4.6:

    *All same-step newborns see one mean_cred (the pre-batch mean) rather than
    a progressively-updated mean that includes earlier same-step newborns.*

**Why this is a Tier-3 change (not Tier-1):**
The oracle's birth loop calls ``mean_cred()`` per newborn, so each newborn
sees the creds of earlier same-step newborns — sequential update semantics.
The pre-batch mean is computed once from the pre-birth agent set —
simultaneous semantics. For small step birth counts (mode="fixed", N~500) the
difference is negligible; at high N with dynamic births (n_carry ~10k+) the
oracle's O(N²) per step is the occupancy cliff that prevents OCC_3200+ from
running. Wiring ``mean_cred_vec`` here gives:

- **Correct semantics:** simultaneous-update birth endowment
- **O(N) per step:** one column-mean replaces O(N_births) × O(N) = O(N²)

Logged in ARCHITECTURE §12.1-H §H.4 as the WS-A step 6 C-wire completion.

Nothing here modifies ``run.py``; the oracle stays the reference until FINAL
(decision D4).
"""
from __future__ import annotations

import numpy as np

from sic_games.run import SugarWorld
from sic_games.soa_tier1 import mean_cred_vec


class SoAWorld(SugarWorld):
    """SugarWorld with pre-batch mean_cred() caching (WS-A step 6).

    Drop-in replacement for SugarWorld in benchmarks and the Tier-3 battery.
    All behaviour is identical to SugarWorld except that ``mean_cred()`` returns
    a single per-step cached value computed from the pre-birth agent snapshot
    using the vectorised ``mean_cred_vec``.

    Usage::

        m = SoAWorld(cfg)
        m._jt_manager = VecJointTaskManager(...)  # swap VecJTM as usual
        for _ in range(n_steps):
            m.step()

    Tier-3 validation: the B1 statistical battery (``test_tier3_gate_b1_battery``)
    uses SoAWorld as the VecJTM host; the combined (VecJTM + pre-batch endowment)
    model must pass Tests 1–4 against the unmodified oracle.
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
