# NowcastingCLI — Pending Improvements

## Done

- [x] task #1 **Fix DEBUG log order in `main.py`** — moved `logger.debug(...)` to immediately after inputs are collected, before `normalize_pressure` and observation construction.

## Pending

- [x] task #2 **Increase `main.py` test coverage to ≥ 80%** — current coverage is 71% (41 missed statements). New code paths to cover: `_parse_csv()` validation errors (missing columns, non-numeric values, out-of-range fields, empty file), `cli()` entry point, `_record_observation()` verdict-change warning branch, and the `--input` file mode path through `run()`.
