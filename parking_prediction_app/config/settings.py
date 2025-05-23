import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base project directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data_files"
MODEL_DIR = BASE_DIR / "models"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
MODEL_DIR.mkdir(exist_ok=True)

# API configuration
API_CONFIG = {
    "base_url": "https://mobility.api.opendatahub.com",
    "auth_url": "https://auth.opendatahub.com/auth/realms/noi/protocol/openid-connect/token",
    "client_id": os.getenv("CLIENT_ID", "opendatahub-bootcamp-2025"),
    "client_secret": os.getenv("CLIENT_SECRET", "QiMsLjDpLi5ffjKRkI7eRgwOwNXoU9l1"),
    "timeout": 30,  # API request timeout in seconds
    "max_retries": 3,  # Number of retries for failed requests
}

# Data processing configurations
DATA_CONFIG = {
    "default_csv_path": DATA_DIR / "parking.csv",
    "date_format": "%Y-%m-%d",
    "datetime_format": "%Y-%m-%d %H:%M:%S",
}

# Machine learning configurations
ML_CONFIG = {
    "model_path": MODEL_DIR / "rf.pkl",
    "feature_cols_path": MODEL_DIR / "rf_feature_cols.pkl",
    "test_size": 0.2,
    "random_state": 42,
    "n_estimators": 100,
    "n_jobs": -1,  # Use all available CPU cores
}

# Threading configurations
THREAD_CONFIG = {
    "max_workers": 4,  # Maximum number of worker threads
    "data_chunk_size": 1000,  # Process data in chunks of this size
}

# UI configurations
UI_CONFIG = {
    "page_title": "Free Parking Spots Prediction",
    "page_layout": "wide",
}

def get_config() -> Dict[str, Any]:
    """Return all configuration settings."""
    return {
        "api": API_CONFIG,
        "data": DATA_CONFIG,
        "ml": ML_CONFIG,
        "thread": THREAD_CONFIG,
        "ui": UI_CONFIG,
    }