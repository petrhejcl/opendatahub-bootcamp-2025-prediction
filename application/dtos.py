# application/dtos.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict


@dataclass
class StationDTO:
    scode: str
    sname: str
    municipality: Optional[str] = None
    scoordinate: Optional[Dict] = None


@dataclass
class TrainingRequestDTO:
    station_code: str
    start_date: str
    end_date: str


@dataclass
class PredictionRequestDTO:
    station_code: str
    prediction_time: datetime


@dataclass
class VisualizationDataDTO:
    timestamp: datetime
    free_spaces: int
    occupied_spaces: int
    hour: int


@dataclass
class ModelPerformanceDTO:
    actual_values: List[float]
    predicted_values: List[float]
    timestamps: List[datetime]
    mae: float
    rmse: float


@dataclass
class CoordinateDTO:
    scode: str
    sname: str
    lat: float
    lon: float