# tests/test_physics.py
import pytest
from nowcastingcli.physics import normalize_pressure


# --- Basic correctness ---

def test_sea_level_returns_input():
    """At altitude=0, QNH should equal raw pressure."""
    assert normalize_pressure(1013.25, altitude_m=0.0, temperature_c=15.0) == pytest.approx(1013.25, rel=1e-4)


def test_positive_altitude_increases_qnh():
    """Station above sea level → QNH > raw pressure."""
    raw = 1000.0
    qnh = normalize_pressure(raw, altitude_m=500.0, temperature_c=15.0)
    assert qnh > raw


def test_known_value_burgos():
    """
    Burgos is ~856m ASL. At 15°C, 950 hPa raw → ~1052 hPa QNH approx.
    Tolerance loose — we're testing the formula, not ICAO tables.
    """
    qnh = normalize_pressure(950.0, altitude_m=856.0, temperature_c=15.0)
    assert pytest.approx(qnh, abs=2.0) == 1052.0


# --- Edge cases and guard rails ---

def test_negative_altitude_decreases_qnh():
    """Below sea level (Dead Sea ~-430m) → QNH < raw pressure."""
    raw = 1060.0
    qnh = normalize_pressure(raw, altitude_m=-430.0, temperature_c=25.0)
    assert qnh < raw


def test_extreme_cold_does_not_crash():
    """Formula must survive extreme temperatures, not divide by zero."""
    result = normalize_pressure(900.0, altitude_m=3000.0, temperature_c=-40.0)
    assert result > 0