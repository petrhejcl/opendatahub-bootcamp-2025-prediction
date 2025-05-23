import pandas as pd
import numpy as np
from typing import List, Tuple
import logging
from concurrent.futures import ThreadPoolExecutor
from functools import partial

from config.settings import ML_CONFIG, THREAD_CONFIG
from core.exceptions import DataError

logger = logging.getLogger("parking_prediction")


class FeatureEngineer:
    """Service for creating features from raw parking data."""

    def __init__(self, config: dict = None, thread_config: dict = None):
        """
        Initialize the feature engineer.

        Args:
            config: ML configuration
            thread_config: Threading configuration
        """
        self.config = config or ML_CONFIG
        self.thread_config = thread_config or THREAD_CONFIG

    def create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create features from raw parking data.

        Args:
            df: Raw parking data

        Returns:
            DataFrame with extracted features

        Raises:
            DataError: If feature engineering fails
        """
        try:
            # Make a copy to avoid modifying the original
            df_features = df.copy()

            # Sort by datetime to ensure chronological order
            df_features = df_features.sort_values("mvalidtime")

            # Extract datetime features
            self._extract_datetime_features(df_features)

            # Calculate time differences
            df_features["time_diff"] = df_features["mvalidtime"].diff().dt.total_seconds()

            # Create lag features using parallel processing
            df_features = self._create_lag_features(df_features)

            # Calculate rate of change
            df_features["rate_of_change"] = (df_features["free"] - df_features["free_lag_1"]) / df_features["time_diff"]

            # Create target variable: free spaces in one hour
            # 3600 seconds = 1 hour, our interval is 300 seconds, so shift by 12 rows
            df_features["target"] = df_features["free"].shift(-12)

            logger.info(f"Created features for {len(df_features)} rows")
            return df_features

        except Exception as e:
            logger.error(f"Feature engineering failed: {e}")
            raise DataError(f"Feature engineering failed: {e}")

    def _extract_datetime_features(self, df: pd.DataFrame) -> None:
        """
        Extract datetime features from the timestamp column.

        Args:
            df: DataFrame with mvalidtime column

        Modifies df in-place.
        """
        df["hour"] = df["mvalidtime"].dt.hour
        df["day_of_week"] = df["mvalidtime"].dt.dayofweek
        df["day_of_month"] = df["mvalidtime"].dt.day
        df["month"] = df["mvalidtime"].dt.month
        df["year"] = df["mvalidtime"].dt.year

    def _create_lag_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create lagged features in parallel.

        Args:
            df: DataFrame with features

        Returns:
            DataFrame with lag features added
        """
        # Create a temporary DataFrame with just datetime and free
        temp_df = df[["mvalidtime", "free"]].copy()

        # Create lag functions in parallel
        lag_range = range(1, 13)  # Create 12 lags (assuming 5-minute intervals)

        # Use ThreadPoolExecutor for parallel processing
        with ThreadPoolExecutor(max_workers=self.thread_config["max_workers"]) as executor:
            # Create a partial function with the df already specified
            lag_func = partial(self._create_single_lag, df=temp_df)

            # Execute in parallel
            results = list(executor.map(lag_func, lag_range))

        # Combine results
        for lag_df in results:
            temp_df = pd.concat([temp_df, lag_df], axis=1)

        # Add these features back to the original DataFrame
        lag_columns = [col for col in temp_df.columns if "lag" in col]
        df = pd.concat([df, temp_df[lag_columns]], axis=1)

        return df

    def _create_single_lag(self, lag: int, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create a single lag feature.

        Args:
            lag: Lag period
            df: DataFrame

        Returns:
            DataFrame with single lag column
        """
        return pd.DataFrame(
            {f"free_lag_{lag}": df["free"].shift(lag)},
            index=df.index
        )

    def get_feature_columns(self) -> List[str]:
        """
        Get the list of feature columns to use for modeling.

        Returns:
            List of feature column names
        """
        base_features = [
            "hour",
            "day_of_week",
            "day_of_month",
            "month",
            "year",
            "free",
            "occupied",
            "rate_of_change",
        ]

        # Add lag features
        lag_features = [f"free_lag_{i}" for i in range(1, 13)]

        return base_features + lag_features