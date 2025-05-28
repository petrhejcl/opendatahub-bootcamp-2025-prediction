# infrastructure/services/sklearn_model_training_service.py
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from typing import List, Tuple, Any
from domain.entities import ParkingData, ModelPerformance
from domain.interfaces import IModelTrainingService
from infrastructure.services.pandas_data_processing_service import PandasDataProcessingService


class SklearnModelTrainingService(IModelTrainingService):
    def __init__(self, data_processing_service: PandasDataProcessingService):
        self.data_processing_service = data_processing_service

    def train_model(self, parking_data: List[ParkingData]) -> Tuple[Any, List[str]]:
        if not parking_data:
            raise ValueError("No data provided for training")

        # Create features
        df = self.data_processing_service.create_features(parking_data)
        X, y, feature_cols = self.data_processing_service.prepare_training_data(df)

        # Split data
        X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

        # Train model
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)

        return model, feature_cols

    def evaluate_model(self, model: Any, feature_columns: List[str], parking_data: List[ParkingData]) -> ModelPerformance:
        df = self.data_processing_service.create_features(parking_data)
        clean_df = df.dropna(subset=["target"] + feature_columns)

        if clean_df.empty:
            raise ValueError("No valid data for evaluation")

        X = clean_df[feature_columns]
        y_actual = clean_df["target"]
        y_pred = model.predict(X)

        # Calculate metrics
        mae = float(np.mean(np.abs(y_pred - y_actual)))
        rmse = float(np.sqrt(np.mean((y_pred - y_actual) ** 2)))

        return ModelPerformance(
            actual_values=y_actual.tolist(),
            predicted_values=y_pred.tolist(),
            timestamps=clean_df["mvalidtime"].tolist(),
            mae=mae,
            rmse=rmse
        )