import pickle as pkl

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from task2 import load_data, create_features


def render_data_plot(df):
    # Create subplots with 2 rows and 1 column
    fig = make_subplots(
        rows=2,
        cols=1,
        subplot_titles=(
            "Parking Space Availability Over Time",
            "Average Free Spaces by Hour of Day",
        ),
    )

    # Plot free spaces over time
    fig.add_trace(
        go.Scatter(x=df["mvalidtime"], y=df["free"], mode="lines", name="Free Spaces"),
        row=1,
        col=1,
    )

    # Plot daily patterns
    df_grouped = df.groupby("hour")["free"].mean()
    fig.add_trace(go.Bar(x=df_grouped.index, y=df_grouped.values), row=2, col=1)

    # Update layout
    fig.update_layout(
        height=800, width=1000, showlegend=True, title_text="Parking Data Analysis"
    )

    # Update x-axis for the second subplot
    fig.update_xaxes(
        title_text="Hour of Day", row=2, col=1, tickvals=list(range(0, 24))
    )

    # Update y-axes
    fig.update_yaxes(
        title_text="Number of Free Spaces",
        row=1,
        col=1,
        gridwidth=1,
        gridcolor="LightGrey",
    )
    fig.update_yaxes(
        title_text="Average Free Spaces",
        row=2,
        col=1,
        gridwidth=1,
        gridcolor="LightGrey",
    )

    # Save to HTML file or as image
    # fig.write_html("parking_analysis.html")
    # fig.write_image("parking_analysis.png")

    st.plotly_chart(fig)


def render_performance_plot(df, model, feature_cols):
    # Get data with complete features and target
    clean_df = df.dropna(subset=["target"] + feature_cols)

    # Get features and make predictions for all available data
    X = clean_df[feature_cols]
    y_actual = clean_df["target"]
    y_pred = model.predict(X)

    # Get datetime for plotting
    datetimes = clean_df["mvalidtime"]

    # Create a DataFrame for easy plotting
    results_df = pd.DataFrame(
        {"mvalidtime": datetimes, "actual": y_actual, "predicted": y_pred}
    )

    # Create time series comparison plots with two subplots
    fig1 = make_subplots(
        rows=2,
        cols=1,
        subplot_titles=(
            "Actual vs Predicted Free Parking Spaces",
            "Actual vs Predicted Free Parking Spaces (Last 2 Days)",
        ),
    )

    # Plot full time series
    fig1.add_trace(
        go.Scatter(
            x=results_df["mvalidtime"],
            y=results_df["actual"],
            mode="lines",
            name="Actual Free Spaces",
            line=dict(color="blue"),
        ),
        row=1,
        col=1,
    )

    fig1.add_trace(
        go.Scatter(
            x=results_df["mvalidtime"],
            y=results_df["predicted"],
            mode="lines",
            name="Predicted Free Spaces",
            line=dict(color="red"),
        ),
        row=1,
        col=1,
    )

    # Focus on a smaller time window for better visibility (last 2 days)
    last_two_days = results_df["mvalidtime"] > (
            results_df["mvalidtime"].max() - pd.Timedelta(days=2)
    )
    zoom_df = results_df[last_two_days]

    fig1.add_trace(
        go.Scatter(
            x=zoom_df["mvalidtime"],
            y=zoom_df["actual"],
            mode="lines",
            name="Actual Free Spaces (Last 2 Days)",
            line=dict(color="blue"),
            showlegend=False,
        ),
        row=2,
        col=1,
    )

    fig1.add_trace(
        go.Scatter(
            x=zoom_df["mvalidtime"],
            y=zoom_df["predicted"],
            mode="lines",
            name="Predicted Free Spaces (Last 2 Days)",
            line=dict(color="red"),
            showlegend=False,
        ),
        row=2,
        col=1,
    )

    # Update layout for first figure
    fig1.update_layout(
        height=800,
        width=1000,
        title_text="Actual vs Predicted Free Parking Spaces Analysis",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
    )

    fig1.update_xaxes(title_text="Date & Time", row=1, col=1)
    fig1.update_xaxes(title_text="Date & Time", row=2, col=1)
    fig1.update_yaxes(
        title_text="Number of Free Spaces",
        row=1,
        col=1,
        gridwidth=1,
        gridcolor="LightGrey",
    )
    fig1.update_yaxes(
        title_text="Number of Free Spaces",
        row=2,
        col=1,
        gridwidth=1,
        gridcolor="LightGrey",
    )

    st.plotly_chart(fig1)

    # Create scatter plot to see correlation
    fig2 = go.Figure()

    # Add scatter plot
    fig2.add_trace(
        go.Scatter(
            x=results_df["actual"],
            y=results_df["predicted"],
            mode="markers",
            marker=dict(size=8, color="blue", opacity=0.5),
            name="Data Points",
        )
    )

    # Add diagonal reference line
    min_val = min(results_df["actual"].min(), results_df["predicted"].min())
    max_val = max(results_df["actual"].max(), results_df["predicted"].max())

    fig2.add_trace(
        go.Scatter(
            x=[min_val, max_val],
            y=[min_val, max_val],
            mode="lines",
            line=dict(color="red", dash="dash"),
            name="Perfect Prediction",
        )
    )

    # Update layout for scatter plot
    fig2.update_layout(
        height=700,
        width=700,
        title_text="Actual vs Predicted Parking Spaces",
        xaxis_title="Actual Free Spaces",
        yaxis_title="Predicted Free Spaces",
        xaxis=dict(gridwidth=1, gridcolor="LightGrey"),
        yaxis=dict(gridwidth=1, gridcolor="LightGrey"),
    )

    st.plotly_chart(fig2)

    # Calculate some statistics
    error = results_df["predicted"] - results_df["actual"]
    mae = np.mean(np.abs(error))
    rmse = np.sqrt(np.mean(error ** 2))

    st.metric(label="Mean Absolute Error", value=f"{mae:.2f} spaces")
    st.metric(label="Root Mean Square Error", value=f"{rmse:.2f} spaces")


def plots_page():
    df = load_data(file_path="parking.csv")
    df = create_features(df=df)

    render_data_plot(df=df)

    model = pkl.load(open("rf.pkl", "rb"))
    feature_cols = pkl.load(open("rf_feature_cols.pkl", "rb"))

    render_performance_plot(df=df, model=model, feature_cols=feature_cols)
