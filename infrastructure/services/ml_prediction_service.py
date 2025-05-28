# infrastructure/services/ml_prediction_service.py
from datetime import datetime
from typing import Optional, List
import pandas as pd
import numpy as np
from domain.entities import ParkingData
from domain.repositories import IMLModelRepository
from domain.interfaces import IPredictionService, IDataProcessingService


class MLPredictionService(IPredictionService):
    def __init__(self, model_repository: IMLModelRepository, data_processing_service: IDataProcessingService):
        self.model_repository = model_repository
        self.data_processing_service = data_processing_service

    def predict_free_spaces(self, parking_data: List[ParkingData], prediction_time: datetime, use_stored_model: bool = True) -> Optional[int]:
        try:
            if not parking_data:
                print("No parking data provided for prediction")
                return None

            print(f"Making prediction for {prediction_time} with {len(parking_data)} data points")

            # Create features from historical data
            df = self.data_processing_service.create_features(parking_data)
            if df.empty:
                print("No features could be created from parking data")
                return None

            # Load model
            if use_stored_model and self.model_repository.model_exists():
                model, feature_cols = self.model_repository.load_model()
                print(f"Loaded model with {len(feature_cols)} features")
            else:
                raise ValueError("No trained model available")

            # Get the most recent data point as base for prediction
            latest_data = df.iloc[-1:].copy()
            print(f"Using latest data point from: {latest_data['mvalidtime'].iloc[0]}")

            # Create prediction row
            prediction_row = latest_data.copy()
            prediction_row["mvalidtime"] = prediction_time

            # Update datetime features for prediction time
            prediction_row["hour"] = prediction_time.hour
            prediction_row["day_of_week"] = prediction_time.weekday()
            prediction_row["day_of_month"] = prediction_time.day
            prediction_row["month"] = prediction_time.month
            prediction_row["year"] = prediction_time.year

            # Handle missing features by setting them to safe defaults
            missing_cols = set(feature_cols) - set(prediction_row.columns)
            for col in missing_cols:
                if "lag" in col:
                    # For lag features, use the current free spaces value
                    prediction_row[col] = prediction_row["free"].iloc[0] if not prediction_row["free"].empty else 0
                elif "rolling" in col:
                    # For rolling features, use current free spaces
                    prediction_row[col] = prediction_row["free"].iloc[0] if not prediction_row["free"].empty else 0
                else:
                    # For other features, use 0
                    prediction_row[col] = 0
                print(f"Added missing feature {col} with default value")

            # Ensure all features are available and in correct order
            try:
                X_pred = prediction_row[feature_cols]
            except KeyError as e:
                print(f"Missing required features: {e}")
                # Try to create a minimal feature set
                available_features = [col for col in feature_cols if col in prediction_row.columns]
                if not available_features:
                    print("No features available for prediction")
                    return None
                X_pred = prediction_row[available_features]
                print(f"Using {len(available_features)} available features instead of {len(feature_cols)}")

            # Fill any remaining NaN values
            X_pred = X_pred.fillna(0)

            # Make prediction
            predicted_spaces = model.predict(X_pred)[0]
            result = max(0, round(predicted_spaces))

            print(f"Prediction successful: {result} free spaces")
            return result

        except Exception as e:
            print(f"Prediction error: {e}")
            import traceback
            traceback.print_exc()
            return None