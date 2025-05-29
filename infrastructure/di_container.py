# infrastructure/di_container.py
from application.services import ParkingApplicationService
from infrastructure.config import AppConfig
from infrastructure.external_apis.opendatahub_client import OpenDataHubClient
from infrastructure.repositories.csv_parking_data_repository import CsvParkingDataRepository
from infrastructure.repositories.file_model_repository import FileModelRepository
from infrastructure.repositories.opendatahub_station_repository import OpenDataHubStationRepository
from infrastructure.services.ml_prediction_service import MLPredictionService
from infrastructure.services.pandas_data_processing_service import PandasDataProcessingService
from infrastructure.services.sklearn_model_training_service import SklearnModelTrainingService


class DIContainer:
    def __init__(self, config: AppConfig = None):
        self.config = config or AppConfig()

        # Infrastructure dependencies
        self._api_client = OpenDataHubClient(self.config.opendatahub)

        # Repository implementations
        self._station_repo = OpenDataHubStationRepository(self._api_client)
        self._data_repo = CsvParkingDataRepository(self._api_client, self.config.csv_file_path)
        self._model_repo = FileModelRepository(self.config.model.model_path, self.config.model.features_path)

        # Service implementations
        self._data_processing = PandasDataProcessingService()
        self._training_service = SklearnModelTrainingService(self._data_processing)
        self._prediction_service = MLPredictionService(self._model_repo, self._data_processing)

    def create_application_service(self) -> ParkingApplicationService:
        return ParkingApplicationService(
            station_repository=self._station_repo,
            data_repository=self._data_repo,
            model_repository=self._model_repo,
            data_processing_service=self._data_processing,
            training_service=self._training_service,
            prediction_service=self._prediction_service
        )
