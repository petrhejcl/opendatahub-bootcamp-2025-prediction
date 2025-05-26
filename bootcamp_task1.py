from _1_presentation.cli import predict

if __name__ == "__main__":
    # Usa stringa oraria, oppure lascia None per default
    predict(prediction_time_str="2025-05-26 15:00", use_stored_model=True)
