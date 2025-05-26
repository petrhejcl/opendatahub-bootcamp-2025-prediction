from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

def train_model(df: pd.DataFrame) -> Tuple[Any, List[str], float, float]:
    feature_cols = [
        "hour", "day_of_week", "day_of_month", "month", "year",
        "free", "occupied", "rate_of_change"
    ] + [col for col in df.columns if "lag" in col]

    clean_df = df.dropna()
    X = clean_df[feature_cols]
    y = clean_df["target"]

    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    train_score = model.score(X_train, y_train)
    val_score = model.score(X_val, y_val)

    return model, feature_cols, train_score, val_score