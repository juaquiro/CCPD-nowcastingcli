from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Observation:
    timestamp: datetime
    pressure_raw: float      # as measured
    pressure_qnh: float      # normalized to sea level
    temperature: float
    humidity: float
    altitude: float
    units: dict = field(default_factory=lambda: {
        "pressure_raw": "hPa",
        "pressure_qnh": "hPa",
        "temperature": "°C",
        "humidity": "%",
        "altitude": "m",
    })

    def __post_init__(self):
        if not (0 <= self.humidity <= 100):
            raise ValueError(f"humidity fuera de rango: {self.humidity}")
        if self.pressure_raw <= 0:
            raise ValueError(f"pressure inválida: {self.pressure_raw}")

    def __str__(self):
        u = self.units
        return (
            f"Observation @ {self.timestamp}\n"
            f"  pressure_raw : {self.pressure_raw} {u.get('pressure_raw', '')}\n"
            f"  pressure_qnh : {self.pressure_qnh} {u.get('pressure_qnh', '')}\n"
            f"  temperature  : {self.temperature} {u.get('temperature', '')}\n"
            f"  humidity     : {self.humidity} {u.get('humidity', '')}\n"
            f"  altitude     : {self.altitude} {u.get('altitude', '')}"
        )