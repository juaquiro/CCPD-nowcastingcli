# NowcastingCLI — Usage Guide

## Starting the app

```bash
conda activate nowcastingcli
nowcastingcli
```

On launch the app prints a header and enters the input loop:

```
NowcastingCLI v1.0 — type 'q' at any prompt to quit
```

---

## Input loop

Each iteration of the loop collects one observation. The app prompts for four
fields in sequence:

```
Enter pressure (hPa), 'e' to edit a past reading, or 'q' to quit: 1013
Temperature (°C): 18
Relative Humidity (%): 60
GPS Altitude (m): 340
```

After all four values are accepted the dashboard is redrawn with the new row
appended.

### Special commands at the pressure prompt

| Input | Action |
|-------|--------|
| `q` | End the session — prints "Session ended." and exits |
| `e` | Open the edit menu for a past observation (see [Editing a past observation](#editing-a-past-observation)) |
| Any number | Treated as the raw station pressure in hPa and continues the loop |

`Ctrl+C` and `Ctrl+D` (EOF) are also handled gracefully and end the session.

### Validation and retry

Every field is validated before the loop advances. If a value is out of range
or non-numeric the app prints an inline error and re-prompts the same field —
no observation is recorded until all four values are accepted:

```
Value must be between 0.1 and 1100.0
Enter pressure (hPa), 'e' to edit a past reading, or 'q' to quit:
```

---

## Valid input ranges

These ranges are enforced in both interactive mode and CSV file mode.

| Field | Unit | Valid range | Notes |
|-------|------|-------------|-------|
| `pressure_hpa` | hPa | 0.1 – 1100.0 | Raw station pressure as measured by the sensor |
| `temperature_c` | °C | -60 – 60 | Ambient air temperature at the station |
| `humidity_pct` | % | 0 – 100 | Relative humidity |
| `altitude_m` | m | -500 – 5000 | GPS altitude above sea level; upper limit is the ISA troposphere model boundary |

The altitude ceiling of 5000 m is a hard limit of the barometric formula used
to compute QNH. Inputs above that value raise a `ValueError` in `physics.py`.

---

## What the dashboard shows

After every observation the terminal is cleared and the dashboard is redrawn.
It has two sections: the observation table and the nowcast panel.

### Observation table

One row per observation, columns left to right:

| Column | Content |
|--------|---------|
| **Time** | Wall-clock time the observation was recorded (`HH:MM`) |
| **Raw (hPa)** | Raw station pressure as entered, in hPa |
| **QNH (hPa)** | Pressure normalised to sea level via the barometric formula, in hPa, with a trend arrow (↑ ↓ →) relative to the previous row |
| **Temp** | Temperature in °C with a trend arrow |
| **RH** | Relative humidity in % with a trend arrow |
| **Alt** | GPS altitude in m |

Trend arrows compare each value to the immediately preceding observation:
`↑` rise above 0.1, `↓` fall below −0.1, `→` change within ±0.1.
The first row always shows `→` (no prior reading to compare against).

### Nowcast panel

Below the table a bordered panel shows three lines:

```
Pressure trend:  ▁▃▇  (−3.2 hPa over session)

Nowcast:  🔴 CONDITIONS WORSENING
Reason:   Rapid pressure fall (−1.7 hPa) + High humidity (86%)
```

| Element | Description |
|---------|-------------|
| **Pressure trend sparkline** | Unicode block characters (▁▂▃▄▅▆▇█) mapping the min–max QNH range across all observations in the session, followed by the total delta since the first reading |
| **Nowcast verdict** | One of three states (see below) |
| **Reason** | Human-readable explanation of why that verdict was assigned |

### Verdict logic

The verdict is derived by comparing the last two observations.

| Verdict | Condition |
|---------|-----------|
| 🔴 CONDITIONS WORSENING | QNH dropped more than **1.0 hPa** since the previous reading, **and/or** current humidity exceeds **85 %** |
| 🟢 CONDITIONS IMPROVING | QNH rose more than **1.0 hPa** since the previous reading **and** humidity is falling |
| 🟡 CONDITIONS STABLE | Neither worsening nor improving condition is met |

With fewer than two observations the verdict is always STABLE with the note
"Insufficient data — enter at least one more reading".

When the verdict transitions between states (e.g. STABLE → WORSENING) a
`WARNING` log entry is written to `logs/nowcastingcli.log`.

---

## Editing a past observation

Type `e` at the pressure prompt to open the edit menu. The app lists all
recorded observations numbered from 1:

```
  [1] 10:02  1013.0 hPa  18°C  60%  340m
  [2] 10:15  1011.5 hPa  17°C  72%  340m
Select observation to edit (number): 2
Field: [1] pressure  [2] temperature  [3] humidity  [4] altitude
Field to edit: 1
New pressure (hPa): 1010.0
```

After the edit the dashboard is redrawn immediately. If the changed field is
pressure, temperature, or altitude the QNH value is automatically re-derived
from the updated inputs via the barometric formula. Editing humidity alone does
not recalculate QNH.

---

## File input mode

Pass a CSV file with `--input` to run the session non-interactively:

```bash
nowcastingcli --input scripts/test_observations.csv
```

The file must contain exactly these four columns (order matters, header required):

```csv
pressure_hpa,temperature_c,humidity_pct,altitude_m
1013,18,60,340
1011.5,17,72,340
1009.8,17,86,340
```

All rows are validated before any observation is recorded. A descriptive error
is printed and the session exits if any row is invalid:

```
Input file error: Row 3: temperature = 99.0 out of range [-60, 60]
```

The same dashboard renders after each row, identical to interactive mode.

---

## Logging smoke-test scripts

Two scripts in `scripts/` run `test_observations.csv` through the CLI and then
pretty-print the JSON log to verify that events were written in the correct order.

**Bash (Git Bash / Linux / macOS):**

```bash
bash scripts/test_logging.sh
```

**Windows CMD:**

```bat
scripts\test_logging.bat
```

Expected log events per observation cycle, in order:

| Level | Source | Event |
|-------|--------|-------|
| `INFO` | `main` | Session start (once, on startup) |
| `DEBUG` | `main` | Raw sensor input — pressure, temperature, humidity, altitude |
| `INFO` | `display` | Observation recorded — includes `pressure_qnh` and current verdict as structured JSON fields |
| `WARNING` | `main` | Verdict changed (only when the verdict transitions between states) |

Log files are written to `logs/nowcastingcli.log` (auto-created on first run,
rotates at 1 MB, keeps 3 backups). The console only shows `WARNING` and above
so normal operation stays clean.
