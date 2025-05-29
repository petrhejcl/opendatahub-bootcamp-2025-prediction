import pickle as pkl

import streamlit as st

from get_data import get_data
from task2 import load_data, create_features, train_model


def model_training_page(station, start_date, end_date):
    get_data(station_code=station["scode"], start_date=start_date, end_date=end_date)
    df = load_data("parking.csv")
    df_features = create_features(df)

    if st.button("Train model", use_container_width=True, type="primary"):
        try:
            model, feature_cols = train_model(df_features)
            pkl.dump(model, open("rf.pkl", "wb"))
            pkl.dump(feature_cols, open("rf_feature_cols.pkl", "wb"))
        except ValueError:
            st.warning("Make sure to have some data to train the model")
