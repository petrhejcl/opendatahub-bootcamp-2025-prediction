# app/services/prediction_service.py
from datetime import datetime
from ..domain.prediction.occupancy_prediction import OccupancyPredictor
from ..data_access.model_repository import ModelRepository
from ..data_access.parking_repository import ParkingRepository
from ..domain.models.prediction import PredictionResult

class PredictionService:
    def __init__(self,
                 parking_repository: ParkingRepository = None,
                 model_repository: ModelRepository = None):
        self._parking_repository = parking_repository or ParkingRepository()
        self._model_repository = model_repository or ModelRepository()
        self._predictor = OccupancyPredictor(self._model_repository, self._parking_repository)

    def predict_free_spaces(self, station_code: str,
                          prediction_datetime: datetime) -> PredictionResult:
        return self._predictor.predict(station_code, prediction_datetime)