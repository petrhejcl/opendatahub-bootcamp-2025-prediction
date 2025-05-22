import requests
import json

def get_token():
    url = "https://auth.opendatahub.com/auth/realms/noi/protocol/openid-connect/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "client_credentials",
        "client_id": "opendatahub-bootcamp-2025",
        "client_secret": "QiMsLjDpLi5ffjKRkI7eRgwOwNXoU9l1",
    }

    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        return response.json().get("access_token")
    except (requests.RequestException, json.JSONDecodeError) as e:
        print(f"Token retrieval failed: {e}")
        return None
