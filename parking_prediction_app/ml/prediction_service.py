import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, Any, List, Dict
import logging

from config.settings import ML_CONFIG
from core.exceptions import ModelError
from ml.model_repository import ModelRepository
from ml.feature_engineering import FeatureEngineer

logger = logging.getLogger("parking_prediction")


class PredictionService:
    """Service for making parking predictions."""

    def __init__(self, config: dict = None, model_repo: Optional[ModelRepository] = None):
        """
        Initialize the prediction service.

        Args:
            config: ML configuration
            model_repo: Model repository instance
        """
        self.config = config or ML_CONFIG
        self.model_repo = model_repo or ModelRepository()
        self.feature_engineer = FeatureEngineer()
        self._model = None
        self._feature_cols = None

    def _load_model_if_needed(self) -> None:
        """Load the model if it hasn't been loaded yet."""
        if self._model is None or self._feature_cols is None:
            try:
                self._model, self._feature_cols = self.model_repo.load_model()
                logger.info("Model loaded successfully for predictions")
            except Exception as e:
                logger.error(f"Failed to load model: {e}")
                raise ModelError(f"Failed to load model for predictions: {e}")

    def predict_future(self, df: pd.DataFrame, prediction_time: Optional[datetime] = None) -> tuple[datetime, int]:
        """
        Predict future parking availability for a specific time.

        Args:
            df: DataFrame with historical data
            prediction_time: Time to make prediction for (default: 1 hour from latest data)

        Returns:
            Tuple of (prediction_time, predicted_spaces)

        Raises:
            ModelError: If prediction fails
        """
        try:
            # Load model if needed
            self._load_model_if_needed()

            if prediction_time is None:
                # Use the last timestamp in the dataset plus one hour
                last_time = df["mvalidtime"].iloc[-1]
                prediction_time = last_time + timedelta(hours=1)

            # Get the most recent complete row of data to use as a base
            latest_data = df.iloc[-1:].copy()

            # Create a new row for the prediction time
            prediction_row = latest_data.copy()
            prediction_row["mvalidtime"] = prediction_time

            # Update datetime features for the custom time
            prediction_row["hour"] = prediction_time.hour
            prediction_row["day_of_week"] = prediction_time.dayofweek
            prediction_row["day_of_month"] = prediction_time.day
            prediction_row["month"] = prediction_time.month
            prediction_row["year"] = prediction_time.year

            # Use latest available values for lagged features and other time-dependent features
            # (we're making a prediction for a specific time point, not a time series)

            # Make sure we have all required features
            missing_cols = set(self._feature_cols) - set(prediction_row.columns)
            for col in missing_cols:
                prediction_row[col] = 0

            # Make prediction
            X_pred = prediction_row[self._feature_cols]
            predicted_spaces = self._model.predict(X_pred)[0]

            # Ensure prediction is non-negative and round to integer
            predicted_spaces = max(0, round(predicted_spaces))

            logger.info(f"Predicted {predicted_spaces} free spaces for {prediction_time}")
            return prediction_time, predicted_spaces

        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            raise ModelError(f"Prediction failed: {e}")

    def predict_multiple_times(self, df: pd.DataFrame,
                               prediction_times: List[datetime]) -> Dict[datetime, int]:
        """
        Make predictions for multiple times.

        Args:
            df: DataFrame with historical data
            prediction_times: List of times to make predictions for

        Returns:
            Dictionary mapping prediction times to predicted spaces

        Raises:
            ModelError: If prediction fails
        """
        try:
            # Load model if needed
            self._load_model_if_needed()

            predictions = {}

            for pred_time in prediction_times:
                _, predicted_spaces = self.predict_future(df, pred_time)
                predictions[pred_time] = predicted_spaces

            logger.info(f"Made predictions for {len(prediction_times)} time points")
            return predictions

        except Exception as e:
            logger.error(f"Multiple predictions failed: {e}")
            raise ModelError(f"Multiple predictions failed: {e}")

    def is_model_available(self) -> bool:
        """
        Check if a trained model is available for predictions.

        Returns:
            True if model is available, False otherwise
        """
        return self.model_repo.model_exists()