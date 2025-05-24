from dataclasses import dataclass
from typing import Optional

@dataclass
class Coordinates:
    latitude: float
    longitude: float

@dataclass
class Station:
    code: str
    name: str
    coordinates: Optional[Coordinates] = None