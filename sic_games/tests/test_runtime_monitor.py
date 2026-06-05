"""Tests for runtime_monitor — suspension vs live-compute discrimination."""
from __future__ import annotations

from sic_games.runtime_monitor import classify_gap, timed_step, RuntimeMonitor


def test_classify_live_when_wall_matches_cpu():
    # Busy interval: wall ~= cpu -> LIVE
    status, susp = classify_gap(wall_dt=2.0, cpu_dt=1.95)
    assert status == "LIVE" and susp == 0.0


def test_classify_suspend_when_wall_far_exceeds_cpu():
    # Paused 5 h while cpu advanced 2 s -> SUSPEND ~ (18000 - 2)
    status, susp = classify_gap(wall_dt=18000.0, cpu_dt=2.0)
    assert status == "SUSPEND"
    assert abs(susp - 17998.0) < 1.0


def test_classify_small_gap_not_flagged():
    # Small wall>cpu gap below threshold (e.g. brief I/O wait) stays LIVE
    status, _ = classify_gap(wall_dt=3.0, cpu_dt=0.5)  # excess 2.5 < gap_s 5.0
    assert status == "LIVE"


def test_classify_busy_long_interval_not_suspend():
    # Long but genuinely busy interval (wall~cpu) is LIVE even if large
    status, _ = classify_gap(wall_dt=600.0, cpu_dt=595.0)
    assert status == "LIVE"


def test_monitor_flags_suspension_with_injected_clock(tmp_path):
    # Injected clocks: wall jumps 10000s between beats while cpu advances 1s -> SUSPEND
    wall = [1000.0]
    cpu = [10.0]
    mon = RuntimeMonitor(tmp_path / "rt.log",
                         wall_fn=lambda: wall[0], cpu_fn=lambda: cpu[0])
    # beat 1: live (wall+2, cpu+2)
    wall[0] += 2.0; cpu[0] += 2.0
    assert mon.beat(1, 100) == "LIVE"
    # beat 2: suspension (wall+10000, cpu+1)
    wall[0] += 10000.0; cpu[0] += 1.0
    st = mon.beat(2, 100)
    assert st.startswith("SUSPEND")
    s = mon.close()
    assert s["n_suspends"] == 1
    assert abs(s["suspended_s"] - 9999.0) < 2.0


def test_timed_step_reports_wall_and_cpu(tmp_path):
    # timed_step with injected clocks: a "suspended" step has wall>>cpu
    wall = [0.0]; cpu = [0.0]
    wf = lambda: wall[0]; cf = lambda: cpu[0]
    with timed_step(wall_fn=wf, cpu_fn=cf) as t:
        wall[0] += 100.0   # 100 s wall
        cpu[0] += 0.01     # 10 ms cpu  -> paused mid-step
    assert t.wall_ms > 90000
    assert t.cpu_ms < 100
    assert t.suspended is True
