# NowcastingCLI

A terminal-based weather nowcasting CLI built with Python and [Rich](https://github.com/Textualize/rich).

---

## Branching Model

This repo uses a two-branch model:

| Branch | Role | Notes |
|---|---|---|
| `develop` | Default branch — everyday feature integration | All feature work and PRs target this branch |
| `main` | Stable / production-ready branch | Updated only via PR from `develop` at release time; protected — no direct pushes, no force-pushes, no deletion |

Everyday workflow: branch off `develop`, open a PR back into `develop`. When
`develop` is stable and ready to ship, open a PR from `develop` into `main`
to cut a release.

---

## Project Structure

```
NOWCASTINGCLI/
├── nowcastingcli/              # installable package
│   ├── __init__.py             # package marker
│   ├── main.py                 # CLI entry point — cli(), run(), get_float(), edit_observation()
│   ├── models.py               # Observation dataclass
│   ├── physics.py              # barometric QNH normalisation
│   ├── heuristics.py           # worsening / stable / improving logic
│   ├── display.py              # Rich dashboard, sparkline, trend arrows
│   └── logging_config.py       # dictConfig setup — rotating JSON file + stderr handlers
├── tests/                      # pytest test suite
│   ├── __init__.py
│   ├── test_display.py         # tests for sparkline, trend_arrow, render_dashboard
│   ├── test_heuristics.py      # tests for assess_conditions()
│   ├── test_main.py            # tests for run() and get_float()
│   ├── test_models.py          # tests for Observation dataclass
│   └── test_physics.py         # tests for normalize_pressure()
├── scripts/                    # standalone helper scripts
│   ├── Init_observation.py     # quick manual smoke-test for Observation
│   ├── test_observations.csv   # sample CSV for --input and logging smoke-tests
│   ├── test_logging.sh         # logging smoke-test (Bash / Git Bash / macOS)
│   ├── test_logging.bat        # logging smoke-test (Windows CMD)
│   ├── sync_env.bat            # sync conda environment between machines
│   └── update_lock.bat         # regenerate environment.lock.yml
├── docs/                       # project documentation
│   ├── index.md                # landing page
│   ├── architecture.md         # module map and data-flow diagram
│   ├── usage.md                # input loop, valid ranges, dashboard reference
│   └── api/                    # per-module API reference (mkdocstrings stubs)
│       ├── physics.md
│       ├── models.md
│       ├── heuristics.md
│       └── display.md
├── logs/                       # auto-created at runtime — rotating JSON log files
├── .vscode/
│   ├── launch.json             # pytest debug configuration
│   └── settings.json
├── environment.lock.yml        # pinned conda environment snapshot
├── pyproject.toml              # build, dependencies, and pytest config
├── TODO.md                     # pending improvements
├── SESSION_SUMMARY.md          # per-session change log
├── README.md
├── course_notes/                # course notes, split per module
│   ├── Course_Notes_Index.md
│   ├── Module1_Course_Notes.md
│   ├── Module2_Course_Notes.md
│   ├── Module3_Course_Notes.md
│   ├── Module4_Course_Notes.md
│   └── Module5_Course_Notes.md
└── README_CONDA_ENV_SYNC.md    # guide for syncing conda envs across machines
```

---

## Documentation

Human-readable docs live in `docs/`:

| File | Contents |
|------|----------|
| [`docs/index.md`](docs/index.md) | Project overview and quick-start |
| [`docs/architecture.md`](docs/architecture.md) | Module map and data-flow diagram |
| [`docs/usage.md`](docs/usage.md) | Full input-loop reference, valid ranges, dashboard column guide |
| [`docs/api/physics.md`](docs/api/physics.md) | `normalize_pressure()` API reference |
| [`docs/api/models.md`](docs/api/models.md) | `Observation` dataclass field reference |
| [`docs/api/heuristics.md`](docs/api/heuristics.md) | `assess_conditions()` API reference |
| [`docs/api/display.md`](docs/api/display.md) | Dashboard rendering functions API reference |

Course notes live in [`course_notes/`](course_notes/), split per module and
indexed in [`course_notes/Course_Notes_Index.md`](course_notes/Course_Notes_Index.md).

To build and serve the docs site locally:

```bash
pip install -e ".[docs]"
mkdocs serve
```

To install every optional extra (`docs` + `dev`) alongside the runtime
dependencies in one shot:

```bash
pip install -e ".[docs,dev]"
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
dependencies = ["rich>=13.0", "python-json-logger"]

[project.scripts]
nowcastingcli = "nowcastingcli.main:cli"

[tool.setuptools.packages.find]
where = ["."]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--cov=nowcastingcli --cov-fail-under=80"

[project.optional-dependencies]
docs = [
    "mkdocs",
    "mkdocs-material",
    "mkdocstrings[python]",
]
dev = [
    "pytest",
    "pytest-cov",
    "setuptools",
    "wheel",
]
```

Key sections explained:

- **`[build-system]`** — tells pip to use `setuptools` to build the package.
- **`[project]`** — package metadata: name, version, Python version constraint, and runtime dependencies (`rich`, `python-json-logger`).
- **`[project.scripts]`** — registers the `nowcastingcli` shell command, pointing it at the `cli()` entry point in `main.py`. `cli()` parses `--input` from `sys.argv` and delegates to `run()`. Available anywhere in the active environment after `pip install -e .`.
- **`[project.optional-dependencies]`** — extra dependency groups. `docs` (MkDocs, the Material theme, `mkdocstrings`) installs with `pip install -e ".[docs]"`; `dev` (`pytest`, `pytest-cov`, `setuptools`, `wheel`) installs with `pip install -e ".[dev]"`. Install both together, on top of the required dependencies, with `pip install -e ".[docs,dev]"`.
- **`[tool.setuptools.packages.find]`** — tells setuptools to auto-discover the `nowcastingcli` package from the project root.
- **`[tool.pytest.ini_options]`** — pytest configuration baked into `pyproject.toml` so no separate `pytest.ini` is needed:
  - `testpaths` tells pytest to look for tests only in `tests/`.
  - `addopts` automatically adds coverage flags to every `pytest` run: `--cov=nowcastingcli` measures coverage of the source package, and `--cov-fail-under=80` fails the run if total coverage drops below 80 %.

---

## Building a Distributable Package

Full detail, verification steps, and rationale live in
[`course_notes/Module6_Course_Notes.md`](course_notes/Module6_Course_Notes.md).
Five ways to hand off a build, depending on what the target machine has:

| Path | Output | Target needs | Command |
|---|---|---|---|
| **1. PyPI / TestPyPI** | Published package, installable by name | Python + pip, network access | `python -m build` then `twine upload dist/*` (or `--repository testpypi`) |
| **2. conda packaging** | conda package | conda | Not used for this project yet (no compiled/Qt deps) — see notes for a `meta.yaml` sketch |
| **3. Local wheel / editable install** | `.whl` file or a git clone | Python + pip (no PyPI account, no network needed for the wheel option) | `pip install nowcastingcli-<version>-py3-none-any.whl`, or `git clone` + `pip install -e .` |
| **4. Standalone `.exe` (PyInstaller)** | Single self-contained executable | **Nothing** — no Python required at all | `pyinstaller nowcastingcli.spec` (rebuilds from the committed spec; see `launcher.py` and `nowcastingcli.spec`) |
| **5. Unix / Raspberry Pi (`pipx`)** | Isolated CLI install, no conda needed | Python + pip on a Unix target (e.g. Raspberry Pi OS) | `pipx install nowcastingcli` (or `pipx install --index-url https://test.pypi.org/simple/ --pip-args="--extra-index-url https://pypi.org/simple/" nowcastingcli` for TestPyPI) |

Paths 1–3 and 5 all assume a Python interpreter is already on the target
machine (a "framework-dependent" deployment); Path 4 bundles the
interpreter itself (a "self-contained" deployment) and is distributed
directly — zipped, attached to a release, handed over on a USB stick —
never uploaded to PyPI. Path 5 is the Unix/Raspberry Pi counterpart to
conda on Windows: NowcastingCLI's wheel is pure Python (`py3-none-any`),
so the same wheel installs unmodified on ARM — no PyInstaller rebuild or
conda/miniforge overhead needed, and `pipx` avoids Debian's PEP 668
`externally-managed-environment` guard that blocks a bare `pip install`.

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

This installs the required runtime dependencies (`rich`, `python-json-logger`)
and registers the `nowcastingcli` console script.

To also pull in the documentation toolchain (`docs` extra) and development
tooling (`dev` extra — `pytest`, `pytest-cov`, `setuptools`, `wheel`):

```bash
pip install -e ".[docs,dev]"
```

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

## Input Modes

### Interactive mode (default)

```bash
nowcastingcli
```

The CLI prompts for each field one at a time. Type `q` at any pressure prompt to quit, or `e` to edit a past reading.

### File input mode (`--input`)

```bash
nowcastingcli --input path/to/observations.csv
```

Reads observations from a CSV file and runs the full session non-interactively. Useful for automated testing, replaying scenarios, and log verification.

### CSV file format

The file must have exactly these four columns (order matters, header required):

| Column | Unit | Valid range |
|---|---|---|
| `pressure_hpa` | hPa | 0.1 – 1100.0 |
| `temperature_c` | °C | -60 – 60 |
| `humidity_pct` | % | 0 – 100 |
| `altitude_m` | m | -500 – 5000 |

Example — `scripts/test_observations.csv`:

```csv
pressure_hpa,temperature_c,humidity_pct,altitude_m
1013,18,60,340
1011.5,17,72,340
1009.8,17,86,340
```

Validation errors are reported with the row number and field name before the session starts:

```
Input file error: Row 3: temperature = 99.0 out of range [-60, 60]
```

### Logging smoke-test scripts

Both scripts run `test_observations.csv` through the CLI and pretty-print the JSON log to verify that `DEBUG`, `INFO`, and `WARNING` events were written in the correct order.

**Bash (Git Bash / Linux / macOS):**

```bash
bash scripts/test_logging.sh
```

**Windows CMD:**

```bat
scripts\test_logging.bat
```

Expected log events per observation cycle, in order:

| Event | Level | Source |
|---|---|---|
| Session start | `INFO` | `main` |
| Raw sensor input | `DEBUG` | `main` |
| Observation recorded | `INFO` | `display` |
| Verdict change (when it occurs) | `WARNING` | `main` |

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

## `normalize_pressure()` — Barometric QNH Formula

### What it computes

A weather station sits at some altitude. Its raw reading is **station pressure** (what the air actually weighs at that height). To compare stations at different elevations — and to produce the sea-level pressure shown on synoptic charts — you need **QNH**, the pressure the station *would* read if it were at sea level. `normalize_pressure()` does that conversion.

### The math, step by step

The underlying physics is the **hypsometric (barometric) formula**, derived from hydrostatic equilibrium and the ideal-gas law:

```
P₀ = P_station × (T₀ / T_station) ^ (g·M / R·L)
```

Rearranging so T₀ appears only once:

```
P₀ = P_station × (1 − L·h / T₀) ^ −(g·M / R·L)
```

The code substitutes each piece:

**`0.0065` — the temperature lapse rate, L (K/m)**

The International Standard Atmosphere (ISA) assumes temperature falls by **6.5 K per 1000 m** of altitude. This is `L = 0.0065 K/m`.

**`temperature_c + 0.0065 * altitude_m + 273.15` — sea-level temperature, T₀ (K)**

The station temperature is measured at `altitude_m` above sea level. To get what the temperature *would be* at sea level, you add back the lapse-rate warming for the full column:

```
T₀ = T_station_Kelvin + L × h
   = (temperature_c + 273.15) + 0.0065 × altitude_m
```

The `+ 273.15` converts Celsius to Kelvin.

**`(0.0065 * altitude_m) / T₀` — the fractional temperature drop**

This ratio is `L·h / T₀`, the fraction by which the temperature column contracts between station and sea level. It is always < 1 for realistic inputs.

**`(1 − L·h/T₀) ^ −5.257` — the pressure correction factor**

The exponent **5.257** is `g·M / (R·L)`:

| Symbol | Meaning | Value |
|--------|---------|-------|
| g | gravitational acceleration | 9.80665 m/s² |
| M | molar mass of dry air | 0.028964 kg/mol |
| R | universal gas constant | 8.31446 J/(mol·K) |
| L | lapse rate | 0.0065 K/m |

```
g·M / (R·L) = (9.80665 × 0.028964) / (8.31446 × 0.0065) ≈ 5.257
```

The **negative** exponent flips the ratio: because pressure decreases with altitude, correcting upward to sea level requires multiplying by something **greater than 1**, which `(fraction < 1)^−5.257` delivers.

**Final multiplication**

```
QNH = P_station × correction_factor
```

For a typical mountain station at 1500 m, 15 °C, 850 hPa, the correction factor is ≈ 1.196, giving QNH ≈ 1016 hPa — a plausible sea-level pressure.

### Approximations being made

| Approximation | What it assumes | Reality |
|--------------|-----------------|---------|
| Constant lapse rate | Temperature always drops at 6.5 K/km | Varies with weather: inversions, convective instability, fronts |
| Dry air molar mass | Uses M = 0.02896 kg/mol | Humid air is lighter (M_water = 0.018). Error scales with humidity and altitude |
| Ideal gas | PV = nRT exactly | Small correction at high pressures, negligible here |
| Hydrostatic equilibrium | No vertical accelerations | Breaks in strong convection or turbulence |
| Constant gravity | g does not change with altitude | g decreases by ~0.03% per 100 m — negligible below 5 km |

### When it breaks down

- **Above ~5000 m**: the ISA lapse rate diverges from the actual atmosphere; the tropopause (~11 km) has L ≈ 0 and the formula is simply wrong above it.
- **Temperature inversions**: when temperature *increases* with altitude (common at night, in fog, near fronts), the real pressure correction can differ substantially from what the 6.5 K/km constant predicts.
- **High-humidity environments**: using dry-air molar mass underestimates the correction slightly; significant in tropical boundary layers.
- **Precision aviation/meteorology**: ICAO QNH procedures tolerate this approximation, but scientific reanalysis systems use more sophisticated vertical integration.

For the intended use case — surface weather station normalization below 5000 m in mid-latitudes — the error is typically < 1–2 hPa, which is within observational uncertainty.

---

## Logging

### Strategy

The app uses Python's standard `logging` module, configured once at startup via `logging_config.py` using `dictConfig`. Two handlers run in parallel:

| Handler | Destination | Level | Format |
|---------|-------------|-------|--------|
| `console` | `stderr` | `WARNING` and above | Plain text with timestamp |
| `file` | `logs/nowcastingcli.log` | `DEBUG` and above | JSON (via `python-json-logger`) |

The `logs/` directory is created automatically on first run. The file handler rotates at 1 MB and keeps 3 backups.

### Log levels in use

| Level | Where | What is logged |
|-------|-------|----------------|
| `DEBUG` | `main.py` | Raw sensor input per observation (pressure, temperature, humidity, altitude) |
| `INFO` | `display.py` | Each observation recorded, with `pressure_qnh` and the current verdict |
| `WARNING` | `main.py` | Verdict transitions (e.g. `stable → worsening`) |
| `INFO` | `main.py` | Session start |

### Implementation

`logging_config.py` was built with the following design goals:

- Use the `dictConfig` pattern to declare the full logging topology in one place as a plain dictionary, keeping configuration separate from application code.
- A `RotatingFileHandler` writes JSON-formatted logs to `logs/nowcastingcli.log` at `DEBUG` level, capturing all events for post-session analysis.
- A `StreamHandler` to `stderr` is set to `WARNING` only, so the terminal stays clean during normal operation.
- `setup_logging()` creates the `logs/` directory if it does not exist before applying the config, avoiding a `FileNotFoundError` on first run.

### Wiring

`setup_logging()` is called once in `main.py` before any `getLogger()` call. Other modules (`display.py`, `heuristics.py`) obtain a logger with `logging.getLogger(__name__)` and rely on the handlers already being registered by the time they are imported.

---

## Interactive REPL

```bash
python -i test_scripts/Init_observation.py
```

Executes the script and leaves the interpreter open with all variables defined.
