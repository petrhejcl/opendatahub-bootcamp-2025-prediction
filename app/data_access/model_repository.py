# app/data_access/model_repository.py
import pickle as pkl
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
from typing import List, Optional

class ModelRepository:
    def __init__(self, model_path: str = "models/rf.pkl",
                 features_path: str = "models/rf_feature_cols.pkl"):
        self._model_path = Path(model_path)
        self._features_path = Path(features_path)

    def load_model(self) -> Optional[RandomForestRegressor]:
        try:
            with open(self._model_path, "rb") as f:
                return pkl.load(f)
        except FileNotFoundError:
            print(f"Model file not found: {self._model_path}")
            return None

    def load_feature_columns(self) -> Optional[List[str]]:
        try:
            with open(self._features_path, "rb") as f:
                return pkl.load(f)
        except FileNotFoundError:
            print(f"Feature columns file not found: {self._features_path}")
            return None

    def save_model(self, model: RandomForestRegressor):
        self._model_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._model_path, "wb") as f:
            pkl.dump(model, f)

    def save_feature_columns(self, feature_cols: List[str]):
        self._features_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._features_path, "wb") as f:
            pkl.dump(feature_cols, f)

    def model_exists(self) -> bool:
        return self._model_path.exists() and self._features_path.exists()