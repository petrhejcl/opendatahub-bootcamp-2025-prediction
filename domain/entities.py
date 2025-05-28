# domain/entities.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List


@dataclass
class ParkingStation:
    scode: str
    sname: str
    municipality: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


@dataclass
class ParkingData:
    timestamp: datetime
    free_spaces: int
    occupied_spaces: int
    station_code: str


@dataclass
class ModelPerformance:
    actual_values: List[float]
    predicted_values: List[float]
    timestamps: List[datetime]
    mae: float
    rmse: float