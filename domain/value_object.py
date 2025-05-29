# domain/value_objects.py
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class DateRange:
    start_date: datetime
    end_date: datetime

    def __post_init__(self):
        if self.start_date > self.end_date:
            raise ValueError("Start date must be before or equal to end date")


@dataclass(frozen=True)
class StationCoordinate:
    latitude: float
    longitude: float


@dataclass(frozen=True)
class PredictionResult:
    predicted_free_spaces: int
    prediction_time: datetime
    station_code: str
