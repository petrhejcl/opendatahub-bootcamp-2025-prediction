# app/presentation/pages/normal_version.py
import streamlit as st
from datetime import datetime, timedelta
from ...services.prediction_service import PredictionService
from ...services.station_service import StationService


class NormalVersionPage:
    def __init__(self, prediction_service: PredictionService, station_service: StationService):
        self.prediction_service = prediction_service
        self.station_service = station_service

    def render(self):
        st.title("Parking Prediction - Normal Version")

        # Sidebar for station selection
        with st.sidebar:
            st.header("Configuration")
            stations = self.station_service.get_all_stations()

            if not stations:
                st.error("No stations available")
                return

            station_options = {f"{s.name} ({s.code})": s.code for s in stations}
            selected_station = st.selectbox("Select Station", list(station_options.keys()))

        # Main content
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Single Prediction")
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

                    st.metric("Predicted Free Spaces", result.predicted_spaces)
                    st.info(f"For time: {result.prediction_time}")

                except Exception as e:
                    st.error(f"Prediction failed: {str(e)}")

        with col2:
            st.subheader("Multiple Predictions")
            hours_ahead = st.slider("Hours ahead", 1, 24, 6)

            if st.button("Make Multiple Predictions"):
                try:
                    station_code = station_options[selected_station]
                    predictions = []

                    for i in range(1, hours_ahead + 1):
                        pred_time = datetime.now() + timedelta(hours=i)
                        result = self.prediction_service.predict_free_spaces(
                            station_code, pred_time
                        )
                        predictions.append({
                            'Hour': f"+{i}h",
                            'Time': pred_time.strftime("%H:%M"),
                            'Predicted Spaces': result.predicted_spaces
                        })

                    st.table(predictions)

                except Exception as e:
                    st.error(f"Predictions failed: {str(e)}")