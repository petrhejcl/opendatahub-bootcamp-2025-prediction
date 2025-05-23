import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import streamlit as st
from typing import Any, List
import logging

from core.exceptions import DataError

logger = logging.getLogger("parking_prediction")


class PerformancePlotService:
    """Service for creating model performance visualization plots."""

    def __init__(self):
        """Initialize the performance plot service."""
        pass

    def render_performance_plot(self, df: pd.DataFrame, model: Any, feature_cols: List[str]) -> None:
        """
        Render model performance visualization plots.

        Args:
            df: DataFrame with features and target
            model: Trained model
            feature_cols: List of feature column names

        Raises:
            DataError: If plotting fails
        """
        try:
            # Get data with complete features and target
            clean_df = df.dropna(subset=["target"] + feature_cols)

            if clean_df.empty:
                st.warning("No data available for performance visualization")
                return

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

            # Create time series comparison plots
            self._create_time_series_plot(results_df)

            # Create scatter plot
            self._create_scatter_plot(results_df)

            # Display metrics
            self._display_metrics(results_df)

        except Exception as e:
            logger.error(f"Failed to render performance plot: {e}")
            raise DataError(f"Failed to render performance plot: {e}")

    def _create_time_series_plot(self, results_df: pd.DataFrame) -> None:
        """Create time series comparison plot."""
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
                line=dict(color="blue", width=2),
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
                line=dict(color="red", width=2),
            ),
            row=1,
            col=1,
        )

        # Focus on a smaller time window for better visibility (last 2 days)
        last_two_days = results_df["mvalidtime"] > (
                results_df["mvalidtime"].max() - pd.Timedelta(days=2)
        )
        zoom_df = results_df[last_two_days]

        if not zoom_df.empty:
            fig1.add_trace(
                go.Scatter(
                    x=zoom_df["mvalidtime"],
                    y=zoom_df["actual"],
                    mode="lines",
                    name="Actual (Last 2 Days)",
                    line=dict(color="blue", width=2),
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
                    name="Predicted (Last 2 Days)",
                    line=dict(color="red", width=2),
                    showlegend=False,
                ),
                row=2,
                col=1,
            )

        # Update layout for first figure
        fig1.update_layout(
            height=800,
            title_text="Model Performance: Actual vs Predicted Analysis",
            title_x=0.5,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5
            ),
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

        st.plotly_chart(fig1, use_container_width=True)

    def _create_scatter_plot(self, results_df: pd.DataFrame) -> None:
        """Create scatter plot for correlation analysis."""
        fig2 = go.Figure()

        # Add scatter plot
        fig2.add_trace(
            go.Scatter(
                x=results_df["actual"],
                y=results_df["predicted"],
                mode="markers",
                marker=dict(
                    size=8,
                    color="blue",
                    opacity=0.6,
                    line=dict(width=1, color="darkblue")
                ),
                name="Predictions",
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
                line=dict(color="red", dash="dash", width=3),
                name="Perfect Prediction",
            )
        )

        # Update layout for scatter plot
        fig2.update_layout(
            height=600,
            title_text="Prediction Accuracy: Actual vs Predicted Values",
            title_x=0.5,
            xaxis_title="Actual Free Spaces",
            yaxis_title="Predicted Free Spaces",
            xaxis=dict(gridwidth=1, gridcolor="LightGrey"),
            yaxis=dict(gridwidth=1, gridcolor="LightGrey"),
        )

        st.plotly_chart(fig2, use_container_width=True)

    def _display_metrics(self, results_df: pd.DataFrame) -> None:
        """Display performance metrics."""
        # Calculate metrics
        error = results_df["predicted"] - results_df["actual"]
        mae = np.mean(np.abs(error))
        rmse = np.sqrt(np.mean(error ** 2))
        mape = np.mean(np.abs(error / results_df["actual"])) * 100  # Mean Absolute Percentage Error

        # Display metrics in columns
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                label="Mean Absolute Error",
                value=f"{mae:.2f} spaces",
                help="Average absolute difference between predicted and actual values"
            )

        with col2:
            st.metric(
                label="Root Mean Square Error",
                value=f"{rmse:.2f} spaces",
                help="Square root of the average squared differences"
            )

        with col3:
            st.metric(
                label="Mean Absolute Percentage Error",
                value=f"{mape:.2f}%",
                help="Average percentage difference between predicted and actual values"
            )