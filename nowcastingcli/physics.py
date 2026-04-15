def normalize_pressure(pressure_hpa: float, altitude_m: float, temperature_c: float) -> float:
    """
    Barometric formula: correct station pressure to QNH (sea-level equivalent).
    Uses the hypsometric approximation valid below ~5000m.
    """
    return pressure_hpa * (1 - (0.0065 * altitude_m) / (temperature_c + 0.0065 * altitude_m + 273.15)) ** -5.257