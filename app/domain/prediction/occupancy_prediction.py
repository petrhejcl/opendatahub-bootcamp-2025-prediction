# app/domain/prediction/occupancy_prediction.py
from datetime import datetime
import pandas as pd
import pickle as pkl
from typing import Tuple
from ..models.prediction import PredictionFeatures, PredictionResult
from ...data_access.model_repository import ModelRepository
from ...data_access.parking_repository import ParkingRepository


class OccupancyPredictor:
    def __init__(self, model_repository: ModelRepository, parking_repository: ParkingRepository):
        self._model_repository = model_repository
        self._parking_repository = parking_repository
        self._model = None
        self._feature_cols = None
        self._load_model()

    def _load_model(self):
        self._model = self._model_repository.load_model()
        self._feature_cols = self._model_repository.load_feature_columns()

    def _create_features(self, df: pd.DataFrame) -> pd.DataFrame:
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

        return df

    def _prepare_prediction_data(self, df: pd.DataFrame, prediction_time: datetime) -> PredictionFeatures:
        latest_data = df.iloc[-1:].copy()

        features = PredictionFeatures(
            hour=prediction_time.hour,
            day_of_week=prediction_time.weekday(),
            day_of_month=prediction_time.day,
            month=prediction_time.month,
            year=prediction_time.year,
            free=latest_data["free"].iloc[0],
            occupied=latest_data["occupied"].iloc[0],
            rate_of_change=latest_data["rate_of_change"].iloc[0],
            lag_features={
                i: latest_data[f"free_lag_{i}"].iloc[0]
                for i in range(1, 13)
                if f"free_lag_{i}" in latest_data.columns
            }
        )

        return features

    def predict(self, station_code: str, prediction_time: datetime) -> PredictionResult:
        # Get historical data
        df = self._parking_repository.get_parking_data(station_code)
        if df is None or df.empty:
            raise ValueError("No data available for prediction")

        # Create features
        df_features = self._create_features(df)

        # Prepare prediction data
        features = self._prepare_prediction_data(df_features, prediction_time)

        # Convert features to model input format
        X_pred = pd.DataFrame([{
            "hour": features.hour,
            "day_of_week": features.day_of_week,
            "day_of_month": features.day_of_month,
            "month": features.month,
            "year": features.year,
            "free": features.free,
            "occupied": features.occupied,
            "rate_of_change": features.rate_of_change,
            **{f"free_lag_{k}": v for k, v in features.lag_features.items()}
        }])

        # Make prediction
        predicted_spaces = self._model.predict(X_pred[self._feature_cols])[0]

        return PredictionResult(
            prediction_time=prediction_time,
            predicted_spaces=round(predicted_spaces)
        )