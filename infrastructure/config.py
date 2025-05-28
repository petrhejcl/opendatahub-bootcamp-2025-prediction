# infrastructure/config.py
from dataclasses import dataclass
from typing import Optional


@dataclass
class OpenDataHubConfig:
    client_id: str
    client_secret: str
    token_url: str
    base_url: str


@dataclass
class ModelConfig:
    model_path: str = "rf.pkl"
    features_path: str = "rf_feature_cols.pkl"


@dataclass
class AppConfig:
    csv_file_path: str = "parking.csv"
    opendatahub: OpenDataHubConfig = None
    model: ModelConfig = None

    def __post_init__(self):
        if self.opendatahub is None:
            self.opendatahub = OpenDataHubConfig(
                client_id="your_client_id",
                client_secret="your_client_secret",
                token_url="https://auth.opendatahub.com/auth/realms/noi/protocol/openid-connect/token",
                base_url="https://mobility.api.opendatahub.com/v2"
            )

        if self.model is None:
            self.model = ModelConfig()