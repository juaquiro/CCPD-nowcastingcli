# Claude Code for Python Developers — Course Notes

> **Course:** Claude Code for Python Developers: Hands-On Agentic Coding
> **Repo:** CCPD-nowcastingcli
> **Last updated:** 2026-04-22

---

## Table of Contents

- [Part 1 — NowcastingCLI: Project Setup](#part-1--nowcastingcli-project-setup)
  - [Project Overview](#project-overview)
  - [Project Structure](#project-structure)
  - [Environment Setup](#environment-setup)
  - [Module Breakdown](#module-breakdown)
  - [Key Concepts](#key-concepts)
  - [Exercise Checklist](#exercise-checklist)
  - [What Each Module Will Touch](#what-each-module-will-touch)
- [Part 2 — pytest: Unit Testing NowcastingCLI](#part-2--pytest-unit-testing-nowcastingcli)
  - [Why pytest](#why-pytest)
  - [Install](#install)
  - [Where Tests Live](#where-tests-live)
  - [Testing physics.py](#testing-physicspy)
  - [Testing heuristics.py](#testing-heuristicspy)
  - [pytest.approx](#pytestapprox)
  - [Parameterized Tests](#parameterized-tests)
  - [Coverage](#coverage)
  - [Running Subsets](#running-subsets)
  - [Debugging Tests in VS Code](#debugging-tests-in-vs-code)
  - [Exercise Checklist](#exercise-checklist-1)
- [Part 3 — Claude Code: Refactoring, Test Generation, Code Explanation](#part-3--claude-code-refactoring-test-generation-code-explanation)
  - [What Claude Code Is](#what-claude-code-is)
  - [Installation](#installation)
  - [First Launch](#first-launch)
  - [Use Case 1 — Code Explanation](#use-case-1--code-explanation)
  - [Use Case 2 — Refactoring](#use-case-2--refactoring)
  - [Use Case 3 — Test Generation](#use-case-3--test-generation)
  - [Slash Commands](#slash-commands)
  - [CLAUDE.md — Persistent Project Instructions](#claudemd--persistent-project-instructions)
  - [VS Code Integration](#vs-code-integration)
  - [Exercise Checklist](#exercise-checklist-2)

---

## Part 1 — NowcastingCLI: Project Setup

### Project Overview

**NowcastingCLI** is the hands-on vehicle for the entire first arc of the course.
It is a terminal-based weather nowcasting dashboard that accepts periodic manual
observations and classifies atmospheric conditions as improving, stable, or worsening.

**Inputs per observation cycle:**

| Field | Unit | Range |
|---|---|---|
| Pressure (raw) | hPa | 800–1100 |
| Temperature | °C | −60 to +60 |
| Relative Humidity | % | 0–100 |
| GPS Altitude | m | −500 to 5000 |

**Outputs:**

- Live `rich` dashboard with per-variable trend arrows (↑ ↓ →)
- Pressure sparkline over the session
- Nowcast verdict: 🔴 Worsening / 🟡 Stable / 🟢 Improving
- Human-readable reason string

**Why this project:** The domain logic is simple enough (one formula, a handful
of heuristic rules) that tooling is always the focus — not the science.

---

### Project Structure

```
nowcastingcli/
├── nowcastingcli/
│   ├── __init__.py
│   ├── main.py          # Entry point and interactive loop
│   ├── models.py        # Observation dataclass
│   ├── physics.py       # Barometric formula (QNH normalization)
│   ├── heuristics.py    # Nowcast verdict logic
│   └── display.py       # Rich dashboard rendering
├── tests/
│   └── __init__.py
├── pyproject.toml
├── README.md
└── .gitignore
```

The inner `nowcastingcli/` directory is the importable package.
The layout is packaging-ready from day one — no restructuring needed later.

---

### Environment Setup

```bash
conda create -n nowcastingcli python=3.11
conda activate nowcastingcli
pip install rich
pip install -e .          # editable install — makes `nowcastingcli` available on PATH
```

After the editable install, the app launches with:

```bash
nowcastingcli
```

No `python -m` needed. The entry point is declared in `pyproject.toml`:

```toml
[project.scripts]
nowcastingcli = "nowcastingcli.main:run"
```

---

### Module Breakdown

#### `models.py` — Observation dataclass

```python
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Observation:
    timestamp: datetime
    pressure_raw: float      # hPa, as measured
    pressure_qnh: float      # hPa, normalized to sea level
    temperature: float       # °C
    humidity: float          # %
    altitude: float          # m (GPS)
```

A plain dataclass. No methods, no logic — just structured storage for one
observation cycle. The list of these objects is the entire in-memory time series.

---

#### `physics.py` — Barometric formula

```python
def normalize_pressure(pressure_hpa: float, altitude_m: float, temperature_c: float) -> float:
    """
    Barometric formula: correct station pressure to QNH (sea-level equivalent).
    Uses the hypsometric approximation valid below ~5000m.
    """
    return pressure_hpa * (1 - (0.0065 * altitude_m) / (temperature_c + 0.0065 * altitude_m + 273.15)) ** -5.257
```

**QNH** (Query: Nautical Height) is the standard aviation/meteorology term for
pressure corrected to sea level. Without this correction, observers at different
altitudes cannot compare readings.

This is a pure function with no side effects — ideal for unit testing.

---

#### `heuristics.py` — Nowcast logic

```python
WORSENING = "worsening"
STABLE    = "stable"
IMPROVING = "improving"

def assess_conditions(observations: list[Observation]) -> tuple[str, str]:
    """Returns (verdict, reason) based on the last two observations."""
```

**Heuristic rules (simplified field meteorology):**

| Verdict | Condition |
|---|---|
| 🔴 Worsening | Pressure drop > 1 hPa since last reading, **or** humidity > 85% |
| 🟢 Improving | Pressure rise > 1 hPa since last reading **and** humidity falling |
| 🟡 Stable | Everything else |

Key design decision: the function takes the full observation list but only
examines the last two entries. This keeps the signature stable as the list grows,
and makes the logic easy to test with minimal fixtures.

---

#### `display.py` — Rich dashboard

Key helpers:

```python
SPARKLINE_CHARS = "▁▂▃▄▅▆▇█"

def sparkline(values: list[float]) -> str:
    """Renders a unicode block sparkline for a list of floats."""

def trend_arrow(current: float, previous: float | None, threshold: float = 0.1) -> str:
    """Returns ↑, ↓, or → based on delta vs threshold."""

def render_dashboard(observations: list[Observation]) -> None:
    """Clears terminal and redraws the full dashboard."""
```

`console.clear()` at the top of `render_dashboard` gives the illusion of a
live-updating display — the terminal is redrawn from scratch on every observation.

---

#### `main.py` — Entry point

```python
def get_float(prompt: str, min_val: float, max_val: float) -> float:
    """Validated float input with range checking. Loops until valid."""

def run() -> None:
    """Main loop: collect observation → compute QNH → append → redraw."""
```

`run()` is the function bound to the `nowcastingcli` console script entry point.
`KeyboardInterrupt` and `EOFError` are caught so `Ctrl+C` exits cleanly.

---

#### `pyproject.toml` — Packaging metadata

```toml
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.backends.legacy:build"

[project]
name = "nowcastingcli"
version = "0.1.0"
description = "Terminal weather nowcasting dashboard"
requires-python = ">=3.11"
dependencies = ["rich>=13.0"]

[project.scripts]
nowcastingcli = "nowcastingcli.main:run"

[tool.setuptools.packages.find]
where = ["."]
```

`pyproject.toml` is the modern Python packaging standard (PEP 517/518).
It replaces the legacy `setup.py` + `setup.cfg` pair.
`setuptools` is used here as the build backend — the most common choice
for scientific/engineering packages.

---

### Key Concepts

#### Editable install (`pip install -e .`)

Installs the package by reference to the source tree rather than copying it.
Changes to `.py` files take effect immediately without reinstalling.
Essential for development. Equivalent to `python setup.py develop` (old style).

#### Pure functions and testability

`physics.py` and `heuristics.py` contain only pure functions:
no I/O, no global state, deterministic output for any given input.
This is the property that makes unit testing trivial — no mocking required.

#### `rich` console lifecycle

`Console()` is instantiated once at module level in `display.py` and imported
into `main.py`. This avoids creating multiple console instances, which can
cause interleaved output. `console.clear()` + full redraw is the simplest
approach to a live dashboard without `asyncio` or `curses`.

#### In-memory time series

The entire session history is a plain Python `list[Observation]`.
No database, no file I/O, no persistence between sessions.
This is intentional for Project 1 — persistence is introduced in Projects 4–5.

---

### Exercise Checklist

- [ ] Create directory structure and all module files
- [ ] Run `pip install -e .` — verify no errors
- [ ] Run `nowcastingcli` — verify dashboard launches
- [ ] Enter 3 worsening observations:
  - Reading 1: 1013 hPa, 18°C, 60% RH, 340m
  - Reading 2: 1011.5 hPa, 17°C, 72% RH, 340m
  - Reading 3: 1009.8 hPa, 17°C, 86% RH, 340m
- [ ] Confirm 🔴 verdict and downward sparkline
- [ ] Push to GitHub repo `CCPD-nowcastingcli`

---

### What Each Module Will Touch

| Course Module | Target in NowcastingCLI |
|---|---|
| **pytest** | `physics.py`, `heuristics.py` — pure functions, no fixtures needed |
| **Claude Code** | Refactoring, test generation, code explanation |
| **Logging** | Observation loop in `main.py` — structured log per cycle |
| **MkDocs** | Public API of `physics.py` and `heuristics.py` |
| **GitHub Actions** | pytest on push; ruff linting |
| **Packaging** | Build wheel; publish to TestPyPI or local index |

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

## Part 3 — Claude Code: Refactoring, Test Generation, Code Explanation

### What Claude Code Is

Claude Code is Anthropic's agentic CLI coding tool — a coding agent that lives
in your terminal, has full read/write access to your repo, can run commands,
and reasons about your codebase as a whole, not just a pasted snippet.

| This chat (Claude.ai) | Claude Code |
|---|---|
| You copy-paste code in | Reads your files directly |
| Stateless per message | Persistent session with repo awareness |
| You apply suggestions manually | Edits files and runs commands itself |
| Good for explaining concepts | Good for doing work inside your project |

The three core workflows covered in this module:

1. **Explaining** — "What does this formula actually do?"
2. **Refactoring** — "Restructure this without changing behavior"
3. **Generating tests** — "Write pytest tests for `physics.py`"

---

### Installation

Claude Code is a Node.js CLI tool — installed globally, not into your conda env:

```bash
npm install -g @anthropic-ai/claude-code
claude --version
```

If Node.js is not available or is too old (need ≥ 18):

```bash
conda install -c conda-forge nodejs
```

**Authentication:** on first run, `claude` opens a browser to authenticate via
your Anthropic account. API usage is billed separately from Claude.ai subscriptions.

---

### First Launch

Always launch from the project root — Claude Code reads the directory structure immediately:

```bash
cd ~/path/to/CCPD-nowcastingcli
claude
```

This drops into an interactive REPL. The interaction model is:
**conversation + file access + command execution**, all in one session.

---

### Use Case 1 — Code Explanation

Claude Code reads the actual file — you don't paste code. Example prompt:

```
Explain normalize_pressure() in physics.py. Walk through the math step by step,
relate each constant to its physical meaning, and state what approximations are
being made and when they break down.
```

It will break down the hypsometric equation: `0.0065` is the standard
tropospheric lapse rate (K/m); `-5.257` is the barometric exponent derived
from the ideal gas law + hydrostatic equation; validity domain is ~5000m
under standard atmosphere assumptions.

It can also cross-reference `models.py` to understand units flowing in — the
whole repo is its context, not just the file you mention.

---

### Use Case 2 — Refactoring

A concrete refactoring task for `physics.py`:

```
Refactor physics.py:
1. Extract the magic numbers (0.0065, 5.257, 273.15) as named module-level
   constants with comments explaining their physical meaning
2. Add a guard that raises ValueError if altitude_m > 5000 or pressure_hpa <= 0
3. Keep the function signature identical — no behavioral changes
4. Update the docstring to document the raised exception
Run the existing pytest suite after to confirm no regressions.
```

Claude Code will edit the file and run `pytest` itself. If tests fail, it
attempts to fix the issue before reporting back.

**The agentic loop:** edit → test → observe → fix. You watch; you don't drive.

The resulting `physics.py` after refactoring:

```python
# Physical constants
LAPSE_RATE = 0.0065          # Standard tropospheric lapse rate, K/m
BAROMETRIC_EXPONENT = 5.257  # Derived from ideal gas law + hydrostatic equation
KELVIN_OFFSET = 273.15       # °C to Kelvin conversion

def normalize_pressure(pressure_hpa: float, altitude_m: float, temperature_c: float) -> float:
    """
    Barometric formula: correct station pressure to QNH (sea-level equivalent).
    Uses the hypsometric approximation valid below ~5000m.

    Raises:
        ValueError: if pressure_hpa <= 0 or altitude_m > 5000.
    """
    if pressure_hpa <= 0:
        raise ValueError(f"pressure_hpa must be positive, got {pressure_hpa}")
    if altitude_m > 5000:
        raise ValueError(f"altitude_m exceeds valid range (>5000m): got {altitude_m}")

    return pressure_hpa * (
        1 - (LAPSE_RATE * altitude_m) / (temperature_c + LAPSE_RATE * altitude_m + KELVIN_OFFSET)
    ) ** -BAROMETRIC_EXPONENT
```

---

### Use Case 3 — Test Generation

After refactoring, prompt Claude Code to generate tests for the new validation:

```
Add tests to tests/test_physics.py for the new ValueError guards added in
physics.py. Follow the existing test style. Run pytest when done and confirm all pass.
```

Claude Code reads your existing `test_physics.py` to match the style
(naming conventions, `pytest.approx` usage, fixture patterns), appends the
new tests, and runs them.

**Critical caveat:** generated tests need review. Claude Code produces
syntactically correct, passing tests — but can write tautological ones
(testing that the function returns what it's hardcoded to return, not that
it constrains behavior). Ask yourself: *does this test fail if I break the
implementation in a plausible way?* If not, strengthen it.

---

### Slash Commands

In the Claude Code REPL, slash commands control the session:

| Command | Purpose |
|---|---|
| `/help` | List all commands |
| `/clear` | Clear conversation history (start fresh) |
| `/compact` | Summarize history to save context window |
| `/cost` | Show token usage for this session |
| `/review` | Request a code review of recent changes |
| `/undo` | Revert last file edit (uses git under the hood) |
| `/diff` | Show what's changed since session start |

`/undo` is the safety net — Claude Code edits real files. Your git history
is always there as a second line of defense.

---

### CLAUDE.md — Persistent Project Instructions

Drop `CLAUDE.md` at the repo root. Claude Code reads it at session start as
a persistent project-level system prompt — equivalent to a `Jenkinsfile`
that describes how the project works, but for the AI agent.

```markdown
# NowcastingCLI — Claude Code Instructions

## Environment
- conda env: `nowcastingcli` (Python 3.11)
- activate before running: `conda activate nowcastingcli`
- run tests: `pytest`
- run app: `nowcastingcli`

## Code Conventions
- Type hints on all public functions
- Docstrings on all public functions
- Named constants for magic numbers in physics.py
- No print() — use rich console for all output

## Architecture
- models.py: only dataclasses, no logic
- physics.py: pure functions only, no I/O
- heuristics.py: pure functions only, depends only on models.py
- display.py: all rich rendering, single Console() instance
- main.py: orchestration only, thin layer over the others

## Test Conventions
- pytest.approx for all float comparisons
- parametrize for table-driven tests
- test file mirrors source: test_physics.py tests physics.py
```

With `CLAUDE.md` in place, every session starts with your conventions loaded.
It won't suggest `print()` when you've told it to use `rich`; it won't create
flat test files when you've specified a mirrored structure.

---

### VS Code Integration

Install the "Claude Code" extension from the VS Code marketplace.

- `Ctrl+Shift+P` → "Claude Code: Open" — launches the REPL panel inside VS Code
- Highlight code and send it to Claude Code with surrounding file context
- File edits appear live in your editor as Claude Code makes them

The terminal workflow and the VS Code panel are the same underlying session.
Use whichever keeps you in flow.

---

### Exercise Checklist

- [ ] Install Claude Code: `npm install -g @anthropic-ai/claude-code`, verify launch from repo root
- [ ] Create `CLAUDE.md` with project conventions (adapt the template above)
- [ ] Run the **explanation** task: ask Claude Code to explain `normalize_pressure()` step by step
- [ ] Run the **refactoring** task: extract named constants + add validation, let it run pytest
- [ ] Run the **test generation** task: generate tests for the new validators
- [ ] Review generated tests critically — strengthen at least one that is too weak
- [ ] Commit: `git commit -m "refactor: extract constants and add validation to physics.py"`

---

*Notes will be extended as each module is completed.*
