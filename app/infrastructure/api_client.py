# app/infrastructure/api_client.py
import requests
import json
import csv
import pandas as pd
import os
from datetime import datetime
from typing import Optional, Dict, Any, List


class APIClient:
    BASE_URL = "https://mobility.api.opendatahub.com/v2"
    AUTH_URL = "https://auth.opendatahub.com/auth/realms/noi/protocol/openid-connect/token"

    def __init__(self):
        self.client_id = "opendatahub-bootcamp-2025"
        self.client_secret = "QiMsLjDpLi5ffjKRkI7eRgwOwNXoU9l1"
        self._access_token = None

    def _get_bearer_token(self) -> Optional[str]:
        """Get authentication token from the OpenDataHub API."""
        token_headers = {"Content-Type": "application/x-www-form-urlencoded"}

        token_body = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

        try:
            token_response = requests.post(
                self.AUTH_URL,
                headers=token_headers,
                data=token_body
            )
            token_response.raise_for_status()
            token_data = token_response.json()
            print("Token obtained successfully")
            return token_data.get("access_token")
        except requests.RequestException as e:
            print(f"Failed to get bearer token: {e}")
            return None
        except json.JSONDecodeError:
            print("Token response was not valid JSON.")
            return None

    def _make_request(self, url: str) -> Optional[Dict[str, Any]]:
        """Make authenticated request to the API."""
        bearer_token = self._get_bearer_token()

        if bearer_token is None:
            print("Authentication failed. Cannot proceed with request.")
            return None

        headers = {
            "Authorization": f"Bearer {bearer_token}",
            "Accept": "application/json"
        }

        try:
            print(f"Making request to: {url}")
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            print(f"Request successful, received {len(data.get('data', []))} data points")
            return data
        except requests.RequestException as e:
            print(f"Request failed: {e}")
            return None
        except json.JSONDecodeError:
            print("Response was not valid JSON.")
            return None

    def get_stations(self) -> List[Dict[str, Any]]:
        """Fetch all parking station data."""
        url = f"{self.BASE_URL}/flat%2Cnode/ParkingStation?limit=-1&offset=0&select=scode%2Csname%2Csmetadata.municipality%2Cscoordinate&shownull=false&distinct=true"

        response = self._make_request(url)

        if response is None:
            print("Error: Could not retrieve station data")
            return []

        data = response.get("data", [])
        return data

    def get_parking_data(self, station_code: str, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
        """
        Fetch parking data for a specific station within a date range.

        Args:
            station_code (str): The station code to fetch data for
            start_date (str): Start date in YYYY-MM-DD format
            end_date (str): End date in YYYY-MM-DD format

        Returns:
            pd.DataFrame: DataFrame with columns [mvalidtime, free, occupied] or None if error
        """
        # Ensure station_code is a string
        station_code = str(station_code)

        # Format dates if they're datetime objects
        if not isinstance(start_date, str):
            start_date = start_date.strftime("%Y-%m-%d")
        if not isinstance(end_date, str):
            end_date = end_date.strftime("%Y-%m-%d")

        print(f"Fetching data for station {station_code} from {start_date} to {end_date}")

        url = f"{self.BASE_URL}/flat/ParkingStation/free,occupied/{start_date}/{end_date}?where=and%28sorigin.eq.FAMAS%2Cscode.eq.%22{station_code}%22%29&select=mvalue,mvalidtime,sname,scode,sorigin,tname&limit=-1"

        # Perform the GET request
        response = self._make_request(url)

        # Add error handling
        if response is None:
            print("Error: No data received from the API")
            return pd.DataFrame(columns=["mvalidtime", "free", "occupied"])

        data = response.get("data", [])

        if not data:
            print("Warning: API returned empty data array")
            return pd.DataFrame(columns=["mvalidtime", "free", "occupied"])

        return self._process_parking_data(data, station_code)

    def _process_parking_data(self, data: List[Dict], station_code: str) -> pd.DataFrame:
        """
        Process raw parking data from API into a DataFrame.

        Args:
            data: Raw data from API
            station_code: Station code for file naming

        Returns:
            pd.DataFrame: Processed parking data
        """
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)
        csv_filename = f"data/parking_{station_code}.csv"

        try:
            with open(csv_filename, "w", newline="") as csvfile:
                parking_writer = csv.writer(
                    csvfile, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL
                )
                parking_writer.writerow(["mvalidtime", "free", "occupied"])

                data_dict = {}

                # Process the data
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

        # Read and return the DataFrame
        return self._read_processed_data(csv_filename)

    def _read_processed_data(self, csv_filename: str) -> pd.DataFrame:
        """
        Read processed parking data from CSV file.

        Args:
            csv_filename: Path to the CSV file

        Returns:
            pd.DataFrame: Parking data or empty DataFrame if error
        """
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

    def get_station_by_code(self, station_code: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific station by its code.

        Args:
            station_code: The station code to search for

        Returns:
            Dict containing station data or None if not found
        """
        stations = self.get_stations()

        for station in stations:
            if station.get("scode") == station_code:
                return station

        return None

    def check_connection(self) -> bool:
        """
        Test the API connection by attempting to get an authentication token.

        Returns:
            bool: True if connection is successful, False otherwise
        """
        token = self._get_bearer_token()
        return token is not None


# Example usage and testing
if __name__ == "__main__":
    from datetime import datetime, timedelta

    # Initialize API client
    api_client = APIClient()

    # Test connection
    if api_client.check_connection():
        print("✓ API connection successful")
    else:
        print("✗ API connection failed")
        exit(1)

    # Test getting stations
    stations = api_client.get_stations()
    print(f"Found {len(stations)} stations")

    if stations:
        # Print first few stations
        for i, station in enumerate(stations[:3]):
            print(f"Station {i+1}: {station.get('sname')} (Code: {station.get('scode')})")

    # Test getting parking data
    today = datetime.now()
    yesterday = today - timedelta(days=1)

    df = api_client.get_parking_data(
        station_code="116",
        start_date=yesterday.strftime("%Y-%m-%d"),
        end_date=today.strftime("%Y-%m-%d")
    )

    print(f"DataFrame shape: {df.shape}")
    if not df.empty:
        print("Sample data:")
        print(df.head())