# tests/test_display.py
# Run all tests in this file: pytest tests/test_display.py -v
import pytest
from unittest.mock import patch
from datetime import datetime

from nowcastingcli.models import Observation
from nowcastingcli.display import sparkline, trend_arrow, render_dashboard, format_observation, SPARKLINE_CHARS


VALID_TS = datetime(2024, 6, 1, 12, 0, 0)


def _obs(**overrides):
    """Factory helper — same pattern as in test_models.py."""
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


# ---------------------------------------------------------------------------
# Shared fixture
# ---------------------------------------------------------------------------
# autouse=True silences Rich console output for every test in this file.
# Yielding the mock lets individual tests declare `mock_console` as a parameter
# to inspect calls — without needing a second patch() block inside the test.
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def mock_console():
    with patch("nowcastingcli.display.console") as m:
        yield m


# ---------------------------------------------------------------------------
# sparkline
# ---------------------------------------------------------------------------
# sparkline() maps a list of floats to Unicode block characters (▁▂▃▄▅▆▇█).
# It is a pure function — no side effects — so tests just call it and assert.
# ---------------------------------------------------------------------------

def test_sparkline_empty_returns_empty_string():
    """Empty input → empty string (no characters to render).

    Run: pytest tests/test_display.py::test_sparkline_empty_returns_empty_string -v
    """
    assert sparkline([]) == ""


def test_sparkline_length_matches_input():
    """Output has exactly one character per input value.

    Run: pytest tests/test_display.py::test_sparkline_length_matches_input -v
    """
    values = [1.0, 2.0, 3.0, 4.0, 5.0]
    assert len(sparkline(values)) == len(values)


def test_sparkline_single_value_returns_one_char():
    """Single value → one character; no IndexError or empty result.

    Run: pytest tests/test_display.py::test_sparkline_single_value_returns_one_char -v
    """
    assert len(sparkline([42.0])) == 1


def test_sparkline_min_maps_to_lowest_char():
    """The minimum value always maps to the first (lowest) block character.

    Run: pytest tests/test_display.py::test_sparkline_min_maps_to_lowest_char -v
    """
    result = sparkline([0.0, 50.0, 100.0])
    assert result[0] == SPARKLINE_CHARS[0]  # "▁"


def test_sparkline_max_maps_to_highest_char():
    """The maximum value always maps to the last (tallest) block character.

    Run: pytest tests/test_display.py::test_sparkline_max_maps_to_highest_char -v
    """
    result = sparkline([0.0, 50.0, 100.0])
    assert result[-1] == SPARKLINE_CHARS[-1]  # "█"


def test_sparkline_all_same_values():
    """When all values are equal, span collapses to 1.0 (guard against /0).
    Every value maps to index 0 — all chars are the lowest block.

    Run: pytest tests/test_display.py::test_sparkline_all_same_values -v
    """
    result = sparkline([5.0, 5.0, 5.0])
    assert result == SPARKLINE_CHARS[0] * 3


def test_sparkline_ascending_chars_are_nondecreasing():
    """Strictly ascending input → characters must also be non-decreasing.

    Run: pytest tests/test_display.py::test_sparkline_ascending_chars_are_nondecreasing -v
    """
    result = sparkline([1.0, 2.0, 3.0, 4.0])
    for a, b in zip(result, result[1:]):
        assert a <= b


# ---------------------------------------------------------------------------
# trend_arrow
# ---------------------------------------------------------------------------

def test_trend_arrow_no_previous_returns_space():
    """No previous reading → neutral space character (nothing to compare against).

    Run: pytest tests/test_display.py::test_trend_arrow_no_previous_returns_space -v
    """
    assert trend_arrow(1013.0, None) == " "


def test_trend_arrow_rising_above_threshold():
    """delta > threshold → upward arrow.

    Run: pytest tests/test_display.py::test_trend_arrow_rising_above_threshold -v
    """
    assert trend_arrow(1015.0, 1013.0) == "↑"   # delta = +2.0


def test_trend_arrow_falling_below_threshold():
    """delta < -threshold → downward arrow.

    Run: pytest tests/test_display.py::test_trend_arrow_falling_below_threshold -v
    """
    assert trend_arrow(1011.0, 1013.0) == "↓"   # delta = -2.0


