import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from typing import Tuple, Any, List, Dict, Optional
import logging
from concurrent.futures import ThreadPoolExecutor

from config.settings import ML_CONFIG
from core.exceptions import ModelError
from ml.model_repository import ModelRepository
from ml.feature_engineering import FeatureEngineer

logger = logging.getLogger("parking_prediction")


class TrainingService:
    """Service for training machine learning models."""

    def __init__(self, config: dict = None, model_repo: Optional[ModelRepository] = None):
        """
        Initialize the training service.

        Args:
            config: ML configuration
            model_repo: Model repository instance
        """
        self.config = config or ML_CONFIG
        self.model_repo = model_repo or ModelRepository()
        self.feature_engineer = FeatureEngineer()

    def train_model(self, df: pd.DataFrame, save_model: bool = True) -> Tuple[Any, List[str], Dict[str, float]]:
        """
        Train a parking prediction model.

        Args:
            df: DataFrame with features and target
            save_model: Whether to save the trained model

        Returns:
            Tuple of (model, feature_columns, metrics)

        Raises:
            ModelError: If training fails
        """
        try:
            # Get feature columns
            feature_cols = self.feature_engineer.get_feature_columns()

            # Remove rows with NaN (will be at the beginning due to lag features)
            clean_df = df.dropna(subset=["target"] + feature_cols)

            if len(clean_df) == 0:
                raise ModelError("No valid data points available for training")

            # Split features and target
            X = clean_df[feature_cols]
            y = clean_df["target"]

            # Split into training and validation sets
            X_train, X_val, y_train, y_val = train_test_split(
                X, y,
                test_size=self.config["test_size"],
                random_state=self.config["random_state"]
            )

            # Create and train the model with parallel processing
            model = RandomForestRegressor(
                n_estimators=self.config["n_estimators"],
                random_state=self.config["random_state"],
                n_jobs=self.config["n_jobs"]  # Use all available CPU cores
            )

            logger.info(f"Training model on {len(X_train)} samples...")
            model.fit(X_train, y_train)

            # Evaluate the model
            train_score = model.score(X_train, y_train)
            val_score = model.score(X_val, y_val)

            # Predict on validation set and calculate metrics
            y_pred = model.predict(X_val)
            mae = np.mean(np.abs(y_pred - y_val))
            rmse = np.sqrt(np.mean((y_pred - y_val) ** 2))

            metrics = {
                "train_r2": train_score,
                "val_r2": val_score,
                "mae": mae,
                "rmse": rmse
            }

            # Log training results
            logger.info(f"Training completed:")
            logger.info(f"  Training R² score: {train_score:.4f}")
            logger.info(f"  Validation R² score: {val_score:.4f}")
            logger.info(f"  Mean Absolute Error: {mae:.2f} parking spaces")
            logger.info(f"  Root Mean Square Error: {rmse:.2f} parking spaces")

            # Feature importance analysis
            feature_importance = self._analyze_feature_importance(model, feature_cols)
            logger.info("Top 10 most important features:")
            for feature, importance in feature_importance.head(10).values:
                logger.info(f"  {feature}: {importance:.4f}")

            # Save model if requested
            if save_model:
                self.model_repo.save_model(model, feature_cols)
                logger.info("Model saved successfully")

            return model, feature_cols, metrics

        except Exception as e:
            logger.error(f"Model training failed: {e}")
            raise ModelError(f"Model training failed: {e}")

    def _analyze_feature_importance(self, model: RandomForestRegressor, feature_cols: List[str]) -> pd.DataFrame:
        """
        Analyze feature importance from the trained model.

        Args:
            model: Trained RandomForest model
            feature_cols: List of feature column names

        Returns:
            DataFrame with feature importance scores
        """
        feature_importance = pd.DataFrame({
            "Feature": feature_cols,
            "Importance": model.feature_importances_
        }).sort_values("Importance", ascending=False)

        return feature_importance