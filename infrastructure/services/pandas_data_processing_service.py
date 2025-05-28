# infrastructure/services/pandas_data_processing_service.py
import pandas as pd
import numpy as np
from typing import List, Tuple
from datetime import datetime
from domain.entities import ParkingData
from application.interfaces import IDataProcessingService


class PandasDataProcessingService(IDataProcessingService):
    def create_features(self, parking_data: List[ParkingData]) -> pd.DataFrame:
        if not parking_data:
            return pd.DataFrame()

        # Convert to DataFrame
        data = []
        for item in parking_data:
            data.append({
                'mvalidtime': item.timestamp,
                'free': item.free_spaces,
                'occupied': item.occupied_spaces
            })

        df = pd.DataFrame(data)
        df = df.sort_values("mvalidtime")

        # Extract datetime features
        df["hour"] = df["mvalidtime"].dt.hour
        df["day_of_week"] = df["mvalidtime"].dt.dayofweek
        df["day_of_month"] = df["mvalidtime"].dt.day
        df["month"] = df["mvalidtime"].dt.month
        df["year"] = df["mvalidtime"].dt.year

        # Calculate time differences
        df["time_diff"] = df["mvalidtime"].diff().dt.total_seconds()

        # Create lagged features
        for i in range(1, 13):
            df[f"free_lag_{i}"] = df["free"].shift(i)

        # Calculate rate of change
        df["rate_of_change"] = (df["free"] - df["free_lag_1"]) / df["time_diff"]

        # Create target variable
        df["target"] = df["free"].shift(-12)

        return df

    def prepare_training_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, List[str]]:
        feature_cols = [
            "hour", "day_of_week", "day_of_month", "month", "year",
            "free", "occupied", "rate_of_change"
        ]

        lag_cols = [col for col in df.columns if "lag" in col]
        feature_cols.extend(lag_cols)

        clean_df = df.dropna()
        if clean_df.empty:
            raise ValueError("No valid data after preprocessing")

        X = clean_df[feature_cols]
        y = clean_df["target"]

        return X, y, feature_cols


