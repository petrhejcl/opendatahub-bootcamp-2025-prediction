import requests

class ApiTokenProvider(ITokenProvider):
    def get_token(self, client_id: str, client_secret: str) -> str:
        token_url = "https://auth.opendatahub.com/auth/realms/noi/protocol/openid-connect/token"
        token_data = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret
        }

        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response = requests.post(token_url, data=token_data, headers=headers)
        response.raise_for_status()
        return response.json()["access_token"]

class ApiDataRepository(IDataRepository):
    def fetch_parking_data(self, station_code: int, start_date: str, end_date: str, token: str) -> List[Dict[str, Any]]:
        url = (
            f"https://mobility.api.opendatahub.com/v2/flat/ParkingStation/free,occupied/"
            f"{start_date}/{end_date}?where=and(sorigin.eq.FAMAS,scode.eq.%22{station_code}%22)"
            "&select=mvalue,mvalidtime,sname,scode,sorigin,tname&limit=-1"
        )
        headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()["data"]