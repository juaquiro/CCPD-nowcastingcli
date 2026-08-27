# Module 2 — pytest: Unit Testing NowcastingCLI

> Part of: Claude Code for Python Developers: Hands-On Agentic Coding
> Repo: CCPD-nowcastingcli
> See also: [Course_Notes_Index.md](./Course_Notes_Index.md)

---

## Part 2 — pytest: Unit Testing NowcastingCLI

### Why pytest

Python ships with `unittest`, but pytest is the de facto standard in the
scientific Python ecosystem (NumPy, SciPy, scikit-image all use it).

Key advantages over `unittest`:

- No boilerplate classes — test functions, not methods
- Better assertion introspection — plain `assert`, not `assertEqual`/`assertAlmostEqual`
- Composable fixtures instead of `setUp`/`tearDown`
- Rich plugin ecosystem: `pytest-cov`, `pytest-benchmark`, `pytest-xdist`, etc.

Think of the difference between NAnt's verbose XML task definitions and a
modern build system — same capability, far less ceremony.

---

### Install

```bash
conda activate nowcastingcli
pip install pytest pytest-cov debugpy
```

---

### Where Tests Live

The project layout already has the right shape:

```
nowcastingcli/
├── nowcastingcli/
│   ├── physics.py
│   ├── heuristics.py
│   └── models.py
├── tests/
│   ├── __init__.py          # keep this — makes imports predictable
│   ├── test_physics.py
│   └── test_heuristics.py
└── pyproject.toml
```

pytest discovers anything matching `test_*.py` or `*_test.py` automatically.
No registration needed — no XML manifests, no test suite declarations.

---

### Testing `physics.py`

`normalize_pressure` is a pure function with no side effects. Perfect first target.

```python
# tests/test_physics.py
import pytest
from nowcastingcli.physics import normalize_pressure


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
    Tolerance loose — testing the formula direction, not ICAO tables.
    """
    qnh = normalize_pressure(950.0, altitude_m=856.0, temperature_c=15.0)
    assert pytest.approx(qnh, abs=2.0) == 1052.0


def test_negative_altitude_decreases_qnh():
    """Below sea level (Dead Sea ~-430m) → QNH < raw pressure."""
    raw = 1060.0
    qnh = normalize_pressure(raw, altitude_m=-430.0, temperature_c=25.0)
    assert qnh < raw


def test_extreme_cold_does_not_crash():
    """Formula must survive extreme temperatures without dividing by zero."""
    result = normalize_pressure(900.0, altitude_m=3000.0, temperature_c=-40.0)
    assert result > 0
```

Run:

```bash
pytest tests/test_physics.py -v
```

---

### Testing `heuristics.py`

Heuristics work on `list[Observation]`. Use a local factory function to build
test observations without going through the full input loop.

```python
# tests/test_heuristics.py
import pytest
from datetime import datetime, timedelta
from nowcastingcli.models import Observation
from nowcastingcli.heuristics import assess_conditions, WORSENING, STABLE, IMPROVING


def make_obs(pressure_qnh: float, humidity: float,
             temperature: float = 15.0, minutes_ago: int = 0) -> Observation:
    return Observation(
        timestamp=datetime.now() - timedelta(minutes=minutes_ago),
        pressure_raw=pressure_qnh - 2.0,
        pressure_qnh=pressure_qnh,
        temperature=temperature,
        humidity=humidity,
        altitude=340.0,
    )


def test_single_observation_returns_stable():
    obs = [make_obs(1013.0, 60.0)]
    verdict, _ = assess_conditions(obs)
    assert verdict == STABLE


def test_rapid_pressure_drop_is_worsening():
    obs = [
        make_obs(1013.0, 60.0, minutes_ago=30),
        make_obs(1011.5, 72.0, minutes_ago=15),
        make_obs(1009.8, 86.0, minutes_ago=0),
    ]
    verdict, reason = assess_conditions(obs)
    assert verdict == WORSENING
    assert reason  # non-empty string


def test_high_humidity_alone_triggers_worsening():
    obs = [
        make_obs(1013.0, 60.0, minutes_ago=30),
        make_obs(1013.0, 88.0, minutes_ago=0),   # pressure stable, humidity spiked
    ]
    verdict, _ = assess_conditions(obs)
    assert verdict == WORSENING


def test_pressure_rise_is_improving():
    obs = [
        make_obs(1008.0, 70.0, minutes_ago=30),
        make_obs(1010.5, 55.0, minutes_ago=0),
    ]
    verdict, _ = assess_conditions(obs)
    assert verdict == IMPROVING


def test_no_change_is_stable():
    obs = [
        make_obs(1013.0, 60.0, minutes_ago=30),
        make_obs(1013.2, 61.0, minutes_ago=0),
    ]
    verdict, _ = assess_conditions(obs)
    assert verdict == STABLE
```

---

### `pytest.approx`

Never use `==` for floats. Always use `pytest.approx`:

```python
# Bad — may fail due to floating-point representation
assert 0.1 + 0.2 == 0.3

# Good — tolerant comparison with default relative tolerance (1e-6)
assert 0.1 + 0.2 == pytest.approx(0.3)

# Explicit tolerances
assert result == pytest.approx(expected, rel=1e-4)   # 0.01% relative
assert result == pytest.approx(expected, abs=0.5)    # absolute ±0.5
```

