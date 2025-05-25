# app/infrastructure/authentication.py
import requests
from typing import Optional

class AuthenticationService:
    def __init__(self):
        self.token_url = "https://auth.opendatahub.com/auth/realms/noi/protocol/openid-connect/token"
        self.client_id = "opendatahub-bootcamp-2025"
        self.client_secret = "QiMsLjDpLi5ffjKRkI7eRgwOwNXoU9l1"

    def get_token(self) -> Optional[str]:
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

        try:
            response = requests.post(self.token_url, headers=headers, data=data)
            response.raise_for_status()
            return response.json().get("access_token")
        except Exception as e:
            print(f"Token retrieval failed: {e}")
            return None
