def main_pipeline():
    """Entry point per il pipeline principale"""
    config = {
        "client_id": "opendatahub-bootcamp-2025",
        "client_secret": "QiMsLjDpLi5ffjKRkI7eRgwOwNXoU9l1",
        "station_code": 116,
        "start_date": "2024-04-08",
        "end_date": "2025-04-08"
    }

    parking_service = create_parking_service()
    train_score, val_score = parking_service.run_pipeline(config)
    print(f"Training R²: {train_score:.4f}, Validation R²: {val_score:.4f}")

def main_prediction(prediction_time_str: Optional[str] = None, use_stored_model: bool = True):
    """Entry point per le predizioni"""
    prediction_service = create_prediction_service()
    prediction_service.predict(prediction_time_str, use_stored_model)

if __name__ == "__main__":
    # Esegui il pipeline
    main_pipeline()

    # Esegui predizione
    main_prediction()