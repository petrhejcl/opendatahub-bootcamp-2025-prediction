# app/infrastructure/api_client.py
import requests
from typing import Optional, Dict, Any
from .authentication import AuthenticationService

class APIClient:
    def __init__(self):
        self.auth_service = AuthenticationService()
        self.base_url = "https://mobility.api.opendatahub.com/v2"

    def _get_headers(self) -> Dict[str, str]:
        token = self.auth_service.get_token()
        if not token:
            raise ValueError("Failed to get authentication token")
        return {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
        }

    def make_request(self, endpoint: str) -> Optional[Dict[str, Any]]:
        try:
            response = requests.get(
                f"{self.base_url}/{endpoint}",
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"API request failed: {e}")
            return None

    def get_parking_data(self, station_code: str, start_date: str, end_date: str) -> Optional[Dict[str, Any]]:
        endpoint = f"flat/ParkingStation/free,occupied/{start_date}/{end_date}?where=and%28sorigin.eq.FAMAS%2Cscode.eq.%22{station_code}%22%29&select=mvalue,mvalidtime,sname,scode,sorigin,tname&limit=-1"
        return self.make_request(endpoint)

    def get_stations(self) -> Optional[Dict[str, Any]]:
        endpoint = "flat%2Cnode/ParkingStation?limit=-1&offset=0&select=scode%2Csname%2Csmetadata.municipality%2Cscoordinate&shownull=false&distinct=true"
        return self.make_request(endpoint)