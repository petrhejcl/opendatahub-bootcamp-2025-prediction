# app/domain/model_training/training_service.py
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from typing import Tuple, Optional
from ...data_access.model_repository import ModelRepository


class ModelTrainingService:
    def __init__(self, model_repository: ModelRepository):
        self._model_repository = model_repository

    def create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create features for ML model"""
        df = df.copy()

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
        df["rate_of_change"] = df["rate_of_change"].fillna(0)

        # Create target variable: free spaces in one hour (12 periods ahead)
        df["target"] = df["free"].shift(-12)

        return df

    def train_model(self, df: pd.DataFrame) -> Tuple[RandomForestRegressor, list]:
        """Train the Random Forest model"""

        # Create features
        df_features = self.create_features(df)

        # Feature columns for training
        feature_cols = [
            "hour", "day_of_week", "day_of_month", "month", "year",
            "free", "occupied", "rate_of_change"
        ]

        # Add lag features
        lag_cols = [col for col in df_features.columns if "lag" in col]
        feature_cols.extend(lag_cols)

        # Remove rows with NaN
        clean_df = df_features.dropna()

        if clean_df.empty:
            raise ValueError("No valid data for training after feature engineering")

        # Split features and target
        X = clean_df[feature_cols]
        y = clean_df["target"]

        # Split into training and validation sets
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # Create and train the model
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)

        # Evaluate the model
        train_score = model.score(X_train, y_train)
        val_score = model.score(X_val, y_val)

        print(f"Training R² score: {train_score:.4f}")
        print(f"Validation R² score: {val_score:.4f}")

        # Save model and features
        self._model_repository.save_model(model)
        self._model_repository.save_feature_columns(feature_cols)

        return model, feature_cols