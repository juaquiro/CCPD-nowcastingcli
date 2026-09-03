# tests/test_heuristics.py
# Run all tests in this file: pytest tests/test_heuristics.py -v
import pytest
from datetime import datetime, timedelta
from nowcastingcli.models import Observation
from nowcastingcli.heuristics import assess_conditions, WORSENING, STABLE, IMPROVING



# --- Fixture: factory function for Observations ---

def make_obs(pressure_qnh: float, humidity: float, temperature: float = 15.0, minutes_ago: int = 0) -> Observation:
    return Observation(
        timestamp=datetime.now() - timedelta(minutes=minutes_ago),
        pressure_raw=pressure_qnh - 2.0,   # raw is always less than QNH for our alt
        pressure_qnh=pressure_qnh,
        temperature=temperature,
        humidity=humidity,
        altitude=340.0,
    )


# --- Insufficient data ---

@pytest.mark.smoke
def test_single_observation_returns_stable():
    """Single reading, no trend possible yet.

    Smoke: confirms assess_conditions() runs without error and returns a
    sane default when there isn't enough history for a real verdict.

    Run: pytest tests/test_heuristics.py::test_single_observation_returns_stable -v
    """
    obs = [make_obs(1013.0, 60.0)]
    verdict, _ = assess_conditions(obs)
    assert verdict == STABLE


# --- Worsening scenarios ---

def test_rapid_pressure_drop_is_worsening():
    """Run: pytest tests/test_heuristics.py::test_rapid_pressure_drop_is_worsening -v"""
    obs = [
        make_obs(1013.0, 60.0, minutes_ago=30),
        make_obs(1011.5, 72.0, minutes_ago=15),
        make_obs(1009.8, 86.0, minutes_ago=0),
    ]
    verdict, reason = assess_conditions(obs)
    assert verdict == WORSENING
    assert reason  # non-empty string


def test_high_humidity_alone_triggers_worsening():
    """Run: pytest tests/test_heuristics.py::test_high_humidity_alone_triggers_worsening -v"""
    obs = [
        make_obs(1013.0, 60.0, minutes_ago=30),
        make_obs(1013.0, 88.0, minutes_ago=0),   # pressure stable, humidity spiked
    ]
    verdict, _ = assess_conditions(obs)
    assert verdict == WORSENING


# --- Improving scenarios ---

def test_pressure_rise_is_improving():
    """Run: pytest tests/test_heuristics.py::test_pressure_rise_is_improving -v"""
    obs = [
        make_obs(1008.0, 70.0, minutes_ago=30),
        make_obs(1010.5, 55.0, minutes_ago=0),
    ]
    verdict, _ = assess_conditions(obs)
    assert verdict == IMPROVING


# --- Stable scenario ---

def test_no_change_is_stable():
    """Run: pytest tests/test_heuristics.py::test_no_change_is_stable -v"""
    obs = [
        make_obs(1013.0, 60.0, minutes_ago=30),
        make_obs(1013.2, 61.0, minutes_ago=0),
    ]
    verdict, _ = assess_conditions(obs)
    assert verdict == STABLE

