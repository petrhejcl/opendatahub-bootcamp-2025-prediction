import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
from datetime import timedelta
import pickle as pkl


# Load the data
def load_data(file_path):
    df = pd.read_csv(file_path)

    # Ensure the first column is parsed as datetime
    df.columns = ["mvalidtime", "free", "occupied"]
    df["mvalidtime"] = pd.to_datetime(df["mvalidtime"])

    # Sort by datetime to ensure chronological order
    df = df.sort_values("mvalidtime")

    return df


# Feature engineering
def create_features(df):
    # Extract datetime features
    df["hour"] = df["mvalidtime"].dt.hour
    df["day_of_week"] = df["mvalidtime"].dt.dayofweek
    df["day_of_month"] = df["mvalidtime"].dt.day
    df["month"] = df["mvalidtime"].dt.month
    df["year"] = df["mvalidtime"].dt.year

    # Calculate time differences since the data might have gaps
    df["time_diff"] = df["mvalidtime"].diff().dt.total_seconds()

    # Calculate rolling statistics (last hour's trend)
    # First, create a temporary DataFrame with just datetime and free
    temp_df = df[["mvalidtime", "free"]].copy()

    # Create lagged features (values from previous time steps)
    for i in range(1, 13):  # Create 12 lags (assuming 5-minute intervals)
        temp_df[f"free_lag_{i}"] = temp_df["free"].shift(i)

    # Add these features back to the original DataFrame
    lag_columns = [col for col in temp_df.columns if "lag" in col]
    df = pd.concat([df, temp_df[lag_columns]], axis=1)

    # Calculate rate of change
    df["rate_of_change"] = (df["free"] - df["free_lag_1"]) / df["time_diff"]

    # Create target variable: free spaces in one hour
    # 3600 seconds = 1 hour, our interval is 300 seconds, so shift by 12 rows
    df["target"] = df["free"].shift(-12)

    return df


# Train the model
def train_model(df):
    # Features we'll use for prediction
    feature_cols = [
        "hour",
        "day_of_week",
        "day_of_month",
        "month",
        "year",
        "free",
        "occupied",
        "rate_of_change",
    ]

    # Add lag features
    lag_cols = [col for col in df.columns if "lag" in col]
    feature_cols.extend(lag_cols)

    # Remove rows with NaN (will be at the beginning due to lag features)
    clean_df = df.dropna()

    # Split features and target
    X = clean_df[feature_cols]
    y = clean_df["target"]

    # Split into training and validation sets
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Create and train the model
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Evaluate the model
    train_score = model.score(X_train, y_train)
    val_score = model.score(X_val, y_val)

    print(f"Training R² score: {train_score:.4f}")
    print(f"Validation R² score: {val_score:.4f}")

    # Predict on validation set and calculate MAE
    y_pred = model.predict(X_val)
    mae = np.mean(np.abs(y_pred - y_val))
    print(f"Mean Absolute Error: {mae:.2f} parking spaces")

    # Feature importance
    feature_importance = pd.DataFrame(
        {"Feature": feature_cols, "Importance": model.feature_importances_}
    ).sort_values("Importance", ascending=False)

    print("\nTop 10 most important features:")
    print(feature_importance.head(10))

    return model, feature_cols


# Predict future availability
def predict_future(df, model, feature_cols, prediction_time=None):
    if prediction_time is None:
        # Use the last timestamp in the dataset
        last_time = df["mvalidtime"].iloc[-1]
        prediction_time = last_time + timedelta(hours=1)

    # Get the most recent complete row of data
    latest_data = df.iloc[-1:].copy()

    # Create a new row for the prediction time
    prediction_row = latest_data.copy()
    prediction_row["mvalidtime"] = prediction_time

    # Update datetime features
    prediction_row["hour"] = prediction_time.hour
    prediction_row["day_of_week"] = prediction_time.dayofweek
    prediction_row["day_of_month"] = prediction_time.day
    prediction_row["month"] = prediction_time.month
    prediction_row["year"] = prediction_time.year

    # Make sure we have all required features
    missing_cols = set(feature_cols) - set(prediction_row.columns)
    for col in missing_cols:
        prediction_row[col] = 0

    # Make prediction
    X_pred = prediction_row[feature_cols]
    predicted_spaces = model.predict(X_pred)[0]

    return prediction_time, round(predicted_spaces)


