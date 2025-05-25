from abc import ABC, abstractmethod
from ...services.prediction_service import PredictionService
from ...services.station_service import StationService

class BaseParkingPage(ABC):
    def __init__(self, prediction_service: PredictionService, station_service: StationService):
        self._prediction_service = prediction_service
        self._station_service = station_service

    @abstractmethod
    def render(self):
        pass