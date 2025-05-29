from typing import List, Dict, Optional

import requests

from infrastructure.config import OpenDataHubConfig
import urllib.parse

class OpenDataHubClient:
    def __init__(self, config: OpenDataHubConfig):
        self.config = config
        self._token = None

    def _get_bearer_token(self) -> Optional[str]:
        token_headers = {"Content-Type": "application/x-www-form-urlencoded"}
        token_body = {
            "grant_type": "client_credentials",
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
        }

        try:
            response = requests.post(self.config.token_url, headers=token_headers, data=token_body)
            response.raise_for_status()
            token_data = response.json()
            return token_data.get("access_token")
        except Exception as e:
            print(f"Failed to get bearer token: {e}")
            return None

    def _make_request(self, url: str) -> Optional[Dict]:
        if not self._token:
            self._token = self._get_bearer_token()

        if not self._token:
            return None

        headers = {"Authorization": f"Bearer {self._token}", "Accept": "application/json"}
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Request failed: {e}")
            return None

    def get_stations_data(self) -> List[Dict]:
        url = f"{self.config.base_url}/flat%2Cnode/ParkingStation?limit=-1&offset=0&select=scode%2Csname%2Csmetadata.municipality%2Cscoordinate&shownull=false&distinct=true"
        response = self._make_request(url)
        return response.get("data", []) if response else []

    def get_stations(self) -> List[Dict]:
        return self.get_stations_data()

    def get_parking_data(self, station_code: str, start_date: str, end_date: str) -> List[Dict]:
        # URL encode the station code properly
        encoded_station_code = urllib.parse.quote(station_code, safe='')
        # Remove the sorigin.eq.FAMAS filter from the where clause
        url = f"{self.config.base_url}/flat/ParkingStation/free,occupied/{start_date}/{end_date}?where=scode.eq.%22{encoded_station_code}%22&select=mvalue,mvalidtime,sname,scode,sorigin,tname&limit=-1"
        print(f"Making API request with URL: {url}")  # Add this debug line
        response = self._make_request(url)
        return response.get("data", []) if response else []