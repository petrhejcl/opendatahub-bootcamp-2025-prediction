from _2_service.prediction_service import predict_future, parse_prediction_time
from _3_domain.features import create_features
from _3_domain.model import train_model
from _4_infrastructure.io import load_data, save_model, load_model
from _4_infrastructure.visualization import visualize_parking_data
import pickle

def predict(prediction_time_str=None, use_stored_model=True):
    df = load_data("parking.csv")
    print(f"Loaded {len(df)} rows. Date range: {df['mvalidtime'].min()} to {df['mvalidtime'].max()}")

    df_features = create_features(df)

    if use_stored_model:
        try:
            model, feature_cols = load_model()
            print("Loaded model from disk.")
        except FileNotFoundError:
            print("Model not found, training a new one...")
            model, feature_cols, _, _ = train_model(df_features)
            save_model(model, feature_cols)
    else:
        model, feature_cols, _, _ = train_model(df_features)
        save_model(model, feature_cols)

    prediction_time = parse_prediction_time(prediction_time_str) if prediction_time_str else None
    prediction_time, predicted = predict_future(df_features, model, feature_cols, prediction_time)

    print(f"Prediction for {prediction_time}: {predicted} free parking spaces")

    visualize_parking_data(df)
