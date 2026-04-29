# setup_logging() is called in main.py before this module is imported — handlers already registered.
import logging
logger = logging.getLogger(__name__)


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
    """Convert station pressure to QNH (sea-level equivalent) via the barometric formula.

    Uses the hypsometric approximation valid in the ISA troposphere below ~5000 m:

        P₀ = P_station × (1 − L·h / T₀) ^ −(g·M / R·L)

    where:
        - L = 0.0065 K/m  (ISA lapse rate, LAPSE_RATE_K_PER_M)
        - T₀ = temperature_c + L·altitude_m + 273.15  (extrapolated sea-level temp, K)
        - Exponent 5.257 = g·M / (R·L), encoding gravity (9.80665 m/s²),
          dry-air molar mass (0.028964 kg/mol), and the gas constant (8.31446 J/mol·K)

    Assumes a constant lapse rate, dry air, and hydrostatic equilibrium.
    Accuracy degrades above 5000 m and in temperature-inversion conditions.

    Args:
        pressure_hpa: Raw station pressure in hectopascals (hPa). Must be > 0.
        altitude_m: GPS altitude of the station above sea level in metres (m).
            Must not exceed 5000 m (ISA troposphere model limit).
        temperature_c: Ambient temperature at the station in degrees Celsius (°C).

    Returns:
        QNH pressure in hectopascals (hPa) — station pressure normalised to sea level.

    Raises:
        ValueError: If pressure_hpa <= 0 or altitude_m > 5000 m.
    """
    if pressure_hpa <= 0:
        logger.error("Invalid pressure: %.2f hPa", pressure_hpa)
        raise ValueError(f"pressure_hpa must be positive, got {pressure_hpa}")
    if altitude_m > MAX_ALTITUDE_M:
        logger.error("Altitude exceeds model limit: %.2f m", altitude_m)
        raise ValueError(
            f"altitude_m {altitude_m} exceeds model limit of {MAX_ALTITUDE_M} m"
        )

    t0 = temperature_c + LAPSE_RATE_K_PER_M * altitude_m + KELVIN_OFFSET
    return pressure_hpa * (1 - (LAPSE_RATE_K_PER_M * altitude_m) / t0) ** -BAROMETRIC_EXPONENT
