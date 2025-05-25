# app/presentation/pages/simplified_version.py
import streamlit as st
from datetime import datetime, timedelta
from ...services.prediction_service import PredictionService
from ...services.station_service import StationService


class SimplifiedVersionPage:
    def __init__(self, prediction_service: PredictionService, station_service: StationService):
        self.prediction_service = prediction_service
        self.station_service = station_service

    def render(self):
        st.title("Parking Prediction - Simplified Version")

        # Station selection
        stations = self.station_service.get_all_stations()
        if not stations:
            st.error("No stations available")
            return

        station_options = {f"{s.name} ({s.code})": s.code for s in stations}
        selected_station = st.selectbox("Select Station", list(station_options.keys()))

        # Time selection
        prediction_time = st.datetime_input(
            "Prediction Time",
            datetime.now() + timedelta(hours=1)
        )

        if st.button("Make Prediction", type="primary"):
            try:
                station_code = station_options[selected_station]
                result = self.prediction_service.predict_free_spaces(
                    station_code, prediction_time
                )

                st.success(f"Predicted free spaces: {result.predicted_spaces}")
                st.info(f"Prediction time: {result.prediction_time}")

            except Exception as e:
                st.error(f"Prediction failed: {str(e)}")