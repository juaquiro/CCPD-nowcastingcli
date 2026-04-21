# NowcastingCLI

A terminal-based weather nowcasting CLI built with Python and [Rich](https://github.com/Textualize/rich).

---

## Project Structure

```
NOWCASTINGCLI/
├── nowcastingcli/              # installable package
│   ├── __init__.py             # package marker
│   ├── main.py                 # CLI entry point — run() and get_float()
│   ├── models.py               # Observation dataclass
│   ├── physics.py              # barometric QNH normalisation
│   ├── heuristics.py           # worsening / stable / improving logic
│   └── display.py              # Rich dashboard, sparkline, trend arrows
├── tests/                      # pytest test suite
│   ├── __init__.py
│   ├── test_display.py         # tests for sparkline, trend_arrow, render_dashboard
│   ├── test_heuristics.py      # tests for assess_conditions()
│   ├── test_main.py            # tests for run() and get_float()
│   ├── test_models.py          # tests for Observation dataclass
│   └── test_physics.py         # tests for normalize_pressure()
├── scripts/                    # standalone helper scripts
│   ├── Init_observation.py     # quick manual smoke-test for Observation
│   ├── sync_env.bat            # sync conda environment between machines
│   └── update_lock.bat         # regenerate environment.lock.yml
├── .vscode/
│   ├── launch.json             # pytest debug configuration
│   └── settings.json
├── environment.lock.yml        # pinned conda environment snapshot
├── pyproject.toml              # build, dependencies, and pytest config
├── README.md
├── COURSE_NOTES.md
└── README_CONDA_ENV_SYNC.md    # guide for syncing conda envs across machines
```

---

## `pyproject.toml`

```toml
[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"

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

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--cov=nowcastingcli --cov-fail-under=80"
```

Key sections explained:

- **`[build-system]`** — tells pip to use `setuptools` to build the package.
- **`[project]`** — package metadata: name, version, Python version constraint, and runtime dependencies (`rich`).
- **`[project.scripts]`** — registers the `nowcastingcli` shell command, pointing it at the `run()` function in `main.py`. Available anywhere in the active environment after `pip install -e .`.
- **`[tool.setuptools.packages.find]`** — tells setuptools to auto-discover the `nowcastingcli` package from the project root.
- **`[tool.pytest.ini_options]`** — pytest configuration baked into `pyproject.toml` so no separate `pytest.ini` is needed:
  - `testpaths` tells pytest to look for tests only in `tests/`.
  - `addopts` automatically adds coverage flags to every `pytest` run: `--cov=nowcastingcli` measures coverage of the source package, and `--cov-fail-under=80` fails the run if total coverage drops below 80 %.

---

## Setup

### 1. Create and activate the conda environment

```bash
conda create -n nowcastingcli python=3.11
conda activate nowcastingcli
```

### 2. Install setuptools

```bash
conda install setuptools -c conda-forge
```

### 3. Install the package in editable mode

From the project root (`NOWCASTINGCLI/`):

```bash
pip install -e .
```

This installs all dependencies (including `rich`) and registers the
`nowcastingcli` console script.

---

## Verifying the CLI

### Step 1 — Launch

```bash
nowcastingcli
```

You should see:

```
NowcastingCLI v1.0 — type 'q' at any prompt to quit
```

### Step 2 — Enter 3 observations that simulate a worsening scenario

Respond to each prompt as shown below.

**Reading 1 — baseline**

```
Enter pressure (hPa), or 'q' to quit: 1013
Temperature (°C): 18
Relative Humidity (%): 60
GPS Altitude (m): 340
```

**Reading 2 — slight drop**

```
Enter pressure (hPa), or 'q' to quit: 1011.5
Temperature (°C): 17
Relative Humidity (%): 72
GPS Altitude (m): 340
```

**Reading 3 — accelerating drop + high humidity**

```
Enter pressure (hPa), or 'q' to quit: 1009.8
Temperature (°C): 17
Relative Humidity (%): 86
GPS Altitude (m): 340
```

### Step 3 — Confirm expected dashboard output

After Reading 3 the dashboard panel should show:

| What to check | Expected |
|---|---|
| Nowcast verdict | `🔴 CONDITIONS WORSENING` |
| Reason | `Rapid pressure fall … + High humidity (86%)` |
| Pressure sparkline | characters tracking a downward trend (e.g. `█▅▂`) with a negative total delta |

The worsening verdict is triggered because:
- QNH pressure dropped more than 1 hPa between consecutive readings **and/or**
- humidity exceeded 85 % (Reading 3 = 86 %)

---

## Running scripts from VS Code

Once installed in editable mode the VS Code **▶ play button** works on any
script without a `launch.json`:

```python
# test_scripts/Init_observation.py
from datetime import datetime
from nowcastingcli.models import Observation

obs = Observation(
    timestamp    = datetime.now(),
    pressure_raw = 1013.25,
    pressure_qnh = 1015.80,
    temperature  = 18.5,
    humidity     = 62.0,
    altitude     = 340.0
)

print(obs)
```

---

## Naming Conventions

This project follows **PEP 8** — the official Python style guide
(<https://peps.python.org/pep-0008/>). PEP 8 defines naming rules per
identifier type:

| Identifier type | Convention | Examples from this project |
|---|---|---|
| Functions | `snake_case` | `get_float`, `run`, `render_dashboard`, `normalize_pressure` |
| Variables | `snake_case` | `pressure_raw`, `pressure_qnh`, `min_val`, `pressure_delta` |
| Dataclass fields | `snake_case` | `timestamp`, `pressure_raw`, `pressure_qnh`, `humidity` |
| Classes | `PascalCase` | `Observation` |
| Module-level constants | `UPPER_SNAKE_CASE` | `WORSENING`, `STABLE`, `SPARKLINE_CHARS`, `VERDICT_STYLE` |
| Module-level singletons | `snake_case` | `console` (a `Console()` instance, not a true constant) |
| Private / internal helpers | `_snake_case` | `_obs` in test files (leading underscore signals "not public") |
| Test functions | `test_snake_case` | `test_run_quits_on_lowercase_q`, `test_valid_observation_is_created` |
| pytest fixtures | `snake_case` | `silence_console`, `make_obs` |

### Why these rules matter

- **`snake_case` for functions and variables** is the most visible rule and
  the one that most clearly separates Python from languages like Java or
  JavaScript which use `camelCase` for the same things.
- **`PascalCase` for classes** makes it immediately obvious at the call site
  that `Observation(...)` constructs an object, not calls a function.
- **`UPPER_SNAKE_CASE` for constants** signals "this value is fixed at module
  load time and should not be reassigned".
- **Leading `_` for private helpers** is a convention, not enforcement — Python
  does not block access, but it tells readers (and tools like pytest) that the
  identifier is an implementation detail.

### Type hints (PEP 484 / PEP 604)

Type hints use the modern syntax available from Python 3.10+:

```python
def get_float(prompt: str, min_val: float, max_val: float) -> float: ...
def run() -> None: ...
observations: list[Observation] = []   # lowercase generic, not List[Observation]
float | None                           # union with | instead of Union[float, None]
```

---

## Unit Testing

### Tools and conventions

This project uses **pytest** as the test runner and **`unittest.mock`** from
the Python standard library for mocking. They are used together — this is the
standard convention in the Python ecosystem:

| Tool | Role |
|---|---|
| `pytest` | Test runner, assertions (`assert`, `pytest.raises`, `pytest.approx`), fixtures |
| `unittest.mock` | Mocking (`patch`, `MagicMock`, `side_effect`) |

`unittest.mock` is part of the standard library — no extra install is needed.
The key rule is to avoid mixing **`unittest.TestCase`** (the class-based style)
with pytest, as that conflicts with fixtures and other pytest features.

### Running tests

```bash
# all tests
pytest -v

# one file
pytest tests/test_models.py -v

# one test
pytest tests/test_main.py::test_run_one_full_observation_cycle -v
```

### Mocking interactive input

`main.py` uses `rich.prompt.Prompt.ask` to read user input. In tests, that
call is replaced with a mock so tests run non-interactively:

```python
from unittest.mock import patch

# Single scripted answer
with patch("nowcastingcli.main.Prompt.ask", return_value="20.0"):
    result = get_float("Temperature", -60, 60)

# Queue of scripted answers (consumed in order)
with patch("nowcastingcli.main.Prompt.ask", side_effect=["abc", "20.0"]):
    result = get_float("Temperature", -60, 60)
```

`side_effect` with a list makes the mock return each value in turn, which lets
you script retry loops and multi-prompt sequences without touching the terminal.

### Test helper pattern (`_obs`)

Test files use a factory helper prefixed with `_` to build valid objects with
sensible defaults. The leading underscore tells pytest not to collect it as a
test:

```python
def _obs(**overrides):
    defaults = dict(pressure_raw=1013.25, humidity=50.0, ...)
    defaults.update(overrides)          # caller overrides only what it needs
    return Observation(**defaults)      # unpack dict as keyword arguments

# Each test changes only the one field it cares about
def test_humidity_above_100_raises():
    with pytest.raises(ValueError):
        _obs(humidity=100.1)
```

---

## Interactive REPL

```bash
python -i test_scripts/Init_observation.py
```

Executes the script and leaves the interpreter open with all variables defined.
