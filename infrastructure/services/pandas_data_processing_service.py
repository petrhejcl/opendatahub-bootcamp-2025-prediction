# infrastructure/services/pandas_data_processing_service.py
import pandas as pd
import numpy as np
from typing import List, Tuple, Any
from datetime import datetime
from domain.entities import ParkingData
from domain.interfaces import IDataProcessingService


class PandasDataProcessingService(IDataProcessingService):
    """Implementazione concreta usando pandas - Infrastructure layer"""

    def create_features(self, parking_data: List[ParkingData]) -> Any:
        """Restituisce Any invece di DataFrame per rispettare l'interfaccia"""
        if not parking_data:
            return pd.DataFrame()

        print(f"Processing {len(parking_data)} parking data points")

        # Convert to DataFrame
        data = []
        for item in parking_data:
            data.append({
                'mvalidtime': item.timestamp,
                'free': item.free_spaces,
                'occupied': item.occupied_spaces
            })

        df = pd.DataFrame(data)
        df = df.sort_values("mvalidtime").reset_index(drop=True)

        print(f"Initial dataframe shape: {df.shape}")
        print(f"Date range: {df['mvalidtime'].min()} to {df['mvalidtime'].max()}")

        # Remove duplicates and handle missing values
        df = df.drop_duplicates(subset=['mvalidtime']).reset_index(drop=True)
        df['free'] = df['free'].fillna(0)
        df['occupied'] = df['occupied'].fillna(0)

        # Extract datetime features
        df["hour"] = df["mvalidtime"].dt.hour
        df["day_of_week"] = df["mvalidtime"].dt.dayofweek
        df["day_of_month"] = df["mvalidtime"].dt.day
        df["month"] = df["mvalidtime"].dt.month
        df["year"] = df["mvalidtime"].dt.year

        # Calculate time differences in hours for better handling
        df["time_diff"] = df["mvalidtime"].diff().dt.total_seconds() / 3600.0  # Convert to hours
        df["time_diff"] = df["time_diff"].fillna(1.0)  # Fill first value with 1 hour

        # Create lagged features (reduce number of lags if data is limited)
        max_lags = min(12, len(df) // 4)  # Ensure we don't use too many lags for small datasets
        for i in range(1, max_lags + 1):
            df[f"free_lag_{i}"] = df["free"].shift(i)

        # Calculate rate of change (handle division by zero)
        df["rate_of_change"] = (df["free"] - df["free_lag_1"]) / df["time_diff"]
        df["rate_of_change"] = df["rate_of_change"].fillna(0).replace([np.inf, -np.inf], 0)

        # Create rolling statistics for more robust features
        if len(df) > 5:
            df["free_rolling_mean_3"] = df["free"].rolling(window=3, min_periods=1).mean()
            df["free_rolling_std_3"] = df["free"].rolling(window=3, min_periods=1).std().fillna(0)
        else:
            df["free_rolling_mean_3"] = df["free"]
            df["free_rolling_std_3"] = 0

        # Create target variable (predict 12 steps ahead, or fewer if data is limited)
        target_shift = min(12, len(df) // 3) if len(df) > 12 else 1
        df["target"] = df["free"].shift(-target_shift)

        print(f"Features created. Final shape: {df.shape}")
        print(f"Non-null target values: {df['target'].notna().sum()}")

        return df  # Restituisce DataFrame ma tipizzato come Any

    def prepare_training_data(self, processed_data: Any) -> Tuple[Any, Any, List[str]]:
        """Prepara dati per training - processed_data è il DataFrame dal metodo precedente"""
        df = processed_data  # Cast implicito da Any a DataFrame

        # Base feature columns
        feature_cols = [
            "hour", "day_of_week", "day_of_month", "month", "year",
            "free", "occupied", "rate_of_change"
        ]

        # Add rolling features if they exist
        if "free_rolling_mean_3" in df.columns:
            feature_cols.extend(["free_rolling_mean_3", "free_rolling_std_3"])

        # Add lag features that exist
        lag_cols = [col for col in df.columns if "lag" in col and col in df.columns]
        feature_cols.extend(lag_cols)

        print(f"Selected feature columns: {feature_cols}")

        # Remove rows with NaN in target or essential features
        essential_cols = ["target"] + feature_cols
        clean_df = df.dropna(subset=essential_cols)

        if clean_df.empty:
            raise ValueError("No valid data after preprocessing. The dataset might be too small or contain too many missing values.")

        print(f"Clean data shape: {clean_df.shape}")

        # Ensure all feature columns exist
        missing_cols = set(feature_cols) - set(clean_df.columns)
        if missing_cols:
            print(f"Warning: Missing feature columns: {missing_cols}")
            feature_cols = [col for col in feature_cols if col in clean_df.columns]

        X = clean_df[feature_cols]
        y = clean_df["target"]

        # Final validation
        if X.isna().any().any():
            print("Warning: Found NaN values in features, filling with 0")
            X = X.fillna(0)

        print(f"Final training data - X shape: {X.shape}, y shape: {y.shape}")
        print(f"Feature columns used: {len(feature_cols)}")

        return X, y, feature_cols