# tests/test_main.py
# Run all tests in this file: pytest tests/test_main.py -v
import pytest
from unittest.mock import patch
from nowcastingcli.main import get_float, run


# ---------------------------------------------------------------------------
# autouse fixture — applied automatically to every test in this file.
# It replaces the Rich `console` object inside main.py with a silent mock so
# console.print() calls don't produce output during test runs.
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def silence_console():
    """Suppress all Rich console.print() calls made by main.py.

    autouse=True means pytest activates this fixture for every test in this
    file without each test having to declare it explicitly.  The `with` block
    keeps the patch active for the duration of the test, then restores the
    real console automatically.
    """
    with patch("nowcastingcli.main.console"):
        yield


# ---------------------------------------------------------------------------
# get_float
# ---------------------------------------------------------------------------
# get_float() wraps Prompt.ask() in a retry loop: it keeps asking until the
# user enters a number that falls inside [min_val, max_val].
# We use patch() to replace Prompt.ask with a mock whose side_effect list
# acts as a queue of pre-scripted "user answers".
# ---------------------------------------------------------------------------

def test_get_float_returns_valid_value():
    """Valid input on the first try — returns immediately.

    Run: pytest tests/test_main.py::test_get_float_returns_valid_value -v
    """
    with patch("nowcastingcli.main.Prompt.ask", return_value="20.0"):
        assert get_float("Temperature", -60, 60) == 20.0


def test_get_float_accepts_min_boundary():
    """Exactly at min_val — boundary is inclusive.

    Run: pytest tests/test_main.py::test_get_float_accepts_min_boundary -v
    """
    with patch("nowcastingcli.main.Prompt.ask", return_value="-60.0"):
        assert get_float("Temperature", -60, 60) == -60.0


def test_get_float_accepts_max_boundary():
    """Exactly at max_val — boundary is inclusive.

    Run: pytest tests/test_main.py::test_get_float_accepts_max_boundary -v
    """
    with patch("nowcastingcli.main.Prompt.ask", return_value="60.0"):
        assert get_float("Temperature", -60, 60) == 60.0


def test_get_float_retries_when_out_of_range():
    """Out-of-range answer triggers a retry; the second valid answer is returned.

    side_effect with a list makes the mock return each item in sequence:
    first call → "200.0" (rejected), second call → "20.0" (accepted).

    Run: pytest tests/test_main.py::test_get_float_retries_when_out_of_range -v
    """
    with patch("nowcastingcli.main.Prompt.ask", side_effect=["200.0", "20.0"]):
        assert get_float("Temperature", -60, 60) == 20.0


def test_get_float_retries_on_non_numeric():
    """Non-numeric input raises ValueError internally; the loop retries.

    Run: pytest tests/test_main.py::test_get_float_retries_on_non_numeric -v
    """
    with patch("nowcastingcli.main.Prompt.ask", side_effect=["abc", "20.0"]):
        assert get_float("Temperature", -60, 60) == 20.0


# ---------------------------------------------------------------------------
# run
# ---------------------------------------------------------------------------
# run() calls Prompt.ask for pressure (directly) and then for temperature,
# humidity, and altitude (via get_float).  The call order within one cycle is:
#   1. Prompt.ask  →  pressure  (or "q" to quit)
#   2. Prompt.ask  →  temperature  (get_float)
#   3. Prompt.ask  →  humidity     (get_float)
#   4. Prompt.ask  →  altitude     (get_float)
#
# We also patch render_dashboard to prevent terminal output and to inspect
# which observations were passed to it.
# ---------------------------------------------------------------------------

def test_run_quits_on_lowercase_q():
    """'q' at the pressure prompt exits immediately without creating an observation.

    Run: pytest tests/test_main.py::test_run_quits_on_lowercase_q -v
    """
    with patch("nowcastingcli.main.Prompt.ask", return_value="q"):
        run()  # must return, not hang


def test_run_quits_on_uppercase_Q():
    """The quit check is case-insensitive: 'Q' works the same as 'q'.

    Run: pytest tests/test_main.py::test_run_quits_on_uppercase_Q -v
    """
    with patch("nowcastingcli.main.Prompt.ask", return_value="Q"):
        run()


