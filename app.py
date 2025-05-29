import streamlit as st

from tabs.normal_version import normal_version_page
from tabs.simplified_version import simplified_version_page

st.set_page_config(layout="wide")

# Streamlit UI
st.title("Free Parking Spots Prediction")

on = st.toggle(label="Simplified version", value=True)

if on:
    simplified_version_page()
else:
    normal_version_page()
