import datetime

import streamlit as st

from predict import predict


def get_current_time():
    # Get current date and time
    now = datetime.datetime.now()

    # Round minutes to nearest 5-minute interval
    rounded_minute = 5 * round(now.minute / 5)

    # Handle the case when rounded_minute becomes 60
    if rounded_minute == 60:
        # Add an hour and set minutes to 0 instead of using replace with minute=60
        rounded_time = (now + datetime.timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
    else:
        rounded_time = now.replace(minute=rounded_minute, second=0, microsecond=0)

    return rounded_time


def occupancy_prediction_page():
    start_date = st.date_input('Enter date of arrival', value=datetime.date.today())
    start_time = st.time_input('Enter time of arrival', get_current_time())

    prediction_datetime = datetime.datetime.combine(start_date, start_time)

    if st.button("Estimate", use_container_width=True, type="primary", key="occupancy_prediction"):
        with st.spinner("Wait for it...", show_time=True):
            free_spaces = predict(prediction_datetime, False)

        if free_spaces is not None:
            st.subheader(f"Expected number of free parking spaces {free_spaces}", divider=True)
