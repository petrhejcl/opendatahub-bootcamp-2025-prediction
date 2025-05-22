# app/presentation/pages/simplified_version.py
import streamlit as st
from datetime import datetime
from folium import Map, CircleMarker
from streamlit_folium import st_folium
from .base_page import BaseParkingPage
from app.domain.models.station import Station


class SimplifiedVersionPage(BaseParkingPage):
    def render(self):
        stations = self._station_service.get_all_stations()

        # Initialize session state
        if "selected_station_id" not in st.session_state:
            st.session_state.selected_station_id = stations[0].code if stations else None

        col1, col2 = st.columns([2, 1])

        with col1:
            self._render_map(stations)

        with col2:
            self._render_station_selector(stations)
            self._render_prediction_interface()

    def _render_map(self, stations: list[Station]):
        if not stations:
            st.warning("No stations available")
            return

        selected_station = next(
            (s for s in stations if s.code == st.session_state.selected_station_id),
            stations[0]
        )

        m = Map(
            location=[selected_station.coordinates.latitude,
                      selected_station.coordinates.longitude],
            zoom_start=15
        )

        for station in stations:
            if station.coordinates:
                CircleMarker(
                    location=[station.coordinates.latitude,
                              station.coordinates.longitude],
                    radius=20,
                    color="blue" if station.code == st.session_state.selected_station_id
                    else "green",
                    fill=True,
                    fill_opacity=0.7,
                    weight=4,
                    tooltip=station.name
                ).add_to(m)

        map_data = st_folium(
            m,
            width=600,
            height=400,
            key="station_map",
            returned_objects=["last_clicked"]
        )

        self._handle_map_click(map_data, stations)

    def _handle_map_click(self, map_data, stations):
        if map_data and map_data.get("last_clicked"):
            clicked_coords = map_data["last_clicked"]
            clicked_lat = clicked_coords["lat"]
            clicked_lon = clicked_coords["lng"]

            nearest_station = self._find_nearest_station(
                clicked_lat, clicked_lon, stations)

            if nearest_station and nearest_station.code != st.session_state.selected_station_id:
                st.session_state.selected_station_id = nearest_station.code
                st.rerun()

    def _render_station_selector(self, stations: list[Station]):
        station_index = next(
            (i for i, s in enumerate(stations)
             if s.code == st.session_state.selected_station_id),
            0
        )

        selected_station = st.selectbox(
            "Select the parking",
            options=stations,
            index=station_index,
            format_func=lambda s: s.name,
            key="station_selector"
        )

        if selected_station and selected_station.code != st.session_state.selected_station_id:
            st.session_state.selected_station_id = selected_station.code
            st.rerun()

    def _render_prediction_interface(self):
        if not st.session_state.selected_station_id:
            st.warning("Please select a station first")
            return

        end_date = st.date_input('Enter date of arrival',
                                 value=datetime.today())
        end_time = st.time_input('Enter time of arrival',
                                 value=datetime.now().time())

        if st.button("Predict", use_container_width=True, type="primary"):
            prediction_datetime = datetime.combine(end_date, end_time)

            with st.spinner(text="Predicting..."):
                try:
                    result = self._prediction_service.predict_free_spaces(
                        station_code=st.session_state.selected_station_id,
                        prediction_datetime=prediction_datetime
                    )
                    st.subheader(
                        f"Expected number of free parking spaces: {result.predicted_spaces}",
                        divider=True
                    )
                except Exception as e:
                    st.error(f"Prediction failed: {str(e)}")

    @staticmethod
    def _find_nearest_station(lat, lon, stations):
        min_distance = float('inf')
        nearest_station = None

        for station in stations:
            if station.coordinates:
                distance = ((station.coordinates.latitude - lat) ** 2 +
                            (station.coordinates.longitude - lon) ** 2) ** 0.5
                if distance < min_distance:
                    min_distance = distance
                    nearest_station = station

        return nearest_station if min_distance < 0.03 else None