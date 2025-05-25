# app/services/parking_service.py
from typing import List
from datetime import datetime
from ..data_access.parking_repository import ParkingRepository
from ..domain.models.parking_data import ParkingData

class ParkingService:
    def __init__(self, parking_repository: ParkingRepository = None):
        self.repository = parking_repository or ParkingRepository()

    def get_parking_status(
        self,
        station_code: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[ParkingData]:
        return self.repository.get_parking_data(station_code, start_date, end_date)