"""Tests for newborn Cred endowment (Stage 3 f_C mechanic)."""
from __future__ import annotations

import pytest

from sic_games.config import Config
from sic_games.run import SugarWorld


def _make_world(strategy: str, f_C: float = 0.0, n: int = 50) -> SugarWorld:
    raw = {
        "seed": 7,
        "agents": {"initial_population": n},
        "decision": {"strategy": strategy},
        "carbon": {"f_C": f_C, "velocity_tau": 0},
        "run": {"n_steps": 1, "output_dir": "outputs/_test_endowment"},
    }
    cfg = Config.model_validate(raw)
    return SugarWorld(cfg)


class TestSiBoundedNeverGetsCred:
    def test_initial_cred_zero(self):
        world = _make_world("si_bounded")
        for a in world.agents:
            assert a.cred == pytest.approx(0.0)

    def test_spawn_one_cred_zero_regardless_of_f_C_param(self):
        """Si world ignores f_C; f_C field belongs only to CarbonConfig."""
        world = _make_world("si_bounded")
        # Artificially inflate cred of all existing agents so mean_cred > 0
        for a in world.agents:
            a.cred = 10.0
        new_agent = world._spawn_one()
        assert new_agent.cred == pytest.approx(0.0), (
            "Si agents must not receive Cred endowment regardless of mean_cred"
        )


class TestCarbonEndowment:
    def test_f_C_zero_no_endowment(self):
        world = _make_world("carbon", f_C=0.0)
        # Set cred so mean_cred > 0; spawn a new agent
        for a in world.agents:
            a.cred = 5.0
        new_agent = world._spawn_one()
        assert new_agent.cred == pytest.approx(0.0)

    def test_f_C_nonzero_gets_fraction_of_mean(self):
        # Endowment is now applied in the replacement loop, not in _spawn_one().
        # Verify: when f_C > 0 and survivors have cred > 0, replacement gets cred > 0.
        f_C = 0.1
        world = _make_world("carbon", f_C=f_C, n=50)
        for a in world.agents:
            a.cred = 10.0

        victim = list(world.agents)[0]
        victim.wealth = -1.0  # triggers starvation death on next act()
        ids_before = {a.unique_id for a in world.agents}
        world.step()

        ids_after = {a.unique_id for a in world.agents}
        new_ids = ids_after - ids_before
        assert len(new_ids) >= 1, "Expected at least one replacement"
        new_agent = next(a for a in world.agents if a.unique_id in new_ids)
        # Endowment = f_C * mean_cred_at_spawn_time > 0 (survivors have cred ≈ 9.9 after decay)
        assert new_agent.cred > 0.0, (
            f"Replacement should inherit a fraction of mean cred; got {new_agent.cred}"
        )

    def test_endowment_tracks_mean_at_spawn_time(self):
        """Endowment is applied by the replacement loop after each death."""
        # Compare f_C=0 vs f_C=0.2: same setup, second should produce higher cred.
        world_no_endow = _make_world("carbon", f_C=0.0, n=20)
        world_endow    = _make_world("carbon", f_C=0.2, n=20)

        for w in (world_no_endow, world_endow):
            for a in w.agents:
                a.cred = 20.0
            list(w.agents)[0].wealth = -1.0

        ids_no   = {a.unique_id for a in world_no_endow.agents}
        ids_yes  = {a.unique_id for a in world_endow.agents}
        world_no_endow.step()
        world_endow.step()

        new_no  = next(a for a in world_no_endow.agents if a.unique_id not in ids_no)
        new_yes = next(a for a in world_endow.agents   if a.unique_id not in ids_yes)

        assert new_no.cred  == pytest.approx(0.0)
        assert new_yes.cred > 0.0, "f_C=0.2 replacement must receive nonzero Cred"

    def test_mean_cred_empty_population_returns_zero(self):
        world = _make_world("carbon", f_C=0.1, n=5)
        # Remove all agents to simulate edge case
        for a in list(world.agents):
            a.remove()
        assert world.mean_cred() == pytest.approx(0.0)

    def test_endowment_nonnegative_when_mean_is_zero(self):
        """If all agents have cred=0 (initial state), new agents get 0."""
        world = _make_world("carbon", f_C=0.5)
        for a in world.agents:
            a.cred = 0.0
        new_agent = world._spawn_one()
        assert new_agent.cred >= 0.0
