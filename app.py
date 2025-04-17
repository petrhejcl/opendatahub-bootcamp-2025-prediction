import streamlit as st

from datetime import date
from get_data import get_stations, get_data
from tabs.model_training import model_training_page
from tabs.occupancy_prediction import occupancy_prediction_page
from tabs.plots import plots_page

import streamlit as st
from streamlit_folium import st_folium
import folium

st.set_page_config(layout="wide")

# Streamlit UI
st.title("Free Parking Spots Prediction")

station = st.selectbox(
    label="Select the parking",
    options=get_stations(),
    format_func=lambda e: f"{e['sname']}",
)
start_date = str(st.date_input("Start Date", value=date.today()))
end_date = str(st.date_input("End Date", value=date.today()))

on=st.toggle(label="prova",value=False)
if on:
    # Sample stations
    def get_stations():
        return [
            {"id": 1, "sname": "Central Park", "lat": 40.785091, "lon": -73.968285},
            {"id": 2, "sname": "Times Square", "lat": 40.758896, "lon": -73.985130},
            {"id": 3, "sname": "Empire State", "lat": 40.748817, "lon": -73.985428},
        ]


    stations = get_stations()

    # Init session state
    if "selected_station_id" not in st.session_state:
        st.session_state.selected_station_id = stations[0]["id"]

    # Get last selected station
    selected_station = next((s for s in stations if s["id"] == st.session_state.selected_station_id), stations[0])

    # --- 1. Folium map first ---
    m = folium.Map(location=[selected_station["lat"], selected_station["lon"]], zoom_start=15)

    # Add markers
    for s in stations:
        color = "blue" if s["id"] == st.session_state.selected_station_id else "green"
        folium.Marker(
            location=[s["lat"], s["lon"]],
            popup=s["sname"],
            tooltip=s["sname"],
            icon=folium.Icon(color=color)
        ).add_to(m)

    # Display map and capture interaction
    map_data = st_folium(m, width=700, height=500)

    # --- 2. Handle map click before rendering selectbox ---
    if map_data and map_data.get("last_object_clicked"):
        clicked_coords = map_data["last_object_clicked"]
        clicked_lat = clicked_coords["lat"]
        clicked_lon = clicked_coords["lng"]

        # Match by coordinates (within small tolerance)
        tolerance = 0.0001
        clicked_station = next(
            (s for s in stations if
             abs(s["lat"] - clicked_lat) < tolerance and abs(s["lon"] - clicked_lon) < tolerance),
            None
        )

        # If clicked station is different, update state and rerun
        if clicked_station and clicked_station["id"] != st.session_state.selected_station_id:
            st.session_state.selected_station_id = clicked_station["id"]
            st.rerun()

    # --- 3. Render selectbox, bound to session state ---
    station = st.selectbox(
        "Select the parking",
        options=stations,
        index=next(i for i, s in enumerate(stations) if s["id"] == st.session_state.selected_station_id),
        format_func=lambda e: e["sname"]
    )

    # Update state if selectbox changes
    if station["id"] != st.session_state.selected_station_id:
        st.session_state.selected_station_id = station["id"]
        st.rerun()

else:
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
