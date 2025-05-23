import streamlit as st
import logging

from ui.components import UIComponentService
from core.exceptions import ParkingAppError

logger = logging.getLogger("parking_prediction")


class OccupancyPredictionPage:
    """Page for occupancy prediction functionality."""

    def __init__(self):
        """Initialize the occupancy prediction page."""
        self.ui_service = UIComponentService()

    def render(self) -> None:
        """Render the occupancy prediction page."""
        try:
            st.header("Occupancy Prediction", divider=True)

            # Information section
            with st.expander("ℹ️ About Occupancy Prediction", expanded=False):
                st.markdown("""
                This section allows you to predict the number of free parking spaces for a specific date and time.

                **Requirements:**
                - A trained model must be available
                - Historical data is used to make predictions

                **How it works:**
                - Select your desired arrival date and time
                - The model analyzes historical patterns
                - Provides an estimate of available parking spaces
                """)

            # Prediction component
            self.ui_service.prediction_component("predict_occupancy_page")

        except Exception as e:
            logger.error(f"Occupancy prediction page error: {e}")
            st.error(f"Occupancy prediction page error: {e}")