import pickle
from pathlib import Path
from typing import Any, Optional, Tuple, List
import logging

from config.settings import ML_CONFIG
from core.exceptions import ModelError

logger = logging.getLogger("parking_prediction")


class ModelRepository:
    """Repository for storing and retrieving ML models."""

    def __init__(self, config: dict = None):
        """
        Initialize the model repository.

        Args:
            config: ML configuration
        """
        self.config = config or ML_CONFIG
        self.model_path = Path(self.config["model_path"])
        self.feature_cols_path = Path(self.config["feature_cols_path"])

        # Ensure the directory exists
        self.model_path.parent.mkdir(parents=True, exist_ok=True)

    def save_model(self, model: Any, feature_cols: List[str]) -> Tuple[Path, Path]:
        """
        Save a model and its feature columns.

        Args:
            model: Trained model
            feature_cols: List of feature column names

        Returns:
            Tuple of paths where model and feature columns were saved

        Raises:
            ModelError: If saving fails
        """
        try:
            # Save model
            with open(self.model_path, "wb") as f:
                pickle.dump(model, f)

            # Save feature columns
            with open(self.feature_cols_path, "wb") as f:
                pickle.dump(feature_cols, f)

            logger.info(f"Saved model to {self.model_path} and feature columns to {self.feature_cols_path}")
            return self.model_path, self.feature_cols_path

        except Exception as e:
            logger.error(f"Failed to save model: {e}")
            raise ModelError(f"Failed to save model: {e}")

    def load_model(self) -> Tuple[Any, List[str]]:
        """
        Load a model and its feature columns.

        Returns:
            Tuple of (model, feature_columns)

        Raises:
            ModelError: If loading fails
        """
        try:
            # Check if model exists
            if not self.model_path.exists() or not self.feature_cols_path.exists():
                logger.warning("Model or feature columns file not found")
                raise ModelError("Model files not found")

            # Load model
            with open(self.model_path, "rb") as f:
                model = pickle.load(f)

            # Load feature columns
            with open(self.feature_cols_path, "rb") as f:
                feature_cols = pickle.load(f)

            logger.info(f"Loaded model from {self.model_path} and feature columns from {self.feature_cols_path}")
            return model, feature_cols

        except Exception as e:
            if isinstance(e, ModelError):
                raise
            logger.error(f"Failed to load model: {e}")
            raise ModelError(f"Failed to load model: {e}")

    def model_exists(self) -> bool:
        """
        Check if a model and feature columns exist.

        Returns:
            True if both model and feature columns exist, False otherwise
        """
        return self.model_path.exists() and self.feature_cols_path.exists()