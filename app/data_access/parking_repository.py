from typing import List
from datetime import datetime
from ..domain.models.parking_data import ParkingData
from ..infrastructure.api_client import APIClient

class ParkingRepository:
    def __init__(self):
        self.api_client = APIClient()

    def get_parking_data(
        self,
        station_code: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[ParkingData]:
        endpoint = f"flat/ParkingStation/free,occupied/{start_date:%Y-%m-%d}/{end_date:%Y-%m-%d}"
        data = self.api_client.make_request(endpoint)

        # Trasforma i dati grezzi in oggetti domain
        return self._map_to_domain(data)


    def _map_to_domain(self, raw_data: dict) -> List[ParkingData]:
        if not raw_data or 'data' not in raw_data:
            return []

        parking_data_list = []
        data_dict = {}

        for measurement in raw_data['data']:
            timestamp = measurement.get('mvalidtime')
            if not timestamp:
                continue

            if timestamp not in data_dict:
                data_dict[timestamp] = {}

            data_dict[timestamp][measurement.get('tname')] = measurement.get('mvalue')

        for timestamp, values in data_dict.items():
            if 'free' in values and 'occupied' in values:
                parking_data = ParkingData(
                    timestamp=datetime.fromisoformat(timestamp),
                    free_spaces=values['free'],
                    occupied_spaces=values['occupied'],
                    station_code=str(values.get('scode', '')),
                    station_name=values.get('sname')
                )
                parking_data_list.append(parking_data)

        return sorted(parking_data_list, key=lambda x: x.timestamp)