# Claude Code for Python Developers — Course Notes

> **Course:** Claude Code for Python Developers: Hands-On Agentic Coding
> **Repo:** CCPD-nowcastingcli
> **Last updated:** 2026-04-15

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

*Notes will be extended as each module is completed.*
