import streamlit as st
from datetime import datetime
from app.services.prediction_service import PredictionService
from app.infrastructure.dependencies import get_prediction_service


def occupancy_prediction_page():
    prediction_service = get_prediction_service()

    start_date = st.date_input('Enter date of arrival', value=datetime.today())
    start_time = st.time_input('Enter time of arrival', value=datetime.now().time())

    prediction_datetime = datetime.combine(start_date, start_time)

    if st.button("Estimate", use_container_width=True, type="primary"):
        with st.spinner("Predicting..."):
            try:
                result = prediction_service.predict_free_spaces(
                    station_code="your_station_code",  # Get this from state/parameters
                    prediction_datetime=prediction_datetime
                )
                st.subheader(
                    f"Expected number of free parking spaces: {result.predicted_spaces}",
                    divider=True
                )
            except Exception as e:
                st.error(f"Prediction failed: {str(e)}")