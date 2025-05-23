import streamlit as st
import logging

from ui.components import UIComponentService
from core.exceptions import ParkingAppError

logger = logging.getLogger("parking_prediction")


class ModelTrainingPage:
    """Page for model training functionality."""

    def __init__(self):
        """Initialize the model training page."""
        self.ui_service = UIComponentService()

    def render(self) -> None:
        """Render the model training page."""
        try:
            st.header("Model Training", divider=True)

            # Information section
            with st.expander("ℹ️ About Model Training", expanded=False):
                st.markdown("""
                This section allows you to train a machine learning model to predict parking space availability.

                **Requirements:**
                - Historical parking data must be available (fetch data first)
                - The model uses Random Forest algorithm
                - Training includes feature engineering and validation

                **Features used:**
                - Time-based features (hour, day of week, month, etc.)
                - Lagged values (previous observations)
                - Rate of change
                """)

            # Model training component
            self.ui_service.model_training_component("train_model_page")

        except Exception as e:
            logger.error(f"Model training page error: {e}")
            st.error(f"Model training page error: {e}")