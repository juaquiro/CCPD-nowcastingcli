from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box

from .models import Observation, OBSERVATION_UNITS
from .heuristics import WORSENING, IMPROVING, STABLE, assess_conditions

console = Console()

VERDICT_STYLE = {
    WORSENING: ("🔴 CONDITIONS WORSENING", "bold red"),
    IMPROVING: ("🟢 CONDITIONS IMPROVING", "bold green"),
    STABLE:    ("🟡 CONDITIONS STABLE",    "bold yellow"),
}

SPARKLINE_CHARS = "▁▂▃▄▅▆▇█"


def format_observation(obs: Observation) -> str:
    """Return a human-readable multi-line string for a single Observation."""
    u = OBSERVATION_UNITS
    return (
        f"Observation @ {obs.timestamp}\n"
        f"  pressure_raw : {obs.pressure_raw} {u['pressure_raw']}\n"
        f"  pressure_qnh : {obs.pressure_qnh} {u['pressure_qnh']}\n"
        f"  temperature  : {obs.temperature} {u['temperature']}\n"
        f"  humidity     : {obs.humidity} {u['humidity']}\n"
        f"  altitude     : {obs.altitude} {u['altitude']}"
    )


def sparkline(values: list[float]) -> str:
    if not values:
        return ""
    lo, hi = min(values), max(values)
    span = hi - lo or 1.0
    return "".join(
        SPARKLINE_CHARS[int((v - lo) / span * (len(SPARKLINE_CHARS) - 1))]
        for v in values
    )


def trend_arrow(current: float, previous: float | None, threshold: float = 0.1) -> str:
    if previous is None:
        return " "
    delta = current - previous
    if delta > threshold:
        return "↑"
    if delta < -threshold:
        return "↓"
    return "→"


def render_dashboard(observations: list[Observation]) -> None:
    console.clear()

    table = Table(box=box.SIMPLE_HEAD, show_header=True, header_style="bold cyan")
    table.add_column("Time",          style="dim",     width=8)
    table.add_column("Pressure(QNH)", justify="right", width=16)
    table.add_column("Temp",          justify="right", width=8)
    table.add_column("RH",            justify="right", width=8)
    table.add_column("Alt",           justify="right", width=8)

    for i, obs in enumerate(observations):
        prev = observations[i - 1] if i > 0 else None
        table.add_row(
            obs.timestamp.strftime("%H:%M"),
            f"{obs.pressure_qnh:.1f} hPa {trend_arrow(obs.pressure_qnh, prev.pressure_qnh if prev else None)}",
            f"{obs.temperature:.0f}°C {trend_arrow(obs.temperature, prev.temperature if prev else None)}",
            f"{obs.humidity:.0f}% {trend_arrow(obs.humidity, prev.humidity if prev else None)}",
            f"{obs.altitude:.0f}m",
        )

    verdict, reason = assess_conditions(observations)
    label, style    = VERDICT_STYLE[verdict]

    pressures = [o.pressure_qnh for o in observations]
    spark     = sparkline(pressures)
    if len(pressures) >= 2:
        total_delta = pressures[-1] - pressures[0]
        spark_line  = f"{spark}  ({total_delta:+.1f} hPa over session)"
    else:
        spark_line = spark or "—"

    footer = Text()
    footer.append("Pressure trend:  ", style="dim")
    footer.append(spark_line + "\n\n")
    footer.append("Nowcast:  ")
    footer.append(label + "\n", style=style)
    footer.append("Reason:   ", style="dim")
    footer.append(reason)

    console.print(table)
    console.print(Panel(footer, title="[bold]NowcastingCLI v1.0[/bold]", border_style="blue"))