# NowcastingCLI

A terminal-based weather nowcasting CLI built with Python and [Rich](https://github.com/Textualize/rich).

---

## Project Structure

```
NOWCASTINGCLI/
├── nowcastingcli/
│   ├── __init__.py        # package marker
│   ├── main.py            # CLI entry point — run() function
│   ├── models.py          # Observation dataclass
│   ├── physics.py         # barometric QNH normalisation
│   ├── heuristics.py      # worsening / stable / improving logic
│   └── display.py         # Rich dashboard, sparkline, trend arrows
├── test_scripts/
│   └── Init_observation.py
├── pyproject.toml
└── README.md
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
```

The `[project.scripts]` block registers the `nowcastingcli` command so it is
available anywhere in the active environment after installation.

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

## Interactive REPL

```bash
python -i test_scripts/Init_observation.py
```

Executes the script and leaves the interpreter open with all variables defined.
