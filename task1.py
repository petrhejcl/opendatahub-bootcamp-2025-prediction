import csv
import json

import requests

# Configuration

start_date = "2024-04-08"
end_date = "2025-04-08"  # not included

station_name = "P16 - Fiera via Marco Polo/Buozzi"
station_code = 116

url = f"https://mobility.api.opendatahub.com/v2/flat/ParkingStation/free,occupied/{start_date}/{end_date}?where=and%28sorigin.eq.FAMAS%2Cscode.eq.%22{station_code}%22%29&select=mvalue,mvalidtime,sname,scode,sorigin,tname&limit=-1"

# TODO: Maybe add this to separate file
token_url = "https://auth.opendatahub.com/auth/realms/noi/protocol/openid-connect/token"

token_headers = {
    "Content-Type": "application/x-www-form-urlencoded"
}

token_body = {
    "grant_type": "client_credentials",
    # TODO: Add these to env secrets
    "client_id": "opendatahub-bootcamp-2025",
    "client_secret": "QiMsLjDpLi5ffjKRkI7eRgwOwNXoU9l1"
}

token_response = requests.post(token_url, headers=token_headers, data=token_body)

bearer_token = token_response.json().get('access_token')

print(bearer_token)

output_file = "response.json"

# Set headers
headers = {"Authorization": f"Bearer {bearer_token}", "Accept": "application/json"}

# Perform the GET request
try:
    response = requests.get(url, headers=headers)
    print(response.headers)
    response.raise_for_status()  # Raise an error for bad status codes\
    print(response.status_code)
    data = response.json().get("data")  # Parse JSON response

    with open("data/parking.csv", "w", newline="") as csvfile:
        parking_writer = csv.writer(
            csvfile, delimiter=",", quotechar="|", quoting=csv.QUOTE_MINIMAL
        )
        parking_writer.writerow(["mvalidtime", "free", "occupied"])

        data_dict = dict()

        for measurement in data:
            if measurement["mvalidtime"] in data_dict:
                data_dict[measurement["mvalidtime"]].update(
                    {measurement["tname"]: measurement["mvalue"]}
                )
            else:
                data_dict[measurement["mvalidtime"]] = {
                    measurement["tname"]: measurement["mvalue"]
                }

        for mvalidtime, data in data_dict.items():
            parking_writer.writerow(
                [mvalidtime, data.get("free"), data.get("occupied")]
            )

        print(f"Response saved to {csvfile}")

except requests.RequestException as e:
    print(f"Request failed: {e}")
except json.JSONDecodeError:
    print("Response was not valid JSON.")