def test_trend_arrow_stable_within_threshold():
    """Small delta inside threshold → stable arrow.

    Run: pytest tests/test_display.py::test_trend_arrow_stable_within_threshold -v
    """
    assert trend_arrow(1013.05, 1013.0) == "→"  # delta = +0.05 < default 0.1


def test_trend_arrow_just_below_threshold_is_stable():
    """delta just below threshold → '→'; the check is strict (>) not (>=).

    Floating-point note: 1013.1 - 1013.0 evaluates to 0.10000000000002274 in
    IEEE 754, which is > 0.1, so those values would return '↑' — not the '→'
    a naive "boundary = threshold" test would expect.  Using 1013.09 keeps the
    delta clearly below 0.1 regardless of rounding.

    Run: pytest tests/test_display.py::test_trend_arrow_just_below_threshold_is_stable -v
    """
    assert trend_arrow(1013.09, 1013.0, threshold=0.1) == "→"  # delta ≈ 0.09 < 0.1


def test_trend_arrow_custom_threshold():
    """A higher threshold makes a normally-rising delta appear stable.

    Run: pytest tests/test_display.py::test_trend_arrow_custom_threshold -v
    """
    assert trend_arrow(1015.0, 1013.0, threshold=5.0) == "→"  # delta=2 < 5


# ---------------------------------------------------------------------------
# render_dashboard
# ---------------------------------------------------------------------------
# render_dashboard() produces Rich terminal output — the return value is None.
# There is nothing to assert on directly, so tests use two strategies:
#   1. Smoke tests — call the function and assert it does not raise.
#   2. Interaction tests — inspect the mocked console to verify it was used.
# The mock_console fixture (autouse) handles suppressing terminal output.
# ---------------------------------------------------------------------------

def test_render_dashboard_single_observation_does_not_raise():
    """Smoke test: one observation, no crash.

    Run: pytest tests/test_display.py::test_render_dashboard_single_observation_does_not_raise -v
    """
    render_dashboard([_obs()])


def test_render_dashboard_multiple_observations_does_not_raise():
    """Smoke test: three observations (enough to trigger trend arrows and sparkline delta).

    Run: pytest tests/test_display.py::test_render_dashboard_multiple_observations_does_not_raise -v
    """
    obs_list = [
        _obs(pressure_qnh=1013.0),
        _obs(pressure_qnh=1011.0),
        _obs(pressure_qnh=1009.0),
    ]
    render_dashboard(obs_list)


def test_render_dashboard_clears_screen(mock_console):
    """render_dashboard must call console.clear() once to refresh the display.

    mock_console is the fixture defined above — declaring it as a parameter
    gives this test access to the mock object to assert on its calls.

    Run: pytest tests/test_display.py::test_render_dashboard_clears_screen -v
    """
    render_dashboard([_obs()])
    mock_console.clear.assert_called_once()


def test_render_dashboard_prints_to_console(mock_console):
    """render_dashboard must call console.print() at least twice
    (once for the table, once for the panel).

    Run: pytest tests/test_display.py::test_render_dashboard_prints_to_console -v
    """
    render_dashboard([_obs()])
    assert mock_console.print.call_count >= 2


# ---------------------------------------------------------------------------
# format_observation
# ---------------------------------------------------------------------------

def test_format_observation_contains_timestamp():
    """Output must include the observation timestamp.

    Run: pytest tests/test_display.py::test_format_observation_contains_timestamp -v
    """
    obs = _obs()
    assert str(VALID_TS) in format_observation(obs)


def test_format_observation_contains_all_field_labels():
    """Output must include all field labels.

    Run: pytest tests/test_display.py::test_format_observation_contains_all_field_labels -v
    """
    text = format_observation(_obs())
    for label in ("pressure_raw", "pressure_qnh", "temperature", "humidity", "altitude"):
        assert label in text


def test_format_observation_contains_units():
    """Output must include unit strings from the units dict.

    Run: pytest tests/test_display.py::test_format_observation_contains_units -v
    """
    text = format_observation(_obs())
    assert "hPa" in text
    assert "°C" in text
    assert "%" in text


def test_format_observation_contains_values():
    """Output must include the numeric field values.

    Run: pytest tests/test_display.py::test_format_observation_contains_values -v
    """
    text = format_observation(_obs(pressure_raw=999.9, temperature=-5.5, humidity=33.0, altitude=250.0))
    assert "999.9" in text
    assert "-5.5" in text
    assert "33.0" in text
    assert "250.0" in text


