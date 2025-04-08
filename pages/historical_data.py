import streamlit as st
from datetime import date

from get_data import get_data
from get_data import get_stations

def historical_data_page(station,start_date,end_date):
        # Button to trigger the function
        if st.button("Fetch Data", use_container_width=True, type="primary"):
            df = get_data(
                station_code=station["scode"], start_date=start_date, end_date=end_date
            )
            st.success("Data retrieved successfully!")

            st.dataframe(df)