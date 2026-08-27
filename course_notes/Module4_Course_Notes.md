# Module 4 — Logging: Structured Logs for NowcastingCLI

> Part of: Claude Code for Python Developers: Hands-On Agentic Coding
> Repo: CCPD-nowcastingcli
> See also: [Course_Notes_Index.md](./Course_Notes_Index.md)

---

## Part 4 — Logging: Structured Logs for NowcastingCLI

### Why Logging Not print()

The same motivation as switching from ad-hoc `echo` statements in a Jenkins
pipeline to structured build logs: severity levels, runtime control, and
configurable output destinations — with no code changes to silence or redirect.

| Concern | `print()` | `logging` |
|---|---|---|
| Severity levels | None | DEBUG / INFO / WARNING / ERROR / CRITICAL |
| Silence without code change | Comment out / delete | Set level at runtime |
| Output destination | stdout only | Any handler: file, rotating file, stderr |
| Timestamps / context | Manual | Built into formatter |
| Production vs dev | Same output | Different config, same code |

The key payoff: `logger.debug("raw obs: %s", obs)` is written once.
In dev you see it. In production you filter it out with one config change —
no touching source files.

---

### Logger Hierarchy

Python's logging system is a tree rooted at the **root logger**. Named loggers
are created with `logging.getLogger(__name__)`. In `nowcastingcli/physics.py`,
`__name__` resolves to `nowcastingcli.physics` — automatically a child of
`nowcastingcli`, which is a child of root.

```
root
└── nowcastingcli
    ├── nowcastingcli.main
    ├── nowcastingcli.physics
    ├── nowcastingcli.heuristics
    └── nowcastingcli.display
```

**Key rule:** log records propagate up the tree. Configure handlers on the
package root (`nowcastingcli`) and all child loggers feed into them
automatically. Never configure handlers in leaf modules — only in
`logging_config.py`.

In every module, just:

```python
import logging
logger = logging.getLogger(__name__)
```

No handler setup in library code — ever.

---

### Handlers and Formatters

A **handler** decides *where* a log record goes. A **formatter** decides
*what it looks like*.

```
LogRecord → Logger → Handler → Formatter → Output
```

The three handlers used in this project:

```python
import logging
from logging.handlers import RotatingFileHandler

# Console — stderr so it doesn't pollute rich's stdout
sh = logging.StreamHandler()   # stream defaults to sys.stderr

# Plain file
fh = logging.FileHandler("nowcastingcli.log")

# Rotating file — analogous to Jenkins rolling build logs
rfh = RotatingFileHandler(
    "nowcastingcli.log",
    maxBytes=1_000_000,   # 1 MB per file
    backupCount=3          # keeps .log, .log.1, .log.2, .log.3
)
```

Plain text formatter:

```python
fmt = logging.Formatter(
    fmt="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)
```

---

### dictConfig vs basicConfig

`basicConfig` is fine for a single-handler script. For anything with multiple
handlers, JSON output, or non-trivial level routing, use `dictConfig` —
declarative, readable, and equivalent to what you would put in an external
config file.

```python
# nowcastingcli/logging_config.py
import logging.config

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,   # don't silence third-party loggers
    "formatters": {
        "plain": {
            "format": "%(asctime)s %(levelname)-8s %(name)s — %(message)s",
            "datefmt": "%Y-%m-%dT%H:%M:%S",
        },
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "WARNING",        # only warnings+ to terminal
            "formatter": "plain",
            "stream": "ext://sys.stderr",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",          # everything to the log file
            "formatter": "json",
            "filename": "logs/nowcastingcli.log",
            "maxBytes": 1_000_000,
            "backupCount": 3,
        },
    },
    "loggers": {
        "nowcastingcli": {
            "level": "DEBUG",
            "handlers": ["console", "file"],
            "propagate": False,        # don't double-log to root
        },
    },
}


def setup_logging() -> None:
    import os
    os.makedirs("logs", exist_ok=True)
    logging.config.dictConfig(LOGGING_CONFIG)
```

`disable_existing_loggers: False` is the sane default. Without it, any
third-party library loggers you import get silenced when `dictConfig` runs.

---

### Structured JSON Logging

Plain text is human-readable. JSON logs are machine-parseable — queryable
with `jq`, or ingestible by any log aggregator (Loki, Splunk, etc.).

Install the formatter:

```bash
pip install python-json-logger
```

Add to `pyproject.toml`:

```toml
[project]
dependencies = [
    "rich",
    "python-json-logger",
]
```

With the `dictConfig` above, file logs look like:

```json
{"asctime": "2026-04-22T10:15:00", "levelname": "INFO", "name": "nowcastingcli.main", "message": "Observation recorded", "pressure_qnh": 1012.1, "verdict": "WORSENING"}
```

Pass structured fields via `extra={}`:

```python
logger.info("Observation recorded", extra={
    "pressure_qnh": obs.pressure_qnh,
    "verdict": verdict,
    "reason": reason,
})
```

