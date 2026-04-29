# NowcastingCLI — Pending Improvements

## Done

## Pending

- [x] **#11** **Show raw pressure alongside QNH in the dashboard table**
  `render_dashboard` in `display.py` currently shows only `pressure_qnh`.
  Add a `Pressure(raw)` column (or combine into one cell, e.g. `1013.2 / 1015.8 hPa`)
  so the user can see the uncorrected station reading next to the sea-level value.
