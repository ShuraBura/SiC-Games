"""Tests for Matthew partition math in joint_task.py."""
import pytest

from sic_games.joint_task import matthew_shares


class _A:
    def __init__(self, cred):
        self.cred = cred


def test_equal_cred_gives_equal_shares():
    cluster = [_A(5.0), _A(5.0), _A(5.0)]
    shares = matthew_shares(cluster, total=9.0, alpha=1.5, epsilon=0.01)
    assert len(shares) == 3
    for s in shares:
        assert s == pytest.approx(3.0, rel=1e-4)


def test_shares_sum_to_total():
    cluster = [_A(1.0), _A(5.0), _A(10.0)]
    total = 12.0
    shares = matthew_shares(cluster, total=total, alpha=1.5, epsilon=0.01)
    assert sum(shares) == pytest.approx(total, rel=1e-6)


def test_higher_cred_gets_larger_share():
    cluster = [_A(0.0), _A(10.0)]
    shares = matthew_shares(cluster, total=1.0, alpha=1.5, epsilon=0.01)
    assert shares[1] > shares[0]


def test_zero_cred_still_gets_nonzero_share_due_to_epsilon():
    cluster = [_A(0.0), _A(0.0)]
    shares = matthew_shares(cluster, total=4.0, alpha=1.5, epsilon=0.01)
    assert shares[0] == pytest.approx(2.0, rel=1e-4)
    assert shares[1] == pytest.approx(2.0, rel=1e-4)


def test_exact_matthew_shares_two_agents():
    """Verify formula to 4 decimal places for a known case."""
    # C_0=1, C_1=9, alpha=1.5, eps=0.01, total=10
    alpha, eps, total = 1.5, 0.01, 10.0
    c0, c1 = 1.0, 9.0
    w0 = (c0 + eps) ** alpha
    w1 = (c1 + eps) ** alpha
    expected_0 = total * w0 / (w0 + w1)
    expected_1 = total * w1 / (w0 + w1)

    cluster = [_A(c0), _A(c1)]
    shares = matthew_shares(cluster, total=total, alpha=alpha, epsilon=eps)
    assert shares[0] == pytest.approx(expected_0, abs=1e-4)
    assert shares[1] == pytest.approx(expected_1, abs=1e-4)


def test_alpha_one_reduces_to_proportional():
    cluster = [_A(2.0), _A(8.0)]
    shares = matthew_shares(cluster, total=10.0, alpha=1.0, epsilon=0.0)
    assert shares[0] == pytest.approx(2.0, rel=1e-5)
    assert shares[1] == pytest.approx(8.0, rel=1e-5)
