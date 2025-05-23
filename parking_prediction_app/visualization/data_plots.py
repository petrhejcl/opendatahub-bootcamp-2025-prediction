import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import streamlit as st
from typing import Optional
import logging

from core.exceptions import DataError

logger = logging.getLogger("parking_prediction")


class DataPlotService:
    """Service for creating data visualization plots."""

    def __init__(self):
        """Initialize the data plot service."""
        pass

    def render_data_plot(self, df: pd.DataFrame) -> None:
        """
        Render parking data visualization plots.

        Args:
            df: DataFrame with parking data

        Raises:
            DataError: If plotting fails
        """
        try:
            if df.empty:
                st.warning("No data available for visualization")
                return

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
                go.Scatter(
                    x=df["mvalidtime"],
                    y=df["free"],
                    mode="lines",
                    name="Free Spaces",
                    line=dict(color="blue", width=2)
                ),
                row=1,
                col=1,
            )

            # Plot daily patterns
            df_grouped = df.groupby("hour")["free"].mean()
            fig.add_trace(
                go.Bar(
                    x=df_grouped.index,
                    y=df_grouped.values,
                    name="Average by Hour",
                    marker_color="lightblue"
                ),
                row=2,
                col=1
            )

            # Update layout
            fig.update_layout(
                height=800,
                width=1000,
                showlegend=True,
                title_text="Parking Data Analysis",
                title_x=0.5
            )

            # Update x-axis for the second subplot
            fig.update_xaxes(
                title_text="Date & Time", row=1, col=1
            )
            fig.update_xaxes(
                title_text="Hour of Day",
                row=2,
                col=1,
                tickvals=list(range(0, 24))
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

            st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            logger.error(f"Failed to render data plot: {e}")
            raise DataError(f"Failed to render data plot: {e}")