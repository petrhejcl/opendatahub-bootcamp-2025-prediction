import matplotlib.pyplot as plt
import numpy as np

class MatplotlibVisualizationService(IVisualizationService):
    def visualize_parking_data(self, df: pd.DataFrame, output: str = "parking_analysis.png") -> None:
        plt.figure(figsize=(14, 8))
        plt.subplot(2, 1, 1)
        plt.plot(df["mvalidtime"], df["free"], label="Free Spaces")
        plt.title("Parking Space Availability Over Time")
        plt.xlabel("Date & Time")
        plt.ylabel("Free Spaces")
        plt.grid(True)
        plt.subplot(2, 1, 2)
        df_grouped = df.groupby("hour")["free"].mean()
        plt.bar(df_grouped.index, df_grouped.values)
        plt.title("Average Free Spaces by Hour")
        plt.xlabel("Hour")
        plt.ylabel("Average")
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(output)
        plt.close()