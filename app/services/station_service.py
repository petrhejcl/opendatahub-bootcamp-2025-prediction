from typing import List
from typing import Optional
from ..data_access.station_repository import StationRepository
from ..domain.models.station import Station

class StationService:
    def __init__(self, station_repository: StationRepository):
        self._repository = station_repository

    def get_all_stations(self) -> List[Station]:
        return self._repository.get_all_stations()

    def get_station_by_code(self, code: str) -> Optional[Station]:
        stations = self.get_all_stations()
        return next((s for s in stations if s.code == code), None)