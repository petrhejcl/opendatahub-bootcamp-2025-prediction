import streamlit as st

from datetime import date
from get_data import get_stations, get_data
from tabs.model_training import model_training_page
from tabs.normal_version import normal_version_page
from tabs.occupancy_prediction import occupancy_prediction_page
from tabs.plots import plots_page

import streamlit as st
from streamlit_folium import st_folium
import folium

from tabs.simplified_version import simplified_version_page

st.set_page_config(layout="wide")

# Streamlit UI
st.title("Free Parking Spots Prediction")

on = st.toggle(label="Simplified version", value=True)
if on:
    simplified_version_page()
else:
    normal_version_page()
