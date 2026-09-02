# Module 6 — Build, Packaging, and Manual Delivery

> Part of: Claude Code for Python Developers: Hands-On Agentic Coding
> Project: NowcastingCLI (`CCPD-nowcastingcli`)
> Prerequisite for: Module 7 (CI/CD) — CI automates exactly the manual steps here.
> **Status: hands-on completed and verified** (fresh-env wheel install, fresh-env
> sdist install, and standalone `.exe` all tested and passing).

**Repo state note:** at the close of this module, the current single
branch will be renamed `develop`, and a new `main` branch will be created
from it as the stable/release branch. Nothing in this module's build steps
is branch-dependent — build/package/publish commands run identically
regardless of branch — but this rename is the setup Module 7's branch
model (`develop` = integration, `main` = release) assumes as its starting
point.

---

## 1. Build Backends and `pyproject.toml`

Everything in this module runs through the build backend declared in
`pyproject.toml`. NowcastingCLI already has one from Module 1 (editable
install); this module completes the picture for a **distributable** build.

**Actual verified state** (package name and entry point as they exist in
the repo — not `nowcasting-cli`/`nowcast` as originally drafted):

```toml
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "nowcastingcli"
version = "0.6.0"
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
    "mkdocs>=1.5,<2.0",
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

- `[build-system]` tells `pip`/`build` *how* to build (analogous to
  specifying which build tool NAnt invokes — here it's `setuptools`, but
  `hatchling` or `flit_core` are common alternatives; NowcastingCLI stays on
  `setuptools` since Module 1 already used it).
- `[project.scripts]` is what gives you the `nowcastingcli` command after
  install — this is the packaging equivalent of registering an entry point.
  (Command name kept as `nowcastingcli`, matching the package name, rather
  than shortening to `nowcast` — deliberate choice, not a default.)

**Opinionated note:** `setuptools` is the safe default (universal support,
what Module 1 already used). `hatchling` is lighter-weight and increasingly
common for new projects but not necessary to switch to here.

---

## 2. `python -m build`: Wheel vs sdist

```bash
conda activate nowcasting-cli
pip install build --break-system-packages   # not needed inside conda env, shown for completeness
python -m build
```

Produces `dist/`:
```
dist/
  nowcastingcli-0.6.0-py3-none-any.whl
  nowcastingcli-0.6.0.tar.gz
```

| Artifact | Contents | Use |
|---|---|---|
| **wheel** (`.whl`) | Pre-built, ready to `pip install` | Fast install, what most users get |
| **sdist** (`.tar.gz`) | Source + `pyproject.toml`, built on install | Needed if wheel isn't compatible with target platform, or for PyPI's index requirements (PyPI wants both) |

For a pure-Python project like NowcastingCLI, the wheel is platform-agnostic
(`py3-none-any`) — no compiled extensions, no per-OS builds needed. This is
the simple case; fringeDemod (Project 2) may pull in NumPy/compiled deps
later, worth revisiting the wheel story then.

**Verified:** both artifacts built cleanly with names/version matching
`pyproject.toml` exactly.

---

## 3. Version Source of Truth

**Single source: `version` in `pyproject.toml`.** Do not duplicate the
version string in code, `CLAUDE.md`, or docs — Module 7's auto-tagging
reads this field directly.

```python
# nowcastingcli/__init__.py — read it back, don't hardcode a second copy
from importlib.metadata import version

