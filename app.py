import streamlit as st
from datetime import date

from get_data import get_data
from get_data import get_stations


st.set_page_config(layout="wide")

# Streamlit UI
st.title("Station Data Fetcher")

# User inputs
station_code = st.text_input("Enter Station Code")
start_date = str(st.date_input("Start Date", value=date.today()))
end_date = str(st.date_input("End Date", value=date.today()))

# Ensure start date is before end date
if start_date > end_date:
    st.error("Start date must be before or equal to end date.")
else:
    # Button to trigger the function
    if st.button("Fetch Data", use_container_width=True, type="primary"):
        df = get_data(
            station_code=station_code, start_date=start_date, end_date=end_date
        )
        st.success("Data retrieved successfully!")

        st.dataframe(df)

st.write(get_stations())