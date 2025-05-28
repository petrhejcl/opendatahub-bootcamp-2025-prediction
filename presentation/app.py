# presentation/app.py
import streamlit as st
import pandas as pd
from datetime import date, datetime
from typing import Dict, List

from application.services import ParkingApplicationService
from application.dtos import TrainingRequestDTO
from presentation.visualizations import ParkingDataVisualizer
from presentation.utils import get_current_time


class ParkingApp:
    """Main Streamlit application - Presentation layer entry point"""

    def __init__(self, app_service: ParkingApplicationService):
        self.app_service = app_service
        self.visualizer = ParkingDataVisualizer()

    def run(self):
        """Run the Streamlit application"""
        st.set_page_config(layout="wide")
        st.title("Free Parking Spots Prediction")

        # Version toggle
        on = st.toggle(label="Simplified version", value=True)

        if on:
            self._render_simplified_version()
        else:
            self._render_normal_version()

    def _render_simplified_version(self):
        """Render the simplified version with map"""
        st.write("## Parking Stations Map")

        try:
            coordinates = self.app_service.get_station_coordinates()

            if coordinates:
                # Create map data for Streamlit
                map_data = pd.DataFrame([{
                    'lat': coord.lat,
                    'lon': coord.lon
                } for coord in coordinates])

                if not map_data.empty:
                    st.map(map_data)

                    # Show station list
                    st.write("### Available Stations")
                    for coord in coordinates:
                        st.write(f"- **{coord.sname}** ({coord.scode})")
                else:
                    st.warning("No stations with valid coordinates found.")
            else:
                st.warning("No station data available.")

        except Exception as e:
            st.error(f"Error loading station data: {str(e)}")

    def _render_normal_version(self):
        """Render the normal (detailed) version of the app"""
        # Station selection
        stations = self._get_stations_for_selectbox()
        station = st.selectbox(
            label="Select the parking",
            options=stations,
            format_func=lambda e: f"{e['sname']}",
        )

        # Date inputs
        start_date = str(st.date_input("Start Date", value=date.today()))
        end_date = str(st.date_input("End Date", value=date.today()))

        if start_date > end_date:
            st.error("Start date must be before or equal to end date.")
            return

        # Fetch data button
        if st.button("Fetch Data", use_container_width=True, type="primary"):
            df = self.app_service.fetch_parking_data(station["scode"], start_date, end_date)
            st.success("Data retrieved successfully!")
            st.dataframe(df)

        # Tabs
        predict_tab, train_tab, plots_tab = st.tabs(["Occupancy Prediction", "Model Training", "Plots"])

        with predict_tab:
            self._render_prediction_tab()
        with train_tab:
            self._render_training_tab(station, start_date, end_date)
        with plots_tab:
            self._render_plots_tab()

    def _get_stations_for_selectbox(self) -> List[Dict]:
        """Get stations formatted for selectbox"""
        stations_dto = self.app_service.get_all_stations()
        return [{"scode": s.scode, "sname": s.sname, "scoordinate": s.scoordinate} for s in stations_dto]

    def _render_prediction_tab(self):
        """Render the prediction tab"""
        start_date = st.date_input('Enter date of arrival', value=date.today())
        start_time = st.time_input('Enter time of arrival', get_current_time())
        prediction_datetime = datetime.combine(start_date, start_time)

        if st.button("Estimate", use_container_width=True, type="primary", key="occupancy_prediction"):
            with st.spinner("Wait for it...", show_time=True):
                free_spaces = self.app_service.predict_occupancy(prediction_datetime)

            if free_spaces is not None:
                st.subheader(f"Expected number of free parking spaces {free_spaces}", divider=True)
            else:
                st.error("Unable to make prediction. Please ensure data is loaded and model is trained.")

    def _render_training_tab(self, station: Dict, start_date: str, end_date: str):
        """Render the training tab"""
        if st.button("Train model", use_container_width=True, type="primary"):
            try:
                self.app_service.train_model(TrainingRequestDTO(
                    station_code=station["scode"],
                    start_date=start_date,
                    end_date=end_date
                ))
                st.success("Model trained successfully!")
            except ValueError as e:
                st.warning(f"Make sure to have some data to train the model: {str(e)}")
            except Exception as e:
                st.error(f"Training failed: {str(e)}")

    def _render_plots_tab(self):
        """Render the plots tab"""
        try:
            # Get visualization data as DTOs
            visualization_data = self.app_service.get_visualization_data()
            if visualization_data:
                self.visualizer.render_data_plot(visualization_data)

                # Show performance plot if model exists
                performance = self.app_service.evaluate_model_performance()
                if performance:
                    self.visualizer.render_performance_plot(performance)
                else:
                    st.info("Train a model to see performance metrics.")
            else:
                st.warning("No data available. Please fetch data first.")
        except Exception as e:
            st.warning(f"Make sure to have some data and a trained model ready: {str(e)}")