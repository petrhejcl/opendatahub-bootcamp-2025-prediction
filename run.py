# run.py
import streamlit as st
from app.presentation.pages.simplified_version import SimplifiedVersionPage
from app.presentation.pages.normal_version import NormalVersionPage
from app.infrastructure.dependencies import get_prediction_service, get_station_service


def main():
    st.set_page_config(page_title="Parking Prediction", layout="wide")

    # Get services
    prediction_service = get_prediction_service()
    station_service = get_station_service()

    # Create pages
    simplified_page = SimplifiedVersionPage(prediction_service, station_service)
    normal_page = NormalVersionPage(prediction_service, station_service)

    # Page selection
    page = st.sidebar.radio("Select Version", ["Simplified", "Normal"])

    # Render selected page
    if page == "Simplified":
        simplified_page.render()
    else:
        normal_page.render()


if __name__ == "__main__":
    main()