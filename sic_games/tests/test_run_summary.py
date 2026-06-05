"""Tests for R6 terminal-state run summary (Stage 5.2 Task 0).

Blueprint requirement:
  "add one test confirming extinction_step is null for a surviving run and
   equals the first zero-population step for a forced-extinction fixture."
"""
from __future__ import annotations

import pandas as pd

from sic_games.metrics import compute_run_summary


def _make_df(populations: list[int], pop_col: str = "population") -> pd.DataFrame:
    """Build a minimal metrics DataFrame with the given population trajectory."""
    return pd.DataFrame({
        "step": list(range(len(populations))),
        pop_col: populations,
    })


# ─── Required blueprint tests ─────────────────────────────────────────────────

def test_extinction_step_is_none_for_surviving_run():
    """extinction_step is None when population never reaches 0."""
    df = _make_df([250, 240, 230, 220, 215])
    summary = compute_run_summary(df, strategy="carbon")
    assert summary["extinction_step"] is None, (
        f"Expected None for surviving run, got {summary['extinction_step']}"
    )


def test_extinction_step_equals_first_zero_population_step():
    """extinction_step equals the step index where population first hits 0."""
    # Population survives until step 3, then collapses at step 3
    df = _make_df([250, 180, 90, 0, 0])
    summary = compute_run_summary(df, strategy="carbon")
    assert summary["extinction_step"] == 3, (
        f"Expected extinction_step=3, got {summary['extinction_step']}"
    )


def test_extinction_step_first_occurrence_not_later():
    """When population recovers after briefly hitting 0, extinction_step is first zero."""
    df = _make_df([200, 50, 0, 10, 0])
    summary = compute_run_summary(df, strategy="carbon")
    assert summary["extinction_step"] == 2  # first zero at step 2, not step 4


# ─── N_min and argmin_t ───────────────────────────────────────────────────────

def test_n_min_is_minimum_over_run():
    df = _make_df([300, 150, 50, 200, 250])
    summary = compute_run_summary(df, strategy="carbon")
    assert summary["N_min"] == 50


def test_argmin_t_is_step_of_minimum():
    df = _make_df([300, 150, 50, 200, 250])
    summary = compute_run_summary(df, strategy="carbon")
    assert summary["argmin_t"] == 2


def test_n_active_t_end_is_last_population():
    df = _make_df([300, 200, 150, 175, 190])
    summary = compute_run_summary(df, strategy="carbon")
    assert summary["N_active_t_end"] == 190


# ─── Si strategy uses n_active_si column ─────────────────────────────────────

def test_si_strategy_uses_n_active_si_column():
    """For si_bounded strategy, compute_run_summary reads n_active_si, not population."""
    df = pd.DataFrame({
        "step": [0, 1, 2, 3],
        "population": [400, 400, 400, 400],   # dormant+active combined
        "n_active_si": [200, 150, 0, 0],       # active only; collapses at step 2
    })
    summary = compute_run_summary(df, strategy="si_bounded")
    assert summary["extinction_step"] == 2
    assert summary["N_min"] == 0
    assert summary["N_active_t_end"] == 0


def test_carbon_strategy_uses_population_column():
    """For carbon strategy, compute_run_summary reads population column."""
    df = pd.DataFrame({
        "step": [0, 1, 2],
        "population": [250, 200, 180],
        "n_active_si": [0, 0, 0],   # irrelevant for carbon
    })
    summary = compute_run_summary(df, strategy="carbon")
    assert summary["N_active_t_end"] == 180
    assert summary["extinction_step"] is None


def test_n_steps_equals_step_count():
    df = _make_df([100, 90, 80, 70, 60])
    summary = compute_run_summary(df, strategy="carbon")
    assert summary["n_steps"] == 5
