# app/data_access/station_repository.py
from typing import List
from ..domain.models.station import Station, Coordinates
from ..infrastructure.api_client import APIClient


class StationRepository:
    def __init__(self, api_client: APIClient = None):
        self._api_client = api_client or APIClient()

    def get_all_stations(self) -> List[Station]:
        stations_data = self._api_client.get_stations()
        if not stations_data or 'data' not in stations_data:
            return []

        stations = []
        for station in stations_data['data']:
            coordinates = None
            if 'scoordinate' in station and station['scoordinate']:
                coordinates = Coordinates(
                    latitude=station['scoordinate']['y'],
                    longitude=station['scoordinate']['x']
                )

            stations.append(Station(
                code=station['scode'],
                name=station['sname'],
                coordinates=coordinates
            ))

        return stations