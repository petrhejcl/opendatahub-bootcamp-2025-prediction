# app/domain/models/parking_data.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class ParkingData:
    timestamp: datetime
    free_spaces: int
    occupied_spaces: int
    station_code: str
    station_name: Optional[str] = None

@dataclass
class ParkingStation:
    code: str
    name: str
    municipality: Optional[str] = None