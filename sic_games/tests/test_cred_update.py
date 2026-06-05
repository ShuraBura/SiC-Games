"""Tests for Cred decay and delta-accumulation logic."""
import pytest


def _apply_cred_update(agent, delta: float, decay: float):
    """Mirrors the run-loop flush: apply pending delta then decay all."""
    agent.cred = (1 - decay) * agent.cred + agent._pending_cred_delta
    agent._pending_cred_delta = 0.0


class _Agent:
    def __init__(self, cred=0.0):
        self.cred = cred
        self._pending_cred_delta = 0.0


def test_cred_decay_only_no_delta():
    a = _Agent(cred=10.0)
    _apply_cred_update(a, delta=0.0, decay=0.01)
    assert a.cred == pytest.approx(9.9, rel=1e-6)


def test_cred_delta_accumulates():
    a = _Agent(cred=0.0)
    a._pending_cred_delta = 5.0
    _apply_cred_update(a, delta=5.0, decay=0.0)
    assert a.cred == pytest.approx(5.0, rel=1e-6)


def test_pending_delta_cleared_after_flush():
    a = _Agent(cred=0.0)
    a._pending_cred_delta = 3.0
    _apply_cred_update(a, delta=3.0, decay=0.01)
    assert a._pending_cred_delta == 0.0


def test_two_step_sequence():
    """Verify formula over two steps."""
    decay = 0.01
    a = _Agent(cred=0.0)

    # Step 1: participate in joint task, receive delta=5
    a._pending_cred_delta = 5.0
    _apply_cred_update(a, delta=5.0, decay=decay)
    expected_after_1 = (1 - decay) * 0.0 + 5.0  # = 5.0
    assert a.cred == pytest.approx(expected_after_1, rel=1e-6)

    # Step 2: no joint task (delta=0), cred decays
    _apply_cred_update(a, delta=0.0, decay=decay)
    expected_after_2 = (1 - decay) * expected_after_1 + 0.0
    assert a.cred == pytest.approx(expected_after_2, rel=1e-6)


def test_cred_never_negative_with_only_decay():
    a = _Agent(cred=0.01)
    for _ in range(1000):
        _apply_cred_update(a, delta=0.0, decay=0.01)
    assert a.cred >= 0.0


def test_delta_from_multiple_joint_tasks_same_step():
    """Pending delta accumulates across multiple joint-task events per step."""
    a = _Agent(cred=0.0)
    a._pending_cred_delta += 2.0  # first event
    a._pending_cred_delta += 3.0  # second event (same step)
    _apply_cred_update(a, delta=5.0, decay=0.0)
    assert a.cred == pytest.approx(5.0, rel=1e-6)
