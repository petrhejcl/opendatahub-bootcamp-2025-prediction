# presentation/visualizations.py
from typing import List

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots
import numpy as np

from application.dtos import VisualizationDataDTO, ModelPerformanceDTO


class ParkingDataVisualizer:
    """Visualizer per i dati di parcheggio - solo logica di presentazione"""

    def render_data_plot(self, visualization_data: List[VisualizationDataDTO]) -> None:
        """Render basic parking data plots using DTOs"""
        if not visualization_data:
            st.warning("No data available for visualization")
            return

        # Convert DTOs to DataFrame for plotting
        df = self._convert_dtos_to_dataframe(visualization_data)

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
            go.Scatter(x=df["timestamp"], y=df["free_spaces"], mode="lines", name="Free Spaces"),
            row=1,
            col=1,
        )

        # Plot daily patterns
        df_grouped = df.groupby("hour")["free_spaces"].mean()
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

        st.plotly_chart(fig)

    def render_performance_plot(self, performance: ModelPerformanceDTO) -> None:
        """Render model performance visualization usando DTOs"""
        if not performance.actual_values or not performance.predicted_values:
            st.warning("No performance data available for visualization")
            return

        # Create DataFrame for plotting
        results_df = pd.DataFrame({
            'timestamp': performance.timestamps,
            'actual': performance.actual_values,
            'predicted': performance.predicted_values
        })

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
                x=results_df["timestamp"],
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
                x=results_df["timestamp"],
                y=results_df["predicted"],
                mode="lines",
                name="Predicted Free Spaces",
                line=dict(color="red"),
            ),
            row=1,
            col=1,
        )

        # Focus on last 2 days
        last_two_days = results_df["timestamp"] > (
                results_df["timestamp"].max() - pd.Timedelta(days=2)
        )
        zoom_df = results_df[last_two_days]

        fig1.add_trace(
            go.Scatter(
                x=zoom_df["timestamp"],
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
                x=zoom_df["timestamp"],
                y=zoom_df["predicted"],
                mode="lines",
                name="Predicted Free Spaces (Last 2 Days)",
                line=dict(color="red"),
                showlegend=False,
            ),
            row=2,
            col=1,
        )

        # Update layout
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

        # Create scatter plot
        fig2 = go.Figure()

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

        # Calculate and display metrics
        error = np.array(performance.predicted_values) - np.array(performance.actual_values)
        mae = np.mean(np.abs(error))
        rmse = np.sqrt(np.mean(error ** 2))

        st.metric(label="Mean Absolute Error", value=f"{mae:.2f} spaces")
        st.metric(label="Root Mean Square Error", value=f"{rmse:.2f} spaces")

    def _convert_dtos_to_dataframe(self, visualization_data: List[VisualizationDataDTO]) -> pd.DataFrame:
        """Convert VisualizationDataDTO to DataFrame for plotting"""
        data = []
        for item in visualization_data:
            data.append({
                'timestamp': item.timestamp,
                'free_spaces': item.free_spaces,
                'occupied_spaces': item.occupied_spaces,
                'hour': item.hour
            })
        return pd.DataFrame(data)