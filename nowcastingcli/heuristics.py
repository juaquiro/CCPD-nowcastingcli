from .models import Observation


WORSENING = "worsening"
STABLE    = "stable"
IMPROVING = "improving"

PRESSURE_FALL_THRESHOLD  = -1.0   # hPa — rapid drop signals worsening conditions
HIGH_HUMIDITY_THRESHOLD  = 85.0   # %   — high humidity signals worsening conditions
PRESSURE_RISE_THRESHOLD  =  1.0   # hPa — sustained rise signals improving conditions


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

    if pressure_delta < PRESSURE_FALL_THRESHOLD or current.humidity > HIGH_HUMIDITY_THRESHOLD:
        reason_parts = []
        if pressure_delta < PRESSURE_FALL_THRESHOLD:
            reason_parts.append(f"Rapid pressure fall ({pressure_delta:+.1f} hPa)")
        if current.humidity > HIGH_HUMIDITY_THRESHOLD:
            reason_parts.append(f"High humidity ({current.humidity:.0f}%)")
        return WORSENING, " + ".join(reason_parts)

    if pressure_delta > PRESSURE_RISE_THRESHOLD and current.humidity < previous.humidity:
        return IMPROVING, f"Pressure rising ({pressure_delta:+.1f} hPa), humidity falling"

    return STABLE, f"Pressure change within normal range ({pressure_delta:+.1f} hPa)"