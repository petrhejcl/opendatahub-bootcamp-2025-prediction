class PredictionService:
    def __init__(self, 
                 data_loader: IDataLoader,
                 model_persistence: IModelPersistence,
                 prediction_service: IPredictionService,
                 visualization_service: IVisualizationService):
        self._data_loader = data_loader
        self._model_persistence = model_persistence
        self._prediction_service = prediction_service
        self._visualization_service = visualization_service

    def predict(self, prediction_time_str: Optional[str] = None, use_stored_model: bool = True) -> None:
        df = self._data_loader.load_data("parking.csv")
        print(f"Loaded {len(df)} rows. Date range: {df['mvalidtime'].min()} to {df['mvalidtime'].max()}")

        df_features = create_features(df)

        if use_stored_model:
            try:
                model, feature_cols = self._model_persistence.load_model("models/rf.pkl", "models/rf_feature_cols.pkl")
                print("Loaded model from disk.")
            except FileNotFoundError:
                print("Model not found, training a new one...")
                model, feature_cols, _, _ = train_model(df_features)
                self._model_persistence.save_model(model, feature_cols, "models/rf.pkl", "models/rf_feature_cols.pkl")
        else:
            model, feature_cols, _, _ = train_model(df_features)
            self._model_persistence.save_model(model, feature_cols, "models/rf.pkl", "models/rf_feature_cols.pkl")

        prediction_time = self._prediction_service.parse_prediction_time(prediction_time_str) if prediction_time_str else None
        prediction_time, predicted = self._prediction_service.predict_future(df_features, model, feature_cols, prediction_time)

        print(f"Prediction for {prediction_time}: {predicted} free parking spaces")

        self._visualization_service.visualize_parking_data(df)