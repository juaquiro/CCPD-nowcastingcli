def normalize_pressure(pressure_hpa: float, altitude_m: float, temperature_c: float) -> float:
    """
    Barometric formula: correct station pressure to QNH (sea-level equivalent).
    Uses the hypsometric approximation valid below ~5000m.

    Applies P0 = P * (1 - L*h/T0)^(-g*M/R*L) where L=0.0065 K/m is the ISA
    lapse rate, T0 is the extrapolated sea-level temperature in Kelvin, and the
    exponent 5.257 = g*M/(R*L) encodes gravity, dry-air molar mass, and the gas
    constant. Assumes a constant lapse rate, dry air, and hydrostatic equilibrium;
    accuracy degrades above 5000 m, in temperature inversions, and at high humidity.
    """
    return pressure_hpa * (1 - (0.0065 * altitude_m) / (temperature_c + 0.0065 * altitude_m + 273.15)) ** -5.257