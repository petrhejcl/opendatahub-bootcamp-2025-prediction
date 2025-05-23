import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
from typing import List, Optional, Dict, Any
import logging
from concurrent.futures import ThreadPoolExecutor

from data.data_fetcher import ParkingDataFetcher
from data.data_repository import ParkingDataRepository
from data.models import ParkingStation
from ml.feature_engineering import FeatureEngineer
from ml.training_service import TrainingService
from ml.prediction_service import PredictionService
from visualization.data_plots import DataPlotService
from visualization.performance_plots import PerformancePlotService
from core.exceptions import ParkingAppError

logger = logging.getLogger("parking_prediction")


class UIComponentService:
    """Service providing reusable UI components."""

    def __init__(self):
        """Initialize the UI component service."""
        self.data_fetcher = ParkingDataFetcher()
        self.data_repo = ParkingDataRepository()
        self.feature_engineer = FeatureEngineer()
        self.training_service = TrainingService()
        self.prediction_service = PredictionService()
        self.data_plot_service = DataPlotService()
        self.performance_plot_service = PerformancePlotService()

    def station_selector(self, key: str = "station_selector") -> Optional[ParkingStation]:
        """
        Create a station selection component.

        Args:
            key: Unique key for the selectbox

        Returns:
            Selected ParkingStation or None if failed to load
        """
        try:
            # Cache stations to avoid repeated API calls
            if f"stations_{key}" not in st.session_state:
                with st.spinner("Loading parking stations..."):
                    stations = self.data_fetcher.get_stations()
                    st.session_state[f"stations_{key}"] = stations

            stations = st.session_state[f"stations_{key}"]

            if not stations:
                st.error("No parking stations available")
                return None

            selected_station = st.selectbox(
                label="Select the parking station",
                options=stations,
                format_func=lambda station: f"{station.name} (ID: {station.id})",
                key=key
            )

            return selected_station

        except Exception as e:
            logger.error(f"Failed to load stations: {e}")
            st.error(f"Failed to load parking stations: {e}")
            return None

    def date_range_selector(self, key_prefix: str = "date") -> tuple[str, str]:
        """
        Create date range selection components.

        Args:
            key_prefix: Prefix for the component keys

        Returns:
            Tuple of (start_date, end_date) as strings
        """
        col1, col2 = st.columns(2)

        with col1:
            start_date = st.date_input(
                "Start Date",
                value=date.today() - timedelta(days=7),  # Default to 1 week ago
                key=f"{key_prefix}_start"
            )

        with col2:
            end_date = st.date_input(
                "End Date",
                value=date.today(),
                key=f"{key_prefix}_end"
            )

        # Validation
        if start_date > end_date:
            st.error("Start date must be before or equal to end date.")
            # Return today's date for both to avoid errors
            today = date.today()
            return str(today), str(today)

        return str(start_date), str(end_date)

    def data_fetch_button(self, station: ParkingStation, start_date: str,
                          end_date: str, key: str = "fetch_data") -> Optional[pd.DataFrame]:
        """
        Create a data fetch button and handle the data fetching process.

        Args:
            station: Selected parking station
            start_date: Start date string
            end_date: End date string
            key: Unique key for the button

        Returns:
            Fetched DataFrame or None if failed
        """
        if st.button("Fetch Data", use_container_width=True, type="primary", key=key):
            try:
                with st.spinner("Fetching parking data..."):
                    # Fetch data
                    df = self.data_fetcher.get_station_data(
                        station_code=station.id,
                        start_date=start_date,
                        end_date=end_date
                    )

                    if df.empty:
                        st.warning("No data found for the selected date range")
                        return None

                    # Save data to CSV
                    self.data_repo.save_dataframe(df)

                    st.success(f"Successfully retrieved {len(df)} data points!")
                    return df

            except Exception as e:
                logger.error(f"Data fetch failed: {e}")
                st.error(f"Failed to fetch data: {e}")
                return None

        return None

    def model_training_component(self, key: str = "train_model") -> None:
        """
        Create a model training component.

        Args:
            key: Unique key for the button
        """
        try:
            # Load existing data
            df = self.data_repo.load_dataframe()

            if df.empty:
                st.warning("No data available. Please fetch data first.")
                return

            # Show data info
            st.info(f"Available data: {len(df)} records from {df['mvalidtime'].min()} to {df['mvalidtime'].max()}")

            if st.button("Train Model", use_container_width=True, type="primary", key=key):
                try:
                    with st.spinner("Training model... This may take a few minutes."):
                        # Create features
                        df_features = self.feature_engineer.create_features(df)

                        # Train model
                        model, feature_cols, metrics = self.training_service.train_model(df_features)

                        # Display training results
                        st.success("Model trained successfully!")

                        # Show metrics
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Training R²", f"{metrics['train_r2']:.4f}")
                        with col2:
                            st.metric("Validation R²", f"{metrics['val_r2']:.4f}")
                        with col3:
                            st.metric("MAE", f"{metrics['mae']:.2f} spaces")
                        with col4:
                            st.metric("RMSE", f"{metrics['rmse']:.2f} spaces")

                except Exception as e:
                    logger.error(f"Model training failed: {e}")
                    st.error(f"Model training failed: {e}")

        except Exception as e:
            logger.error(f"Model training component error: {e}")
            st.error(f"Model training component error: {e}")

    def prediction_component(self, key: str = "make_prediction") -> None:
        """
        Create a prediction component.

        Args:
            key: Unique key for the component
        """
        try:
            # Check if model is available
            if not self.prediction_service.is_model_available():
                st.warning("No trained model available. Please train a model first.")
                return

            # Date and time selection
            col1, col2 = st.columns(2)

            with col1:
                prediction_date = st.date_input(
                    'Enter date of arrival',
                    value=date.today(),
                    key=f"{key}_date"
                )

            with col2:
                prediction_time = st.time_input(
                    'Enter time of arrival',
                    value=self._get_current_rounded_time(),
                    key=f"{key}_time"
                )

            # Combine date and time
            prediction_datetime = datetime.combine(prediction_date, prediction_time)

            if st.button("Estimate", use_container_width=True, type="primary", key=key):
                try:
                    with st.spinner("Making prediction..."):
                        # Load historical data
                        df = self.data_repo.load_dataframe()

                        if df.empty:
                            st.error("No historical data available for prediction")
                            return

                        # Create features
                        df_features = self.feature_engineer.create_features(df)

                        # Make prediction
                        pred_time, free_spaces = self.prediction_service.predict_future(
                            df_features, prediction_datetime
                        )

                        # Display result
                        st.success(f"Prediction completed!")
                        st.subheader(f"Expected number of free parking spaces: {free_spaces}", divider=True)

                        # Additional info
                        st.info(f"Prediction for: {pred_time.strftime('%Y-%m-%d %H:%M')}")

                except Exception as e:
                    logger.error(f"Prediction failed: {e}")
                    st.error(f"Prediction failed: {e}")

        except Exception as e:
            logger.error(f"Prediction component error: {e}")
            st.error(f"Prediction component error: {e}")

    def data_visualization_component(self, key: str = "data_viz") -> None:
        """
        Create a data visualization component.

        Args:
            key: Unique key for the component
        """
        try:
            # Load data
            df = self.data_repo.load_dataframe()

            if df.empty:
                st.warning("No data available for visualization. Please fetch data first.")
                return

            # Create features for plotting
            df_features = self.feature_engineer.create_features(df)

            # Render data plots
            st.subheader("Data Analysis", divider=True)
            self.data_plot_service.render_data_plot(df_features)

        except Exception as e:
            logger.error(f"Data visualization error: {e}")
            st.error(f"Data visualization failed: {e}")

    def model_performance_component(self, key: str = "model_perf") -> None:
        """
        Create a model performance visualization component.

        Args:
            key: Unique key for the component
        """
        try:
            # Check if model is available
            if not self.prediction_service.is_model_available():
                st.warning("No trained model available. Please train a model first.")
                return

            # Load data
            df = self.data_repo.load_dataframe()

            if df.empty:
                st.warning("No data available for performance analysis. Please fetch data first.")
                return

            # Create features
            df_features = self.feature_engineer.create_features(df)

            # Load model
            model, feature_cols = self.prediction_service._model_repo.load_model()

            # Render performance plots
            st.subheader("Model Performance", divider=True)
            self.performance_plot_service.render_performance_plot(df_features, model, feature_cols)

        except Exception as e:
            logger.error(f"Model performance visualization error: {e}")
            st.error(f"Model performance visualization failed: {e}")

    def _get_current_rounded_time(self) -> datetime.time:
        """
        Get current time rounded to nearest 5-minute interval.

        Returns:
            Rounded time object
        """
        now = datetime.now()

        # Round minutes to nearest 5-minute interval
        rounded_minute = 5 * round(now.minute / 5)
        rounded_time = now.replace(minute=rounded_minute, second=0, microsecond=0)

        # If rounding pushed us to the next hour
        if rounded_minute == 60:
            rounded_time = rounded_time + timedelta(hours=1)
            rounded_time = rounded_time.replace(minute=0)

        return rounded_time.time()