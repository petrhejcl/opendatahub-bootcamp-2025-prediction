from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from datetime import datetime


@dataclass
class ParkingStation:
    """Represents a parking station with its metadata."""
    id: str
    name: str
    latitude: float
    longitude: float
    municipality: Optional[str] = None

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> 'ParkingStation':
        """Create a ParkingStation instance from API response data."""
        return cls(
            id=data.get('scode', ''),
            name=data.get('sname', ''),
            latitude=data['scoordinate']['y'] if 'scoordinate' in data else 0.0,
            longitude=data['scoordinate']['x'] if 'scoordinate' in data else 0.0,
            municipality=data.get('smetadata', {}).get('municipality', None)
        )


@dataclass
class ParkingMeasurement:
    """Represents a parking measurement record."""
    timestamp: datetime
    free_spaces: int
    occupied_spaces: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ParkingMeasurement':
        """Create a ParkingMeasurement from a dictionary."""
        return cls(
            timestamp=datetime.fromisoformat(data['mvalidtime'].replace('Z', '+00:00')),
            free_spaces=data.get('free', 0),
            occupied_spaces=data.get('occupied', 0)
        )