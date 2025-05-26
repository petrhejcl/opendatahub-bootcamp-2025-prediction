import pandas as pd
import pickle

class CsvDataLoader(IDataLoader):
    def load_data(self, file_path: str) -> pd.DataFrame:
        df = pd.read_csv(file_path)
        df.columns = ["mvalidtime", "free", "occupied"]
        df["mvalidtime"] = pd.to_datetime(df["mvalidtime"])
        return df.sort_values("mvalidtime")

class PickleModelPersistence(IModelPersistence):
    def save_model(self, model: Any, feature_cols: List[str], model_path: str = "models/rf.pkl", cols_path: str = "models/rf_feature_cols.pkl") -> None:
        with open(model_path, "wb") as f:
            pickle.dump(model, f)
        with open(cols_path, "wb") as f:
            pickle.dump(feature_cols, f)

    def load_model(self, model_path: str = "models/rf.pkl", cols_path: str = "models/rf_feature_cols.pkl") -> Tuple[Any, List[str]]:
        with open(model_path, "rb") as f:
            model = pickle.load(f)
        with open(cols_path, "rb") as f:
            feature_cols = pickle.load(f)
        return model, feature_cols