from .models import Observation

# setup_logging() is called in main.py before this module is imported — handlers already registered.
import logging
logger = logging.getLogger(__name__)



WORSENING = "worsening"
STABLE    = "stable"
IMPROVING = "improving"

PRESSURE_FALL_THRESHOLD  = -1.0   # hPa — rapid drop signals worsening conditions
HIGH_HUMIDITY_THRESHOLD  = 85.0   # %   — high humidity signals worsening conditions
PRESSURE_RISE_THRESHOLD  =  1.0   # hPa — sustained rise signals improving conditions


def assess_conditions(observations: list[Observation]) -> tuple[str, str]:
    """Derive a nowcast verdict and human-readable reason from recent observations.

    Compares the last two observations to detect rapid pressure falls or high
    humidity (WORSENING), sustained pressure rises with falling humidity
    (IMPROVING), or neither (STABLE). Decision thresholds are defined by the
    module-level constants PRESSURE_FALL_THRESHOLD, PRESSURE_RISE_THRESHOLD,
    and HIGH_HUMIDITY_THRESHOLD.

    Args:
        observations: Ordered list of Observation objects, earliest first.
            At least two entries are required for a meaningful verdict.

    Returns:
        A tuple of (verdict, reason) where:
            - verdict is one of the module constants WORSENING, STABLE, or IMPROVING.
            - reason is a human-readable string explaining the verdict.
        If fewer than two observations are provided, returns
        (STABLE, "Insufficient data — enter at least one more reading").
    """
    if len(observations) < 2:
        verdict = STABLE
        reason  = "Insufficient data — enter at least one more reading"
        return (verdict, reason)

    current  = observations[-1]
    previous = observations[-2]

    pressure_delta = current.pressure_qnh - previous.pressure_qnh  # hPa

    if pressure_delta < PRESSURE_FALL_THRESHOLD or current.humidity > HIGH_HUMIDITY_THRESHOLD:
        reason_parts = []
        if pressure_delta < PRESSURE_FALL_THRESHOLD:
            reason_parts.append(f"Rapid pressure fall ({pressure_delta:+.1f} hPa)")
        if current.humidity > HIGH_HUMIDITY_THRESHOLD:
            reason_parts.append(f"High humidity ({current.humidity:.0f}%)")
        verdict = WORSENING
        reason  = " + ".join(reason_parts)
        return (verdict, reason)

    if pressure_delta > PRESSURE_RISE_THRESHOLD and current.humidity < previous.humidity:
        verdict = IMPROVING
        reason  = f"Pressure rising ({pressure_delta:+.1f} hPa), humidity falling"
        return (verdict, reason)

    verdict = STABLE
    reason  = f"Pressure change within normal range ({pressure_delta:+.1f} hPa)"
    return (verdict, reason)