# infrastructure/repositories/file_model_repository.py
import os
import pickle as pkl
from typing import List, Tuple, Any

from domain.repositories import IMLModelRepository


class FileModelRepository(IMLModelRepository):
    def __init__(self, model_path: str = "rf.pkl", features_path: str = "rf_feature_cols.pkl"):
        self.model_path = model_path
        self.features_path = features_path

    def save_model(self, model: Any, feature_cols: List[str]) -> None:
        try:
            with open(self.model_path, "wb") as f:
                pkl.dump(model, f)
            with open(self.features_path, "wb") as f:
                pkl.dump(feature_cols, f)
        except Exception as e:
            raise Exception(f"Failed to save model: {str(e)}")

    def load_model(self) -> Tuple[Any, List[str]]:
        try:
            with open(self.model_path, "rb") as f:
                model = pkl.load(f)
            with open(self.features_path, "rb") as f:
                feature_cols = pkl.load(f)
            return model, feature_cols
        except FileNotFoundError:
            raise FileNotFoundError("Model files not found. Please train a model first.")
        except Exception as e:
            raise Exception(f"Failed to load model: {str(e)}")

    def model_exists(self) -> bool:
        return os.path.exists(self.model_path) and os.path.exists(self.features_path)