This is the single-value equivalent of `numpy.testing.assert_allclose`,
which you'll use for array comparisons in Projects 2–3.

---

### Parameterized Tests

Instead of writing N nearly identical test functions, use `@pytest.mark.parametrize`:

```python
@pytest.mark.parametrize("altitude, expected_min", [
    (0,    1013.0),
    (500,  1070.0),
    (1000, 1130.0),
    (2000, 1260.0),
])
def test_qnh_increases_with_altitude(altitude, expected_min):
    qnh = normalize_pressure(1013.25, altitude_m=altitude, temperature_c=15.0)
    assert qnh >= expected_min - 10
```

This generates 4 named tests from one function. CI output names them individually:

```
test_physics.py::test_qnh_increases_with_altitude[0-1013.0] PASSED
test_physics.py::test_qnh_increases_with_altitude[500-1070.0] PASSED
...
```

---

### Coverage

```bash
pytest --cov=nowcastingcli --cov-report=term-missing
```

Example output:

```
Name                          Stmts   Miss  Cover   Missing
-----------------------------------------------------------
nowcastingcli/physics.py          3      0   100%
nowcastingcli/heuristics.py      28      4    86%   45-48
```

Lines 45-48 are untested — go look at them. Coverage is a navigation tool,
not a goal. 100% coverage with weak assertions is worthless; 85% with tight
assertions is solid.

Configure in `pyproject.toml` to set a minimum and make it the default:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--cov=nowcastingcli --cov-fail-under=80"
```

After this, plain `pytest` runs everything with coverage and fails the build
if you drop below 80%.

---

### Running Subsets

```bash
pytest tests/test_physics.py                                        # one file
pytest tests/test_physics.py::test_sea_level_returns_input          # one test
pytest -k "worsening"                                               # name filter
pytest -x                                                           # stop on first failure
pytest -v                                                           # verbose names
pytest --tb=short                                                   # shorter tracebacks
```

---

### Debugging Tests in VS Code

Two modes — pick by context.

#### Mode 1: VS Code Debugger (GUI)

**One-time setup:**

```bash
pip install --upgrade debugpy
```

Create `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Debug Pytest",
      "type": "debugpy",
      "request": "launch",
      "module": "pytest",
      "args": ["tests", "-v", "-s"],
      "justMyCode": false,
      "console": "integratedTerminal"
    }
  ]
}
```

Then: `Ctrl+Shift+P` → `Python: Select Interpreter` → select your conda env.

**Per-session:**

1. Click the gutter to set a breakpoint (red dot)
2. Press `F5` to launch
3. Inspect locals in the Variables panel or evaluate expressions in the Debug Console

`"justMyCode": false` is important — without it, the debugger won't step into
library source code (e.g., into `normalize_pressure` from a calling test).

---

#### Mode 2: `breakpoint()` + Terminal

No setup. Works in any terminal, including CI-like environments.

Drop `breakpoint()` anywhere — in test code or in source under test:

```python
def normalize_pressure(pressure_hpa, altitude_m, temperature_c):
    breakpoint()   # drops into pdb during any test that calls this
    return pressure_hpa * (1 - (0.0065 * altitude_m) / ...) ** -5.257
```

Run with output capture disabled (required — otherwise pdb I/O is swallowed):

```bash
pytest tests/ -v -s
```

Essential `pdb` commands at the `(Pdb)` prompt:

| Command | Action |
|---|---|
| `p <var>` | Print variable |
| `locals()` | All local variables |
| `n` | Next line (step over) |
| `s` | Step into function call |
| `c` | Continue to next breakpoint |
| `q` | Quit |

**Auto-drop on failure — no code changes needed:**

```bash
pytest tests/ -v -s --pdb
```

`--pdb` drops into the debugger at the point of any test failure. Useful when
you don't know in advance where to place a `breakpoint()`.

---

#### When to Use Which

| | Mode 1 (VS Code GUI) | Mode 2 (`pdb` terminal) |
|---|---|---|
| **Setup** | One-time `launch.json` | None |
| **Interface** | GUI — Variables panel, call stack, watch expressions | Terminal prompt |
| **Best for** | Complex multi-frame inspection, stepping through unfamiliar call stacks | Quick checks, CI-like environment |
| **`--pdb` flag** | Not applicable | Auto-drop on failure — no code change needed |

The two modes are not mutually exclusive. If you launch via `F5`, VS Code will
intercept `breakpoint()` calls and open its GUI at that line.

---

### Exercise Checklist

- [ ] `pip install pytest pytest-cov debugpy`
- [ ] Write `tests/test_physics.py` — at least 4 tests for `normalize_pressure`
- [ ] Write `tests/test_heuristics.py` — at least one test per verdict (WORSENING, STABLE, IMPROVING)
- [ ] Run `pytest -v` — all green
- [ ] Run with `--cov` — identify one untested branch and add a test for it
- [ ] Add `[tool.pytest.ini_options]` to `pyproject.toml` with `testpaths` and `addopts`
- [ ] Set a breakpoint in `normalize_pressure` and step through it via F5
- [ ] Reproduce the same inspection using `breakpoint()` + `pytest -v -s`
- [ ] Commit: `git add tests/ pyproject.toml .vscode/ && git commit -m "feat: add pytest test suite"`

---

---

