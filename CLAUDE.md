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

## Last Session (2026-08-24)

Status: in progress — see `SESSION_SUMMARY.md` for full detail.

- Synced `TODO.md` with GitHub issues (all 13 prior issues closed);
  committed and pushed (`0be428f`).
- Opened GitHub issue **#14**: log entries should carry `timestamp` and
  `pressure_qnh`, not just the raw inputs. Tracked in `TODO.md`,
  **not yet implemented**.
- Moved `pytest`, `pytest-cov`, `setuptools`, `wheel` from
  `[project] dependencies` to a new `[project.optional-dependencies].dev`
  group in `pyproject.toml`; committed and pushed (`2c66a07`). Full
  install command: `pip install -e ".[docs,dev]"`.
- `README.md` / `COURSE_NOTES.md` were updated to document the `dev`
  extra and combined install command; committed and pushed (`591668b`).

Next session should start by implementing issue #14 in
`main.py::_record_observation`.
