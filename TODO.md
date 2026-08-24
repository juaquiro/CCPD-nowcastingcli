# NowcastingCLI — Pending Improvements

## Done

- [x] **#1** Fix unhandled ValueError on bad pressure input in main.py
- [x] **#2** Fix pytest.approx used backwards in test_known_value_burgos
- [x] **#3** Translate Spanish error messages in models.py to English
- [x] **#4** Fix hardcoded "stable" string in VERDICT_STYLE dict in display.py
- [x] **#5** Move __str__ display logic out of models.py into display.py
- [x] **#6** Extract magic number thresholds in heuristics.py to named constants
- [x] **#7** Add type hints and docstring to get_float in main.py
- [x] **#8** Move units dict out of Observation to a module-level constant
- [x] **#9** Allow deleting/editing observations once recorded
- [x] **#10** Remove units instance field from Observation
- [x] **#11** Fix DEBUG log order in main.py
- [x] **#12** Increase main.py test coverage to >= 80%
- [x] **#13** Show raw pressure alongside QNH in the dashboard table
  `render_dashboard` in `display.py` now shows a `Pressure(raw)` column
  alongside `pressure_qnh`, so the user can see the uncorrected station
  reading next to the sea-level value.

## Pending

- [ ] **#14** Change logging to store raw measurements together with timestamp and corrected pressure at sea level
  `_record_observation` in `main.py` currently logs only the raw inputs
  (`p`, `T`, `RH`, `alt`) via `logger.debug(...)` before normalization.
  Update the log entry to also include the observation `timestamp` and
  the computed `pressure_qnh`, so the log file captures the same data
  as the in-memory `Observation` record.
