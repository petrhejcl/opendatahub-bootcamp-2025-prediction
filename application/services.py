# application/services.py
from datetime import datetime
from typing import List, Optional, Tuple, Any
from domain.entities import ParkingStation, ParkingData, ModelPerformance
from domain.repositories import IParkingStationRepository, IParkingDataRepository, IMLModelRepository
from domain.interfaces import IDataProcessingService, IModelTrainingService, IPredictionService
from application.dtos import StationDTO, TrainingRequestDTO, VisualizationDataDTO, ModelPerformanceDTO, CoordinateDTO


class ParkingApplicationService:
    """Servizio applicativo - orchestrazione casi d'uso"""

    def __init__(
        self,
        station_repository: IParkingStationRepository,
        data_repository: IParkingDataRepository,
        model_repository: IMLModelRepository,
        data_processing_service: IDataProcessingService,
        training_service: IModelTrainingService,
        prediction_service: IPredictionService
    ):
        self.station_repository = station_repository
        self.data_repository = data_repository
        self.model_repository = model_repository
        self.data_processing_service = data_processing_service
        self.training_service = training_service
        self.prediction_service = prediction_service
        self._current_parking_data: List[ParkingData] = []

    def get_all_stations(self) -> List[StationDTO]:
        """Caso d'uso: Ottenere tutte le stazioni"""
        stations = self.station_repository.get_all_stations()
        return [self._station_to_dto(station) for station in stations]

    def get_station_coordinates(self) -> List[CoordinateDTO]:
        """Caso d'uso: Ottenere coordinate per visualizzazione mappa"""
        stations = self.station_repository.get_all_stations()
        coordinates = []
        for station in stations:
            if station.latitude and station.longitude:
                coordinates.append(CoordinateDTO(
                    scode=station.scode,
                    sname=station.sname,
                    lat=station.latitude,
                    lon=station.longitude
                ))
        return coordinates

    def fetch_parking_data(self, station_code: str, start_date: str, end_date: str) -> List[VisualizationDataDTO]:
        """Caso d'uso: Recuperare dati parcheggio per visualizzazione"""
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")

        parking_data = self.data_repository.get_parking_data(station_code, start_dt, end_dt)
        self._current_parking_data = parking_data

        # Restituisce DTO invece di DataFrame
        return [
            VisualizationDataDTO(
                timestamp=item.timestamp,
                free_spaces=item.free_spaces,
                occupied_spaces=item.occupied_spaces,
                hour=item.timestamp.hour
            ) for item in parking_data
        ]

    def train_model(self, training_request: TrainingRequestDTO) -> Tuple[Any, List[str]]:
        """Caso d'uso: Addestrare modello ML"""
        if not self._current_parking_data:
            self.fetch_parking_data(
                training_request.station_code,
                training_request.start_date,
                training_request.end_date
            )

        model, feature_cols = self.training_service.train_model(self._current_parking_data)
        self.model_repository.save_model(model, feature_cols)
        return model, feature_cols

    def predict_occupancy(self, prediction_time: datetime) -> Optional[int]:
        """Caso d'uso: Predire occupazione parcheggio"""
        if not self._current_parking_data:
            return None

        return self.prediction_service.predict_free_spaces(
            self._current_parking_data,
            prediction_time,
            True
        )

    def get_visualization_data(self) -> List[VisualizationDataDTO]:
        """Caso d'uso: Ottenere dati per visualizzazione"""
        if not self._current_parking_data:
            return []

        return [
            VisualizationDataDTO(
                timestamp=item.timestamp,
                free_spaces=item.free_spaces,
                occupied_spaces=item.occupied_spaces,
                hour=item.timestamp.hour
            ) for item in self._current_parking_data
        ]

    def evaluate_model_performance(self) -> Optional[ModelPerformanceDTO]:
        """Caso d'uso: Valutare performance modello"""
        if not self._current_parking_data or not self.model_repository.model_exists():
            return None

        try:
            model, feature_cols = self.model_repository.load_model()
            performance = self.training_service.evaluate_model(model, feature_cols, self._current_parking_data)

            return ModelPerformanceDTO(
                actual_values=performance.actual_values,
                predicted_values=performance.predicted_values,
                timestamps=performance.timestamps,
                mae=performance.mae,
                rmse=performance.rmse
            )
        except Exception as e:
            print(f"Error evaluating model: {e}")
            return None

    def _station_to_dto(self, station: ParkingStation) -> StationDTO:
        """Converte entità in DTO"""
        scoordinate = None
        if station.latitude and station.longitude:
            scoordinate = {"x": station.longitude, "y": station.latitude}

        return StationDTO(
            scode=station.scode,
            sname=station.sname,
            municipality=station.municipality,
            scoordinate=scoordinate
        )