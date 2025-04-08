import streamlit as st

from datetime import date
from get_data import get_stations
from pages.historical_data import historical_data_page
from pages.model_training import model_training_page
from pages.occupancy_prediction import occupancy_prediction_page
from pages.plots import plots_page

st.set_page_config(layout="wide")

# Streamlit UI
st.title("Station Data Fetcher")

station = st.selectbox(label="Select Station Code", options=get_stations(), format_func=lambda e: f"{e['sname']}")
start_date = str(st.date_input("Start Date", value=date.today()))
end_date = str(st.date_input("End Date", value=date.today()))
if start_date > end_date:
    st.error("Start date must be before or equal to end date.")

tab1, tab2, tab3, tab4 = st.tabs(["Historical Data", "Occupancy Prediction", "Plots", "Model Training", ])

with tab1:
    historical_data_page(station,start_date,end_date)
with tab2:
    occupancy_prediction_page(station,start_date,end_date)
with tab3:
    plots_page(station,start_date,end_date)
with tab4:
    model_training_page(station,start_date,end_date)