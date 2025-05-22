# app/data_access/parking_repository.py
from typing import Optional
import pandas as pd
from ..infrastructure.api_client import APIClient

class ParkingRepository:
    def __init__(self, api_client: APIClient):
        self._api_client = api_client

    def get_parking_data(self, station_code: str, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
        return self._api_client.get_parking_data(station_code, start_date, end_date)