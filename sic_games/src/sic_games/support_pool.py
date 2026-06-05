"""Stage 4.1c — Proximity support pool.

Two-level support:
  Level 1: parental wealth transfer at birth (wired in reproduction.py).
  Level 2: proximity pool — active adults contribute surplus; non-active draw deficit.

Stage 4.1c uses a single global pool (r_pool stored for Stage 5+ spatial clustering).
Ordering: contribution → draw. Both happen between harvest and metabolism.

C agents: Cred-scaled contribution; Cred reward for above-base contribution.
Si agents (Stage 4.3): pool disabled (support_pool.enabled=False in Si configs).
  Si pool parameters are present in SupportPoolConfig as toggle-ready for Stage 5+.

Stage 4.3 additions:
  rho_carryover: fraction of unused pool carried to next step (default 0 = Stage 4.1c behavior).
  k_pool_cap: pool cap in units of N_active_C × mean_metabolism_C; 0 = no cap.
  _balance: persistent pool balance carries over across steps.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sic_games.agents.base import BaseAgent
    from sic_games.config import SupportPoolConfig


@dataclass
class PoolStepMetrics:
    pool_total_contributed: float = 0.0
    pool_total_drawn: float = 0.0
    pool_draw_requests: int = 0
    pool_draw_unmet: int = 0
    parental_transfer_total: float = 0.0
    parental_transfer_count: int = 0
    cred_pool_contribution: float = 0.0
    # Stage 4.3 carry-over and cap diagnostics
    pool_carryover_balance: float = 0.0   # pool balance carried in from previous step
    pool_cap_clipped: float = 0.0         # contribution wealth blocked by pool cap

    @property
    def pool_draw_unmet_frac(self) -> float:
        if self.pool_draw_requests == 0:
            return 0.0
        return self.pool_draw_unmet / self.pool_draw_requests

    @property
    def mean_parental_transfer(self) -> float:
        if self.parental_transfer_count == 0:
            return 0.0
        return self.parental_transfer_total / self.parental_transfer_count


class SupportPool:
    """Single global pool for Stage 4.1c+.

    r_pool preserved for Stage 5+ spatial upgrade.
    Stage 4.3: carry-over (rho_carryover) and pool cap (k_pool_cap) added.
    Si pool disabled in Stage 4.3; config parameters present for Stage 5+ toggle.
    """

    def __init__(self, cfg: "SupportPoolConfig") -> None:
        self.cfg = cfg
        self.metrics = PoolStepMetrics()
        # Stage 4.3: persistent pool balance for carry-over between steps
        self._balance: float = 0.0

    def reset_metrics(self) -> None:
        self.metrics = PoolStepMetrics()

    def step(self, agents: list["BaseAgent"]) -> PoolStepMetrics:
        """Run one full pool cycle: contribution then draw. Call between harvest and metabolism."""
        import math
        self.reset_metrics()
        if not self.cfg.enabled:
            self._balance = 0.0
            return self.metrics

        # --- Stage 4.3 carry-over: bring in ρ fraction of last step's leftover ---
        rho = self.cfg.rho_carryover
        pool_balance = rho * self._balance
        self.metrics.pool_carryover_balance = pool_balance

        # --- Pool cap computation (done once, before contributions) ---
        # Cap uses active C agents only (Si not pool participants)
        if self.cfg.k_pool_cap > 0:
            active_c = [
                a for a in agents
                if a.strategy == "carbon"
                and getattr(a, '_use_eta', False)
                and not a.is_juvenile()
                and not a.is_elder()
            ]
            n_active_c = len(active_c)
            mean_m_c = (
                sum(a.metabolism for a in active_c) / n_active_c
                if n_active_c > 0 else 1.0
            )
            pool_cap = self.cfg.k_pool_cap * n_active_c * mean_m_c
        else:
            pool_cap = float("inf")

        # Available room for new contributions (carry-over may already fill part of cap)
        available_room = max(0.0, pool_cap - pool_balance)
        pool_cap_clipped = 0.0

        # --- Contribution phase ---
        # Si agents participate when pool is enabled (Stage 4.1c behaviour).
        # Stage 4.3 Si configs disable the pool entirely (enabled=False → early return above).
        for agent in agents:
            if not getattr(agent, '_use_eta', False):
                continue  # no lh_config → skip
            if agent.is_juvenile() or agent.is_elder():
                continue  # non-active agents don't contribute

            # surplus = wealth above reserve floor
            reserve = self.cfg.k_reserve * agent.metabolism
            surplus = max(0.0, agent.wealth - reserve)
            if surplus <= 0.0:
                continue

            base_contribution = self.cfg.tau_pool * surplus

            if agent.strategy == "carbon":
                # cred_scale (C*) lives on agent._decision.cred_scale
                c_star = getattr(getattr(agent, '_decision', None), 'cred_scale', 10.0)
                cred_factor = math.tanh(agent.cred / c_star)
                desired_contribution = base_contribution * (1.0 + self.cfg.tau_cred * cred_factor)
                desired_contribution = min(desired_contribution, surplus)
            else:
                # Si: flat contribution, no Cred scaling
                desired_contribution = base_contribution

            # Apply pool cap: clip contribution to available room
            if desired_contribution > available_room:
                actual_contribution = available_room
                pool_cap_clipped += desired_contribution - available_room
                available_room = 0.0
            else:
                actual_contribution = desired_contribution
                available_room -= actual_contribution

            if actual_contribution <= 0.0:
                continue

            # Cred reward for above-base contribution (C only, on uncapped portion)
            if agent.strategy == "carbon":
                excess = actual_contribution - base_contribution
                if excess > 0.0:
                    cred_reward = self.cfg.tau_cred_reward * excess
                    agent.cred = getattr(agent, 'cred', 0.0) + cred_reward
                    self.metrics.cred_pool_contribution += cred_reward

            agent.wealth -= actual_contribution
            pool_balance += actual_contribution
            self.metrics.pool_total_contributed += actual_contribution

        self.metrics.pool_cap_clipped = pool_cap_clipped

        # --- Draw phase ---
        # Collect eligible drawers: non-active agents with metabolic deficit.
        # Si agents draw when pool is enabled (Stage 4.1c); disabled via enabled=False in Stage 4.3.
        drawers = []
        for agent in agents:
            if not getattr(agent, '_use_eta', False):
                continue
            if not (agent.is_juvenile() or agent.is_elder()):
                continue  # only non-active draw
            draw_target = self.cfg.k_draw * agent.metabolism
            need = draw_target - agent.wealth
            if need > 0.0:
                drawers.append((agent, need))

        self.metrics.pool_draw_requests = len(drawers)

        if drawers and pool_balance > 0.0:
            # Equal share among drawers; each gets min(need, share)
            equal_share = pool_balance / len(drawers)
            for agent, need in drawers:
                draw = min(need, equal_share)
                if draw <= 0.0:
                    self.metrics.pool_draw_unmet += 1
                    continue
                agent.wealth += draw
                pool_balance -= draw
                self.metrics.pool_total_drawn += draw
                if draw < need:
                    self.metrics.pool_draw_unmet += 1
        elif drawers:
            # Pool exhausted before any draws
            self.metrics.pool_draw_unmet = len(drawers)

        # Store leftover for next step's carry-over
        # Note: (1 - ρ) × leftover decays (modelled as overhead/spoilage) — intentional.
        self._balance = pool_balance  # full leftover stored; rho applied at START of next step

        return self.metrics

    def record_parental_transfer(self, amount: float) -> None:
        """Called by reproduction.py when a parental transfer occurs."""
        self.metrics.parental_transfer_total += amount
        self.metrics.parental_transfer_count += 1
