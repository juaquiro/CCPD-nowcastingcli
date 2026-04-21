# tests/test_models.py
# Run all tests in this file: pytest tests/test_models.py -v
import pytest
from datetime import datetime
from nowcastingcli.models import Observation


VALID_TS = datetime(2024, 6, 1, 12, 0, 0)


def _obs(**overrides):
    """Factory helper that creates a valid Observation with sensible defaults.

    The leading underscore signals that this is a private test helper, not a
    test itself — pytest will not collect it as a test case.

    Syntax explained
    ----------------
    **overrides  (in the signature)
        The double-star prefix makes Python collect any keyword arguments the
        caller passes into a single dict called `overrides`.  For example:

            _obs(humidity=90.0, altitude=500.0)
            # → overrides == {"humidity": 90.0, "altitude": 500.0}

    defaults.update(overrides)
        dict.update() merges one dict into another, overwriting any keys that
        already exist.  So `overrides` silently replaces only the fields the
        caller specified; every other field keeps its default value.

            defaults == {"humidity": 50.0, "altitude": 100.0, ...}
            defaults.update({"humidity": 90.0, "altitude": 500.0})
            # → defaults == {"humidity": 90.0, "altitude": 500.0, ...}

    Observation(**defaults)  (in the return statement)
        The double-star prefix *unpacks* the dict as keyword arguments,
        which is the reverse of collecting them.  It is equivalent to
        writing every key=value pair by hand:

            Observation(timestamp=VALID_TS, pressure_raw=1013.25, ...)

    Combined pattern
    ----------------
    This two-step idiom (collect with **overrides, merge with .update(),
    unpack with **defaults) lets each test override only the one field it
    cares about, while keeping every other field at a known-good value:

        def test_humidity_above_100_raises():
            _obs(humidity=100.1)   # only humidity changes; rest stay default
    """
    defaults = dict(
        timestamp=VALID_TS,
        pressure_raw=1013.25,
        pressure_qnh=1015.0,
        temperature=20.0,
        humidity=50.0,
        altitude=100.0,
    )
    defaults.update(overrides)
    return Observation(**defaults)


# --- __post_init__ validation ---

def test_valid_observation_is_created():
    """Happy path: all fields in range, no exception raised.

    Run: pytest tests/test_models.py::test_valid_observation_is_created -v
    """
    obs = _obs()
    assert obs.humidity == 50.0
    assert obs.pressure_raw == 1013.25


def test_humidity_zero_is_valid():
    """Boundary: humidity=0 is valid.

    Run: pytest tests/test_models.py::test_humidity_zero_is_valid -v
    """
    obs = _obs(humidity=0.0)
    assert obs.humidity == 0.0


def test_humidity_100_is_valid():
    """Boundary: humidity=100 is valid.

    Run: pytest tests/test_models.py::test_humidity_100_is_valid -v
    """
    obs = _obs(humidity=100.0)
    assert obs.humidity == 100.0


def test_humidity_below_zero_raises():
    """humidity < 0 must raise ValueError.

    Run: pytest tests/test_models.py::test_humidity_below_zero_raises -v
    """
    with pytest.raises(ValueError, match="humidity"):
        _obs(humidity=-0.1)


def test_humidity_above_100_raises():
    """humidity > 100 must raise ValueError.

    Run: pytest tests/test_models.py::test_humidity_above_100_raises -v
    """
    with pytest.raises(ValueError, match="humidity"):
        _obs(humidity=100.1)


def test_zero_pressure_raises():
    """pressure_raw=0 must raise ValueError.

    Run: pytest tests/test_models.py::test_zero_pressure_raises -v
    """
    with pytest.raises(ValueError, match="pressure"):
        _obs(pressure_raw=0.0)


def test_negative_pressure_raises():
    """Negative pressure_raw must raise ValueError.

    Run: pytest tests/test_models.py::test_negative_pressure_raises -v
    """
    with pytest.raises(ValueError, match="pressure"):
        _obs(pressure_raw=-1.0)


# --- __str__ ---

def test_str_contains_timestamp():
    """__str__ must include the timestamp.

    Run: pytest tests/test_models.py::test_str_contains_timestamp -v
    """
    obs = _obs()
    assert str(VALID_TS) in str(obs)


def test_str_contains_all_field_labels():
    """__str__ must include all field labels.

    Run: pytest tests/test_models.py::test_str_contains_all_field_labels -v
    """
    obs = _obs()
    text = str(obs)
    for label in ("pressure_raw", "pressure_qnh", "temperature", "humidity", "altitude"):
        assert label in text


def test_str_contains_units():
    """__str__ must include the unit strings from the units dict.

    Run: pytest tests/test_models.py::test_str_contains_units -v
    """
    obs = _obs()
    text = str(obs)
    assert "hPa" in text
    assert "°C" in text
    assert "%" in text


def test_str_contains_values():
    """__str__ must include the numeric field values.

    Run: pytest tests/test_models.py::test_str_contains_values -v
    """
    obs = _obs(pressure_raw=999.9, temperature=-5.5, humidity=33.0, altitude=250.0)
    text = str(obs)
    assert "999.9" in text
    assert "-5.5" in text
    assert "33.0" in text
    assert "250.0" in text


def test_str_with_custom_units():
    """Custom units dict is reflected in __str__ output.

    Run: pytest tests/test_models.py::test_str_with_custom_units -v
    """
    obs = _obs()
    obs.units["temperature"] = "K"
    assert "K" in str(obs)
