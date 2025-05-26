class ParkingService:
    def __init__(self, 
                 token_provider: ITokenProvider,
                 data_repository: IDataRepository,
                 model_persistence: IModelPersistence):
        self._token_provider = token_provider
        self._data_repository = data_repository
        self._model_persistence = model_persistence

    def run_pipeline(self, config: Dict[str, Any]) -> Tuple[float, float]:
        token = self._token_provider.get_token(config["client_id"], config["client_secret"])
        raw_data = self._data_repository.fetch_parking_data(
            config["station_code"], config["start_date"], config["end_date"], token
        )

        df = pd.DataFrame(raw_data)
        df = df.pivot(index="mvalidtime", columns="tname", values="mvalue").reset_index()

        df = create_features(df)

        model, feature_cols, train_score, val_score = train_model(df)

        self._model_persistence.save_model(model, feature_cols, "models/rf.pkl", "models/rf_feature_cols.pkl")

        return train_score, val_score