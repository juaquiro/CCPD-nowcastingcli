# NowcastingCLI — Claude Code Instructions

## Environment

- conda env: `nowcastingcli` (Python 3.11)
- activate before running: `conda activate nowcastingcli`
- run tests: `pytest`
- run app: `nowcastingcli`

## Code Conventions

- Type hints on all public functions
- Docstrings on all public functions (single-line for simple, multi-line for complex)
- Named constants for magic numbers in physics.py
- No print() — use rich console for all output

## Architecture Notes

- models.py: only dataclasses, no logic
- physics.py: pure functions only, no I/O
- heuristics.py: pure functions only, depends only on models.py
- display.py: all rich rendering lives here, single Console() instance
- main.py: orchestration only, thin layer over the others

## Test Conventions

- pytest.approx for all float comparisons
- parametrize for table-driven tests
- test file mirrors source file: test_physics.py tests physics.py

## Last Session (2026-09-02)

Status: completed (packaging docs) — see `SESSION_SUMMARY.md` for full
detail. Issue #14 below is still **pending**, carried over untouched.

- Added PyInstaller standalone `.exe` packaging: `launcher.py` (absolute-
  import entry point, works around PyInstaller's relative-import failure)
  and `nowcastingcli.spec` (build config, force-added past the repo's
  `*.spec` gitignore rule via a permanent `!nowcastingcli.spec` exception).
  `hiddenimports=['pythonjsonlogger.json']` is required because
  `logging_config.py` references it as a string inside `dictConfig()`,
  invisible to PyInstaller's static import scan.
- Bumped `pyproject.toml` to its verified `0.6.0` state (`build-system`
  requires `setuptools>=68`+`wheel`; `version` `0.1.0` → `0.6.0`).
- Cleaned up `nowcastingcli/__init__.py`'s docstring/comments; added a
  "Building a Distributable Package" summary table to `README.md`; filled
  out `course_notes/Module6_Course_Notes.md` in full.
- Committed and pushed to `develop` (`ada2feb`, `cb569c7`).
- Not fixed, flagged only: `.gitignore`'s trailing `site/` entry is
  UTF-16LE-encoded while the rest of the file is UTF-8 (likely from a
  Windows PowerShell `Out-File`/`Set-Content` without `-Encoding utf8`).

Next session should start by implementing issue #14 in
`main.py::_record_observation` (unchanged priority from the prior
session).
