from .models import Observation


WORSENING = "worsening"
STABLE    = "stable"
IMPROVING = "improving"


def assess_conditions(observations: list[Observation]) -> tuple[str, str]:
    """
    Returns (verdict, reason) based on the last two observations.
    Requires at least 2 observations; returns STABLE with a note if insufficient.
    """
    if len(observations) < 2:
        return STABLE, "Insufficient data — enter at least one more reading"

    current  = observations[-1]
    previous = observations[-2]

    pressure_delta = current.pressure_qnh - previous.pressure_qnh  # hPa

    if pressure_delta < -1.0 or current.humidity > 85:  # pressure_qnh: hPa; humidity: %
        reason_parts = []
        if pressure_delta < -1.0:
            reason_parts.append(f"Rapid pressure fall ({pressure_delta:+.1f} hPa)")
        if current.humidity > 85:
            reason_parts.append(f"High humidity ({current.humidity:.0f}%)")
        return WORSENING, " + ".join(reason_parts)

    if pressure_delta > 1.0 and current.humidity < previous.humidity:  # pressure_qnh: hPa; humidity: %
        return IMPROVING, f"Pressure rising ({pressure_delta:+.1f} hPa), humidity falling"

    return STABLE, f"Pressure change within normal range ({pressure_delta:+.1f} hPa)"