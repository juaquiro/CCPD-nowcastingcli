from datetime import datetime
from rich.prompt import Prompt

from .models import Observation
from .physics import normalize_pressure
from .display import render_dashboard, console


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
        obs.pressure_raw = get_float("New pressure (hPa)", 0.1, 1100.0)
    elif field == "2":
        obs.temperature = get_float("New temperature (°C)", -60, 60)
    elif field == "3":
        obs.humidity = get_float("New humidity (%)", 0, 100)
    elif field == "4":
        obs.altitude = get_float("New altitude (m)", -500, 5000)
    else:
        console.print("[red]Invalid field choice[/red]")
        return

    if field in ("1", "2", "4"):
        obs.pressure_qnh = normalize_pressure(obs.pressure_raw, obs.altitude, obs.temperature)

    render_dashboard(observations)


def run() -> None:
    """Run the interactive NowcastingCLI session."""
    observations: list[Observation] = []
    console.print("[bold blue]NowcastingCLI v1.0[/bold blue] — type 'q' at any prompt to quit\n")

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
            temperature  = get_float("Temperature (°C)", -60, 60)
            humidity     = get_float("Relative Humidity (%)", 0, 100)
            altitude     = get_float("GPS Altitude (m)", -500, 5000)

        except (KeyboardInterrupt, EOFError):
            break

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

    console.print("\n[dim]Session ended.[/dim]")


if __name__ == "__main__":
    run()