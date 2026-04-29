from dataclasses import dataclass
from datetime import datetime


OBSERVATION_UNITS: dict[str, str] = {
    "pressure_raw": "hPa",
    "pressure_qnh": "hPa",
    "temperature": "°C",
    "humidity": "%",
    "altitude": "m",
}


@dataclass
class Observation:
    """A single weather observation recorded at a station.

    Attributes:
        timestamp: Date and time the observation was recorded.
        pressure_raw: Raw station pressure as measured by the sensor, in hPa.
            Reflects actual atmospheric pressure at the station's altitude.
        pressure_qnh: Station pressure normalised to sea level (QNH), in hPa.
            Derived from pressure_raw via the barometric formula in physics.py.
        temperature: Ambient air temperature at the station, in °C.
        humidity: Relative humidity at the station, in %. Must be in [0, 100].
        altitude: GPS altitude of the station above sea level, in m.

    Raises:
        ValueError: If humidity is outside [0, 100] or pressure_raw <= 0.
    """

    timestamp: datetime
    pressure_raw: float      # as measured
    pressure_qnh: float      # normalized to sea level
    temperature: float
    humidity: float
    altitude: float

    def __post_init__(self):
        if not (0 <= self.humidity <= 100):
            raise ValueError(f"humidity out of range: {self.humidity}")
        if self.pressure_raw <= 0:
            raise ValueError(f"invalid pressure: {self.pressure_raw}")

