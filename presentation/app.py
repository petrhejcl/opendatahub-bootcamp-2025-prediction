# presentation/app.py
from datetime import date, datetime
from typing import Dict, List

import folium
import pandas as pd
import streamlit as st
from dateutil.relativedelta import relativedelta
# Import per la mappa interattiva
from streamlit_folium import st_folium

from application.dtos import TrainingRequestDTO, VisualizationDataDTO
from application.services import ParkingApplicationService
from presentation.utils import get_current_time
from presentation.visualizations import ParkingDataVisualizer


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

    def _get_cached_stations(self):
        """Get stations with caching to avoid multiple API calls"""
        if "all_stations_cache" not in st.session_state:
            st.session_state.all_stations_cache = self.app_service.get_all_stations()
        return st.session_state.all_stations_cache

    def _get_cached_coordinates(self):
        """Get station coordinates with caching"""
        if "coordinates_cache" not in st.session_state:
            st.session_state.coordinates_cache = self.app_service.get_station_coordinates()
        return st.session_state.coordinates_cache

    def _format_station_for_dropdown(self, station_dto) -> str:
        """Format station for dropdown display"""
        if hasattr(station_dto, 'scoordinate') and station_dto.scoordinate:
            return station_dto.sname
        else:
            return f"{station_dto.sname} (not available on the map)"

    def _render_simplified_version(self):
        """Render the simplified version with interactive Folium map"""
        st.write("## Parking Stations Map")

        try:
            # Get cached data to avoid repeated API calls
            all_stations = self._get_cached_stations()
            coordinates = self._get_cached_coordinates()

            if not coordinates:
                st.warning("No stations with coordinates found.")
                return

            # Convert coordinates to the format needed for the map (same as original)
            stations_with_coords = [
                {
                    "scode": coord.scode,
                    "sname": coord.sname,
                    "lat": coord.lat,
                    "lon": coord.lon
                }
                for coord in coordinates
            ]

            # Initialize session state (same as original)
            if "selected_station_id" not in st.session_state:
                st.session_state.selected_station_id = stations_with_coords[0]["scode"]

            # Get current selected station
            selected_station = next(
                (s for s in stations_with_coords if s["scode"] == st.session_state.selected_station_id),
                stations_with_coords[0]
            )

            col1, col2 = st.columns([2, 1])

            with col1:
                # Create Folium map centered on selected station
                m = folium.Map(location=[selected_station["lat"], selected_station["lon"]], zoom_start=15)

                # Add interactive markers for each station
                for s in stations_with_coords:
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

                    for s in stations_with_coords:
                        # Calculate distance
                        distance = ((s["lat"] - clicked_lat) ** 2 + (s["lon"] - clicked_lon) ** 2) ** 0.5
                        if distance < min_distance:
                            min_distance = distance
                            clicked_station = s

                    # More generous click tolerance for user-friendliness
                    if min_distance < 0.05 and clicked_station and clicked_station[
                        "scode"] != st.session_state.selected_station_id:
                        # Update selection and auto-center map
                        st.session_state.selected_station_id = clicked_station["scode"]
                        st.rerun()

            with col2:
                # Station selection dropdown (same logic as original)
                station_index = next(
                    (i for i, s in enumerate(all_stations) if s.scode == st.session_state.selected_station_id), 0)

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

                # Get the complete station data for display
                current_station_data = next(
                    (s for s in all_stations if s.scode == st.session_state.selected_station_id), None)

                if current_station_data:
                    # Display station info (same as original)
                    st.markdown(f"### {current_station_data.sname}")
                    st.write(f"ID: {current_station_data.scode}")

                    # Check if coordinates available and display them
                    station_coords = next(
                        (s for s in stations_with_coords if s["scode"] == current_station_data.scode), None)
                    if station_coords:
                        st.write(f"Latitude: {station_coords['lat']:.6f}")
                        st.write(f"Longitude: {station_coords['lon']:.6f}")

                        # Show on Map button (same as original)
                        if st.button("Show on Map"):
                            st.rerun()
                    else:
                        st.info("Coordinates not available for this station")

                    # Prediction section (same inputs as original)
                    end_date = st.date_input('Enter date of arrival', value=date.today())
                    end_time = st.time_input('Enter time of arrival', get_current_time())
                    past = date.today() - relativedelta(months=6)

                    prediction_datetime = datetime.combine(end_date, end_time)
                    if past > end_date:
                        st.error("Start date must be before or equal to end date.")

                    if st.button("Predict", use_container_width=True, type="primary"):
                        if current_station_data:
                            with st.spinner("Fetching data and training model..."):
                                try:
                                    # Fetch data first
                                    visualization_data = self.app_service.fetch_parking_data(
                                        station_code=st.session_state.selected_station_id,
                                        start_date=past.strftime("%Y-%m-%d"),
                                        end_date=date.today().strftime("%Y-%m-%d")
                                    )

                                    if not visualization_data:
                                        st.warning("No data available for this station in the selected period.")
                                        return

                                    try:
                                        model, feature_cols = self.app_service.train_model(TrainingRequestDTO(
                                            station_code=st.session_state.selected_station_id,
                                            start_date=past.strftime("%Y-%m-%d"),
                                            end_date=date.today().strftime("%Y-%m-%d")
                                        ))
                                    except Exception as training_error:
                                        st.error(f"Model training failed: {str(training_error)}")
                                        return

                                    # Predict occupancy
                                    free_spaces = self.app_service.predict_occupancy(
                                        station_code=st.session_state.selected_station_id,
                                        prediction_time=prediction_datetime,
                                        data_start_date=past.strftime("%Y-%m-%d"),
                                        data_end_date=date.today().strftime("%Y-%m-%d")
                                    )

                                    if free_spaces is not None:
                                        st.success(f"Expected number of free parking spaces: {free_spaces}")
                                    else:
                                        st.warning("Unable to make prediction with available data.")
                                except Exception as e:
                                    st.error(f"Prediction failed: {str(e)}")
                        else:
                            st.error("Please select a valid station first.")

        except Exception as e:
            st.error(f"Error loading simplified version: {str(e)}")

    def _render_normal_version(self):
        """Render the normal (detailed) version of the app"""
        # Station selection - use cached data
        all_stations = self._get_cached_stations()
        stations_for_selectbox = [{"scode": s.scode, "sname": s.sname, "scoordinate": getattr(s, 'scoordinate', None)}
                                  for s in all_stations]

        if not stations_for_selectbox:
            st.error("No stations available. Please check your connection.")
            return

        station = st.selectbox(
            label="Select the parking",
            options=stations_for_selectbox,
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
            with st.spinner("Fetching data from OpenDataHub..."):
                visualization_data = self.app_service.fetch_parking_data(station["scode"], start_date, end_date)

            if visualization_data:
                st.success(f"Data retrieved successfully! Found {len(visualization_data)} data points.")
                df = self._convert_visualization_data_to_dataframe(visualization_data)
                st.dataframe(df)

                # Store data in session state for other tabs
                st.session_state.current_station = station["scode"]
                st.session_state.current_start_date = start_date
                st.session_state.current_end_date = end_date
                st.session_state.has_data = True
            else:
                st.warning("No data found for the selected station and date range.")
                st.session_state.has_data = False

        # Tabs
        predict_tab, train_tab, plots_tab = st.tabs(["Occupancy Prediction", "Model Training", "Plots"])

        with predict_tab:
            self._render_prediction_tab()
        with train_tab:
            self._render_training_tab(station, start_date, end_date)
        with plots_tab:
            self._render_plots_tab()

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