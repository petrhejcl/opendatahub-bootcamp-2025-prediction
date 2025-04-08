import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import datetime

df = pd.read_csv("parking.csv", parse_dates=["mvalidtime"])  # Adjust column name
df = df.sort_values("mvalidtime")

df["sum"] = df[["occupied", "free"]].sum(axis=1)

df.set_index("mvalidtime", inplace=True)

df = df.resample("5T").mean()  # or "1H" if already hourly

print(df)

df = df.fillna(method="ffill")

df["target"] = df["occupied"].shift(-12)

df = df.dropna()  # Drop rows with NaNs from shifting

X = df[["occupied"]]  # Or other features
y = df["target"]

X_train, X_test, y_train, y_test = train_test_split(X, y, shuffle=False)

model = LinearRegression()
model.fit(X_train, y_train)

latest = df.iloc[-1:]
prediction = model.predict(latest[["occupied"]])

print(f"Predicted occupancy in 1 hour: {prediction[0]:.2f}")