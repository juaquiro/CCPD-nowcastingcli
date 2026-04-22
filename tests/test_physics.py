# tests/test_physics.py
# Run all tests in this file: pytest tests/test_physics.py -v
import pytest
from nowcastingcli.physics import normalize_pressure


# --- Basic correctness ---

def test_sea_level_returns_input():
    """At altitude=0, QNH should equal raw pressure.

    Run: pytest tests/test_physics.py::test_sea_level_returns_input -v
    """
    assert normalize_pressure(1013.25, altitude_m=0.0, temperature_c=15.0) == pytest.approx(1013.25, rel=1e-4)


def test_positive_altitude_increases_qnh():
    """Station above sea level → QNH > raw pressure.

    Run: pytest tests/test_physics.py::test_positive_altitude_increases_qnh -v
    """
    raw = 1000.0
    qnh = normalize_pressure(raw, altitude_m=500.0, temperature_c=15.0)
    assert qnh > raw


## --- Parameterized test for pressure increase with altitude ---
# This is more of a sanity check on the formula than a precise table test, so we allow a loose tolerance.
# Run: pytest tests/test_physics.py::test_qnh_increases_with_altitude -v
# Instead of writing 5 nearly identical test functions for different altitudes:
@pytest.mark.parametrize("altitude, expected_min", [
    (0,    1013.0),
    (500,  1070.0),
    (1000, 1130.0),
    (2000, 1260.0),
])
def test_qnh_increases_with_altitude(altitude, expected_min):
    qnh = normalize_pressure(1013.25, altitude_m=altitude, temperature_c=15.0)
    assert qnh >= expected_min - 10  # loose: direction test, not exact table

def test_known_value_burgos():
    """
    Burgos is ~856m ASL. At 15°C, 950 hPa raw → ~1052 hPa QNH approx.
    Tolerance loose — we're testing the formula, not ICAO tables.

    Run: pytest tests/test_physics.py::test_known_value_burgos -v
    """
    qnh = normalize_pressure(950.0, altitude_m=856.0, temperature_c=15.0)
    assert qnh == pytest.approx(1052.0, abs=2.0)


# --- Edge cases and guard rails ---

def test_negative_altitude_decreases_qnh():
    """Below sea level (Dead Sea ~-430m) → QNH < raw pressure.

    Run: pytest tests/test_physics.py::test_negative_altitude_decreases_qnh -v
    """
    raw = 1060.0
    qnh = normalize_pressure(raw, altitude_m=-430.0, temperature_c=25.0)
    assert qnh < raw


def test_extreme_cold_does_not_crash():
    """Formula must survive extreme temperatures, not divide by zero.

    Run: pytest tests/test_physics.py::test_extreme_cold_does_not_crash -v
    """
    result = normalize_pressure(900.0, altitude_m=3000.0, temperature_c=-40.0)
    assert result > 0


# --- Guards ---

def test_zero_pressure_raises():
    """pressure_hpa=0 is physically impossible — must raise ValueError.

    Run: pytest tests/test_physics.py::test_zero_pressure_raises -v
    """
    with pytest.raises(ValueError, match="pressure_hpa"):
        normalize_pressure(0.0, altitude_m=100.0, temperature_c=15.0)


def test_negative_pressure_raises():
    """Negative pressure is physically impossible — must raise ValueError.

    Run: pytest tests/test_physics.py::test_negative_pressure_raises -v
    """
    with pytest.raises(ValueError, match="pressure_hpa"):
        normalize_pressure(-10.0, altitude_m=100.0, temperature_c=15.0)


def test_altitude_above_limit_raises():
    """altitude_m > 5000 exceeds the ISA troposphere model — must raise ValueError.

    Run: pytest tests/test_physics.py::test_altitude_above_limit_raises -v
    """
    with pytest.raises(ValueError, match="altitude_m"):
        normalize_pressure(1013.25, altitude_m=5001.0, temperature_c=15.0)


def test_altitude_at_limit_is_accepted():
    """altitude_m == 5000 is exactly at the boundary — must not raise.

    Run: pytest tests/test_physics.py::test_altitude_at_limit_is_accepted -v
    """
    result = normalize_pressure(1013.25, altitude_m=5000.0, temperature_c=15.0)
    assert result > 0