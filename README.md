# NowcastingCLI

A terminal-based weather nowcasting CLI built with Python.

## Project Structure

```
NOWCASTINGCLI/
├── nowcastingcli/
│   ├── __init__.py
│   └── models.py
├── test_scripts/
│   └── Init_observation.py
├── pyproject.toml
└── README.md
```

## Setup

### 1. Create and activate the conda environment

```bash
conda create -n nowcastingcli python=3.11
conda activate nowcastingcli
```

### 2. Install setuptools and other packages

```bash
pip install rich
conda install setuptools -c conda-forge
```

### 3. Install the package in editable mode

From the project root (`NOWCASTINGCLI/`):

```bash
pip install -e .
```

This registers the `nowcastingcli` package in the conda environment so imports
work correctly from any script or REPL, without `sys.path` hacks.

---

## `pyproject.toml`

The project requires the following `pyproject.toml` at the root:

```toml
[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"

[project]
name = "nowcastingcli"
version = "0.1.0"

[tool.setuptools.packages.find]
include = ["nowcastingcli*"]
```

> The `include` directive tells setuptools to package only `nowcastingcli/`
> and ignore `test_scripts/`.

---

## Running scripts from VS Code

Once the package is installed in editable mode, the VS Code **▶ play button**
works directly on any script — no `launch.json` configuration needed.

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
    altitude     = 667.0
)

print(obs)
```

---

## Interactive REPL

To explore the package interactively, launch Python from the project root:

```bash
python
```

Or use a setup script with the `-i` flag to pre-load variables:

```bash
python -i test_scripts/Init_observation.py
```

This executes the script and leaves the interpreter open with all variables
already defined.