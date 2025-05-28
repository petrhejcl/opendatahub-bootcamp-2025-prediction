# application/interfaces.py
from abc import ABC, abstractmethod
from typing import Any, List, Tuple, Optional
from datetime import datetime
import pandas as pd
from domain.entities import ParkingData, ModelPerformance


class IDataProcessingService(ABC):
    @abstractmethod
    def create_features(self, parking_data: List[ParkingData]) -> pd.DataFrame:
        pass

    @abstractmethod
    def prepare_training_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, List[str]]:
        pass


class IModelTrainingService(ABC):
    @abstractmethod
    def train_model(self, parking_data: List[ParkingData]) -> Tuple[Any, List[str]]:
        pass

    @abstractmethod
    def evaluate_model(self, model: Any, feature_columns: List[str], parking_data: List[ParkingData]) -> ModelPerformance:
        pass


class IPredictionService(ABC):
    @abstractmethod
    def predict_free_spaces(self, parking_data: List[ParkingData], prediction_time: datetime, use_stored_model: bool) -> Optional[int]:
        pass
