import requests
import json
from app.infrastructure.authentication import AuthenticationService

def make_request(url: str):
    token = AuthenticationService.get_token()
    if not token:
        return None

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, json.JSONDecodeError) as e:
        print(f"Request failed: {e}")
        return None

def get_stations():
    url = (
        "https://mobility.api.opendatahub.com/v2/flat%2Cnode/ParkingStation"
        "?limit=-1&offset=0&select=scode%2Csname%2Csmetadata.municipality"
        "%2Cscoordinate&shownull=false&distinct=true"
    )
    response = make_request(url)
    return response.get("data", []) if response else []
