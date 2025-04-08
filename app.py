import streamlit as st

from datetime import date
from get_data import get_stations, get_data
from tabs.model_training import model_training_page
from tabs.occupancy_prediction import occupancy_prediction_page
from tabs.plots import plots_page

st.set_page_config(layout="wide")

# Streamlit UI
st.title("Station Data Fetcher")

station = st.selectbox(
    label="Select Station Code",
    options=get_stations(),
    format_func=lambda e: f"{e['sname']}",
)
start_date = str(st.date_input("Start Date", value=date.today()))
end_date = str(st.date_input("End Date", value=date.today()))
if start_date > end_date:
    st.error("Start date must be before or equal to end date.")

if st.button("Fetch Data", use_container_width=True, type="primary"):
    df = get_data(
        station_code=station["scode"], start_date=start_date, end_date=end_date
    )
    st.success("Data retrieved successfully!")

    st.dataframe(df)

tab2, tab3, tab4 = st.tabs(["Occupancy Prediction", "Plots", "Model Training"])

with tab2:
    occupancy_prediction_page()
with tab3:
    plots_page()
with tab4:
    model_training_page(station, start_date, end_date)
