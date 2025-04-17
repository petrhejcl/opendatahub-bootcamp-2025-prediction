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

on = st.toggle(label="toggle map", value=False)
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

    # Get current selected station
    selected_station = next((s for s in stations if s["id"] == st.session_state.selected_station_id), stations[0])

    col1, col2 = st.columns([2, 1])

    with col1:
        # Create Folium map centered on selected station
        m = folium.Map(location=[selected_station["lat"], selected_station["lon"]], zoom_start=15)

        # Add only single, large circle markers for each station
        for s in stations:
            # Set color based on selection
            color = "blue" if s["id"] == st.session_state.selected_station_id else "green"

            # Create a single large circle marker with good clickability
            # Removed popup parameter to avoid fixed dialog
            folium.CircleMarker(
                location=[s["lat"], s["lon"]],
                radius=20,  # Large radius for better clicking
                color=color,
                fill=True,
                fill_opacity=0.7,
                weight=4,  # Thick border for visibility
                tooltip=s["sname"]  # Only tooltip (hover text) remains
            ).add_to(m)

        # Display map
        map_data = st_folium(
            m,
            width=600,
            height=400,
            key="station_map",
            returned_objects=["last_clicked"]
        )

        # Process map clicks with generous tolerance
        if map_data and map_data.get("last_clicked"):
            clicked_coords = map_data["last_clicked"]
            clicked_lat = clicked_coords["lat"]
            clicked_lon = clicked_coords["lng"]

            # Find nearest station
            min_distance = float('inf')
            clicked_station = None

            for s in stations:
                # Calculate distance
                distance = ((s["lat"] - clicked_lat) ** 2 + (s["lon"] - clicked_lon) ** 2) ** 0.5
                if distance < min_distance:
                    min_distance = distance
                    clicked_station = s

            # Use a generous click tolerance
            if min_distance < 0.03 and clicked_station and clicked_station[
                "id"] != st.session_state.selected_station_id:
                # Update selection and auto-center map
                st.session_state.selected_station_id = clicked_station["id"]
                # Rerun to update the map
                st.rerun()

    with col2:
        # Station selection dropdown
        station_index = next(i for i, s in enumerate(stations) if s["id"] == st.session_state.selected_station_id)

        station = st.selectbox(
            "Select the parking",
            options=stations,
            index=station_index,
            format_func=lambda e: e["sname"],
            key="station_selector"
        )

        # Update selection from dropdown without auto-centering
        if station["id"] != st.session_state.selected_station_id:
            st.session_state.selected_station_id = station["id"]
            selected_station = station

        # Display station info
        st.markdown(f"### {selected_station['sname']}")
        st.write(f"ID: {selected_station['id']}")
        st.write(f"Latitude: {selected_station['lat']:.6f}")
        st.write(f"Longitude: {selected_station['lon']:.6f}")

        # Show on Map button
        if st.button("Show on Map"):
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
