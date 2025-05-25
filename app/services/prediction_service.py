from datetime import datetime
from app.domain.prediction.occupancy_prediction import OccupancyPredictor
from app.data_access.model_repository import ModelRepository
from app.data_access.parking_repository import ParkingRepository
from app.domain.models.prediction import PredictionResult

class PredictionService:
    def __init__(self,
                 parking_repository: ParkingRepository,
                 model_repository: ModelRepository):
        self._predictor = OccupancyPredictor(model_repository, parking_repository)

    def predict_free_spaces(self, station_code: str,
                          prediction_datetime: datetime) -> PredictionResult:
        return self._predictor.predict(station_code, prediction_datetime)