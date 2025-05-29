# application/services.py
from datetime import datetime
from typing import List, Optional, Tuple, Any

from application.dtos import StationDTO, TrainingRequestDTO, VisualizationDataDTO, ModelPerformanceDTO, CoordinateDTO
from domain.entities import ParkingStation
from domain.interfaces import IDataProcessingService, IModelTrainingService, IPredictionService
from domain.repositories import IParkingStationRepository, IParkingDataRepository, IMLModelRepository


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

    def fetch_parking_data(self, station_code: str, start_date: str, end_date: str, force_refresh: bool = False) -> \
            List[VisualizationDataDTO]:
        """
        Caso d'uso: Recuperare dati parcheggio per visualizzazione
        I dati vengono automaticamente salvati/aggiornati nel CSV repository
        """
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")

            print(f"Fetching parking data for station {station_code} from {start_date} to {end_date}")

            # Il repository CSV gestisce automaticamente il fetch da API se necessario
            if force_refresh and hasattr(self.data_repository, 'force_refresh_data'):
                parking_data = self.data_repository.force_refresh_data(station_code, start_dt, end_dt)
            else:
                parking_data = self.data_repository.get_parking_data(station_code, start_dt, end_dt)

            if not parking_data:
                print("No parking data retrieved")
                return []

            print(f"Retrieved {len(parking_data)} parking data points from CSV repository")

            # Return DTO for visualization
            return [
                VisualizationDataDTO(
                    timestamp=item.timestamp,
                    free_spaces=item.free_spaces,
                    occupied_spaces=item.occupied_spaces,
                    hour=item.timestamp.hour
                ) for item in parking_data
            ]

        except Exception as e:
            print(f"Error fetching parking data: {e}")
            return []

    def train_model(self, training_request: TrainingRequestDTO, force_refresh: bool = False) -> Tuple[Any, List[str]]:
        """
        Caso d'uso: Addestrare modello ML
        Usa i dati dal CSV repository
        """
        try:
            print(f"Training model for station {training_request.station_code}")

            start_dt = datetime.strptime(training_request.start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(training_request.end_date, "%Y-%m-%d")

            # Ottieni i dati dal CSV repository
            if force_refresh and hasattr(self.data_repository, 'force_refresh_data'):
                parking_data = self.data_repository.force_refresh_data(training_request.station_code, start_dt, end_dt)
            else:
                parking_data = self.data_repository.get_parking_data(training_request.station_code, start_dt, end_dt)

            if not parking_data:
                raise ValueError("No data available for training. Please fetch data first.")

            print(f"Training with {len(parking_data)} data points from CSV")

            # Train the model
            model, feature_cols = self.training_service.train_model(parking_data)

            # Save the model
            self.model_repository.save_model(model, feature_cols)
            print("Model trained and saved successfully")

            return model, feature_cols

        except Exception as e:
            print(f"Error training model: {e}")
            raise

    def predict_occupancy(self, station_code: str, prediction_time: datetime, data_start_date: str = None,
                          data_end_date: str = None) -> Optional[int]:
        """
        Caso d'uso: Predire occupazione parcheggio
        Usa i dati dal CSV repository
        """
        try:
            print(f"Predicting occupancy for station {station_code} at {prediction_time}")

            # Se non specificate, usa un range di default (es. ultimi 30 giorni)
            if not data_start_date or not data_end_date:
                from datetime import timedelta
                end_dt = datetime.now()
                start_dt = end_dt - timedelta(days=30)
            else:
                start_dt = datetime.strptime(data_start_date, "%Y-%m-%d")
                end_dt = datetime.strptime(data_end_date, "%Y-%m-%d")

            # Ottieni i dati dal CSV repository
            parking_data = self.data_repository.get_parking_data(station_code, start_dt, end_dt)

            if not parking_data:
                print(f"ERROR: No parking data available for prediction for station {station_code}")
                print(f"Date range: {start_dt} to {end_dt}")
                # Debug: verifica se ci sono dati per questa stazione in generale
                if hasattr(self.data_repository, '_read_csv_data'):
                    # Prova a leggere tutti i dati per la stazione
                    debug_start = datetime.now() - timedelta(days=365)  # Ultimo anno
                    debug_end = datetime.now()
                    debug_data = self.data_repository._read_csv_data(station_code, debug_start, debug_end)
                    print(
                        f"DEBUG: Found {len(debug_data) if debug_data else 0} total records for station {station_code} in last year")
                return None

            print(f"Using {len(parking_data)} data points from CSV for prediction")
            print(f"Data range: {parking_data[0].timestamp} to {parking_data[-1].timestamp}")

            # Verifica che esista un modello
            if not self.model_repository.model_exists():
                print("ERROR: No trained model available for prediction")
                return None

            result = self.prediction_service.predict_free_spaces(
                parking_data,
                prediction_time,
                True
            )

            if result is not None:
                print(f"Prediction result: {result} free spaces")
            else:
                print("Prediction failed")

            return result

        except Exception as e:
            print(f"Error predicting occupancy: {e}")
            return None

    # METODI AGGIUNTI/CORRETTI per la UI:

    def get_visualization_data(self, station_code: str = None, start_date: str = None, end_date: str = None) -> List[
        VisualizationDataDTO]:
        """
        Caso d'uso: Ottenere dati per visualizzazione dal CSV
        Se i parametri non sono forniti, usa dati dall'ultima sessione o valori di default
        """
        try:
            # Gestisci i parametri mancanti
            if not station_code:
                # Prova a ottenere la prima stazione disponibile
                stations_in_csv = self.get_csv_data_info().get('stations', [])
                if not stations_in_csv:
                    return []
                station_code = stations_in_csv[0]

            if not start_date or not end_date:
                # Usa date di default se non specificate
                from datetime import timedelta
                end_dt = datetime.now()
                start_dt = end_dt - timedelta(days=7)  # Ultimi 7 giorni
                start_date = start_dt.strftime("%Y-%m-%d")
                end_date = end_dt.strftime("%Y-%m-%d")

            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")

            parking_data = self.data_repository.get_parking_data(station_code, start_dt, end_dt)

            return [
                VisualizationDataDTO(
                    timestamp=item.timestamp,
                    free_spaces=item.free_spaces,
                    occupied_spaces=item.occupied_spaces,
                    hour=item.timestamp.hour
                ) for item in parking_data
            ]
        except Exception as e:
            print(f"Error getting visualization data: {e}")
            return []

    def evaluate_model_performance(self, station_code: str = None, start_date: str = None, end_date: str = None) -> \
            Optional[ModelPerformanceDTO]:
        """
        Caso d'uso: Valutare performance modello usando dati dal CSV
        """
        if not self.model_repository.model_exists():
            return None

        try:
            print("Evaluating model performance")

            # Gestisci i parametri mancanti
            if not station_code:
                stations_in_csv = self.get_csv_data_info().get('stations', [])
                if not stations_in_csv:
                    return None
                station_code = stations_in_csv[0]

            if not start_date or not end_date:
                from datetime import timedelta
                end_dt = datetime.now()
                start_dt = end_dt - timedelta(days=7)
                start_date = start_dt.strftime("%Y-%m-%d")
                end_date = end_dt.strftime("%Y-%m-%d")

            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")

            # Ottieni i dati dal CSV
            parking_data = self.data_repository.get_parking_data(station_code, start_dt, end_dt)

            if not parking_data:
                print("No data available for evaluation")
                return None

            model, feature_cols = self.model_repository.load_model()
            performance = self.training_service.evaluate_model(model, feature_cols, parking_data)

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

    def get_csv_data_info(self, station_code: str = None) -> dict:
        """
        Caso d'uso: Ottenere informazioni sui dati disponibili nel CSV
        """
        try:
            if hasattr(self.data_repository, 'get_all_stations_in_csv'):
                stations_in_csv = self.data_repository.get_all_stations_in_csv()

                info = {
                    'stations_count': len(stations_in_csv),
                    'stations': stations_in_csv
                }

                if station_code and hasattr(self.data_repository, 'get_data_date_range'):
                    start_date, end_date = self.data_repository.get_data_date_range(station_code)
                    info['date_range'] = {
                        'start': start_date,
                        'end': end_date
                    }

                return info
            else:
                return {'error': 'CSV repository methods not available'}

        except Exception as e:
            return {'error': f'Error getting CSV info: {str(e)}'}

    def force_refresh_station_data(self, station_code: str, start_date: str, end_date: str) -> List[
        VisualizationDataDTO]:
        """
        Caso d'uso: Forzare il refresh dei dati per una stazione
        """
        return self.fetch_parking_data(station_code, start_date, end_date, force_refresh=True)

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
