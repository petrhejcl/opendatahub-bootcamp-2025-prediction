from datetime import datetime, timedelta

class StandardPredictionService(IPredictionService):
    def parse_prediction_time(self, time_str: str) -> datetime:
        formats = [
            "%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S", "%d/%m/%Y %H:%M",
            "%m/%d/%Y %H:%M", "%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"
        ]
        for fmt in formats:
            try:
                return pd.to_datetime(time_str, format=fmt)
            except ValueError:
                continue
        return datetime.now() + timedelta(hours=1)

    def predict_future(self, df: pd.DataFrame, model: Any, feature_cols: List[str], prediction_time: Optional[datetime] = None) -> Tuple[datetime, int]:
        if prediction_time is None:
            prediction_time = df["mvalidtime"].iloc[-1] + timedelta(hours=1)

        latest_data = df.iloc[-1:].copy()
        prediction_row = latest_data.copy()
        prediction_row["mvalidtime"] = prediction_time
        prediction_row["hour"] = prediction_time.hour
        prediction_row["day_of_week"] = prediction_time.dayofweek
        prediction_row["day_of_month"] = prediction_time.day
        prediction_row["month"] = prediction_time.month
        prediction_row["year"] = prediction_time.year

        for col in feature_cols:
            if col not in prediction_row.columns:
                prediction_row[col] = 0

        X_pred = prediction_row[feature_cols]
        predicted = model.predict(X_pred)[0]
        return prediction_time, round(predicted)