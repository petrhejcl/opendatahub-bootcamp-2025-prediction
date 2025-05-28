# infrastructure/repositories/api_parking_station_repository.py
from typing import List, Optional
from domain.entities import ParkingStation
from domain.repositories import IParkingStationRepository
from infrastructure.external_apis.opendatahub_client import OpenDataHubClient


class ApiParkingStationRepository(IParkingStationRepository):
    def __init__(self, api_client: OpenDataHubClient):
        self.api_client = api_client

    def get_all_stations(self) -> List[ParkingStation]:
        data = self.api_client.get_stations_data()
        stations = []
        for item in data:
            latitude = None
            longitude = None
            municipality = None

            if 'scoordinate' in item and item['scoordinate']:
                latitude = item['scoordinate'].get('y')
                longitude = item['scoordinate'].get('x')

            if 'smetadata' in item and item['smetadata']:
                municipality = item['smetadata'].get('municipality')

            station = ParkingStation(
                scode=item['scode'],
                sname=item['sname'],
                municipality=municipality,
                latitude=latitude,
                longitude=longitude
            )
            stations.append(station)
        return stations

    def get_station_by_code(self, code: str) -> Optional[ParkingStation]:
        stations = self.get_all_stations()
        return next((s for s in stations if s.scode == code), None)