# infrastructure/repositories/api_parking_data_repository.py
import pandas as pd
import csv
import os
from datetime import datetime
from typing import List
from domain.entities import ParkingData
from domain.repositories import IParkingDataRepository
from infrastructure.external_apis.opendatahub_client import OpenDataHubClient


class ApiParkingDataRepository(IParkingDataRepository):
    def __init__(self, api_client: OpenDataHubClient, csv_file_path: str = "parking.csv"):
        self.api_client = api_client
        self.csv_file_path = csv_file_path

    def get_parking_data(self, station_code: str, start_date: datetime, end_date: datetime) -> List[ParkingData]:
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")

        data = self.api_client.get_parking_data(str(station_code), start_str, end_str)

        if not data:
            return []

        # Save to CSV for compatibility with existing code
        try:
            with open(self.csv_file_path, "w", newline="") as csvfile:
                writer = csv.writer(csvfile, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL)
                writer.writerow(["mvalidtime", "free", "occupied"])

                data_dict = {}
                for measurement in data:
                    timestamp = measurement.get("mvalidtime")
                    if not timestamp:
                        continue

                    tname = measurement.get("tname")
                    mvalue = measurement.get("mvalue")

                    if not tname or mvalue is None:
                        continue

                    if timestamp in data_dict:
                        data_dict[timestamp].update({tname: mvalue})
                    else:
                        data_dict[timestamp] = {tname: mvalue}

                parking_data = []
                for mvalidtime, values in data_dict.items():
                    free_spaces = values.get("free", 0)
                    occupied_spaces = values.get("occupied", 0)
                    timestamp = datetime.fromisoformat(mvalidtime.replace('Z', '+00:00'))

                    parking_data.append(ParkingData(
                        timestamp=timestamp,
                        free_spaces=free_spaces,
                        occupied_spaces=occupied_spaces,
                        station_code=station_code
                    ))

                return parking_data

        except Exception as e:
            print(f"Error processing data: {e}")
            return []