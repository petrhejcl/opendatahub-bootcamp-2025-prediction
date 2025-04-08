import requests
import json
import csv
import pandas as pd


def get_data(station_code: str, start_date: str, end_date: str) -> pd.DataFrame:
    url = f"https://mobility.api.opendatahub.com/v2/flat/ParkingStation/free,occupied/{start_date}/{end_date}?where=and%28sorigin.eq.FAMAS%2Cscode.eq.%22{station_code}%22%29&select=mvalue,mvalidtime,sname,scode,sorigin,tname&limit=-1"

    # Perform the GET request

    data = make_request(url).get("data")

    with open("parking.csv", "w", newline="") as csvfile:
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

    return pd.read_csv("parking.csv")

def get_bearer_token():
    token_url = (
        "https://auth.opendatahub.com/auth/realms/noi/protocol/openid-connect/token"
    )

    token_headers = {"Content-Type": "application/x-www-form-urlencoded"}

    token_body = {
        "grant_type": "client_credentials",
        # TODO: Add these to env secrets
        "client_id": "opendatahub-bootcamp-2025",
        "client_secret": "QiMsLjDpLi5ffjKRkI7eRgwOwNXoU9l1",
    }

    token_response = requests.post(token_url, headers=token_headers, data=token_body)

    return token_response.json().get("access_token")

def make_request(url: str):
    bearer_token = get_bearer_token()
    headers = {"Authorization": f"Bearer {bearer_token}", "Accept": "application/json"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an error for bad status codes\
        return response.json()
    except requests.RequestException as e:
        print(f"Request failed: {e}")
    except json.JSONDecodeError:
        print("Response was not valid JSON.")


def get_stations():
    url="https://mobility.api.opendatahub.com/v2/flat%2Cnode/ParkingStation?limit=-1&offset=0&select=scode%2Csname%2Csmetadata.municipality&shownull=false&distinct=true"
    data=make_request(url).get("data")
    print(data)
    return data


if __name__ == "__main__":
    df = get_data(station_code="116", start_date="2025-04-07", end_date="2025-04-08")
    print(df)
