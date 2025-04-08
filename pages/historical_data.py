import streamlit as st
from datetime import date

from get_data import get_data
from get_data import get_stations

def historical_data_page(station):
    # User inputs

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