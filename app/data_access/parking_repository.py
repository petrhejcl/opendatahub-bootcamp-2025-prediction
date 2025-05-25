# app/data_access/parking_repository.py
from typing import List, Optional
from datetime import datetime
import pandas as pd
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
        data = self.api_client.get_parking_data(
            station_code,
            start_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d")
        )
        return self._map_to_domain(data)

    def get_parking_dataframe(
            self,
            station_code: str,
            start_date: datetime,
            end_date: datetime
    ) -> Optional[pd.DataFrame]:
        """Returns parking data as DataFrame for ML operations"""
        parking_data = self.get_parking_data(station_code, start_date, end_date)
        if not parking_data:
            return None

        df_data = []
        for data in parking_data:
            df_data.append({
                'mvalidtime': data.timestamp,
                'free': data.free_spaces,
                'occupied': data.occupied_spaces
            })

        df = pd.DataFrame(df_data)
        df['mvalidtime'] = pd.to_datetime(df['mvalidtime'])
        return df.sort_values('mvalidtime')

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
                    timestamp=datetime.fromisoformat(timestamp.replace('Z', '+00:00')),
                    free_spaces=values['free'],
                    occupied_spaces=values['occupied'],
                    station_code=str(values.get('scode', '')),
                    station_name=values.get('sname')
                )
                parking_data_list.append(parking_data)

        return sorted(parking_data_list, key=lambda x: x.timestamp)