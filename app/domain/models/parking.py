# app/domain/models/parking.py
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ParkingData:
    timestamp: datetime
    free_spaces: int
    occupied_spaces: int
    station_code: str