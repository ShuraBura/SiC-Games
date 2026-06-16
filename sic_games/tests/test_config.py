"""Tests for config loading, LOCKED parameter guard, and config defaults."""
import io
import sys
import pathlib
import textwrap
import tempfile
import pytest

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "src"))

from sic_games.config import (
    Config, load_config,
    _LOCKED_PARAMS, _assert_locked_params_explicit,
    BirthCConfig, BirthSiConfig, ReproductionConfig, DormancyConfig, C2DefectionConfig,
)


# ── Default values match PARAMETERS.md locked values ──────────────────────

def test_birth_c_p_max_default():
    """BirthCConfig.p_max default = 0.12 (PARAMETERS.md §7, Stage 4.5)."""
    assert abs(BirthCConfig().p_max - 0.12) < 1e-12


def test_birth_si_p_fission_default():
    """BirthSiConfig.p_fission_max default = 0.065 (PARAMETERS.md §7, Stage 4.4)."""
    assert abs(BirthSiConfig().p_fission_max - 0.065) < 1e-12


def test_reproduction_inherit_sigma_default():
    """ReproductionConfig.inherit_sigma default = 0.10 (PARAMETERS.md §7, Stage 5.2)."""
    assert abs(ReproductionConfig().inherit_sigma - 0.10) < 1e-12


def test_dormancy_tau_trickle_default():
    """DormancyConfig.tau_trickle default = 0.3 (PARAMETERS.md §8, Stage 4.3)."""
    assert abs(DormancyConfig().tau_trickle - 0.3) < 1e-12


def test_c2_defection_enabled_default():
    """C2DefectionConfig.enabled default = True (PARAMETERS.md §4, Stage 5.2)."""
    assert C2DefectionConfig().enabled is True


# ── LOCKED guard: load_config refuses when LOCKED param absent from YAML ──

_MINIMAL_YAML_ALL_LOCKED = textwrap.dedent("""\
    seed: 42
    dormancy:
      enabled: false
      k_dormant: 1.0
      tau_trickle: 0.3
      k_reactivate: 3.0
      t_dormant_max: 50
    reproduction:
      mode: random
      parent_radius: 3
      inherit_sigma: 0.10
      coordinator: individual
      lambda_inheritance: 0.0
    birth_si:
      p_fission_max: 0.065
      fission_wealth_mult: 1.5
      rep_age_min: 15
    birth_c:
      p_max: 0.12
      tau_sub: 5.0
      r_stress: 0.75
      r_wealth: 0.5
      rep_age_min: 15
    c2_defection:
      enabled: true
""")


def _write_yaml(content: str) -> str:
    """Write content to a temp file and return path."""
    tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
    tmp.write(content)
    tmp.close()
    return tmp.name


def test_locked_guard_passes_when_all_explicit():
    """load_config succeeds when all five LOCKED params are explicit in YAML."""
    path = _write_yaml(_MINIMAL_YAML_ALL_LOCKED)
    cfg = load_config(path)
    assert abs(cfg.dormancy.tau_trickle - 0.3) < 1e-12
    assert abs(cfg.reproduction.inherit_sigma - 0.10) < 1e-12
    assert abs(cfg.birth_si.p_fission_max - 0.065) < 1e-12
    assert abs(cfg.birth_c.p_max - 0.12) < 1e-12
    assert cfg.c2_defection.enabled is True


def test_locked_guard_refuses_missing_tau_trickle():
    """load_config raises RuntimeError when dormancy.tau_trickle absent from YAML."""
    yaml = textwrap.dedent("""\
        seed: 42
        dormancy:
          enabled: false
          k_dormant: 1.0
        reproduction:
          inherit_sigma: 0.10
        birth_si:
          p_fission_max: 0.065
        birth_c:
          p_max: 0.12
        c2_defection:
          enabled: true
    """)
    path = _write_yaml(yaml)
    with pytest.raises(RuntimeError, match="dormancy.tau_trickle"):
        load_config(path)


def test_locked_guard_refuses_missing_c2_defection():
    """load_config raises RuntimeError when c2_defection block absent from YAML."""
    yaml = textwrap.dedent("""\
        seed: 42
        dormancy:
          tau_trickle: 0.3
        reproduction:
          inherit_sigma: 0.10
        birth_si:
          p_fission_max: 0.065
        birth_c:
          p_max: 0.12
    """)
    path = _write_yaml(yaml)
    with pytest.raises(RuntimeError, match="c2_defection.enabled"):
        load_config(path)


def test_locked_guard_error_message_lists_all_missing():
    """RuntimeError names every missing LOCKED param, not just the first."""
    yaml = "seed: 42\n"  # all sub-configs default — all five LOCKED params missing
    path = _write_yaml(yaml)
    with pytest.raises(RuntimeError) as exc_info:
        load_config(path)
    msg = str(exc_info.value)
    assert "dormancy.tau_trickle" in msg
    assert "reproduction.inherit_sigma" in msg
    assert "birth_si.p_fission_max" in msg
    assert "birth_c.p_max" in msg
    assert "c2_defection.enabled" in msg


def test_locked_guard_does_not_fire_on_direct_config_construction():
    """Config() construction (not load_config) bypasses the LOCKED guard — tests unaffected."""
    cfg = Config()  # must not raise
    assert cfg is not None
