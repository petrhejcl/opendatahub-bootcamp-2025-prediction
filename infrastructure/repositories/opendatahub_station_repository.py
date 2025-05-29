# infrastructure/repositories/opendatahub_station_repository.py
from typing import List, Optional

from domain.entities import ParkingStation
from domain.repositories import IParkingStationRepository
from infrastructure.external_apis.opendatahub_client import OpenDataHubClient


class OpenDataHubStationRepository(IParkingStationRepository):
    """Concrete repository implementation for parking stations via OpenDataHub API"""

    def __init__(self, api_client: OpenDataHubClient):
        self.api_client = api_client
        self._stations_cache = None

    def get_all_stations(self) -> List[ParkingStation]:
        """Fetch all parking stations from OpenDataHub API"""
        if self._stations_cache is None:
            self._stations_cache = self._fetch_stations_from_api()
        return self._stations_cache

    def get_station_by_code(self, code: str) -> Optional[ParkingStation]:
        """Get a specific station by its code"""
        stations = self.get_all_stations()
        for station in stations:
            if station.scode == code:
                return station
        return None

    def _fetch_stations_from_api(self) -> List[ParkingStation]:
        """Fetch stations from the OpenDataHub API"""
        try:
            print("Fetching stations from OpenDataHub API...")
            # Usa il metodo corretto del client
            raw_stations = self.api_client.get_stations_data()

            if not raw_stations:
                print("No stations data received from API")
                return []

            stations = []
            for raw_station in raw_stations:
                try:
                    # Estrai la municipalità dai metadata se disponibile
                    municipality = None
                    if raw_station.get('smetadata') and isinstance(raw_station['smetadata'], dict):
                        municipality = raw_station['smetadata'].get('municipality')

                    # Estrai coordinate se disponibili
                    latitude = None
                    longitude = None
                    if raw_station.get('scoordinate') and isinstance(raw_station['scoordinate'], dict):
                        latitude = raw_station['scoordinate'].get('y')
                        longitude = raw_station['scoordinate'].get('x')

                    station = ParkingStation(
                        scode=raw_station.get('scode', ''),
                        sname=raw_station.get('sname', ''),
                        municipality=municipality,
                        latitude=latitude,
                        longitude=longitude
                    )
                    stations.append(station)

                except Exception as e:
                    print(f"Error processing station {raw_station.get('scode', 'unknown')}: {e}")
                    continue

            print(f"Successfully loaded {len(stations)} stations")
            return stations

        except Exception as e:
            print(f"Error fetching stations from API: {e}")
            return []

    def refresh_cache(self):
        """Force refresh of stations cache"""
        self._stations_cache = None
