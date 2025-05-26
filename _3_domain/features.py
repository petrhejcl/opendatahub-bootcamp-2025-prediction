def create_features(df: pd.DataFrame) -> pd.DataFrame:
    df["hour"] = df["mvalidtime"].dt.hour
    df["day_of_week"] = df["mvalidtime"].dt.dayofweek
    df["day_of_month"] = df["mvalidtime"].dt.day
    df["month"] = df["mvalidtime"].dt.month
    df["year"] = df["mvalidtime"].dt.year
    df["time_diff"] = df["mvalidtime"].diff().dt.total_seconds()

    temp_df = df[["mvalidtime", "free"]].copy()
    for i in range(1, 13):
        temp_df[f"free_lag_{i}"] = temp_df["free"].shift(i)
    df = pd.concat([df, temp_df.drop(columns="free")], axis=1)

    df["rate_of_change"] = (df["free"] - df["free_lag_1"]) / df["time_diff"]
    df["target"] = df["free"].shift(-12)
    return df