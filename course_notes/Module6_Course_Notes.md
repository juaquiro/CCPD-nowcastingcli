# Module 6 — Build, Packaging, and Manual Delivery

> Part of: Claude Code for Python Developers: Hands-On Agentic Coding
> Project: NowcastingCLI (`CCPD-nowcastingcli`)
> Prerequisite for: Module 7 (CI/CD) — CI automates exactly the manual steps here.

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

```toml
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "nowcasting-cli"
version = "0.6.0"
description = "Terminal-based weather nowcasting CLI dashboard"
requires-python = ">=3.10"
dependencies = [
    "rich>=13.0",
]

[project.scripts]
nowcast = "nowcastingcli.main:app"
```

- `[build-system]` tells `pip`/`build` *how* to build (analogous to
  specifying which build tool NAnt invokes — here it's `setuptools`, but
  `hatchling` or `flit_core` are common alternatives; NowcastingCLI stays on
  `setuptools` since Module 1 already used it).
- `[project.scripts]` is what gives you the `nowcast` command after install
  — this is the packaging equivalent of registering an entry point.

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
  nowcasting_cli-0.6.0-py3-none-any.whl
  nowcasting_cli-0.6.0.tar.gz
```

| Artifact | Contents | Use |
|---|---|---|
| **wheel** (`.whl`) | Pre-built, ready to `pip install` | Fast install, what most users get |
| **sdist** (`.tar.gz`) | Source + `pyproject.toml`, built on install | Needed if wheel isn't compatible with target platform, or for PyPI's index requirements (PyPI wants both) |

For a pure-Python project like NowcastingCLI, the wheel is platform-agnostic
(`py3-none-any`) — no compiled extensions, no per-OS builds needed. This is
the simple case; fringeDemod (Project 2) may pull in NumPy/compiled deps
later, worth revisiting the wheel story then.

---

## 3. Version Source of Truth

**Single source: `version` in `pyproject.toml`.** Do not duplicate the
version string in code, `CLAUDE.md`, or docs — Module 7's auto-tagging
reads this field directly.

```python
# nowcastingcli/__init__.py — read it back, don't hardcode a second copy
from importlib.metadata import version
__version__ = version("nowcasting-cli")
```

This is the same discipline as keeping a single `<Version>` node in an
`.nuspec`/AssemblyInfo rather than scattering the version string — one
place to bump, everything else reads from it.

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
pip install --index-url https://test.pypi.org/simple/ nowcasting-cli
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
  name: nowcasting-cli
  version: "0.6.0"
source:
  path: ..
build:
  script: pip install . --no-deps
requirements:
  host: [python, pip, setuptools]
  run: [python, rich]
```

---

## 6. Manual Delivery Path 3 — Local/Editable Install on Another Machine

For a colleague or another of your own machines, no index needed:

```bash
# Option A — from built wheel (no repo access needed)
pip install nowcasting_cli-0.6.0-py3-none-any.whl

# Option B — from source, editable (for development on that machine)
git clone https://github.com/<you>/CCPD-nowcastingcli.git
cd CCPD-nowcastingcli
conda create -n nowcasting-cli python=3.11
conda activate nowcasting-cli
pip install -e .
```

Option A is the "standalone package ready for installation on another
machine" deliverable — copy the `.whl`, no git, no PyPI account needed.

---

## 7. Standalone Package Checklist

A build is genuinely ready for another machine when:

- [ ] `pip install dist/*.whl` succeeds in a **fresh** conda env (no leftover
      dev dependencies masking a missing runtime dependency)
- [ ] `nowcast` command is on `PATH` after install and runs
- [ ] `dependencies` in `pyproject.toml` lists everything actually imported
      at runtime (not dev-only tools like `pytest`, `mkdocs`)
- [ ] Version in the built wheel filename matches `pyproject.toml`
- [ ] sdist also builds cleanly (`pip install dist/*.tar.gz` in a separate
      fresh env) — catches missing `MANIFEST.in`/packaging data issues that
      only show up when building from source

---

## Exercise Checklist

- [ ] Add `[project.scripts]` entry point to NowcastingCLI's `pyproject.toml`
- [ ] Run `python -m build`, inspect `dist/` contents
- [ ] Install the wheel into a fresh conda env, verify `nowcast` runs
- [ ] Upload to TestPyPI manually with `twine`, install from TestPyPI into
      a second fresh env
- [ ] Confirm `__version__` resolves via `importlib.metadata.version()`
      rather than a hardcoded string
