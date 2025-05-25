# app/presentation/pages/model_training_page.py
import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
from ...domain.model_training.training_service import ModelTrainingService
from ...data_access.model_repository import ModelRepository
from ...data_access.parking_repository import ParkingRepository


def model_training_page():
    st.title("Model Training")

    # Initialize services
    model_repository = ModelRepository()
    parking_repository = ParkingRepository()
    training_service = ModelTrainingService(model_repository)

    # Station selection
    st.subheader("Select Station and Date Range")
    station_code = st.text_input("Station Code", value="116")

    # Date selection
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", datetime.now() - timedelta(days=30))
    with col2:
        end_date = st.date_input("End Date", datetime.now())

    if st.button("Load Data and Train Model", type="primary"):
        try:
            with st.spinner("Loading data..."):
                # Load data
                df = parking_repository.get_parking_dataframe(
                    station_code,
                    datetime.combine(start_date, datetime.min.time()),
                    datetime.combine(end_date, datetime.min.time())
                )

                if df is None or df.empty:
                    st.error("No data found for the selected station and date range")
                    return

                st.success(f"Loaded {len(df)} data points")

                # Display data preview
                st.subheader("Data Preview")
                st.dataframe(df.head())

            with st.spinner("Training model..."):
                # Train model
                model, feature_cols = training_service.train_model(df)
                st.success("Model trained successfully!")

                # Display feature importance if available
                if hasattr(model, 'feature_importances_'):
                    importance_df = pd.DataFrame({
                        'Feature': feature_cols,
                        'Importance': model.feature_importances_
                    }).sort_values('Importance', ascending=False)

                    st.subheader("Feature Importance")
                    st.dataframe(importance_df.head(10))

        except Exception as e:
            st.error(f"Error during training: {str(e)}")