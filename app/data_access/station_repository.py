# app/data_access/station_repository.py
from typing import List
from ..domain.models.station import Station, Coordinates
from ..infrastructure.api_client import APIClient

class StationRepository:
    def __init__(self, api_client: APIClient):
        self._api_client = api_client

    def get_all_stations(self) -> List[Station]:
        stations_data = self._api_client.get_stations()
        return [
            Station(
                code=station['scode'],
                name=station['sname'],
                coordinates=Coordinates(
                    latitude=station['scoordinate']['y'],
                    longitude=station['scoordinate']['x']
                ) if 'scoordinate' in station else None
            )
            for station in stations_data
        ]