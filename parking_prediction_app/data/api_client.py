import requests
import json
import time
import logging
from typing import Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor

from config.settings import API_CONFIG
from core.exceptions import APIError, AuthenticationError

logger = logging.getLogger("parking_prediction")


class APIClient:
    """Client for interacting with the OpenDataHub API."""

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the API client.

        Args:
            config: API configuration dictionary
        """
        self.config = config or API_CONFIG
        self._token = None
        self._token_expiry = 0

    def _get_bearer_token(self) -> str:
        """
        Get a valid bearer token for API authentication.

        Returns:
            str: Bearer token

        Raises:
            AuthenticationError: If unable to obtain token
        """
        current_time = time.time()

        # Check if we have a valid token
        if self._token and current_time < self._token_expiry:
            return self._token

        # Use the exact same method as the working version
        token_url = "https://auth.opendatahub.com/auth/realms/noi/protocol/openid-connect/token"
        token_headers = {"Content-Type": "application/x-www-form-urlencoded"}

        # Try with config values first, fallback to hardcoded values
        token_body = {
            "grant_type": "client_credentials",
            "client_id": self.config.get("client_id", "opendatahub-bootcamp-2025"),
            "client_secret": self.config.get("client_secret", "QiMsLjDpLi5ffjKRkI7eRgwOwNXoU9l1"),
        }

        # Debug logging
        logger.info(f"Attempting authentication with client_id: {token_body['client_id']}")
        logger.info(f"Using auth URL: {token_url}")

        try:
            token_response = requests.post(token_url, headers=token_headers, data=token_body)
            token_response.raise_for_status()  # Raise exception for HTTP errors
            token_data = token_response.json()

            self._token = token_data.get("access_token")
            if not self._token:
                raise AuthenticationError("No access_token in response")

            # Set expiry with a safety margin of 60 seconds
            expires_in = token_data.get("expires_in", 3600)
            self._token_expiry = current_time + expires_in - 60

            logger.info("Token obtained successfully")
            return self._token

        except requests.RequestException as e:
            logger.error(f"Failed to get bearer token: {e}")
            raise AuthenticationError(f"Failed to obtain bearer token: {e}")
        except json.JSONDecodeError:
            logger.error("Token response was not valid JSON")
            raise AuthenticationError("Token response was not valid JSON")

    def make_request(self, endpoint: str, method: str = "GET", params: Dict = None,
                     data: Dict = None, retry_count: int = 0, require_auth: bool = True) -> Dict[str, Any]:
        """
        Make a request to the API with optional authentication.

        Args:
            endpoint: API endpoint path
            method: HTTP method (GET, POST, etc.)
            params: URL parameters
            data: Request body for POST requests
            retry_count: Current retry attempt
            require_auth: Whether authentication is required for this endpoint

        Returns:
            Dict containing the API response

        Raises:
            APIError: If the request fails
        """
        # Construct full URL
        if endpoint.startswith('http'):
            url = endpoint  # Full URL provided
        else:
            url = f"{self.config['base_url']}{endpoint}"

        # Prepare headers
        headers = {
            "Accept": "application/json"
        }

        # Add authentication if required
        if require_auth:
            try:
                bearer_token = self._get_bearer_token()
                headers["Authorization"] = f"Bearer {bearer_token}"
            except AuthenticationError as e:
                if retry_count == 0:  # Only log on first attempt
                    logger.warning(f"Authentication failed, trying without auth: {e}")
                # Continue without authentication
                pass

        try:
            logger.info(f"Making request to: {url}")
            logger.debug(f"Headers: {headers}")
            logger.debug(f"Params: {params}")

            if method.upper() == "GET":
                response = requests.get(
                    url,
                    headers=headers,
                    params=params,
                    timeout=self.config.get("timeout", 30)
                )
            elif method.upper() == "POST":
                response = requests.post(
                    url,
                    headers=headers,
                    params=params,
                    json=data,
                    timeout=self.config.get("timeout", 30)
                )
            else:
                raise APIError(f"Unsupported HTTP method: {method}")

            # Log response status
            logger.info(f"Response status: {response.status_code}")

            response.raise_for_status()  # Raise an error for bad status codes
            response_data = response.json()

            logger.info(f"Request successful, received {len(response_data.get('data', []))} data points")
            return response_data

        except requests.RequestException as e:
            logger.warning(f"Request failed: {e}")

            # If it's a 401 error and we were using auth, try without auth
            if (hasattr(e, 'response') and e.response and
                e.response.status_code == 401 and require_auth and retry_count == 0):
                logger.info("Got 401 with auth, trying without authentication...")
                return self.make_request(endpoint, method, params, data, retry_count + 1, require_auth=False)

            # If it's an auth error, clear the token to force refresh
            if hasattr(e, 'response') and e.response and e.response.status_code == 401:
                logger.info("Clearing cached token due to 401 error")
                self._token = None
                self._token_expiry = 0

            # Retry logic for other errors
            if retry_count < self.config.get("max_retries", 3):
                retry_wait = 2 ** retry_count  # Exponential backoff
                logger.info(f"Retrying in {retry_wait} seconds...")
                time.sleep(retry_wait)
                return self.make_request(endpoint, method, params, data, retry_count + 1, require_auth)

            raise APIError(f"Request failed after {retry_count} retries: {e}")
        except json.JSONDecodeError:
            logger.error("Response was not valid JSON")
            raise APIError("Response was not valid JSON")

    def test_connection(self) -> bool:
        """
        Test the API connection and authentication.

        Returns:
            bool: True if connection is successful
        """
        try:
            # Test without authentication first
            test_endpoint = "/v2/flat/ParkingStation"
            test_params = {"limit": 1}
            self.make_request(test_endpoint, params=test_params, require_auth=False)
            logger.info("API connection test successful (no auth required)")
            return True
        except Exception as e:
            logger.error(f"API connection test failed: {e}")
            return False

    # Convenience method that matches the working version's pattern
    def get_bearer_token(self) -> Optional[str]:
        """
        Public method to get bearer token (matches working version interface).

        Returns:
            Optional[str]: Bearer token or None if failed
        """
        try:
            return self._get_bearer_token()
        except Exception as e:
            logger.error(f"Failed to get bearer token: {e}")
            return None