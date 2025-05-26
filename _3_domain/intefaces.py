from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple, Optional
import pandas as pd
from datetime import datetime


# Domain Interfaces
class ITokenProvider(ABC):
    @abstractmethod
    def get_token(self, client_id: str, client_secret: str) -> str:
        pass


class IDataRepository(ABC):
    @abstractmethod
    def fetch_parking_data(self, station_code: int, start_date: str, end_date: str, token: str) -> List[Dict[str, Any]]:
        pass


class IDataLoader(ABC):
    @abstractmethod
    def load_data(self, file_path: str) -> pd.DataFrame:
        pass


class IModelPersistence(ABC):
    @abstractmethod
    def save_model(self, model: Any, feature_cols: List[str], model_path: str, cols_path: str) -> None:
        pass

    @abstractmethod
    def load_model(self, model_path: str, cols_path: str) -> Tuple[Any, List[str]]:
        pass


class IVisualizationService(ABC):
    @abstractmethod
    def visualize_parking_data(self, df: pd.DataFrame, output: str) -> None:
        pass


class IPredictionService(ABC):
    @abstractmethod
    def parse_prediction_time(self, time_str: str) -> datetime:
        pass

    @abstractmethod
    def predict_future(self, df: pd.DataFrame, model: Any, feature_cols: List[str],
                       prediction_time: Optional[datetime]) -> Tuple[datetime, int]:
        pass