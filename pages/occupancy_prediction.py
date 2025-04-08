import streamlit as st
import datetime

from predict import predict


def get_current_time():
    # Get current date and time
    now = datetime.datetime.now()

    # Round minutes to nearest 5-minute interval
    rounded_minute = 5 * round(now.minute / 5)
    rounded_time = now.replace(minute=rounded_minute, second=0, microsecond=0)

    # If rounding pushed us to the next hour
    if rounded_minute == 60:
        rounded_time = rounded_time + datetime.timedelta(hours=1)
        rounded_time = rounded_time.replace(minute=0)

    return rounded_time

def occupancy_prediction_page():
    start_date = st.date_input('Enter start date', value=datetime.date.today())
    start_time = st.time_input('Enter start time', get_current_time())

    prediction_datetime = datetime.datetime.combine(start_date, start_time)

    if st.button("Fetch Data", use_container_width=True, type="primary", key="occupancy_prediction"):
        with st.spinner("Wait for it...", show_time=True):
            free_spaces = predict(prediction_datetime, True)

        st.subheader(f"Expected number of free parking spaces {free_spaces}", divider=True)