**Style note:** use `%s` style in log calls, not f-strings.
`logger.debug("val: %s", x)` is lazy — the string is never built if the
level is filtered. `logger.debug(f"val: {x}")` always evaluates the f-string,
even when DEBUG is disabled.

---

### Where to Log in NowcastingCLI

| Location | What to log | Level |
|---|---|---|
| `main.py` — startup | App starting | INFO |
| `main.py` — each obs cycle | Raw inputs received | DEBUG |
| `main.py` — each obs cycle | QNH + verdict (with `extra` fields) | INFO |
| `physics.py` — `normalize_pressure()` | Before each `ValueError` raise | ERROR |
| `heuristics.py` — `assess_conditions()` | When verdict changes | WARNING |
| `main.py` — shutdown | Clean exit | INFO |

---

### Implementation

**Step 1 — Install and update deps**

```bash
pip install python-json-logger
```

Add `python-json-logger` to `[project] dependencies` in `pyproject.toml`.

**Step 2 — Create `nowcastingcli/logging_config.py`**

Use the `dictConfig` + `setup_logging()` from above verbatim.

**Step 3 — Wire into `main.py`**

```python
from nowcastingcli.logging_config import setup_logging
setup_logging()

import logging
logger = logging.getLogger(__name__)

def run() -> None:
    logger.info("NowcastingCLI started")

    # inside the observation loop:
    logger.debug("Raw input received: p=%.1f T=%.1f RH=%.1f alt=%.1f",
                 pressure, temperature, humidity, altitude)

    logger.info("Observation recorded", extra={
        "pressure_qnh": obs.pressure_qnh,
        "verdict": verdict,
        "reason": reason,
    })
```

**Step 4 — Log `ValueError` in `physics.py`**

```python
import logging
logger = logging.getLogger(__name__)

def normalize_pressure(pressure_hpa, altitude_m, temperature_c):
    if pressure_hpa <= 0:
        logger.error("Invalid pressure: %.2f hPa", pressure_hpa)
        raise ValueError(f"pressure_hpa must be positive, got {pressure_hpa}")
    if altitude_m > 5000:
        logger.error("Altitude out of range: %.1f m", altitude_m)
        raise ValueError(f"altitude_m exceeds valid range: got {altitude_m}")
    # ...
```

**Step 5 — Log verdict changes in `heuristics.py`**

```python
import logging
logger = logging.getLogger(__name__)

def assess_conditions(observations):
    # ... compute verdict ...
    if len(observations) >= 2:
        prev_verdict = _previous_verdict(observations)
        if verdict != prev_verdict:
            logger.warning("Verdict changed: %s → %s", prev_verdict, verdict)
    return verdict, reason
```

**Step 6 — `.gitignore` entry**

```
logs/
```

---

### Claude Code Agentic Task

Hand this off to Claude Code in one session:

```
Add structured logging to NowcastingCLI using the dictConfig pattern.

Create nowcastingcli/logging_config.py with:
- A RotatingFileHandler writing JSON logs to logs/nowcastingcli.log (DEBUG level)
- A StreamHandler to stderr (WARNING level only)
- setup_logging() that creates the logs/ directory if missing

Then add logging to:
- main.py: INFO on startup, DEBUG on raw inputs, INFO with extra fields on each observation
- physics.py: ERROR before each ValueError raise
- heuristics.py: WARNING when the verdict changes between consecutive observations

Use logging.getLogger(__name__) in every module. Do not configure handlers in
any module other than logging_config.py. Use %s style formatting, not f-strings,
in all log calls. Run pytest after changes to confirm no regressions.
```

**Review checklist for Claude Code's output:**

- Handler setup only in `logging_config.py` — nowhere else
- `%s` style used in all log calls, not f-strings
- `logs/` added to `.gitignore`
- `pytest` passes clean after changes

---

### Verifying Output

```bash
nowcastingcli        # enter 3 observations, then quit
cat logs/nowcastingcli.log | python -m json.tool | head -30
```

With `jq`:

```bash
cat logs/nowcastingcli.log | jq '{t: .asctime, level: .levelname, msg: .message}'
```

---

### Exercise Checklist

- [ ] `pip install python-json-logger`, add to `pyproject.toml` dependencies
- [ ] Create `nowcastingcli/logging_config.py` with `dictConfig` + `setup_logging()`
- [ ] Add `logs/` to `.gitignore`
- [ ] Wire `setup_logging()` into `main.py` before any other code runs
- [ ] Add `logger = logging.getLogger(__name__)` in `main.py`, `physics.py`, `heuristics.py`
- [ ] Add log calls at the locations listed in the table above
- [ ] Run the app, enter 3 observations, inspect `logs/nowcastingcli.log` with `jq` or `python -m json.tool`
- [ ] Run `pytest` — all green
- [ ] Commit: `git commit -m "feat: add structured JSON logging with RotatingFileHandler"`

---

---

