# ISA (International Standard Atmosphere) constants used in the barometric formula.

# Temperature lapse rate: the rate at which temperature drops with altitude
# in the troposphere under standard conditions. Units: K/m (kelvin per metre).
LAPSE_RATE_K_PER_M = 0.0065

# Barometric exponent: encodes gravity (g=9.80665 m/s²), dry-air molar mass
# (M=0.028964 kg/mol), and the universal gas constant (R=8.31446 J/mol·K)
# as g*M / (R*L) = 9.80665*0.028964 / (8.31446*0.0065) ≈ 5.257. Dimensionless.
BAROMETRIC_EXPONENT = 5.257

# Offset to convert Celsius to Kelvin. Units: K.
KELVIN_OFFSET = 273.15

# Upper altitude limit of the ISA troposphere model. Accuracy degrades above
# this altitude due to non-standard lapse rates and humidity effects. Units: m.
MAX_ALTITUDE_M = 5000.0


def normalize_pressure(pressure_hpa: float, altitude_m: float, temperature_c: float) -> float:
    """Barometric formula: correct station pressure to QNH (sea-level equivalent).

    Uses the hypsometric approximation valid below ~5000 m.

    Applies P0 = P * (1 - L*h/T0)^(-g*M/R*L) where L is the ISA lapse rate,
    T0 is the extrapolated sea-level temperature in Kelvin, and the exponent
    encodes gravity, dry-air molar mass, and the gas constant.  Assumes a
    constant lapse rate, dry air, and hydrostatic equilibrium.

    Raises:
        ValueError: if pressure_hpa <= 0 or altitude_m > MAX_ALTITUDE_M (5000 m).
    """
    if pressure_hpa <= 0:
        raise ValueError(f"pressure_hpa must be positive, got {pressure_hpa}")
    if altitude_m > MAX_ALTITUDE_M:
        raise ValueError(
            f"altitude_m {altitude_m} exceeds model limit of {MAX_ALTITUDE_M} m"
        )

    t0 = temperature_c + LAPSE_RATE_K_PER_M * altitude_m + KELVIN_OFFSET
    return pressure_hpa * (1 - (LAPSE_RATE_K_PER_M * altitude_m) / t0) ** -BAROMETRIC_EXPONENT
