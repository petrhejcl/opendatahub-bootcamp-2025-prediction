import streamlit as st
from datetime import date

from get_data import get_data
from get_data import get_stations

def historical_data_page():
    # User inputs
    station = st.selectbox(label="Select Station Code", options=get_stations(), format_func=lambda e: f"{e['sname']}")
    start_date = str(st.date_input("Start Date", value=date.today()))
    end_date = str(st.date_input("End Date", value=date.today()))

    # Ensure start date is before end date
    if start_date > end_date:
        st.error("Start date must be before or equal to end date.")
    else:
        # Button to trigger the function
        if st.button("Fetch Data", use_container_width=True, type="primary"):
            df = get_data(
                station_code=station["scode"], start_date=start_date, end_date=end_date
            )
            st.success("Data retrieved successfully!")

            st.dataframe(df)