import argparse
import csv
from dataclasses import dataclass
from datetime import datetime
from rich.prompt import Prompt

from .models import Observation
from .physics import normalize_pressure
from .display import render_dashboard, console
from .heuristics import assess_conditions

# Must be called before any getLogger() — wires up file+console handlers via dictConfig.
from nowcastingcli.logging_config import setup_logging
setup_logging()
import logging
logger = logging.getLogger(__name__)

CSV_COLUMNS   = ["pressure_hpa", "temperature_c", "humidity_pct", "altitude_m"]
PRESSURE_RANGE = (0.1,  1100.0)
TEMP_RANGE     = (-60,    60.0)
HUMIDITY_RANGE = (0.0,   100.0)
ALTITUDE_RANGE = (-500, 5000.0)


@dataclass
class _InputRow:
    pressure:    float
    temperature: float
    humidity:    float
    altitude:    float


def _parse_csv(path: str) -> list[_InputRow]:
    """Read and validate observations from a CSV file.

    Raises ValueError with a descriptive message on missing columns,
    non-numeric values, or out-of-range fields.
    """
    rows: list[_InputRow] = []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)

        missing = [c for c in CSV_COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"CSV missing columns: {missing}. Expected: {CSV_COLUMNS}")

        for line_num, row in enumerate(reader, start=2):
            try:
                pressure    = float(row["pressure_hpa"])
                temperature = float(row["temperature_c"])
                humidity    = float(row["humidity_pct"])
                altitude    = float(row["altitude_m"])
            except ValueError as exc:
                raise ValueError(f"Row {line_num}: non-numeric value — {exc}") from exc

            _check_range("pressure",    pressure,    *PRESSURE_RANGE, line_num)
            _check_range("temperature", temperature, *TEMP_RANGE,     line_num)
            _check_range("humidity",    humidity,    *HUMIDITY_RANGE, line_num)
            _check_range("altitude",    altitude,    *ALTITUDE_RANGE, line_num)

            rows.append(_InputRow(pressure, temperature, humidity, altitude))

    if not rows:
        raise ValueError("CSV contains no data rows.")
    return rows


def _check_range(field: str, value: float, lo: float, hi: float, line_num: int) -> None:
    if not (lo <= value <= hi):
        raise ValueError(
            f"Row {line_num}: {field} = {value} out of range [{lo}, {hi}]"
        )


def get_float(prompt: str, min_val: float, max_val: float) -> float:
    """Prompt the user for a float within [min_val, max_val], retrying on invalid input."""
    while True:
        try:
            value = float(Prompt.ask(prompt))
            if min_val <= value <= max_val:
                return value
            console.print(f"[red]Value must be between {min_val} and {max_val}[/red]")
        except ValueError:
            console.print("[red]Please enter a valid number[/red]")


def _record_observation(pressure_raw: float, temperature: float, humidity: float,
                        altitude: float, observations: list[Observation],
                        verdicts: list[str]) -> None:
    """Normalize, store, render, and log one observation."""
    logger.debug("Raw input received: p=%.1f T=%.1f RH=%.1f alt=%.1f",
                 pressure_raw, temperature, humidity, altitude)

    pressure_qnh = normalize_pressure(pressure_raw, altitude, temperature)
    obs = Observation(
        timestamp    = datetime.now(),
        pressure_raw = pressure_raw,
        pressure_qnh = pressure_qnh,
        temperature  = temperature,
        humidity     = humidity,
        altitude     = altitude,
    )
    observations.append(obs)
    render_dashboard(observations)

    verdict, _ = assess_conditions(observations)
    if verdicts and verdict != verdicts[-1]:
        logger.warning("Verdict changed: %s → %s", verdicts[-1], verdict)
    verdicts.append(verdict)


def edit_observation(observations: list[Observation]) -> None:
    """Let the user select a past observation by index and correct any field.

    Re-derives pressure_qnh when pressure, temperature, or altitude is changed.
    """
    for i, obs in enumerate(observations, 1):
        console.print(
            f"  [{i}] {obs.timestamp.strftime('%H:%M')}  "
            f"{obs.pressure_raw} hPa  {obs.temperature}°C  "
            f"{obs.humidity}%  {obs.altitude}m"
        )

    raw_idx = Prompt.ask("Select observation to edit (number)")
    try:
        idx = int(raw_idx) - 1
        if not (0 <= idx < len(observations)):
            console.print("[red]Index out of range[/red]")
            return
    except ValueError:
        console.print("[red]Please enter a number[/red]")
        return

    obs = observations[idx]
    console.print("Field: [1] pressure  [2] temperature  [3] humidity  [4] altitude")
    field = Prompt.ask("Field to edit")

    if field == "1":
        obs.pressure_raw = get_float("New pressure (hPa)", *PRESSURE_RANGE)
    elif field == "2":
        obs.temperature = get_float("New temperature (°C)", *TEMP_RANGE)
    elif field == "3":
        obs.humidity = get_float("New humidity (%)", *HUMIDITY_RANGE)
    elif field == "4":
        obs.altitude = get_float("New altitude (m)", *ALTITUDE_RANGE)
    else:
        console.print("[red]Invalid field choice[/red]")
        return

    if field in ("1", "2", "4"):
        obs.pressure_qnh = normalize_pressure(obs.pressure_raw, obs.altitude, obs.temperature)

    render_dashboard(observations)


def run(input_file: str | None = None) -> None:
    """Run the interactive NowcastingCLI session."""
    observations: list[Observation] = []
    verdicts:     list[str]         = []

    console.print("[bold blue]NowcastingCLI v1.0[/bold blue] — type 'q' at any prompt to quit\n")
    logger.info("NowcastingCLI started")

    if input_file:
        try:
            rows = _parse_csv(input_file)
        except (ValueError, OSError) as exc:
            console.print(f"[red]Input file error: {exc}[/red]")
            return
        for row in rows:
            _record_observation(row.pressure, row.temperature, row.humidity,
                                row.altitude, observations, verdicts)
    else:
        while True:
            try:
                raw = Prompt.ask("\nEnter pressure (hPa), 'e' to edit a past reading, or 'q' to quit")
                cmd = raw.strip().lower()
                if cmd == "q":
                    break
                if cmd == "e":
                    if not observations:
                        console.print("[yellow]No observations to edit yet[/yellow]")
                    else:
                        edit_observation(observations)
                    continue
                try:
                    pressure_raw = float(raw)
                    if not (0.1 <= pressure_raw <= 1100.0):
                        raise ValueError
                except ValueError:
                    console.print("[red]Value must be between 0.1 and 1100.0[/red]")
                    continue
                temperature = get_float("Temperature (°C)", *TEMP_RANGE)
                humidity    = get_float("Relative Humidity (%)", *HUMIDITY_RANGE)
                altitude    = get_float("GPS Altitude (m)", *ALTITUDE_RANGE)

            except (KeyboardInterrupt, EOFError):
                break

            _record_observation(pressure_raw, temperature, humidity, altitude,
                                observations, verdicts)

    console.print("\n[dim]Session ended.[/dim]")


def cli() -> None:
    """CLI entry point — parses argv and delegates to run()."""
    parser = argparse.ArgumentParser(description="NowcastingCLI — terminal weather nowcasting")
    parser.add_argument("--input", metavar="FILE",
                        help="CSV file with columns: pressure_hpa, temperature_c, humidity_pct, altitude_m")
    args = parser.parse_args()
    run(input_file=args.input)


if __name__ == "__main__":
    cli()