__version__ = version("nowcastingcli")
```

Note the string passed to `version()` must match `[project] name` exactly
(`"nowcastingcli"`, not a module path). This only resolves once the package
is actually installed — editable install (Module 1) or a real install both
satisfy this.

This is the same discipline as keeping a single `<Version>` node in an
`.nuspec`/AssemblyInfo rather than scattering the version string — one
place to bump, everything else reads from it.

**Verified:** confirmed `__version__` resolves to `0.6.0` both via editable
install (`pip install -e .`) and via a real install from the built wheel in
a fresh conda env.

---

## 4. Manual Delivery Path 1 — TestPyPI / PyPI

**Trusted Publishing (recommended, no stored secrets):**
GitHub Actions authenticates to PyPI via short-lived OIDC tokens — no API
key stored anywhere, configured once on pypi.org against your repo. This is
what Module 7's `build-and-publish` job uses.

**Token-based upload (manual, for this module):**
```bash
pip install twine --break-system-packages
python -m twine upload --repository testpypi dist/*
# then, once verified:
python -m twine upload dist/*
```
Requires an API token from TestPyPI/PyPI stored in `~/.pypirc` or passed via
env var — acceptable for manual/local publishing, but this is exactly the
secret-management burden Trusted Publishing removes once CI takes over.

**Install from TestPyPI to verify:**
```bash
pip install --index-url https://test.pypi.org/simple/ nowcastingcli
```

---

## 5. Manual Delivery Path 2 — conda packaging

Not used for NowcastingCLI's primary distribution (PyPI is simpler here,
no compiled/Qt dependencies yet), but worth knowing as the alternative —
this becomes the *preferred* path in Project 2 Module 3 (fringeDemod-qt),
where Qt's dependency management makes conda meaningfully better than pip.

Minimal `meta.yaml` sketch (conda-build), for reference — not built out
in this module:
```yaml
package:
  name: nowcastingcli
  version: "0.6.0"
source:
  path: ..
build:
  script: pip install . --no-deps
requirements:
  host: [python, pip, setuptools]
  run: [python, rich, python-json-logger]
```

---

## 6. Manual Delivery Path 3 — Local/Editable Install on Another Machine

For a colleague or another of your own machines, no index needed:

```bash
# Option A — from built wheel (no repo access needed)
pip install nowcastingcli-0.6.0-py3-none-any.whl

# Option B — from source, editable (for development on that machine)
git clone https://github.com/<you>/CCPD-nowcastingcli.git
cd CCPD-nowcastingcli
conda create -n nowcasting-cli python=3.11
conda activate nowcasting-cli
pip install -e .
```

Option A is the "standalone package ready for installation on another
machine" deliverable — copy the `.whl`, no git, no PyPI account needed.
Requires the target machine to have Python + pip (via conda or otherwise)
already set up. For a target with **no Python at all**, see Path 4 below.

---

## 7. Manual Delivery Path 4 — Standalone `.exe` (PyInstaller)

**Different model from Paths 1–3.** Wheel/sdist/conda all assume the target
machine has a Python interpreter and `pip`. PyInstaller instead bundles the
interpreter *and* all dependencies into a single executable — the target
needs nothing pre-installed. Closest .NET-world analogy: a self-contained
publish that ships the runtime with the app, rather than assuming the
runtime is already present (vs. a framework-dependent deployment, which is
closer to what wheel/pip installs are).

This is **not** part of the PyPI publishing pipeline — the `.exe` is
distributed directly (zip it, attach to a GitHub Release, hand it to a
colleague on a USB stick), never uploaded to PyPI/TestPyPI.

### 7.1 Two problems PyInstaller hits with this project, and their fixes

**Problem 1 — relative imports break when pointing PyInstaller at the raw
file.** Running `pyinstaller nowcastingcli/main.py` directly executes
`main.py` as a top-level script, stripping its package context — any
relative import (`from . import ...`) inside `main.py` then fails with
`ImportError: attempted relative import with no known parent package`.

**Fix:** build against a small launcher script at the repo root (not inside
the `nowcastingcli/` package) that imports the entry point absolutely:

```python
# launcher.py — repo root, alongside pyproject.toml
from nowcastingcli.main import cli

if __name__ == "__main__":
    cli()
```

This works because `launcher.py` isn't part of the package itself — it does
a normal absolute import, which only requires `nowcastingcli` to be
importable (it is, since it's installed in the active env). PyInstaller then
discovers the full package by walking that import.

**Problem 2 — dynamically-resolved imports aren't auto-detected.**
PyInstaller builds its dependency list by statically scanning `import`
statements. `logging_config.py` in this project configures a JSON log
formatter via `logging.config.dictConfig()`, referencing
`pythonjsonlogger.json.JsonFormatter` as a **string**, resolved at runtime
by `logging.config` — not a direct `import python_json_logger` PyInstaller
can see. Result: `ModuleNotFoundError: No module named 'pythonjsonlogger'`
at runtime, even though it's correctly listed in `dependencies` and the
wheel/sdist installs work fine.

Same class of problem as reflection-based assembly loading breaking a naive
ILMerge — anything resolved dynamically by name needs to be declared
explicitly to the bundler.

**Fix:** declare it as a hidden import:

```bash
pyinstaller --onefile --name nowcastingcli --distpath dist-exe \
    --hidden-import pythonjsonlogger.json launcher.py
```

If a future dependency has the same dynamic-resolution pattern, stack
additional `--hidden-import` flags (or add to the `.spec` file — see below).

### 7.2 Build commands

```bash
conda activate nowcasting-cli
pip install pyinstaller
pyinstaller --onefile --name nowcastingcli --distpath dist-exe \
    --hidden-import pythonjsonlogger.json launcher.py
```

- `--onefile` bundles everything into a single `.exe` (slower startup,
  simplest to distribute). `--onedir` (the default without `--onefile`) is
  a folder of files instead — faster startup, still just one thing to zip.
- `--distpath dist-exe` keeps output out of `dist/`, which is reserved for
  the wheel/sdist from `python -m build` (Path 1–3). Don't let these
  collide.
- Also generates a `build/` scratch folder (PyInstaller's own — unrelated
  to `python -m build`'s output) and a `.spec` file at the repo root.

### 7.3 The `.spec` file

Every `pyinstaller` invocation writes a `.spec` file named after `--name`
— in this case `nowcastingcli.spec` — to the working directory. It's a
Python file capturing every option passed on the command line, the same
role a `.nuspec`/build script plays in capturing target parameters so you
don't retype them.

Once it exists, rebuild with just:

```bash
pyinstaller nowcastingcli.spec
```

No more repeating `--onefile --name ... --hidden-import ...` — it's all in
the file. The relevant block:

```python
a = Analysis(
    ['launcher.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['pythonjsonlogger.json'],
    ...
)
```

Add future hidden imports directly to this list rather than accumulating
CLI flags. `--onefile` and `--distpath` are also baked in further down (look
for a single `EXE(...)` call with no separate `COLLECT()` step — that's the
onefile signature; switching to `--onedir` later means restoring a
`COLLECT()` step, not something to hand-edit casually).

### 7.4 Repo hygiene

- **Commit** `launcher.py` and `nowcastingcli.spec` — both are reusable
  build configuration, not generated output.
- **Gitignore** `dist-exe/` and PyInstaller's `build/` — generated
  artifacts, rebuildable from the `.spec` file at any time.

```gitignore
# PyInstaller
dist-exe/
build/
*.spec.bak
```
(Do **not** gitignore `nowcastingcli.spec` itself — only add wildcard
backup patterns if your editor generates them.)

### 7.5 Verification

Test in a directory/environment with **no Python or conda active on
PATH** — that's the actual claim being verified ("runs with zero Python
installed"). Two ways to get a genuinely clean test, in increasing order
of rigor:

**Option 1 — clean `cmd` window, same user account:**

```
Win+R → cmd
```

This opens `cmd.exe` without inheriting VS Code's/your shell profile's
conda initialization. Confirm no env is active before testing:

```bash
conda info --envs
```

Look for the `*` marker — it should be on `base` at most, ideally conda
isn't even initialized in this shell at all (no `*` shown, `conda` command
not found). Then run the `.exe` from this window. This catches "works only
because my terminal happens to have PATH set up right" but does **not**
prove the target machine lacks Python entirely — conda/Python may still be
installed system-wide, just not active in this particular shell.

**Option 2 — different Windows user account, no conda/Python installed:**

Log in as (or switch to, via Fast User Switching) a separate local Windows
account that has never had conda or Python installed. Open `cmd` there and
run the `.exe` directly. This is the rigorous version — it proves the
`.exe` is genuinely self-contained, not just "not currently active in this
shell." Closest to what an actual non-technical recipient's machine looks
like.

```bash
dist-exe\nowcastingcli.exe
```

(Copy the `.exe` — not the whole `dist-exe` folder or repo — to a location
the second user account can reach, e.g. a shared `Downloads` folder or a
USB drive, to keep the test honest: no accidental fallback to a
repo-adjacent Python environment.)

**Verified:** builds and runs cleanly after both fixes above (launcher
script for the import-context issue, `--hidden-import` for the dynamic
JSON-formatter resolution), tested via Option 1.

---

## 8. Standalone Package Checklist

A build is genuinely ready for another machine when:

- [x] `pip install dist/*.whl` succeeds in a **fresh** conda env (no leftover
      dev dependencies masking a missing runtime dependency)
- [x] `nowcastingcli` command is on `PATH` after install and runs
- [x] `dependencies` in `pyproject.toml` lists everything actually imported
      at runtime (not dev-only tools like `pytest`, `mkdocs`)
- [x] Version in the built wheel filename matches `pyproject.toml`
- [x] sdist also builds cleanly (`pip install dist/*.tar.gz` in a separate
      fresh env) — catches missing `MANIFEST.in`/packaging data issues that
      only show up when building from source
- [x] (Optional path) Standalone `.exe` built via PyInstaller runs cleanly
      on a machine/env with no Python installed

---

## Exercise Checklist

- [x] Add `[project.scripts]` entry point to NowcastingCLI's `pyproject.toml`
- [x] Run `python -m build`, inspect `dist/` contents
- [x] Install the wheel into a fresh conda env, verify `nowcastingcli` runs
- [ ] Upload to TestPyPI manually with `twine`, install from TestPyPI into
      a second fresh env
- [x] Confirm `__version__` resolves via `importlib.metadata.version()`
      rather than a hardcoded string
- [x] (Extra) Build and verify a standalone `.exe` via PyInstaller as an
      alternative delivery path for machines without Python installed