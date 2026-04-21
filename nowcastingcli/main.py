from datetime import datetime
from rich.prompt import Prompt

from .models import Observation
from .physics import normalize_pressure
from .display import render_dashboard, console


def get_float(prompt: str, min_val: float, max_val: float) -> float:
    while True:
        try:
            value = float(Prompt.ask(prompt))
            if min_val <= value <= max_val:
                return value
            console.print(f"[red]Value must be between {min_val} and {max_val}[/red]")
        except ValueError:
            console.print("[red]Please enter a valid number[/red]")


def run() -> None:
    observations: list[Observation] = []
    console.print("[bold blue]NowcastingCLI v1.0[/bold blue] — type 'q' at any prompt to quit\n")

    while True:
        try:
            raw = Prompt.ask("\nEnter pressure (hPa), or 'q' to quit")
            if raw.strip().lower() == "q":
                break
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