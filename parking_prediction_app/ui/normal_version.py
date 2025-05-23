import streamlit as st
import logging

from ui.components import UIComponentService
from ui.model_training import ModelTrainingPage
from ui.occupancy_prediction import OccupancyPredictionPage
from ui.plots import PlotsPage
from core.exceptions import ParkingAppError

logger = logging.getLogger("parking_prediction")


class NormalVersionPage:
    """Main page for the normal (full-featured) version of the app."""

    def __init__(self):
        """Initialize the normal version page."""
        self.ui_service = UIComponentService()
        self.model_training_page = ModelTrainingPage()
        self.occupancy_prediction_page = OccupancyPredictionPage()
        self.plots_page = PlotsPage()

    def render(self) -> None:
        """Render the normal version page."""
        try:
            st.header("Parking Prediction System", divider=True)

            # Station and date selection
            col1, col2 = st.columns([2, 3])

            with col1:
                station = self.ui_service.station_selector("normal_version_station")
                if not station:
                    st.stop()

            with col2:
                start_date, end_date = self.ui_service.date_range_selector("normal_version_dates")

            # Data fetching section
            st.subheader("Data Management", divider=True)

            # Fetch data button and display
            df = self.ui_service.data_fetch_button(station, start_date, end_date, "normal_version_fetch")

            if df is not None:
                # Display data preview
                with st.expander("📋 Data Preview", expanded=False):
                    st.dataframe(df.head(100), use_container_width=True)

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Records", len(df))
                    with col2:
                        st.metric("Date Range", f"{len(df['mvalidtime'].dt.date.unique())} days")
                    with col3:
                        st.metric("Avg Free Spaces", f"{df['free'].mean():.1f}")

            # Main functionality tabs
            st.subheader("Analysis & Prediction", divider=True)
            predict_tab, train_tab, plots_tab = st.tabs(
                ["🔮 Occupancy Prediction", "🤖 Model Training", "📈 Analysis & Performance"]
            )

            with predict_tab:
                self.occupancy_prediction_page.render()

            with train_tab:
                self.model_training_page.render()

            with plots_tab:
                self.plots_page.render()

        except Exception as e:
            logger.error(f"Normal version page error: {e}")
            st.error(f"Normal version page error: {e}")