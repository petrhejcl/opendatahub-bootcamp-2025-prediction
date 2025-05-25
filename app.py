import streamlit as st

from app.data_access.model_repository import ModelRepository
from app.data_access.parking_repository import ParkingRepository
from app.presentation.pages.simplified_version import SimplifiedVersionPage
from app.presentation.pages.normal_version import NormalVersionPage
from app.services.prediction_service import PredictionService
from app.services.station_service import StationService


def main():
    st.set_page_config(page_title="Parking Prediction", layout="wide")

    # Instantiate repositories
    parking_repository = ParkingRepository()
    model_repository = ModelRepository()

    # Pass them to the service
    prediction_service = PredictionService(parking_repository, model_repository)
    station_service = StationService()  # Assuming no args needed here

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
