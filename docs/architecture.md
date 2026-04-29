# Architecture

## Module map

| Module | Responsibility |
|--------|----------------|
| `models.py` | `Observation` dataclass — pure data, no logic |
| `physics.py` | Barometric normalisation (`normalize_pressure`) |
| `heuristics.py` | Condition classification (`assess_conditions`) |
| `display.py` | `rich` dashboard rendering |
| `main.py` | Input loop, orchestration, logging init |
| `logging_config.py` | `dictConfig` setup, `RotatingFileHandler` |

## Data flow

```
User input
    │
    ▼
Observation (models.py)
    │
    ├──► normalize_pressure() → QNH       (physics.py)
    │
    └──► assess_conditions()  → verdict   (heuristics.py)
                │
                ▼
           display.py (rich Panel)
                │
                ▼
           logging_config.py → logs/
```