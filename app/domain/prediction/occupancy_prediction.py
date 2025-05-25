# app/domain/prediction/occupancy_prediction.py
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from typing import Optional
from ..models.prediction import PredictionFeatures, PredictionResult
from ...data_access.model_repository import ModelRepository
from ...data_access.parking_repository import ParkingRepository


class OccupancyPredictor:
    def __init__(self, model_repository: ModelRepository, parking_repository: ParkingRepository):
        self._model_repository = model_repository
        self._parking_repository = parking_repository
        self._model = None
        self._feature_cols = None

    def _load_model(self):
        """Load model and feature columns"""
        self._model = self._model_repository.load_model()
        self._feature_cols = self._model_repository.load_feature_columns()

        if self._model is None or self._feature_cols is None:
            raise ValueError("Model or feature columns not found. Train a model first.")

    def _create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create features for prediction"""
        df = df.copy()

        # Extract datetime features
        df["hour"] = df["mvalidtime"].dt.hour
        df["day_of_week"] = df["mvalidtime"].dt.dayofweek
        df["day_of_month"] = df["mvalidtime"].dt.day
        df["month"] = df["mvalidtime"].dt.month
        df["year"] = df["mvalidtime"].dt.year

        # Calculate time differences
        df["time_diff"] = df["mvalidtime"].diff().dt.total_seconds()

        # Create lag features
        for i in range(1, 13):
            df[f"free_lag_{i}"] = df["free"].shift(i)

        # Calculate rate of change
        df["rate_of_change"] = (df["free"] - df["free_lag_1"]) / df["time_diff"]
        df["rate_of_change"] = df["rate_of_change"].fillna(0)

        return df

    def predict(self, station_code: str, prediction_time: datetime) -> PredictionResult:
        """Make prediction for given station and time"""

        # Load model if not already loaded
        if self._model is None:
            self._load_model()

        # Get historical data (last 7 days)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)

        df = self._parking_repository.get_parking_dataframe(station_code, start_date, end_date)

        if df is None or df.empty:
            raise ValueError("No data available for prediction")

        # Create features
        df_features = self._create_features(df)

        # Get the most recent complete row
        latest_data = df_features.dropna().iloc[-1:].copy()

        if latest_data.empty:
            raise ValueError("No complete data available for prediction")

        # Create prediction row
        prediction_row = latest_data.copy()
        prediction_row["hour"] = prediction_time.hour
        prediction_row["day_of_week"] = prediction_time.weekday()
        prediction_row["day_of_month"] = prediction_time.day
        prediction_row["month"] = prediction_time.month
        prediction_row["year"] = prediction_time.year

        # Ensure all required features are present
        for col in self._feature_cols:
            if col not in prediction_row.columns:
                prediction_row[col] = 0

        # Make prediction
        X_pred = prediction_row[self._feature_cols]
        predicted_spaces = self._model.predict(X_pred)[0]

        return PredictionResult(
            prediction_time=prediction_time,
            predicted_spaces=max(0, round(predicted_spaces))  # Ensure non-negative
        )