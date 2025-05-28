# # infrastructure/ml_models.py
# import pickle as pkl
# import pandas as pd
# import numpy as np
# from sklearn.ensemble import RandomForestRegressor
# from sklearn.model_selection import train_test_split
# from typing import List, Tuple, Optional
# from datetime import datetime, timedelta
#
# from domain.interfaces import IMLModelRepository
# from domain.entities import ParkingData, ModelPerformance
# from domain.value_objects import PredictionResult
#
#
# class RandomForestModelRepository(IMLModelRepository):
#     """Random Forest implementation of ML model repository"""
#
#     def __init__(self, model_path: str = "rf.pkl", features_path: str = "rf_feature_cols.pkl"):
#         self.model_path = model_path
#         self.features_path = features_path
#         self._model = None
#         self._feature_columns = None
#
#     def save_model(self, model, feature_columns: List[str]) -> None:
#         """Save trained model and feature columns"""
#         try:
#             with open(self.model_path, "wb") as f:
#                 pkl.dump(model, f)
#             with open(self.features_path, "wb") as f:
#                 pkl.dump(feature_columns, f)
#         except Exception as e:
#             raise Exception(f"Failed to save model: {str(e)}")
#
#     def load_model(self) -> Tuple[object, List[str]]:
#         """Load trained model and feature columns"""
#         try:
#             with open(self.model_path, "rb") as f:
#                 model = pkl.load(f)
#             with open(self.features_path, "rb") as f:
#                 feature_columns = pkl.load(f)
#             return model, feature_columns
#         except FileNotFoundError:
#             raise FileNotFoundError("Model files not found. Please train a model first.")
#         except Exception as e:
#             raise Exception(f"Failed to load model: {str(e)}")
#
#     def model_exists(self) -> bool:
#         """Check if model files exist"""
#         try:
#             import os
#             return os.path.exists(self.model_path) and os.path.exists(self.features_path)
#         except:
#             return False
#
#     def train_model(self, parking_data: List[ParkingData]) -> Tuple[object, List[str]]:
#         """Train a new Random Forest model"""
#         if not parking_data:
#             raise ValueError("No data provided for training")
#
#         # Convert to DataFrame and create features
#         df = self._prepare_training_data(parking_data)
#
#         # Define feature columns
#         feature_cols = [
#             "hour", "day_of_week", "day_of_month", "month", "year",
#             "free", "occupied", "rate_of_change"
#         ]
#
#         # Add lag features
#         lag_cols = [col for col in df.columns if "lag" in col]
#         feature_cols.extend(lag_cols)
#
#         # Remove rows with NaN
#         clean_df = df.dropna()
#
#         if clean_df.empty:
#             raise ValueError("No valid data after preprocessing")
#
#         # Split features and target
#         X = clean_df[feature_cols]
#         y = clean_df["target"]
#
#         # Split into training and validation sets
#         X_train, X_val, y_train, y_val = train_test_split(
#             X, y, test_size=0.2, random_state=42
#         )
#
#         # Create and train the model
#         model = RandomForestRegressor(n_estimators=100, random_state=42)
#         model.fit(X_train, y_train)
#
#         # Cache the trained model
#         self._model = model
#         self._feature_columns = feature_cols
#
#         return model, feature_cols
#
#     def predict(self, model, feature_columns: List[str], features: dict) -> int:
#         """Make a prediction using the trained model"""
#         try:
#             # Create a DataFrame with the features
#             feature_df = pd.DataFrame([features])
#
#             # Ensure all required columns are present
#             for col in feature_columns:
#                 if col not in feature_df.columns:
#                     feature_df[col] = 0
#
#             # Select only the required features in the right order
#             X_pred = feature_df[feature_columns]
#
#             # Make prediction
#             prediction = model.predict(X_pred)[0]
#
#             return max(0, round(prediction))  # Ensure non-negative integer
#
#         except Exception as e:
#             raise Exception(f"Prediction failed: {str(e)}")
#
#     def evaluate_model(self, model, feature_columns: List[str], parking_data: List[ParkingData]) -> ModelPerformance:
#         """Evaluate model performance"""
#         try:
#             df = self._prepare_training_data(parking_data)
#             clean_df = df.dropna(subset=["target"] + feature_columns)
#
#             if clean_df.empty:
#                 raise ValueError("No valid data for evaluation")
#
#             X = clean_df[feature_columns]
#             y_actual = clean_df["target"]
#             y_pred = model.predict(X)
#
#             # Calculate metrics
#             mae = np.mean(np.abs(y_pred - y_actual))
#             rmse = np.sqrt(np.mean((y_pred - y_actual) ** 2))
#
#             return ModelPerformance(
#                 actual_values=y_actual.tolist(),
#                 predicted_values=y_pred.tolist(),
#                 timestamps=clean_df["mvalidtime"].tolist(),
#                 mae=mae,
#                 rmse=rmse
#             )
#
#         except Exception as e:
#             raise Exception(f"Model evaluation failed: {str(e)}")
#
#     def _prepare_training_data(self, parking_data: List[ParkingData]) -> pd.DataFrame:
#         """Convert parking data to DataFrame with features"""
#         # Convert to basic DataFrame
#         data = []
#         for item in parking_data:
#             data.append({
#                 'mvalidtime': item.timestamp,
#                 'free': item.free_spaces,
#                 'occupied': item.occupied_spaces
#             })
#
#         df = pd.DataFrame(data)
#         df = df.sort_values("mvalidtime")
#
#         # Create features
#         df = self._create_features(df)
#
#         return df
#
#     def _create_features(self, df: pd.DataFrame) -> pd.DataFrame:
#         """Create features for model training"""
#         # Extract datetime features
#         df["hour"] = df["mvalidtime"].dt.hour
#         df["day_of_week"] = df["mvalidtime"].dt.dayofweek
#         df["day_of_month"] = df["mvalidtime"].dt.day
#         df["month"] = df["mvalidtime"].dt.month
#         df["year"] = df["mvalidtime"].dt.year
#
#         # Calculate time differences
#         df["time_diff"] = df["mvalidtime"].diff().dt.total_seconds()
#
#         # Create lagged features
#         for i in range(1, 13):
#             df[f"free_lag_{i}"] = df["free"].shift(i)
#
#         # Calculate rate of change
#         df["rate_of_change"] = (df["free"] - df["free_lag_1"]) / df["time_diff"]
#
#         # Create target variable (free spaces in one hour)
#         df["target"] = df["free"].shift(-12)
#
#         return df