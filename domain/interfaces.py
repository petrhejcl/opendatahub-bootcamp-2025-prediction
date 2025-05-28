# domain/interfaces.py
from abc import ABC, abstractmethod
from typing import Any, List, Tuple, Optional
from datetime import datetime
from domain.entities import ParkingData, ModelPerformance


class IDataProcessingService(ABC):
    """Interface per servizi di elaborazione dati - spostata nel Domain"""
    @abstractmethod
    def create_features(self, parking_data: List[ParkingData]) -> Any:
        """Restituisce un oggetto generico invece di pandas DataFrame"""
        pass

    @abstractmethod
    def prepare_training_data(self, processed_data: Any) -> Tuple[Any, Any, List[str]]:
        """Prepara dati per training - parametri generici"""
        pass


class IModelTrainingService(ABC):
    """Interface per servizi di training modelli"""
    @abstractmethod
    def train_model(self, parking_data: List[ParkingData]) -> Tuple[Any, List[str]]:
        pass

    @abstractmethod
    def evaluate_model(self, model: Any, feature_columns: List[str], parking_data: List[ParkingData]) -> ModelPerformance:
        pass


class IPredictionService(ABC):
    """Interface per servizi di predizione"""
    @abstractmethod
    def predict_free_spaces(self, parking_data: List[ParkingData], prediction_time: datetime, use_stored_model: bool) -> Optional[int]:
        pass