# Compare predicted vs actual values
def plot_predicted_vs_actual(df, model, feature_cols):
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

    # Plot the comparison
    plt.figure(figsize=(14, 8))

    # Time series plot of actual vs predicted
    plt.subplot(2, 1, 1)
    plt.plot(
        results_df["mvalidtime"], results_df["actual"], "b-", label="Actual Free Spaces"
    )
    plt.plot(
        results_df["mvalidtime"],
        results_df["predicted"],
        "r-",
        label="Predicted Free Spaces",
    )
    plt.title("Actual vs Predicted Free Parking Spaces")
    plt.xlabel("Date & Time")
    plt.ylabel("Number of Free Spaces")
    plt.legend()
    plt.grid(True)

    # Focus on a smaller time window for better visibility (last 2 days)
    last_two_days = results_df["mvalidtime"] > (
        results_df["mvalidtime"].max() - pd.Timedelta(days=2)
    )
    zoom_df = results_df[last_two_days]

    plt.subplot(2, 1, 2)
    plt.plot(zoom_df["mvalidtime"], zoom_df["actual"], "b-", label="Actual Free Spaces")
    plt.plot(
        zoom_df["mvalidtime"], zoom_df["predicted"], "r-", label="Predicted Free Spaces"
    )
    plt.title("Actual vs Predicted Free Parking Spaces (Last 2 Days)")
    plt.xlabel("Date & Time")
    plt.ylabel("Number of Free Spaces")
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.savefig("predicted_vs_actual.png")

    # Also create a scatter plot to see correlation
    plt.figure(figsize=(10, 8))
    plt.scatter(results_df["actual"], results_df["predicted"], alpha=0.5)
    plt.plot(
        [min(results_df["actual"]), max(results_df["actual"])],
        [min(results_df["actual"]), max(results_df["actual"])],
        "r--",
    )
    plt.title("Actual vs Predicted Parking Spaces")
    plt.xlabel("Actual Free Spaces")
    plt.ylabel("Predicted Free Spaces")
    plt.grid(True)
    plt.savefig("correlation_plot.png")

    # Calculate some statistics
    error = results_df["predicted"] - results_df["actual"]
    mae = np.mean(np.abs(error))
    rmse = np.sqrt(np.mean(error**2))

    print(f"Mean Absolute Error: {mae:.2f} spaces")
    print(f"Root Mean Square Error: {rmse:.2f} spaces")

    return results_df


# Visualize results
def visualize_parking_data(df):
    plt.figure(figsize=(14, 8))

    # Plot free spaces over time
    plt.subplot(2, 1, 1)
    plt.plot(df["mvalidtime"], df["free"], label="Free Spaces")
    plt.title("Parking Space Availability Over Time")
    plt.xlabel("Date & Time")
    plt.ylabel("Number of Free Spaces")
    plt.legend()
    plt.grid(True)

    # Plot daily patterns
    plt.subplot(2, 1, 2)
    df_grouped = df.groupby("hour")["free"].mean()
    plt.bar(df_grouped.index, df_grouped.values)
    plt.title("Average Free Spaces by Hour of Day")
    plt.xlabel("Hour of Day")
    plt.ylabel("Average Free Spaces")
    plt.xticks(range(0, 24))
    plt.grid(True, axis="y")

    plt.tight_layout()
    plt.savefig("parking_analysis.png")
    plt.close()


def main(use_stored_model=True):
    # Load data
    file_path = "parking.csv"  # Update with your file path
    try:
        df = load_data(file_path)
        print(f"Loaded {len(df)} records from {file_path}")
        print(f"Date range: {df['mvalidtime'].min()} to {df['mvalidtime'].max()}")
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return

    # Feature engineering
    df_features = create_features(df)
    print(f"Created features. Shape: {df_features.shape}")

    if use_stored_model:
        model = pkl.load(open("rf.pkl", "rb"))
        feature_cols = pkl.load(open("rf_feature_cols.pkl", "rb"))
    else:
        # Train model
        model, feature_cols = train_model(df_features)
        pkl.dump(model, open("rf.pkl", "wb"))
        pkl.dump(feature_cols, open("rf_feature_cols.pkl", "wb"))

    # Plot predicted vs actual
    print("\nGenerating predicted vs actual comparison plots...")
    plot_predicted_vs_actual(df_features, model, feature_cols)
    print("Created visualization: predicted_vs_actual.png and correlation_plot.png")

    # Make prediction for one hour in the future
    prediction_time, predicted_spaces = predict_future(df_features, model, feature_cols)

    print(f"\nPrediction for {prediction_time}:")
    print(f"Estimated free parking spaces: {predicted_spaces}")

    # Visualize data
    visualize_parking_data(df)
    print("Created visualization: parking_analysis.png")


if __name__ == "__main__":
    main(False)
