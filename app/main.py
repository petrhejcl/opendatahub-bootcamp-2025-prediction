# app/main.py - Streamlit application entry point
import streamlit as st
from .data_access.model_repository import ModelRepository
from .data_access.parking_repository import ParkingRepository
from .data_access.station_repository import StationRepository
from .services.prediction_service import PredictionService
from .services.station_service import StationService
from .presentation.pages.simplified_version import SimplifiedVersionPage
from .presentation.pages.normal_version import NormalVersionPage
from .presentation.pages.model_training_page import model_training_page

def main():
    st.set_page_config(page_title="Parking Prediction", layout="wide")

    # Initialize repositories
    parking_repository = ParkingRepository()
    model_repository = ModelRepository()
    station_repository = StationRepository()

    # Initialize services
    prediction_service = PredictionService(parking_repository, model_repository)
    station_service = StationService(station_repository)

    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Select Page", ["Simplified", "Normal", "Model Training"])

    # Page routing
    if page == "Simplified":
        simplified_page = SimplifiedVersionPage(prediction_service, station_service)
        simplified_page.render()
    elif page == "Normal":
        normal_page = NormalVersionPage(prediction_service, station_service)
        normal_page.render()
    elif page == "Model Training":
        model_training_page()

if __name__ == "__main__":
    main()