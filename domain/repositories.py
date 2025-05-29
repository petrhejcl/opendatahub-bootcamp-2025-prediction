# domain/repositories.py
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional, Tuple, Any

from domain.entities import ParkingStation, ParkingData


class IParkingStationRepository(ABC):
    @abstractmethod
    def get_all_stations(self) -> List[ParkingStation]:
        pass

    @abstractmethod
    def get_station_by_code(self, code: str) -> Optional[ParkingStation]:
        pass


class IParkingDataRepository(ABC):
    @abstractmethod
    def get_parking_data(self, station_code: str, start_date: datetime, end_date: datetime) -> List[ParkingData]:
        pass


class IMLModelRepository(ABC):
    @abstractmethod
    def save_model(self, model: Any, feature_cols: List[str]) -> None:
        pass

    @abstractmethod
    def load_model(self) -> Tuple[Any, List[str]]:
        pass

    @abstractmethod
    def model_exists(self) -> bool:
        pass
