import pandas as pd
import os
from typing import Optional
from pathlib import Path
import logging

from config.settings import DATA_CONFIG
from core.exceptions import DataError

logger = logging.getLogger("parking_prediction")


class ParkingDataRepository:
    """Repository for storing and retrieving parking data."""

    def __init__(self, data_config: dict = None):
        """
        Initialize the data repository.

        Args:
            data_config: Configuration for data storage
        """
        self.config = data_config or DATA_CONFIG
        self.default_csv_path = Path(self.config["default_csv_path"])

        # Ensure the directory exists
        self.default_csv_path.parent.mkdir(parents=True, exist_ok=True)

    def save_dataframe(self, df: pd.DataFrame, file_path: Optional[Path] = None) -> Path:
        """
        Save a DataFrame to CSV.

        Args:
            df: DataFrame to save
            file_path: Path to save the CSV file (uses default if None)

        Returns:
            Path where the file was saved

        Raises:
            DataError: If saving fails
        """
        path = file_path or self.default_csv_path

        try:
            # Create directory if it doesn't exist
            path.parent.mkdir(parents=True, exist_ok=True)

            # Save DataFrame to CSV
            df.to_csv(path, index=False)
            logger.info(f"Saved DataFrame with {len(df)} rows to {path}")
            return path

        except Exception as e:
            logger.error(f"Failed to save DataFrame to {path}: {e}")
            raise DataError(f"Failed to save DataFrame: {e}")

    def load_dataframe(self, file_path: Optional[Path] = None) -> pd.DataFrame:
        """
        Load a DataFrame from CSV.

        Args:
            file_path: Path to the CSV file (uses default if None)

        Returns:
            Loaded DataFrame

        Raises:
            DataError: If loading fails
        """
        path = file_path or self.default_csv_path

        try:
            if not path.exists():
                logger.warning(f"CSV file not found at {path}")
                return pd.DataFrame(columns=["mvalidtime", "free", "occupied"])

            # Load DataFrame from CSV
            df = pd.read_csv(path)

            # Convert mvalidtime to datetime if it exists
            if "mvalidtime" in df.columns:
                df["mvalidtime"] = pd.to_datetime(df["mvalidtime"])

            logger.info(f"Loaded DataFrame with {len(df)} rows from {path}")
            return df

        except Exception as e:
            logger.error(f"Failed to load DataFrame from {path}: {e}")
            raise DataError(f"Failed to load DataFrame: {e}")