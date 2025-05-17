from get_data import get_stations, get_data
import streamlit as st
from datetime import date

from tabs.model_training import model_training_page
from tabs.occupancy_prediction import occupancy_prediction_page
from tabs.plots import plots_page


def normal_version_page():
    station = st.selectbox(
        label="Select the parking",
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

    predict_tab, train_tab, plots_tab = st.tabs(
        ["Occupancy Prediction", "Model Training", "Plots"]
    )

    with predict_tab:
        occupancy_prediction_page()
    with train_tab:
        model_training_page(station, start_date, end_date)
    with plots_tab:
        try:
            plots_page()
        except ValueError:
            st.warning("Make sure to have some data and a trained model ready")