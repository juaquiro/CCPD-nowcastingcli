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