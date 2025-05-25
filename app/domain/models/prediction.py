# app/domain/models/prediction.py
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional

@dataclass
class PredictionFeatures:
    hour: int
    day_of_week: int
    day_of_month: int
    month: int
    year: int
    free: int
    occupied: int
    rate_of_change: float
    lag_features: Dict[int, int]

@dataclass
class PredictionResult:
    prediction_time: datetime
    predicted_spaces: int
    confidence_score: Optional[float] = None
