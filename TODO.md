# NowcastingCLI — Pending Improvements

## Done
- [x] **#1** Fix unhandled `ValueError` on bad pressure input in `main.py` — pressure now goes through `get_float` with bounds validation

## Pending

- [ ] **#2** **Fix `pytest.approx` used backwards in `test_known_value_burgos`**
  `test_physics.py:49` wraps the actual value instead of the expected.
  Change to: `assert qnh == pytest.approx(1052.0, abs=2.0)`

- [ ] **#3** **Translate Spanish error messages in `models.py` to English**
  `__post_init__` raises `ValueError` with `"humidity fuera de rango"` and `"pressure inválida"`.

- [ ] **#4** **Fix hardcoded `"stable"` string in `VERDICT_STYLE` dict (`display.py`)**
  Import the `STABLE` constant from `heuristics` and use it as the dict key instead of the bare string.

- [ ] **#5** **Move `__str__` display logic out of `models.py` into `display.py`**
  CLAUDE.md requires `models.py` to contain only dataclasses with no logic.

- [ ] **#6** **Extract magic number thresholds in `heuristics.py` to named constants**
  The inline literals `-1.0` hPa and `85`% in `assess_conditions` should become
  `PRESSURE_FALL_THRESHOLD` and `HIGH_HUMIDITY_THRESHOLD`.

- [ ] **#7** **Add type hints and docstring to `get_float` in `main.py`**
  Public function missing return type hint and docstring (CLAUDE.md convention).

- [ ] **#8** **Move `units` dict out of `Observation` to a module-level constant**
  The dict is identical for every instance — no need to allocate it per `Observation`.

- [ ] **#9** **Allow editing observations once recorded**
  After the dashboard renders, let the user select a past observation by index and
  correct any field. Re-derive `pressure_qnh` after edits and re-render.
