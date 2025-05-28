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

        print(f"Training with {len(parking_data)} data points")

        # Create features
        df = self.data_processing_service.create_features(parking_data)
        print(f"Created features dataframe with shape: {df.shape}")

        if df.empty:
            raise ValueError("No features could be created from the data")

        X, y, feature_cols = self.data_processing_service.prepare_training_data(df)
        print(f"Training data shape: X={X.shape}, y={y.shape}")
        print(f"Feature columns: {feature_cols}")

        if X.empty or y.empty:
            raise ValueError("No valid training data after preprocessing. Check if data has sufficient history for lag features.")

        # Split data for validation
        if len(X) < 4:  # Need at least 4 samples to split
            X_train, y_train = X, y
            print("Using all data for training (insufficient data for validation split)")
        else:
            X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)
            print(f"Split data: train={len(X_train)}, val={len(X_val)}")

        # Train model
        model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
        model.fit(X_train, y_train)
        print("Model training completed successfully")

        return model, feature_cols

    def evaluate_model(self, model: Any, feature_columns: List[str], parking_data: List[ParkingData]) -> ModelPerformance:
        if not parking_data:
            raise ValueError("No data provided for evaluation")

        df = self.data_processing_service.create_features(parking_data)
        clean_df = df.dropna(subset=["target"] + feature_columns)

        if clean_df.empty:
            raise ValueError("No valid data for evaluation after removing NaN values")

        X = clean_df[feature_columns]
        y_actual = clean_df["target"]
        y_pred = model.predict(X)

        # Calculate metrics
        mae = float(np.mean(np.abs(y_pred - y_actual)))
        rmse = float(np.sqrt(np.mean((y_pred - y_actual) ** 2)))

        print(f"Model evaluation - MAE: {mae:.2f}, RMSE: {rmse:.2f}")

        return ModelPerformance(
            actual_values=y_actual.tolist(),
            predicted_values=y_pred.tolist(),
            timestamps=clean_df["mvalidtime"].tolist(),
            mae=mae,
            rmse=rmse
        )