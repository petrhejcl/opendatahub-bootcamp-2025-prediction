import streamlit as st
import logging

from ui.components import UIComponentService
from core.exceptions import ParkingAppError

logger = logging.getLogger("parking_prediction")


class PlotsPage:
    """Page for data visualization and model performance plots."""

    def __init__(self):
        """Initialize the plots page."""
        self.ui_service = UIComponentService()

    def render(self) -> None:
        """Render the plots page."""
        try:
            st.header("Data Analysis & Model Performance", divider=True)

            # Create tabs for different types of plots
            data_tab, performance_tab = st.tabs(["📊 Data Analysis", "🎯 Model Performance"])

            with data_tab:
                st.subheader("Parking Data Visualization")
                with st.expander("ℹ️ About Data Analysis", expanded=False):
                    st.markdown("""
                    This section shows visualizations of your parking data:

                    - **Time Series Plot**: Shows how parking availability changes over time
                    - **Hourly Patterns**: Shows average parking availability by hour of day
                    """)

                self.ui_service.data_visualization_component("data_viz_plots_page")

            with performance_tab:
                st.subheader("Model Performance Analysis")
                with st.expander("ℹ️ About Model Performance", expanded=False):
                    st.markdown("""
                    This section shows how well your trained model performs:

                    - **Time Series Comparison**: Actual vs predicted values over time
                    - **Scatter Plot**: Correlation between actual and predicted values
                    - **Performance Metrics**: MAE, RMSE, and MAPE scores
                    """)

                self.ui_service.model_performance_component("model_perf_plots_page")

        except Exception as e:
            logger.error(f"Plots page error: {e}")
            st.error(f"Plots page error: {e}")