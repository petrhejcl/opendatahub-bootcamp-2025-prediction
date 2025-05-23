import streamlit as st
import folium
from streamlit_folium import st_folium
from datetime import date, datetime
from dateutil.utils import today
from dateutil.relativedelta import relativedelta
import logging

from ui.components import UIComponentService
from core.exceptions import ParkingAppError

logger = logging.getLogger("parking_prediction")


class SimplifiedVersionPage:
    """Simplified version page with map interface."""

    def __init__(self):
        """Initialize the simplified version page."""
        self.ui_service = UIComponentService()

    def render(self) -> None:
        """Render the simplified version page."""
        try:
            st.header("Quick Parking Prediction", divider=True)

            # Load stations
            if "simplified_stations" not in st.session_state:
                with st.spinner("Loading parking stations..."):
                    stations = self.ui_service.data_fetcher.get_stations()
                    st.session_state.simplified_stations = stations

            stations = st.session_state.simplified_stations

            if not stations:
                st.error("No parking stations available")
                return

            # Get coordinates for map-enabled stations
            map_stations = self._get_coordinates(stations)

            # Initialize session state
            if "selected_station_id" not in st.session_state:
                st.session_state.selected_station_id = stations[0].get('scode', stations[0].id)

            # Get current selected station for map
            selected_map_station = next(
                (s for s in map_stations if s["scode"] == st.session_state.selected_station_id),
                map_stations[0] if map_stations else None
            )

            # Layout with map and controls
            col1, col2 = st.columns([2, 1])

            with col1:
                # Create and display map
                if selected_map_station:
                    self._render_map(map_stations, selected_map_station)
                else:
                    st.info("Map not available for selected station")

            with col2:
                # Station selection and controls
                self._render_controls(stations, map_stations)

            # Prediction section
            st.subheader("Make Prediction", divider=True)

            col1, col2 = st.columns(2)
            with col1:
                end_date = st.date_input(
                    "Arrival Date",
                    value=date.today(),
                    key="simplified_arrival_date"
                )

            with col2:
                end_time = st.time_input(
                    'Arrival Time',
                    value=self.ui_service._get_current_rounded_time(),
                    key="simplified_arrival_time"
                )

            # Date validation
            past = date.today() - relativedelta(months=6)
            if past > end_date:
                st.error("Start date must be before or equal to end date.")
                return

            # Prediction button
            if st.button("Predict", use_container_width=True, type="primary"):
                prediction_datetime = datetime.combine(end_date, end_time)
                self._make_prediction(prediction_datetime, past)

        except Exception as e:
            logger.error(f"Simplified version page error: {e}")
            st.error(f"Simplified version page error: {e}")

    def _get_coordinates(self, stations):
        """Extract coordinates from stations data for map display."""
        map_stations = []
        if isinstance(stations, list):
            key = 'scoordinate'
            for station in stations:
                if key in station:
                    map_stations.append({
                        "scode": station['scode'],
                        "sname": station['sname'],
                        "lat": station[key]['y'],
                        "lon": station[key]['x']
                    })
        return map_stations

    def _render_map(self, map_stations, selected_station):
        """Render the interactive map."""
        if not selected_station:
            st.info("Map not available for this station")
            return

        # Create Folium map centered on selected station
        m = folium.Map(
            location=[selected_station["lat"], selected_station["lon"]],
            zoom_start=15
        )

        # Add markers for each station
        for station in map_stations:
            # Set color based on selection
            color = "blue" if station["scode"] == st.session_state.selected_station_id else "green"

            # Create circle marker
            folium.CircleMarker(
                location=[station["lat"], station["lon"]],
                radius=20,
                color=color,
                fill=True,
                fill_opacity=0.7,
                weight=4,
                tooltip=station["sname"]
            ).add_to(m)

        # Display map and handle clicks
        map_data = st_folium(
            m,
            width=600,
            height=400,
            key="simplified_station_map",
            returned_objects=["last_clicked"]
        )

        # Process map clicks
        if map_data and map_data.get("last_clicked"):
            self._handle_map_click(map_data["last_clicked"], map_stations)

    def _render_controls(self, all_stations, map_stations):
        """Render the control panel."""
        def custom_formats(station):
            key = 'scoordinate'
            if key in station:
                return station['sname']
            else:
                return f"{station['sname']} ( not available on the map)"

        # Station selection dropdown
        station_index = next(
            (i for i, s in enumerate(all_stations) if s["scode"] == st.session_state.selected_station_id),
            0
        )

        selected_station_from_dropdown = st.selectbox(
            "Select the parking",
            options=all_stations,
            index=station_index,
            format_func=custom_formats,
            key="simplified_station_selector"
        )

        # Update session state from dropdown selection
        if selected_station_from_dropdown and "scode" in selected_station_from_dropdown:
            dropdown_station_id = selected_station_from_dropdown["scode"]
            if dropdown_station_id != st.session_state.selected_station_id:
                st.session_state.selected_station_id = dropdown_station_id

        # Get current station data for display
        current_station_data = next(
            (s for s in all_stations if s["scode"] == st.session_state.selected_station_id),
            None
        )

        if current_station_data:
            # Display station info
            st.markdown(f"### {current_station_data['sname']}")
            st.write(f"**ID:** {current_station_data['scode']}")

            if 'scoordinate' in current_station_data:
                st.write(f"**Latitude:** {current_station_data['scoordinate']['y']:.6f}")
                st.write(f"**Longitude:** {current_station_data['scoordinate']['x']:.6f}")

                # Show on Map button only for stations with coordinates
                if st.button("Show on Map", use_container_width=True):
                    # Find the station with coordinates in our map-enabled stations list
                    map_station = next(
                        (s for s in map_stations if s["scode"] == st.session_state.selected_station_id),
                        None
                    )
                    if map_station:
                        st.rerun()
                    else:
                        st.warning("This station is not available on the map.")
            else:
                st.info("Coordinates not available for this station")

    def _handle_map_click(self, clicked_coords, map_stations):
        """Handle map click events."""
        clicked_lat = clicked_coords["lat"]
        clicked_lon = clicked_coords["lng"]

        # Find nearest station
        min_distance = float('inf')
        clicked_station = None

        for station in map_stations:
            # Calculate distance
            distance = ((station["lat"] - clicked_lat) ** 2 +
                        (station["lon"] - clicked_lon) ** 2) ** 0.5
            if distance < min_distance:
                min_distance = distance
                clicked_station = station

        # Use generous click tolerance
        if (min_distance < 0.03 and clicked_station and
                clicked_station["scode"] != st.session_state.selected_station_id):
            st.session_state.selected_station_id = clicked_station["scode"]
            st.rerun()

    def _make_prediction(self, prediction_datetime, past_date):
        """Make prediction for the selected station and time."""
        try:
            # Get current station data
            current_station_data = next(
                (s for s in st.session_state.simplified_stations
                 if s["scode"] == st.session_state.selected_station_id),
                None
            )

            if not current_station_data:
                st.error("Please select a valid station first.")
                return

            with st.spinner(text="Fetching data..."):
                # Load historical data for the specific station
                df = self.ui_service.data_repo.get_data(
                    station_code=st.session_state.selected_station_id,
                    start_date=past_date,
                    end_date=today()
                )

                if df.empty:
                    st.error("No historical data available for this station")
                    return

            with st.spinner(text="Predicting available spaces..."):
                # Check if model is available
                if not self.ui_service.prediction_service.is_model_available():
                    st.warning("No trained model available. Using demo mode with sample data.")
                    st.info("Demo prediction: 15 free parking spaces")
                    return

                # Make prediction using the prediction service
                free_spaces = self.ui_service.prediction_service.predict(
                    prediction_datetime,
                    use_demo=False
                )

            if free_spaces is not None:
                # Display result
                st.success("Prediction completed!")
                st.subheader(f"🅿️ Expected number of free parking spaces: {free_spaces}", divider=True)
                st.info(f"📅 For: {prediction_datetime.strftime('%Y-%m-%d %H:%M')}")
                st.info(f"📍 At: {current_station_data['sname']}")
            else:
                st.error("Prediction failed - please try again")

        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            st.error(f"Prediction failed: {e}")