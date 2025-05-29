# infrastructure/repositories/csv_parking_data_repository.py
import os
from datetime import datetime
from typing import List

import pandas as pd

from domain.entities import ParkingData
from domain.repositories import IParkingDataRepository
from infrastructure.external_apis.opendatahub_client import OpenDataHubClient


class CsvParkingDataRepository(IParkingDataRepository):
    """Repository che gestisce i dati usando un file CSV come storage persistente"""

    def __init__(self, api_client: OpenDataHubClient, csv_file_path: str = "data/parking.csv"):
        self.api_client = api_client
        self.csv_file_path = csv_file_path
        self._ensure_csv_exists()

    def _ensure_csv_exists(self):
        """Crea il file CSV se non esiste"""
        # Assicurati che la directory esista
        os.makedirs(os.path.dirname(self.csv_file_path), exist_ok=True)

        if not os.path.exists(self.csv_file_path):
            empty_df = pd.DataFrame(columns=[
                'station_code', 'timestamp', 'free_spaces', 'occupied_spaces'
            ])
            empty_df.to_csv(self.csv_file_path, index=False)
            print(f"Created empty CSV file: {self.csv_file_path}")

    def get_parking_data(self, station_code: str, start_date: datetime, end_date: datetime) -> List[ParkingData]:
        """
        Recupera dati dal CSV. Se non esistono per il range esatto richiesto,
        fa fetch da OpenDataHub e aggiorna il CSV.
        """
        print(f"Getting parking data for station {station_code} from {start_date} to {end_date}")

        # Prima controlla se abbiamo già i dati per questo range esatto
        existing_data = self._read_csv_data(station_code, start_date, end_date)

        if existing_data:
            print(f"Found {len(existing_data)} existing records in CSV for exact range")
            return existing_data

        # Se non abbiamo dati per questo range, fetch da API
        print("No data found for this exact range, fetching from OpenDataHub...")
        self._fetch_and_update_csv(station_code, start_date, end_date)

        # Rileggi i dati dopo l'aggiornamento
        return self._read_csv_data(station_code, start_date, end_date)

    def force_refresh_data(self, station_code: str, start_date: datetime, end_date: datetime) -> List[ParkingData]:
        """
        Forza il refresh dei dati dall'API indipendentemente da cosa c'è nel CSV
        """
        print(f"Force refreshing data for station {station_code} from {start_date} to {end_date}")

        # Fetch direttamente dall'API senza controllare il CSV
        self._fetch_and_update_csv(station_code, start_date, end_date)

        # Ritorna i dati aggiornati
        return self._read_csv_data(station_code, start_date, end_date)

    def get_all_stations_in_csv(self) -> List[str]:
        """Restituisce tutte le stazioni presenti nel CSV"""
        try:
            if not os.path.exists(self.csv_file_path):
                return []

            df = pd.read_csv(self.csv_file_path)
            if df.empty:
                return []

            return sorted(df['station_code'].astype(str).unique().tolist())
        except Exception as e:
            print(f"Error getting stations from CSV: {e}")
            return []

    def get_data_date_range(self, station_code: str) -> tuple:
        """Restituisce il range di date disponibili per una stazione nel CSV"""
        try:
            if not os.path.exists(self.csv_file_path):
                return None, None

            df = pd.read_csv(self.csv_file_path)
            if df.empty:
                return None, None

            station_df = df[df['station_code'].astype(str) == str(station_code)]
            if station_df.empty:
                return None, None

            station_df['timestamp'] = pd.to_datetime(station_df['timestamp'])
            min_date = station_df['timestamp'].min()
            max_date = station_df['timestamp'].max()

            return min_date, max_date
        except Exception as e:
            print(f"Error getting date range: {e}")
            return None, None

    def _read_csv_data(self, station_code: str, start_date: datetime, end_date: datetime) -> List[ParkingData]:
        """Legge i dati dal file CSV per la stazione e periodo specificati"""
        try:
            if not os.path.exists(self.csv_file_path):
                print(f"CSV file {self.csv_file_path} does not exist")
                return []

            df = pd.read_csv(self.csv_file_path)
            print(f"CSV contains {len(df)} total records")

            if df.empty:
                print("CSV is empty")
                return []

            df['station_code'] = df['station_code'].astype(str)
            station_code_str = str(station_code)

            print(f"Looking for station_code: '{station_code_str}' (type: {type(station_code_str)})")
            print(f"Unique station codes in CSV: {df['station_code'].unique()}")

            # Filtra per stazione
            station_df = df[df['station_code'] == station_code_str]
            print(f"Found {len(station_df)} records for station {station_code_str}")

            if station_df.empty:
                print(f"No records found for station {station_code_str}")
                return []

            # Converti timestamp e filtra per date
            station_df = station_df.copy()

            try:
                station_df['timestamp'] = pd.to_datetime(station_df['timestamp'], format='%Y-%m-%dT%H:%M:%S')
            except:
                try:
                    station_df['timestamp'] = pd.to_datetime(station_df['timestamp'], format='mixed')
                except:
                    # Fallback to automatic parsing
                    station_df['timestamp'] = pd.to_datetime(station_df['timestamp'])

            print(f"Timestamp range in data: {station_df['timestamp'].min()} to {station_df['timestamp'].max()}")
            print(f"Requested range: {start_date} to {end_date}")

            # Filter by date range
            date_filtered_df = station_df[
                (station_df['timestamp'] >= start_date) &
                (station_df['timestamp'] <= end_date)
            ]

            print(f"After date filtering: {len(date_filtered_df)} records")

            # Converti in oggetti ParkingData
            parking_data = []
            for _, row in date_filtered_df.iterrows():
                try:
                    parking_data.append(ParkingData(
                        timestamp=row['timestamp'],
                        free_spaces=int(row['free_spaces']) if pd.notna(row['free_spaces']) else 0,
                        occupied_spaces=int(row['occupied_spaces']) if pd.notna(row['occupied_spaces']) else 0,
                        station_code=row['station_code']
                    ))
                except Exception as e:
                    print(f"Error converting row to ParkingData: {e}")
                    continue

            return sorted(parking_data, key=lambda x: x.timestamp)

        except Exception as e:
            print(f"Error reading CSV data: {e}")
            import traceback
            traceback.print_exc()
            return []

    def _fetch_and_update_csv(self, station_code: str, start_date: datetime, end_date: datetime):
        """Fetch dati da OpenDataHub e aggiorna il CSV"""
        try:
            # Fetch dai dati API
            start_str = start_date.strftime("%Y-%m-%d")
            end_str = end_date.strftime("%Y-%m-%d")

            print(f"Fetching data from OpenDataHub API for {station_code}: {start_str} to {end_str}")
            api_data = self.api_client.get_parking_data(station_code, start_str, end_str)

            if not api_data:
                print("No data received from API")
                return

            print(f"Received {len(api_data)} measurements from API")

            # Processa i dati API
            new_records = []
            data_dict = {}

            for measurement in api_data:
                timestamp = measurement.get("mvalidtime")
                if not timestamp:
                    continue

                tname = measurement.get("tname")
                mvalue = measurement.get("mvalue")

                if not tname or mvalue is None:
                    continue

                # Group by timestamp
                if timestamp not in data_dict:
                    data_dict[timestamp] = {}
                data_dict[timestamp][tname] = mvalue

            # Converti in record per il CSV
            for mvalidtime, values in data_dict.items():
                try:
                    # Handle different timestamp formats
                    if mvalidtime.endswith('Z'):
                        timestamp = datetime.fromisoformat(mvalidtime.replace('Z', '+00:00'))
                    elif '+' in mvalidtime or mvalidtime.endswith('00'):
                        # Try to parse as ISO format with timezone
                        timestamp = datetime.fromisoformat(mvalidtime)
                    else:
                        # Simple ISO format without timezone
                        timestamp = datetime.fromisoformat(mvalidtime)

                    # Convert to naive datetime for consistency
                    if timestamp.tzinfo is not None:
                        timestamp = timestamp.replace(tzinfo=None)

                    free_spaces = values.get("free", 0)
                    occupied_spaces = values.get("occupied", 0)

                    new_records.append({
                        'station_code': str(station_code),
                        'timestamp': timestamp.strftime('%Y-%m-%dT%H:%M:%S'),  # Consistent format
                        'free_spaces': free_spaces,
                        'occupied_spaces': occupied_spaces
                    })
                except Exception as e:
                    print(f"Error processing timestamp {mvalidtime}: {e}")
                    continue

            if new_records:
                self._replace_csv_data(new_records)
                print(f"Added {len(new_records)} new records to CSV")

        except Exception as e:
            print(f"Error fetching and updating CSV: {e}")

    def _replace_csv_data(self, new_records: List[dict]):
        """Sostituisce i dati esistenti nel CSV con i nuovi record"""
        try:
            # Debug: check what we received
            print(f"Received new_records type: {type(new_records)}")
            print(f"Received new_records content: {new_records}")

            # Ensure new_records is a list
            if not isinstance(new_records, list):
                raise ValueError(f"Expected list, got {type(new_records)}")

            # Crea DataFrame con i nuovi record
            new_df = pd.DataFrame(new_records)

            # Se non ci sono nuovi record, crea un DataFrame vuoto con le colonne corrette
            if new_df.empty:
                new_df = pd.DataFrame(columns=['station_code', 'timestamp', 'free_spaces', 'occupied_spaces'])
            else:
                # Convert timestamp column to datetime
                new_df['timestamp'] = pd.to_datetime(new_df['timestamp'])

                # Rimuovi duplicati nei nuovi dati (mantieni l'ultimo)
                new_df = new_df.drop_duplicates(subset=['station_code', 'timestamp'], keep='last')

                # Ordina per timestamp
                new_df = new_df.sort_values(['station_code', 'timestamp'])

                # Convert back to string with consistent format for CSV storage
                new_df['timestamp'] = new_df['timestamp'].dt.strftime('%Y-%m-%dT%H:%M:%S')

                print(f"Processed {len(new_df)} unique records")

            # Assicurati che la directory esista
            os.makedirs(os.path.dirname(self.csv_file_path), exist_ok=True)

            # Salva nel CSV (sostituisce completamente il file esistente)
            new_df.to_csv(self.csv_file_path, index=False)
            print(f"CSV saved successfully - total records: {len(new_df)}")

        except Exception as e:
            print(f"Error replacing CSV data: {e}")
            import traceback
            traceback.print_exc()
            raise