def test_run_one_full_observation_cycle():
    """One valid reading is stored and the dashboard is rendered once, then 'q' exits.

    The five side_effect values map to the five Prompt.ask calls:
      "1013.25" → pressure, "20.0" → temperature, "50.0" → humidity,
      "100.0"   → altitude, "q"    → second pressure prompt (quit).

    Run: pytest tests/test_main.py::test_run_one_full_observation_cycle -v
    """
    prompts = ["1013.25", "20.0", "50.0", "100.0", "q"]
    with patch("nowcastingcli.main.Prompt.ask", side_effect=prompts), \
         patch("nowcastingcli.main.render_dashboard") as mock_render:
        run()

    mock_render.assert_called_once()
    observations = mock_render.call_args[0][0]   # first positional arg of last call
    assert len(observations) == 1
    assert observations[0].pressure_raw == pytest.approx(1013.25)
    assert observations[0].temperature  == pytest.approx(20.0)
    assert observations[0].humidity     == pytest.approx(50.0)
    assert observations[0].altitude     == pytest.approx(100.0)


def test_run_accumulates_multiple_observations():
    """Two readings accumulate in the list before 'q' quits.

    Run: pytest tests/test_main.py::test_run_accumulates_multiple_observations -v
    """
    prompts = [
        "1013.25", "20.0", "50.0", "100.0",   # first observation
        "1005.0",  "15.0", "60.0", "200.0",   # second observation
        "q",
    ]
    with patch("nowcastingcli.main.Prompt.ask", side_effect=prompts), \
         patch("nowcastingcli.main.render_dashboard") as mock_render:
        run()

    assert mock_render.call_count == 2
    final_observations = mock_render.call_args[0][0]
    assert len(final_observations) == 2


def test_run_exits_on_keyboard_interrupt():
    """KeyboardInterrupt (Ctrl-C) breaks the loop; run() must not re-raise it.

    Run: pytest tests/test_main.py::test_run_exits_on_keyboard_interrupt -v
    """
    with patch("nowcastingcli.main.Prompt.ask", side_effect=KeyboardInterrupt):
        run()


def test_run_exits_on_eof():
    """EOFError (e.g. stdin closed / piped input exhausted) exits gracefully.

    Run: pytest tests/test_main.py::test_run_exits_on_eof -v
    """
    with patch("nowcastingcli.main.Prompt.ask", side_effect=EOFError):
        run()


# --- Regression: invalid pressure input must not crash ---
# Before the fix, pressure was read with a raw float() call that bypassed
# validation.  Entering 0 or a negative value would reach normalize_pressure()
# and raise an unhandled ValueError.  The loop now validates pressure inline
# and uses `continue` to re-prompt rather than crashing.

def test_run_zero_pressure_does_not_crash():
    """Entering '0' for pressure must be rejected and re-prompt, not crash.

    side_effect sequence: '0' is rejected → 'q' exits the session.
    render_dashboard is never called because no valid observation was created.

    Run: pytest tests/test_main.py::test_run_zero_pressure_does_not_crash -v
    """
    with patch("nowcastingcli.main.Prompt.ask", side_effect=["0", "q"]), \
         patch("nowcastingcli.main.render_dashboard") as mock_render:
        run()
    mock_render.assert_not_called()


def test_run_negative_pressure_does_not_crash():
    """Entering a negative pressure must be rejected and re-prompt, not crash.

    Run: pytest tests/test_main.py::test_run_negative_pressure_does_not_crash -v
    """
    with patch("nowcastingcli.main.Prompt.ask", side_effect=["-5", "q"]), \
         patch("nowcastingcli.main.render_dashboard") as mock_render:
        run()
    mock_render.assert_not_called()


def test_run_non_numeric_pressure_does_not_crash():
    """Entering a non-numeric string for pressure must be rejected gracefully.

    Run: pytest tests/test_main.py::test_run_non_numeric_pressure_does_not_crash -v
    """
    with patch("nowcastingcli.main.Prompt.ask", side_effect=["abc", "q"]), \
         patch("nowcastingcli.main.render_dashboard") as mock_render:
        run()
    mock_render.assert_not_called()


def test_run_recovers_after_bad_pressure():
    """After a rejected pressure, the next valid entry completes a full cycle.

    Sequence: '0' rejected → '1013.25' accepted → temperature, humidity,
    altitude → 'q' exits.  One observation must be created.

    Run: pytest tests/test_main.py::test_run_recovers_after_bad_pressure -v
    """
    prompts = ["0", "1013.25", "20.0", "50.0", "100.0", "q"]
    with patch("nowcastingcli.main.Prompt.ask", side_effect=prompts), \
         patch("nowcastingcli.main.render_dashboard") as mock_render:
        run()
    mock_render.assert_called_once()
    assert len(mock_render.call_args[0][0]) == 1
