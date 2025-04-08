import streamlit as st

from pages.historical_data import historical_data_page
from pages.model_training import model_training_page
from pages.occupancy_prediction import occupancy_prediction_page
from pages.plots import plots_page

st.set_page_config(layout="wide")

# Streamlit UI
st.title("Station Data Fetcher")

tab1, tab2, tab3, tab4 = st.tabs(["Historical Data", "Occupancy Prediction", "Plots", "Model Training", ])

with tab1:
    historical_data_page()
with tab2:
    occupancy_prediction_page()
with tab3:
    plots_page()
with tab4:
    model_training_page()