# presentation/app.py
import streamlit as st
import pandas as pd
from datetime import date, datetime
from typing import Dict, List

from application.services import ParkingApplicationService
from application.dtos import TrainingRequestDTO, VisualizationDataDTO
from presentation.visualizations import ParkingDataVisualizer
from presentation.utils import get_current_time

# Import per la mappa interattiva
from streamlit_folium import st_folium
import folium
from dateutil.relativedelta import relativedelta


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
        """Render the simplified version with interactive Folium map"""
        st.write("## Parking Stations Map")

        try:
            # Get stations with coordinates
            stations = self._get_stations_with_coordinates()
            all_stations = self.app_service.get_all_stations()

            if not stations:
                st.warning("No stations with coordinates found.")
                return

            # Initialize session state
            if "selected_station_id" not in st.session_state:
                st.session_state.selected_station_id = stations[0]["scode"]

            # Get current selected station
            selected_station = next(
                (s for s in stations if s["scode"] == st.session_state.selected_station_id),
                stations[0]
            )

            col1, col2 = st.columns([2, 1])

            with col1:
                # Create Folium map centered on selected station
                m = folium.Map(
                    location=[selected_station["lat"], selected_station["lon"]],
                    zoom_start=15
                )

                # Add interactive markers for each station
                for s in stations:
                    # Set color based on selection
                    color = "blue" if s["scode"] == st.session_state.selected_station_id else "green"

                    # Create a large circle marker with good clickability
                    folium.CircleMarker(
                        location=[s["lat"], s["lon"]],
                        radius=20,  # Large radius for better clicking
                        color=color,
                        fill=True,
                        fill_opacity=0.7,
                        weight=4,  # Thick border for visibility
                        tooltip=s["sname"]  # Hover text
                    ).add_to(m)

                # Display interactive map
                map_data = st_folium(
                    m,
                    width=600,
                    height=400,
                    key="station_map",
                    returned_objects=["last_clicked"]
                )

                # Process map clicks with generous tolerance
                if map_data and map_data.get("last_clicked"):
                    clicked_coords = map_data["last_clicked"]
                    clicked_lat = clicked_coords["lat"]
                    clicked_lon = clicked_coords["lng"]

                    # Find nearest station
                    min_distance = float('inf')
                    clicked_station = None

                    for s in stations:
                        # Calculate distance
                        distance = ((s["lat"] - clicked_lat) ** 2 + (s["lon"] - clicked_lon) ** 2) ** 0.5
                        if distance < min_distance:
                            min_distance = distance
                            clicked_station = s

                    # Use generous click tolerance
                    if min_distance < 0.03 and clicked_station and clicked_station["scode"] != st.session_state.selected_station_id:
                        # Update selection and re-center map
                        st.session_state.selected_station_id = clicked_station["scode"]
                        st.rerun()

            with col2:
                # Station selection dropdown
                station_index = next(
                    (i for i, s in enumerate(all_stations) if s.scode == st.session_state.selected_station_id),
                    0
                )

                selected_station_from_dropdown = st.selectbox(
                    "Select the parking",
                    options=all_stations,
                    index=station_index,
                    format_func=self._format_station_for_dropdown,
                    key="station_selector"
                )

                # Update session state from dropdown selection
                if selected_station_from_dropdown and selected_station_from_dropdown.scode != st.session_state.selected_station_id:
                    st.session_state.selected_station_id = selected_station_from_dropdown.scode
                    st.rerun()

                # Display current station info
                current_station = next(
                    (s for s in all_stations if s.scode == st.session_state.selected_station_id),
                    None
                )

                if current_station:
                    st.markdown(f"### {current_station.sname}")
                    st.write(f"ID: {current_station.scode}")

                    if current_station.scoordinate:
                        st.write(f"Latitude: {current_station.scoordinate['y']:.6f}")
                        st.write(f"Longitude: {current_station.scoordinate['x']:.6f}")

                        # Show on Map button
                        if st.button("Show on Map"):
                            st.rerun()
                    else:
                        st.info("Coordinates not available for this station")

                # Prediction section
                st.write("### Prediction")
                end_date = st.date_input('Enter date of arrival', value=date.today())
                end_time = st.time_input('Enter time of arrival', get_current_time())

                prediction_datetime = datetime.combine(end_date, end_time)
                past_date = date.today() - relativedelta(months=6)

                if past_date > end_date:
                    st.error("Date must be in the future or today.")

                if st.button("Predict", use_container_width=True, type="primary"):
                    if current_station:
                        with st.spinner(text="Fetching data..."):
                            # Fetch data for the selected station
                            visualization_data = self.app_service.fetch_parking_data(
                                station_code=st.session_state.selected_station_id,
                                start_date=past_date.strftime("%Y-%m-%d"),
                                end_date=date.today().strftime("%Y-%m-%d")
                            )

                        if visualization_data:
                            with st.spinner(text="Predicting available spaces..."):
                                free_spaces = self.app_service.predict_occupancy(prediction_datetime)

                            if free_spaces is not None:
                                st.subheader(f"Expected number of free parking spaces: {free_spaces}", divider=True)
                            else:
                                st.warning("Unable to make prediction. Please train a model first.")
                        else:
                            st.warning("No data available for this station in the selected period.")
                    else:
                        st.error("Please select a valid station first.")

        except Exception as e:
            st.error(f"Error loading simplified version: {str(e)}")

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
        visualization_data = []

        if st.button("Fetch Data", use_container_width=True, type="primary"):
            visualization_data = self.app_service.fetch_parking_data(station["scode"], start_date, end_date)
            st.success("Data retrieved successfully!")

            df = self._convert_visualization_data_to_dataframe(visualization_data)
            st.dataframe(df)

        # Tabs
        predict_tab, train_tab, plots_tab = st.tabs(["Occupancy Prediction", "Model Training", "Plots"])

        with predict_tab:
            self._render_prediction_tab()
        with train_tab:
            self._render_training_tab(station, start_date, end_date)
        with plots_tab:
            self._render_plots_tab()

    def _get_stations_with_coordinates(self) -> List[Dict]:
        """Get stations that have coordinates for map display"""
        coordinates = self.app_service.get_station_coordinates()
        return [
            {
                "scode": coord.scode,
                "sname": coord.sname,
                "lat": coord.lat,
                "lon": coord.lon
            }
            for coord in coordinates
        ]

    def _get_stations_for_selectbox(self) -> List[Dict]:
        """Get stations formatted for selectbox"""
        stations_dto = self.app_service.get_all_stations()
        return [{"scode": s.scode, "sname": s.sname, "scoordinate": s.scoordinate} for s in stations_dto]

    def _format_station_for_dropdown(self, station_dto) -> str:
        """Format station for dropdown display"""
        if hasattr(station_dto, 'scoordinate') and station_dto.scoordinate:
            return station_dto.sname
        else:
            return f"{station_dto.sname} (not available on the map)"

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

    def _convert_visualization_data_to_dataframe(self, visualization_data: List[VisualizationDataDTO]) -> pd.DataFrame:
        """Converts DTO to DataFrame for presentation only"""
        data = []
        for item in visualization_data:
            data.append({
                'mvalidtime': item.timestamp,
                'free': item.free_spaces,
                'occupied': item.occupied_spaces
            })
        return pd.DataFrame(data)