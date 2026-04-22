from dataclasses import dataclass, field
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
    timestamp: datetime
    pressure_raw: float      # as measured
    pressure_qnh: float      # normalized to sea level
    temperature: float
    humidity: float
    altitude: float
    units: dict = field(default_factory=OBSERVATION_UNITS.copy)

    def __post_init__(self):
        if not (0 <= self.humidity <= 100):
            raise ValueError(f"humidity out of range: {self.humidity}")
        if self.pressure_raw <= 0:
            raise ValueError(f"invalid pressure: {self.pressure_raw}")

