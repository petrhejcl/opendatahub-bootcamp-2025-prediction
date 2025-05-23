import pandas as pd
from typing import List, Dict, Any, Optional
import logging
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta

from data.api_client import APIClient
from data.models import ParkingStation
from core.exceptions import DataError

logger = logging.getLogger("parking_prediction")


class ParkingDataFetcher:
    """Service for fetching parking data from the API."""

    def __init__(self, api_client: Optional[APIClient] = None):
        """
        Initialize the data fetcher.

        Args:
            api_client: API client instance
        """
        self.api_client = api_client or APIClient()

    def get_stations(self) -> List[ParkingStation]:
        """
        Fetch all available parking stations.

        Returns:
            List of ParkingStation objects

        Raises:
            DataError: If fetching stations fails
        """
        try:
            endpoint = "/v2/flat/ParkingStation"
            params = {
                "limit": -1,
                "offset": 0,
                "select": "scode,sname,smetadata.municipality,scoordinate",
                "shownull": "false",
                "distinct": "true"
            }

            # Try without authentication first since the endpoint works in browser
            response = self.api_client.make_request(endpoint, params=params, require_auth=False)
            stations_data = response.get("data", [])

            # Debug logging
            logger.info(f"Raw response keys: {response.keys()}")
            logger.info(f"Number of stations in response: {len(stations_data)}")
            if stations_data:
                logger.info(
                    f"Sample station data keys: {list(stations_data[0].keys()) if stations_data[0] else 'No keys'}")
                logger.info(f"First station sample: {stations_data[0] if stations_data else 'No data'}")

            # Convert raw data to ParkingStation objects
            stations = []
            for i, station_data in enumerate(stations_data):
                try:
                    # Debug logging for problematic data
                    if i < 3:  # Log first 3 stations for debugging
                        logger.info(f"Processing station {i}: {station_data}")
                        logger.info(
                            f"Station scode type: {type(station_data.get('scode'))}, value: {station_data.get('scode')}")

                    # Check if the raw data has coordinates before converting
                    if "scoordinate" in station_data and station_data["scoordinate"]:
                        # Ensure scode is always a string
                        if 'scode' in station_data:
                            station_data['scode'] = str(station_data['scode'])

                        station = ParkingStation.from_api_response(station_data)
                        stations.append(station)

                except Exception as e:
                    logger.error(f"Failed to parse station {i} with data {station_data}: {e}")
                    logger.error(f"Exception type: {type(e).__name__}")
                    import traceback
                    logger.error(f"Traceback: {traceback.format_exc()}")
                    continue

            logger.info(f"Retrieved {len(stations)} parking stations")
            return stations

        except Exception as e:
            logger.error(f"Failed to fetch parking stations: {e}")
            raise DataError(f"Failed to fetch parking stations: {e}")

    def get_station_data(self, station_code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Fetch parking data for a specific station and date range.

        Args:
            station_code: Station code (ensure it's a string)
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            DataFrame with parking data

        Raises:
            DataError: If fetching data fails
        """
        try:
            # Ensure station_code is a string
            station_code = str(station_code)
            logger.info(f"Fetching data for station: {station_code} (type: {type(station_code)})")

            # Prepare API endpoint
            endpoint = f"/v2/flat/ParkingStation/free,occupied/{start_date}/{end_date}"
            params = {
                "where": f"and(sorigin.eq.FAMAS,scode.eq.\"{station_code}\")",
                "select": "mvalue,mvalidtime,sname,scode,sorigin,tname",
                "limit": -1
            }

            logger.info(f"API endpoint: {endpoint}")
            logger.info(f"API params: {params}")

            # Try without authentication first, then with if needed
            response = self.api_client.make_request(endpoint, params=params, require_auth=False)
            raw_data = response.get("data", [])

            if not raw_data:
                logger.warning(f"No data returned for station {station_code}")
                return pd.DataFrame(columns=["mvalidtime", "free", "occupied"])

            logger.info(f"Retrieved {len(raw_data)} raw data points")
            if raw_data:
                logger.info(f"Sample raw data: {raw_data[0]}")

            # Process data - using a more efficient approach than the original code
            data_dict = {}

            # Process data in parallel with ThreadPoolExecutor
            with ThreadPoolExecutor() as executor:
                # Divide data into chunks to process in parallel
                chunk_size = 1000
                data_chunks = [raw_data[i:i + chunk_size] for i in range(0, len(raw_data), chunk_size)]

                # Process each chunk in parallel
                results = list(executor.map(self._process_data_chunk, data_chunks))

                # Combine results from all chunks
                for chunk_result in results:
                    data_dict.update(chunk_result)

            # Convert the processed data to a DataFrame
            records = []
            for timestamp, values in data_dict.items():
                records.append({
                    "mvalidtime": timestamp,
                    "free": values.get("free"),
                    "occupied": values.get("occupied")
                })

            df = pd.DataFrame(records)

            # Convert timestamp to datetime
            df["mvalidtime"] = pd.to_datetime(df["mvalidtime"])

            # Sort by timestamp
            df = df.sort_values("mvalidtime")

            logger.info(f"Retrieved {len(df)} data points for station {station_code}")
            return df

        except Exception as e:
            logger.error(f"Failed to fetch parking data for station {station_code}: {e}")
            logger.error(f"Exception type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise DataError(f"Failed to fetch parking data: {e}")

    def _process_data_chunk(self, data_chunk: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Process a chunk of raw data from the API.

        Args:
            data_chunk: List of raw data records

        Returns:
            Processed data dictionary
        """
        result = {}
        for measurement in data_chunk:
            timestamp = measurement["mvalidtime"]
            tname = measurement["tname"]
            mvalue = measurement["mvalue"]

            if timestamp not in result:
                result[timestamp] = {}

            result[timestamp][tname] = mvalue

        return result