from dateutil.utils import today
from networkx.classes import is_empty

from get_data import get_stations, get_data
import streamlit as st
from streamlit_folium import st_folium
import folium
import datetime
from dateutil.relativedelta import relativedelta

from predict import predict
from tabs.occupancy_prediction import get_current_time


def simplified_version_page():
    def get_coordinates():
        data = get_stations()
        stations = []
        if isinstance(data, list):
            key = 'pcoordinate'
            for d in data:
                if key in d:
                    stations.append(
                        {"scode": int(d['scode']), "sname": d['sname'], "lat": d[key]['y'], "lon": d[key]['x']})
        return stations

    stations = get_coordinates()

    def custom_formats(station):
        key = 'pcoordinate'
        if key in station:
            return f"{station['sname']} (available on the map)"
        else:
            return station['sname']

    # Init session state
    if "selected_station_id" not in st.session_state:
        st.session_state.selected_station_id = stations[0]["scode"]

    # Get current selected station
    selected_station = next((s for s in stations if s["scode"] == st.session_state.selected_station_id), stations[0])

    col1, col2 = st.columns([2, 1])

    with col1:
        # Create Folium map centered on selected station
        m = folium.Map(location=[selected_station["lat"], selected_station["lon"]], zoom_start=15)

        # Add only single, large circle markers for each station
        for s in stations:
            # Set color based on selection
            color = "blue" if s["scode"] == st.session_state.selected_station_id else "green"

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
                "scode"] != st.session_state.selected_station_id:
                # Update selection and auto-center map
                st.session_state.selected_station_id = clicked_station["scode"]
                # Rerun to update the map
                st.rerun()

    with col2:
        # Station selection dropdown
        all_stations = get_stations()
        station_index = next(
            (i for i, s in enumerate(all_stations) if int(s["scode"]) == st.session_state.selected_station_id), 0)

        selected_station_from_dropdown = st.selectbox(
            "Select the parking",
            options=all_stations,
            index=station_index,
            format_func=custom_formats,
            key="station_selector"
        )

        # Update session state from dropdown selection
        if selected_station_from_dropdown and "scode" in selected_station_from_dropdown:
            dropdown_station_id = int(selected_station_from_dropdown["scode"])
            if dropdown_station_id != st.session_state.selected_station_id:
                st.session_state.selected_station_id = dropdown_station_id
                # No rerun here to prevent infinite loop

        # Now get the complete station data for display
        current_station_data = next(
            (s for s in all_stations if int(s["scode"]) == st.session_state.selected_station_id), None)

        if current_station_data:
            # Display station info
            st.markdown(f"### {current_station_data['sname']}")
            st.write(f"ID: {current_station_data['scode']}")

            if 'pcoordinate' in current_station_data:
                st.write(f"Latitude: {current_station_data['pcoordinate']['y']:.6f}")
                st.write(f"Longitude: {current_station_data['pcoordinate']['x']:.6f}")

                # Show on Map button only for stations with coordinates
                if st.button("Show on Map"):
                    # Find the station with coordinates in our map-enabled stations list
                    map_station = next((s for s in stations if s["scode"] == st.session_state.selected_station_id),
                                       None)
                    if map_station:
                        st.rerun()
                    else:
                        st.warning("This station is not available on the map.")
            else:
                st.info("Coordinates not available for this station")

        end_date = st.date_input('Enter date of arrival', value=datetime.date.today())
        end_time = st.time_input('Enter time of arrival', get_current_time())
        past = datetime.date.today() - relativedelta(months=6)

        prediction_datetime = datetime.datetime.combine(end_date, end_time)
        if past > end_date:
            st.error("Start date must be before or equal to end date.")

        if st.button("Fetch Data", use_container_width=True, type="primary"):
            if current_station_data:  # Make sure we have a station selected
                df = get_data(
                    station_code=st.session_state.selected_station_id,
                    start_date=past,
                    end_date=today()
                )

                free_spaces = predict(prediction_datetime, True)
                if free_spaces is not None:
                    st.subheader(f"Expected number of free parking spaces: {free_spaces}", divider=True)
            else:
                st.error("Please select a valid station first.")