import csv
import json
import os

import pandas as pd
import requests


def get_data(station_code, start_date, end_date) -> pd.DataFrame:
    # Ensure station_code is a string
    station_code = str(station_code)

    # Format dates if they're datetime objects
    if not isinstance(start_date, str):
        start_date = start_date.strftime("%Y-%m-%d")
    if not isinstance(end_date, str):
        end_date = end_date.strftime("%Y-%m-%d")

    print(f"Fetching data for station {station_code} from {start_date} to {end_date}")

    url = f"https://mobility.api.opendatahub.com/v2/flat/ParkingStation/free,occupied/{start_date}/{end_date}?where=and%28sorigin.eq.FAMAS%2Cscode.eq.%22{station_code}%22%29&select=mvalue,mvalidtime,sname,scode,sorigin,tname&limit=-1"

    # Perform the GET request
    response = make_request(url)

    # Add error handling
    if response is None:
        print("Error: No data received from the API")
        # Return an empty DataFrame with the expected columns
        return pd.DataFrame(columns=["mvalidtime", "free", "occupied"])

    data = response.get("data", [])  # Default to empty list if "data" key doesn't exist

    if not data:
        print("Warning: API returned empty data array")
        return pd.DataFrame(columns=["mvalidtime", "free", "occupied"])

    csv_filename = "parking.csv"

    try:
        with open(csv_filename, "w", newline="") as csvfile:
            parking_writer = csv.writer(
                csvfile, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL
            )
            parking_writer.writerow(["mvalidtime", "free", "occupied"])

            data_dict = dict()

            # Process the data
            for measurement in data:
                timestamp = measurement.get("mvalidtime")
                if not timestamp:
                    continue  # Skip entries without timestamp

                tname = measurement.get("tname")
                mvalue = measurement.get("mvalue")

                if not tname or mvalue is None:
                    continue  # Skip incomplete entries

                if timestamp in data_dict:
                    data_dict[timestamp].update({tname: mvalue})
                else:
                    data_dict[timestamp] = {tname: mvalue}

            # Check if we have any processed data
            if not data_dict:
                print("Warning: No valid data points found to write to CSV")
                return pd.DataFrame(columns=["mvalidtime", "free", "occupied"])

            # Write data to CSV
            for mvalidtime, values in data_dict.items():
                parking_writer.writerow(
                    [mvalidtime, values.get("free"), values.get("occupied")]
                )

            print(f"Data successfully written to {csv_filename}")

    except Exception as e:
        print(f"Error writing to CSV: {e}")
        return pd.DataFrame(columns=["mvalidtime", "free", "occupied"])

    # Verify the file exists and has content
    if os.path.exists(csv_filename) and os.path.getsize(csv_filename) > 0:
        try:
            df = pd.read_csv(csv_filename)
            print(f"Successfully loaded data: {len(df)} rows")
            return df
        except Exception as e:
            print(f"Error reading CSV file: {e}")
            return pd.DataFrame(columns=["mvalidtime", "free", "occupied"])
    else:
        print(f"Warning: CSV file {csv_filename} is empty or doesn't exist")
        return pd.DataFrame(columns=["mvalidtime", "free", "occupied"])


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

    try:
        token_response = requests.post(token_url, headers=token_headers, data=token_body)
        token_response.raise_for_status()  # Raise exception for HTTP errors
        token_data = token_response.json()
        print("Token obtained successfully")
        return token_data.get("access_token")
    except requests.RequestException as e:
        print(f"Failed to get bearer token: {e}")
        return None
    except json.JSONDecodeError:
        print("Token response was not valid JSON.")
        return None


def make_request(url: str):
    bearer_token = get_bearer_token()

    if bearer_token is None:
        print("Authentication failed. Cannot proceed with request.")
        return None

    headers = {"Authorization": f"Bearer {bearer_token}", "Accept": "application/json"}
    try:
        print(f"Making request to: {url}")
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an error for bad status codes
        data = response.json()
        print(f"Request successful, received {len(data.get('data', []))} data points")
        return data
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return None
    except json.JSONDecodeError:
        print("Response was not valid JSON.")
        return None


def get_stations():
    url = "https://mobility.api.opendatahub.com/v2/flat%2Cnode/ParkingStation?limit=-1&offset=0&select=scode%2Csname%2Csmetadata.municipality%2Cscoordinate&shownull=false&distinct=true"
    response = make_request(url)

    if response is None:
        print("Error: Could not retrieve station data")
        return []

    data = response.get("data", [])  # Default to empty list if "data" key doesn't exist
    return data


if __name__ == "__main__":
    # Test the function
    from datetime import datetime, timedelta

    today = datetime.now()
    yesterday = today - timedelta(days=1)

    df = get_data(station_code="116",
                  start_date=yesterday.strftime("%Y-%m-%d"),
                  end_date=today.strftime("%Y-%m-%d"))

    print(f"DataFrame shape: {df.shape}")
    if not df.empty:
        print(df.head())
