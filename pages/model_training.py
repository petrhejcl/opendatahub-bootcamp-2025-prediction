import streamlit as st
from datetime import date
from task2 import load_data, create_features, train_model
import pickle as pkl

from get_data import get_data

def model_training_page(station,start_date,end_date):
    # start_date2 = str(st.date_input("Start Date", value=date.today(),key="noh"))
    # end_date2 = str(st.date_input("End Date", value=date.today(),key="boh"))
    #
    #
    # if start_date2 > end_date2:
    #     st.error("Start date must be before or equal to end date.")
    # else:
    #     # Button to trigger the function
    df = load_data("parking.csv")
    df_features = create_features(df)

    if st.button("Train model", use_container_width=True, type="primary"):
        model, feature_cols = train_model(df_features)
        pkl.dump(model, open("rf.pkl", "wb"))
        pkl.dump(feature_cols, open("rf_feature_cols.pkl", "wb"))