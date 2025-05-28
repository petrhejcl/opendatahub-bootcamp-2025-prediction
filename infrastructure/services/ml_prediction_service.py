# infrastructure/services/ml_prediction_service.py
import pandas as pd
from datetime import datetime
from typing import Optional, Any, List
from domain.entities import ParkingData
from domain.repositories import IMLModelRepository
from application.interfaces import IPredictionService, IDataProcessingService


class MLPredictionService(IPredictionService):
    def __init__(self, model_repository: IMLModelRepository, data_processing_service: IDataProcessingService):
        self.model_repository = model_repository
        self.data_processing_service = data_processing_service

    def predict_free_spaces(self, parking_data: List[ParkingData], prediction_time: datetime, use_stored_model: bool = True) -> Optional[int]:
        try:
            if not parking_data:
                return None

            # Create features
            df = self.data_processing_service.create_features(parking_data)

            # Load model
            if use_stored_model and self.model_repository.model_exists():
                model, feature_cols = self.model_repository.load_model()
            else:
                raise ValueError("No trained model available")

            # Prepare prediction data
            latest_data = df.iloc[-1:].copy()
            prediction_row = latest_data.copy()
            prediction_row["mvalidtime"] = prediction_time

            # Update datetime features
            prediction_row["hour"] = prediction_time.hour
            prediction_row["day_of_week"] = prediction_time.dayofweek
            prediction_row["day_of_month"] = prediction_time.day
            prediction_row["month"] = prediction_time.month
            prediction_row["year"] = prediction_time.year

            # Handle missing features
            missing_cols = set(feature_cols) - set(prediction_row.columns)
            for col in missing_cols:
                prediction_row[col] = 0

            X_pred = prediction_row[feature_cols]
            predicted_spaces = model.predict(X_pred)[0]

            return max(0, round(predicted_spaces))

        except Exception as e:
            print(f"Prediction error: {e}")
            return None
