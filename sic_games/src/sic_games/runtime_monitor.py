"""Runtime monitor — distinguish LIVE heavy compute from process SUSPENSION.

Motivation (Stage 6.0a-perf, 2026-06-05): an unattended run's log froze for ~5.5 h.
It was ambiguous whether the process was (a) grinding on one pathological mega-step
(live heavy compute) or (b) suspended by a usage-outage pause. The two need different
responses — (a) is a real cost finding to record/kill, (b) is a harmless pause to wait
out — but a plain wall-clock log cannot tell them apart.

DISCRIMINATOR: wall-clock time advances while a process is suspended; the process's own
CPU time (`time.process_time()`, user+system) does NOT. So between two heartbeats:

    wall_delta ~= cpu_delta            -> LIVE compute (CPU busy the whole interval)
    wall_delta  >> cpu_delta           -> SUSPENDED for ~ (wall_delta - cpu_delta) seconds
                                          (e.g. wall jumped 5 h, cpu advanced 2 s -> paused)

This module provides:
  - classify_gap(...)   : pure, testable classifier of one (wall_dt, cpu_dt) interval.
  - RuntimeMonitor      : flushed heartbeat logger that tags each interval LIVE/SUSPEND
                          and accumulates total suspended time, so a frozen log is
                          self-diagnosing on resume.
  - timed_step(...)     : measure one unit of work in BOTH wall and CPU ms, so a step
                          paused mid-compute can be excluded from heavy-compute timing
                          stats (its wall time is inflated by the pause; its cpu time is not).

Clock functions are injectable (wall_fn / cpu_fn) for testing.
"""
from __future__ import annotations

import time
from contextlib import contextmanager
from typing import Callable

# Defaults: wall = real time (advances during suspend); cpu = process CPU (frozen during suspend).
_DEFAULT_WALL: Callable[[], float] = time.time
_DEFAULT_CPU: Callable[[], float] = time.process_time

# A heartbeat interval is flagged SUSPENDED when wall outran cpu by more than
# SUSPEND_GAP_S seconds AND by more than SUSPEND_RATIO times (so a normal busy
# interval, where wall ~= cpu, is never mislabelled).
SUSPEND_GAP_S = 5.0
SUSPEND_RATIO = 3.0


def classify_gap(wall_dt: float, cpu_dt: float,
                 gap_s: float = SUSPEND_GAP_S,
                 ratio: float = SUSPEND_RATIO) -> tuple[str, float]:
    """Classify one heartbeat interval.

    Returns (status, suspended_seconds):
      ("LIVE", 0.0)                 -> CPU was busy ~the whole interval (heavy compute).
      ("SUSPEND", susp_seconds)     -> process was paused for ~susp_seconds.
    """
    excess = wall_dt - cpu_dt
    if excess > gap_s and wall_dt > ratio * max(cpu_dt, 1e-9):
        return "SUSPEND", excess
    return "LIVE", 0.0


@contextmanager
def timed_step(wall_fn: Callable[[], float] = time.perf_counter,
               cpu_fn: Callable[[], float] = _DEFAULT_CPU):
    """Measure one unit of work in both wall and CPU ms.

    Usage:
        with timed_step() as t:
            do_work()
        t.wall_ms, t.cpu_ms   # available after the block
    If t.wall_ms >> t.cpu_ms, the step was paused mid-compute (exclude from compute stats).
    """
    class _T:
        wall_ms = 0.0
        cpu_ms = 0.0
        @property
        def suspended(self) -> bool:
            return (self.wall_ms - self.cpu_ms) > (SUSPEND_GAP_S * 1000.0) and \
                   self.wall_ms > SUSPEND_RATIO * max(self.cpu_ms, 1e-9)
    t = _T()
    w0, c0 = wall_fn(), cpu_fn()
    try:
        yield t
    finally:
        t.wall_ms = (wall_fn() - w0) * 1000.0
        t.cpu_ms = (cpu_fn() - c0) * 1000.0


class RuntimeMonitor:
    """Flushed heartbeat logger that self-diagnoses suspension vs live compute.

    Call beat(step, n, ms_step) every logging interval. Each line records wall/cpu
    deltas and a LIVE / SUSPEND~<s> tag; a frozen-then-resumed log therefore shows
    exactly where (and for how long) it was paused. close() writes a SUMMARY with
    total wall, total cpu, and total suspended time.
    """

    def __init__(self, logfile, *, suspend_gap_s: float = SUSPEND_GAP_S,
                 suspend_ratio: float = SUSPEND_RATIO,
                 wall_fn: Callable[[], float] = _DEFAULT_WALL,
                 cpu_fn: Callable[[], float] = _DEFAULT_CPU):
        self._f = open(logfile, "w")
        self.gap_s = suspend_gap_s
        self.ratio = suspend_ratio
        self._wall_fn = wall_fn
        self._cpu_fn = cpu_fn
        self._wall = wall_fn()
        self._cpu = cpu_fn()
        self._t0_wall = self._wall
        self._t0_cpu = self._cpu
        self.total_suspended_s = 0.0
        self.n_suspends = 0
        self._w(f"# runtime_monitor start wall={self._wall:.1f}")
        self._w("# wall_ts\tstep\tN\twall_dt_s\tcpu_dt_s\tms_step\tstatus")

    def _w(self, s: str) -> None:
        self._f.write(s + "\n"); self._f.flush()

    def beat(self, step: int, n: int, ms_step: float = float("nan")) -> str:
        w, c = self._wall_fn(), self._cpu_fn()
        wall_dt, cpu_dt = w - self._wall, c - self._cpu
        status, susp = classify_gap(wall_dt, cpu_dt, self.gap_s, self.ratio)
        if status == "SUSPEND":
            self.total_suspended_s += susp
            self.n_suspends += 1
            status = f"SUSPEND~{susp:.0f}s"
        self._w(f"{w:.1f}\t{step}\t{n}\t{wall_dt:.2f}\t{cpu_dt:.2f}\t{ms_step:.1f}\t{status}")
        self._wall, self._cpu = w, c
        return status

    def summary(self) -> dict:
        w, c = self._wall_fn(), self._cpu_fn()
        wall_total = w - self._t0_wall
        cpu_total = c - self._t0_cpu
        self._w(f"# SUMMARY wall_total={wall_total:.1f}s cpu_total={cpu_total:.1f}s "
                f"suspended~={self.total_suspended_s:.1f}s n_suspends={self.n_suspends} "
                f"(wall-cpu-gap={wall_total - cpu_total:.1f}s)")
        return {"wall_total_s": wall_total, "cpu_total_s": cpu_total,
                "suspended_s": self.total_suspended_s, "n_suspends": self.n_suspends}

    def close(self) -> dict:
        s = self.summary()
        self._f.close()
        return s
